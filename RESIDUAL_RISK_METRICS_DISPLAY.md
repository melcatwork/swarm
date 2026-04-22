# Residual Risk Metrics Display in Attack Path Cards

**Date**: 2026-04-23  
**Status**: ✅ **IMPLEMENTED** (Commit: 10dee2b)  
**Component**: CsaPathCard

---

## What Was Added

Added a new **"Residual Risk Details"** section that displays post-mitigation risk metrics (Likelihood, Impact, Risk Level) directly in each attack path card, appearing below the original risk assessment.

---

## Display Format

When mitigations are applied, each attack path card now shows:

### Original Risk (existing):
```
┌─────────────────────────────────────────┐
│ LIKELIHOOD          4 / 5               │
│ High                                    │
│                                         │
│ IMPACT (USER-SET)   5 / 5               │
│ Very Severe                             │
│                                         │
│ RISK LEVEL          20 / 25             │
│ [Very High]                             │
└─────────────────────────────────────────┘
```

### Residual Risk (NEW):
```
┌─────────────────────────────────────────┐
│ RESIDUAL LIKELIHOOD     1 / 5           │
│ Very Low                                │
│                                         │
│ RESIDUAL IMPACT         5 / 5           │
│ Very Severe                             │
│                                         │
│ RESIDUAL RISK LEVEL     5 / 25          │
│ [Medium]                                │
└─────────────────────────────────────────┘
```

---

## Visual Design

**Color Scheme**:
- Background: Light green (`#10b98110`) - indicates positive improvement
- Border: Green (`#10b98140`) - subtle emphasis
- Headers: Dark green (`#059669`) - "RESIDUAL LIKELIHOOD", "RESIDUAL IMPACT", "RESIDUAL RISK LEVEL"
- Values: Colored with residual risk band color (matches risk severity)
- Risk Band Badge: Colored badge showing "Low", "Medium", "Medium-High", "High", or "Very High"

**Layout**:
- Three-column grid (same as original risk details)
- Appears immediately below original risk details
- Only shown when residual risk data is available (after applying mitigations)

---

## Example Scenarios

### Scenario 1: High Risk Fully Mitigated

**Original Risk**:
- Likelihood: 4 / 5 (High)
- Impact: 5 / 5 (Very Severe)
- Risk Level: 20 / 25 (Very High)

**After Applying All Mitigations**:
- Residual Likelihood: 1 / 5 (Very Low) ← Reduced!
- Residual Impact: 5 / 5 (Very Severe) ← Unchanged (data classification)
- Residual Risk Level: 5 / 25 (Medium) ← Significantly reduced!

**Reduction**: 75% (20 → 5)

---

### Scenario 2: Medium Risk Partially Mitigated

**Original Risk**:
- Likelihood: 3 / 5 (Moderate)
- Impact: 3 / 5 (Moderate)
- Risk Level: 9 / 25 (Medium-High)

**After Applying Some Mitigations**:
- Residual Likelihood: 2 / 5 (Low) ← Reduced slightly
- Residual Impact: 3 / 5 (Moderate) ← Unchanged
- Residual Risk Level: 6 / 25 (Medium) ← Reduced

**Reduction**: 33% (9 → 6)

---

### Scenario 3: Low Risk with Minimal Mitigations

**Original Risk**:
- Likelihood: 2 / 5 (Low)
- Impact: 4 / 5 (Severe)
- Risk Level: 8 / 25 (Medium-High)

**After Applying Few Mitigations**:
- Residual Likelihood: 1 / 5 (Very Low) ← Reduced
- Residual Impact: 4 / 5 (Severe) ← Unchanged
- Residual Risk Level: 4 / 25 (Medium) ← Reduced

**Reduction**: 50% (8 → 4)

---

## CSA Methodology Reminder

**Key Principle**: Mitigations reduce **LIKELIHOOD** (how easy to attack), NOT **IMPACT** (data classification)

- **Likelihood** = Average of Discoverability, Exploitability, Reproducibility (D/E/R)
- **Impact** = User-configured data classification (1=Negligible, 2=Minor, 3=Moderate, 4=Severe, 5=Very Severe)
- **Risk Level** = Likelihood × Impact (1-25 scale)

**After Mitigation**:
- Residual Likelihood = Original Likelihood × (1 - reduction_percentage)
- Residual Impact = Original Impact (unchanged)
- Residual Risk Level = Residual Likelihood × Residual Impact

---

## Implementation Details

**File**: `frontend/src/components/CsaPathCard.jsx` (lines 864-1016)

**Conditional Rendering**:
```javascript
{hasResidualRisk && residualScore && (
  <div style={{ /* Green background, border */ }}>
    {/* Residual Likelihood column */}
    {/* Residual Impact column */}
    {/* Residual Risk Level column */}
  </div>
)}
```

**Data Source**:
- `residualScore = path.residual_csa_risk_score` (from backend)
- Contains: `likelihood`, `impact`, `risk_level`, `risk_band`
- Calculated by backend in `backend/app/swarm/mitigations.py`

**Styling**:
- Matches original risk details layout for consistency
- Green color scheme distinguishes residual from original
- Same 3-column grid structure
- Risk band badge at bottom of Risk Level column

---

## When Displayed

**Conditions**:
1. ✅ User has applied mitigations
2. ✅ Backend has calculated `residual_csa_risk_score`
3. ✅ Path has `hasResidualRisk === true`

**Not Displayed**:
- ❌ Before any mitigations applied
- ❌ If backend couldn't calculate residual risk (no CSA score)
- ❌ If path is collapsed (only shown when expanded)

---

## User Benefits

### Clarity
- ✅ Users see exact post-mitigation metrics
- ✅ No guessing about residual risk state
- ✅ Clear numerical evidence of mitigation effectiveness

### Comparison
- ✅ Original and residual risk side-by-side
- ✅ Easy to see before/after comparison
- ✅ Visual distinction (grey vs green) makes comparison obvious

### Validation
- ✅ Confirms mitigations are working correctly
- ✅ Shows which attack paths are still high risk post-mitigation
- ✅ Helps prioritize additional mitigations

### Reporting
- ✅ Exact metrics for management reports
- ✅ CSA CII methodology compliance
- ✅ Justification for security investments

---

## Example UI Flow

### Step 1: View Original Risk
User expands attack path card, sees:
- Likelihood: 4 / 5 (High)
- Impact: 5 / 5 (Very Severe)
- Risk Level: 20 / 25 (Very High)

### Step 2: Select Mitigations
User checks mitigation checkboxes for steps in the attack path

### Step 3: Apply Mitigations
User clicks "Apply Mitigations & Analyze" button

### Step 4: View Residual Risk (NEW!)
Attack path card now shows BOTH:

**Original Risk** (grey background):
- Likelihood: 4 / 5 (High)
- Impact: 5 / 5 (Very Severe)
- Risk Level: 20 / 25 (Very High)

**Residual Risk** (green background):
- Residual Likelihood: 1 / 5 (Very Low) ✅
- Residual Impact: 5 / 5 (Very Severe) (unchanged)
- Residual Risk Level: 5 / 25 (Medium) ✅

**Reduction**: 75% improvement visible!

---

## Integration with Other Components

### Works With

1. **ResidualRiskSummary Component**
   - Summary box shows aggregate reduction across all paths
   - Individual paths show detailed metrics
   - Consistent color scheme (green for residual)

2. **Overall Risk Reduction %**
   - Percentage reflects sum of risk level changes
   - Individual path cards show the breakdown
   - Validates the overall percentage

3. **Attack Path Header**
   - Header shows: Original [Very High] 20/25 → Residual [Medium] 5/25
   - Expanded section shows detailed likelihood/impact breakdown
   - Consistent messaging throughout

---

## Affected Run Types

All 4 run types show residual risk metrics after mitigation:

1. ✅ **Full Swarm Pipeline**
2. ✅ **Quick Run (2 Agents)**
3. ✅ **Single Agent**
4. ✅ **Stigmergic Swarm**

---

## Testing Verification

To verify the display works correctly:

1. **Run any threat model** with confirmed vulnerabilities
2. **Expand an attack path card** - should see original risk details (3 columns)
3. **Apply some mitigations** to that path
4. **Click "Apply Mitigations & Analyze"**
5. **Re-expand the attack path card**
6. **Expected**: See BOTH original risk (grey) AND residual risk (green) sections
7. **Check**:
   - Residual Likelihood ≤ Original Likelihood
   - Residual Impact = Original Impact (unchanged)
   - Residual Risk Level ≤ Original Risk Level
   - Green background on residual section

---

## Future Enhancements

Potential improvements:

1. **Arrow indicator** between original and residual (↓ symbol)
2. **Percentage reduction** displayed inline (e.g., "75% ↓")
3. **Color gradient** based on reduction amount (more green = better)
4. **Hover tooltip** explaining why impact doesn't change
5. **Animation** when transitioning from original to residual

---

**Status**: ✅ Implemented and committed  
**Commit**: 10dee2b  
**Date**: 2026-04-23  
**Impact**: Users can now see exact residual risk metrics in each attack path card after applying mitigations
