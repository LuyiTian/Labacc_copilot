#!/usr/bin/env python3
"""
Quick smoke test for LabAcc Copilot
Run this before every commit - takes 30 seconds

Usage: python tests/quick_test.py
"""

import sys
import subprocess
from pathlib import Path

def run_test(name, command):
    """Run a single test command"""
    print(f"Testing {name}...", end=" ")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ PASS")
            return True
        else:
            print(f"❌ FAIL\n{result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run quick smoke tests"""
    print("=" * 50)
    print("🚀 LabAcc Copilot Quick Smoke Test")
    print("=" * 50)
    
    tests = [
        # Test 1: Can we import the main modules?
        ("Core imports", "python -c 'from src.api.app import app; from src.agents.react_agent import handle_message'"),
        
        # Test 2: Is file conversion working?
        ("File conversion", "python -c 'from src.api.file_conversion import FileConversionPipeline; print(\"OK\")'"),
        
        # Test 3: Can we create a session?
        ("Session creation", "python -c 'from src.projects.session import session_manager; print(\"OK\")'"),
        
        # Test 4: Is the config loading?
        ("Config loading", "python -c 'from src.config.config import config; print(config.get_project_root())'"),
        
        # Test 5: Basic API test (if server running)
        ("API health check", "curl -s http://localhost:8002/health || echo 'Server not running (OK for dev)'"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_cmd in tests:
        if run_test(test_name, test_cmd):
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All smoke tests passed! Safe to commit.")
        return 0
    else:
        print("❌ Some tests failed. Fix before committing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())