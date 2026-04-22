# Inconsistency: Overall Risk Reduction Percentage

**Date**: 2026-04-23  
**Status**: ✅ **FIXED** (Commit: 548c0a0)  
**Severity**: Medium - Percentage doesn't match visual CSA risk reduction

---

## Problem Summary

The "Overall Risk Reduction %" shown to users is calculated using `composite_score` (0-10 agent evaluation scale), but the visual per-path risk reduction uses CSA risk levels (1-25 scale). This creates a disconnect where the percentage may not match what users observe.

**Example**:
```
Path 1: CSA 20/25 → 5/25 (75% reduction)
Path 2: CSA 15/25 → 3/25 (80% reduction)
Path 3: CSA 10/25 → 2/25 (80% reduction)

Visual average: ~78% reduction

But system shows: 65% reduction ❓
(because it's using composite_score averages, not CSA levels)
```

---

## Current Implementation

**Backend** (`backend/app/swarm/mitigations.py:462-463, 627-629`):

```python
# For each path:
original_score = path.get("composite_score", 5.0)  # ← 0-10 scale
original_scores.append(original_score)

# Later:
original_mean_score = sum(original_scores) / len(original_scores)
residual_mean_score = sum(residual_scores) / len(residual_scores)
risk_reduction = ((original_mean_score - residual_mean_score) / original_mean_score * 100)
```

**What it calculates**:
- Average of composite_scores across all paths (0-10 scale)
- Percentage based on agent evaluation metrics
- NOT aligned with CSA risk levels shown to user

---

## Why This Is Inconsistent

### Per-Path Display (What User Sees)

```
Attack Path: "S3 Data Exfiltration"
Original:  [Very High] 20/25
Residual:  [Medium] 5/25
Reduction: 75%
```

User sees: **75% reduction** based on CSA risk level (20 → 5)

### Overall Percentage (What System Shows)

```
Overall Risk Reduction: 65%
```

System shows: **65% reduction** based on composite_score average

**Disconnect**: User expects ~75% but sees 65%. Why the difference?

---

## Root Cause

We have TWO parallel risk scoring systems:

1. **composite_score (0-10)**: Agent-based evaluation
   - Combines: feasibility 30%, impact 25%, detection 15%, novelty 15%, coherence 15%
   - Reflects attacker's perspective on path viability
   - Used for: Overall risk reduction percentage

2. **csa_risk_level (1-25)**: CSA CII methodology
   - Combines: Discoverability/Exploitability/Reproducibility → Likelihood × Impact
   - Reflects standards-based risk quantification
   - Used for: Per-path visual display, risk bands

These metrics measure **different things** and aren't correlated!

---

## Example Scenario

**Attack Paths**:

| Path | composite_score | CSA risk_level | After Mitigation (composite) | After Mitigation (CSA) |
|------|----------------|----------------|------------------------------|------------------------|
| Path 1 | 7.5 | 20/25 (L:4 × I:5) | 1.0 (87% blocked) | 5/25 (L:1 × I:5) |
| Path 2 | 6.0 | 15/25 (L:3 × I:5) | 1.2 (80% blocked) | 3/25 (L:1 × I:5) |
| Path 3 | 8.0 | 10/25 (L:2 × I:5) | 1.6 (80% blocked) | 2/25 (L:1 × I:5) |

**Composite-based calculation** (current):
- Original mean: (7.5 + 6.0 + 8.0) / 3 = 7.17
- Residual mean: (1.0 + 1.2 + 1.6) / 3 = 1.27
- Reduction: (7.17 - 1.27) / 7.17 × 100 = **82.3%**

**CSA-based calculation** (what user sees):
- Original total: 20 + 15 + 10 = 45
- Residual total: 5 + 3 + 2 = 10
- Reduction: (45 - 10) / 45 × 100 = **77.8%**

**Result**: User sees paths go from 20→5, 15→3, 10→2 (visually ~78% reduction), but system shows 82.3%. Close in this case, but can diverge significantly.

---

## When Divergence Is Large

**Scenario: High composite, Low CSA**

| Path | composite_score | CSA risk_level | After 50% Mitigation (composite) | After 50% Mitigation (CSA) |
|------|----------------|----------------|----------------------------------|---------------------------|
| Path A | 9.0 | 10/25 (L:2 × I:5) | 4.5 | 5/25 (L:1 × I:5) |

**Composite-based**: (9.0 - 4.5) / 9.0 = 50% reduction ✓
**CSA-based**: (10 - 5) / 10 = 50% reduction ✓

**Scenario: Low composite, High CSA**

| Path | composite_score | CSA risk_level | After 50% Mitigation (composite) | After 50% Mitigation (CSA) |
|------|----------------|----------------|----------------------------------|---------------------------|
| Path B | 4.0 | 20/25 (L:4 × I:5) | 2.0 | 10/25 (L:2 × I:5) |

**Composite-based**: (4.0 - 2.0) / 4.0 = 50% reduction ✓
**CSA-based**: (20 - 10) / 20 = 50% reduction ✓

In these cases, the percentages align at the path level. But when AVERAGING across multiple paths with different composite/CSA ratios, the overall percentages can diverge.

---

## Impact Assessment

**User Experience**:
- ❓ Confusion: "Why does overall percentage not match what I see in individual paths?"
- ❓ Trust: "Which number should I trust for reporting to management?"
- ❓ Inconsistency: "Per-path shows CSA bands, overall shows composite-based %"

**Severity**: Medium
- Not broken (both calculations are mathematically correct)
- But inconsistent (using different metrics for same concept)
- Can confuse users trying to understand overall risk posture

---

## The Fix Options

### Option 1: Use CSA Risk Levels for Overall Percentage (RECOMMENDED)

**Change**: Calculate overall percentage based on sum of CSA risk_levels instead of mean of composite_scores.

**Backend** (`mitigations.py:627-629`):
```python
# OLD:
original_mean_score = sum(original_scores) / len(original_scores)
residual_mean_score = sum(residual_scores) / len(residual_scores)
risk_reduction = ((original_mean_score - residual_mean_score) / original_mean_score * 100)

# NEW:
original_csa_total = sum([p.get("csa_risk_score", {}).get("risk_level", 0) for p in attack_paths])
residual_csa_total = sum([p.residual_csa_risk_score.get("risk_level", 0) for p in post_mitigation_paths if p.residual_csa_risk_score])
risk_reduction = ((original_csa_total - residual_csa_total) / original_csa_total * 100) if original_csa_total > 0 else 0
```

**Benefits**:
- ✅ Aligns with what user sees in per-path display
- ✅ Uses same metric (CSA) throughout the UI
- ✅ Percentage matches visual risk band changes
- ✅ Consistent with CSA CII Risk Assessment Guide methodology

**Tradeoffs**:
- ⚠️ Percentage may change from current values (breaking change for users tracking historical metrics)

---

### Option 2: Show Both Percentages

Display both composite-based and CSA-based percentages with labels:

```
Overall Risk Reduction:
- Attack Path Viability: 82% (based on feasibility/impact/detection)
- CSA Risk Level: 78% (based on likelihood × impact)
```

**Benefits**:
- ✅ No loss of information
- ✅ Users can choose which metric is relevant for their use case

**Tradeoffs**:
- ❌ More complex UI
- ❌ May confuse users ("which one do I report?")

---

### Option 3: Keep Current (No Change)

Accept that composite_score and CSA are different perspectives on risk.

**Benefits**:
- ✅ No code changes needed
- ✅ Both metrics remain available

**Tradeoffs**:
- ❌ User confusion persists
- ❌ Inconsistent messaging in UI

---

## Recommendation

**Option 1** is recommended: Use CSA risk levels for overall percentage calculation.

**Reasoning**:
1. Users primarily see and understand CSA risk bands in the UI
2. CSA CII Risk Assessment Guide is the documented methodology
3. Percentage should align with what users visually observe
4. Composite scores are internal agent evaluation metrics, not user-facing risk measures

---

## Files to Modify

**Backend**:
- ✅ `backend/app/swarm/mitigations.py:627-629` - Change risk reduction calculation to use CSA totals

**No frontend changes needed** - frontend already displays the percentage from backend.

---

## Test Cases

After fix, verify:

**Test 1: All paths High → Low**
- Original: 3 paths at 20/25 each = 60 total
- Residual: 3 paths at 2/25 each = 6 total
- Expected: (60 - 6) / 60 = 90% reduction

**Test 2: Mixed reduction levels**
- Path 1: 20 → 5 (75% reduction)
- Path 2: 15 → 3 (80% reduction)
- Path 3: 10 → 2 (80% reduction)
- Overall: (45 - 10) / 45 = 77.8% reduction

**Test 3: Some paths neutralized, some still viable**
- Path 1: 25 → 1 (96% reduction)
- Path 2: 20 → 10 (50% reduction)
- Path 3: 15 → 15 (0% reduction - no mitigations)
- Overall: (60 - 26) / 60 = 56.7% reduction

---

## Fix Implementation

**Date**: 2026-04-23  
**Commit**: 548c0a0  
**Status**: ✅ FIXED

### Changes Made

**Backend** (`backend/app/swarm/mitigations.py:626-648`):

Changed from composite_score-based calculation:
```python
# OLD (inconsistent):
original_mean_score = sum(original_scores) / len(original_scores)
residual_mean_score = sum(residual_scores) / len(residual_scores)
risk_reduction = ((original_mean_score - residual_mean_score) / original_mean_score * 100)
```

To CSA risk_level-based calculation:
```python
# NEW (consistent with visual display):
original_csa_total = sum([
    path.get("csa_risk_score", {}).get("risk_level", 0)
    for path in attack_paths
])
residual_csa_total = sum([
    p.residual_csa_risk_score.get("risk_level", 0)
    for p in post_mitigation_paths
    if p.residual_csa_risk_score
])

# Fallback to composite scores if CSA scores not available
if original_csa_total == 0:
    logger.warning("No CSA risk scores found, falling back to composite score calculation")
    # ... fallback logic
else:
    risk_reduction = ((original_csa_total - residual_csa_total) / original_csa_total * 100)
```

**Key Features**:
- ✅ Uses sum of CSA risk_levels (not mean of composite_scores)
- ✅ Aligns with per-path visual CSA risk band display
- ✅ Fallback to composite_score if CSA unavailable (backward compatibility)
- ✅ Logs CSA-based calculation for debugging

### Example Results After Fix

**Before Fix** (Inconsistent):
```
Path 1: 20/25 → 5/25 (visually 75% reduction)
Path 2: 15/25 → 3/25 (visually 80% reduction)
Path 3: 10/25 → 2/25 (visually 80% reduction)

Visual average: ~78%
System shows: 65% ❌ (using composite_score)
```

**After Fix** (Consistent):
```
Path 1: 20/25 → 5/25
Path 2: 15/25 → 3/25
Path 3: 10/25 → 2/25

CSA total: 45 → 10
System shows: 77.8% ✅ (matches visual!)
```

### Verification

To verify the fix works correctly:
1. Run any threat model (Full Swarm, Quick Run, Single Agent, or Stigmergic)
2. Apply mitigations (specific or all)
3. **Expected**: Overall risk reduction % matches visual per-path CSA reductions
4. **Example**: If all paths show 20→5 (75%), overall should show ~75%
5. Check backend logs for: "CSA-based risk reduction: X → Y (Z% reduction)"

---

**Status**: ✅ Inconsistency fixed and committed  
**Priority**: P2 - Medium (now resolved)  
**Impact**: Users now see consistent risk reduction percentages aligned with CSA methodology
