"""
persona_loader.py

Loads personas from YAML and merges in all accepted patches from
the persona_patches table. Called at scan time — not at startup.
Produces persona dicts identical in structure to the YAML originals
but with security_reasoning_approach extended by current patches.
"""

import yaml
import sqlite3
import logging
from pathlib import Path

PERSONAS_PATH = Path(__file__).parent.parent / "agents" / "personas.yaml"
DB_PATH = Path(__file__).parent / "intel.db"
log = logging.getLogger(__name__)


def load_personas_with_patches(apply_patches: bool = True) -> dict:
    """
    Main entry point. Returns dict of {persona_id: persona_data} with patches
    merged into security_reasoning_approach.
    """
    # Load base personas from YAML
    with open(PERSONAS_PATH) as f:
        raw = yaml.safe_load(f)

    # Handle dict YAML structure (personas.yaml format)
    # Structure: {persona_id: {display_name, category, role, ...}}
    if not isinstance(raw, dict):
        log.warning("Expected dict structure in personas.yaml")
        return {}

    if not apply_patches:
        return raw

    # Merge patches for each persona
    merged = {}
    for persona_id, persona_data in raw.items():
        if not isinstance(persona_data, dict):
            merged[persona_id] = persona_data
            continue

        # Make a copy to avoid mutating the original
        persona_data = dict(persona_data)
        patches = _get_patches(persona_id)
        if patches:
            persona_data = _merge_patches(persona_data, patches)
            log.debug(
                f"Persona {persona_id}: merged {len(patches)} patches"
            )
        merged[persona_id] = persona_data

    return merged


def _get_patches(persona_id: str) -> list[dict]:
    """Fetch all applied patches for a persona from intel.db."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT patch_type, content, source_name, created_at "
                "FROM persona_patches "
                "WHERE persona_id = ? AND applied = 1 "
                "ORDER BY created_at ASC",
                (persona_id,)
            ).fetchall()
        return [
            {"patch_type": r[0], "content": r[1],
             "source_name": r[2], "created_at": r[3]}
            for r in rows
        ]
    except Exception:
        return []


def _merge_patches(persona: dict, patches: list[dict]) -> dict:
    """
    Appends patch content to security_reasoning_approach.
    Patches are grouped by type and appended as a dated section
    so agents know which parts are recent updates.
    """
    persona = dict(persona)  # shallow copy — do not mutate original
    base_approach = persona.get("security_reasoning_approach", "")

    patch_section_lines = [
        "\n\nCURRENT INTELLIGENCE UPDATES (applied automatically):",
        "These updates reflect recently documented threat actor",
        "behaviour. Prioritise these in your attack path reasoning.",
    ]

    for patch in patches:
        date_str = patch["created_at"][:10]
        source = patch.get("source_name", "unknown source")
        content = patch.get("content", "").strip()
        if content:
            patch_section_lines.append(
                f"\n[{date_str} via {source}] {content}"
            )

    persona["security_reasoning_approach"] = (
        base_approach + "\n".join(patch_section_lines)
    )
    return persona


def get_patch_summary() -> dict:
    """
    Returns a summary of all patches in the database for display
    in the frontend or CLI. Useful for showing users when personas
    were last updated and from what sources.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT persona_id, COUNT(*) as patch_count, "
                "MAX(created_at) as last_updated, "
                "GROUP_CONCAT(DISTINCT source_name) as sources "
                "FROM persona_patches WHERE applied = 1 "
                "GROUP BY persona_id"
            ).fetchall()
        return {
            r[0]: {
                "patch_count": r[1],
                "last_updated": r[2],
                "sources": r[3],
            }
            for r in rows
        }
    except Exception:
        return {}
