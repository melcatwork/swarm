# Work In Progress Model Restriction Implementation

**Date**: 2026-04-14
**Status**: ✅ Complete

## Overview

Implemented restriction system to prevent users from selecting and using commented (Work In Progress) LLM models from the `.env` file. Only the default uncommented model can be used for threat modeling.

## Changes Made

### Backend Changes

#### 1. `backend/app/routers/llm.py`
- **Added `is_wip` field** to `ModelInfo` Pydantic model
- **Added `_get_commented_ollama_models()` helper function** to parse .env and identify commented models
- **Enhanced `get_available_models()` endpoint**:
  - Parses `.env` to identify commented Ollama models
  - Cross-references with Ollama API results
  - Marks models as WIP if commented in `.env`
  - Adds "Work In Progress" suffix to display names
  - Works correctly both when Ollama is running (dynamic discovery) and as fallback

#### 2. `backend/app/routers/swarm.py`
- **Added `validate_model_not_wip()` function** to reject WIP model usage
- **Added validation calls** to all three pipeline endpoints:
  - `/api/swarm/run` (full pipeline)
  - `/api/swarm/run/quick` (quick pipeline)
  - `/api/swarm/run/single` (single agent pipeline)
- **Returns HTTP 400 error** with clear message if WIP model is selected

### Frontend Changes

#### 3. `frontend/src/pages/ThreatModelPage.jsx`
- **Enhanced model dropdown** to disable WIP models (disabled attribute on option)
- **Added client-side validation** before running pipeline
- **Updated help text** to mention WIP models
- **Display "Work In Progress" suffix** comes from backend API

## How It Works

### .env Configuration
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3.5:27b          # Default (uncommented) - CAN USE ✅
#OLLAMA_MODEL=qwen3:14b            # Commented - WIP - CANNOT USE ❌
#OLLAMA_MODEL=qwen3:4b             # Commented - WIP - CANNOT USE ❌
#OLLAMA_MODEL=llama3.2:3b          # Commented - WIP - CANNOT USE ❌
```

### Model Discovery Flow

1. **Backend queries Ollama API** (`/api/tags`) to get ALL locally available models
2. **Backend parses .env file** to identify which models are commented
3. **Backend marks models as WIP** if they have `#OLLAMA_MODEL=<name>` in .env
4. **Frontend receives model list** with `is_wip: true/false` for each model
5. **Frontend disables WIP models** in dropdown (grayed out, not selectable)
6. **Backend validates** on pipeline submission and rejects WIP models

### API Response Example

```json
{
  "current_provider": "ollama",
  "current_model": "qwen3.5:27b",
  "models": [
    {
      "name": "qwen3.5:27b",
      "provider": "ollama",
      "available": true,
      "is_default": true,
      "is_wip": false,
      "display_name": "qwen3.5:27b (16.2GB)",
      "description": "Local Ollama model - 16.2GB"
    },
    {
      "name": "qwen3:14b",
      "provider": "ollama",
      "available": true,
      "is_default": false,
      "is_wip": true,
      "display_name": "qwen3:14b (8.6GB) - Work In Progress",
      "description": "Local Ollama model - 8.6GB (WIP - not yet enabled)"
    },
    {
      "name": "qwen3:4b",
      "provider": "ollama",
      "available": true,
      "is_default": false,
      "is_wip": true,
      "display_name": "qwen3:4b (2.3GB) - Work In Progress",
      "description": "Local Ollama model - 2.3GB (WIP - not yet enabled)"
    }
  ]
}
```

### Error Response When WIP Model Used

```json
{
  "detail": {
    "error": "Model Not Available",
    "message": "The model 'qwen3:4b' is marked as Work In Progress and cannot be used. Please select the default model or another enabled model.",
    "model": "qwen3:4b",
    "status": "work_in_progress"
  }
}
```

## Testing Verification

### Test 1: Model List API
```bash
curl http://localhost:8000/api/llm/models | jq '.models[] | select(.is_wip == true)'
```
**Result**: ✅ Correctly identifies qwen3:14b, qwen3:4b, llama3.2:3b as WIP

### Test 2: WIP Model Rejection
```bash
curl -X POST http://localhost:8000/api/swarm/run/quick \
  -F "file=@test.tf" \
  -F "model=qwen3:4b"
```
**Result**: ✅ Returns HTTP 400 with error message

### Test 3: Default Model Allowed
```bash
curl -X POST http://localhost:8000/api/swarm/run/quick \
  -F "file=@test.tf" \
  -F "model=qwen3.5:27b"
```
**Result**: ✅ Validation passes, pipeline starts (or would if Ollama working)

## User Experience

1. **User opens threat modeling page**
2. **Dropdown shows all models** including WIP ones
3. **WIP models have suffix** "- Work In Progress" and are grayed out
4. **User cannot select WIP models** (disabled in dropdown)
5. **If somehow selected** (e.g., via API), backend rejects with clear error
6. **User must use default model** (qwen3.5:27b) or another enabled model

## Benefits

- **Clear separation** between production-ready and experimental models
- **No accidental usage** of untested models
- **Easy to enable models** (just uncomment in .env, no code changes)
- **Backwards compatible** (existing code works, WIP models just disabled)
- **Self-documenting** (WIP suffix shows status to users)

## Modified Files

- `backend/app/routers/llm.py` — Model discovery with WIP detection
- `backend/app/routers/swarm.py` — Pipeline validation
- `frontend/src/pages/ThreatModelPage.jsx` — UI display and validation

## Notes

- **Ollama-only feature**: WIP detection only works for Ollama provider. Bedrock/Anthropic models are always marked as `is_wip: false`
- **Dynamic discovery still works**: ALL models from `ollama list` appear in dropdown, but only uncommented ones are selectable
- **No .env editing required**: To add/enable models, just `ollama pull <model>` (discovery) and uncomment line in .env (enable)
- **.env path fixed**: Validation function correctly finds .env at project root (`backend/app/routers/swarm.py` goes up 4 levels)
