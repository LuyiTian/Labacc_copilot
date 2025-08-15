"""
Temporary Simple Project Manager for Development
This bridges the old data/ structure with the new session system for testing
"""

from pathlib import Path
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class TempProjectManager:
    """Temporary project manager that maps existing data folders to projects"""
    
    def __init__(self, data_root: str):
        self.data_root = Path(data_root)
        
        # Simple project mapping based on existing folders
        self.projects = {}
        self._scan_existing_projects()
    
    def _scan_existing_projects(self):
        """Scan existing data folders and create project mappings"""
        if not self.data_root.exists():
            logger.warning(f"Data root not found: {self.data_root}")
            return
        
        # Map existing subfolders as projects
        for item in self.data_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                project_id = f"project_{item.name}"
                self.projects[project_id] = {
                    "name": item.name.replace('_', ' ').title(),
                    "path": item,
                    "owner": "temp_user",
                    "created": item.stat().st_mtime
                }
                logger.info(f"Mapped existing folder {item.name} to project {project_id}")
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects accessible to user (for now, all projects)"""
        return [
            {
                "project_id": pid,
                "name": info["name"],
                "permission": "owner"  # Temp: everyone is owner
            }
            for pid, info in self.projects.items()
        ]
    
    def get_project_path(self, project_id: str) -> Optional[Path]:
        """Get absolute path to project directory"""
        project_info = self.projects.get(project_id)
        if not project_info:
            return None
        return project_info["path"]
    
    def get_user_permission(self, user_id: str, project_id: str) -> str:
        """Get user permission level for project"""
        if project_id in self.projects:
            return "owner"  # Temp: everyone is owner
        return "none"
    
    def _can_access_project(self, user_id: str, project_id: str) -> bool:
        """Check if user can access project"""
        return project_id in self.projects  # Temp: everyone can access all projects
    
    def create_demo_project(self) -> str:
        """Create a demo project for testing"""
        demo_path = self.data_root / "demo_project"
        demo_path.mkdir(exist_ok=True)
        
        # Create some demo content
        (demo_path / "experiments").mkdir(exist_ok=True)
        (demo_path / "README.md").write_text("# Demo Project\n\nThis is a demo project for testing the new system.")
        
        project_id = "project_demo_project"
        self.projects[project_id] = {
            "name": "Demo Project",
            "path": demo_path,
            "owner": "temp_user",
            "created": demo_path.stat().st_mtime
        }
        
        logger.info(f"Created demo project: {project_id}")
        return project_id

# Global instance
temp_project_manager = None

def get_temp_project_manager():
    """Get or create the temporary project manager"""
    global temp_project_manager
    if not temp_project_manager:
        import os
        data_root = os.environ.get("LABACC_PROJECT_ROOT", "data")
        temp_project_manager = TempProjectManager(data_root)
    return temp_project_manager