#!/usr/bin/env python3
"""Verify threat intelligence database contents."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.swarm.vuln_intel.intel_db import IntelDatabase

def main():
    db = IntelDatabase()

    print("=" * 80)
    print("THREAT INTELLIGENCE DATABASE VERIFICATION")
    print("=" * 80)
    print()

    # Get sync state
    state = db.get_sync_state()
    print("SYNC STATE:")
    for src, info in state.items():
        print(f"  {src}: {info['record_count']} records (last sync: {info['last_sync']})")
    print()

    # Test CVE query for postgres
    print("CVE QUERY TEST: aws_db_instance with postgres")
    cves = db.get_cves_for_resource('aws_db_instance', 'postgres', '', min_cvss=6.0, limit=5)
    print(f"  Found {len(cves)} CVEs:")
    for c in cves[:5]:
        print(f"    {c.cve_id} | CVSS:{c.cvss_v3_score} | KEV:{c.in_kev} | EPSS:{c.epss_score:.4f}")
        print(f"      {c.description[:100]}...")
    print()

    # Test abuse pattern query
    print("ABUSE PATTERN TEST: aws_instance")
    abuses = db.get_abuse_patterns_for_resource('aws_instance')
    print(f"  Found {len(abuses)} abuse patterns:")
    for a in abuses[:5]:
        print(f"    {a.abuse_id}: {a.name}")
        print(f"      Technique: {a.technique_id} | Phase: {a.kill_chain_phase}")
    print()

    # Test KEV entries
    kev_entries = db.get_kev_entries()
    print(f"KNOWN EXPLOITED VULNERABILITIES: {len(kev_entries)} total")
    print(f"  Top 5 by EPSS score:")
    for k in kev_entries[:5]:
        print(f"    {k.cve_id} | EPSS:{k.epss_score:.4f} | Added:{k.kev_date_added}")
    print()

    # Test S3 bucket patterns
    print("ABUSE PATTERN TEST: aws_s3_bucket")
    s3_abuses = db.get_abuse_patterns_for_resource('aws_s3_bucket')
    print(f"  Found {len(s3_abuses)} abuse patterns:")
    for a in s3_abuses[:3]:
        print(f"    {a.abuse_id}: {a.name}")
    print()

    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
