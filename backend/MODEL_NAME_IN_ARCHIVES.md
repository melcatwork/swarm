# Model Name in Archived Runs Feature

**Date**: 2026-04-13
**Feature**: Display LLM model name in archived runs sidebar

---

## Overview

The archived runs sidebar now displays which LLM model was used for each threat modeling run. This helps users:
- Track which models produced which results
- Compare outputs from different models
- Understand historical model usage
- Reproduce results with the same model

---

## Changes Made

### Backend Changes

#### 1. **Updated Archive Service** (`backend/app/services/archive_service.py`)

**Added `model_used` parameter to `save_run()` method:**
```python
def save_run(
    self,
    pipeline_result: Dict[str, Any],
    file_name: str,
    mode: str,
    agent_name: Optional[str] = None,
    custom_name: Optional[str] = None,
    model_used: Optional[str] = None,  # NEW PARAMETER
) -> ArchivedRunMetadata:
```

**Updated metadata creation:**
```python
metadata = ArchivedRunMetadata(
    # ... other fields ...
    model_used=model_used,  # Previously was None
)
```

#### 2. **Added Helper Function** (`backend/app/routers/swarm.py`)

**New function to get current model name:**
```python
def get_current_model_name(model_override: str = None) -> str:
    """
    Get the model name that will be used for this run.

    Args:
        model_override: Optional model override from user selection

    Returns:
        Model name string (e.g., "qwen3:14b", "gemma4:e4b")
    """
    if model_override:
        return model_override

    settings = get_settings()
    if settings.LLM_PROVIDER == "ollama":
        return settings.OLLAMA_MODEL
    elif settings.LLM_PROVIDER == "bedrock":
        return settings.BEDROCK_MODEL
    elif settings.LLM_PROVIDER == "anthropic":
        return settings.ANTHROPIC_MODEL
    else:
        return "unknown"
```

#### 3. **Updated All Archive Calls** (`backend/app/routers/swarm.py`)

**Full Pipeline** (Line ~1180):
```python
archive_service.save_run(
    pipeline_result=response.model_dump(),
    file_name=file.filename,
    mode="full",
    agent_name=None,
    model_used=get_current_model_name(),  # NEW
)
```

**Quick Pipeline** (Line ~1392):
```python
archive_service.save_run(
    pipeline_result=response.model_dump(),
    file_name=file.filename,
    mode="quick",
    agent_name=None,
    model_used=get_current_model_name(),  # NEW
)
```

**Single Agent Pipeline** (Line ~1623):
```python
archive_service.save_run(
    pipeline_result=response.model_dump(),
    file_name=file.filename,
    mode="single",
    agent_name=agent_name,
    model_used=get_current_model_name(),  # NEW
)
```

**Background Pipeline** (Line ~1892):
```python
# Auto-save to archive after completing job
archive_service.save_run(
    pipeline_result=result,
    file_name=filename,
    mode="quick",
    agent_name=None,
    model_used=get_current_model_name(model),  # NEW - passes model parameter
)
```

---

### Frontend Changes

#### 1. **Updated UI Display** (`frontend/src/pages/ThreatModelPage.jsx`)

**Added model badge display in archived run item:**
```jsx
<div className="run-stats">
  <span>{run.paths_count} paths</span>
  <span>{run.execution_time_seconds.toFixed(0)}s</span>
</div>
{run.model_used && (
  <div className="run-model">
    <span className="model-badge">{run.model_used}</span>
  </div>
)}
<div className="run-date">
  {new Date(run.created_at).toLocaleDateString()} {new Date(run.created_at).toLocaleTimeString()}
</div>
```

#### 2. **Added CSS Styling** (`frontend/src/pages/ThreatModelPage.css`)

**New styles for model badge:**
```css
.run-model {
  margin-bottom: 0.5rem;
}

.model-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 500;
  border-radius: 4px;
  background-color: #e0e7ff;
  color: #4338ca;
}
```

---

## Visual Changes

### Before
```
[Archived Run]
TM Swarm Run - ecommerce-platform - 2026-04-13 03:27
📄 ecommerce-platform.tf | QUICK
📊 4 paths | ⏱️ 120s
📅 2026-04-13 03:27:49
```

### After
```
[Archived Run]
TM Swarm Run - ecommerce-platform - 2026-04-13 03:27
📄 ecommerce-platform.tf | QUICK
📊 4 paths | ⏱️ 120s
🤖 qwen3:14b                    ← NEW!
📅 2026-04-13 03:27:49
```

---

## Model Name Sources

The model name is captured from:

1. **User Selection**: If user selects a model in the UI dropdown, that model name is used
2. **Default from .env**: If no model selected, uses the default from `.env`:
   - Ollama: `OLLAMA_MODEL` (e.g., "qwen3:14b")
   - Bedrock: `BEDROCK_MODEL` (e.g., "bedrock/anthropic.claude-sonnet-4-20250514-v1:0")
   - Anthropic: `ANTHROPIC_MODEL` (e.g., "claude-sonnet-4-20250514")

---

## Data Model

### ArchivedRunMetadata Schema
```python
class ArchivedRunMetadata(BaseModel):
    run_id: str
    name: str
    created_at: str
    updated_at: Optional[str]
    file_name: str
    file_type: str
    mode: str  # "full", "quick", or "single"
    agent_name: Optional[str]
    execution_time_seconds: float
    paths_count: int
    model_used: Optional[str]  # NEW FIELD
```

### Example JSON Response
```json
{
  "runs": [
    {
      "run_id": "run_20260413_103045_abc123",
      "name": "TM Swarm Run - ecommerce-platform",
      "created_at": "2026-04-13T10:30:45.123Z",
      "file_name": "ecommerce-platform.tf",
      "file_type": ".tf",
      "mode": "quick",
      "agent_name": null,
      "execution_time_seconds": 125.5,
      "paths_count": 4,
      "model_used": "qwen3:14b"
    }
  ],
  "total": 1
}
```

---

## Backward Compatibility

**Existing Archived Runs:**
- Old runs without `model_used` will show `null` or nothing
- The UI conditionally displays the badge: `{run.model_used && ...}`
- No breaking changes to existing data

**Migration Not Required:**
- Old runs continue to work
- New runs will have model information
- No database migration needed (JSON file storage)

---

## Testing

### Manual Test Steps

1. **Restart Backend**:
   ```bash
   cd /Users/bland/Desktop/swarm-tm/backend
   source .venv/bin/activate
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Run Threat Modeling**:
   - Upload an IaC file
   - Select a model (or use default)
   - Click "Quick Run (2 agents)"
   - Wait for completion

3. **Check Archived Runs Sidebar**:
   - Look for the newly created run
   - Should see model badge below the stats
   - Badge should show the model name (e.g., "qwen3:14b")

4. **Test Different Models**:
   - Run with "qwen3:14b" → should show "qwen3:14b"
   - Run with "gemma4:e4b" → should show "gemma4:e4b"
   - Compare runs in sidebar

### API Test

**Check if model is saved:**
```bash
# Get latest archived run
curl -s http://localhost:8000/api/archive/runs | jq '.runs[0] | {name, model_used, paths_count}'
```

**Expected Output:**
```json
{
  "name": "TM Swarm Run - ecommerce-platform - 2026-04-13 10:30",
  "model_used": "qwen3:14b",
  "paths_count": 4
}
```

---

## Benefits

### For Users
- ✅ See which model produced which results
- ✅ Compare model performance visually
- ✅ Reproduce results with same model
- ✅ Track model usage over time

### For Debugging
- ✅ Quickly identify if issues are model-specific
- ✅ Correlate output quality with model
- ✅ Test hypothesis about which models work better

### For Compliance
- ✅ Audit trail of which models were used
- ✅ Track model versions over time
- ✅ Compliance documentation

---

## Future Enhancements

### Possible Improvements
- [ ] Add model performance metrics in sidebar (avg paths, avg time)
- [ ] Filter archived runs by model
- [ ] Sort by model name
- [ ] Show model availability status in archive
- [ ] Add "Run with same model" button
- [ ] Model comparison view (side-by-side)
- [ ] Export model usage statistics

---

## Files Modified

### Backend
- ✅ `backend/app/services/archive_service.py` - Added model_used parameter
- ✅ `backend/app/routers/swarm.py` - Added get_current_model_name() helper
- ✅ `backend/app/routers/swarm.py` - Updated all archive_service.save_run() calls
- ✅ `backend/app/models/archived_run.py` - Already had model_used field (no change)

### Frontend
- ✅ `frontend/src/pages/ThreatModelPage.jsx` - Added model badge display
- ✅ `frontend/src/pages/ThreatModelPage.css` - Added model badge styling

### Documentation
- ✅ `backend/MODEL_NAME_IN_ARCHIVES.md` - This file

---

## Summary

The archived runs sidebar now displays which LLM model was used for each threat modeling run. The model name is captured from user selection or the default `.env` configuration and displayed as a badge in the sidebar. This feature helps users track, compare, and reproduce results across different models.

**Try it now**: Run a threat model, check the archived runs sidebar, and see the model badge! 🎯
