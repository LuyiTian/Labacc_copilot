"""Tests for LLM configuration and instances."""

import os
import pytest
from unittest.mock import patch, MagicMock


def test_llm_instance_creation():
    """Test creating LLM instances with different providers."""
    # Mock environment variables
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key",
        "SILICONFLOW_API_KEY": "test-siliconflow-key",
        "TAVILY_API_KEY": "test-tavily-key"
    }
    
    with patch.dict(os.environ, env_vars):
        from src.components.llm import get_llm_instance
        
        # Test OpenAI instance
        llm = get_llm_instance(model_name="gpt-4o")
        assert llm is not None
        assert llm.model == "gpt-4o"
        
        # Test SiliconFlow instance
        llm = get_llm_instance(model_name="siliconflow-qwen")
        assert llm is not None


def test_missing_api_key_error():
    """Test that missing API keys raise appropriate errors."""
    with patch.dict(os.environ, {"TAVILY_API_KEY": "test"}, clear=True):
        from src.components.llm import get_llm_instance
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            get_llm_instance(model_name="gpt-4o")


def test_structured_llm():
    """Test structured LLM creation for JSON outputs."""
    env_vars = {
        "OPENAI_API_KEY": "test-key",
        "TAVILY_API_KEY": "test-tavily-key"
    }
    
    with patch.dict(os.environ, env_vars):
        from src.components.llm import get_structured_llm
        
        llm = get_structured_llm(model_name="gpt-4o")
        assert llm is not None
        # Temperature should be lower for structured outputs
        assert llm.temperature == 0.1