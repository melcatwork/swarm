# AWS Bedrock Migration - Changes Summary

## ✅ Completed Changes

### 1. Environment Configuration

**Files Updated:**
- `.env.example` - New format with `LLM_PROVIDER`, `AWS_BEARER_TOKEN_BEDROCK`, `AWS_REGION_NAME`
- `.env` - Updated with new configuration (placeholder values)

**Removed:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

**Added:**
- `LLM_PROVIDER` - Choose "bedrock" or "anthropic"
- `AWS_BEARER_TOKEN_BEDROCK` - Bearer token for Bedrock auth
- `AWS_REGION_NAME` - AWS region (default: "us-east-1")
- `BEDROCK_MODEL` - Full model path (default: "bedrock/anthropic.claude-sonnet-4-20250514-v1:0")
- `ANTHROPIC_MODEL` - Anthropic model name (fallback option)

### 2. Configuration Module (`app/config.py`)

**New Settings:**
```python
class Settings(BaseSettings):
    LLM_PROVIDER: str = "bedrock"
    AWS_BEARER_TOKEN_BEDROCK: Optional[str] = None
    AWS_REGION_NAME: str = "us-east-1"
    BEDROCK_MODEL: str = "bedrock/anthropic.claude-sonnet-4-20250514-v1:0"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
```

**New Methods:**
- `get_llm_config()` - Returns `{"model": "...", "provider": "..."}`
- `is_llm_configured()` - Checks if credentials are set
- `get_settings()` - Singleton access function

### 3. Crew Builder (`app/swarm/crews.py`)

**New Function:**
```python
def get_llm() -> LLM:
    """Get configured LLM instance based on settings."""
    settings = get_settings()

    if settings.LLM_PROVIDER == "bedrock":
        os.environ["AWS_BEARER_TOKEN_BEDROCK"] = settings.AWS_BEARER_TOKEN_BEDROCK
        os.environ["AWS_REGION_NAME"] = settings.AWS_REGION_NAME
        return LLM(model=settings.BEDROCK_MODEL, temperature=0.7)
    else:
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
        return LLM(model=f"anthropic/{settings.ANTHROPIC_MODEL}", temperature=0.7)
```

**Updated:**
- `build_exploration_crew()` now calls `get_llm()` instead of hardcoding LLM config

### 4. Main Application (`app/main.py`)

**Added Startup Validation:**
```python
@app.on_event("startup")
async def startup_validation():
    """Validate LLM configuration on startup."""
    # Checks LLM_PROVIDER and credentials
    # Logs clear error messages if misconfigured
```

**New Endpoint:**
```python
@app.get("/api/llm-status")
async def llm_status():
    """Get LLM configuration status."""
    return {
        "provider": "bedrock" | "anthropic",
        "model": "bedrock/anthropic.claude-sonnet-4-20250514-v1:0",
        "configured": true | false
    }
```

### 5. Dependencies (`requirements.txt`)

**Changed:**
```diff
- crewai>=0.28.8
+ crewai[bedrock]>=0.28.8
```

**Added:**
```diff
+ boto3>=1.28.57
```

### 6. Testing (`test_llm_config.py`)

**New Test Script:**
- Tests configuration loading
- Tests `get_llm_config()` method
- Tests `is_llm_configured()` check
- Tests `get_llm()` helper function
- Tests startup validation

## 🔑 Key Features

### Dual Provider Support

Switch between Bedrock and Anthropic by changing one environment variable:

```bash
# Use Bedrock
LLM_PROVIDER=bedrock
AWS_BEARER_TOKEN_BEDROCK=your-token

# Or use Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Centralized LLM Configuration

All crew builders use the same `get_llm()` helper:

```python
from app.swarm.crews import get_llm

llm = get_llm()  # Automatically uses configured provider
```

### Startup Validation

Application checks LLM configuration on startup and logs clear messages:

```
INFO: LLM Provider: bedrock
INFO: AWS Bedrock configured with model: bedrock/anthropic.claude-sonnet-4-20250514-v1:0
```

Or:

```
ERROR: AWS_BEARER_TOKEN_BEDROCK not set. Set it in .env to use Bedrock.
```

### Status Endpoint

Frontend can check LLM configuration:

```bash
curl http://localhost:8000/api/llm-status

{
  "provider": "bedrock",
  "model": "bedrock/anthropic.claude-sonnet-4-20250514-v1:0",
  "configured": true
}
```

## 🚫 What Was NOT Changed

- No changes to API endpoints (except new `/api/llm-status`)
- No changes to request/response formats
- No changes to persona management
- No changes to IaC parsers
- No changes to threat intelligence
- No changes to exploration logic

All existing functionality works the same - only the LLM provider configuration changed.

## 📋 Setup Checklist

To use the new configuration:

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Edit `.env` file
- [ ] Set `LLM_PROVIDER=bedrock` or `LLM_PROVIDER=anthropic`
- [ ] Set `AWS_BEARER_TOKEN_BEDROCK` (for Bedrock) or `ANTHROPIC_API_KEY` (for Anthropic)
- [ ] Verify with: `python3 test_llm_config.py`
- [ ] Start app: `uvicorn app.main:app --reload`
- [ ] Check status: `curl http://localhost:8000/api/llm-status`
- [ ] Test exploration: `POST /api/swarm/explore/quick`

## 🎯 Benefits

1. **Bearer Token Auth**: No AWS IAM credentials needed
2. **Flexible**: Easy switch between Bedrock and Anthropic
3. **Validated**: Startup checks catch configuration errors early
4. **Observable**: `/api/llm-status` endpoint for monitoring
5. **Centralized**: Single `get_llm()` function for consistency
6. **Secure**: No hardcoded credentials, all from environment

## 📖 Documentation

- `BEDROCK_MIGRATION.md` - Complete migration guide
- `test_llm_config.py` - Configuration test suite
- `.env.example` - Configuration template

---

**Status:** ✅ Complete
**Breaking Changes:** Yes (authentication method)
**Backward Compatible:** No (requires new environment variables)
**Action Required:** Update `.env` with bearer token or API key
