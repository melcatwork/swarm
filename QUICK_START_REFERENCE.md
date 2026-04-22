# Swarm TM Quick Start Reference

**Updated**: 2026-04-21  
**Version**: v2.0 (Multi-provider support + 10-step paths)

---

## 🚀 Quick Start

### 1. Check Your Configuration

```bash
# View your LLM provider
grep "^LLM_PROVIDER=" .env

# Should show one of:
# LLM_PROVIDER=ollama      (Local, free)
# LLM_PROVIDER=bedrock     (AWS, requires credentials)
# LLM_PROVIDER=anthropic   (Anthropic API, requires key)
```

### 2. Start All Services

**Option A: Tmux Mode (Recommended)**
```bash
./start-all-tmux.sh
```
- Split panes for easy monitoring
- `Ctrl+B` then arrow keys to switch panes
- `Ctrl+B` then `d` to detach (keeps running)

**Option B: Standard Mode**
```bash
./start-all.sh
```
- Shows logs in terminal
- `Ctrl+C` to stop

### 3. Access Services

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop Services

```bash
./stop-all.sh
```

---

## 📊 Four Run Modes

| Mode | Endpoint | Duration | Use Case |
|------|----------|----------|----------|
| **Full** | `/api/swarm/run` | 25-30 min | Production threat models (all agents) |
| **Quick** | `/api/swarm/run/quick` | ~14 min | Development, rapid testing (2 agents) |
| **Single** | `/api/swarm/run/single?agent_name=...` | 10-15 min | Specific threat actor analysis |
| **Swarm** | `/api/swarm/run/stigmergic` | Varies | Emergent intelligence (sequential) |

---

## 🧪 Quick Tests

### Check Backend Health
```bash
curl http://localhost:8000/api/health
```

### List Available Models
```bash
curl http://localhost:8000/api/llm/models
```

### Run Quick Analysis
```bash
curl -X POST http://localhost:8000/api/swarm/run/quick \
  -F "file=@samples/capital-one-breach-replica.tf"
```

---

## 📁 Sample Files

| File | Description | Expected Output |
|------|-------------|-----------------|
| `capital-one-breach-replica.tf` | Capital One 2019 breach | 7-8 step paths |
| `scarleteel-breach-replica.tf` | Scarleteel cryptomining campaign | 8-9 step paths |
| `llmjacking-breach-replica.tf` | LLM infrastructure compromise | 6-7 step paths |

---

## 🔧 LLM Provider Setup

### Ollama (Local)
```bash
# .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3.5:27b
OLLAMA_BASE_URL=http://localhost:11434

# Install Ollama
# https://ollama.ai

# Pull model
ollama pull qwen3.5:27b
```

### AWS Bedrock
```bash
# .env
LLM_PROVIDER=bedrock
BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
AWS_BEARER_TOKEN_BEDROCK=your_token_here
AWS_REGION=us-east-1
```

### Anthropic API
```bash
# .env
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🎯 Recommended Agents

Best for single-agent testing:

- **apt29_cozy_bear** — Nation-state sophistication, cloud-native attacks
- **scattered_spider** — Identity/SSO/MFA specialist
- **cloud_native_attacker** — Cloud services abuse expert

---

## ✨ Recent Updates (2026-04-21)

- ✅ **Attack paths now support up to 10 steps** (was 3-5)
- ✅ Multi-provider support (Ollama/Bedrock/Anthropic)
- ✅ Dynamic model selection via UI
- ✅ Comprehensive test suite
- ✅ Updated scripts with provider awareness

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :11434 # Ollama (if using)

# Kill existing processes
./stop-all.sh

# Try again
./start-all.sh
```

### Model Not Found (Ollama)

```bash
# Check available models
ollama list

# Pull missing model
ollama pull qwen3.5:27b
```

### Backend Connection Failed

```bash
# Check backend logs
tail -f logs/backend.log

# Verify .env configuration
cat .env | grep -E "LLM_PROVIDER|OLLAMA_MODEL|BEDROCK|ANTHROPIC"

# Test LLM connectivity
curl http://localhost:8000/api/llm/status
```

---

## 🧰 Useful Commands

### Status Check
```bash
# All services
./check-status.sh

# Backend only
curl http://localhost:8000/api/health

# LLM status
curl http://localhost:8000/api/llm/status
```

### Logs
```bash
# Backend logs
tail -f logs/backend.log

# Ollama logs (if using Ollama)
tail -f logs/ollama.log

# Frontend logs
tail -f logs/frontend.log
```

### Testing
```bash
# Run unit tests
cd backend
source .venv/bin/activate
pytest tests/test_ten_step_paths.py -v

# Run integration tests (requires server running)
pytest tests/test_long_paths_integration.py -v
```

---

## 📚 Documentation

- **Implementation Report**: `backend/TEN_STEP_PATH_IMPLEMENTATION_REPORT.md`
- **Shell Scripts Update**: `SHELL_SCRIPTS_UPDATE_SUMMARY.md`
- **Project README**: `README.md`
- **API Documentation**: http://localhost:8000/docs

---

## 🎓 Workflow Examples

### Example 1: Quick Infrastructure Test

```bash
# 1. Start services
./start-all-tmux.sh

# 2. Wait ~30 seconds for backend to initialize

# 3. Test with sample
curl -X POST http://localhost:8000/api/swarm/run/quick \
  -F "file=@samples/capital-one-breach-replica.tf" \
  | jq '.final_paths[0].steps | length'

# 4. View results in browser
open http://localhost:5173
```

### Example 2: Single Agent Deep Dive

```bash
# Using apt29_cozy_bear for nation-state analysis
curl -X POST "http://localhost:8000/api/swarm/run/single?agent_name=apt29_cozy_bear" \
  -F "file=@samples/scarleteel-breach-replica.tf"
```

### Example 3: Production Analysis

```bash
# Full pipeline with all agents
curl -X POST http://localhost:8000/api/swarm/run \
  -F "file=@your-infrastructure.tf" \
  -F "model=qwen3.5:27b"  # Optional: override default model
```

---

## ⚡ Performance Tips

### Fast Development Cycle
- Use **Quick mode** (`/api/swarm/run/quick`) for iteration
- ~14 minutes vs 25-30 for full pipeline
- 2 agents provide good coverage for testing

### Production Runs
- Use **Full mode** (`/api/swarm/run`) for comprehensive analysis
- Run during off-hours (25-30 min execution time)
- Consider using faster models for evaluation (gemma4:e4b ~20% faster)

### Model Selection
- **qwen3.5:27b**: Best quality, longer runtime
- **qwen3:14b**: Good balance
- **gemma4:e4b**: Faster (~20%), slightly lower quality

---

## 🔐 Security Notes

1. **Never commit `.env` file** — Contains API keys and tokens
2. **Rotate credentials regularly** — Especially for cloud providers
3. **Use least-privilege AWS credentials** — Bedrock access only
4. **Monitor API usage** — Anthropic/Bedrock have usage costs
5. **Review attack paths before sharing** — May contain infrastructure details

---

## 📞 Support

- **Issues**: https://github.com/redcountryroad/swarm-tm/issues
- **Documentation**: See `README.md` and `CLAUDE.md`
- **Logs**: Check `logs/` directory for debugging

---

**Last Updated**: 2026-04-21  
**Compatible With**: Swarm TM v2.0+
