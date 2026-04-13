# Attack Paths Not Showing - Debugging Report

**Date**: 2026-04-13
**Issue**: Frontend not showing attack paths even though backend completes successfully

---

## Root Cause Identified

The exploration phase is producing **0 attack paths** (`"raw_paths_found": 0`), which means the frontend has nothing to display.

### Evidence

Checking recent archived runs:
```bash
curl http://localhost:8000/api/archive/runs
```

Recent runs with qwen3:14b (current default):
- run_20260413_032749: **0 paths**
- run_20260413_032329: **0 paths**
- run_20260413_032021: **0 paths**
- run_20260413_031545: **0 paths**
- run_20260413_025601: **0 paths**

Older runs with working models:
- run_20260413_020838 (gemma4:e4b): **5 paths** ✓
- run_20260412_152736 (qwen3:14b): **4 paths** ✓

---

## Problem Analysis

### 1. Quality Validation Too Strict
I added quality validation that rejects paths with >50% fallback values:
- `technique_id == "T1000"`
- `target_asset == "unknown_asset"`
- `technique_name == "Unknown Technique"`

**Fix Applied**: Relaxed threshold from 50% to 100% (only reject if ALL steps are fallback)

### 2. Model Not Producing Valid Output
The qwen3:14b model may be:
- Not generating valid JSON
- Generating JSON in unexpected format
- Producing empty responses

**Fix Applied**: Added detailed logging to see:
- JSON parse success/failure
- Number of paths in parsed output
- How many paths pass validation
- Which paths are being rejected and why

---

## Changes Made for Debugging

### File: `backend/app/swarm/crews.py`

**1. Relaxed Quality Validation** (Line ~479):
```python
# Before: reject if >50% fallback
if fallback_ratio > 0.5:

# After: only reject if 100% fallback
if fallback_ratio >= 1.0:
```

**2. Added JSON Parse Logging** (Line ~358):
```python
try:
    parsed_output = json.loads(output_text)
    logger.info(f"✓ Successfully parsed JSON from task {idx + 1}")
except json.JSONDecodeError as json_err:
    logger.error(f"✗ JSON parse error in task {idx + 1}: {json_err}")
    logger.debug(f"Failed JSON content: {output_text[:500]}")
    continue
```

**3. Added Path Processing Logs**:
- Logs when paths are added: `✓ Added attack path: {name}`
- Logs fallback warnings but still adds paths
- Tracks paths before/after each task

---

## How to Debug

### Step 1: Restart Backend with Logging
```bash
cd /Users/bland/Desktop/swarm-tm/backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000 --log-level debug
```

### Step 2: Run Threat Modeling
1. Open frontend at http://localhost:5173
2. Upload an IaC file (e.g., ecommerce-platform.tf)
3. Click "Quick Run (2 agents)"
4. Watch the backend terminal output

### Step 3: Look for These Log Messages

**Success Indicators**:
```
✓ Successfully parsed JSON from task 1
Task 1: Parsed as list with X items
✓ Added attack path: <name> with X steps
Task 1 complete: Processed X raw paths, added X valid paths
```

**Failure Indicators**:
```
✗ JSON parse error in task 1
Task 1 output is neither list nor dict
Attack path has X/X steps with fallback values, skipping
Missing technique_id in step
```

---

## Expected Behavior After Fix

With the relaxed validation, the backend should now:
1. ✅ Accept paths even if some steps have fallback values
2. ✅ Log detailed information about what's being parsed
3. ✅ Show which paths are being added vs rejected
4. ✅ Return paths to frontend for display

---

## If Issue Persists

### Check 1: Model Output Quality
If backend logs show:
- "JSON parse error" → Model not producing valid JSON
- "Missing technique_id" → Model not following prompt format
- "0 paths in parsed output" → Model returning empty responses

**Solution**: Try a different model in the UI dropdown (select gemma4:e4b or another model)

### Check 2: Model Availability
```bash
# Check which models are pulled
curl http://localhost:11434/api/tags

# Pull qwen3:14b if missing
ollama pull qwen3:14b
```

### Check 3: Frontend Not Receiving Data
If backend shows paths but frontend doesn't:
1. Open browser DevTools → Network tab
2. Find the `/api/swarm/run/quick` request
3. Check the response JSON
4. Look for `final_paths` array

**Expected Response**:
```json
{
  "status": "ok",
  "asset_graph": {...},
  "final_paths": [
    {
      "name": "Attack path name",
      "steps": [...]
    }
  ]
}
```

---

## Quick Test Command

Test the API directly:
```bash
# Check latest archived run
curl -s http://localhost:8000/api/archive/runs | jq '.runs[0]'

# Get full run data
RUN_ID=$(curl -s http://localhost:8000/api/archive/runs | jq -r '.runs[0].run_id')
curl -s "http://localhost:8000/api/archive/runs/$RUN_ID" | jq '.result | {
  status,
  raw_paths: .exploration_summary.raw_paths_found,
  final_paths: (.final_paths | length)
}'
```

**Expected Output**:
```json
{
  "status": "ok",
  "raw_paths": 4,
  "final_paths": 4
}
```

---

## Rollback Instructions

If the relaxed validation causes too many low-quality paths:

**Restore Original Validation** in `backend/app/swarm/crews.py`:
```python
# Change back from 1.0 to 0.5
if fallback_ratio > 0.5:  # More than 50% fallback values
    logger.warning(...)
    continue
```

---

## Summary

**Issue**: Recent runs with qwen3:14b producing 0 attack paths
**Root Cause**: Either model output quality OR overly strict validation
**Fix Applied**:
1. Relaxed validation threshold (50% → 100%)
2. Added detailed logging to diagnose issue
3. Ready to test and observe logs

**Next Steps**:
1. Restart backend with new logging
2. Run threat modeling
3. Check backend logs for diagnostic info
4. Adjust validation threshold based on results

The frontend will automatically display paths once the backend starts returning them in `final_paths` array.
