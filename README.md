# LabAcc Copilot

AI laboratory assistant for experimental data analysis and optimization.

## 🚀 Quick Start

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repo-url>
cd Labacc_copilot
uv sync
cd frontend && npm install && cd ..

# Set API keys
export TAVILY_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"

# Start
./start-dev.sh
# Open http://localhost:5173
```

## 💡 Features

- **Multi-language Support**: Works in English, Chinese, Spanish, etc.
- **Memory System**: Each experiment has persistent README memory
- **Real-time Tool Visibility**: See which tools are running live
- **Literature Search**: Integrated Tavily API for research papers
- **Smart Context**: Pre-loads relevant data to reduce tool calls

## 📝 Example Usage

```
"列出我的实验"               → Lists all experiments
"Analyze exp_001 data"      → Analyzes specific experiment
"PCR optimization tips"     → Provides optimization suggestions
"Research CRISPR methods"   → Searches scientific literature
"创建新实验文件夹"            → Creates new experiment folder
```

## ⚙️ Configuration

```bash
export TAVILY_API_KEY="tvly-..."     # Literature search
export OPENROUTER_API_KEY="sk-..."   # LLM provider
```
## 🔧 Troubleshooting

- **Port already in use**: Kill existing processes or use different ports
- **API key errors**: Ensure environment variables are set correctly
- **Frontend not loading**: Check if backend is running on port 8002
- **Tool not found**: Restart the backend after code changes

## 📚 Documentation

- `STATUS.md` - Current system status and changelog
- `CLAUDE.md` - Development guidelines (for developers)
- `/spec/` - Technical specifications
- `/dev_plan/` - Development roadmap

## 📄 License

MIT License - See LICENSE file for details

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