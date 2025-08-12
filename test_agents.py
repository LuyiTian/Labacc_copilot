#!/usr/bin/env python3
"""Quick test of the multi-agent orchestrator"""

import asyncio
import uuid
from datetime import datetime

from src.agents.orchestrator import OrchestratorAgent
from src.agents.base_agent import Task

async def test_orchestrator():
    """Test the orchestrator with different query types"""
    
    print("🤖 Testing Multi-Agent Orchestrator...")
    print("=" * 50)
    
    orchestrator = OrchestratorAgent()
    
    # Test queries
    test_queries = [
        ("scan_project", "Scan my project and show me an overview", {}),
        ("analyze_experiment", "Analyze my PCR experiment", {
            "current_folder": "exp_001_pcr_optimization",
            "selected_files": ["protocol.md", "results.csv"]
        }),
        ("research_problem", "Research PCR optimization methods", {}),
        ("suggest_optimization", "How can I improve my PCR protocol?", {}),
        ("general_query", "What experiments should I do next?", {})
    ]
    
    for task_type, query, metadata in test_queries:
        print(f"\n🧪 Testing: {task_type}")
        print(f"Query: {query}")
        
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            content=query,
            metadata=metadata,
            created_at=datetime.now(),
            priority=1
        )
        
        try:
            result = await orchestrator.process(task)
            
            print(f"✅ Success: {result.success}")
            print(f"⏱️  Processing time: {result.processing_time:.2f}s")
            print(f"📝 Response preview: {result.content[:200]}...")
            
            if "agents_used" in result.metadata:
                print(f"🤝 Agents used: {result.metadata['agents_used']}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Multi-agent testing complete!")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())