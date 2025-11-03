# BOOTSTRAP PROMPTS - ALL AGENTS
## Complete Fail-Pass Bootstrap Methodology Prompts

**Purpose:** Ready-to-use prompts for each agent with built-in fail-pass validation  
**Date:** 2025-10-30  
**Version:** 1.0 (MVP - No Security)  
**Usage:** Copy prompt, provide to LLM/developer, begin implementation  

---

## 🎯 WHAT IS BOOTSTRAP FAIL-PASS?

**Principle:** Every component must self-validate before being considered operational.

**Implementation:**
1. Component implements functionality
2. Component runs self-validation tests
3. If tests PASS → Component is operational
4. If tests FAIL → Component reports failure and does not proceed
5. No downstream components use failed components

**Result:** System-wide reliability from ground up

---

## 📋 PROMPT FORMAT

Each prompt contains:
- ✅ Complete mission statement
- ✅ Isolated scope (branch, ports, database)
- ✅ All deliverables listed
- ✅ Implementation steps
- ✅ Bootstrap fail-pass tests (CRITICAL)
- ✅ Success criteria
- ✅ Integration checklist

---

# AGENT 01: INFRASTRUCTURE

## Complete Bootstrap Prompt

```markdown
# AGENT 01: INFRASTRUCTURE - BOOTSTRAP IMPLEMENTATION

## Your Mission
You are Agent 01: Infrastructure. You build the foundational Docker infrastructure for all 11 agents.

## Isolation Guarantee
- Branch: agent-01-infrastructure
- Ports: 8001, 5401, 7401, 6301, 11401, 9001, 3101, 8091
- Network: agent01_network
- Database: orchestrator_agent01
- Data: ./data/agent01/

**NO OTHER AGENT CAN INTERFERE WITH YOUR WORK**

## Phase 1: Environment Setup (2 hours)

Create .env.agent01:
```bash
cat > .env.agent01 <<'EOF'
AGENT_ID=01
AGENT_NAME=infrastructure
BACKEND_PORT=8001
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
NETWORK_NAME=agent01_network
DATA_PATH=./data/agent01
EOF

mkdir -p data/agent01/{postgres,neo4j,influxdb,qdrant,redis,ollama,prometheus,grafana}
```

## Phase 2: Docker Compose (4 hours)

Create docker-compose.agent01.yml with ALL 11 services:
- backend (FastAPI)
- postgres (PostgreSQL 15)
- neo4j (Neo4j 5.0)
- influxdb (InfluxDB 2.7)
- qdrant (Qdrant latest)
- redis (Redis 7)
- ollama (Ollama latest)
- prometheus (Prometheus latest)
- grafana (Grafana latest)
- nginx (Nginx latest)
- frontend (Next.js)

**Each service MUST have:**
- healthcheck directive
- restart: unless-stopped
- proper volume mounts
- environment variables
- network: agent01_network

## Phase 3: Setup Scripts (2 hours)

Create:
1. scripts/agent-start.sh 01
2. scripts/agent-stop.sh 01
3. scripts/health-check.sh 01

## ✅ BOOTSTRAP FAIL-PASS TESTS (CRITICAL)

Create tests/agent01/test_bootstrap.py:

```python
import pytest
import docker
import requests
import time

@pytest.mark.agent01
class TestAgent01Bootstrap:
    """
    Bootstrap fail-pass tests for Agent 01
    ALL MUST PASS before Agent 01 is considered operational
    """
    
    @pytest.fixture
    def docker_client(self):
        return docker.from_env()
    
    def test_01_CRITICAL_all_containers_exist(self, docker_client):
        """FAIL-PASS: All 11 containers must exist"""
        required = [
            "agent01_backend", "agent01_postgres", "agent01_neo4j",
            "agent01_influxdb", "agent01_qdrant", "agent01_redis",
            "agent01_ollama", "agent01_prometheus", "agent01_grafana",
            "agent01_nginx", "agent01_frontend"
        ]
        
        containers = [c.name for c in docker_client.containers.list(all=True)]
        
        for container in required:
            assert container in containers, f"❌ FAIL: {container} does not exist"
        
        print("✅ PASS: All 11 containers exist")
    
    def test_02_CRITICAL_all_containers_running(self, docker_client):
        """FAIL-PASS: All containers must be running"""
        required = [
            "agent01_backend", "agent01_postgres", "agent01_neo4j",
            "agent01_influxdb", "agent01_qdrant", "agent01_redis",
            "agent01_ollama", "agent01_prometheus", "agent01_grafana",
            "agent01_nginx", "agent01_frontend"
        ]
        
        running = [c.name for c in docker_client.containers.list()]
        
        for container in required:
            assert container in running, f"❌ FAIL: {container} not running"
        
        print("✅ PASS: All 11 containers running")
    
    def test_03_CRITICAL_all_containers_healthy(self, docker_client):
        """FAIL-PASS: All containers must be healthy"""
        required = [
            "agent01_backend", "agent01_postgres", "agent01_redis"
        ]
        
        for container_name in required:
            container = docker_client.containers.get(container_name)
            health = container.attrs['State'].get('Health', {}).get('Status')
            
            # Wait up to 60 seconds for healthy
            for i in range(60):
                if health == 'healthy':
                    break
                time.sleep(1)
                container.reload()
                health = container.attrs['State'].get('Health', {}).get('Status')
            
            assert health == 'healthy', f"❌ FAIL: {container_name} not healthy (status: {health})"
        
        print("✅ PASS: All containers healthy")
    
    def test_04_CRITICAL_backend_responds(self):
        """FAIL-PASS: Backend must respond to health check"""
        response = requests.get("http://localhost:8001/health", timeout=10)
        assert response.status_code == 200, f"❌ FAIL: Backend returned {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "healthy", f"❌ FAIL: Backend unhealthy: {data}"
        
        print("✅ PASS: Backend responding and healthy")
    
    def test_05_CRITICAL_postgres_accessible(self):
        """FAIL-PASS: PostgreSQL must be accessible"""
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port=5401,
            database="orchestrator_agent01",
            user="agent01",
            password="agent01_secure_password"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        assert result[0] == 1, "❌ FAIL: PostgreSQL query failed"
        
        cursor.close()
        conn.close()
        
        print("✅ PASS: PostgreSQL accessible and responding")
    
    def test_06_CRITICAL_redis_accessible(self):
        """FAIL-PASS: Redis must be accessible"""
        import redis
        
        r = redis.Redis(
            host="localhost",
            port=6301,
            password="agent01_redis_password",
            decode_responses=True
        )
        
        r.set("bootstrap_test", "success")
        value = r.get("bootstrap_test")
        
        assert value == "success", "❌ FAIL: Redis read/write failed"
        
        r.delete("bootstrap_test")
        
        print("✅ PASS: Redis accessible and functioning")
    
    def test_07_CRITICAL_network_isolation(self, docker_client):
        """FAIL-PASS: Network must be isolated"""
        network = docker_client.networks.get("agent01_network")
        containers = network.attrs["Containers"]
        
        assert len(containers) == 11, f"❌ FAIL: Expected 11 containers on network, found {len(containers)}"
        
        print("✅ PASS: Network isolation correct (11 containers)")
    
    def test_08_CRITICAL_data_persistence(self, docker_client):
        """FAIL-PASS: Data directories must exist"""
        import os
        
        required_dirs = [
            "./data/agent01/postgres",
            "./data/agent01/neo4j",
            "./data/agent01/redis",
            "./data/agent01/ollama"
        ]
        
        for dir_path in required_dirs:
            assert os.path.exists(dir_path), f"❌ FAIL: {dir_path} does not exist"
        
        print("✅ PASS: All data directories exist")

# Run with: AGENT_ID=01 pytest tests/agent01/test_bootstrap.py -v
```

## ✅ SUCCESS CRITERIA

Agent 01 is OPERATIONAL when:
- [ ] ALL 8 bootstrap tests PASS
- [ ] `docker ps` shows 11 containers running
- [ ] `curl http://localhost:8001/health` returns 200
- [ ] `./scripts/health-check.sh 01` reports all healthy
- [ ] No error logs in any container

## ⚠️ FAIL CONDITIONS

Agent 01 has FAILED if:
- ❌ Any bootstrap test fails
- ❌ Any container exits/restarts repeatedly
- ❌ Any health check fails after 2 minutes
- ❌ Backend returns 500 errors
- ❌ Ports conflict with other agents

## 🚀 INTEGRATION CHECKLIST

Before requesting integration:
- [ ] All bootstrap tests pass
- [ ] Documentation complete (README.md)
- [ ] Committed to agent-01-infrastructure branch
- [ ] PR created to develop
- [ ] No security features (MVP)

## 📚 REFERENCE

Full specification: agent-implementation-modules/01-INFRASTRUCTURE-AGENT/COMPLETE-AGENT-01-SPECIFICATION.md

---

**BEGIN IMPLEMENTATION. REPORT BOOTSTRAP TEST RESULTS.**
```

---

# AGENT 02: DATABASE

## Complete Bootstrap Prompt

```markdown
# AGENT 02: DATABASE - BOOTSTRAP IMPLEMENTATION

## Your Mission
You are Agent 02: Database. You design and implement all database schemas for the system.

## Isolation Guarantee
- Branch: agent-02-database
- Ports: 8002, 5402, 7402, 7432, 8062, 6332, 6302
- Network: agent02_network
- Database: orchestrator_agent02
- Data: ./data/agent02/

**NO OTHER AGENT CAN INTERFERE WITH YOUR WORK**

## Phase 1: PostgreSQL Schema (4 hours)

Create backend/database/migrations/init.sql with:

```sql
-- Extension for UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    input JSONB NOT NULL,
    output JSONB,
    parameters JSONB,
    metadata JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    agent_id VARCHAR(20),
    parent_task_id UUID REFERENCES tasks(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(type);
CREATE INDEX idx_tasks_created ON tasks(created_at DESC);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'idle',
    capabilities JSONB DEFAULT '[]'::jsonb,
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_name ON metrics(name);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);

-- Learning experiences table
CREATE TABLE IF NOT EXISTS learning_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(20) REFERENCES agents(id),
    task_id UUID REFERENCES tasks(id),
    experience_type VARCHAR(50) NOT NULL,
    success BOOLEAN NOT NULL,
    confidence DOUBLE PRECISION,
    learning_points JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Phase 2: SQLAlchemy Models (4 hours)

Create backend/app/models/database.py with complete models:
- Task model
- Agent model
- Metric model
- LearningExperience model

Each with:
- All fields
- Relationships
- to_dict() method
- Validators

## Phase 3: Alembic Migrations (2 hours)

Setup Alembic and create initial migration

## ✅ BOOTSTRAP FAIL-PASS TESTS (CRITICAL)

Create tests/agent02/test_bootstrap.py:

```python
import pytest
from sqlalchemy import text

@pytest.mark.agent02
class TestAgent02Bootstrap:
    """Bootstrap fail-pass tests for Agent 02"""
    
    async def test_01_CRITICAL_postgres_connection(self, db_service):
        """FAIL-PASS: PostgreSQL must be accessible"""
        health = await db_service.health_check()
        assert health["status"] == "healthy", "❌ FAIL: PostgreSQL not accessible"
        print("✅ PASS: PostgreSQL accessible")
    
    async def test_02_CRITICAL_all_tables_exist(self, db_session):
        """FAIL-PASS: All required tables must exist"""
        required_tables = [
            'tasks', 'agents', 'metrics', 'learning_experiences'
        ]
        
        async with db_session() as session:
            result = await session.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]
        
        for table in required_tables:
            assert table in tables, f"❌ FAIL: Table {table} missing"
        
        print(f"✅ PASS: All {len(required_tables)} tables exist")
    
    async def test_03_CRITICAL_indexes_exist(self, db_session):
        """FAIL-PASS: Performance indexes must exist"""
        required_indexes = [
            'idx_tasks_status',
            'idx_tasks_type',
            'idx_tasks_created',
            'idx_metrics_name',
            'idx_metrics_timestamp'
        ]
        
        async with db_session() as session:
            result = await session.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE schemaname = 'public'
            """))
            indexes = [row[0] for row in result]
        
        for index in required_indexes:
            assert index in indexes, f"❌ FAIL: Index {index} missing"
        
        print(f"✅ PASS: All {len(required_indexes)} indexes exist")
    
    async def test_04_CRITICAL_crud_operations(self, db_service):
        """FAIL-PASS: CRUD operations must work"""
        # Create
        task_id = await db_service.create("tasks", {
            "type": "test",
            "input": {"test": "data"}
        })
        assert task_id, "❌ FAIL: Create failed"
        
        # Read
        task = await db_service.read("tasks", task_id)
        assert task, "❌ FAIL: Read failed"
        assert task["type"] == "test", "❌ FAIL: Data mismatch"
        
        # Update
        success = await db_service.update("tasks", task_id, {"status": "completed"})
        assert success, "❌ FAIL: Update failed"
        
        # Delete
        success = await db_service.delete("tasks", task_id)
        assert success, "❌ FAIL: Delete failed"
        
        print("✅ PASS: CRUD operations working")
    
    async def test_05_CRITICAL_foreign_keys_enforced(self, db_session):
        """FAIL-PASS: Foreign key constraints must work"""
        with pytest.raises(Exception):
            async with db_session() as session:
                await session.execute(text("""
                    INSERT INTO tasks (type, input, agent_id)
                    VALUES ('test', '{}', 'nonexistent_agent')
                """))
                await session.commit()
        
        print("✅ PASS: Foreign key constraints enforced")
    
    async def test_06_CRITICAL_triggers_working(self, db_session):
        """FAIL-PASS: updated_at triggers must work"""
        async with db_session() as session:
            # Insert task
            result = await session.execute(text("""
                INSERT INTO tasks (type, input)
                VALUES ('test', '{"data": "test"}')
                RETURNING id, updated_at
            """))
            task_id, first_updated = result.fetchone()
            await session.commit()
            
            # Wait briefly
            import asyncio
            await asyncio.sleep(0.1)
            
            # Update task
            await session.execute(text("""
                UPDATE tasks SET status = 'completed'
                WHERE id = :id
            """), {"id": task_id})
            await session.commit()
            
            # Check updated_at changed
            result = await session.execute(text("""
                SELECT updated_at FROM tasks WHERE id = :id
            """), {"id": task_id})
            second_updated = result.fetchone()[0]
            
            assert second_updated > first_updated, "❌ FAIL: updated_at not updating"
        
        print("✅ PASS: Triggers working")
    
    async def test_07_CRITICAL_neo4j_accessible(self, neo4j_driver):
        """FAIL-PASS: Neo4j must be accessible"""
        with neo4j_driver.session() as session:
            result = session.run("RETURN 1 AS num")
            value = result.single()["num"]
            assert value == 1, "❌ FAIL: Neo4j query failed"
        
        print("✅ PASS: Neo4j accessible")
    
    async def test_08_CRITICAL_models_importable(self):
        """FAIL-PASS: SQLAlchemy models must import"""
        from app.models.database import Task, Agent, Metric, LearningExperience
        
        assert Task, "❌ FAIL: Task model not importable"
        assert Agent, "❌ FAIL: Agent model not importable"
        assert Metric, "❌ FAIL: Metric model not importable"
        assert LearningExperience, "❌ FAIL: LearningExperience model not importable"
        
        print("✅ PASS: All models importable")

# Run with: AGENT_ID=02 pytest tests/agent02/test_bootstrap.py -v
```

## ✅ SUCCESS CRITERIA

Agent 02 is OPERATIONAL when:
- [ ] ALL 8 bootstrap tests PASS
- [ ] All tables created
- [ ] All indexes created
- [ ] CRUD operations work
- [ ] Foreign keys enforced
- [ ] Neo4j accessible

## ⚠️ FAIL CONDITIONS

Agent 02 has FAILED if:
- ❌ Any bootstrap test fails
- ❌ Schema creation errors
- ❌ Missing tables or indexes
- ❌ Foreign key violations not caught
- ❌ CRUD operations fail

## 🚀 INTEGRATION CHECKLIST

- [ ] All bootstrap tests pass
- [ ] Alembic migrations working
- [ ] Documentation complete
- [ ] Committed to agent-02-database
- [ ] PR created

## 📚 REFERENCE

Full specification: agent-implementation-modules/02-DATABASE-AGENT/COMPLETE-AGENT-02-SPECIFICATION.md

---

**BEGIN IMPLEMENTATION. REPORT BOOTSTRAP TEST RESULTS.**
```

---

# AGENT 03: CORE ENGINE

## Complete Bootstrap Prompt

```markdown
# AGENT 03: CORE ENGINE - BOOTSTRAP IMPLEMENTATION

## Your Mission
You are Agent 03: Core Engine. You implement the task processing and execution engine.

## Isolation Guarantee
- Branch: agent-03-core-engine
- Ports: 8003, 5403, 6303, 7403
- Network: agent03_network
- Database: orchestrator_agent03

## Phase 1: Task Decomposer (6 hours)

Implement app/core/task_decomposer.py with:
- analyze_complexity()
- decompose()
- build_dependency_graph()
- get_parallel_tasks()

## Phase 2: Execution Engine (6 hours)

Implement app/core/execution_engine.py with:
- execute_task()
- execute_simple_task()
- execute_complex_task()
- retry_task()

## Phase 3: Caching Layer (2 hours)

Implement app/services/cache_service.py

## ✅ BOOTSTRAP FAIL-PASS TESTS (CRITICAL)

```python
@pytest.mark.agent03
class TestAgent03Bootstrap:
    
    async def test_01_CRITICAL_simple_task_not_decomposed(self, task_decomposer):
        """FAIL-PASS: Simple tasks must not decompose"""
        subtasks, graph = task_decomposer.decompose(
            "simple_task",
            {"data": "test"},
            {}
        )
        
        assert len(subtasks) == 1, f"❌ FAIL: Simple task decomposed to {len(subtasks)}"
        print("✅ PASS: Simple tasks not decomposed")
    
    async def test_02_CRITICAL_complex_task_decomposed(self, task_decomposer):
        """FAIL-PASS: Complex tasks must decompose"""
        subtasks, graph = task_decomposer.decompose(
            "data_processing",
            {"data": "x" * 1000},
            {}
        )
        
        assert len(subtasks) > 1, "❌ FAIL: Complex task not decomposed"
        assert graph.number_of_nodes() > 0, "❌ FAIL: No dependency graph"
        print(f"✅ PASS: Complex task decomposed to {len(subtasks)} subtasks")
    
    async def test_03_CRITICAL_dependency_graph_valid(self, task_decomposer):
        """FAIL-PASS: Dependency graph must be valid DAG"""
        import networkx as nx
        
        subtasks, graph = task_decomposer.decompose(
            "multi_step",
            {"data": "test"},
            {"steps": ["step1", "step2", "step3"]}
        )
        
        assert nx.is_directed_acyclic_graph(graph), "❌ FAIL: Graph has cycles"
        print("✅ PASS: Dependency graph is valid DAG")
    
    async def test_04_CRITICAL_execution_engine_works(self, db, execution_engine):
        """FAIL-PASS: Execution engine must execute tasks"""
        from app.models.database import Task
        
        task = Task(
            type="test_task",
            input={"data": "test"},
            status="pending"
        )
        db.add(task)
        await db.commit()
        
        result = await execution_engine.execute_task(db, task)
        
        assert result["status"] == "success", f"❌ FAIL: Execution failed: {result}"
        assert task.status == "completed", f"❌ FAIL: Task status: {task.status}"
        print("✅ PASS: Execution engine works")
    
    async def test_05_CRITICAL_cache_works(self, cache_service):
        """FAIL-PASS: Caching must work"""
        await cache_service.set("test_key", {"value": 123}, ttl=60)
        result = await cache_service.get("test_key")
        
        assert result == {"value": 123}, f"❌ FAIL: Cache returned {result}"
        print("✅ PASS: Caching works")
    
    async def test_06_CRITICAL_parallel_execution(self, execution_engine, task_decomposer):
        """FAIL-PASS: Parallel execution must be faster"""
        import time
        
        subtasks, graph = task_decomposer.decompose(
            "data_processing",
            {"data": "x" * 5000},
            {}
        )
        
        parallel_groups = task_decomposer.get_parallel_tasks(graph)
        
        assert len(parallel_groups) > 1, "❌ FAIL: No parallelization detected"
        print(f"✅ PASS: {len(parallel_groups)} parallel execution groups")

# Run with: AGENT_ID=03 pytest tests/agent03/test_bootstrap.py -v
```

## ✅ SUCCESS CRITERIA

- [ ] ALL 6 bootstrap tests PASS
- [ ] Task decomposition working
- [ ] Execution engine functional
- [ ] Caching operational
- [ ] Parallel execution proven

## 📚 REFERENCE

Full specification: agent-implementation-modules/03-CORE-ENGINE-AGENT/COMPLETE-AGENT-03-SPECIFICATION.md

---

**BEGIN IMPLEMENTATION. REPORT BOOTSTRAP TEST RESULTS.**
```

---

# AGENT 06: AGENT FRAMEWORK (CORE INNOVATION)

## Complete Bootstrap Prompt

```markdown
# AGENT 06: AGENT FRAMEWORK - BOOTSTRAP IMPLEMENTATION

## Your Mission
You are Agent 06: Agent Framework. You implement the multi-agent system with META-RECURSIVE SELF-LEARNING. THIS IS THE CORE INNOVATION.

## Isolation Guarantee
- Branch: agent-06-agent-framework
- Ports: 8006, 5406, 6306, 7406, 11406
- Network: agent06_network
- Database: orchestrator_agent06

## Phase 1: BaseAgent Class (4 hours)

Implement app/agents/base_agent.py

## Phase 2: Specialist Agents (8 hours)

Implement:
- app/agents/nlp_agent.py
- app/agents/code_agent.py
- app/agents/data_agent.py
- app/agents/research_agent.py

## Phase 3: Orchestrator Agent (4 hours)

Implement app/agents/orchestrator_agent.py

## Phase 4: Meta-Learner Agent (8 hours) ⭐ CORE INNOVATION

Implement app/agents/meta_learner_agent.py with:
- continuous_learning_loop()
- _analyze_performance()
- _generate_hypotheses()
- _run_experiment()
- _validate_improvement()
- _deploy_optimization() ← META-RECURSION

## Phase 5: Agent Registry (2 hours)

Implement app/agents/agent_registry.py

## ✅ BOOTSTRAP FAIL-PASS TESTS (CRITICAL)

```python
@pytest.mark.agent06
class TestAgent06Bootstrap:
    
    async def test_01_CRITICAL_base_agent_executes(self):
        """FAIL-PASS: BaseAgent must execute tasks"""
        from app.agents.nlp_agent import NLPAgent
        
        agent = NLPAgent()
        result = await agent.execute_task(
            "task_001",
            "text_analysis",
            {"text": "Test text"}
        )
        
        assert result["success"] is True, f"❌ FAIL: {result.get('error')}"
        assert agent.tasks_completed == 1, "❌ FAIL: Task count not incremented"
        print("✅ PASS: BaseAgent executes tasks")
    
    async def test_02_CRITICAL_specialist_agents_work(self):
        """FAIL-PASS: All specialist agents must work"""
        from app.agents.nlp_agent import NLPAgent
        from app.agents.code_agent import CodeAgent
        from app.agents.data_agent import DataAgent
        from app.agents.research_agent import ResearchAgent
        
        agents = [NLPAgent(), CodeAgent(), DataAgent(), ResearchAgent()]
        
        for agent in agents:
            result = await agent.execute_task(
                f"task_{agent.agent_id}",
                agent.supported_tasks[0] if hasattr(agent, 'supported_tasks') else "test",
                {"test": "data"}
            )
            assert result["success"], f"❌ FAIL: {agent.name} failed"
        
        print("✅ PASS: All 4 specialist agents work")
    
    async def test_03_CRITICAL_orchestrator_coordinates(self, orchestrator):
        """FAIL-PASS: Orchestrator must coordinate tasks"""
        result = await orchestrator.execute_task(
            "orch_001",
            "multi_step",
            {"data": "test"},
            {"steps": ["analyze", "process", "summarize"]}
        )
        
        assert result["success"] is True, f"❌ FAIL: Orchestration failed"
        assert "orchestrated" in result["result"], "❌ FAIL: Not orchestrated"
        print("✅ PASS: Orchestrator coordinates tasks")
    
    async def test_04_CRITICAL_meta_learner_analyzes(self, meta_learner):
        """FAIL-PASS: Meta-learner must analyze performance"""
        analysis = await meta_learner.process_task(
            "analyze_performance",
            {}
        )
        
        assert "optimization_opportunities" in analysis, "❌ FAIL: No analysis output"
        print("✅ PASS: Meta-learner analyzes performance")
    
    async def test_05_CRITICAL_meta_learner_generates_hypotheses(self, meta_learner):
        """FAIL-PASS: Meta-learner must generate hypotheses"""
        hypotheses = await meta_learner.process_task(
            "generate_hypotheses",
            {}
        )
        
        assert len(hypotheses["hypotheses"]) > 0, "❌ FAIL: No hypotheses generated"
        print(f"✅ PASS: Meta-learner generated {len(hypotheses['hypotheses'])} hypotheses")
    
    async def test_06_CRITICAL_meta_recursion_proven(self, meta_learner):
        """FAIL-PASS: Meta-recursive loop must work (CORE INNOVATION)"""
        # This proves the system can improve itself
        
        # Generate hypothesis
        hypotheses = await meta_learner.process_task("generate_hypotheses", {})
        hypothesis = hypotheses["hypotheses"][0]
        
        # Run experiment
        experiment = await meta_learner.process_task("run_experiment", hypothesis)
        
        assert experiment["success"] is True, "❌ FAIL: Experiment failed"
        assert "improvement_percent" in experiment, "❌ FAIL: No improvement measured"
        
        # Validate
        validation = await meta_learner.process_task("validate_improvement", experiment)
        
        assert "validated" in validation, "❌ FAIL: No validation result"
        
        # If validated, system would deploy (meta-recursion)
        if validation["validated"]:
            deploy = await meta_learner.process_task("deploy_optimization", validation)
            assert deploy["deployed"] is True, "❌ FAIL: Deployment failed"
        
        print("✅ PASS: META-RECURSIVE LOOP PROVEN - SYSTEM CAN IMPROVE ITSELF")
    
    async def test_07_CRITICAL_agent_registry_works(self, agent_registry):
        """FAIL-PASS: Agent registry must route correctly"""
        agent = agent_registry.get_agent_for_task("text_analysis")
        
        assert agent is not None, "❌ FAIL: No agent found"
        assert "nlp" in agent.agent_id.lower(), "❌ FAIL: Wrong agent selected"
        print("✅ PASS: Agent registry routes correctly")
    
    async def test_08_CRITICAL_parallel_agent_execution(self, agent_registry):
        """FAIL-PASS: Multiple agents must execute in parallel"""
        import asyncio
        
        tasks = [
            ("text_analysis", {"text": f"Text {i}"})
            for i in range(5)
        ]
        
        results = await asyncio.gather(*[
            agent_registry.get_agent_for_task(t[0]).execute_task(f"t{i}", t[0], t[1])
            for i, t in enumerate(tasks)
        ])
        
        assert all(r["success"] for r in results), "❌ FAIL: Some agents failed"
        print("✅ PASS: Parallel agent execution works")

# Run with: AGENT_ID=06 pytest tests/agent06/test_bootstrap.py -v
```

## ✅ SUCCESS CRITERIA (MOST CRITICAL)

- [ ] ALL 8 bootstrap tests PASS
- [ ] Meta-recursive loop proven (test_06)
- [ ] System demonstrates self-improvement capability
- [ ] All specialist agents operational
- [ ] Orchestration functional

## ⚠️ FAIL CONDITIONS

- ❌ Meta-recursion test fails (CRITICAL)
- ❌ Any agent cannot execute
- ❌ Orchestrator fails
- ❌ Registry cannot route

## 📚 REFERENCE

Full specification: agent-implementation-modules/06-AGENT-FRAMEWORK-AGENT/COMPLETE-AGENT-06-SPECIFICATION.md

---

**BEGIN IMPLEMENTATION. REPORT BOOTSTRAP TEST RESULTS. THIS IS THE CORE INNOVATION.**
```

---

# REMAINING AGENTS (07-11)

## Agent 07: LLM Integration

```markdown
# AGENT 07: LLM INTEGRATION - BOOTSTRAP TESTS

async def test_01_CRITICAL_ollama_accessible():
    """Ollama must respond"""
    health = await ollama_service.health_check()
    assert health["status"] == "healthy"

async def test_02_CRITICAL_models_downloaded():
    """All 4 models must exist"""
    models = await ollama_service.list_models()
    required = ["llama3.2", "mixtral", "qwen2.5-coder", "deepseek-r1"]
    for model in required:
        assert model in [m["name"] for m in models]

async def test_03_CRITICAL_inference_works():
    """Must generate text"""
    result = await ollama_service.generate("Say hello", model="llama3.2")
    assert result["success"] is True
    assert len(result["text"]) > 0

# Reference: agent-implementation-modules/07-LLM-INTEGRATION-AGENT/
```

## Agent 04: API Layer

```markdown
# AGENT 04: API LAYER - BOOTSTRAP TESTS

async def test_01_CRITICAL_create_task_endpoint():
    """Must create tasks"""
    response = client.post("/tasks", json={"type": "test", "input": {}})
    assert response.status_code == 200

async def test_02_CRITICAL_websocket_connects():
    """WebSocket must connect"""
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data is not None

# Reference: agent-implementation-modules/AGENTS-04-05-08-09-10-11-COMPLETE-SPECS.md
```

## Agent 05: Frontend

```markdown
# AGENT 05: FRONTEND - BOOTSTRAP TESTS (Playwright)

test('task submission works', async ({ page }) => {
    await page.goto('http://localhost:3005')
    await page.fill('textarea', 'Test input')
    await page.click('button:has-text("Submit")')
    await expect(page.locator('.result')).toBeVisible()
})

# Reference: agent-implementation-modules/AGENTS-04-05-08-09-10-11-COMPLETE-SPECS.md
```

## Agent 08: Monitoring

```markdown
# AGENT 08: MONITORING - BOOTSTRAP TESTS

async def test_01_CRITICAL_prometheus_collecting():
    """Prometheus must collect metrics"""
    response = requests.get("http://localhost:9008/api/v1/query?query=up")
    assert response.status_code == 200

async def test_02_CRITICAL_grafana_accessible():
    """Grafana must be accessible"""
    response = requests.get("http://localhost:3108/api/health")
    assert response.status_code == 200
```

## Agent 09: Testing

```markdown
# AGENT 09: TESTING - BOOTSTRAP TESTS

def test_01_CRITICAL_pytest_configured():
    """Pytest must be configured"""
    assert os.path.exists("pytest.ini")

def test_02_CRITICAL_all_agent_tests_exist():
    """Tests must exist for all agents"""
    for i in range(1, 12):
        assert os.path.exists(f"tests/agent{i:02d}")
```

## Agent 10: Documentation

```markdown
# AGENT 10: DOCUMENTATION - BOOTSTRAP TESTS

def test_01_CRITICAL_readme_exists():
    """README must exist"""
    assert os.path.exists("README.md")

def test_02_CRITICAL_api_docs_generated():
    """API docs must be generated"""
    response = requests.get("http://localhost:8000/docs")
    assert response.status_code == 200
```

## Agent 11: Deployment

```markdown
# AGENT 11: DEPLOYMENT - BOOTSTRAP TESTS

def test_01_CRITICAL_github_actions_configured():
    """CI/CD must be configured"""
    assert os.path.exists(".github/workflows/ci-cd.yml")

def test_02_CRITICAL_docker_compose_valid():
    """Docker compose must be valid"""
    result = subprocess.run(["docker-compose", "config"], capture_output=True)
    assert result.returncode == 0
```

---

# SUMMARY OF BOOTSTRAP METHODOLOGY

## For Each Agent

**1. Implement Functionality** (according to specification)

**2. Run Bootstrap Tests**
```bash
AGENT_ID=XX pytest tests/agentXX/test_bootstrap.py -v
```

**3. Interpret Results**

✅ **ALL TESTS PASS** → Agent is OPERATIONAL → Proceed to integration

❌ **ANY TEST FAILS** → Agent has FAILED → Fix issues, re-test, do NOT proceed

**4. Report Results**

"Agent XX Bootstrap: X/Y tests passed. Status: OPERATIONAL/FAILED"

**5. Integration Only After Bootstrap Pass**

No agent proceeds to integration until bootstrap tests pass.

---

# BOOTSTRAP TEST EXECUTION ORDER

## Week 1-2
1. Agent 01 bootstrap tests → MUST PASS
2. Agent 02 bootstrap tests → MUST PASS

## Week 3-5
3. Agent 03 bootstrap tests → MUST PASS
4. Agent 06 bootstrap tests → MUST PASS (CRITICAL - Core Innovation)
5. Agent 07 bootstrap tests → MUST PASS
6. Agent 08 bootstrap tests → MUST PASS

## Week 6-8
7. Agent 04 bootstrap tests → MUST PASS
8. Agent 05 bootstrap tests → MUST PASS
9. Agent 09 bootstrap tests → MUST PASS

## Week 9-10
10. Agent 10 bootstrap tests → MUST PASS
11. Agent 11 bootstrap tests → MUST PASS

---

# FAILURE HANDLING

## If Bootstrap Tests Fail

**DO:**
- ✅ Review test output carefully
- ✅ Fix the identified issue
- ✅ Re-run bootstrap tests
- ✅ Repeat until all pass
- ✅ Document what was fixed

**DO NOT:**
- ❌ Skip failed tests
- ❌ Proceed to integration
- ❌ Mark as "mostly working"
- ❌ Blame the test
- ❌ Modify test to pass without fixing issue

---

# SUCCESS METRICS

## MVP is Ready When

- [ ] ALL 11 agents have ALL bootstrap tests passing
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Meta-recursive loop demonstrated (Agent 06)
- [ ] System improves itself by >10%

---

**Document Version:** 1.0  
**Created:** 2025-10-30  
**Purpose:** Fail-Pass Bootstrap Prompts for All Agents  
**Status:** COMPLETE  

**BOOTSTRAP TESTS ENSURE QUALITY FROM GROUND UP** ✅

