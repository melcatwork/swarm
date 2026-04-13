# Swarm TM - AI-Powered Threat Modeling

> Multi-agent swarm intelligence for automated infrastructure threat analysis

Swarm TM is an advanced threat modeling system that uses AI-powered agent swarms to automatically discover, evaluate, and validate attack paths against your cloud infrastructure. By analyzing Infrastructure-as-Code (IaC) files, it identifies realistic attack scenarios from the perspective of multiple threat actors.

## 🚀 Features

- **Multi-Agent Analysis**: Uses CrewAI to coordinate specialized threat actors, evaluators, and validators
- **Three-Layer Validation**: Exploration → Evaluation → Adversarial Review
- **MITRE ATT&CK Mapping**: Automatic technique identification and mitigation recommendations
- **AWS-Specific Context**: Contextual mitigations for AWS security controls
- **Interactive Dashboard**: Modern React UI for exploring attack paths
- **Threat Intelligence**: Real-time threat intel from multiple sources (NIST NVD, CISA KEV, MITRE ATT&CK)
- **Multiple LLM Support**: Works with AWS Bedrock, Anthropic API, or Ollama (local)

## 📋 Architecture Overview
<img width="2455" height="1361" alt="image" src="https://github.com/user-attachments/assets/6af85187-43f5-407b-a1ae-6f483911a3c5" />


### Swarm Intelligence System

Swarm TM uses a three-layer agent architecture:

#### **Layer 1: Exploration Swarm**
Multiple threat actor personas explore the infrastructure in parallel:
- APT29 (Cozy Bear) - State-sponsored sophistication
- Scattered Spider - Social engineering focus
- Lazarus Group - Financial motivation
- Cloud-native Attacker - AWS exploitation
- Opportunistic Attacker - Quick wins

Each agent generates attack paths with:
- Step-by-step techniques (MITRE ATT&CK IDs)
- Target assets from the infrastructure
- Prerequisites and outcomes
- Impact assessment

#### **Layer 2: Evaluation Swarm**
Five specialized evaluators score each attack path:
- **Feasibility Scorer** (30%): Can this attack realistically be executed?
- **Detection Scorer** (15%): How stealthy is this attack?
- **Impact Scorer** (25%): What's the business impact?
- **Novelty Scorer** (15%): Is this a creative/unexpected attack?
- **Coherence Checker** (15%): Does the attack chain make logical sense?

Paths are ranked by composite score and sorted by priority.

#### **Layer 3: Adversarial Validation**
Three agents perform red team / blue team / arbitrator review:
- **Red Team**: Identifies gaps in coverage, proposes additional paths
- **Blue Team**: Challenges feasibility based on actual controls
- **Arbitrator**: Produces final validated threat model with confidence ratings

### Technology Stack

**Backend:**
- FastAPI for REST API
- CrewAI for multi-agent orchestration
- LiteLLM for unified LLM access
- Python 3.11+

**Frontend:**
- React 18 with Vite
- Tailwind CSS for styling
- Axios for API communication
- Lucide React for icons

**LLM Providers:**
- AWS Bedrock (Claude via bearer token)
- Anthropic API (direct)
- Ollama (local models)

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

2. Pull a model:
   ```bash
   ollama pull qwen3:14b
   ```

3. Start Ollama:
   ```bash
   ollama serve
   ```

4. Configure `.env`:
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen3:14b
   ```

#### **AWS Bedrock**

1. Obtain bearer token from AWS Bedrock console
2. Configure `.env`:
   ```bash
   LLM_PROVIDER=bedrock
   AWS_BEARER_TOKEN_BEDROCK=your-token-here
   AWS_REGION_NAME=us-east-1
   ```

#### **Anthropic API**

1. Get API key from https://console.anthropic.com
2. Configure `.env`:
   ```bash
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

## 📖 Usage

### Threat Modeling Workflow

1. **Prepare IaC File**
   - Export Terraform (.tf) or CloudFormation (.yaml/.json)
   - File must be < 1MB
   - Should describe AWS infrastructure

2. **Upload and Run**
   - Navigate to Threat Modeling page
   - Upload IaC file
   - Choose "Full Swarm" (5 agents, ~10min) or "Quick Run" (2 agents, ~5min)

3. **Review Results**
   - **Asset Graph**: View parsed infrastructure components
   - **Executive Summary**: High-level threat assessment
   - **Attack Paths**: Detailed attack scenarios ranked by composite score
   - **Mitigations**: MITRE ATT&CK + AWS-specific recommendations

### API Endpoints

#### **Health Check**
```bash
GET /api/health
```

#### **LLM Status**
```bash
GET /api/llm-status
```

#### **Threat Intelligence**
```bash
GET /api/intel/items?category=cve&limit=50
POST /api/intel/pull
```

#### **Threat Modeling**
```bash
# Full pipeline (all agents)
POST /api/swarm/run
Content-Type: multipart/form-data
file: <iac-file>

# Quick pipeline (2 agents)
POST /api/swarm/run/quick
Content-Type: multipart/form-data
file: <iac-file>
```

#### **Personas Management**
```bash
GET /api/swarm/personas
PUT /api/swarm/personas/{name}/toggle
POST /api/swarm/personas
```

Full API documentation: `http://localhost:8000/docs`

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

**Issue**: `LLM is not properly configured`

**Solution**: Check your `.env` file has the correct LLM provider credentials:
- Ollama: Ensure `ollama serve` is running
- Bedrock: Verify `AWS_BEARER_TOKEN_BEDROCK` is set
- Anthropic: Verify `ANTHROPIC_API_KEY` is set

### Frontend Can't Connect

**Issue**: Red banner "Backend Unreachable"

**Solution**:
1. Ensure backend is running: `http://localhost:8000/api/health`
2. Check CORS settings in backend `.env`
3. Verify no firewall blocking port 8000

### Pipeline Timeout

**Issue**: 504 Gateway Timeout

**Solution**:
- Use "Quick Run" instead of "Full Swarm"
- Reduce file size if very large
- Check LLM provider is responsive

### File Upload Fails

**Issue**: 413 Payload Too Large

**Solution**: Reduce file size to under 1MB. Extract relevant infrastructure if needed.

**Issue**: 422 Unprocessable Entity

**Solution**: Ensure file is valid Terraform or CloudFormation format.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent orchestration
- [MITRE ATT&CK](https://attack.mitre.org/) - Threat intelligence framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - Frontend framework

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/redcountryroad/swarm-tm/issues)
- Documentation: This README and `/docs` endpoint

---

**Note**: Swarm TM is designed for security research and authorized testing only. Always ensure you have proper authorization before conducting threat modeling or security assessments.
