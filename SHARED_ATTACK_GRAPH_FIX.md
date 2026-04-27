# Shared Attack Graph Fix - Attack Paths Tab

**Date**: 2026-04-25  
**Issue**: Shared Attack Graph shows "No graph data available" on Attack Paths tab, but works correctly on Main tab  
**Root Cause**: Incorrect prop names passed to SharedAttackGraph component

---

## Problem

### User Report
- **Main tab**: Shared Attack Graph displays correctly
- **Attack Paths tab**: "No graph data available" error message

### Root Cause Analysis

**SharedAttackGraph component expects these props** (line 256-259):
```javascript
export default function SharedAttackGraph({
  data,              // NOT "sharedGraph"
  coverageGaps = [],
  convergentPaths = []
}) {
```

**What I was passing (INCORRECT)**:
```javascript
<SharedAttackGraph
  sharedGraph={result.shared_graph_snapshot}  // ❌ Wrong prop name
  attackPaths={result.attack_paths || []}      // ❌ Wrong prop name
/>
```

**What StigmergicResultsView passes (CORRECT)** (line 767):
```javascript
<SharedAttackGraph
  data={shared_graph_snapshot}                           // ✅ Correct
  coverageGaps={emergent_insights?.coverage_gaps || []}  // ✅ Correct
  convergentPaths={emergent_insights?.convergent_paths || []} // ✅ Correct
/>
```

---

## Solution

**Fixed Attack Paths Tab** (Lines 1468-1493):

```javascript
{/* Attack Paths Tab */}
{activeTab === 'attack-paths' && (
  <>
    {result.shared_graph_snapshot && (
      <div style={{ marginBottom: 32 }}>
        <h3 style={{ fontSize: 18, marginBottom: 16 }}>Shared Attack Graph</h3>
        <SharedAttackGraph
          data={result.shared_graph_snapshot}                              // ✅ Fixed
          coverageGaps={result.emergent_insights?.coverage_gaps || []}     // ✅ Added
          convergentPaths={result.emergent_insights?.convergent_paths || []} // ✅ Added
        />
      </div>
    )}
    <div className="attack-paths-list">
      <h3>Attack Paths ({result.attack_paths?.length || 0})</h3>
      {(result.attack_paths || []).map((path, i) => (
        <CsaPathCard ... />
      ))}
    </div>
  </>
)}
```

### Changes Made

1. **Changed `sharedGraph` → `data`**: Matches component prop definition
2. **Changed `attackPaths` → `coverageGaps`**: Passes emergent insights coverage gaps
3. **Added `convergentPaths`**: Passes emergent insights convergent paths

---

## Data Structure

### Stigmergic Result Object
```javascript
{
  run_type: 'multi_agents_swarm',
  shared_graph_snapshot: {
    nodes: [...],
    edges: [...],
    kill_chain_lanes: {...}
  },
  emergent_insights: {
    coverage_gaps: [...],        // Techniques not explored
    convergent_paths: [...],     // Paths discovered by multiple agents
    high_confidence_techniques: [...]
  },
  attack_paths: [...]
}
```

### SharedAttackGraph Props
```javascript
{
  data: {                    // The graph structure
    nodes: [],
    edges: [],
    kill_chain_lanes: {}
  },
  coverageGaps: [],          // Optional: techniques with no coverage
  convergentPaths: []        // Optional: techniques reinforced by multiple agents
}
```

---

## Testing

### Before Fix
```
Attack Paths Tab > Shared Attack Graph
┌─────────────────────────────────────┐
│ Shared Attack Graph                 │
├─────────────────────────────────────┤
│ No graph data available             │
└─────────────────────────────────────┘
```

### After Fix
```
Attack Paths Tab > Shared Attack Graph
┌─────────────────────────────────────┐
│ Shared Attack Graph                 │
├─────────────────────────────────────┤
│ [Graph visualization with nodes,    │
│  edges, swim lanes, and controls]   │
└─────────────────────────────────────┘
```

---

## Verification Steps

1. **Run a Stigmergic Swarm threat model**
2. **Click "Attack Paths" tab**
3. **Verify Shared Attack Graph appears at the top**
4. **Check for**:
   - ✅ Graph nodes visible
   - ✅ Edges connecting nodes
   - ✅ Kill chain swim lanes (Initial Access, Execution, etc.)
   - ✅ Graph controls (zoom, pan, fit view)
   - ✅ Coverage gaps section (if any)
   - ✅ Node click interaction works
   - ✅ No "No graph data available" error

---

## Related Components

- **SharedAttackGraph.jsx** (lines 256-260): Component prop definition
- **StigmergicResultsView.jsx** (line 767): Working reference implementation
- **ThreatModelPage.jsx** (lines 1468-1493): Fixed Attack Paths tab section

---

## Files Modified

- `frontend/src/pages/ThreatModelPage.jsx` (lines 1474-1478)
  - Changed prop names from `sharedGraph`/`attackPaths` to `data`/`coverageGaps`/`convergentPaths`

---

**Build Status**: ✅ Built successfully (559.31 kB bundle)  
**Frontend Status**: ✅ Running on http://localhost:5173  
**Issue Status**: ✅ FIXED - Shared Attack Graph now displays on Attack Paths tab
