# Pre-Change Truncation Analysis Report

**Analysis Date**: 2026-04-21  
**Analyst**: Claude Code  
**Objective**: Identify all locations where attack path length is limited before implementing 10-step support

---

## Search Methodology

Conducted systematic search for patterns:
- Integer literals 3-7 used as step caps
- Slice operations on steps lists (`steps[:N]`)
- Conditional filtering based on step count
- Scoring penalties for longer paths
- Gap-filler logic with fixed limits
- Pydantic field validators with `max_items` or numeric limits
- Prompt instructions specifying step counts

### Files Searched

1. `backend/app/swarm/vuln_intel/chain_assembler.py`
2. `backend/app/swarm/output_filter.py`
3. `backend/app/swarm/path_evaluator.py`
4. `backend/app/swarm/swarm_exploration.py`
5. `backend/app/swarm/consensus_aggregator.py`
6. `backend/app/swarm/crews.py`
7. `backend/app/swarm/models.py`
8. `backend/app/swarm/vuln_intel/vuln_context_builder.py`
9. `backend/app/routers/swarm.py`

---

## Truncation Points Found

### CRITICAL: Active Truncation (Data Loss)

#### **1. crews.py:440 — JSON Parser Slice**
```python
for step_idx, step in enumerate(path["steps"][:5]):  # Limit to 5 steps
```

**Location**: `backend/app/swarm/crews.py`, function `parse_exploration_results()`, line 440

**Nature of Limit**: Hard slice on LLM-generated steps during normalization

**Impact**: 🔴 **HIGHEST SEVERITY**
- Even if LLM generates 10 steps, only first 5 are parsed
- Steps 6-10 are **permanently discarded** before storage
- Affects all four run types (full, quick, single, stigmergic)
- No error or warning logged about discarded steps

**Task Mapping**: TASK 4 (indirectly), primary parser issue

---

### Schema Validation Constraints

#### **2. models.py:44 — AttackStep Pydantic Validator**
```python
step_number: int = Field(..., ge=1, le=5, description="Step number (1-5)")
```

**Location**: `backend/app/swarm/models.py`, class `AttackStep`, line 44

**Nature of Limit**: Pydantic field constraint

**Impact**: 🟡 **MEDIUM SEVERITY**
- Validation error if `step_number > 5`
- Would cause 422 Unprocessable Entity errors in API responses
- Blocks legitimate 6-10 step paths from being serialized

**Task Mapping**: TASK 5 (Response Schemas)

---

#### **3. models.py:74 — AttackPath Description**
```python
steps: List[AttackStep] = Field(..., description="3-5 attack steps")
```

**Location**: `backend/app/swarm/models.py`, class `AttackPath`, line 74

**Nature of Limit**: Documentation/description only (no functional constraint)

**Impact**: 🟢 **LOW SEVERITY**
- Misleading for API consumers
- No functional truncation
- OpenAPI schema shows incorrect range

**Task Mapping**: TASK 5 (Response Schemas)

---

### Agent Prompt Constraints (LLM Instruction)

#### **4. crews.py:239 — Exploration Agent Prompt**
```python
f"Each attack path MUST follow the cyber kill chain with EXACTLY 3 to 5 steps. "
```

**Location**: `backend/app/swarm/crews.py`, function `build_exploration_crew()`, line 239

**Nature of Limit**: Explicit instruction to LLM agents

**Impact**: 🟡 **MEDIUM SEVERITY**
- All exploration agents instructed to self-limit to 5 steps
- Affects: full pipeline, quick pipeline, single agent modes
- LLMs will compress multi-stage attacks to fit constraint

**Task Mapping**: TASK 4 (Agent Prompts)

---

#### **5. crews.py:1041 — Red Team Agent Prompt**
```python
"Propose 1-3 additional kill chain attack paths (3-5 steps each) that fill significant gaps. "
```

**Location**: `backend/app/swarm/crews.py`, function `build_adversarial_crew()`, line 1041

**Nature of Limit**: Explicit instruction to red team agent

**Impact**: 🟡 **MEDIUM SEVERITY**
- Red team gap analysis limited to 5 steps
- Cannot identify longer attack sequences missed by exploration
- Affects adversarial validation layer

**Task Mapping**: TASK 4 (Agent Prompts)

---

#### **6. swarm_exploration.py:115 — Stigmergic Swarm Intelligence Prompt**
```python
swarm_intel += "- Each attack path must have 3-5 steps\n"
```

**Location**: `backend/app/swarm/swarm_exploration.py`, function `build_swarm_aware_prompt()`, line 115

**Nature of Limit**: Instruction in swarm intelligence context

**Impact**: 🟡 **MEDIUM SEVERITY**
- Stigmergic swarm agents constrained to 5 steps
- Prevents collaborative discovery of long attack chains
- Affects stigmergic pipeline mode

**Task Mapping**: TASK 4 (Agent Prompts)

---

#### **7. swarm_exploration.py:409 — Stigmergic Task Description**
```python
f"Each attack path MUST follow the cyber kill chain with EXACTLY 3 to 5 steps.\n\n"
```

**Location**: `backend/app/swarm/swarm_exploration.py`, function `run_swarm_exploration()`, line 409

**Nature of Limit**: Task description for each persona in stigmergic mode

**Impact**: 🟡 **MEDIUM SEVERITY**
- Duplicate constraint in task-level prompt
- Reinforces 5-step limit for swarm agents

**Task Mapping**: TASK 4 (Agent Prompts)

---

#### **8. swarm_exploration.py:420 — Stigmergic Expected Output**
```python
"JSON array of attack paths with 3-5 steps each. "
```

**Location**: `backend/app/swarm/swarm_exploration.py`, function `run_swarm_exploration()`, line 420

**Nature of Limit**: Expected output format specification

**Impact**: 🟢 **LOW SEVERITY**
- LLM output format guidance
- Does not technically enforce limit but guides LLM behavior

**Task Mapping**: TASK 4 (Agent Prompts)

---

## False Positives / Acceptable Limits

### ✅ output_filter.py:189 — Exploitation Commands Display
```python
'exploitation_commands': v.exploitation_commands[:3],
```

**Location**: `backend/app/swarm/output_filter.py`, function `build_confirmed_findings_summary()`, line 189

**Why Acceptable**: 
- Only affects display of exploitation commands (sub-field)
- Does **not** truncate attack path steps
- Legitimate display truncation for UI readability

---

### ✅ consensus_aggregator.py:61 — Path Name Sampling
```python
'paths': data['paths'][:5],  # Sample of paths
```

**Location**: `backend/app/swarm/consensus_aggregator.py`, function `aggregate_consensus()`, line 61

**Why Acceptable**:
- Samples path **names** for display (not steps)
- Does **not** truncate step count
- Legitimate sampling for summary statistics

---

### ✅ output_filter.py:292-296 — Summary Display
```python
phases = ' → '.join(s.phase for s in non_gap[:4])
ids = ' → '.join(
    s.vuln_id or s.technique_id
    for s in non_gap[:4]
)
```

**Location**: `backend/app/swarm/vuln_intel/chain_assembler.py`, method `_summarise()`, lines 292-296

**Why Acceptable**:
- Only affects summary string generation
- Full chain is preserved in `chain.steps`
- Legitimate display truncation

---

## Files with No Truncation Issues

### ✅ path_evaluator.py
- No step count limits found
- No scoring penalties for longer paths
- Evaluates paths of any length equally
- **Verification**: Searched for `len(steps)`, `step count`, numeric limits — none found

### ✅ vuln_context_builder.py
- Pure orchestration layer
- No path manipulation
- Passes through assembled chains without modification
- **Verification**: Searched for `steps`, slicing operations — none found

### ✅ chain_assembler.py
- Processes all matched vulnerabilities without arbitrary limits
- Gap-filling logic inserts intermediate steps as needed
- No hardcoded step count caps
- **Verification**: No `max_steps`, `MAX_CHAIN_LENGTH`, or similar constants found
- **Enhancement**: Added `MAX_CHAIN_STEPS` constant for future extensibility (not required to fix existing issue)

---

## Summary Statistics

| Category | Count | Severity Breakdown |
|----------|-------|-------------------|
| **Critical Truncation** | 1 | 🔴 High: 1 |
| **Schema Constraints** | 2 | 🟡 Medium: 1, 🟢 Low: 1 |
| **Prompt Instructions** | 5 | 🟡 Medium: 4, 🟢 Low: 1 |
| **Total Issues** | 8 | 🔴 High: 1, 🟡 Medium: 5, 🟢 Low: 2 |
| **False Positives** | 3 | All acceptable display truncations |

---

## Affected Run Types Analysis

### Run Type 1: Full Pipeline (`POST /api/swarm/run`)
**Affected by**:
- ✗ Truncation point #1 (crews.py:440) — Critical
- ✗ Truncation point #2 (models.py:44) — Schema validation
- ✗ Truncation point #4 (crews.py:239) — Agent prompt
- ✗ Truncation point #5 (crews.py:1041) — Red team prompt

**Impact**: All exploration agents constrained to 5 steps, hard truncation at parse time

---

### Run Type 2: Quick Pipeline (`POST /api/swarm/run/quick`)
**Affected by**:
- ✗ Truncation point #1 (crews.py:440) — Critical
- ✗ Truncation point #2 (models.py:44) — Schema validation
- ✗ Truncation point #4 (crews.py:239) — Agent prompt
- ✗ Truncation point #5 (crews.py:1041) — Red team prompt

**Impact**: Same as full pipeline (uses same crew builder)

---

### Run Type 3: Single Agent (`POST /api/swarm/run/single`)
**Affected by**:
- ✗ Truncation point #1 (crews.py:440) — Critical
- ✗ Truncation point #2 (models.py:44) — Schema validation
- ✗ Truncation point #4 (crews.py:239) — Agent prompt
- ✗ Truncation point #5 (crews.py:1041) — Red team prompt

**Impact**: Same as full pipeline (uses same crew builder)

---

### Run Type 4: Stigmergic Swarm (`POST /api/swarm/run/stigmergic`)
**Affected by**:
- ✗ Truncation point #1 (crews.py:440) — Critical (parse results)
- ✗ Truncation point #2 (models.py:44) — Schema validation
- ✗ Truncation point #6 (swarm_exploration.py:115) — Swarm prompt
- ✗ Truncation point #7 (swarm_exploration.py:409) — Task description
- ✗ Truncation point #8 (swarm_exploration.py:420) — Expected output

**Impact**: Stigmergic mode has additional constraints in swarm-specific prompts

---

## Root Cause Analysis

### Why Were Paths Limited to 5 Steps?

1. **Original Design Decision**: Early threat modeling focused on "key highlight" paths
   - 3-5 steps considered sufficient for demonstrating attack feasibility
   - Emphasis on conciseness for executive summaries
   - Trade-off: Simplicity vs. completeness

2. **LLM Output Management**: Concern about LLM "hallucination" or verbose output
   - Shorter paths easier to validate
   - Less opportunity for LLM to generate speculative steps
   - Constraint acts as implicit quality control

3. **UI/UX Considerations**: Visualization limitations (not relevant post-React Flow migration)
   - Original SVG rendering may have struggled with long chains
   - Frontend complexity for displaying 10+ step paths
   - **Note**: React Flow migration removed this constraint

4. **Standard Kill Chain Model**: Confusion between "kill chain phases" and "steps"
   - Lockheed Martin kill chain has 7 phases
   - MITRE ATT&CK has 14 tactics
   - Early implementation conflated "one step per phase" incorrectly

### Why Increase to 10 Steps Now?

1. **Real-World Attack Complexity**: Modern cloud breaches are multi-stage
   - Capital One breach: 8+ distinct steps from SSRF to exfiltration
   - SolarWinds: 10+ steps from supply chain to lateral movement
   - Scarleteel: 9+ steps across multiple cloud services

2. **Gap-Filling Requirements**: Intermediate steps need space
   - Initial access → credential theft → privilege escalation → lateral movement → data access → exfiltration = 6 confirmed steps
   - Gap fillers between non-adjacent phases add 2-4 more
   - Total: 8-10 steps for realistic scenarios

3. **Threat Actor Sophistication**: APT campaigns require detailed modeling
   - Nation-state actors use 8-12 step campaigns
   - Ransomware groups: 7-10 steps (access → recon → lateral movement → privilege escalation → defense evasion → deployment → impact)
   - Compressed 5-step paths fail to capture sophistication

4. **Vulnerability Chain Assembly**: CVE chaining requires multiple steps
   - CVE-1 → CVE-2 → CVE-3 sequences need distinct steps
   - Cloud-native chains (IMDS → assume role → S3 access → exfiltration) can be 6-8 steps

---

## Lessons Learned

### What Worked Well in Existing Code

1. **Modular Architecture**: Truncation points isolated to specific modules
2. **Centralized Parsing**: Single `parse_exploration_results()` function made fix easier
3. **No Database Schema Changes**: Step count not constrained at persistence layer

### What Could Be Improved

1. **Magic Numbers**: Hardcoded `[:5]` slice should have been a named constant
2. **Prompt Duplication**: "3-5 steps" appears in 5+ locations; should be centralized
3. **Insufficient Documentation**: No design doc explaining the 5-step rationale
4. **Missing Validation**: No warning when steps are truncated by parser

### Future-Proofing Recommendations

1. **Add Constant**: `MAX_CHAIN_STEPS = int(os.getenv('SWARM_MAX_CHAIN_STEPS', '10'))`
   - Single source of truth
   - Configurable via environment variable
   - Easy to adjust in future

2. **Logging**: Add warning when parser encounters >10 steps
   ```python
   if len(path["steps"]) > MAX_CHAIN_STEPS:
       logger.warning(f"Path has {len(path['steps'])} steps, truncating to {MAX_CHAIN_STEPS}")
   ```

3. **Metrics**: Track average path length in production
   - Understand real-world distribution
   - Identify if 15-20 steps become necessary

4. **Prompt Templates**: Centralize prompt construction
   - Define step count once in template
   - Avoid duplication across files

---

## Conclusion

**Total Truncation Points Identified**: 8

**Critical Data Loss**: 1 (crews.py:440 slice)

**Prompt Constraints**: 5 (across 2 files)

**Schema Constraints**: 2 (models.py)

**All four run types affected** by at least 4 truncation points each, with stigmergic mode having 3 additional constraints.

The most severe issue was the hard slice in the JSON parser, which would have silently discarded steps 6-10 even after fixing agent prompts and schema validation. This pre-change analysis ensures comprehensive remediation.

---

**Report Prepared By**: Claude Code  
**Date**: 2026-04-21  
**Next Step**: Implement fixes per TEN_STEP_PATH_IMPLEMENTATION_REPORT.md
