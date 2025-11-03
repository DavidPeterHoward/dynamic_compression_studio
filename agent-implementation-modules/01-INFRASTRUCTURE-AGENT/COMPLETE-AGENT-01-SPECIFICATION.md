# AGENT 01: INFRASTRUCTURE - COMPLETE SPECIFICATION
## Single Document: Everything You Need to Complete Your Work

**Agent ID:** 01  
**Agent Name:** Infrastructure  
**Priority:** 🔴 CRITICAL  
**Timeline:** Week 1-2 (Start Immediately)  
**Status:** Ready to Begin  

---

## 🎯 YOUR MISSION

You are **Agent 01: Infrastructure**. Your mission is to build the complete infrastructure foundation that all other agents depend on. You work in **complete isolation** - no other agent can interfere with your work, and you cannot interfere with theirs.

**What Success Looks Like:**
- All 12 services running in Docker containers
- Each agent has isolated environment (ports, networks, databases)
- Health checks passing for all services
- Setup scripts working
- Documentation complete
- Ready for other agents to begin work

---

## 🔒 YOUR ISOLATED SCOPE

### What You Control (100% Yours)

**Your Git Branch:** `agent-01-infrastructure`
- You are the ONLY one working on this branch
- No conflicts possible with other agents

**Your Ports:**
- Backend: `8001`
- PostgreSQL: `5401`
- Neo4j: `7401`
- Redis: `6301`
- Ollama: `11401`
- Frontend: `3001`
- Prometheus: `9001`
- Grafana: `3101`

**Your Network:** `agent01_network`
- Completely isolated from other agents
- Only your containers on this network

**Your Database:** `orchestrator_agent01`
- Separate database instance
- Your data never touches other agents

**Your Data Directory:** `./data/agent01/`
- Your files stored here
- Other agents use `./data/agent02/`, etc.

**Your Docker Compose:** `docker-compose.agent01.yml`
- Your service definitions
- Other agents have their own compose files

**Your Environment:** `.env.agent01`
- Your configuration
- Other agents have `.env.agent02`, etc.

### What You CANNOT Touch

- Other agent branches (agent-02-*, agent-03-*, etc.)
- Other agent ports (8002-8012, 5402-5412, etc.)
- Other agent networks
- Other agent databases
- Other agent data directories
- The `develop` or `main` branches (until integration)

### Integration Points (Later)

You will integrate with `develop` branch through Master Orchestrator after:
1. All your tasks complete
2. All your tests pass
3. Documentation complete
4. Master Orchestrator validates

---

## 📋 COMPLETE REQUIREMENTS

### Primary Deliverables

**1. Docker Infrastructure**
- Dockerfile for backend service
- Dockerfile for frontend service
- Dockerfiles for all supporting services
- Multi-stage builds for optimization
- Health checks for all containers
- Resource limits configured

**2. Docker Compose Configuration**
- Main compose file: `docker-compose.agent01.yml`
- Service definitions for all 12 services
- Network configuration (isolated networks)
- Volume definitions (persistent storage)
- Environment variable configuration
- Dependency management (service startup order)

**3. Environment Configuration**
- Template: `.env.example`
- Agent-specific: `.env.agent01`
- All environment variables documented
- Secrets management strategy
- Multi-environment support (dev/staging/prod)

**4. Setup Scripts**
- `scripts/setup-all-agents.sh` - Master setup for all 12 agents
- `scripts/agent-start.sh` - Start specific agent environment
- `scripts/agent-stop.sh` - Stop specific agent environment
- `scripts/agent-test.sh` - Run tests for specific agent
- `scripts/health-check.sh` - Verify all services healthy

**5. Network Isolation**
- Separate Docker network per agent
- Network policies (if using Kubernetes)
- Port mappings documented
- DNS configuration

**6. Storage Configuration**
- Volume definitions per agent
- Backup procedures
- Data retention policies
- Permission configuration

**7. Health Checks**
- Health check endpoints for all services
- Automated health monitoring
- Failure recovery procedures
- Status reporting

**8. Documentation**
- README with quick start
- Architecture diagram
- Troubleshooting guide
- FAQ document

### Technical Requirements

**Docker Version:** 20.10+  
**Docker Compose Version:** 2.0+  
**Required Services:**
- PostgreSQL 15
- Neo4j 5.0
- InfluxDB 2.7
- Qdrant (latest)
- Redis 7
- Ollama (latest)
- Prometheus (latest)
- Grafana (latest)
- Nginx (latest)

**Resource Requirements:**
- Minimum: 16GB RAM, 50GB disk
- Recommended: 32GB RAM, 100GB disk
- CPU: 8+ cores

**Platform Support:**
- Linux (primary)
- macOS (development)
- Windows (WSL2)

---

## 📚 COMPLETE CONTEXT

### Project Overview

**Project:** Meta-Recursive Multi-Agent Orchestration System

**Description:** A self-improving AI system where multiple agents work together to accomplish complex tasks. The system uses:
- LLM inference (Ollama)
- Knowledge graphs (Neo4j)
- Time-series metrics (InfluxDB)
- Vector storage (Qdrant)
- Traditional database (PostgreSQL)
- Caching (Redis)
- Monitoring (Prometheus/Grafana)

**Your Role:** You build the infrastructure that makes all of this possible.

### Why This Matters

Without your infrastructure:
- No other agent can work
- Services can't run
- Development can't proceed
- Testing impossible
- Deployment blocked

**You are the foundation of everything.**

### Multi-Agent Architecture

```
12 Agents Total:
├── Agent 01: Infrastructure (YOU) - Foundation layer
├── Agent 02: Database - Schema design
├── Agent 03: Core Engine - Processing logic
├── Agent 04: API Layer - REST/WebSocket API
├── Agent 05: Frontend - React UI
├── Agent 06: Agent Framework - Multi-agent system
├── Agent 07: LLM Integration - Ollama setup
├── Agent 08: Monitoring - Metrics & observability
├── Agent 09: Testing - Test framework
├── Agent 10: Documentation - User docs
├── Agent 11: Deployment - CI/CD
└── Agent 12: Security - Auth & encryption
```

**Each agent works in complete isolation.**

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Alembic (migrations)

**Frontend:**
- React 18+
- Next.js 14+
- TypeScript 5+
- TailwindCSS

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL (main database)
- Neo4j (knowledge graph)
- InfluxDB (metrics)
- Qdrant (vectors)
- Redis (cache)
- Ollama (LLM inference)
- Prometheus (metrics collection)
- Grafana (visualization)
- Nginx (reverse proxy)

---

## 🔨 COMPLETE IMPLEMENTATION GUIDE

### Step 1: Environment Setup (Day 1 - Morning)

**1.1 Create Your Branch**

```bash
# Start from develop branch
git checkout develop
git pull origin develop

# Create your isolated branch
git checkout -b agent-01-infrastructure

# Verify you're on the right branch
git branch
# Should show: * agent-01-infrastructure
```

**1.2 Create Your Environment File**

```bash
# Create .env.agent01
cat > .env.agent01 <<'EOF'
# Agent 01: Infrastructure Environment Configuration
# This file is ONLY for Agent 01's isolated environment

# Agent Identification
AGENT_ID=01
AGENT_NAME=infrastructure

# Port Configuration (Unique to Agent 01)
BACKEND_PORT=8001
POSTGRES_PORT=5401
NEO4J_HTTP_PORT=7401
NEO4J_BOLT_PORT=7431
INFLUXDB_PORT=8061
QDRANT_PORT=6331
REDIS_PORT=6301
OLLAMA_PORT=11401
FRONTEND_PORT=3001
PROMETHEUS_PORT=9001
GRAFANA_PORT=3101
NGINX_PORT=8091

# Database Configuration (Unique to Agent 01)
DATABASE_NAME=orchestrator_agent01
DATABASE_USER=agent01
DATABASE_PASSWORD=agent01_secure_password_change_in_production
DATABASE_HOST=postgres
DATABASE_PORT=5432

# Neo4j Configuration
NEO4J_AUTH=neo4j/agent01_neo4j_password
NEO4J_DATABASE=agent01

# InfluxDB Configuration
INFLUXDB_DB=metrics_agent01
INFLUXDB_ADMIN_USER=agent01
INFLUXDB_ADMIN_PASSWORD=agent01_influx_password
INFLUXDB_ORG=agent01_org
INFLUXDB_BUCKET=agent01_bucket

# Redis Configuration
REDIS_PASSWORD=agent01_redis_password

# Ollama Configuration
OLLAMA_MODELS=llama3.2,mixtral,qwen2.5-coder,deepseek-r1

# Network Configuration
NETWORK_NAME=agent01_network
NAMESPACE=agent01

# Volume Configuration
DATA_PATH=./data/agent01
POSTGRES_DATA=./data/agent01/postgres
NEO4J_DATA=./data/agent01/neo4j
INFLUXDB_DATA=./data/agent01/influxdb
QDRANT_DATA=./data/agent01/qdrant
REDIS_DATA=./data/agent01/redis
OLLAMA_DATA=./data/agent01/ollama
PROMETHEUS_DATA=./data/agent01/prometheus
GRAFANA_DATA=./data/agent01/grafana

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF

# Create data directories
mkdir -p data/agent01/{postgres,neo4j,influxdb,qdrant,redis,ollama,prometheus,grafana,uploads}

echo "✅ Environment file created: .env.agent01"
echo "✅ Data directories created: data/agent01/"
```

**1.3 Create Docker Compose File**

```bash
# Create docker-compose.agent01.yml
cat > docker-compose.agent01.yml <<'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: agent01_backend
    ports:
      - "8001:8000"
    env_file:
      - .env.agent01
    environment:
      - DATABASE_URL=postgresql://agent01:agent01_secure_password_change_in_production@postgres:5432/orchestrator_agent01
      - NEO4J_URL=bolt://neo4j:7687
      - INFLUXDB_URL=http://influxdb:8086
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379
      - OLLAMA_URL=http://ollama:11434
    networks:
      - agent01_network
    volumes:
      - ./backend:/app
      - ./data/agent01/uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: agent01_frontend
    ports:
      - "3001:3000"
    env_file:
      - .env.agent01
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8001
    networks:
      - agent01_network
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: agent01_postgres
    ports:
      - "5401:5432"
    environment:
      - POSTGRES_DB=orchestrator_agent01
      - POSTGRES_USER=agent01
      - POSTGRES_PASSWORD=agent01_secure_password_change_in_production
    volumes:
      - ./data/agent01/postgres:/var/lib/postgresql/data
      - ./backend/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - agent01_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent01 -d orchestrator_agent01"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  neo4j:
    image: neo4j:5.0
    container_name: agent01_neo4j
    ports:
      - "7401:7474"  # HTTP
      - "7431:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/agent01_neo4j_password
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - ./data/agent01/neo4j:/data
    networks:
      - agent01_network
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "agent01_neo4j_password", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    restart: unless-stopped

  influxdb:
    image: influxdb:2.7-alpine
    container_name: agent01_influxdb
    ports:
      - "8061:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=agent01
      - DOCKER_INFLUXDB_INIT_PASSWORD=agent01_influx_password
      - DOCKER_INFLUXDB_INIT_ORG=agent01_org
      - DOCKER_INFLUXDB_INIT_BUCKET=agent01_bucket
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=agent01_admin_token
    volumes:
      - ./data/agent01/influxdb:/var/lib/influxdb2
    networks:
      - agent01_network
    healthcheck:
      test: ["CMD", "influx", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    container_name: agent01_qdrant
    ports:
      - "6331:6333"
    volumes:
      - ./data/agent01/qdrant:/qdrant/storage
    networks:
      - agent01_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: agent01_redis
    ports:
      - "6301:6379"
    command: redis-server --requirepass agent01_redis_password
    volumes:
      - ./data/agent01/redis:/data
    networks:
      - agent01_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  ollama:
    build:
      context: ./docker/ollama
      dockerfile: Dockerfile
    container_name: agent01_ollama
    ports:
      - "11401:11434"
    volumes:
      - ./data/agent01/ollama:/root/.ollama
    networks:
      - agent01_network
    environment:
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    restart: unless-stopped
    # Uncomment if you have GPU
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  prometheus:
    image: prom/prometheus:latest
    container_name: agent01_prometheus
    ports:
      - "9001:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data/agent01/prometheus:/prometheus
    networks:
      - agent01_network
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: agent01_grafana
    ports:
      - "3101:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=agent01_grafana_password
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./data/agent01/grafana:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - agent01_network
    depends_on:
      - prometheus
      - influxdb
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: agent01_nginx
    ports:
      - "8091:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
    networks:
      - agent01_network
    depends_on:
      - backend
      - frontend
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

networks:
  agent01_network:
    name: agent01_network
    driver: bridge

volumes:
  agent01_postgres_data:
  agent01_neo4j_data:
  agent01_influxdb_data:
  agent01_qdrant_data:
  agent01_redis_data:
  agent01_ollama_data:
  agent01_prometheus_data:
  agent01_grafana_data:
EOF

echo "✅ Docker Compose file created: docker-compose.agent01.yml"
```

---

### Step 2: Create Dockerfiles (Day 1 - Afternoon)

**2.1 Backend Dockerfile**

```bash
# Create backend/Dockerfile
mkdir -p backend
cat > backend/Dockerfile <<'EOF'
# Multi-stage build for Python backend
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

echo "✅ Backend Dockerfile created"
```

**2.2 Frontend Dockerfile**

```bash
# Create frontend/Dockerfile
mkdir -p frontend
cat > frontend/Dockerfile <<'EOF'
# Multi-stage build for Next.js frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s \
  CMD wget --spider -q http://localhost:3000 || exit 1

# Run application
CMD ["npm", "start"]
EOF

echo "✅ Frontend Dockerfile created"
```

**2.3 Ollama Dockerfile**

```bash
# Create docker/ollama/Dockerfile
mkdir -p docker/ollama
cat > docker/ollama/Dockerfile <<'EOF'
FROM ollama/ollama:latest

# Pre-download models during build (optional, can be done at runtime)
# RUN ollama pull llama3.2 && \
#     ollama pull mixtral && \
#     ollama pull qwen2.5-coder && \
#     ollama pull deepseek-r1

# Expose Ollama port
EXPOSE 11434

# Start Ollama server
CMD ["ollama", "serve"]
EOF

echo "✅ Ollama Dockerfile created"
```

---

### Step 3: Create Configuration Files (Day 2 - Morning)

**3.1 Nginx Configuration**

```bash
# Create nginx/nginx.conf
mkdir -p nginx/conf.d
cat > nginx/nginx.conf <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    gzip on;

    include /etc/nginx/conf.d/*.conf;
}
EOF

cat > nginx/conf.d/default.conf <<'EOF'
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name localhost;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "✅ Nginx configuration created"
```

**3.2 Prometheus Configuration**

```bash
# Create prometheus/prometheus.yml
mkdir -p prometheus
cat > prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

echo "✅ Prometheus configuration created"
```

---

### Step 4: Create Setup Scripts (Day 2 - Afternoon)

**4.1 Agent Start Script**

```bash
# Create scripts/agent-start.sh
mkdir -p scripts
cat > scripts/agent-start.sh <<'EOF'
#!/bin/bash
# Start Agent Environment

set -e

AGENT_NUM=$1

if [ -z "$AGENT_NUM" ]; then
    echo "Usage: ./scripts/agent-start.sh <agent_number>"
    echo "Example: ./scripts/agent-start.sh 01"
    exit 1
fi

# Pad agent number
AGENT_ID=$(printf "%02d" $AGENT_NUM)

echo "🚀 Starting Agent $AGENT_ID environment..."

# Check if environment file exists
if [ ! -f ".env.agent$AGENT_ID" ]; then
    echo "❌ Environment file .env.agent$AGENT_ID not found"
    exit 1
fi

# Load environment
source .env.agent$AGENT_ID

# Create data directories if they don't exist
mkdir -p data/agent$AGENT_ID/{postgres,neo4j,influxdb,qdrant,redis,ollama,prometheus,grafana,uploads}

# Start containers
echo "📦 Starting Docker containers..."
docker-compose -f docker-compose.agent$AGENT_ID.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health check
echo "🏥 Running health checks..."

# Check backend
if curl -sf http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    echo "✅ Backend healthy (port $BACKEND_PORT)"
else
    echo "⚠️  Backend not ready yet (port $BACKEND_PORT)"
fi

# Check PostgreSQL
if pg_isready -h localhost -p $POSTGRES_PORT -U agent$AGENT_ID > /dev/null 2>&1; then
    echo "✅ PostgreSQL healthy (port $POSTGRES_PORT)"
else
    echo "⚠️  PostgreSQL not ready yet (port $POSTGRES_PORT)"
fi

# Check Redis
if redis-cli -h localhost -p $REDIS_PORT -a agent${AGENT_ID}_redis_password ping > /dev/null 2>&1; then
    echo "✅ Redis healthy (port $REDIS_PORT)"
else
    echo "⚠️  Redis not ready yet (port $REDIS_PORT)"
fi

echo ""
echo "✅ Agent $AGENT_ID environment started!"
echo ""
echo "📊 Service URLs:"
echo "   Backend:    http://localhost:$BACKEND_PORT"
echo "   Frontend:   http://localhost:$FRONTEND_PORT"
echo "   PostgreSQL: localhost:$POSTGRES_PORT"
echo "   Neo4j:      http://localhost:$NEO4J_HTTP_PORT"
echo "   Grafana:    http://localhost:$GRAFANA_PORT"
echo ""
echo "💡 View logs: docker-compose -f docker-compose.agent$AGENT_ID.yml logs -f"
echo "🛑 Stop: ./scripts/agent-stop.sh $AGENT_NUM"
EOF

chmod +x scripts/agent-start.sh
echo "✅ Agent start script created"
```

**4.2 Agent Stop Script**

```bash
# Create scripts/agent-stop.sh
cat > scripts/agent-stop.sh <<'EOF'
#!/bin/bash
# Stop Agent Environment

set -e

AGENT_NUM=$1

if [ -z "$AGENT_NUM" ]; then
    echo "Usage: ./scripts/agent-stop.sh <agent_number> [--clean]"
    echo "Example: ./scripts/agent-stop.sh 01"
    echo "         ./scripts/agent-stop.sh 01 --clean  # Also remove data"
    exit 1
fi

# Pad agent number
AGENT_ID=$(printf "%02d" $AGENT_NUM)

echo "🛑 Stopping Agent $AGENT_ID environment..."

# Stop containers
docker-compose -f docker-compose.agent$AGENT_ID.yml down

# Optional: Clean data
if [ "$2" == "--clean" ]; then
    echo "🧹 Cleaning data..."
    rm -rf data/agent$AGENT_ID/*
    echo "✅ Data cleaned"
fi

echo "✅ Agent $AGENT_ID stopped"
EOF

chmod +x scripts/agent-stop.sh
echo "✅ Agent stop script created"
```

**4.3 Health Check Script**

```bash
# Create scripts/health-check.sh
cat > scripts/health-check.sh <<'EOF'
#!/bin/bash
# Health Check Script

check_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -n "Checking $name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo " ✅"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    echo " ❌ FAILED"
    return 1
}

AGENT_ID=${1:-01}

source .env.agent$AGENT_ID

echo "🏥 Health Check for Agent $AGENT_ID"
echo "=================================="

check_service "Backend" "http://localhost:$BACKEND_PORT/health"
check_service "Frontend" "http://localhost:$FRONTEND_PORT"
check_service "Neo4j" "http://localhost:$NEO4J_HTTP_PORT"
check_service "Qdrant" "http://localhost:$QDRANT_PORT"
check_service "Prometheus" "http://localhost:$PROMETHEUS_PORT/-/healthy"
check_service "Grafana" "http://localhost:$GRAFANA_PORT/api/health"

echo ""
echo "Health check complete!"
EOF

chmod +x scripts/health-check.sh
echo "✅ Health check script created"
```

---

### Step 5: Testing (Day 3)

**5.1 Create Test Suite**

```python
# Create tests/agent01/test_infrastructure.py
# (This will be created in your test implementation)

import pytest
import docker
import requests
import psycopg2
import redis
from neo4j import GraphDatabase

@pytest.mark.agent01
@pytest.mark.infrastructure
class TestAgent01Infrastructure:
    """Tests for Agent 01: Infrastructure"""
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """Docker client"""
        return docker.from_env()
    
    @pytest.fixture(scope="class")
    def agent_config(self):
        """Agent configuration"""
        return {
            "agent_id": "01",
            "backend_port": 8001,
            "postgres_port": 5401,
            "neo4j_port": 7401,
            "redis_port": 6301,
            "qdrant_port": 6331,
            "ollama_port": 11401
        }
    
    def test_all_containers_running(self, docker_client, agent_config):
        """Test all containers are running"""
        expected_containers = [
            "agent01_backend",
            "agent01_frontend",
            "agent01_postgres",
            "agent01_neo4j",
            "agent01_influxdb",
            "agent01_qdrant",
            "agent01_redis",
            "agent01_ollama",
            "agent01_prometheus",
            "agent01_grafana",
            "agent01_nginx"
        ]
        
        running_containers = [c.name for c in docker_client.containers.list()]
        
        for container in expected_containers:
            assert container in running_containers, f"Container {container} not running"
    
    def test_backend_health(self, agent_config):
        """Test backend health endpoint"""
        response = requests.get(f"http://localhost:{agent_config['backend_port']}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_postgres_connection(self, agent_config):
        """Test PostgreSQL connection"""
        conn = psycopg2.connect(
            host="localhost",
            port=agent_config["postgres_port"],
            database="orchestrator_agent01",
            user="agent01",
            password="agent01_secure_password_change_in_production"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        
        cursor.close()
        conn.close()
    
    def test_redis_connection(self, agent_config):
        """Test Redis connection"""
        r = redis.Redis(
            host="localhost",
            port=agent_config["redis_port"],
            password="agent01_redis_password",
            decode_responses=True
        )
        
        # Test set/get
        r.set("test_key", "test_value")
        value = r.get("test_key")
        assert value == "test_value"
        
        # Cleanup
        r.delete("test_key")
    
    def test_neo4j_connection(self, agent_config):
        """Test Neo4j connection"""
        driver = GraphDatabase.driver(
            f"bolt://localhost:{agent_config['neo4j_port'] + 30}",
            auth=("neo4j", "agent01_neo4j_password")
        )
        
        with driver.session() as session:
            result = session.run("RETURN 1 AS num")
            record = result.single()
            assert record["num"] == 1
        
        driver.close()
    
    def test_network_isolation(self, docker_client):
        """Test network isolation"""
        network = docker_client.networks.get("agent01_network")
        containers = network.attrs["Containers"]
        
        # Should have exactly 11 containers on this network
        assert len(containers) == 11
    
    def test_port_allocation(self, agent_config):
        """Test ports are correctly allocated"""
        import socket
        
        ports_to_check = [
            agent_config["backend_port"],
            agent_config["postgres_port"],
            agent_config["redis_port"]
        ]
        
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            assert result == 0, f"Port {port} not accessible"
            sock.close()

# Run: AGENT_ID=01 pytest tests/agent01/ -v -m agent01
```

---

## 🧪 BOOTSTRAP FAIL-PASS TESTING

### What is Bootstrap Fail-Pass?

**Principle:** Every component must self-validate before being considered operational. If any check fails, the component reports failure and doesn't proceed.

**Your Responsibility:** Implement self-validation for all infrastructure components.

### Implementation

**1. Health Check Endpoints**

Every service must have `/health` endpoint that returns:
```json
{
  "status": "healthy|unhealthy",
  "checks": [
    {"name": "database", "status": "pass"},
    {"name": "cache", "status": "pass"},
    {"name": "storage", "status": "pass"}
  ],
  "timestamp": "2025-10-30T12:00:00Z"
}
```

**2. Container Health Checks**

All Docker containers must have `HEALTHCHECK` directive:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1
```

**3. Service Dependencies**

Use `depends_on` with `condition: service_healthy`:
```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

**4. Startup Validation Script**

```bash
# scripts/validate-agent01.sh
#!/bin/bash

echo "🔍 Validating Agent 01 Infrastructure..."

# Check 1: All containers running
echo -n "✓ Checking containers..."
RUNNING=$(docker ps --filter "name=agent01_" --format "{{.Names}}" | wc -l)
if [ $RUNNING -eq 11 ]; then
    echo " PASS"
else
    echo " FAIL ($RUNNING/11 running)"
    exit 1
fi

# Check 2: All containers healthy
echo -n "✓ Checking container health..."
HEALTHY=$(docker ps --filter "name=agent01_" --filter "health=healthy" --format "{{.Names}}" | wc -l)
if [ $HEALTHY -eq 11 ]; then
    echo " PASS"
else
    echo " FAIL ($HEALTHY/11 healthy)"
    exit 1
fi

# Check 3: Backend responding
echo -n "✓ Checking backend..."
if curl -sf http://localhost:8001/health > /dev/null; then
    echo " PASS"
else
    echo " FAIL"
    exit 1
fi

# Check 4: Database accessible
echo -n "✓ Checking database..."
if pg_isready -h localhost -p 5401 -U agent01 > /dev/null 2>&1; then
    echo " PASS"
else
    echo " FAIL"
    exit 1
fi

# Check 5: Network isolation
echo -n "✓ Checking network isolation..."
NETWORK_CONTAINERS=$(docker network inspect agent01_network -f '{{len .Containers}}')
if [ $NETWORK_CONTAINERS -eq 11 ]; then
    echo " PASS"
else
    echo " FAIL"
    exit 1
fi

echo ""
echo "✅ All validation checks passed!"
echo "🎉 Agent 01 infrastructure is operational!"
```

---

## 📝 DOCUMENTATION REQUIREMENTS

### Create These Documents

**1. README.md**
```markdown
# Agent 01: Infrastructure

## Overview
Infrastructure layer for Meta-Recursive Multi-Agent Orchestration System.

## Quick Start
```bash
# Start environment
./scripts/agent-start.sh 01

# Check health
./scripts/health-check.sh 01

# Run tests
AGENT_ID=01 pytest tests/agent01/ -v

# Stop environment
./scripts/agent-stop.sh 01
```

## Architecture
[Include diagram]

## Services
- Backend (port 8001)
- Frontend (port 3001)
- PostgreSQL (port 5401)
- Neo4j (port 7401)
- ... [list all]

## Troubleshooting
[Common issues]
```

**2. ARCHITECTURE.md**
- System diagram
- Network topology
- Port allocation table
- Data flow

**3. TROUBLESHOOTING.md**
- Common issues
- Solutions
- Debug commands
- Log locations

---

## ✅ COMPLETION CHECKLIST

### Before Requesting Integration

- [ ] All Docker containers built successfully
- [ ] All services start with `docker-compose up`
- [ ] Health checks passing for all services (11/11)
- [ ] Network isolation verified (separate network)
- [ ] Port allocation correct (no conflicts)
- [ ] Data persistence working (volumes)
- [ ] All tests passing (>90% coverage)
- [ ] Bootstrap fail-pass validation passing
- [ ] Setup scripts working (`agent-start.sh`, etc.)
- [ ] Documentation complete (README, etc.)
- [ ] All files committed to `agent-01-infrastructure` branch
- [ ] Ready for integration review

### Integration Process

1. **Self-Validate:** Run `scripts/validate-agent01.sh`
2. **Run Tests:** `AGENT_ID=01 pytest tests/agent01/ -v`
3. **Commit Changes:** `git add . && git commit -m "Agent 01: Complete"`
4. **Push Branch:** `git push origin agent-01-infrastructure`
5. **Create PR:** To `develop` branch
6. **Request Review:** From Master Orchestrator
7. **Fix Issues:** If any found
8. **Integration:** Master Orchestrator merges when ready

---

## 🚀 YOUR PROMPT TO BEGIN

```
I am Agent 01: Infrastructure. I am ready to build the complete infrastructure foundation.

My mission:
- Build Docker infrastructure for all 12 services
- Ensure complete isolation per agent
- Implement health checks and monitoring
- Create setup and management scripts
- Test everything thoroughly
- Document all components

I will work on branch: agent-01-infrastructure
I will use ports: 8001, 5401, 7401, 6301, etc.
I will not interfere with other agents.

Starting implementation now...
```

---

**You are Agent 01. You have everything you need. BEGIN!** 🚀

---

**Document Version:** 1.0  
**Created:** 2025-10-30  
**Agent:** 01 - Infrastructure  
**Status:** COMPLETE SPECIFICATION - READY TO EXECUTE  
**Isolation:** 100% (Zero conflicts possible)  

**EVERYTHING YOU NEED IN ONE DOCUMENT** ✅

