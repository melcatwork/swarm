# Overall Risk Reduction - Redefined to Primary and Alternate Attack Paths Only

**Date**: 2026-04-23  
**Status**: ✅ **IMPLEMENTED** (Commit: 6518dbd)  
**Change Type**: Feature Refinement

---

## Changes Made

### 1. Overall Risk Reduction Now ONLY Includes Primary and Alternate Attack Paths

**Before**:
- Calculation included ALL paths in `final_paths`
- Primary + Alternates + Agent explorations = Overall %

**After**:
- Calculation ONLY includes vulnerability-grounded paths (source: `'confirmed_vuln_synthesis'`)
- Primary + Alternates ONLY = Overall %
- Agent explorations excluded from percentage

---

### 2. Renamed "Chain" to "Attack Path"

**Before**:
- "Primary chain: CVE-2023-1234 → CVE-2023-5678"
- "Alternate-1 chain: CVE-2023-1234 → CVE-2023-9999"

**After**:
- "Primary attack path: CVE-2023-1234 → CVE-2023-5678"
- "Alternate-1 attack path: CVE-2023-1234 → CVE-2023-9999"

---

### 3. Updated Residual Risk Assessment UI Text

**Before**:
```
CSA CII 5×5 Risk Matrix — After applying X mitigations
...
Overall Risk Reduction
Achieved through applied mitigations
```

**After**:
```
CSA CII 5×5 Risk Matrix — After applying X mitigations on primary and alternate attack paths
...
Overall Risk Reduction
For primary and alternate attack paths
```

---

## Implementation Details

### Backend Changes

**File**: `backend/app/swarm/mitigations.py` (lines 626-643)

**Changed from**:
```python
original_csa_total = sum([
    path.get("csa_risk_score", {}).get("risk_level", 0)
    for path in attack_paths  # ALL PATHS
])
```

**Changed to**:
```python
# ONLY include primary and alternate attack paths (confirmed_vuln_synthesis)
# Excludes agent exploration paths
original_csa_total = sum([
    path.get("csa_risk_score", {}).get("risk_level", 0)
    for path in attack_paths
    if path.get("source") == "confirmed_vuln_synthesis"  # FILTER!
])
```

Same filtering applied to `residual_csa_total` calculation.

**File**: `backend/app/swarm/vuln_intel/chain_assembler.py` (line 238)

**Changed from**:
```python
name = f'{chain_type.title()} chain: ' + ' → '.join(vuln_ids[:2])
```

**Changed to**:
```python
name = f'{chain_type.title()} attack path: ' + ' → '.join(vuln_ids[:2])
```

### Frontend Changes

**File**: `frontend/src/components/ResidualRiskSummary.jsx`

**Line 64** - Changed subtitle:
```jsx
// Before:
CSA CII 5×5 Risk Matrix — After applying {mitigationsApplied} mitigation{mitigationsApplied !== 1 ? 's' : ''}

// After:
CSA CII 5×5 Risk Matrix — After applying {mitigationsApplied} mitigation{mitigationsApplied !== 1 ? 's' : ''} on primary and alternate attack paths
```

**Line 133** - Changed description:
```jsx
// Before:
Achieved through applied mitigations

// After:
For primary and alternate attack paths
```

---

## Example Impact

### Before Change

**6 Total Paths**:
1. Primary attack path (confirmed vuln): 20/25 → 5/25
2. Alternate-1 attack path (confirmed vuln): 15/25 → 3/25
3. Alternate-2 attack path (confirmed vuln): 18/25 → 4/25
4. Agent path (Hacktivist): 12/25 → 8/25
5. Agent path (Nation State): 25/25 → 15/25
6. Agent path (Script Kiddie): 10/25 → 2/25

**Calculation**:
- Original total: 20 + 15 + 18 + 12 + 25 + 10 = **100**
- Residual total: 5 + 3 + 4 + 8 + 15 + 2 = **37**
- **Overall Risk Reduction: 63%**

---

### After Change

**Only 3 Confirmed Vulnerability Paths Counted**:
1. Primary attack path: 20/25 → 5/25 ✅ COUNTED
2. Alternate-1 attack path: 15/25 → 3/25 ✅ COUNTED
3. Alternate-2 attack path: 18/25 → 4/25 ✅ COUNTED
4. Agent path (Hacktivist): 12/25 → 8/25 ❌ EXCLUDED
5. Agent path (Nation State): 25/25 → 15/25 ❌ EXCLUDED
6. Agent path (Script Kiddie): 10/25 → 2/25 ❌ EXCLUDED

**Calculation**:
- Original total: 20 + 15 + 18 = **53**
- Residual total: 5 + 3 + 4 = **12**
- **Overall Risk Reduction: 77%**

---

## Rationale for Change

### User Intent
Users wanted the "Overall Risk Reduction %" to reflect only the vulnerability-grounded attack vectors (CVE-based), not the creative agent exploration scenarios.

### Benefits

1. **Clearer Metrics**
   - Percentage reflects confirmed, evidence-based attack paths only
   - More meaningful for reporting CVE remediation effectiveness

2. **Focused on Known Vulnerabilities**
   - Primary and alternate paths are grounded in actual CVEs
   - Easier to justify to stakeholders ("We mitigated 77% of confirmed vulnerability risk")

3. **Agent Paths Still Visible**
   - Agent exploration paths still analyzed, displayed, and show individual risk reduction
   - Just not included in the aggregate percentage
   - Users can still see per-path mitigation effectiveness for agent scenarios

4. **More Accurate Risk Posture**
   - Vulnerability-based paths represent known, exploitable weaknesses
   - Agent paths represent theoretical scenarios (may or may not be exploitable)
   - Separating them provides clearer risk posture assessment

---

## What Still Includes Agent Paths

**Post-mitigation analysis continues to process ALL paths**:
- ✅ Agent exploration paths still analyzed for mitigation effectiveness
- ✅ Individual residual risk scores calculated for each agent path
- ✅ Agent paths displayed in UI with original → residual risk bands
- ✅ Users can apply mitigations to agent paths and see results

**Only excluded from**:
- ❌ Overall risk reduction percentage calculation
- ❌ "Residual Risk Assessment" summary box

---

## UI Display Changes

### Residual Risk Assessment Box

**Before**:
```
┌─────────────────────────────────────────────────┐
│ Residual Risk Assessment (Post-Mitigation)      │
│ CSA CII 5×5 Risk Matrix — After applying 42     │
│ mitigations                                      │
│                                                  │
│ ↓ 63%  Overall Risk Reduction                   │
│        Achieved through applied mitigations     │
│                                                  │
│ Residual risk distribution — 6 paths re-scored  │
└─────────────────────────────────────────────────┘
```

**After**:
```
┌─────────────────────────────────────────────────┐
│ Residual Risk Assessment (Post-Mitigation)      │
│ CSA CII 5×5 Risk Matrix — After applying 42     │
│ mitigations on primary and alternate attack     │
│ paths                                            │
│                                                  │
│ ↓ 77%  Overall Risk Reduction                   │
│        For primary and alternate attack paths   │
│                                                  │
│ Residual risk distribution — 3 paths re-scored  │
└─────────────────────────────────────────────────┘
```

### Attack Path Names

**Before**:
- Primary chain: CVE-2023-38408 → CVE-2024-6387
- Alternate-1 chain: CVE-2023-38408 → CVE-2024-1234
- Alternate-2 chain: CVE-2024-5555 → CVE-2024-6387

**After**:
- Primary attack path: CVE-2023-38408 → CVE-2024-6387
- Alternate-1 attack path: CVE-2023-38408 → CVE-2024-1234
- Alternate-2 attack path: CVE-2024-5555 → CVE-2024-6387

---

## Affected Run Types

All 4 run types implement these changes consistently:

1. ✅ **Full Swarm Pipeline**
2. ✅ **Quick Run (2 Agents)**
3. ✅ **Single Agent**
4. ✅ **Stigmergic Swarm**

---

## Testing Verification

To verify the changes work correctly:

1. **Run any threat model** with confirmed vulnerabilities
2. **Check path names** - Should say "attack path" not "chain"
3. **Apply mitigations** to all paths
4. **View Residual Risk Assessment**:
   - Overall % should reflect only confirmed vuln paths
   - Text should say "on primary and alternate attack paths"
5. **Check backend logs**:
   ```
   INFO: CSA-based risk reduction: 53 → 12 (77.4% reduction)
   ```
6. **Compare path counts**:
   - "X paths re-scored" should match number of confirmed vuln paths only
   - Agent paths excluded from count

---

## Breaking Changes

**None** - This is a refinement, not a breaking change:
- Agent paths still analyzed and displayed
- API response structure unchanged
- Only the percentage calculation scope changed

---

**Status**: ✅ Implemented and committed  
**Commit**: 6518dbd  
**Date**: 2026-04-23  
**Impact**: More accurate and meaningful overall risk reduction metrics
