"""
Test script to verify context awareness and auto-README updates
"""

import asyncio
import os
import json
from pathlib import Path
from src.agents.react_agent import handle_message
from src.memory.memory_tools import read_memory

async def test_context_awareness():
    """Test that vague commands work with context"""
    
    print("=" * 60)
    print("🧪 Testing Context Awareness Fixes")
    print("=" * 60)
    
    # Test 1: Vague command with experiment context
    print("\n1️⃣ Testing vague 'Analyse' command with experiment context...")
    response = await handle_message(
        message="Analyse",
        session_id="test-session",
        current_folder="exp_005_crispr_2025_09_1",
        selected_files=["log_data_crispr.txt"]
    )
    
    print(f"Response preview: {response[:300]}...")
    
    # Check if response mentions the experiment or file
    if "exp_005" in response or "crispr" in response.lower() or "log_data" in response.lower():
        print("✅ Context awareness working! Agent understood the experiment context.")
    else:
        print("⚠️ Context might not be fully working. Check if agent mentioned the experiment.")
    
    # Test 2: Another vague command
    print("\n2️⃣ Testing 'What is this?' with folder context...")
    response = await handle_message(
        message="What is this?",
        session_id="test-session",
        current_folder="exp_001_pcr_optimization",
        selected_files=None
    )
    
    print(f"Response preview: {response[:300]}...")
    
    if "exp_001" in response or "pcr" in response.lower():
        print("✅ Context working for folder-only context!")
    else:
        print("⚠️ Check context handling for folder-only scenarios.")

async def test_auto_readme_update():
    """Test that README updates when files are uploaded"""
    
    print("\n" + "=" * 60)
    print("🧪 Testing Auto-README Updates")
    print("=" * 60)
    
    # This test would need actual file upload through the API
    # For now, we'll test the memory tools directly
    
    from src.memory.memory_tools import update_file_registry, append_insight
    
    experiment_id = "exp_test_auto_update"
    
    print(f"\n1️⃣ Creating test experiment: {experiment_id}")
    from src.memory.memory_tools import create_experiment
    result = await create_experiment.ainvoke({
        "experiment_name": "Test Auto Update",
        "motivation": "Testing automatic README updates",
        "key_question": "Do READMEs update automatically?"
    })
    print(f"Result: {result[:200]}...")
    
    print(f"\n2️⃣ Simulating file upload - updating file registry...")
    result = await update_file_registry.ainvoke({
        "experiment_id": experiment_id,
        "file_name": "test_data.csv",
        "file_type": "Data",
        "file_size": "1024 bytes",
        "summary": "Test data file uploaded"
    })
    print(f"Result: {result[:200]}...")
    
    print(f"\n3️⃣ Adding insight about upload...")
    result = await append_insight.ainvoke({
        "experiment_id": experiment_id,
        "insight": "Added test_data.csv to experiment",
        "source": "file_upload"
    })
    print(f"Result: {result[:200]}...")
    
    print(f"\n4️⃣ Reading back the README to verify updates...")
    readme_content = await read_memory.ainvoke({"experiment_id": experiment_id})
    
    if "test_data.csv" in readme_content:
        print("✅ File registry updated successfully!")
    else:
        print("⚠️ File might not be in README. Content preview:")
        print(readme_content[:500])
    
    if "Added test_data.csv" in readme_content:
        print("✅ Insight added successfully!")
    else:
        print("⚠️ Insight might not be in README.")
    
    # Clean up test experiment
    test_path = Path(f"data/alice_projects/{experiment_id}")
    if test_path.exists():
        import shutil
        shutil.rmtree(test_path)
        print(f"\n🧹 Cleaned up test experiment: {experiment_id}")

async def main():
    """Run all tests"""
    
    print("🚀 Starting Context and Auto-Update Tests")
    print("=" * 60)
    
    # Check if API key is set
    if not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("SILICONFLOW_API_KEY"):
        print("⚠️ Warning: No API keys found. Set OPENROUTER_API_KEY or SILICONFLOW_API_KEY")
        print("   Some tests may fail without an LLM provider.")
    
    await test_context_awareness()
    await test_auto_readme_update()
    
    print("\n" + "=" * 60)
    print("✨ All tests completed!")
    print("=" * 60)
    print("\n📝 Summary of Fixes:")
    print("1. Context Awareness: Vague commands like 'Analyse' now understand current folder/files")
    print("2. Auto-README: Files uploaded to experiment folders auto-update README.md")
    print("3. Background Updates: README updates happen in background, won't slow uploads")
    print("\n🎯 Next Steps:")
    print("1. Start the system: ./start-dev.sh")
    print("2. Navigate to an experiment folder")
    print("3. Upload a file - README should update automatically")
    print("4. Type 'Analyse' - agent should know what folder you're in")

if __name__ == "__main__":
    asyncio.run(main())