#!/usr/bin/env python3
"""
Comprehensive test runner for LabAcc Copilot multi-user system.
Runs all test suites including unit, integration, and multi-user specific tests.
"""

import asyncio
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

# Test categories and their files
TEST_SUITES = {
    "Unit Tests": [
        "tests/unit/test_config/test_config.py",
        "tests/unit/test_config/test_llm.py",
        "tests/unit/test_file_registry.py",
        "tests/unit/test_tools/test_deep_research.py",
        "tests/unit/test_tools/test_file_analyzer.py",
    ],
    "Integration Tests": [
        "tests/integration/test_upload_workflow.py",
        "tests/integration/test_memory_update.py",
        "tests/test_file_conversion_unit.py",
        "tests/test_file_conversion_integration.py",
    ],
    "API Tests": [
        "tests/test_api_simple.py",
    ],
    "Multi-User Tests": [
        "tests/test_admin_functionality.py",
        "tests/test_session_management.py",
        "tests/validate_multiuser_system.py",
    ],
    "Memory System Tests": [
        "tests/test_simple_memory.py",
    ],
}

class TestRunner:
    """Comprehensive test runner with detailed reporting"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {}
        self.start_time = None
        
    def print_header(self):
        """Print test runner header"""
        print("=" * 70)
        print("🧪 LabAcc Copilot Comprehensive Test Suite")
        print("=" * 70)
        print(f"Running tests for multi-user system v3.4.0")
        print(f"Test categories: {len(TEST_SUITES)}")
        print(f"Total test files: {sum(len(files) for files in TEST_SUITES.values())}")
        print("=" * 70)
        
    def run_test_file(self, test_file: str) -> Tuple[bool, str]:
        """Run a single test file and return success status and output"""
        test_path = Path(test_file)
        
        if not test_path.exists():
            return False, f"Test file not found: {test_file}"
        
        try:
            # Run test with uv
            result = subprocess.run(
                ["uv", "run", "python", str(test_path)],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout per test
            )
            
            if result.returncode == 0:
                return True, result.stdout if self.verbose else "Test passed"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Test timed out after 60 seconds"
        except Exception as e:
            return False, f"Error running test: {str(e)}"
    
    async def run_test_file_async(self, test_file: str) -> Tuple[bool, str]:
        """Async wrapper for running test files"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_test_file, test_file)
    
    async def run_suite(self, suite_name: str, test_files: List[str]):
        """Run a test suite"""
        print(f"\n📦 {suite_name}")
        print("-" * 50)
        
        suite_results = []
        
        for test_file in test_files:
            test_name = Path(test_file).stem
            print(f"  Running {test_name}...", end=" ")
            
            success, output = await self.run_test_file_async(test_file)
            
            if success:
                print("✅")
            else:
                print("❌")
                if not self.verbose:
                    # Show first line of error even in non-verbose mode
                    first_error = output.split('\n')[0] if output else "Unknown error"
                    print(f"    Error: {first_error}")
            
            suite_results.append((test_name, success, output))
        
        self.results[suite_name] = suite_results
    
    async def run_all_tests(self, categories: List[str] = None):
        """Run all test suites or specific categories"""
        self.start_time = time.time()
        
        if categories:
            suites_to_run = {k: v for k, v in TEST_SUITES.items() if k in categories}
        else:
            suites_to_run = TEST_SUITES
        
        for suite_name, test_files in suites_to_run.items():
            await self.run_suite(suite_name, test_files)
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 70)
        print("📊 Test Results Summary")
        print("=" * 70)
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for suite_name, suite_results in self.results.items():
            passed = sum(1 for _, success, _ in suite_results if success)
            failed = len(suite_results) - passed
            total_tests += len(suite_results)
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "⚠️"
            print(f"{status_icon} {suite_name}: {passed}/{len(suite_results)} passed")
            
            # Show failed tests
            if failed > 0:
                for test_name, success, _ in suite_results:
                    if not success:
                        print(f"    ❌ {test_name}")
        
        # Overall summary
        print("\n" + "-" * 50)
        print(f"Total Tests Run: {total_tests}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"⏱️ Duration: {duration:.2f} seconds")
        
        # Final verdict
        print("\n" + "=" * 70)
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! The multi-user system is working correctly.")
        else:
            print(f"⚠️ {total_failed} test(s) failed. Please review the failures above.")
        print("=" * 70)
        
        return total_failed == 0
    
    def save_report(self, filename: str = "test_report.txt"):
        """Save detailed test report to file"""
        report_path = Path(f"tests/reports/{filename}")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, "w") as f:
            f.write("LabAcc Copilot Test Report\n")
            f.write("=" * 70 + "\n\n")
            
            for suite_name, suite_results in self.results.items():
                f.write(f"{suite_name}\n")
                f.write("-" * 50 + "\n")
                
                for test_name, success, output in suite_results:
                    status = "PASS" if success else "FAIL"
                    f.write(f"{test_name}: {status}\n")
                    
                    if not success and output:
                        f.write("Error Output:\n")
                        f.write(output[:500] + "\n")  # First 500 chars of error
                        f.write("\n")
                
                f.write("\n")
        
        print(f"\n📄 Detailed report saved to: {report_path}")

async def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run LabAcc Copilot test suite")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--category", action="append", help="Specific test category to run")
    parser.add_argument("-q", "--quick", action="store_true", help="Run only critical tests")
    parser.add_argument("-r", "--report", action="store_true", help="Save detailed report")
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    runner.print_header()
    
    if args.quick:
        # Quick mode: only run critical tests
        categories = ["API Tests", "Multi-User Tests"]
        print("\n⚡ Quick mode: Running only API and Multi-User tests")
    else:
        categories = args.category
    
    await runner.run_all_tests(categories)
    
    success = runner.print_summary()
    
    if args.report:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        runner.save_report(f"test_report_{timestamp}.txt")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)