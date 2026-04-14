# Long-Running Operation UI Enhancements

**Date**: 2026-04-14
**Status**: ✅ Implemented

## Problem
Users running threat modeling pipelines (14-30 minutes) couldn't tell if the frontend and backend were still alive during long operations. The 30-second timeout was causing "Backend Unreachable" errors, and the UI provided minimal feedback.

## Solution Implemented

### 1. Extended Backend Timeout (Frontend)
**File**: `frontend/src/api/client.js:13`
- Increased default axios timeout from **30 seconds** to **30 minutes** (1,800,000ms)
- Prevents premature timeout errors during long-running LLM operations
- Aligns with pipeline-specific timeouts already configured

### 2. Enhanced Visual Progress Indicators
**Files**:
- `frontend/src/pages/ThreatModelPage.jsx`
- `frontend/src/pages/ThreatModelPage.css`

#### Features Added:

**A. Elapsed Time Display (MM:SS format)**
- Large, prominent countdown timer showing elapsed time
- Formatted as `MM:SS` (e.g., `15:42`)
- Purple gradient background for high visibility
- Updates every second

**B. Backend Keepalive Polling**
- Polls backend `/api/health` endpoint every 10 seconds during operation
- Visual indicators:
  - 🟢 **Green pulse**: Backend responsive
  - 🔴 **Red pulse**: Backend not responding
- Displays "Last check: HH:MM:SS" timestamp
- Automatically starts when pipeline begins, stops when complete

**C. Frontend Heartbeat Indicator**
- Always shows frontend is active with green pulsing dot
- Reassures user the UI hasn't frozen

**D. Contextual Status Messages**
- Dynamic messages based on elapsed time:
  - **0-60s**: "Initializing threat modeling pipeline..."
  - **1-3 min**: "Parsing infrastructure and building asset graph..."
  - **3-10 min**: "Exploration agents analyzing attack vectors..."
  - **10-15 min**: "Evaluation crew scoring attack paths..."
  - **15-20 min**: "Adversarial validation in progress..."
  - **20-30 min**: "Final arbitration and mitigation mapping..."
  - **30+ min**: "Long-running operation, almost there..."

**E. Long Operation Warning**
- After 10 minutes, displays informational notice:
  - ⚠️ "Long-running operation detected. This is normal for comprehensive threat modeling with LLMs."
  - Shows expected duration based on pipeline mode

**F. Visual Pulse Animations**
- **Alive pulse**: Smooth expanding ring animation (green)
- **Warning pulse**: Fading opacity animation (red)
- **Progress bar**: Continuous left-to-right sweep animation

## Implementation Details

### New State Variables
```javascript
const [heartbeat, setHeartbeat] = useState(0);           // Seconds elapsed
const [backendAlive, setBackendAlive] = useState(true);  // Backend health status
const [lastBackendCheck, setLastBackendCheck] = useState(null); // Last health check timestamp
```

### New Helper Functions
```javascript
formatElapsedTime(seconds)           // Returns "MM:SS" format
getContextualStatusMessage(seconds)  // Returns phase-appropriate message
```

### Enhanced useEffect Hook
- **Heartbeat counter**: Updates every 1 second
- **Backend health check**: Polls every 10 seconds
- **Cleanup**: Clears intervals when operation completes
- **Initial check**: Immediate health check when operation starts

### CSS Enhancements
- `.elapsed-time-display`: Large timer with gradient background
- `.heartbeat-pulse`: Animated pulse indicators (alive/dead states)
- `.heartbeat-indicators`: Flex container for status items
- `.long-operation-notice`: Warning banner for extended operations
- `@keyframes pulse-beat`: Expanding ring animation for alive state
- `@keyframes pulse-warning`: Fading animation for dead state

## User Experience Improvements

### Before
- ❌ 30-second timeout caused "Backend Unreachable" errors
- ❌ No indication of elapsed time
- ❌ No way to tell if backend is responding
- ❌ Generic "Running for Xs..." message
- ❌ Users uncertain if operation is progressing

### After
- ✅ 30-minute timeout prevents premature errors
- ✅ Large, visible elapsed time counter (MM:SS)
- ✅ Real-time backend health checks with visual indicators
- ✅ Contextual messages explaining what's happening
- ✅ Clear confirmation that both frontend and backend are alive
- ✅ Warning notice for operations exceeding 10 minutes
- ✅ Professional, reassuring UI during long waits

## Testing Recommendations

1. **Quick Run Test** (~14 minutes):
   ```bash
   # Start backend
   cd backend && source .venv/bin/activate
   uvicorn app.main:app --reload --port 8000

   # Start frontend
   cd frontend && npm run dev

   # Upload a .tf file and run Quick Run mode
   # Observe: Elapsed time, backend health checks, contextual messages
   ```

2. **Full Swarm Test** (~25-30 minutes):
   ```bash
   # Run full swarm mode
   # Verify: Long operation warning appears after 10 minutes
   # Confirm: Backend keepalive polls continue throughout
   ```

3. **Backend Failure Simulation**:
   ```bash
   # Start operation, then kill backend
   # Verify: Backend status changes to "Not Responding" with red pulse
   # Confirm: Frontend continues to show elapsed time
   ```

4. **Timeout Verification**:
   ```bash
   # Run operation that takes 20+ minutes
   # Verify: No timeout errors occur
   # Confirm: Operation completes successfully
   ```

## Files Modified

### Frontend
- `frontend/src/api/client.js` — Extended timeout to 30 minutes
- `frontend/src/pages/ThreatModelPage.jsx` — Added heartbeat, keepalive, contextual messages
- `frontend/src/pages/ThreatModelPage.css` — Added styles for new UI elements

## Performance Impact
- **Minimal**: Health checks every 10 seconds add negligible network overhead
- **No blocking**: Async health checks don't block main operation
- **Efficient**: Single state update per second for heartbeat counter

## Future Enhancements (Optional)

1. **WebSocket/SSE support**: Real-time progress events from backend
2. **Phase progress bars**: Visual breakdown of exploration → evaluation → adversarial
3. **Estimated time remaining**: Based on historical run data
4. **Abort/cancel button**: Allow user to cancel long-running operations
5. **Background mode**: Continue operation in background, notify when complete

## Lessons Learned

1. **Timeout configuration matters**: Default 30s timeout is too short for LLM operations
2. **Visual feedback is critical**: Users need constant reassurance during long waits
3. **Backend health checks**: Simple polling provides valuable status information
4. **Contextual messaging**: Phase-appropriate messages improve UX significantly
5. **Animations draw attention**: Pulse animations indicate activity without being distracting

## References
- Related: `backend/COMPREHENSIVE_BACKEND_TEST_REPORT.md` — Pipeline execution times
- Related: `CLAUDE.md` — Performance characteristics section
