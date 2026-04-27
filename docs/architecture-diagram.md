# Swarm TM System Architecture

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[React Web Dashboard<br/>Port 5173]
        UI_COMPONENTS[Components:<br/>- ThreatModelPage<br/>- StigmergicResultsView<br/>- Attack Graph Visualization<br/>- Mitigation Selection]
    end

    subgraph "API Gateway Layer"
        API[FastAPI REST API<br/>Port 8000]
        ROUTERS[API Routers:<br/>- /api/swarm/* - Threat modeling<br/>- /api/intel/* - Threat intelligence<br/>- /api/archive/* - Results storage<br/>- /api/llm/* - Model management]
    end

    subgraph "IaC Processing Layer"
        UPLOAD[File Upload Handler<br/>Max 1MB, .tf/.yaml/.json]
        TF_PARSER[Terraform Parser<br/>python-hcl2]
        CF_PARSER[CloudFormation Parser<br/>PyYAML]
        NORMALIZER[Asset Graph Normalizer<br/>Asset + Relationship models]
    end

    subgraph "Vulnerability Intelligence Layer"
        INTEL_DB[(SQLite intel.db<br/>CVEs, EPSS, KEV,<br/>Abuse Patterns,<br/>Threat Signals,<br/>Persona Patches)]
        VULN_CONTEXT[Vulnerability Context Builder<br/>Asset → CVE mapping<br/>EPSS scoring<br/>Exploit references]
        THREAT_INGEST[Threat Signal Ingestor<br/>Sources: CISA KEV, MITRE ATT&CK,<br/>StopRansomware]
    end

    subgraph "Multi-Agent Orchestration Layer - CrewAI"
        subgraph "Pipeline Mode Selection"
            MODE_SELECT{Pipeline Mode<br/>Selector}
            FULL[Full Swarm<br/>5+ agents<br/>~30 min]
            QUICK[Quick Run<br/>2 agents<br/>~14 min]
            SINGLE[Single Agent<br/>1 persona<br/>~10 min]
            STIGMERGIC[Stigmergic Swarm<br/>Sequential + Graph<br/>~20-25 min]
        end

        subgraph "Layer 1: Exploration Swarm"
            PERSONAS[13 Threat Actor Personas:<br/>APT29, Lazarus, Scattered Spider,<br/>Cloud-Native, Supply Chain,<br/>Insider, Ransomware, etc.]
            SHARED_GRAPH[Stigmergic Shared Graph<br/>Pheromone-based reinforcement<br/>AttackNode + AttackEdge]
            SECURITY_REASONING[Dynamic Security Reasoning<br/>Generic approach<br/>Applied to any config]
        end

        subgraph "Layer 2: Evaluation Swarm"
            EVAL_AGENTS[5 Evaluation Agents:<br/>- Feasibility 30%<br/>- Impact 25%<br/>- Detection 15%<br/>- Novelty 15%<br/>- Coherence 15%]
            SCORING[Composite Score Calculation<br/>Threshold ≥5.0]
        end

        subgraph "Layer 3: Adversarial Validation"
            RED_TEAM[Red Team Agent<br/>Challenge assumptions]
            BLUE_TEAM[Blue Team Agent<br/>Validate defenses]
            ARBITRATOR[Arbitrator Agent<br/>Final adjudication]
            FALLBACK[Fallback Mechanism<br/>Use scored paths if empty]
        end
    end

    subgraph "LLM Provider Layer"
        LLM_SELECT{LLM Provider<br/>get_llm}
        OLLAMA[Ollama Local<br/>Dynamic model discovery<br/>100% offline<br/>FREE]
        BEDROCK[AWS Bedrock<br/>Claude 4 Sonnet/Opus/Haiku<br/>Access Key auth]
        ANTHROPIC[Anthropic API<br/>Claude 4 direct<br/>API key auth]
    end

    subgraph "Output Processing Layer"
        MITIGATION_MAP[Mitigation Mapper<br/>MITRE ATT&CK → AWS mitigations<br/>Defense-in-depth layers]
        RISK_CALC[Risk Calculator<br/>CSA CII 5×5 Matrix<br/>Completeness-based reduction]
        OUTPUT_FILTER[Output Filter<br/>Validate JSON schema<br/>Strip markdown fences]
    end

    subgraph "Data Persistence Layer"
        ARCHIVE_DB[(Archive System<br/>JSON files<br/>GMT+8 timestamps)]
        PERSONA_YAML[(Personas YAML<br/>persona_registry.py<br/>Protected + Custom)]
        THREAT_DATA[(Threat Actor Data<br/>MITRE ATT&CK STIX<br/>Group mappings)]
    end

    subgraph "External Intelligence Sources"
        CISA_KEV[CISA KEV<br/>Known Exploited Vulns]
        MITRE_ATTACK[MITRE ATT&CK<br/>Techniques + Groups]
        STOP_RANSOM[StopRansomware<br/>Campaign data]
        NVD[NVD CVE Database]
    end

    %% User Flow
    UI --> API
    UI_COMPONENTS -.part of.-> UI
    ROUTERS -.part of.-> API

    %% IaC Processing Flow
    API --> UPLOAD
    UPLOAD --> TF_PARSER
    UPLOAD --> CF_PARSER
    TF_PARSER --> NORMALIZER
    CF_PARSER --> NORMALIZER

    %% Vulnerability Intelligence Flow
    NORMALIZER --> VULN_CONTEXT
    VULN_CONTEXT --> INTEL_DB
    THREAT_INGEST --> INTEL_DB
    CISA_KEV --> THREAT_INGEST
    MITRE_ATTACK --> THREAT_INGEST
    STOP_RANSOM --> THREAT_INGEST
    NVD --> INTEL_DB

    %% Multi-Agent Orchestration Flow
    NORMALIZER --> MODE_SELECT
    VULN_CONTEXT --> MODE_SELECT
    MODE_SELECT --> FULL
    MODE_SELECT --> QUICK
    MODE_SELECT --> SINGLE
    MODE_SELECT --> STIGMERGIC

    FULL --> PERSONAS
    QUICK --> PERSONAS
    SINGLE --> PERSONAS
    STIGMERGIC --> PERSONAS
    STIGMERGIC --> SHARED_GRAPH

    PERSONAS --> SECURITY_REASONING
    PERSONAS --> LLM_SELECT
    PERSONA_YAML --> PERSONAS
    INTEL_DB --> PERSONAS

    %% LLM Provider Flow
    LLM_SELECT --> OLLAMA
    LLM_SELECT --> BEDROCK
    LLM_SELECT --> ANTHROPIC

    %% Evaluation Flow
    SECURITY_REASONING --> EVAL_AGENTS
    EVAL_AGENTS --> SCORING
    SCORING --> RED_TEAM
    RED_TEAM --> BLUE_TEAM
    BLUE_TEAM --> ARBITRATOR
    ARBITRATOR --> FALLBACK

    %% Output Processing Flow
    FALLBACK --> MITIGATION_MAP
    THREAT_DATA --> MITIGATION_MAP
    MITIGATION_MAP --> RISK_CALC
    RISK_CALC --> OUTPUT_FILTER
    OUTPUT_FILTER --> API

    %% Data Persistence Flow
    OUTPUT_FILTER --> ARCHIVE_DB
    API --> ARCHIVE_DB

    %% Styling
    classDef userLayer fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    classDef apiLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef processingLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef agentLayer fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef dataLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef llmLayer fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    classDef externalLayer fill:#eceff1,stroke:#455a64,stroke-width:2px

    class UI,UI_COMPONENTS userLayer
    class API,ROUTERS apiLayer
    class UPLOAD,TF_PARSER,CF_PARSER,NORMALIZER,VULN_CONTEXT,MITIGATION_MAP,RISK_CALC,OUTPUT_FILTER processingLayer
    class MODE_SELECT,FULL,QUICK,SINGLE,STIGMERGIC,PERSONAS,SHARED_GRAPH,SECURITY_REASONING,EVAL_AGENTS,SCORING,RED_TEAM,BLUE_TEAM,ARBITRATOR,FALLBACK agentLayer
    class INTEL_DB,ARCHIVE_DB,PERSONA_YAML,THREAT_DATA dataLayer
    class LLM_SELECT,OLLAMA,BEDROCK,ANTHROPIC llmLayer
    class CISA_KEV,MITRE_ATTACK,STOP_RANSOM,NVD externalLayer
```

## Component Details

### 1. User Interface Layer
- **Technology**: React 18 + Vite
- **Key Components**:
  - ThreatModelPage: Main threat modeling interface
  - StigmergicResultsView: Results display with emergent insights
  - Attack Graph Visualization: Interactive React Flow graphs
  - Mitigation Selection: Checkbox-based mitigation application

### 2. API Gateway Layer
- **Technology**: FastAPI + Uvicorn
- **Endpoints**:
  - `/api/swarm/run` - Full swarm threat modeling
  - `/api/swarm/run/quick` - Quick run (2 agents)
  - `/api/swarm/run/single` - Single agent mode
  - `/api/swarm/run/stigmergic` - Stigmergic swarm (recommended)
  - `/api/intel/*` - Threat intelligence operations
  - `/api/archive/*` - Save/load threat models
  - `/api/llm/*` - LLM configuration and model listing

### 3. IaC Processing Layer
- **Parsers**:
  - Terraform: python-hcl2 library
  - CloudFormation: PyYAML safe_load
- **Normalizer**: Converts to Asset + Relationship models
- **Output**: Cloud-agnostic graph representation

### 4. Vulnerability Intelligence Layer
- **Database**: SQLite (intel.db)
- **Tables**:
  - cves: CVE entries with CVSS, EPSS, KEV status
  - abuse_patterns: Cloud misconfigurations and exploits
  - threat_intel_signals: Latest threat actor TTPs
  - persona_patches: AI-generated persona updates
- **Context Builder**: Maps assets to relevant CVEs

### 5. Multi-Agent Orchestration Layer
- **Framework**: CrewAI
- **Layer 1 (Exploration)**: 13 threat actor personas with security reasoning
- **Layer 2 (Evaluation)**: 5 specialized scorers with weighted composite scoring
- **Layer 3 (Adversarial)**: Red/Blue team validation + Arbitrator
- **Stigmergic Graph**: Pheromone-based coordination for emergent insights

### 6. LLM Provider Layer
- **Ollama**: Local models, dynamic discovery, 100% offline
- **AWS Bedrock**: Claude 4 models, enterprise auth
- **Anthropic API**: Direct Claude API access

### 7. Output Processing Layer
- **Mitigation Mapper**: MITRE ATT&CK techniques → AWS-specific mitigations
- **Risk Calculator**: CSA CII 5×5 matrix with completeness-based reduction
- **Output Filter**: JSON validation and markdown fence stripping

### 8. Data Persistence Layer
- **Archive System**: JSON files with GMT+8 timestamps
- **Persona YAML**: 13 default (protected) + custom personas
- **Threat Actor Data**: MITRE ATT&CK STIX format

### 9. External Intelligence Sources
- **CISA KEV**: Known Exploited Vulnerabilities catalog
- **MITRE ATT&CK**: Techniques, groups, and campaigns
- **StopRansomware**: Ransomware campaign data
- **NVD**: National Vulnerability Database

## Data Flow Summary

1. **User uploads IaC** → FastAPI receives file
2. **Parse & Normalize** → Terraform/CloudFormation → Asset Graph
3. **Enrich with Vuln Intel** → Query intel.db for CVEs, EPSS, KEV
4. **Select Pipeline Mode** → Full/Quick/Single/Stigmergic
5. **Layer 1: Explore** → 13 personas generate attack paths (with LLM)
6. **Layer 2: Evaluate** → 5 scorers compute composite scores
7. **Layer 3: Validate** → Red/Blue/Arbitrator produce final threat model
8. **Process Output** → Map mitigations, calculate risk, filter JSON
9. **Return Results** → API → React UI displays attack paths, graph, insights
10. **Archive** → Save threat model with timestamp for future reference

## Key Design Principles

1. **Modularity**: Each layer is independently testable and replaceable
2. **Cloud-Agnostic**: Normalized asset graph supports future GCP/Azure parsers
3. **Provider-Agnostic**: LLM abstraction layer supports multiple providers
4. **Stigmergic Intelligence**: Emergent insights from agent coordination
5. **Defense-in-Depth**: Three-layer validation ensures quality
6. **Living Intelligence**: Automatic persona updates from threat signals
7. **Vulnerability-Grounded**: Real CVE/EPSS/KEV data, not theoretical risks
