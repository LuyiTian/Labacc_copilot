# LabAcc Copilot

**AI-powered autonomous laboratory assistant with multi-agent system for analyzing experimental data, diagnosing issues, and suggesting optimizations.**

## 🎯 Current Status: v2.0 - Multi-Agent Foundation

✅ **OPERATIONAL**: Multi-agent orchestration with smart routing  
✅ **NEW**: Deep research integration with Tavily API  
✅ **FAST**: Instant responses with intelligent depth selection  
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
# Terminal 1: Backend API + Multi-Agent System
uv run uvicorn src.api.app:app --port 8002 --reload

# Terminal 2: React Frontend
cd frontend && npm run dev

# Access the application at: http://localhost:5173
```

## 🤖 Multi-Agent System (v2.0)

### Agent Architecture
```
User Query → Smart Orchestrator
    ├─→ Quick Response Mode (instant, <1s)
    │     └─→ Pattern matching for common queries
    │
    └─→ Deep Processing Mode (when needed)
          ├─→ 🔍 Explorer Agent: Project scanning & mapping
          ├─→ 🧪 Analyzer Agent: Protocol & data analysis
          ├─→ 📚 Researcher Agent: Literature search via Tavily
          └─→ ⚡ Advisor Agent: Optimization suggestions
```

### Available Agents

#### 🔍 **Explorer Agent**
- Scans entire project structure
- Maps experiment relationships
- Identifies experiment types (PCR, gel, western blot, etc.)
- Tracks recent activity and success rates

#### 🧪 **Analyzer Agent**
- Analyzes experimental protocols
- Compares results across experiments
- Identifies patterns and anomalies
- Provides data interpretation

#### 📚 **Researcher Agent**
- Searches scientific literature via Tavily API
- Validates methods against published protocols
- Provides evidence-based recommendations
- Generates comprehensive research reports

#### ⚡ **Advisor Agent**
- Suggests protocol optimizations
- Designs next experiments
- Provides strategic planning
- Risk assessment and mitigation

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

### Three-Tier Response System

1. **Quick Mode** (default):
   - Pattern-matched responses
   - No LLM calls
   - Response time: <1 second
   - Perfect for common queries

2. **Smart Mode** (automatic):
   - Balances speed and depth
   - Selective LLM usage
   - Response time: 2-5 seconds
   - Activates for complex queries

3. **Deep Mode** (on request):
   - Full literature search
   - Comprehensive analysis
   - Response time: 10-30 seconds
   - Triggered by "research" keywords

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

### Current Capabilities (v2.0)
- ✅ **Multi-Agent Orchestration**: Intelligent query routing
- ✅ **Deep Research**: Tavily-powered literature search
- ✅ **Project Scanning**: Automatic experiment discovery
- ✅ **Smart Responses**: Context-aware analysis
- ✅ **File Management**: Integrated experiment browser
- ✅ **Unified Interface**: 40% files / 60% chat layout

### Coming Soon (v2.1)
- 🚧 **Background Processing**: Proactive experiment monitoring
- 🚧 **Pattern Recognition**: Cross-experiment analysis
- 🚧 **Predictive Modeling**: Success probability calculations
- 🚧 **Multimodal Analysis**: Advanced image processing

## 🔧 Development

### Project Structure
```
├── frontend/                 # React application
│   └── src/components/      # UI components
├── src/
│   ├── agents/              # Multi-agent system
│   │   ├── orchestrator.py # Agent coordination
│   │   ├── explorer.py     # Project scanning
│   │   ├── analyzer.py     # Data analysis
│   │   ├── researcher.py   # Literature search
│   │   └── advisor.py      # Optimization
│   ├── api/                 # FastAPI endpoints
│   ├── tools/               # Utility tools
│   │   └── deep_research/  # Tavily integration
│   └── components/          # Core components
├── data/
│   └── alice_projects/      # Experiment storage
└── CLAUDE.md               # Development guidelines
```

### Running Tests
```bash
# Test multi-agent orchestrator
uv run python test_agents.py

# Test explorer agent
uv run python test_explorer.py

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

- **Quick Response**: <1 second (pattern matching)
- **Smart Response**: 2-5 seconds (selective LLM)
- **Deep Research**: 10-30 seconds (full Tavily search)
- **Project Scan**: <1 second for 100 experiments
- **File Operations**: <100ms response time

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

**Version**: 2.0.0  
**Last Updated**: 2025-01-08  
**Status**: Multi-agent system operational