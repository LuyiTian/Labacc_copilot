"""Pytest configuration and fixtures."""

import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch
import time
from typing import Generator


# Path to the backup directory
BACKUP_DIR = Path("/data/luyit/script/git/Labacc_copilot/data/bob_projects_backup_20250813_174456")
TEST_DATA_DIR = Path("/data/luyit/script/git/Labacc_copilot/data/bob_projects")


@pytest.fixture(autouse=True)
def mock_api_keys():
    """Automatically mock API keys for all tests."""
    env_vars = {
        "TAVILY_API_KEY": "test-tavily-key",
        "OPENAI_API_KEY": "test-openai-key",
        "SILICONFLOW_API_KEY": "test-siliconflow-key",
        "OPENROUTER_API_KEY": "test-openrouter-key",
    }
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Create subdirectories
    (data_dir / "experiments").mkdir()
    (data_dir / "ref").mkdir()
    (data_dir / "history").mkdir()
    
    return data_dir


@pytest.fixture(scope="session")
def restore_bob_projects() -> Generator[None, None, None]:
    """
    Session-level fixture that restores bob_projects from backup
    at the start and end of the entire test session.
    """
    # Backup current state (if needed) before tests
    if TEST_DATA_DIR.exists():
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        temp_backup = TEST_DATA_DIR.parent / f"bob_projects_test_backup_{timestamp}"
        shutil.copytree(TEST_DATA_DIR, temp_backup, dirs_exist_ok=False)
        print(f"\n[Setup] Created temporary backup at: {temp_backup}")
    
    # Restore from backup
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
    shutil.copytree(BACKUP_DIR, TEST_DATA_DIR)
    print(f"[Setup] Restored bob_projects from backup: {BACKUP_DIR}")
    
    yield  # Run all tests
    
    # Final cleanup - restore from backup again
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
    shutil.copytree(BACKUP_DIR, TEST_DATA_DIR)
    print(f"\n[Cleanup] Restored bob_projects to original state from backup")


@pytest.fixture
def reset_bob_projects():
    """
    Function-level fixture that resets bob_projects before each test.
    Use this for tests that modify bob_projects data.
    """
    # Reset before test
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
    shutil.copytree(BACKUP_DIR, TEST_DATA_DIR)
    
    yield TEST_DATA_DIR
    
    # Reset after test
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
    shutil.copytree(BACKUP_DIR, TEST_DATA_DIR)


@pytest.fixture
def bob_projects_path(restore_bob_projects) -> Path:
    """
    Provides path to bob_projects directory.
    Depends on session-level restore to ensure clean state.
    """
    return TEST_DATA_DIR


@pytest.fixture
def isolated_test_dir(tmp_path) -> Path:
    """
    Create an isolated test directory that won't affect bob_projects.
    Use this for tests that don't need actual bob_projects data.
    """
    test_dir = tmp_path / "isolated_test"
    test_dir.mkdir()
    
    # Create basic structure
    exp_dir = test_dir / "test_experiment"
    exp_dir.mkdir()
    
    # Create a basic README
    readme = exp_dir / "README.md"
    readme.write_text("""# Test Experiment

## Status
- Created: Test
- Type: Testing

## Files
- No files yet

## Insights
- No insights yet

## Change Log
- Experiment created for testing
""")
    
    return exp_dir


@pytest.fixture
def alice_projects_path() -> Path:
    """
    Provides path to alice_projects directory.
    This is production data - tests should NOT modify this!
    """
    alice_dir = Path("/data/luyit/script/git/Labacc_copilot/data/alice_projects")
    if not alice_dir.exists():
        alice_dir.mkdir(parents=True)
    return alice_dir


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "modifies_data: mark test as modifying bob_projects data"
    )
    config.addinivalue_line(
        "markers", "readonly: mark test as read-only, safe to run"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )