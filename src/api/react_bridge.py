"""
Bridge API endpoints for React-Chainlit integration
"""

import asyncio
import json
import uuid
from typing import Dict, Optional, Any
from fastapi import APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from src.agents.smart_orchestrator import SmartOrchestratorAgent
from src.agents.base_agent import Task
from datetime import datetime
import uuid

# Initialize Smart Multi-Agent System
orchestrator = SmartOrchestratorAgent()

# Store active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

router = APIRouter(prefix="/api/chat")

class InitRequest(BaseModel):
    currentFolder: Optional[str] = None
    selectedFiles: list[str] = []

class MessageRequest(BaseModel):
    sessionId: str
    message: str
    currentFolder: Optional[str] = None
    selectedFiles: list[str] = []

class ContextUpdate(BaseModel):
    sessionId: str
    currentFolder: Optional[str] = None
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
        # Prepare context for the AI
        context_info = ""
        if request.currentFolder:
            context_info += f"Current folder: {request.currentFolder}\n"
        if request.selectedFiles:
            context_info += f"Selected files: {', '.join(request.selectedFiles)}\n"
        
        # Prepare message with context
        full_message = request.message
        if context_info:
            full_message = f"{context_info}\nUser message: {request.message}"
        
        # Create task for orchestrator
        task = Task(
            id=str(uuid.uuid4()),
            type="general_query",
            content=full_message,
            metadata={
                "current_folder": request.currentFolder,
                "selected_files": request.selectedFiles,
                "project_root": "/data/luyit/script/git/Labacc_copilot/data/alice_projects",
                "session_id": request.sessionId
            },
            created_at=datetime.now(),
            priority=1
        )
        
        # Process with orchestrator
        result = await orchestrator.process(task)
        
        # Get AI response
        ai_response = result.content if result.success else f"Error: {result.content}"
        
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