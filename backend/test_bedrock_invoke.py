#!/usr/bin/env python3
"""Test script to invoke AWS Bedrock and find working models."""

import os
import json
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

print(f"Testing AWS Bedrock Runtime in region: {region}")
print("=" * 60)

# Try different model IDs to find which ones work
test_models = [
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-v2:1",
    "anthropic.claude-v2",
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
]

try:
    # Create Bedrock Runtime client
    session = boto3.Session(
        aws_session_token=bearer_token,
        region_name=region
    )

    bedrock_runtime = session.client("bedrock-runtime", region_name=region)

    print("\n🔍 Testing models to find which ones are active:\n")

    for model_id in test_models:
        try:
            # Try to invoke the model with a minimal request
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            })

            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body
            )

            print(f"✅ {model_id} - ACTIVE")

        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "end of its life" in error_msg.lower():
                print(f"❌ {model_id} - DEPRECATED/NOT FOUND")
            elif "ValidationException" in error_msg:
                print(f"⚠️  {model_id} - INVALID MODEL ID FORMAT")
            else:
                print(f"❓ {model_id} - ERROR: {error_msg[:100]}")

    print("\n" + "=" * 60)
    print("\n💡 Use the ACTIVE models above in your .env file")

except Exception as e:
    print(f"❌ Error creating Bedrock client: {e}")
    print("\nNote: Verify your AWS_BEARER_TOKEN_BEDROCK is valid")
