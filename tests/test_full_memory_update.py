#!/usr/bin/env python3
"""
Test the complete memory update flow without hallucinations.

This test simulates:
1. File upload and agent analysis
2. User answering follow-up questions  
3. Memory update with actual information only
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.react_bridge import notify_agent_of_upload
from src.agents.react_agent import handle_message
from src.projects.session import session_manager, set_current_session, ProjectSession
from src.memory.memory import SimpleMemoryManager
from src.memory.memory_tools import init_memory_tools
from src.components.llm import get_llm_instance


async def test_full_memory_update_flow():
    """Test complete flow from upload to memory update"""
    
    print("=" * 60)
    print("Testing Full Memory Update Flow (No Hallucinations)")
    print("=" * 60)
    
    # Setup
    test_project = "data/bob_projects"
    test_experiment = "exp_002_optimization"
    test_file = "For lung cancer tissue dissociation.pdf"
    converted_file = "For lung cancer tissue dissociation.md"
    
    # Create session with proper setup
    session_id = "test-session-002"
    user_id = "test_user"
    
    session_manager.create_session(session_id, user_id)
    
    # Create proper project session
    project_session = ProjectSession(
        session_id=session_id,
        user_id=user_id,
        selected_project="bob_projects",
        project_path=Path(test_project),
        permission="owner"
    )
    project_session.pending_questions = {}
    project_session.recent_uploads = []
    
    session_manager.sessions[session_id] = project_session
    set_current_session(session_id)
    
    # Initialize memory tools
    llm = get_llm_instance()
    init_memory_tools(project_root=test_project, llm=llm)
    
    print(f"\n1. Simulating file upload...")
    print(f"   File: {test_file}")
    print(f"   Experiment: {test_experiment}")
    
    # Step 1: Upload notification (agent reads and analyzes)
    agent_analysis = await notify_agent_of_upload(
        session_id=session_id,
        file_path=f"{test_experiment}/{converted_file}",
        experiment_id=test_experiment,
        original_name=test_file,
        conversion_status="success"
    )
    
    print("\n2. Agent Analysis (with follow-up questions):")
    print("-" * 40)
    print(agent_analysis[:600])
    print("-" * 40)
    
    # Check that agent asked questions
    if "?" in agent_analysis:
        print("✅ Agent asked follow-up questions")
    else:
        print("⚠️ Agent didn't ask questions")
    
    # Step 2: Simulate user answering the questions
    print("\n3. Simulating user response to questions...")
    
    user_response = """This is a reference document about optimal digestion times for lung cancer tissue dissociation. 
    We're using it to guide our protocol optimization for exp_002, specifically to reduce the warm digestion 
    time from 45 minutes to 20-25 minutes as suggested in the document. The cold protease approach mentioned 
    in the document is particularly interesting for preserving epithelial cells."""
    
    # Handle user message (this should trigger memory update)
    agent_response = await handle_message(
        message=user_response,
        session_id=session_id
    )
    
    print("\n4. Agent response to user context:")
    print("-" * 40)
    print(agent_response[:400])
    print("-" * 40)
    
    # Step 3: Check memory was updated correctly
    print("\n5. Checking README for proper memory update...")
    
    memory_manager = SimpleMemoryManager(test_project)
    memory = memory_manager.load_memory(test_experiment)
    
    if memory and memory.raw_content:
        readme_content = memory.raw_content
        
        # Check for correct information
        correct_info = []
        if test_file in readme_content or "lung cancer tissue dissociation" in readme_content.lower():
            correct_info.append("File reference")
        if "digestion time" in readme_content.lower() or "20-25 minutes" in readme_content:
            correct_info.append("Actual content")
        if "cold protease" in readme_content.lower():
            correct_info.append("User context")
        
        # Check for hallucinations
        hallucinations = []
        forbidden_terms = ["Stanford", "test_protocol.pdf", "collaborator", "45% epithelial", 
                          "validated protocol", "external validation"]
        
        for term in forbidden_terms:
            if term.lower() in readme_content.lower():
                hallucinations.append(term)
        
        print("\nMemory Update Analysis:")
        print(f"✅ Correct information captured: {correct_info}")
        
        if hallucinations:
            print(f"❌ HALLUCINATIONS DETECTED: {hallucinations}")
            print("\nREADME excerpt showing hallucination:")
            # Find and show the hallucinated section
            for line in readme_content.split('\n'):
                for term in hallucinations:
                    if term.lower() in line.lower():
                        print(f"  > {line}")
                        break
            return False
        else:
            print("✅ No hallucinations detected!")
        
        # Show the actual update section
        print("\nActual memory update in README:")
        print("-" * 40)
        # Find the file upload section
        lines = readme_content.split('\n')
        for i, line in enumerate(lines):
            if "File Upload:" in line and test_file in line:
                # Show next 15 lines
                for j in range(i, min(i+15, len(lines))):
                    print(lines[j])
                break
        print("-" * 40)
    
    # Cleanup
    session_manager.end_session(session_id)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
    return True


async def main():
    """Run the test"""
    success = await test_full_memory_update_flow()
    
    if success:
        print("\n✅ FULL TEST PASSED: Memory update working without hallucinations!")
    else:
        print("\n❌ TEST FAILED: Hallucinations still occurring in memory updates")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)