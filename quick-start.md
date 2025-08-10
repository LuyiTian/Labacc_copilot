# Quick Start Guide - Remote Server (36.163.20.6)

## Immediate Test (Single User)

### 1. Start the App

```bash
# Option A: Run in foreground (see logs)
./run-remote.sh

# Option B: Run in background
./run-remote-background.sh
```

### 2. Access the App

Open browser to: **http://36.163.20.6:8000**

### 3. Test Commands

In the chat interface, try:
- `/help` - Show available commands
- `/ls` - List experiment folders
- `/cat exp_001_pcr_test/data.csv` - View example data
- "Analyze my PCR results" - Test AI analysis
- "Why am I getting low yield?" - Test troubleshooting

### 4. Stop the App

```bash
# If running in foreground: Ctrl+C

# If running in background:
kill $(lsof -ti:8000)
```

## Multi-User Setup (Later)

For production with multiple users:

### Option 1: Multiple Ports
```bash
# Alice on port 8001
LABACC_PROJECT_ROOT=/home/alice/experiments uv run chainlit run src/ui/app.py --host 0.0.0.0 --port 8001 &

# Bob on port 8002  
LABACC_PROJECT_ROOT=/home/bob/experiments uv run chainlit run src/ui/app.py --host 0.0.0.0 --port 8002 &
```

### Option 2: With Docker
```bash
docker-compose up -d
```

## Troubleshooting

### Port Already in Use
```bash
lsof -i:8000  # Check what's using port
kill $(lsof -ti:8000)  # Kill process
```

### Check Logs
```bash
tail -f labacc.log  # If running in background
```

### Firewall Issues
```bash
# Open port 8000 if needed
sudo ufw allow 8000/tcp
```

## Important Notes

- **API Keys**: Must be set in your .bashrc
- **Data Location**: Example data in `data/alice_projects/`
- **File Commands**: Use `/ls`, `/cat`, `/pwd` to explore
- **Analysis**: Upload CSV files or point to existing experiments