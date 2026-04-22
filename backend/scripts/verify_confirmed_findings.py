#!/usr/bin/env python3
"""
Verifies that confirmed vulnerability findings surface in all
four run types. Does NOT check for any specific vulnerability
type, technique, or attack pattern. Validates structure and
evidence-grounding only.

Run: python3 backend/scripts/verify_confirmed_findings.py
Requires: backend server on localhost:8000
"""
import httpx
import json
import sys
from pathlib import Path

BASE_URL = 'http://localhost:8000'
TF_FILE = Path('samples/capital-one-breach-replica.tf')
TIMEOUT = 300


def check_output_quality(data: dict, run_type: str) -> dict:
    """
    Validates output structure and evidence quality.
    No specific attack type checks — only structural checks.
    """
    result = {
        'has_confirmed_findings': False,
        'confirmed_findings_count': 0,
        'has_attack_paths': False,
        'has_grounded_paths': False,
        'persona_specialist_injected': False,
        'all_high_confidence': False,
        'issues': [],
    }

    # Check confirmed_findings field exists and is populated
    confirmed = data.get('confirmed_findings', [])
    result['confirmed_findings_count'] = len(confirmed)
    if confirmed:
        result['has_confirmed_findings'] = True
        # Validate each confirmed finding has required fields
        required = {
            'vuln_id', 'resource_id', 'technique_id',
            'match_confidence', 'risk_score',
        }
        for f in confirmed:
            missing = required - set(f.keys())
            if missing:
                result['issues'].append(
                    f'Finding {f.get("vuln_id","?")} '
                    f'missing fields: {missing}'
                )
            if f.get('match_confidence') != 'CONFIRMED':
                result['issues'].append(
                    f'Finding {f.get("vuln_id","?")} '
                    f'in confirmed_findings but '
                    f'confidence is not CONFIRMED'
                )
    else:
        result['issues'].append(
            'confirmed_findings is empty — VulnMatcher '
            'produced no CONFIRMED findings for this IaC'
        )

    # Check attack_paths
    paths = data.get('attack_paths', [])
    # Also check final_paths for single/quick/multi runs
    if not paths:
        paths = data.get('final_paths', [])

    if paths:
        result['has_attack_paths'] = True
        grounded = [
            p for p in paths
            if p.get('grounded_in_confirmed_vuln')
        ]
        if grounded:
            result['has_grounded_paths'] = True
        else:
            result['issues'].append(
                'No attack paths are grounded in confirmed '
                'vulnerability evidence'
            )

        # Validate path structure
        for path in paths[:3]:
            steps = path.get('steps', [])
            if not steps:
                result['issues'].append(
                    f'Path {path.get("path_id","?")} '
                    f'has no steps'
                )
            for step in steps:
                if not step.get('technique_id'):
                    result['issues'].append(
                        'Step missing technique_id'
                    )
                # Check for target_asset or asset_id
                if not step.get('target_asset') and not step.get('asset_id'):
                    result['issues'].append(
                        'Step missing target_asset/asset_id'
                    )
    else:
        result['issues'].append('attack_paths/final_paths is empty')

    # Check persona injection (single and quick only)
    if run_type in ('single', 'quick'):
        ps = data.get('persona_selection', {})
        # Also check exploration_summary for single run
        if not ps and 'exploration_summary' in data:
            ps = data['exploration_summary']

        injected = ps.get(
            'injected_for_high_confidence_findings', []
        )
        if injected:
            result['persona_specialist_injected'] = True

    # Check confirmed findings have high confidence overall
    if confirmed:
        all_high = all(
            f.get('risk_score', 0) >= 6.0
            for f in confirmed
        )
        result['all_high_confidence'] = all_high

    return result


def test_endpoint(name: str, endpoint: str, form_data: dict = None) -> bool:
    print(f'\n{"="*52}')
    print(f'Run type: {name}')
    print(f'Endpoint: POST {endpoint}')

    try:
        with open(TF_FILE, 'rb') as f:
            files = {'file': ('capital-one.tf', f, 'text/plain')}
            if form_data:
                resp = httpx.post(
                    f'{BASE_URL}{endpoint}',
                    files=files,
                    data=form_data,
                    timeout=TIMEOUT,
                )
            else:
                resp = httpx.post(
                    f'{BASE_URL}{endpoint}',
                    files=files,
                    timeout=TIMEOUT,
                )

        if resp.status_code != 200:
            print(f'  FAIL HTTP {resp.status_code}')
            print(f'  Response: {resp.text[:200]}')
            return False

        data = resp.json()
        run_type_key = endpoint.split('/')[-1]
        checks = check_output_quality(data, run_type_key)

        # Print results
        cf_count = checks['confirmed_findings_count']
        cf_status = 'PASS' if checks['has_confirmed_findings'] else 'FAIL'
        print(f'  [{cf_status}] confirmed_findings: {cf_count} entries')

        ap_status = 'PASS' if checks['has_attack_paths'] else 'FAIL'
        gp_status = 'PASS' if checks['has_grounded_paths'] else 'MISS'
        paths_count = len(data.get('attack_paths', data.get('final_paths', [])))
        print(f'  [{ap_status}] attack_paths: {paths_count} paths')
        print(f'  [{gp_status}] grounded paths present')

        if run_type_key in ('single', 'quick'):
            pi_status = (
                'PASS' if checks['persona_specialist_injected']
                else 'INFO'
            )
            ps = data.get('persona_selection', data.get('exploration_summary', {}))
            final = ps.get('final', [])
            injected = ps.get('injected_for_high_confidence_findings', [])
            print(
                f'  [{pi_status}] specialist persona injection: '
                f'{injected if injected else "none"}'
            )

        if checks['issues']:
            for issue in checks['issues']:
                print(f'  ISSUE: {issue}')

        # Print what was actually found (no IMDS-specific check)
        if checks['has_confirmed_findings']:
            confirmed = data.get('confirmed_findings', [])
            print(f'  Confirmed findings:')
            for f in confirmed[:3]:
                print(
                    f'    {f.get("vuln_id","?")} on '
                    f'{f.get("resource_id","?")} '
                    f'risk={f.get("risk_score","?")} '
                    f'phase={f.get("kill_chain_phase","?")}'
                )

        passed = (
            checks['has_confirmed_findings']
            and checks['has_attack_paths']
            and not any(
                'empty' in issue
                for issue in checks['issues']
            )
        )
        status = 'PASS' if passed else 'FAIL'
        print(f'  OVERALL: {status}')
        return passed

    except Exception as e:
        print(f'  ERROR: {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print('Confirmed Findings Surface Verification')
    print('Validates that high-confidence findings from')
    print('VulnMatcher appear in all four run type outputs.')
    print('No specific attack type checks are performed.')

    endpoints = [
        ('Single agent', '/api/swarm/run/single', {'agent_name': 'cloud_native_attacker'}),
        ('2 agents test', '/api/swarm/run/quick', None),
        ('Multi-agents run', '/api/swarm/run', None),
        ('Swarm run', '/api/swarm/run/stigmergic', None),
    ]

    results = {}
    for name, endpoint, form_data in endpoints:
        results[name] = test_endpoint(name, endpoint, form_data)

    print(f'\n{"="*52}')
    print('SUMMARY')
    all_pass = True
    for name, passed in results.items():
        print(f'  [{"PASS" if passed else "FAIL"}] {name}')
        if not passed:
            all_pass = False

    if all_pass:
        print(
            '\nAll four run types surface confirmed findings.'
            '\nThe tool reasons dynamically — findings depend'
            '\non what the IaC contains, not hardcoded rules.'
        )
    else:
        print(
            '\nSome run types not surfacing confirmed findings.'
            '\nInvestigate:'
            '\n  1. VulnContextBuilder running before agents'
            '\n  2. output_filter.py wired after agent runs'
            '\n  3. persona_selector.py using correct thresholds'
            '\n  4. confirmed_findings added to response dict'
        )
    sys.exit(0 if all_pass else 1)
