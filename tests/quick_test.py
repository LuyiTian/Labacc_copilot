#!/usr/bin/env python3
"""Quick test without LLM calls"""

import asyncio
import uuid
from datetime import datetime

# Quick test - just test agent routing
from src.agents.orchestrator import OrchestratorAgent
from src.agents.base_agent import Task

async def test_routing():
    """Test agent routing logic"""
    
    print("🤖 Testing Agent Routing...")
    
    orchestrator = OrchestratorAgent()
    
    # Test routing decisions
    test_cases = [
        ("scan_project", ["explorer"]),
        ("analyze_experiment", ["analyzer", "explorer"]),
        ("research_problem", ["researcher"]),
        ("suggest_optimization", ["advisor", "analyzer"]),
        ("general_query", ["analyzer", "researcher", "advisor"])
    ]
    
    for task_type, expected_agents in test_cases:
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            content=f"Test {task_type}",
            metadata={},
            created_at=datetime.now(),
            priority=1
        )
        
        agents = orchestrator.determine_agents(task)
        print(f"✅ {task_type}: {agents} (expected: {expected_agents})")
        
        if agents == expected_agents:
            print("   ✓ Routing correct!")
        else:
            print("   ⚠️  Routing differs from expected")
    
    print("\n🎉 Agent routing test complete!")

if __name__ == "__main__":
    asyncio.run(test_routing())