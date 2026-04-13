#!/usr/bin/env python3
"""
Test script for persona management API.

Tests CRUD operations on agent personas.
"""

import requests
import json


BASE_URL = "http://localhost:8000"


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    else:
        print("-" * 80)


def test_get_all_personas():
    """Test GET /api/swarm/personas"""
    print_separator("Testing GET /api/swarm/personas")

    response = requests.get(f"{BASE_URL}/api/swarm/personas")

    if response.status_code == 200:
        personas = response.json()
        print(f"✓ Retrieved {len(personas)} personas")

        # Group by category
        threat_actors = [
            name
            for name, p in personas.items()
            if p.get("category") == "threat_actor"
        ]
        archetypes = [
            name for name, p in personas.items() if p.get("category") == "archetype"
        ]

        print(f"  Threat Actors: {len(threat_actors)}")
        for name in threat_actors:
            status = "✓" if personas[name]["enabled"] else "✗"
            protected = "🔒" if personas[name]["protected"] else "  "
            print(f"    {status} {protected} {personas[name]['display_name']}")

        print(f"  Archetypes: {len(archetypes)}")
        for name in archetypes:
            status = "✓" if personas[name]["enabled"] else "✗"
            protected = "🔒" if personas[name]["protected"] else "  "
            print(f"    {status} {protected} {personas[name]['display_name']}")

        return personas
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return None


def test_get_enabled_personas():
    """Test GET /api/swarm/personas/enabled"""
    print_separator("Testing GET /api/swarm/personas/enabled")

    response = requests.get(f"{BASE_URL}/api/swarm/personas/enabled")

    if response.status_code == 200:
        enabled = response.json()
        print(f"✓ Retrieved {len(enabled)} enabled personas")
        for name, persona in list(enabled.items())[:5]:
            print(f"  - {persona['display_name']} ({persona['category']})")
        if len(enabled) > 5:
            print(f"  ... and {len(enabled) - 5} more")
        return enabled
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return None


def test_create_custom_persona():
    """Test POST /api/swarm/personas"""
    print_separator("Testing POST /api/swarm/personas (Create Custom)")

    custom_persona = {
        "display_name": "Ransomware Operator",
        "category": "threat_actor",
        "role": "Ransomware Deployment and Extortion Specialist",
        "goal": "Identify attack paths for ransomware deployment, data exfiltration before encryption, and maximum business disruption",
        "backstory": "You are a sophisticated ransomware operator who combines data theft with encryption. You target backup systems, shadow copies, and offline storage to prevent recovery. You exfiltrate sensitive data before encryption to enable double extortion.",
        "ttp_focus": ["T1486", "T1490", "T1489", "T1491", "T1529", "T1485", "T1486"],
    }

    response = requests.post(
        f"{BASE_URL}/api/swarm/personas?name=custom_ransomware",
        json=custom_persona,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Created custom persona: {result['persona']}")
        print(f"  Message: {result['message']}")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return False


def test_get_single_persona():
    """Test GET /api/swarm/personas/{name}"""
    print_separator("Testing GET /api/swarm/personas/apt29_cozy_bear")

    response = requests.get(f"{BASE_URL}/api/swarm/personas/apt29_cozy_bear")

    if response.status_code == 200:
        persona = response.json()
        print(f"✓ Retrieved persona: {persona['display_name']}")
        print(f"  Category: {persona['category']}")
        print(f"  Role: {persona['role']}")
        print(f"  Protected: {persona['protected']}")
        print(f"  Enabled: {persona['enabled']}")
        print(f"  TTP Focus: {', '.join(persona['ttp_focus'][:5])}...")
        return persona
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return None


def test_toggle_persona():
    """Test PUT /api/swarm/personas/{name}/toggle"""
    print_separator("Testing PUT /api/swarm/personas/fin7/toggle")

    # First, disable FIN7
    response = requests.put(
        f"{BASE_URL}/api/swarm/personas/fin7/toggle",
        json={"enabled": False},
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Disabled persona: {result['persona']}")

        # Then re-enable it
        response = requests.put(
            f"{BASE_URL}/api/swarm/personas/fin7/toggle",
            json={"enabled": True},
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Re-enabled persona: {result['persona']}")
            return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return False


def test_update_persona():
    """Test PUT /api/swarm/personas/{name}"""
    print_separator("Testing PUT /api/swarm/personas/custom_ransomware")

    updates = {
        "goal": "Updated goal: Focus on identifying ransomware deployment paths with emphasis on backup destruction and double extortion",
    }

    response = requests.put(
        f"{BASE_URL}/api/swarm/personas/custom_ransomware",
        json=updates,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Updated persona: {result['persona']}")
        print(f"  Message: {result['message']}")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return False


def test_delete_custom_persona():
    """Test DELETE /api/swarm/personas/{name}"""
    print_separator("Testing DELETE /api/swarm/personas/custom_ransomware")

    response = requests.delete(f"{BASE_URL}/api/swarm/personas/custom_ransomware")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Deleted persona: {result['persona']}")
        print(f"  Message: {result['message']}")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return False


def test_delete_protected_persona():
    """Test DELETE /api/swarm/personas/{name} on protected persona"""
    print_separator("Testing DELETE on Protected Persona (Should Fail)")

    response = requests.delete(f"{BASE_URL}/api/swarm/personas/apt29_cozy_bear")

    if response.status_code == 403:
        error = response.json()
        print(f"✓ Correctly rejected deletion with 403 Forbidden")
        print(f"  Error: {error.get('detail', 'No detail')}")
        return True
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        print(response.text)
        return False


def main():
    """Run all tests."""
    print_separator("Persona Management API Test Suite")
    print("Make sure the FastAPI server is running on http://localhost:8000")

    try:
        # Test health check first
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code != 200:
            print("✗ Server is not responding. Please start the server first.")
            return 1
        print("✓ Server is running")
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to server. Please start the server first:")
        print("  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload")
        return 1

    # Run tests
    all_personas = test_get_all_personas()
    enabled_personas = test_get_enabled_personas()
    single_persona = test_get_single_persona()
    created = test_create_custom_persona()
    toggled = test_toggle_persona()
    updated = test_update_persona() if created else False
    deleted = test_delete_custom_persona() if created else False
    protected = test_delete_protected_persona()

    # Summary
    print_separator("Test Summary")
    results = {
        "Get all personas": all_personas is not None,
        "Get enabled personas": enabled_personas is not None,
        "Get single persona": single_persona is not None,
        "Create custom persona": created,
        "Toggle persona": toggled,
        "Update persona": updated,
        "Delete custom persona": deleted,
        "Reject protected deletion": protected,
    }

    passed = sum(results.values())
    total = len(results)

    print(f"Passed: {passed}/{total} tests")
    for test_name, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {test_name}")

    if passed == total:
        print("\n✓ All tests passed!")
        print("\nThe persona management API is working correctly:")
        print("  - Can list all personas")
        print("  - Can filter enabled personas")
        print("  - Can create custom personas")
        print("  - Can toggle personas on/off")
        print("  - Can update persona fields")
        print("  - Can delete custom personas")
        print("  - Protected personas cannot be deleted")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
