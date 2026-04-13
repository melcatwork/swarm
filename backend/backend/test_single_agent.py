#!/usr/bin/env python3
"""Test script for single agent endpoint debugging."""

import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.parsers.terraform_parser import TerraformParser
from app.swarm import PersonaRegistry


async def test_single_agent_parsing():
    """Test the parsing and persona selection."""
    print("=" * 60)
    print("Testing Single Agent Pipeline Components")
    print("=" * 60)

    # Test 1: Parse the Terraform file
    print("\n[1] Testing Terraform parsing...")
    try:
        with open('../samples/ecommerce-platform.tf', 'r') as f:
            content = f.read()

        parser = TerraformParser()
        asset_graph = parser.parse(content)
        print(f"✓ Parsed successfully: {len(asset_graph.assets)} assets")

        # Test model_dump
        asset_graph_dict = asset_graph.model_dump()
        print(f"✓ model_dump() successful, type: {type(asset_graph_dict)}")
        print(f"✓ Keys: {list(asset_graph_dict.keys())}")

    except Exception as e:
        print(f"✗ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Load personas
    print("\n[2] Testing persona loading...")
    try:
        registry = PersonaRegistry()
        all_personas = registry.get_all()
        print(f"✓ Loaded {len(all_personas)} personas")

        # Test get_by_name
        agent_name = "insider_threat"
        selected_persona = registry.get_by_name(agent_name)
        if selected_persona is None:
            print(f"✗ Persona '{agent_name}' not found")
            return False

        print(f"✓ Found persona: {selected_persona['display_name']}")
        print(f"✓ Persona type: {type(selected_persona)}")
        print(f"✓ Persona keys: {list(selected_persona.keys())}")

    except Exception as e:
        print(f"✗ Persona loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Create exploration summary
    print("\n[3] Testing exploration summary creation...")
    try:
        exploration_summary = {
            "agents_used": 1,
            "agent_name": agent_name,
            "agent_display_name": selected_persona["display_name"],
            "raw_paths_found": 0,
            "execution_time_seconds": 0.0,
            "threat_intel_items": 0,
        }
        print(f"✓ Created exploration_summary")
        print(f"✓ Type: {type(exploration_summary)}")
        print(f"✓ Contents: {exploration_summary}")

        # Test if we can modify it
        exploration_summary["test_key"] = "test_value"
        print(f"✓ Can modify exploration_summary")

    except Exception as e:
        print(f"✗ Exploration summary failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = asyncio.run(test_single_agent_parsing())
    sys.exit(0 if result else 1)
