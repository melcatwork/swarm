#!/bin/bash
#
# get_aws_token.sh
#
# Helper script to get AWS session token for Bedrock authentication
# Outputs the token in a format ready to copy to .env
#

echo "=========================================="
echo "AWS Session Token Generator for Bedrock"
echo "=========================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ ERROR: AWS CLI not found"
    echo ""
    echo "Install AWS CLI:"
    echo "  - macOS: brew install awscli"
    echo "  - Linux: pip install awscli"
    echo "  - Windows: https://aws.amazon.com/cli/"
    echo ""
    exit 1
fi

echo "✓ AWS CLI found"
echo ""

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ ERROR: AWS credentials not configured"
    echo ""
    echo "Configure AWS credentials first:"
    echo "  aws configure"
    echo ""
    echo "Or if using SSO:"
    echo "  aws sso login --profile your-profile"
    echo ""
    exit 1
fi

echo "✓ AWS credentials configured"
echo ""

# Get caller identity
echo "Current AWS identity:"
aws sts get-caller-identity
echo ""

# Ask for duration
echo "How long should the token be valid?"
echo "  1 = 1 hour (3600 seconds)"
echo "  6 = 6 hours (21600 seconds)"
echo "  12 = 12 hours (43200 seconds) [recommended]"
echo ""
read -p "Enter duration in hours [default: 12]: " duration_hours
duration_hours=${duration_hours:-12}
duration_seconds=$((duration_hours * 3600))

echo ""
echo "Requesting session token (valid for $duration_hours hours)..."
echo ""

# Get session token
TOKEN_OUTPUT=$(aws sts get-session-token --duration-seconds $duration_seconds 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to get session token"
    echo ""
    echo "$TOKEN_OUTPUT"
    echo ""
    echo "Possible causes:"
    echo "  - IAM user doesn't have sts:GetSessionToken permission"
    echo "  - You're using IAM role credentials (use IAM user instead)"
    echo "  - Session token requested duration is too long"
    echo ""
    exit 1
fi

# Extract session token
SESSION_TOKEN=$(echo "$TOKEN_OUTPUT" | grep -o '"SessionToken": "[^"]*' | sed 's/"SessionToken": "//')

if [ -z "$SESSION_TOKEN" ]; then
    echo "❌ ERROR: Could not extract session token from response"
    echo ""
    echo "Response:"
    echo "$TOKEN_OUTPUT"
    echo ""
    exit 1
fi

# Display results
echo "=========================================="
echo "✅ SESSION TOKEN GENERATED"
echo "=========================================="
echo ""
echo "Copy this line to your backend/.env file:"
echo ""
echo "AWS_BEARER_TOKEN_BEDROCK=$SESSION_TOKEN"
echo ""
echo "Also add (if not already present):"
echo "AWS_REGION=us-east-1"
echo ""
echo "Token expires in: $duration_hours hours"
echo "Expiration time: $(date -d "+$duration_hours hours" 2>/dev/null || date -v +${duration_hours}H 2>/dev/null)"
echo ""
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Add the token to backend/.env"
echo "  2. Test connection: python3 backend/scripts/test_bedrock_connection.py"
echo "  3. Run sync: python3 backend/scripts/sync_intel.py --force"
echo ""
