# Testing the Sync Now Button

Quick visual guide to test the new manual intelligence sync button.

---

## Prerequisites

1. **Backend running**: `./start-all.sh` or `./start-all-tmux.sh`
2. **LLM credentials configured**: Check `.env` has either:
   - `AWS_BEARER_TOKEN_BEDROCK=...` OR
   - `ANTHROPIC_API_KEY=...`

---

## Visual Test Steps

### 1. Navigate to Threat Modeling Page

```
Open: http://localhost:5173/model
```

**Expected**:
- Page loads successfully
- "Persona Intelligence Status" panel visible above upload section

---

### 2. Locate the Sync Button

**What to look for**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Persona Intelligence Status  [69 patches applied]  [Sync Now ▼]    │
└─────────────────────────────────────────────────────────────────────┘
```

**Button location**: Right side of header, purple color

**Verify**:
- ✓ "Sync Now" button visible
- ✓ Button is purple (#667eea background)
- ✓ Hover shows tooltip: "Fetch latest threat intelligence and update personas"

---

### 3. Click "Sync Now" Button

**Immediate changes** (within 100ms):

```
┌─────────────────────────────────────────────────────────────────────┐
│ Persona Intelligence Status  [69 patches]  [Syncing... ▼]          │
├─────────────────────────────────────────────────────────────────────┤
│ ✓ Intelligence sync started in background. This may take 2-5...    │
└─────────────────────────────────────────────────────────────────────┘
```

**Verify**:
- ✓ Button text changes to "Syncing..."
- ✓ Button becomes gray and disabled
- ✓ Green status message appears below header
- ✓ Message says "Intelligence sync started in background..."

---

### 4. Wait 5-10 Seconds

**After auto-refresh** (~5 seconds):

```
┌─────────────────────────────────────────────────────────────────────┐
│ Persona Intelligence Status  [72 patches]  [Sync Now ▼]            │
├─────────────────────────────────────────────────────────────────────┤
│ ✓ Intelligence sync completed. Status refreshed.                   │
└─────────────────────────────────────────────────────────────────────┘
```

**Verify**:
- ✓ Button returns to "Sync Now" (clickable, purple)
- ✓ Status message updates to "Intelligence sync completed"
- ✓ Patch count may have increased (if new intelligence available)
- ✓ Last sync date unchanged (updates only when patches applied)

---

### 5. Expand Panel to See Details

**Click anywhere on header to expand**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Persona Intelligence Status  [72 patches]  [Sync Now ▲]            │
├─────────────────────────────────────────────────────────────────────┤
│ ✓ Intelligence sync completed. Status refreshed.                   │
├─────────────────────────────────────────────────────────────────────┤
│ ● Nation-State APT                 35 patches    2026-04-25        │
│ ● Scattered Spider                 13 patches    2026-04-25        │
│ ● Volt Typhoon                      9 patches    2026-04-25        │
│ ● APT29 — Cozy Bear                 6 patches    2026-04-25        │
│ ● Lazarus Group                     4 patches    2026-04-25        │
│ ● FIN7 / Carbanak                   1 patches    2026-04-25        │
│ ● Cloud-Native Attacker             1 patches    2026-04-25        │
│ ● Ransomware Operator                           base only          │
│ ● Supply Chain Attacker                         base only          │
│ ● Insider Threat                                base only          │
│ ● Cryptominer                                   base only          │
│ ● Red Team Operator                             base only          │
│ ● Script Kiddie                                 base only          │
└─────────────────────────────────────────────────────────────────────┘
```

**Verify**:
- ✓ Table shows all 13 personas
- ✓ Personas with patches show green/amber/red dots
- ✓ Patch counts and dates visible
- ✓ "base only" shown for personas without patches

---

## Error Scenario Test

### Test No Credentials Error

1. **Stop backend**
2. **Comment out LLM credentials in `.env`**:
   ```bash
   # AWS_BEARER_TOKEN_BEDROCK=...
   # ANTHROPIC_API_KEY=...
   ```
3. **Restart backend**
4. **Click "Sync Now"**

**Expected result**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Persona Intelligence Status  [69 patches]  [Sync Now ▼]            │
├─────────────────────────────────────────────────────────────────────┤
│ ✗ Sync failed: AWS_BEARER_TOKEN_BEDROCK or ANTHROPIC_API_KEY...   │
└─────────────────────────────────────────────────────────────────────┘
```

**Verify**:
- ✓ Status message appears (red background)
- ✓ Message starts with "✗ Sync failed:"
- ✓ Error mentions credential requirement
- ✓ Button returns to clickable state

---

## Backend Verification

### Check Sync Actually Runs

**Open backend logs**:
```bash
tail -f logs/backend.log
```

**Click "Sync Now" button**

**Expected log entries**:
```
INFO:     127.0.0.1:XXXXX - "POST /api/swarm/sync-intelligence HTTP/1.1" 200 OK
INFO:     Intelligence sync completed: 0
```

**Check sync output** (if --force was successful):
```bash
ls -lah logs/intel-sync.log
# File should exist but might be empty (sync runs via subprocess)
```

---

## API Endpoint Test

**Test backend directly**:
```bash
curl -X POST http://localhost:8000/api/swarm/sync-intelligence | jq
```

**Expected response**:
```json
{
  "status": "started",
  "message": "Intelligence sync started in background. This may take 2-5 minutes. Refresh the persona status panel to see updates.",
  "provider": "bedrock"
}
```

**Verify**:
- ✓ HTTP 200 status
- ✓ `status: "started"`
- ✓ Provider field shows "bedrock" or "anthropic"

---

## Integration Test

### Full Sync Flow with New Patches

**Scenario**: Ensure new patches are actually generated and applied

1. **Check current state**:
   ```bash
   sqlite3 backend/app/swarm/vuln_intel/intel.db \
     "SELECT COUNT(*) FROM persona_patches WHERE applied = 1;"
   # Example: 69
   ```

2. **Mark some signals as unprocessed** (simulate new intelligence):
   ```bash
   sqlite3 backend/app/swarm/vuln_intel/intel.db \
     "UPDATE threat_intel_signals SET processed = 0 WHERE id IN (SELECT id FROM threat_intel_signals LIMIT 5);"
   ```

3. **Click "Sync Now" in UI**

4. **Wait 2-5 minutes**

5. **Check patch count increased**:
   ```bash
   sqlite3 backend/app/swarm/vuln_intel/intel.db \
     "SELECT COUNT(*) FROM persona_patches WHERE applied = 1;"
   # Example: 72 (should be higher if patches generated)
   ```

6. **Verify in UI**:
   - Patch count badge updated
   - Expanded view shows new patches
   - Last sync date unchanged (only updates when patches created)

---

## Performance Test

### Measure Sync Duration

**Start timer**:
```bash
time curl -X POST http://localhost:8000/api/swarm/sync-intelligence
```

**Expected**:
- HTTP response: ~50-200ms (immediate return)
- Background sync: 2-5 minutes

**Check backend process**:
```bash
ps aux | grep sync_intel.py
# Should show running python process during sync
```

**After completion**:
```bash
# Process should no longer exist
ps aux | grep sync_intel.py
```

---

## Browser Console Test

### Check for JavaScript Errors

1. **Open browser dev tools** (F12)
2. **Go to Console tab**
3. **Click "Sync Now" button**
4. **Check for errors**

**Expected console output**:
```
POST http://localhost:8000/api/swarm/sync-intelligence 200 OK
```

**No errors should appear**

---

## Multiple Clicks Test

### Verify Button Prevents Double-Clicks

1. **Click "Sync Now"**
2. **Immediately click again** (while showing "Syncing...")

**Expected**:
- ✓ Second click does nothing
- ✓ Only one sync process runs
- ✓ Button stays disabled until first sync completes

---

## Summary Checklist

Run through all these checks:

### Visual
- [ ] Button visible in panel header
- [ ] Button is purple when idle
- [ ] Button shows "Syncing..." when active
- [ ] Button grayed out during sync
- [ ] Status message appears (green/red)
- [ ] Status message auto-updates after 5 seconds

### Functional
- [ ] Clicking button triggers sync
- [ ] Sync runs in background
- [ ] Backend returns HTTP 200 immediately
- [ ] Status refreshes after sync
- [ ] Patch counts update when new intelligence available
- [ ] Error shown when credentials missing

### Performance
- [ ] UI remains responsive during sync
- [ ] No JavaScript errors in console
- [ ] Backend logs show sync activity
- [ ] Sync completes within 10 minutes
- [ ] Multiple clicks don't spawn multiple syncs

---

## Success Criteria

✅ **All checks passed**: Feature is working correctly

⚠️ **Some checks failed**: Review `SYNC_BUTTON_FEATURE.md` for troubleshooting

❌ **Button not visible**: Verify frontend built correctly (`npm run build`)

---

**Test Date**: ____________
**Tester**: ____________
**Result**: ✅ Pass / ⚠️ Partial / ❌ Fail
**Notes**: _______________________________________________
