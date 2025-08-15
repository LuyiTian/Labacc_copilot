"""
Multi-User Test Utilities for LabAcc Copilot

Provides utilities for testing the new multi-user, project-based architecture.
Handles session management, project selection, and backward compatibility.
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import logging

from src.projects.session import session_manager, set_current_session, get_current_session
from src.projects.temp_manager import get_temp_project_manager

logger = logging.getLogger(__name__)

@dataclass
class TestSession:
    """Represents a test session with project context"""
    session_id: str
    user_id: str
    selected_project: Optional[str] = None
    project_path: Optional[Path] = None
    permission: str = "owner"
    
@dataclass
class ProjectMapping:
    """Maps old test folder structure to new project structure"""
    old_folder: str
    project_id: str
    relative_path: str
    
class MultiUserTestManager:
    """Manages multi-user test sessions and project mappings"""
    
    def __init__(self):
        self.temp_manager = get_temp_project_manager()
        self.active_sessions: Dict[str, TestSession] = {}
        self._setup_project_mappings()
    
    def _setup_project_mappings(self):
        """Create mappings from old test folder structure to new projects"""
        self.project_mappings = {
            # Alice's experiments (typically in alice_projects folder)
            "exp_001_protocol_test": ProjectMapping("exp_001_protocol_test", "project_alice_projects", "exp_001_protocol_test"),
            "exp_002_optimization": ProjectMapping("exp_002_optimization", "project_alice_projects", "exp_002_optimization"), 
            "exp_003_exp_002_optimized_dissociation": ProjectMapping("exp_003_exp_002_optimized_dissociation", "project_alice_projects", "exp_003_exp_002_optimized_dissociation"),
            
            # Bob's experiments (typically in bob_projects folder)  
            "exp_001_lung_cancer_scrna": ProjectMapping("exp_001_lung_cancer_scrna", "project_bob_projects", "exp_001_lung_cancer_scrna"),
            "exp_002_optimization": ProjectMapping("exp_002_optimization", "project_bob_projects", "exp_002_optimization"),
            
            # General experiments folder
            "exp_unknown": ProjectMapping("exp_unknown", "project_experiments", "exp_unknown"),
            
            # Top-level data folders map to projects
            "alice_projects": ProjectMapping("alice_projects", "project_alice_projects", "."),
            "bob_projects": ProjectMapping("bob_projects", "project_bob_projects", "."),
            "experiments": ProjectMapping("experiments", "project_experiments", "."),
        }
    
    async def create_test_session(self, 
                                 session_id: Optional[str] = None,
                                 user_id: str = "temp_user",
                                 auto_select_project: Optional[str] = None) -> TestSession:
        """Create a test session with optional project selection
        
        Args:
            session_id: Custom session ID or auto-generate
            user_id: User ID for the session
            auto_select_project: Project ID to auto-select
            
        Returns:
            TestSession object with session details
        """
        if not session_id:
            session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        
        # Create session in session manager
        success = session_manager.create_session(session_id, user_id)
        if not success:
            raise RuntimeError(f"Failed to create session {session_id}")
        
        test_session = TestSession(session_id=session_id, user_id=user_id)
        
        # Auto-select project if requested
        if auto_select_project:
            await self.select_project_for_session(test_session, auto_select_project)
        
        self.active_sessions[session_id] = test_session
        logger.info(f"Created test session {session_id} for user {user_id}")
        
        return test_session
    
    async def select_project_for_session(self, test_session: TestSession, project_id: str):
        """Select a project for a test session
        
        Args:
            test_session: TestSession to update
            project_id: Project ID to select
        """
        # Select project in session manager
        project_session = session_manager.select_project(test_session.session_id, project_id)
        
        if not project_session:
            available_projects = self.temp_manager.get_user_projects(test_session.user_id)
            project_list = [p["project_id"] for p in available_projects]
            raise RuntimeError(f"Failed to select project {project_id}. Available: {project_list}")
        
        # Update test session
        test_session.selected_project = project_id
        test_session.project_path = project_session.project_path
        test_session.permission = project_session.permission
        
        logger.info(f"Selected project {project_id} for session {test_session.session_id}")
    
    def map_old_folder_to_project(self, old_folder: str) -> Optional[ProjectMapping]:
        """Map old test folder reference to new project structure
        
        Args:
            old_folder: Old folder reference from test case
            
        Returns:
            ProjectMapping if found, None otherwise
        """
        return self.project_mappings.get(old_folder)
    
    async def setup_test_context_from_old_format(self,
                                                session_id: str,
                                                current_folder: Optional[str],
                                                selected_files: Optional[List[str]] = None) -> Optional[TestSession]:
        """Setup test context from old test case format
        
        This provides backward compatibility for existing test cases.
        
        Args:
            session_id: Session ID to use
            current_folder: Old-format folder reference
            selected_files: Selected files (for context)
            
        Returns:
            TestSession if successfully set up, None otherwise
        """
        if not current_folder:
            # No specific folder - create session without project selection
            return await self.create_test_session(session_id=session_id)
        
        # Try to map old folder to new project structure
        mapping = self.map_old_folder_to_project(current_folder)
        if not mapping:
            logger.warning(f"Could not map old folder '{current_folder}' to project")
            # Create session without project for now
            return await self.create_test_session(session_id=session_id)
        
        # Create session and select mapped project
        test_session = await self.create_test_session(
            session_id=session_id,
            auto_select_project=mapping.project_id
        )
        
        logger.info(f"Mapped old folder '{current_folder}' to project '{mapping.project_id}' with path '{mapping.relative_path}'")
        
        return test_session
    
    def set_current_test_session(self, session_id: str):
        """Set the current session context for the calling thread
        
        Args:
            session_id: Session ID to set as current
        """
        set_current_session(session_id)
        logger.debug(f"Set current session to {session_id}")
    
    def get_available_projects(self, user_id: str = "temp_user") -> List[Dict[str, str]]:
        """Get list of available projects for a user
        
        Args:
            user_id: User ID to get projects for
            
        Returns:
            List of project info dictionaries
        """
        return self.temp_manager.get_user_projects(user_id)
    
    def cleanup_session(self, session_id: str):
        """Clean up a test session
        
        Args:
            session_id: Session to clean up
        """
        # End session in session manager
        session_manager.end_session(session_id)
        
        # Remove from our tracking
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        logger.debug(f"Cleaned up test session {session_id}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a test session
        
        Args:
            session_id: Session ID to query
            
        Returns:
            Session info dictionary or None
        """
        if session_id in self.active_sessions:
            test_session = self.active_sessions[session_id]
            return {
                "session_id": test_session.session_id,
                "user_id": test_session.user_id,
                "selected_project": test_session.selected_project,
                "project_path": str(test_session.project_path) if test_session.project_path else None,
                "permission": test_session.permission
            }
        return None

# Global instance for tests
test_manager = MultiUserTestManager()

# Convenience functions for tests
async def create_test_session(session_id: Optional[str] = None,
                             user_id: str = "temp_user",
                             project_id: Optional[str] = None) -> TestSession:
    """Create a test session with optional project selection"""
    return await test_manager.create_test_session(session_id, user_id, project_id)

async def setup_legacy_test_context(session_id: str,
                                   current_folder: Optional[str],
                                   selected_files: Optional[List[str]] = None) -> Optional[TestSession]:
    """Setup test context from legacy test case format"""
    return await test_manager.setup_test_context_from_old_format(session_id, current_folder, selected_files)

def set_test_session(session_id: str):
    """Set current session for tests"""
    test_manager.set_current_test_session(session_id)

def cleanup_test_session(session_id: str):
    """Clean up test session"""
    test_manager.cleanup_session(session_id)

def get_test_projects(user_id: str = "temp_user") -> List[Dict[str, str]]:
    """Get available test projects"""
    return test_manager.get_available_projects(user_id)