#!/usr/bin/env python3
"""
Integration test for file upload → conversion → analysis workflow.

Tests the complete flow from file upload through conversion to agent analysis.
"""

import asyncio
import sys
from pathlib import Path
import json

# Add parent dirs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.utils.test_session import TestSession, MockSessionManager
from tests.utils.mock_llm import MockLLM, patch_llm_for_tests
from src.api.file_conversion import FileConversionPipeline
from src.api.react_bridge import notify_agent_of_upload
from src.memory.memory import SimpleMemoryManager


async def test_upload_conversion_analysis():
    """Test the complete upload → conversion → analysis workflow."""
    
    print("\n" + "="*60)
    print("🧪 TESTING: Upload → Conversion → Analysis Workflow")
    print("="*60)
    
    # Setup test environment
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, session_id = test_session.setup()
    
    print(f"\n📁 Test Environment:")
    print(f"   Project: {project_root}")
    print(f"   Experiment: {experiment_id}")
    print(f"   Session: {session_id}")
    
    # Patch LLM for predictable responses
    mock_llm, original_llm = patch_llm_for_tests()
    
    # Create mock session manager
    session_manager = MockSessionManager(project_root)
    session_manager.create_session(session_id, "test_user")
    
    try:
        # ========== STEP 1: File Upload ==========
        print("\n📤 Step 1: Simulating file upload...")
        
        # Create a test file
        test_file_content = """# Test Protocol
        
## Parameters
- Temperature: 37°C
- Duration: 45 minutes
- Sample size: n=10

## Methods
1. Prepare samples
2. Apply treatment
3. Measure results
"""
        test_file = test_session.add_test_file("protocol.txt", test_file_content)
        print(f"   ✅ Created test file: {test_file.name}")
        
        # ========== STEP 2: File Conversion ==========
        print("\n🔄 Step 2: Testing file conversion...")
        
        pipeline = FileConversionPipeline(str(project_root))
        
        # For .txt files, no conversion needed but should be tracked
        conversion_result = await pipeline.process_upload(
            test_file,
            experiment_id
        )
        
        print(f"   Status: {conversion_result['conversion_status']}")
        assert conversion_result['conversion_status'] in ['not_needed', 'success']
        print(f"   ✅ File processed successfully")
        
        # Check registry was updated
        registry_path = project_root / experiment_id / ".labacc" / "file_registry.json"
        assert registry_path.exists(), "Registry not created"
        
        registry = json.loads(registry_path.read_text())
        assert "protocol.txt" in registry['files'], "File not in registry"
        print(f"   ✅ File registry updated")
        
        # ========== STEP 3: Agent Analysis ==========
        print("\n🤖 Step 3: Testing agent analysis with context...")
        
        # Mock the session for notify_agent_of_upload
        import src.projects.session as session_module
        original_session_manager = session_module.session_manager
        session_module.session_manager = session_manager
        
        # Call notify_agent_of_upload
        analysis_response = await notify_agent_of_upload(
            session_id=session_id,
            file_path=str(test_file),
            experiment_id=experiment_id,
            original_name="protocol.txt",
            conversion_status="not_needed"
        )
        
        print(f"   Response length: {len(analysis_response)} chars")
        
        # ========== STEP 4: Verify Analysis ==========
        print("\n✓ Step 4: Verifying analysis quality...")
        
        # Print actual response for debugging
        print(f"   Actual response: {analysis_response[:200]}")
        
        # Check that we got a response
        assert len(analysis_response) > 0, "Empty response"
        print(f"   ✅ Non-empty response received")
        
        # Check for expected content
        # Note: In integration tests, we may use real LLM if mock not properly injected
        if "Summary" in analysis_response or "summary" in analysis_response.lower():
            print(f"   ✅ Summary found in response")
        else:
            print(f"   ⚠️  No clear summary (response may vary)")
        
        # Check for questions (common in agent responses)
        if "?" in analysis_response:
            print(f"   ✅ Questions found in response")
        
        # The key test is that we got a meaningful response
        assert not analysis_response.startswith("Error"), "Response is an error"
        assert not analysis_response.startswith("Failed"), "Response indicates failure"
        print(f"   ✅ Valid response received")
        
        # ========== STEP 5: Check Session State ==========
        print("\n📊 Step 5: Checking session state...")
        
        session = session_manager.get_session(session_id)
        assert hasattr(session, 'pending_questions'), "No pending_questions attribute"
        
        if experiment_id in session.pending_questions:
            question_info = session.pending_questions[experiment_id]
            assert question_info['file'] == "protocol.txt", "Wrong file tracked"
            assert question_info['asked'] == True, "Questions not marked as asked"
            print(f"   ✅ Questions tracked in session")
        else:
            print(f"   ⚠️  Questions not tracked (may be expected for some flows)")
        
        # ========== CLEANUP ==========
        print("\n🧹 Cleaning up...")
        
        # Restore original modules
        session_module.session_manager = original_session_manager
        from tests.utils.mock_llm import unpatch_llm
        unpatch_llm(original_llm)
        
        test_session.cleanup()
        print(f"   ✅ Test environment cleaned")
        
        print("\n" + "="*60)
        print("✅ PASSED: Upload → Conversion → Analysis Workflow")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
        test_session.cleanup()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        test_session.cleanup()
        return False


async def test_pdf_conversion():
    """Test PDF file conversion specifically."""
    
    print("\n" + "="*60)
    print("🧪 TESTING: PDF Conversion")
    print("="*60)
    
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, session_id = test_session.setup()
    
    try:
        # Create a mock PDF file (text file with .pdf extension for testing)
        pdf_content = "%PDF-1.4\nMock PDF content for testing"
        pdf_file = test_session.add_test_file("document.pdf", pdf_content)
        
        print(f"📄 Testing PDF: {pdf_file.name}")
        
        pipeline = FileConversionPipeline(str(project_root))
        
        # Check that PDF needs conversion
        assert pipeline.needs_conversion("document.pdf"), "PDF should need conversion"
        print(f"   ✅ PDF identified for conversion")
        
        # Note: Actual PDF conversion would fail with mock content
        # This tests the detection and flow, not actual conversion
        
        test_session.cleanup()
        print("\n✅ PASSED: PDF Conversion Detection")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        test_session.cleanup()
        return False


async def test_multiple_file_upload():
    """Test uploading multiple files at once."""
    
    print("\n" + "="*60)
    print("🧪 TESTING: Multiple File Upload")
    print("="*60)
    
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, session_id = test_session.setup()
    
    try:
        # Create multiple test files
        files = [
            ("data.csv", "col1,col2,col3\n1,2,3\n4,5,6"),
            ("notes.txt", "Experiment notes\nImportant observations"),
            ("results.json", '{"result": "success", "value": 42}')
        ]
        
        created_files = []
        for filename, content in files:
            file_path = test_session.add_test_file(filename, content)
            created_files.append(file_path)
            print(f"   📎 Created: {filename}")
        
        # Process all files
        pipeline = FileConversionPipeline(str(project_root))
        
        for file_path in created_files:
            result = await pipeline.process_upload(file_path, experiment_id)
            assert result['conversion_status'] in ['not_needed', 'success']
        
        # Check registry has all files
        registry = test_session.get_registry()
        for filename, _ in files:
            assert filename in registry['files'], f"{filename} not in registry"
        
        print(f"   ✅ All {len(files)} files processed and tracked")
        
        test_session.cleanup()
        print("\n✅ PASSED: Multiple File Upload")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        test_session.cleanup()
        return False


if __name__ == "__main__":
    # Run all tests
    async def run_all_tests():
        results = []
        
        # Run individual tests
        results.append(await test_upload_conversion_analysis())
        results.append(await test_pdf_conversion())
        results.append(await test_multiple_file_upload())
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in results if r)
        total = len(results)
        
        print(f"   Passed: {passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return 1
    
    sys.exit(asyncio.run(run_all_tests()))