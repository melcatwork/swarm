#!/usr/bin/env python3
"""
Test script to verify Ollama works with CrewAI LLM.
"""
import os
import sys

# Set environment variables BEFORE importing CrewAI
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["OLLAMA_MODEL"] = "qwen3:4b"
os.environ["OPENAI_API_KEY"] = "sk-disabled-no-openai"
os.environ["OPENAI_API_BASE"] = "http://localhost:11434"
os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"

print("=" * 60)
print("Testing Ollama + CrewAI Integration")
print("=" * 60)

# Test 1: Check Ollama server
print("\n1. Testing Ollama server connectivity...")
import requests
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        data = response.json()
        models = [m["name"] for m in data.get("models", [])]
        print(f"   ✓ Ollama is running")
        print(f"   ✓ Available models: {', '.join(models)}")
        if "qwen3:4b" in models:
            print(f"   ✓ qwen3:4b is available")
        else:
            print(f"   ✗ qwen3:4b NOT found. Please run: ollama pull qwen3:4b")
            sys.exit(1)
    else:
        print(f"   ✗ Ollama returned status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Cannot connect to Ollama: {e}")
    print("   Please start Ollama with: ollama serve")
    sys.exit(1)

# Test 2: Import CrewAI
print("\n2. Importing CrewAI...")
try:
    from crewai import LLM, Agent, Task, Crew
    print("   ✓ CrewAI imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import CrewAI: {e}")
    sys.exit(1)

# Test 3: Create LLM instance
print("\n3. Creating LLM instance with Ollama...")
try:
    llm = LLM(
        model="ollama/qwen3:4b",
        temperature=0.7,
        api_base="http://localhost:11434",
    )
    print("   ✓ LLM instance created")
except Exception as e:
    print(f"   ✗ Failed to create LLM: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Create a simple agent
print("\n4. Creating test agent...")
try:
    agent = Agent(
        role="Test Agent",
        goal="Say hello",
        backstory="You are a test agent to verify Ollama integration.",
        verbose=True,
        llm=llm,
    )
    print("   ✓ Agent created")
except Exception as e:
    print(f"   ✗ Failed to create agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Create a simple task
print("\n5. Creating test task...")
try:
    task = Task(
        description="Say 'Hello from Ollama!' and nothing else.",
        expected_output="A simple greeting message",
        agent=agent,
    )
    print("   ✓ Task created")
except Exception as e:
    print(f"   ✗ Failed to create task: {e}")
    sys.exit(1)

# Test 6: Create crew and execute
print("\n6. Creating and executing crew...")
print("   (This will call Ollama - may take 10-30 seconds)")
try:
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    print("   ✓ Crew created")

    print("\n   Executing crew (calling Ollama)...")
    result = crew.kickoff()

    print("\n   ✓ Crew execution completed!")
    print(f"\n   Result: {result}")

except Exception as e:
    print(f"\n   ✗ Crew execution failed: {e}")
    import traceback
    traceback.print_exc()

    # Check if it's an OpenAI error
    if "openai" in str(e).lower() or "api.openai.com" in str(e).lower():
        print("\n   ⚠️  ERROR: CrewAI is still trying to call OpenAI!")
        print("   This means the environment variables aren't being respected.")
        print("   Possible fixes:")
        print("   1. Restart your terminal/shell")
        print("   2. Check if there's a .env file setting OPENAI_API_KEY")
        print("   3. Try: export OPENAI_API_KEY='sk-disabled'")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("Ollama + CrewAI integration is working correctly.")
print("=" * 60)
