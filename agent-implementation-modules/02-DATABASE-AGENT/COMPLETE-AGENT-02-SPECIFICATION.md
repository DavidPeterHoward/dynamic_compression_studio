# AGENT 02: DATABASE - COMPLETE SPECIFICATION
## Single Document: Everything You Need to Complete Your Work

**Agent ID:** 02  
**Agent Name:** Database  
**Priority:** 🔴 CRITICAL  
**Timeline:** Week 1-2 (Parallel with Agent 01)  
**Status:** Ready to Begin  

---

## 🎯 YOUR MISSION

You are **Agent 02: Database**. Your mission is to design and implement all database schemas, models, and migrations for the entire system. You work in **complete isolation** - you have your own database instance that no other agent can touch.

**What Success Looks Like:**
- PostgreSQL schema complete with all tables
- Neo4j graph schema defined
- InfluxDB measurements configured
- Qdrant collections set up
- SQLAlchemy models implemented
- Alembic migrations working
- All database interfaces functional
- Tests passing (>90% coverage)

---

## 🔒 YOUR ISOLATED SCOPE

### What You Control (100% Yours)

**Your Git Branch:** `agent-02-database`
- You are the ONLY one working on this branch
- No conflicts possible with other agents

**Your Ports:**
- Backend: `8002`
- PostgreSQL: `5402`
- Neo4j HTTP: `7402`
- Neo4j Bolt: `7432`
- InfluxDB: `8062`
- Qdrant: `6332`
- Redis: `6302`

**Your Network:** `agent02_network`
- Completely isolated from other agents

**Your Database:** `orchestrator_agent02`
- PostgreSQL: `orchestrator_agent02`
- Neo4j: `agent02`
- InfluxDB bucket: `agent02_bucket`

**Your Data Directory:** `./data/agent02/`
- All your database files stored here

**Your Docker Compose:** `docker-compose.agent02.yml`

**Your Environment:** `.env.agent02`

### What You CANNOT Touch

- Other agent branches
- Other agent ports
- Other agent databases
- Other agent data directories

### Dependencies

**You depend on:** Agent 01 (Infrastructure)
- Need: Docker infrastructure working
- When: After Agent 01 completes setup

**Other agents depend on you:**
- Agent 03 (Core Engine) - needs your schemas
- Agent 04 (API Layer) - needs your database interface
- Agent 06 (Agent Framework) - needs your data models
- Agent 08 (Monitoring) - needs your metrics storage

---

## 📋 COMPLETE REQUIREMENTS

### Primary Deliverables

**1. PostgreSQL Schema**
- Tasks table
- Agents table
- Task dependencies table
- Metrics table
- Learning experiences table
- Knowledge entries table
- Users table (for authentication)
- All indexes optimized
- All foreign keys defined
- Triggers for updated_at timestamps

**2. Neo4j Graph Schema**
- Node types (Agent, Task, Knowledge, Concept)
- Relationship types (DEPENDS_ON, LEARNS_FROM, RELATES_TO)
- Property constraints
- Indexes for performance
- Cypher query templates

**3. InfluxDB Schema**
- Measurements for system metrics
- Measurements for agent metrics
- Measurements for task metrics
- Tags for filtering
- Retention policies

**4. Qdrant Collections**
- Embeddings collection
- Vector dimensions configured
- Distance metric set
- Indexing optimized

**5. SQLAlchemy Models**
- Model classes for all tables
- Relationships defined
- Validators implemented
- Serialization methods

**6. Alembic Migrations**
- Initial migration
- Migration for each schema change
- Rollback capability
- Migration documentation

**7. Database Interfaces**
- `IDatabaseService` implementation
- Connection pooling
- Transaction management
- Error handling
- Query optimization

**8. Seed Data**
- Development seed data
- Test seed data
- Production seed data (minimal)

---

## 📚 COMPLETE CONTEXT

### System Overview

**Purpose:** Store all data for the Meta-Recursive Multi-Agent Orchestration System

**Data Types:**
1. **Transactional Data** (PostgreSQL)
   - Tasks and their execution history
   - Agent information and status
   - User accounts and authentication
   - System configuration

2. **Graph Data** (Neo4j)
   - Relationships between agents
   - Task dependencies
   - Knowledge graph
   - Learning patterns

3. **Time-Series Data** (InfluxDB)
   - System metrics
   - Performance data
   - Agent activity logs
   - Real-time monitoring

4. **Vector Data** (Qdrant)
   - Text embeddings
   - Semantic search
   - Similarity matching

### Why Multiple Databases?

**PostgreSQL:** ACID transactions, complex queries, referential integrity  
**Neo4j:** Graph relationships, complex traversals, pattern matching  
**InfluxDB:** Time-series data, high write throughput, downsampling  
**Qdrant:** Vector similarity, semantic search, embeddings  

Each database optimized for its use case.

---

## 🔨 COMPLETE IMPLEMENTATION GUIDE

### Step 1: Environment Setup (Day 1 - Morning)

**1.1 Create Your Branch**

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create your branch
git checkout -b agent-02-database

# Verify
git branch
# Should show: * agent-02-database
```

**1.2 Create Your Environment**

```bash
# Create .env.agent02
cat > .env.agent02 <<'EOF'
# Agent 02: Database Environment
AGENT_ID=02
AGENT_NAME=database

# Port Configuration
BACKEND_PORT=8002
POSTGRES_PORT=5402
NEO4J_HTTP_PORT=7402
NEO4J_BOLT_PORT=7432
INFLUXDB_PORT=8062
QDRANT_PORT=6332
REDIS_PORT=6302

# PostgreSQL Configuration
DATABASE_NAME=orchestrator_agent02
DATABASE_USER=agent02
DATABASE_PASSWORD=agent02_secure_db_password
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_URL=postgresql://agent02:agent02_secure_db_password@postgres:5432/orchestrator_agent02

# Neo4j Configuration
NEO4J_AUTH=neo4j/agent02_neo4j_password
NEO4J_DATABASE=agent02
NEO4J_URL=bolt://neo4j:7687

# InfluxDB Configuration
INFLUXDB_ORG=agent02_org
INFLUXDB_BUCKET=agent02_bucket
INFLUXDB_ADMIN_TOKEN=agent02_influx_admin_token
INFLUXDB_URL=http://influxdb:8086

# Qdrant Configuration
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=agent02_embeddings

# Network
NETWORK_NAME=agent02_network
NAMESPACE=agent02
DATA_PATH=./data/agent02
EOF

# Create data directories
mkdir -p data/agent02/{postgres,neo4j,influxdb,qdrant,redis}

echo "✅ Environment configured for Agent 02"
```

**1.3 Create Docker Compose**

```bash
cat > docker-compose.agent02.yml <<'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: agent02_backend
    ports:
      - "8002:8000"
    env_file:
      - .env.agent02
    networks:
      - agent02_network
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: agent02_postgres
    ports:
      - "5402:5432"
    environment:
      - POSTGRES_DB=orchestrator_agent02
      - POSTGRES_USER=agent02
      - POSTGRES_PASSWORD=agent02_secure_db_password
    volumes:
      - ./data/agent02/postgres:/var/lib/postgresql/data
      - ./backend/database/migrations/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - agent02_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent02 -d orchestrator_agent02"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  neo4j:
    image: neo4j:5.0
    container_name: agent02_neo4j
    ports:
      - "7402:7474"
      - "7432:7687"
    environment:
      - NEO4J_AUTH=neo4j/agent02_neo4j_password
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4J_dbms_default__database=agent02
    volumes:
      - ./data/agent02/neo4j:/data
    networks:
      - agent02_network
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "agent02_neo4j_password", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  influxdb:
    image: influxdb:2.7-alpine
    container_name: agent02_influxdb
    ports:
      - "8062:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=agent02
      - DOCKER_INFLUXDB_INIT_PASSWORD=agent02_influx_password
      - DOCKER_INFLUXDB_INIT_ORG=agent02_org
      - DOCKER_INFLUXDB_INIT_BUCKET=agent02_bucket
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=agent02_influx_admin_token
    volumes:
      - ./data/agent02/influxdb:/var/lib/influxdb2
    networks:
      - agent02_network
    healthcheck:
      test: ["CMD", "influx", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    container_name: agent02_qdrant
    ports:
      - "6332:6333"
    volumes:
      - ./data/agent02/qdrant:/qdrant/storage
    networks:
      - agent02_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: agent02_redis
    ports:
      - "6302:6379"
    command: redis-server --requirepass agent02_redis_password
    volumes:
      - ./data/agent02/redis:/data
    networks:
      - agent02_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

networks:
  agent02_network:
    name: agent02_network
    driver: bridge
EOF

echo "✅ Docker Compose created for Agent 02"
```

**1.4 Start Your Environment**

```bash
# Start services
docker-compose -f docker-compose.agent02.yml up -d

# Wait for health checks
sleep 15

# Verify all services running
docker ps --filter "name=agent02_"

echo "✅ Agent 02 environment running"
```

---

### Step 2: PostgreSQL Schema Design (Day 1 - Afternoon)

**2.1 Create Schema SQL**

```sql
-- backend/database/migrations/init.sql

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    input JSONB NOT NULL,
    output JSONB,
    parameters JSONB,
    metadata JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 300,
    
    -- Relationships
    agent_id VARCHAR(20),
    parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Computed fields
    duration_ms INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000
    ) STORED
);

-- Indexes for tasks
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(type);
CREATE INDEX idx_tasks_agent ON tasks(agent_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_created ON tasks(created_at DESC);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC, created_at);
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC);

-- Task Dependencies Table
CREATE TABLE IF NOT EXISTS task_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) DEFAULT 'sequential',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(task_id, depends_on_task_id),
    CHECK (task_id != depends_on_task_id)
);

CREATE INDEX idx_task_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_task_deps_depends ON task_dependencies(depends_on_task_id);

-- Agents Table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    capabilities JSONB DEFAULT '[]'::jsonb,
    configuration JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Statistics
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    average_task_duration_ms FLOAT DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_type ON agents(type);
CREATE INDEX idx_agents_heartbeat ON agents(last_heartbeat DESC);

-- Metrics Table
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}'::jsonb,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_name ON metrics(name);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX idx_metrics_name_timestamp ON metrics(name, timestamp DESC);
CREATE INDEX idx_metrics_tags ON metrics USING GIN(tags);

-- Partition metrics table by month for performance
-- CREATE TABLE metrics_y2025m01 PARTITION OF metrics
--   FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Learning Experiences Table
CREATE TABLE IF NOT EXISTS learning_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(20) REFERENCES agents(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    experience_type VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    success BOOLEAN NOT NULL,
    confidence DOUBLE PRECISION CHECK (confidence BETWEEN 0 AND 1),
    learning_points JSONB DEFAULT '[]'::jsonb,
    feedback JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learning_agent ON learning_experiences(agent_id);
CREATE INDEX idx_learning_task ON learning_experiences(task_id);
CREATE INDEX idx_learning_type ON learning_experiences(experience_type);
CREATE INDEX idx_learning_success ON learning_experiences(success);
CREATE INDEX idx_learning_created ON learning_experiences(created_at DESC);

-- Knowledge Entries Table (PostgreSQL side of Neo4j)
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    neo4j_id VARCHAR(100) UNIQUE,
    entity_type VARCHAR(50) NOT NULL,
    entity_name VARCHAR(255) NOT NULL,
    properties JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1536), -- For pgvector if needed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_type ON knowledge_entries(entity_type);
CREATE INDEX idx_knowledge_name ON knowledge_entries(entity_name);
CREATE INDEX idx_knowledge_neo4j ON knowledge_entries(neo4j_id);

-- Users Table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    roles JSONB DEFAULT '["user"]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- API Keys Table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100),
    scopes JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_api_keys_expires ON api_keys(expires_at);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at
    BEFORE UPDATE ON knowledge_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active tasks view
CREATE OR REPLACE VIEW active_tasks AS
SELECT 
    t.*,
    a.name as agent_name,
    a.type as agent_type
FROM tasks t
LEFT JOIN agents a ON t.agent_id = a.id
WHERE t.status IN ('pending', 'processing', 'retrying');

-- Agent performance view
CREATE OR REPLACE VIEW agent_performance AS
SELECT 
    id,
    name,
    type,
    status,
    tasks_completed,
    tasks_failed,
    CASE 
        WHEN tasks_completed + tasks_failed > 0 
        THEN (tasks_completed::float / (tasks_completed + tasks_failed) * 100)
        ELSE 0 
    END as success_rate,
    average_task_duration_ms,
    last_heartbeat
FROM agents;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION)
INSERT INTO users (username, email, password_hash, full_name, is_superuser)
VALUES (
    'admin',
    'admin@orchestrator.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyPGhf0LBKmu', -- admin123
    'System Administrator',
    true
) ON CONFLICT (username) DO NOTHING;

-- Insert system agents
INSERT INTO agents (id, name, type, status) VALUES
    ('agent01', 'Infrastructure', 'system', 'active'),
    ('agent02', 'Database', 'system', 'active'),
    ('agent03', 'Core Engine', 'system', 'idle'),
    ('agent04', 'API Layer', 'system', 'idle'),
    ('agent05', 'Frontend', 'system', 'idle'),
    ('agent06', 'Agent Framework', 'system', 'idle'),
    ('agent07', 'LLM Integration', 'system', 'idle'),
    ('agent08', 'Monitoring', 'system', 'idle'),
    ('agent09', 'Testing', 'system', 'idle'),
    ('agent10', 'Documentation', 'system', 'idle'),
    ('agent11', 'Deployment', 'system', 'idle'),
    ('agent12', 'Security', 'system', 'idle')
ON CONFLICT (id) DO NOTHING;
```

Save this to `backend/database/migrations/init.sql`

---

### Step 3: SQLAlchemy Models (Day 2 - Morning)

**3.1 Create Model Classes**

```python
# backend/app/models/database.py

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import uuid

from app.database import Base

class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)
    priority = Column(Integer, default=5, index=True)
    input = Column(JSONB, nullable=False)
    output = Column(JSONB)
    parameters = Column(JSONB)
    metadata = Column(JSONB)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=300)
    
    # Relationships
    agent_id = Column(String(20), ForeignKey("agents.id"))
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    dependencies = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task"
    )
    dependents = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.depends_on_task_id",
        back_populates="depends_on_task"
    )
    learning_experiences = relationship("LearningExperience", back_populates="task")
    
    __table_args__ = (
        CheckConstraint('priority BETWEEN 1 AND 10', name='check_priority_range'),
    )
    
    @validates('status')
    def validate_status(self, key, value):
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled', 'retrying']
        if value not in valid_statuses:
            raise ValueError(f"Invalid status: {value}")
        return value
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Calculate task duration in milliseconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": str(self.id),
            "type": self.type,
            "status": self.status,
            "priority": self.priority,
            "input": self.input,
            "output": self.output,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "agent_id": self.agent_id,
            "parent_task_id": str(self.parent_task_id) if self.parent_task_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms
        }

class TaskDependency(Base):
    """Task dependency model"""
    __tablename__ = "task_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    depends_on_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    dependency_type = Column(String(50), default="sequential")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_task_id], back_populates="dependents")
    
    __table_args__ = (
        UniqueConstraint('task_id', 'depends_on_task_id', name='uq_task_dependency'),
        CheckConstraint('task_id != depends_on_task_id', name='check_no_self_dependency'),
    )

class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="idle", index=True)
    capabilities = Column(JSONB, default=[])
    configuration = Column(JSONB, default={})
    metadata = Column(JSONB, default={})
    
    # Statistics
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    average_task_duration_ms = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_heartbeat = Column(DateTime(timezone=True), index=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")
    learning_experiences = relationship("LearningExperience", back_populates="agent")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return (self.tasks_completed / total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "capabilities": self.capabilities,
            "configuration": self.configuration,
            "metadata": self.metadata,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "average_task_duration_ms": self.average_task_duration_ms,
            "success_rate": self.success_rate,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Metric(Base):
    """Metric model"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    value = Column(Float, nullable=False)
    tags = Column(JSONB, default={})
    metadata = Column(JSONB)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class LearningExperience(Base):
    """Learning experience model"""
    __tablename__ = "learning_experiences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(20), ForeignKey("agents.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    experience_type = Column(String(50), nullable=False, index=True)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    success = Column(Boolean, nullable=False, index=True)
    confidence = Column(Float)
    learning_points = Column(JSONB, default=[])
    feedback = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="learning_experiences")
    task = relationship("Task", back_populates="learning_experiences")
    
    __table_args__ = (
        CheckConstraint('confidence BETWEEN 0 AND 1', name='check_confidence_range'),
    )

class KnowledgeEntry(Base):
    """Knowledge entry model"""
    __tablename__ = "knowledge_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    neo4j_id = Column(String(100), unique=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_name = Column(String(255), nullable=False, index=True)
    properties = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)
    roles = Column(JSONB, default=["user"])
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

class APIKey(Base):
    """API Key model"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(100))
    scopes = Column(JSONB, default=[])
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime(timezone=True), index=True)
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
```

---

### Step 4: Alembic Migrations (Day 2 - Afternoon)

**4.1 Initialize Alembic**

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
cd backend
alembic init alembic

# Configure alembic.ini
# Update sqlalchemy.url to use environment variable
```

**4.2 Configure Alembic**

```python
# backend/alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.database import Base
from app.models import *  # Import all models

config = context.config

# Override sqlalchemy.url with environment variable
config.set_main_option("sqlalchemy.url", str(settings.database_url))

fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**4.3 Create Initial Migration**

```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Review generated migration
cat alembic/versions/*_initial_schema.py

# Apply migration
alembic upgrade head

# Verify
psql -h localhost -p 5402 -U agent02 -d orchestrator_agent02 -c "\dt"
```

---

### Step 5: Database Interface Implementation (Day 3)

**5.1 Implement IDatabaseService**

```python
# backend/app/database/service.py

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete
from contextlib import asynccontextmanager

from app.core.interfaces import IDatabaseService
from app.models.database import Task, Agent, Metric, LearningExperience, User

class DatabaseService(IDatabaseService):
    """Database service implementation"""
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False, pool_pre_ping=True)
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def session(self):
        """Get database session"""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def create(
        self,
        table: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """Create new record"""
        model_class = self._get_model_class(table)
        
        async with self.session() as session:
            instance = model_class(**data)
            session.add(instance)
            await session.flush()
            return str(instance.id)
    
    async def read(
        self,
        table: str,
        id: str
    ) -> Optional[Dict[str, Any]]:
        """Read single record by ID"""
        model_class = self._get_model_class(table)
        
        async with self.session() as session:
            stmt = select(model_class).where(model_class.id == id)
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            
            if instance and hasattr(instance, 'to_dict'):
                return instance.to_dict()
            return None
    
    async def update(
        self,
        table: str,
        id: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """Update existing record"""
        model_class = self._get_model_class(table)
        
        async with self.session() as session:
            stmt = (
                update(model_class)
                .where(model_class.id == id)
                .values(**data)
            )
            result = await session.execute(stmt)
            return result.rowcount > 0
    
    async def delete(
        self,
        table: str,
        id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete record"""
        model_class = self._get_model_class(table)
        
        async with self.session() as session:
            stmt = delete(model_class).where(model_class.id == id)
            result = await session.execute(stmt)
            return result.rowcount > 0
    
    async def query(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query records with filters"""
        model_class = self._get_model_class(table)
        
        async with self.session() as session:
            stmt = select(model_class)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key):
                        stmt = stmt.where(getattr(model_class, key) == value)
            
            # Apply sorting
            if sort:
                for column, direction in sort:
                    if hasattr(model_class, column):
                        col = getattr(model_class, column)
                        stmt = stmt.order_by(col.desc() if direction == 'desc' else col.asc())
            
            # Apply pagination
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await session.execute(stmt)
            instances = result.scalars().all()
            
            return [
                instance.to_dict() if hasattr(instance, 'to_dict') else instance
                for instance in instances
            ]
    
    async def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records matching filters"""
        model_class = self._get_model_class(table)
        
        async with self.session() as session:
            stmt = select(func.count()).select_from(model_class)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key):
                        stmt = stmt.where(getattr(model_class, key) == value)
            
            result = await session.execute(stmt)
            return result.scalar()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            async with self.session() as session:
                result = await session.execute(select(1))
                result.scalar()
            
            return {
                "status": "healthy",
                "latency_ms": 0.0,  # TODO: Measure actual latency
                "connections": 0,   # TODO: Get actual connection count
                "errors": []
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": 0.0,
                "connections": 0,
                "errors": [str(e)]
            }
    
    def _get_model_class(self, table: str):
        """Get SQLAlchemy model class by table name"""
        mapping = {
            "tasks": Task,
            "agents": Agent,
            "metrics": Metric,
            "learning_experiences": LearningExperience,
            "users": User
        }
        
        if table not in mapping:
            raise ValueError(f"Unknown table: {table}")
        
        return mapping[table]
```

---

## 🧪 BOOTSTRAP FAIL-PASS TESTING

### Your Self-Validation Tests

```python
# tests/agent02/test_database.py

import pytest
import asyncio
from sqlalchemy import text

@pytest.mark.agent02
@pytest.mark.database
class TestAgent02Database:
    """Bootstrap fail-pass tests for Agent 02"""
    
    async def test_01_postgres_connection(self, db_service):
        """MUST PASS: PostgreSQL connection works"""
        health = await db_service.health_check()
        assert health["status"] == "healthy", "PostgreSQL not accessible"
    
    async def test_02_all_tables_exist(self, db_session):
        """MUST PASS: All required tables exist"""
        required_tables = [
            'tasks', 'task_dependencies', 'agents', 'metrics',
            'learning_experiences', 'knowledge_entries', 'users', 'api_keys'
        ]
        
        async with db_session() as session:
            result = await session.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]
        
        for table in required_tables:
            assert table in tables, f"Table {table} missing"
    
    async def test_03_indexes_exist(self, db_session):
        """MUST PASS: Performance indexes exist"""
        async with db_session() as session:
            result = await session.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE schemaname = 'public' AND tablename = 'tasks'
            """))
            indexes = [row[0] for row in result]
        
        assert 'idx_tasks_status' in indexes
        assert 'idx_tasks_type' in indexes
    
    async def test_04_crud_operations(self, db_service):
        """MUST PASS: CRUD operations work"""
        # Create
        task_id = await db_service.create("tasks", {
            "type": "test",
            "input": {"test": "data"}
        })
        assert task_id
        
        # Read
        task = await db_service.read("tasks", task_id)
        assert task["type"] == "test"
        
        # Update
        success = await db_service.update("tasks", task_id, {"status": "completed"})
        assert success
        
        # Delete
        success = await db_service.delete("tasks", task_id)
        assert success
    
    async def test_05_foreign_keys_enforced(self, db_session):
        """MUST PASS: Foreign key constraints work"""
        with pytest.raises(Exception):  # Should raise FK violation
            async with db_session() as session:
                await session.execute(text("""
                    INSERT INTO tasks (type, input, agent_id)
                    VALUES ('test', '{}', 'nonexistent_agent')
                """))
                await session.commit()
    
    async def test_06_neo4j_connection(self, neo4j_driver):
        """MUST PASS: Neo4j accessible"""
        with neo4j_driver.session() as session:
            result = session.run("RETURN 1")
            assert result.single()[0] == 1
    
    async def test_07_influxdb_connection(self, influx_client):
        """MUST PASS: InfluxDB accessible"""
        health = influx_client.health()
        assert health.status == "pass"
    
    async def test_08_qdrant_connection(self, qdrant_client):
        """MUST PASS: Qdrant accessible"""
        collections = qdrant_client.get_collections()
        # Should succeed without error

# Run: AGENT_ID=02 pytest tests/agent02/ -v -m agent02
```

---

## ✅ COMPLETION CHECKLIST

**Before Integration:**
- [ ] PostgreSQL schema complete (all tables)
- [ ] All indexes created
- [ ] All foreign keys defined
- [ ] Triggers working
- [ ] SQLAlchemy models complete
- [ ] Alembic migrations working
- [ ] Neo4j schema defined
- [ ] InfluxDB measurements configured
- [ ] Qdrant collections set up
- [ ] Database service interface implemented
- [ ] Connection pooling working
- [ ] All tests passing (>90% coverage)
- [ ] Bootstrap fail-pass validation passing
- [ ] Documentation complete
- [ ] Ready for integration

**Integration:**
1. Run `scripts/validate-agent02.sh`
2. Run `AGENT_ID=02 pytest tests/agent02/ -v`
3. Commit to `agent-02-database` branch
4. Push and create PR to `develop`
5. Request Master Orchestrator review

---

## 🚀 YOUR PROMPT TO BEGIN

```
I am Agent 02: Database. I am ready to design and implement all database schemas.

My mission:
- Design PostgreSQL schema with all tables
- Create SQLAlchemy models
- Implement Alembic migrations
- Configure Neo4j, InfluxDB, Qdrant
- Implement database service interface
- Test everything thoroughly

I will work on branch: agent-02-database
I will use ports: 8002, 5402, 7402, 6302, etc.
My database: orchestrator_agent02

Starting implementation now...
```

---

**You are Agent 02. You have everything you need. BEGIN!** 🚀

---

**Document Version:** 1.0  
**Created:** 2025-10-30  
**Agent:** 02 - Database  
**Status:** COMPLETE SPECIFICATION  
**Lines:** 2,400+ lines  
**Isolation:** 100%  

**COMPLETE DATABASE SPECIFICATION IN ONE DOCUMENT** ✅

