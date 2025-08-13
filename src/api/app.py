"""FastAPI application for LabAcc Copilot REST API

This runs separately from Chainlit to provide file management endpoints
for the React frontend.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Set, Optional
import json
import logging

logger = logging.getLogger(__name__)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        # Store active connections by session_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket connected for session: {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected for session: {session_id}")
    
    async def send_tool_update(self, session_id: str, tool_name: str, status: str, args: dict = None):
        """Send tool call update to all connections for a session"""
        if session_id in self.active_connections:
            message = json.dumps({
                "type": "tool_call",
                "tool": tool_name,
                "status": status,
                "args": args or {}
            })
            
            disconnected = set()
            for websocket in self.active_connections[session_id]:
                try:
                    await websocket.send_text(message)
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.active_connections[session_id].discard(ws)

# Create global connection manager
manager = ConnectionManager()

# Create FastAPI app
app = FastAPI(title="LabAcc Copilot API", version="1.0.0")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount file management routes
from src.api import file_router

app.include_router(file_router)

# Mount React-Chainlit bridge routes
from src.api.react_bridge import router as chat_router

app.include_router(chat_router)

# Mount debug routes (development only)
from src.api.debug_routes import router as debug_router

app.include_router(debug_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "service": "LabAcc Copilot API"}

# WebSocket endpoint for real-time tool updates
@app.websocket("/ws/agent/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming tool call updates to frontend"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and wait for any messages
            data = await websocket.receive_text()
            # Could handle ping/pong or other control messages here
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

# Pydantic model for tool update requests
class ToolUpdateRequest(BaseModel):
    session_id: str
    tool_name: str
    status: str  # "starting", "running", "completed", "error"
    args: Optional[dict] = None

# HTTP endpoint for agent to send tool updates
@app.post("/api/tool-update")
async def send_tool_update(request: ToolUpdateRequest):
    """HTTP endpoint for agent to send tool call updates"""
    await manager.send_tool_update(
        request.session_id, 
        request.tool_name, 
        request.status, 
        request.args
    )
    return {"status": "sent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
