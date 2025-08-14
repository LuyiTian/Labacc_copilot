#!/usr/bin/env python3
"""
Test Runner with Data Integrity Verification
Ensures bob_projects is properly restored before and after test runs
"""

import sys
import subprocess
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import json


class TestDataVerifier:
    """Verify test data integrity before and after test runs"""
    
    def __init__(self):
        self.backup_dir = Path("/data/luyit/script/git/Labacc_copilot/data/bob_projects_backup_20250813_174456")
        self.test_dir = Path("/data/luyit/script/git/Labacc_copilot/data/bob_projects")
        
    def calculate_dir_hash(self, directory: Path) -> str:
        """Calculate hash of directory contents for comparison"""
        if not directory.exists():
            return "MISSING"
            
        file_hashes = []
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file():
                rel_path = file_path.relative_to(directory)
                try:
                    content = file_path.read_bytes()
                    file_hash = hashlib.md5(content).hexdigest()
                    file_hashes.append(f"{rel_path}:{file_hash}")
                except Exception as e:
                    file_hashes.append(f"{rel_path}:ERROR:{str(e)}")
                    
        return hashlib.md5("\n".join(file_hashes).encode()).hexdigest()
    
    def verify_backup_exists(self) -> bool:
        """Verify backup directory exists and has content"""
        if not self.backup_dir.exists():
            print(f"❌ ERROR: Backup directory not found: {self.backup_dir}")
            return False
            
        file_count = len(list(self.backup_dir.rglob("*")))
        if file_count < 5:  # Should have at least some files
            print(f"❌ ERROR: Backup directory seems empty (only {file_count} items)")
            return False
            
        print(f"✅ Backup directory verified: {file_count} items")
        return True
    
    def restore_from_backup(self) -> bool:
        """Restore test directory from backup"""
        try:
            print(f"🔄 Restoring bob_projects from backup...")
            
            # Remove existing test directory
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
                
            # Copy from backup
            shutil.copytree(self.backup_dir, self.test_dir)
            
            print(f"✅ Successfully restored from backup")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to restore from backup: {e}")
            return False
    
    def verify_restoration(self) -> bool:
        """Verify test directory matches backup"""
        backup_hash = self.calculate_dir_hash(self.backup_dir)
        test_hash = self.calculate_dir_hash(self.test_dir)
        
        if backup_hash == test_hash:
            print(f"✅ Test directory matches backup (hash: {test_hash[:8]}...)")
            return True
        else:
            print(f"⚠️  WARNING: Test directory differs from backup")
            print(f"   Backup hash:  {backup_hash[:8]}...")
            print(f"   Test hash:    {test_hash[:8]}...")
            return False
    
    def create_verification_report(self, phase: str) -> dict:
        """Create detailed verification report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "backup_exists": self.backup_dir.exists(),
            "test_dir_exists": self.test_dir.exists(),
            "backup_hash": self.calculate_dir_hash(self.backup_dir),
            "test_hash": self.calculate_dir_hash(self.test_dir),
            "matches": False
        }
        
        report["matches"] = report["backup_hash"] == report["test_hash"]
        
        # Count files in each directory
        if self.backup_dir.exists():
            report["backup_file_count"] = len(list(self.backup_dir.rglob("*.csv"))) + \
                                         len(list(self.backup_dir.rglob("*.txt"))) + \
                                         len(list(self.backup_dir.rglob("*.md")))
        
        if self.test_dir.exists():
            report["test_file_count"] = len(list(self.test_dir.rglob("*.csv"))) + \
                                       len(list(self.test_dir.rglob("*.txt"))) + \
                                       len(list(self.test_dir.rglob("*.md")))
        
        return report


def run_tests_with_verification(test_args: list = None):
    """Run tests with pre and post verification"""
    
    verifier = TestDataVerifier()
    
    print("\n" + "="*60)
    print("🧪 LabAcc Copilot Test Runner with Data Verification")
    print("="*60)
    
    # Step 1: Verify backup exists
    if not verifier.verify_backup_exists():
        print("\n❌ Cannot proceed without valid backup")
        return 1
    
    # Step 2: Create pre-test report
    pre_report = verifier.create_verification_report("pre-test")
    print(f"\n📋 Pre-test verification:")
    print(f"   Backup files: {pre_report.get('backup_file_count', 'N/A')}")
    print(f"   Test files:   {pre_report.get('test_file_count', 'N/A')}")
    
    # Step 3: Restore from backup
    if not verifier.restore_from_backup():
        print("\n❌ Failed to restore test data")
        return 1
    
    # Step 4: Verify restoration
    if not verifier.verify_restoration():
        print("⚠️  Continuing anyway, but results may be unreliable")
    
    # Step 5: Run tests
    print("\n" + "-"*60)
    print("🚀 Running tests...")
    print("-"*60 + "\n")
    
    # Prepare test command
    if test_args:
        cmd = ["python", "-m", "pytest"] + test_args
    else:
        cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    # Run tests
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    print("\n" + "-"*60)
    print("✅ Tests completed")
    print("-"*60)
    
    # Step 6: Post-test verification
    post_report = verifier.create_verification_report("post-test")
    print(f"\n📋 Post-test verification:")
    print(f"   Test files after: {post_report.get('test_file_count', 'N/A')}")
    
    # Step 7: Final restoration
    print("\n🔄 Final cleanup: Restoring original state...")
    if verifier.restore_from_backup():
        print("✅ Test data restored to original state")
    else:
        print("⚠️  WARNING: Could not restore test data to original state")
    
    # Step 8: Final verification
    final_report = verifier.create_verification_report("final")
    
    # Save verification report
    report_file = Path("tests/reports") / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, "w") as f:
        json.dump({
            "pre_test": pre_report,
            "post_test": post_report,
            "final": final_report,
            "test_exit_code": result.returncode
        }, f, indent=2)
    
    print(f"\n📄 Verification report saved to: {report_file}")
    
    # Summary
    print("\n" + "="*60)
    if final_report["matches"]:
        print("✅ SUCCESS: Test data properly restored")
    else:
        print("⚠️  WARNING: Test data may have been modified")
    
    print(f"🧪 Test Result: {'PASSED' if result.returncode == 0 else 'FAILED'}")
    print("="*60 + "\n")
    
    return result.returncode


if __name__ == "__main__":
    # Pass any command line arguments to pytest
    test_args = sys.argv[1:] if len(sys.argv) > 1 else None
    exit_code = run_tests_with_verification(test_args)
    sys.exit(exit_code)