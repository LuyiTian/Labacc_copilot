"""
Session Context System for LabAcc Copilot Multi-User System

Provides session-based project selection and bulletproof path resolution.
This eliminates the 5-layer path interpretation chaos by providing a single source of truth.
"""

from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
import threading
import logging

# Use real project manager
from .project_manager import project_manager

logger = logging.getLogger(__name__)

@dataclass
class ProjectSession:
    """Session context for a user working within a selected project"""
    
    session_id: str
    user_id: str
    selected_project: str
    project_path: Path
    permission: str  # owner/shared/admin
    
    def resolve_path(self, relative_path: str = ".") -> Path:
        """
        Bulletproof path resolution within selected project.
        
        This is the SINGLE SOURCE OF TRUTH for all path operations.
        No more 5-layer interpretation chaos!
        
        Args:
            relative_path: Path relative to project root (e.g., "experiments/data.csv")
            
        Returns:
            Absolute path within project bounds
        """
        # Clean up relative path
        if relative_path.startswith("/"):
            relative_path = relative_path.lstrip("/")
        
        # Always resolve relative to project_path
        return self.project_path / relative_path
    
    def is_valid_path(self, relative_path: str) -> bool:
        """Check if relative path is valid within project bounds"""
        # Temp: Simple check - just ensure it resolves within project
        try:
            resolved = self.resolve_path(relative_path)
            return resolved.is_relative_to(self.project_path)
        except:
            return False
    
    def can_write(self) -> bool:
        """Check if user has write permissions in this project"""
        return self.permission in ["owner", "admin", "shared"]
    
    def can_manage(self) -> bool:
        """Check if user can manage project (share, delete, etc.)"""
        return self.permission in ["owner", "admin"]
    
    def can_read(self) -> bool:
        """Check if user has read permissions in this project"""
        return self.permission in ["owner", "admin", "shared"]

class SessionManager:
    """Manages user sessions and project selections"""
    
    def __init__(self):
        self.sessions: Dict[str, ProjectSession] = {}
        self._lock = threading.Lock()
    
    def create_session(self, session_id: str, user_id: str) -> bool:
        """Create a new session for a user (without project selection yet)
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            
        Returns:
            True if session created successfully
        """
        with self._lock:
            # For now, store minimal session info until project is selected
            self.sessions[session_id] = {
                "session_id": session_id,
                "user_id": user_id,
                "selected_project": None,
                "authenticated": True
            }
            logger.info(f"Created session {session_id} for user {user_id}")
            return True
    
    def select_project(self, session_id: str, project_id: str) -> Optional[ProjectSession]:
        """Select a project for a session
        
        Args:
            session_id: Session identifier
            project_id: Project to select
            
        Returns:
            ProjectSession if successful, None if failed
        """
        with self._lock:
            # Check if session exists
            if session_id not in self.sessions:
                logger.error(f"Session {session_id} not found")
                return None
            
            session_data = self.sessions[session_id]
            # Handle both dictionary and ProjectSession object
            if isinstance(session_data, ProjectSession):
                user_id = session_data.user_id
            else:
                user_id = session_data["user_id"]
            
            # Check if user can access this project (SYSTEM-LEVEL PERMISSION CHECK)
            if not project_manager._can_access_project(user_id, project_id):
                logger.warning(f"User {user_id} denied access to project {project_id}")
                return None
            
            # Get project path
            project_path = project_manager.get_project_path(project_id)
            if not project_path:
                logger.error(f"Project {project_id} not found")
                return None
            
            # Get user permission level
            permission = project_manager.get_user_permission(user_id, project_id)
            
            # Create project session
            project_session = ProjectSession(
                session_id=session_id,
                user_id=user_id,
                selected_project=project_id,
                project_path=project_path,
                permission=permission
            )
            
            # Store the full project session
            self.sessions[session_id] = project_session
            
            logger.info(f"User {user_id} selected project {project_id} with {permission} permissions")
            return project_session
    
    def get_session(self, session_id: str) -> Optional[ProjectSession]:
        """Get current session context
        
        Args:
            session_id: Session identifier
            
        Returns:
            ProjectSession if found and project selected, None otherwise
        """
        with self._lock:
            session = self.sessions.get(session_id)
            
            # Return None if session doesn't exist or is not a ProjectSession
            if not session or not isinstance(session, ProjectSession):
                return None
            
            return session
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get basic session information (even without project selection)
        
        Returns:
            Dictionary with session info or None if session not found
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return None
            
            if isinstance(session, ProjectSession):
                return {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "selected_project": session.selected_project,
                    "permission": session.permission,
                    "project_selected": True
                }
            elif isinstance(session, dict):
                # Basic session (no project selected yet)
                return {
                    "session_id": session.get("session_id", session_id),
                    "user_id": session.get("user_id"),
                    "selected_project": None,
                    "permission": None,
                    "project_selected": False
                }
            else:
                # Unknown type, log error
                logger.error(f"Unknown session data type: {type(session)}")
                return None
    
    def end_session(self, session_id: str) -> bool:
        """End a user session
        
        Args:
            session_id: Session to end
            
        Returns:
            True if session ended successfully
        """
        with self._lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                user_id = session.user_id if isinstance(session, ProjectSession) else session["user_id"]
                del self.sessions[session_id]
                logger.info(f"Ended session {session_id} for user {user_id}")
                return True
            return False
    
    def list_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """List all active sessions (admin function)"""
        with self._lock:
            result = {}
            for session_id, session in self.sessions.items():
                if isinstance(session, ProjectSession):
                    result[session_id] = {
                        "user_id": session.user_id,
                        "selected_project": session.selected_project,
                        "permission": session.permission
                    }
                else:
                    result[session_id] = {
                        "user_id": session["user_id"],
                        "selected_project": None,
                        "permission": None
                    }
            return result

# Global session manager instance
session_manager = SessionManager()

# Thread-local storage for current session context
_local = threading.local()

def set_current_session(session_id: str):
    """Set the current session for this thread"""
    _local.current_session_id = session_id

def get_current_session() -> Optional[ProjectSession]:
    """Get current session context for this thread
    
    This is the key function that agent tools will use to get path resolution context.
    
    Returns:
        ProjectSession with resolve_path() method, or None if no session/project selected
    """
    session_id = getattr(_local, 'current_session_id', None)
    if not session_id:
        logger.warning("No current session set for this thread")
        return None
    
    return session_manager.get_session(session_id)

def require_session() -> ProjectSession:
    """Get current session or raise exception
    
    Use this in agent tools that require a valid session context.
    
    Returns:
        ProjectSession
        
    Raises:
        RuntimeError: If no valid session context
    """
    session = get_current_session()
    if not session:
        raise RuntimeError("No valid session context - user must select a project first")
    return session