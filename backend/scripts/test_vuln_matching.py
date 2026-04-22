#!/usr/bin/env python3
"""Test vulnerability matching from signals"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parsers.terraform_parser import TerraformParser
from app.swarm.iac_signal_extractor import IaCSignalExtractor
from app.swarm.vuln_intel.vuln_matcher import VulnMatcher

TF_FILE = Path('samples/capital-one-breach-replica.tf')

async def main():
    if not TF_FILE.exists():
        print(f"ERROR: {TF_FILE} not found")
        return 1

    # Parse the TF file
    with open(TF_FILE, 'r') as f:
        content = f.read()

    parser = TerraformParser()
    asset_graph = parser.parse(content)
    asset_graph_dict = asset_graph.model_dump()

    print(f"Parsed {len(asset_graph_dict.get('assets', []))} assets")

    # Extract signals
    extractor = IaCSignalExtractor()
    signals = extractor.extract(asset_graph_dict)
    print(f"Extracted {len(signals)} signals")
    print()

    # Match vulnerabilities
    matcher = VulnMatcher(nvd_api_key=None)
    matched_vulns = await matcher.match(
        asset_graph=asset_graph_dict,
        cloud_signals=signals,
        include_cve_lookup=False,  # Skip CVE lookup for speed
    )

    print(f"="*70)
    print(f"VULNERABILITY MATCHING RESULTS")
    print(f"="*70)
    print(f"Total matched vulnerabilities: {len(matched_vulns)}\n")

    if not matched_vulns:
        print("ERROR: No vulnerabilities matched!")
        print("Expected at least:")
        print("  - AWS-IMDS-001 on aws_instance.waf_ec2")
        print("  - AWS-IAM-001 or AWS-S3-003 on aws_iam_role_policy.waf_s3_policy")
        print("  - AWS-NET-002 on aws_security_group.waf_sg")
        print("  - AWS-NET-001 on aws_security_group.waf_sg")
        return 1

    # Group by confidence
    by_confidence = {'CONFIRMED': [], 'PROBABLE': [], 'POSSIBLE': []}
    for vuln in matched_vulns:
        by_confidence[vuln.match_confidence].append(vuln)

    for confidence in ['CONFIRMED', 'PROBABLE', 'POSSIBLE']:
        vulns = by_confidence[confidence]
        if vulns:
            print(f"\n{confidence} ({len(vulns)} vulns):")
            print("-" * 70)
            for vuln in vulns[:10]:  # Show first 10
                print(f"  Vuln ID: {vuln.vuln_id}")
                print(f"  Resource: {vuln.resource_id} ({vuln.resource_type})")
                print(f"  Technique: {vuln.technique_id}")
                print(f"  Phase: {vuln.kill_chain_phase}")
                print(f"  Risk Score: {vuln.risk_score:.1f}")
                print(f"  Reason: {vuln.match_reason[:80]}...")
                print()

    # Check for expected vulns
    print("="*70)
    print("EXPECTED VULNERABILITY CHECK")
    print("="*70)

    expected_vuln_patterns = [
        ('ATTCK-T1552-005', 'aws_instance.waf_ec2', 'IMDS metadata API'),
        ('ATTCK-T1530', 'aws_iam_role_policy.waf_s3_policy', 'S3 data access'),
        ('ATTCK-T1537', 'aws_iam_role_policy.waf_s3_policy', 'S3 data transfer'),
        ('ATTCK-T1190', 'aws_security_group.waf_sg', 'Public ingress'),
        ('ATTCK-T1041', 'aws_security_group.waf_sg', 'Unrestricted egress'),
    ]

    found_count = 0
    for vuln_id, resource_pattern, description in expected_vuln_patterns:
        found = any(
            v.vuln_id == vuln_id and resource_pattern in v.resource_id
            for v in matched_vulns
        )
        status = "✓ FOUND" if found else "✗ MISSING"
        print(f"{status:12s} {vuln_id:15s} ({description})")
        if found:
            found_count += 1

    print()
    if found_count >= 3:  # At least 3 out of 5 expected patterns
        print(f"✅ {found_count}/5 EXPECTED VULNERABILITIES MATCHED")
        return 0
    else:
        print(f"❌ ONLY {found_count}/5 EXPECTED VULNERABILITIES MATCHED")
        return 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
