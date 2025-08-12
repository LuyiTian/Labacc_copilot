# LabAcc Copilot

**AI-powered laboratory assistant for wet-lab biologists to analyze experimental data, diagnose issues, and suggest optimizations.**

## 🎯 Current Status: v1.1 - Unified Interface

✅ **OPERATIONAL**: Fully integrated React + AI chat interface  
🚧 **NEXT**: Evolving toward autonomous laboratory copilot (v2.0)

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

# Set API keys (optional for basic use)
export TAVILY_API_KEY="your-tavily-key"
export LANGFUSE_SECRET_KEY="your-langfuse-key"
```

### Start Development Environment
```bash
# Method 1: Start both services
npm run dev                 # React frontend (port 5173)
uv run uvicorn src.api.app:app --port 8002 --reload  # API + Chat bridge

# Method 2: Use the start script
./start-dev.sh  # Starts all services automatically
```

**Access the application**: http://localhost:5173

## 🏗️ Architecture

### Current System (v1.1)
```
┌─────────────────────────────────────────────────────────┐
│              React Frontend (5173)                     │
│  ┌──────────────────┐  ┌────────────────────────────┐  │
│  │  File Manager    │  │    AI Chat Interface       │  │
│  │     (40%)        │  │        (60%)               │  │
│  └──────────────────┘  └────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│            FastAPI Bridge (8002)                       │
│  File Operations + Chat API + LangGraph Integration    │
├─────────────────────────────────────────────────────────┤
│                File-Based Memory                       │
│         data/alice_projects/ (Project Root)            │
└─────────────────────────────────────────────────────────┘
```

### Key Features
- **🎨 Unified Interface**: File management + AI chat in single application
- **🤖 Context-Aware AI**: Chat knows your current folder and selected files
- **📁 Smart File Management**: Intelligent experiment organization
- **💾 File-Based Memory**: README files as structured context (no vector DB)
- **🔍 Deep Research Integration**: Tavily-powered literature search
- **📊 Multi-modal Analysis**: CSV data and image analysis capabilities
- **⚡ Performance Optimized**: 2-3 second response times

## 📖 User Guide

### Basic Usage
1. **File Management**: Browse experiments, upload data, organize files
2. **Context Selection**: Select files/folders to provide AI context
3. **Natural Conversation**: Ask questions about your experiments
4. **Smart Organization**: AI helps organize and name experiments

### Example Workflows
```
User: [selects PCR data files]
User: "Why is my yield so low?"
AI: "I notice your annealing temp in exp_005 was 65°C vs 58°C in successful runs..."

User: "Create a new cloning experiment folder"
AI: [creates exp_003_cloning_2025-08-12 with README template]

User: [uploads gel image]  
User: "Analyze this gel"
AI: "I can see bands at ~200bp and ~500bp. The ladder suggests..."
```

## 🔧 Development

### Project Structure
```
├── frontend/                 # React application
│   ├── src/components/ChatPanel.jsx  # Integrated chat
│   └── src/App.jsx          # Main UI with file manager
├── src/
│   ├── api/                 # FastAPI backend
│   │   ├── file_routes.py   # File operations
│   │   └── react_bridge.py  # Chat integration
│   ├── graph/               # LangGraph agents
│   ├── components/          # AI components
│   └── tools/              # Deep research, file tools
├── data/alice_projects/     # Project data (gitignored)
└── spec/                   # Technical specifications
```

### Configuration
- **Project Root**: `data/alice_projects/` (customizable via LABACC_PROJECT_ROOT)
- **LLM Models**: Configured in `src/config/llm_config.json`
- **API Keys**: Set via environment variables (see CLAUDE.md)

### Testing
```bash
# Backend tests
uv run pytest tests/

# Frontend development
cd frontend && npm run dev

# Full system test
./start-dev.sh  # Then visit http://localhost:5173
```

## 🔮 Vision: v2.0 - Autonomous Laboratory Copilot

**Current v1.1**: Reactive chat assistant  
**Future v2.0**: Proactive research partner

### Planned Capabilities
- **🧠 Autonomous Analysis**: Scans all experiments, builds project knowledge
- **📈 Pattern Recognition**: Identifies what works across experiments
- **🔬 Predictive Insights**: Suggests likely outcomes, warns of issues
- **📚 Literature Integration**: Auto-searches relevant papers
- **🎯 Experiment Design**: Proposes next experiments based on results
- **🔄 Continuous Learning**: Gets smarter from your lab's data

See `dev_plan/v2_copilot_vision.md` for detailed roadmap.

## 📚 Documentation

- **`/spec/`**: Technical specifications
- **`/dev_plan/`**: Development roadmaps and vision
- **`CLAUDE.md`**: Development guidelines and architecture notes

## 🤝 Contributing

This is a research prototype. See development guidelines in `CLAUDE.md`.

## 📄 License

[License information]

---

**Status**: v1.1 Operational | **Next**: v2.0 Autonomous Copilot  
**Architecture**: File-based memory + LangGraph agents + React UI  
**Focus**: Wet-lab biology experiment analysis and optimization