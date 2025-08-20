#!/usr/bin/env python3
"""
Multi-User Test System Validation

Quick validation script to verify that all components of the new multi-user
test system are working correctly without running full evaluations.
"""

import asyncio
import sys
from pathlib import Path

# Add src and project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from tests.utils.multiuser_test_utils import test_manager, create_test_session, cleanup_test_session
from tests.utils.compatibility_layer import handle_message_with_compatibility
from tests.agent_evaluation.multiuser_test_cases import MultiUserTestGenerator, MultiUserTestCase
from tests.agent_evaluation.multiuser_test_runner import MultiUserTestRunner


class MultiUserSystemValidator:
    """Validates core multi-user test system components"""
    
    def __init__(self):
        self.test_results = []
        
    async def run_validation(self) -> bool:
        """Run all validation tests"""
        print("🧪 Multi-User Test System Validation")
        print("=" * 50)
        
        validation_tests = [
            ("Project Mapping", self._test_project_mapping),
            ("Session Management", self._test_session_management),  
            ("Compatibility Layer", self._test_compatibility_layer),
            ("Test Case Generation", self._test_case_generation),
            ("Multi-User Test Runner", self._test_multiuser_runner),
        ]
        
        passed_tests = 0
        total_tests = len(validation_tests)
        
        for test_name, test_func in validation_tests:
            try:
                print(f"\n🔍 Testing {test_name}...")
                success = await test_func()
                if success:
                    print(f"✅ {test_name}: PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Validation Summary:")
        print(f"  Passed: {passed_tests}/{total_tests}")
        print(f"  Success Rate: {passed_tests/total_tests:.1%}")
        
        if passed_tests == total_tests:
            print("🎉 All validation tests PASSED!")
            return True
        else:
            print("⚠️ Some validation tests FAILED")
            return False
    
    async def _test_project_mapping(self) -> bool:
        """Test project mapping functionality"""
        try:
            # Test old folder to project mapping
            mapping = test_manager.map_old_folder_to_project("alice_projects/exp_001")
            if not mapping:
                print("  Warning: Failed to map 'alice_projects/exp_001'")
                # Try a simpler mapping
                mapping = test_manager.map_old_folder_to_project("alice_projects")
                if not mapping:
                    print("  Error: Failed to map 'alice_projects' as well")
                    return False
                
            print(f"  Mapped folder to project '{mapping.project_id}'")
            
            # Test project mapping works
            print(f"  Project mapping functionality verified")
            
            # Validate the mapping object
            if hasattr(mapping, 'project_id') and hasattr(mapping, 'relative_path'):
                print(f"  Mapping structure: project='{mapping.project_id}', path='{mapping.relative_path}'")
                return True
            else:
                print(f"  Invalid mapping structure")
                return False
            
        except Exception as e:
            print(f"  Project mapping error: {e}")
            return False
    
    async def _test_session_management(self) -> bool:
        """Test session creation and management"""
        try:
            # Create test session
            session = await create_test_session(
                session_id="validation_test_session",
                user_id="test_user",
                project_id="project_alice_projects"
            )
            
            if not session:
                return False
            
            print(f"  Created session: {session.session_id}")
            print(f"  Selected project: {session.selected_project}")
            
            # Cleanup
            cleanup_test_session("validation_test_session")
            print("  Session cleaned up successfully")
            
            return True
            
        except Exception as e:
            print(f"  Session management error: {e}")
            return False
    
    async def _test_compatibility_layer(self) -> bool:
        """Test compatibility layer for legacy tests"""
        try:
            # Test compatibility wrapper
            response = await handle_message_with_compatibility(
                message="What is this folder?",
                session_id="compatibility_test", 
                current_folder="alice_projects"
            )
            
            print(f"  Compatibility response length: {len(response)} chars")
            
            # Cleanup
            cleanup_test_session("compatibility_test")
            
            return len(response) > 0
            
        except Exception as e:
            print(f"  Compatibility layer error: {e}")
            return False
    
    async def _test_case_generation(self) -> bool:
        """Test multi-user test case generation"""
        try:
            generator = MultiUserTestGenerator()
            
            # Test different test case types
            isolation_tests = generator.generate_project_isolation_tests()
            session_tests = generator.generate_session_management_tests()
            multilingual_tests = generator.generate_multilingual_multiuser_tests()
            
            total_tests = len(isolation_tests) + len(session_tests) + len(multilingual_tests)
            
            print(f"  Generated {len(isolation_tests)} isolation tests")
            print(f"  Generated {len(session_tests)} session tests") 
            print(f"  Generated {len(multilingual_tests)} multilingual tests")
            print(f"  Total: {total_tests} test cases")
            
            # Validate a test case structure
            if isolation_tests:
                test_case = isolation_tests[0]
                has_project_context = test_case.project_context is not None
                print(f"  Sample test has project context: {has_project_context}")
                return total_tests > 0 and has_project_context
            
            return total_tests > 0
            
        except Exception as e:
            print(f"  Test case generation error: {e}")
            return False
    
    async def _test_multiuser_runner(self) -> bool:
        """Test multi-user test runner setup"""
        try:
            runner = MultiUserTestRunner(max_parallel=1)
            
            # Test compatibility mode toggle
            runner.set_compatibility_mode(True)
            print("  Compatibility mode enabled")
            
            runner.set_compatibility_mode(False)
            print("  Native mode enabled")
            
            # Test runner configuration
            print(f"  Max parallel workers: {runner.max_parallel}")
            print(f"  Evaluator configured: {runner.evaluator is not None}")
            
            return True
            
        except Exception as e:
            print(f"  Multi-user runner error: {e}")
            return False


async def main():
    """Main validation entry point"""
    validator = MultiUserSystemValidator()
    success = await validator.run_validation()
    
    if success:
        print("\n🎉 Multi-user test system is ready!")
        return 0
    else:
        print("\n❌ Multi-user test system has issues that need to be resolved")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)