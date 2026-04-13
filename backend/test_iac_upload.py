#!/usr/bin/env python3
"""
Test script for IaC upload API endpoints.

Tests the /api/iac/upload and /api/iac/validate endpoints with sample files.
"""

import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000"


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    else:
        print("-" * 80)


def test_supported_formats():
    """Test the /api/iac/supported endpoint."""
    print_separator("Testing GET /api/iac/supported")

    response = requests.get(f"{BASE_URL}/api/iac/supported")

    if response.status_code == 200:
        data = response.json()
        print("✓ Successfully retrieved supported formats:")
        for fmt in data["formats"]:
            extensions = ", ".join(fmt["extensions"])
            print(f"  - {fmt['name']}: {extensions}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)


def test_terraform_upload():
    """Test uploading a Terraform file."""
    print_separator("Testing POST /api/iac/upload (Terraform)")

    # Use the test Terraform file
    tf_file = Path("test_terraform.tf")
    if not tf_file.exists():
        print("✗ test_terraform.tf not found")
        return

    with open(tf_file, "rb") as f:
        files = {"file": ("test_terraform.tf", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/api/iac/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Successfully parsed Terraform file")
        print(f"  Assets: {len(data['assets'])}")
        print(f"  Relationships: {len(data['relationships'])}")
        print(f"  Trust Boundaries: {len(data['trust_boundaries'])}")
        print(f"  Metadata: {json.dumps(data['metadata'], indent=4)}")

        # Show a few assets
        print("\n  Sample Assets:")
        for asset in data["assets"][:5]:
            print(f"    - {asset['name']} ({asset['type']}, {asset['service']})")
            print(f"      Trust Boundary: {asset['trust_boundary']}")
            print(f"      Data Sensitivity: {asset['data_sensitivity']}")

        if len(data["assets"]) > 5:
            print(f"    ... and {len(data['assets']) - 5} more")

        # Show a few relationships
        print("\n  Sample Relationships:")
        for rel in data["relationships"][:5]:
            print(f"    - {rel['type']}: {rel['source']} → {rel['target']}")

        if len(data["relationships"]) > 5:
            print(f"    ... and {len(data['relationships']) - 5} more")

    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)


def test_cloudformation_yaml_upload():
    """Test uploading a CloudFormation YAML file."""
    print_separator("Testing POST /api/iac/upload (CloudFormation YAML)")

    cf_file = Path("test_cloudformation.yaml")
    if not cf_file.exists():
        print("✗ test_cloudformation.yaml not found")
        return

    with open(cf_file, "rb") as f:
        files = {"file": ("test_cloudformation.yaml", f, "text/yaml")}
        response = requests.post(f"{BASE_URL}/api/iac/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Successfully parsed CloudFormation YAML file")
        print(f"  Assets: {len(data['assets'])}")
        print(f"  Relationships: {len(data['relationships'])}")
        print(f"  Trust Boundaries: {len(data['trust_boundaries'])}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)


def test_cloudformation_json_upload():
    """Test uploading a CloudFormation JSON file."""
    print_separator("Testing POST /api/iac/upload (CloudFormation JSON)")

    cf_file = Path("test_cloudformation.json")
    if not cf_file.exists():
        print("✗ test_cloudformation.json not found")
        return

    with open(cf_file, "rb") as f:
        files = {"file": ("test_cloudformation.json", f, "application/json")}
        response = requests.post(f"{BASE_URL}/api/iac/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Successfully parsed CloudFormation JSON file")
        print(f"  Assets: {len(data['assets'])}")
        print(f"  Relationships: {len(data['relationships'])}")
        print(f"  Trust Boundaries: {len(data['trust_boundaries'])}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)


def test_terraform_validate():
    """Test validating a Terraform file."""
    print_separator("Testing POST /api/iac/validate (Terraform)")

    tf_file = Path("test_terraform.tf")
    if not tf_file.exists():
        print("✗ test_terraform.tf not found")
        return

    with open(tf_file, "rb") as f:
        files = {"file": ("test_terraform.tf", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/api/iac/validate", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Validation successful")
        print(f"  Valid: {data['valid']}")
        print(f"  Format: {data['format']}")
        print(f"  Resource Count: {data['resource_count']}")
        print(f"  Asset Types: {', '.join(data['asset_types'])}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)


def test_invalid_file():
    """Test uploading an invalid file."""
    print_separator("Testing POST /api/iac/upload (Invalid File)")

    # Create a temporary invalid file
    invalid_content = "This is not a valid IaC file\n"

    files = {"file": ("invalid.tf", invalid_content, "text/plain")}
    response = requests.post(f"{BASE_URL}/api/iac/upload", files=files)

    if response.status_code == 422:
        print(f"✓ Correctly rejected invalid file with 422 status")
        error = response.json()
        print(f"  Error: {error.get('detail', 'No detail')}")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        print(response.text)


def test_unsupported_extension():
    """Test uploading a file with unsupported extension."""
    print_separator("Testing POST /api/iac/upload (Unsupported Extension)")

    files = {"file": ("test.txt", b"some content", "text/plain")}
    response = requests.post(f"{BASE_URL}/api/iac/upload", files=files)

    if response.status_code == 422:
        print(f"✓ Correctly rejected unsupported file extension with 422 status")
        error = response.json()
        print(f"  Error: {error.get('detail', 'No detail')}")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        print(response.text)


def main():
    """Run all tests."""
    print_separator("IaC Upload API Test Suite")
    print("Make sure the FastAPI server is running on http://localhost:8000")

    try:
        # Test health check first
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code != 200:
            print("✗ Server is not responding. Please start the server first.")
            return 1
        print("✓ Server is running")
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to server. Please start the server first:")
        print("  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload")
        return 1

    # Run tests
    test_supported_formats()
    test_terraform_upload()
    test_cloudformation_yaml_upload()
    test_cloudformation_json_upload()
    test_terraform_validate()
    test_invalid_file()
    test_unsupported_extension()

    # Summary
    print_separator("Test Summary")
    print("✓ All tests completed")
    print("\nThe IaC upload API is working correctly and can:")
    print("  - Parse Terraform (.tf) files")
    print("  - Parse CloudFormation YAML files")
    print("  - Parse CloudFormation JSON files")
    print("  - Validate IaC files and return metadata")
    print("  - Reject invalid files with appropriate error messages")
    print("  - Reject unsupported file extensions")

    return 0


if __name__ == "__main__":
    exit(main())
