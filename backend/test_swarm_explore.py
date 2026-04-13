#!/usr/bin/env python3
"""
Test script for swarm exploration endpoints.

Tests endpoint availability and request/response structure.
Does NOT run actual LLM calls (too expensive and slow for testing).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_endpoint_structure():
    """Test that exploration endpoints are properly defined."""
    print("=" * 80)
    print("  Testing Swarm Exploration Endpoint Structure")
    print("=" * 80)

    try:
        from app.routers.swarm import router, ExploreRequest, ExploreResponse

        # Check that router has the expected endpoints
        routes = [route.path for route in router.routes]

        expected_routes = [
            "/personas",
            "/personas/enabled",
            "/personas/{name}",
            "/explore",
            "/explore/quick",
        ]

        print("\n✓ Router imported successfully")
        print(f"  Found {len(routes)} routes")

        # Check for exploration endpoints
        explore_found = any("/explore" in route for route in routes)
        explore_quick_found = any("/explore/quick" in route for route in routes)

        if explore_found:
            print("✓ /explore endpoint defined")
        else:
            print("✗ /explore endpoint not found")

        if explore_quick_found:
            print("✓ /explore/quick endpoint defined")
        else:
            print("✗ /explore/quick endpoint not found")

        # Test request model
        print("\n✓ ExploreRequest model imported")
        print("  Required fields:")
        for field_name, field in ExploreRequest.model_fields.items():
            print(f"    - {field_name}: {field.annotation}")

        # Test response model
        print("\n✓ ExploreResponse model imported")
        print("  Response fields:")
        for field_name, field in ExploreResponse.model_fields.items():
            required = field.is_required()
            req_marker = "required" if required else "optional"
            print(f"    - {field_name} ({req_marker}): {field.annotation}")

        return explore_found and explore_quick_found

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_threat_intel_context():
    """Test threat intelligence context building."""
    print("\n" + "=" * 80)
    print("  Testing Threat Intel Context Building")
    print("=" * 80)

    try:
        from app.routers.swarm import _build_threat_intel_context

        context, count = _build_threat_intel_context()

        print(f"✓ Built threat intel context")
        print(f"  Context length: {len(context)} characters")
        print(f"  Items used: {count}")
        print(f"  Preview: {context[:150]}...")

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_request_validation():
    """Test request model validation."""
    print("\n" + "=" * 80)
    print("  Testing Request Validation")
    print("=" * 80)

    try:
        from app.routers.swarm import ExploreRequest

        # Valid request
        valid_request = ExploreRequest(
            asset_graph={
                "assets": [
                    {
                        "id": "test.asset",
                        "name": "test",
                        "type": "compute.vm",
                        "cloud": "aws",
                        "service": "EC2",
                        "properties": {},
                        "data_sensitivity": "medium",
                        "trust_boundary": "private",
                    }
                ],
                "relationships": [],
                "trust_boundaries": [],
                "metadata": {"format": "terraform"},
            }
        )

        print("✓ Valid request accepted")
        print(f"  Asset count: {len(valid_request.asset_graph['assets'])}")

        # Test required fields
        try:
            invalid_request = ExploreRequest()
            print("✗ Empty request should have failed validation")
            return False
        except Exception:
            print("✓ Empty request correctly rejected")

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_imports():
    """Test that all required imports work."""
    print("\n" + "=" * 80)
    print("  Testing Module Imports")
    print("=" * 80)

    imports_to_test = [
        ("app.swarm", ["PersonaRegistry"]),
        ("app.swarm.crews", ["build_exploration_crew", "parse_exploration_results"]),
        ("app.parsers", ["AssetGraph"]),
        ("app.threat_intel.core.feed_manager", ["FeedManager"]),
    ]

    all_passed = True

    for module_name, items in imports_to_test:
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                if not hasattr(module, item):
                    print(f"✗ {module_name}.{item} not found")
                    all_passed = False
            print(f"✓ {module_name}: {', '.join(items)}")
        except Exception as e:
            print(f"✗ {module_name}: {e}")
            all_passed = False

    return all_passed


def main():
    """Run all tests."""
    print("Swarm Exploration Endpoint Test Suite\n")

    results = []
    results.append(("Module Imports", test_imports()))
    results.append(("Endpoint Structure", test_endpoint_structure()))
    results.append(("Threat Intel Context", test_threat_intel_context()))
    results.append(("Request Validation", test_request_validation()))

    # Summary
    print("\n" + "=" * 80)
    print("  Test Summary")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")

    if passed == total:
        print(f"\n✓ All tests passed ({passed}/{total})")
        print("\nThe exploration endpoints are ready:")
        print("  POST /api/swarm/explore - Full analysis (all enabled personas)")
        print("  POST /api/swarm/explore/quick - Quick analysis (2 personas)")
        print("\nREQUIRED: Set ANTHROPIC_API_KEY in .env before running")
        print("\nWARNING: These endpoints make real API calls and are expensive!")
        print("  - Full exploration: ~$0.20+ per run (13 agents)")
        print("  - Quick exploration: ~$0.03+ per run (2 agents)")
        print("  - Each run takes several minutes")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
