# Swarm TM - AI-Powered Threat Modeling

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-purple.svg)](https://github.com/joaomdmoura/crewAI)
[![MITRE ATT&CK](https://img.shields.io/badge/MITRE-ATT%26CK-red.svg)](https://attack.mitre.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> Multi-agent swarm intelligence for automated infrastructure threat analysis

Swarm TM is an advanced threat modeling system that uses AI-powered agent swarms to automatically discover, evaluate, and validate attack paths against your cloud infrastructure. By analyzing Infrastructure-as-Code (IaC) files, it identifies realistic attack scenarios from the perspective of multiple threat actors with MITRE ATT&CK mapping and AWS-specific mitigations.

**⚠️ Important**: Pipeline runs take **14-30 minutes** depending on mode. This is normal for LLM-based multi-agent systems.

---

## 📚 Table of Contents

- [Key Features](#-key-features)
- [TL;DR - Get Started in 5 Minutes](#-tldr---get-started-in-5-minutes)
- [Architecture Overview](#-architecture-overview)
  - [Four Pipeline Modes](#four-pipeline-modes)
  - [Three-Layer Agent Architecture](#three-layer-agent-architecture)
  - [Technology Stack](#technology-stack)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
- [Docker Deployment](#-docker-deployment)
- [Railway Deployment](#️-railway-deployment)
- [Configuration](#-configuration)
  - [Environment Variables](#environment-variables)
  - [LLM Provider Setup](#llm-provider-setup)
- [Usage](#-usage)
  - [Threat Modeling Workflow](#threat-modeling-workflow)
  - [API Endpoints](#api-endpoints)
- [Development](#️-development)
  - [Project Structure](#project-structure)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
- [Performance Characteristics](#-performance-characteristics)
- [Security Considerations](#-security-considerations)
- [File Size Limits](#-file-size-limits)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Screenshots](#-screenshots)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Support & Community](#-support--community)
- [Roadmap](#-roadmap)

---

## 🚀 Key Features

### 🤖 Multi-Agent Swarm Intelligence
- **4 Pipeline Modes**: Full Swarm (5+ agents), Quick Run (2 agents), Single Agent, Stigmergic Swarm
- **13 Threat Actor Personas**: APT29, Scattered Spider, Lazarus Group, Cloud-native Attacker, and more
- **Three-Layer Validation**: Exploration → Evaluation → Adversarial Review
- **Stigmergic Coordination**: Agents build on each other's discoveries through shared graph reinforcement

### 🎯 Attack Path Analysis
- **MITRE ATT&CK Mapping**: Automatic technique identification (T1078, T1552, etc.) for every kill chain step
- **Target Asset Identification**: Maps attacks to specific infrastructure resources from IaC files
- **CSA CII Risk Assessment**: 5×5 risk matrix (likelihood × impact) with residual risk calculation
- **Completeness-Based Mitigation**: Granular risk reduction based on mitigation selection percentage

### 🔧 Flexible LLM Support
- **Dynamic Model Selection**: Choose from ANY locally installed Ollama model via UI dropdown
- **3 Provider Options**: Ollama (local), AWS Bedrock (Claude via Access Key), Anthropic API (direct)
- **Work-in-Progress Models**: Mark experimental models as WIP to prevent accidental production use

### 📊 Modern Web Dashboard
- **Interactive Attack Graph**: React Flow visualization with swim lanes, path traversal animation, zoom/pan
- **Threat Model Summary**: High-level overview showing total paths, risk distribution, coverage percentage
- **Mitigation Selection**: Checkbox-based mitigation application with real-time residual risk calculation
- **Threat Intelligence**: Real-time threat intel from 13 sources (NVD, SecurityWeek, BleepingComputer, etc.)
- **Long-Running Operation UI**: Elapsed timer, backend health polling, contextual status messages

### ⚡ Advanced Features
- **Cancel Run**: Stop long-running operations gracefully without orphaned processes
- **Archive System**: Save and load previous threat models with GMT+8 timestamps
- **Model Size Display**: See model sizes in dropdown for resource planning
- **Normalized Citation Scoring**: 0-10 scale for threat intelligence relevance

## ⚡ TL;DR - Get Started in 5 Minutes

```bash
# 1. Install Ollama (local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3.5:27b
ollama serve

# 2. Clone and setup backend
git clone https://github.com/redcountryroad/swarm-tm.git
cd swarm-tm/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env: Set LLM_PROVIDER=ollama, OLLAMA_MODEL=qwen3.5:27b
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Setup frontend (new terminal)
cd frontend
npm install && npm run dev

# 4. Access http://localhost:5173
# Upload sample file: samples/clouddocs-saas-app.tf
# Click "Quick Run" (14 min) or "Full Swarm" (30 min)
```

## 📋 Architecture Overview

![Swarm TM Architecture](docs/architecture.png)
*Click to enlarge: Comprehensive architecture showing 7-step workflow from user upload to threat model display*


### Four Pipeline Modes

Choose the mode that fits your use case:

| Mode | Agents | Duration | Use Case |
|------|--------|----------|----------|
| **Full Swarm** | 5+ exploration + 5 evaluators + 3 adversarial | ~25-30 min | Production threat models, comprehensive analysis |
| **Quick Run** | 2 exploration + 5 evaluators + 3 adversarial | ~14 min | Development, testing, rapid iteration |
| **Single Agent** | 1 specific persona + full validation | ~10-15 min | Targeted analysis (e.g., "How would APT29 attack this?") |
| **Stigmergic Swarm** | Sequential agents with shared graph | ~20-25 min | Emergent insights, cross-agent pattern detection |

### Three-Layer Agent Architecture

#### **Layer 1: Exploration Swarm**
Multiple threat actor personas explore the infrastructure:
- **APT29 (Cozy Bear)**: State-sponsored sophistication, persistence focus
- **Scattered Spider**: Social engineering, identity compromise
- **Lazarus Group**: Financial motivation, supply chain attacks
- **Cloud-native Attacker**: AWS-specific exploitation, misconfiguration abuse
- **Opportunistic Attacker**: Quick wins, low-hanging fruit
- **Insider Threat**, **Ransomware Operator**, **Nation-State APT**, **Hacktivism**, **Supply Chain Attacker**, **Cryptojacking**, **Data Exfiltration Specialist**, **IoT Botnet Operator**

Each agent generates attack paths with:
- Kill chain steps (Initial Access → Execution → Lateral Movement → Objective → Covering Tracks)
- MITRE ATT&CK technique IDs (T1078, T1552.005, etc.)
- Target assets from infrastructure (specific S3 buckets, IAM roles, Lambda functions)
- Prerequisites, actions, outcomes for each step

#### **Layer 2: Evaluation Swarm**
Five specialized evaluators score each attack path (0-10 scale):
- **Feasibility Scorer** (30%): Can this attack realistically be executed with the infrastructure?
- **Impact Scorer** (25%): What's the business impact (data loss, downtime, financial)?
- **Detection Scorer** (15%): How stealthy is this attack against AWS CloudTrail, GuardDuty?
- **Novelty Scorer** (15%): Is this a creative/unexpected attack vector?
- **Coherence Checker** (15%): Does the attack chain make logical sense?

**Composite Score** = (F×0.30 + I×0.25 + D×0.15 + N×0.15 + C×0.15)

Paths are ranked by composite score and filtered by threshold (≥5.0).

#### **Layer 3: Adversarial Validation**
Three agents perform adversarial review:
- **Red Team**: Identifies gaps, proposes additional attack paths, challenges assumptions
- **Blue Team**: Defends against red team, validates existing controls, suggests improvements
- **Arbitrator**: Produces final validated threat model with confidence ratings and challenged flags

**Fallback Mechanism**: If arbitrator returns empty results, system automatically uses scored paths from Layer 2 to prevent data loss.

### Technology Stack

**Backend (Python 3.11+):**
- **FastAPI** - REST API framework with automatic OpenAPI docs
- **CrewAI** - Multi-agent orchestration framework
- **LiteLLM** - Unified LLM interface (Ollama, Bedrock, Anthropic)
- **python-hcl2** - Terraform parser
- **PyYAML** - CloudFormation parser
- **Pydantic** - Data validation and settings management
- **SQLite** - Local database for threat intel cache
- **feedparser** - RSS/Atom feed parsing for threat intel
- **STIX/TAXII** - MITRE ATT&CK framework integration

**Frontend (React 18 + Vite):**
- **React 18** - UI framework with hooks
- **Vite** - Fast development server and build tool
- **React Flow** - Interactive node-based graph visualization
- **Axios** - HTTP client with request cancellation
- **Lucide React** - Icon library (ChevronDown, Shield, AlertTriangle, etc.)
- **Tailwind CSS** - Utility-first CSS framework (via CDN)
- **Date-fns** - Date formatting and timezone handling (GMT+8)

**LLM Providers (3 options):**
1. **Ollama** - Local models (qwen, mistral, llama, gemma) - FREE, 100% offline
2. **AWS Bedrock** - Claude 3.5 Sonnet, Claude 3 Opus/Sonnet/Haiku - AWS Access Key auth
3. **Anthropic API** - Direct Claude API access - API key auth

**Infrastructure & Deployment:**
- **Docker** - Containerization for backend and frontend
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Frontend static file serving (production)
- **Uvicorn** - ASGI server for FastAPI
- **Railway** - Cloud deployment platform (backend)

**Security & Compliance:**
- **CORS** - Configurable origin restrictions
- **File validation** - Size limits (<1MB), extension whitelisting
- **No code execution** - IaC parsed, never executed
- **Secrets management** - `.env` file (gitignored)
- **CSA CII** - Cloud Security Alliance Critical Information Infrastructure risk matrix

## 🏃 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- An LLM provider:
  - Ollama running locally (easiest for testing), OR
  - AWS Bedrock API key, OR
  - Anthropic API key

### Local Development

#### 1. Clone the Repository

```bash
git clone https://github.com/redcountryroad/swarm-tm.git
cd swarm-tm
```

#### 2. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp ../.env.example ../.env
# Edit .env with your LLM provider credentials

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

#### 3. Set Up Frontend

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

#### 4. Access the Application

Navigate to `http://localhost:5173` in your browser.

## 🐋 Docker Deployment

### Using Docker Compose

The easiest way to deploy Swarm TM is with Docker Compose:

```bash
# Ensure .env file is configured
cp .env.example .env
# Edit .env with your LLM provider credentials

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Building Individual Containers

**Backend:**
```bash
cd backend
docker build -t swarm-tm-backend .
docker run -p 8000:8000 --env-file ../.env swarm-tm-backend
```

**Frontend:**
```bash
cd frontend
docker build -t swarm-tm-frontend .
docker run -p 3000:80 swarm-tm-frontend
```

## ☁️ Railway Deployment

Deploy the backend to Railway:

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login and initialize:
   ```bash
   railway login
   railway init
   ```

3. Set environment variables in Railway dashboard:
   - `LLM_PROVIDER`
   - `ANTHROPIC_API_KEY` or `AWS_BEARER_TOKEN_BEDROCK`
   - Other required variables from `.env.example`

4. Deploy:
   ```bash
   railway up
   ```

The `Procfile` will automatically configure the service.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### **LLM Provider Configuration**

Choose ONE provider:

**Option 1: Ollama (Local, Free)**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:14b
```

**Option 2: AWS Bedrock**
```bash
LLM_PROVIDER=bedrock
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key-here
AWS_REGION_NAME=us-east-1
BEDROCK_MODEL=bedrock/anthropic.claude-sonnet-4-20250514-v1:0
```

**Option 3: Anthropic API**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

#### **CORS Configuration (Production)**
```bash
# Comma-separated list of allowed origins
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

#### **Database**
```bash
DATABASE_URL=sqlite:///data/swarm_tm.db
```

### LLM Provider Setup

#### **Ollama (Recommended for Local Development)**

1. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull any model (automatically discovered by UI):
   ```bash
   ollama pull qwen3.5:27b       # Recommended (best quality)
   ollama pull mistral           # Fast alternative
   ollama pull llama3.2:3b       # Lightweight
   ```

3. Start Ollama:
   ```bash
   ollama serve
   ```

4. Configure `.env`:
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen3.5:27b      # Default model (uncommented = production-ready)
   #OLLAMA_MODEL=qwen3:14b        # Commented = Work In Progress (disabled in UI)
   ```

**Dynamic Model Discovery**: ALL models from `ollama list` automatically appear in the UI dropdown with sizes. Just `ollama pull <model>` and it's immediately available for selection. No `.env` editing required!

**Work-in-Progress Models**: Commented models in `.env` are marked as "Work In Progress" and disabled in the UI to prevent accidental use of experimental models.

#### **AWS Bedrock**

1. Obtain AWS Access Key credentials (IAM user or role)
2. Configure `.env`:
   ```bash
   LLM_PROVIDER=bedrock
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   AWS_REGION_NAME=us-east-1
   BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514-v1:0
   ```

**Available Models**:
- Claude 3.5 Sonnet v2 (most capable)
- Claude 3.5 Sonnet v1
- Claude 3 Opus (most powerful)
- Claude 3 Sonnet (balanced)
- Claude 3 Haiku (fastest)

#### **Anthropic API**

1. Get API key from https://console.anthropic.com
2. Configure `.env`:
   ```bash
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ANTHROPIC_MODEL=claude-sonnet-4-20250514
   ```

## 📖 Usage

### Threat Modeling Workflow

#### 1. **Prepare IaC File**
   - Export Terraform (`.tf`) or CloudFormation (`.yaml`/`.json`)
   - File must be **< 1MB**
   - Should describe AWS infrastructure (S3, Lambda, IAM, EC2, RDS, etc.)
   - Sample files available in `samples/` directory

#### 2. **Configure LLM Model**
   - Navigate to Threat Modeling page
   - Select model from dropdown (dynamically populated from Ollama or configured provider)
   - Model sizes displayed for reference (e.g., "qwen3.5:27b - 15.3 GB")
   - WIP models are disabled and cannot be selected

#### 3. **Upload and Run**
   - Upload IaC file
   - Choose pipeline mode:
     - **Full Swarm**: 5+ agents, 25-30 min, comprehensive analysis
     - **Quick Run**: 2 agents, 14 min, rapid iteration
     - **Single Agent**: Choose specific threat actor (e.g., APT29), 10-15 min
     - **Stigmergic Swarm**: Sequential agents with shared graph, 20-25 min
   - Click "Run Threat Model" button
   - **Progress tracking**: Elapsed timer shows MM:SS, backend health indicators pulse every 10s
   - **Cancel anytime**: Stop button appears during run for graceful cancellation

#### 4. **Review Results**

Results appear in sequential phases:

1. **Threat Model Summary** (top section)
   - Total discovered attack paths
   - Primary & alternate paths (CVE-grounded) with highest risk band
   - Overall highest risk level across all paths
   - Attack surface coverage percentage (stigmergic swarm)
   - Risk distribution: Critical/High/Medium/Low/Very Low counts
   - Data classification impact configuration

2. **Infrastructure Asset Graph**
   - Parsed infrastructure components (S3 buckets, Lambda functions, IAM roles, etc.)
   - Node-link diagram showing relationships
   - Click nodes to explore connections

3. **Attack Path Cards** (ranked by composite score)
   - Threat actor attribution (e.g., APT29 - Cozy Bear)
   - Kill chain visualization (5 phases with MITRE ATT&CK technique IDs)
   - Target assets from infrastructure (specific resource names)
   - CSA CII risk assessment: Likelihood × Impact = Risk Score
   - Composite score breakdown (Feasibility, Impact, Detection, Novelty, Coherence)
   - Inline mitigations for each technique

4. **Mitigation Action Toolbar**
   - Appears between Attack Paths and Comprehensive Mitigation Summary
   - **Clear Selections**: Reset all checkboxes
   - **Apply All Mitigations & Analyze**: Select all and calculate residual risk
   - **Apply Mitigations & Analyze**: Calculate residual risk for selected mitigations only

5. **Comprehensive Mitigation Summary**
   - All MITRE ATT&CK techniques across all paths
   - AWS-specific mitigation recommendations
   - **Checkbox selection**: Choose which mitigations to implement
   - **Completeness-based reduction**: 100% selection = maximum risk reduction, partial selection = proportional reduction
   - **Residual Risk Calculation**: Shows likelihood/impact/risk before and after mitigation

6. **Shared Attack Graph** (stigmergic swarm only)
   - Interactive React Flow visualization with swim lanes
   - Path traversal animation: Click any node to trace all attack paths through it
   - Reinforced nodes: Techniques validated by multiple agents
   - Coverage gaps: Unexplored kill chain phases

### API Endpoints

#### **Health Check**
```bash
GET /api/health
# Returns: {"status": "ok", "message": "Swarm TM Backend is running"}
```

#### **LLM Configuration**
```bash
# Get current LLM provider and model
GET /api/llm/status

# List all available models (with sizes, WIP status, provider info)
GET /api/llm/models

# Configure AWS Bedrock credentials (via UI form)
POST /api/llm/bedrock/configure
Content-Type: application/json
{
  "access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCY...",
  "region": "us-east-1"
}
```

#### **Threat Intelligence**
```bash
# Get threat intel items (13 sources)
GET /api/intel/items?category=cve&limit=50&source=NVD

# Pull latest threat intel from all sources
POST /api/intel/pull

# Get all configured sources
GET /api/intel/sources
```

#### **Threat Modeling - 4 Pipeline Modes**
```bash
# Mode 1: Full Swarm (5+ agents, 25-30 min)
POST /api/swarm/run
Content-Type: multipart/form-data
file: <iac-file>
model: qwen3.5:27b  # optional, overrides default

# Mode 2: Quick Run (2 agents, 14 min)
POST /api/swarm/run/quick
Content-Type: multipart/form-data
file: <iac-file>
model: qwen3.5:27b  # optional

# Mode 3: Single Agent (1 specific threat actor, 10-15 min)
POST /api/swarm/run/single?agent_name=apt29_cozy_bear
Content-Type: multipart/form-data
file: <iac-file>
model: qwen3.5:27b  # optional

# Mode 4: Stigmergic Swarm (sequential with shared graph, 20-25 min)
POST /api/swarm/run/stigmergic
Content-Type: multipart/form-data
file: <iac-file>
execution_order: capability_asc  # capability_asc, capability_desc, or random
model: qwen3.5:27b  # optional

# Cancel running operation
POST /api/swarm/cancel/{job_id}
```

#### **Mitigation Analysis**
```bash
# Analyze post-mitigation impact with completeness-based reduction
POST /api/swarm/mitigations/analyze
Content-Type: application/json
{
  "attack_paths": [...],
  "selected_mitigations": {
    "T1078": ["mit1", "mit2"],
    "T1552.005": ["mit1"]
  }
}
```

#### **Personas Management**
```bash
# Get all personas (default + custom)
GET /api/swarm/personas

# Toggle persona enabled/disabled
PUT /api/swarm/personas/{name}/toggle

# Create custom persona
POST /api/swarm/personas
Content-Type: application/json
{
  "name": "custom_attacker",
  "role": "Custom Threat Actor",
  "goal": "...",
  "backstory": "..."
}

# Delete custom persona (protected personas cannot be deleted)
DELETE /api/swarm/personas/{name}
```

#### **Archive Management**
```bash
# Save current threat model
POST /api/archive/save

# List all archived runs (with GMT+8 timestamps)
GET /api/archive/list

# Load specific archived run
GET /api/archive/load/{run_id}

# Delete archived run
DELETE /api/archive/delete/{run_id}
```

**Full API Documentation**: `http://localhost:8000/docs` (Swagger UI with interactive testing)

## 🛠️ Development

### Project Structure

```
swarm-tm/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── parsers/             # IaC parsers (Terraform, CloudFormation)
│   │   ├── routers/             # API endpoints
│   │   │   ├── swarm.py         # Swarm operations
│   │   │   ├── threat_intel.py  # Threat intelligence
│   │   │   └── iac_upload.py    # IaC file handling
│   │   ├── swarm/
│   │   │   ├── agents/          # Persona definitions
│   │   │   ├── crews.py         # Crew construction
│   │   │   └── mitigations.py   # Mitigation mapping
│   │   └── threat_intel/        # Threat intel adapters
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   └── utils/               # Utilities
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── Procfile
├── .env.example
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
flake8 app/
black app/

# Frontend linting
cd frontend
npm run lint
```

## 📝 File Size Limits

- Maximum IaC file size: **1 MB**
- Supported formats: `.tf`, `.yaml`, `.yml`, `.json`

## 🐛 Troubleshooting

### Backend Won't Start

**Issue**: `ERROR: [Errno 48] Address already in use`

**Solution**: Kill process on port 8000 and restart:
```bash
lsof -ti :8000 | xargs kill -9
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Issue**: `LLM is not properly configured`

**Solution**: Check your `.env` file has the correct LLM provider credentials:
- **Ollama**: Ensure `ollama serve` is running, verify `OLLAMA_BASE_URL=http://localhost:11434`
- **Bedrock**: Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
- **Anthropic**: Verify `ANTHROPIC_API_KEY` is set

**Verification**:
```bash
curl http://localhost:8000/api/llm/status
curl http://localhost:8000/api/llm/models
```

### Frontend Can't Connect

**Issue**: Red banner "Backend Unreachable"

**Solution**:
1. Ensure backend is running: `curl http://localhost:8000/api/health`
2. Check CORS settings in `.env`: `CORS_ORIGINS=http://localhost:5173`
3. Verify no firewall blocking port 8000
4. Check browser console for specific error messages

### Attack Paths Missing Data

**Issue**: Attack paths show in UI but missing technique IDs, target assets, or mitigations

**Likely Cause**: Arbitrator returned empty `final_paths` array

**Verification**: Check backend logs for "Using scored paths as fallback"

**Status**: Automatically handled by fallback mechanism (no user action needed)

### Model Selection Not Working

**Issue**: Selected model not being used for threat modeling

**Solution**:
1. Check available models: `curl http://localhost:8000/api/llm/models`
2. Verify Ollama is running: `ollama list`
3. Check backend logs for "pipeline using model override: <model_name>"
4. Ensure model exists: `ollama pull <model_name>`

**Issue**: "Work In Progress" model is disabled in dropdown

**Explanation**: Commented models in `.env` (e.g., `#OLLAMA_MODEL=qwen3:14b`) are marked as WIP and cannot be used. Uncomment the line in `.env` to enable.

### Pipeline Timeout / Long Execution Time

**Issue**: Request taking 15-30 minutes

**Expected Behavior**: This is NORMAL for LLM-based multi-agent systems:
- Full Swarm: 25-30 minutes
- Quick Run: 14 minutes  
- Single Agent: 10-15 minutes
- Stigmergic Swarm: 20-25 minutes

**Frontend timeout increased to 30 minutes** to handle long operations. The elapsed timer shows progress.

**Issue**: Operation takes longer than expected

**Solution**:
- Use "Quick Run" (2 agents) instead of "Full Swarm" (5+ agents)
- Try smaller/faster model (e.g., `llama3.2:3b` instead of `qwen3.5:27b`)
- Check LLM provider is responsive: `curl http://localhost:11434/api/tags` (Ollama)

### File Upload Fails

**Issue**: `413 Payload Too Large`

**Solution**: Reduce file size to under 1MB. Extract only relevant infrastructure components.

**Issue**: `422 Unprocessable Entity`

**Solution**: Ensure file is valid Terraform (`.tf`) or CloudFormation (`.yaml`/`.json`) format. Test parsing:
```bash
# Terraform
python -c "import hcl2; print(hcl2.load(open('file.tf')))"

# CloudFormation
python -c "import yaml; print(yaml.safe_load(open('file.yaml')))"
```

### Git Push Fails

**Issue**: `fatal: refusing to merge unrelated histories`

**Solution**:
```bash
git pull origin main --no-rebase --allow-unrelated-histories
# Resolve conflicts if any
git add .
git commit -m "Merge unrelated histories"
git push origin main
```

### Ollama Dynamic Discovery Not Working

**Issue**: Models from `ollama list` don't appear in UI dropdown

**Solution**:
1. Verify Ollama is running: `ollama serve`
2. Check Ollama API is accessible: `curl http://localhost:11434/api/tags`
3. Restart backend to refresh model list
4. Check backend logs for "Discovered N Ollama models"

**Fallback**: If Ollama unreachable, system falls back to `.env` configured models only.

## ⚡ Performance Characteristics

Execution times based on **qwen3:14b** model on local hardware (Apple M-series or equivalent):

### Quick Run Pipeline (~14 minutes)
- **IaC Parsing**: ~5s (1%)
- **Exploration** (2 agents): ~230s (28%)
- **Evaluation** (5 scorers): ~280s (34%)
- **Adversarial** (3 agents): ~310s (37%)
- **Mitigation Mapping**: ~3s (<1%)

### Full Swarm Pipeline (~25-30 minutes)
- More exploration agents run in parallel (5+ vs 2)
- Same evaluation and adversarial phases
- Majority of time spent in LLM inference (expected)

### Model Speed Comparison
Relative speeds (qwen3:14b = 1.0x baseline):

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `qwen3.5:27b` | 0.7x | ⭐⭐⭐⭐⭐ | Production (recommended) |
| `qwen3:14b` | 1.0x | ⭐⭐⭐⭐ | Development baseline |
| `mistral` | 1.2x | ⭐⭐⭐⭐ | Fast production alternative |
| `gemma4:e4b` | 1.3x | ⭐⭐⭐ | Quick testing |
| `llama3.2:3b` | 2.0x | ⭐⭐ | Rapid prototyping only |

**Note**: Larger models (27b+) produce higher quality attack paths with better MITRE ATT&CK technique accuracy but take ~30% longer.

## 🔐 Security Considerations

### Important Notes
- **Authorized Testing Only**: Swarm TM is designed for security research and authorized security assessments. Always ensure you have proper authorization before conducting threat modeling.
- **Sensitive Data**: IaC files may contain sensitive infrastructure details. Never upload production IaC to third-party services.
- **API Keys**: Store all API keys in `.env` file (already in `.gitignore`). Never commit secrets to version control.
- **LLM Output**: Attack path suggestions are AI-generated and should be validated by security professionals before implementation.

### What Swarm TM Does NOT Do
- **Does not execute attacks**: Only generates theoretical attack scenarios
- **Does not access your infrastructure**: Only analyzes IaC files (static analysis)
- **Does not store uploaded files permanently**: Files are processed in-memory and discarded after analysis
- **Does not send data to external services**: When using Ollama, all processing is 100% local

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 💡 Example Output

### Input: Terraform File
```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "company-logs-bucket"
  acl    = "private"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_lambda_function" "data_processor" {
  function_name = "data-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"
  
  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.logs.id
    }
  }
}
```

### Output: Attack Path Example

**Threat Actor**: APT29 (Cozy Bear) - State-Sponsored  
**Composite Score**: 7.8/10 (High Priority)  
**Risk Assessment**: Likelihood 4 × Impact 5 = **Risk 20 (Very High)**

**Kill Chain**:
1. **Initial Access** (T1078 - Valid Accounts)
   - Target: `lambda_execution_role`
   - Action: Compromise AWS credentials through phishing or leaked access keys
   - Mitigations: MFA enforcement, AWS IAM Access Analyzer, credential rotation policy

2. **Execution** (T1204 - User Execution)
   - Target: `data-processor` Lambda function
   - Action: Execute malicious code via compromised Lambda function
   - Mitigations: Lambda function signing, runtime monitoring with CloudWatch

3. **Collection** (T1530 - Data from Cloud Storage)
   - Target: `company-logs-bucket`
   - Action: Exfiltrate sensitive logs from S3 bucket
   - Mitigations: S3 Block Public Access, bucket encryption, CloudTrail logging

**Post-Mitigation** (if all mitigations selected):  
Residual Risk: Likelihood 1 × Impact 5 = **Risk 5 (Medium)** - 75% risk reduction ✅

---

## 📸 Screenshots

### Threat Model Dashboard
![Threat Model Summary](docs/screenshots/threat-model-summary.png)
*High-level overview showing total paths, risk distribution, and coverage percentage*

### Attack Path Visualization
![Attack Path Card](docs/screenshots/attack-path-card.png)
*Kill chain visualization with MITRE ATT&CK techniques and target assets*

### Interactive Attack Graph
![Shared Attack Graph](docs/screenshots/shared-attack-graph.png)
*React Flow visualization with swim lanes, path traversal, and reinforced nodes*

### Mitigation Selection
![Mitigation Summary](docs/screenshots/mitigation-summary.png)
*Checkbox-based mitigation selection with residual risk calculation*

### Threat Intelligence Feed
![Threat Intel Dashboard](docs/screenshots/threat-intel-dashboard.png)
*Real-time threat intelligence from 13 sources with normalized scoring*

> **Note**: Add screenshots to `docs/screenshots/` directory before pushing to GitHub.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2026 redcountryroad**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent orchestration
- [MITRE ATT&CK](https://attack.mitre.org/) - Threat intelligence framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - Frontend framework

## 📧 Support & Community

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/redcountryroad/swarm-tm/issues)
- **API Documentation**: Interactive Swagger UI at `http://localhost:8000/docs`
- **Sample Files**: Test with examples in `samples/` directory
- **Project Documentation**: See `CLAUDE.md` for detailed architecture and development notes

### Common Questions

**Q: How long should a threat model take?**  
A: 14-30 minutes depending on mode. This is normal for LLM-based multi-agent systems.

**Q: Can I use this with GCP or Azure?**  
A: Not yet. Currently AWS-focused (Terraform/CloudFormation). GCP/Azure support is planned.

**Q: How do I add custom threat actors?**  
A: Use the Personas Management page to create custom personas with specific goals and backstories.

**Q: Can I run this offline?**  
A: Yes! Use Ollama provider for 100% local operation (no internet required after model download).

**Q: What LLM model should I use?**  
A: For production: `qwen3.5:27b` (best quality). For testing: `mistral` or `gemma4:e4b` (faster).

### Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests: `pytest` (backend) and `npm test` (frontend)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Reporting Security Issues

If you discover a security vulnerability, please email directly instead of using public issues. We take all security reports seriously.

---

## 🎯 Roadmap

### Planned Features
- [ ] GCP and Azure infrastructure support
- [ ] Real-time streaming progress updates for long pipelines
- [ ] Background job submission with status polling API
- [ ] Multi-file infrastructure analysis (analyze related IaC files together)
- [ ] Custom mitigation library per organization
- [ ] Export threat model to PDF/DOCX reports
- [ ] Integration with SIEM systems (Splunk, ElasticSearch)
- [ ] Historical risk tracking and trending

### Recent Updates (2026-04-23)

✅ **Threat Model Summary Component** - High-level overview with total paths, risk bands, coverage %  
✅ **Completeness-Based Mitigation Logic** - Granular risk reduction based on selection percentage  
✅ **Mitigation Action Toolbar** - Single consolidated toolbar for mitigation actions  
✅ **React Flow Migration** - Fixed swim lane rendering with proper zoom/pan behavior  
✅ **Stigmergic Swarm Mode** - Sequential agents with shared graph coordination  
✅ **AWS Bedrock Integration** - Access Key credentials with 5 Claude models  
✅ **Dynamic Model Selection** - Choose ANY Ollama model via UI dropdown  
✅ **Cancel Run Feature** - Gracefully stop long-running operations  
✅ **Enhanced Threat Intelligence** - Expanded from 3 to 13 sources with normalized scoring  

See `CLAUDE.md` for detailed change history.

---

**⚠️ Disclaimer**: Swarm TM is designed for security research, authorized penetration testing, and security assessments only. Always ensure you have proper authorization before conducting threat modeling or security testing. The developers assume no liability for misuse of this tool.
