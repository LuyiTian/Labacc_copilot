"""
Bridge API endpoints for React-LangGraph integration
Simplified to use a single React agent instead of complex orchestration
"""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agents.react_agent import handle_message as handle_user_message

# Store active sessions
active_sessions: dict[str, dict[str, Any]] = {}

router = APIRouter(prefix="/api/chat")

class InitRequest(BaseModel):
    currentFolder: str | None = None
    selectedFiles: list[str] = []

class MessageRequest(BaseModel):
    sessionId: str
    message: str
    currentFolder: str | None = None
    selectedFiles: list[str] = []

class ContextUpdate(BaseModel):
    sessionId: str
    currentFolder: str | None = None
    selectedFiles: list[str] = []

@router.post("/init")
async def init_session(request: InitRequest):
    """Initialize a new chat session"""
    session_id = str(uuid.uuid4())

    active_sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "current_folder": request.currentFolder,
        "selected_files": request.selectedFiles,
        "thread_id": f"react_user:{session_id}",
        "message_history": []
    }

    return {
        "sessionId": session_id,
        "status": "initialized"
    }

@router.post("/context")
async def update_context(request: ContextUpdate):
    """Update session context (current folder, selected files)"""
    if request.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[request.sessionId]
    session["current_folder"] = request.currentFolder
    session["selected_files"] = request.selectedFiles

    return {"status": "context_updated"}

@router.post("/message")
async def send_message(request: MessageRequest):
    """Send a message to the AI assistant"""
    if request.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[request.sessionId]

    # Update context
    session["current_folder"] = request.currentFolder
    session["selected_files"] = request.selectedFiles

    # Add user message to history
    user_message = {
        "id": str(uuid.uuid4()),
        "content": request.message,
        "author": "User",
        "timestamp": datetime.now().isoformat(),
        "type": "user_message"
    }
    session["message_history"].append(user_message)

    try:
        # Add context to message if needed
        full_message = request.message
        if request.currentFolder:
            full_message += f"\n[Current folder: {request.currentFolder}]"
        if request.selectedFiles:
            full_message += f"\n[Selected files: {', '.join(request.selectedFiles)}]"
        
        # Process with the simplified React agent
        ai_response = await handle_user_message(
            message=full_message,
            session_id=request.sessionId
        )

        # Add AI response to history
        ai_message = {
            "id": str(uuid.uuid4()),
            "content": ai_response,
            "author": "Assistant",
            "timestamp": datetime.now().isoformat(),
            "type": "ai_message"
        }
        session["message_history"].append(ai_message)

        return {
            "response": ai_response,
            "author": "Assistant",
            "sessionId": request.sessionId
        }

    except Exception as e:
        error_message = f"Error processing your message: {str(e)}"

        # Add error to history
        error_msg = {
            "id": str(uuid.uuid4()),
            "content": error_message,
            "author": "System",
            "timestamp": datetime.now().isoformat(),
            "type": "error_message"
        }
        session["message_history"].append(error_msg)

        raise HTTPException(status_code=500, detail=error_message)

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    return {
        "sessionId": session_id,
        "currentFolder": session.get("current_folder"),
        "selectedFiles": session.get("selected_files", []),
        "messageCount": len(session.get("message_history", [])),
        "createdAt": session.get("created_at")
    }

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del active_sessions[session_id]
    return {"status": "session_deleted"}
