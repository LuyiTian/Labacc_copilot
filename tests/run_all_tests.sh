#!/bin/bash
# Run all tests for LabAcc Copilot

echo "🧪 LABACC COPILOT TEST RUNNER"
echo "=============================="
echo ""

# Check if server is running
echo "📍 Checking if server is running..."
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ Server is running"
else
    echo "⚠️  Server not running. Starting it now..."
    echo "   Run this in another terminal:"
    echo "   uv run uvicorn src.api.app:app --port 8002 --reload"
    echo ""
    echo "Starting server in background..."
    uv run uvicorn src.api.app:app --port 8002 --reload &
    SERVER_PID=$!
    sleep 5
fi

echo ""
echo "📍 Running Comprehensive Integration Tests..."
echo "----------------------------------------------"
uv run python tests/test_comprehensive_integration.py

echo ""
echo "📍 Running Simple API Tests..."
echo "----------------------------------------------"
uv run python tests/test_api_simple.py

echo ""
echo "📍 Running Unit Tests..."
echo "----------------------------------------------"
uv run pytest tests/unit/ -v --tb=short

# Kill server if we started it
if [ ! -z "$SERVER_PID" ]; then
    echo ""
    echo "Stopping test server..."
    kill $SERVER_PID 2>/dev/null
fi

echo ""
echo "✅ All tests completed!"