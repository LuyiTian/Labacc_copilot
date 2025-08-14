"""
Unit Test Configuration and Fixtures
Provides isolated, fast fixtures for unit testing individual components
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest


@pytest.fixture(autouse=True)
def mock_api_keys():
    """Mock all API keys for unit tests - no real API calls allowed"""
    env_vars = {
        "TAVILY_API_KEY": "unit-test-tavily-key",
        "OPENAI_API_KEY": "unit-test-openai-key", 
        "SILICONFLOW_API_KEY": "unit-test-siliconflow-key",
        "OPENROUTER_API_KEY": "unit-test-openrouter-key",
    }
    with pytest.MonkeyPatch().context() as m:
        for key, value in env_vars.items():
            m.setenv(key, value)
        yield


@pytest.fixture
def temp_dir():
    """Create isolated temporary directory for unit tests"""
    with tempfile.TemporaryDirectory(prefix="unit_test_") as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_llm():
    """Mock LLM instance for unit tests - no real LLM calls"""
    mock = MagicMock()
    mock.invoke.return_value = "Mock LLM response for unit testing"
    mock.model_name = "mock-model"
    return mock


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing file operations"""
    return """sample,cell_count,viability,treatment
control,50000,95.2,none
treated,35000,88.7,drug_a
stressed,15000,72.1,heat_shock"""


@pytest.fixture
def sample_readme_content():
    """Sample README content for testing memory operations"""
    return """# Experiment: Unit Test

## Status
- Created: 2025-01-14
- Type: Unit Testing

## Files
- No files yet

## Insights
- Unit test experiment

## Change Log
- Experiment created for unit testing
"""


@pytest.fixture
def temp_experiment_dir(temp_dir):
    """Create temporary experiment directory with basic structure"""
    exp_dir = temp_dir / "test_experiment"
    exp_dir.mkdir()
    
    # Create README
    readme = exp_dir / "README.md"
    readme.write_text("""# Test Experiment

## Status
- Created: Test
- Type: Unit Test

## Files
- No files yet

## Insights
- No insights yet

## Change Log
- Created for unit testing
""")
    
    return exp_dir


@pytest.fixture
def mock_file_analyzer():
    """Mock file analyzer for testing without actual file processing"""
    mock = MagicMock()
    mock.analyze_csv.return_value = {
        "columns": ["sample", "cell_count", "viability"],
        "rows": 3,
        "summary": "Mock CSV analysis"
    }
    mock.analyze_image.return_value = {
        "type": "image",
        "description": "Mock image analysis"
    }
    mock.analyze_text.return_value = {
        "type": "text", 
        "summary": "Mock text analysis"
    }
    return mock


@pytest.fixture
def mock_auto_memory_updater():
    """Mock auto memory updater for testing"""
    mock = MagicMock()
    mock.process_uploaded_file.return_value = True
    mock.update_readme.return_value = True
    return mock


# Unit test markers
def pytest_configure(config):
    """Configure pytest with unit test specific markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests - fast, isolated, deterministic"
    )
    config.addinivalue_line(
        "markers", "memory: Unit tests for memory system components"
    )
    config.addinivalue_line(
        "markers", "tools: Unit tests for tool components"
    )
    config.addinivalue_line(
        "markers", "api: Unit tests for API components"
    )
    config.addinivalue_line(
        "markers", "config: Unit tests for configuration components"
    )