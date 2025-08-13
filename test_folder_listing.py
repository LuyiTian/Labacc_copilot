#!/usr/bin/env python
"""
Test folder listing to debug issues
"""

import asyncio
from src.agents.react_agent import handle_message


async def test_folder_operations():
    """Test folder and file operations."""
    
    print("🧪 Testing Folder and File Operations")
    print("=" * 60)
    
    # Test 1: What is in this folder?
    print("\n1️⃣ Testing 'what is in this folder?'...")
    response = await handle_message(
        message="what is in this folder?",
        current_folder="exp_004_test_auto_update",
        selected_files=None
    )
    print(f"Response: {response}\n")
    
    # Test 2: How many files?
    print("\n2️⃣ Testing 'how many files in this folder?'...")
    response = await handle_message(
        message="how many files in this folder?",
        current_folder="exp_004_test_auto_update",
        selected_files=None
    )
    print(f"Response: {response}\n")
    
    # Test 3: What is in this file?
    print("\n3️⃣ Testing 'what is in this file?' with selected file...")
    response = await handle_message(
        message="what is in this file?",
        current_folder="exp_004_test_auto_update",
        selected_files=["GMB背景compareto_GV20.md"]
    )
    print(f"Response: {response[:500]}...\n")
    
    # Test 4: Direct tool call
    print("\n4️⃣ Testing direct tool invocation...")
    from src.agents.react_agent import list_folder_contents
    result = await list_folder_contents("exp_004_test_auto_update")
    print(f"Direct tool result:\n{result}\n")
    
    print("=" * 60)


if __name__ == "__main__":
    import os
    os.environ["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "test-key")
    asyncio.run(test_folder_operations())