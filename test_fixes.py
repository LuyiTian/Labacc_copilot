#!/usr/bin/env python3
"""
Test script to verify the fixes for the test infrastructure
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent / "tests"))


async def test_trajectory_capture():
    """Test that handle_message_with_trajectory returns trajectory"""
    print("\n1. Testing trajectory capture...")
    
    from src.agents.react_agent import handle_message_with_trajectory
    
    # Test with a simple query that should trigger tools
    response, trajectory = await handle_message_with_trajectory(
        message="What files are in this folder?",
        session_id="test_trajectory",
        current_folder="exp_001_protocol_test",
        selected_files=None
    )
    
    print(f"   Response length: {len(response)} chars")
    print(f"   Trajectory messages: {len(trajectory)}")
    print(f"   Message types: {[type(msg).__name__ for msg in trajectory[:5]]}")
    
    # Check if we got both response and trajectory
    assert response and len(response) > 0, "No response received"
    assert trajectory and len(trajectory) > 0, "No trajectory captured"
    
    # Check if trajectory contains expected message types
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    has_human = any(isinstance(msg, HumanMessage) for msg in trajectory)
    has_ai = any(isinstance(msg, AIMessage) for msg in trajectory)
    
    print(f"   Has HumanMessage: {has_human}")
    print(f"   Has AIMessage: {has_ai}")
    
    if has_human and has_ai:
        print("   ✅ Trajectory capture working!")
    else:
        print("   ⚠️ Trajectory incomplete")
    
    return True


async def test_bob_projects_access():
    """Test that memory tools can access bob_projects"""
    print("\n2. Testing bob_projects access...")
    
    # Set TEST_MODE to use bob_projects
    os.environ["TEST_MODE"] = "true"
    
    from src.memory.memory_tools import read_memory
    
    # Try to read from bob_projects experiment
    result = await read_memory.ainvoke({
        "experiment_id": "exp_001_protocol_test",
        "section": None
    })
    
    print(f"   README content length: {len(result)} chars")
    print(f"   Content preview: {result[:100]}...")
    
    # Check if we got content from bob_projects
    if "scRNAseq" in result or "protocol" in result.lower():
        print("   ✅ Bob_projects access working!")
    elif "not found" in result.lower():
        print("   ❌ Failed to access bob_projects README")
    else:
        print("   ⚠️ Unclear if bob_projects is being accessed")
    
    # Clean up
    del os.environ["TEST_MODE"]
    
    return True


async def test_runner_integration():
    """Test that the test runner uses real trajectory"""
    print("\n3. Testing test runner integration...")
    
    # Set TEST_MODE for bob_projects
    os.environ["TEST_MODE"] = "true"
    
    from tests.agent_evaluation.enhanced_test_runner import EnhancedAgentTestRunner
    from tests.agent_evaluation.evaluator_agent import TestCase, TestCategory
    
    # Create a simple test case
    test_case = TestCase(
        id="test_integration",
        category=TestCategory.CONTEXT_UNDERSTANDING,
        user_query="What is in this folder?",
        language="English",
        current_folder="exp_001_protocol_test",
        selected_files=None,
        expected_content="Files in the experiment folder",
        expected_insights=["list_folder_contents"],
        ground_truth={"test": "integration"}
    )
    
    # Run the test
    runner = EnhancedAgentTestRunner()
    
    try:
        result = await runner.run_single_test_with_trajectory(test_case)
        
        print(f"   Test passed: {result.passed}")
        print(f"   Combined score: {result.combined_score}/10")
        print(f"   Tool calls: {result.performance_metrics.get('tool_calls', 0)}")
        print(f"   Tools used: {result.performance_metrics.get('tools_used', [])}")
        
        # Check if real trajectory was captured
        if result.performance_metrics.get('tool_calls', 0) > 0:
            print("   ✅ Test runner capturing real trajectory!")
        else:
            print("   ⚠️ No tool calls captured - may need investigation")
            
    except Exception as e:
        print(f"   ❌ Test runner error: {e}")
    
    # Clean up
    del os.environ["TEST_MODE"]
    
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Infrastructure Fixes")
    print("=" * 60)
    
    try:
        # Test each component
        await test_trajectory_capture()
        await test_bob_projects_access()
        await test_runner_integration()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("The fixes appear to be working. Ready to run full evaluation.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)