# AWS Bedrock Quick Start (3 Minutes)

Get your living intelligence system running with AWS Bedrock in 3 simple steps.

---

## ⚡ Quick Setup

### Step 1: Get Your AWS Token (1 minute)

Run the helper script:

```bash
bash backend/scripts/get_aws_token.sh
```

This will:
- ✓ Check your AWS CLI is configured
- ✓ Generate a session token (valid for 12 hours)
- ✓ Output the exact line to copy to `.env`

**Output example:**
```
AWS_BEARER_TOKEN_BEDROCK=IQoJb3JpZ2luX2VjEJD//...
```

### Step 2: Add Token to .env (30 seconds)

Add these two lines to `backend/.env`:

```bash
AWS_BEARER_TOKEN_BEDROCK=your-token-from-step-1
AWS_REGION=us-east-1
```

### Step 3: Test & Run (1 minute)

```bash
# Test connection
python3 backend/scripts/test_bedrock_connection.py

# If test passes, run sync
python3 backend/scripts/sync_intel.py --force
```

Done! Your personas are now automatically updating with latest threat intelligence.

---

## 📊 Verify It's Working

```bash
# Check patches generated
python3 backend/scripts/review_patches.py --summary

# Check personas have patches
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('backend').absolute()))
sys.path.insert(0, str(Path('backend/app').absolute()))

from app.swarm.agents.persona_registry import PersonaRegistry

registry = PersonaRegistry()
personas = registry.get_all()
cna = personas['cloud_native_attacker']

if 'CURRENT INTELLIGENCE UPDATES' in cna['security_reasoning_approach']:
    print('✓ Patches successfully applied to personas!')
else:
    print('✗ No patches found')
"
```

---

## 🔍 What Just Happened?

1. **484 threat signals** ingested from CISA KEV and MITRE ATT&CK
2. **Claude 3.5 Sonnet v2** evaluated each signal for relevance
3. **AI-generated patches** added to personas (5-20 patches typical)
4. **Personas automatically updated** without touching YAML files

---

## ⚙️ Automated Daily Updates

Add to crontab for automatic updates:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2am daily):
0 2 * * * cd /path/to/swarm-tm && python3 backend/scripts/sync_intel.py --force
```

Token refresh (tokens expire after 12 hours):
```bash
# Add this line (runs at midnight daily):
0 0 * * * cd /path/to/swarm-tm && bash backend/scripts/get_aws_token.sh | grep AWS_BEARER_TOKEN_BEDROCK >> backend/.env
```

---

## 🛠️ Troubleshooting

### Test fails: "Token expired"

```bash
# Get new token
bash backend/scripts/get_aws_token.sh

# Update .env with new token
# Re-run test
```

### Test fails: "Model not found"

**Solution:**
1. Go to AWS Console → Bedrock → Model access
2. Enable access to Claude models
3. Wait for approval (usually instant)
4. Re-run test

### Test fails: "AccessDeniedException"

**Solution:** Add IAM policy to your user/role:

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

---

## 💰 Cost Estimate

- **Per sync:** ~$0.06 (evaluates 20 signals)
- **Daily syncs:** ~$1.80/month
- **Very affordable** for automatic threat intelligence updates

---

## 🔄 Alternative: Use Anthropic API Instead

If you prefer direct Anthropic API:

```bash
# Add to .env
ANTHROPIC_API_KEY=sk-ant-api03-...

# Comment out Bedrock config
# AWS_BEARER_TOKEN_BEDROCK=...

# Run sync (will auto-detect Anthropic API)
python3 backend/scripts/sync_intel.py --force
```

**Cost:** Similar to Bedrock (~$1-2/month for daily syncs)

---

## 📖 Full Documentation

For detailed configuration, see:
- `BEDROCK_CONFIGURATION_GUIDE.md` — Complete setup guide
- `LIVING_INTELLIGENCE_IMPLEMENTATION.md` — System architecture

---

## ✅ Success Indicators

After running sync, you should see:

```
Running persona patch generator...
INFO: Using AWS Bedrock for patch generation
INFO: Using Bedrock model: bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
INFO: PersonaPatchGenerator: evaluating 20 signals
INFO: PersonaPatchGenerator: processed 20 signals, wrote 5 patches
Done.
```

And when checking patches:
```bash
$ python3 backend/scripts/review_patches.py --summary

Persona                         Total  Applied Last update
-----------------------------------------------------------------
cloud_native_attacker               3        3 2026-04-25
apt29_cozy_bear                     2        2 2026-04-25
lazarus_group                       1        1 2026-04-25
```

---

**That's it!** Your threat actor personas are now living documents that update automatically with the latest intelligence. 🎉

**Questions?** Check the full guides or open an issue.
