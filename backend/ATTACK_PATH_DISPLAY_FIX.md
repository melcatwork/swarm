# Attack Path Display Bug Fix

**Date**: 2026-04-13
**Issue**: Frontend not displaying technique information for attack paths
**Severity**: High - Complete loss of attack path details in UI

---

## Problem Description

When running threat modeling on IaC files (e.g., ecommerce-platform.tf), the attack paths were displayed in the frontend **without any technique information**. The attack path cards showed only validation metadata but lacked:

- ❌ Attack steps with technique IDs and names
- ❌ MITRE ATT&CK technique information
- ❌ Kill chain phase details
- ❌ Target assets and action descriptions
- ❌ Threat actor, difficulty, and impact type

The frontend was expecting complete attack path objects but receiving only adversarial validation metadata.

---

## Root Cause Analysis

### Data Flow Issue

The attack path data flows through three backend phases:

1. **Exploration Phase** → Discovers attack paths with full details (steps, techniques, threat_actor, etc.)
   - Paths use key: `"name"`

2. **Evaluation Phase** → Adds scoring data to attack paths
   - Evaluation scores use key: `"path_name"` (from LLM output)
   - But aggregate_scores() merges with exploration paths using `"name"`
   - Output (scored_paths) uses key: `"name"`

3. **Adversarial Phase** → Validates and challenges attack paths
   - Arbitrator LLM output uses key: `"path_name"`
   - Merge logic tried to look up paths using `"name"` from arbitrator output
   - **KEY MISMATCH** → Lookup always failed!

### The Bug

In `backend/app/swarm/crews.py` at line 1212:

```python
# BEFORE (BROKEN):
for final_path in final_paths:
    path_name = final_path.get("name", "")  # ❌ Arbitrator uses "path_name", not "name"!

    if path_name in scored_lookup:
        enriched_path = {**scored_lookup[path_name]}  # Never executed!
    else:
        enriched_path = {**final_path}  # Always fell through to here
```

**Result**: The merge always fell through to the `else` branch, using only the arbitrator's output (`final_path`) which had:
- ✅ Validation metadata (confidence, challenged, validation_notes)
- ❌ NO original path data (steps, techniques, threat_actor, evaluation scores)

---

## The Fix

### Code Changes

**File**: `backend/app/swarm/crews.py`
**Function**: `parse_adversarial_results()` (lines 1206-1241)

#### Change 1: Handle both key names

```python
# AFTER (FIXED):
for final_path in final_paths:
    # Try both "path_name" (from arbitrator LLM) and "name" (standard key)
    path_name = final_path.get("path_name") or final_path.get("name", "")

    if path_name and path_name in scored_lookup:
        enriched_path = {**scored_lookup[path_name]}  # ✅ Now works!
        logger.info(f"Merged arbitrator validation with scored path: {path_name}")
    else:
        enriched_path = {**final_path}
        if path_name:
            logger.warning(f"Could not find scored path for: {path_name}")
        else:
            logger.warning("Arbitrator path missing name/path_name key")
```

#### Change 2: Add more validation fields

```python
# Overlay arbitrator's validation data
enriched_path.update({
    "confidence": final_path.get("confidence", "medium"),
    "validation_notes": final_path.get("validation_notes", ""),
    "challenged": final_path.get("challenged", False),
    "challenge_resolution": final_path.get("challenge_resolution"),
    "challenged_steps": final_path.get("challenged_steps", []),  # NEW
    "status": final_path.get("status", "valid"),                # NEW
})
```

#### Change 3: Ensure frontend compatibility

```python
# Ensure "name" key exists for frontend compatibility
if "name" not in enriched_path and path_name:
    enriched_path["name"] = path_name
```

### What This Fixes

1. **Key Lookup**: Now checks both `"path_name"` and `"name"` to find the path name from arbitrator output
2. **Successful Merge**: The scored_lookup now finds matching paths correctly
3. **Complete Data**: Enriched paths now include:
   - ✅ All original exploration data (steps, techniques, threat_actor, etc.)
   - ✅ All evaluation scores (composite_score, feasibility, impact, etc.)
   - ✅ All adversarial validation data (confidence, challenged, validation_notes)
4. **Logging**: Added debug logging to track merge success/failures
5. **Additional Fields**: Preserved `challenged_steps` and `status` from arbitrator

---

## Frontend Expectations

The frontend (`ThreatModelPage.jsx`) expects attack paths with this structure:

```javascript
{
  // Core identification
  "name": "Attack Path Name",

  // Attack details
  "threat_actor": "APT29",
  "objective": "Gain access to S3 data",
  "difficulty": "medium",
  "impact_type": "confidentiality",

  // Attack steps (REQUIRED for display)
  "steps": [
    {
      "step_number": 1,
      "technique_id": "T1566.001",     // MITRE ATT&CK ID
      "technique_name": "Spearphishing", // Technique name
      "kill_chain_phase": "Initial Access",
      "target_asset": "IAM User Credentials",
      "action_description": "Send phishing email...",
      "outcome": "Obtain valid credentials",
      "prerequisite": "None",
      "mitigation": {
        "mitigation_id": "M1017",
        "mitigation_name": "User Training",
        "description": "...",
        "aws_service_action": "Enable MFA..."
      }
    }
  ],

  // Evaluation scores
  "evaluation": {
    "composite_score": 8.5,
    "feasibility_score": 9,
    "impact_score": 8,
    "detection_score": 7,
    // ...
  },

  // Adversarial validation
  "confidence": "high",
  "challenged": false,
  "validation_notes": "...",
  "challenged_steps": [],
  "status": "fully_valid"
}
```

---

## Testing

### Before Fix

**Observation**: Attack paths displayed with only:
```json
{
  "path_name": "Phishing-Driven Console Compromise",
  "status": "partially_valid",
  "challenged_steps": [...],
  "mitigations": [...],
  "confidence": "medium",
  "validation_notes": "",
  "challenged": false,
  "challenge_resolution": null
}
```

**Result**: Frontend couldn't display techniques because `steps` array was missing.

### After Fix

**Expected Output**: Attack paths should now include:
```json
{
  "name": "Phishing-Driven Console Compromise",
  "threat_actor": "Scattered Spider",
  "objective": "Compromise S3 data through console access",
  "difficulty": "medium",
  "impact_type": "confidentiality",
  "steps": [
    {
      "step_number": 1,
      "technique_id": "T1566.001",
      "technique_name": "Spearphishing Attachment",
      "kill_chain_phase": "Initial Access",
      "target_asset": "IAM User Credentials",
      "action_description": "Attacker sends spear-phishing email...",
      "outcome": "Obtain valid IAM user credentials"
    },
    // ... more steps
  ],
  "evaluation": {
    "composite_score": 7.8,
    "feasibility_score": 8,
    "impact_score": 8,
    "detection_score": 6,
    "novelty_score": 7,
    "coherence_score": 9
  },
  "confidence": "medium",
  "challenged": true,
  "challenged_steps": [...],
  "status": "partially_valid"
}
```

**Result**: Frontend displays complete kill chain with techniques, mitigations, and scores! ✅

---

## How to Verify

### 1. Restart Backend

```bash
cd /Users/bland/Desktop/swarm-tm
./stop-all.sh
./start-all.sh
```

### 2. Run Threat Model

1. Navigate to `http://localhost:5173`
2. Upload `samples/ecommerce-platform.tf`
3. Click "Quick Run (2 agents)"
4. Wait for completion (~5 minutes)

### 3. Check Attack Paths

**What to look for**:

✅ **Kill chain steps displayed** with technique IDs (e.g., T1566.001)
✅ **Technique names** shown next to IDs
✅ **Target assets** displayed for each step
✅ **Action descriptions** visible
✅ **Mitigations** expandable under each path
✅ **Composite scores** shown in score circles

**What should NOT happen**:

❌ Empty attack path cards
❌ Missing technique information
❌ Only showing validation metadata

### 4. Check Backend Logs

Look for these log messages confirming successful merge:

```
INFO: Merged arbitrator validation with scored path: Phishing-Driven Console Compromise
INFO: Merged arbitrator validation with scored path: S3 Data Exfiltration via Console
INFO: Arbitrator produced 3 final validated paths
```

**Warning messages** (if merge fails):
```
WARNING: Could not find scored path for: [path_name]
WARNING: Arbitrator path missing name/path_name key
```

---

## Impact

### Before
- ❌ Frontend showed incomplete attack paths
- ❌ No technique information visible
- ❌ No kill chain steps
- ❌ Evaluation scores missing
- ❌ Poor user experience

### After
- ✅ Complete attack path information displayed
- ✅ Full MITRE ATT&CK technique details
- ✅ Kill chain visualization with steps
- ✅ All evaluation scores visible
- ✅ Professional, informative UI

---

## Related Files

- ✅ `backend/app/swarm/crews.py` - Fixed merge logic (lines 1206-1241)
- 📖 `frontend/src/pages/ThreatModelPage.jsx` - Expects complete path structure
- 📖 `backend/app/routers/swarm.py` - Calls parse_adversarial_results()

---

## Lessons Learned

### Key Naming Consistency

**Problem**: Different phases used different key names for path identification:
- Exploration: `"name"`
- Evaluation LLM output: `"path_name"`
- Scored paths: `"name"` (after merge)
- Adversarial LLM output: `"path_name"`

**Solution**: Handle both keys when doing lookups, and normalize to `"name"` for frontend.

### LLM Output Reliability

LLMs don't always follow expected JSON structures. The arbitrator was asked to return paths with "all original data" but only returned validation metadata.

**Lesson**: Always merge LLM outputs with existing structured data, don't rely on LLMs to preserve complex nested structures.

### Debugging Structured Data

Adding logging at merge points makes it much easier to identify where data is being lost:

```python
logger.info(f"Merged arbitrator validation with scored path: {path_name}")
logger.warning(f"Could not find scored path for: {path_name}")
```

---

## Summary

The attack path display issue was caused by a **key name mismatch** during the merge of adversarial validation results with scored attack paths. The arbitrator LLM used `"path_name"` but the merge logic looked for `"name"`, causing all lookups to fail.

The fix ensures both keys are checked, properly merges the data, and preserves all attack path information (steps, techniques, scores) through to the frontend.

**Status**: ✅ Fixed and ready for testing
**Test**: Run threat modeling and verify complete attack path information displays in frontend
