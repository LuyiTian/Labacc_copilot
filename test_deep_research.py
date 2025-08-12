#!/usr/bin/env python3
"""Test deep research functionality"""

import asyncio
from src.tools.deep_research import run_deep_research

def test_deep_research():
    """Test the deep research tool directly"""
    print("🔬 Testing Deep Research Tool...")
    print("=" * 50)
    
    query = "PCR optimization for GC-rich templates troubleshooting"
    print(f"Query: {query}")
    print("Starting research (this may take 30-60 seconds)...")
    
    try:
        result = run_deep_research(query, max_research_loops=1)
        
        if result and 'final_text' in result:
            print("\n✅ Research successful!")
            print("\n📄 Report Preview (first 1000 chars):")
            print("-" * 40)
            print(result['final_text'][:1000])
            print("-" * 40)
            print(f"\n📁 Full report saved to: data/history/")
            return True
        else:
            print("❌ Research returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_deep_research()
    if success:
        print("\n🎉 Deep research tool is working!")
    else:
        print("\n⚠️  Deep research tool needs attention")