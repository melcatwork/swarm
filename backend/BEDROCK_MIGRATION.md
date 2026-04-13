# AWS Bedrock Migration Guide

## Overview

The Swarm TM application has been migrated from direct Anthropic API to AWS Bedrock with bearer token authentication. This provides access to Claude models through AWS infrastructure without requiring IAM credentials.

## Changes Made

### 1. Configuration Files

**`.env.example` and `.env`:**
- Removed: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Added: `LLM_PROVIDER`, `AWS_BEARER_TOKEN_BEDROCK`, `AWS_REGION_NAME`, `BEDROCK_MODEL`
- Added support for both Bedrock and Anthropic providers

**`app/config.py`:**
- Added `LLM_PROVIDER` setting (default: "bedrock")
- Added `AWS_BEARER_TOKEN_BEDROCK` for Bedrock authentication
- Added `AWS_REGION_NAME` (default: "us-east-1")
- Added `BEDROCK_MODEL` (default: "bedrock/anthropic.claude-sonnet-4-20250514-v1:0")
- Added `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` for direct API fallback
- Added `get_llm_config()` method to return current LLM configuration
- Added `is_llm_configured()` method to check if credentials are set

**`app/swarm/crews.py`:**
- Added `get_llm()` helper function for centralized LLM instantiation
- Supports both Bedrock and Anthropic providers based on `LLM_PROVIDER` setting
- Sets environment variables for LiteLLM/boto3 to use bearer token auth
- Updated `build_exploration_crew()` to use `get_llm()`

**`app/main.py`:**
- Added startup validation to check LLM configuration
- Logs clear error messages if credentials are missing
- Added `GET /api/llm-status` endpoint to check configuration status

**`requirements.txt`:**
- Changed `crewai>=0.28.8` to `crewai[bedrock]>=0.28.8`
- Added `boto3>=1.28.57` for AWS Bedrock support

### 2. Authentication Flow

**Old (IAM-based):**
```
AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY → boto3 → Bedrock API
```

**New (Bearer Token):**
```
AWS_BEARER_TOKEN_BEDROCK → LiteLLM → Bedrock API
```

**Environment Variables Set by `get_llm()`:**
- `AWS_BEARER_TOKEN_BEDROCK` - Bearer token for Bedrock authentication
- `AWS_REGION_NAME` - AWS region (e.g., "us-east-1")

**No IAM credentials required.**

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate

# Install updated requirements (includes crewai[bedrock] and boto3)
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file and set **one** of the following:

**Option A: AWS Bedrock (Recommended)**
```bash
LLM_PROVIDER=bedrock
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key-here
AWS_REGION_NAME=us-east-1
BEDROCK_MODEL=bedrock/anthropic.claude-sonnet-4-20250514-v1:0
```

**Option B: Direct Anthropic API**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### 3. Verify Configuration

```bash
# Run configuration tests
python3 test_llm_config.py

# Check if LLM is configured
curl http://localhost:8000/api/llm-status
```

Expected output:
```json
{
  "provider": "bedrock",
  "model": "bedrock/anthropic.claude-sonnet-4-20250514-v1:0",
  "configured": true
}
```

### 4. Start Application

```bash
uvicorn app.main:app --reload
```

Check startup logs for LLM configuration:
```
INFO: LLM Provider: bedrock
INFO: AWS Bedrock configured with model: bedrock/anthropic.claude-sonnet-4-20250514-v1:0 in region: us-east-1
```

## API Changes

### New Endpoint: GET /api/llm-status

Returns LLM configuration status:

```bash
curl http://localhost:8000/api/llm-status
```

Response:
```json
{
  "provider": "bedrock",
  "model": "bedrock/anthropic.claude-sonnet-4-20250514-v1:0",
  "configured": true
}
```

### Existing Endpoints

All existing endpoints work the same way:
- `POST /api/swarm/explore` - Full threat modeling
- `POST /api/swarm/explore/quick` - Quick analysis

The LLM provider is now configured globally via `.env` instead of being hardcoded.

## Troubleshooting

### Error: "AWS_BEARER_TOKEN_BEDROCK not set"

**Cause:** Bearer token not configured in `.env`

**Solution:** Add `AWS_BEARER_TOKEN_BEDROCK=your-token` to `.env`

### Error: "AWS Bedrock native provider not available"

**Cause:** CrewAI Bedrock extras not installed

**Solution:**
```bash
pip install 'crewai[bedrock]>=0.28.8'
```

### Error: "ANTHROPIC_API_KEY not set"

**Cause:** Using `LLM_PROVIDER=anthropic` but key not configured

**Solution:** Add `ANTHROPIC_API_KEY=sk-ant-...` to `.env`

### LLM Status Shows "configured: false"

**Cause:** Credentials not set or empty

**Check:**
1. Verify `.env` has the correct credentials
2. Check `LLM_PROVIDER` matches the credentials you set
3. Restart the application to reload environment variables

### "Invalid LLM_PROVIDER"

**Cause:** `LLM_PROVIDER` set to something other than "bedrock" or "anthropic"

**Solution:** Set `LLM_PROVIDER=bedrock` or `LLM_PROVIDER=anthropic` in `.env`

## Migration Checklist

- [x] Updated `.env.example` with new format
- [x] Updated `.env` with new values (placeholder, needs real token)
- [x] Updated `config.py` with new settings
- [x] Added `get_llm_config()` and `is_llm_configured()` methods
- [x] Updated `crews.py` with `get_llm()` helper
- [x] Updated `main.py` with startup validation
- [x] Added `/api/llm-status` endpoint
- [x] Updated `requirements.txt` with `crewai[bedrock]` and `boto3`
- [x] Created test script (`test_llm_config.py`)
- [x] Removed all references to `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

## Provider Comparison

| Feature | Bedrock | Anthropic |
|---------|---------|-----------|
| **Authentication** | Bearer token | API key |
| **Model Format** | `bedrock/anthropic.claude-*` | `anthropic/claude-*` |
| **Region** | Required | N/A |
| **Cost** | AWS pricing | Anthropic pricing |
| **Latency** | Depends on region | Direct to Anthropic |
| **Compliance** | AWS infrastructure | Anthropic infrastructure |

## Code Example

### Getting LLM Instance

```python
from app.swarm.crews import get_llm

# Automatically uses configured provider (Bedrock or Anthropic)
llm = get_llm()

# Use in CrewAI Agent
from crewai import Agent

agent = Agent(
    role="Security Analyst",
    goal="Analyze infrastructure",
    backstory="You are a security expert...",
    llm=llm,  # Uses configured LLM
    verbose=True,
)
```

### Checking Configuration

```python
from app.config import get_settings

settings = get_settings()

# Get current configuration
config = settings.get_llm_config()
print(f"Provider: {config['provider']}")
print(f"Model: {config['model']}")

# Check if configured
if settings.is_llm_configured():
    print("LLM is ready to use")
else:
    print("LLM not configured - set credentials in .env")
```

### Switching Providers

To switch from Bedrock to Anthropic (or vice versa):

1. Edit `.env`:
   ```bash
   # Switch to Anthropic
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. Restart application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Verify:
   ```bash
   curl http://localhost:8000/api/llm-status
   ```

No code changes required!

## Security Notes

1. **Never commit `.env` to git** - Contains sensitive credentials
2. **Bearer tokens are like passwords** - Treat `AWS_BEARER_TOKEN_BEDROCK` as a secret
3. **Rotate tokens regularly** - Follow your organization's security policy
4. **Use environment-specific tokens** - Different tokens for dev/staging/prod
5. **Monitor usage** - Track API calls in AWS CloudWatch or Anthropic dashboard

## Next Steps

1. **Obtain Bedrock Bearer Token:**
   - Contact your AWS administrator
   - Or generate via AWS Console/CLI
   - Token format: typically starts with `ey...`

2. **Update `.env`:**
   - Set `AWS_BEARER_TOKEN_BEDROCK`
   - Verify region is correct

3. **Test Configuration:**
   - Run `python3 test_llm_config.py`
   - Check `/api/llm-status` endpoint

4. **Run Exploration:**
   - Upload infrastructure via `/api/iac/upload`
   - Run threat modeling via `/api/swarm/explore/quick`

## Support

If you encounter issues:

1. Check logs for detailed error messages
2. Verify credentials are correctly set in `.env`
3. Ensure `crewai[bedrock]` is installed
4. Test with `/api/llm-status` endpoint
5. Review this migration guide

---

**Last Updated:** 2026-04-10
**Status:** Complete
**Breaking Changes:** Yes (authentication method changed)
