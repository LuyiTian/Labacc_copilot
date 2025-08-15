"""
Project management API routes for multi-user system
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import uuid

from src.projects.session import session_manager
from src.projects.temp_manager import get_temp_project_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

class ProjectInfo(BaseModel):
    project_id: str
    name: str
    permission: str

class ProjectListResponse(BaseModel):
    projects: List[ProjectInfo]
    current_session: str

class SelectProjectRequest(BaseModel):
    project_id: str

@router.get("/list", response_model=ProjectListResponse)
async def list_projects(request: Request) -> ProjectListResponse:
    """Get list of projects accessible to the current user"""
    
    # Create or get session ID (simplified for development)
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        # Create session with temp user
        session_manager.create_session(session_id, "temp_user")
    else:
        # Ensure existing session is still valid, recreate if needed
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            session_manager.create_session(session_id, "temp_user")
    
    # Get projects from temp manager
    temp_manager = get_temp_project_manager()
    projects = temp_manager.get_user_projects("temp_user")
    
    return ProjectListResponse(
        projects=[
            ProjectInfo(
                project_id=p["project_id"],
                name=p["name"],
                permission=p["permission"]
            )
            for p in projects
        ],
        current_session=session_id
    )

@router.post("/select")
async def select_project(request: SelectProjectRequest, http_request: Request) -> Dict[str, Any]:
    """Select a project for the current session"""
    
    # Get session ID
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required in X-Session-ID header")
    
    # Select the project
    project_session = session_manager.select_project(session_id, request.project_id)
    
    if not project_session:
        raise HTTPException(status_code=403, detail=f"Cannot access project {request.project_id}")
    
    return {
        "status": "success",
        "selected_project": project_session.selected_project,
        "permission": project_session.permission,
        "project_path": str(project_session.project_path)
    }

@router.get("/current")
async def get_current_project(request: Request) -> Dict[str, Any]:
    """Get currently selected project information"""
    
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return {"project_selected": False, "session_id": None}
    
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        return {"project_selected": False, "session_id": session_id}
    
    return {
        "project_selected": session_info["project_selected"],
        "session_id": session_id,
        "selected_project": session_info.get("selected_project"),
        "permission": session_info.get("permission"),
        "user_id": session_info.get("user_id")
    }

@router.post("/create-demo")
async def create_demo_project(request: Request) -> Dict[str, Any]:
    """Create a demo project for testing"""
    
    session_id = request.headers.get("X-Session-ID", f"session_{uuid.uuid4().hex[:8]}")
    
    # Ensure session exists
    if not session_manager.get_session_info(session_id):
        session_manager.create_session(session_id, "temp_user")
    
    # Create demo project
    temp_manager = get_temp_project_manager()
    project_id = temp_manager.create_demo_project()
    
    return {
        "status": "success",
        "project_id": project_id,
        "message": "Demo project created successfully",
        "session_id": session_id
    }

@router.get("/debug/sessions")
async def debug_sessions() -> Dict[str, Any]:
    """Debug endpoint to see active sessions"""
    return {
        "active_sessions": session_manager.list_active_sessions()
    }