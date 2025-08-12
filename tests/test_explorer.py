#!/usr/bin/env python3
"""Test Explorer agent scanning functionality"""

import asyncio
import uuid
from datetime import datetime
from src.agents.explorer import ExplorerAgent
from src.agents.base_agent import Task

async def test_explorer():
    """Test the Explorer agent"""
    print("🔍 Testing Explorer Agent...")
    print("=" * 50)
    
    explorer = ExplorerAgent()
    
    task = Task(
        id=str(uuid.uuid4()),
        type="scan_project",
        content="Scan my project and show all experiments",
        metadata={"project_root": "data/alice_projects"},
        created_at=datetime.now(),
        priority=1
    )
    
    print("Scanning project...")
    result = await explorer.process(task)
    
    if result.success:
        print("\n✅ Scan successful!")
        print(f"⏱️  Time: {result.processing_time:.2f}s")
        print("\n📊 Results:")
        print("-" * 40)
        print(result.content)
        print("-" * 40)
    else:
        print(f"❌ Scan failed: {result.content}")
    
    return result.success

if __name__ == "__main__":
    success = asyncio.run(test_explorer())
    if success:
        print("\n🎉 Explorer agent is working!")
    else:
        print("\n⚠️  Explorer agent needs attention")