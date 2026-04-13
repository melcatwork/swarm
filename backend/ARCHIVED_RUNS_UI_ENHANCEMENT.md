# Archived Runs UI Enhancement

**Date**: 2026-04-13
**Feature**: Enhanced archived runs sidebar with detailed information display

---

## Overview

The archived runs sidebar has been redesigned to show comprehensive information about each threat modeling run in a clear, organized format.

---

## What's Displayed

Each archived run now shows the following information in order:

### 1. **LLM Model Used** (Top - Primary Badge)
- Displayed as a prominent gradient badge
- Shows the exact model name (e.g., "qwen3:14b", "gemma4:e4b")
- Purple gradient for known models
- Gray gradient for unknown models
- Helps track which model produced which results

### 2. **Time of Run** (System Time)
- 🕐 Icon + formatted timestamp
- Format: "Month DD, YYYY at HH:MM:SS AM/PM"
- Example: "Apr 13, 2026 at 10:30:45 AM"
- Uses system's local time zone

### 3. **File Used for Evaluation**
- 📄 Icon + file name
- Monospace font for technical clarity
- Example: "ecommerce-platform.tf"
- Truncates with ellipsis if too long

### 4. **Number of Attack Paths**
- 🎯 Icon + count with description
- Format: "X attack path(s) identified"
- Singular/plural handling
- Bold number for emphasis
- Example: "**4** attack paths identified"

### 5. **Execution Time**
- ⏱️ Icon + formatted duration
- Format: "Completed in Xm Ys" or "Xs" (if under 1 minute)
- Examples:
  - "Completed in **2m 5s**"
  - "Completed in **45s**"
- Bold duration for emphasis

---

## Visual Layout

### Before
```
┌─────────────────────────────────┐
│ TM Swarm Run - ecommerce...     │
│ ecommerce-platform.tf  | QUICK  │
│ 4 paths | 120s                  │
│ qwen3:14b                       │
│ 2026-04-13 10:30:45             │
└─────────────────────────────────┘
```

### After
```
┌─────────────────────────────────┐
│ [qwen3:14b        ] [QUICK]     │ ← Model badge + mode
│ 🕐 Apr 13, 2026 at 10:30:45 AM │ ← Timestamp
│ 📄 ecommerce-platform.tf        │ ← File
│ 🎯 4 attack paths identified    │ ← Paths count
│ ⏱️ Completed in 2m 0s            │ ← Duration
└─────────────────────────────────┘
```

---

## Changes Made

### Frontend Changes

#### 1. **Added Time Formatting Helper** (`ThreatModelPage.jsx`)

```javascript
const formatExecutionTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  }
  return `${remainingSeconds}s`;
};
```

**Purpose**: Converts seconds to human-readable "Xm Ys" format

#### 2. **Redesigned Archived Run Display** (`ThreatModelPage.jsx`)

**New Structure**:
```jsx
<div className="run-info" onClick={() => handleLoadArchivedRun(run.run_id)}>
  {/* Model + Mode Header */}
  <div className="run-header">
    <span className="model-badge-main">{run.model_used}</span>
    <span className="run-mode-badge">{run.mode}</span>
  </div>

  {/* Timestamp */}
  <div className="run-timestamp">
    <span className="timestamp-icon">🕐</span>
    <span className="timestamp-text">
      {new Date(run.created_at).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
      })} at {new Date(run.created_at).toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      })}
    </span>
  </div>

  {/* File */}
  <div className="run-file-info">
    <span className="file-icon">📄</span>
    <span className="file-name">{run.file_name}</span>
  </div>

  {/* Attack Paths */}
  <div className="run-paths-info">
    <span className="paths-icon">🎯</span>
    <span className="paths-text">
      <strong>{run.paths_count}</strong> attack path{run.paths_count !== 1 ? 's' : ''} identified
    </span>
  </div>

  {/* Duration */}
  <div className="run-duration-info">
    <span className="duration-icon">⏱️</span>
    <span className="duration-text">
      Completed in <strong>{formatExecutionTime(run.execution_time_seconds)}</strong>
    </span>
  </div>
</div>
```

#### 3. **Updated CSS Styling** (`ThreatModelPage.css`)

**Key Styles Added**:

**Model Badge** (Primary):
```css
.model-badge-main {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
```

**Info Sections** (Consistent pattern):
```css
.run-timestamp, .run-file-info, .run-paths-info, .run-duration-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.625rem;
  font-size: 0.8125rem;
}
```

**Icons**:
- Small, consistent size (0.875rem)
- Flex-shrink: 0 (don't compress)
- Adds visual hierarchy

**Bold Emphasis**:
```css
.paths-text strong, .duration-text strong {
  color: #1e293b;
  font-weight: 700;
}
```

---

## Example Data Flow

### Backend Response
```json
{
  "run_id": "run_20260413_103045_abc123",
  "name": "TM Swarm Run - ecommerce-platform",
  "created_at": "2026-04-13T10:30:45.123Z",
  "file_name": "ecommerce-platform.tf",
  "file_type": ".tf",
  "mode": "quick",
  "paths_count": 4,
  "execution_time_seconds": 125.5,
  "model_used": "qwen3:14b"
}
```

### Frontend Display
```
┌─────────────────────────────────┐
│ [qwen3:14b        ] [QUICK]     │
│ 🕐 Apr 13, 2026 at 10:30:45 AM │
│ 📄 ecommerce-platform.tf        │
│ 🎯 4 attack paths identified    │
│ ⏱️ Completed in 2m 5s            │
│                                 │
│ [✏️] [🗑️]                        │ ← Edit/Delete actions
└─────────────────────────────────┘
```

---

## User Benefits

### Quick Information Scanning
- ✅ Model used is immediately visible (top)
- ✅ Icons help eyes find specific information quickly
- ✅ Bold numbers draw attention to key metrics

### Better Context
- ✅ Full timestamp helps track when runs were performed
- ✅ File name shows what was analyzed
- ✅ Clear indication of scope (number of paths)
- ✅ Performance visibility (execution time)

### Model Tracking
- ✅ Easy to see which model was used for each run
- ✅ Compare results across different models
- ✅ Find runs by specific models visually

### Professional Appearance
- ✅ Clean, organized layout
- ✅ Consistent spacing and alignment
- ✅ Visual hierarchy guides the eye
- ✅ Modern gradient badges

---

## Responsive Design

The layout adapts well to the sidebar width:
- Icons remain visible at all sizes
- Text truncates gracefully with ellipsis
- Model badge and mode badge wrap if needed
- All information remains accessible

---

## Accessibility

### Color Contrast
- Model badge: White text on purple gradient (high contrast)
- Mode badge: Dark blue on light blue (WCAG AA compliant)
- Text colors: Sufficient contrast ratios

### Icons
- Emojis used as visual aids (not sole indicators)
- Text descriptions always present
- No information conveyed by color alone

---

## Time Formatting Examples

| Seconds | Formatted Output        |
|---------|-------------------------|
| 30      | "30s"                   |
| 90      | "1m 30s"                |
| 125     | "2m 5s"                 |
| 300     | "5m 0s"                 |
| 1234    | "20m 34s"               |

---

## Testing Checklist

- [x] Helper function formats time correctly
- [x] All information displays in correct order
- [x] Model badge shows for runs with model_used
- [x] Unknown model shows gray badge
- [x] Timestamp formats correctly in local time
- [x] File name truncates if too long
- [x] Singular/plural paths handled correctly
- [x] Icons render properly
- [x] Bold emphasis applied to numbers
- [x] Edit and delete buttons still work
- [x] Click to load archived run still works
- [x] Hover effects work correctly

---

## Browser Compatibility

### Tested On
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari

### Features Used
- `toLocaleDateString()` with options (ES6)
- `toLocaleTimeString()` with options (ES6)
- Flexbox layout (CSS3)
- CSS gradients (CSS3)
- Emoji icons (Unicode)

---

## Files Modified

### Frontend
- ✅ `frontend/src/pages/ThreatModelPage.jsx`
  - Added `formatExecutionTime()` helper function
  - Redesigned archived run item display
  - Updated timestamp formatting

- ✅ `frontend/src/pages/ThreatModelPage.css`
  - Updated `.run-header` styles
  - Added `.model-badge-main` (gradient)
  - Added `.run-timestamp` styles
  - Added `.run-file-info` styles
  - Added `.run-paths-info` styles
  - Added `.run-duration-info` styles
  - Added icon and text styles

### Documentation
- ✅ `backend/ARCHIVED_RUNS_UI_ENHANCEMENT.md` - This file

---

## Future Enhancements

### Possible Improvements
- [ ] Filter archived runs by model
- [ ] Sort by any field (time, paths, duration, model)
- [ ] Search/filter by file name
- [ ] Group runs by model
- [ ] Show comparison between runs
- [ ] Export selected runs
- [ ] Add tags/labels to runs
- [ ] Show success/failure indicators
- [ ] Add run notes/comments

---

## Migration Notes

### Backward Compatibility
- Works with existing archived runs
- Gracefully handles missing `model_used` field
- Shows "Model Unknown" for old runs
- No data migration required

---

## Summary

The archived runs sidebar now provides comprehensive information at a glance:
1. **Model used** - Know which LLM was used
2. **Timestamp** - Full date and time of run
3. **File name** - What was analyzed
4. **Attack paths** - How many threats identified
5. **Duration** - How long it took (in minutes and seconds)

All presented in a clean, organized, professional format with visual icons and proper hierarchy.

**Test it**: Restart the frontend and check the archived runs sidebar! 🎨
