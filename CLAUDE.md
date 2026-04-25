# Swarm Threat Modeling Engine (swarm-tm)

AI-powered threat modeling platform using CrewAI multi-agent swarm intelligence against AWS infrastructure defined in Terraform or CloudFormation.

**Repository**: https://github.com/redcountryroad/swarm-tm (private)
**Status**: Production Ready ✅
**Last Updated**: 2026-04-25

## Recent Changes (2026-04-25)

### ✅ Vulnerability Intelligence UI Components
- **Added comprehensive CVE evidence display in attack path steps**
- **Added persona intelligence status panel showing patch currency**
- **Added vulnerability aggregation summary across all paths**
- Surfaces all vulnerability intelligence from Living Intelligence System
- **Frontend changes**:
  - `frontend/src/components/CveEvidenceStrip.jsx` — CVE evidence display with CVSS, EPSS, KEV flag, exploit references (NEW FILE)
  - `frontend/src/components/PersonaStatusPanel.jsx` — Collapsible panel showing patch count, last sync date, sources for all 13 personas (NEW FILE)
  - `frontend/src/components/VulnIntelSummary.jsx` — Aggregate summary showing unique CVEs, KEV count, PoC count, CVSS critical, peak EPSS (NEW FILE)
  - `frontend/src/components/EolWarningBadge.jsx` — Amber warning badge for EOL runtimes (NEW FILE)
  - `frontend/src/components/CsaPathCard.jsx` — Integrated CveEvidenceStrip below each step description (lines 11, 206)
  - `frontend/src/pages/ThreatModelPage.jsx` — Added PersonaStatusPanel above upload form, VulnIntelSummary above attack paths (lines 12-13, 1118, 1489)
- **Backend changes**:
  - `backend/app/routers/swarm.py` — Added GET /api/swarm/persona-status endpoint (line 291)
  - Uses `get_patch_summary()` from persona_loader to return patch statistics
- **CVE Evidence Strip Features**:
  - Only renders when step contains cve_id field
  - Shows CVE ID, CVSS score (color-coded), EPSS percentage with bar
  - KEV (Known Exploited Vulnerability) badge for CISA-listed CVEs
  - Exploit priority label (CRITICAL/HIGH/MEDIUM-HIGH/MEDIUM)
  - Clickable references: ExploitDB, Nuclei templates, GitHub Security Advisories
  - Color-coded background and border based on priority level
- **Persona Status Panel Features**:
  - Collapsible header showing total patches applied across all personas
  - Expandable table with 13 rows (one per persona)
  - Status dot: green (≤7 days), amber (≤30 days), red (>30 days) since last update
  - Shows patch count, sources (comma-separated), last updated date
  - Fetches from /api/swarm/persona-status on mount
- **Vuln Intel Summary Features**:
  - 5 stat boxes: Unique CVEs, KEV Listed, PoC Confirmed, CVSS Critical, Peak EPSS
  - Only renders if at least one step contains cve_id
  - Color-coded stat values (red for high severity, amber for medium, green for low)
  - Positioned between CSA Risk Summary and Attack Paths heading
- **Benefits**:
  - ✅ Real-time visibility of vulnerability intelligence driving attack paths
  - ✅ Users can see CVE evidence supporting each step without leaving UI
  - ✅ Persona intelligence currency visible before running scans
  - ✅ Aggregate metrics provide instant severity assessment
  - ✅ Clickable exploit references enable immediate verification
  - ✅ Graceful degradation: components only render when data available
- **Integration Points**:
  - Works with all 4 run types (Full Swarm, Quick Run, Single Agent, Stigmergic Swarm)
  - Backward compatible: no breaking changes to existing components
  - ImpactSelector and pipeline visualization unchanged
  - All new components use existing CSS variables for theming
- See implementation verification in conversation history

## Recent Changes (2026-04-23)

### ✅ Threat Model Summary Component
- **Added high-level summary section for all 4 run types**
- Appears between "Upload Infrastructure-as-Code" and "Infrastructure Asset Graph"
- Displays comprehensive overview at a glance:
  - Total number of discovered attack paths
  - Primary & alternate attack paths count with highest risk band
  - Overall highest risk level across all paths
  - Attack surface coverage percentage (for stigmergic swarm)
  - Risk distribution for primary/alternate paths (vulnerability-grounded)
  - Risk distribution for all attack paths
  - Data classification impact configuration
- **Frontend changes**:
  - `frontend/src/components/ThreatModelSummary.jsx` — New summary component with responsive grid layout (NEW FILE)
  - `frontend/src/pages/ThreatModelPage.jsx` — Added ThreatModelSummary import and rendering (lines 1275-1278)
- **Visual design**:
  - Purple gradient background with 2px border
  - 4-stat responsive grid (Total Paths, Primary/Alternate, Overall Risk, Coverage)
  - Color-coded stat cards based on risk bands
  - Two risk distribution sections with pill-style badges
  - Impact configuration banner at bottom
- **Benefits**:
  - ✅ Instant visibility of critical metrics without scrolling
  - ✅ Focused priority on CVE-based vulnerability paths
  - ✅ Visual hierarchy draws attention to high-risk areas
  - ✅ Coverage validation for stigmergic swarm runs
  - ✅ Context before diving into detailed attack paths
- **Data filtering**:
  - Primary & alternate paths: `source === 'confirmed_vuln_synthesis'`
  - Agent exploration paths: `source !== 'confirmed_vuln_synthesis'`
  - Risk calculations based on CSA CII 5×5 risk matrix
- See: `THREAT_MODEL_SUMMARY_COMPONENT.md`

### ✅ Mitigation Action Toolbar - Single Location
- **Consolidated to single toolbar between Attack Paths and Comprehensive Mitigation Summary**
- Removed redundant toolbar from bottom of MitigationSummary component
- Provides action opportunity after reviewing attack path cards
- 3-button design: Clear Selections, Apply All Mitigations & Analyze, Apply Mitigations & Analyze
- Purple gradient background (#667eea → #764ba2)
- Simplified MitigationSummary to display-only component (removed 5 unused props, 121 lines)
- See: `MITIGATION_TOOLBAR_REMOVAL.md`

### ✅ Completeness-Based Mitigation Reduction Logic
- **Implemented granular mitigation effectiveness based on selection completeness**
- System now differentiates between full and partial mitigation selection
- Selecting ALL preventive mitigations results in lower residual likelihood than selecting SOME
- **Backend changes**:
  - `backend/app/swarm/mitigations.py` — Updated `analyze_post_mitigation_impact()` to calculate per-step completeness ratios
  - `backend/app/swarm/mitigations.py` — Enhanced `_evaluate_mitigation_effectiveness()` to scale reduction by completeness (15%-100% for HIGH, 6%-50% for MEDIUM techniques)
  - Added `selected_count` and `total_recommended` parameters to effectiveness evaluator
  - Changed path-level reduction from binary blocked/reduced to average of step reduction percentages
- **Completeness scaling**:
  - **HIGH effectiveness techniques** (T1552.005, T1078, T1530, etc.): 100% completeness → 100% reduction (blocked), 67% completeness → 70% reduction (reduced), 33% completeness → 30% reduction (minimally reduced)
  - **MEDIUM effectiveness techniques** (T1098, T1486, T1496, etc.): 100% completeness → 50% reduction, 50% completeness → 20% reduction
  - **GENERIC techniques**: 100% completeness → 25% reduction, scale down to 3% for partial selection
- **Path-level calculation**: Average of all step reductions → ensures full mitigation selection produces lower residual likelihood than partial
- **Example impact**:
  - All mitigations (100% complete): 4 steps → 95% avg reduction → Likelihood 4 → 1, Risk 20 → 5 (75% reduction)
  - Half mitigations (50% complete): 4 steps → 57% avg reduction → Likelihood 4 → 2, Risk 20 → 10 (50% reduction)
  - Minimal mitigations (20% complete): 4 steps → 20% avg reduction → Likelihood 4 → 3, Risk 20 → 15 (25% reduction)
- **Benefits**:
  - ✅ Incentivizes complete mitigation implementation
  - ✅ Realistic risk modeling: partial mitigation = partial protection
  - ✅ Granular control over risk reduction
  - ✅ Transparent completeness display in reasoning field
- **Applies to**: All 4 run types (Full Swarm, Quick Run, Single Agent, Stigmergic Swarm)
- See: `COMPLETENESS_BASED_MITIGATION_LOGIC.md`

## Recent Changes (2026-04-15)

### ✅ React Flow Migration for Shared Attack Graph
- **Complete rewrite of SharedAttackGraph component** using React Flow library instead of raw SVG/D3
- Fixed critical rendering issues: swim lane misalignment on zoom/pan, invisible arrows, broken animations
- **Frontend changes**:
  - `frontend/src/components/SharedAttackGraph.jsx` — Completely rebuilt with React Flow (NEW IMPLEMENTATION)
  - `frontend/package.json` — Added reactflow@11.11.4 dependency
  - `frontend/src/components/StigmergicResultsView.jsx` — Replaced inline SVG graph with SharedAttackGraph component import
- **Key architectural changes**:
  - **Swim lanes as React Flow nodes**: Lane backgrounds and labels now render as custom `LaneNode` components inside the React Flow canvas, ensuring they move and scale correctly with zoom/pan
  - **Custom node types**: `AttackNode` (technique circles) and `LaneNode` (swim lane backgrounds) defined at module level for stable references
  - **Proper edge rendering**: Fixed arrow markers using `MarkerType.ArrowClosed` with validated color strings, changed edge type from 'smoothstep' to 'default' (bezier) for better cross-lane routing
  - **Handle positioning**: Changed from Top/Bottom to Left/Right positioning for cleaner horizontal edge routing between vertically-stacked swim lanes
  - **Valid edge filtering**: Added `validNodeIds` check to filter out edges referencing non-existent nodes before rendering
- **Layout algorithm**:
  - Horizontal swim lane layout with 5 kill chain phases (Initial Access, Execution, Lateral Movement, Objective, Covering Tracks)
  - Nodes positioned by incoming edge count (more central nodes positioned left)
  - Vertical staggering for dense lanes to reduce overlap
  - Lane dimensions: 1600px width × 200px height per lane
- **Features preserved**:
  - Path traversal animation: Click any node to trace all attack paths through it with hop-by-hop animated reveal (500ms intervals)
  - Node dimming: Off-path nodes fade to 12% opacity, path nodes stay at 100% opacity with highlight rings
  - Edge animation: Edges with 2+ reinforcements show React Flow's built-in flowing dash animation
  - Interactive controls: Zoom, pan, minimap, fit view, drag nodes
  - Legend, info bar, coverage gaps sections unchanged
- **Debug logging**: Added `[SAG]` console logs for troubleshooting edge rendering (nodes count, edges count, sample edge structure, valid node IDs)
- **Benefits**:
  - ✅ Swim lanes now move and scale correctly with zoom/pan (no misalignment)
  - ✅ Arrows visible with proper markers at target end
  - ✅ Robust rendering using battle-tested React Flow library
  - ✅ Better performance for large graphs
  - ✅ Built-in controls (zoom, pan, minimap) with no custom implementation needed

### ✅ Stigmergic Multi-Agent Swarm Implementation
- Added fourth pipeline mode: **Stigmergic Swarm** with shared graph coordination
- Agents build on each other's discoveries through reinforced technique nodes
- Sequential execution with configurable ordering strategies (capability ascending/descending, random)
- **Backend changes**:
  - `backend/app/swarm/shared_graph.py` — New SharedThreatGraph class for agent coordination (NEW FILE)
  - `backend/app/swarm/swarm_exploration.py` — Stigmergic exploration orchestration logic (NEW FILE)
  - `backend/app/routers/swarm.py` — Added POST /api/swarm/run/stigmergic endpoint with execution_order parameter
- **Frontend changes**:
  - `frontend/src/components/StigmergicResultsView.jsx` — New component for displaying stigmergic results with shared graph visualization (NEW FILE)
  - `frontend/src/components/StigmergicResultsView.css` — Styling for stigmergic results view (NEW FILE)
  - `frontend/src/api/client.js` — Added uploadAndRunStigmergic() function
  - `frontend/src/pages/ThreatModelPage.jsx` — Added execution order selector, stigmergic run button, result normalization
  - `frontend/src/pages/ThreatModelPage.css` — Added styling for execution order dropdown
- **Features**:
  - Emergent insights from cross-agent pattern detection
  - Reinforced technique nodes show high-confidence attack vectors validated by multiple agents
  - Execution order strategies: capability-based (ASC/DESC) or random
  - Coverage percentage calculation for attack surface exploration
  - Backward compatible with existing pipeline modes
- See: `frontend/STIGMERGIC_RESULTS_INTEGRATION.md`

### ✅ Threat Intelligence Enhancements
- **Expanded sources from 3 to 13**: Added 10 new security news RSS feeds
- **Normalized citation scoring**: All scores now on 0-10 scale using min-max normalization
- **Added scoring documentation**: New "News Score Definition" section in UI explaining score calculation
- **Backend changes**:
  - `backend/app/threat_intel/config/sources.yaml` — Added News4Hackers, SecurityWeek, Dark Reading, Krebs on Security, BleepingComputer, Cybersecurity News, CSO Online, Threatpost, Ars Technica Security, Simon Willison
  - `backend/app/threat_intel/core/scorer.py` — Implemented min-max normalization to 0-10 scale
  - `backend/app/threat_intel/adapters/hackernews_rss.py` — Fixed source name to use dynamic self.get_name() instead of hardcoded "The Hacker News"
- **Frontend changes**:
  - `frontend/src/pages/ThreatIntelPage.jsx` — Added "News Score Definition" section with formula and scoring components
  - `frontend/src/pages/ThreatIntelPage.css` — Added styling for score definition section with monospace formula display
- **Features**:
  - 13 total threat intel sources (1 CVE database, 11 security news feeds, 1 threat framework)
  - Citation scores normalized: highest item = 10.0, lowest = 0.0, proportional scaling for others
  - Clear documentation of scoring formula: (Base × Severity × Recency) + Cross-Source Bonus
  - All new sources enabled by default with 30-minute refresh intervals

### ✅ UI/UX Improvements
- **Removed AWS Bedrock credentials configuration UI**: Simplified frontend by removing Bedrock config form from threat modeling page
- **Renamed stigmergic header**: Changed "Phase 10: Stigmergic Swarm Exploration Results" to "Multi-agents Swarm Exploration Results" for clarity
- **Frontend changes**:
  - `frontend/src/pages/ThreatModelPage.jsx` — Removed Bedrock state variables, handler function, and configuration form section
  - `frontend/src/components/StigmergicResultsView.jsx` — Updated header title to "Multi-agents Swarm Exploration Results"
- **Impact**:
  - Cleaner UI without credential management complexity
  - More intuitive naming for stigmergic swarm feature
  - Bedrock configuration now handled server-side via .env only

## Recent Changes (2026-04-14)

### ✅ AWS Bedrock Integration with Anthropic Models
- Added support for AWS Bedrock API with AWS Access Key credentials
- Users can now configure AWS credentials via frontend UI
- 5 Anthropic Claude models available through Bedrock:
  - Claude 3.5 Sonnet v2 (most capable)
  - Claude 3.5 Sonnet v1
  - Claude 3 Opus (most powerful)
  - Claude 3 Sonnet (balanced)
  - Claude 3 Haiku (fastest)
- **Backend changes**:
  - `.env` — Added AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY variables
  - `backend/app/config.py` — Added `get_bedrock_anthropic_models()`, updated credential validation
  - `backend/app/routers/llm.py` — Added POST /api/llm/bedrock/configure endpoint
  - `backend/app/swarm/crews.py` — Updated LLM initialization to use AWS credentials
- **Frontend changes**:
  - `frontend/src/api/client.js` — Added `configureBedrockCredentials()` function
  - `frontend/src/pages/ThreatModelPage.jsx` — Added collapsible Bedrock configuration form
  - `frontend/src/pages/ThreatModelPage.css` — Added form styling
- **Features**:
  - Collapsible configuration UI with AWS Access Key ID, Secret Key, and Region selection
  - Credentials persisted to .env file for reuse
  - Automatic model list refresh after configuration
  - Toast notifications for success/failure
  - Backward compatible with bearer token authentication
- See: `AWS_BEDROCK_INTEGRATION.md`

### ✅ Cancel Run Feature
- Added stop button to cancel running threat modeling operations
- Implemented frontend-backend synchronization for graceful cancellation
- Stop button appears on UI when any threat model run is in progress
- Backend checks for cancellation at phase boundaries (parsing, exploration, evaluation, adversarial)
- **Backend changes**:
  - `backend/app/swarm/job_tracker.py` — Added CANCELLED status, cancel() method, cancellation flag
  - `backend/app/routers/swarm.py` — Added POST /api/swarm/cancel/{job_id} endpoint, cancellation checks in pipeline
- **Frontend changes**:
  - `frontend/src/api/client.js` — Added cancelRun() function, cancel token support in upload functions
  - `frontend/src/pages/ThreatModelPage.jsx` — Added handleCancelRun(), stop button with StopCircle icon
  - `frontend/src/pages/ThreatModelPage.css` — Added btn-danger styling for stop button
- **Features**:
  - Graceful cancellation without errors or orphaned processes
  - Immediate HTTP request abortion via axios cancel tokens
  - Toast notification confirming cancellation
  - Job tracker maintains cancelled job history
  - Clean UI state reset after cancellation
- See: `CANCEL_RUN_FEATURE.md`

### ✅ GMT+8 Timezone Implementation
- Standardized all timestamps across frontend and backend to use GMT+8 timezone
- Created centralized timezone utility for consistent datetime handling
- All archived runs, job tracking, and UI displays now show GMT+8 time
- Timestamps explicitly labeled with "GMT+8" in frontend for clarity
- **Backend changes**:
  - New utility module: `backend/app/utils/timezone.py` with GMT+8 helper functions
  - `backend/app/services/archive_service.py` — Uses `now_gmt8()` and `now_gmt8_iso()` for all timestamps
  - `backend/app/swarm/job_tracker.py` — Job status timestamps in GMT+8
- **Frontend changes**:
  - `frontend/src/utils/formatters.js` — Added GMT+8 conversion and formatting utilities
  - `frontend/src/pages/ThreatModelPage.jsx` — Display timestamps with "GMT+8" label
- **Format**: ISO 8601 with explicit timezone: `2026-04-14T14:36:54+08:00`
- See: `GMT8_TIMEZONE_UPDATE.md`

### ✅ Long-Running Operation UI Enhancements
- Extended frontend timeout from 30 seconds to 30 minutes to prevent premature errors
- Added prominent elapsed time display (MM:SS format) with gradient background
- Implemented backend keepalive polling (every 10 seconds) with visual health indicators
- Added contextual status messages that update based on elapsed time and pipeline phase
- Visual heartbeat pulse animations show frontend and backend are alive
- Long operation warning appears after 10 minutes with expected duration
- Users now have clear visibility that both systems are responsive during 20-30 minute operations
- **Modified files**:
  - `frontend/src/api/client.js` — Extended axios timeout to 1800000ms (30 minutes)
  - `frontend/src/pages/ThreatModelPage.jsx` — Added heartbeat counter, backend health polling, contextual messages, elapsed time formatting
  - `frontend/src/pages/ThreatModelPage.css` — Added styles for elapsed time display, pulse animations, heartbeat indicators, long operation notice
- See: `LONG_OPERATION_UI_ENHANCEMENTS.md`

### ✅ Work In Progress Model Restriction
- Implemented restriction to prevent use of commented (WIP) models from `.env`
- Only uncommented models can be selected and used for threat modeling
- WIP models appear in dropdown but are disabled with "Work In Progress" label
- Backend validates and rejects WIP model usage with HTTP 400 error
- **How it works**:
  - Uncommented: `OLLAMA_MODEL=qwen3.5:27b` → **CAN USE** ✅
  - Commented: `#OLLAMA_MODEL=qwen3:14b` → **CANNOT USE (WIP)** ❌
- **Modified files**:
  - `backend/app/routers/llm.py` — Added `is_wip` field, `_get_commented_ollama_models()` helper, WIP detection in model list
  - `backend/app/routers/swarm.py` — Added `validate_model_not_wip()` validation in all three pipeline endpoints
  - `frontend/src/pages/ThreatModelPage.jsx` — Disable WIP models in dropdown, add client-side validation
- See: `backend/WIP_MODEL_RESTRICTION.md`

### ✅ Enhanced Dynamic Model Discovery from Local Ollama
- ALL models from local `ollama list` automatically discovered and selectable
- No need to edit `.env` to add new models - just `ollama pull <model>` and it appears in UI
- Model sizes displayed in dropdown for easy reference
- Backend queries Ollama API `/api/tags` to get complete model list dynamically
- Falls back to `.env` configuration if Ollama unreachable
- **Modified files**:
  - `backend/app/routers/llm.py` — Enhanced `get_available_models()` to query Ollama API for ALL local models
  - `CLAUDE.md` — Updated documentation for dynamic discovery behavior

## Recent Changes (2026-04-13)

### ✅ Dynamic Model Selection Implemented
- Users can now select which LLM model to use for threat modeling
- Model dropdown in frontend populated from backend API
- All three pipeline endpoints accept optional `model` parameter
- Model selection propagates through all pipeline layers
- Backend logs show which model is used for each run
- **Modified files**:
  - `backend/app/routers/swarm.py` — Added `Form` import, added `model: str = Form(None)` to all pipeline endpoints, propagated model through layers
  - `frontend/src/api/client.js` — Updated all three upload functions to accept and pass model parameter
  - `frontend/src/pages/ThreatModelPage.jsx` — Pass selectedModel to all pipeline functions
- See: `backend/MODEL_SELECTION_TEST_REPORT.md`

### ✅ Attack Path Data Loss Fix
- Fixed arbitrator key mismatch causing empty attack paths
- Implemented fallback mechanism when arbitrator returns empty results
- Added validation metadata to fallback paths (confidence, notes, challenged flag)
- All attack paths now preserved and displayed correctly
- **Root causes**:
  1. Arbitrator LLM returns `"path_name"` key but merge logic expected `"name"`
  2. Arbitrator sometimes returns valid JSON with empty `final_paths` array
- **Solutions**:
  1. Dual-key lookup: `final_path.get("path_name") or final_path.get("name", "")` (line 1213)
  2. Fallback to scored paths with metadata when arbitrator returns 0 paths (lines 1246-1255)
- **Modified file**: `backend/app/swarm/crews.py`
- **Test verification**: Run on clouddocs-saas-app.tf returned 2 complete attack paths with all required fields
- See: `backend/ATTACK_PATH_DISPLAY_FIX.md`, `backend/FINAL_TEST_VERIFICATION_SUCCESS.md`

### ✅ Comprehensive Testing Completed
- Full API endpoint verification
- TF file processing validation
- Attack path generation with threat actor profiles
- MITRE ATT&CK technique tagging verification
- Target asset identification from IaC files
- All tests passing with 2 complete attack paths
- See: `backend/COMPREHENSIVE_BACKEND_TEST_REPORT.md`

### ✅ Repository Initialized
- Git repository initialized and pushed to GitHub
- `.env` properly excluded via `.gitignore`
- README.md merged and comprehensive version preserved

## Project structure

Monorepo with two apps:
- `backend/` — Python 3.11+, FastAPI, CrewAI agents, threat intel feeds
- `frontend/` — React 18 + Vite SPA dashboard

Key backend directories:
- `backend/app/swarm/` — CrewAI crews, agent personas (YAML), orchestration
- `backend/app/parsers/` — Terraform + CloudFormation → normalised asset graph
- `backend/app/threat_intel/` — modular feed adapters, scorer, feed manager
- `backend/app/routers/` — FastAPI route handlers
- `backend/data/` — SQLite DB, ATT&CK STIX cache, persona YAML

Key frontend directories:
- `frontend/src/pages/` — ThreatIntelPage, ThreatModelPage
- `frontend/src/components/` — ThreatFeedCard, SourceManager, ResultsView (kill chain)
- `frontend/src/api/` — axios client for backend API

## Key Features

### Threat Modeling Pipelines
Three pipeline modes available, each supporting dynamic model selection:

1. **Full Swarm** (`POST /api/swarm/run`)
   - All enabled agent personas (exploration)
   - 5 evaluators (feasibility, impact, detection, novelty, coherence)
   - 3 adversarial agents (red team, blue team, arbitrator)
   - Execution time: ~25-30 minutes
   - Use case: Comprehensive production threat models

2. **Quick Run** (`POST /api/swarm/run/quick`)
   - 2 exploration agents only
   - Faster evaluation layer
   - Simplified adversarial validation
   - Execution time: ~14 minutes
   - Use case: Development, testing, rapid iteration

3. **Single Agent** (`POST /api/swarm/run/single?agent_name=<persona>`)
   - One specific threat actor persona
   - Full evaluation and validation
   - Execution time: ~10-15 minutes
   - Use case: Targeted attack path analysis

All endpoints accept optional `model` form parameter to override default LLM model.

### Performance Characteristics (qwen3:14b on local hardware)

**Quick Run Pipeline** (~14 minutes total):
- IaC Parsing: ~5s (1%)
- Exploration (2 agents): ~230s (28%)
- Evaluation (5 scorers): ~280s (34%)
- Adversarial (3 agents): ~310s (37%)
- Mitigation Mapping: ~3s (<1%)

**Full Swarm Pipeline** (~25-30 minutes):
- More exploration agents run in parallel
- Same evaluation and adversarial phases
- Majority of time spent in LLM inference (expected)

**Model comparison** (relative speed, qwen3:14b = 1.0x):
- `qwen3:14b`: 1.0x (baseline, best quality)
- `gemma4:e4b`: ~0.8x (20% faster)
- `llama3.2:3b`: ~0.5x (50% faster, lower quality)
- `qwen3:4b`: ~0.6x (40% faster)

### Model Selection API
- `GET /api/llm/models` — List all available models with provider, availability, default flag, WIP status, and size info
- `GET /api/llm/status` — Current LLM provider and model configuration
- **Ollama models**: Automatically discovered from local Ollama installation via `/api/tags` endpoint
- **Bedrock/Anthropic models**: Defined in `.env` configuration
- **WIP models**: Models marked as Work In Progress (commented in `.env`) are discovered but disabled for use

### Attack Path Features
- **MITRE ATT&CK technique tagging** on every kill chain step
- **Target asset identification** from IaC files (specific resource names)
- **Threat actor attribution** with APT profiles
- **AWS-specific mitigations** with implementation guidance
- **Composite scoring** (feasibility 30%, impact 25%, detection 15%, novelty 15%, coherence 15%)
- **Fallback mechanism** prevents data loss from LLM variability

## Commands

```bash
# Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000       # start API server
python -m pytest tests/ -v                       # run tests
python -m pytest tests/test_parsers.py -v        # run specific test file

# Frontend
cd frontend && npm run dev                       # start dev server on :5173
npm run build                                    # production build
npm run lint                                     # lint check

# Quick verification
curl http://localhost:8000/api/health              # Backend health check
curl http://localhost:8000/api/llm/status          # LLM provider status
curl http://localhost:8000/api/llm/models          # Available models for selection
```

## LLM provider

The project supports 3 LLM backends configured via `.env` → `LLM_PROVIDER`:
- `ollama` — local, no API key needed. Ensure `ollama serve` is running.
- `bedrock` — AWS Bedrock via bearer token. Uses `AWS_BEARER_TOKEN_BEDROCK`.
- `anthropic` — direct Anthropic API. Uses `ANTHROPIC_API_KEY`.

All agent LLM instances MUST use the `get_llm()` helper in `backend/app/swarm/crews.py`. Never hardcode a model name or provider in any agent definition.

### Dynamic Model Selection

Users can dynamically select which LLM model to use for each threat modeling run:
- **Frontend**: Model dropdown in ThreatModelPage populated from `/api/llm/models` endpoint
- **Backend**: All three pipeline endpoints (`/run`, `/run/quick`, `/run/single`) accept optional `model` parameter
- **Default behavior**: Uses uncommented `OLLAMA_MODEL` from `.env` if no model specified
- **Available models**:
  - **Ollama**: ALL models from local `ollama list` automatically discovered
  - **Bedrock/Anthropic**: Models defined in `.env` configuration
- **Work In Progress restriction**:
  - Models commented in `.env` (e.g., `#OLLAMA_MODEL=qwen3:14b`) are marked as WIP
  - WIP models appear in dropdown but are disabled and cannot be used
  - Labeled with "Work In Progress" suffix in UI
  - Backend validates and rejects WIP model usage with HTTP 400 error
  - Only uncommented models can be used for threat modeling
- **Model discovery**: For Ollama provider, backend queries `http://localhost:11434/api/tags` to get all pulled models dynamically
- **Model override logging**: Backend logs which model is used for each run
- **Implementation**: Model parameter propagates through all three pipeline layers (exploration → evaluation → adversarial)

**Configuration in .env**:
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:27b        # Default model (uncommented = ENABLED)
#OLLAMA_MODEL=qwen3:14b          # Commented = Work In Progress (DISABLED)
#OLLAMA_MODEL=qwen3:4b           # Commented = Work In Progress (DISABLED)
#OLLAMA_MODEL=llama3.2:3b        # Commented = Work In Progress (DISABLED)
```

**How it works**:
1. User pulls any model: `ollama pull mistral` or `ollama pull llama3.2:3b`
2. Model automatically appears in frontend dropdown (no .env editing required)
3. **Commented models** appear but are disabled (marked "Work In Progress")
4. **Only uncommented models** can be selected and used
5. User selects enabled model from dropdown before running threat model
6. Backend validates model is not WIP and uses it for entire pipeline

**Benefits**:
- Clear separation between production-ready and experimental models
- No accidental usage of untested models
- Easy to enable models (just uncomment in .env)
- Shows model size and WIP status in dropdown
- Falls back to `.env` if Ollama unreachable

## Code style

- Python: type hints on all function signatures. Pydantic models for all data structures. Docstrings on public functions and classes.
- React: functional components with hooks. No class components. Destructured imports.
- No `print()` in Python — use `logging` module with appropriate levels (INFO, WARNING, ERROR).
- API responses always return JSON with a `status` field.

## Security rules — NEVER violate these

1. **No secrets in code.** API keys, tokens, passwords, and private keys go in `.env` only. Never hardcode, log, or commit them. The `.env` file is in `.gitignore`.
2. **No secret logging.** Never log request bodies containing credentials, secret ARNs, or API keys. Sanitise before logging.
3. **Validate all file uploads.** Reject files >1MB. Only accept `.tf`, `.yaml`, `.yml`, `.json` extensions. Validate content structure before parsing.
4. **No `eval()` or `exec()` on user input.** IaC files are parsed by python-hcl2 or PyYAML safe_load — never executed.
5. **No shell commands from user input.** CrewAI agents must not have Code Interpreter enabled (CVE-2026-2275).
6. **Pin dependency versions.** When adding packages, pin to a specific range in requirements.txt. Check for known CVEs before adding.
7. **Sanitise LLM output before rendering.** Attack path JSON from agents may contain injection attempts. Validate against Pydantic models before passing to frontend.
8. **CORS is restricted.** Only `http://localhost:5173` in development. Production origins must be set via `ALLOWED_ORIGINS` env var.
9. **No wildcard IAM in agent prompts.** When agents suggest mitigations, they must recommend least-privilege — never `*` resource policies.

## Architecture decisions

- **CrewAI** orchestrates the 3-layer swarm (exploration → evaluation → adversarial). Do not replace with LangGraph, raw API calls, or other frameworks without discussion.
- **Modular threat intel** uses the adapter pattern in `threat_intel/adapters/`. To add a source: create a new adapter file implementing `BaseAdapter`, add entry to `config/sources.yaml`. No other code changes needed.
- **Persona registry** at `swarm/agents/persona_registry.py` manages agent personas. Default personas are `protected: true` and cannot be deleted, only disabled. Custom personas are `protected: false`.
- **Kill chain output** — all attack paths must follow the 3-5 step kill chain format with ATT&CK technique IDs and inline mitigations. See `swarm/models.py` for the schema.
- **Asset graph is cloud-agnostic** — parsers normalise to a common schema (`parsers/models.py`). The swarm layer never sees raw Terraform or CloudFormation.
- **Arbitrator fallback mechanism** — if the arbitrator LLM returns empty `final_paths` despite successful exploration and evaluation, the system falls back to using scored paths directly (with validation metadata). This prevents data loss from LLM output variability. See `backend/app/swarm/crews.py` lines 1246-1255.

## Detailed docs (read when relevant)

### Core Configuration
- `@backend/app/swarm/agents/personas.yaml` — all 13 default agent persona definitions
- `@backend/app/threat_intel/config/sources.yaml` — configured threat intel feeds
- `@backend/requirements.txt` — pinned Python dependencies
- `@samples/README.md` — test IaC files and expected results
- `@.env.example` — all environment variables with descriptions

### Test Reports & Documentation
- `@backend/MODEL_SELECTION_TEST_REPORT.md` — Dynamic model selection implementation and verification (2026-04-13)
- `@backend/FINAL_TEST_VERIFICATION_SUCCESS.md` — Comprehensive backend test: TF parsing, attack paths, MITRE ATT&CK tagging, fallback mechanism (2026-04-13)
- `@backend/COMPREHENSIVE_BACKEND_TEST_REPORT.md` — Full API endpoint testing and pipeline validation
- `@backend/ATTACK_PATH_DISPLAY_FIX.md` — Arbitrator key mismatch fix and fallback mechanism documentation
- `@backend/GEMMA4_FIX_REPORT.md` — gemma4:e4b model compatibility fix for JSON key name variations (2026-04-13)

## Task workflow

1. Plan first: outline changes before coding
2. Make minimal changes: only touch what's necessary
3. Run tests after changes: `python -m pytest tests/ -v`
4. Verify API: `curl http://localhost:8000/api/health`
5. Check frontend renders: `npm run dev` and visually verify
6. Create test report documenting changes and verification
7. Update this file if you learn something new about the project

### When Adding New Features

If the feature affects the threat modeling pipeline:
1. **Backend changes**: Update `app/routers/swarm.py` and/or `app/swarm/crews.py`
2. **Frontend changes**: Update API client (`frontend/src/api/client.js`) and page components
3. **Test with sample file**: Use `samples/clouddocs-saas-app.tf` or similar
4. **Verify attack path structure**: Ensure all required fields present (technique_id, target_asset, mitigations, etc.)
5. **Check backend logs**: Confirm feature is working as intended
6. **Create test report**: Document implementation, verification, and results (see existing reports in `backend/`)
7. **Update OpenAPI schema**: Ensure `/openapi.json` reflects new parameters
8. **Update this file**: Add to "Recent Changes" and relevant sections

### When Fixing Bugs

1. **Document root cause**: Explain why the bug occurred
2. **Document solution**: Explain the fix and why it works
3. **Identify affected files**: List all files modified with line numbers
4. **Test verification**: Run the scenario that previously failed
5. **Create fix documentation**: Save as `backend/<FIX_NAME>.md`
6. **Update "Lessons learned"**: Add to prevent future recurrence

## Known Limitations

1. **Long execution times**: Full pipeline takes 25-30 minutes, quick run takes ~14 minutes. This is inherent to LLM-based multi-agent systems. Not a bug.

2. **LLM output variability**: Even with structured prompts, LLMs occasionally return inconsistent JSON keys or empty results. The fallback mechanism mitigates data loss but can't prevent all variability.

3. **Ollama dynamic discovery**: Dynamic model discovery from local installation only works with Ollama provider. Anthropic and Bedrock models must be explicitly defined in .env.

4. **No streaming progress updates**: Long-running pipelines don't provide real-time progress. User sees loading spinner until completion or timeout.

5. **Synchronous API calls**: All three pipeline endpoints are blocking. Backend doesn't support async job submission with status polling yet.

6. **Single infrastructure file**: Each pipeline run processes one IaC file. No support for analyzing multiple related files in a single run.

7. **AWS-focused mitigations**: Mitigation recommendations are tailored for AWS. GCP/Azure equivalents not yet implemented.

## Troubleshooting

### Backend Won't Start
**Symptom**: `ERROR: [Errno 48] Address already in use`
**Solution**:
```bash
lsof -ti :8000 | xargs kill -9
cd backend && source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Attack Paths Missing Data
**Symptom**: Attack paths show in UI but missing technique IDs or target assets
**Likely Cause**: Arbitrator returned empty `final_paths` array
**Verification**: Check backend logs for "Using scored paths as fallback"
**Status**: Fixed with fallback mechanism (2026-04-13)

### Model Selection Not Working
**Symptom**: Selected model not being used for threat modeling
**Verification**:
1. Check `/api/llm/models` returns available models
2. Check backend logs for "pipeline using model override: <model_name>"
3. Verify `ollama serve` is running if using Ollama
4. Confirm model exists: `ollama list | grep <model_name>`

### Git Push Fails
**Symptom**: `fatal: refusing to merge unrelated histories`
**Solution**:
```bash
git pull origin main --no-rebase --allow-unrelated-histories
# Resolve conflicts if any
git push origin main
```

### Frontend API Calls Timeout
**Symptom**: Request timeout after 30 seconds (default axios timeout)
**Expected Behavior**: Pipeline endpoints are intentionally long-running:
- Full swarm: 30 minute timeout (1800000ms)
- Quick run: 20 minute timeout (1200000ms)
- Single agent: 20 minute timeout (1200000ms)
**Not an Error**: Requests taking 10-30 minutes are normal for LLM-based threat modeling

## Lessons learned

### LLM Output Handling
- CrewAI agents sometimes return markdown-wrapped JSON (```json ... ```). Always strip code fences before parsing.
- Ollama qwen3:14b struggles with strict JSON output. Add explicit "Return ONLY valid JSON" in every task expected_output.
- **Arbitrator key mismatch** (Fixed 2026-04-13): Arbitrator LLM returns paths with key `"path_name"` but merge logic expected `"name"`. Solution: Try both keys with `final_path.get("path_name") or final_path.get("name", "")` (see `crews.py:1213`)
- **Empty arbitrator output** (Fixed 2026-04-13): Arbitrator sometimes returns valid JSON with empty `final_paths` array despite successful exploration/evaluation. Solution: Fallback to scored paths with validation metadata when `len(enriched_final_paths) == 0` (see `crews.py:1246-1255`)
- **Model output variability** (Fixed 2026-04-13): Different LLM models use different JSON key names even with identical prompts. gemma4:e4b returns `"technique"` instead of `"technique_name"`, `"target"` instead of `"target_asset"`, `"attack_details"` instead of `"action_description"`, and `"impact"` instead of `"outcome"`. Solution: Enhanced parser to accept multiple fallback keys for each field (see `crews.py:433, 440, 446-453`). Always design parsers with flexibility for model variations. See `backend/GEMMA4_FIX_REPORT.md`.

### API & Integration
- NVD API rate limits at 5 req/30s without API key. The adapter handles this with retry + backoff.
- **FastAPI Form data**: When adding multipart form parameters to endpoints, must import `Form` from `fastapi` and use `param: str = Form(None)` syntax. Forgetting import causes `NameError: name 'Form' is not defined`.

### IaC Parsing
- python-hcl2 returns resources as a list of single-key dicts, not a flat dict. Iterate carefully.
- CloudFormation Ref values are strings, not objects — check for both `{"Ref": "X"}` dict and plain string references.

### Testing & Validation
- **Attack path validation checklist**: Every path must have: (1) threat actor attribution, (2) MITRE ATT&CK technique IDs on each step, (3) specific target assets from IaC file, (4) logical kill chain progression, (5) mitigations with AWS-specific actions
- Full pipeline takes ~14 minutes with qwen3:14b for quick run (2 agents). Majority of time spent in LLM inference, which is expected behavior.
