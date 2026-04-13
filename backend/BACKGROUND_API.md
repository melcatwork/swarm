# Background Pipeline API Usage Guide

The swarm threat modeling pipeline takes 5-10 minutes to complete. To prevent HTTP timeouts and keep your backend responsive, use the **background processing endpoints**.

## Quick Start

### 1. Submit a File for Analysis

```bash
curl -X POST http://localhost:8000/api/swarm/run/quick/background \
  -F "file=@samples/file-transfer-system.tf"
```

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "Pipeline started for file-transfer-system.tf. Use the status_url to check progress.",
  "estimated_time_minutes": 7,
  "status_url": "/api/swarm/job/a1b2c3d4-e5f6-7890-abcd-ef1234567890/status"
}
```

**Save the `job_id`** - you'll need it to check status and get results!

### 2. Check Job Status

Poll this endpoint every 10-30 seconds to see progress:

```bash
curl http://localhost:8000/api/swarm/job/a1b2c3d4-e5f6-7890-abcd-ef1234567890/status
```

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "file-transfer-system.tf",
  "status": "exploration",  // pending → parsing → exploration → evaluation → adversarial → mitigations → completed
  "progress_percent": 35,
  "current_phase": "Exploring attack paths (2 agents)",
  "started_at": "2026-04-10T12:00:00Z",
  "completed_at": null,
  "elapsed_seconds": 120.5,
  "error": null,
  "logs": [
    "2026-04-10T12:00:00Z - [a1b2c3d4] pending: Starting pipeline (0%)",
    "2026-04-10T12:00:05Z - [a1b2c3d4] parsing: Parsing IaC file (5%)",
    "2026-04-10T12:00:10Z - [a1b2c3d4] exploration: Exploring attack paths (20%)"
  ]
}
```

**Status Flow:**
1. `pending` (0%) - Job queued
2. `parsing` (5-10%) - Parsing IaC file
3. `exploration` (20-50%) - AI agents exploring attack paths
4. `evaluation` (50-75%) - Scoring attack paths
5. `adversarial` (75-90%) - Red/blue team validation
6. `mitigations` (90-95%) - Mapping mitigations
7. `completed` (100%) - Done! Ready to fetch results

### 3. Get Results (When Complete)

Once `status` is `"completed"`:

```bash
curl http://localhost:8000/api/swarm/job/a1b2c3d4-e5f6-7890-abcd-ef1234567890/result
```

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "result": {
    "status": "ok",
    "asset_graph": { ... },
    "exploration_summary": { ... },
    "evaluation_summary": { ... },
    "adversarial_summary": { ... },
    "final_paths": [ ... ],  // Full attack paths with mitigations
    "executive_summary": "...",
    "execution_time_seconds": 420.5
  }
}
```

## List All Jobs

See recent pipeline runs:

```bash
curl http://localhost:8000/api/swarm/jobs?limit=10
```

## Shell Script Example

Save this as `run_swarm_analysis.sh`:

```bash
#!/bin/bash

FILE="${1:-samples/file-transfer-system.tf}"

echo "Submitting $FILE for analysis..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/swarm/run/quick/background \
  -F "file=@$FILE")

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"
echo "Estimated time: 7 minutes"
echo ""

# Poll status
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/swarm/job/$JOB_ID/status")
  CURRENT_STATUS=$(echo $STATUS | jq -r '.status')
  PROGRESS=$(echo $STATUS | jq -r '.progress_percent')
  PHASE=$(echo $STATUS | jq -r '.current_phase')

  echo -ne "\r[$PROGRESS%] $CURRENT_STATUS: $PHASE                    "

  if [ "$CURRENT_STATUS" = "completed" ]; then
    echo -e "\n\n✓ Analysis complete!"
    curl -s "http://localhost:8000/api/swarm/job/$JOB_ID/result" | jq '.result' > "threat_model_$JOB_ID.json"
    echo "Results saved to: threat_model_$JOB_ID.json"
    break
  elif [ "$CURRENT_STATUS" = "failed" ]; then
    echo -e "\n\n✗ Analysis failed!"
    echo $STATUS | jq '.error'
    exit 1
  fi

  sleep 10  # Poll every 10 seconds
done
```

Run it:
```bash
chmod +x run_swarm_analysis.sh
./run_swarm_analysis.sh samples/file-transfer-system.tf
```

## Integration with Frontend

### JavaScript/TypeScript Example

```typescript
async function runThreatModel(file: File) {
  // 1. Submit file
  const formData = new FormData();
  formData.append('file', file);

  const submitResp = await fetch('http://localhost:8000/api/swarm/run/quick/background', {
    method: 'POST',
    body: formData
  });
  const { job_id } = await submitResp.json();

  // 2. Poll for status
  const pollStatus = async () => {
    const statusResp = await fetch(`http://localhost:8000/api/swarm/job/${job_id}/status`);
    const status = await statusResp.json();

    // Update UI
    updateProgressBar(status.progress_percent);
    updateStatusMessage(status.current_phase);

    if (status.status === 'completed') {
      // 3. Fetch results
      const resultResp = await fetch(`http://localhost:8000/api/swarm/job/${job_id}/result`);
      const { result } = await resultResp.json();
      displayResults(result);
    } else if (status.status === 'failed') {
      showError(status.error);
    } else {
      // Continue polling
      setTimeout(pollStatus, 10000);  // Poll every 10 seconds
    }
  };

  pollStatus();
}
```

## Error Handling

### Job Not Found (404)
```bash
curl http://localhost:8000/api/swarm/job/invalid-id/status
# Response: {"detail": "Job invalid-id not found"}
```

### Job Still Running (425 - Too Early)
```bash
curl http://localhost:8000/api/swarm/job/{job_id}/result
# Response: {"detail": "Job is still running (status: exploration, 35% complete)..."}
```

### Job Failed (500)
```bash
curl http://localhost:8000/api/swarm/job/{job_id}/result
# Response: {"detail": "Job failed: OpenAI API timeout"}
```

## Comparison: Sync vs Background

### Old Way (Synchronous)
```bash
# POST /api/swarm/run/quick
# - Waits 5-10 minutes for response
# - Connection can timeout
# - Backend blocked during execution
# - No progress updates
```

### New Way (Background)
```bash
# POST /api/swarm/run/quick/background
# - Returns immediately with job_id
# - No connection timeouts
# - Backend stays responsive
# - Real-time progress updates via polling
# - Multiple jobs can run concurrently
```

## Benefits

✅ **No Timeouts** - HTTP connections don't time out during long analyses
✅ **Progress Tracking** - See real-time progress and current phase
✅ **Backend Responsive** - Backend stays available for other requests
✅ **Concurrent Jobs** - Run multiple analyses simultaneously (up to 2)
✅ **Better UX** - Show progress bars and status updates in UI
✅ **Debugging** - View logs to see where failures occur

## Notes

- Maximum 2 concurrent pipeline jobs (configurable in `executor = ThreadPoolExecutor(max_workers=2)`)
- Jobs are kept in memory (lost on server restart)
- Old completed/failed jobs are automatically cleaned up after 100 total jobs
- Poll status every 10-30 seconds (don't overload with rapid polls)
- Logs show last 10 entries only (to keep response size small)

## Troubleshooting

### Backend connection lost during analysis

**Old problem:** With synchronous endpoints, HTTP connections would timeout after 2-5 minutes, even though the backend was still running.

**Solution:** Use `/run/quick/background` instead. The HTTP request returns immediately, and you poll for status separately.

### How do I know if the analysis is still running?

Check the `/job/{job_id}/status` endpoint. If `status` is anything other than `"completed"` or `"failed"`, it's still running. Look at:
- `status` - Current phase (exploration, evaluation, etc.)
- `progress_percent` - How far along (0-100%)
- `current_phase` - Human-readable description
- `elapsed_seconds` - How long it's been running

### Backend keeps trying to call OpenAI

See the main README for Ollama configuration. Make sure:
1. `LLM_PROVIDER=ollama` in `.env`
2. Ollama is running: `ollama serve`
3. Model is pulled: `ollama pull qwen3:4b`
4. Backend restarted after `.env` changes
