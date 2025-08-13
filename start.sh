#!/bin/bash

# Activate virtual environment and start UI
source .venv/bin/activate 2>/dev/null || uv venv

# Set project root to user's project folder
export LABACC_PROJECT_ROOT="$(pwd)/data/alice_projects"

# Start FastAPI backend with React agent
uv run uvicorn src.api.app:app --host 0.0.0.0 --port 8002