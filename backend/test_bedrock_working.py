#!/usr/bin/env python3
"""Verify that Claude 3 Sonnet model works with bearer token."""

import os
import json
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
region = os.getenv("AWS_REGION", "us-east-1")
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

print(f"Testing model: {model_id}")
print("=" * 60)

try:
    session = boto3.Session(
        aws_session_token=bearer_token,
        region_name=region
    )

    bedrock_runtime = session.client("bedrock-runtime", region_name=region)

    # Simple test prompt
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "Say 'Hello, I am Claude 3 Sonnet on AWS Bedrock!'"}]
    })

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=body
    )

    response_body = json.loads(response['body'].read())
    content = response_body.get('content', [])

    if content:
        print("✅ SUCCESS! Model is working correctly.\n")
        print("Response:")
        print(content[0].get('text', ''))
        print("\n" + "=" * 60)
        print("\n🎉 Your AWS Bedrock configuration is ready for threat modeling!")
    else:
        print("⚠️  Model responded but with unexpected format")

except Exception as e:
    print(f"❌ Error: {e}")
