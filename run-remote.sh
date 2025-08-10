#!/bin/bash
# Run LabAcc Copilot on remote server for testing

echo "Starting LabAcc Copilot on remote server..."

# Install dependencies if needed
echo "Checking dependencies..."
uv pip install -r requirements.txt

# Set test project root
export LABACC_PROJECT_ROOT="$(pwd)/data/alice_projects"

# Check API keys
if [ -z "$TAVILY_API_KEY" ]; then
    echo "Warning: TAVILY_API_KEY not set. Deep research features won't work."
    echo "Set it in your .bashrc: export TAVILY_API_KEY='your-key'"
fi

# Create example data if not exists
if [ ! -f "data/alice_projects/exp_001_pcr_test/data.csv" ]; then
    echo "Creating example experiment data..."
    mkdir -p data/alice_projects/exp_001_pcr_test
    cat > data/alice_projects/exp_001_pcr_test/README.md << 'EOF'
# PCR Optimization Experiment
**Status**: In Progress
**Issue**: Low yield with GC-rich template (68% GC)

## Results
See data.csv for temperature optimization results.
EOF

    cat > data/alice_projects/exp_001_pcr_test/data.csv << 'EOF'
Temperature,Yield_ng/ul,Specificity,Notes
55,12.3,Low,Multiple bands
58,18.5,Medium,Some non-specific
60,22.1,High,Clean band
62,15.2,High,Weak band
65,5.3,High,Very weak
EOF
fi

# Start Chainlit on all interfaces
echo "======================================"
echo "Starting Chainlit..."
echo "Access URL: http://36.163.20.6:8000"
echo "Project root: $LABACC_PROJECT_ROOT"
echo "Press Ctrl+C to stop"
echo "======================================"

uv run chainlit run src/ui/app.py --host 0.0.0.0 --port 8000