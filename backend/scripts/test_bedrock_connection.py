#!/usr/bin/env python3
"""
test_bedrock_connection.py

Quick test to verify AWS Bedrock credentials work before running full sync.
Tests both the connection and the PersonaPatchGenerator initialization.

Usage:
  python3 backend/scripts/test_bedrock_connection.py
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def test_bedrock_connection():
    """Test Bedrock connection and configuration."""

    print("=" * 70)
    print("AWS BEDROCK CONNECTION TEST")
    print("=" * 70)
    print()

    # Check environment variables
    print("Step 1: Checking environment variables...")
    bedrock_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not bedrock_token:
        print("❌ ERROR: AWS_BEARER_TOKEN_BEDROCK not set")
        print()
        print("Please add to your .env file:")
        print("  AWS_BEARER_TOKEN_BEDROCK=your-token-here")
        print("  AWS_REGION=us-east-1")
        print()
        return False

    print(f"✓ AWS_BEARER_TOKEN_BEDROCK: {bedrock_token[:20]}...")
    print(f"✓ AWS_REGION: {aws_region}")
    print()

    # Test LLM initialization
    print("Step 2: Testing LLM initialization...")
    try:
        from crewai import LLM

        # Set environment variables
        os.environ["AWS_BEARER_TOKEN_BEDROCK"] = bedrock_token
        os.environ["AWS_REGION_NAME"] = aws_region
        os.environ["AWS_DEFAULT_REGION"] = aws_region
        os.environ["AWS_REGION"] = aws_region

        model = "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"
        llm = LLM(
            model=model,
            temperature=0.3,
            max_tokens=100
        )

        print(f"✓ LLM initialized: {model}")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize LLM: {e}")
        print()
        return False

    # Test simple LLM call
    print("Step 3: Testing LLM call...")
    try:
        response = llm.call([
            {"role": "user", "content": "Say 'Bedrock connection successful' in JSON format with a 'status' field."}
        ])

        # Extract response text
        if isinstance(response, dict) and "choices" in response:
            content = response["choices"][0]["message"]["content"]
        elif isinstance(response, str):
            content = response
        else:
            content = str(response)

        print(f"✓ LLM response received:")
        print(f"  {content[:200]}")
        print()
    except Exception as e:
        print(f"❌ ERROR: LLM call failed: {e}")
        print()
        print("Possible causes:")
        print("  - Token expired (get new token with: aws sts get-session-token)")
        print("  - Model not enabled in Bedrock console")
        print("  - Insufficient IAM permissions (need bedrock:InvokeModel)")
        print("  - Wrong region (check AWS_REGION)")
        print()
        return False

    # Test PersonaPatchGenerator initialization
    print("Step 4: Testing PersonaPatchGenerator initialization...")
    try:
        from backend.app.swarm.vuln_intel.persona_patch_generator import PersonaPatchGenerator

        generator = PersonaPatchGenerator(
            llm_provider="bedrock",
            bedrock_token=bedrock_token,
            aws_region=aws_region
        )

        print("✓ PersonaPatchGenerator initialized successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize PersonaPatchGenerator: {e}")
        print()
        return False

    # Success
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print()
    print("Your Bedrock configuration is working correctly!")
    print()
    print("Next step: Run the full intel sync:")
    print("  python3 backend/scripts/sync_intel.py --force")
    print()

    return True


if __name__ == "__main__":
    success = test_bedrock_connection()
    sys.exit(0 if success else 1)
