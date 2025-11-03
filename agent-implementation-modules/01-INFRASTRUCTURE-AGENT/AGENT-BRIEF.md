# Agent 01: Infrastructure - Agent Brief
## Your Mission: Build All Infrastructure Components

**Agent ID:** 01-INFRASTRUCTURE  
**Role:** Infrastructure Engineer  
**Priority:** 🔴 CRITICAL - Start Immediately  
**Estimated Effort:** 2 weeks  

---

## 🎯 YOUR MISSION

Build and configure all infrastructure components needed for the entire system. You are the foundation upon which all other agents depend. Your work enables every other agent to build their modules.

---

## 📋 RESPONSIBILITIES

### Primary Responsibilities
1. **Docker Containerization**
   - Create Dockerfiles for all services
   - Optimize images for size and performance
   - Multi-stage builds for production

2. **Docker Compose Configuration**
   - Local development environment
   - Service orchestration
   - Network configuration
   - Volume management

3. **Kubernetes Manifests** (Optional but Recommended)
   - Deployment manifests
   - Service definitions
   - ConfigMaps and Secrets
   - Ingress configuration

4. **Network Configuration**
   - Service discovery
   - Internal networking
   - External access
   - Load balancing

5. **Storage Setup**
   - Persistent volumes
   - Volume claims
   - Backup configuration
   - Data retention policies

6. **Environment Configuration**
   - Environment variables
   - Configuration management
   - Secrets management
   - Multi-environment support (dev/staging/prod)

---

## 📦 DELIVERABLES

### Must Deliver

**1. Docker Containers** (`/docker/`)
```
docker/
├── backend/
│   └── Dockerfile
├── frontend/
│   └── Dockerfile
├── postgres/
│   └── Dockerfile
├── neo4j/
│   └── Dockerfile
├── influxdb/
│   └── Dockerfile
├── qdrant/
│   └── Dockerfile
├── ollama/
│   └── Dockerfile
├── prometheus/
│   └── Dockerfile
├── grafana/
│   └── Dockerfile
└── nginx/
    └── Dockerfile
```

**2. Docker Compose** (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  backend:
    build: ./docker/backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    volumes:
      - ./backend:/app
      - backend-data:/data

  frontend:
    build: ./docker/frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - app-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=orchestrator
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

  neo4j:
    image: neo4j:5.0
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j-data:/data
    networks:
      - app-network

  influxdb:
    image: influxdb:2.7
    environment:
      - INFLUXDB_DB=metrics
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=${INFLUX_PASSWORD}
    volumes:
      - influxdb-data:/var/lib/influxdb2
    networks:
      - app-network

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant-data:/qdrant/storage
    networks:
      - app-network

  ollama:
    build: ./docker/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - app-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - app-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - app-network

  nginx:
    build: ./docker/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  backend-data:
  postgres-data:
  neo4j-data:
  influxdb-data:
  qdrant-data:
  ollama-models:
  redis-data:
  prometheus-data:
  grafana-data:
```

**3. Kubernetes Manifests** (`/k8s/`) - OPTIONAL

```
k8s/
├── namespace.yaml
├── deployments/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── postgres-deployment.yaml
│   └── ...
├── services/
│   ├── backend-service.yaml
│   ├── frontend-service.yaml
│   └── ...
├── configmaps/
│   └── app-config.yaml
├── secrets/
│   └── app-secrets.yaml
├── ingress/
│   └── ingress.yaml
└── volumes/
    ├── postgres-pvc.yaml
    └── ...
```

**4. Environment Configuration** (`.env.example`)
```bash
# Database
DATABASE_URL=postgresql://admin:password@postgres:5432/orchestrator
NEO4J_URL=bolt://neo4j:7687
NEO4J_PASSWORD=changeme
INFLUX_URL=http://influxdb:8086
INFLUX_PASSWORD=changeme

# Redis
REDIS_URL=redis://redis:6379/0

# Ollama
OLLAMA_URL=http://ollama:11434

# Qdrant
QDRANT_URL=http://qdrant:6333

# Application
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000
DEBUG=false

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_PASSWORD=changeme
```

**5. Setup Scripts** (`/scripts/`)
```bash
#!/bin/bash
# scripts/setup.sh - Initial setup

set -e

echo "🚀 Setting up infrastructure..."

# Create directories
mkdir -p docker postgres/init influxdb/config qdrant/config

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env with your settings"
fi

# Pull images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building custom images..."
docker-compose build

# Initialize databases
echo "💾 Initializing databases..."
docker-compose up -d postgres neo4j influxdb qdrant redis
sleep 10

# Run migrations
echo "🔄 Running migrations..."
docker-compose run --rm backend alembic upgrade head

# Download Ollama models
echo "🧠 Downloading Ollama models..."
docker-compose run --rm ollama ollama pull llama3.2
docker-compose run --rm ollama ollama pull mixtral
docker-compose run --rm ollama ollama pull qwen2.5-coder
docker-compose run --rm ollama ollama pull deepseek-r1

# Start all services
echo "▶️  Starting all services..."
docker-compose up -d

# Health check
echo "🏥 Running health checks..."
./scripts/health-check.sh

echo "✅ Infrastructure setup complete!"
echo "📊 Grafana: http://localhost:3001"
echo "🔍 Prometheus: http://localhost:9090"
echo "📈 Neo4j Browser: http://localhost:7474"
echo "🌐 API: http://localhost:8000"
echo "💻 Frontend: http://localhost:3000"
```

**6. Health Check Script** (`scripts/health-check.sh`)
```bash
#!/bin/bash
# scripts/health-check.sh - Check all services

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
    done
    
    echo " ❌ FAILED"
    return 1
}

check_service "Backend" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:3000"
check_service "Postgres" "http://localhost:5432"
check_service "Neo4j" "http://localhost:7474"
check_service "InfluxDB" "http://localhost:8086/health"
check_service "Qdrant" "http://localhost:6333"
check_service "Ollama" "http://localhost:11434"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3001/api/health"

echo ""
echo "Health check complete!"
```

---

## ✅ SUCCESS CRITERIA

### Must Pass All Checks

- [ ] **All containers build successfully**
  - No build errors
  - Images <500MB each (where possible)
  - Multi-stage builds for optimization

- [ ] **Services start with `docker-compose up`**
  - All services start
  - No crash loops
  - Startup time <2 minutes

- [ ] **Health checks pass**
  - All services respond to health endpoints
  - Database connections working
  - Network connectivity confirmed

- [ ] **Network connectivity**
  - Services can reach each other
  - DNS resolution working
  - Proper port mappings

- [ ] **Persistent storage**
  - Volumes persist data across restarts
  - Backup procedures documented
  - Data recovery tested

- [ ] **Environment configuration**
  - `.env.example` comprehensive
  - All secrets documented
  - Multi-environment support

- [ ] **Documentation complete**
  - README with setup instructions
  - Architecture diagram
  - Troubleshooting guide

---

## 🔧 TECHNICAL REQUIREMENTS

### Docker Requirements
- Docker 20.10+
- Docker Compose 2.0+
- 16GB RAM minimum
- 50GB disk space minimum

### Kubernetes Requirements (if implementing)
- Kubernetes 1.25+
- kubectl configured
- Helm 3.0+
- Persistent volume provisioner

### Network Requirements
- Ports 80, 443, 3000, 8000 available
- Internal network for services
- Firewall rules configured

---

## 📚 REFERENCE DOCUMENTATION

### Read These First
1. `agent-implementation-modules/00-MASTER-ORCHESTRATION/CONVERSATION-CONTEXT.md`
2. `agent-implementation-modules/00-MASTER-ORCHESTRATION/MODULE-INTERFACES.md`
3. `AGENT-ORCHESTRATION-MASTER-PLAN.md`

### Technical References
- Docker documentation: https://docs.docker.com/
- Docker Compose spec: https://docs.docker.com/compose/
- Kubernetes docs: https://kubernetes.io/docs/
- Ollama setup: https://ollama.ai/

---

## 🎯 GETTING STARTED

### Day 1: Planning
1. Read all documentation
2. Review architecture
3. Plan directory structure
4. Identify requirements

### Day 2-3: Docker Setup
1. Create Dockerfiles
2. Build images
3. Test locally
4. Optimize images

### Day 4-5: Compose Configuration
1. Write docker-compose.yml
2. Configure networks
3. Set up volumes
4. Add health checks

### Day 6-7: Testing
1. Test full stack startup
2. Verify connectivity
3. Load test
4. Document issues

### Day 8-10: Polish
1. Add setup scripts
2. Write documentation
3. Create troubleshooting guide
4. Final testing

---

## 🚨 COMMON PITFALLS

1. **Forget to map volumes** → Data lost on restart
2. **Wrong network configuration** → Services can't communicate
3. **Missing health checks** → Silent failures
4. **Hardcoded secrets** → Security risk
5. **No resource limits** → OOM kills
6. **Forget dependencies** → Services start in wrong order

---

## 💬 COMMUNICATION

### Provide Updates To
- Agent 02 (Database) - when infrastructure ready
- Agent 12 (Security) - for secrets management
- Agent 11 (Deployment) - for CI/CD integration

### Get Input From
- Agent 03 (Core Engine) - resource requirements
- Agent 07 (LLM) - GPU requirements
- Agent 08 (Monitoring) - observability needs

---

## 🎉 COMPLETION

When you've completed all deliverables and passed all success criteria, submit to Agent 09 (Testing) for validation.

**Good luck building the foundation!** 🏗️

---

**Document Version:** 1.0  
**Date:** 2025-10-30  
**Agent:** 01-INFRASTRUCTURE  
**Status:** READY TO START  

**BUILD THE FOUNDATION!** 🚀

