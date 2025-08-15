"""File registry system for tracking original and converted files.

This module manages the file registry that tracks all uploaded files,
their conversion status, and metadata.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FileRegistry:
    """Manages file registry for experiments."""
    
    def __init__(self, project_root: str):
        """Initialize file registry.
        
        Args:
            project_root: Root directory for all projects
        """
        self.project_root = Path(project_root)
    
    def get_registry_path(self, experiment_id: str) -> Path:
        """Get path to registry file for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Path to registry JSON file
        """
        return self.project_root / experiment_id / ".labacc" / "file_registry.json"
    
    def load_registry(self, experiment_id: str) -> Dict:
        """Load registry for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Registry dictionary
        """
        registry_path = self.get_registry_path(experiment_id)
        
        if registry_path.exists():
            with open(registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Return default registry structure
        return {
            "version": "3.0",
            "experiment_id": experiment_id,
            "files": {},
            "last_updated": None,
            "total_files": 0
        }
    
    def save_registry(self, experiment_id: str, registry: Dict):
        """Save registry for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            registry: Registry dictionary to save
        """
        registry_path = self.get_registry_path(experiment_id)
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update metadata
        registry["last_updated"] = datetime.now().isoformat()
        registry["total_files"] = len(registry.get("files", {}))
        
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved registry for {experiment_id} with {registry['total_files']} files")
    
    def add_file(
        self,
        experiment_id: str,
        filename: str,
        original_path: str,
        converted_path: Optional[str] = None,
        file_size: Optional[int] = None,
        conversion_status: str = "not_needed",
        conversion_method: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Add or update a file in the registry.
        
        Args:
            experiment_id: ID of the experiment
            filename: Name of the file
            original_path: Path to original file
            converted_path: Path to converted file (if any)
            file_size: Size of the file in bytes
            conversion_status: Status of conversion
            conversion_method: Method used for conversion
            metadata: Additional metadata
            
        Returns:
            Updated file entry
        """
        registry = self.load_registry(experiment_id)
        
        # Create file entry
        file_entry = {
            "original_path": original_path,
            "converted_path": converted_path,
            "upload_time": datetime.now().isoformat(),
            "file_size": file_size,
            "conversion": {
                "status": conversion_status,
                "method": conversion_method,
                "timestamp": datetime.now().isoformat() if conversion_status == "success" else None
            },
            "analysis": {
                "analyzed": False,
                "summary": None,
                "context": None
            }
        }
        
        # Add custom metadata if provided
        if metadata:
            file_entry["metadata"] = metadata
        
        # Update registry
        registry["files"][filename] = file_entry
        self.save_registry(experiment_id, registry)
        
        return file_entry
    
    def get_file(self, experiment_id: str, filename: str) -> Optional[Dict]:
        """Get file information from registry.
        
        Args:
            experiment_id: ID of the experiment
            filename: Name of the file
            
        Returns:
            File entry or None if not found
        """
        registry = self.load_registry(experiment_id)
        return registry.get("files", {}).get(filename)
    
    def get_file_by_path(self, experiment_id: str, file_path: str) -> Optional[Dict]:
        """Get file information by matching original or converted path.
        
        Args:
            experiment_id: ID of the experiment
            file_path: Path to match (original or converted)
            
        Returns:
            File entry with filename, or None if not found
        """
        registry = self.load_registry(experiment_id)
        
        for filename, file_info in registry.get("files", {}).items():
            if (file_info.get("original_path") == file_path or 
                file_info.get("converted_path") == file_path):
                return {"filename": filename, **file_info}
        
        return None
    
    def update_analysis(
        self,
        experiment_id: str,
        filename: str,
        summary: str,
        context: Optional[str] = None
    ):
        """Update analysis information for a file.
        
        Args:
            experiment_id: ID of the experiment
            filename: Name of the file
            summary: Analysis summary
            context: Additional context
        """
        registry = self.load_registry(experiment_id)
        
        if filename in registry.get("files", {}):
            registry["files"][filename]["analysis"] = {
                "analyzed": True,
                "summary": summary,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            self.save_registry(experiment_id, registry)
            logger.info(f"Updated analysis for {experiment_id}/{filename}")
        else:
            logger.warning(f"File {filename} not found in registry for {experiment_id}")
    
    def list_files(
        self,
        experiment_id: str,
        only_converted: bool = False,
        only_analyzed: bool = False
    ) -> List[Dict]:
        """List all files in the registry.
        
        Args:
            experiment_id: ID of the experiment
            only_converted: Only return files that have been converted
            only_analyzed: Only return files that have been analyzed
            
        Returns:
            List of file entries with filenames
        """
        registry = self.load_registry(experiment_id)
        files = []
        
        for filename, file_info in registry.get("files", {}).items():
            # Apply filters
            if only_converted and not file_info.get("converted_path"):
                continue
            if only_analyzed and not file_info.get("analysis", {}).get("analyzed"):
                continue
            
            files.append({"filename": filename, **file_info})
        
        return files
    
    def get_readable_path(self, experiment_id: str, file_path: str) -> str:
        """Get the best readable version of a file (converted if available).
        
        Args:
            experiment_id: ID of the experiment
            file_path: Original file path
            
        Returns:
            Path to the best readable version (converted or original)
        """
        # Try to find file in registry
        file_info = self.get_file_by_path(experiment_id, file_path)
        
        if file_info:
            # Return converted path if available and successful
            if (file_info.get("converted_path") and 
                file_info.get("conversion", {}).get("status") == "success"):
                return file_info["converted_path"]
        
        # Return original path as fallback
        return file_path
    
    def cleanup_orphaned_conversions(self, experiment_id: str):
        """Remove converted files that no longer have originals.
        
        Args:
            experiment_id: ID of the experiment
        """
        registry = self.load_registry(experiment_id)
        exp_dir = self.project_root / experiment_id
        updated = False
        
        for filename in list(registry.get("files", {}).keys()):
            file_info = registry["files"][filename]
            original_path = exp_dir / file_info.get("original_path", "")
            
            # If original doesn't exist, remove from registry
            if not original_path.exists():
                # Also remove converted file if it exists
                if file_info.get("converted_path"):
                    converted_path = exp_dir / file_info["converted_path"]
                    if converted_path.exists():
                        converted_path.unlink()
                        logger.info(f"Removed orphaned conversion: {converted_path}")
                
                del registry["files"][filename]
                updated = True
                logger.info(f"Removed orphaned entry from registry: {filename}")
        
        if updated:
            self.save_registry(experiment_id, registry)


# Global registry instance (singleton pattern)
_global_registry = None


def get_file_registry(project_root: str = "data/alice_projects") -> FileRegistry:
    """Get global file registry instance.
    
    Args:
        project_root: Root directory for projects
        
    Returns:
        FileRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = FileRegistry(project_root)
    return _global_registry


# Convenience functions for easy access
def load_file_registry(experiment_id: str, project_root: str = "data/alice_projects") -> Dict:
    """Load registry for an experiment.
    
    Args:
        experiment_id: ID of the experiment
        project_root: Root directory for projects
        
    Returns:
        Registry dictionary
    """
    registry = get_file_registry(project_root)
    return registry.load_registry(experiment_id)


def update_file_registry(
    experiment_id: str,
    filename: str,
    original_path: str,
    converted_path: Optional[str] = None,
    **kwargs
) -> Dict:
    """Add or update a file in the registry.
    
    Args:
        experiment_id: ID of the experiment
        filename: Name of the file
        original_path: Path to original file
        converted_path: Path to converted file
        **kwargs: Additional arguments for registry
        
    Returns:
        Updated file entry
    """
    registry = get_file_registry()
    return registry.add_file(
        experiment_id,
        filename,
        original_path,
        converted_path,
        **kwargs
    )


def get_file_info(experiment_id: str, filename: str) -> Optional[Dict]:
    """Get file information from registry.
    
    Args:
        experiment_id: ID of the experiment
        filename: Name of the file
        
    Returns:
        File information or None
    """
    registry = get_file_registry()
    return registry.get_file(experiment_id, filename)


def get_readable_file_path(experiment_id: str, file_path: str) -> str:
    """Get the best readable version of a file.
    
    Args:
        experiment_id: ID of the experiment
        file_path: File path
        
    Returns:
        Best readable path (converted or original)
    """
    registry = get_file_registry()
    return registry.get_readable_path(experiment_id, file_path)