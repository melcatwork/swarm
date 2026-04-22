#!/usr/bin/env python3
"""Debug script to inspect asset_graph structure after parsing."""
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parsers.terraform_parser import TerraformParser

TF_FILE = Path('samples/capital-one-breach-replica.tf')

if not TF_FILE.exists():
    print(f"ERROR: {TF_FILE} not found")
    sys.exit(1)

# Parse the TF file
with open(TF_FILE, 'r') as f:
    content = f.read()

parser = TerraformParser()
asset_graph = parser.parse(content)

# Convert to dict
asset_graph_dict = asset_graph.model_dump()

print(f"Assets: {len(asset_graph_dict.get('assets', []))}")
print(f"Relationships: {len(asset_graph_dict.get('relationships', []))}")
print()

# Show all assets
print(f"\nAll {len(asset_graph_dict.get('assets', []))} assets:")
for asset in asset_graph_dict.get('assets', []):
    aid = asset.get('id')
    atype = asset.get('type')
    props = asset.get('properties', {})
    resource_type = props.get('resource_type', 'unknown')
    print(f"  {aid:50s} type={atype:25s} resource_type={resource_type}")

# Check for expected misconfigurations
print("\n" + "="*60)
print("Checking for expected misconfigurations:")
print("="*60)

# Check for IMDSv1
instances = [a for a in asset_graph_dict.get('assets', [])
             if a.get('properties', {}).get('resource_type') == 'aws_instance']
for inst in instances:
    props = inst.get('properties', {})
    metadata_opts_raw = props.get('metadata_options')
    print(f"\nEC2 Instance: {inst.get('id')}")
    print(f"  Properties keys: {list(props.keys())}")
    print(f"  metadata_options type: {type(metadata_opts_raw)}")
    print(f"  metadata_options raw: {metadata_opts_raw}")

    # Handle both list and dict formats
    if isinstance(metadata_opts_raw, list) and metadata_opts_raw:
        metadata_opts = metadata_opts_raw[0]
    elif isinstance(metadata_opts_raw, dict):
        metadata_opts = metadata_opts_raw
    else:
        metadata_opts = {}

    http_tokens = metadata_opts.get('http_tokens') if isinstance(metadata_opts, dict) else None
    print(f"  http_tokens: {http_tokens}")
    print(f"  IMDSv1 enabled: {http_tokens == 'optional'}")

# Check for wildcard IAM
iam_policies = [a for a in asset_graph_dict.get('assets', [])
                if a.get('properties', {}).get('resource_type') in ['aws_iam_role_policy', 'aws_iam_policy']]
for policy in iam_policies:
    props = policy.get('properties', {})
    policy_doc = props.get('policy')
    print(f"\nIAM Policy: {policy.get('id')}")
    print(f"  Properties keys: {list(props.keys())}")
    print(f"  Has policy document: {policy_doc is not None}")
    if policy_doc:
        print(f"  Policy type: {type(policy_doc)}")
        print(f"  Policy value (first 200 chars): {str(policy_doc)[:200]}")

        # Try to parse if string
        if isinstance(policy_doc, str):
            try:
                import json
                policy_doc = json.loads(policy_doc)
                print(f"  Successfully parsed JSON policy")
            except:
                print(f"  Failed to parse as JSON")

        if isinstance(policy_doc, dict):
            statements = policy_doc.get('Statement', [])
            print(f"  Statements: {len(statements)}")
            for stmt in statements[:2]:
                print(f"    Actions: {stmt.get('Action')}")
                print(f"    Resources: {stmt.get('Resource')}")

# Check for security groups
sgs = [a for a in asset_graph_dict.get('assets', [])
       if a.get('properties', {}).get('resource_type') == 'aws_security_group']
for sg in sgs:
    props = sg.get('properties', {})
    ingress = props.get('ingress', [])
    egress = props.get('egress', [])
    print(f"\nSecurity Group: {sg.get('id')}")
    print(f"  Properties keys: {list(props.keys())}")
    print(f"  Ingress rules: {len(ingress)}")
    print(f"  Egress rules: {len(egress)}")
    for rule in ingress:
        cidr_blocks = rule.get('cidr_blocks', [])
        if '0.0.0.0/0' in cidr_blocks:
            print(f"    PUBLIC INGRESS port {rule.get('from_port')}: {cidr_blocks}")
    for rule in egress:
        cidr_blocks = rule.get('cidr_blocks', [])
        protocol = rule.get('protocol')
        if '0.0.0.0/0' in cidr_blocks and protocol == '-1':
            print(f"    UNRESTRICTED EGRESS: protocol={protocol}, cidr={cidr_blocks}")
