# Use Python 3.11 slim image (smaller than full Python image)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for Python packages
# gcc: C compiler needed for psycopg2-binary
# Clean apt cache to reduce image size
RUN apt-get update && apt-get install -y \
    gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (before source code)
# This creates a separate Docker layer that can be cached
# If requirements.txt doesn't change, this layer is reused
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir prevents pip from caching packages (saves space)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
# This happens after pip install so code changes don't invalidate dependency layer
COPY . .

# Default command to run the FastAPI application
# --host 0.0.0.0: Bind to all interfaces (required for Docker networking)
# --port 8000: Listen on port 8000
# --reload: Auto-restart on code changes (development only)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]