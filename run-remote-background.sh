#!/bin/bash
# Run LabAcc Copilot in background with nohup

echo "Starting LabAcc Copilot in background..."

# Install dependencies
uv pip install -r requirements.txt

# Set project root
export LABACC_PROJECT_ROOT="$(pwd)/data/alice_projects"

# Kill any existing process on port 8000
echo "Checking for existing processes on port 8000..."
lsof -ti:8000 | xargs -r kill -9 2>/dev/null

# Start in background
nohup uv run chainlit run src/ui/app.py --host 0.0.0.0 --port 8000 > labacc.log 2>&1 &

echo "Started with PID: $!"
echo "Logs: tail -f labacc.log"
echo ""
echo "======================================"
echo "Access URL: http://36.163.20.6:8000"
echo "======================================"
echo ""
echo "To stop: kill $(lsof -ti:8000)"