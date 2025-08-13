# React Agent API Specification v2.1

## Executive Summary

This specification documents the simplified React Agent API architecture implemented in LabAcc Copilot v2.1, using LangGraph's React agent pattern with tools.

## 1. Architecture Overview

### Current Implementation (v2.1)
```
User → React Frontend → FastAPI → LangGraph React Agent → Tools → Response
```

### Key Components
- **React Frontend**: localhost:5173 (unchanged)
- **FastAPI Backend**: localhost:8002
- **React Agent**: Single LangGraph agent with tools
- **Tools**: Simple @tool decorated functions

## 2. API Endpoints

### 2.1 Chat Endpoints

#### Initialize Session
```http
POST /api/chat/init
Content-Type: application/json

{
  "currentFolder": string | null,
  "selectedFiles": string[]
}

Response:
{
  "sessionId": string,
  "status": "initialized"
}
```

#### Send Message
```http
POST /api/chat/message
Content-Type: application/json

{
  "sessionId": string,
  "message": string,
  "currentFolder": string | null,
  "selectedFiles": string[]
}

Response:
{
  "response": string,
  "author": "Assistant",
  "sessionId": string
}
```

#### Update Context
```http
POST /api/chat/context
Content-Type: application/json

{
  "sessionId": string,
  "currentFolder": string | null,
  "selectedFiles": string[]
}

Response:
{
  "status": "context_updated"
}
```

### 2.2 File Management Endpoints (unchanged)

#### List Files
```http
GET /api/files/list?path=/

Response:
{
  "files": [
    {
      "name": string,
      "type": "file" | "folder",
      "path": string,
      "size": number
    }
  ]
}
```

#### Upload Files
```http
POST /api/files/upload
Content-Type: multipart/form-data

FormData:
- files: File[]
- path: string

Response:
{
  "uploaded": string[],
  "failed": string[]
}
```

## 3. React Agent Implementation

### 3.1 Agent Structure
```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Define tools
@tool
def scan_project() -> str:
    """Scan all experiments in the project."""
    # Implementation
    return "Found experiments: ..."

@tool
def analyze_experiment(folder_name: str) -> str:
    """Analyze a specific experiment folder."""
    # Implementation
    return f"Analysis of {folder_name}: ..."

# Create agent
agent = create_react_agent(llm, [scan_project, analyze_experiment, ...])
```

### 3.2 Message Processing
```python
async def handle_message(message: str, session_id: str) -> str:
    """Process user message through React agent."""
    
    # Create agent
    agent = create_simple_agent()
    
    # Invoke with message
    result = agent.invoke({
        "messages": [HumanMessage(content=message)]
    })
    
    # Extract response
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    
    return "No response generated."
```

## 4. Available Tools

### 4.1 Project Scanning
```python
@tool
def scan_project() -> str:
    """Scan all experiments in the project. Lists experiment folders with details."""
```

### 4.2 Experiment Analysis
```python
@tool
def analyze_experiment(folder_name: str) -> str:
    """Analyze a specific experiment folder.
    Args:
        folder_name: Name of experiment folder like 'exp_001_pcr'
    """
```

### 4.3 Literature Research
```python
@tool
def research_literature(query: str) -> str:
    """Search scientific literature.
    Args:
        query: Research topic or question
    """
```

### 4.4 Protocol Optimization
```python
@tool
def optimize_protocol(experiment_type: str, issue: str = "") -> str:
    """Get optimization suggestions.
    Args:
        experiment_type: Type like 'PCR', 'Western blot'
        issue: Current problem (optional)
    """
```

### 4.5 File Management
```python
@tool
def manage_files(action: str, folder_name: str = "", ...) -> str:
    """Manage experimental files and folders.
    Args:
        action: 'create_folder', 'save_files', 'list_files'
        folder_name: Name of the folder
    """
```

## 5. Adding New Capabilities

### 5.1 Simple Tool Addition
```python
# 1. Define the tool
@tool
def new_capability(param: str) -> str:
    """Description for LLM to understand when to use this tool."""
    # Implementation
    return "Result"

# 2. Add to tools list
tools = [
    scan_project,
    analyze_experiment,
    new_capability,  # Just add here!
    ...
]

# 3. That's it! The agent will automatically use it when appropriate
```

## 6. Key Improvements in v2.1

### Simplifications
- **No orchestrators**: Single React agent handles everything
- **No intent detection**: LLM naturally understands intent
- **No keyword matching**: Works in any language
- **No complex routing**: Agent selects tools automatically

### Benefits
- **70% less code** than v2.0
- **Easier to maintain** and extend
- **Natural language** understanding
- **Multi-language** support out of the box

## 7. Testing

### Quick Test
```bash
# Start backend
uv run uvicorn src.api.app:app --port 8002 --reload

# Test with curl
curl -X POST http://localhost:8002/api/chat/init -H "Content-Type: application/json" -d '{}'

# Send message
curl -X POST http://localhost:8002/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "...", "message": "Scan my experiments"}'
```

### Direct Agent Test
```bash
uv run python src/agents/react_agent.py
```

## 8. Performance Characteristics

- **Response Time**: 2-3 seconds for most queries
- **Deep Research**: 10-30 seconds (Tavily API)
- **Concurrent Sessions**: Supported
- **Memory**: Conversation history per session

## 9. Error Handling

The system gracefully handles:
- Invalid session IDs
- Tool execution failures
- LLM timeouts
- File operation errors

All errors return structured responses with helpful messages.

## 10. Future Enhancements (v2.2)

- Background task execution
- Proactive monitoring tools
- Scheduled analysis
- Real-time notifications
- Extended tool library

---

**Version**: 2.1.0  
**Status**: Implemented and Operational  
**Architecture**: LangGraph React Agent with Tools