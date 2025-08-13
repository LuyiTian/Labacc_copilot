"""
Quick test script for LabAcc Copilot system
Tests core functionality of the React agent with memory system
"""

import asyncio
import os
from src.agents.react_agent import handle_message

async def quick_test():
    """Quick test of core functionality"""
    
    print("=" * 60)
    print("🧪 LabAcc Copilot System Test")
    print("=" * 60)
    
    # Check if API key is set
    if not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("SILICONFLOW_API_KEY"):
        print("⚠️  Warning: No API keys found. Set OPENROUTER_API_KEY or SILICONFLOW_API_KEY")
        print("   The system may not work without an LLM provider configured.")
    
    tests = [
        ("Scan my experiments", "Should list all experiments in the project"),
        ("Create a new experiment for testing Western blot optimization", "Should create new experiment folder with README"),
        ("What experiments do I have now?", "Should show the newly created experiment"),
        ("Search for optimization across all experiments", "Should search through README files"),
        ("Read the project insights", "Should show patterns across experiments")
    ]
    
    for test_query, expected in tests:
        print(f"\n📝 Test: {test_query}")
        print(f"   Expected: {expected}")
        
        try:
            response = await handle_message(test_query)
            
            # Show first 300 chars of response
            if len(response) > 300:
                print(f"✅ Response: {response[:300]}...")
                print(f"   [Full response: {len(response)} characters]")
            else:
                print(f"✅ Response: {response}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✨ Test complete! Check data/alice_projects/ for created experiments")
    print("=" * 60)

async def test_with_context():
    """Test with experiment context"""
    
    print("\n" + "=" * 60)
    print("🔬 Testing with Experiment Context")
    print("=" * 60)
    
    # First create an experiment
    print("\n1️⃣ Creating test experiment...")
    response = await handle_message("Create experiment for PCR troubleshooting")
    print(f"   {response[:200]}")
    
    # Extract experiment ID if created
    if "exp_" in response:
        # Find the experiment ID in the response
        import re
        match = re.search(r'(exp_\d+_\w+)', response)
        if match:
            exp_id = match.group(1)
            print(f"\n2️⃣ Working with experiment: {exp_id}")
            
            # Test with context
            context_tests = [
                f"Add insight to {exp_id}: Primers may be degraded",
                f"Read the overview of {exp_id}",
                f"Update {exp_id} results: No amplification observed"
            ]
            
            for test in context_tests:
                print(f"\n📝 Test: {test}")
                try:
                    response = await handle_message(
                        test,
                        current_folder=exp_id
                    )
                    print(f"✅ Response: {response[:200]}...")
                except Exception as e:
                    print(f"❌ Error: {str(e)}")

async def main():
    """Run all tests"""
    
    # Basic tests
    await quick_test()
    
    # Context tests
    await test_with_context()
    
    print("\n🎉 All tests completed!")
    print("📂 Check data/alice_projects/ for created experiments and README files")

if __name__ == "__main__":
    asyncio.run(main())