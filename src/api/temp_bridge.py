"""
Temporary bridge for development - simplified React-Agent integration
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import logging
import uuid

from src.agents.react_agent import handle_message
from src.projects.session import session_manager, set_current_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    session_id: str
    project_selected: bool

@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest, http_request: Request) -> MessageResponse:
    """Send a message to the agent with session context"""
    
    # Get or create session ID
    session_id = request.session_id or http_request.headers.get("X-Session-ID")
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        # Auto-create session with temp user
        session_manager.create_session(session_id, "temp_user")
    
    # Set current session for this thread
    set_current_session(session_id)
    
    # Check if project is selected
    session_info = session_manager.get_session_info(session_id)
    project_selected = session_info and session_info.get("project_selected", False)
    
    try:
        # Handle the message
        if project_selected:
            response = await handle_message(request.message, session_id)
        else:
            response = "Please select a project first before chatting with the agent."
        
        return MessageResponse(
            response=response,
            session_id=session_id,
            project_selected=project_selected
        )
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return MessageResponse(
            response=f"Error: {str(e)}",
            session_id=session_id,
            project_selected=project_selected
        )

@router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Get session status"""
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_info