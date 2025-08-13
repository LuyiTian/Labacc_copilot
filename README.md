# LabAcc Copilot

**AI-powered autonomous laboratory assistant using LangGraph React Agent for analyzing experimental data, diagnosing issues, and suggesting optimizations.**

## 🎯 Current Status: v2.1 - Simplified React Agent

✅ **SIMPLIFIED**: Single React agent with tools (LangGraph)  
✅ **NATURAL**: LLM understands intent in any language  
✅ **MAINTAINABLE**: 70% less code, easier to extend  
✅ **PROVEN**: Uses LangGraph's battle-tested React pattern  
🚧 **NEXT**: Background processing and proactive insights

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv (Python package manager)

### Installation
```bash
# Clone repository
git clone <repo-url>
cd Labacc_copilot

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && npm install && cd ..

# Set API keys (required for deep research)
export TAVILY_API_KEY="your-tavily-key"      # For literature search
export LANGFUSE_SECRET_KEY="your-langfuse-key"  # Optional: LLM tracking
```

### Start Development Environment
```bash
# Terminal 1: Backend API + React Agent
uv run uvicorn src.api.app:app --port 8002 --reload

# Terminal 2: React Frontend
cd frontend && npm run dev

# Access the application at: http://localhost:5173
```

## 🤖 React Agent System (v2.1)

### Simple Architecture
```
User Query → LangGraph React Agent → Appropriate Tool
                     │
                     ├─→ 📁 scan_project: List all experiments
                     ├─→ 🔬 analyze_experiment: Analyze specific folder
                     ├─→ 📚 research_literature: Search papers (Tavily)
                     ├─→ ⚡ optimize_protocol: Optimization suggestions
                     └─→ 💾 manage_files: File operations
```

### How It Works

**No Manual Intent Detection!** The LangGraph React agent uses the LLM's natural language understanding to:
1. Understand user intent in any language
2. Decide which tool(s) to use
3. Execute the appropriate tool
4. Return a natural response

### Available Tools

#### 📁 **scan_project**
- Lists all experiments in the project
- Shows file counts and creation dates
- Provides experiment summaries

#### 🔬 **analyze_experiment**
- Analyzes specific experiment folders
- Reviews protocols and data files
- Provides insights based on experiment type

#### 📚 **research_literature**
- Searches scientific literature via Tavily API
- Quick or deep research modes
- Returns relevant papers and methods

#### ⚡ **optimize_protocol**
- Provides optimization suggestions
- Troubleshoots specific issues
- Offers protocol improvements

#### 💾 **manage_files**
- Creates experiment folders
- Organizes files
- Lists folder contents

### Example Commands

**Quick Responses (instant):**
```
"hi"                        → Welcome message with capabilities
"scan my project"           → Overview of all experiments
"optimize my protocol"      → Strategic suggestions
"what should I do next?"    → Next steps guidance
```

**Deep Research (10-30 seconds):**
```
"deep research PCR optimization"     → Literature search + reports
"research GC-rich template methods"  → Scientific papers analysis
"literature on gel electrophoresis"  → Method validation
```

## 🏗️ System Architecture

### Simplified Response Flow

1. **User sends message** in any language
2. **React agent understands** intent naturally
3. **Agent selects tool(s)** automatically
4. **Tool executes** and returns results
5. **Agent formats response** naturally

**Response Times:**
- Simple queries: 2-3 seconds
- Analysis tasks: 3-5 seconds
- Literature search: 10-30 seconds (Tavily API)

### File-Based Memory System
```
data/alice_projects/
├── .labacc/                    # Copilot metadata
│   ├── project_knowledge.md   # Cross-experiment insights
│   └── agent_state.json       # Persistent agent memory
├── exp_001_pcr_optimization/
│   ├── README.md              # Experiment documentation
│   └── [data files...]
└── [more experiments...]
```

## 📊 Key Features

### Current Capabilities (v2.1)
- ✅ **React Agent**: Single agent with multiple tools
- ✅ **Natural Language**: Works in any language
- ✅ **Deep Research**: Tavily-powered literature search
- ✅ **Project Scanning**: Automatic experiment discovery
- ✅ **Smart Tools**: Context-aware analysis
- ✅ **File Management**: Integrated experiment browser
- ✅ **Simple & Maintainable**: 70% less code than v2.0

### Coming Soon (v2.2)
- 🚧 **Background Processing**: Proactive experiment monitoring
- 🚧 **Pattern Recognition**: Cross-experiment analysis
- 🚧 **Predictive Modeling**: Success probability calculations
- 🚧 **Multimodal Analysis**: Advanced image processing
- 🚧 **More Tools**: Easy to add new capabilities

## 🔧 Development

### Project Structure
```
├── frontend/                 # React application
│   └── src/components/      # UI components
├── src/
│   ├── agents/              
│   │   └── react_agent.py  # Single React agent with tools
│   ├── api/                 # FastAPI endpoints
│   │   ├── app.py          # Main API
│   │   └── react_bridge.py # Bridge to React agent
│   ├── tools/               # Utility tools
│   │   └── deep_research/  # Tavily integration
│   └── components/          # Core components
├── data/
│   └── alice_projects/      # Experiment storage
└── CLAUDE.md               # Development guidelines
```

### Running Tests
```bash
# Test React agent
uv run python src/agents/react_agent.py

# Test with API server
uv run uvicorn src.api.app:app --port 8002 --reload
# Then: curl -X POST http://localhost:8002/api/chat/message ...

# Test deep research (requires Tavily API key)
uv run python test_deep_research.py
```

### Configuration

**Environment Variables:**
```bash
# Required for deep research
export TAVILY_API_KEY="tvly-xxxxx"

# Optional LLM configuration
export LANGFUSE_SECRET_KEY="sk-lf-xxxxx"
export LANGFUSE_PUBLIC_KEY="pk-lf-xxxxx"

# Custom project root (default: data/alice_projects)
export LABACC_PROJECT_ROOT="/path/to/projects"
```

**Deep Research Settings** (reduced for testing):
- Query fanout: 3 queries (reduced from 10)
- Research loops: 1 (reduced from 2)
- Timeout: 30 seconds
- Cost: ~$0.01-0.03 per research query

## 📈 Performance Metrics

- **Simple Queries**: 2-3 seconds (tool selection + execution)
- **Analysis Tasks**: 3-5 seconds (data processing)
- **Deep Research**: 10-30 seconds (Tavily API)
- **Project Scan**: <2 seconds for 100 experiments
- **File Operations**: <1 second

## 🔒 Security & Privacy

- All data stored locally in `data/alice_projects/`
- No automatic cloud uploads
- API keys stored as environment variables
- File path validation to prevent traversal
- Human-readable file-based memory (no black box embeddings)

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and architecture decisions.

## 📝 License

[License information]

## 🔗 Resources

- **Documentation**: See `/dev_plan/` for detailed plans
- **Status**: Check `STATUS.md` for current capabilities
- **Vision**: Read `dev_plan/v2_copilot_vision.md` for roadmap

---

## 🎯 Adding New Features (Super Easy!)

With v2.1's simplified architecture, adding new features is trivial:

```python
# 1. Open src/agents/react_agent.py
# 2. Add your tool:
from langchain_core.tools import tool

@tool
def your_new_tool(param: str) -> str:
    """Tool description - LLM reads this to know when to use it."""
    # Implementation
    return "Result"

# 3. Add to tools list
tools = [...existing_tools, your_new_tool]

# 4. That's it! The agent will use it when appropriate
```

---

**Version**: 2.1.0  
**Last Updated**: 2025-01-12  
**Status**: Simplified React agent operational