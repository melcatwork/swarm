# 🚀 Swarm TM - Quick Start

Start all services (Ollama, Backend, Frontend) with one command!

## ⚡ Quick Start (Recommended - Tmux)

```bash
./start-all-tmux.sh
```

**What it does:**
- ✅ Starts Ollama (or detects if already running)
- ✅ Starts Backend (FastAPI on port 8000)
- ✅ Starts Frontend (Vite on port 5173)
- ✅ Shows all logs in split-screen tmux panes

**Tmux Layout:**
```
┌─────────────┬─────────────┐
│   Ollama    │   Backend   │
├─────────────┼─────────────┤
│  Frontend   │ Quick Cmds  │
└─────────────┴─────────────┘
```

**Tmux Navigation:**
- `Ctrl+B` then `arrow keys` - Switch between panes
- `Ctrl+B` then `[` - Scroll mode (press `q` to exit)
- `Ctrl+B` then `d` - Detach (services keep running)
- `tmux attach -t swarm-tm` - Re-attach later

## 🔧 Alternative: Standard Start

If you don't have tmux:

```bash
./start-all.sh
```

This starts all services in background and shows combined logs.

## 🛑 Stop All Services

```bash
./stop-all.sh
```

Or press `Ctrl+C` in each tmux pane.

## 📊 Service URLs

Once started, access:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React UI |
| **Backend** | http://localhost:8000 | FastAPI server |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Ollama** | http://localhost:11434 | Local LLM server |

## ✅ Quick Health Check

```bash
# Check backend
curl http://localhost:8000/api/health

# Check Ollama
curl http://localhost:11434/api/tags

# Check frontend
curl http://localhost:5173
```

## 🧪 Run Test Analysis

After starting all services:

```bash
cd backend
./test_background_api.sh ../samples/file-transfer-system.tf
```

This will:
1. Submit the sample Terraform file
2. Poll for progress every 10 seconds
3. Show real-time status updates
4. Save results when complete (5-8 minutes)

## 📝 Manual API Testing

### Submit Analysis

```bash
curl -X POST http://localhost:8000/api/swarm/run/quick/background \
  -F "file=@samples/file-transfer-system.tf"
```

Save the `job_id` from response!

### Check Status

```bash
# Replace YOUR_JOB_ID with actual job ID
curl http://localhost:8000/api/swarm/job/YOUR_JOB_ID/status
```

### Get Results (when complete)

```bash
curl http://localhost:8000/api/swarm/job/YOUR_JOB_ID/result > results.json
```

## 🐛 Troubleshooting

### "Ollama not found"
```bash
# Install Ollama
# macOS: Download from https://ollama.ai
# Linux: curl https://ollama.ai/install.sh | sh
```

### "Model qwen3:4b not found"
```bash
ollama pull qwen3:4b
```

### "Backend won't start"
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### "Frontend won't start"
```bash
cd frontend  # or client/ui/web
npm install
```

### "Port already in use"
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9  # Backend port
lsof -ti:5173 | xargs kill -9  # Frontend port
lsof -ti:11434 | xargs kill -9 # Ollama port
```

### "OpenAI API errors"
Check `.env` file:
```bash
# Should have:
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
OPENAI_API_KEY=""
```

Then restart backend:
```bash
./stop-all.sh
./start-all-tmux.sh
```

## 📂 Log Files

Logs are saved to `logs/` directory:

```bash
tail -f logs/ollama.log     # Ollama logs
tail -f logs/backend.log    # Backend logs
tail -f logs/frontend.log   # Frontend logs
```

## 🎯 Development Workflow

### Day-to-day usage:

```bash
# Start everything
./start-all-tmux.sh

# Do your work in browser:
# - http://localhost:5173 (UI)
# - http://localhost:8000/docs (API)

# Stop when done
./stop-all.sh
```

### Making code changes:

**Backend changes:**
- Edit Python files in `backend/app/`
- Uvicorn auto-reloads on file save
- Watch logs in tmux pane or `tail -f logs/backend.log`

**Frontend changes:**
- Edit files in `frontend/src/`
- Vite hot-reloads automatically
- Changes appear instantly in browser

## 📚 Additional Resources

- **Background API Guide:** `backend/BACKGROUND_API.md`
- **Quick API Reference:** `QUICK_START_BACKGROUND_API.md`
- **Test Ollama+CrewAI:** `backend/test_ollama_crewai.py`

## ⚡ Quick Commands Reference

```bash
# Start all services (tmux - recommended)
./start-all-tmux.sh

# Start all services (standard)
./start-all.sh

# Stop all services
./stop-all.sh

# Run full test
cd backend && ./test_background_api.sh ../samples/file-transfer-system.tf

# Check health
curl http://localhost:8000/api/health

# List recent jobs
curl http://localhost:8000/api/swarm/jobs

# View logs
tail -f logs/backend.log

# Re-attach to tmux session
tmux attach -t swarm-tm
```

## 🎓 First Time Setup

```bash
# 1. Install Ollama
# Download from https://ollama.ai

# 2. Pull model
ollama pull qwen3:4b

# 3. Setup backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..

# 4. Setup frontend (if exists)
cd frontend
npm install
cd ..

# 5. Start everything!
./start-all-tmux.sh
```

## 💡 Tips

- **Use tmux mode** for best experience - see all logs at once
- **Detach tmux** (`Ctrl+B` then `d`) to keep services running while you do other work
- **Check logs first** if something fails - `logs/backend.log` has detailed errors
- **Ollama stays running** after `./stop-all.sh` - it won't interfere with other projects
- **Background API** prevents connection timeouts - always use `/run/quick/background`

---

**Need help?** Check `backend/BACKGROUND_API.md` for detailed API documentation.
