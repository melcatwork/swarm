# Script Updates Changelog

## Changes Made (2026-04-12)

### 1. `.env` - LLM Model Configuration
**Changed:**
- `OLLAMA_MODEL=qwen3:4b` → `OLLAMA_MODEL=qwen3:14b`

**Reason:**
- qwen3:4b (4B parameters) was too small to generate valid JSON attack paths
- qwen3:14b (14B parameters) provides much better structured output
- Fixes the "0 attack paths" issue

---

### 2. `start-all.sh` - Startup Script

**Changes:**

#### Added .env validation check (lines 57-67)
```bash
# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "✗ .env file not found"
    exit 1
fi

# Show configured model
OLLAMA_MODEL=$(grep "^OLLAMA_MODEL=" .env | cut -d'=' -f2)
echo "Configured Model: $OLLAMA_MODEL"
```

#### Updated model check (lines 116-124)
**Before:**
```bash
echo -n "  Checking for qwen3:4b model... "
if ollama list | grep -q "qwen3:4b"; then
    echo "✓ Found"
else
    ollama pull qwen3:4b
fi
```

**After:**
```bash
echo -n "  Checking for qwen3:14b model... "
if ollama list | grep -q "qwen3:14b"; then
    echo "✓ Found"
else
    echo "Pulling qwen3:14b (this may take a few minutes, ~9.3GB)..."
    ollama pull qwen3:14b
fi
```

#### Added agent recommendations (lines 280-284)
```bash
echo "Recommended Agents for Single Agent Testing:"
echo "  apt29_cozy_bear      # Best for cloud infrastructure"
echo "  scattered_spider     # Best for identity/SSO/MFA testing"
echo "  Use in frontend: Select agent → Run Single Agent Test"
```

---

### 3. `stop-all.sh` - Shutdown Script

**Changes:**

#### Added port status checking (lines 17-37)
```bash
# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Show current status before stopping
echo "Current Status:"
if check_port 5173; then
    echo "  Frontend:  Running (port 5173)"
else
    echo "  Frontend:  Not running"
fi
# ... similar for 8000 and 11434
```

#### Added Python process cleanup (lines 52-55)
```bash
# Also kill any Python processes running the backend
if pkill -f "python.*app.main" 2>/dev/null; then
    sleep 1
fi
```

#### Added verification after shutdown (lines 65-88)
```bash
# Verify all services stopped
echo "Verifying services stopped:"
if check_port 5173; then
    echo "  Frontend:  Still running on port 5173"
    STILL_RUNNING=true
else
    echo "  Frontend:  ✓ Stopped"
fi
# ... verification for all services
```

---

## New Files Created

### 4. `AGENT_TESTING_GUIDE.md`
Complete guide for:
- Recommended agents for testing (apt29_cozy_bear, scattered_spider)
- Detailed agent capabilities and use cases
- How to test via frontend and API
- Expected results with qwen3:14b
- Troubleshooting guide
- Performance comparison table

---

## Testing the Changes

### 1. Restart with new scripts:
```bash
./stop-all.sh
./start-all.sh
```

### 2. Verify model in use:
```bash
curl -s http://localhost:8000/api/health
tail -f logs/backend.log | grep "Ollama Model"
# Should show: qwen3:14b
```

### 3. Test single agent:
- Frontend: http://localhost:5173
- Upload: `samples/ecommerce-platform.tf`
- Agent: Select "APT29 (Cozy Bear)"
- Click: "Single Agent Test"
- Wait: 5-10 minutes
- Result: Should show attack paths (not 0)

---

## Key Improvements

✅ **Model Quality:** 4B → 14B parameters (3.5x larger)
✅ **Validation:** Scripts now check .env and ports
✅ **Visibility:** Shows which model is configured
✅ **Guidance:** Recommends best agents for testing
✅ **Verification:** Confirms services stopped properly
✅ **Documentation:** Complete testing guide included

---

## Rollback (if needed)

If qwen3:14b is too slow or too large:

```bash
# Edit .env
OLLAMA_MODEL=qwen3:8b  # Middle ground: 5.2 GB

# Or use cloud models
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

Note: qwen3:4b is NOT recommended - it generates 0 attack paths.

---

## Questions?

- Check logs: `tail -f logs/backend.log`
- Review guide: `cat AGENT_TESTING_GUIDE.md`
- Test health: `curl http://localhost:8000/api/health`
