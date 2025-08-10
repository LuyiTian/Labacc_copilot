"""
LabAcc Copilot LLM Configuration
Centralized configuration and setup for all LLM instances used in the wet-lab biology assistant.

Design Principles:
- Use environment variables for all API keys (no hardcoded secrets)
- Provide multiple model options for different tasks
- Include retry logic and error handling
- Support structured outputs with validation
- Integrate with observability tools (Langfuse)
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

def get_required_env(key: str, description: str = "") -> str:
    """Get a required environment variable or raise an error."""
    value = os.environ.get(key)
    if not value:
        raise ValueError(
            f"Required environment variable '{key}' not found. "
            f"{description}"
        )
    return value

def get_optional_env(key: str, default: str = "") -> str:
    """Get an optional environment variable with a default value."""
    return os.environ.get(key, default)

# Langfuse observability setup
_langfuse_handler = None
try:
    if get_optional_env("LANGFUSE_SECRET_KEY") and get_optional_env("LANGFUSE_PUBLIC_KEY"):
        from langfuse.callback import CallbackHandler
        _langfuse_handler = CallbackHandler()
        logger.info("✅ Langfuse callback handler initialized")
    else:
        logger.info("ℹ️  Langfuse keys not found - LLM interactions will not be logged")
except ImportError:
    # Optional dependency
    logger.info("Langfuse not installed - skipping observability setup")
except Exception as e:
    logger.error(f"❌ Failed to initialize Langfuse: {e}")

# Model configurations for different providers
# Optional external overrides loaded from JSON config (if present)
_EXTERNAL_CONFIG: Dict[str, Any] = {}
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "llm_config.json")
try:
    with open(os.path.abspath(_CONFIG_PATH), "r", encoding="utf-8") as f:
        _EXTERNAL_CONFIG = json.load(f)
        logger.info("🔧 Loaded external LLM config overrides from src/config/llm_config.json")
except FileNotFoundError:
    # It's optional; continue with defaults
    pass
except Exception as e:
    logger.warning(f"Failed to load external LLM config: {e}")


MODEL_CONFIGS = {
    # OpenAI models
    "gpt-4o": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o",
        "recommended_temperature": 0.7,
        "description": "OpenAI's most capable multimodal model, good for complex analysis",
    },
    "gpt-4o-mini": {
        "api_key_env": "OPENAI_API_KEY", 
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o-mini",
        "recommended_temperature": 0.7,
        "description": "Faster, cheaper OpenAI model for simpler tasks",
    },
    
    # SiliconFlow models
    "siliconflow-qwen": {
        "api_key_env": "SILICONFLOW_API_KEY",
        "base_url": "https://api.siliconflow.cn/v1", 
        "model_name": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "recommended_temperature": 0.7,
        "description": "Large Qwen model via SiliconFlow, good for complex reasoning",
    },
    "siliconflow-qwen-30b": {
        "api_key_env": "SILICONFLOW_API_KEY",
        "base_url": "https://api.siliconflow.cn/v1",
        "model_name": "Qwen/Qwen3-30B-A3B-Instruct-2507", 
        "recommended_temperature": 0.7,
        "description": "Medium Qwen model, good balance of speed and capability",
    },
    "siliconflow-qwen-8b": {
        "api_key_env": "SILICONFLOW_API_KEY",
        "base_url": "https://api.siliconflow.cn/v1",
        "model_name": "Qwen/Qwen3-8B",
        "recommended_temperature": 0.7,
        "description": "Fast smaller model for simple tasks",
    },
    
    # Anthropic Claude models
    "claude-sonnet": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,  # Uses default Anthropic endpoint
        "model_name": "claude-3-sonnet-20240229",
        "recommended_temperature": 0.7,
        "description": "Claude Sonnet, excellent for reasoning and analysis",
    },
    
    # Google Gemini models
    "gemini-pro": {
        "api_key_env": "GOOGLE_API_KEY", 
        "base_url": None,  # Uses default Google endpoint
        "model_name": "gemini-pro",
        "recommended_temperature": 0.8,
        "description": "Google's multimodal model, good for diverse tasks",
    },
}

# Apply external overrides if any
MODEL_CONFIGS = _EXTERNAL_CONFIG.get("model_configs", MODEL_CONFIGS)
AGENT_MODEL_ASSIGNMENTS = _EXTERNAL_CONFIG.get("agent_model_assignments", {}) or {}

# Role-based model assignments for different agent tasks
AGENT_MODEL_ASSIGNMENTS = {
    **{
        "query_writer": get_optional_env("QUERY_WRITER_MODEL", "siliconflow-qwen-30b"),
        "web_searcher": get_optional_env("WEB_SEARCHER_MODEL", "siliconflow-qwen-8b"),
        "analyst": get_optional_env("ANALYST_MODEL", "siliconflow-qwen-30b"),
        "critic": get_optional_env("CRITIC_MODEL", "siliconflow-qwen-30b"),
        "writer": get_optional_env("WRITER_MODEL", "siliconflow-qwen"),
        "planner": get_optional_env("PLANNER_MODEL", "siliconflow-qwen-30b"),
        "default": get_optional_env("DEFAULT_MODEL", "siliconflow-qwen-30b"),
    },
    **AGENT_MODEL_ASSIGNMENTS,
}

def get_available_models() -> Dict[str, str]:
    """Get list of available models with descriptions."""
    available = {}
    for model_name, config in MODEL_CONFIGS.items():
        try:
            # Check if API key is available
            get_required_env(config["api_key_env"])
            available[model_name] = config["description"]
        except ValueError:
            # Skip models without API keys
            continue
    return available

def get_llm_instance(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: int = 600,
    streaming: bool = False,
) -> ChatOpenAI:
    """
    Get a configured LangChain ChatOpenAI instance.
    
    Args:
        model_name: Name of the model to use. If None, uses default.
        temperature: Temperature for the model. If None, uses model's recommended temperature.
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
        streaming: Whether to enable streaming
        
    Returns:
        Configured ChatOpenAI instance
    """
    # Use default model if none specified
    if model_name is None:
        model_name = AGENT_MODEL_ASSIGNMENTS["default"]
    
    # Get model configuration
    config = MODEL_CONFIGS.get(model_name)
    if not config:
        available_models = list(MODEL_CONFIGS.keys())
        raise ValueError(
            f"Model '{model_name}' not found. Available models: {available_models}"
        )
    
    # Get API key
    try:
        api_key = get_required_env(config["api_key_env"])
    except ValueError as e:
        logger.error(f"Cannot create LLM instance for {model_name}: {e}")
        raise
    
    # Use model's recommended temperature if not specified
    if temperature is None:
        temperature = config["recommended_temperature"]
    
    # Build LLM configuration
    llm_config = {
        "model": config["model_name"],
        "openai_api_key": api_key,
        "temperature": temperature,
        "timeout": timeout,
        "streaming": streaming,
    }
    
    # Add base URL if specified
    if config["base_url"]:
        llm_config["openai_api_base"] = config["base_url"]
    
    # Add max_tokens if specified
    if max_tokens:
        llm_config["max_tokens"] = max_tokens
    
    # Create ChatOpenAI instance
    llm = ChatOpenAI(**llm_config)
    
    # Add Langfuse callback if available
    if _langfuse_handler:
        llm = llm.with_config(callbacks=[_langfuse_handler])
    
    logger.info(f"✅ Created LLM instance: {model_name} (temp={temperature})")
    return llm

def get_structured_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs
) -> ChatOpenAI:
    """
    Get an LLM instance configured for structured outputs (JSON).
    
    Args:
        model_name: Name of the model to use
        temperature: Temperature (defaults to lower value for structured outputs)
        **kwargs: Additional arguments for get_llm_instance
        
    Returns:
        ChatOpenAI instance configured for JSON output
    """
    # Use lower temperature for structured outputs if not specified
    if temperature is None:
        temperature = 0.1
        
    llm = get_llm_instance(
        model_name=model_name,
        temperature=temperature,
        **kwargs
    )
    
    # Configure for JSON output
    llm = llm.bind(response_format={"type": "json_object"})
    return llm

# Pre-configured LLM instances for different agent roles
class LLMFactory:
    """Factory class for creating role-specific LLM instances."""
    
    @staticmethod
    def get_query_writer() -> ChatOpenAI:
        """LLM for generating search queries."""
        return get_llm_instance(AGENT_MODEL_ASSIGNMENTS["query_writer"])
    
    @staticmethod 
    def get_web_searcher() -> ChatOpenAI:
        """LLM for processing web search results."""
        return get_llm_instance(AGENT_MODEL_ASSIGNMENTS["web_searcher"])
    
    @staticmethod
    def get_analyst() -> ChatOpenAI:
        """LLM for analyzing experimental data and images."""
        return get_llm_instance(AGENT_MODEL_ASSIGNMENTS["analyst"])
    
    @staticmethod
    def get_critic() -> ChatOpenAI:
        """LLM for evaluating results and suggesting improvements."""
        return get_llm_instance(AGENT_MODEL_ASSIGNMENTS["critic"])
    
    @staticmethod
    def get_writer() -> ChatOpenAI:
        """LLM for writing final decision cards and reports."""
        return get_llm_instance(AGENT_MODEL_ASSIGNMENTS["writer"])
    
    @staticmethod
    def get_planner() -> ChatOpenAI:
        """LLM for planning experiment analysis workflow."""
        return get_llm_instance(AGENT_MODEL_ASSIGNMENTS["planner"])

# Backward compatibility - expose commonly used instances
LLM_QUERY_WRITER = LLMFactory.get_query_writer()
LLM_TRIAGE = LLMFactory.get_critic()  # Maps to critic role
LLM_SMALL = LLMFactory.get_web_searcher()  # Maps to web searcher (fast model)

def get_langfuse_handler():
    """Get the Langfuse callback handler."""
    return _langfuse_handler

def validate_llm_configuration():
    """Validate that at least one LLM provider is properly configured."""
    available_models = get_available_models()
    if not available_models:
        raise ValueError(
            "No LLM providers configured. Please set API keys for at least one provider:\n"
            "- OpenAI: OPENAI_API_KEY\n"
            "- SiliconFlow: SILICONFLOW_API_KEY\n"
            "- Anthropic: ANTHROPIC_API_KEY\n"
            "- Google: GOOGLE_API_KEY"
        )
    
    logger.info(f"✅ Available LLM models: {list(available_models.keys())}")
    return available_models

# Validate configuration on import
try:
    validate_llm_configuration()
except ValueError as e:
    logger.error(f"❌ LLM configuration validation failed: {e}")
    # Don't raise here to allow for partial imports, but log the error