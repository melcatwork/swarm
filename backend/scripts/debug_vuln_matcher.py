#!/usr/bin/env python3
"""Debug vulnerability matching"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parsers.terraform_parser import TerraformParser
from app.swarm.iac_signal_extractor import IaCSignalExtractor
from app.swarm.vuln_intel.vuln_matcher import VulnMatcher
from app.swarm.vuln_intel.abuse_kb_loader import AbuseKBLoader

TF_FILE = Path('samples/capital-one-breach-replica.tf')

async def main():
    # Parse and extract signals
    with open(TF_FILE, 'r') as f:
        content = f.read()

    parser = TerraformParser()
    asset_graph = parser.parse(content)
    asset_graph_dict = asset_graph.model_dump()

    extractor = IaCSignalExtractor()
    signals = extractor.extract(asset_graph_dict)

    print(f"Extracted {len(signals)} signals:")
    for sig in signals[:5]:
        print(f"  {sig.signal_id:30s} on {sig.resource_id}")
    print()

    # Check abuse KB
    loader = AbuseKBLoader()
    print("Checking abuse KB for expected IDs...")

    # Hardcoded mapping from VulnMatcher
    SIGNAL_TO_ABUSE = {
        'IMDS_V1_ENABLED': ['AWS-IMDS-001'],
        'IAM_S3_WILDCARD': ['AWS-IAM-001', 'AWS-S3-003'],
        'IAM_PRIVILEGE_ESCALATION_ACTIONS': ['AWS-IAM-002', 'AWS-IAM-003', 'AWS-IAM-004'],
        'CLOUDTRAIL_NO_S3_DATA_EVENTS': ['AWS-CT-001'],
        'SHARED_IAM_INSTANCE_PROFILE': ['AWS-IAM-006'],
        'S3_NO_RESOURCE_POLICY': ['AWS-S3-001'],
        'PUBLIC_INGRESS_OPEN': ['AWS-NET-002'],
        'UNRESTRICTED_EGRESS': ['AWS-NET-001'],
    }

    for signal_id, abuse_ids in SIGNAL_TO_ABUSE.items():
        print(f"\nSignal: {signal_id}")
        for abuse_id in abuse_ids:
            abuse = loader.get_abuse_by_id(abuse_id)
            if abuse:
                print(f"  ✓ {abuse_id:20s} found in DB: {abuse.get('name', 'N/A')[:50]}")
            else:
                print(f"  ✗ {abuse_id:20s} NOT FOUND IN DB")

    # Check what IDs are actually in the DB
    print("\n" + "="*70)
    print("Abuse patterns in DB (first 20):")
    all_abuses = loader.get_all()
    for abuse in all_abuses[:20]:
        if isinstance(abuse, dict):
            abuse_id = abuse.get('abuse_id', '?')
            name = abuse.get('name', '?')
        else:
            abuse_id = getattr(abuse, 'abuse_id', '?')
            name = getattr(abuse, 'name', '?')
        print(f"  {abuse_id:20s} {name[:50]}")

if __name__ == '__main__':
    asyncio.run(main())
