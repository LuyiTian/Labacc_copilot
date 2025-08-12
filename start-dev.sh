#!/bin/bash

# Development startup script for LabAcc Copilot with React frontend

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || uv venv

# Set project root to user's project folder
export LABACC_PROJECT_ROOT="$(pwd)/data/alice_projects"

echo "Starting LabAcc Copilot Development Environment..."
echo "Project root: $LABACC_PROJECT_ROOT"

# Start Chainlit backend
echo "Starting Chainlit on http://localhost:8000..."
uv run chainlit run src/ui/app.py --host 0.0.0.0 --port 8000 &
CHAINLIT_PID=$!

# Start FastAPI REST API
echo "Starting REST API on http://localhost:8001..."
uv run uvicorn src.api.app:app --host 0.0.0.0 --port 8001 --reload &
API_PID=$!

# Start React frontend
echo "Starting frontend on http://localhost:5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo "Chainlit PID: $CHAINLIT_PID"
echo "API PID: $API_PID"
echo "Frontend PID: $FRONTEND_PID"

# Function to kill both processes on exit
cleanup() {
    echo "Stopping services..."
    kill $CHAINLIT_PID 2>/dev/null
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Wait for both processes
wait