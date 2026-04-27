# AWS Bedrock Configuration Guide for Living Intelligence System

This guide shows you how to configure AWS Bedrock for the persona patch generator instead of using the direct Anthropic API.

---

## ✅ What You Need

1. **AWS Account** with Bedrock access
2. **AWS Bearer Token** for authentication
3. **AWS Region** where Bedrock is available (e.g., us-east-1, us-west-2)

---

## 📝 Step 1: Add Bedrock Credentials to .env

Add these lines to your `backend/.env` file (or `backend/app/.env`):

```bash
# AWS Bedrock Configuration for Persona Patch Generator
AWS_BEARER_TOKEN_BEDROCK=your-bearer-token-here
AWS_REGION=us-east-1

# Model Configuration (Claude 3.5 Sonnet v2 recommended)
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Available Bedrock Models

The system uses **Claude 3.5 Sonnet v2** by default for patch generation. This is the most capable model for threat intelligence evaluation.

Other models available on Bedrock:
- `anthropic.claude-3-5-sonnet-20241022-v2:0` — Claude 3.5 Sonnet v2 (recommended)
- `anthropic.claude-3-5-sonnet-20240620-v1:0` — Claude 3.5 Sonnet v1
- `anthropic.claude-3-opus-20240229-v1:0` — Claude 3 Opus (most powerful)
- `anthropic.claude-3-sonnet-20240229-v1:0` — Claude 3 Sonnet (balanced)
- `anthropic.claude-3-haiku-20240307-v1:0` — Claude 3 Haiku (fastest)

---

## 🔑 Step 2: Get Your AWS Bearer Token

### Option A: Using AWS CLI

If you have AWS CLI configured with credentials:

```bash
# Get temporary credentials (valid for 1-12 hours)
aws sts get-session-token --duration-seconds 43200

# The output includes:
# - AccessKeyId
# - SecretAccessKey
# - SessionToken (this is your bearer token)
```

Copy the `SessionToken` value and use it as your `AWS_BEARER_TOKEN_BEDROCK`.

### Option B: Using AWS IAM Credentials

1. Go to AWS Console → IAM → Users → Your User
2. Security credentials tab
3. Create Access Key
4. Use the generated Access Key ID and Secret Access Key

**Note:** For bearer token authentication, you typically need the session token from `aws sts get-session-token`.

### Option C: Using AWS SSO

```bash
aws sso login --profile your-profile
aws sts get-session-token --profile your-profile --duration-seconds 43200
```

---

## 🌍 Step 3: Choose Your AWS Region

Bedrock is available in these regions:
- `us-east-1` (N. Virginia) ✅ Recommended
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

Set the region in your `.env`:
```bash
AWS_REGION=us-east-1
```

---

## ✅ Step 4: Verify Configuration

Check that your credentials are working:

```bash
# Test Bedrock access
python3 -c "
import os
os.environ['AWS_BEARER_TOKEN_BEDROCK'] = 'your-token-here'
os.environ['AWS_REGION'] = 'us-east-1'

from crewai import LLM

llm = LLM(
    model='bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0',
    temperature=0.3,
    max_tokens=100
)

response = llm.call([{'role': 'user', 'content': 'Say hello'}])
print('✓ Bedrock connection successful!')
print(response)
"
```

---

## 🚀 Step 5: Run Intel Sync with Bedrock

Once configured, run the sync:

```bash
python3 backend/scripts/sync_intel.py --force
```

**Expected output:**
```
Syncing threat intelligence...
KEV: 1583 records
EPSS: 1000 scores
ATT&CK: 150 records

Ingesting threat intelligence signals...
CISA advisories: ingested 89 new signals
ATT&CK: ingested 153 cloud-relevant group signals

Loading personas for patch evaluation...
Running persona patch generator...
INFO: Using AWS Bedrock for patch generation
INFO: Using Bedrock model: bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0, region: us-east-1
INFO: PersonaPatchGenerator: evaluating 20 signals
INFO: PersonaPatchGenerator: processed 20 signals, wrote 5 patches

Done.
```

---

## 📊 Check Results

After running sync, check the generated patches:

```bash
# View patch summary
python3 backend/scripts/review_patches.py --summary

# Expected output:
# Persona                         Total  Applied Last update
# -----------------------------------------------------------------
# cloud_native_attacker               3        3 2026-04-25
# apt29_cozy_bear                     2        2 2026-04-25
# lazarus_group                       1        1 2026-04-25
```

---

## 🔧 Troubleshooting

### Error: "AWS_BEARER_TOKEN_BEDROCK required for Bedrock"

**Solution:** Make sure you've added the token to `.env`:
```bash
AWS_BEARER_TOKEN_BEDROCK=your-token-here
```

### Error: "Bedrock model not found" or "AccessDeniedException"

**Possible causes:**
1. **Model not enabled in your region**
   - Go to AWS Console → Bedrock → Model access
   - Request access to Claude models
   - Wait for approval (usually instant)

2. **Wrong region**
   - Check which region has Claude models enabled
   - Update `AWS_REGION` in `.env`

3. **Insufficient IAM permissions**
   - Your IAM user/role needs `bedrock:InvokeModel` permission
   - Add this policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/*"
       }
     ]
   }
   ```

### Error: "Token expired"

AWS session tokens typically expire after 1-12 hours. Solutions:

1. **Use longer duration:**
   ```bash
   aws sts get-session-token --duration-seconds 43200  # 12 hours
   ```

2. **Set up automatic token refresh:**
   - Use AWS SSO with automatic refresh
   - Or create a script to refresh tokens before each sync

3. **Use IAM credentials instead:**
   - If you have long-term IAM credentials, they don't expire
   - Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` instead

### Slow patch generation

**Normal behavior:**
- 20 signals take ~30-60 seconds to evaluate
- Each LLM call takes ~2-3 seconds

**To speed up:**
- Reduce `limit=20` to `limit=10` in sync_intel.py
- Use Claude 3 Haiku (faster but less accurate)

---

## 💰 Cost Considerations

**Bedrock Pricing (Claude 3.5 Sonnet v2):**
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens

**Typical patch generation costs:**
- 20 signals evaluated: ~10,000 input tokens + ~2,000 output tokens
- **Cost per sync: ~$0.06**
- **Monthly cost (daily syncs): ~$1.80**

**Compare to Anthropic API Direct:**
- Similar pricing structure
- No significant cost difference

---

## 🔄 Switching Between Bedrock and Anthropic API

The system auto-detects which credentials are available:

**Use Bedrock:**
```bash
AWS_BEARER_TOKEN_BEDROCK=your-token
# ANTHROPIC_API_KEY not set or commented out
```

**Use Anthropic API:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
# AWS_BEARER_TOKEN_BEDROCK not set or commented out
```

**Priority:** If both are set, **Bedrock is used first**.

---

## ✅ Complete Example .env File

```bash
# =============================================================================
# LLM Configuration for Living Intelligence System
# =============================================================================

# Option 1: AWS Bedrock (recommended for existing AWS users)
AWS_BEARER_TOKEN_BEDROCK=AQoDYXdzEJr...  # Your AWS session token
AWS_REGION=us-east-1
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# Option 2: Anthropic API (alternative)
# ANTHROPIC_API_KEY=sk-ant-api03-...

# =============================================================================
# Existing Configuration (unchanged)
# =============================================================================

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:27b
LLM_TEMPERATURE=0.5
LLM_MAX_TOKENS=4096
```

---

## 🎯 Next Steps

1. ✅ Add `AWS_BEARER_TOKEN_BEDROCK` to `.env`
2. ✅ Set `AWS_REGION` to your preferred region
3. ✅ Run `python3 backend/scripts/sync_intel.py --force`
4. ✅ Verify patches generated: `python3 backend/scripts/review_patches.py --summary`
5. ✅ Check personas load with patches: see verification commands below

### Verification Commands

```bash
# Check database
python3 -c "
import sqlite3
from pathlib import Path
db = Path('backend/app/swarm/vuln_intel/intel.db')
with sqlite3.connect(db) as conn:
    patches = conn.execute('SELECT COUNT(*) FROM persona_patches WHERE applied=1').fetchone()[0]
    print(f'✓ Applied patches: {patches}')
"

# Check personas load with patches
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('backend').absolute()))
sys.path.insert(0, str(Path('backend/app').absolute()))

from app.swarm.agents.persona_registry import PersonaRegistry

registry = PersonaRegistry()
personas = registry.get_all()

for pid in ['cloud_native_attacker', 'apt29_cozy_bear', 'lazarus_group']:
    if pid in personas:
        p = personas[pid]
        approach = p.get('security_reasoning_approach', '')
        has_patches = 'CURRENT INTELLIGENCE UPDATES' in approach
        if has_patches:
            print(f'✓ {pid}: patches applied')
"
```

---

## 📞 Support

If you encounter issues:
1. Check logs: Look for errors in sync output
2. Verify IAM permissions: Ensure `bedrock:InvokeModel` access
3. Test Bedrock directly: Use AWS CLI to test model access
4. Check region availability: Confirm Claude models are enabled in your region

**Common fixes:**
- Token expired → Get new session token
- Model not found → Request model access in Bedrock console
- Permission denied → Add IAM policy for Bedrock access

---

**Updated:** 2026-04-25  
**System:** swarm-tm Living Intelligence v2.0  
**Status:** Production Ready ✅
