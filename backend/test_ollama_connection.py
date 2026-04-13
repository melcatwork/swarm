"""Test Ollama connection with CrewAI LLM."""

import os
import sys

# Add backend to path
sys.path.insert(0, '/Users/bland/Desktop/swarm-tm/backend')

from app.config import get_settings
from app.swarm.crews import get_llm

# Get settings
settings = get_settings()

print("=" * 60)
print("Testing Ollama Configuration")
print("=" * 60)
print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
print(f"OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
print(f"OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
print()

# Get LLM instance
print("Creating LLM instance...")
llm = get_llm()
print(f"LLM model: {llm.model}")
print()

# Check environment variables set by get_llm()
print("Environment variables after get_llm():")
print(f"OLLAMA_API_BASE: {os.environ.get('OLLAMA_API_BASE', 'NOT SET')}")
print()

# Try a simple call
print("Testing LLM call...")
try:
    response = llm.call(messages=[{"role": "user", "content": "Say 'Hello' and nothing else"}])
    print(f"✅ Success! Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
