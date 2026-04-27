# Automatic Persona Intelligence Sync Guide

This guide explains how persona intelligence updates work and how to configure automatic updates.

---

## How Persona Intelligence Updates Work

### Current Architecture

1. **Threat Intelligence Sources** (free, public, no API keys):
   - CISA Known Exploited Vulnerabilities (KEV)
   - MITRE ATT&CK STIX data
   - CISA StopRansomware advisories

2. **Intelligence Processing**:
   - `sync_intel.py` fetches latest threat data
   - Filters for cloud-relevant signals (AWS, Azure, GCP, IaaS, SaaS)
   - Matches signals to 13 threat actor personas
   - Stores in `backend/app/swarm/vuln_intel/intel.db`

3. **AI Patch Generation**:
   - Claude (via Bedrock or Anthropic API) evaluates each signal
   - Determines if signal warrants persona update
   - Generates concise patch (2-5 sentences) in persona's style
   - Stores accepted patches in `persona_patches` table

4. **Runtime Merging**:
   - When threat model runs, personas loaded from `personas.yaml`
   - Patches automatically merged into `security_reasoning_approach`
   - Section added: "CURRENT INTELLIGENCE UPDATES (applied automatically)"
   - Agents see both base persona + latest threat intelligence

---

## Current Status

### Your Intelligence Database

**Last Update**: April 25, 2026 at 2:12 AM

| Persona | Patches Applied | Last Updated |
|---------|-----------------|--------------|
| Nation State APT | 35 | 2026-04-25 02:12:04 |
| Scattered Spider | 13 | 2026-04-25 02:11:57 |
| Volt Typhoon | 9 | 2026-04-25 02:10:36 |
| APT29 Cozy Bear | 6 | 2026-04-25 02:11:02 |
| Lazarus Group | 4 | 2026-04-25 02:09:32 |
| FIN7 | 1 | 2026-04-25 02:08:01 |
| Cloud Native Attacker | 1 | 2026-04-25 01:46:37 |
| **TOTAL** | **69 patches** | **All from today** |

**Source Breakdown**:
- CISA KEV entries: ~484 signals
- MITRE ATT&CK cloud techniques: ~200 signals
- CISA StopRansomware: Variable

---

## ⚠️ Problem: No Automatic Updates

**BY DEFAULT, INTELLIGENCE DOES NOT UPDATE AUTOMATICALLY.**

You must manually run:
```bash
python3 backend/scripts/sync_intel.py --force
```

**Why this matters**:
- New CVEs discovered daily
- Threat actor TTPs evolve weekly
- CISA KEV updated when exploits are active
- Personas become stale without updates

**Example**: If APT29 starts using a new cloud technique today, your personas won't know about it until you run sync again.

---

## ✅ Solution: Automatic Daily Updates

### Option 1: Quick Setup (Recommended)

**Run the setup script**:
```bash
./setup-auto-intel-sync.sh
```

This will:
1. Detect your LLM provider (Bedrock or Anthropic)
2. Create appropriate cron jobs
3. Configure daily intelligence sync at 2:00 AM
4. Configure token refresh for Bedrock (if needed)
5. Show you exactly what will run

**Interactive prompts**:
- Shows current crontab
- Shows proposed cron jobs
- Asks for confirmation before installing

**Logs**:
- `logs/intel-sync.log` — Intelligence sync output
- `logs/token-refresh.log` — AWS token refresh output (Bedrock only)

---

### Option 2: Manual Crontab Setup

#### For AWS Bedrock Users

```bash
# Edit crontab
crontab -e

# Add these lines:

# Swarm TM - Daily Intelligence Sync (2:00 AM)
0 2 * * * cd /Users/bland/Desktop/swarm-tm && python3 backend/scripts/sync_intel.py --force >> logs/intel-sync.log 2>&1

# Swarm TM - AWS Token Refresh (midnight)
0 0 * * * cd /Users/bland/Desktop/swarm-tm && bash backend/scripts/get_aws_token.sh >> logs/token-refresh.log 2>&1
```

**Why two jobs?**
- Bedrock tokens expire after 12 hours
- Token refresh runs at midnight to ensure morning sync has valid token
- Token refresh script updates `.env` with new bearer token

#### For Anthropic API Users

```bash
# Edit crontab
crontab -e

# Add this line:

# Swarm TM - Daily Intelligence Sync (2:00 AM)
0 2 * * * cd /Users/bland/Desktop/swarm-tm && python3 backend/scripts/sync_intel.py --force >> logs/intel-sync.log 2>&1
```

**Note**: Anthropic API keys don't expire, so no token refresh needed.

---

### Option 3: Custom Schedule

**Run more frequently** (every 6 hours):
```bash
0 */6 * * * cd /Users/bland/Desktop/swarm-tm && python3 backend/scripts/sync_intel.py --force >> logs/intel-sync.log 2>&1
```

**Run weekly** (Sunday at 3:00 AM):
```bash
0 3 * * 0 cd /Users/bland/Desktop/swarm-tm && python3 backend/scripts/sync_intel.py --force >> logs/intel-sync.log 2>&1
```

**Cron syntax reminder**:
```
* * * * *
│ │ │ │ └─── Day of week (0-7, Sunday = 0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

---

## Verification

### Check Cron Jobs Are Running

```bash
# View installed cron jobs
crontab -l

# Check sync log (should update daily)
tail -f logs/intel-sync.log

# Check when last sync ran
ls -lah logs/intel-sync.log

# Check patch status
python3 backend/scripts/review_patches.py --summary
```

### Verify Intelligence is Current

**Backend API**:
```bash
curl http://localhost:8000/api/swarm/persona-status | jq
```

**Frontend UI**:
1. Open http://localhost:5173/model
2. See "Persona Intelligence Status" panel
3. Click to expand
4. Check "Last sync" date for each persona
5. Green dot = updated within 7 days
6. Amber dot = 8-30 days old
7. Red dot = >30 days old (need to re-sync)

---

## Manual Sync (When Needed)

You have two options for manual sync:

### Option 1: UI Button (Easiest)

1. **Open the threat modeling page**: http://localhost:5173/model
2. **Find "Persona Intelligence Status" panel** (above upload section)
3. **Click "Sync Now" button** (purple button in header)
4. **Wait 2-5 minutes** (button shows "Syncing...")
5. **Status automatically refreshes** with new patch counts

**Benefits**:
- ✅ One-click operation
- ✅ Visual feedback during sync
- ✅ Status message confirms completion
- ✅ Auto-refreshes when done
- ✅ No terminal needed

**What you'll see**:
```
[Persona Intelligence Status] [69 patches] [Syncing...] [Last sync: 2026-04-25]
✓ Intelligence sync started in background. This may take 2-5 minutes...
```

After 5 seconds:
```
[Persona Intelligence Status] [72 patches] [Sync Now] [Last sync: 2026-04-25]
✓ Intelligence sync completed. Status refreshed.
```

### Option 2: Command Line

```bash
python3 backend/scripts/sync_intel.py --force
```

**Expected output**:
```
Syncing threat intelligence...
Syncing ExploitDB...
Syncing Nuclei template CVE index...

Ingesting threat intelligence signals...
INFO: CISA advisories: ingested 15 new signals
INFO: ATT&CK: ingested 8 cloud-relevant group signals

Loading personas for patch evaluation...
INFO: Loaded 13 personas for patch evaluation

Running persona patch generator...
INFO: Using AWS Bedrock for patch generation
INFO: PersonaPatchGenerator: evaluating 23 signals
INFO: Patch written: nation_state_apt | new_ttp | confidence=high
INFO: Patch written: volt_typhoon | updated_ttp | confidence=high
INFO: PersonaPatchGenerator: processed 23 signals, wrote 5 patches

Done.
```

### Review Generated Patches

```bash
python3 backend/scripts/review_patches.py --summary
```

**Expected output**:
```
Persona                         Total  Applied  Last update
-----------------------------------------------------------------
nation_state_apt                   35       35  2026-04-25
scattered_spider                   13       13  2026-04-25
volt_typhoon                        9        9  2026-04-25
apt29_cozy_bear                     6        6  2026-04-25
lazarus_group                       4        4  2026-04-25
fin7                                1        1  2026-04-25
cloud_native_attacker               1        1  2026-04-25
```

### Review Specific Persona's Patches

```bash
python3 backend/scripts/review_patches.py --persona nation_state_apt
```

---

## Cost Considerations

### AWS Bedrock

- **Model**: Claude 3 Sonnet (anthropic.claude-3-sonnet-20240229-v1:0)
- **Per sync**: ~$0.03-0.06 (processes 20-100 signals depending on volume)
- **Daily syncs**: ~$0.90-1.80/month
- **Token refresh**: Free (just AWS STS call)

### Anthropic API

- **Model**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Per sync**: ~$0.03-0.06
- **Daily syncs**: ~$0.90-1.80/month
- **No token refresh needed**

**Recommendation**: Daily syncs are very affordable (<$2/month) and keep your personas current.

---

## Troubleshooting

### Cron Job Not Running

**Check cron service**:
```bash
# macOS
sudo launchctl list | grep cron

# Restart if needed
sudo launchctl stop com.vix.cron
sudo launchctl start com.vix.cron
```

**Check logs**:
```bash
# View system mail for cron errors
mail

# View sync log
tail -f logs/intel-sync.log
```

### No New Patches Generated

**Possible reasons**:
1. No new threat intelligence available (signals already processed)
2. New signals not cloud-relevant (filtered out)
3. New signals already covered by existing patches (LLM determined no update needed)
4. LLM API error (check logs)

**Check signal processing**:
```bash
sqlite3 backend/app/swarm/vuln_intel/intel.db "SELECT COUNT(*) FROM threat_intel_signals WHERE processed = 0;"
```

If result is 0: all signals processed, no new intelligence available.

### Token Expired (Bedrock)

**Manual token refresh**:
```bash
bash backend/scripts/get_aws_token.sh
```

**Copy output to `.env`**:
```bash
AWS_BEARER_TOKEN_BEDROCK=IQoJb3JpZ2luX2VjEJD...
```

---

## Best Practices

1. **Monitor logs weekly**: `tail -20 logs/intel-sync.log`
2. **Check frontend status**: Green dots = healthy, red dots = need attention
3. **Manual sync after major events**: When CISA publishes new advisories, run manual sync
4. **Review patches quarterly**: Use `review_patches.py --summary` to audit intelligence sources
5. **Update Bedrock tokens**: If using Bedrock, ensure token refresh cron is working

---

## Disabling Automatic Updates

**Remove cron jobs**:
```bash
crontab -e

# Delete the lines:
# Swarm TM - Daily Intelligence Sync
# Swarm TM - AWS Token Refresh
```

**Or remove all crontab**:
```bash
crontab -r
```

Intelligence will remain at current state until you manually run sync again.

---

## Summary

✅ **Setup automatic updates**: `./setup-auto-intel-sync.sh`
✅ **Verify cron installed**: `crontab -l`
✅ **Check logs**: `tail -f logs/intel-sync.log`
✅ **Manual sync**: `python3 backend/scripts/sync_intel.py --force`
✅ **Review patches**: `python3 backend/scripts/review_patches.py --summary`
✅ **Frontend check**: http://localhost:5173/model (Persona Intelligence Status panel)

---

**Last Updated**: 2026-04-25
**Related Files**:
- `setup-auto-intel-sync.sh` — Automatic setup script
- `backend/scripts/sync_intel.py` — Intelligence sync script
- `backend/scripts/review_patches.py` — Patch review tool
- `BEDROCK_QUICK_START.md` — Bedrock configuration guide
