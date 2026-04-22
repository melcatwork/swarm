# Shell Scripts Update Summary

**Date**: 2026-04-21  
**Updated Files**: `start-all.sh`, `stop-all.sh`, `start-all-tmux.sh`

---

## Overview of Changes

All three shell scripts have been updated to:
1. **Support multiple LLM providers** (Ollama, AWS Bedrock, Anthropic API)
2. **Reflect current project state** (10-step attack paths, new features)
3. **Provide accurate status information** based on `.env` configuration
4. **Update test commands** to reference new samples and capabilities

---

## 1. start-all.sh Updates

### Multi-Provider Support

**Before**:
- Hardcoded to check for `qwen3:14b` model only
- Always attempted to start Ollama regardless of configuration

**After**:
- Reads `LLM_PROVIDER` from `.env` file
- Supports three providers:
  - **ollama**: Starts local Ollama server, pulls configured model
  - **bedrock**: Shows Bedrock model, reminds about AWS credentials
  - **anthropic**: Validates API key in `.env`
- Only starts Ollama if `LLM_PROVIDER=ollama`

### Dynamic Model Detection

```bash
# NEW: Reads actual configured model
OLLAMA_MODEL=$(grep "^OLLAMA_MODEL=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
echo -n "  Checking for $OLLAMA_MODEL model... "

# OLD: Hardcoded qwen3:14b
echo -n "  Checking for qwen3:14b model... "
```

### Updated Quick Start Information

**New sections added**:
- Four run modes clearly documented:
  - `/api/swarm/run` — Full pipeline (25-30 min)
  - `/api/swarm/run/quick` — Quick test (14 min)
  - `/api/swarm/run/single` — Single agent
  - `/api/swarm/run/stigmergic` — Stigmergic swarm

- Recent updates section:
  ```
  Recent Updates (2026-04-21):
    ✓ Attack paths now support up to 10 steps (was 3-5)
    ✓ All four run types updated
    ✓ Test suite: pytest tests/test_ten_step_paths.py
  ```

- Updated test commands to use new samples:
  - `capital-one-breach-replica.tf`
  - `scarleteel-breach-replica.tf`
  - `llmjacking-breach-replica.tf`

- New API endpoint showcased:
  ```bash
  # Check available LLM models
  curl http://localhost:8000/api/llm/models
  ```

### Conditional Log Display

```bash
# Only show Ollama logs if using Ollama provider
if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo -e "  Ollama:   $LOG_DIR/ollama.log"
fi
```

---

## 2. start-all-tmux.sh Updates

### LLM Provider Pane (Pane 0)

**Before**:
- Always labeled "OLLAMA"
- Always attempted to start Ollama server

**After**:
- **Ollama mode**: Starts Ollama server, shows model list
- **Bedrock/Anthropic mode**: Shows provider status, notes no local server needed
- Pane label changes based on provider:
  - `=== OLLAMA (Local LLM) ===` for Ollama
  - `=== LLM PROVIDER STATUS ===` for Bedrock/Anthropic

### Updated Quick Commands Panel

**Changes**:
- Added model listing command
- Updated sample file references
- Added four run modes documentation
- Included recent updates (10-step support)
- Simplified test commands

**Example**:
```bash
Quick Test Commands:
  # Check backend health
  curl http://localhost:8000/api/health

  # Check available models
  curl http://localhost:8000/api/llm/models

  # Quick test (14 min, 2 agents)
  curl -X POST http://localhost:8000/api/swarm/run/quick \
    -F "file=@samples/capital-one-breach-replica.tf"
```

---

## 3. stop-all.sh Updates

### Provider-Aware Status Checking

**New**:
- Reads `LLM_PROVIDER` from `.env`
- Shows configured provider at startup
- Conditionally checks Ollama based on provider

```bash
# Check LLM provider for more accurate status
if [ -f ".env" ]; then
    LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2 2>/dev/null)
else
    LLM_PROVIDER="unknown"
fi

echo -e "${YELLOW}LLM Provider:${NC} ${BLUE}$LLM_PROVIDER${NC}"
```

### Conditional Ollama Handling

**Before**:
- Always checked for Ollama process
- Always showed Ollama status

**After**:
```bash
if [ "$LLM_PROVIDER" = "ollama" ]; then
    # Check and warn about Ollama
elif [ "$LLM_PROVIDER" = "bedrock" ] || [ "$LLM_PROVIDER" = "anthropic" ]; then
    echo -e "${BLUE}No local LLM server to stop (using $LLM_PROVIDER)${NC}"
fi
```

### Enhanced Status Display

**New verification output**:
```
Verifying services stopped:
  Frontend:  ✓ Stopped
  Backend:   ✓ Stopped
  LLM:       Using bedrock (no local server)  # If not Ollama

  # OR

  Frontend:  ✓ Stopped
  Backend:   ✓ Stopped
  Ollama:    Running (not stopped, may be used by other projects)
```

### Added Quick Status Commands

```bash
Quick Status Check:
  lsof -i :5173         # Check frontend
  lsof -i :8000         # Check backend
  lsof -i :11434        # Check Ollama (only if using Ollama)
```

---

## Configuration Detection Logic

All three scripts now use this pattern:

```bash
# Read provider from .env
LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2)

case "$LLM_PROVIDER" in
    "ollama")
        # Ollama-specific logic
        ;;
    "bedrock")
        # Bedrock-specific logic
        ;;
    "anthropic")
        # Anthropic-specific logic
        ;;
    *)
        # Unknown provider handling
        ;;
esac
```

---

## Sample Test Files Referenced

Updated to use production-quality breach replicas:

| File | Description | Complexity |
|------|-------------|------------|
| `capital-one-breach-replica.tf` | Capital One 2019 breach scenario | 7-8 step paths |
| `scarleteel-breach-replica.tf` | Scarleteel campaign (AWS cryptomining) | 8-9 step paths |
| `llmjacking-breach-replica.tf` | LLM infrastructure compromise | 6-7 step paths |

---

## Backward Compatibility

### ✅ Maintained

- Scripts still work with Ollama (default provider)
- Existing `.env` files remain valid
- No breaking changes to workflow
- Graceful fallback if provider not specified

### ⚠️ Recommendations

1. **Update .env**: Explicitly set `LLM_PROVIDER` even if using Ollama
   ```bash
   LLM_PROVIDER=ollama  # Make it explicit
   ```

2. **Use new samples**: Old samples still work, but new ones have better coverage
   ```bash
   # Recommended
   samples/capital-one-breach-replica.tf
   samples/scarleteel-breach-replica.tf
   
   # Still works
   samples/file-transfer-system.tf
   ```

3. **Test with new capabilities**:
   ```bash
   # After starting services
   curl http://localhost:8000/api/llm/models
   ```

---

## Usage Examples

### Scenario 1: Using Ollama (Default)

```bash
# .env configuration
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3.5:27b

# Start services
./start-all-tmux.sh

# Result:
# - Ollama server started in pane 0
# - Model qwen3.5:27b checked/pulled
# - Backend and frontend started
```

### Scenario 2: Using AWS Bedrock

```bash
# .env configuration
LLM_PROVIDER=bedrock
BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
AWS_BEARER_TOKEN_BEDROCK=your_token_here

# Start services
./start-all.sh

# Result:
# - No Ollama server started
# - Pane 0 shows Bedrock status
# - Backend connects to Bedrock
# - Frontend ready for analysis
```

### Scenario 3: Using Anthropic API

```bash
# .env configuration
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-...

# Start services
./start-all.sh

# Result:
# - No local LLM server
# - API key validated
# - Backend uses Anthropic API
```

---

## Testing the Updates

### 1. Test Provider Detection

```bash
# Check what scripts will detect
grep "^LLM_PROVIDER=" .env

# Expected: ollama, bedrock, or anthropic
```

### 2. Test Start Script

```bash
# Standard mode
./start-all.sh

# Tmux mode (recommended)
./start-all-tmux.sh

# Watch for:
# - Correct provider identified
# - Appropriate services started
# - Correct status messages
```

### 3. Test Stop Script

```bash
./stop-all.sh

# Verify:
# - All services stopped
# - Correct provider shown
# - Appropriate status for LLM server
```

### 4. Test Quick Commands

```bash
# After services start
curl http://localhost:8000/api/health
curl http://localhost:8000/api/llm/models

# Submit a test
curl -X POST http://localhost:8000/api/swarm/run/quick \
  -F "file=@samples/capital-one-breach-replica.tf"
```

---

## New Features Highlighted in Scripts

### 1. 10-Step Attack Paths

Scripts now mention:
```
Recent Updates (2026-04-21):
  ✓ Attack paths now support up to 10 steps (was 3-5)
  ✓ All four run types updated
  ✓ Test suite: pytest tests/test_ten_step_paths.py
```

### 2. Model Selection API

New endpoint showcased:
```bash
# Check available LLM models
curl http://localhost:8000/api/llm/models
```

### 3. Four Run Modes

Clearly documented in status output:
- Full pipeline (all agents, 25-30 min)
- Quick test (2 agents, 14 min)
- Single agent (specify agent name)
- Stigmergic swarm (sequential, emergent)

### 4. Production Samples

Better test files recommended:
- capital-one-breach-replica.tf
- scarleteel-breach-replica.tf
- llmjacking-breach-replica.tf

---

## File Summary

| File | Lines Changed | Key Updates |
|------|---------------|-------------|
| `start-all.sh` | ~80 lines | Multi-provider support, dynamic model detection, updated docs |
| `start-all-tmux.sh` | ~40 lines | Provider-aware pane 0, updated quick commands |
| `stop-all.sh` | ~30 lines | Provider-aware status, conditional Ollama checks |

**Total Impact**: 150+ lines updated across 3 files

---

## Migration Notes

### If Upgrading from Old Scripts

**No migration needed** — scripts are backward compatible.

**Optional improvements**:

1. Add explicit `LLM_PROVIDER=ollama` to `.env` if using Ollama
2. Test new sample files for better attack path coverage
3. Try tmux mode: `./start-all-tmux.sh` for better monitoring

### If Switching Providers

Example: Ollama → Bedrock

```bash
# 1. Update .env
LLM_PROVIDER=bedrock
BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
AWS_BEARER_TOKEN_BEDROCK=your_token_here

# 2. Stop existing services
./stop-all.sh

# 3. Start with new provider
./start-all.sh

# 4. Verify
curl http://localhost:8000/api/llm/status
```

---

## Troubleshooting

### Issue: Script shows "Unknown LLM_PROVIDER"

**Cause**: `.env` has invalid or missing `LLM_PROVIDER` setting

**Fix**:
```bash
# Check .env
grep LLM_PROVIDER .env

# Should be one of: ollama, bedrock, anthropic
# Update if needed
```

### Issue: Ollama pane shows error in Bedrock mode

**Expected Behavior**: If using Bedrock/Anthropic, pane 0 shows status message instead of starting Ollama

**Not an Error**: Working as designed

### Issue: Model check fails

**For Ollama**:
```bash
# Verify model exists
ollama list | grep your-model

# Pull if missing
ollama pull your-model
```

**For Bedrock/Anthropic**:
- No local check needed
- Backend will validate on first API call

---

## Conclusion

All three shell scripts are now:
- ✅ **Multi-provider aware** (Ollama, Bedrock, Anthropic)
- ✅ **Up-to-date** with 10-step path support
- ✅ **Better documented** with clear command examples
- ✅ **More intelligent** with conditional logic
- ✅ **Backward compatible** with existing setups

**Recommended Next Steps**:
1. Test scripts with your current provider
2. Try tmux mode: `./start-all-tmux.sh`
3. Run new test suite: `pytest tests/test_ten_step_paths.py`
4. Test with production samples (capital-one, scarleteel)

---

**Updated By**: Claude Code  
**Date**: 2026-04-21  
**Status**: Complete and tested
