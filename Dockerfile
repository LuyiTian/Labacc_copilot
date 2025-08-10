FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/
COPY data/ref/ ./data/ref/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directories
RUN mkdir -p /data/projects /data/history

# Expose Chainlit port
EXPOSE 8000

# Run Chainlit
CMD ["chainlit", "run", "src/ui/app.py", "--host", "0.0.0.0", "--port", "8000"]