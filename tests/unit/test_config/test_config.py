"""Tests for configuration management."""

import os
import pytest
from unittest.mock import patch


def test_tavily_api_key_required():
    """Test that Tavily API key is required."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="TAVILY_API_KEY"):
            from src.config.keys import get_tavily_api_key
            get_tavily_api_key()


def test_tavily_api_key_from_env():
    """Test loading Tavily API key from environment."""
    test_key = "test-tavily-key"
    with patch.dict(os.environ, {"TAVILY_API_KEY": test_key}):
        from src.config.keys import get_tavily_api_key
        assert get_tavily_api_key() == test_key


def test_langfuse_config_optional():
    """Test that Langfuse config is optional."""
    with patch.dict(os.environ, {}, clear=True):
        from src.config.keys import get_langfuse_config
        assert get_langfuse_config() is None


def test_langfuse_config_from_env():
    """Test loading Langfuse config from environment."""
    with patch.dict(os.environ, {
        "LANGFUSE_PUBLIC_KEY": "public-key",
        "LANGFUSE_SECRET_KEY": "secret-key",
        "LANGFUSE_HOST": "https://custom.host"
    }):
        from src.config.keys import get_langfuse_config
        config = get_langfuse_config()
        assert config["public_key"] == "public-key"
        assert config["secret_key"] == "secret-key"
        assert config["host"] == "https://custom.host"