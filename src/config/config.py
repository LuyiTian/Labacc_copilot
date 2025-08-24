"""
Configuration management for LabAcc Copilot.

This module loads configuration from config.yaml and provides
a centralized way to access configuration values throughout the application.
Environment variables can override config file values.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Singleton configuration manager."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from YAML file."""
        # Find config file - check multiple possible locations
        config_paths = [
            Path(__file__).parent.parent.parent / "config.yaml",  # Project root
            Path.cwd() / "config.yaml",  # Current working directory
            Path("/etc/labacc/config.yaml"),  # System config location
        ]
        
        config_file = None
        for path in config_paths:
            if path.exists():
                config_file = path
                break
        
        if config_file:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                self._config = {}
        else:
            logger.warning("No config file found, using defaults")
            self._config = {}
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        # Set defaults if not specified
        self._set_defaults()
    
    def _apply_env_overrides(self):
        """Override config values with environment variables."""
        # Project root path
        if os.environ.get("LABACC_PROJECT_ROOT"):
            self._set_nested("projects.root_path", os.environ["LABACC_PROJECT_ROOT"])
        
        # Server settings
        if os.environ.get("LABACC_SERVER_HOST"):
            self._set_nested("server.host", os.environ["LABACC_SERVER_HOST"])
        if os.environ.get("LABACC_SERVER_PORT"):
            self._set_nested("server.port", int(os.environ["LABACC_SERVER_PORT"]))
        
        # Auth secret key
        if os.environ.get("LABACC_SECRET_KEY"):
            self._set_nested("auth.secret_key", os.environ["LABACC_SECRET_KEY"])
        
        # Debug mode
        if os.environ.get("LABACC_DEBUG"):
            self._set_nested("development.debug", 
                           os.environ["LABACC_DEBUG"].lower() in ('true', '1', 'yes'))
    
    def _set_defaults(self):
        """Set default values if not specified in config."""
        defaults = {
            "projects": {
                "root_path": "data",
                "structure": {
                    "default_folders": ["experiments", ".labacc"],
                    "metadata_folder": ".labacc"
                }
            },
            "conversion": {
                "mineru_timeout": 120,
                "max_file_size": 100
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8002,
                "reload": True
            },
            "frontend": {
                "host": "0.0.0.0",
                "port": 5173
            },
            "auth": {
                "token_expiry_hours": 24,
                "secret_key": "default-secret-key-change-in-production"
            },
            "logging": {
                "level": "INFO"
            },
            "session": {
                "timeout_minutes": 1440,
                "max_per_user": 5
            },
            "development": {
                "debug": False,
                "hot_reload": True,
                "verbose_errors": True
            }
        }
        
        # Merge defaults with loaded config
        self._config = self._deep_merge(defaults, self._config)
    
    def _deep_merge(self, default: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _set_nested(self, path: str, value: Any):
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            path: Dot-separated path to config value (e.g., "projects.root_path")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        current = self._config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def get_project_root(self) -> Path:
        """Get the project root path as a Path object."""
        return Path(self.get("projects.root_path", "data"))
    
    def get_user_projects_path(self, user_id: str) -> Path:
        """Get the path to a specific user's projects directory."""
        return self.get_project_root() / f"{user_id}_projects"
    
    def get_conversion_timeout(self) -> int:
        """Get the conversion timeout in seconds."""
        return self.get("conversion.mineru_timeout", 120)
    
    def get_supported_formats(self) -> list:
        """Get list of supported file formats for conversion."""
        return self.get("conversion.supported_formats", [
            ".pdf", ".docx", ".doc", ".pptx", ".ppt", 
            ".xlsx", ".xls", ".html", ".htm"
        ])
    
    def get_server_config(self) -> Dict:
        """Get server configuration."""
        return self.get("server", {})
    
    def get_auth_secret(self) -> str:
        """Get authentication secret key."""
        # Always prefer environment variable for security
        return os.environ.get("LABACC_SECRET_KEY", 
                            self.get("auth.secret_key", "default-secret-key"))
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("development.debug", False)
    
    def get_deep_research_config(self) -> Dict:
        """Get deep research configuration."""
        return {
            "initial_search_query_count": self.get("deep_research.initial_search_query_count", 10),
            "max_research_loops": self.get("deep_research.max_research_loops", 5),
            "search_results_per_query": self.get("deep_research.search_results_per_query", 5),
            "verbose": self.get("deep_research.verbose", True),
            "response_language": self.get("deep_research.response_language", None)
        }
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")


# Global config instance
config = Config()


# Convenience functions for common access patterns
def get_project_root() -> Path:
    """Get the project root path."""
    return config.get_project_root()


def get_user_projects_path(user_id: str) -> Path:
    """Get path to user's projects directory."""
    return config.get_user_projects_path(user_id)


def get_config() -> Config:
    """Get the global config instance."""
    return config


# Export commonly used values
PROJECT_ROOT = config.get_project_root()
CONVERSION_TIMEOUT = config.get_conversion_timeout()
AUTH_SECRET = config.get_auth_secret()
DEBUG_MODE = config.is_debug()