# Swarm Exploration API

## Overview

The Swarm Exploration API provides endpoints for running multi-agent threat modeling analysis on cloud infrastructure. Each enabled persona (threat actor or archetype) analyzes the infrastructure and generates structured attack paths with MITRE ATT&CK mappings.

## ⚠️ Important Warnings

**These endpoints make real API calls to Anthropic Claude and are expensive:**
- **Full exploration** (`/explore`): ~$0.20+ per run, several minutes (13 agents)
- **Quick exploration** (`/explore/quick`): ~$0.03+ per run, 1-2 minutes (2 agents)

**Required:** Set `ANTHROPIC_API_KEY` in `.env` before using these endpoints.

## Endpoints

### POST /api/swarm/explore

Run comprehensive threat modeling analysis using all enabled personas.

**Request:**
```json
{
  "asset_graph": {
    "assets": [
      {
        "id": "aws_instance.web",
        "name": "web",
        "type": "compute.vm",
        "cloud": "aws",
        "service": "EC2",
        "properties": {
          "internet_facing": true,
          "ports": [80, 443]
        },
        "data_sensitivity": "medium",
        "trust_boundary": "internet"
      }
    ],
    "relationships": [
      {
        "source": "aws_instance.web",
        "target": "aws_s3_bucket.data",
        "type": "data_flow",
        "properties": {"direction": "read"}
      }
    ],
    "trust_boundaries": [
      {
        "id": "boundary_internet",
        "name": "Internet Facing",
        "assets": ["aws_instance.web"],
        "exposure": "internet"
      }
    ],
    "metadata": {
      "format": "terraform",
      "resource_count": 10
    }
  }
}
```

**Response:**
```json
{
  "status": "ok",
  "paths": [
    {
      "name": "S3 Data Exfiltration via Compromised EC2",
      "steps": [
        {
          "technique_id": "T1078",
          "technique_name": "Valid Accounts",
          "target_asset": "aws_instance.web",
          "description": "Exploit internet-facing EC2 instance using default credentials",
          "prerequisites": "EC2 instance accessible from internet with weak authentication",
          "outcome": "Initial access to EC2 instance with shell access"
        },
        {
          "technique_id": "T1552.005",
          "technique_name": "Cloud Instance Metadata API",
          "target_asset": "aws_instance.web",
          "description": "Query EC2 metadata service to retrieve IAM role credentials",
          "prerequisites": "EC2 instance has IAM role attached",
          "outcome": "Temporary AWS credentials with EC2 instance's permissions"
        },
        {
          "technique_id": "T1530",
          "technique_name": "Data from Cloud Storage",
          "target_asset": "aws_s3_bucket.data",
          "description": "Use stolen IAM credentials to access S3 bucket and download data",
          "prerequisites": "IAM role has s3:GetObject permissions",
          "outcome": "Sensitive data exfiltrated from S3 bucket"
        }
      ],
      "impact_type": "confidentiality",
      "difficulty": "medium",
      "threat_actor": "APT29 (Cozy Bear)"
    },
    {
      "name": "Lambda Function Privilege Escalation",
      "steps": [
        {
          "technique_id": "T1190",
          "technique_name": "Exploit Public-Facing Application",
          "target_asset": "aws_api_gateway.api",
          "description": "Exploit API Gateway endpoint vulnerability",
          "prerequisites": "Unpatched API endpoint",
          "outcome": "Access to backend Lambda function"
        },
        {
          "technique_id": "T1098.001",
          "technique_name": "Additional Cloud Roles",
          "target_asset": "aws_iam_role.lambda_role",
          "description": "Exploit overly permissive IAM role to create new admin user",
          "prerequisites": "Lambda role has iam:CreateUser permissions",
          "outcome": "New admin account created"
        }
      ],
      "impact_type": "integrity",
      "difficulty": "high",
      "threat_actor": "Scattered Spider"
    }
  ],
  "agent_count": 13,
  "total_paths": 47,
  "execution_time_seconds": 234.56,
  "threat_intel_items": 20
}
```

**Error Response:**
```json
{
  "status": "error",
  "paths": [],
  "agent_count": 0,
  "total_paths": 0,
  "execution_time_seconds": 12.34,
  "threat_intel_items": 0,
  "error": "Error message here"
}
```

**Process:**
1. Fetches top 20 threat intelligence items by citation score
2. Builds threat context string from CVEs, incidents, TTPs, and news
3. Converts asset graph to JSON string
4. Loads all enabled personas from PersonaRegistry
5. Builds CrewAI crew with Claude Sonnet 4
6. Each agent analyzes infrastructure and generates attack paths
7. Parses JSON output from each agent
8. Combines all attack paths into single response

**Typical Execution Time:** 3-5 minutes with 13 agents

---

### POST /api/swarm/explore/quick

Run quick threat modeling analysis using only 2 personas for faster testing.

**Request:** Same as `/explore` endpoint

**Response:** Same format as `/explore` endpoint

**Personas Used:**
- `apt29_cozy_bear` - Nation-state espionage specialist
- `scattered_spider` - Social engineering and identity specialist

**Process:**
1. Temporarily disables all personas
2. Enables only APT29 and Scattered Spider
3. Runs analysis with 2 agents
4. Restores original persona states

**Typical Execution Time:** 1-2 minutes with 2 agents

**Use Cases:**
- Testing infrastructure changes quickly
- Rapid prototyping and iteration
- Development and debugging
- Cost-conscious analysis

---

## Attack Path Schema

Each attack path in the response follows this structure:

```typescript
{
  name: string;                    // Descriptive attack path name
  steps: Array<{
    technique_id: string;          // MITRE ATT&CK ID (e.g., "T1078")
    technique_name: string;        // MITRE ATT&CK technique name
    target_asset: string;          // Asset ID from the graph
    description: string;           // What the attacker does
    prerequisites: string;         // What's needed for this step
    outcome: string;              // Result of this step
  }>;
  impact_type: "confidentiality" | "integrity" | "availability";
  difficulty: "low" | "medium" | "high";
  threat_actor: string;           // Persona display name
}
```

## Threat Intelligence Context

The exploration endpoints automatically incorporate threat intelligence:

**Sources:**
- Recent CVEs with high citation scores
- Security incidents from threat feeds
- Active MITRE ATT&CK TTPs
- Latest security news

**Format:**
```
Recent CVEs: CVE-2024-12345 affecting AWS ECS... |
Recent incidents: MGM Resorts breach, Caesars Entertainment attack |
Active TTPs: T1078, T1530, T1552.005, T1098.001 |
Security news: New APT29 campaign targeting cloud infrastructure
```

This context is provided to each agent to inform their analysis with current threat landscape.

## Example Usage

### Full Exploration with curl

```bash
# Parse infrastructure
curl -X POST http://localhost:8000/api/iac/upload \
  -F "file=@infrastructure.tf" \
  -o asset_graph.json

# Run exploration
curl -X POST http://localhost:8000/api/swarm/explore \
  -H "Content-Type: application/json" \
  -d @asset_graph.json \
  -o attack_paths.json

# Results
cat attack_paths.json | jq '.total_paths'
cat attack_paths.json | jq '.paths[0].name'
```

### Quick Exploration with Python

```python
import requests
import json

# Get asset graph from IaC parser
with open("infrastructure.tf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/iac/upload",
        files={"file": f}
    )
    asset_graph = response.json()

# Run quick exploration
response = requests.post(
    "http://localhost:8000/api/swarm/explore/quick",
    json={"asset_graph": asset_graph}
)

result = response.json()

print(f"Status: {result['status']}")
print(f"Found {result['total_paths']} attack paths in {result['execution_time_seconds']}s")

for path in result["paths"]:
    print(f"\n{path['name']} ({path['threat_actor']})")
    print(f"  Impact: {path['impact_type']}")
    print(f"  Difficulty: {path['difficulty']}")
    print(f"  Steps: {len(path['steps'])}")

    for step in path["steps"]:
        print(f"    {step['technique_id']}: {step['description']}")
```

### Filter by Threat Actor

```python
# Get only APT29 attack paths
apt29_paths = [
    path for path in result["paths"]
    if "APT29" in path["threat_actor"]
]

print(f"APT29 found {len(apt29_paths)} attack paths")
```

### Find Critical Paths

```python
# Get high-difficulty paths affecting confidentiality
critical_paths = [
    path for path in result["paths"]
    if path["difficulty"] == "high" and path["impact_type"] == "confidentiality"
]

print(f"Found {len(critical_paths)} critical confidentiality attack paths")
```

## Performance Considerations

### Cost Optimization

**Use Quick Mode When:**
- Testing infrastructure changes
- Developing/debugging
- Cost is a concern
- Speed is prioritized over coverage

**Use Full Mode When:**
- Comprehensive assessment needed
- Preparing for production deployment
- Multiple threat perspectives required
- Budget allows for thorough analysis

### Caching Strategy

**Currently Not Implemented:**
- Prompt caching would reduce costs by ~50%
- Asset graph is identical for all agents
- Future enhancement to enable Anthropic prompt caching

### Parallel Processing

**Current:** Sequential (Process.sequential)
- Reliable and predictable
- Each agent runs one after another
- Total time = sum of agent times

**Future:** Parallel (Process.parallel)
- Faster overall execution
- Agents run concurrently
- Requires robust error handling

## Error Handling

The endpoints handle various error scenarios:

1. **No Enabled Personas:**
   - Fallback: Enables 2 default personas automatically
   - Continues with analysis

2. **LLM Timeout/Error:**
   - Returns error response with details
   - Execution time still recorded

3. **Invalid JSON from Agent:**
   - Logs error for that agent
   - Continues with other agents
   - Returns partial results

4. **Threat Intel Fetch Failure:**
   - Uses fallback message
   - Analysis continues without intel context

5. **Quick Mode State Restoration:**
   - Always restores original persona states
   - Even on error or exception

## Next Steps

1. **Frontend Integration:**
   - Attack path visualization
   - Real-time progress updates (websockets)
   - Interactive filtering and sorting

2. **Result Storage:**
   - Database persistence
   - Historical comparison
   - Trend analysis

3. **Enhancements:**
   - Attack path deduplication
   - Severity/likelihood scoring
   - Mitigation recommendations
   - Export to STRIDE/attack trees

4. **Optimization:**
   - Enable parallel processing
   - Implement prompt caching
   - Persona selection before run

## API Integration

The exploration endpoints integrate with other APIs:

```
IaC Parser → Exploration → Threat Modeling Report
    ↓            ↓              ↓
Upload File → Generate Paths → Visualize/Export
```

**Workflow:**
1. Upload IaC file via `/api/iac/upload`
2. Get asset graph JSON
3. Run exploration via `/api/swarm/explore`
4. Display/export attack paths

## Summary

The Swarm Exploration API is **production-ready** for generating detailed, MITRE ATT&CK-mapped attack paths from multiple threat actor perspectives. Use the quick endpoint for testing and the full endpoint for comprehensive analysis.

**Key Features:**
- ✓ Multi-agent threat modeling
- ✓ MITRE ATT&CK technique mapping
- ✓ Structured JSON output
- ✓ Threat intelligence integration
- ✓ Quick mode for testing
- ✓ Comprehensive error handling
