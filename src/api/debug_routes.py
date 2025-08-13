"""
Debug API routes for testing and development
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Create debug log file
DEBUG_LOG = Path("debug_agent.log")

router = APIRouter(prefix="/api/debug", tags=["debug"])


class AgentDebugInfo(BaseModel):
    """Debug information from agent interactions"""
    timestamp: str
    user_message: str
    current_folder: str | None
    selected_files: list[str] | None
    agent_response: str
    context_sent: str | None = None
    error: str | None = None


# Store recent debug info in memory
debug_history: list[Dict[str, Any]] = []


@router.post("/log")
async def log_debug_info(info: AgentDebugInfo):
    """Log debug information from agent interactions."""
    
    # Add to memory
    debug_entry = info.dict()
    debug_history.append(debug_entry)
    
    # Keep only last 100 entries
    if len(debug_history) > 100:
        debug_history.pop(0)
    
    # Also write to file
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{info.timestamp}]\n")
        f.write(f"USER: {info.user_message}\n")
        f.write(f"FOLDER: {info.current_folder}\n")
        f.write(f"FILES: {info.selected_files}\n")
        f.write(f"RESPONSE: {info.agent_response[:500]}...\n")
        if info.error:
            f.write(f"ERROR: {info.error}\n")
    
    return {"status": "logged", "entries": len(debug_history)}


@router.get("/history")
async def get_debug_history(limit: int = 10):
    """Get recent debug history."""
    
    # Return last N entries
    recent = debug_history[-limit:] if debug_history else []
    
    return {
        "total_entries": len(debug_history),
        "showing": len(recent),
        "history": recent
    }


@router.get("/analyze")
async def analyze_issues():
    """Analyze common issues in debug history."""
    
    if not debug_history:
        return {"message": "No debug history available"}
    
    # Analyze patterns
    total = len(debug_history)
    errors = [d for d in debug_history if d.get('error')]
    
    # Common user queries
    queries = {}
    for entry in debug_history:
        msg = entry.get('user_message', '').lower()
        # Group similar queries
        if 'folder' in msg:
            queries['folder_queries'] = queries.get('folder_queries', 0) + 1
        elif 'file' in msg:
            queries['file_queries'] = queries.get('file_queries', 0) + 1
        elif 'how many' in msg:
            queries['count_queries'] = queries.get('count_queries', 0) + 1
    
    # Response patterns
    response_issues = {
        'tool_not_available': 0,
        'cannot_read': 0,
        'trouble_processing': 0,
        'raw_json': 0
    }
    
    for entry in debug_history:
        resp = entry.get('agent_response', '').lower()
        if 'not available' in resp or "can't" in resp:
            response_issues['tool_not_available'] += 1
        if 'cannot read' in resp or 'unable to read' in resp:
            response_issues['cannot_read'] += 1
        if 'trouble processing' in resp:
            response_issues['trouble_processing'] += 1
        if resp.strip().startswith('{') and '"name"' in resp:
            response_issues['raw_json'] += 1
    
    return {
        "total_interactions": total,
        "errors": len(errors),
        "query_patterns": queries,
        "response_issues": response_issues,
        "recommendations": [
            "Check if tools are properly registered" if response_issues['tool_not_available'] > 0 else None,
            "Verify file paths are correct" if response_issues['cannot_read'] > 0 else None,
            "Review agent prompt engineering" if response_issues['trouble_processing'] > 0 else None,
            "Fix JSON response formatting" if response_issues['raw_json'] > 0 else None
        ]
    }


@router.delete("/clear")
async def clear_debug_history():
    """Clear debug history."""
    
    debug_history.clear()
    
    # Clear log file
    if DEBUG_LOG.exists():
        DEBUG_LOG.unlink()
    
    return {"status": "cleared"}