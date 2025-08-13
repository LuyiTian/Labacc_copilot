"""FastAPI application for LabAcc Copilot REST API

This runs separately from Chainlit to provide file management endpoints
for the React frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "service": "LabAcc Copilot API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
