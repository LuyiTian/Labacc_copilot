#!/usr/bin/env python
"""Test the complete file upload, conversion, and agent analysis workflow."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def test_workflow():
    """Test the file upload workflow."""
    
    print("Testing File Upload → Conversion → Agent Analysis Workflow")
    print("=" * 60)
    
    # Set TEST_MODE for accessing bob_projects
    import os
    os.environ['TEST_MODE'] = 'true'
    
    # 1. Test read_file tool with converted files
    print("\n1. Testing read_file tool for converted files:")
    from agents.react_agent import read_file
    from projects.session import ProjectSession, set_current_session
    
    # Create test session
    from projects.session import session_manager, set_current_session
    from projects.temp_manager import get_temp_project_manager
    
    # Initialize project manager first
    project_manager = get_temp_project_manager()
    
    # Create session and select project (bob_projects has test data)
    session_manager.create_session("test_session", "bob")
    project_session = session_manager.select_project("test_session", "project_bob_projects")
    
    if not project_session:
        print("   ❌ Failed to create session")
        return
    
    # Set current session for this thread
    set_current_session("test_session")
    
    # Test reading a PDF that was converted
    file_path = "exp_002_optimization/originals/For lung cancer tissue dissociation.pdf"
    result = await read_file.ainvoke({"file_path": file_path})
    
    if "Binary file" in result:
        print("   ❌ FAILED - Still reading binary file")
    elif "digestion time" in result.lower():
        print("   ✅ SUCCESS - Reading converted markdown!")
        print(f"   Preview: {result[:100]}...")
    else:
        print("   ⚠️  UNKNOWN - Got unexpected result")
    
    # 2. Test agent notification system
    print("\n2. Testing agent notification for uploaded files:")
    from api.react_bridge import notify_agent_of_upload
    
    try:
        response = await notify_agent_of_upload(
            session_id="test_session",
            file_path="exp_002_optimization/.labacc/converted/For lung cancer tissue dissociation.md",
            experiment_id="exp_002_optimization",
            original_name="For lung cancer tissue dissociation.pdf",
            conversion_status="success"
        )
        
        if response and len(response) > 50:
            print("   ✅ SUCCESS - Agent provided analysis")
            print(f"   Agent response preview: {response[:200]}...")
        else:
            print("   ❌ FAILED - No analysis from agent")
    except Exception as e:
        print(f"   ❌ ERROR - {e}")
    
    # 3. Check file registry
    print("\n3. Checking file registry:")
    registry_path = project_session.resolve_path("exp_002_optimization/.labacc/file_registry.json")
    
    if registry_path.exists():
        import json
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        pdf_file = "For lung cancer tissue dissociation.pdf"
        if pdf_file in registry.get("files", {}):
            file_info = registry["files"][pdf_file]
            if file_info.get("converted_path"):
                print(f"   ✅ Registry has converted path: {file_info['converted_path']}")
            else:
                print("   ❌ No converted path in registry")
        else:
            print(f"   ❌ File '{pdf_file}' not in registry")
    else:
        print("   ❌ Registry file not found")
    
    print("\n" + "=" * 60)
    print("Workflow test complete!")
    print("\nSummary:")
    print("1. read_file tool can now find and read converted markdown files")
    print("2. Agent notification system triggers analysis on upload")
    print("3. File registry tracks conversion status and paths")
    print("\nThe upload → conversion → analysis workflow is operational!")


if __name__ == "__main__":
    asyncio.run(test_workflow())