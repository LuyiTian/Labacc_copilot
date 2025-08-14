#!/usr/bin/env python3
"""
LabAcc Copilot Unit Test Runner
Runs fast, isolated unit tests for code correctness verification

This script ONLY runs unit tests using pytest.
For agent evaluation, use: python run_evaluation.py
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time


def run_unit_tests(test_args: list = None):
    """Run unit tests with proper configuration"""
    
    print("🧪 LabAcc Copilot Unit Test Runner")
    print("=" * 50)
    print("Testing: Individual components and functions")
    print("Method: Fast, isolated, deterministic tests")
    print("Expected: <30 seconds total execution time")
    print("-" * 50)
    
    # Base pytest command
    cmd = ["uv", "run", "pytest", "tests/unit/"]
    
    # Add default options
    default_args = [
        "-v",                    # Verbose output
        "--tb=short",           # Short traceback format
        "--strict-markers",     # Strict marker checking
        "--disable-warnings",   # Disable warnings for cleaner output
        "-x",                   # Stop on first failure
    ]
    
    # Add coverage if not in CI
    if "--no-cov" not in (test_args or []):
        default_args.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-fail-under=80"  # Require 80% coverage
        ])
    
    cmd.extend(default_args)
    
    # Add user-provided arguments
    if test_args:
        cmd.extend(test_args)
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=False)
        execution_time = time.time() - start_time
        
        print("\n" + "=" * 50)
        print(f"⏱️  Execution time: {execution_time:.1f} seconds")
        
        if result.returncode == 0:
            print("✅ All unit tests passed!")
            if execution_time > 30:
                print("⚠️  WARNING: Tests took longer than expected (>30s)")
                print("   Consider optimizing slow tests or using mocks")
        else:
            print("❌ Some unit tests failed")
            print("💡 Fix failing tests before continuing development")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure 'uv' is installed and in PATH")
        return 1


def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Run unit tests for LabAcc Copilot components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_unit_tests.py                    # Run all unit tests (default)
  python run_unit_tests.py --fast             # Skip coverage for faster execution
  python run_unit_tests.py --last-failed      # Run only previously failed tests
        """
    )
    
    # Options
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip coverage reporting for faster execution"
    )
    
    # Pytest pass-through options
    parser.add_argument(
        "--last-failed",
        action="store_true",
        help="Run only tests that failed in the last run"
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Show which tests would be run without executing them"
    )
    parser.add_argument(
        "-k",
        type=str,
        help="Run tests matching the given keyword expression"
    )
    parser.add_argument(
        "--maxfail",
        type=int,
        help="Stop after N test failures"
    )
    
    args = parser.parse_args()
    
    # Build pytest arguments
    test_args = []
    
    # Handle fast mode
    if args.fast:
        test_args.append("--no-cov")
        print("🚀 Fast mode: Skipping coverage reporting")
    
    # Handle pytest options
    if args.last_failed:
        test_args.append("--lf")
    if args.collect_only:
        test_args.append("--collect-only")
    if args.k:
        test_args.extend(["-k", args.k])
    if args.maxfail:
        test_args.extend(["--maxfail", str(args.maxfail)])
    
    return run_unit_tests(test_args)


if __name__ == "__main__":
    sys.exit(main())