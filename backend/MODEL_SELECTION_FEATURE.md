# Model Selection Feature - Implementation Guide

**Date**: 2026-04-13
**Feature**: User-selectable LLM models for threat modeling

---

## Overview

Users can now select which LLM model to use when running threat modeling, directly from the frontend UI. The list of available models is dynamically loaded from the `.env` file configuration.

---

## Changes Made

### Backend Changes

#### 1. **New API Endpoint - LLM Model Management** (`backend/app/routers/llm.py`)

Created new router with two endpoints:

**GET /api/llm/models**
- Returns all available models from .env (including commented ones)
- Checks Ollama server for actually pulled models
- Returns models with availability status and display names

Response format:
```json
{
  "current_provider": "ollama",
  "current_model": "gemma4:e4b",
  "models": [
    {
      "name": "gemma4:e4b",
      "provider": "ollama",
      "available": true,
      "is_default": true,
      "display_name": "gemma4:e4b (Ollama)",
      "description": "Local Ollama model"
    },
    {
      "name": "qwen3:14b",
      "provider": "ollama",
      "available": true,
      "is_default": false,
      "display_name": "qwen3:14b (Ollama)",
      "description": "Local Ollama model"
    }
  ]
}
```

**GET /api/llm/status**
- Returns current LLM configuration and status
- Checks Ollama server reachability
- Shows model availability

#### 2. **Updated Configuration** (`backend/app/config.py`)

Added `get_available_models()` method:
- Parses `.env` file to find all model configurations
- Extracts both active and commented models
- Returns models grouped by provider (ollama, bedrock, anthropic)
- Handles duplicates and validates availability

#### 3. **Updated LLM Initialization** (`backend/app/swarm/crews.py`)

Modified `get_llm()` function:
- Accepts optional `model_override` parameter
- Accepts optional `provider_override` parameter
- Uses centralized config for temperature and max_tokens
- Auto-detects provider from model name if not specified

Updated crew building functions:
- `build_exploration_crew()` - accepts `model_override`
- `build_evaluation_crew()` - accepts `model_override`
- `build_adversarial_crew()` - accepts `model_override`

#### 4. **Updated API Routers** (`backend/app/routers/swarm.py`)

Updated internal helper functions:
- `_run_exploration()` - accepts and passes `model` parameter
- `_run_evaluation()` - accepts and passes `model` parameter
- `_run_quick_pipeline_sync()` - accepts and passes `model` parameter

Updated API endpoints:
- `POST /api/swarm/run/quick/background` - accepts optional `model` form parameter
- `ExploreRequest` model - added optional `model` field

#### 5. **Registered New Router** (`backend/app/main.py`)

Added `llm` router to the application:
```python
app.include_router(llm.router)
```

---

### Frontend Changes

#### 1. **Updated API Client** (`frontend/src/api/client.js`)

**Added Functions**:
- `getAvailableModels()` - Fetches available models from backend
- `getLLMStatus()` - Gets current LLM configuration

**Updated Functions**:
- `uploadAndRunQuick(file, model)` - Now accepts optional `model` parameter

#### 2. **Updated Threat Model Page** (`frontend/src/pages/ThreatModelPage.jsx`)

**Added State**:
```javascript
const [availableModels, setAvailableModels] = useState([]);
const [selectedModel, setSelectedModel] = useState(null); // null = use default
```

**Added useEffect**:
- Fetches available models on component mount
- Populates model dropdown

**Added UI**:
- Model selection dropdown between agent selection and run buttons
- Shows model availability status
- Marks current default model
- Disabled models show "(Not Available)"

**Updated Behavior**:
- Passes selected model to `uploadAndRunQuick()`
- `null` value uses default from .env

---

## How to Use

### For Users

1. **Start Backend**:
```bash
cd /Users/bland/Desktop/swarm-tm/backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

2. **Start Frontend**:
```bash
cd /Users/bland/Desktop/swarm-tm/frontend
npm run dev
```

3. **Access UI**: Open http://localhost:5173

4. **Select Model**:
   - Upload your IaC file
   - Select desired LLM model from dropdown (or leave as default)
   - Click "Quick Run (2 agents)"

### For Developers

#### Adding New Models to .env

Simply add new models to `.env`:
```bash
# Currently active model
OLLAMA_MODEL=gemma4:e4b

# Other available models (commented out)
#OLLAMA_MODEL=qwen3:14b
#OLLAMA_MODEL=qwen3:4b
#OLLAMA_MODEL=llama3.2:3b
#OLLAMA_MODEL=mistral:7b
```

The frontend will automatically pick up all models (including commented ones) and display them in the dropdown.

#### Pull New Ollama Models

```bash
ollama pull qwen3:14b
ollama pull gemma4:e4b
ollama pull mistral:7b
```

#### Model Selection Priority

1. User selects model in UI → `model` parameter sent to backend
2. Backend receives `model` parameter → passes to `get_llm(model_override=model)`
3. `get_llm()` uses `model_override` if provided, otherwise uses `.env` default
4. LLM instance created with the specified model

---

## API Examples

### Get Available Models

**Request**:
```bash
curl http://localhost:8000/api/llm/models
```

**Response**:
```json
{
  "current_provider": "ollama",
  "current_model": "gemma4:e4b",
  "models": [
    {
      "name": "gemma4:e4b",
      "provider": "ollama",
      "available": true,
      "is_default": true,
      "display_name": "gemma4:e4b (Ollama)",
      "description": "Local Ollama model"
    },
    {
      "name": "qwen3:14b",
      "provider": "ollama",
      "available": true,
      "is_default": false,
      "display_name": "qwen3:14b (Ollama)",
      "description": "Local Ollama model"
    }
  ]
}
```

### Run Threat Modeling with Specific Model

**Request**:
```bash
curl -X POST http://localhost:8000/api/swarm/run/quick/background \
  -F "file=@infrastructure.tf" \
  -F "model=qwen3:14b"
```

**Response**:
```json
{
  "job_id": "abc123",
  "status": "pending",
  "message": "Pipeline started for infrastructure.tf using model: qwen3:14b",
  "estimated_time_minutes": 7,
  "status_url": "/api/swarm/job/abc123/status"
}
```

---

## Benefits

### User Experience
- ✅ No need to edit `.env` file to switch models
- ✅ See all available models in one place
- ✅ Know which models are actually pulled and ready
- ✅ Experiment with different models easily
- ✅ Model availability shown in real-time

### Developer Experience
- ✅ Easy to add new models (just update `.env`)
- ✅ Model selection isolated from other code
- ✅ Backward compatible (default behavior unchanged)
- ✅ No restart required to see new models

### System Design
- ✅ Centralized model configuration
- ✅ Model selection flows through entire pipeline
- ✅ Same temperature/max_tokens for all models
- ✅ Provider auto-detection

---

## Testing

### Test Model Switching

1. **Start with default model** (gemma4:e4b)
2. **Upload IaC file** and run threat modeling
3. **Check results** - should see valid technique IDs and assets
4. **Switch to qwen3:14b** in dropdown
5. **Run again** - should work with no code changes
6. **Compare results** - both should be high quality

### Test Model Availability

1. **Pull only one model**: `ollama pull gemma4:e4b`
2. **Check dropdown** - gemma4:e4b marked as available
3. **Try to select unpulled model** - should show "(Not Available)"
4. **Pull second model**: `ollama pull qwen3:14b`
5. **Refresh page** - both now marked as available

---

## Troubleshooting

### Model Not Showing in Dropdown

**Problem**: Model in `.env` not appearing in dropdown

**Solution**:
1. Check `.env` format: `#OLLAMA_MODEL=model_name`
2. Restart backend if `.env` was just edited
3. Check browser console for errors

### Model Shows as "Not Available"

**Problem**: Model in dropdown but marked as unavailable

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull the model
ollama pull model_name

# Verify it's pulled
ollama list
```

### Selected Model Not Being Used

**Problem**: Selected model in UI but threat modeling uses default

**Solution**:
1. Check browser DevTools Network tab
2. Verify `model` parameter in form data
3. Check backend logs for "Using model: X"

---

## Files Modified

### Backend
- ✅ `backend/app/config.py` - Added `get_available_models()`
- ✅ `backend/app/routers/llm.py` - New router (created)
- ✅ `backend/app/routers/swarm.py` - Updated endpoints and helpers
- ✅ `backend/app/swarm/crews.py` - Updated `get_llm()` and crew builders
- ✅ `backend/app/main.py` - Registered llm router

### Frontend
- ✅ `frontend/src/api/client.js` - Added model functions, updated upload
- ✅ `frontend/src/pages/ThreatModelPage.jsx` - Added model selection UI

### Documentation
- ✅ `backend/MODEL_SELECTION_FEATURE.md` - This file
- ✅ `backend/LLM_MODULARITY_REVIEW.md` - LLM modularity analysis
- ✅ `backend/LLM_MODULARITY_FIXES_APPLIED.md` - Modularity fixes

---

## Future Enhancements

### Possible Improvements
- [ ] Add model performance metrics (speed, quality)
- [ ] Show model size and memory requirements
- [ ] Add "recommended for" tags (speed, accuracy, etc.)
- [ ] Save user's preferred model selection
- [ ] Add model comparison view
- [ ] Support custom model parameters per model
- [ ] Add model health check before run
- [ ] Show estimated time per model

---

## Summary

Users can now select LLM models from a dropdown in the UI without editing configuration files. The system automatically detects available models, checks their availability, and passes the selection through the entire threat modeling pipeline. This makes it easy to experiment with different models and compare results.

**Test it now**: Start the backend, open the UI, select a model from the dropdown, and run threat modeling! 🎉
