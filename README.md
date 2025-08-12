# LabAcc Copilot

AI assistant for wet-lab biology experiments using LangGraph agents.

## Setup

```bash
# Install dependencies
uv venv
uv pip install -r requirements.txt

# Set API key (add to ~/.bashrc)
export TAVILY_API_KEY="your-key"

# Start
./start.sh
```

Access at: http://localhost:8000 (or your server IP)

## Features

- Multi-modal analysis (CSV/images)
- File-based memory (README context)
- Deep research (Tavily search)
- Decision cards with citations
- Visual file manager with action buttons
- File management commands in chat

## Architecture

```
Planner → Retriever → Analyst → Critic → Writer
```

## File Management

### Visual File Browser
Click action buttons to browse folders and preview files. The file manager shows:
- 📁 Folders (click to browse)
- 📊 Data files (CSV/Excel)
- 🖼️ Images
- 📝 Documents
- 🔙 Back button to navigate up

### Chat Commands
You can also use text commands:
- `/pwd` - Show project root
- `/ls [dir]` - List directory
- `/cat <file>` - Preview file
- `/save [dir]` - Save uploaded files
- `/rm <path>` - Delete file/folder
- `/mv <src> <dst>` - Move/rename
- `/help` - Show commands

## Development

```bash
# Run tests
uv run pytest tests/

# Check code
uv run ruff check src/
```

## Project Structure

- `src/` - Source code
- `data/experiments/` - Experiment data
- `data/ref/` - Reference documents
- `data/history/` - Decision history