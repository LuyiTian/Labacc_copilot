# LabAcc Copilot - Development Guidelines

AI-powered autonomous laboratory assistant for wet-lab biologists to analyze experimental data, diagnose issues, and suggest optimizations.

No Fallback, this is a project in early development stage so DO NOT consider aspect in real projection stage, such as fallback, security, high parallel etc. just quick dev and quick fail and move on fast.

## 📍 Current Status: v1.1 - Unified Interface

**✅ OPERATIONAL**: Fully integrated React + AI chat system  
**🚧 NEXT**: Developing v2.0 autonomous copilot capabilities

## 🏗️ Architecture Overview

### Current v1.1 System
```
React Frontend (5173) ←→ FastAPI Bridge (8002) ←→ LangGraph Agents
┌─────────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ File Manager + Chat │ → │ API + Chat Bridge│ → │ AI Processing   │
│ Context Sharing     │   │ Session Mgmt     │   │ Agent Workflows │
│ 40% Files / 60% Chat│   │ REST + JSON      │   │ File-based Memory│
└─────────────────────┘   └──────────────────┘   └─────────────────┘
```

### v2.0 Vision: Multi-Agent Copilot
```
┌─────────────────────────────────────────────────────────┐
│                 Orchestrator Agent                      │
│           (Coordinates all specialized agents)          │
├─────────────────────────────────────────────────────────┤
│  Explorer    │  Analyzer     │  Researcher  │  Advisor  │
│  Agent       │  Agent        │  Agent       │  Agent    │
│              │               │              │           │
│ - Scans all  │ - Compares    │ - Literature │ - Suggests│
│   experiments│   protocols   │   search     │   optimiz │
│ - Maps       │ - Identifies  │ - Validates  │ - Designs │
│   project    │   patterns    │   methods    │   experiments│
│ - Monitors   │ - Predicts    │ - Updates    │ - Plans   │
│   changes    │   outcomes    │   knowledge  │   research│
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

**1. Read Specifications First**
- Check `/spec/` directory for component specifications
- Update specs when making architectural changes
- Write specs for new features before implementation

**2. File-Based Memory Priority**
- Use README files as primary context source
- Store insights in human-readable markdown
- Avoid vector databases and embeddings
- Make AI reasoning transparent and auditable

**3. Multi-Agent Development (v2.0+)**
- Design specialized agents with clear responsibilities
- Use LangGraph for agent orchestration
- Implement persistent agent state management
- Enable background processing capabilities

## 🛠️ Technical Implementation

### Current Stack (v1.1)
```python
# Frontend: React + Vite
# Backend: FastAPI + LangGraph
# AI: Qwen models (8B for parsing, 30B for analysis)
# Memory: File-based with README context
# Integration: REST API with chat bridge
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
- `src/api/react_bridge.py` - Chat integration bridge
- `frontend/src/App.jsx` - Main React UI
- `frontend/src/components/ChatPanel.jsx` - Integrated chat

**AI Components:**
- `src/components/llm.py` - LLM configuration and models
- `src/graph/` - LangGraph agent implementation
- `src/tools/deep_research/` - Literature search integration
- `src/models/decision_card.py` - Structured response models

**File Intelligence:**
- `src/components/file_intent_parser.py` - Natural language file operations
- `src/components/smart_folder_manager.py` - Intelligent experiment organization
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
# Use role-based model assignments in llm.py
parser_llm = get_llm_instance("siliconflow-qwen-8b")    # Fast parsing
analysis_llm = get_llm_instance("siliconflow-qwen-30b") # Deep analysis
```

### 3. File-Based Memory Priority
```python
# Always prefer README context over vector search
readme_context = read_experiment_readme(experiment_path)
# Use structured markdown for insights
insights = generate_markdown_insights(analysis_results)
```

### 4. Multi-Agent Coordination (v2.0)
```python
# Agent orchestration pattern
from langgraph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

# Specialized agent roles
class AgentRoles:
    EXPLORER = "explorer"    # Project scanning
    ANALYZER = "analyzer"    # Pattern recognition  
    RESEARCHER = "researcher" # Literature search
    ADVISOR = "advisor"      # Strategic planning
```

### 5. Background Processing (v2.0)
```python
# Async background analysis
import asyncio
from watchdog.observers import Observer

# File monitoring for proactive analysis
async def monitor_project_changes():
    # Detect new experiments, data uploads
    # Trigger appropriate agent workflows
```

## 🔒 Security and Safety

### Data Protection
- Validate all file paths to prevent directory traversal
- Sanitize user inputs and file uploads
- Keep sensitive data within project boundaries
- No hardcoded API keys or credentials

### Human-in-the-Loop (v2.0)
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
# Test AI components
uv run pytest tests/test_llm.py
uv run pytest tests/test_file_analyzer.py

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

### Agent Testing (v2.0)
```python
# Mock agent interactions
@pytest.fixture
def mock_agent_state():
    return AgentState(
        project_map={},
        insights=[],
        active_tasks=[]
    )

def test_explorer_agent_scan(mock_agent_state):
    # Test project scanning capabilities
    pass
```

## 🚀 Development Phases

### Current: v1.1 Maintenance
- Bug fixes and performance improvements
- UI/UX enhancements
- Documentation updates
- Testing and reliability improvements

### Phase 1: Multi-Agent Foundation (v2.0)
- Implement multi-agent orchestration
- Add persistent agent state management
- Create background processing system
- Build project scanning capabilities

### Phase 2: Intelligence Layer
- Pattern recognition across experiments
- Proactive insight generation
- Literature integration enhancement
- Predictive modeling capabilities

### Phase 3: Autonomous Operation
- Full proactive operation
- Advanced dashboard and notifications
- Multimodal analysis (images, plots)
- Autonomous experimental design

## 🔍 Deep Research Integration

### Current Implementation
```python
from src.tools.deep_research import run_deep_research

# Manual literature search
result = run_deep_research(
    query="PCR optimization for GC-rich templates", 
    max_loops=3
)
# Reports saved to data/history/
```

### v2.0 Enhancement
```python
# Automatic literature integration
class ResearcherAgent:
    async def auto_research_problem(self, problem_description):
        # Triggered by failed experiments or novel challenges
        # Searches literature, validates methods
        # Updates project knowledge base
        # Suggests evidence-based solutions
```

## 📈 Success Metrics

### v1.1 Performance
- Response time: <3 seconds (optimized from 60s)
- User satisfaction: Unified interface experience
- Reliability: Stable file operations and chat

### v2.0 Goals
- **Proactive Value**: >50% insights surfaced without user asking
- **Accuracy**: >80% of suggestions improve outcomes
- **Time Savings**: >30% reduction in debugging time
- **Coverage**: AI analysis available for >90% of experiments

## 🔗 Important Resources

### Documentation
- **`/spec/`** - Technical specifications
- **`dev_plan/v2_copilot_vision.md`** - Comprehensive v2.0 roadmap
- **`STATUS.md`** - Current system status and capabilities

### External Tools
- **Tavily API** - Literature search and web research
- **LangFuse** - LLM observability and tracking
- **uv** - Python package management
- **Vite** - Frontend development server

## ⚡ Quick Commands

### Start Development Environment
```bash
# Terminal 1: Backend
uv run uvicorn src.api.app:app --port 8002 --reload

# Terminal 2: Frontend  
npm run dev  # Opens http://localhost:5173

# Alternative: Use start script
./start-dev.sh
```

### Common Development Tasks
```bash
# Add new dependencies
uv add <package-name>
cd frontend && npm install <package-name>

# Run tests
uv run pytest tests/ -v
uv run ruff check src/

# Update documentation
# Edit relevant .md files
# Update version in STATUS.md
```

---

## 🎯 Development Mindset

**v1.1 Focus**: Maintain stability, improve user experience  
**v2.0 Vision**: Build autonomous research partner, not just chat assistant

**Core Principle**: Like Claude Code proactively analyzes codebases, LabAcc Copilot should autonomously analyze experimental projects and surface insights that researchers didn't know to look for.

**Success Metric**: Research teams say "I can't imagine doing experiments without the copilot" - it becomes an indispensable research partner.

---

**Last Updated**: 2025-08-12  
**Version**: v1.1 operational, v2.0 in planning  
**Status**: Ready for autonomous copilot development