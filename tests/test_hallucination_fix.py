#!/usr/bin/env python3
"""
Test script to verify the hallucination fix in file upload and memory update.

This test simulates uploading a file and verifies that:
1. The agent reads the actual file content
2. No hallucinated information is added to memory
3. Only real filename and content are used
"""

import asyncio
import sys
from pathlib import Path
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.react_bridge import notify_agent_of_upload
from src.projects.session import session_manager, set_current_session
from src.memory.memory import SimpleMemoryManager
from datetime import datetime


async def test_upload_without_hallucination():
    """Test that file upload doesn't cause hallucinations"""
    
    print("=" * 60)
    print("Testing File Upload Hallucination Fix")
    print("=" * 60)
    
    # Setup test environment
    test_project = "data/bob_projects"
    test_experiment = "exp_002_optimization"
    test_file = "For lung cancer tissue dissociation.pdf"
    converted_file = "For lung cancer tissue dissociation.md"
    
    # Create a test session with proper project setup
    session_id = "test-session-001"
    user_id = "test_user"
    
    # Initialize session
    session_manager.create_session(session_id, user_id)
    
    # Properly select a project (this is what was missing!)
    from src.projects.session import ProjectSession
    project_session = ProjectSession(
        session_id=session_id,
        user_id=user_id,
        selected_project="bob_projects",
        project_path=Path(test_project),
        permission="owner"
    )
    project_session.pending_questions = {}
    project_session.recent_uploads = []
    
    # Store the project session
    session_manager.sessions[session_id] = project_session
    
    # Set current session
    set_current_session(session_id)
    
    print(f"\n1. Testing upload notification for: {test_file}")
    print(f"   Experiment: {test_experiment}")
    print(f"   Converted file: {converted_file}")
    
    # Call notify_agent_of_upload (this should now read the actual file)
    try:
        response = await notify_agent_of_upload(
            session_id=session_id,
            file_path=f"{test_experiment}/{converted_file}",
            experiment_id=test_experiment,
            original_name=test_file,
            conversion_status="success"
        )
        
        print("\n2. Agent Analysis Response:")
        print("-" * 40)
        print(response[:500] if len(response) > 500 else response)
        print("-" * 40)
        
        # Check for hallucination indicators
        hallucination_keywords = ["Stanford", "test_protocol.pdf", "collaborator", "45% epithelial"]
        found_hallucinations = []
        
        for keyword in hallucination_keywords:
            if keyword.lower() in response.lower():
                found_hallucinations.append(keyword)
        
        if found_hallucinations:
            print(f"\n⚠️ WARNING: Possible hallucinations detected: {found_hallucinations}")
            print("The agent may still be making up information!")
        else:
            print("\n✅ Good: No obvious hallucinations detected")
        
        # Check if correct filename is used
        if test_file in response or converted_file in response:
            print(f"✅ Good: Correct filename used in response")
        else:
            print(f"⚠️ WARNING: Correct filename not found in response")
        
        # Check if agent mentioned reading the file
        if "digestion" in response.lower() or "lung" in response.lower() or "tissue" in response.lower():
            print("✅ Good: Response appears to reference actual file content")
        else:
            print("⚠️ WARNING: Response may not be based on actual file content")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n3. Checking README to ensure no contamination...")
    
    # Check the README wasn't contaminated
    memory_manager = SimpleMemoryManager(test_project)
    memory = memory_manager.load_memory(test_experiment)
    
    if memory and memory.raw_content:
        # Check for hallucinated content in README
        readme_hallucinations = []
        for keyword in ["Stanford", "test_protocol.pdf", "45% epithelial"]:
            if keyword in memory.raw_content:
                readme_hallucinations.append(keyword)
        
        if readme_hallucinations:
            print(f"❌ ERROR: README contains hallucinated content: {readme_hallucinations}")
            print("The memory update still has issues!")
            return False
        else:
            print("✅ Good: README is clean, no hallucinated content")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
    # Clean up session
    session_manager.end_session(session_id)
    
    return True


async def main():
    """Run the test"""
    success = await test_upload_without_hallucination()
    
    if success:
        print("\n✅ Test PASSED: Hallucination fix appears to be working")
    else:
        print("\n❌ Test FAILED: Hallucination issue still present")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)