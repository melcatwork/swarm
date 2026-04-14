# Cancel Run Feature Implementation

**Date**: 2026-04-14
**Status**: ✅ Completed

## Overview
Implemented stop/cancel button functionality to allow users to cancel long-running threat modeling operations. The feature provides frontend-backend synchronization with proper state management and graceful cancellation handling.

## Changes Made

### Backend Changes

#### 1. Job Tracker Enhancements (`backend/app/swarm/job_tracker.py`)
- **Added CANCELLED status** to `JobStatus` enum
- **Added cancellation flag** (`cancelled`) to `Job` class for tracking cancellation state
- **Added Job.cancel()** method to mark jobs as cancelled by user
- **Added Job.is_cancelled()** method to check cancellation status
- **Added JobTracker.cancel_job(job_id)** method to cancel running jobs
- **Added JobTracker.is_job_cancelled(job_id)** method for checking cancellation
- **Updated cleanup logic** to include cancelled jobs in cleanup

#### 2. Cancel API Endpoint (`backend/app/routers/swarm.py`)
- **Added POST /api/swarm/cancel/{job_id}** endpoint
  - Validates job exists before cancellation
  - Prevents cancellation of already completed/failed/cancelled jobs
  - Returns success response with job ID
  - HTTP 404 if job not found
  - HTTP 400 if job cannot be cancelled
  - HTTP 500 if cancellation fails

#### 3. Pipeline Cancellation Checks (`backend/app/routers/swarm.py`)
- **Added cancellation checks** in `_run_quick_pipeline_sync()` function
  - Check after parsing phase
  - Check after exploration phase
  - Check after evaluation phase
  - Check after adversarial validation phase
- **Graceful exit** when cancellation detected (returns immediately, no error)
- **Prevents wasted computation** by stopping at phase boundaries

### Frontend Changes

#### 4. API Client Cancel Support (`frontend/src/api/client.js`)
- **Added cancelRun(jobId)** function to call backend cancel endpoint
- **Added cancelToken parameter** to upload functions:
  - `uploadAndRunSwarm(file, model, cancelToken)`
  - `uploadAndRunQuick(file, model, cancelToken)`
  - `uploadAndRunSingleAgent(file, agentName, model, cancelToken)`
- **Cancel token support** enables immediate HTTP request abortion

#### 5. Threat Model Page Enhancements (`frontend/src/pages/ThreatModelPage.jsx`)
- **Imported axios** for cancel token creation
- **Imported StopCircle** icon from lucide-react
- **Added cancelTokenSource state** to track active cancel tokens
- **Added handleCancelRun()** function:
  - Cancels ongoing HTTP request via axios cancel token
  - Resets UI state (running, currentPhase, currentJobId)
  - Shows toast notification confirming cancellation
  - Handles errors gracefully
- **Updated runSwarm()** function:
  - Creates axios cancel token before request
  - Passes cancel token to API functions
  - Handles cancellation errors (axios.isCancel)
  - Cleans up cancel token in finally block
- **Added Stop button** to UI:
  - Appears only when `running === true`
  - Uses StopCircle icon
  - Styled with btn-danger class
  - Calls handleCancelRun() on click

#### 6. CSS Styling (`frontend/src/pages/ThreatModelPage.css`)
- **Added base button styles** (.btn class)
- **Added btn-primary styles** (blue background)
- **Added btn-secondary styles** (white background with border)
- **Added btn-danger styles** (red background for stop button):
  - Background: #ef4444
  - Hover: #dc2626
  - White text

## How It Works

### User Workflow
1. User uploads IaC file and starts a threat modeling run
2. Stop button appears next to Run buttons while operation is in progress
3. User clicks Stop button to cancel
4. Frontend immediately cancels HTTP request
5. Backend detects cancellation at next phase boundary
6. Backend stops processing and marks job as cancelled
7. Frontend shows "Operation cancelled" toast message
8. UI returns to ready state

### Technical Flow
```
User clicks Stop button
    ↓
handleCancelRun() called
    ↓
Axios cancel token triggered
    ↓
HTTP request aborted
    ↓
Backend receives cancellation (if mid-request)
    ↓
Job marked as CANCELLED in tracker
    ↓
Pipeline checks is_job_cancelled() at phase boundaries
    ↓
Pipeline exits gracefully on next check
    ↓
Frontend catch block handles axios.isCancel()
    ↓
UI state reset, toast notification shown
```

### Cancellation Points
Backend checks for cancellation after:
- **Parsing phase** (after IaC file parsed and threat intel loaded)
- **Exploration phase** (after agents generate attack paths)
- **Evaluation phase** (after paths scored)
- **Adversarial validation phase** (after red/blue team review)

This ensures:
- No wasted computation on cancelled jobs
- Clean exit without partial data corruption
- Immediate response to user cancellation request

## Files Modified

### Backend (2 files)
- `backend/app/swarm/job_tracker.py` — Added cancellation support to job tracking
- `backend/app/routers/swarm.py` — Added cancel endpoint and pipeline checks

### Frontend (3 files)
- `frontend/src/api/client.js` — Added cancel API function and token support
- `frontend/src/pages/ThreatModelPage.jsx` — Added stop button and cancel handler
- `frontend/src/pages/ThreatModelPage.css` — Added button styles including btn-danger

## Testing

### Manual Testing Steps
1. Start backend server: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to http://localhost:5173/model
4. Upload a sample IaC file (e.g., `samples/clouddocs-saas-app.tf`)
5. Click "Quick Run (2 agents)"
6. Observe Stop button appears
7. Click Stop button after a few seconds
8. Verify:
   - ✅ Toast message shows "Threat modeling operation cancelled"
   - ✅ UI returns to ready state
   - ✅ Stop button disappears
   - ✅ No error messages displayed
   - ✅ Can start a new run immediately

### API Testing
```bash
# Start a quick run (in terminal)
curl -X POST http://localhost:8000/api/swarm/run/quick \
  -F "file=@samples/clouddocs-saas-app.tf"

# In another terminal, immediately cancel (replace JOB_ID)
curl -X POST http://localhost:8000/api/swarm/cancel/JOB_ID

# Verify response:
# {
#   "status": "success",
#   "message": "Job JOB_ID has been cancelled",
#   "job_id": "JOB_ID"
# }
```

## Benefits

1. **User Control**: Users can stop long-running operations without waiting
2. **Resource Efficiency**: Backend stops processing when cancelled, saving compute
3. **Better UX**: Clear visual feedback with stop button and toast notifications
4. **Clean State**: Proper cleanup prevents orphaned processes or corrupt state
5. **Synchronization**: Frontend and backend stay in sync during cancellation
6. **Graceful Handling**: No errors or warnings for user-initiated cancellations
7. **Immediate Response**: HTTP request aborted immediately via cancel token

## Known Limitations

1. **Phase Boundary Cancellation**: Backend only checks for cancellation between phases, not during LLM calls. If an LLM call is in progress, cancellation waits until that call completes.

2. **No Partial Results**: Cancelled operations don't save partial results. Future enhancement could save completed phases.

3. **No Background Job Support**: Current implementation works with synchronous API calls. Background job cancellation would require additional polling logic.

## Future Enhancements

1. **Progress Indicators**: Show which phase is currently executing
2. **Partial Result Saving**: Save completed phases before cancellation
3. **Background Job Support**: Implement true async jobs with status polling
4. **Cancellation Confirmation**: Add confirmation dialog for long-running operations
5. **Cancel All**: Add ability to cancel all running jobs at once
6. **Cancel Timeout**: Add timeout for graceful cancellation before force-kill

## Notes

- Cancellation is graceful and doesn't leave orphaned processes
- Cancel token approach works with synchronous API endpoints
- Job tracker maintains history of cancelled jobs for debugging
- Frontend handles axios cancellation errors separately from other errors
- Stop button only appears during active operations (when `running === true`)
- Backend logs all cancellations for audit trail
