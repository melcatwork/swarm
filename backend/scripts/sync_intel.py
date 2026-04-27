#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import yaml

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.swarm.vuln_intel import run_sync
from backend.app.swarm.vuln_intel.exploit_adapters import (
    ExploitDBAdapter, NucleiTemplateAdapter
)
from backend.app.swarm.vuln_intel.threat_signal_ingestor import ThreatSignalIngestor
from backend.app.swarm.vuln_intel.persona_patch_generator import PersonaPatchGenerator
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

if __name__ == '__main__':
    force = '--force' in sys.argv
    print('Syncing threat intelligence...')
    run_sync(force=force)

    print('\nSyncing ExploitDB...')
    log.info("Syncing ExploitDB...")
    ExploitDBAdapter().sync()

    print('Syncing Nuclei template CVE index...')
    log.info("Syncing Nuclei template CVE index...")
    NucleiTemplateAdapter().sync()

    # Ingest threat intelligence signals
    print('\nIngesting threat intelligence signals...')
    log.info("Ingesting threat intelligence signals...")
    ingestor = ThreatSignalIngestor()
    ingestor.ingest_all()

    # Load current personas for patch evaluation context
    print('\nLoading personas for patch evaluation...')
    personas_path = Path(__file__).parent.parent / "app" / "swarm" / "agents" / "personas.yaml"
    with open(personas_path) as f:
        raw = yaml.safe_load(f)

    # personas.yaml structure: {persona_id: {display_name, role, security_reasoning_approach, ...}}
    personas_map = {}
    if isinstance(raw, dict):
        for persona_id, persona_data in raw.items():
            if isinstance(persona_data, dict):
                personas_map[persona_id] = persona_data.get("security_reasoning_approach", "")

    log.info(f"Loaded {len(personas_map)} personas for patch evaluation")

    # Generate patches from unprocessed signals
    # Check for Bedrock or Anthropic credentials
    bedrock_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if bedrock_token or anthropic_key:
        print('\nRunning persona patch generator...')
        log.info("Running persona patch generator...")

        # Auto-detect provider based on available credentials
        if bedrock_token:
            log.info("Using AWS Bedrock for patch generation")
            generator = PersonaPatchGenerator(
                llm_provider="bedrock",
                bedrock_token=bedrock_token,
                aws_region=os.getenv("AWS_REGION", "us-east-1")
            )
        else:
            log.info("Using Anthropic API for patch generation")
            generator = PersonaPatchGenerator(
                llm_provider="anthropic",
                anthropic_key=anthropic_key
            )

        generator.run(
            personas=personas_map,
            ingestor=ingestor,
            auto_accept=True,
            limit=100,  # Increased from 20 to 100 to process more signals per run
        )
    else:
        log.warning(
            "No LLM credentials found — skipping persona patch generation\n"
            "Set AWS_BEARER_TOKEN_BEDROCK or ANTHROPIC_API_KEY to enable"
        )

    print('Done.')
