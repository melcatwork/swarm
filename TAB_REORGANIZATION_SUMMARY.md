# Tab Content Reorganization - Summary

**Date**: 2026-04-25  
**Issue**: Tabs (Risk Assessment, Attack Paths, Mitigations, Post-Mitigation) did not display content correctly when clicked  
**Root Cause**: Stigmergic swarm results were monolithic and only appeared on "main" tab

---

## Changes Made

### 1. Modified `frontend/src/pages/ThreatModelPage.jsx`

**Added Import**:
```javascript
import SharedAttackGraph from '../components/SharedAttackGraph';
```

**Restructured Stigmergic Results** (Lines 1445-1558):
- **Before**: `StigmergicResultsView` only appeared when `activeTab === 'main'`
- **After**: Added tab-aware sections for stigmergic runs that respect individual tabs

---

## Tab Content Organization (All 4 Run Types)

### Main Tab (`activeTab === 'main'`)
✅ Shows **everything** (full StigmergicResultsView for stigmergic, full results-panel for standard runs)

### Risk Assessment Tab (`activeTab === 'risk-assessment'`)
✅ **CSA CII Risk Assessment** (CsaRiskSummary component)
- For stigmergic: Builds summary from `evaluation_summary`
- For standard: Uses `result.csa_risk_assessment`

### Attack Paths Tab (`activeTab === 'attack-paths'`)
✅ **Shared Attack Graph** (if available, stigmergic runs only)
✅ **Vulnerability Intelligence Summary** (VulnIntelSummary)
✅ **Attack Path Cards** (CsaPathCard components)
- For stigmergic: Shows `result.attack_paths`
- For standard: Shows `result.final_paths` or `result.csa_risk_assessment.scored_paths`

### Mitigations Tab (`activeTab === 'mitigations'`)
✅ **Mitigation Action Toolbar** (Clear Selections, Apply Mitigations buttons)
✅ **Comprehensive Mitigation Summary** (MitigationSummary component)
- Shows all mitigations across all attack paths

### Post-Mitigation Risk Assessment Tab (`activeTab === 'post-mitigation'`)
✅ **Residual Risk Summary** (ResidualRiskSummary component)
✅ **Post-Mitigation Attack Paths** with residual risk levels
- Only enabled when `postMitigationAnalysis` exists

---

## Run Type Compatibility

| Run Type | Risk Assessment | Attack Paths | Mitigations | Post-Mitigation |
|----------|----------------|--------------|-------------|-----------------|
| **Full Swarm** | ✅ | ✅ | ✅ | ✅ (after analysis) |
| **Quick Run** | ✅ | ✅ | ✅ | ✅ (after analysis) |
| **Single Agent** | ✅ | ✅ | ✅ | ✅ (after analysis) |
| **Stigmergic Swarm** | ✅ | ✅ + Graph | ✅ | ✅ (after analysis) |

---

## Code Structure

### Stigmergic Results (Tab-Aware)
```javascript
{result && result.run_type === 'multi_agents_swarm' && activeTab !== 'main' && (
  <div className="results-panel">
    {/* Risk Assessment Tab */}
    {activeTab === 'risk-assessment' && result.evaluation_summary && (
      <CsaRiskSummary ... />
    )}

    {/* Attack Paths Tab */}
    {activeTab === 'attack-paths' && (
      <>
        {result.shared_graph_snapshot && (
          <SharedAttackGraph ... />
        )}
        <div className="attack-paths-list">
          {result.attack_paths.map(...)}
        </div>
      </>
    )}

    {/* Mitigations Tab */}
    {activeTab === 'mitigations' && (
      <>
        <div>{/* Mitigation Toolbar */}</div>
        <MitigationSummary ... />
      </>
    )}
  </div>
)}
```

### Standard Results (Tab-Aware)
```javascript
{result && result.run_type !== 'multi_agents_swarm' && result.final_paths && (
  <div className="results-panel">
    {/* Each section checks activeTab condition */}
    {(activeTab === 'main' || activeTab === 'risk-assessment') && ...}
    {(activeTab === 'main' || activeTab === 'attack-paths') && ...}
    {(activeTab === 'main' || activeTab === 'mitigations') && ...}
  </div>
)}
```

---

## Testing Checklist

### For Standard Runs (Full Swarm, Quick Run, Single Agent):
- [ ] Click "Risk Assessment" tab → Only shows CSA risk summary
- [ ] Click "Attack Paths" tab → Only shows vulnerability intel summary + attack path cards
- [ ] Click "Mitigations" tab → Only shows mitigation toolbar + comprehensive mitigation summary
- [ ] Click "Post-Mitigation" tab → Only shows residual risk (if analysis exists)
- [ ] Click "Main" tab → Shows all sections together

### For Stigmergic Swarm Run:
- [ ] Click "Risk Assessment" tab → Only shows CSA risk summary
- [ ] Click "Attack Paths" tab → Shows shared attack graph + attack path cards
- [ ] Click "Mitigations" tab → Only shows mitigation toolbar + mitigation summary
- [ ] Click "Post-Mitigation" tab → Only shows residual risk (if analysis exists)
- [ ] Click "Main" tab → Shows full StigmergicResultsView (all sections)

---

## Benefits

1. **Consistent UX**: All 4 run types now have the same tab structure
2. **Focused Views**: Each tab shows only relevant content
3. **Shared Attack Graph**: Now accessible on Attack Paths tab for stigmergic runs
4. **No Breaking Changes**: Main tab still shows everything, backward compatible
5. **Clean Separation**: Risk assessment, attack paths, and mitigations are clearly separated

---

## Files Modified

- `frontend/src/pages/ThreatModelPage.jsx` — Added SharedAttackGraph import, restructured stigmergic results to respect tabs

---

**Build Status**: ✅ Successful (559.24 kB bundle)  
**Breaking Changes**: None (Main tab behavior unchanged)  
**Frontend Restart Required**: Yes (rebuild completed)
