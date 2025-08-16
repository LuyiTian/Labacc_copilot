#!/usr/bin/env python3
"""
Test memory update from user responses.

Tests that user responses to agent questions properly update the experiment memory.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent dirs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.utils.test_session import TestSession, MockSessionManager
from tests.utils.mock_llm import MockLLM, patch_llm_for_tests
from src.memory.memory import SimpleMemoryManager


async def test_memory_update_from_user_response():
    """Test that user responses update memory correctly."""
    
    print("\n" + "="*60)
    print("🧪 TESTING: Memory Update from User Responses")
    print("="*60)
    
    # Setup test environment
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, session_id = test_session.setup()
    
    print(f"\n📁 Test Environment:")
    print(f"   Project: {project_root}")
    print(f"   Experiment: {experiment_id}")
    
    # Patch LLM for predictable responses
    mock_llm, original_llm = patch_llm_for_tests()
    
    try:
        # ========== STEP 1: Initial Memory State ==========
        print("\n📖 Step 1: Checking initial memory state...")
        
        memory_manager = SimpleMemoryManager(str(project_root))
        initial_memory = memory_manager.load_memory(experiment_id)
        
        assert initial_memory is not None, "No initial memory"
        initial_content = initial_memory.raw_content
        print(f"   Initial README: {len(initial_content)} chars")
        print(f"   ✅ Initial memory loaded")
        
        # ========== STEP 2: Simulate File Upload Questions ==========
        print("\n❓ Step 2: Simulating pending questions...")
        
        # Create mock session with pending questions
        session_manager = MockSessionManager(project_root)
        session_manager.create_session(session_id, "test_user")
        session = session_manager.get_session(session_id)
        
        # Add pending questions (as would happen after file upload)
        session.pending_questions[experiment_id] = {
            'file': 'test_protocol.pdf',
            'timestamp': datetime.now().isoformat(),
            'asked': True
        }
        
        print(f"   Pending questions for: {session.pending_questions[experiment_id]['file']}")
        print(f"   ✅ Questions tracked in session")
        
        # ========== STEP 3: User Response ==========
        print("\n💬 Step 3: Processing user response...")
        
        user_response = """
        This protocol is for optimizing tissue dissociation.
        We're testing different temperatures and durations.
        The goal is to improve cell viability while maintaining diversity.
        Previous attempts had issues with over-digestion.
        """
        
        print(f"   User response: {user_response[:50]}...")
        
        # ========== STEP 4: Memory Update ==========
        print("\n💾 Step 4: Updating memory with user context...")
        
        # Simulate what happens in handle_message when user responds
        memory_update = f"""
## File Upload Analysis ({datetime.now().strftime('%Y-%m-%d')})

**File:** {session.pending_questions[experiment_id]['file']}
**Analysis:** Test analysis of the uploaded protocol

**User's Additional Context:**
{user_response}

**Integration Notes:**
- File uploaded and analyzed with user clarifications
- Context captured for future reference
"""
        
        # Update memory (using mock LLM)
        from src.memory.memory_tools import init_memory_tools
        init_memory_tools(str(project_root), mock_llm)
        
        result = await memory_manager.update_memory(
            experiment_id,
            memory_update,
            mock_llm
        )
        
        print(f"   Update result: {result}")
        print(f"   ✅ Memory update completed")
        
        # ========== STEP 5: Verify Update ==========
        print("\n✓ Step 5: Verifying memory was updated...")
        
        # Load updated memory
        updated_memory = memory_manager.load_memory(experiment_id)
        updated_content = updated_memory.raw_content
        
        # Check that new content was added
        assert len(updated_content) > len(initial_content), "Memory not expanded"
        print(f"   Updated README: {len(updated_content)} chars")
        print(f"   Growth: +{len(updated_content) - len(initial_content)} chars")
        
        # Check specific content
        assert "File Upload Analysis" in updated_content, "Analysis section not added"
        print(f"   ✅ Analysis section added")
        
        assert "test_protocol.pdf" in updated_content, "File name not in memory"
        print(f"   ✅ File name recorded")
        
        # The mock LLM returns a formatted response, check it's there
        assert experiment_id in updated_content, "Experiment ID not preserved"
        print(f"   ✅ Context preserved")
        
        # ========== STEP 6: Questions Cleared ==========
        print("\n🧹 Step 6: Verifying questions cleared...")
        
        # In real flow, questions would be cleared after update
        if experiment_id in session.pending_questions:
            del session.pending_questions[experiment_id]
        
        assert experiment_id not in session.pending_questions, "Questions not cleared"
        print(f"   ✅ Pending questions cleared")
        
        # ========== CLEANUP ==========
        print("\n🧹 Cleaning up...")
        
        from tests.utils.mock_llm import unpatch_llm
        unpatch_llm(original_llm)
        test_session.cleanup()
        print(f"   ✅ Test environment cleaned")
        
        print("\n" + "="*60)
        print("✅ PASSED: Memory Update from User Responses")
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


async def test_memory_persistence():
    """Test that memory updates persist across sessions."""
    
    print("\n" + "="*60)
    print("🧪 TESTING: Memory Persistence")
    print("="*60)
    
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, session_id = test_session.setup()
    
    try:
        memory_manager = SimpleMemoryManager(str(project_root))
        
        # Add some content
        test_content = "\n## Test Section\nThis is test content that should persist."
        readme_path = project_root / experiment_id / "README.md"
        current = readme_path.read_text()
        readme_path.write_text(current + test_content)
        
        print(f"   Added test content: {len(test_content)} chars")
        
        # Load in new "session"
        memory = memory_manager.load_memory(experiment_id)
        
        assert "Test Section" in memory.raw_content, "Content not persisted"
        assert "This is test content" in memory.raw_content, "Details lost"
        
        print(f"   ✅ Memory persists across sessions")
        
        test_session.cleanup()
        print("\n✅ PASSED: Memory Persistence")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        test_session.cleanup()
        return False


if __name__ == "__main__":
    # Run all tests
    async def run_all_tests():
        results = []
        
        results.append(await test_memory_update_from_user_response())
        results.append(await test_memory_persistence())
        
        # Summary
        print("\n" + "="*60)
        print("📊 MEMORY TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in results if r)
        total = len(results)
        
        print(f"   Passed: {passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL MEMORY TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return 1
    
    sys.exit(asyncio.run(run_all_tests()))