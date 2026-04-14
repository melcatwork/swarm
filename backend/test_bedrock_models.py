#!/usr/bin/env python3
"""Test script to list available AWS Bedrock models."""

import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

# Get credentials
bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
region = os.getenv("AWS_REGION", "us-east-1")

if not bearer_token:
    print("❌ AWS_BEARER_TOKEN_BEDROCK not set in .env")
    exit(1)

print(f"Testing AWS Bedrock in region: {region}")
print("=" * 60)

try:
    # Create Bedrock client (using bearer token as session token)
    session = boto3.Session(
        aws_session_token=bearer_token,
        region_name=region
    )

    bedrock = session.client("bedrock", region_name=region)

    # List foundation models
    print("\n🔍 Listing all Anthropic models available in Bedrock:\n")

    response = bedrock.list_foundation_models(
        byProvider="Anthropic"
    )

    anthropic_models = response.get("modelSummaries", [])

    if not anthropic_models:
        print("⚠️  No Anthropic models found")
    else:
        for model in anthropic_models:
            model_id = model.get("modelId", "unknown")
            model_name = model.get("modelName", "unknown")
            status = model.get("modelLifecycle", {}).get("status", "unknown")

            # Filter out deprecated models
            if status == "ACTIVE":
                print(f"✅ {model_name}")
                print(f"   ID: {model_id}")
                print(f"   Status: {status}")
                print()

    print("=" * 60)
    print("\n💡 Use the model IDs above in your .env file")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nNote: Bearer token authentication might not work for bedrock:ListFoundationModels")
    print("You may need AWS Access Keys (AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY)")
