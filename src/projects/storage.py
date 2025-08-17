"""
Storage Management for LabAcc Copilot Multi-User System

Handles external storage path management and file operations within projects.
Provides utilities for safe path operations and storage initialization.
"""

import os
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages external storage for LabAcc Copilot projects"""
    
    def __init__(self, storage_root: str = "data/"):
        # Future: This will be configurable from a config file
        self.storage_root = Path(storage_root).resolve()
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage directory structure exists"""
        self.storage_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage root: {self.storage_root}")
    
    def get_project_path(self, project_id: str) -> Path:
        """Get absolute path to project directory"""
        return self.storage_root / project_id
    
    def ensure_project_directory(self, project_id: str) -> Path:
        """Ensure project directory exists and return path"""
        project_path = self.get_project_path(project_id)
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path
    
    def is_valid_project_path(self, project_id: str, relative_path: str) -> bool:
        """Check if a relative path is valid within a project
        
        This prevents directory traversal attacks and ensures paths stay within project bounds.
        """
        try:
            project_path = self.get_project_path(project_id)
            full_path = (project_path / relative_path).resolve()
            
            # Ensure the resolved path is still within the project directory
            return full_path.is_relative_to(project_path)
        except (ValueError, OSError):
            return False
    
    def resolve_project_path(self, project_id: str, relative_path: str) -> Optional[Path]:
        """Safely resolve a relative path within a project
        
        Args:
            project_id: Project identifier
            relative_path: Path relative to project root
            
        Returns:
            Absolute path if valid, None if invalid/unsafe
        """
        if not self.is_valid_project_path(project_id, relative_path):
            logger.warning(f"Invalid path attempted: {project_id}/{relative_path}")
            return None
        
        project_path = self.get_project_path(project_id)
        return (project_path / relative_path).resolve()
    
    def list_project_contents(self, project_id: str, relative_path: str = ".") -> Optional[List[str]]:
        """List contents of a directory within a project
        
        Returns:
            List of filenames/directory names, or None if path is invalid
        """
        full_path = self.resolve_project_path(project_id, relative_path)
        if not full_path or not full_path.exists() or not full_path.is_dir():
            return None
        
        try:
            return [item.name for item in full_path.iterdir()]
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to list directory {full_path}: {e}")
            return None
    
    def read_project_file(self, project_id: str, relative_path: str) -> Optional[str]:
        """Read contents of a file within a project
        
        Returns:
            File contents as string, or None if file doesn't exist/invalid
        """
        full_path = self.resolve_project_path(project_id, relative_path)
        if not full_path or not full_path.exists() or not full_path.is_file():
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read file {full_path}: {e}")
            return None
    
    def write_project_file(self, project_id: str, relative_path: str, content: str) -> bool:
        """Write content to a file within a project
        
        Args:
            project_id: Project identifier
            relative_path: Path relative to project root
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        full_path = self.resolve_project_path(project_id, relative_path)
        if not full_path:
            return False
        
        try:
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.debug(f"Wrote file: {full_path}")
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to write file {full_path}: {e}")
            return False
    
    def delete_project_item(self, project_id: str, relative_path: str) -> bool:
        """Delete a file or directory within a project
        
        Args:
            project_id: Project identifier  
            relative_path: Path relative to project root
            
        Returns:
            True if successful, False otherwise
        """
        full_path = self.resolve_project_path(project_id, relative_path)
        if not full_path or not full_path.exists():
            return False
        
        try:
            if full_path.is_file():
                full_path.unlink()
            elif full_path.is_dir():
                import shutil
                shutil.rmtree(full_path)
            
            logger.debug(f"Deleted: {full_path}")
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to delete {full_path}: {e}")
            return False
    
    def get_file_info(self, project_id: str, relative_path: str) -> Optional[dict]:
        """Get metadata about a file or directory
        
        Returns:
            Dictionary with file info, or None if path doesn't exist
        """
        full_path = self.resolve_project_path(project_id, relative_path)
        if not full_path or not full_path.exists():
            return None
        
        try:
            stat = full_path.stat()
            return {
                "name": full_path.name,
                "path": relative_path,
                "is_file": full_path.is_file(),
                "is_directory": full_path.is_dir(),
                "size_bytes": stat.st_size if full_path.is_file() else 0,
                "modified_time": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:]
            }
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to get file info for {full_path}: {e}")
            return None
    
    def create_directory(self, project_id: str, relative_path: str) -> bool:
        """Create a directory within a project
        
        Args:
            project_id: Project identifier
            relative_path: Directory path relative to project root
            
        Returns:
            True if successful, False otherwise
        """
        full_path = self.resolve_project_path(project_id, relative_path)
        if not full_path:
            return False
        
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {full_path}")
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create directory {full_path}: {e}")
            return False
    
    def get_storage_stats(self) -> dict:
        """Get storage usage statistics"""
        try:
            total_size = 0
            total_files = 0
            total_dirs = 0
            
            for project_dir in self.storage_root.iterdir():
                if project_dir.is_dir():
                    for item in project_dir.rglob("*"):
                        if item.is_file():
                            total_files += 1
                            total_size += item.stat().st_size
                        elif item.is_dir():
                            total_dirs += 1
            
            return {
                "storage_root": str(self.storage_root),
                "total_size_bytes": total_size,
                "total_files": total_files,
                "total_directories": total_dirs,
                "projects_count": len([d for d in self.storage_root.iterdir() if d.is_dir()])
            }
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}

# Global storage manager instance
storage_manager = StorageManager()