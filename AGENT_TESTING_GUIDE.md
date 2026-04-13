# Agent Testing Guide

## Recommended Agents for Single Agent Testing

### 🏆 Best Choice: `apt29_cozy_bear`

**Display Name:** APT29 (Cozy Bear)
**Category:** Nation-State Threat Actor
**Status:** ✅ Enabled by default

**Why use this agent:**
- Emulates sophisticated Russian SVR-linked threat actor (SolarWinds attack)
- Focuses on cloud services, OAuth tokens, and supply chain compromise
- Generates realistic, stealthy attack paths with high dwell time
- Best for comprehensive AWS infrastructure testing
- Techniques include: T1195 (Supply Chain), T1078.004 (Cloud Accounts), T1550.001 (Application Access Tokens)

**Best for:**
- ✅ Cloud infrastructure security assessment
- ✅ Identity and credential theft scenarios
- ✅ Long-term persistence testing
- ✅ Supply chain risk analysis

---

### 🥈 Alternative: `scattered_spider`

**Display Name:** Scattered Spider
**Category:** Cybercrime Threat Actor
**Status:** ✅ Enabled by default

**Why use this agent:**
- Emulates recent high-profile attacks (MGM Resorts, Caesars 2023)
- Focuses on identity systems, SSO, MFA weaknesses
- Specializes in social engineering + cloud console access
- Techniques include: T1621 (Multi-Factor Authentication Request Generation), T1078.004 (Cloud Accounts), T1098.001 (Additional Cloud Credentials)

**Best for:**
- ✅ Identity and Access Management (IAM) testing
- ✅ SSO/Federation security assessment
- ✅ MFA bypass scenarios
- ✅ Cloud console compromise paths

---

## Other Available Agents (Currently Disabled)

### `lazarus_group`
- **Focus:** Financial crime, cryptocurrency, destructive operations
- **Use case:** Payment systems, financial data stores, ransomware scenarios

### `volt_typhoon`
- **Focus:** Critical infrastructure pre-positioning, living-off-the-land
- **Use case:** Persistent access to network infrastructure, minimal tooling

### `fin7`
- **Focus:** E-commerce, payment processing, PII/PCI data
- **Use case:** Web applications, payment systems, database exfiltration

---

## How to Test

### Via Frontend (Recommended)

1. **Start all services:**
   ```bash
   ./start-all.sh
   ```

2. **Open frontend:** http://localhost:5173

3. **Upload IaC file:**
   - `samples/ecommerce-platform.tf`
   - `samples/healthcare-data-pipeline.tf`
   - `samples/file-transfer-system.tf`
   - `samples/clouddocs-saas-app.tf`

4. **Select agent:**
   - Choose `APT29 (Cozy Bear)` from dropdown

5. **Run test:**
   - Click "Single Agent Test"
   - Wait 5-10 minutes for results

### Via API

```bash
curl -X POST "http://localhost:8000/api/swarm/run/single?agent_name=apt29_cozy_bear" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/ecommerce-platform.tf"
```

---

## Expected Results with qwen3:14b

With the updated model, you should see:

✅ **Attack paths generated** (not 0)
✅ **Valid JSON structure**
✅ **Kill chain phases** (Initial Access → Execution → Lateral Movement → Objective → Covering Tracks)
✅ **MITRE ATT&CK techniques** (T-numbers with links)
✅ **Target assets** from your infrastructure
✅ **Mitigations** mapped to each step
✅ **Confidence scores** (High/Medium/Low)

---

## Troubleshooting

### Still seeing 0 attack paths?

1. **Check backend logs:**
   ```bash
   tail -f logs/backend.log | grep -i "exploration\|paths\|json"
   ```

2. **Verify model:**
   ```bash
   ollama list | grep qwen3
   # Should show qwen3:14b (9.3 GB)
   ```

3. **Check LLM configuration:**
   ```bash
   cat .env | grep OLLAMA_MODEL
   # Should show: OLLAMA_MODEL=qwen3:14b
   ```

4. **Restart backend:**
   ```bash
   ./stop-all.sh
   ./start-all.sh
   ```

### Model too slow?

The 14B model is more accurate but slower (5-10 min per run). If speed is critical:

- Use **"Quick Run (2 agents)"** instead of full swarm
- Use **Single Agent Test** (fastest, 3-5 min)
- Consider cloud-based models (Anthropic Claude, AWS Bedrock) for production

---

## Performance Comparison

| Model | Size | Speed | JSON Quality | Recommended |
|-------|------|-------|--------------|-------------|
| qwen3:4b | 2.5 GB | Fast | ❌ Poor (0 paths) | ❌ No |
| qwen3:14b | 9.3 GB | Medium | ✅ Good | ✅ Yes |
| Claude Sonnet | API | Fast | ✅ Excellent | ✅ Production |

---

## Next Steps

1. ✅ Updated model to qwen3:14b
2. ✅ Restart backend (./stop-all.sh && ./start-all.sh)
3. ✅ Test with apt29_cozy_bear agent
4. ✅ Upload sample .tf file
5. ✅ Verify attack paths appear on frontend

For questions or issues, check logs in `logs/` directory.
