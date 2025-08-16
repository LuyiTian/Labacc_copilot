#!/usr/bin/env python3
"""
Unit tests for file registry functionality.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent dirs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.utils.test_session import TestSession


def test_registry_creation():
    """Test that file registry is created correctly."""
    
    print("\n🧪 Testing: File Registry Creation")
    
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, _ = test_session.setup()
    
    try:
        registry_path = project_root / experiment_id / ".labacc" / "file_registry.json"
        
        # Check registry exists
        assert registry_path.exists(), "Registry not created"
        print("   ✅ Registry file exists")
        
        # Check registry structure
        registry = json.loads(registry_path.read_text())
        assert "version" in registry, "No version field"
        assert registry["version"] == "3.0", f"Wrong version: {registry['version']}"
        assert "experiment_id" in registry, "No experiment_id field"
        assert "files" in registry, "No files field"
        assert isinstance(registry["files"], dict), "Files field not a dict"
        
        print("   ✅ Registry structure valid")
        
        test_session.cleanup()
        print("\n✅ PASSED: File Registry Creation")
        return True
        
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
        test_session.cleanup()
        return False


def test_registry_update():
    """Test updating the file registry."""
    
    print("\n🧪 Testing: File Registry Update")
    
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, _ = test_session.setup()
    
    try:
        registry_path = project_root / experiment_id / ".labacc" / "file_registry.json"
        
        # Load registry
        registry = json.loads(registry_path.read_text())
        
        # Add a file entry
        registry["files"]["test.pdf"] = {
            "original_path": f"{experiment_id}/originals/test.pdf",
            "converted_path": f"{experiment_id}/test.md",
            "upload_time": datetime.now().isoformat(),
            "conversion": {
                "status": "success",
                "method": "MockConversion",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Save updated registry
        registry_path.write_text(json.dumps(registry, indent=2))
        print("   ✅ Registry updated")
        
        # Verify update persisted
        reloaded = json.loads(registry_path.read_text())
        assert "test.pdf" in reloaded["files"], "File not in registry"
        assert reloaded["files"]["test.pdf"]["conversion"]["status"] == "success"
        
        print("   ✅ Update persisted correctly")
        
        test_session.cleanup()
        print("\n✅ PASSED: File Registry Update")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        test_session.cleanup()
        return False


if __name__ == "__main__":
    # Run tests
    results = []
    
    results.append(test_registry_creation())
    results.append(test_registry_update())
    
    # Summary
    print("\n" + "="*40)
    passed = sum(1 for r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        sys.exit(0)
    else:
        print(f"⚠️  {total - passed}/{total} tests failed")
        sys.exit(1)