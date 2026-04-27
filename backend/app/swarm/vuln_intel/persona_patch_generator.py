"""
persona_patch_generator.py

Reads unprocessed threat_intel_signals and uses Claude to determine
whether each signal warrants a patch to one or more personas.
Writes accepted patches to the persona_patches table.
Designed to run after each intel sync — lightweight, idempotent.
"""

import sqlite3
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from crewai import LLM

DB_PATH = Path(__file__).parent / "intel.db"
log = logging.getLogger(__name__)

PATCH_GENERATOR_SYSTEM_PROMPT = """
You are a threat intelligence analyst specialising in cloud security
and adversary emulation. Your job is to read raw threat intelligence
signals and determine whether they represent a meaningful update to
how a specific threat actor persona should reason about cloud attacks.

You will be given:
1. A threat intelligence signal (new CVE, new technique, new report)
2. The current security_reasoning_approach for the relevant persona

You must decide:
- Does this signal change how the persona should behave?
- If yes: write a concise structured patch

A patch is warranted when the signal represents:
- A genuinely new technique or procedure used by this actor
- A newly discovered cloud-specific attack method
- A significant shift in the actor's targeting or objectives
- A newly confirmed exploitation of a specific cloud service

A patch is NOT warranted when:
- The signal is already covered by the existing persona
- The signal is minor or duplicative
- The signal is not relevant to cloud/AWS environments
- The signal is about a different actor than the persona

Respond ONLY with valid JSON in this exact format:
{
  "patch_warranted": true or false,
  "rationale": "one sentence explaining your decision",
  "patch_type": "new_ttp | updated_ttp | new_cloud_procedure | new_target_sector | deprecated_ttp | new_tool",
  "patch_content": "the text to append to security_reasoning_approach — write in the same style as the existing approach, 2-5 sentences maximum, starting with the ATT&CK technique ID where applicable",
  "confidence": "high | medium | low"
}

If patch_warranted is false, set patch_content to null.
Do not include any text outside the JSON object.
"""


class PersonaPatchGenerator:

    def __init__(self, llm_provider: str = None, bedrock_token: str = None,
                 anthropic_key: str = None, aws_region: str = "us-east-1"):
        """
        Initialize patch generator with LLM configuration.

        Args:
            llm_provider: "bedrock" or "anthropic" (auto-detected if None)
            bedrock_token: AWS bearer token for Bedrock (optional)
            anthropic_key: Anthropic API key (optional)
            aws_region: AWS region for Bedrock (default: us-east-1)
        """
        # Auto-detect provider if not specified
        if llm_provider is None:
            if bedrock_token or os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
                llm_provider = "bedrock"
            elif anthropic_key or os.getenv("ANTHROPIC_API_KEY"):
                llm_provider = "anthropic"
            else:
                raise ValueError(
                    "No LLM credentials found. Set AWS_BEARER_TOKEN_BEDROCK "
                    "or ANTHROPIC_API_KEY environment variable."
                )

        self.llm_provider = llm_provider
        self.bedrock_token = bedrock_token or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        self.anthropic_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
        self.aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")

        # Initialize LLM based on provider
        self.llm = self._get_llm()
        self._ensure_patch_table()

        log.info(f"PersonaPatchGenerator initialized with {llm_provider} provider")

    def _get_llm(self) -> LLM:
        """Get configured LLM instance for patch generation."""
        if self.llm_provider == "bedrock":
            if not self.bedrock_token:
                raise ValueError("AWS_BEARER_TOKEN_BEDROCK required for Bedrock")

            # Set environment variables for Bedrock
            os.environ["AWS_BEARER_TOKEN_BEDROCK"] = self.bedrock_token
            os.environ["AWS_REGION_NAME"] = self.aws_region
            os.environ["AWS_DEFAULT_REGION"] = self.aws_region
            os.environ["AWS_REGION"] = self.aws_region

            # Use Claude 3 Sonnet on Bedrock (stable, widely available)
            # This is the most reliable model version available
            # Alternative: anthropic.claude-3-opus-20240229-v1:0 (more capable but slower/costlier)
            model = "bedrock/anthropic.claude-3-sonnet-20240229-v1:0"
            log.info(f"Using Bedrock model: {model}, region: {self.aws_region}")

            return LLM(
                model=model,
                temperature=0.3,  # Lower temperature for more consistent evaluation
                max_tokens=1024,
            )
        else:  # anthropic
            if not self.anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY required for Anthropic API")

            os.environ["ANTHROPIC_API_KEY"] = self.anthropic_key

            model = "anthropic/claude-sonnet-4-20250514"
            log.info(f"Using Anthropic API model: {model}")

            return LLM(
                model=model,
                temperature=0.3,
                max_tokens=1024,
            )

    def _ensure_patch_table(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persona_patches (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id      TEXT NOT NULL,
                    patch_type      TEXT NOT NULL,
                    content         TEXT NOT NULL,
                    source_name     TEXT,
                    source_url      TEXT,
                    rationale       TEXT,
                    confidence      TEXT,
                    signal_id       INTEGER,
                    created_at      TEXT DEFAULT (datetime('now')),
                    review_status   TEXT DEFAULT 'auto_accepted',
                    applied         INTEGER DEFAULT 1
                )
            """)

    def run(
        self,
        personas: dict,
        ingestor,
        auto_accept: bool = True,
        limit: int = 20
    ):
        """
        Main entry point. Reads unprocessed signals, runs LLM
        evaluation for each, and writes accepted patches.

        personas: dict of persona_id → current security_reasoning_approach
        ingestor: ThreatSignalIngestor instance
        auto_accept: if True, patches are applied without human review
        limit: max signals to process per run
        """
        signals = ingestor.get_unprocessed_signals(limit=limit)
        if not signals:
            log.info("PersonaPatchGenerator: no unprocessed signals")
            return

        log.info(f"PersonaPatchGenerator: evaluating {len(signals)} signals")
        processed_ids = []
        patches_written = 0

        for signal in signals:
            persona_id = signal.get("actor_name")
            if not persona_id or persona_id not in personas:
                processed_ids.append(signal["id"])
                continue

            current_approach = personas[persona_id]
            patch = self._evaluate_signal(signal, current_approach)

            if patch and patch.get("patch_warranted"):
                self._write_patch(
                    persona_id=persona_id,
                    patch=patch,
                    signal=signal,
                    auto_accept=auto_accept,
                )
                patches_written += 1

            processed_ids.append(signal["id"])

        if processed_ids:
            ingestor.mark_processed(processed_ids)

        log.info(
            f"PersonaPatchGenerator: processed {len(processed_ids)} signals, "
            f"wrote {patches_written} patches"
        )

    def _evaluate_signal(
        self, signal: dict, current_approach: str
    ) -> dict | None:
        """
        Calls Claude to evaluate whether the signal warrants a patch.
        Returns the parsed JSON response or None on failure.
        """
        user_message = f"""
THREAT INTELLIGENCE SIGNAL:
  Type: {signal.get('signal_type')}
  Title: {signal.get('title')}
  Description: {signal.get('description')}
  Source: {signal.get('source_name')} — {signal.get('source_url')}
  Published: {signal.get('published_date')}

CURRENT PERSONA REASONING APPROACH:
{current_approach[:1500]}

Evaluate whether this signal warrants a patch to this persona.
Respond with valid JSON only.
"""
        try:
            # Use CrewAI LLM instance with system prompt + user message
            full_prompt = f"{PATCH_GENERATOR_SYSTEM_PROMPT}\n\n{user_message}"
            response = self.llm.call([{"role": "user", "content": full_prompt}])

            # Extract text from response
            if isinstance(response, dict) and "choices" in response:
                content = response["choices"][0]["message"]["content"]
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)

            # Clean up markdown code fences if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse JSON
            return json.loads(content)
        except json.JSONDecodeError as e:
            log.warning(f"Patch generator JSON parse error: {e}")
            log.debug(f"Raw response: {content[:200] if 'content' in locals() else 'N/A'}")
            return None
        except Exception as e:
            log.error(f"Patch generator LLM call failed: {e}")
            return None

    def _write_patch(
        self,
        persona_id: str,
        patch: dict,
        signal: dict,
        auto_accept: bool,
    ):
        review_status = "auto_accepted" if auto_accept else "pending"
        applied = 1 if auto_accept else 0
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO persona_patches "
                "(persona_id, patch_type, content, source_name, source_url, "
                "rationale, confidence, signal_id, review_status, applied) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    persona_id,
                    patch.get("patch_type", "new_ttp"),
                    patch.get("patch_content", ""),
                    signal.get("source_name"),
                    signal.get("source_url"),
                    patch.get("rationale"),
                    patch.get("confidence"),
                    signal.get("id"),
                    review_status,
                    applied,
                )
            )
        log.info(
            f"Patch written: {persona_id} | {patch.get('patch_type')} | "
            f"confidence={patch.get('confidence')} | "
            f"status={review_status}"
        )

    def get_patches_for_persona(
        self, persona_id: str, applied_only: bool = True
    ) -> list[dict]:
        """
        Returns all patches for a given persona.
        Called by the persona loader at scan time.
        """
        with sqlite3.connect(DB_PATH) as conn:
            query = (
                "SELECT patch_type, content, source_name, source_url, "
                "rationale, confidence, created_at "
                "FROM persona_patches WHERE persona_id = ?"
            )
            params = [persona_id]
            if applied_only:
                query += " AND applied = 1"
            query += " ORDER BY created_at ASC"
            rows = conn.execute(query, params).fetchall()
        cols = ["patch_type", "content", "source_name", "source_url",
                "rationale", "confidence", "created_at"]
        return [dict(zip(cols, r)) for r in rows]
