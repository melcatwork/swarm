# CVE Detection Test Report
**Date**: 2026-04-24
**Test File**: Capital One Breach Replica (22 assets, 12 cloud signals)

## Executive Summary

❌ **NO CVE IDs are being returned** in threat modeling runs
❌ **NO exploit enrichment** (edb_ids, nuclei_templates, poc_sources) is working
✅ **Cloud abuse patterns** (ATTCK-*) ARE working correctly

## Root Cause Analysis

### Database Status
```
Total CVEs in intel.db: 2,714
CVEs with product information: 0
CVEs with version information: 0
```

### The Problem

The `intel.db` SQLite database contains **2,714 CVE records** BUT:

1. **ALL `affected_products_json` fields are EMPTY** (`[]`)
2. **ALL `affected_versions` fields are EMPTY** (`""`)
3. **CVEs are populated from CISA KEV only** (source: "KEV")

The CISA KEV (Known Exploited Vulnerabilities) catalog provides:
- ✅ CVE IDs (CVE-YYYY-NNNNN)
- ✅ ATT&CK technique mappings (T1190, etc.)
- ❌ Product names
- ❌ Version ranges
- ❌ CPE strings
- ❌ Detailed descriptions

### How CVE Matching Works

From `backend/app/swarm/vuln_intel/cve_adapter.py` (lines 35-54):

```python
for asset in asset_graph.get('assets', []):
    resource_type = asset.get('type', '')
    software = asset.get('engine') or asset.get('runtime') or ...
    version = asset.get('engine_version') or asset.get('runtime_version') or ...
    
    entries = self.db.get_cves_for_resource(
        resource_type=resource_type,
        software=software,
        version=version,
    )
```

The CVE adapter extracts:
- Software name from asset (e.g., "postgres", "mysql")
- Version from asset (e.g., "14.7", "8.0.32")
- Then queries the database for matching CVEs

**BUT** because all CVEs in the database have empty product/version fields, the query returns **0 matches**.

## Test Results

### Sample Run: Capital One Breach Replica

```
[1] Parsing sample Terraform file...
    ✓ Parsed 22 assets

[2] Building vulnerability context (CVE lookup enabled)...
    ✓ Detected 12 cloud signals
    ✓ Matched 12 vulnerabilities

[3] Analyzing matched vulnerabilities...
    CVE vulnerabilities: 0
    Cloud abuse patterns: 12

SUMMARY
Total vulnerabilities: 12
CVE-format IDs (CVE-YYYY-NNNN): 0
ATT&CK-based abuse patterns (ATTCK-*): 12

⚠️  No CVE-format IDs found (CVE-YYYY-NNNN)
⚠️  No exploit enrichment found (edb_ids, nuclei_templates, poc_sources all empty)
```

### What IS Working

✅ **Cloud Signal Detection**: 12 signals detected correctly
- IMDS_V1_ENABLED
- PUBLIC_INGRESS_OPEN
- UNRESTRICTED_EGRESS
- IAM_S3_WILDCARD
- CLOUDTRAIL_NO_S3_DATA_EVENTS
- etc.

✅ **Cloud Abuse Pattern Matching**: 12 ATTCK-* patterns matched
- ATTCK-T1190 (Exploit Public-Facing Application)
- ATTCK-T1530 (Data from Cloud Storage)
- ATTCK-T1552-005 (Cloud Instance Metadata API)
- ATTCK-T1562-008 (Disable or Modify Cloud Logs)
- ATTCK-T1567 (Exfiltration Over Web Service)
- etc.

✅ **Attack Chain Assembly**: Chains are created from matched abuse patterns

### What IS NOT Working

❌ **CVE Matching**: 0 CVEs matched (database has no product/version data)
❌ **Exploit Enrichment**: 0 vulnerabilities enriched with:
- ExploitDB IDs (`edb_ids`, `edb_titles`)
- Nuclei templates (`nuclei_templates`, `nuclei_severity`)
- PoC sources (`poc_sources`, `poc_available`)

## Why No `cve_id` or `exploit_ref` Fields

**Question**: Is there `cve_id` or `exploit_ref` in the data model?

**Answer**:

### In `MatchedVuln` dataclass:
- ❌ `cve_id` does NOT exist
- ✅ `vuln_id` exists (contains either CVE-YYYY-NNNN or ATTCK-*)
- ✅ `edb_ids` exists (list of ExploitDB IDs) - but always empty due to no CVE matches
- ✅ `nuclei_templates` exists (list of Nuclei template IDs) - but always empty
- ✅ `poc_sources` exists (list like ["ExploitDB:12345", "Nuclei:cve-2024-1234"]) - but always empty
- ❌ `exploit_ref` does NOT exist

### In `VulnRecord` dataclass:
- ✅ `cve_id` EXISTS
- ✅ Same exploit enrichment fields
- ❌ `exploit_ref` does NOT exist

**Current field naming**:
- Use `vuln_id` instead of `cve_id` in MatchedVuln
- Use `edb_ids`, `nuclei_templates`, `poc_sources` instead of generic `exploit_ref`

## Solution Path

To get CVE matching and exploit enrichment working, you need to:

### Option 1: Populate Database from NVD API
Enhance the database population script to fetch full CVE details from NVD including:
- Affected products (CPE strings)
- Version ranges
- Descriptions
- CVSS scores
- References

### Option 2: Use Alternative CVE Sources
- OSV (Open Source Vulnerabilities)
- GitHub Security Advisories (GHSA)
- Snyk Vulnerability Database
- VulnDB

### Option 3: Manual Enrichment for Key Software
Manually add product/version data for commonly used software:
- PostgreSQL versions
- MySQL versions
- Redis versions
- Node.js versions
- Python versions
- etc.

## Files Checked

- ✅ `backend/app/swarm/vuln_intel/vuln_matcher.py` - Matching logic
- ✅ `backend/app/swarm/vuln_intel/cve_adapter.py` - CVE adapter
- ✅ `backend/app/swarm/vuln_intel/intel_db.py` - Database schema
- ✅ `backend/app/swarm/vuln_intel/exploit_adapters.py` - ExploitDB/Nuclei enrichment
- ✅ `backend/data/intel.db` - SQLite database (2714 CVEs, 0 with product data)
- ✅ `logs/backend.log` - Runtime logs

## Recommendations

1. **Short-term**: Document that only cloud abuse patterns are supported
2. **Medium-term**: Implement NVD API integration to populate product/version data
3. **Long-term**: Add multiple CVE sources for comprehensive coverage

## Test Script

A test script has been created at:
```
/Users/bland/Desktop/swarm-tm/test_cve_detection.py
```

Run it to reproduce these results:
```bash
python3 test_cve_detection.py
```
