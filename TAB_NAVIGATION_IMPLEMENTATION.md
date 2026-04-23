# Tab Navigation Implementation

**Date**: 2026-04-23  
**Status**: ✅ **IMPLEMENTED**  
**Applies To**: All 4 run types (Full Swarm, Quick Run, Single Agent, Stigmergic Swarm)

---

## Overview

Revamped the frontend by organizing various sections into tabs for better navigation and focused viewing. The interface now provides a tabbed navigation system that allows users to view all content together (Main tab) or focus on specific sections individually.

---

## Tab Structure

### Tab Order (Left to Right)

1. **Main** - Full page view with all sections (default, leftmost)
2. **Run Test** - Upload Infrastructure-as-Code section only
3. **Summary** - Threat Model Summary section only
4. **System-under-test Architecture** - Infrastructure Asset Graph section only
5. **Result - Risk Assessment** - CSA CII Risk Assessment section only
6. **Result - Attack Paths** - Attack Paths section only
7. **Result - Mitigations** - Mitigation toolbar + Comprehensive Mitigation Summary section only

---

## Tab Behavior

### Main Tab
- **Shows**: Everything (all sections visible)
- **Purpose**: Traditional single-page view for comprehensive analysis
- **Always Available**: Yes
- **Default**: Active on page load

### Run Test Tab
- **Shows**: Upload Infrastructure-as-Code panel with:
  - Impact Score selector
  - File dropzone
  - Model selection
  - Run buttons (Full Swarm, Quick Run, Single Agent, Stigmergic)
- **Purpose**: Focus on test execution and configuration
- **Enabled**: When result exists (after first run)
- **Use Case**: Running additional tests with different configurations

### Summary Tab
- **Shows**: Threat Model Summary component with:
  - Total attack paths count
  - Primary & alternate paths with highest risk
  - Overall highest risk band
  - Attack surface coverage (if available)
  - Risk distribution charts
  - Impact configuration
- **Purpose**: High-level overview at a glance
- **Enabled**: When result exists
- **Use Case**: Quick risk posture assessment

### System-under-test Architecture Tab
- **Shows**: Infrastructure Asset Graph with:
  - Visual graph of infrastructure components
  - Asset details (resources, dependencies, trust boundaries)
  - Toggle for detailed view
- **Purpose**: Understand infrastructure topology
- **Enabled**: When result exists and asset_graph available
- **Use Case**: Visual exploration of system architecture

### Result - Risk Assessment Tab
- **Shows**: CSA CII Risk Assessment component with:
  - Risk matrix (5×5)
  - Highest risk band badge
  - Impact configuration
  - Risk distribution by band
  - Tolerance actions
- **Purpose**: Detailed risk assessment methodology
- **Enabled**: When result exists and csa_risk_assessment available
- **Use Case**: CSA CII compliance reporting

### Result - Attack Paths Tab
- **Shows**: Attack Path Cards section with:
  - Confirmed vulnerability-grounded paths
  - Agent exploration paths
  - Expandable path details
  - Mitigation checkboxes
- **Purpose**: Detailed attack scenario analysis
- **Enabled**: When result exists
- **Use Case**: Understanding specific attack vectors

### Result - Mitigations Tab
- **Shows**: 
  - Mitigation Action Toolbar (Clear, Apply All, Apply Selected buttons)
  - Comprehensive Mitigation Summary (defense-in-depth catalog)
- **Purpose**: Mitigation planning and application
- **Enabled**: When result exists
- **Use Case**: Selecting and applying security controls

---

## Visual Design

### Tab Navigation Bar

```
┌─────────────────────────────────────────────────────────────┐
│ [Main] [Run Test] [Summary] [System...] [Result...] [...]   │
│ ─────  ─────────  ────────  ──────────  ──────────  ─────   │
│   Active                      Disabled tabs (no result yet)  │
└─────────────────────────────────────────────────────────────┘
```

**Styling**:
- Active tab: Purple (#667eea) text and bottom border
- Inactive tab: Gray (#64748b) text, no border
- Hover: Purple text, light gray background
- Disabled: Light gray (#cbd5e1), reduced opacity, cursor not-allowed

**Layout**:
- Horizontal flex with 8px gap
- Bottom border: 2px solid #e2e8f0
- Scrollable on narrow screens (horizontal overflow)

### Tab Content

**Animation**: Fade-in on tab switch (0.3s ease)
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

## Implementation Details

### State Management

**New State Variable**:
```javascript
const [activeTab, setActiveTab] = useState('main');
```

**Tab Values**:
- `'main'` - Default, shows everything
- `'run-test'` - Upload panel only
- `'summary'` - Threat model summary only
- `'architecture'` - Asset graph only
- `'risk-assessment'` - CSA risk assessment only
- `'attack-paths'` - Attack paths only
- `'mitigations'` - Mitigation controls only

---

### Conditional Rendering Logic

Each section wrapped with conditional based on `activeTab`:

```javascript
// Example: Upload Panel shown in Main OR Run Test tabs
{(activeTab === 'main' || activeTab === 'run-test') && (
  <div className="upload-panel">
    ...
  </div>
)}

// Example: Summary shown in Main OR Summary tabs
{(activeTab === 'main' || activeTab === 'summary') && result && (
  <ThreatModelSummary result={result} />
)}
```

**Pattern**: `activeTab === 'main' || activeTab === '<specific-tab>'`

This ensures:
- ✅ Main tab shows everything
- ✅ Specific tabs show only their content
- ✅ Content appears in both contexts

---

### Section Mappings

| Section | Main Tab | Specific Tab | Condition |
|---------|----------|--------------|-----------|
| Landing State | ✅ | ❌ | `!result && !running` |
| Upload Panel | ✅ | Run Test | `activeTab === 'main' \|\| activeTab === 'run-test'` |
| Threat Model Summary | ✅ | Summary | `activeTab === 'main' \|\| activeTab === 'summary'` |
| Asset Graph | ✅ | Architecture | `activeTab === 'main' \|\| activeTab === 'architecture'` |
| Stigmergic Results | ✅ | ❌ | `activeTab === 'main' && run_type === 'multi_agents_swarm'` |
| Executive Summary | ✅ | ❌ | `activeTab === 'main'` |
| Stats Bar | ✅ | ❌ | `activeTab === 'main'` |
| CSA Risk Assessment | ✅ | Risk Assessment | `activeTab === 'main' \|\| activeTab === 'risk-assessment'` |
| Attack Paths | ✅ | Attack Paths | `activeTab === 'main' \|\| activeTab === 'attack-paths'` |
| Mitigation Toolbar | ✅ | Mitigations | `activeTab === 'main' \|\| activeTab === 'mitigations'` |
| Comprehensive Summary | ✅ | Mitigations | `activeTab === 'main' \|\| activeTab === 'mitigations'` |
| Post-Mitigation Analysis | ✅ | ❌ | `activeTab === 'main'` |

---

## Files Modified

### 1. frontend/src/pages/ThreatModelPage.jsx

**Lines Added/Modified**:

**State Management** (line ~52):
```javascript
const [activeTab, setActiveTab] = useState('main');
```

**Tab Navigation UI** (lines ~997-1046):
```javascript
<div className="tab-navigation">
  <button className={`tab-button ${activeTab === 'main' ? 'active' : ''}`} 
          onClick={() => setActiveTab('main')}>
    Main
  </button>
  {/* 6 more tab buttons */}
</div>
```

**Tab Content Wrapper** (lines ~1047, ~1748):
```javascript
<div className="tab-content">
  {/* All sections */}
</div>
```

**Conditional Rendering**: Added to multiple sections throughout the file

---

### 2. frontend/src/pages/ThreatModelPage.css

**New Styles Added** (lines 5-62):

```css
/* Tab Navigation */
.tab-navigation { /* ... */ }
.tab-button { /* ... */ }
.tab-button:hover:not(:disabled) { /* ... */ }
.tab-button.active { /* ... */ }
.tab-button:disabled { /* ... */ }
.tab-content { /* ... */ }
@keyframes fadeIn { /* ... */ }
```

---

## User Experience

### Navigation Flow

**Initial Load**:
1. User arrives at page → Main tab active
2. All sections visible (traditional view)
3. Other tabs disabled (grayed out)

**After First Run**:
1. Upload and run threat model
2. Results appear in Main tab
3. Other tabs become enabled (clickable)
4. User can switch tabs to focus on specific sections

**Tab Switching**:
1. Click any enabled tab
2. Content fades in (0.3s animation)
3. Only relevant section visible
4. Purple underline indicates active tab

---

## Benefits

### 1. Reduced Cognitive Load
Users can focus on one section at a time without scrolling through all content.

### 2. Flexible Workflows
- **Comprehensive view**: Stay on Main tab
- **Focused analysis**: Switch to specific tabs
- **Quick reference**: Jump between tabs for comparison

### 3. Better Organization
Clear separation of concerns:
- Input (Run Test)
- Overview (Summary)
- Architecture (System-under-test)
- Detailed Analysis (Risk Assessment, Attack Paths, Mitigations)

### 4. Improved Navigation
No more scrolling through long pages to find specific sections.

### 5. Progressive Disclosure
Tabs are disabled until relevant (after results exist), guiding users through the workflow.

---

## Responsive Behavior

### Desktop (>1024px)
- All tab buttons visible in single row
- No scrolling needed

### Tablet (600-1024px)
- Tab buttons may wrap or require horizontal scroll
- Content areas adapt to width

### Mobile (<600px)
- Horizontal scroll for tab navigation
- `overflow-x: auto` on `.tab-navigation`
- `white-space: nowrap` prevents wrapping
- Content stacks vertically

---

## Testing Verification

To verify tabs work correctly:

1. **Initial State**:
   - ✅ Main tab active (purple underline)
   - ✅ Other tabs disabled (gray, not clickable)
   - ✅ All sections visible in Main tab

2. **After Running Threat Model**:
   - ✅ All tabs enabled (blue on hover)
   - ✅ Click each tab → only relevant content shows
   - ✅ Active tab has purple underline and text
   - ✅ Content fades in smoothly

3. **Tab-Specific Content**:
   - ✅ Run Test: Only upload panel visible
   - ✅ Summary: Only threat model summary visible
   - ✅ Architecture: Only asset graph visible
   - ✅ Risk Assessment: Only CSA assessment visible
   - ✅ Attack Paths: Only attack paths visible
   - ✅ Mitigations: Toolbar + summary visible
   - ✅ Main: Everything visible

4. **Edge Cases**:
   - ✅ Stigmergic results only in Main tab
   - ✅ Post-mitigation analysis only in Main tab
   - ✅ Stats bar and executive summary only in Main tab
   - ✅ Disabled tabs cannot be clicked

---

## Future Enhancements

Potential improvements:

1. **Keyboard Navigation**: Arrow keys to switch tabs
2. **Tab Badges**: Show counts (e.g., "Attack Paths (10)")
3. **Deep Linking**: URL parameters for tab state (e.g., `#tab=summary`)
4. **Tab History**: Remember last visited tab per session
5. **Comparison Mode**: View two tabs side-by-side
6. **Sticky Tabs**: Tab bar stays visible on scroll
7. **Tab Groups**: Collapse related tabs into dropdown menu on mobile

---

## Backward Compatibility

### No Breaking Changes
- Main tab provides exact same view as before
- All functionality preserved
- No API changes
- No data structure changes

### Migration
- Users accustomed to scrolling can stay on Main tab
- New users can explore tabs for focused navigation

---

**Status**: ✅ Implemented and ready for testing  
**Files Modified**: 2 (ThreatModelPage.jsx, ThreatModelPage.css)  
**Lines Added**: ~120 (tab UI + conditionals)  
**Impact**: Improved navigation and focus across all 4 run types
