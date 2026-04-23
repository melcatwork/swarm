# Threat Model Summary Component

**Date**: 2026-04-23  
**Status**: ✅ **IMPLEMENTED**  
**Component**: ThreatModelSummary.jsx  
**Applies To**: All 4 run types (Full Swarm, Quick Run, Single Agent, Stigmergic Swarm)

---

## Overview

Created a new high-level summary component that displays comprehensive threat model results at a glance. The component appears **immediately below "Upload Infrastructure-as-Code"** and **above "Infrastructure Asset Graph"**, providing users with instant visibility into:

1. ✅ Total number of discovered attack paths
2. ✅ Coverage details (for stigmergic swarm runs)
3. ✅ Overall risk levels across all paths
4. ✅ Risk levels of primary and alternate attack paths (vulnerability-grounded)

---

## Visual Design

### Layout
- **Card Style**: Rounded 8px border, purple gradient background (#667eea15 → #764ba215)
- **Border**: 2px solid primary color
- **Padding**: 20px all sides
- **Margin**: 24px bottom spacing

### Header Section
- **Icon**: Target icon (24px, purple #667eea)
- **Title**: "Threat Model Summary" (20px, bold)
- **Subtitle**: Descriptive text in secondary color

### Stats Grid
- **Layout**: Responsive grid (auto-fit, minimum 200px per card)
- **Cards**: 3-4 stat cards depending on data availability
- **Gap**: 16px between cards

---

## Stat Cards

### 1. Total Attack Paths
**Display**:
- Large number (32px, bold, purple #667eea)
- Breakdown: "X vulnerability-grounded, Y agent exploration"
- Label: "TOTAL ATTACK PATHS" (uppercase, 11px)

**Data Source**: 
```javascript
allPaths.length
confirmedVulnPaths.length  // source === 'confirmed_vuln_synthesis'
agentExplorationPaths.length  // source !== 'confirmed_vuln_synthesis'
```

**Example**: 
```
TOTAL ATTACK PATHS
       10
5 vulnerability-grounded, 5 agent exploration
```

---

### 2. Primary & Alternate Paths
**Display**:
- Large number (32px, bold, color = highest risk band color)
- Highest risk indicator with colored dot
- Border: 2px colored based on highest risk band
- Label: "PRIMARY & ALTERNATE PATHS" (uppercase, 11px)

**Data Source**:
```javascript
confirmedVulnPaths.length
highestConfirmedBand  // Calculated from csa_risk_score.risk_band
```

**Example**:
```
PRIMARY & ALTERNATE PATHS
       3
🔴 Highest risk: Very High
```

---

### 3. Overall Highest Risk
**Display**:
- Risk band name (24px, bold, color = band color)
- "Across all X attack paths" subtitle
- Border: 2px colored based on risk band
- Label: "OVERALL HIGHEST RISK" (uppercase, 11px)

**Data Source**:
```javascript
result.csa_risk_assessment.risk_distribution.highest_band
result.csa_risk_assessment.highest_band
```

**Example**:
```
OVERALL HIGHEST RISK
  Very High
Across all 10 attack paths
```

---

### 4. Attack Surface Coverage (Optional)
**Display**:
- Percentage (32px, bold, green #10b981)
- "Exploration completeness" subtitle
- Border: 1px green outline
- Label: "ATTACK SURFACE COVERAGE" (uppercase, 11px)
- **Only shows**: When coverage data is available (stigmergic swarm)

**Data Source**:
```javascript
result.emergent_insights?.summary?.coverage_percentage
result.adversarial_summary?.coverage_estimate
```

**Example**:
```
ATTACK SURFACE COVERAGE
     87.3%
Exploration completeness
```

---

## Risk Distribution Sections

### Primary & Alternate Paths Distribution
**Title**: "Primary & Alternate Attack Paths Risk Distribution"  
**Icon**: Shield icon (16px, purple)

**Display**:
- Horizontal flex layout with gap
- Each risk band shown as pill:
  - Colored square (10×10px)
  - Count number (14px, bold, band color)
  - Band name (12px, medium)
  - Background: Band color at 15% opacity
  - Border: Band color at 50% opacity

**Data**: Calculated from `confirmedVulnPaths` CSA risk scores

**Example**:
```
🛡️ Primary & Alternate Attack Paths Risk Distribution
[🟥 2 Very High]  [🟧 1 High]  [🟨 0 Medium]
```

---

### Overall Risk Distribution
**Title**: "Overall Risk Distribution (All Attack Paths)"  
**Icon**: TrendingUp icon (16px, purple)

**Display**: Same pill style as primary/alternate section

**Data**: `result.csa_risk_assessment.risk_distribution`

**Example**:
```
📈 Overall Risk Distribution (All Attack Paths)
[🟥 3 Very High]  [🟧 2 High]  [🟨 2 Medium]  [🟩 3 Low]
```

---

## Impact Configuration Banner

**Display**:
- Light background box at bottom
- Alert icon (14px, purple)
- Text: "Data classification (impact): X — Label"
- Color: Band color based on impact score
- Note: "(applies to all paths)"

**Data Source**:
```javascript
result.csa_risk_assessment.impact_configuration.user_set_score
result.csa_risk_assessment.impact_configuration.label
```

**Example**:
```
⚠️ Data classification (impact): 5 — Very Severe (applies to all paths)
```

---

## Placement

**File**: `frontend/src/pages/ThreatModelPage.jsx`  
**Lines**: 1275-1278

**Position**:
```
Line 1273: </div>  ← Upload panel closes
Line 1274: 
Line 1275: {/* Threat Model Summary */}  ← NEW COMPONENT HERE
Line 1276-1278: <ThreatModelSummary result={result} />
Line 1279:
Line 1280: {/* Section B: Asset Graph View */}  ← Asset Graph starts
```

---

## Data Flow

### Input Props
```javascript
<ThreatModelSummary result={result} />
```

**`result` object structure**:
```javascript
{
  final_paths: [...],  // All attack paths
  csa_risk_assessment: {
    scored_paths: [...],  // Paths with CSA scores
    risk_distribution: {
      'Very High': 2,
      'High': 1,
      'Medium': 3,
      'Low': 4,
      highest_band: 'Very High'
    },
    impact_configuration: {
      user_set_score: 5,
      label: 'Very Severe'
    }
  },
  emergent_insights: {  // Only for stigmergic swarm
    summary: {
      coverage_percentage: 87.3
    }
  },
  adversarial_summary: {  // For other run types
    coverage_estimate: '85%'
  }
}
```

### Path Filtering
```javascript
// Confirmed vulnerability-grounded paths (primary/alternate)
const confirmedVulnPaths = allPaths.filter(p => p.source === 'confirmed_vuln_synthesis')

// Agent exploration paths
const agentExplorationPaths = allPaths.filter(p => p.source !== 'confirmed_vuln_synthesis')
```

### Risk Band Calculation
```javascript
// For each confirmed vuln path
const riskBand = path.csa_risk_score?.risk_band  // 'Very High', 'High', etc.
const riskLevel = path.csa_risk_score?.risk_level  // 1-25 numeric score

// Determine highest
const bandOrder = ['Low', 'Medium', 'Medium-High', 'High', 'Very High']
```

---

## Responsive Behavior

### Grid Breakpoints
- **Desktop** (>800px): 4 columns (Total, Primary, Overall, Coverage)
- **Tablet** (600-800px): 2 columns (2×2 grid)
- **Mobile** (<600px): 1 column (stacked)

**CSS**: `gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'`

### Card Sizing
- **Minimum width**: 200px per card
- **Maximum width**: Equal fractions of available space
- **Gap**: 16px maintained at all breakpoints

---

## Color Scheme

### Risk Band Colors
```javascript
const BAND_COLOURS = {
  'Low':         '#FFEB3B',  // Yellow
  'Medium':      '#F4A460',  // Sandy Brown
  'Medium-High': '#FF8C00',  // Dark Orange
  'High':        '#B71C1C',  // Dark Red
  'Very High':   '#F44336',  // Red
}
```

### Accent Colors
- **Purple gradient**: #667eea → #764ba2 (background)
- **Green**: #10b981 (coverage percentage)
- **Borders**: Band colors at 60% opacity for stat cards
- **Backgrounds**: Band colors at 15% opacity for pills

---

## User Benefits

### 1. Instant Overview
Users see critical metrics **immediately** after upload without scrolling:
- Total paths discovered
- Risk severity levels
- Coverage completeness

### 2. Focused Priority
**Primary & Alternate Paths** card highlights CVE-based vectors with highest risk, helping users prioritize remediation efforts.

### 3. Visual Hierarchy
Color-coded borders and large numbers draw attention to high-risk areas first.

### 4. Coverage Validation
Stigmergic swarm users can verify exploration completeness before diving into details.

### 5. Context Before Details
Summary provides mental model before users explore detailed attack paths and asset graphs.

---

## Implementation Details

### Component File
**Path**: `frontend/src/components/ThreatModelSummary.jsx`  
**Lines**: 296 total  
**Exports**: Default export `ThreatModelSummary`

### Import Statement
```javascript
import ThreatModelSummary from '../components/ThreatModelSummary';
```

### Usage
```jsx
{result && (
  <ThreatModelSummary result={result} />
)}
```

**Conditional Rendering**: Only shows when `result` exists (after successful threat model run)

---

## Example Scenarios

### Scenario A: Full Swarm with High Risk

**Display**:
```
┌────────────────────────────────────────────────────────────┐
│ 🎯 Threat Model Summary                                   │
│ High-level overview of discovered attack paths and risk   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│ │TOTAL ATTACK │ │PRIMARY &    │ │OVERALL      │         │
│ │PATHS        │ │ALTERNATE    │ │HIGHEST RISK │         │
│ │             │ │PATHS        │ │             │         │
│ │     12      │ │     4       │ │  Very High  │         │
│ │             │ │             │ │             │         │
│ │4 vuln, 8 ag │ │🔴 Very High │ │Across 12    │         │
│ └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                            │
│ 🛡️ Primary & Alternate Attack Paths Risk Distribution     │
│ [🟥 2 Very High] [🟧 1 High] [🟨 1 Medium]                │
│                                                            │
│ 📈 Overall Risk Distribution (All Attack Paths)           │
│ [🟥 3 Very High] [🟧 2 High] [🟨 4 Medium] [🟩 3 Low]    │
│                                                            │
│ ⚠️ Data classification (impact): 5 — Very Severe          │
└────────────────────────────────────────────────────────────┘
```

---

### Scenario B: Stigmergic Swarm with Coverage

**Display**:
```
┌────────────────────────────────────────────────────────────┐
│ 🎯 Threat Model Summary                                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│ │TOTAL     │ │PRIMARY & │ │OVERALL   │ │ATTACK    │     │
│ │ATTACK    │ │ALTERNATE │ │HIGHEST   │ │SURFACE   │     │
│ │PATHS     │ │PATHS     │ │RISK      │ │COVERAGE  │     │
│ │          │ │          │ │          │ │          │     │
│ │    15    │ │    3     │ │   High   │ │  87.3%   │     │
│ │          │ │          │ │          │ │          │     │
│ │3v, 12ag  │ │🟧 High  │ │Across 15 │ │Expl comp │     │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                            │
│ [Risk distribution sections...]                           │
└────────────────────────────────────────────────────────────┘
```

---

### Scenario C: Quick Run with Few Paths

**Display**:
```
┌────────────────────────────────────────────────────────────┐
│ 🎯 Threat Model Summary                                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│ │TOTAL ATTACK │ │PRIMARY &    │ │OVERALL      │         │
│ │PATHS        │ │ALTERNATE    │ │HIGHEST RISK │         │
│ │             │ │PATHS        │ │             │         │
│ │      3      │ │     2       │ │   Medium    │         │
│ │             │ │             │ │             │         │
│ │2 vuln, 1 ag │ │🟨 Medium   │ │Across 3     │         │
│ └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                            │
│ 🛡️ Primary & Alternate Attack Paths Risk Distribution     │
│ [🟨 2 Medium]                                              │
│                                                            │
│ 📈 Overall Risk Distribution (All Attack Paths)           │
│ [🟨 2 Medium] [🟩 1 Low]                                  │
└────────────────────────────────────────────────────────────┘
```

---

## Edge Cases Handled

### 1. No Confirmed Vulnerability Paths
- "Primary & Alternate Paths" card shows "0"
- Risk distribution section for primary/alternate is not rendered
- Overall distribution still shows all agent paths

### 2. No Coverage Data
- Coverage stat card is not rendered (only 3 cards shown)
- Applies to: Full Swarm, Quick Run, Single Agent

### 3. No Risk Distribution Data
- Fallback to 'Low' risk band
- Empty distribution object handled gracefully

### 4. Missing Impact Configuration
- Impact banner not rendered
- Component still displays other sections

---

## Testing Verification

To verify the component works correctly:

1. **Run any threat model** (Full Swarm, Quick, Single, or Stigmergic)
2. **Wait for completion**
3. **Expected**: Summary appears immediately after upload panel
4. **Check position**: Should be ABOVE "Infrastructure Asset Graph"
5. **Verify stat cards**:
   - Total Attack Paths: Should show correct count
   - Primary & Alternate: Should show vulnerability-grounded paths only
   - Overall Highest Risk: Should match highest band from all paths
   - Coverage: Only visible for stigmergic swarm
6. **Check risk distributions**:
   - Primary/Alternate distribution: Only confirmed vuln paths
   - Overall distribution: All paths
7. **Verify colors**: Risk bands should use correct color scheme
8. **Test responsiveness**: Resize browser window to check grid behavior

---

## Files Modified

### New File
- `frontend/src/components/ThreatModelSummary.jsx` (296 lines)

### Modified Files
- `frontend/src/pages/ThreatModelPage.jsx`:
  - Line 6: Added import statement
  - Lines 1275-1278: Added component rendering

---

## Related Components

### CsaRiskSummary
- **Location**: Further down page (line ~1390)
- **Purpose**: Detailed CSA risk matrix with tolerance actions
- **Difference**: ThreatModelSummary is high-level overview, CsaRiskSummary is detailed assessment

### ResidualRiskSummary
- **Location**: Post-mitigation section
- **Purpose**: Shows risk after applying mitigations
- **Difference**: ThreatModelSummary shows pre-mitigation baseline

### CsaPathCard
- **Location**: Attack paths section
- **Purpose**: Individual attack path details
- **Difference**: ThreatModelSummary shows aggregated stats

---

## Design Philosophy

### Progressive Disclosure
1. **High-level summary** (ThreatModelSummary) → Instant context
2. **Infrastructure graph** → Visual asset relationships
3. **Detailed risk assessment** (CsaRiskSummary) → Methodology details
4. **Attack path cards** → Step-by-step scenarios
5. **Mitigation summary** → Defense strategies

### Information Hierarchy
- **Most important first**: Total paths and highest risk
- **Visual priority**: Large numbers, bold colors
- **Context next**: Risk distributions and impact configuration
- **Details later**: Scroll down for granular data

---

**Status**: ✅ Implemented and ready for testing  
**Component**: `ThreatModelSummary.jsx`  
**Page Integration**: `ThreatModelPage.jsx` (lines 1275-1278)  
**Applies To**: All 4 run types  
**Impact**: Improved UX with immediate high-level visibility of threat model results
