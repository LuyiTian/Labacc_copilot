"""
Bridge API endpoints for React-LangGraph integration with Multi-User Support

Handles authenticated sessions, project selection, and agent communication.
Integrates with the new session-based project system for bulletproof path resolution.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from pydantic import BaseModel

from src.agents.react_agent import handle_message as handle_user_message
from src.projects.auth import auth_manager
from src.projects.session import session_manager, set_current_session
from src.projects.project_manager import project_manager

router = APIRouter(prefix="/api/chat")
security = HTTPBearer()

# Request/Response models
class InitSessionRequest(BaseModel):
    """Initialize session after authentication"""
    pass

class ProjectSelectionRequest(BaseModel):
    sessionId: str
    projectId: str

class MessageRequest(BaseModel):
    sessionId: str
    message: str
    # Note: No more currentFolder/selectedFiles - path resolution is session-based!

class ProjectInfo(BaseModel):
    project_id: str
    name: str
    description: str
    permission: str  # owner/shared/admin
    owner_id: str

class SessionInfo(BaseModel):
    sessionId: str
    user_id: str
    selected_project: Optional[str]
    permission: Optional[str] 
    project_selected: bool
    message_count: int
    created_at: str

# Dependency to get current authenticated user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and verify user from bearer token"""
    token = credentials.credentials
    user_info = auth_manager.verify_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

@router.post("/init")
async def init_session(request: InitSessionRequest, 
                      current_user: dict = Depends(get_current_user)):
    """Initialize a new authenticated chat session"""
    session_id = str(uuid.uuid4())
    
    # Create session in session manager
    success = session_manager.create_session(session_id, current_user["user_id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )
    
    return {
        "sessionId": session_id,
        "status": "session_created",
        "user_id": current_user["user_id"],
        "message": "Session created. Please select a project to continue."
    }

@router.get("/projects")
async def get_user_projects(current_user: dict = Depends(get_current_user)) -> List[ProjectInfo]:
    """Get list of projects accessible to current user"""
    projects = project_manager.get_user_projects(current_user["user_id"])
    
    return [
        ProjectInfo(
            project_id=project.project_id,
            name=project.name,
            description=project.description,
            permission=project_manager.get_user_permission(current_user["user_id"], project.project_id),
            owner_id=project.owner_id
        )
        for project in projects
    ]

@router.post("/select-project")
async def select_project(request: ProjectSelectionRequest,
                        current_user: dict = Depends(get_current_user)):
    """Select a project for the session"""
    
    # Verify session belongs to current user
    session_info = session_manager.get_session_info(request.sessionId)
    if not session_info or session_info["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session not found or access denied"
        )
    
    # Select project in session manager (includes permission checks)
    project_session = session_manager.select_project(request.sessionId, request.projectId)
    
    if not project_session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to project or project not found"
        )
    
    return {
        "status": "project_selected",
        "sessionId": request.sessionId,
        "projectId": request.projectId,
        "permission": project_session.permission,
        "message": f"Project selected. You can now chat with the agent about this project."
    }

@router.post("/message")
async def send_message(request: MessageRequest,
                      current_user: dict = Depends(get_current_user)):
    """Send a message to the AI assistant"""
    
    # Get session context
    project_session = session_manager.get_session(request.sessionId)
    
    if not project_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No project selected. Please select a project first."
        )
    
    # Verify session belongs to current user
    if project_session.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to session"
        )
    
    try:
        # Set current session context for this request thread
        set_current_session(request.sessionId)
        
        # Process with the enhanced React agent
        # NOTE: No more currentFolder/selectedFiles - agent uses session.resolve_path()!
        ai_response = await handle_user_message(
            message=request.message,
            session_id=request.sessionId,
            current_folder=None,  # Not used anymore
            selected_files=None   # Not used anymore
        )
        
        # Log for debugging (in development)
        try:
            from src.api.debug_routes import debug_history
            debug_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": current_user["user_id"],
                "project_id": project_session.selected_project,
                "user_message": request.message,
                "agent_response": ai_response
            }
            debug_history.append(debug_entry)
            if len(debug_history) > 100:
                debug_history.pop(0)
        except:
            pass  # Don't fail if debug logging fails

        return {
            "response": ai_response,
            "author": "Assistant",
            "sessionId": request.sessionId,
            "projectId": project_session.selected_project
        }

    except Exception as e:
        error_message = f"Error processing your message: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

@router.get("/session/{session_id}")
async def get_session(session_id: str,
                     current_user: dict = Depends(get_current_user)) -> SessionInfo:
    """Get session information"""
    
    session_info = session_manager.get_session_info(session_id)
    
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to current user  
    if session_info["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to session"
        )
    
    return SessionInfo(
        sessionId=session_id,
        user_id=session_info["user_id"],
        selected_project=session_info.get("selected_project"),
        permission=session_info.get("permission"),
        project_selected=session_info.get("project_selected", False),
        message_count=0,  # TODO: Implement message history if needed
        created_at=datetime.now().isoformat()  # TODO: Get from session
    )

@router.delete("/session/{session_id}")
async def delete_session(session_id: str,
                        current_user: dict = Depends(get_current_user)):
    """Delete a session"""
    
    session_info = session_manager.get_session_info(session_id)
    
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to current user
    if session_info["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to session"
        )
    
    success = session_manager.end_session(session_id)
    
    if success:
        return {"status": "session_deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


async def notify_agent_of_upload(
    session_id: str,
    file_path: str,
    experiment_id: str,
    original_name: str,
    conversion_status: str = "success"
) -> str:
    """Notify agent about a newly uploaded file and get proactive analysis
    
    Args:
        session_id: Current session ID
        file_path: Path to the converted file (or original if no conversion)
        experiment_id: Experiment folder name
        original_name: Original filename that was uploaded
        conversion_status: Status of the conversion (success/failed/not_needed)
    
    Returns:
        Agent's analysis response with follow-up questions
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Set current session context for the agent
        set_current_session(session_id)
        
        # Load experiment context from README
        from src.memory.memory import SimpleMemoryManager
        from src.projects.session import session_manager
        
        session = session_manager.get_session(session_id)
        if session:
            memory_manager = SimpleMemoryManager(session.project_path)
            experiment_memory = memory_manager.load_memory(experiment_id)
            
            if experiment_memory:
                experiment_context = f"""
## Experiment Context from README:
{experiment_memory.raw_content[:1000]}  # First 1000 chars for context
"""
            else:
                experiment_context = "\n## Note: No README found for this experiment yet.\n"
        else:
            experiment_context = ""
        
        # Construct a comprehensive message with context
        if conversion_status == "success":
            message = f"""A new file was uploaded and converted to {experiment_id}:
• Original file: {original_name}
• Converted location: {file_path}
{experiment_context}

IMPORTANT: First, use the read_file tool to read the actual content of {file_path}

After reading the file, please:
1. Analyze the ACTUAL content you read (do not make up information)
2. Provide a brief summary of the content (2-3 sentences) based on what you actually read
3. Identify any important findings or patterns from the real content
4. Generate 1-2 specific follow-up questions to clarify:
   - The purpose or context of this file
   - Any experimental parameters or conditions
   - How this relates to other experiment data

Format your response with clear sections:
**Summary:** [your summary based on actual file content]
**Key Findings:** [findings from the real file]
**Questions for User:** [numbered questions]

Focus on practical insights relevant to the experiment. Base everything on the actual file content, not assumptions."""
        else:
            message = f"""A new file was uploaded to {experiment_id}:
• File: {original_name}
• Location: {experiment_id}/originals/{original_name}
{experiment_context}

IMPORTANT: First, try to use the read_file tool to read {experiment_id}/originals/{original_name}

If you can read it, analyze the actual content. If it's a binary file that cannot be read as text, note that and provide context based on the filename and experiment.

Please provide a brief summary, then ask 1-2 clarifying questions about its purpose or experimental context."""
        
        # Get analysis from agent
        logger.info(f"Requesting contextual analysis for uploaded file: {original_name}")
        ai_response = await handle_user_message(
            message=message,
            session_id=session_id
        )
        
        # Store uploaded file info in session for context
        if session:
            # Track recent uploads (keep last 10)
            if not hasattr(session, 'recent_uploads'):
                session.recent_uploads = []
            
            upload_info = {
                'file': original_name,
                'path': file_path,
                'experiment': experiment_id,
                'timestamp': datetime.now().isoformat(),
                'converted': conversion_status == 'success',
                'analysis': ai_response[:200]  # Store first 200 chars of analysis
            }
            session.recent_uploads.append(upload_info)
            
            # Keep only last 10 uploads
            if len(session.recent_uploads) > 10:
                session.recent_uploads = session.recent_uploads[-10:]
            
            # Also track pending questions for memory update
            if not hasattr(session, 'pending_questions'):
                session.pending_questions = {}
            session.pending_questions[experiment_id] = {
                'file': original_name,
                'path': file_path,
                'timestamp': datetime.now().isoformat(),
                'asked': True,
                'initial_analysis': ai_response
            }
        
        logger.info(f"Agent analysis with questions complete for {original_name}")
        return ai_response
        
    except Exception as e:
        logger.error(f"Failed to notify agent of upload: {e}")
        return f"File uploaded successfully but analysis failed: {str(e)}"
