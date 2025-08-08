"""
Secure configuration file for API keys and configuration.

All API keys must be set as environment variables - no hardcoded secrets allowed.
Create a .env file or set environment variables with the required keys.

Usage:
    from src.config.keys import API_KEYS
    api_key = API_KEYS["service_name"]["api_key"]
"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_required_env(key: str, description: str = "") -> str:
    """Get a required environment variable or raise an error."""
    value = os.environ.get(key)
    if not value:
        raise ValueError(
            f"Required environment variable '{key}' not found. "
            f"{description}. Please set this in your .env file or environment."
        )
    return value

def get_optional_env(key: str, default: str = "") -> str:
    """Get an optional environment variable with a default value."""
    return os.environ.get(key, default)

# Build API configuration from environment variables only
API_KEYS: dict = {
    # OpenAI/Compatible API configuration
    "openai": {
        "openai_api_key": get_required_env("OPENAI_API_KEY", "Get from https://platform.openai.com/api-keys"),
        "openai_api_base": get_optional_env("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": get_optional_env("OPENAI_MODEL", "gpt-4o"),
        "temperature": float(get_optional_env("OPENAI_TEMPERATURE", "0.7")),
    },
    
    # SiliconFlow API configuration
    "siliconflow": {
        "openai_api_key": get_required_env("SILICONFLOW_API_KEY", "Get from SiliconFlow provider"),
        "openai_api_base": get_optional_env("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        "model": get_optional_env("SILICONFLOW_MODEL", "Qwen/Qwen3-235B-A22B-Instruct-2507"),
        "temperature": float(get_optional_env("SILICONFLOW_TEMPERATURE", "1.0")),
    },
    
    "siliconflow-Qwen3-30B-A3B": {
        "openai_api_key": get_required_env("SILICONFLOW_API_KEY", "Get from SiliconFlow provider"),
        "openai_api_base": get_optional_env("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        "model": get_optional_env("SILICONFLOW_MODEL_30B", "Qwen/Qwen3-30B-A3B-Instruct-2507"),
        "temperature": float(get_optional_env("SILICONFLOW_TEMPERATURE", "0.7")),
        "extra_body": {"enable_thinking": False},
    },
    
    "siliconflow-Qwen3-8B": {
        "openai_api_key": get_required_env("SILICONFLOW_API_KEY", "Get from SiliconFlow provider"),
        "openai_api_base": get_optional_env("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        "model": get_optional_env("SILICONFLOW_MODEL_8B", "Qwen/Qwen3-8B"),
        "temperature": float(get_optional_env("SILICONFLOW_TEMPERATURE", "0.7")),
        "extra_body": {"enable_thinking": False},
    },
    
    # Anthropic API configuration
    "anthropic": {
        "anthropic_api_key": get_optional_env("ANTHROPIC_API_KEY"),
        "model": get_optional_env("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
        "temperature": float(get_optional_env("ANTHROPIC_TEMPERATURE", "0.7")),
    },
    
    # Google API configuration
    "google": {
        "google_api_key": get_optional_env("GOOGLE_API_KEY"),
        "model": get_optional_env("GOOGLE_MODEL", "gemini-pro"),
        "temperature": float(get_optional_env("GOOGLE_TEMPERATURE", "0.7")),
    },
    
    # Langfuse observability platform configuration
    "langfuse": {
        "public_key": get_optional_env("LANGFUSE_PUBLIC_KEY"),
        "secret_key": get_optional_env("LANGFUSE_SECRET_KEY"), 
        "host": get_optional_env("LANGFUSE_HOST", "https://us.cloud.langfuse.com"),
    },
    
    # Tavily search API configuration
    "tavily": {
        "api_key": get_required_env("TAVILY_API_KEY", "Get from https://tavily.com/")
    },
}

# Validate that required services have keys
def validate_configuration():
    """Validate that required API keys are present."""
    required_services = ["tavily"]  # Add more as needed
    
    for service in required_services:
        if service not in API_KEYS:
            raise ValueError(f"Configuration for required service '{service}' not found")
        
        service_config = API_KEYS[service]
        if "api_key" in service_config and not service_config["api_key"]:
            raise ValueError(f"API key for required service '{service}' is empty")

# Run validation on import
validate_configuration()