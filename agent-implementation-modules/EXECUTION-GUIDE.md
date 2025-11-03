# EXECUTION GUIDE
## Copy-Paste Commands to Build Entire System

**Purpose:** Command-by-command guide - just copy and execute  
**Format:** Every command needed from start to finish  
**Usage:** Follow sequentially, paste each block into terminal  

---

## 🚀 QUICK EXECUTION PATH

```bash
# This is the fastest path to a working system.
# Follow these commands in order.
```

---

## PHASE 0: PREPARATION (30 minutes)

### Verify Prerequisites
```bash
# Check versions
docker --version          # Need 20.10+
docker-compose --version  # Need 2.0+
python3 --version         # Need 3.11+
node --version            # Need 18+
git --version             # Need 2.30+

# If any missing, install them first
```

### Create Project
```bash
# Create and enter project directory
mkdir meta-recursive-orchestration
cd meta-recursive-orchestration

# Initialize git
git init
git checkout -b main
git checkout -b develop

# Create structure
mkdir -p backend/{app,tests,alembic,database}
mkdir -p backend/app/{api,core,models,services,agents}
mkdir -p frontend/{src,public}
mkdir -p scripts data logs prometheus grafana nginx
mkdir -p data/agent{01..11}/{postgres,neo4j,influxdb,qdrant,redis,ollama,prometheus,grafana}

# Create .gitignore
cat > .gitignore <<'EOF'
__pycache__/
*.py[cod]
venv/
node_modules/
.next/
data/*/
*.db
.env*
!.env.example
logs/
.DS_Store
EOF

git add .gitignore
git commit -m "Initial structure"
```

---

## PHASE 1: AGENT 01 - INFRASTRUCTURE (Day 1-4)

### Create Environment File
```bash
cat > .env.agent01 <<'EOF'
AGENT_ID=01
AGENT_NAME=infrastructure
BACKEND_PORT=8001
FRONTEND_PORT=3001
POSTGRES_PORT=5401
NEO4J_HTTP_PORT=7401
NEO4J_BOLT_PORT=7431
INFLUXDB_PORT=8061
QDRANT_PORT=6331
REDIS_PORT=6301
OLLAMA_PORT=11401
PROMETHEUS_PORT=9001
GRAFANA_PORT=3101
NGINX_PORT=8091
DATABASE_NAME=orchestrator_agent01
DATABASE_USER=agent01
DATABASE_PASSWORD=agent01_secure_password
NEO4J_AUTH=neo4j/agent01_neo4j_password
REDIS_PASSWORD=agent01_redis_password
NETWORK_NAME=agent01_network
DATA_PATH=./data/agent01
EOF
```

### Create Backend Files
```bash
# Backend Dockerfile
cat > backend/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl libpq5 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/uploads /app/logs
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Requirements
cat > backend/requirements.txt <<'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
psycopg2-binary==2.9.9
neo4j==5.14.0
redis==5.0.1
httpx==0.25.2
prometheus-client==0.19.0
python-dotenv==1.0.0
EOF

# Main app
cat > backend/main.py <<'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Meta-Recursive Orchestration System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Meta-Recursive Multi-Agent System", "status": "operational"}

@app.get("/health")
def health():
    return {"status": "healthy", "agent": "01"}
EOF
```

### Create Frontend Files
```bash
# Frontend Dockerfile
cat > frontend/Dockerfile <<'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
EOF

# Package.json
cat > frontend/package.json <<'EOF'
{
  "name": "meta-recursive-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
EOF

# Create minimal Next.js app
mkdir -p frontend/src/app
cat > frontend/src/app/page.tsx <<'EOF'
export default function Home() {
  return <div><h1>Meta-Recursive System</h1><p>Coming soon...</p></div>
}
EOF

cat > frontend/src/app/layout.tsx <<'EOF'
export default function RootLayout({children}: {children: React.ReactNode}) {
  return <html><body>{children}</body></html>
}
EOF
```

### Create Docker Compose
```bash
cat > docker-compose.agent01.yml <<'EOF'
version: '3.8'
services:
  backend:
    build: ./backend
    container_name: agent01_backend
    ports: ["8001:8000"]
    env_file: [.env.agent01]
    networks: [agent01_network]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  postgres:
    image: postgres:15-alpine
    container_name: agent01_postgres
    ports: ["5401:5432"]
    environment:
      POSTGRES_DB: orchestrator_agent01
      POSTGRES_USER: agent01
      POSTGRES_PASSWORD: agent01_secure_password
    volumes: ["./data/agent01/postgres:/var/lib/postgresql/data"]
    networks: [agent01_network]
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent01"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    container_name: agent01_redis
    ports: ["6301:6379"]
    command: redis-server --requirepass agent01_redis_password
    volumes: ["./data/agent01/redis:/data"]
    networks: [agent01_network]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

networks:
  agent01_network:
    name: agent01_network
EOF
```

### Create Scripts
```bash
# Start script
cat > scripts/agent-start.sh <<'EOF'
#!/bin/bash
set -e
AGENT_NUM=$1
AGENT_ID=$(printf "%02d" $AGENT_NUM)
echo "🚀 Starting Agent $AGENT_ID..."
mkdir -p data/agent$AGENT_ID/{postgres,neo4j,redis,ollama}
docker-compose -f docker-compose.agent$AGENT_ID.yml up -d
echo "✅ Agent $AGENT_ID started!"
EOF

chmod +x scripts/agent-start.sh

# Health check
cat > scripts/health-check.sh <<'EOF'
#!/bin/bash
AGENT_ID=${1:-01}
source .env.agent$AGENT_ID
echo "🏥 Health Check Agent $AGENT_ID"
curl -sf http://localhost:$BACKEND_PORT/health && echo "✅ Backend" || echo "❌ Backend"
docker ps --filter "name=agent${AGENT_ID}_"
EOF

chmod +x scripts/health-check.sh
```

### Start Agent 01
```bash
# Start services
./scripts/agent-start.sh 01

# Wait for startup
sleep 30

# Check health
./scripts/health-check.sh 01

# Verify backend
curl http://localhost:8001/health

# Expected output: {"status":"healthy","agent":"01"}
```

### Test Agent 01
```bash
# Install test dependencies
cd backend
pip install pytest pytest-asyncio docker psycopg2-binary redis requests

# Create test
mkdir -p tests/agent01
cat > tests/agent01/test_basic.py <<'EOF'
import pytest
import requests

def test_backend_health():
    response = requests.get("http://localhost:8001/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_postgres_connection():
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5401,
        database="orchestrator_agent01",
        user="agent01",
        password="agent01_secure_password"
    )
    assert conn is not None
    conn.close()
EOF

# Run tests
pytest tests/agent01/test_basic.py -v

# Expected: All tests pass
cd ..
```

### Commit Agent 01
```bash
git add .
git commit -m "Agent 01: Infrastructure complete - services running and tested"
```

---

## PHASE 2: AGENT 02 - DATABASE (Day 5-10)

### Repeat Pattern for Agent 02
```bash
# Create branch
git checkout -b agent-02-database

# Create .env.agent02 (copy .env.agent01, change ports to 80XX, 54XX, etc.)
sed 's/agent01/agent02/g; s/8001/8002/g; s/5401/5402/g' .env.agent01 > .env.agent02

# Create database schema
cat > backend/database/init.sql <<'EOF'
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    input JSONB NOT NULL,
    output JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'idle'
);

-- Add more tables as specified in Agent 02 spec
EOF

# Create SQLAlchemy models
cat > backend/app/models/__init__.py <<'EOF'
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
EOF

cat > backend/app/models/database.py <<'EOF'
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from . import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    input = Column(JSON, nullable=False)
    output = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(50), default="idle")
EOF

# Update docker-compose to include database init
# Create docker-compose.agent02.yml
# Start Agent 02
# Test Agent 02
# Commit
```

---

## CONTINUE FOR ALL AGENTS (3-11)

### Agent Completion Pattern

For each agent (03-11), follow this pattern:

```bash
# 1. Create branch
git checkout develop
git checkout -b agent-0X-[name]

# 2. Read bootstrap prompt
cat docs/specifications/BOOTSTRAP-PROMPTS-ALL-AGENTS.md | grep -A 1000 "AGENT 0X"

# 3. Create environment
sed 's/agent01/agent0X/g; s/8001/800X/g; ...' .env.agent01 > .env.agent0X

# 4. Implement code (according to bootstrap prompt)
# - Create required files
# - Implement required functions
# - Add to docker-compose

# 5. Start services
./scripts/agent-start.sh 0X

# 6. Run bootstrap tests
AGENT_ID=0X pytest tests/agent0X/test_bootstrap.py -v

# 7. Verify ALL tests pass

# 8. Commit
git add .
git commit -m "Agent 0X: [Name] complete - all bootstrap tests passing"
git push origin agent-0X-[name]
```

---

## CRITICAL: AGENT 06 META-RECURSION TEST

### When You Get to Agent 06 (Week 4, Day 19)

```bash
# This is THE MOST IMPORTANT test - proves core innovation

# After implementing Meta-Learner, run:
cd backend
AGENT_ID=06 pytest tests/agent06/test_bootstrap.py::TestAgent06Bootstrap::test_06_CRITICAL_meta_recursion_proven -v

# This test MUST show:
# ✅ PASS: META-RECURSIVE LOOP PROVEN - SYSTEM CAN IMPROVE ITSELF

# If this test passes, you have proven the core innovation works!
```

---

## INTEGRATION & DEPLOYMENT (Week 9-10)

### Merge All Agents
```bash
# After all agents complete, merge to develop
git checkout develop
git merge agent-01-infrastructure
git merge agent-02-database
# ... merge all agents
git merge agent-11-deployment

# Run full system test
./scripts/test-all-agents.sh

# Deploy
./scripts/deploy.sh production
```

### Verify MVP Complete
```bash
# Check all services
for i in {01..11}; do
    ./scripts/health-check.sh $i
done

# Run full test suite
pytest backend/tests/ -v

# Performance test
./scripts/performance-test.sh

# Load test
./scripts/load-test.sh

# If all pass: MVP COMPLETE! 🎉
```

---

## COMMANDS SUMMARY

### Daily Workflow
```bash
# Morning: Start your agent
./scripts/agent-start.sh 0X

# Work: Implement code, test frequently
pytest tests/agent0X/ -v

# Evening: Check health before leaving
./scripts/health-check.sh 0X
docker-compose -f docker-compose.agent0X.yml logs

# Commit progress
git add .
git commit -m "Agent 0X: Progress on [component]"
```

### Troubleshooting Commands
```bash
# View logs
docker-compose -f docker-compose.agent0X.yml logs -f [service]

# Restart a service
docker-compose -f docker-compose.agent0X.yml restart [service]

# Rebuild
docker-compose -f docker-compose.agent0X.yml up -d --build

# Clean slate
docker-compose -f docker-compose.agent0X.yml down -v
docker system prune -a
./scripts/agent-start.sh 0X
```

### Validation Commands
```bash
# Backend health
curl http://localhost:800X/health

# Database connection
psql -h localhost -p 540X -U agent0X -d orchestrator_agent0X -c "SELECT 1"

# Redis connection
redis-cli -h localhost -p 630X -a agent0X_redis_password ping

# All containers
docker ps --filter "name=agent0X_"

# Bootstrap tests
AGENT_ID=0X pytest tests/agent0X/test_bootstrap.py -v
```

---

## FINAL VALIDATION

### When All 11 Agents Complete

```bash
# 1. Start all agents
for i in {01..11}; do
    ./scripts/agent-start.sh $i
done

# 2. Wait for all healthy
sleep 60

# 3. Check all
for i in {01..11}; do
    echo "=== Agent $i ==="
    ./scripts/health-check.sh $i
done

# 4. Run all tests
pytest backend/tests/ -v --cov=backend --cov-report=html

# 5. Performance benchmark
./scripts/benchmark.sh

# 6. Generate report
./scripts/generate-report.sh

# Expected output:
# ✅ 11/11 agents operational
# ✅ All bootstrap tests passing
# ✅ >90% test coverage
# ✅ Meta-recursive loop proven
# ✅ MVP COMPLETE!
```

---

## 🎉 SUCCESS CRITERIA

**You have successfully built the system when:**

```bash
# This command shows all green checkmarks:
./scripts/final-validation.sh

# Expected output:
# ✅ Agent 01: Infrastructure operational
# ✅ Agent 02: Database operational
# ✅ Agent 03: Core Engine operational
# ✅ Agent 04: API Layer operational
# ✅ Agent 05: Frontend operational
# ✅ Agent 06: Agent Framework operational
# ✅ Agent 06: META-RECURSIVE LOOP PROVEN ⭐
# ✅ Agent 07: LLM Integration operational
# ✅ Agent 08: Monitoring operational
# ✅ Agent 09: Testing operational (>90% coverage)
# ✅ Agent 10: Documentation complete
# ✅ Agent 11: Deployment successful
# 
# 🎉 MVP COMPLETE - SYSTEM OPERATIONAL!
```

---

**Document Version:** 1.0  
**Created:** 2025-10-30  
**Purpose:** Command-by-command execution guide  
**Result:** Working MVP in 10 weeks  

**FOLLOW THESE COMMANDS TO BUILD THE SYSTEM** ⚡

