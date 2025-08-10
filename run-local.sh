#!/bin/bash
# Quick local testing script without Docker

echo "Starting LabAcc Copilot locally for testing..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Set a test project root
export LABACC_PROJECT_ROOT="$(pwd)/data/alice_projects"

# Check if API keys are set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "Warning: TAVILY_API_KEY not set. Deep research features won't work."
fi

# Start Chainlit
echo "Starting Chainlit on http://localhost:8000"
echo "Project root: $LABACC_PROJECT_ROOT"
echo "Press Ctrl+C to stop..."

uv run chainlit run src/ui/app.py --port 8000