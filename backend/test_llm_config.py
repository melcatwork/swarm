#!/usr/bin/env python3
"""
Test script for LLM configuration validation.

Tests that the configuration is properly set up for Bedrock or Anthropic.
Does NOT make actual LLM API calls.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_config_loading():
    """Test that configuration loads correctly."""
    print("=" * 80)
    print("  Testing Configuration Loading")
    print("=" * 80)

    try:
        from app.config import get_settings

        settings = get_settings()

        print(f"\n✓ Settings loaded successfully")
        print(f"  LLM Provider: {settings.LLM_PROVIDER}")

        if settings.LLM_PROVIDER == "bedrock":
            print(f"  Bedrock Model: {settings.BEDROCK_MODEL}")
            print(f"  AWS Region: {settings.AWS_REGION_NAME}")
            token_status = "SET" if settings.AWS_BEARER_TOKEN_BEDROCK else "NOT SET"
            print(f"  Bearer Token: {token_status}")
        elif settings.LLM_PROVIDER == "anthropic":
            print(f"  Anthropic Model: {settings.ANTHROPIC_MODEL}")
            key_status = "SET" if settings.ANTHROPIC_API_KEY else "NOT SET"
            print(f"  API Key: {key_status}")

        return True

    except Exception as e:
        print(f"\n✗ Failed to load settings: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_llm_config_method():
    """Test get_llm_config() method."""
    print("\n" + "=" * 80)
    print("  Testing get_llm_config() Method")
    print("=" * 80)

    try:
        from app.config import get_settings

        settings = get_settings()
        config = settings.get_llm_config()

        print(f"\n✓ LLM config retrieved")
        print(f"  Provider: {config['provider']}")
        print(f"  Model: {config['model']}")

        return True

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        return False


def test_llm_configured_check():
    """Test is_llm_configured() method."""
    print("\n" + "=" * 80)
    print("  Testing is_llm_configured() Method")
    print("=" * 80)

    try:
        from app.config import get_settings

        settings = get_settings()
        is_configured = settings.is_llm_configured()

        status = "✓ CONFIGURED" if is_configured else "✗ NOT CONFIGURED"
        print(f"\n{status}")

        if not is_configured:
            if settings.LLM_PROVIDER == "bedrock":
                print("  → Set AWS_BEARER_TOKEN_BEDROCK in .env")
            elif settings.LLM_PROVIDER == "anthropic":
                print("  → Set ANTHROPIC_API_KEY in .env")

        return True

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        return False


def test_get_llm_helper():
    """Test get_llm() helper function in crews.py."""
    print("\n" + "=" * 80)
    print("  Testing get_llm() Helper Function")
    print("=" * 80)

    try:
        from app.swarm.crews import get_llm
        from app.config import get_settings

        settings = get_settings()

        if not settings.is_llm_configured():
            print("\n⚠️  LLM not configured, skipping get_llm() test")
            print("  Set credentials in .env to test LLM instantiation")
            return True

        llm = get_llm()

        print(f"\n✓ LLM instance created")
        print(f"  Type: {type(llm).__name__}")

        # Check if model attribute exists
        if hasattr(llm, "model"):
            print(f"  Model: {llm.model}")

        return True

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_startup_validation():
    """Test that startup validation works."""
    print("\n" + "=" * 80)
    print("  Testing Startup Validation")
    print("=" * 80)

    try:
        from app.main import startup_validation
        import asyncio

        print("\n✓ Running startup validation...")
        asyncio.run(startup_validation())
        print("✓ Startup validation completed")

        return True

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("LLM Configuration Test Suite\n")

    results = []
    results.append(("Configuration Loading", test_config_loading()))
    results.append(("get_llm_config() Method", test_llm_config_method()))
    results.append(("is_llm_configured() Check", test_llm_configured_check()))
    results.append(("get_llm() Helper", test_get_llm_helper()))
    results.append(("Startup Validation", test_startup_validation()))

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
        print("\nConfiguration Summary:")
        from app.config import get_settings

        settings = get_settings()
        print(f"  Provider: {settings.LLM_PROVIDER}")
        config = settings.get_llm_config()
        print(f"  Model: {config['model']}")
        print(f"  Configured: {settings.is_llm_configured()}")

        if not settings.is_llm_configured():
            print("\n⚠️  To use the LLM, set credentials in .env:")
            if settings.LLM_PROVIDER == "bedrock":
                print("  AWS_BEARER_TOKEN_BEDROCK=your-token-here")
            elif settings.LLM_PROVIDER == "anthropic":
                print("  ANTHROPIC_API_KEY=sk-ant-...")

        print("\nNew endpoints available:")
        print("  GET /api/llm-status - Check LLM configuration status")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
