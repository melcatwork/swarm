#!/usr/bin/env python3
"""Test signal extraction from capital-one-breach-replica.tf"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parsers.terraform_parser import TerraformParser
from app.swarm.iac_signal_extractor import IaCSignalExtractor

TF_FILE = Path('samples/capital-one-breach-replica.tf')

if not TF_FILE.exists():
    print(f"ERROR: {TF_FILE} not found")
    sys.exit(1)

# Parse the TF file
with open(TF_FILE, 'r') as f:
    content = f.read()

parser = TerraformParser()
asset_graph = parser.parse(content)
asset_graph_dict = asset_graph.model_dump()

print(f"Parsed {len(asset_graph_dict.get('assets', []))} assets")
print()

# Extract signals
extractor = IaCSignalExtractor()
signals = extractor.extract(asset_graph_dict)

print(f"="*70)
print(f"SIGNAL EXTRACTION RESULTS")
print(f"="*70)
print(f"Total signals detected: {len(signals)}\n")

if not signals:
    print("ERROR: No signals detected!")
    print("Expected signals:")
    print("  - IMDS_V1_ENABLED (HIGH) on aws_instance.waf_ec2")
    print("  - IAM_S3_WILDCARD (HIGH) on aws_iam_role_policy.waf_s3_policy")
    print("  - PUBLIC_INGRESS_OPEN (HIGH) on aws_security_group.waf_sg")
    print("  - UNRESTRICTED_EGRESS (MEDIUM) on aws_security_group.waf_sg")
    sys.exit(1)

# Group by severity
by_severity = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
for sig in signals:
    by_severity[sig.severity].append(sig)

for severity in ['HIGH', 'MEDIUM', 'LOW']:
    sigs = by_severity[severity]
    if sigs:
        print(f"\n{severity} Severity ({len(sigs)} signals):")
        print("-" * 70)
        for sig in sigs:
            print(f"  Signal ID: {sig.signal_id}")
            print(f"  Resource: {sig.resource_id} ({sig.resource_type})")
            print(f"  Detail: {sig.detail}")
            print()

# Check for expected signals
expected_signals = {
    'IMDS_V1_ENABLED': 'aws_instance.waf_ec2',
    'IAM_S3_WILDCARD': 'aws_iam_role_policy.waf_s3_policy',
    'PUBLIC_INGRESS_OPEN': 'aws_security_group.waf_sg',
    'UNRESTRICTED_EGRESS': 'aws_security_group.waf_sg',
}

print("="*70)
print("EXPECTED SIGNAL CHECK")
print("="*70)

all_found = True
for signal_id, expected_resource in expected_signals.items():
    found = any(s.signal_id == signal_id and expected_resource in s.resource_id
                for s in signals)
    status = "✓ FOUND" if found else "✗ MISSING"
    print(f"{status:12s} {signal_id:35s} on {expected_resource}")
    if not found:
        all_found = False

if all_found:
    print("\n✅ ALL EXPECTED SIGNALS DETECTED")
    sys.exit(0)
else:
    print("\n❌ SOME EXPECTED SIGNALS MISSING")
    sys.exit(1)
