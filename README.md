# LabAcc Copilot Project

**Status**: Development
**Started**: 2025-01-08
**Last Updated**: 2025-01-08

## Project Overview

LabAcc Copilot is an AI-powered assistant designed specifically for wet-lab biologists to analyze experimental data, diagnose issues, and suggest optimizations. This project provides intelligent troubleshooting and experimental design recommendations through a chat-based interface.

## Current Focus

- Setting up core infrastructure and file-based memory system
- Integrating deep research capabilities for literature search
- Developing multi-modal analysis for experimental data and images
- Creating structured decision-making framework for experiment optimization

## Key Features

- **Multi-modal Analysis**: Handles CSV data files and experimental images (gels, plots, etc.)
- **File-based Memory**: Uses README files for context instead of complex vector databases
- **Deep Research**: Integrated literature search and synthesis capabilities
- **Decision Cards**: Structured recommendations with evidence citations
- **Experiment Tracking**: Organized memory system for experimental progress and insights

## Active Experiments

*No experiments currently tracked. When experiments are added to `/data/experiments/`, they will be listed here with status summaries.*

## System Architecture

- **Agents**: LangGraph-based multi-agent system (Planner → Retriever → Analyst → Critic → Writer)
- **Memory**: File-based context system using structured README files
- **Deep Research**: Tavily-powered web search with iterative refinement
- **UI**: Chainlit-based chat interface with file upload support
- **Storage**: SQLite for conversation persistence, file system for data organization

## Directory Structure

- [`src/`](./src/) - Source code and modules
- [`data/experiments/`](./data/experiments/) - Individual experiment folders with context
- [`data/ref/`](./data/ref/) - Reference documents and protocols  
- [`data/history/`](./data/history/) - AI decision history and research reports
- [`config/`](./config/) - Configuration files (see `.env.example`)

## Setup & Configuration

1. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (Tavily required, LLM provider of choice)
   ```

2. **Dependencies**:
   ```bash
   # Option A: pip
   pip install -r requirements.txt

   # Option B: uv (recommended for fast, reproducible dev)
   # Install uv: https://github.com/astral-sh/uv
   uv venv
   uv pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   chainlit run src/ui/app.py
   ```

4. **Deep Research (as a function or LangChain Tool)**:
   - Programmatic API:
     ```python
     from src.tools.deep_research import run_deep_research
     result = run_deep_research("How to optimize PCR annealing temperature for GC-rich templates?", max_research_loops=3)
     print(result["final_text"])  # Markdown report
     ```
   - As a tool in ReAct agents:
     ```python
     from src.tools.deep_research.tools import deep_research_tool
     tools = [deep_research_tool]
     ```
   - Configure required key:
     - Set `TAVILY_API_KEY` in `.env`. LLM providers are optional; if configured, they will be used via `src/components/llm.py`.

5. **LLM Config Overrides**:
   - You can override model mappings and assignments with `src/config/llm_config.json` (optional). This mirrors successful patterns from AutoCell.

## API Keys Required

- **Tavily**: For web search and literature research (required)
- **LLM Provider**: Optional, choose one:
  - OpenAI (GPT-4o recommended)
  - SiliconFlow (Qwen models)
  - Anthropic Claude
  - Google Gemini

See `.env.example` for configuration details.

## Resources & References

- [CLAUDE.md](./CLAUDE.md) - Complete technical specification and implementation guide
- [Deep Research Tool](./src/tools/deep_research/) - Integrated literature search system
- Configuration examples and templates in project structure

## Development Status

### Completed
- ✅ Project specification and architecture design
- ✅ Deep research tool integration with secure configuration
- ✅ File-based memory system design and structure
- ✅ Environment configuration and security improvements

### In Progress
- 🔄 Core agent system implementation
- 🔄 Multi-modal data processing pipeline
- 🔄 Chainlit UI development

### Planned
- ⏳ DecisionCard generation and persistence
- ⏳ Experiment tracking and analysis features
- ⏳ Integration testing and optimization

## Notes

This project prioritizes simplicity and maintainability over complexity. The file-based memory system allows for transparent, editable context that can be version-controlled and easily understood by both users and AI agents.

For technical implementation details, see [CLAUDE.md](./CLAUDE.md).