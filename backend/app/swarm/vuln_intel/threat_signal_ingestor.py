"""
threat_signal_ingestor.py

Ingests structured threat actor intelligence from public sources
into the threat_intel_signals table. Called from sync_intel.py.
Sources used are all free and public — no API keys required beyond
what the project already uses.
"""

import sqlite3
import httpx
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "intel.db"
log = logging.getLogger(__name__)

PERSONA_ACTOR_MAP = {
    "apt29_cozy_bear":       ["APT29", "Cozy Bear", "NOBELIUM", "Midnight Blizzard"],
    "lazarus_group":         ["Lazarus", "HIDDEN COBRA", "Lazarus Group"],
    "volt_typhoon":          ["Volt Typhoon", "BRONZE SILHOUETTE"],
    "fin7":                  ["FIN7", "Carbanak", "ELBRUS"],
    "scattered_spider":      ["Scattered Spider", "UNC3944", "0ktapus"],
    "ransomware_operator":   ["LockBit", "BlackCat", "ALPHV", "DarkSide",
                               "RansomHub", "Cl0p"],
    "supply_chain_attacker": ["supply chain", "dependency confusion",
                               "software supply chain"],
    "insider_threat":        ["insider", "insider threat"],
    "cryptominer":           ["cryptominer", "LLMjacking", "resource hijacking"],
    "cloud_native_attacker": ["cloud-native", "cloud attacker", "LLMjacking",
                               "cloud intrusion"],
    "nation_state_apt":      ["nation-state", "APT", "espionage"],
    "opportunistic_attacker":["opportunistic", "script kiddie", "mass exploitation"],
}


class ThreatSignalIngestor:

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_intel_signals (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_type     TEXT,
                    actor_name      TEXT,
                    title           TEXT,
                    description     TEXT,
                    source_name     TEXT,
                    source_url      TEXT,
                    published_date  TEXT,
                    raw_content     TEXT,
                    processed       INTEGER DEFAULT 0,
                    ingested_at     TEXT DEFAULT (datetime('now'))
                )
            """)

    def ingest_all(self):
        """Run all ingestors. Called from sync_intel.py."""
        log.info("Ingesting threat intelligence signals...")
        self._ingest_cisa_advisories()
        self._ingest_attck_group_updates()
        self._ingest_cisa_kev_actor_context()
        log.info("Threat signal ingestion complete.")

    def _ingest_cisa_advisories(self):
        """
        Pulls CISA advisories from their JSON feed.
        Free, no auth required.
        URL: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
        Also pulls AA (Alert Advisory) feed where available.
        """
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        try:
            resp = httpx.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            vulns = data.get("vulnerabilities", [])
            # Only process entries from last 90 days
            cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            new_signals = []
            for v in vulns:
                date_added = v.get("dateAdded", "")
                if date_added < cutoff:
                    continue
                notes = v.get("notes", "") or ""
                vendor = v.get("vendorProject", "")
                product = v.get("product", "")
                actor_name = self._detect_actor(notes + " " + vendor)
                new_signals.append((
                    "kev_entry",
                    actor_name,
                    f"KEV: {v.get('vulnerabilityName', '')}",
                    f"{vendor} {product}: {v.get('shortDescription', '')} "
                    f"Required action: {v.get('requiredAction', '')}",
                    "CISA KEV",
                    "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
                    date_added,
                    json.dumps(v),
                ))
            if new_signals:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.executemany(
                        "INSERT OR IGNORE INTO threat_intel_signals "
                        "(signal_type, actor_name, title, description, "
                        "source_name, source_url, published_date, raw_content) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        new_signals
                    )
                log.info(f"CISA advisories: ingested {len(new_signals)} new signals")
        except Exception as e:
            log.error(f"CISA advisory ingest failed: {e}")

    def _ingest_attck_group_updates(self):
        """
        Pulls ATT&CK STIX group data to detect new techniques
        attributed to tracked actors. Uses the existing ATT&CK
        STIX bundle that may already be in intel.db or re-fetches.
        """
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        try:
            resp = httpx.get(url, timeout=60)
            resp.raise_for_status()
            bundle = resp.json()
            objects = bundle.get("objects", [])

            # Build technique lookup
            techniques = {
                o["id"]: o for o in objects
                if o.get("type") == "attack-pattern"
            }

            # Build group → technique relationships
            groups = {
                o["id"]: o for o in objects
                if o.get("type") == "intrusion-set"
            }
            relationships = [
                o for o in objects
                if o.get("type") == "relationship"
                and o.get("relationship_type") == "uses"
            ]

            signals = []
            for rel in relationships:
                src = rel.get("source_ref", "")
                tgt = rel.get("target_ref", "")
                if src not in groups or tgt not in techniques:
                    continue
                group = groups[src]
                technique = techniques[tgt]
                group_name = group.get("name", "")
                persona_id = self._detect_actor(group_name)
                if not persona_id:
                    continue
                tech_name = technique.get("name", "")
                tech_id = next(
                    (r.get("external_id") for r in
                     technique.get("external_references", [])
                     if r.get("source_name") == "mitre-attack"),
                    ""
                )
                # Only cloud-relevant techniques
                platforms = technique.get("x_mitre_platforms", [])
                if not any(p in platforms for p in
                           ["AWS", "Azure", "GCP", "IaaS", "SaaS"]):
                    continue
                signals.append((
                    "attck_technique",
                    persona_id,
                    f"ATT&CK: {group_name} uses {tech_id} {tech_name}",
                    technique.get("description", "")[:500],
                    "MITRE ATT&CK",
                    f"https://attack.mitre.org/techniques/{tech_id}/",
                    rel.get("modified", "")[:10],
                    json.dumps({"group": group_name, "technique_id": tech_id,
                                "technique_name": tech_name}),
                ))

            if signals:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.executemany(
                        "INSERT OR IGNORE INTO threat_intel_signals "
                        "(signal_type, actor_name, title, description, "
                        "source_name, source_url, published_date, raw_content) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        signals
                    )
                log.info(f"ATT&CK: ingested {len(signals)} cloud-relevant group signals")
        except Exception as e:
            log.error(f"ATT&CK group ingest failed: {e}")

    def _ingest_cisa_kev_actor_context(self):
        """
        Reads the ransomware campaign data from CISA's
        StopRansomware feed to extract actor-specific context.
        URL: https://www.cisa.gov/sites/default/files/2024-07/StopRansomware-Guide-508c.pdf
        Uses the JSON structured version where available.
        """
        url = "https://raw.githubusercontent.com/cisagov/stopransomware/main/data/advisories.json"
        try:
            resp = httpx.get(url, timeout=30)
            if resp.status_code != 200:
                return
            advisories = resp.json()
            signals = []
            for adv in advisories:
                actor = adv.get("actor", "") or ""
                title = adv.get("title", "") or ""
                description = adv.get("description", "") or ""
                persona_id = self._detect_actor(actor + " " + title)
                if not persona_id:
                    continue
                signals.append((
                    "ransomware_advisory",
                    persona_id,
                    title,
                    description[:500],
                    "CISA StopRansomware",
                    adv.get("url", ""),
                    adv.get("date", ""),
                    json.dumps(adv),
                ))
            if signals:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.executemany(
                        "INSERT OR IGNORE INTO threat_intel_signals "
                        "(signal_type, actor_name, title, description, "
                        "source_name, source_url, published_date, raw_content) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        signals
                    )
                log.info(f"CISA StopRansomware: ingested {len(signals)} signals")
        except Exception as e:
            log.warning(f"CISA StopRansomware ingest skipped: {e}")

    def _detect_actor(self, text: str) -> str:
        """
        Returns the persona_id most likely associated with the
        given text based on actor name matching. Returns empty
        string if no match.
        """
        if not text:
            return ""
        text_lower = text.lower()
        for persona_id, aliases in PERSONA_ACTOR_MAP.items():
            for alias in aliases:
                if alias.lower() in text_lower:
                    return persona_id
        return ""

    def get_unprocessed_signals(
        self, persona_id: str = None, limit: int = 50
    ) -> list[dict]:
        """
        Fetch signals not yet processed into patches.

        Prioritizes cloud-relevant signals (those with actor_name set)
        to ensure persona patches are generated from relevant intelligence first.
        """
        with sqlite3.connect(DB_PATH) as conn:
            if persona_id:
                rows = conn.execute(
                    "SELECT id, signal_type, actor_name, title, "
                    "description, source_name, source_url, published_date "
                    "FROM threat_intel_signals "
                    "WHERE processed = 0 AND actor_name = ? "
                    "ORDER BY ingested_at DESC LIMIT ?",
                    (persona_id, limit)
                ).fetchall()
            else:
                # Prioritize signals with actor_name (cloud-relevant)
                # then process generic KEV entries
                rows = conn.execute(
                    "SELECT id, signal_type, actor_name, title, "
                    "description, source_name, source_url, published_date "
                    "FROM threat_intel_signals "
                    "WHERE processed = 0 "
                    "ORDER BY "
                    "CASE WHEN actor_name IS NOT NULL AND actor_name != '' THEN 0 ELSE 1 END, "
                    "ingested_at DESC "
                    "LIMIT ?",
                    (limit,)
                ).fetchall()
        cols = ["id", "signal_type", "actor_name", "title",
                "description", "source_name", "source_url", "published_date"]
        return [dict(zip(cols, r)) for r in rows]

    def mark_processed(self, signal_ids: list[int]):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                f"UPDATE threat_intel_signals SET processed = 1 "
                f"WHERE id IN ({','.join('?' * len(signal_ids))})",
                signal_ids
            )
