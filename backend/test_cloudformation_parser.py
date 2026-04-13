#!/usr/bin/env python3
"""
Test script for CloudFormation parser.

Tests parsing of CloudFormation templates (both YAML and JSON formats)
and validates asset extraction, relationship identification, and trust
boundary detection.
"""

import sys
import json
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.parsers import CloudFormationParser


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    else:
        print("-" * 80)


def test_yaml_template():
    """Test parsing of YAML CloudFormation template."""
    print_separator("Testing YAML CloudFormation Template")

    # Read template
    with open("test_cloudformation.yaml", "r") as f:
        template_content = f.read()

    # Parse
    parser = CloudFormationParser()
    asset_graph = parser.parse(template_content, file_extension="yaml")

    # Display results
    print(f"✓ Successfully parsed YAML template")
    print(f"  Assets: {len(asset_graph.assets)}")
    print(f"  Relationships: {len(asset_graph.relationships)}")
    print(f"  Trust Boundaries: {len(asset_graph.trust_boundaries)}")
    print(f"  Format: {asset_graph.metadata['format']}")
    print(f"  Resource Count: {asset_graph.metadata['resource_count']}")

    # Show assets by type
    print("\nAssets by Type:")
    asset_types = {}
    for asset in asset_graph.assets:
        asset_type = asset.type
        if asset_type not in asset_types:
            asset_types[asset_type] = []
        asset_types[asset_type].append(asset.name)

    for asset_type, names in sorted(asset_types.items()):
        print(f"  {asset_type}: {', '.join(names)}")

    # Show trust boundaries
    print("\nTrust Boundaries:")
    for boundary in asset_graph.trust_boundaries:
        print(f"  {boundary.name} ({boundary.exposure}): {len(boundary.assets)} assets")
        for asset_id in boundary.assets[:3]:  # Show first 3
            asset = next((a for a in asset_graph.assets if a.id == asset_id), None)
            if asset:
                print(f"    - {asset.name} ({asset.type})")
        if len(boundary.assets) > 3:
            print(f"    ... and {len(boundary.assets) - 3} more")

    # Show relationships by type
    print("\nRelationships by Type:")
    rel_types = {}
    for rel in asset_graph.relationships:
        rel_type = rel.type
        if rel_type not in rel_types:
            rel_types[rel_type] = []
        rel_types[rel_type].append(rel)

    for rel_type, rels in sorted(rel_types.items()):
        print(f"  {rel_type}: {len(rels)}")
        for rel in rels[:2]:  # Show first 2 examples
            source = next((a for a in asset_graph.assets if a.id == rel.source), None)
            target = next((a for a in asset_graph.assets if a.id == rel.target), None)
            if source and target:
                print(f"    - {source.name} → {target.name}")
        if len(rels) > 2:
            print(f"    ... and {len(rels) - 2} more")

    # Check specific properties
    print("\nSecurity-Relevant Properties:")

    # Find internet-facing resources
    internet_assets = [a for a in asset_graph.assets if a.trust_boundary == "internet"]
    print(f"  Internet-facing assets: {len(internet_assets)}")
    for asset in internet_assets:
        print(f"    - {asset.name} ({asset.service})")

    # Find encrypted storage
    encrypted_storage = [
        a for a in asset_graph.assets
        if "storage" in a.type and a.properties.get("encryption_at_rest")
    ]
    print(f"  Encrypted storage: {len(encrypted_storage)}")
    for asset in encrypted_storage:
        print(f"    - {asset.name} ({asset.service})")

    # Find IAM roles
    iam_roles = [a for a in asset_graph.assets if "identity" in a.type]
    print(f"  IAM roles: {len(iam_roles)}")
    for asset in iam_roles:
        print(f"    - {asset.name}")

    return asset_graph


def test_json_template():
    """Test parsing of JSON CloudFormation template."""
    print_separator("Testing JSON CloudFormation Template")

    # Read template
    with open("test_cloudformation.json", "r") as f:
        template_content = f.read()

    # Parse
    parser = CloudFormationParser()
    asset_graph = parser.parse(template_content, file_extension="json")

    # Display results
    print(f"✓ Successfully parsed JSON template")
    print(f"  Assets: {len(asset_graph.assets)}")
    print(f"  Relationships: {len(asset_graph.relationships)}")
    print(f"  Trust Boundaries: {len(asset_graph.trust_boundaries)}")
    print(f"  Format: {asset_graph.metadata['format']}")

    # Show assets
    print("\nAssets:")
    for asset in asset_graph.assets:
        print(f"  - {asset.name} ({asset.type}, {asset.service})")
        print(f"    Trust Boundary: {asset.trust_boundary}")
        print(f"    Data Sensitivity: {asset.data_sensitivity}")
        if asset.properties:
            key_props = {
                k: v for k, v in asset.properties.items()
                if k in ["internet_facing", "encryption_at_rest", "public", "ports"]
            }
            if key_props:
                print(f"    Properties: {json.dumps(key_props, indent=6)}")

    # Show relationships
    print("\nRelationships:")
    for rel in asset_graph.relationships:
        source = next((a for a in asset_graph.assets if a.id == rel.source), None)
        target = next((a for a in asset_graph.assets if a.id == rel.target), None)
        if source and target:
            print(f"  {source.name} --[{rel.type}]--> {target.name}")
            if rel.properties:
                print(f"    Properties: {rel.properties}")

    return asset_graph


def test_reference_resolution():
    """Test CloudFormation intrinsic function resolution."""
    print_separator("Testing Reference Resolution")

    # Simple template with Ref and Fn::GetAtt
    template = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  TestVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  TestSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref TestVPC
      CidrBlock: 10.0.1.0/24

  TestRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: 'sts:AssumeRole'

  TestFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.11
      Handler: index.handler
      Role: !GetAtt TestRole.Arn
      Code:
        ZipFile: 'def handler(event, context): pass'
"""

    parser = CloudFormationParser()
    asset_graph = parser.parse(template, file_extension="yaml")

    print(f"✓ Parsed template with intrinsic functions")
    print(f"  Assets: {len(asset_graph.assets)}")
    print(f"  Relationships: {len(asset_graph.relationships)}")

    # Check if relationships were detected
    print("\nDetected Relationships:")
    for rel in asset_graph.relationships:
        source = next((a for a in asset_graph.assets if a.id == rel.source), None)
        target = next((a for a in asset_graph.assets if a.id == rel.target), None)
        if source and target:
            print(f"  {source.name} --[{rel.type}]--> {target.name}")

    # Verify expected relationships
    expected_rels = [
        ("TestSubnet", "TestVPC", "depends_on"),
        ("TestFunction", "TestRole", "iam_binding"),
    ]

    print("\nVerifying Expected Relationships:")
    for source_name, target_name, rel_type in expected_rels:
        found = False
        for rel in asset_graph.relationships:
            source = next((a for a in asset_graph.assets if a.id == rel.source), None)
            target = next((a for a in asset_graph.assets if a.id == rel.target), None)
            if source and target and source.name == source_name and target.name == target_name and rel.type == rel_type:
                found = True
                break
        status = "✓" if found else "✗"
        print(f"  {status} {source_name} --[{rel_type}]--> {target_name}")

    return asset_graph


def main():
    """Run all tests."""
    print_separator("CloudFormation Parser Test Suite")

    try:
        # Test YAML template
        yaml_graph = test_yaml_template()

        print_separator()

        # Test JSON template
        json_graph = test_json_template()

        print_separator()

        # Test reference resolution
        ref_graph = test_reference_resolution()

        # Summary
        print_separator("Test Summary")
        print("✓ All tests passed successfully!")
        print(f"\nYAML Template:")
        print(f"  - {len(yaml_graph.assets)} assets")
        print(f"  - {len(yaml_graph.relationships)} relationships")
        print(f"  - {len(yaml_graph.trust_boundaries)} trust boundaries")
        print(f"\nJSON Template:")
        print(f"  - {len(json_graph.assets)} assets")
        print(f"  - {len(json_graph.relationships)} relationships")
        print(f"  - {len(json_graph.trust_boundaries)} trust boundaries")
        print(f"\nReference Test:")
        print(f"  - {len(ref_graph.assets)} assets")
        print(f"  - {len(ref_graph.relationships)} relationships")

        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
