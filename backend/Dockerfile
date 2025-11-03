# =============================================================================
# Dynamic Compression Algorithms Backend - Dockerfile
# Optimized for Windows 10, Intel 5820K, NVIDIA 4080Ti, Docker
# =============================================================================

# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Install additional dependencies for metrics and monitoring
RUN pip install --no-cache-dir psutil

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads

# Expose port
EXPOSE 8000

# Health check (give app more time to start on cold boot)
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (no --reload in container to prevent watcher-related restarts)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# DOCKER BUILD INSTRUCTIONS
# =============================================================================
# Build the image:
# docker build -t compression-backend .
#
# Run with basic configuration:
# docker run -p 8443:8443 compression-backend
#
# Run with environment variables:
# docker run -p 8443:8443 \
#   -e POSTGRES_SERVER=postgres \
#   -e POSTGRES_USER=postgres \
#   -e POSTGRES_PASSWORD=password \
#   -e POSTGRES_DB=file_service \
#   -e REDIS_HOST=redis \
#   -e REDIS_PORT=6379 \
#   compression-backend
#
# Run with GPU support (requires NVIDIA Docker runtime):
# docker run --gpus all -p 8443:8443 compression-backend
#
# Run with Docker Compose:
# docker-compose up backend
# =============================================================================
