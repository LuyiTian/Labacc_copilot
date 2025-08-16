#!/usr/bin/env python
"""Test that read_file tool can read converted files."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up session for testing
from projects.session import ProjectSession, set_current_session


async def test_read_converted():
    """Test reading a converted PDF file."""
    
    print("Testing read_file with converted documents...")
    print("=" * 60)
    
    # Create test session
    test_session = ProjectSession(
        session_id="test_session",
        user_id="test_user",
        selected_project="bob_projects",
        project_path=Path("/data/luyit/script/git/Labacc_copilot/data/bob_projects"),
        permission="owner"
    )
    set_current_session(test_session)
    
    # Import after setting up session
    from agents.react_agent import read_file
    
    # Test 1: Read the uploaded PDF (should get converted version)
    print("\n1. Testing PDF that was converted:")
    file_path = "exp_002_optimization/originals/For lung cancer tissue dissociation.pdf"
    result = await read_file.ainvoke({"file_path": file_path})
    
    if "Binary file" in result:
        print("   ❌ FAILED - Still reading binary file")
        print(f"   Result: {result[:200]}")
    elif "digestion time" in result.lower():
        print("   ✅ SUCCESS - Reading converted markdown!")
        print(f"   Preview: {result[:200]}...")
    else:
        print("   ⚠️  UNKNOWN - Got unexpected result")
        print(f"   Result: {result[:200]}")
    
    # Test 2: Read a regular markdown file
    print("\n2. Testing regular markdown file:")
    result = await read_file.ainvoke({"file_path": "exp_002_optimization/README.md"})
    if "Experiment:" in result:
        print("   ✅ SUCCESS - Regular files still work")
    else:
        print("   ❌ FAILED - Can't read regular files")
    
    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_read_converted())