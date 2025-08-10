"""Pytest configuration and fixtures."""

import os
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_api_keys():
    """Automatically mock API keys for all tests."""
    env_vars = {
        "TAVILY_API_KEY": "test-tavily-key",
        "OPENAI_API_KEY": "test-openai-key",
        "SILICONFLOW_API_KEY": "test-siliconflow-key",
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