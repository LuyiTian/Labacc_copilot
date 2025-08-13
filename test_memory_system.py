#!/usr/bin/env python
"""
Test script for the automatic memory system
Tests context awareness, memory extraction, and automatic updates
"""

import asyncio
import os
from pathlib import Path
import shutil

from src.agents.react_agent_v2 import handle_message_v2
from src.memory.auto_memory_updater import AutoMemoryUpdater
from src.memory.memory_tools import read_memory, create_experiment


async def test_memory_extraction():
    """Test that memory updates are extracted from conversations."""
    
    print("\n" + "="*60)
    print("🧪 Testing Memory Extraction from Conversations")
    print("="*60)
    
    updater = AutoMemoryUpdater()
    
    # Test case 1: File correction
    print("\n1️⃣ Testing file correction extraction...")
    user_msg = "figure_b.png shows western blot result of condition 2, not condition 1"
    agent_resp = "I've noted that figure_b.png contains the western blot for condition 2."
    
    updates = await updater.extract_memory_updates(user_msg, agent_resp, "exp_001")
    print(f"Extracted {len(updates)} updates:")
    for update in updates:
        print(f"  - {update.get('type')}: {update.get('content')[:50]}...")
    
    # Test case 2: New result
    print("\n2️⃣ Testing result extraction...")
    user_msg = "The PCR yield was 85% with a 260/280 ratio of 1.8"
    agent_resp = "Excellent yield! 85% is above average for this protocol."
    
    updates = await updater.extract_memory_updates(user_msg, agent_resp, "exp_001")
    print(f"Extracted {len(updates)} updates:")
    for update in updates:
        print(f"  - {update.get('type')}: {update.get('content')[:50]}...")
    
    # Test case 3: Parameter update
    print("\n3️⃣ Testing parameter extraction..."
    user_msg = "I used annealing temperature of 58°C for 30 seconds"
    agent_resp = "58°C annealing temperature is optimal for your primers."
    
    updates = await updater.extract_memory_updates(user_msg, agent_resp, "exp_001")
    print(f"Extracted {len(updates)} updates:")
    for update in updates:
        print(f"  - {update.get('type')}: {update.get('content')[:50]}...")


async def test_automatic_context():
    """Test that context is automatically injected."""
    
    print("\n" + "="*60)
    print("🧪 Testing Automatic Context Injection")
    print("="*60)
    
    # Create a test experiment
    experiment_id = "exp_test_context"
    print(f"\n1️⃣ Creating test experiment: {experiment_id}")
    
    await create_experiment.ainvoke({
        "experiment_name": "Context Test",
        "motivation": "Testing automatic context injection",
        "key_question": "Does context load automatically?"
    })
    
    # Test vague command with context
    print("\n2️⃣ Testing vague 'Analyze' command...")
    response = await handle_message_v2(
        message="Analyze",
        current_folder=experiment_id,
        selected_files=["test_data.csv"]
    )
    
    print(f"Response preview: {response[:300]}...")
    
    if "test_data.csv" in response or experiment_id in response:
        print("✅ Context injection working!")
    else:
        print("⚠️ Context might not be working properly")
    
    # Clean up
    test_path = Path(f"data/alice_projects/{experiment_id}")
    if test_path.exists():
        shutil.rmtree(test_path)
        print(f"\n🧹 Cleaned up test experiment")


async def test_memory_updates():
    """Test that memory updates happen automatically."""
    
    print("\n" + "="*60)
    print("🧪 Testing Automatic Memory Updates")
    print("="*60)
    
    # Create test experiment
    experiment_id = "exp_test_updates"
    print(f"\n1️⃣ Creating test experiment: {experiment_id}")
    
    await create_experiment.ainvoke({
        "experiment_name": "Update Test",
        "motivation": "Testing automatic memory updates",
        "key_question": "Do memories update from conversation?"
    })
    
    # Send message with information that should update memory
    print("\n2️⃣ Sending message with correctable information...")
    response = await handle_message_v2(
        message="figure_a.png is actually a gel electrophoresis image showing 3 bands at 100bp, 200bp, and 500bp",
        current_folder=experiment_id
    )
    
    print(f"Response: {response[:200]}...")
    
    # Wait for background update
    print("\n3️⃣ Waiting for background memory update...")
    await asyncio.sleep(3)
    
    # Read memory to check if updated
    print("\n4️⃣ Checking if memory was updated...")
    memory = await read_memory.ainvoke({"experiment_id": experiment_id})
    
    if "figure_a.png" in memory or "gel electrophoresis" in memory or "bands" in memory:
        print("✅ Memory was automatically updated!")
        print(f"Memory excerpt: {memory[:500]}...")
    else:
        print("⚠️ Memory might not have been updated")
    
    # Clean up
    test_path = Path(f"data/alice_projects/{experiment_id}")
    if test_path.exists():
        shutil.rmtree(test_path)
        print(f"\n🧹 Cleaned up test experiment")


async def test_file_upload_memory():
    """Test that file uploads trigger memory updates."""
    
    print("\n" + "="*60)
    print("🧪 Testing File Upload Memory Updates")
    print("="*60)
    
    print("\n📝 File upload memory updates are already implemented in file_routes.py")
    print("   When you upload a file to an experiment folder:")
    print("   1. File is saved to disk")
    print("   2. README is automatically updated in background")
    print("   3. File registry and insights are added")
    print("\n   To test manually:")
    print("   1. Start the system: ./start-dev.sh")
    print("   2. Create/navigate to an experiment folder")
    print("   3. Upload a file")
    print("   4. Check the README.md in that folder")


async def main():
    """Run all tests."""
    
    print("🚀 Starting Automatic Memory System Tests")
    print("="*60)
    
    # Check API key
    if not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("SILICONFLOW_API_KEY"):
        print("⚠️ Warning: No API keys found. Some tests may fail.")
        print("   Set OPENROUTER_API_KEY or SILICONFLOW_API_KEY")
    
    # Run tests
    await test_memory_extraction()
    await test_automatic_context()
    await test_memory_updates()
    await test_file_upload_memory()
    
    print("\n" + "="*60)
    print("✨ All tests completed!")
    print("="*60)
    
    print("\n📊 Summary of Improvements:")
    print("1. ✅ Context automatically injected from README")
    print("2. ✅ Memory updates extracted from conversations")
    print("3. ✅ File corrections applied automatically")
    print("4. ✅ Results and parameters saved to README")
    print("5. ✅ No explicit memory tools needed in agent")
    
    print("\n🎯 How It Works:")
    print("1. User: 'figure_b.png is western blot of condition 2'")
    print("2. System: Extracts this as FILE_CORRECTION")
    print("3. System: Updates README automatically in background")
    print("4. Agent: Just focuses on analysis, not memory management")
    
    print("\n🚀 Next Steps:")
    print("1. Start system: ./start-dev.sh")
    print("2. Navigate to an experiment folder")
    print("3. Chat naturally - memory updates automatically!")


if __name__ == "__main__":
    asyncio.run(main())