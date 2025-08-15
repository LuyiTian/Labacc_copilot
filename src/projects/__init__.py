"""
LabAcc Copilot Multi-User Project Management System

This module provides:
- Project-based workspace isolation
- User authentication and session management  
- Bulletproof session-based path resolution
- System-level permission enforcement

Key components:
- project_manager: Core project CRUD and permissions
- auth: User authentication and authorization
- session: Session context and path resolution
- storage: External storage management
"""

from .project_manager import project_manager, Project
from .auth import auth_manager, User
from .session import session_manager, get_current_session, require_session
from .storage import storage_manager

__all__ = [
    'project_manager',
    'Project', 
    'auth_manager',
    'User',
    'session_manager',
    'get_current_session',
    'require_session',
    'storage_manager'
]