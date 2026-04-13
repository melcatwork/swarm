# LLM Modularity Review Report

**Date**: 2026-04-13
**Project**: Swarm Threat Modeling
**Objective**: Assess LLM provider modularity and identify potential breaking points when switching models

---

## Executive Summary

The project has **good foundational modularity** with centralized LLM configuration, but several issues exist that could cause problems when switching between different LLM models (e.g., qwen3:14b → gemma4:e4b).

### Critical Issues Found: 3
### Medium Issues Found: 4
### Low Issues Found: 2

---

## 🔴 Critical Issues

### 1. **Inconsistent Temperature Settings Across Providers**
**Location**: `backend/app/swarm/crews.py:53, 81, 97`

**Problem**:
- Bedrock: `temperature=0.7`
- Ollama: `temperature=0.5`
- Anthropic: `temperature=0.7`

**Impact**: Different models will produce outputs with different levels of creativity/consistency, making results unpredictable when switching providers.

**Recommendation**:
```python
# Add to config.py
LLM_TEMPERATURE: float = 0.5

# Use in crews.py
llm = LLM(
    model=...,
    temperature=settings.LLM_TEMPERATURE,
    api_base=...
)
```

---

### 2. **No Max Tokens / Context Window Configuration**
**Location**: `backend/app/swarm/crews.py` (get_llm function)

**Problem**:
- No `max_tokens` parameter set for any provider
- No context window limits configured
- Different models have vastly different context windows:
  - Claude Sonnet: ~200K tokens
  - qwen3:14b: ~32K tokens (typical)
  - gemma4:e4b: ~8K tokens (typical)

**Impact**:
- Large prompts may fail silently on smaller models
- No truncation strategy for long asset graphs

**Recommendation**:
```python
# Add to config.py
LLM_MAX_TOKENS: int = 4096
LLM_CONTEXT_WINDOW: int = 32000  # Safe default

# Use in crews.py with fallback
llm = LLM(
    model=...,
    max_tokens=settings.LLM_MAX_TOKENS,
    temperature=settings.LLM_TEMPERATURE,
)
```

---

### 3. **Model-Specific Output Format Assumptions**
**Location**: `backend/app/swarm/crews.py:339-365`

**Problem**:
- Parser assumes models will return specific JSON field names
- Falls back to generic values ("T1000", "unknown_asset") when fields missing
- Different models may use different naming conventions or omit fields

**Current Fallback Behavior**:
```python
normalized_step["technique_id"] = tech_id or "T1000"  # Generic fallback
normalized_step["technique_name"] = tech_name or "Unknown Technique"
normalized_step["target_asset"] = target or "unknown_asset"
```

**Impact**: Low-quality models produce unusable threat intelligence with placeholder values.

**Status**: ✅ **Partially Fixed** (improved prompting in recent changes)

**Further Recommendation**:
- Add validation to reject paths with fallback values
- Return error to user instead of accepting garbage data
- Add retry logic with improved prompting

---

## 🟡 Medium Issues

### 4. **No Model-Specific Prompt Templates**
**Location**: `backend/app/swarm/crews.py:165-246`

**Problem**:
- Single prompt template used for all models
- Some models need more explicit instructions (as seen with gemma4:e4b)
- No mechanism to customize prompts per model family

**Recommendation**:
Create prompt templates per model type:
```python
def get_task_description_template(model_name: str) -> str:
    """Get appropriate prompt template based on model capabilities."""
    if "gemma" in model_name or "llama" in model_name:
        return EXPLICIT_PROMPT_TEMPLATE  # More detailed
    elif "claude" in model_name or "gpt" in model_name:
        return CONCISE_PROMPT_TEMPLATE  # Less verbose
    else:
        return DEFAULT_PROMPT_TEMPLATE
```

---

### 5. **Hard-Coded Crew Timeouts**
**Location**: `backend/app/routers/swarm.py:56`

**Problem**:
```python
CREW_TIMEOUT_SECONDS = 600  # 10 minutes max
```

**Impact**:
- Faster models (Claude) may not need 10 minutes
- Slower models (local Ollama) may need more time
- No per-model timeout configuration

**Recommendation**:
```python
# Add to config.py
LLM_TIMEOUT_SECONDS: int = 600

# Adjust based on provider
def get_crew_timeout(provider: str) -> int:
    timeouts = {
        "ollama": 900,     # 15 min for local models
        "bedrock": 600,    # 10 min for API models
        "anthropic": 300   # 5 min for fast API
    }
    return timeouts.get(provider, 600)
```

---

### 6. **No Retry Logic for Model Failures**
**Location**: `backend/app/swarm/crews.py` (entire file)

**Problem**:
- No retry mechanism if model returns invalid JSON
- No fallback to simpler prompt if model fails
- Single attempt = single point of failure

**Recommendation**:
```python
def parse_with_retry(output_text: str, max_retries: int = 3):
    """Parse JSON with retry logic and prompt simplification."""
    for attempt in range(max_retries):
        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            if attempt < max_retries - 1:
                logger.warning(f"JSON parse failed, retry {attempt + 1}")
                # Try cleaning/fixing common issues
                output_text = clean_json_output(output_text)
            else:
                raise
```

---

### 7. **Provider-Specific Environment Variable Pollution**
**Location**: `backend/app/swarm/crews.py:33-42`

**Problem**:
```python
# Set dummy values to prevent LiteLLM from trying to connect to OpenAI
os.environ["OPENAI_API_KEY"] = "sk-disabled-no-openai"
os.environ["OPENAI_API_BASE"] = settings.OLLAMA_BASE_URL
os.environ["OPENAI_API_TYPE"] = "ollama"
```

**Impact**:
- Global environment pollution
- May affect other parts of application
- Not cleaned up after use

**Recommendation**:
- Use context managers for environment variable setting
- Scope environment changes to LLM calls only

---

## 🟢 Low Issues

### 8. **No Model Capability Detection**
**Location**: N/A (missing feature)

**Problem**:
- No way to detect if model supports JSON mode
- No check for model context window size
- No validation of model availability before starting long-running jobs

**Recommendation**:
```python
def validate_model_capabilities(model_name: str) -> Dict[str, Any]:
    """Check if model meets minimum requirements."""
    return {
        "supports_json": check_json_support(model_name),
        "context_window": get_context_window(model_name),
        "is_available": check_model_availability(model_name)
    }
```

---

### 9. **No Model Performance Metrics**
**Location**: N/A (missing feature)

**Problem**:
- No tracking of which models produce better results
- No metrics on parsing success rates per model
- No automatic model selection based on historical performance

**Recommendation**:
```python
# Track in database
class ModelPerformance(Base):
    model_name = Column(String)
    success_rate = Column(Float)
    avg_execution_time = Column(Float)
    json_parse_failures = Column(Integer)
```

---

## ✅ Good Modularity Practices

### 1. Centralized Configuration
- Single `get_llm()` function for all LLM instantiation ✅
- Environment-based configuration in `config.py` ✅
- Provider selection via `LLM_PROVIDER` variable ✅

### 2. Abstraction Layer
- CrewAI abstracts direct model API calls ✅
- No hardcoded API endpoints in business logic ✅

### 3. Provider Detection
- `check_llm_configured()` validates credentials ✅
- Startup checks in `main.py` verify model availability ✅

---

## Recommended Priority Actions

### High Priority (Do First)
1. ✅ **DONE**: Enhance prompts with explicit field requirements
2. ✅ **DONE**: Add better error logging for missing fields
3. ✅ **DONE**: Lower temperature for consistency
4. **TODO**: Add max_tokens and context_window configuration
5. **TODO**: Implement validation to reject fallback values

### Medium Priority
6. **TODO**: Add retry logic for JSON parsing failures
7. **TODO**: Create model-specific prompt templates
8. **TODO**: Add per-provider timeout configuration

### Low Priority
9. **TODO**: Implement model capability detection
10. **TODO**: Add model performance tracking

---

## Configuration Changes Needed

### Recommended `.env` additions:
```bash
# LLM Performance Tuning
LLM_TEMPERATURE=0.5
LLM_MAX_TOKENS=4096
LLM_CONTEXT_WINDOW=32000
LLM_TIMEOUT_SECONDS=600
LLM_RETRY_ATTEMPTS=3

# Model-specific overrides
OLLAMA_TIMEOUT_SECONDS=900
BEDROCK_TIMEOUT_SECONDS=600
ANTHROPIC_TIMEOUT_SECONDS=300
```

### Recommended `config.py` additions:
```python
class Settings(BaseSettings):
    # ... existing fields ...

    # LLM Performance Configuration
    LLM_TEMPERATURE: float = 0.5
    LLM_MAX_TOKENS: int = 4096
    LLM_CONTEXT_WINDOW: int = 32000
    LLM_TIMEOUT_SECONDS: int = 600
    LLM_RETRY_ATTEMPTS: int = 3

    # Model-specific settings
    OLLAMA_TIMEOUT_SECONDS: int = 900
    BEDROCK_TIMEOUT_SECONDS: int = 600
    ANTHROPIC_TIMEOUT_SECONDS: int = 300
```

---

## Testing Recommendations

### Before Switching Models:
1. Run test with sample IaC file on current model
2. Archive the output JSON
3. Switch model in `.env`
4. Run same test with new model
5. Compare outputs for:
   - All required fields populated
   - No "T1000", "unknown_asset" fallbacks
   - Valid MITRE ATT&CK technique IDs
   - Specific asset names from graph

### Automated Test Suite Needed:
```python
def test_model_output_quality(model_name: str):
    """Validate model produces quality output."""
    result = run_threat_modeling(sample_iac)

    for path in result["attack_paths"]:
        for step in path["steps"]:
            assert step["technique_id"] != "T1000"
            assert step["target_asset"] != "unknown_asset"
            assert step["technique_name"] != "Unknown Technique"
            assert re.match(r"T\d{4}", step["technique_id"])
```

---

## Conclusion

The project has **acceptable modularity** but needs improvements to be truly model-agnostic. The recent enhancements (explicit prompts, error logging, temperature adjustment) address the immediate gemma4:e4b issue, but longer-term improvements are needed for production robustness.

**Risk Level**: 🟡 **MEDIUM** - System works but may break on model switch without proper testing

**Effort to Fix Critical Issues**: ~4-8 hours
**Effort to Implement All Recommendations**: ~2-3 days
