#!/usr/bin/env python
"""
Test agent context handling for folder and file queries
"""

import asyncio
from src.agents.react_agent import handle_message


async def test_context_handling():
    """Test that agent handles context properly."""
    
    print("🧪 Testing Agent Context Handling")
    print("=" * 60)
    
    # Test 1: "What is in this folder?"
    print("\n1️⃣ Testing 'what is in this folder?' with context...")
    
    response = await handle_message(
        message="what is in this folder?",
        current_folder="exp_004_test_auto_update",
        selected_files=None
    )
    
    print(f"Response: {response[:500]}...")
    
    # Test 2: "Tell me about this file" with selected file
    print("\n2️⃣ Testing 'tell me about this file' with selected file...")
    
    response = await handle_message(
        message="tell me about this file",
        current_folder="exp_004_test_auto_update", 
        selected_files=["GMB背景compareto_GV20.md"]
    )
    
    print(f"Response: {response[:500]}...")
    
    # Test 3: Direct command
    print("\n3️⃣ Testing direct command without vague language...")
    
    response = await handle_message(
        message="list the contents of exp_004_test_auto_update",
        current_folder="exp_004_test_auto_update",
        selected_files=None
    )
    
    print(f"Response: {response[:500]}...")
    
    print("\n" + "=" * 60)
    print("✅ Tests completed!")


if __name__ == "__main__":
    import os
    # Set a dummy key for testing
    os.environ["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "test")
    
    asyncio.run(test_context_handling())