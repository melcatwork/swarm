# CVE Index Population Guide

## What Was Done

✅ **Created `populate_cve_index.py`** - Script to populate the critical `resource_type_cve_index` table

✅ **Populated index with test data** - 36 index entries from 6 test CVEs

## Current Status

```
Total CVEs in database: 2,720
CVEs with product information: 6 (0.2%)
Index entries: 36
```

⚠️ **Only 6 out of 2,720 CVEs have product information** - The remaining 2,714 CVEs need enrichment before they can be indexed and matched.

## What is resource_type_cve_index?

This is the **CRITICAL INDEX TABLE** that enables CVE matching. The CVE adapter uses a SQL JOIN:

```sql
SELECT c.* FROM cves c
JOIN resource_type_cve_index i ON c.cve_id = i.cve_id
WHERE i.resource_type = ? AND i.software_keyword LIKE ?
```

**Without index entries, CVE matching returns ZERO results even if CVE records exist!**

The index maps:
- **Resource types** (from Terraform parser) → CVE IDs
- **Software keywords** (product names) → CVE IDs

Example entries:
```
database.rds → CVE-2021-32027 (postgres)
aws_db_instance → CVE-2021-32027 (postgres)
compute.database → CVE-2021-32027 (postgres)
other.unknown → CVE-2021-32027 (postgres)
```

## How the Script Works

### 1. Resource Type Mappings

The script maintains mappings of software to resource types:

```python
RESOURCE_TYPE_MAPPINGS = {
    'postgres': [
        'database.rds',
        'database.postgresql',
        'aws_db_instance',
        'aws_rds_instance',
        'compute.database',
        'other.unknown',  # Current parser fallback
    ],
    'mysql': [...],
    'redis': [...],
    'kubernetes': [...],
    # ... 30+ software types
}
```

### 2. CVE Product Extraction

For each CVE with `affected_products_json` data:

```python
# CVE record has:
affected_products_json = '["postgresql", "postgres"]'

# Script extracts:
software_names = ['postgresql', 'postgres']

# For each software, gets resource types:
resource_types = get_resource_types_for_software('postgres')
# Returns: ['database.rds', 'aws_db_instance', ...]

# Creates index entry for each combination:
('database.rds', 'CVE-2021-32027', 'postgres')
('aws_db_instance', 'CVE-2021-32027', 'postgres')
...
```

### 3. Index Population

Creates comprehensive mappings to maximize match probability:
- 1 CVE with 2 products (postgres, postgresql)
- 6 resource types per product
- = 12 index entries per CVE

This ensures CVE matches regardless of:
- Parser resource type classification
- Product name variations (postgres vs postgresql)
- Infrastructure evolution (parser improvements)

## Usage

### Check current status
```bash
python3 populate_cve_index.py --status
```

### Dry run (see what would happen)
```bash
python3 populate_cve_index.py --dry-run
```

### Populate the index
```bash
python3 populate_cve_index.py
```

### Force repopulation
```bash
python3 populate_cve_index.py --force
```

## What Happens After Population

With the index populated:

1. **Parser** extracts asset info:
   ```python
   {
       'id': 'aws_db_instance.postgres',
       'type': 'other.unknown',
       'engine': 'postgres',
       'engine_version': '13.3'
   }
   ```

2. **CVE Adapter** queries with index:
   ```python
   resource_type = 'other.unknown'
   software = 'postgres'
   version = '13.3'
   
   # SQL query:
   # SELECT c.* FROM cves c
   # JOIN resource_type_cve_index i ON c.cve_id = i.cve_id
   # WHERE i.resource_type = 'other.unknown'
   #   AND i.software_keyword LIKE '%postgres%'
   ```

3. **Match found**:
   ```python
   MatchedVuln(
       vuln_id='CVE-2021-32027',
       vuln_type='CVE',
       resource_id='aws_db_instance.postgres',
       cvss_score=8.8,
       ...
   )
   ```

## Next Steps to Enable Production CVE Matching

### Immediate: Enrich CVE Records with Product Data

The 2,714 existing CVEs need `affected_products_json` populated. Options:

#### Option 1: Use NVD API (Recommended)

Create script to query NVD for each CVE:

```python
import requests

def enrich_cve_from_nvd(cve_id):
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    response = requests.get(url)
    data = response.json()
    
    # Extract CPE configurations
    cpes = extract_cpes(data)
    products = extract_products_from_cpes(cpes)
    
    # Update database
    db.execute('''
        UPDATE cves
        SET affected_products_json = ?,
            affected_versions = ?,
            cpe_matches_json = ?
        WHERE cve_id = ?
    ''', (
        json.dumps(products),
        extract_version_range(cpes),
        json.dumps(cpes),
        cve_id
    ))
```

**Rate limits**:
- Without API key: 5 requests per 30 seconds
- With API key: 50 requests per 30 seconds
- For 2,714 CVEs: ~90 minutes without key, ~9 minutes with key

#### Option 2: Use OSV Database

Open Source Vulnerabilities (OSV) provides structured data:

```bash
# Download OSV database
curl -o osv-database.zip https://osv-vulnerabilities.storage.googleapis.com/...

# Parse and import
python3 import_osv_data.py
```

#### Option 3: Manual Entry for Critical Software

Focus on commonly used software:

```python
# Add high-value CVEs manually
critical_cves = [
    {
        'cve_id': 'CVE-2021-44228',  # Log4Shell
        'affected_products_json': '["log4j", "apache-log4j"]',
        'affected_versions': '>=2.0-beta9 <=2.14.1',
    },
    {
        'cve_id': 'CVE-2022-22965',  # Spring4Shell
        'affected_products_json': '["spring-framework", "spring"]',
        'affected_versions': '>=5.3.0 <=5.3.17',
    },
    # ... top 100 critical CVEs
]
```

### After Enrichment: Repopulate Index

Once CVEs have product data:

```bash
# Repopulate index with all enriched CVEs
python3 populate_cve_index.py --force
```

This will create thousands of index entries enabling comprehensive CVE matching.

### Update Parser for Better Resource Type Detection

Current issue: `aws_db_instance` classified as `other.unknown`

**Fix needed** in `backend/app/parsers/terraform_parser.py`:

```python
# Add database resource handler
def _handle_aws_db_instance(self, resource_name: str, config: dict) -> Asset:
    return Asset(
        id=resource_name,
        type='database.rds',  # Not 'other.unknown'!
        engine=config.get('engine'),  # Promote to top level
        engine_version=config.get('engine_version'),  # Extract this!
        ...
    )
```

## Resource Type Mappings Included

The script includes mappings for:

### Databases (11 types)
- PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Aurora
- Redis, Memcached, MongoDB

### Container & Orchestration (2 types)
- Kubernetes, Docker

### Runtimes (7 types)
- Node.js, Python, Java, Ruby, Go, .NET

### Web Servers (3 types)
- Nginx, Apache, Tomcat

### Message Queues (3 types)
- RabbitMQ, Kafka, ActiveMQ

### Resource Type Variations Per Software

Each software maps to 4-6 resource types:
- Cloud-specific: `aws_db_instance`, `aws_rds_instance`
- Generic: `database.rds`, `compute.database`
- Fallback: `other.unknown` (current parser behavior)

## Testing CVE Matching After Population

Use the test script:

```bash
python3 test_cve_final_complete.py
```

Expected output:
```
CVE vulnerabilities: 3 ✅
  ✓ CVE-2021-32027 (PostgreSQL 13.3)
  ✓ CVE-2021-32028 (PostgreSQL 13.3)
  ✓ CVE-2022-21245 (MySQL 5.7.38)
```

## Troubleshooting

### No CVEs matched despite index population

**Check 1: Do CVEs have product data?**
```sql
SELECT COUNT(*) FROM cves WHERE affected_products_json != '[]';
```

**Check 2: Are there index entries?**
```sql
SELECT COUNT(*) FROM resource_type_cve_index;
```

**Check 3: Does parser extract engine fields?**
```python
# Should be top-level, not nested in properties
asset['engine'] = 'postgres'
asset['engine_version'] = '13.3'
```

### CVE matches but no enrichment (edb_ids, nuclei_templates)

This is a separate enrichment pipeline. CVE matching works, but exploit enrichment requires:
1. ExploitDB database/API integration
2. Nuclei template scanning
3. Additional enrichment pass after CVE matching

Currently not implemented but architecture supports it (fields exist in `MatchedVuln`).

## Summary

✅ **Index table population script created**
✅ **Test data indexed successfully (36 entries from 6 CVEs)**
⚠️ **2,714 CVEs need product data enrichment for production use**
⚠️ **Parser needs updates to extract engine/version fields**

The critical infrastructure is now in place. CVE matching will work at scale once:
1. CVEs are enriched with product/version data from NVD/OSV
2. Index is repopulated with `--force`
3. Parser is enhanced to extract database engine fields

## Files Created

- `populate_cve_index.py` - Index population script
- `CVE_INDEX_POPULATION_GUIDE.md` - This guide
- `test_cve_final_complete.py` - Test script showing successful CVE matching
- `test_vulnerable_iac.tf` - Test IaC with known vulnerable software
