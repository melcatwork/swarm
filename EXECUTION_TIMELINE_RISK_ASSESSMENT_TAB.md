# Swarm Execution Timeline on Risk Assessment Tab

**Date**: 2026-04-25  
**Feature**: Added Swarm Execution Timeline to Risk Assessment tab for all 4 run types  
**Location**: Below CSA CII Risk Assessment on Risk Assessment tab

---

## Overview

The Swarm Execution Timeline component now appears on the **Risk Assessment tab** for all 4 run types, providing visibility into how the threat modeling agents executed.

---

## What Was Added

### New Component: ExecutionTimeline.jsx

**Purpose**: Display execution timeline with different views based on run type

**Features**:
- **Collapsible/expandable** header with Users icon
- **Two display modes**:
  1. **Stigmergic mode**: Detailed persona sequence with deposit/reinforcement stats
  2. **Standard mode**: Summary grid showing agents used, execution time, paths discovered, consensus findings

**Files Created**:
- `frontend/src/components/ExecutionTimeline.jsx` (202 lines)
- `frontend/src/components/ExecutionTimeline.css` (201 lines)

---

## Display by Run Type

### 1. Full Swarm Run (Standard Mode)

**Shows**:
```
┌─────────────────────────────────────────────────────┐
│ 👥 Swarm Execution Timeline                     [▼] │
├─────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │ 👥  13  │ │ 🕐 45s  │ │ 📈  26  │ │ ✓   8   │   │
│ │ Agents  │ │ Explor. │ │ Paths   │ │ Consensu│   │
│ │ Executed│ │ Time    │ │ Discover│ │ Findings│   │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│                                                     │
│ 13 threat actor personas analyzed the              │
│ infrastructure and discovered 26 potential          │
│ attack paths, with 8 high-consensus findings       │
│ validated by multiple agents.                       │
└─────────────────────────────────────────────────────┘
```

**Data Source**: `result.exploration_summary`
- `agents_used`: Number of agents executed
- `execution_time_seconds`: Exploration phase time
- `raw_paths_found`: Paths discovered
- `consensus_findings`: High-consensus findings count

### 2. Quick Run (Standard Mode)

**Shows**: Same as Full Swarm, but typically:
- 2 agents executed
- Shorter execution time
- Fewer paths discovered

### 3. Single Agent Run (Standard Mode)

**Shows**: Same format, but:
- 1 agent executed
- Single agent perspective
- No consensus findings (requires multiple agents)

### 4. Stigmergic Swarm Run (Stigmergic Mode)

**Shows**:
```
┌─────────────────────────────────────────────────────┐
│ 👥 Swarm Execution Timeline                     [▼] │
├─────────────────────────────────────────────────────┤
│ Execution Order: capability_ascending               │
│ 8 Agents Executed                                   │
│                                                     │
│ ┌─ [1] APT29 (Cozy Bear)                          │
│ │   3 deposits  ✓ 2 reinforced                     │
│ ├─ [2] Lazarus Group                               │
│ │   5 deposits  📈 diverged                        │
│ ├─ [3] Volt Typhoon                                │
│ │   4 deposits  ✓ 3 reinforced                     │
│ └─ ... (continues for all agents)                  │
└─────────────────────────────────────────────────────┘
```

**Data Source**: `result.personas_execution_sequence`, `result.activity_log`
- Shows each persona in execution order
- Displays deposit and reinforcement stats
- Color-coded: green border for reinforced, purple for diverged

---

## Implementation Details

### Component Props

```javascript
<ExecutionTimeline 
  result={result}           // Full result object
  runType="standard"        // "standard" or "stigmergic"
/>
```

### Integration in ThreatModelPage.jsx

#### Stigmergic Runs (Lines 1456-1478)
```javascript
{activeTab === 'risk-assessment' && result.evaluation_summary && (
  <>
    <CsaRiskSummary ... />
    <ExecutionTimeline result={result} runType="stigmergic" />
  </>
)}
```

#### Standard Runs (Lines 1607-1611)
```javascript
{activeTab === 'risk-assessment' && result.exploration_summary && (
  <ExecutionTimeline result={result} runType="standard" />
)}
```

---

## Visual Design

### Standard Mode Grid
- **4-column responsive grid** (auto-fit with 140px minimum)
- **Stat cards** with icon, value, label
- **Gradient icons** (purple gradient background)
- **Hover effects**: Border color change, upward translation, shadow

### Stigmergic Mode Timeline
- **Vertical timeline** with connecting lines
- **Persona cards** with order badge, name, stats
- **Color-coded borders**:
  - Green (3px left border): Reinforced paths (agent confirmed others' findings)
  - Purple (3px left border): Diverged paths (agent explored new territory)
- **Hover effects**: Border color change, rightward translation

### Collapsible Header
- **Users icon** on left
- **Chevron icon** on right (up/down based on state)
- **Hover effect**: Background color change
- **Default**: Expanded on initial render

---

## Data Flow

### Standard Run Response Structure
```javascript
{
  run_type: 'full_swarm',  // or 'quick_run', 'single_agent'
  exploration_summary: {
    agents_used: 13,
    execution_time_seconds: 45.23,
    raw_paths_found: 26,
    consensus_findings: 8,
    threat_intel_items: 150
  },
  // ... other fields
}
```

### Stigmergic Run Response Structure
```javascript
{
  run_type: 'multi_agents_swarm',
  personas_execution_sequence: [
    'APT29 (Cozy Bear)',
    'Lazarus Group',
    'Volt Typhoon',
    // ...
  ],
  execution_order: 'capability_ascending',
  activity_log: [
    { persona: 'APT29 (Cozy Bear)', action: 'deposit', ... },
    { persona: 'APT29 (Cozy Bear)', action: 'reinforce', ... },
    // ...
  ],
  // ... other fields
}
```

---

## CSS Variables Used

- `--color-background-primary`: Card backgrounds
- `--color-background-secondary`: Container background
- `--color-background-tertiary`: Hover states
- `--color-border-secondary`: Primary borders
- `--color-border-tertiary`: Subtle borders
- `--color-text-primary`: Main text
- `--color-text-secondary`: Labels
- `--color-text-tertiary`: Descriptions
- `--color-primary`: Brand purple (#667eea)

---

## Benefits

1. **✅ Consistent placement**: Same location across all 4 run types
2. **✅ Visibility into execution**: Users see how agents executed
3. **✅ Context for risk assessment**: Understanding which agents contributed helps interpret results
4. **✅ Stigmergic insights**: Reinforcement vs divergence patterns visible
5. **✅ Quick summary**: Standard mode provides high-level stats at a glance
6. **✅ Collapsible**: Doesn't clutter Risk Assessment tab when not needed

---

## Testing Checklist

### Full Swarm Run
- [ ] Navigate to Risk Assessment tab
- [ ] Verify Swarm Execution Timeline appears below CSA Risk Assessment
- [ ] Check 4 stat cards display: Agents Executed, Exploration Time, Paths Discovered, Consensus Findings
- [ ] Verify description text summarizes execution correctly
- [ ] Test collapse/expand functionality
- [ ] Verify hover effects on stat cards

### Quick Run
- [ ] Navigate to Risk Assessment tab
- [ ] Verify timeline shows ~2 agents
- [ ] Check execution time is shorter than Full Swarm
- [ ] Verify all stat cards render correctly

### Single Agent Run
- [ ] Navigate to Risk Assessment tab
- [ ] Verify timeline shows 1 agent
- [ ] Check consensus findings shows 0 or N/A
- [ ] Verify component renders without errors

### Stigmergic Swarm Run
- [ ] Navigate to Risk Assessment tab
- [ ] Verify Swarm Execution Timeline appears below CSA Risk Assessment
- [ ] Check persona timeline shows all agents in execution order
- [ ] Verify each persona card shows deposits and reinforcement/divergence stats
- [ ] Check green border for reinforced agents
- [ ] Check purple border for diverged agents
- [ ] Test collapse/expand functionality
- [ ] Verify hover effects on persona cards

---

## Files Modified

1. **frontend/src/pages/ThreatModelPage.jsx**
   - Added `ExecutionTimeline` import (line 14)
   - Added to stigmergic Risk Assessment tab (line 1475)
   - Added to standard Risk Assessment tab (lines 1609-1611)

2. **frontend/src/components/ExecutionTimeline.jsx** (NEW)
   - Component implementation with dual modes

3. **frontend/src/components/ExecutionTimeline.css** (NEW)
   - Styling for both standard and stigmergic modes

---

## Known Limitations

1. **Single Agent consensus**: Shows 0 consensus findings (expected, requires multiple agents)
2. **Standard mode detail**: Less detailed than stigmergic mode (no individual agent names)
3. **Execution order**: Standard mode doesn't show specific execution sequence

---

## Future Enhancements

**Possible improvements**:
1. Add individual agent names for standard runs (requires backend changes)
2. Add execution timestamps for each agent
3. Add click-to-filter: clicking an agent filters attack paths to that agent's discoveries
4. Add execution timeline graph/chart visualization
5. Add export timeline as image/PDF

---

**Build Status**: ✅ Built successfully (564.20 kB bundle, +4.96 kB)  
**Frontend Status**: ✅ Running on http://localhost:5173  
**Feature Status**: ✅ Complete - All 4 run types supported
