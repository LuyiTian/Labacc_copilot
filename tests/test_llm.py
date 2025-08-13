"""Tests for LLM configuration and instances."""

import os
import pytest
from unittest.mock import patch, MagicMock


def test_llm_instance_creation():
    """Test creating LLM instances with different providers."""
    # Mock environment variables
    env_vars = {
        "SILICONFLOW_API_KEY": "test-siliconflow-key",
        "TAVILY_API_KEY": "test-tavily-key"
    }
    
    with patch.dict(os.environ, env_vars):
        from src.components.llm import get_llm_instance
        
        # Test SiliconFlow instance
        llm = get_llm_instance(model_name="siliconflow-qwen-30b")
        assert llm is not None
        # Ensure instance is created and callable for chat
        assert hasattr(llm, "invoke")


def test_missing_api_key_error():
    """Test that missing API keys raise appropriate errors."""
    with patch.dict(os.environ, {"TAVILY_API_KEY": "test"}, clear=True):
        from src.components.llm import get_llm_instance
        
        with pytest.raises(ValueError, match="SILICONFLOW_API_KEY"):
            get_llm_instance(model_name="siliconflow-qwen-30b")


def test_structured_llm():
    """Test structured LLM creation for JSON outputs."""
    env_vars = {
        "SILICONFLOW_API_KEY": "test-key",
        "TAVILY_API_KEY": "test-tavily-key"
    }
    
    with patch.dict(os.environ, env_vars):
        from src.components.llm import get_structured_llm
        
        llm = get_structured_llm(model_name="siliconflow-qwen-30b")
        assert llm is not None
        # Temperature should be lower for structured outputs
        assert llm.temperature == 0.1