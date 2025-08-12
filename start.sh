#!/bin/bash

# Activate virtual environment and start UI
source .venv/bin/activate 2>/dev/null || uv venv

# Set project root to user's project folder
export LABACC_PROJECT_ROOT="$(pwd)/data/alice_projects"

# Start Chainlit
uv run chainlit run src/ui/app.py --host 0.0.0.0 --port 8000