#!/usr/bin/env python3
"""Quick test of single endpoint to see confirmed findings"""
import httpx
from pathlib import Path

TF_FILE = Path('samples/capital-one-breach-replica.tf')
BASE_URL = 'http://localhost:8000'

with open(TF_FILE, 'rb') as f:
    files = {'file': ('test.tf', f, 'text/plain')}
    form_data = {'agent_name': 'cloud_native_attacker'}
    resp = httpx.post(
        f'{BASE_URL}/api/swarm/run/single',
        files=files,
        data=form_data,
        timeout=300,
    )

print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    confirmed = data.get('confirmed_findings', [])
    print(f"Confirmed findings: {len(confirmed)}")
    if confirmed:
        for f in confirmed[:3]:
            print(f"  - {f.get('vuln_id')} on {f.get('resource_id')}")
    else:
        print("ERROR: No confirmed findings in response!")
        print(f"Response keys: {list(data.keys())}")
        # Check if exploration_summary has it
        if 'exploration_summary' in data:
            exp = data['exploration_summary']
            print(f"exploration_summary keys: {list(exp.keys())}")
else:
    print(f"ERROR: {resp.text[:500]}")
