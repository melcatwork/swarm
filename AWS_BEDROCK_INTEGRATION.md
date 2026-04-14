# AWS Bedrock Integration with Anthropic Models

**Date**: 2026-04-14
**Status**: ✅ Completed

## Overview
Integrated AWS Bedrock with Anthropic Claude models, allowing users to provide AWS credentials and access Claude models through AWS Bedrock. The implementation includes frontend UI for credential configuration and backend support for AWS authentication.

## Features

### ✅ AWS Credential Support
- Support for AWS Access Key ID + Secret Access Key authentication
- Backward compatible with legacy bearer token authentication
- Region selection with support for major AWS regions
- Credentials persisted to `.env` file for reuse across sessions

### ✅ Available Anthropic Models on Bedrock
1. **Claude 3.5 Sonnet v2** (`anthropic.claude-3-5-sonnet-20241022-v2:0`)
   - Most capable Claude 3.5 model
   - 200K context window, 8192 max tokens

2. **Claude 3.5 Sonnet v1** (`anthropic.claude-3-5-sonnet-20240620-v1:0`)
   - Claude 3.5 Sonnet first version
   - 200K context window, 8192 max tokens

3. **Claude 3 Opus** (`anthropic.claude-3-opus-20240229-v1:0`)
   - Most powerful Claude 3 model
   - 200K context window, 4096 max tokens

4. **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - Balanced Claude 3 model
   - 200K context window, 4096 max tokens

5. **Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`)
   - Fastest Claude 3 model
   - 200K context window, 4096 max tokens

### ✅ Frontend Configuration UI
- Collapsible configuration form in Threat Model page
- Fields for AWS Access Key ID, Secret Access Key, and Region
- Region dropdown with 6 major AWS regions
- Password masking for secret key
- Save & Apply button to configure credentials
- Success/error toast notifications
- Automatic model list refresh after configuration

### ✅ Backend API Endpoints
- `POST /api/llm/bedrock/configure` - Configure AWS Bedrock credentials
- `GET /api/llm/models` - List all available models including Bedrock
- `GET /api/llm/status` - Check Bedrock configuration status

## Changes Made

### Backend (3 files modified)

#### 1. Configuration (`.env`)
**Updated variables:**
```bash
# AWS Bedrock with AWS credentials
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION_NAME=us-east-1
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Available Bedrock models listed in comments:**
- anthropic.claude-3-5-sonnet-20241022-v2:0 (Claude 3.5 Sonnet v2)
- anthropic.claude-3-5-sonnet-20240620-v1:0 (Claude 3.5 Sonnet v1)
- anthropic.claude-3-opus-20240229-v1:0 (Claude 3 Opus)
- anthropic.claude-3-sonnet-20240229-v1:0 (Claude 3 Sonnet)
- anthropic.claude-3-haiku-20240307-v1:0 (Claude 3 Haiku)

#### 2. Backend Configuration (`backend/app/config.py`)
**Added:**
- `AWS_ACCESS_KEY_ID` configuration variable
- `AWS_SECRET_ACCESS_KEY` configuration variable
- `get_bedrock_anthropic_models()` method returning list of 5 Anthropic models
- Updated `is_llm_configured()` to check for AWS credentials OR bearer token
- Updated `BEDROCK_MODEL` default to use new model ID format

**Changes:**
- Line 13-16: Added AWS credential variables
- Line 77-82: Updated `is_llm_configured()` to support both auth methods
- Line 189-236: Added `get_bedrock_anthropic_models()` method

#### 3. LLM Router (`backend/app/routers/llm.py`)
**Added:**
- `BedrockConfigRequest` Pydantic model for API request validation
- `POST /api/llm/bedrock/configure` endpoint to save credentials
- Logic to update both runtime environment and `.env` file
- Enhanced `get_available_models()` to show all Bedrock Anthropic models when configured
- Added `has_credentials` field to `/api/llm/status` response

**Changes:**
- Line 214-308: Added `configure_bedrock()` endpoint
- Line 178-198: Updated Bedrock model listing logic
- Line 257-261: Added credentials status to `/api/llm/status`

#### 4. LLM Initialization (`backend/app/swarm/crews.py`)
**Updated `get_llm()` function:**
- Support for AWS Access Key ID + Secret Access Key
- Backward compatible with bearer token
- Sets both `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables
- Sets `AWS_REGION_NAME` and `AWS_DEFAULT_REGION` for boto3
- Automatically adds `bedrock/` prefix to model names if missing
- Enhanced error handling for missing credentials
- Updated model detection to recognize `anthropic.claude` prefix

**Changes:**
- Line 62-89: Updated Bedrock credential handling
- Line 39-46: Enhanced model provider detection logic

### Frontend (3 files modified)

#### 5. API Client (`frontend/src/api/client.js`)
**Added:**
- `configureBedrockCredentials(config)` function to call backend configuration endpoint
- JSDoc documentation for the new function

**Changes:**
- Line 409-428: Added `configureBedrockCredentials()` function

#### 6. Threat Model Page (`frontend/src/pages/ThreatModelPage.jsx`)
**Added:**
- Import `Key` and `Settings` icons from lucide-react
- State management for Bedrock configuration:
  - `showBedrockConfig` - Toggle visibility of config form
  - `bedrockConfig` - Form data (access key, secret, region)
  - `configuringBedrock` - Loading state during configuration
- `handleConfigureBedrock()` function to submit credentials
- Bedrock configuration form UI with:
  - AWS Access Key ID input field
  - AWS Secret Access Key input field (password type)
  - AWS Region dropdown (6 regions)
  - Save & Apply button
  - Cancel button
  - Helper text explaining credential storage

**Changes:**
- Line 2: Added Key icon import
- Line 4: Added `configureBedrockCredentials` import
- Line 38-43: Added Bedrock configuration state
- Line 384-413: Added `handleConfigureBedrock()` handler
- Line 857-933: Added Bedrock configuration UI section

#### 7. Page Styling (`frontend/src/pages/ThreatModelPage.css`)
**Added:**
- `.bedrock-config-section` - Container styling
- `.bedrock-config-form` - Form background and border
- `.form-group` - Form field grouping
- `.form-group label` - Label styling
- `.form-input` - Input field styling with focus states
- `.form-actions` - Action button container

**Changes:**
- Line 110-150: Added Bedrock configuration form styles

## How to Use

### Step 1: Obtain AWS Bedrock Credentials
1. Log in to AWS Console
2. Navigate to IAM → Users
3. Create or select a user with Bedrock permissions
4. Create Access Key:
   - Go to Security Credentials tab
   - Click "Create access key"
   - Choose "Application running outside AWS"
   - Save Access Key ID and Secret Access Key

### Step 2: Configure in Frontend
1. Navigate to `http://localhost:5173/model`
2. Click **"Configure AWS Bedrock Credentials"** button
3. Fill in the form:
   - **AWS Access Key ID**: Your AWS access key (e.g., `AKIAIOSFODNN7EXAMPLE`)
   - **AWS Secret Access Key**: Your AWS secret key (masked input)
   - **AWS Region**: Select your region (default: us-east-1)
4. Click **"Save & Apply"**
5. Wait for success toast: "AWS Bedrock configured successfully! 5 models available."

### Step 3: Select Bedrock Model
1. In the "Select LLM Model" dropdown
2. Choose any Anthropic model from AWS Bedrock:
   - Claude 3.5 Sonnet v2 (AWS Bedrock)
   - Claude 3.5 Sonnet v1 (AWS Bedrock)
   - Claude 3 Opus (AWS Bedrock)
   - Claude 3 Sonnet (AWS Bedrock)
   - Claude 3 Haiku (AWS Bedrock)
3. Upload your IaC file
4. Click "Run Quick Run" or "Run Full Swarm"

### Step 4: Alternative - Configure via .env
You can also configure credentials by editing `.env` file directly:

```bash
# Switch provider to bedrock
LLM_PROVIDER=bedrock

# Add AWS credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION_NAME=us-east-1

# Choose Bedrock Anthropic model
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
```

Then restart the backend:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## API Reference

### POST /api/llm/bedrock/configure
Configure AWS Bedrock credentials.

**Request Body:**
```json
{
  "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "aws_region_name": "us-east-1"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "AWS Bedrock configured successfully",
  "region": "us-east-1",
  "available_models": [
    {
      "id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
      "name": "Claude 3.5 Sonnet v2",
      "provider": "bedrock",
      "description": "Most capable Claude 3.5 model",
      "context_window": 200000,
      "max_tokens": 8192
    },
    ...
  ]
}
```

### GET /api/llm/models
Get all available LLM models including Bedrock.

**Response:**
```json
{
  "current_provider": "ollama",
  "current_model": "qwen3:14b",
  "models": [
    {
      "name": "anthropic.claude-3-5-sonnet-20241022-v2:0",
      "provider": "bedrock",
      "available": true,
      "is_default": false,
      "is_wip": false,
      "display_name": "Claude 3.5 Sonnet v2 (AWS Bedrock)",
      "description": "Most capable Claude 3.5 model"
    },
    ...
  ]
}
```

### GET /api/llm/status
Get current LLM configuration status.

**Response:**
```json
{
  "provider": "bedrock",
  "configured": true,
  "temperature": 0.5,
  "max_tokens": 4096,
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "region": "us-east-1",
  "has_credentials": true
}
```

## Security Considerations

### ✅ Credential Storage
- Credentials saved to `.env` file (excluded from git via `.gitignore`)
- Secret access key displayed as password input (masked)
- No credentials logged in application logs
- Credentials only transmitted over localhost (development)

### ⚠️ Production Recommendations
1. **Use IAM Roles**: In AWS environments, use IAM roles instead of access keys
2. **Rotate Keys**: Regularly rotate AWS access keys
3. **Least Privilege**: Grant only Bedrock-specific permissions
4. **HTTPS Only**: Ensure production deployment uses HTTPS
5. **Secrets Manager**: Consider AWS Secrets Manager for production

### Required IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude*"
    }
  ]
}
```

## Troubleshooting

### Issue: "Credentials not configured" error
**Solution**: Ensure you've saved credentials via the UI or added them to `.env`

### Issue: Models not appearing in dropdown
**Solution**:
1. Verify credentials are correct
2. Check AWS region supports Bedrock
3. Refresh the page after configuring

### Issue: "Access Denied" when using Bedrock
**Solution**:
1. Verify IAM permissions include `bedrock:InvokeModel`
2. Check model is available in selected region
3. Ensure Bedrock is enabled in your AWS account

### Issue: Backend fails to start after configuration
**Solution**:
1. Check `.env` file format (no quotes around values)
2. Verify no special characters in credentials
3. Restart backend: `uvicorn app.main:app --reload`

## Testing

### Manual Testing
```bash
# 1. Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 2. Test configuration endpoint
curl -X POST http://localhost:8000/api/llm/bedrock/configure \
  -H "Content-Type: application/json" \
  -d '{
    "aws_access_key_id": "YOUR_KEY_ID",
    "aws_secret_access_key": "YOUR_SECRET_KEY",
    "aws_region_name": "us-east-1"
  }'

# 3. Verify models endpoint
curl http://localhost:8000/api/llm/models | python3 -m json.tool

# 4. Check status
curl http://localhost:8000/api/llm/status | python3 -m json.tool
```

### Frontend Testing
1. Open http://localhost:5173/model
2. Click "Configure AWS Bedrock Credentials"
3. Enter test credentials
4. Verify toast notification shows success
5. Check model dropdown shows Bedrock models
6. Select a Bedrock model and run threat model

## Known Limitations

1. **Manual .env Edit**: Credentials persist in .env but require backend restart to take effect if edited manually
2. **Single Account**: Only one set of AWS credentials supported at a time
3. **Region Hardcoded**: Region selection limited to 6 predefined regions
4. **No Key Validation**: Credentials not validated until first model use
5. **No Multi-Factor Auth**: MFA not supported for AWS credentials

## Future Enhancements

1. **Credential Validation**: Test credentials immediately after configuration
2. **Session Tokens**: Support for temporary AWS session tokens
3. **Multiple Profiles**: Allow multiple AWS credential profiles
4. **IAM Role Support**: Automatic detection of IAM roles in AWS environments
5. **Cross-Region**: Show which models are available in each region
6. **Cost Tracking**: Display estimated costs for model usage

## Files Modified

### Backend (4 files)
- `.env` - Added AWS credential variables and model list
- `backend/app/config.py` - Added AWS credential support and model list
- `backend/app/routers/llm.py` - Added configuration endpoint
- `backend/app/swarm/crews.py` - Updated LLM initialization

### Frontend (3 files)
- `frontend/src/api/client.js` - Added configuration API function
- `frontend/src/pages/ThreatModelPage.jsx` - Added configuration UI
- `frontend/src/pages/ThreatModelPage.css` - Added form styles

## Documentation Created
- `AWS_BEDROCK_INTEGRATION.md` - This comprehensive guide
- Updated `CLAUDE.md` - Added to recent changes section
