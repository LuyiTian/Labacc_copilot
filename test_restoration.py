#!/usr/bin/env python3
"""
Test script to verify bob_projects restoration works correctly
"""
import os
import sys
import hashlib
from pathlib import Path
import shutil

def get_directory_hash(dir_path: Path) -> str:
    """Calculate a hash of all files in a directory"""
    hash_obj = hashlib.md5()
    
    for file_path in sorted(dir_path.rglob("*")):
        if file_path.is_file():
            # Include file path and content in hash
            hash_obj.update(str(file_path.relative_to(dir_path)).encode())
            hash_obj.update(file_path.read_bytes())
    
    return hash_obj.hexdigest()


def test_restoration():
    """Test that bob_projects restoration works correctly"""
    
    backup_dir = Path("/data/luyit/script/git/Labacc_copilot/data/bob_projects_backup_20250813_174456")
    test_dir = Path("/data/luyit/script/git/Labacc_copilot/data/bob_projects")
    
    print("=" * 60)
    print("Testing Bob Projects Restoration")
    print("=" * 60)
    
    # 1. Get hash of backup
    print("\n1. Calculating backup directory hash...")
    backup_hash = get_directory_hash(backup_dir)
    print(f"   Backup hash: {backup_hash}")
    
    # 2. Get current hash
    print("\n2. Checking current bob_projects state...")
    current_hash = get_directory_hash(test_dir)
    print(f"   Current hash: {current_hash}")
    
    if current_hash == backup_hash:
        print("   ✅ bob_projects is already in clean state!")
    else:
        print("   ⚠️ bob_projects has been modified")
    
    # 3. Test restoration function
    print("\n3. Testing restoration process...")
    
    # First, make a small change to verify restoration works
    test_file = test_dir / "exp_001_protocol_test" / "test_file.tmp"
    test_file.write_text("This is a test modification")
    
    modified_hash = get_directory_hash(test_dir)
    print(f"   Modified hash: {modified_hash}")
    
    # Now restore
    if test_dir.exists():
        shutil.rmtree(test_dir)
    shutil.copytree(backup_dir, test_dir)
    
    restored_hash = get_directory_hash(test_dir)
    print(f"   Restored hash: {restored_hash}")
    
    # 4. Verify restoration
    print("\n4. Verification:")
    if restored_hash == backup_hash:
        print("   ✅ Restoration successful - hashes match!")
    else:
        print("   ❌ Restoration failed - hashes don't match")
        return 1
    
    # 5. Test with TEST_MODE
    print("\n5. Testing with TEST_MODE environment variable...")
    os.environ["TEST_MODE"] = "true"
    
    # Import and test memory tools
    sys.path.append(str(Path(__file__).parent / "src"))
    from src.memory.memory_tools import get_memory_manager
    
    manager = get_memory_manager("exp_001_protocol_test")
    if "bob_projects" in str(manager.project_root):
        print("   ✅ TEST_MODE correctly routes to bob_projects")
    else:
        print(f"   ❌ TEST_MODE not working, using: {manager.project_root}")
    
    # Clean up
    del os.environ["TEST_MODE"]
    
    # 6. Final verification
    print("\n6. Final state check:")
    final_hash = get_directory_hash(test_dir)
    if final_hash == backup_hash:
        print("   ✅ bob_projects remains in clean state")
        print("\n" + "=" * 60)
        print("✅ All restoration tests passed!")
        print("=" * 60)
        return 0
    else:
        print("   ❌ bob_projects state changed unexpectedly")
        return 1


if __name__ == "__main__":
    sys.exit(test_restoration())