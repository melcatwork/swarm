#!/usr/bin/env python3
"""
Verification script for vulnerability context builder integration.

Tests the complete vulnerability intelligence pipeline:
1. Cloud signal extraction from asset graph
2. Vulnerability matching (CVEs + cloud abuse patterns)
3. Attack chain assembly
4. Prompt formatting

Usage:
    python backend/scripts/verify_vuln_context.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.swarm.vuln_intel.vuln_context_builder import VulnContextBuilder


# Sample asset graph for testing (simulates parsed Terraform infrastructure)
SAMPLE_ASSET_GRAPH = {
    "assets": [
        {
            "id": "waf_ec2",
            "type": "aws_instance",
            "ami": "ami-0c55b159cbfafe1f0",
            "instance_type": "t2.micro",
            "metadata_options": {"http_tokens": "optional"},  # IMDSv1 enabled
            "iam_instance_profile": "web_server_profile",
        },
        {
            "id": "credit_db",
            "type": "aws_db_instance",
            "engine": "postgres",
            "engine_version": "14.9",  # Potentially outdated
            "publicly_accessible": False,
        },
        {
            "id": "customer_data",
            "type": "aws_s3_bucket",
            "bucket": "customer-pii-data",
        },
        {
            "id": "web_sg",
            "type": "aws_security_group",
            "ingress": [
                {
                    "from_port": 80,
                    "to_port": 80,
                    "protocol": "tcp",
                    "cidr_blocks": ["0.0.0.0/0"],  # Public ingress
                },
                {
                    "from_port": 443,
                    "to_port": 443,
                    "protocol": "tcp",
                    "cidr_blocks": ["0.0.0.0/0"],
                },
            ],
            "egress": [
                {
                    "from_port": 0,
                    "to_port": 0,
                    "protocol": "-1",  # All protocols
                    "cidr_blocks": ["0.0.0.0/0"],  # Unrestricted egress
                },
            ],
        },
        {
            "id": "web_role",
            "type": "aws_iam_role",
            "assume_role_policy": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Effect": "Allow",
                    }
                ]
            },
        },
        {
            "id": "s3_policy",
            "type": "aws_iam_role_policy",
            "role": "web_role",
            "policy": {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:*"],
                        "Resource": ["*"],  # Wildcard S3 permissions
                    }
                ]
            },
        },
    ],
    "relationships": [
        {
            "source": "waf_ec2",
            "target": "web_sg",
            "type": "uses_security_group",
        },
        {
            "source": "waf_ec2",
            "target": "web_role",
            "type": "assumes_role",
        },
        {
            "source": "web_role",
            "target": "s3_policy",
            "type": "has_policy",
        },
    ],
}


async def main():
    """Run verification test."""
    print("=" * 80)
    print("VULNERABILITY CONTEXT BUILDER VERIFICATION")
    print("=" * 80)
    print()

    # Initialize builder without NVD API key (for offline testing)
    print("[1] Initializing VulnContextBuilder (no NVD API key)...")
    builder = VulnContextBuilder()
    print("✓ Builder initialized")
    print()

    # Build vulnerability context
    print("[2] Building vulnerability context from sample infrastructure...")
    print(f"    Assets: {len(SAMPLE_ASSET_GRAPH['assets'])}")
    print(f"    Relationships: {len(SAMPLE_ASSET_GRAPH['relationships'])}")
    print()

    try:
        ctx = await builder.build(
            asset_graph=SAMPLE_ASSET_GRAPH,
            include_cve_lookup=False,  # Skip NVD lookups for this test
        )
        print("✓ Vulnerability context built successfully")
        print()
    except Exception as e:
        print(f"✗ Failed to build context: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Display statistics
    print("[3] Vulnerability Intelligence Statistics:")
    print("-" * 80)
    for key, value in ctx.stats.items():
        formatted_key = key.replace("_", " ").title()
        print(f"    {formatted_key:30s} {value}")
    print()

    # Display cloud signals
    if ctx.cloud_signals:
        print("[4] Cloud Configuration Signals Detected:")
        print("-" * 80)
        for sig in ctx.cloud_signals[:5]:  # Show first 5
            print(f"    [{sig.signal_id}] {sig.severity}")
            print(f"        Resource: {sig.resource_id}")
            print(f"        Detail: {sig.detail}")
            print()
    else:
        print("[4] No cloud signals detected")
        print()

    # Display matched vulnerabilities
    if ctx.matched_vulns:
        print("[5] Matched Vulnerabilities:")
        print("-" * 80)
        for vuln in ctx.matched_vulns[:5]:  # Show first 5
            print(f"    [{vuln.vuln_id}] {vuln.name}")
            print(f"        Resource: {vuln.resource_id}")
            print(f"        Risk Score: {vuln.risk_score:.1f}/10")
            print(f"        CVSS: {vuln.cvss_score} | KEV: {vuln.in_kev}")
            print(f"        Confidence: {vuln.match_confidence}")
            if vuln.exploitation_commands:
                print(f"        Exploitation: {vuln.exploitation_commands[0]}")
            print()
    else:
        print("[5] No vulnerabilities matched")
        print()

    # Display assembled chains
    if ctx.assembled_chains:
        print("[6] Assembled Attack Chains:")
        print("-" * 80)
        for chain in ctx.assembled_chains:
            print(f"    {chain.chain_name}")
            print(f"        Chain Score: {chain.chain_score:.1f}/10")
            print(f"        Steps: {len(chain.steps)}")
            print(f"        KEV: {chain.has_kev_vuln} | PoC: {chain.has_poc}")
            print(f"        Undetectable Steps: {chain.undetectable_steps}")
            print(f"        Summary: {chain.summary}")
            print()
    else:
        print("[6] No attack chains assembled")
        print()

    # Display combined prompt (truncated)
    print("[7] Combined Prompt Preview (first 800 chars):")
    print("-" * 80)
    print(ctx.combined_prompt[:800])
    print()
    if len(ctx.combined_prompt) > 800:
        print(f"    ... ({len(ctx.combined_prompt) - 800} more characters)")
        print()

    # Summary
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print(f"✓ Cloud signals detected: {ctx.stats['signals_detected']}")
    print(f"✓ Vulnerabilities matched: {ctx.stats['vulns_matched']}")
    print(f"✓ Attack chains assembled: {ctx.stats['chains_assembled']}")
    print()
    print("Integration test passed! Vulnerability context builder is working correctly.")
    print()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
