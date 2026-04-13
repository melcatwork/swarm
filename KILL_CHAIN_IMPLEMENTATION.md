# Kill Chain Attack Path Implementation Summary

## Overview

This document summarizes the comprehensive restructuring of attack path generation and display to follow the cyber kill chain methodology. Attack paths now represent end-to-end multi-stage operations with clear objectives, structured phases, and actionable mitigations.

---

## Backend Changes

### 1. New Models (`backend/app/swarm/models.py`)

Created structured Pydantic models for kill chain attack paths:

#### **MitigationDetail**
```python
- mitigation_id: str  # ATT&CK ID (M1048) or custom (CUSTOM-001)
- mitigation_name: str  # Short name
- description: str  # 2-3 sentences
- aws_service_action: str  # Specific AWS implementation
```

#### **AttackStep**
```python
- step_number: int  # 1-5
- kill_chain_phase: str  # Reconnaissance, Initial Access, Execution & Persistence, etc.
- technique_id: str  # MITRE ATT&CK T-number
- technique_name: str  # Human-readable name
- target_asset: str  # Specific asset from graph
- action_description: str  # What attacker does
- outcome: str  # What attacker gains
- mitigation: MitigationDetail  # Inline mitigation
```

#### **AttackPath**
```python
- id: str
- name: str  # Descriptive scenario name
- objective: str  # Attacker's end goal
- threat_actor: str  # Persona name
- impact_type: str  # confidentiality/integrity/availability
- difficulty: str  # low/medium/high
- steps: List[AttackStep]  # 3-5 steps
- composite_score: float  # Evaluation score
- confidence: str  # high/medium/low
- challenged: bool
- challenge_resolution: str
- validation_notes: str
- evaluation: dict
```

### 2. Updated Exploration Crew Prompts (`backend/app/swarm/crews.py`)

**All exploration agents** now receive comprehensive kill chain instructions:

- **Must generate 3-5 steps** following the cyber kill chain
- **Each step must have:**
  - Specific kill chain phase
  - Valid MITRE ATT&CK technique ID
  - Target asset from the infrastructure graph
  - Detailed action description (2-3 sentences)
  - Outcome that enables the next step
  - Inline mitigation with AWS service action

**Kill Chain Phases:**
1. **Reconnaissance** or **Initial Access**
2. **Execution & Persistence**
3. **Lateral Movement & Privilege Escalation**
4. **Objective (Exfiltration/Impact)**
5. **Covering Tracks** (optional)

### 3. Updated Evaluation Crew Prompts

**Feasibility Scorer:**
- Evaluates whether each kill chain step logically follows from the previous
- Checks if outcomes actually enable next steps

**Detection Scorer:**
- Assesses detection likelihood for each kill chain step
- References CloudTrail, GuardDuty, VPC Flow Logs

**Impact Scorer:**
- Focuses on the final objective step
- Evaluates real business impact of achieving the goal

**Novelty Scorer:**
- Evaluates if the kill chain represents a creative path
- Penalizes well-known patterns

**Coherence Checker:**
- Validates kill chain flow logic
- Checks if each step's outcome provides prerequisites for next step

### 4. Updated Adversarial Crew Prompts

**Red Team:**
- Identifies kill chain gaps in coverage
- Looks for assets never targeted in any kill chain step
- Proposes additional 3-5 step kill chains

**Blue Team:**
- Challenges specific kill chain steps
- References actual architectural controls (security groups, IAM, encryption)
- Identifies which kill chain phase would be blocked

**Arbitrator:**
- Unchanged, validates and produces final paths

### 5. Robust Parsing with Normalization (`parse_exploration_results`)

Handles field name variations:
- `technique_id` / `techniqueId` / `attack_technique`
- `kill_chain_phase` / `killChainPhase` / `phase`
- `action_description` / `description` / `action`
- Auto-infers `step_number` from array position if missing
- Auto-infers `kill_chain_phase` from step number if missing
- Validates technique ID format: `T\d{4}(\.\d{3})?`
- Limits to maximum 5 steps
- Requires minimum 3 steps

### 6. Enhanced Mitigation Mapper (`backend/app/swarm/mitigations.py`)

**Added 24 AWS-Specific Technique Mappings:**
- T1078, T1078.004 (Valid Accounts / Cloud Accounts)
- T1190 (Exploit Public-Facing Application)
- T1133 (External Remote Services)
- T1098, T1098.001 (Account Manipulation)
- T1526 (Cloud Service Discovery)
- T1580 (Cloud Infrastructure Discovery)
- T1530 (Data from Cloud Storage)
- T1562.001, T1562.008 (Impair Defenses)
- T1552.005 (Cloud Instance Metadata API)
- T1213.003 (Code Repositories)
- T1537, T1567.002 (Data Transfer/Exfiltration)
- T1486 (Data Encrypted for Impact)
- T1485 (Data Destruction)
- T1496 (Resource Hijacking)
- T1538 (Cloud Service Dashboard)
- T1550.001 (Application Access Token)
- T1136.003 (Create Cloud Account)
- T1071 (Application Layer Protocol)
- T1105 (Ingress Tool Transfer)

Each mapping includes:
- Mitigation name
- Description (2-3 sentences)
- **aws_service_action**: Specific AWS implementation

**Mitigation Logic:**
1. If agent provided inline mitigation → enrich with AWS action if missing
2. If no inline mitigation → look up from STIX data
3. Prefer AWS-specific mitigations over generic STIX mitigations
4. Add AWS service action to all mitigations
5. Fallback to generic mitigation if nothing found

---

## Frontend Changes

### 1. New Kill Chain Visualization (`frontend/src/pages/ThreatModelPage.jsx`)

**Added Helper Functions:**
- `getKillChainPhaseColor()` - Color coding by phase
- `getImpactTypeColor()` - Impact type badges (blue/orange/red)
- `formatTechniqueUrl()` - Convert T1566.001 to MITRE URL format
- `copyMitigationsToClipboard()` - Copy all mitigations as formatted text

**New Attack Path Card Structure:**

#### a) **Header Section**
- Attack path name (bold, prominent)
- **Objective callout** (highlighted box with goal statement)
- Badges:
  - Threat actor
  - Impact type (color-coded)
  - Difficulty
  - Challenged status
  - Confidence rating
- **Composite score** displayed as circular indicator (X.X/10)

#### b) **Kill Chain Pipeline**
- **Horizontal/vertical step visualization**
- Each step displayed as a card with:
  - **Phase header** (color-coded by kill chain phase)
  - Step number badge
  - **Clickable ATT&CK technique badge** (links to MITRE)
  - Technique name
  - Target asset (highlighted)
  - Action description (2-3 sentences)
  - **Outcome box** (shows what attacker gains)
- **Arrows between steps** showing progression
- Responsive: stacks vertically on mobile

#### c) **Mitigations Section** (Expandable)
- "Show Mitigations" / "Hide Mitigations" toggle button
- **Copy All Mitigations** button
- For each step:
  - Step number and phase
  - Mitigation ID and name
  - Description
  - **AWS Service Action** in highlighted code block

#### d) **Provenance Footer** (Collapsed `<details>`)
- Validation notes
- Challenge resolution
- **Evaluation scores grid:**
  - Feasibility
  - Detection Difficulty
  - Impact
  - Novelty
  - Coherence

### 2. Kill Chain CSS Styles (`frontend/src/pages/ThreatModelPage.css`)

**Phase Color Scheme:**
- **Reconnaissance**: Gray (#f3f4f6)
- **Initial Access**: Blue (#dbeafe)
- **Execution & Persistence**: Orange (#fed7aa)
- **Lateral Movement & Privilege Escalation**: Purple (#e9d5ff)
- **Objective (Exfiltration/Impact)**: Red (#fecaca)
- **Covering Tracks**: Dark Gray (#e5e7eb)

**Key CSS Classes:**
- `.attack-path-card-v2` - Main card container
- `.path-header-v2` - Header with title, objective, badges
- `.path-objective` - Highlighted objective callout
- `.score-circle` - Circular score indicator
- `.kill-chain-container` - Pipeline container
- `.kill-chain-step` - Individual step card
- `.step-phase-header` - Color-coded phase header
- `.technique-badge` - Clickable ATT&CK link
- `.step-outcome-box` - Outcome highlight
- `.kill-chain-arrow` - Arrow between steps
- `.mitigations-section` - Expandable mitigations
- `.mitigation-row` - Individual mitigation card
- `.aws-action-block` - AWS action code block
- `.provenance-section` - Collapsible details

**Responsive Design:**
- Desktop: horizontal/vertical pipeline
- Mobile: stacked steps, full width
- Touch-friendly toggle buttons

---

## Testing Instructions

### 1. Backend Testing

```bash
cd backend
source .venv/bin/activate

# Test with insider threat agent on ecommerce platform
uvicorn app.main:app --reload
```

### 2. Upload Test File

Use `samples/ecommerce-platform.tf` which has:
- Developer IAM roles with broad S3 access
- Unencrypted RDS database
- IMDSv1 enabled on EC2
- Hardcoded credentials
- Lambda with excessive permissions

### 3. Expected Results

**Attack Path Example:**
```
Name: Developer Workstation to S3 Customer Data Exfiltration
Objective: Exfiltrate customer PII from S3 bucket for financial gain

Step 1 - Initial Access
  T1078.004 - Valid Cloud Accounts
  Target: developer_workstation (EC2)
  Action: Insider uses legitimate developer IAM credentials...
  Outcome: Access to AWS console with developer role
  Mitigation: Enforce MFA, implement permission boundaries

Step 2 - Execution & Persistence
  T1098 - Account Manipulation
  Target: developer_role (IAM)
  Action: Developer reviews IAM permissions and identifies broad S3 access...
  Outcome: Understanding of S3 access capabilities
  Mitigation: Monitor IAM changes with CloudTrail alerts

Step 3 - Lateral Movement & Privilege Escalation
  T1552.005 - Cloud Instance Metadata API
  Target: web_server_1 (EC2)
  Action: Access EC2 metadata service to retrieve additional credentials...
  Outcome: Elevated access to multiple AWS services
  Mitigation: Enforce IMDSv2, restrict metadata service access

Step 4 - Objective (Exfiltration/Impact)
  T1530 - Data from Cloud Storage Object
  Target: customer_data (S3)
  Action: Use AWS CLI to sync entire S3 bucket to local storage...
  Outcome: Complete exfiltration of customer PII
  Mitigation: Enable S3 Block Public Access, use bucket policies

Composite Score: 7.8/10
Confidence: High
```

### 4. Visual Verification Checklist

✅ Each attack path shows clear objective
✅ Steps are color-coded by kill chain phase
✅ ATT&CK technique badges are clickable (open MITRE)
✅ Each step shows target asset
✅ Arrows connect steps showing progression
✅ Mitigations are expandable/collapsible
✅ AWS service actions are in code blocks
✅ Copy mitigations button works
✅ Evaluation scores are in provenance section
✅ Responsive on mobile (steps stack vertically)

---

## Migration Notes

### Backward Compatibility

The system handles both old and new formats:

**Old Format:**
```json
{
  "steps": [{
    "technique_id": "T1078",
    "description": "...",
    "prerequisites": "...",
    "outcome": "..."
  }]
}
```

**New Format:**
```json
{
  "objective": "Exfiltrate data...",
  "steps": [{
    "step_number": 1,
    "kill_chain_phase": "Initial Access",
    "technique_id": "T1078.004",
    "technique_name": "Valid Cloud Accounts",
    "target_asset": "developer_workstation",
    "action_description": "...",
    "outcome": "...",
    "mitigation": {
      "mitigation_id": "M1032",
      "mitigation_name": "Multi-factor Authentication",
      "description": "...",
      "aws_service_action": "Enforce MFA on all IAM users..."
    }
  }]
}
```

The parser normalizes both to the new format.

### Database Schema

No database changes required - attack paths are stored as JSON.

---

## Benefits

### For Security Teams

1. **Clear Attack Narrative** - Each path tells a complete story from initial access to objective
2. **Actionable Mitigations** - AWS-specific actions for each step
3. **Visual Kill Chain** - Immediate understanding of attack progression
4. **Phase-Based Analysis** - Identify which phases need better controls

### For Developers

1. **Structured Data** - Consistent schema for processing
2. **API-Ready** - JSON format for integration
3. **Extensible** - Easy to add new phases or fields
4. **Type-Safe** - Pydantic models with validation

### For Executives

1. **Risk Communication** - Clear objectives and impact statements
2. **Score-Based Prioritization** - Focus on highest-scoring paths
3. **Compliance Mapping** - MITRE ATT&CK technique coverage
4. **Cost Justification** - Specific AWS services to implement

---

## Future Enhancements

### Phase 2 (Potential)

1. **Interactive Graph View** - D3.js network diagram of kill chains
2. **Phase Coverage Heatmap** - Which phases are well/poorly covered
3. **Export to STIX/TAXII** - Share with threat intelligence platforms
4. **Playbook Generation** - Auto-generate detection playbooks per phase
5. **Red Team Simulator** - Execute kill chains in test environments
6. **Cost Estimator** - Calculate AWS cost to implement all mitigations
7. **Compliance Mapper** - Map to NIST CSF, ISO 27001, PCI-DSS controls

---

## Troubleshooting

### Issue: Attack paths have no kill_chain_phase

**Solution:** The parser auto-infers phases from step numbers. Check that steps have valid step_number fields.

### Issue: Mitigations missing aws_service_action

**Solution:** Add technique ID to `AWS_CONTEXTUAL_MITIGATIONS` in `mitigations.py`.

### Issue: Steps not displaying in correct order

**Solution:** Ensure step_number is set correctly (1-5). Parser uses array index as fallback.

### Issue: Frontend shows old card style

**Solution:** Clear browser cache. The new CSS uses `.attack-path-card-v2` class.

### Issue: MITRE ATT&CK links don't work

**Solution:** Check technique_id format (T1234 or T1234.001). URL format is `/techniques/T1234/` or `/techniques/T1234/001/`.

---

## Files Modified

### Backend
- `backend/app/swarm/models.py` ✨ **NEW**
- `backend/app/swarm/crews.py` (updated prompts)
- `backend/app/swarm/mitigations.py` (24 AWS mappings added)

### Frontend
- `frontend/src/pages/ThreatModelPage.jsx` (kill chain visualization)
- `frontend/src/pages/ThreatModelPage.css` (kill chain styles)

### Documentation
- `KILL_CHAIN_IMPLEMENTATION.md` ✨ **NEW**

---

## Credits

Implementation based on:
- **Lockheed Martin Cyber Kill Chain** framework
- **MITRE ATT&CK** knowledge base
- **AWS Security Best Practices** documentation
- **NIST Cybersecurity Framework** guidance

---

## License

Part of the Swarm TM threat modeling tool.
