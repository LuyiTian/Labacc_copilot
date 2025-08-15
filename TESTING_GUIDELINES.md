# Testing Guidelines for LabAcc Copilot

## 🚨 CRITICAL RULE: Always Clean Up bob_projects

**bob_projects is sacred test data that MUST remain unchanged after tests**

### Why This Matters
- `bob_projects` contains reference test data for evaluations
- Any modifications persist and can break future tests
- The backup (`bob_projects_backup_20250813_174456`) is our source of truth

## ✅ Proper Test Practices

### 1. For Standalone Test Scripts

Always include cleanup in your test scripts:

```python
import shutil
from pathlib import Path

async def test_something():
    # Create test folder
    test_dir = Path("data/bob_projects/exp_test_001")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Do your testing here
        pass
    finally:
        # ALWAYS clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")
```

### 2. Using the Test Cleanup Utility

We provide a cleanup utility for more complex scenarios:

```python
from src.utils.test_cleanup import TestCleanup

async def test_with_cleanup():
    with TestCleanup() as cleanup:
        # Register folders you'll create
        cleanup.register_test_folder("exp_test_001")
        cleanup.register_test_folder("exp_test_002")
        
        # Do your testing
        # Folders are automatically cleaned up when exiting context
```

### 3. For Pytest Tests

Use the provided fixtures that handle restoration:

```python
def test_something(reset_bob_projects):
    # This fixture automatically restores bob_projects after each test
    # Modify bob_projects as needed
    # It will be restored when test completes
```

## 🧹 Emergency Cleanup

If you accidentally leave test artifacts:

```python
from src.utils.test_cleanup import ensure_bob_projects_clean

# This removes any folders not in the original backup
ensure_bob_projects_clean()
```

Or manually restore from backup:

```bash
rm -rf data/bob_projects
cp -r data/bob_projects_backup_20250813_174456 data/bob_projects
```

## 📋 Test Checklist

Before committing test code:

- [ ] Test includes cleanup code in `finally` block or context manager
- [ ] No hardcoded test folders left in bob_projects
- [ ] Test can run multiple times without side effects
- [ ] Used `TestCleanup` utility for complex scenarios
- [ ] Verified bob_projects is clean after test run

## ⚠️ Common Mistakes to Avoid

1. **Creating test folders without cleanup**
   ```python
   # ❌ BAD
   test_dir = Path("data/bob_projects/exp_test")
   test_dir.mkdir()
   # Test ends without cleanup
   ```

2. **Skipping cleanup on error**
   ```python
   # ❌ BAD
   test_dir.mkdir()
   run_test()  # If this fails...
   shutil.rmtree(test_dir)  # This never runs!
   ```

3. **Using alice_projects for testing**
   ```python
   # ❌ BAD - alice_projects is for production data
   test_dir = Path("data/alice_projects/exp_test")
   ```

## ✨ Best Practices

1. **Always use bob_projects for testing** - Never alice_projects
2. **Clean up in finally blocks** - Ensures cleanup even on failure
3. **Use unique test folder names** - Include timestamps or random IDs
4. **Test your cleanup** - Verify folders are actually removed
5. **Document test artifacts** - Comment what folders your test creates

## 🔍 Monitoring Test Data Integrity

Run this check periodically:

```bash
# Check if bob_projects matches backup
diff -r data/bob_projects data/bob_projects_backup_20250813_174456

# Should show no differences
```

Remember: **Clean tests are happy tests!** 🎉