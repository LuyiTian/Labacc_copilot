"""
Storage Configuration for LabAcc Copilot

This module provides centralized configuration for storage paths.
In the future, this will read from a config file to determine where
projects and user data should be stored (potentially outside the codebase).

For now, it uses the existing data/ folder structure.
"""

import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StorageConfig:
    """Central storage configuration"""
    
    def __init__(self):
        # Future: Read from config file (e.g., ~/.labacc/config.json or env variable)
        # For now, use relative paths within the project
        self._storage_root = None
        self._config_file = Path.home() / ".labacc" / "config.json"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or environment"""
        # Try environment variable first
        env_storage = os.environ.get("LABACC_STORAGE_ROOT")
        if env_storage:
            self._storage_root = Path(env_storage)
            logger.info(f"Using storage root from environment: {self._storage_root}")
            return
        
        # Try config file
        if self._config_file.exists():
            try:
                import json
                with open(self._config_file, 'r') as f:
                    config = json.load(f)
                    if "storage_root" in config:
                        self._storage_root = Path(config["storage_root"])
                        logger.info(f"Using storage root from config file: {self._storage_root}")
                        return
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Default to data/ folder
        self._storage_root = Path("data")
        logger.info(f"Using default storage root: {self._storage_root}")
    
    @property
    def storage_root(self) -> Path:
        """Get the root storage path for all projects"""
        return self._storage_root
    
    @property
    def projects_root(self) -> Path:
        """Get the root path for project storage"""
        # In future, this might be storage_root / "projects"
        # For now, it's just the storage root
        return self._storage_root
    
    @property
    def users_file(self) -> Path:
        """Get the path to users database file"""
        return self._storage_root / "users.json"
    
    @property
    def projects_metadata_file(self) -> Path:
        """Get the path to projects metadata file"""
        return self._storage_root / "projects_metadata.json"
    
    def get_project_path(self, project_id: str) -> Path:
        """Get the full path to a specific project"""
        return self.projects_root / project_id
    
    def ensure_storage_exists(self):
        """Ensure all required storage directories exist"""
        self._storage_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage initialized at: {self._storage_root}")

# Global storage configuration instance
storage_config = StorageConfig()