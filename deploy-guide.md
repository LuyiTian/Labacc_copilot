# Deployment Guide for LabAcc Copilot

## Quick Local Testing

For immediate testing on your local machine:

```bash
# Run the setup to create example data
./setup-users.sh

# Start locally (single user mode)
./run-local.sh

# Open browser to http://localhost:8000
```

## Production Deployment (Multiple Users)

### 1. Server Setup

On your remote Linux server:

```bash
# Clone the repository
git clone <your-repo-url> labacc_copilot
cd labacc_copilot

# Run setup script to create users and directories
./setup-users.sh
```

### 2. Configure User Directories

Edit `docker-compose.yml` to map actual user directories:

```yaml
volumes:
  - /path/to/alice/experiments:/data/projects  # Change these paths
  - /path/to/bob/experiments:/data/projects
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application

- URL: `http://your-server-ip/`
- Users: alice, bob (passwords set during setup)
- Each user automatically connects to their own instance

## Alternative: Systemd Services (Without Docker)

For each user, create a systemd service:

```bash
# /etc/systemd/system/labacc-alice.service
[Unit]
Description=LabAcc Copilot for Alice
After=network.target

[Service]
Type=simple
User=alice
WorkingDirectory=/opt/labacc_copilot
Environment="LABACC_PROJECT_ROOT=/home/alice/experiments"
Environment="TAVILY_API_KEY=your-key"
Environment="OPENAI_API_KEY=your-key"
ExecStart=/usr/local/bin/uv run chainlit run src/ui/app.py --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable labacc-alice
sudo systemctl start labacc-alice
```

## Testing the Deployment

1. **Test file operations:**
   ```
   /pwd                    # Show project root
   /ls                     # List files
   /cat exp_001_pcr_test/data.csv  # View data
   ```

2. **Test analysis:**
   - "Analyze my PCR experiment results"
   - "Why am I getting low yield?"
   - "Suggest optimization for GC-rich templates"

3. **Test deep research:**
   - "Search literature for PCR optimization methods"
   - "Find recent papers on reducing PCR background"

## Security Considerations

1. **API Keys:** Set in server's environment or `/etc/environment`
2. **HTTPS:** Add SSL certificates to nginx for production
3. **Firewall:** Only expose port 80/443, not individual Chainlit ports
4. **Backup:** Regular backup of user experiment directories

## Troubleshooting

- **Port conflicts:** Change ports in docker-compose.yml
- **Permission issues:** Ensure docker can read user directories
- **Memory issues:** Adjust Docker memory limits if needed
- **Check logs:** `docker-compose logs labacc-alice`