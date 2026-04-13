# Quick Start: Background API (Prevents Connection Timeouts!)

## 🚀 One-Line Test

```bash
cd backend && ./test_background_api.sh ../samples/file-transfer-system.tf
```

This automatically submits, polls, and retrieves results!

## 📋 Manual Steps

### 1. Submit File (Instant Response ⚡)

```bash
curl -X POST http://localhost:8000/api/swarm/run/quick/background \
  -F "file=@samples/file-transfer-system.tf"
```

**Save the `job_id` from response!**

### 2. Check Progress (Poll Every 10s 🔄)

```bash
# Replace YOUR_JOB_ID with actual job_id
curl http://localhost:8000/api/swarm/job/YOUR_JOB_ID/status
```

Watch for:
- `progress_percent`: 0 → 100%
- `status`: pending → parsing → exploration → evaluation → adversarial → mitigations → **completed**

### 3. Get Results (When Complete ✅)

```bash
curl http://localhost:8000/api/swarm/job/YOUR_JOB_ID/result > results.json
```

## 🎯 Key Differences

| Old Way (`/run/quick`) | New Way (`/run/quick/background`) |
|------------------------|-----------------------------------|
| ❌ Waits 5-10 minutes | ✅ Returns instantly with job_id |
| ❌ Connection timeouts | ✅ No timeouts (separate polling) |
| ❌ No progress updates | ✅ Real-time progress (0-100%) |
| ❌ Backend appears frozen | ✅ Backend stays responsive |
| ❌ "Backend Unreachable" errors | ✅ Always connected |

## 🛠️ Frontend Integration (3 Steps)

```typescript
// 1. Submit
const { job_id } = await fetch('/api/swarm/run/quick/background', {
  method: 'POST',
  body: formData
}).then(r => r.json());

// 2. Poll status
const pollStatus = setInterval(async () => {
  const status = await fetch(`/api/swarm/job/${job_id}/status`).then(r => r.json());

  updateProgressBar(status.progress_percent);
  updateStatusText(status.current_phase);

  if (status.status === 'completed') {
    clearInterval(pollStatus);

    // 3. Get results
    const { result } = await fetch(`/api/swarm/job/${job_id}/result`).then(r => r.json());
    displayResults(result);
  }
}, 10000); // Poll every 10 seconds
```

## 📊 Status Flow

```
pending (0%)
   ↓
parsing (10%) - "Parsing IaC file"
   ↓
exploration (20-50%) - "Exploring attack paths (2 agents)"
   ↓
evaluation (50-75%) - "Scoring attack paths (5 evaluators)"
   ↓
adversarial (75-90%) - "Red/blue team validation"
   ↓
mitigations (90-95%) - "Mapping mitigations"
   ↓
completed (100%) - "Ready to fetch results!"
```

## ⚠️ Important Notes

1. **Always poll the status endpoint** - Don't assume success just because you got a job_id
2. **Poll every 10-15 seconds** - Don't spam the server with rapid polls
3. **Handle failures** - Check if `status === 'failed'` and display `error` message
4. **Show progress** - Display `progress_percent` and `current_phase` to users
5. **Backend restart** - Restart backend after code changes: `pkill -f uvicorn && uvicorn app.main:app --reload`

## 📚 Full Documentation

- `backend/BACKGROUND_API.md` - Complete API reference with examples
- `backend/test_background_api.sh` - Automated test script
- `backend/app/swarm/job_tracker.py` - Source code for job tracking

## 🐛 Troubleshooting

**"Backend Unreachable" error?**
→ Use `/run/quick/background` instead of `/run/quick`

**Status shows "pending" forever?**
→ Check backend logs: `tail -f backend/logs/app.log` (if logging to file)
→ Or watch terminal where `uvicorn` is running

**Still getting OpenAI errors?**
→ Ensure `LLM_PROVIDER=ollama` in `.env`
→ Ollama must be running: `ollama serve`
→ Restart backend after `.env` changes

**Job not found (404)?**
→ Jobs are stored in memory (lost on restart)
→ Check job ID is correct
→ Use `/api/swarm/jobs` to list all recent jobs
