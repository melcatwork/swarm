# Tab Display Debugging Guide

## Issue Report
User says:
1. "Attack Paths" tab not showing Shared Attack Graph and Attack Paths
2. "Risk Assessment" tab should show CSA CII Risk Assessment

## Code Verification

### Standard Runs (Full Swarm, Quick Run, Single Agent)

**Wrapper condition** (Line 1567):
```javascript
{result && result.run_type !== 'multi_agents_swarm' && result.final_paths && (
  <div className="results-panel">
```
✅ Shows results-panel div when there's a result that's NOT stigmergic

**Risk Assessment** (Line 1596):
```javascript
{(activeTab === 'main' || activeTab === 'risk-assessment') && result.csa_risk_assessment && (
  <CsaRiskSummary ... />
)}
```
✅ Shows on Main tab OR Risk Assessment tab

**Attack Paths** (Lines 1603, 1608):
```javascript
{(activeTab === 'main' || activeTab === 'attack-paths') && (
  <VulnIntelSummary ... />
)}
{(activeTab === 'main' || activeTab === 'attack-paths') && (
  <div className="attack-paths-list">...</div>
)}
```
✅ Shows on Main tab OR Attack Paths tab

**Mitigations** (Lines 1674, 1793):
```javascript
{(activeTab === 'main' || activeTab === 'mitigations') && (
  <div>{/* Toolbar */}</div>
)}
{(activeTab === 'main' || activeTab === 'mitigations') && (() => {
  return <MitigationSummary ... />
})()}
```
✅ Shows on Main tab OR Mitigations tab

### Stigmergic Swarm Runs

**Main tab** (Line 1448):
```javascript
{activeTab === 'main' && result && result.run_type === 'multi_agents_swarm' && (
  <StigmergicResultsView results={result} />
)}
```
✅ Shows full StigmergicResultsView on Main tab only

**Other tabs** (Line 1453):
```javascript
{result && result.run_type === 'multi_agents_swarm' && activeTab !== 'main' && (
  <div className="results-panel">
```
✅ Shows tab-specific content when NOT on Main tab

**Risk Assessment** (Line 1456):
```javascript
{activeTab === 'risk-assessment' && result.evaluation_summary && (
  <CsaRiskSummary ... />
)}
```
✅ Shows on Risk Assessment tab only

**Attack Paths** (Line 1469):
```javascript
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
```
✅ Shows Shared Attack Graph (if exists) + Attack Paths on Attack Paths tab only

**Mitigations** (Line 1496):
```javascript
{activeTab === 'mitigations' && (
  <>
    <div>{/* Toolbar */}</div>
    <MitigationSummary ... />
  </>
)}
```
✅ Shows on Mitigations tab only

## Debugging Steps

### Step 1: Check Browser Console
1. Open Chrome DevTools (F12)
2. Go to Console tab
3. Click on different tabs
4. Look for any JavaScript errors

**Expected**: No errors
**If errors**: Note the error message and line number

### Step 2: Check activeTab State
Add this to ThreatModelPage.jsx after line 54:
```javascript
console.log('[TAB DEBUG] activeTab:', activeTab);
```

Then click tabs and watch console output.

**Expected**: 
- Clicking "Risk Assessment" → logs `[TAB DEBUG] activeTab: risk-assessment`
- Clicking "Attack Paths" → logs `[TAB DEBUG] activeTab: attack-paths`
- Clicking "Mitigations" → logs `[TAB DEBUG] activeTab: mitigations`

### Step 3: Check Result Data Structure
Add after line 22 (after result state):
```javascript
useEffect(() => {
  if (result) {
    console.log('[RESULT DEBUG] run_type:', result.run_type);
    console.log('[RESULT DEBUG] has final_paths:', !!result.final_paths);
    console.log('[RESULT DEBUG] has csa_risk_assessment:', !!result.csa_risk_assessment);
    console.log('[RESULT DEBUG] has attack_paths:', !!result.attack_paths);
    console.log('[RESULT DEBUG] has shared_graph_snapshot:', !!result.shared_graph_snapshot);
    console.log('[RESULT DEBUG] has evaluation_summary:', !!result.evaluation_summary);
  }
}, [result]);
```

**Expected output after threat model completes**:

For Standard Runs:
```
[RESULT DEBUG] run_type: full_swarm (or quick_run, single_agent)
[RESULT DEBUG] has final_paths: true
[RESULT DEBUG] has csa_risk_assessment: true
[RESULT DEBUG] has attack_paths: false
[RESULT DEBUG] has shared_graph_snapshot: false
[RESULT DEBUG] has evaluation_summary: false
```

For Stigmergic Run:
```
[RESULT DEBUG] run_type: multi_agents_swarm
[RESULT DEBUG] has final_paths: false
[RESULT DEBUG] has csa_risk_assessment: false
[RESULT DEBUG] has attack_paths: true
[RESULT DEBUG] has shared_graph_snapshot: true
[RESULT DEBUG] has evaluation_summary: true
```

### Step 4: Check Tab Button Clicks
Add onClick logging to tab buttons (lines 1032, 1040, 1048):
```javascript
onClick={() => {
  console.log('[TAB CLICK] Switching to risk-assessment');
  setActiveTab('risk-assessment');
}}
```

**Expected**: Logs appear when clicking tabs

### Step 5: Check Conditional Rendering
Add logging inside each tab condition:
```javascript
{activeTab === 'risk-assessment' && result.evaluation_summary && (() => {
  console.log('[RENDER DEBUG] Rendering Risk Assessment for stigmergic');
  return <CsaRiskSummary ... />
})()}
```

**Expected**: Logs appear when tabs are active

### Step 6: Verify CSS
Check if `.results-panel` has any CSS hiding it:
```bash
grep -n "results-panel" frontend/src/pages/ThreatModelPage.css
```

**Expected**: No `display: none` or `visibility: hidden`

## Quick Test

1. **Run a Quick Run threat model**
2. **Click "Risk Assessment" tab**
   - Should see ONLY: CSA Risk Summary
   - Should NOT see: Attack paths, mitigations
3. **Click "Attack Paths" tab**
   - Should see ONLY: Vulnerability Intel Summary + Attack Path Cards
   - Should NOT see: Risk summary, mitigations
4. **Click "Mitigations" tab**
   - Should see ONLY: Mitigation Toolbar + Comprehensive Mitigation Summary
   - Should NOT see: Risk summary, attack paths
5. **Click "Main" tab**
   - Should see EVERYTHING together

## If Still Not Working

Check these conditions:
1. Is `result` null or undefined?
2. Is `result.run_type` correctly set?
3. Does `result.csa_risk_assessment` exist?
4. Does `result.final_paths` exist and have items?
5. Is there a parent div hiding content with CSS?
6. Are tab buttons actually calling `setActiveTab`?
7. Is React state updating properly (check React DevTools)?

## Files to Check
- `frontend/src/pages/ThreatModelPage.jsx` (lines 1445-1850)
- `frontend/src/pages/ThreatModelPage.css` (check for display issues)
- Browser console for errors
