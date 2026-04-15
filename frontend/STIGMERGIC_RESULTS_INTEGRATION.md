# StigmergicResultsView Component Integration Guide

## Component Location
- **Component**: `/frontend/src/components/StigmergicResultsView.jsx`
- **Styles**: `/frontend/src/components/StigmergicResultsView.css`

## Overview
The `StigmergicResultsView` component displays Phase 10 stigmergic swarm exploration results with four main sections:

1. **Swarm Execution Timeline** - Sequential persona execution with reinforcement indicators
2. **Emergent Insights Panel** - High-confidence techniques, convergent paths, coverage gaps, technique clusters
3. **Shared Graph Visualization** - SVG-based force-directed graph with pheromone-weighted nodes
4. **Attack Paths** - Reuses existing kill chain styling with swarm indicators

## Integration into ThreatModelPage

### Step 1: Import the Component

Add to the imports section of `ThreatModelPage.jsx`:

```javascript
import StigmergicResultsView from '../components/StigmergicResultsView';
```

### Step 2: Conditional Rendering

In the results section of `ThreatModelPage.jsx`, add conditional rendering for stigmergic results:

```javascript
{/* Section C: Results View */}
{result && result.run_type === 'multi_agents_swarm' && (
  <StigmergicResultsView results={result} />
)}

{/* Existing results view (for non-stigmergic runs) */}
{result && result.run_type !== 'multi_agents_swarm' && result.final_paths && (
  <div className="results-panel">
    {/* Existing results rendering code */}
  </div>
)}
```

### Step 3: Alternative Approach (Side-by-Side)

If you want to show both the stigmergic view AND the standard results:

```javascript
{result && result.run_type === 'multi_agents_swarm' && (
  <>
    <StigmergicResultsView results={result} />
    {/* Optionally show standard results below */}
  </>
)}
```

## Component Props

The component expects a single prop:

```typescript
results: {
  run_type: string,                    // "multi_agents_swarm"
  execution_order: string,             // "capability_ascending" | "random" | "threat_actor_first"
  personas_used: string[],             // ["APT29 (Cozy Bear)", ...]
  attack_paths: Array<AttackPath>,     // Attack paths with steps
  shared_graph_snapshot: {
    nodes: Array<AttackNode>,
    edges: Array<AttackEdge>,
    statistics: {
      total_nodes: number,
      reinforced_nodes: number,
      // ...
    }
  },
  emergent_insights: {
    high_confidence_techniques: Array<{
      technique_id: string,
      technique_name: string,
      times_reinforced: number,
      // ...
    }>,
    convergent_paths: Array<{
      technique_sequence: string[],
      path_length: number,
      avg_pheromone: number
    }>,
    coverage_gaps: string[],
    technique_clusters: Array<{
      techniques: [string, string],
      co_occurrence_count: number
    }>
  },
  activity_log: Array<ActivityLogEntry>,
  personas_execution_sequence: string[]
}
```

## Features

### 1. Swarm Execution Timeline
- Displays personas in execution order
- Shows deposits and reinforcements per persona
- Visual indicators: ✓ reinforced vs ⤴ diverged
- Hover effects for interactivity

### 2. Emergent Insights
- **High Confidence Techniques**: Links to MITRE ATT&CK
- **Convergent Paths**: Shows technique sequences with pheromone scores
- **Coverage Gaps**: Lists unexplored assets
- **Technique Clusters**: Co-occurring technique pairs

### 3. Shared Graph Visualization
- SVG-based circular layout by kill chain phase
- Node size = pheromone strength
- Node color = kill chain phase (reuses project colors)
- Edge thickness = reinforcement count
- Interactive tooltips on hover

### 4. Attack Paths
- Reuses existing kill chain card styling
- Adds "Reinforces Swarm" or "Diverges from Swarm" badges
- Expandable/collapsible steps
- MITRE ATT&CK technique links

## Styling

The component follows project conventions:
- Uses existing color schemes for kill chain phases
- Badge styles match project badge system
- Responsive design with mobile breakpoints
- Gradient header matching stigmergic button style

## Self-Contained

The component is fully self-contained:
- No external graph libraries required (SVG-based)
- No modifications to existing components
- All icons from lucide-react (already in project)
- No new dependencies needed

## Example Usage

```jsx
<StigmergicResultsView results={stigmergicResults} />
```

Where `stigmergicResults` is the response from `POST /api/swarm/run/stigmergic`.

## Customization

To customize the component:
- **Colors**: Edit kill chain phase colors in `getKillChainPhaseColor()`
- **Graph Layout**: Modify `layoutNodes()` function for different layouts
- **Sections**: Toggle sections by default in initial `expandedSections` state
- **Limits**: Adjust slice limits (e.g., `.slice(0, 10)`) to show more/fewer items

## Known Limitations

1. Graph visualization is simple circular layout (no physics simulation)
2. Large graphs (>50 nodes) may require zoom/pan functionality
3. Tooltips on SVG nodes work but are basic (no rich formatting)
4. Mobile view may need horizontal scroll for wide graphs

## Future Enhancements

Potential improvements:
- Add zoom/pan to graph SVG
- Implement physics-based force-directed layout
- Add filtering/searching in insights panels
- Export graph as PNG/SVG
- Timeline animation showing sequential execution
