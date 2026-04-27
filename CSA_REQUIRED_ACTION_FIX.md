# CSA Risk Assessment "Required Action" Fix

**Date**: 2026-04-25  
**Issue**: "Required action ():" displays empty on Risk Assessment tab for stigmergic runs  
**Root Cause**: Missing `highest_band` and `paths_scored` fields in constructed csaRiskAssessment object

---

## Problem

### User Report
Risk Assessment tab shows:
```
Required action ():
```

Instead of:
```
Required action (High): Cannot be accepted. Treatment strategies must be developed and implemented within 1 month.
```

### Root Cause

**CsaRiskSummary component logic** (lines 33, 221-241):
```javascript
const highestBand = dist.highest_band || csaRiskAssessment.highest_band

// Later...
<strong>Required action ({highestBand}):</strong>
{
  {
    'Very High': 'Cannot be accepted. Activity must cease immediately...',
    'High': 'Cannot be accepted. Treatment strategies must be developed...',
    'Medium-High': 'Cannot be accepted. Treatment strategies must be developed...',
    'Medium': 'Can be accepted with regular monitoring...',
    'Low': 'Can be accepted with periodic monitoring.'
  }[highestBand]
}
```

If `highestBand` is `undefined`, the object lookup returns `undefined`, rendering as empty text.

**What was being passed** (INCOMPLETE):
```javascript
csaRiskAssessment={{
  scored_paths: result.attack_paths || [],
  total_paths: result.attack_paths?.length || 0,
  risk_distribution: result.evaluation_summary.risk_distribution || {},  // ❌ Missing highest_band
  overall_risk_level: result.evaluation_summary.overall_risk_level || 0,
  impact_config: result.evaluation_summary.impact_config
  // ❌ Missing: paths_scored
  // ❌ Missing: highest_band
  // ❌ Missing: framework
}}
```

---

## Solution

**Added missing fields** (Lines 1456-1473):

```javascript
{activeTab === 'risk-assessment' && result.evaluation_summary && (
  <CsaRiskSummary
    csaRiskAssessment={{
      scored_paths: result.attack_paths || [],
      total_paths: result.attack_paths?.length || 0,
      paths_scored: result.attack_paths?.length || 0,  // ✅ Added
      risk_distribution: {
        ...result.evaluation_summary.risk_distribution,
        highest_band: result.evaluation_summary.risk_distribution?.highest_band ||  // ✅ Added
                      result.evaluation_summary.highest_band || 'Medium'
      },
      highest_band: result.evaluation_summary.risk_distribution?.highest_band ||  // ✅ Added
                   result.evaluation_summary.highest_band || 'Medium',
      overall_risk_level: result.evaluation_summary.overall_risk_level || 0,
      impact_config: result.evaluation_summary.impact_config,
      framework: 'CSA CII Risk Assessment Guide (Feb 2021) Section 4.2'  // ✅ Added
    }}
  />
)}
```

### Changes Made

1. **Added `paths_scored`**: Required for "Risk distribution — X paths scored" display
2. **Added `highest_band` to `risk_distribution`**: Component checks `dist.highest_band` first
3. **Added `highest_band` to top-level object**: Fallback if `dist.highest_band` is missing
4. **Added `framework`**: Shows subtitle "CSA CII Risk Assessment Guide (Feb 2021) Section 4.2"
5. **Added fallback to 'Medium'**: Ensures required action always displays even if data is missing

---

## Required Action Messages by Band

| Band | Message |
|------|---------|
| **Very High** | Cannot be accepted. Activity must cease immediately or mitigation applied immediately. |
| **High** | Cannot be accepted. Treatment strategies must be developed and implemented within 1 month. |
| **Medium-High** | Cannot be accepted. Treatment strategies must be developed and implemented within 3–6 months. |
| **Medium** | Can be accepted with regular monitoring if no cost-effective treatment exists. |
| **Low** | Can be accepted with periodic monitoring. |

---

## Data Flow

### Stigmergic Result Structure
```javascript
{
  run_type: 'multi_agents_swarm',
  evaluation_summary: {
    risk_distribution: {
      'Very High': 0,
      'High': 5,
      'Medium-High': 3,
      'Medium': 0,
      'Low': 0,
      highest_band: 'High'  // ← This is what we needed
    },
    highest_band: 'High',  // ← Or this as fallback
    overall_risk_level: 20,
    impact_config: {
      user_set_score: 3,
      label: 'Moderate'
    }
  },
  attack_paths: [...]
}
```

### CsaRiskSummary Expected Props
```javascript
{
  csaRiskAssessment: {
    risk_distribution: {
      'Very High': number,
      'High': number,
      'Medium-High': number,
      'Medium': number,
      'Low': number,
      highest_band: string  // ← Required
    },
    highest_band: string,    // ← Required (fallback)
    paths_scored: number,    // ← Required
    framework: string,       // ← Optional but nice to have
    impact_config: object,   // ← Optional
    overall_risk_level: number
  }
}
```

---

## Testing

### Before Fix
```
CSA CII Risk Assessment
Highest risk band: High
Risk distribution — paths scored
5 High  3 Medium-High

Required action ():    ← Empty!
```

### After Fix
```
CSA CII Risk Assessment
CSA CII Risk Assessment Guide (Feb 2021) Section 4.2
Highest risk band: High
Risk distribution — 8 paths scored
5 High  3 Medium-High

Required action (High): Cannot be accepted. Treatment strategies must be developed and implemented within 1 month.
```

---

## Verification Steps

1. **Navigate to Risk Assessment tab**
2. **Check "Required action" section at bottom**
3. **Verify it shows**:
   - Band name in parentheses (e.g., "High")
   - Appropriate action text based on band
   - Text is dark red (matches highest band color)
4. **Also verify**:
   - Framework subtitle appears below title
   - "Risk distribution — X paths scored" shows correct count

---

## Related Components

- **CsaRiskSummary.jsx** (lines 33, 221-241): Component logic for required action
- **ThreatModelPage.jsx** (lines 1456-1473): Fixed stigmergic risk assessment data construction

---

## Files Modified

- `frontend/src/pages/ThreatModelPage.jsx` (lines 1456-1473)
  - Added `paths_scored` field
  - Added `highest_band` to `risk_distribution` object
  - Added `highest_band` to top-level `csaRiskAssessment` object
  - Added `framework` field
  - Added fallback to 'Medium' if highest_band missing

---

**Build Status**: ✅ Built successfully (559.64 kB bundle)  
**Frontend Status**: ✅ Running on http://localhost:5173  
**Issue Status**: ✅ FIXED - Required action now displays correctly
