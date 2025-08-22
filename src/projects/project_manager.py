"""
Project Management Core for LabAcc Copilot Multi-User System

Handles project creation, sharing, permissions, and CRUD operations.
All project permissions are enforced at the system level, never by the LLM.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Project:
    """Represents a lab project with metadata and permissions"""
    
    def __init__(self, project_id: str, name: str, owner_id: str, 
                 description: str = "", created_at: str = None):
        self.project_id = project_id
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.created_at = created_at or datetime.now().isoformat()
        self.shared_with: Set[str] = set()  # Set of user_ids with shared access
        self.admins: Set[str] = set()       # Set of user_ids with admin access
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "owner_id": self.owner_id,
            "description": self.description,
            "created_at": self.created_at,
            "shared_with": list(self.shared_with),
            "admins": list(self.admins)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        """Create Project from dictionary"""
        project = cls(
            project_id=data["project_id"],
            name=data["name"],
            owner_id=data["owner_id"],
            description=data.get("description", ""),
            created_at=data.get("created_at")
        )
        project.shared_with = set(data.get("shared_with", []))
        project.admins = set(data.get("admins", []))
        return project

class ProjectManager:
    """Core project management system"""
    
    def __init__(self, storage_root: str = "data/"):
        # Future: This will be configurable from a config file
        # For now, projects are stored in data/ folder
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Project metadata file
        self.metadata_file = self.storage_root / "projects_metadata.json"
        self.projects: Dict[str, Project] = {}
        self._load_projects()
    
    def _load_projects(self):
        """Load project metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    for project_data in data.get("projects", []):
                        project = Project.from_dict(project_data)
                        self.projects[project.project_id] = project
                logger.info(f"Loaded {len(self.projects)} projects")
            except Exception as e:
                logger.error(f"Failed to load projects metadata: {e}")
                self.projects = {}
        else:
            # Initialize with example projects if no metadata exists
            self._create_initial_projects()
    
    def _save_projects(self):
        """Save project metadata to file"""
        try:
            data = {
                "projects": [project.to_dict() for project in self.projects.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.projects)} projects to metadata")
        except Exception as e:
            logger.error(f"Failed to save projects metadata: {e}")
    
    def _create_initial_projects(self):
        """Create initial example projects"""
        logger.info("Creating initial example projects")
        
        # Alice's PCR project
        self.projects["project_001_alice_pcr"] = Project(
            project_id="project_001_alice_pcr",
            name="Alice PCR Optimization",
            owner_id="alice",
            description="PCR protocol optimization experiments"
        )
        
        # Bob's cancer research project  
        self.projects["project_002_bob_cancer"] = Project(
            project_id="project_002_bob_cancer", 
            name="Bob Cancer Research",
            owner_id="bob",
            description="Cancer cell line studies"
        )
        
        # Shared protocols project
        shared_project = Project(
            project_id="project_003_shared_protocols",
            name="Shared Lab Protocols", 
            owner_id="admin",
            description="Lab-wide protocols and procedures"
        )
        shared_project.shared_with.add("alice")
        shared_project.shared_with.add("bob")
        self.projects["project_003_shared_protocols"] = shared_project
        
        self._save_projects()
    
    def create_project(self, user_id: str, project_name: str, description: str = "") -> str:
        """Create a new project for a user
        
        Args:
            user_id: Owner of the project
            project_name: Human-readable project name
            description: Optional project description
            
        Returns:
            project_id: Unique project identifier
        """
        # Generate unique project ID
        project_id = f"project_{uuid.uuid4().hex[:8]}_{project_name.lower().replace(' ', '_')}"
        
        # Create project directory
        project_path = self.storage_root / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create README
        readme_content = f"""# {project_name}

**Owner**: {user_id}  
**Created**: {datetime.now().strftime('%Y-%m-%d')}  
**Description**: {description}

## Project Overview

This project was created using LabAcc Copilot's multi-user workspace system.

## Experiments

No experiments yet. Create your first experiment folder to get started.

## Notes

Add your project notes and observations here.
"""
        
        readme_path = project_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        # Create project metadata
        project = Project(
            project_id=project_id,
            name=project_name,
            owner_id=user_id,
            description=description
        )
        
        self.projects[project_id] = project
        self._save_projects()
        
        logger.info(f"Created project {project_id} for user {user_id}")
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    def get_project_path(self, project_id: str) -> Optional[Path]:
        """Get filesystem path for project"""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id]
        # Projects are stored in user-specific directories
        user_projects_dir = self.storage_root / f"{project.owner_id}_projects"
        return user_projects_dir / project_id
    
    def get_user_projects(self, user_id: str) -> List[Project]:
        """Get all projects accessible to a user"""
        accessible_projects = []
        
        for project in self.projects.values():
            if self._can_access_project(user_id, project.project_id):
                accessible_projects.append(project)
        
        return accessible_projects
    
    def _can_access_project(self, user_id: str, project_id: str) -> bool:
        """Check if user can access project (system-level permission check)"""
        project = self.projects.get(project_id)
        if not project:
            return False
        
        # Owner has full access
        if project.owner_id == user_id:
            return True
        
        # Admin users have access to all projects
        if user_id in project.admins or user_id == "admin":
            return True
        
        # Shared users have access
        if user_id in project.shared_with:
            return True
        
        return False
    
    def get_user_permission(self, user_id: str, project_id: str) -> str:
        """Get user's permission level for project"""
        project = self.projects.get(project_id)
        if not project:
            return "none"
        
        if project.owner_id == user_id:
            return "owner"
        elif user_id in project.admins or user_id == "admin":
            return "admin"  
        elif user_id in project.shared_with:
            return "shared"
        else:
            return "none"
    
    def share_project(self, project_id: str, owner_id: str, shared_with_user: str):
        """Share project with another user
        
        Args:
            project_id: Project to share
            owner_id: Must be project owner
            shared_with_user: User to grant access to
            
        Raises:
            PermissionError: If user is not owner
            ValueError: If project not found
        """
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        if project.owner_id != owner_id:
            raise PermissionError("Only project owners can share projects")
        
        project.shared_with.add(shared_with_user)
        self._save_projects()
        
        logger.info(f"Project {project_id} shared with {shared_with_user} by {owner_id}")
    
    def unshare_project(self, project_id: str, owner_id: str, unshare_user: str):
        """Remove user's access to project"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        if project.owner_id != owner_id:
            raise PermissionError("Only project owners can unshare projects")
        
        project.shared_with.discard(unshare_user)
        self._save_projects()
        
        logger.info(f"Removed {unshare_user} access to project {project_id}")
    
    def delete_project(self, project_id: str, user_id: str):
        """Delete a project (owner only)"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        if project.owner_id != user_id and user_id != "admin":
            raise PermissionError("Only project owners or admins can delete projects")
        
        # Remove project directory
        project_path = self.get_project_path(project_id)
        if project_path and project_path.exists():
            import shutil
            shutil.rmtree(project_path)
        
        # Remove from metadata
        del self.projects[project_id]
        self._save_projects()
        
        logger.info(f"Deleted project {project_id} by {user_id}")
    
    def list_all_projects(self) -> List[Project]:
        """List all projects (admin function)"""
        return list(self.projects.values())

# Global project manager instance
project_manager = ProjectManager()