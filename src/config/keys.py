"""
Configuration for non-LLM API keys.

All API keys must be set as environment variables - no hardcoded secrets allowed.
Set environment variables in your .bashrc file.

Usage:
    from src.config.keys import get_tavily_api_key
    api_key = get_tavily_api_key()
"""

import os


# Tavily API - Required for deep research functionality
def get_tavily_api_key() -> str:
    """Get Tavily API key from environment variable."""
    value = os.environ.get("TAVILY_API_KEY")
    if not value:
        raise ValueError(
            "Required environment variable 'TAVILY_API_KEY' not found. "
            "Get your API key from https://tavily.com/"
        )
    return value

# Langfuse observability (optional)
def get_langfuse_config():
    """Get Langfuse configuration if available."""
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")

    if public_key and secret_key:
        return {
            "public_key": public_key,
            "secret_key": secret_key,
            "host": os.environ.get("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
        }
    return None

# For backward compatibility with existing code that imports API_KEYS
API_KEYS = {
    "tavily": {
        "api_key": get_tavily_api_key()
    }
}
