# Agent Explorations Collapsible Section

**Date**: 2026-04-22  
**Feature**: Collapse agent exploration paths under expandable section  
**Applies to**: ALL 4 run types (Full Swarm, Quick Run, Single Agent, Stigmergic Swarm)

---

## Problem Statement

After expanding chains from 1 primary + 1 alternate to 1 primary + 4 alternates (5 total), plus multiple agent-discovered paths, the attack paths section became cluttered with 10-15+ paths visible simultaneously.

Users wanted:
- Clear distinction between confirmed vulnerability-based paths and agent-discovered paths
- Cleaner initial view focusing on high-confidence confirmed vulnerabilities
- Ability to explore agent discoveries without visual clutter

---

## Solution

Implemented a collapsible section that separates paths by source:

### Confirmed Vulnerability-Grounded Paths
- Source: `confirmed_vuln_synthesis`
- **Always visible** - these are deterministic paths built from actual confirmed vulnerabilities
- 5 paths (1 primary + 4 alternates)
- First path expanded by default

### Agent Explorations
- Source: anything other than `confirmed_vuln_synthesis`
- **Collapsed by default** - these are creative scenarios from LLM agents
- Variable count (typically 5-10 paths)
- Click header to expand/collapse
- All paths collapsed when section is expanded

---

## UI Structure

```
┌────────────────────────────────────────────────────────────────┐
│ Confirmed Vulnerability-Grounded Paths (5)                    │
├────────────────────────────────────────────────────────────────┤
│ ✓ Primary chain: CVE-2024-1234 → AWS-IMDS-001 [EXPANDED]     │
│   └─ Attack steps, mitigations, CSA scoring visible           │
│                                                                 │
│ ▼ Alternate-1 chain: CVE-2024-5678 → AWS-S3-001 [COLLAPSED]  │
│ ▼ Alternate-2 chain: CVE-2024-9012 → AWS-IAM-002 [COLLAPSED] │
│ ▼ Alternate-3 chain: AWS-EKS-001 → AWS-RDS-001 [COLLAPSED]   │
│ ▼ Alternate-4 chain: CVE-2024-3456 → AWS-EC2-003 [COLLAPSED] │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 🌐 Agent Explorations - 8 paths                       ▼        │
└────────────────────────────────────────────────────────────────┘
                    (Click to expand)

When expanded:
┌────────────────────────────────────────────────────────────────┐
│ 🌐 Agent Explorations - 8 paths                       ▲        │
├────────────────────────────────────────────────────────────────┤
│ These attack paths were discovered by threat actor persona    │
│ agents during exploration. They represent creative attack      │
│ scenarios based on infrastructure analysis and agent expertise.│
│                                                                 │
│ ▼ Public Ingress Exploitation to Data Exfiltration            │
│ ▼ Instance Metadata Service Exploitation to Persistence       │
│ ▼ Lambda Function Abuse to Data Exfiltration                  │
│ ▼ ... (remaining paths)                                        │
└────────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Files Modified

1. **frontend/src/pages/ThreatModelPage.jsx**
   - Added path filtering logic to separate by source
   - Created `AgentExplorationsSection` component
   - Modified attack paths rendering to use new structure

2. **frontend/src/components/StigmergicResultsView.jsx**
   - Same changes as ThreatModelPage.jsx
   - Ensures consistency across all run types

### AgentExplorationsSection Component

```jsx
function AgentExplorationsSection({ paths }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div>
      {/* Clickable Header */}
      <button onClick={() => setExpanded(!expanded)}>
        <Network size={16} />
        <span>Agent Explorations - {paths.length} paths</span>
        {expanded ? <ChevronUp /> : <ChevronDown />}
      </button>

      {/* Collapsed Content */}
      {expanded && (
        <div>
          <p>Explanatory text...</p>
          {paths.map((path, i) => (
            <CsaPathCard
              path={path}
              defaultExpanded={false}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

### Path Filtering Logic

```jsx
// Separate paths by source
const confirmedVulnPaths = paths.filter(p => p.source === 'confirmed_vuln_synthesis')
const agentExplorationPaths = paths.filter(p => p.source !== 'confirmed_vuln_synthesis')

// Sort each group by CSA risk level
const sortedConfirmed = [...confirmedVulnPaths].sort((a, b) => {
  const scoreA = a.csa_risk_score?.risk_level ?? 0
  const scoreB = b.csa_risk_score?.risk_level ?? 0
  return scoreB - scoreA
})

const sortedAgent = [...agentExplorationPaths].sort((a, b) => {
  const scoreA = a.csa_risk_score?.risk_level ?? 0
  const scoreB = b.csa_risk_score?.risk_level ?? 0
  return scoreB - scoreA
})
```

---

## User Experience

### Before
- **13+ paths** all displayed in flat list
- No clear distinction between types
- Visual clutter with many collapsed cards
- Hard to focus on high-confidence findings

### After
- **5 confirmed paths** always visible (priority)
- **8+ agent paths** collapsed by default (optional)
- Clear visual hierarchy
- Cleaner initial view
- Easy to expand agent explorations when interested

---

## Visual Elements

### Collapsible Header
- **Network icon** (🌐) for visual distinction
- **Path count** ("8 paths") for transparency
- **Hover effect** - background color change on hover
- **Chevron indicator** - Down (▼) when collapsed, Up (▲) when expanded

### Explanatory Text
When expanded, shows:
> "These attack paths were discovered by threat actor persona agents during exploration. They represent creative attack scenarios based on infrastructure analysis and agent expertise."

This helps users understand the difference between confirmed vuln paths and agent explorations.

---

## Benefits

### 1. Cleaner Initial View
- Only 5 confirmed paths visible by default
- Reduced visual clutter
- Faster scan of high-confidence findings

### 2. Clear Categorization
- Users immediately see which paths are deterministic (vuln-based)
- Which paths are creative (agent-based)
- Better decision-making about which paths to prioritize

### 3. Progressive Disclosure
- Show most important information first (confirmed vulns)
- Allow exploration of additional scenarios (agent paths)
- Users control what they see

### 4. Maintains Full Functionality
- All paths still accessible
- Same CSA scoring, mitigations, attack steps
- No loss of information or features

---

## Technical Details

### State Management
```jsx
const [expanded, setExpanded] = useState(false)
```
- Simple boolean state per section
- No global state needed
- Each section manages its own collapse state

### Styling
- Uses CSS variables for consistency with app theme
- Smooth hover transitions
- Responsive design

### Performance
- No lazy loading needed (paths already loaded)
- Minimal re-renders (only on expand/collapse)
- No additional API calls

---

## Edge Cases Handled

### 1. No Confirmed Vuln Paths
If no confirmed vulnerability paths exist (unlikely), only agent explorations section is shown.

### 2. No Agent Explorations
If no agent explorations exist, only confirmed vuln paths are shown.

### 3. All Paths Same Source
Works correctly - either all in confirmed section or all in agent section.

### 4. Zero Paths
Gracefully handles empty arrays.

---

## Future Enhancements

Possible improvements:
1. **Remember expanded state**: Use localStorage to persist user preference
2. **Expand by default for small counts**: Auto-expand if ≤3 agent paths
3. **Search/filter**: Add search bar to find specific techniques or assets
4. **Bulk expand/collapse**: Button to expand/collapse all agent paths at once
5. **Visual statistics**: Show quick stats in collapsed header (e.g., "8 paths, 3 critical risk")

---

## Testing

### Manual Testing Steps

1. Run any threat modeling pipeline
2. Wait for completion
3. Scroll to "Attack Paths" section
4. Verify structure:
   - ✅ "Confirmed Vulnerability-Grounded Paths (5)" header visible
   - ✅ 5 paths visible (Primary + 4 Alternates)
   - ✅ "Agent Explorations - X paths" collapsed section below
5. Click "Agent Explorations" header
6. Verify:
   - ✅ Section expands
   - ✅ Explanatory text visible
   - ✅ All agent paths listed
   - ✅ Chevron changes from down to up
7. Click header again
8. Verify:
   - ✅ Section collapses
   - ✅ Chevron changes from up to down

### Expected Behavior

- ✅ Confirmed vuln paths always visible
- ✅ Agent explorations collapsed by default
- ✅ Click to expand/collapse works smoothly
- ✅ All paths have full functionality (CSA scoring, mitigations, etc.)
- ✅ Works across all 4 run types

---

## Conclusion

This feature provides a cleaner, more organized view of attack paths by:
- Prioritizing confirmed vulnerability-based paths (deterministic, high-confidence)
- Collapsing agent-discovered paths by default (creative, exploratory)
- Allowing easy expansion when users want to explore additional scenarios

**Result**: Better user experience with progressive disclosure of information.

**Status**: ✅ IMPLEMENTED - Ready for production use

---

**Modified Files**:
- `frontend/src/pages/ThreatModelPage.jsx` (~100 lines added)
- `frontend/src/components/StigmergicResultsView.jsx` (~100 lines added)

**Lines of Code**: ~200 LOC  
**Complexity**: Low  
**Risk**: Low (backward compatible, no breaking changes)  
**Committed**: e579397
