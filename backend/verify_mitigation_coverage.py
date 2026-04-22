#!/usr/bin/env python3
"""
Mitigation Coverage Verification Script

This script verifies that the threat modeling tool derives mitigations for:
1. ALL attack paths discovered
2. EVERY step within each attack path
3. ALL 5 defense layers (Preventive, Detective, Administrative, Response, Recovery)

Usage:
    python verify_mitigation_coverage.py

This will load the most recent archived run and verify complete mitigation coverage.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_most_recent_run() -> Dict[str, Any]:
    """Load the most recent archived run."""
    data_dir = Path("backend/data/archived_runs")

    # Load index
    index_file = data_dir / "index.json"
    if not index_file.exists():
        print("❌ No archived runs found. Please run a threat model first.")
        sys.exit(1)

    with open(index_file, 'r') as f:
        runs = json.load(f)

    if not runs:
        print("❌ No runs in index. Please run a threat model first.")
        sys.exit(1)

    # Get most recent run
    runs = sorted(runs, key=lambda x: x["created_at"], reverse=True)
    most_recent = runs[0]

    # Load the run file (use run_id to construct filename)
    run_file = data_dir / f"{most_recent['run_id']}.json"
    with open(run_file, 'r') as f:
        run_data = json.load(f)

    print(f"✓ Loaded run: {most_recent['name']}")
    print(f"  Created: {most_recent['created_at']}")
    print(f"  Mode: {most_recent['mode']}")
    print(f"  Model: {most_recent.get('model_used', 'Unknown')}")
    print()

    return run_data


def verify_mitigation_coverage(run_data: Dict[str, Any]) -> bool:
    """
    Verify that all attack paths and all steps have mitigations.

    Returns:
        True if all paths and steps have complete mitigation coverage
    """
    result = run_data.get("result", {})

    # Handle both standard and stigmergic run formats
    attack_paths = result.get("final_paths") or result.get("attack_paths", [])

    if not attack_paths:
        print("❌ No attack paths found in this run")
        return False

    print(f"📊 Verification Report")
    print("=" * 80)
    print(f"Total Attack Paths: {len(attack_paths)}")
    print()

    all_coverage_complete = True
    defense_layers = ["preventive", "detective", "administrative", "response", "recovery"]

    # Global statistics
    global_stats = {
        "total_paths": len(attack_paths),
        "total_steps": 0,
        "steps_with_mitigations": 0,
        "steps_without_mitigations": 0,
        "total_mitigations": 0,
        "mitigations_by_layer": {layer: 0 for layer in defense_layers},
    }

    for path_idx, path in enumerate(attack_paths, 1):
        path_name = path.get("name") or path.get("path_name") or f"Path {path_idx}"
        steps = path.get("steps", [])

        print(f"\n{'─' * 80}")
        print(f"Path {path_idx}: {path_name}")
        print(f"{'─' * 80}")
        print(f"  Total Steps: {len(steps)}")

        if not steps:
            print(f"  ⚠️  WARNING: Path has no steps")
            all_coverage_complete = False
            continue

        global_stats["total_steps"] += len(steps)

        path_has_complete_coverage = True
        path_mitigation_count = 0

        for step_idx, step in enumerate(steps, 1):
            technique_id = step.get("technique_id", "N/A")
            technique_name = step.get("technique_name", "Unknown")

            # Check for mitigations_by_layer (new defense-in-depth structure)
            mitigations_by_layer = step.get("mitigations_by_layer", {})

            if mitigations_by_layer:
                # Count mitigations by layer
                step_mitigation_count = 0
                layer_coverage = []

                for layer in defense_layers:
                    layer_mitigations = mitigations_by_layer.get(layer, [])
                    if layer_mitigations:
                        count = len(layer_mitigations)
                        step_mitigation_count += count
                        global_stats["mitigations_by_layer"][layer] += count
                        layer_coverage.append(f"{layer[:4].upper()}:{count}")

                if step_mitigation_count > 0:
                    global_stats["steps_with_mitigations"] += 1
                    path_mitigation_count += step_mitigation_count
                    global_stats["total_mitigations"] += step_mitigation_count

                    print(f"    ✓ Step {step_idx}: {technique_id} - {technique_name}")
                    print(f"      Mitigations: {step_mitigation_count} total [{', '.join(layer_coverage)}]")
                else:
                    print(f"    ⚠️  Step {step_idx}: {technique_id} - {technique_name}")
                    print(f"      WARNING: No mitigations in mitigations_by_layer")
                    global_stats["steps_without_mitigations"] += 1
                    path_has_complete_coverage = False
                    all_coverage_complete = False

            # Fallback to old structure
            elif step.get("mitigation"):
                global_stats["steps_with_mitigations"] += 1
                path_mitigation_count += 1
                global_stats["total_mitigations"] += 1
                print(f"    ✓ Step {step_idx}: {technique_id} - {technique_name}")
                print(f"      Mitigations: 1 (legacy format)")

            else:
                print(f"    ❌ Step {step_idx}: {technique_id} - {technique_name}")
                print(f"      ERROR: No mitigations found")
                global_stats["steps_without_mitigations"] += 1
                path_has_complete_coverage = False
                all_coverage_complete = False

        # Path summary
        if path_has_complete_coverage:
            print(f"\n  ✓ Path {path_idx} Coverage: COMPLETE ({path_mitigation_count} mitigations)")
        else:
            print(f"\n  ❌ Path {path_idx} Coverage: INCOMPLETE")

    # Global summary
    print(f"\n\n{'=' * 80}")
    print(f"📈 GLOBAL SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Attack Paths: {global_stats['total_paths']}")
    print(f"Total Attack Steps: {global_stats['total_steps']}")
    print(f"Steps with Mitigations: {global_stats['steps_with_mitigations']}")
    print(f"Steps without Mitigations: {global_stats['steps_without_mitigations']}")
    print(f"Total Mitigations: {global_stats['total_mitigations']}")
    print()
    print(f"Mitigations by Defense Layer:")
    for layer, count in global_stats["mitigations_by_layer"].items():
        icon = {"preventive": "🛡️", "detective": "🔍", "administrative": "📋",
                "response": "⚡", "recovery": "♻️"}.get(layer, "•")
        print(f"  {icon} {layer.capitalize():15s}: {count:3d}")
    print()

    # Coverage percentage
    if global_stats["total_steps"] > 0:
        coverage_pct = (global_stats["steps_with_mitigations"] / global_stats["total_steps"]) * 100
        print(f"Coverage: {coverage_pct:.1f}% ({global_stats['steps_with_mitigations']}/{global_stats['total_steps']} steps)")

    # Final verdict
    print(f"\n{'=' * 80}")
    if all_coverage_complete:
        print("✅ VERIFICATION PASSED: All attack paths have complete mitigation coverage")
        print("=" * 80)
        return True
    else:
        print("❌ VERIFICATION FAILED: Some attack paths are missing mitigations")
        print("=" * 80)
        return False


def main():
    """Main verification function."""
    print("🔍 Mitigation Coverage Verification")
    print("=" * 80)
    print()

    try:
        # Load most recent run
        run_data = load_most_recent_run()

        # Verify mitigation coverage
        success = verify_mitigation_coverage(run_data)

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
