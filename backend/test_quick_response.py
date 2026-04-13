"""
Quick test to check if /api/swarm/run/quick returns final_paths correctly
"""
import requests
import json

def test_backend_response():
    """Test if backend returns proper structure"""

    # Check if backend is running
    try:
        health = requests.get('http://localhost:8000/api/health', timeout=5)
        print(f"✓ Backend is running: {health.json()}")
    except Exception as e:
        print(f"✗ Backend not reachable: {e}")
        return

    # Check if we have any archived runs to inspect
    try:
        archives = requests.get('http://localhost:8000/api/archive/runs', timeout=5)
        if archives.status_code == 200:
            runs = archives.json()
            if runs and len(runs) > 0:
                print(f"\n✓ Found {len(runs)} archived runs")
                latest_run = runs[0]
                print(f"  Latest run: {latest_run['metadata']['name']}")
                print(f"  Paths count: {latest_run['metadata']['paths_count']}")
                print(f"  Mode: {latest_run['metadata']['mode']}")

                # Get full run data
                run_id = latest_run['metadata']['run_id']
                full_run = requests.get(f'http://localhost:8000/api/archive/runs/{run_id}', timeout=5)
                if full_run.status_code == 200:
                    run_data = full_run.json()
                    result = run_data.get('result', {})

                    print(f"\n=== Latest Run Structure ===")
                    print(f"Status: {result.get('status')}")
                    print(f"Has asset_graph: {bool(result.get('asset_graph'))}")
                    print(f"Has final_paths: {bool(result.get('final_paths'))}")

                    if 'final_paths' in result:
                        paths = result['final_paths']
                        print(f"\n✓ final_paths exists with {len(paths)} paths")

                        if len(paths) > 0:
                            first_path = paths[0]
                            print(f"\nFirst path structure:")
                            print(f"  - name: {first_path.get('name', 'N/A')}")
                            print(f"  - threat_actor: {first_path.get('threat_actor', 'N/A')}")
                            print(f"  - steps: {len(first_path.get('steps', []))} steps")

                            if 'steps' in first_path and len(first_path['steps']) > 0:
                                first_step = first_path['steps'][0]
                                print(f"\nFirst step structure:")
                                print(f"  - technique_id: {first_step.get('technique_id', 'N/A')}")
                                print(f"  - technique_name: {first_step.get('technique_name', 'N/A')}")
                                print(f"  - target_asset: {first_step.get('target_asset', 'N/A')}")

                                # Check for fallback values
                                if first_step.get('technique_id') == 'T1000':
                                    print("\n⚠️  WARNING: First step has fallback technique_id (T1000)")
                                if first_step.get('target_asset') == 'unknown_asset':
                                    print("⚠️  WARNING: First step has fallback target_asset (unknown_asset)")
                        else:
                            print("\n✗ final_paths array is empty!")
                    else:
                        print("\n✗ final_paths key not found in result!")
                        print(f"\nAvailable keys in result: {list(result.keys())}")
            else:
                print("\n✗ No archived runs found. Run a threat model first.")
    except Exception as e:
        print(f"✗ Error checking archives: {e}")

if __name__ == "__main__":
    test_backend_response()
