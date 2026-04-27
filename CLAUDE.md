# Swarm Threat Modeling Engine

AI-powered threat modeling platform using CrewAI multi-agent swarm intelligence for AWS infrastructure (Terraform/CloudFormation).

**Repository**: https://github.com/redcountryroad/swarm-tm (private)  
**Status**: Production Ready ✅

## Project Structure

**Monorepo**: `backend/` (Python 3.11+, FastAPI, CrewAI) + `frontend/` (React 18, Vite)

**Key paths**:
- `backend/app/swarm/` — CrewAI crews, agent personas (YAML), orchestration
- `backend/app/parsers/` — Terraform/CloudFormation → normalized asset graph
- `backend/app/routers/` — FastAPI endpoints
- `backend/app/threat_intel/` — modular feed adapters (13 sources)
- `backend/data/` — SQLite, ATT&CK STIX cache, persona YAML
- `frontend/src/pages/` — ThreatModelPage, ThreatIntelPage
- `frontend/src/components/` — ResultsView, attack path cards, CVE evidence strips
- `frontend/src/api/` — axios client

## Threat Modeling Pipelines

4 pipeline modes (all support dynamic model selection):

1. **Full Swarm** `POST /api/swarm/run` — All personas, 5 evaluators, 3 adversarial agents (~25-30 min)
2. **Quick Run** `POST /api/swarm/run/quick` — 2 agents, fast eval (~14 min)
3. **Single Agent** `POST /api/swarm/run/single?agent_name=X` — One persona (~10-15 min)
4. **Stigmergic Swarm** `POST /api/swarm/run/stigmergic` — Shared graph coordination with emergent insights

All endpoints accept optional `model` form parameter.

## LLM Configuration

**Providers** (`.env` → `LLM_PROVIDER`):
- `ollama` — local (requires `ollama serve`)
- `bedrock` — AWS Bedrock (uses `AWS_BEARER_TOKEN_BEDROCK`)
- `anthropic` — Anthropic API (uses `ANTHROPIC_API_KEY`)

**Dynamic Model Selection**:
- **Ollama**: ALL models from `ollama list` auto-discovered via `/api/tags`
- **Bedrock/Anthropic**: Defined in `.env`
- **WIP models**: Commented models (e.g., `#OLLAMA_MODEL=qwen3:14b`) appear but are disabled
- **Only uncommented models** can be used

**CRITICAL**: Always use `get_llm()` helper in `backend/app/swarm/crews.py`. Never hardcode model names or providers in agent definitions.

## Commands

```bash
# Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev  # :5173

# Health checks
curl http://localhost:8000/api/health
curl http://localhost:8000/api/llm/models
```

## Code Style

- **Python**: Type hints on all functions, Pydantic models for data, `logging` module (never `print()`)
- **React**: Functional components with hooks, destructured imports
- **API**: All responses return JSON with `status` field

## Security Rules — NEVER VIOLATE

1. **No secrets in code** — API keys/tokens/passwords in `.env` only (in `.gitignore`)
2. **No secret logging** — Sanitize credentials/ARNs before logging
3. **Validate uploads** — Max 1MB, only `.tf`/`.yaml`/`.yml`/`.json`, validate structure
4. **No `eval()`/`exec()`** on user input — Use python-hcl2/PyYAML safe_load only
5. **No shell commands from user input** — CrewAI agents must not have Code Interpreter enabled
6. **Pin dependencies** — Specific versions in requirements.txt, check CVEs
7. **Sanitize LLM output** — Validate agent JSON against Pydantic models before frontend
8. **CORS restricted** — `http://localhost:5173` (dev), production via `ALLOWED_ORIGINS` env
9. **No wildcard IAM** — Agents must recommend least-privilege, never `*` policies

## Architecture Decisions — DO NOT CHANGE

- **CrewAI orchestration** — 3-layer swarm (exploration → evaluation → adversarial). Do not replace.
- **Modular threat intel** — Adapter pattern in `threat_intel/adapters/`. Add sources via new adapter + `config/sources.yaml` entry.
- **Persona registry** — Default personas are `protected: true` (disable only, no delete). Custom personas are `protected: false`.
- **Kill chain format** — All attack paths: 3-5 steps with ATT&CK IDs + inline mitigations. Schema in `swarm/models.py`.
- **Cloud-agnostic parser** — Normalizes to common schema (`parsers/models.py`). Swarm never sees raw IaC.
- **Arbitrator fallback** — If arbitrator returns empty `final_paths`, fallback to scored paths with metadata (prevents data loss). See `crews.py:1246-1255`.

## Task Workflow

1. **Plan first** — Outline changes before coding
2. **Minimal changes** — Touch only what's necessary
3. **Test** — `python -m pytest tests/ -v` after changes
4. **Verify** — API health + frontend render
5. **Document** — Create test report if feature/fix affects pipeline
6. **Update CLAUDE.md** — Add to relevant section if architectural change

### Adding Features (Pipeline)

1. Backend: Update `app/routers/swarm.py` and/or `app/swarm/crews.py`
2. Frontend: Update `frontend/src/api/client.js` + page components
3. Test with `samples/clouddocs-saas-app.tf`
4. Verify attack path structure (technique_id, target_asset, mitigations)
5. Check backend logs
6. Create test report in `backend/`
7. Update OpenAPI schema (`/openapi.json`)

### Fixing Bugs

1. Document root cause + solution
2. List affected files with line numbers
3. Test scenario that previously failed
4. Create fix doc: `backend/<FIX_NAME>.md`

## Critical Patterns (LLM Output Handling)

- **Markdown-wrapped JSON**: Strip ```json ... ``` fences before parsing
- **Strict JSON prompts**: Add "Return ONLY valid JSON" in task `expected_output`
- **Key name variations**: Arbitrator may return `path_name` or `name` — try both: `final_path.get("path_name") or final_path.get("name", "")`
- **Empty arbitrator output**: Fallback to scored paths when `len(enriched_final_paths) == 0`
- **Model variability**: Different models use different keys (e.g., `"technique"` vs `"technique_name"`). Use fallback key lookup.
- **FastAPI Form**: Must import `Form` from `fastapi` for multipart params: `param: str = Form(None)`

## Known Limitations

1. Long execution times (14-30 min) — inherent to LLM multi-agent systems
2. LLM output variability — fallback mechanism mitigates but can't prevent all issues
3. Ollama-only dynamic discovery — Bedrock/Anthropic models need `.env` definition
4. No streaming progress — blocking API calls until completion
5. Single IaC file per run — no multi-file analysis support
6. AWS-focused mitigations — GCP/Azure equivalents not implemented

## Key Documentation

- `@backend/app/swarm/agents/personas.yaml` — 13 agent persona definitions
- `@backend/app/threat_intel/config/sources.yaml` — threat intel feed configs
- `@backend/requirements.txt` — pinned dependencies
- `@.env.example` — all environment variables
- `@samples/README.md` — test IaC files
- `@backend/*_REPORT.md` — implementation/verification docs

## Troubleshooting Quick Reference

**Backend won't start**: `lsof -ti :8000 | xargs kill -9` then restart  
**Model not working**: Check `ollama serve` running + model exists in `ollama list`  
**Attack paths missing data**: Check logs for "Using scored paths as fallback" (expected)  
**Timeout errors**: 10-30 min requests are normal for LLM pipelines
