# UI Enhancement and Context Injection Plan

**Created**: 2025-01-13  
**Priority**: HIGH  
**Impact**: Major UX improvement and agent performance boost

## 🎯 Objectives

1. **Real-time Tool Visibility**: Show users what tools are being called in real-time
2. **README Context Injection**: Pre-inject README content into prompts for better context
3. **Better Prompt Engineering**: Improve prompts to guide agent behavior more effectively

## 📊 Current Problems

### Problem 1: Black Box Experience
- Users see "thinking..." but don't know what's happening
- No visibility into which tools are being called
- Can't tell if agent is stuck or working

### Problem 2: Inefficient Context Discovery
- Agent calls `analyze_data` to read README files
- Multiple tool calls just to understand current context
- Wastes tokens and time on discovery phase
- Agent gets confused with empty responses after tool calls

### Problem 3: Poor Prompt Engineering
```
Current: "User is in folder: /bob_projects"
Problem: Agent doesn't know what's IN the folder without calling tools
```

## 🚀 Implementation Plan

### Phase 1: Real-time Tool Call Display (Frontend)

#### 1.1 WebSocket Integration
```python
# Backend (src/api/app.py)
from fastapi import WebSocket
import asyncio

@app.websocket("/ws/agent/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    # Stream tool calls as they happen
    
# Agent hook (src/agents/react_agent.py)
async def stream_tool_call(session_id: str, tool_name: str, status: str):
    # Send to WebSocket: {tool: "analyze_data", status: "running"}
```

#### 1.2 Frontend Component
```jsx
// frontend/src/components/ToolCallIndicator.jsx
const ToolCallIndicator = ({ sessionId }) => {
  const [toolCalls, setToolCalls] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8002/ws/agent/${sessionId}`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setToolCalls(prev => [...prev, data]);
    };
  }, [sessionId]);
  
  return (
    <div className="tool-calls-panel">
      {toolCalls.map(call => (
        <div className="tool-call-item">
          <span className="tool-icon">🔧</span>
          <span className="tool-name">{call.tool}</span>
          <span className="tool-status">{call.status}</span>
        </div>
      ))}
    </div>
  );
};
```

### Phase 2: README Context Injection

#### 2.1 Automatic README Loading
```python
# src/agents/react_agent.py

async def inject_experiment_context(current_folder: str) -> str:
    """Pre-load README content for current experiment."""
    if not current_folder or not current_folder.startswith("exp_"):
        return ""
    
    # Read README directly (no tool call needed)
    readme_path = Path(f"data/alice_projects/{current_folder}/README.md")
    if not readme_path.exists():
        readme_path = Path(f"data/bob_projects/{current_folder}/README.md")
    
    if readme_path.exists():
        content = readme_path.read_text()
        # Parse key sections
        memory = ReadmeParser().parse(content)
        
        # Build rich context
        context = f"""
=== CURRENT EXPERIMENT CONTEXT ===
Experiment: {memory.experiment_id}
Status: {memory.status}
Overview: {memory.overview.get('motivation', '')}

Key Results:
{format_results(memory.results)}

Known Issues:
{format_issues(memory.insights)}

Files in this experiment:
{format_files(memory.files)}
================================
"""
        return context
    return ""
```

#### 2.2 Enhanced Message Handler
```python
async def handle_message(message: str, session_id: str, current_folder: str, selected_files: List[str]) -> str:
    # NEW: Pre-inject experiment context
    experiment_context = await inject_experiment_context(current_folder)
    
    # NEW: Pre-inject project overview if in project root
    project_context = ""
    if current_folder == "/bob_projects" or current_folder == "/alice_projects":
        project_context = await inject_project_overview(current_folder)
    
    # Build enriched prompt with pre-loaded context
    enriched_prompt = f"""
{message}

{experiment_context}
{project_context}

[System Instructions]
You have full context about the current experiment above. You do NOT need to call analyze_data for README files.
When asked about optimization, refer to the "Known Issues" and "Key Results" already provided.
Only call tools when you need NEW information not in the context above.
"""
    
    # This reduces tool calls and improves response quality
    result = await agent.ainvoke({"messages": [HumanMessage(content=enriched_prompt)]})
```

### Phase 3: Better Prompt Engineering

#### 3.1 Structured Context Templates
```python
EXPERIMENT_CONTEXT_TEMPLATE = """
You are analyzing experiment {exp_id} in a {project_type} research project.

COMPLETED WORK:
- Status: {status}
- Key Finding: {main_result}
- Problem Identified: {main_issue}

CURRENT FILES:
{file_list}

OPTIMIZATION NEEDED:
{optimization_focus}

When answering questions:
1. Use the context above first before calling tools
2. For optimization questions, focus on the "Problem Identified" section
3. Only call tools for information NOT in this context
"""

PROJECT_OVERVIEW_TEMPLATE = """
PROJECT: {project_name}
Total Experiments: {exp_count}
Latest Experiment: {latest_exp}
Current Phase: {phase}

EXPERIMENT SUMMARY:
{experiment_list}

When answering project-level questions:
1. Use this overview to understand project progress
2. Call scan_project only if you need detailed status
3. For specific experiment questions, the context is already loaded
"""
```

#### 3.2 Smart Context Selection
```python
def build_smart_context(user_message: str, current_folder: str) -> str:
    """Build context based on query intent."""
    
    # Detect query type using simple heuristics
    is_optimization = any(word in user_message.lower() for word in 
                         ['optimize', 'improve', '优化', '改进', 'enhance'])
    is_overview = any(word in user_message.lower() for word in
                     ['summary', 'overview', '总结', '概览', 'status'])
    
    if is_optimization and current_folder.startswith("exp_"):
        # Load optimization-focused context
        return load_optimization_context(current_folder)
    elif is_overview:
        # Load project overview
        return load_project_overview()
    else:
        # Load standard context
        return load_standard_context(current_folder)
```

## 📈 Expected Improvements

### Before:
1. Agent calls 3-4 tools just to understand context
2. User sees nothing while agent works
3. Empty responses when tool calls don't return expected format
4. 10-15 second response time for simple questions

### After:
1. Zero tool calls for context understanding
2. Real-time visibility of tool execution
3. Rich responses with pre-loaded context
4. 2-3 second response time for context-aware questions

## 🔧 Implementation Steps

### Step 1: Backend WebSocket Support (1 hour)
- [ ] Add WebSocket endpoint to FastAPI
- [ ] Create tool call streaming mechanism
- [ ] Add session-based WebSocket management

### Step 2: Frontend Tool Display (2 hours)
- [ ] Create ToolCallIndicator component
- [ ] Integrate WebSocket client
- [ ] Add styling for tool call display
- [ ] Handle connection/disconnection gracefully

### Step 3: Context Injection System (2 hours)
- [ ] Implement README pre-loading
- [ ] Create context formatting functions
- [ ] Update handle_message with context injection
- [ ] Test with various folder scenarios

### Step 4: Prompt Engineering (1 hour)
- [ ] Create context templates
- [ ] Implement smart context selection
- [ ] Update system instructions
- [ ] Test with Chinese and English queries

### Step 5: Testing & Optimization (1 hour)
- [ ] Test tool visibility with multiple tools
- [ ] Verify context reduces tool calls
- [ ] Measure response time improvements
- [ ] Test with complex optimization queries

## 🎯 Success Metrics

1. **Tool Call Reduction**: 70% fewer tool calls for context discovery
2. **Response Time**: 50% faster for context-aware queries
3. **User Satisfaction**: Clear visibility of agent actions
4. **Error Reduction**: No more empty "..." responses
5. **Multi-language**: Works perfectly in Chinese and English

## 🚦 Risk Mitigation

### Risk 1: WebSocket Connection Issues
- **Mitigation**: Fallback to polling if WebSocket fails
- **Implementation**: Hybrid approach with graceful degradation

### Risk 2: Context Too Large
- **Mitigation**: Smart truncation of README content
- **Implementation**: Extract only relevant sections based on query

### Risk 3: Prompt Confusion
- **Mitigation**: Clear section markers in prompt
- **Implementation**: Use === delimiters and structured format

## 📝 Example: Optimized Flow

### User asks: "结合项目内容，帮我思考下一步如何优化"

**OLD FLOW**:
1. Agent calls list_folder_contents("/bob_projects")
2. Agent calls list_folder_contents("/bob_projects/exp_001") 
3. Agent calls analyze_data("README.md")
4. Agent gets confused, returns "..."

**NEW FLOW**:
1. System pre-injects exp_001 README context
2. Agent immediately sees issues and optimization points
3. Agent responds with specific optimization suggestions
4. UI shows: "🔧 Thinking with experiment context..."

## 🎉 End Result

Users will experience:
1. **Transparency**: See exactly what tools are running
2. **Speed**: Instant context-aware responses
3. **Reliability**: No more empty responses
4. **Intelligence**: Agent has full context from the start

---

**Next Steps**: 
1. Review plan with team
2. Start with WebSocket implementation
3. Test context injection with real experiments
4. Deploy to development environment