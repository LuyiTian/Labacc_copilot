#!/bin/bash
"""
Multi-User Agent Evaluation Runner

Convenient shell script for running agent evaluations.
Automatically sets up the environment and runs the evaluation CLI.

Usage:
    ./tests/run_evaluation.sh [options]
    
Examples:
    # Quick evaluation with default settings
    ./tests/run_evaluation.sh
    
    # Run compatibility mode only
    ./tests/run_evaluation.sh --compatibility
    
    # Run with more parallel workers
    ./tests/run_evaluation.sh --max-parallel 5
    
    # Run specific categories
    ./tests/run_evaluation.sh --categories "project_isolation,session_management"
    
    # Generate and save multi-user test suite
    ./tests/run_evaluation.sh --generate-multiuser --save-tests tests/test_cases/multiuser_tests.json
"""

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 LabAcc Copilot Multi-User Agent Evaluation${NC}"
echo -e "${BLUE}===============================================${NC}"

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/src/agents/react_agent.py" ]; then
    echo -e "${RED}❌ Error: Not in LabAcc Copilot project directory${NC}"
    echo "Please run this script from the project root or tests directory"
    exit 1
fi

# Set up environment
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"
cd "$PROJECT_ROOT"

# Check Python dependencies
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️ Warning: 'uv' not found, falling back to python${NC}"
    PYTHON_CMD="python"
else
    PYTHON_CMD="uv run python"
fi

# Default arguments
DEFAULT_ARGS="--mixed"

# Parse arguments to determine what type of run this is
if [[ "$*" == *"--dry-run"* ]]; then
    echo -e "${YELLOW}🔍 Running in DRY RUN mode${NC}"
elif [[ "$*" == *"--compatibility"* ]]; then
    echo -e "${YELLOW}🔄 Running in COMPATIBILITY mode${NC}"
elif [[ "$*" == *"--native"* ]]; then
    echo -e "${YELLOW}🏗️ Running in NATIVE mode${NC}"
else
    echo -e "${YELLOW}🔀 Running in MIXED mode (default)${NC}"
fi

# Set TEST_MODE environment variable for test data access
export TEST_MODE="true"

# Run the evaluation
echo -e "${BLUE}Starting evaluation...${NC}"
echo ""

if $PYTHON_CMD -m tests.agent_evaluation.run_evaluation $DEFAULT_ARGS "$@"; then
    echo ""
    echo -e "${GREEN}✅ Evaluation completed successfully!${NC}"
    exit 0
else
    exit_code=$?
    echo ""
    if [ $exit_code -eq 1 ]; then
        echo -e "${RED}❌ Evaluation failed or agent needs improvement${NC}"
    else
        echo -e "${RED}❌ Evaluation encountered an error (exit code: $exit_code)${NC}"
    fi
    exit $exit_code
fi