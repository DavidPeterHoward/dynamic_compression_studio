# =============================================================================
# Dynamic Compression Algorithms Backend - Optimized Dockerfile
# Multi-stage build with BuildKit optimizations for maximum performance
# =============================================================================

# Build stage - optimized for dependency installation
FROM python:3.11-alpine AS builder

# Enable BuildKit mount cache for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip config set global.cache-dir /root/.cache/pip

# Set environment variables for build optimization
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install build dependencies in a single layer
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

# Copy requirements first for optimal caching
COPY requirements.txt .

# Install Python dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --user -r requirements.txt

# Runtime stage - optimized for production
FROM python:3.11-alpine AS runtime

# Install minimal runtime dependencies
RUN apk add --no-cache \
    curl \
    postgresql-client \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1001 -S python && \
    adduser -S python -u 1001

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/home/python/.local/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder --chown=python:python /root/.local /home/python/.local

# Copy project files
COPY --chown=python:python . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/uploads && \
    chown -R python:python /app/logs /app/uploads

# Switch to non-root user
USER python

# Expose port
EXPOSE 8000

# Optimized health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
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
