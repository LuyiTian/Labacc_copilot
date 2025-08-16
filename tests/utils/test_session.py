"""
Test session utilities for setting up and tearing down test environments.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import json
from datetime import datetime


class TestSession:
    """Manages test session setup and cleanup."""
    
    def __init__(self, use_temp_dir: bool = True):
        """
        Initialize test session.
        
        Args:
            use_temp_dir: If True, create a temporary directory for testing.
                         If False, use bob_projects (must restore from backup after).
        """
        self.use_temp_dir = use_temp_dir
        self.temp_dir = None
        self.project_root = None
        self.experiment_id = "test_experiment"
        self.session_id = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    def setup(self) -> Tuple[Path, str, str]:
        """
        Set up test environment.
        
        Returns:
            Tuple of (project_root, experiment_id, session_id)
        """
        if self.use_temp_dir:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="labacc_test_")
            self.project_root = Path(self.temp_dir)
        else:
            # Use bob_projects (ensure backup exists first)
            self.project_root = Path("data/bob_projects")
            if not self.project_root.exists():
                raise RuntimeError("bob_projects not found - restore from backup first")
        
        # Create experiment directory
        exp_path = self.project_root / self.experiment_id
        exp_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (exp_path / "originals").mkdir(exist_ok=True)
        (exp_path / ".labacc").mkdir(exist_ok=True)
        
        # Create initial README
        readme_path = exp_path / "README.md"
        readme_content = f"""# {self.experiment_id}

## Overview
Test experiment for automated testing.

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Active

## Purpose
This is a test experiment used for validating the file upload and analysis cycle.

## Files
- No files uploaded yet

## Notes
This experiment will be cleaned up after testing.
"""
        readme_path.write_text(readme_content)
        
        # Create file registry
        registry_path = exp_path / ".labacc" / "file_registry.json"
        registry = {
            "version": "3.0",
            "experiment_id": self.experiment_id,
            "files": {},
            "last_updated": datetime.now().isoformat()
        }
        registry_path.write_text(json.dumps(registry, indent=2))
        
        return self.project_root, self.experiment_id, self.session_id
    
    def add_test_file(self, filename: str, content: str) -> Path:
        """
        Add a test file to the experiment.
        
        Args:
            filename: Name of the file
            content: File content
            
        Returns:
            Path to the created file
        """
        file_path = self.project_root / self.experiment_id / "originals" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    def get_readme_content(self) -> str:
        """Get the current README content."""
        readme_path = self.project_root / self.experiment_id / "README.md"
        if readme_path.exists():
            return readme_path.read_text()
        return ""
    
    def get_registry(self) -> dict:
        """Get the current file registry."""
        registry_path = self.project_root / self.experiment_id / ".labacc" / "file_registry.json"
        if registry_path.exists():
            return json.loads(registry_path.read_text())
        return {}
    
    def cleanup(self):
        """Clean up test environment."""
        if self.use_temp_dir and self.temp_dir:
            # Remove temporary directory
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        elif not self.use_temp_dir:
            # Clean up test experiment from bob_projects
            exp_path = self.project_root / self.experiment_id
            if exp_path.exists():
                shutil.rmtree(exp_path, ignore_errors=True)
    
    def __enter__(self):
        """Context manager entry."""
        return self.setup()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class MockSessionManager:
    """Mock session manager for testing."""
    
    def __init__(self, project_root: Path):
        self.sessions = {}
        self.project_root = project_root
    
    def create_session(self, session_id: str, user_id: str):
        """Create a mock session."""
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "project_path": str(self.project_root),
            "selected_project": "test_project",
            "pending_questions": {}
        }
        return True
    
    def get_session(self, session_id: str):
        """Get a mock session."""
        if session_id in self.sessions:
            # Return an object-like dict
            class SessionObj:
                def __init__(self, data):
                    self.__dict__.update(data)
                
                def resolve_path(self, path):
                    return Path(self.project_path) / path
            
            return SessionObj(self.sessions[session_id])
        return None
    
    def select_project(self, session_id: str, project_id: str):
        """Select a project for the session."""
        if session_id in self.sessions:
            self.sessions[session_id]["selected_project"] = project_id
            return self.get_session(session_id)
        return None


def create_test_environment() -> Tuple[TestSession, Path, str, str]:
    """
    Quick helper to create a complete test environment.
    
    Returns:
        Tuple of (test_session, project_root, experiment_id, session_id)
    """
    test_session = TestSession(use_temp_dir=True)
    project_root, experiment_id, session_id = test_session.setup()
    return test_session, project_root, experiment_id, session_id