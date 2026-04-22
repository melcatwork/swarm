# Dynamic Persona Reasoning Update

**Date:** 2026-04-20  
**Status:** ✅ COMPLETED

## Overview

Replaced hard-coded `iac_signal_to_attack_chain` approach with open-ended `security_reasoning_approach` field for all threat actor personas. This enables personas to dynamically identify ANY misconfiguration or vulnerability in IaC through security reasoning, not just pre-defined signals.

---

## TASK 1: Updated personas.yaml ✅

### Added `security_reasoning_approach` Field

Added a new `security_reasoning_approach` field to 12 personas in `backend/app/swarm/agents/personas.yaml`. Each persona now has tailored reasoning instructions structured with:

#### Structure Components:
1. **Resource examination questions** — Open-ended questions this persona asks about every resource
2. **Relationship analysis** — How this persona reasons about connections between resources
3. **Exploitation mindset** — The attacker's decision criteria and priorities
4. **Detection awareness** — What this persona knows about logging and monitoring gaps

### Personas Updated:

1. **apt29_cozy_bear** — Nation-state espionage with focus on token theft, federation, supply chain
2. **lazarus_group** — Financial crime with dual theft/destruction objectives
3. **volt_typhoon** — Critical infrastructure pre-positioning using living-off-the-land
4. **scattered_spider** — Identity system exploitation and social engineering
5. **fin7** — Application-layer attacks targeting payment systems
6. **opportunistic_attacker** — Low-hanging fruit exploitation with public tools
7. **insider_threat** — Legitimate access abuse and privilege escalation
8. **cloud_native_attacker** — IAM misconfiguration and cloud-specific exploitation
9. **supply_chain_attacker** — CI/CD and dependency compromise
10. **data_exfiltration_optimizer** — Reverse engineering from crown jewels to exfiltration paths
11. **lateral_movement_specialist** — Post-compromise reachability mapping
12. **social_engineering_hybrid** — Phished credential blast radius analysis

### Example Security Reasoning Approach:

```yaml
security_reasoning_approach: |
  Resource examination questions: Does this resource have an IAM role? What does that role permit? 
  Can those permissions be obtained without direct access to this resource?

  Relationship analysis: When I see an EC2 instance with an IAM role that can write to an S3 bucket, 
  I ask: what happens if this instance is compromised?

  Exploitation mindset: I prioritise paths that use legitimate cloud APIs over paths that require 
  OS-level exploitation, because cloud API calls blend into normal traffic and bypass most 
  host-based detection.

  Detection awareness: CloudTrail logs API calls but defenders rarely alert on legitimate API 
  patterns from trusted roles. I avoid GuardDuty triggers by using valid credentials.
```

---

## TASK 2: Updated Prompt Builders ✅

### Modified Files:

#### 1. `backend/app/swarm/swarm_exploration.py`

**Function:** `build_swarm_aware_prompt()` (lines 49-122)

**Changes:**
- Extracts `security_reasoning_approach` from persona config
- Injects reasoning approach into prompt with clear section headers
- Adds instruction to apply reasoning dynamically to full IaC
- Removes dependency on pre-detected signal lists

**New Prompt Structure:**
```python
full_backstory = (
    f"{persona['backstory']}\n\n"
    f"=== YOUR SECURITY REASONING APPROACH ===\n"
    f"{security_reasoning}\n\n"
    f"=== INFRASTRUCTURE TO ANALYZE ===\n"
    f"Apply your security reasoning approach to identify EVERY misconfiguration, "
    f"vulnerability, and attack-enabling condition you can find. Do not limit yourself "
    f"to well-known conditions. Use your full security knowledge to discover what specific "
    f"attributes or relationships make resources dangerous and how you would exploit them.\n\n"
    f"{asset_graph_summary}\n\n"
    f"{swarm_intel}"
)
```

#### 2. `backend/app/swarm/crews.py`

**Function:** `build_exploration_crew()` (lines 140-305)

**Changes:**
- Extracts `security_reasoning_approach` from persona config
- Injects reasoning approach into agent backstory
- Adds open-ended reasoning instructions
- Passes full serialized IaC to agents

**New Prompt Structure:**
```python
full_backstory = (
    f"{persona_config['backstory']}\n\n"
    f"=== YOUR SECURITY REASONING APPROACH ===\n"
    f"{security_reasoning}\n\n"
    f"=== INFRASTRUCTURE TO ANALYZE ===\n"
    f"Apply your security reasoning approach to the infrastructure below. Identify every "
    f"misconfiguration, vulnerability, and attack-enabling condition you can find—not just "
    f"the well-known ones. For each finding, explain what specific attribute or relationship "
    f"makes it dangerous and how you would exploit it. Do not limit yourself to conditions "
    f"you have been pre-briefed on. Use your full security knowledge.\n\n"
    f"{asset_graph_json}\n\n"
    f"Current threat intelligence context:\n"
    f"{threat_intel_context if threat_intel_context else 'No specific threat intelligence provided.'}"
)
```

### All Run Modes Covered:

✅ **Full Swarm** (`POST /api/swarm/run`) — Uses `build_exploration_crew()`  
✅ **Quick Run** (`POST /api/swarm/run/quick`) — Uses `build_exploration_crew()`  
✅ **Single Agent** (`POST /api/swarm/run/single`) — Uses `build_exploration_crew()`  
✅ **Stigmergic Swarm** (`POST /api/swarm/run/stigmergic`) — Uses `build_swarm_aware_prompt()`

All four run types now use dynamic reasoning instead of hard-coded signal injection.

---

## TASK 3: Verified No Hard-Coded Signal Injection ✅

### Search Results:

**No matches found for:**
- `IMDS_V1_ENABLED`
- `IAM_S3_WILDCARD`
- `iac_signal_to_attack_chain`
- Specific signal name patterns

**Confirmed:**
- ✅ No hard-coded signal lists exist in `backend/app/swarm/`
- ✅ No signal injection logic in prompt builders
- ✅ No pre-detected condition lists passed to agents
- ✅ LLMs now discover conditions through reasoning, not through being told

**Only match:** Text in updated prompts saying "Do not limit yourself to conditions you have been pre-briefed on" — this is an instruction telling the LLM NOT to rely on pre-briefing, which is the desired behavior.

---

## Frontend Impact

### No Frontend Files Modified ✅

All changes are backend-only. Frontend continues to work without modification:
- API endpoints unchanged
- Request/response schemas unchanged
- No UI updates required

---

## Benefits

### 1. **Expanded Discovery Capabilities**
- Personas can now identify ANY vulnerability, not just 5 pre-defined signals
- Open-ended reasoning enables discovery of novel attack patterns
- LLMs apply full security knowledge to IaC analysis

### 2. **Persona Differentiation**
- Each persona's unique reasoning approach creates distinct analysis perspectives
- APT29 focuses on federation and tokens; Lazarus on financial systems; Volt Typhoon on LOLBAS
- Emergent insights from diverse reasoning approaches

### 3. **Maintainability**
- No need to maintain hard-coded signal mappings
- Adding new personas only requires defining their reasoning approach
- Infrastructure changes don't require updating signal lists

### 4. **Authenticity**
- Reasoning approaches match real-world threat actor methodologies
- Based on documented TTPs and operational patterns
- Reflects actual attacker decision-making processes

---

## Migration Path

### Before:
```yaml
apt29_cozy_bear:
  iac_signal_to_attack_chain:
    IMDS_V1_ENABLED: "Harvest IAM credentials from metadata service"
    IAM_S3_WILDCARD: "Abuse overly permissive S3 access"
```

Agents were told: "You have been pre-briefed on these 5 specific conditions."

### After:
```yaml
apt29_cozy_bear:
  security_reasoning_approach: |
    Resource examination questions: Does this resource have an IAM role? 
    What federation configurations exist? What identity stores are reachable?
    
    Exploitation mindset: I prioritize token theft over malware deployment...
```

Agents are instructed: "Apply your reasoning to discover ALL dangerous conditions."

---

## Testing Recommendations

1. **Baseline Comparison:**
   - Run same IaC file with old version (if available) vs new version
   - Compare number and diversity of discovered vulnerabilities
   - Verify new version finds previously hard-coded conditions PLUS new ones

2. **Persona Differentiation:**
   - Run single-agent mode with different personas on same IaC
   - Verify each persona produces distinct attack paths reflecting their reasoning approach
   - Example: Opportunistic attacker should find public S3 buckets, APT29 should find federation issues

3. **Novel Discovery Validation:**
   - Use IaC with intentionally obscure misconfigurations not in original 5 signals
   - Verify personas discover these through reasoning
   - Example: IMDSv2 with permissive role, Lambda with broad VPC access

4. **Stigmergic Coordination:**
   - Run stigmergic swarm to verify shared graph still functions
   - Verify personas reinforce each other's findings
   - Check emergent insights from collective reasoning

---

## Files Modified

```
backend/app/swarm/agents/personas.yaml           — Added security_reasoning_approach to 12 personas
backend/app/swarm/swarm_exploration.py           — Updated build_swarm_aware_prompt()
backend/app/swarm/crews.py                       — Updated build_exploration_crew()
backend/DYNAMIC_PERSONA_REASONING_UPDATE.md      — This documentation
```

**Total:** 3 code files modified, 1 documentation file created  
**Lines Changed:** ~1,200 lines added (persona reasoning approaches + prompt updates)

---

## Verification Commands

```bash
# Verify security_reasoning_approach field exists for all 12 personas
grep -A 5 "security_reasoning_approach" backend/app/swarm/agents/personas.yaml | grep -c "Resource examination"

# Expected output: 12

# Verify prompt builders use the new field
grep "security_reasoning_approach" backend/app/swarm/crews.py backend/app/swarm/swarm_exploration.py

# Expected: 2 matches (one in each file)

# Verify no hard-coded signals remain
grep -r "IMDS_V1_ENABLED\|IAM_S3_WILDCARD\|iac_signal_to_attack_chain" backend/app/swarm/

# Expected: No matches
```

---

## Backward Compatibility

✅ **Fully Backward Compatible**

- Old personas without `security_reasoning_approach` gracefully degrade (field is optional with `.get()`)
- Existing API endpoints unchanged
- Frontend requires no updates
- Archived run data structure unchanged
- No database migrations needed

---

## Conclusion

Successfully replaced hard-coded signal-based approach with dynamic security reasoning instructions. All 12 personas now use open-ended reasoning to discover vulnerabilities, enabling broader coverage and more authentic threat actor emulation.

**Status:** ✅ READY FOR TESTING
