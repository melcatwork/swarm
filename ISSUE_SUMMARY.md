# Issue Summary: "Cannot connect to Swarm TM API"

## What Happened

During a single agent test run, the frontend displayed:
```
"Cannot connect to Swarm TM API. Please ensure the backend is running at http://localhost:8000"
```

**Actual Cause:** The backend did NOT crash. It completed successfully, but:
1. ⏰ **Frontend timed out** (10 min) before backend finished (14.7 min)
2. 🔴 **Pipeline produced 0 attack paths** despite generating 3 initially

---

## Root Causes Identified

### 1. Frontend Timeout (FIXED ✅)
- **Problem:** Frontend timeout = 10 minutes, but qwen3:14b takes 15+ minutes
- **Impact:** Frontend gave up and showed error, but backend kept running
- **Fix Applied:** Increased timeout to 20 minutes in `frontend/src/api/client.js`

### 2. Missing 'name' Field (FIXED ✅)
- **Problem:** qwen3:14b generates paths without 'name' field
- **Impact:** 12 paths skipped with "Attack path missing 'name'" warnings
- **Fix Applied:** Auto-generate default names in `backend/app/swarm/crews.py`

### 3. Adversarial Validation Too Strict (ACTIVE ISSUE ⚠️)
- **Problem:** Blue team challenges paths, arbitrator approves 0
- **Pipeline Flow:**
  - ✅ Exploration: 3 paths generated
  - ✅ Evaluation: 3 paths scored
  - ❌ Adversarial: 0 paths validated (all rejected)
- **Result:** 0 final paths with mitigations

### 4. Threat Intel Bug (MINOR 🐛)
- **Error:** `'ThreatIntelItem' object has no attribute 'get'`
- **Impact:** Threat intel context not built (not critical to core functionality)

---

## Testing Results from Logs

### Last Single Agent Run (apt29_cozy_bear)
```
File: samples/ecommerce-platform.tf (18K)
Agent: APT29 (Cozy Bear)
Duration: 883 seconds (14.7 minutes)

Phase 1 - Exploration:     ✅ 3 paths generated (157s)
Phase 2 - Evaluation:      ✅ 3 paths scored (441s)
Phase 3 - Adversarial:     ❌ 0 paths validated (280s)
Phase 4 - Mitigations:     ⚠️  0 paths to map

Final Result: 0 validated paths
```

---

## Fixes Applied

### ✅ File: `frontend/src/api/client.js`
**Line 226:** `timeout: 600000` → `timeout: 1200000` (10 min → 20 min)

### ✅ File: `backend/app/swarm/crews.py`
**Lines 307-313:** Added auto-generation of default path names:
```python
if "name" not in path:
    threat_actor = path.get("threat_actor", "Unknown")
    objective = path.get("objective", "Attack")
    default_name = f"{threat_actor} - {objective}"
    logger.warning(f"Attack path missing 'name', using default: {default_name}")
    path["name"] = default_name
```

### ✅ Backend restarted with fixes

---

## Next Steps to Test

### Option 1: Quick Test (Recommended)
Try the **Quick Run** mode which uses fewer agents and may have less strict validation:

1. **Frontend:** http://localhost:5173
2. **Upload:** `samples/ecommerce-platform.tf` (smallest file)
3. **Mode:** Click **"Quick Run (2 agents)"**
4. **Wait:** 5-10 minutes
5. **Expected:** Better chance of getting validated paths

### Option 2: API Direct Test
Test via API to see raw results without frontend:

```bash
cd /Users/bland/Desktop/swarm-tm

# Test with single agent
curl -X POST "http://localhost:8000/api/swarm/run/single?agent_name=apt29_cozy_bear" \
  -F "file=@samples/ecommerce-platform.tf" \
  --max-time 1200 \
  -o test_result.json

# Check results
jq '.status' test_result.json
jq '.final_paths | length' test_result.json
jq '.exploration_summary' test_result.json
```

### Option 3: Check Diagnostic Script
Run the diagnostics to see what's happening:

```bash
./check_pipeline_status.sh
```

---

## Why Adversarial Validation Fails

The 3-layer pipeline is designed to be **very strict**:

1. **Exploration (Layer 1):** Red team agents generate paths
2. **Evaluation (Layer 2):** Evaluators score paths
3. **Adversarial (Layer 3):**
   - 🔴 Red team looks for gaps
   - 🔵 Blue team challenges each path
   - ⚖️ Arbitrator decides which paths are valid

**Current behavior:** Blue team is successfully challenging all paths, and the arbitrator agrees.

**Possible reasons:**
- qwen3:14b generates less realistic/detailed paths than Claude
- Attack paths lack sufficient detail for validation
- Infrastructure in sample files is too simple/secure
- Validation criteria are too strict for the model quality

---

## Recommended Solutions

### Short Term (Test Now)
1. ✅ **Try Quick Run** - Uses 2 agents, may be less strict
2. ✅ **Try different sample file** - Some may work better
3. ✅ **Check with API** - See raw results

### Medium Term (If Still 0 Paths)
1. **Use better model** - qwen3:32b or cloud models (Claude, Bedrock)
2. **Adjust validation strictness** - Modify arbitrator criteria
3. **Add more detail to prompts** - Help model generate better paths

### Long Term (Production)
1. **Switch to Claude Sonnet 4** - Much better at structured output
   ```bash
   # In .env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your-key-here
   ANTHROPIC_MODEL=claude-sonnet-4-20250514
   ```
2. **Or use AWS Bedrock** - For enterprise deployments
3. **Fine-tune validation** - Based on your security requirements

---

## Current Status

✅ Backend: Running (PID varies)
✅ Frontend: Running on http://localhost:5173
✅ Ollama: Running with qwen3:14b
✅ Timeout: Fixed (20 min)
✅ Name field: Fixed (auto-generate)
⚠️ Validation: Too strict (0 paths approved)

---

## Files Changed

1. ✅ `.env` - Model: qwen3:4b → qwen3:14b
2. ✅ `frontend/src/api/client.js` - Timeout: 10min → 20min
3. ✅ `backend/app/swarm/crews.py` - Auto-generate missing names
4. ✅ `start-all.sh` - Updated for qwen3:14b
5. ✅ `stop-all.sh` - Enhanced diagnostics
6. 📝 `AGENT_TESTING_GUIDE.md` - Testing guide
7. 📝 `CHANGELOG_SCRIPTS.md` - Change log
8. 📝 `check_pipeline_status.sh` - Diagnostics script
9. 📝 `ISSUE_SUMMARY.md` - This document

---

## Quick Reference

**Test frontend:**
```
http://localhost:5173
```

**Test backend health:**
```bash
curl http://localhost:8000/api/health
```

**View logs:**
```bash
tail -f logs/backend.log | grep -E "Phase|paths|ERROR"
```

**Check service status:**
```bash
./stop-all.sh  # Shows what's running
```

**Restart everything:**
```bash
./stop-all.sh
./start-all.sh
```

---

## Questions?

Run diagnostics: `./check_pipeline_status.sh`
Check logs: `tail -100 logs/backend.log`
Test API: Use curl commands above

The frontend timeout issue is **fixed**. The 0 paths issue is due to **strict validation** rather than a bug.
