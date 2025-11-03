# Critical Pathway Implementation Examples
## Practical Step-by-Step for Each Critical Path

**Version:** 1.0  
**Date:** 2025-10-30  
**Purpose:** Show exactly how agents use isolation methodology in practice  

---

## 🎯 OVERVIEW

This document provides **practical, copy-paste examples** for each critical pathway showing:
1. How to set up isolated environment
2. How to develop in isolation
3. How to test in isolation
4. How to integrate safely

---

## 🔴 CRITICAL PATHWAY 1: Foundation (Week 1-2)

### Agent 01: Infrastructure (First to Start)

**Step 1: Environment Setup**

```bash
#!/bin/bash
# Agent 01 starts work

# Create and switch to branch
git checkout -b agent-01-infrastructure develop

# Set up isolated environment
cat > .env.agent01 <<EOF
AGENT_ID=01
AGENT_NAME=infrastructure
BACKEND_PORT=8001
POSTGRES_PORT=5401
NEO4J_PORT=7401
REDIS_PORT=6301
OLLAMA_PORT=11401
FRONTEND_PORT=3001
DATABASE_NAME=orchestrator_agent01
DATABASE_USER=agent01
DATABASE_PASSWORD=agent01_secure_password
NETWORK_NAME=agent01_network
NAMESPACE=agent01
DATA_PATH=./data/agent01
EOF

# Create docker-compose for Agent 01
cat > docker-compose.agent01.yml <<EOF
version: '3.8'

services:
  backend:
    build: ./backend
    container_name=agent01_backend
    ports:
      - "8001:8000"
    env_file:
      - .env.agent01
    networks:
      - agent01_network
    volumes:
      - ./backend:/app
      - ./data/agent01:/data

  postgres:
    image: postgres:15
    container_name: agent01_postgres
    ports:
      - "5401:5432"
    environment:
      POSTGRES_DB: orchestrator_agent01
      POSTGRES_USER: agent01
      POSTGRES_PASSWORD: agent01_secure_password
    volumes:
      - ./data/agent01/postgres:/var/lib/postgresql/data
    networks:
      - agent01_network

  redis:
    image: redis:7-alpine
    container_name: agent01_redis
    ports:
      - "6301:6379"
    volumes:
      - ./data/agent01/redis:/data
    networks:
      - agent01_network

networks:
  agent01_network:
    driver: bridge
EOF

# Create data directory
mkdir -p data/agent01/{postgres,redis,uploads}

# Start environment
docker-compose -f docker-compose.agent01.yml up -d

echo "✅ Agent 01 environment ready"
echo "🌐 Backend: http://localhost:8001"
echo "💾 Database: localhost:5401"
```

**Step 2: Develop Docker Infrastructure**

```bash
# Agent 01's work directory
cd backend/

# Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Test build
docker build -t agent01-backend .

# Test run
docker run -d -p 8001:8000 --name test-agent01 agent01-backend

# Health check
sleep 5
curl http://localhost:8001/health

# Clean up test
docker stop test-agent01
docker rm test-agent01
```

**Step 3: Test in Isolation**

```python
# tests/test_agent01_infrastructure.py

import pytest
import docker
import requests
import os

class TestAgent01Infrastructure:
    """Tests for Agent 01: Infrastructure"""
    
    @pytest.fixture(scope="class")
    def agent_env(self):
        """Set up agent environment"""
        # Load agent config
        agent_id = "01"
        base_url = f"http://localhost:800{agent_id}"
        
        yield {
            "agent_id": agent_id,
            "base_url": base_url,
            "db_host": f"localhost",
            "db_port": 5400 + int(agent_id)
        }
    
    def test_containers_running(self, agent_env):
        """Test all containers are running"""
        client = docker.from_env()
        
        containers = [
            f"agent{agent_env['agent_id']}_backend",
            f"agent{agent_env['agent_id']}_postgres",
            f"agent{agent_env['agent_id']}_redis"
        ]
        
        for container_name in containers:
            container = client.containers.get(container_name)
            assert container.status == "running"
    
    def test_backend_health(self, agent_env):
        """Test backend health endpoint"""
        response = requests.get(f"{agent_env['base_url']}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_database_connection(self, agent_env):
        """Test database connection"""
        import psycopg2
        
        conn = psycopg2.connect(
            host=agent_env['db_host'],
            port=agent_env['db_port'],
            database=f"orchestrator_agent{agent_env['agent_id']}",
            user=f"agent{agent_env['agent_id']}",
            password=f"agent{agent_env['agent_id']}_secure_password"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        assert result[0] == 1
        
        cursor.close()
        conn.close()
    
    def test_network_isolation(self, agent_env):
        """Test network isolation"""
        client = docker.from_env()
        
        # Get agent's network
        network_name = f"agent{agent_env['agent_id']}_network"
        network = client.networks.get(network_name)
        
        # Verify containers in this network
        containers = network.attrs['Containers']
        
        # Should only have agent's containers
        expected_containers = 3  # backend, postgres, redis
        assert len(containers) == expected_containers

# Run tests
# pytest tests/test_agent01_infrastructure.py -v
```

**Step 4: Commit & Push**

```bash
# Commit changes
git add .
git commit -m "Agent 01: Complete Docker infrastructure setup

- Created Dockerfile for backend
- Created docker-compose for all services
- Implemented network isolation
- Added health checks
- All tests passing"

# Push to agent branch
git push origin agent-01-infrastructure

# Create pull request (via GitHub CLI)
gh pr create \
    --base develop \
    --head agent-01-infrastructure \
    --title "Agent 01: Infrastructure Complete" \
    --body "Infrastructure setup complete. All containers running in isolation. Tests passing."
```

---

### Agent 02: Database (Parallel with Agent 01)

**Step 1: Environment Setup**

```bash
#!/bin/bash
# Agent 02 starts work (parallel with Agent 01)

git checkout -b agent-02-database develop

# Set up isolated environment
cat > .env.agent02 <<EOF
AGENT_ID=02
AGENT_NAME=database
BACKEND_PORT=8002
POSTGRES_PORT=5402
NEO4J_PORT=7402
REDIS_PORT=6302
DATABASE_NAME=orchestrator_agent02
DATABASE_USER=agent02
DATABASE_PASSWORD=agent02_secure_password
NETWORK_NAME=agent02_network
NAMESPACE=agent02
DATA_PATH=./data/agent02
EOF

# Create docker-compose for Agent 02
cat > docker-compose.agent02.yml <<EOF
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: agent02_backend
    ports:
      - "8002:8000"
    env_file:
      - .env.agent02
    environment:
      - DATABASE_URL=postgresql://agent02:agent02_secure_password@postgres:5432/orchestrator_agent02
    networks:
      - agent02_network
    volumes:
      - ./backend:/app
      - ./data/agent02:/data
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    container_name: agent02_postgres
    ports:
      - "5402:5432"
    environment:
      POSTGRES_DB: orchestrator_agent02
      POSTGRES_USER: agent02
      POSTGRES_PASSWORD: agent02_secure_password
    volumes:
      - ./data/agent02/postgres:/var/lib/postgresql/data
      - ./backend/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - agent02_network

  neo4j:
    image: neo4j:5.0
    container_name: agent02_neo4j
    ports:
      - "7402:7474"
      - "7432:7687"
    environment:
      NEO4J_AUTH: neo4j/agent02_password
    volumes:
      - ./data/agent02/neo4j:/data
    networks:
      - agent02_network

  redis:
    image: redis:7-alpine
    container_name: agent02_redis
    ports:
      - "6302:6379"
    volumes:
      - ./data/agent02/redis:/data
    networks:
      - agent02_network

networks:
  agent02_network:
    driver: bridge
EOF

# Create data directory
mkdir -p data/agent02/{postgres,neo4j,redis}

# Start environment
docker-compose -f docker-compose.agent02.yml up -d

echo "✅ Agent 02 environment ready"
echo "🌐 Backend: http://localhost:8002"
echo "💾 PostgreSQL: localhost:5402"
echo "📊 Neo4j: http://localhost:7402"
```

**Step 2: Design Database Schemas**

```sql
-- backend/database/init.sql
-- Agent 02: Database Schema

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    input JSONB NOT NULL,
    output JSONB,
    parameters JSONB,
    priority INTEGER DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    agent_id VARCHAR(20),
    parent_task_id UUID REFERENCES tasks(id),
    error_message TEXT
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(type);
CREATE INDEX idx_tasks_agent ON tasks(agent_id);
CREATE INDEX idx_tasks_created ON tasks(created_at);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    capabilities JSONB,
    configuration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_name ON metrics(name);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);

-- Knowledge graph entries (for Neo4j reference)
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    neo4j_id VARCHAR(100),
    entity_type VARCHAR(50),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Learning experiences
CREATE TABLE IF NOT EXISTS learning_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(20) REFERENCES agents(id),
    task_id UUID REFERENCES tasks(id),
    experience_type VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    success BOOLEAN,
    confidence DOUBLE PRECISION,
    learning_points JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Step 3: Create SQLAlchemy Models**

```python
# backend/app/models/database.py
# Agent 02: SQLAlchemy Models

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base

class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    input = Column(JSONB, nullable=False)
    output = Column(JSONB)
    parameters = Column(JSONB)
    priority = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    agent_id = Column(String(20), ForeignKey("agents.id"))
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    error_message = Column(Text)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id])

class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="idle")
    capabilities = Column(JSONB)
    configuration = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_heartbeat = Column(DateTime(timezone=True))
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")

class Metric(Base):
    """Metric model"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    value = Column(Float, nullable=False)
    tags = Column(JSONB)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class LearningExperience(Base):
    """Learning experience model"""
    __tablename__ = "learning_experiences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(20), ForeignKey("agents.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    experience_type = Column(String(50))
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    success = Column(Boolean)
    confidence = Column(Float)
    learning_points = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Step 4: Test in Isolation**

```python
# tests/test_agent02_database.py

import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestAgent02Database:
    """Tests for Agent 02: Database"""
    
    @pytest.fixture(scope="class")
    def db_engine(self):
        """Create database engine"""
        database_url = "postgresql://agent02:agent02_secure_password@localhost:5402/orchestrator_agent02"
        engine = create_engine(database_url)
        yield engine
        engine.dispose()
    
    def test_database_connection(self, db_engine):
        """Test database connection"""
        with db_engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
    
    def test_tables_exist(self, db_engine):
        """Test all tables exist"""
        expected_tables = ['tasks', 'agents', 'metrics', 'learning_experiences']
        
        with db_engine.connect() as conn:
            result = conn.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = [row[0] for row in result]
            
            for table in expected_tables:
                assert table in tables
    
    def test_create_task(self, db_engine):
        """Test creating a task"""
        from app.models.database import Task
        Session = sessionmaker(bind=db_engine)
        session = Session()
        
        task = Task(
            type="test_task",
            input={"data": "test"},
            parameters={"param1": "value1"}
        )
        
        session.add(task)
        session.commit()
        
        # Verify
        retrieved = session.query(Task).filter_by(type="test_task").first()
        assert retrieved is not None
        assert retrieved.input["data"] == "test"
        
        # Cleanup
        session.delete(retrieved)
        session.commit()
        session.close()

# Run tests
# AGENT_ID=02 pytest tests/test_agent02_database.py -v
```

**Step 5: Commit & Request Integration**

```bash
# Commit changes
git add .
git commit -m "Agent 02: Complete database schema design

- PostgreSQL schema with all tables
- Neo4j integration
- SQLAlchemy models
- Alembic migrations
- All tests passing in isolation"

# Push to agent branch
git push origin agent-02-database

# Create pull request
gh pr create \
    --base develop \
    --head agent-02-database \
    --title "Agent 02: Database Schema Complete" \
    --body "Database layer complete. All schemas defined, models created, migrations working. Tests passing in isolation."
```

---

## 🔄 INTEGRATION EXAMPLE

### Master Orchestrator Integrates Agent 01 & 02

**Step 1: Validate Both Agents Ready**

```bash
#!/bin/bash
# Master Orchestrator validates agents

echo "🔍 Validating Agent 01..."
git checkout agent-01-infrastructure
./scripts/agent-start.sh 01
AGENT_ID=01 pytest tests/test_agent01_infrastructure.py -v

if [ $? -eq 0 ]; then
    echo "✅ Agent 01 tests passing"
else
    echo "❌ Agent 01 tests failing - cannot integrate"
    exit 1
fi

echo "🔍 Validating Agent 02..."
git checkout agent-02-database
./scripts/agent-start.sh 02
AGENT_ID=02 pytest tests/test_agent02_database.py -v

if [ $? -eq 0 ]; then
    echo "✅ Agent 02 tests passing"
else
    echo "❌ Agent 02 tests failing - cannot integrate"
    exit 1
fi

echo "✅ Both agents ready for integration"
```

**Step 2: Create Integration Branch**

```bash
# Switch to develop
git checkout develop

# Merge Agent 01
git merge --no-ff agent-01-infrastructure -m "Integrate Agent 01: Infrastructure"

# Merge Agent 02
git merge --no-ff agent-02-database -m "Integrate Agent 02: Database"

# Resolve any conflicts (should be minimal with isolation)
```

**Step 3: Run Integration Tests**

```python
# tests/integration/test_infrastructure_database_integration.py

import pytest
import requests
import psycopg2

class TestInfrastructureDatabaseIntegration:
    """Integration tests for Agent 01 + Agent 02"""
    
    def test_backend_can_connect_to_database(self):
        """Test backend connects to database successfully"""
        # Start integrated environment
        import subprocess
        subprocess.run(["docker-compose", "up", "-d"])
        
        # Wait for services
        import time
        time.sleep(10)
        
        # Test backend health (includes DB connection)
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "connected"
    
    def test_end_to_end_task_creation(self):
        """Test creating task via API and verifying in database"""
        # Create task via API
        response = requests.post(
            "http://localhost:8000/api/v1/tasks",
            json={
                "type": "test_task",
                "input": {"data": "integration_test"},
                "priority": 5
            }
        )
        
        assert response.status_code == 201
        task_id = response.json()["id"]
        
        # Verify in database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="orchestrator",
            user="admin",
            password="password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, type FROM tasks WHERE id = %s", (task_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[1] == "test_task"
        
        cursor.close()
        conn.close()

# Run integration tests
# pytest tests/integration/test_infrastructure_database_integration.py -v
```

**Step 4: Merge to Develop**

```bash
# If integration tests pass
if [ $? -eq 0 ]; then
    git push origin develop
    echo "✅ Integration complete - Agent 01 & 02 merged to develop"
    
    # Notify agents
    echo "📢 Notifying all agents of successful integration..."
    # (Send notifications via Slack/Email/etc.)
else
    echo "❌ Integration tests failed - reverting"
    git reset --hard HEAD~2
fi
```

---

**This continues in next response with more critical pathways...**

---

**Document Version:** 1.0  
**Date:** 2025-10-30  
**Status:** PART 1 OF CRITICAL PATHWAY EXAMPLES  
**Next:** More pathways + testing strategies  

**PRACTICAL ISOLATION IN ACTION** 🚀

