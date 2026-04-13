# Swarm Threat Modeling - Agent Personas

## Overview

The Swarm Threat Modeling Engine uses a **dynamic persona registry** that allows you to enable, disable, add, and customize threat actor personas at runtime. Each persona represents a specific threat actor group (like APT29 or Lazarus) or a threat archetype (like Insider Threat or Cloud-Native Attacker).

When you run a threat modeling analysis, the system dynamically builds a multi-agent crew from **only the enabled personas**, ensuring your analysis reflects the threat landscape you care about.

## Default Personas

The system ships with 13 default personas, all marked as **protected** (cannot be deleted, but can be disabled).

### Real-World Threat Actor Personas (5)

These personas emulate documented, real-world threat actor groups:

1. **APT29 (Cozy Bear)** - `apt29_cozy_bear`
   - Category: Nation-State Espionage
   - Known for: SolarWinds supply chain compromise, OAuth token abuse, cloud intrusions
   - Focus: Long-term persistent access, credential theft, supply chain attacks
   - TTPs: T1195, T1566.002, T1078.004, T1550.001, T1098, T1530

2. **Lazarus Group** - `lazarus_group`
   - Category: Financial Crime & Destructive Operations
   - Known for: Bangladesh Bank SWIFT heist, WannaCry, cryptocurrency theft
   - Focus: Financial systems, destructive wipers, cryptocurrency exchanges
   - TTPs: T1189, T1485, T1486, T1565, T1071, T1020

3. **Volt Typhoon** - `volt_typhoon`
   - Category: Critical Infrastructure Pre-positioning
   - Known for: Living-off-the-land techniques, minimal malware footprint
   - Focus: Network infrastructure, management planes, credential harvesting
   - TTPs: T1133, T1078, T1003, T1018, T1046, T1570

4. **Scattered Spider** - `scattered_spider`
   - Category: Social Engineering & Identity
   - Known for: MGM/Caesars attacks, SIM swapping, MFA fatigue, help desk social engineering
   - Focus: Identity systems, SSO, MFA bypass, cloud console access
   - TTPs: T1566, T1621, T1078.004, T1556, T1098.001, T1538

5. **FIN7** - `fin7`
   - Category: E-Commerce & Payment Systems
   - Known for: $1B+ stolen from banks/retail, POS malware, payment card theft
   - Focus: Web applications, payment processing, PII/PCI data stores
   - TTPs: T1190, T1059.001, T1055, T1041, T1567, T1505.003

### Archetype-Based Personas (8)

These personas represent generalized threat patterns and attack styles:

1. **Nation-State APT (Generic)** - `nation_state_apt`
   - Patient, sophisticated operator with zero-days and supply chain access
   - Focus: Complex multi-stage attacks, maximum persistence, intelligence collection

2. **Opportunistic Attacker** - `opportunistic_attacker`
   - Semi-skilled attacker using public tools and known CVEs
   - Focus: Low-hanging fruit, default credentials, public misconfigurations

3. **Insider Threat** - `insider_threat`
   - Malicious employee or contractor with legitimate access
   - Focus: Privilege escalation from standard permissions, data exfiltration

4. **Cloud-Native Attacker** - `cloud_native_attacker`
   - Specialist in AWS IAM exploitation and cloud-specific attacks
   - Focus: IAM misconfigurations, IMDS abuse, serverless exploitation

5. **Supply Chain Attacker** - `supply_chain_attacker`
   - Attacks through dependencies, CI/CD pipelines, third-party integrations
   - Focus: Compromised upstream components, build pipeline injection

6. **Social Engineering Hybrid** - `social_engineering_hybrid`
   - Starts with phished credentials, maps blast radius
   - Focus: What can be accessed with stolen employee credentials

7. **Lateral Movement Specialist** - `lateral_movement_specialist`
   - Maps all reachable assets from any foothold
   - Focus: Network reachability, credential access, pivot paths

8. **Data Exfiltration Optimizer** - `data_exfiltration_optimizer`
   - Works backward from crown jewels to find exfiltration paths
   - Focus: Shortest, stealthiest paths to extract sensitive data

## API Endpoints

### GET /api/swarm/personas

Get all personas with their configuration.

**Response:**
```json
{
  "apt29_cozy_bear": {
    "display_name": "APT29 (Cozy Bear)",
    "category": "threat_actor",
    "protected": true,
    "enabled": true,
    "role": "Nation-State Espionage Specialist",
    "goal": "Identify attack paths focused on...",
    "backstory": "You are emulating APT29...",
    "ttp_focus": ["T1195", "T1566.002", ...]
  },
  ...
}
```

### GET /api/swarm/personas/enabled

Get only enabled personas (used for crew building).

**Response:** Same format as `/personas` but filtered to `enabled: true`

### GET /api/swarm/personas/{name}

Get a single persona by name.

**Example:** `GET /api/swarm/personas/apt29_cozy_bear`

### POST /api/swarm/personas?name={name}

Create a new custom persona.

**Request Body:**
```json
{
  "display_name": "Ransomware Operator",
  "category": "threat_actor",
  "role": "Ransomware Deployment and Extortion Specialist",
  "goal": "Identify attack paths for ransomware deployment...",
  "backstory": "You are a sophisticated ransomware operator...",
  "ttp_focus": ["T1486", "T1490", "T1489", "T1491"]
}
```

**Response:**
```json
{
  "status": "ok",
  "persona": "ransomware_operator",
  "message": "Created persona 'ransomware_operator'"
}
```

**Notes:**
- Custom personas are automatically marked `protected: false`
- Custom personas can be modified or deleted

### PUT /api/swarm/personas/{name}/toggle

Enable or disable a persona.

**Request Body:**
```json
{
  "enabled": false
}
```

**Example:**
```bash
# Disable FIN7
curl -X PUT http://localhost:8000/api/swarm/personas/fin7/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Re-enable FIN7
curl -X PUT http://localhost:8000/api/swarm/personas/fin7/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### PUT /api/swarm/personas/{name}

Partially update a persona's fields.

**Request Body:**
```json
{
  "goal": "Updated goal statement",
  "ttp_focus": ["T1190", "T1486"]
}
```

**Notes:**
- Only provided fields are updated
- `protected` status cannot be changed
- Works for both custom and protected personas

### DELETE /api/swarm/personas/{name}

Delete a custom persona.

**Response (Success):**
```json
{
  "status": "ok",
  "persona": "custom_persona",
  "message": "Deleted persona 'custom_persona'"
}
```

**Response (Protected Persona - 403 Forbidden):**
```json
{
  "detail": "Cannot delete protected persona 'apt29_cozy_bear'. Protected personas can be disabled but not deleted."
}
```

## Dynamic Crew Building

The `build_exploration_crew()` function in `app/swarm/crews.py` dynamically constructs the threat modeling crew from **enabled personas only**.

### How It Works

1. **Load Enabled Personas:**
   ```python
   from app.swarm import PersonaRegistry

   registry = PersonaRegistry()
   enabled_personas = registry.get_enabled()
   ```

2. **Build Agents:**
   For each enabled persona, create a CrewAI agent with the persona's `role`, `goal`, and `backstory`.

3. **Create Tasks:**
   Each agent receives the same infrastructure analysis task but applies their unique persona perspective.

4. **Execute Crew:**
   The multi-agent crew analyzes the infrastructure from all enabled perspectives simultaneously.

### Example Usage

```python
from app.swarm.crews import run_threat_modeling_swarm

# Parse infrastructure
asset_graph = terraform_parser.parse(tf_content)

# Run swarm analysis
result = run_threat_modeling_swarm(
    asset_graph=asset_graph,
    threat_intel_context="Recent APT29 activity targeting cloud environments"
)

print(f"Status: {result['status']}")
print(f"Agents used: {result['agents_used']}")
print(f"Findings: {result['result']}")
```

## Configuration File

Personas are stored in `app/swarm/agents/personas.yaml`. This file is auto-generated on first run if it doesn't exist.

**File Structure:**
```yaml
persona_name:
  display_name: Human-Readable Name
  category: threat_actor | archetype
  protected: true | false
  enabled: true | false
  role: Agent role description
  goal: What the agent is trying to accomplish
  backstory: Detailed persona description
  ttp_focus:
    - T1195
    - T1566.002
    - ...
```

**Protected Personas:**
- `protected: true` - Cannot be deleted (but can be disabled)
- `protected: false` - Custom personas, can be deleted

## Use Cases

### 1. Focus on Specific Threats

If you're only concerned about insider threats and cloud attacks:

```bash
# Disable all personas
for persona in apt29_cozy_bear lazarus_group volt_typhoon scattered_spider fin7 \
                nation_state_apt opportunistic_attacker supply_chain_attacker \
                social_engineering_hybrid lateral_movement_specialist data_exfiltration_optimizer; do
  curl -X PUT "http://localhost:8000/api/swarm/personas/$persona/toggle" \
    -H "Content-Type: application/json" \
    -d '{"enabled": false}'
done

# Enable only relevant personas
curl -X PUT http://localhost:8000/api/swarm/personas/insider_threat/toggle \
  -d '{"enabled": true}'
curl -X PUT http://localhost:8000/api/swarm/personas/cloud_native_attacker/toggle \
  -d '{"enabled": true}'
```

### 2. Add Industry-Specific Persona

```bash
curl -X POST "http://localhost:8000/api/swarm/personas?name=healthcare_attacker" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Healthcare Data Theft Specialist",
    "category": "archetype",
    "role": "Healthcare PHI/PII Exfiltration Specialist",
    "goal": "Identify attack paths to HIPAA-protected data, EHR systems, and medical device networks",
    "backstory": "You specialize in attacking healthcare infrastructure. You target Electronic Health Records (EHR) systems, PACS (medical imaging), medical IoT devices, and billing systems containing PHI/PII. You understand HIPAA compliance requirements and look for gaps in BAAs (Business Associate Agreements) with third-party vendors.",
    "ttp_focus": ["T1530", "T1567", "T1020", "T1041", "T1213"]
  }'
```

### 3. Adjust Persona Focus

```bash
# Update Scattered Spider to focus more on MFA bypass
curl -X PUT http://localhost:8000/api/swarm/personas/scattered_spider \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Identify MFA bypass techniques, push bombing vulnerabilities, and identity provider weaknesses",
    "ttp_focus": ["T1621", "T1556", "T1078.004", "T1528", "T1539"]
  }'
```

## Integration with Threat Modeling

The persona system integrates with the IaC parser and threat intelligence feeds:

```python
# 1. Upload infrastructure
with open("infrastructure.tf", "rb") as f:
    response = requests.post("http://localhost:8000/api/iac/upload", files={"file": f})
    asset_graph = response.json()

# 2. Get latest threat intelligence
response = requests.get("http://localhost:8000/api/intel/items?category=ttp&limit=10")
threat_intel = response.json()

# Build context from threat intel
threat_context = "\n".join([
    f"- {item['title']}: {item['summary']}"
    for item in threat_intel
])

# 3. Configure personas
requests.put("http://localhost:8000/api/swarm/personas/apt29_cozy_bear/toggle",
             json={"enabled": True})

# 4. Run threat modeling
result = run_threat_modeling_swarm(asset_graph, threat_context)
```

## Benefits

1. **Adaptable:** Enable/disable personas based on current threat landscape
2. **Customizable:** Add industry-specific or organization-specific threat actors
3. **Persistent:** Changes are saved to YAML and survive restarts
4. **Protected Defaults:** Core personas cannot be accidentally deleted
5. **Dynamic:** Crew composition changes instantly when personas are toggled

## Next Steps

- Frontend UI for managing personas visually
- Persona effectiveness metrics (which personas find the most issues)
- Persona templates for different industries (finance, healthcare, government)
- Integration with MITRE ATT&CK for automatic TTP recommendations
