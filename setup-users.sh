#!/bin/bash
# Setup script for creating users and their project directories

echo "Setting up LabAcc Copilot for multiple users..."

# Install htpasswd if not available
if ! command -v htpasswd &> /dev/null; then
    echo "Installing apache2-utils for htpasswd..."
    sudo apt-get update && sudo apt-get install -y apache2-utils
fi

# Create .htpasswd file for nginx authentication
echo "Creating user accounts..."
touch .htpasswd

# Add users (you'll be prompted for passwords)
echo "Adding user 'alice' (you'll be prompted for password):"
htpasswd -B .htpasswd alice

echo "Adding user 'bob' (you'll be prompted for password):"
htpasswd -B .htpasswd bob

# Create example project directories
echo "Creating example project directories..."
mkdir -p data/alice_projects/exp_001_pcr_test
mkdir -p data/bob_projects/exp_001_western_blot

# Create example experiment files
cat > data/alice_projects/exp_001_pcr_test/README.md << 'EOF'
# Experiment: PCR Optimization Test
**Status**: In Progress
**Date Started**: 2025-01-10

## Objective
Optimize PCR conditions for amplifying GC-rich gene fragment (68% GC content).

## Current Issue
Low yield and non-specific bands observed.

## Data Files
- data.csv: PCR results with different annealing temperatures
- gel_image.png: Agarose gel showing amplification products
EOF

cat > data/alice_projects/exp_001_pcr_test/data.csv << 'EOF'
Temperature,Yield_ng/ul,Specificity,Notes
55,12.3,Low,Multiple bands
58,18.5,Medium,Some non-specific
60,22.1,High,Clean band
62,15.2,High,Weak band
65,5.3,High,Very weak
EOF

cat > data/bob_projects/exp_001_western_blot/README.md << 'EOF'
# Experiment: Western Blot Protein Detection
**Status**: Troubleshooting
**Date Started**: 2025-01-09

## Objective
Detect target protein (45 kDa) in cell lysates.

## Current Issue
High background and weak signal.

## Data Files
- protocol.txt: Current protocol details
- blot_image.png: Western blot result
EOF

echo "Setup complete! You can now:"
echo "1. Start the services: docker-compose up -d"
echo "2. Access the app at http://your-server-ip/"
echo "3. Login with alice or bob using the passwords you set"