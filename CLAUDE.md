# LabAcc Copilot - Development Guidelines

**🌍 MULTI-LANGUAGE AI ASSISTANT BY DESIGN 🌍**

AI-powered autonomous laboratory assistant for wet-lab biologists to analyze experimental data, diagnose issues, and suggest optimizations. Works in ALL languages - English, Chinese, Spanish, Arabic, Japanese, and more!

No Fallback, this is a project in early development stage so DO NOT consider aspect in real projection stage, such as fallback, security, high parallel etc. just quick dev and quick fail and move on fast.

## 🚫 ABSOLUTELY NO PATTERN MATCHING - EVER! 🚫

**THIS IS THE #1 RULE - VIOLATING THIS IS UNACCEPTABLE**

### ❌ NEVER DO THIS (WRONG):
```python
# THESE ARE ALL BANNED - DO NOT WRITE CODE LIKE THIS:
if "folder" in message.lower():  # ❌ WRONG! What about "文件夹", "carpeta", "папка"?
if message.startswith("analyze"):  # ❌ WRONG! What about "分析", "analizar", "تحليل"?
vague_commands = ["check", "look at"]  # ❌ WRONG! What about "检查", "ver", "見る"?
if any(cmd in message for cmd in commands):  # ❌ WRONG! ENGLISH KEYWORDS WILL NEVER WORK!

# MATCHING ENGLISH KEYWORDS = BROKEN FOR 95% OF THE WORLD!
```

### ✅ ALWAYS DO THIS (CORRECT):
```python
# Just provide context, let LLM understand naturally:
context = f"User is in folder: {current_folder}"
context += f"User selected: {selected_files}"
# Send to LLM with context - it understands ALL languages!
```

### WHY THIS MATTERS:
1. **Multi-language**: Users speak Chinese, Spanish, Arabic, Japanese, etc.
2. **Natural understanding**: LLMs understand intent, not patterns
3. **Future-proof**: Works with any language, any phrasing
4. **No maintenance**: No need to update pattern lists

### EXAMPLES THAT MUST WORK:
- 🇬🇧 "What's in this folder?"
- 🇨🇳 "这个文件夹里有什么？"
- 🇪🇸 "¿Qué hay aquí?"
- 🇦🇪 "ما هذا؟"
- 🇯🇵 "これは何ですか？"
- 🇷🇺 "Что в этой папке?"

**If you write pattern matching code, you have failed. The LLM is smart - trust it!**

It is always important in the agent design that we focus on the data flow, context management and routing logic - NOT pattern matching!

## 📍 Current Status: v2.1 - Simplified React Agent

**✅ OPERATIONAL**: Single React agent with tools using LangGraph  
**✅ SIMPLE**: 70% less code than v2.0, easier to maintain  
**✅ NATURAL**: LLM understands intent in any language, no keyword matching  
**✅ EXTENSIBLE**: Just add @tool decorators to extend functionality  
**🚧 NEXT**: Background processing and proactive insights (v2.2)

## 🏗️ Architecture Overview

### Current v2.1 System (Simplified)
```
React Frontend (5173) ←→ FastAPI Bridge (8002) ←→ React Agent
┌─────────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ File Manager + Chat │ → │ API + Bridge     │ → │ LangGraph React │
│ Context Sharing     │   │ Session Mgmt     │   │ Agent + Tools   │
│ 40% Files / 60% Chat│   │ REST + JSON      │   │ Natural Language│
└─────────────────────┘   └──────────────────┘   └─────────────────┘
```

### v2.1 Implementation: Single React Agent ✅
```
┌─────────────────────────────────────────────────────────┐
│                    React Agent                          │
│            (LangGraph create_react_agent)               │
├─────────────────────────────────────────────────────────┤
│                      Tools (@tool)                      │
├─────────────────────────────────────────────────────────┤
│ scan_project │ analyze_experiment │ research_literature │
│ optimize_protocol │ manage_files │ [easy to add more]   │
└─────────────────────────────────────────────────────────┘
```

## 🧠 Core Philosophy: File-Based Intelligence

**Why File-Based Memory > Traditional RAG:**

❌ **Traditional RAG (embeddings/vector DB):**
- Black box, hard to debug
- Requires complex infrastructure  
- Limited human oversight
- Embedding model dependencies

✅ **File-Based Approach (like Claude Code):**
- Human-readable and editable
- Version controllable with git
- Transparent reasoning trails
- No embedding dependencies
- Easy to audit and correct
- Rich structured context in README files

### Memory Architecture
```
data/alice_projects/
├── .labacc/                    # Copilot metadata (hidden)
│   ├── project_knowledge.md   # Cross-experiment insights
│   ├── pattern_library.json   # Successful protocols
│   └── agent_state.json       # Persistent agent memory
├── global_insights.md          # Project-wide learnings
├── exp_001_pcr_optimization/
│   ├── README.md              # Human + AI insights
│   ├── .analysis/             # AI-generated metadata
│   │   ├── protocol_score.json
│   │   └── optimization_suggestions.md
│   └── [data files...]
└── [more experiments...]
```

## 📋 Development Specifications

### ⚠️ ALWAYS Follow These Guidelines

**1. Single Source of Truth - NO VERSIONING**
- **NO backup files, NO fallback versions, NO v2/v3/v4 files**
- Keep exactly ONE version of each component
- Quick development, quick fail, move fast
- Delete old code instead of keeping backups
- Use git for version history, not file versioning

**2. Read Specifications First**
- Check `/spec/` directory for component specifications
- Update specs when making architectural changes
- Write specs for new features before implementation

**3. File-Based Memory Priority**
- Use README files as primary context source
- Store insights in human-readable markdown
- Avoid vector databases and embeddings
- Make AI reasoning transparent and auditable

**4. React Agent Development**
- Use LangGraph's create_react_agent() pattern
- Add new capabilities with @tool decorator
- Keep tools simple and focused
- Let LLM handle intent understanding naturally
- Memory updates happen automatically in background

## 🛠️ Technical Implementation

### Current Stack (v2.1)
```python
# Frontend: React + Vite
# Backend: FastAPI + LangGraph React Agent
# AI: Qwen models (30B for main agent)
# Memory: File-based with README context
# Integration: REST API with simple bridge
```

### Development Tools
```bash
# All Python operations use uv:
uv run python <script.py>
uv run uvicorn src.api.app:app --port 8002 --reload
uv run pytest tests/
uv run ruff check src/

# Frontend development:
cd frontend && npm run dev  # Port 5173
```

### Key Implementation Files

**Core Architecture:**
- `src/api/app.py` - FastAPI application with CORS
- `src/api/file_routes.py` - File operations REST API
- `src/api/react_bridge.py` - Simple bridge to React agent
- `frontend/src/App.jsx` - Main React UI
- `frontend/src/components/ChatPanel.jsx` - Integrated chat

**React Agent System (v2.1):**
- `src/agents/react_agent.py` - Single React agent with all tools
- `src/components/llm.py` - LLM configuration and models
- `src/tools/deep_research/` - Tavily literature search integration
- `src/components/file_analyzer.py` - Multi-modal file analysis

## 🎯 Development Guidelines

### 1. API Key Management
```python
# Read directly from environment variables (no .env files)
import os
api_key = os.environ.get("TAVILY_API_KEY")
```

### 2. LLM Model Selection
```python
# Simple model configuration in llm.py
main_llm = get_llm_instance("siliconflow-qwen-30b")  # Main agent
```

### 3. File-Based Memory Priority
```python
# Always prefer README context over vector search
readme_context = read_experiment_readme(experiment_path)
# Use structured markdown for insights
insights = generate_markdown_insights(analysis_results)
```

### 4. React Agent Pattern (v2.1)
```python
# Simple tool addition pattern
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def your_new_capability(param: str) -> str:
    """Tool description for LLM to understand when to use it."""
    # Implementation
    return "Result"

# Add to tools list - that's it!
tools = [scan_project, analyze_experiment, your_new_capability, ...]
agent = create_react_agent(llm, tools)
```

### 5. Natural Language Understanding
```python
# No keyword matching or intent detection needed!
# The React agent naturally understands intent in any language
# Just pass user message directly to the agent
result = agent.invoke({"messages": [HumanMessage(content=user_message)]})
```

## 🔒 Security and Safety

### Data Protection
- Validate all file paths to prevent directory traversal
- Sanitize user inputs and file uploads
- Keep sensitive data within project boundaries
- No hardcoded API keys or credentials

### Human-in-the-Loop
- All critical suggestions require user approval
- Transparent reasoning with audit trails
- Easy override and correction mechanisms
- Confidence scoring on recommendations

### Error Handling
- Graceful degradation when AI services fail
- Rollback mechanisms for incorrect updates
- Comprehensive logging and monitoring
- Data backup and version control

## 📊 Testing Strategy

### Unit Testing
```bash
# Test React agent
uv run python src/agents/react_agent.py

# Test API endpoints
uv run pytest tests/test_api.py
```

### Integration Testing
```bash
# Full system testing
./start-dev.sh  # Start all services
# Navigate to http://localhost:5173
# Test file operations + chat integration
```

### Agent Testing (v2.1)
```python
# Direct agent testing
from src.agents.react_agent import handle_message

# Test with various inputs
response = await handle_message("Scan my experiments", "test-session")
assert "experiments" in response.lower()
```

## 🚀 Development Phases

### ✅ Completed: v2.1 Simplified React Agent
- Replaced multi-agent system with single React agent
- Implemented natural language understanding (no keywords)
- Reduced codebase by 70%
- Uses proven LangGraph React pattern
- Easy tool extension with @tool decorator

### Current: v2.1 Optimization
- Fine-tuning agent responses
- Performance optimization
- Documentation updates
- Testing coverage

### Phase 2: Background Intelligence (v2.2)
- Background monitoring tools
- Proactive insight generation
- Pattern recognition across experiments
- Scheduled literature updates

### Phase 3: Advanced Features
- Multimodal analysis (images, plots)
- Predictive modeling capabilities
- Collaborative features
- Export and reporting tools

## 🔍 Deep Research Integration

### Current Implementation
```python
from src.tools.deep_research import run_deep_research

# Available as a tool in React agent
@tool
def research_literature(query: str) -> str:
    """Search scientific literature using Tavily API."""
    result = run_deep_research(query, max_loops=1)
    return format_research_results(result)
```

### Performance
- Quick response: 2-3 seconds (most queries)
- Deep research: 10-30 seconds (Tavily API)
- API cost: ~$0.01-0.03 per research query

## 📈 Success Metrics

### v2.1 Achieved Performance
- **Simple Queries**: 2-3 seconds (tool selection + execution)
- **Code Simplicity**: 70% reduction from v2.0
- **Natural Language**: Works in any language without configuration
- **Extensibility**: Add new tool in <5 minutes
- **Maintainability**: Single agent, clear tool separation

### v2.2 Goals
- **Proactive Value**: >50% insights surfaced without user asking
- **Background Processing**: Continuous experiment monitoring
- **Pattern Recognition**: Cross-experiment learning
- **Time Savings**: >30% reduction in debugging time

## 🔗 Important Resources

### Documentation
- **`/spec/`** - Technical specifications
- **`/spec/react-agent-api.md`** - React agent API documentation
- **`STATUS.md`** - Current system status and capabilities
- **`README.md`** - User-facing documentation

### External Tools
- **Tavily API** - Literature search and web research
- **LangFuse** - LLM observability and tracking (optional)
- **uv** - Python package management
- **Vite** - Frontend development server

## ⚡ Quick Commands

### Start Development Environment
```bash
# Terminal 1: Backend with React Agent
uv run uvicorn src.api.app:app --port 8002 --reload

# Terminal 2: Frontend  
cd frontend && npm run dev  # Opens http://localhost:5173

# Alternative: Use start script
./start-dev.sh
```

### Add New Capability (v2.1 Pattern)
```python
# 1. Open src/agents/react_agent.py
# 2. Add your tool:
@tool
def my_new_tool(param: str) -> str:
    """What this tool does (LLM reads this)."""
    return do_something(param)

# 3. Add to tools list
tools = [...existing_tools, my_new_tool]

# 4. That's it! The agent will use it when appropriate
```

### Common Development Tasks
```bash
# Add new dependencies
uv add <package-name>
cd frontend && npm install <package-name>

# Run tests
uv run pytest tests/ -v
uv run ruff check src/

# Test React agent directly
uv run python src/agents/react_agent.py
```

---

## 🎯 Development Mindset

**v2.1 Philosophy**: Simplicity is the ultimate sophistication  
**Core Pattern**: LangGraph React Agent with simple tools  
**Extension Model**: Just add @tool decorators, no complex orchestration

**Core Principle**: Natural language understanding should just work - in any language, without configuration, without keyword matching. The LLM is smart enough to understand intent.

**Success Metric**: Developers say "I can add a new feature in 5 minutes" - the architecture is so simple that extending it is trivial.

---

**Last Updated**: 2025-01-12  
**Version**: v2.1 operational with simplified React agent  
**Status**: Single agent with tools, 70% less code than v2.0  
**Next**: Background processing and proactive insights (v2.2)