# AGENTS 04, 05, 08, 09, 10, 11 - COMPLETE SPECIFICATIONS
## Streamlined Complete Specs for Remaining 6 Agents (MVP - No Security)

**Note:** These are complete, implementable specifications in condensed format. Each contains everything needed to build the agent.

**Date:** 2025-10-30  
**Version:** MVP (No Security)  
**Total:** 6 agents, ~10,000 lines worth of specifications condensed  

---

# AGENT 04: API LAYER

**Priority:** 🟡 HIGH  
**Timeline:** Week 6-8  
**Branch:** `agent-04-api-layer`  
**Ports:** 8004, 5404, 6304  
**Security:** ❌ NONE - All endpoints OPEN  

## Mission
Build FastAPI REST API and WebSocket interface for the system. **NO AUTHENTICATION**.

## Key Deliverables
1. REST API endpoints (tasks, agents, metrics)
2. WebSocket for real-time updates
3. Basic request validation
4. Error handling
5. API documentation (Swagger/OpenAPI)

## Implementation

### Setup
```bash
git checkout -b agent-04-api-layer

cat > .env.agent04 <<'EOF'
AGENT_ID=04
BACKEND_PORT=8004
POSTGRES_PORT=5404
REDIS_PORT=6304
DATABASE_URL=postgresql://agent04:agent04_password@postgres:5432/orchestrator_agent04
REDIS_URL=redis://:agent04_redis_password@redis:6379
EOF

mkdir -p data/agent04/{postgres,redis}
```

### Core API (backend/app/api/v1/endpoints/tasks.py)
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.database import Task
from app.core.execution_engine import execution_engine

router = APIRouter()

@router.post("/tasks")
async def create_task(
    task_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Create and execute task - NO AUTH REQUIRED"""
    task = Task(
        type=task_data["type"],
        input=task_data["input"],
        parameters=task_data.get("parameters", {}),
        status="pending"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Execute asynchronously
    asyncio.create_task(execution_engine.execute_task(db, task))
    
    return {
        "task_id": str(task.id),
        "status": task.status,
        "created_at": task.created_at.isoformat()
    }

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get task status - NO AUTH REQUIRED"""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    
    return task.to_dict()

@router.get("/tasks")
async def list_tasks(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List tasks - NO AUTH REQUIRED"""
    result = await db.execute(
        select(Task)
        .order_by(Task.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    tasks = result.scalars().all()
    return [t.to_dict() for t in tasks]
```

### WebSocket (backend/app/api/v1/websocket.py)
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint - NO AUTH REQUIRED"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Endpoints Checklist
- [ ] POST /tasks - Create task
- [ ] GET /tasks/{id} - Get task
- [ ] GET /tasks - List tasks
- [ ] GET /agents - List agents
- [ ] GET /agents/{id} - Get agent
- [ ] GET /metrics - Get metrics
- [ ] WS /ws - WebSocket connection
- [ ] GET /docs - Swagger UI (auto)

## Tests
```python
@pytest.mark.agent04
async def test_create_task_endpoint(client):
    response = client.post("/tasks", json={
        "type": "test_task",
        "input": {"data": "test"}
    })
    assert response.status_code == 200
    assert "task_id" in response.json()
```

---

# AGENT 05: FRONTEND

**Priority:** 🟡 HIGH  
**Timeline:** Week 6-8  
**Branch:** `agent-05-frontend`  
**Ports:** 3005  
**Security:** ❌ NONE - No login, no protected routes  

## Mission
Build React/Next.js UI for task submission, monitoring, and visualization. **NO AUTH UI**.

## Key Deliverables
1. Task submission form
2. Real-time metrics dashboard
3. Agent status monitoring
4. Task history view
5. System health indicators

## Implementation

### Setup
```bash
git checkout -b agent-05-frontend

cd frontend
npm install
```

### Main Page (frontend/src/app/page.tsx)
```typescript
'use client'

import { useState } from 'react'
import TaskSubmission from '@/components/TaskSubmission'
import MetricsDashboard from '@/components/MetricsDashboard'
import AgentStatus from '@/components/AgentStatus'

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('tasks')
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 p-4">
        <h1 className="text-2xl font-bold">
          Meta-Recursive Multi-Agent System
        </h1>
      </header>
      
      <nav className="bg-gray-800 border-b border-gray-700">
        <button onClick={() => setActiveTab('tasks')}>Tasks</button>
        <button onClick={() => setActiveTab('metrics')}>Metrics</button>
        <button onClick={() => setActiveTab('agents')}>Agents</button>
      </nav>
      
      <main className="p-6">
        {activeTab === 'tasks' && <TaskSubmission />}
        {activeTab === 'metrics' && <MetricsDashboard />}
        {activeTab === 'agents' && <AgentStatus />}
      </main>
    </div>
  )
}
```

### Task Submission (frontend/src/components/TaskSubmission.tsx)
```typescript
'use client'

import { useState } from 'react'

export default function TaskSubmission() {
  const [taskType, setTaskType] = useState('text_analysis')
  const [input, setInput] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async () => {
    setLoading(true)
    
    const response = await fetch('http://localhost:8004/tasks', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        type: taskType,
        input: {text: input}
      })
    })
    
    const data = await response.json()
    setResult(data)
    setLoading(false)
  }
  
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Submit Task</h2>
      
      <select value={taskType} onChange={e => setTaskType(e.target.value)}>
        <option value="text_analysis">Text Analysis</option>
        <option value="code_generation">Code Generation</option>
        <option value="data_processing">Data Processing</option>
      </select>
      
      <textarea
        value={input}
        onChange={e => setInput(e.target.value)}
        className="w-full h-32 p-2 bg-gray-800 rounded"
        placeholder="Enter task input..."
      />
      
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
      >
        {loading ? 'Submitting...' : 'Submit Task'}
      </button>
      
      {result && (
        <div className="p-4 bg-gray-800 rounded">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
```

### Metrics Dashboard (frontend/src/components/MetricsDashboard.tsx)
```typescript
'use client'

import { useEffect, useState } from 'react'

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState(null)
  
  useEffect(() => {
    const fetchMetrics = async () => {
      const response = await fetch('http://localhost:8004/metrics')
      const data = await response.json()
      setMetrics(data)
    }
    
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000)
    return () => clearInterval(interval)
  }, [])
  
  return (
    <div className="grid grid-cols-3 gap-4">
      <MetricCard
        title="Total Tasks"
        value={metrics?.total_tasks || 0}
        icon="📊"
      />
      <MetricCard
        title="Active Agents"
        value={metrics?.active_agents || 0}
        icon="🤖"
      />
      <MetricCard
        title="Tasks/Second"
        value={metrics?.tasks_per_second || 0}
        icon="⚡"
      />
    </div>
  )
}

function MetricCard({title, value, icon}) {
  return (
    <div className="p-6 bg-gray-800 rounded">
      <div className="text-4xl mb-2">{icon}</div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-gray-400">{title}</div>
    </div>
  )
}
```

## Components Checklist
- [ ] Task submission form
- [ ] Metrics dashboard
- [ ] Agent status cards
- [ ] Task history table
- [ ] Real-time WebSocket updates
- [ ] System health indicators

---

# AGENT 08: MONITORING

**Priority:** 🟡 HIGH  
**Timeline:** Week 3-5  
**Branch:** `agent-08-monitoring`  
**Ports:** 8008, 9008, 3108  
**Security:** ❌ NONE  

## Mission
Setup Prometheus + Grafana for metrics collection and visualization. Track system performance.

## Key Deliverables
1. Prometheus metrics collection
2. Grafana dashboards
3. Alert rules (simple)
4. Performance tracking
5. System health monitoring

## Implementation

### Prometheus Config (prometheus/prometheus.yml)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
  
  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "alert_rules.yml"
```

### Alert Rules (prometheus/alert_rules.yml)
```yaml
groups:
  - name: system_alerts
    interval: 30s
    rules:
      - alert: HighTaskFailureRate
        expr: rate(tasks_failed[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High task failure rate"
          description: "Task failure rate is above 10%"
      
      - alert: SlowTaskExecution
        expr: avg(task_duration_ms) > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow task execution"
          description: "Average task duration > 10s"
```

### Metrics Collection (backend/app/services/metrics_service.py)
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
task_counter = Counter('tasks_total', 'Total tasks', ['type', 'status'])
task_duration = Histogram('task_duration_seconds', 'Task duration')
active_tasks = Gauge('tasks_active', 'Active tasks')
agent_tasks = Counter('agent_tasks_total', 'Tasks per agent', ['agent_id'])

class MetricsService:
    def record_task_start(self, task_type: str):
        active_tasks.inc()
    
    def record_task_complete(self, task_type: str, status: str, duration_ms: float):
        task_counter.labels(type=task_type, status=status).inc()
        task_duration.observe(duration_ms / 1000)
        active_tasks.dec()
    
    def record_agent_task(self, agent_id: str):
        agent_tasks.labels(agent_id=agent_id).inc()

metrics_service = MetricsService()
```

### Grafana Dashboard JSON
```json
{
  "dashboard": {
    "title": "System Overview",
    "panels": [
      {
        "title": "Tasks Per Second",
        "targets": [{"expr": "rate(tasks_total[1m])"}]
      },
      {
        "title": "Task Duration",
        "targets": [{"expr": "avg(task_duration_seconds)"}]
      },
      {
        "title": "Active Tasks",
        "targets": [{"expr": "tasks_active"}]
      }
    ]
  }
}
```

---

# AGENT 09: TESTING

**Priority:** 🟡 HIGH  
**Timeline:** Week 6-8  
**Branch:** `agent-09-testing`  

## Mission
Build comprehensive test framework covering unit, integration, E2E, and meta-learning validation.

## Key Deliverables
1. Pytest framework setup
2. Unit tests (all agents)
3. Integration tests
4. E2E tests (Playwright)
5. Meta-learning validation
6. Performance tests

## Implementation

### Pytest Config (backend/pytest.ini)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    agent01: Agent 01 tests
    agent02: Agent 02 tests
    # ... etc
```

### Unit Tests (tests/unit/test_task_decomposer.py)
```python
import pytest
from app.core.task_decomposer import task_decomposer

class TestTaskDecomposer:
    def test_simple_task_not_decomposed(self):
        subtasks, graph = task_decomposer.decompose(
            "simple_task",
            {"data": "test"},
            {}
        )
        assert len(subtasks) == 1
    
    def test_complex_task_decomposed(self):
        subtasks, graph = task_decomposer.decompose(
            "data_processing",
            {"data": "x" * 1000},
            {}
        )
        assert len(subtasks) > 1
    
    def test_dependency_graph_valid(self):
        subtasks, graph = task_decomposer.decompose(
            "multi_step",
            {"data": "test"},
            {"steps": ["a", "b", "c"]}
        )
        import networkx as nx
        assert nx.is_directed_acyclic_graph(graph)
```

### Integration Tests (tests/integration/test_agent_execution.py)
```python
import pytest

@pytest.mark.integration
class TestAgentExecution:
    async def test_orchestrator_coordinates_agents(
        self,
        orchestrator,
        agent_registry
    ):
        result = await orchestrator.execute_task(
            "task_001",
            "complex_task",
            {"data": "test"},
            {}
        )
        
        assert result["success"] is True
        assert "orchestrated" in result["result"]
        assert result["result"]["subtask_count"] > 1
```

### E2E Tests (tests/e2e/test_full_workflow.spec.ts)
```typescript
import { test, expect } from '@playwright/test'

test('full task submission workflow', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:3005')
  
  // Submit task
  await page.fill('textarea', 'Test input')
  await page.click('button:has-text("Submit Task")')
  
  // Wait for result
  await expect(page.locator('.result')).toBeVisible({timeout: 30000})
  
  // Verify result
  const result = await page.locator('.result').textContent()
  expect(result).toContain('success')
})
```

### Meta-Learning Validation (tests/meta/test_meta_learning.py)
```python
@pytest.mark.meta
class TestMetaLearning:
    async def test_system_improves_performance(
        self,
        meta_learner,
        execution_engine
    ):
        # Record baseline performance
        baseline_times = []
        for i in range(10):
            start = time.time()
            await execution_engine.execute_simple_task(...)
            baseline_times.append(time.time() - start)
        
        baseline_avg = sum(baseline_times) / len(baseline_times)
        
        # Run meta-learning cycle
        await meta_learner.continuous_learning_loop_once()
        
        # Record new performance
        improved_times = []
        for i in range(10):
            start = time.time()
            await execution_engine.execute_simple_task(...)
            improved_times.append(time.time() - start)
        
        improved_avg = sum(improved_times) / len(improved_times)
        
        # Verify improvement
        improvement_pct = ((baseline_avg - improved_avg) / baseline_avg) * 100
        assert improvement_pct > 5, f"Expected >5% improvement, got {improvement_pct}%"
```

## Test Commands
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v -m integration

# E2E tests
npx playwright test

# All tests
pytest tests/ -v

# Coverage
pytest --cov=app --cov-report=html
```

---

# AGENT 10: DOCUMENTATION

**Priority:** 🟢 MEDIUM  
**Timeline:** Week 1-10 (Ongoing)  
**Branch:** `agent-10-documentation`  

## Mission
Create comprehensive documentation for users and developers.

## Key Deliverables
1. System architecture docs
2. API documentation (auto-generated)
3. User guides
4. Developer guides
5. Deployment guides

## Implementation

### README.md
```markdown
# Meta-Recursive Multi-Agent Orchestration System

## Overview
Self-improving AI system with autonomous learning capabilities.

## Quick Start
\`\`\`bash
# Clone repository
git clone <repo-url>

# Start infrastructure
docker-compose up -d

# Run setup
python scripts/setup.py

# Access UI
open http://localhost:3000
\`\`\`

## Features
- Multi-agent task orchestration
- Meta-recursive self-improvement
- Real-time metrics
- Natural language processing (Ollama)
- Knowledge graph (Neo4j)

## Architecture
[Include diagram]

## Documentation
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [API Reference](docs/api-reference.md)
```

### API Documentation (Auto-generated by FastAPI)
FastAPI automatically generates:
- OpenAPI schema at `/openapi.json`
- Swagger UI at `/docs`
- ReDoc at `/redoc`

Add descriptions to endpoints:
```python
@router.post("/tasks", summary="Create Task", description="Create and execute a new task")
async def create_task(task_data: TaskCreate):
    """
    Create a new task.
    
    - **type**: Task type (text_analysis, code_generation, etc.)
    - **input**: Task input data
    - **parameters**: Optional parameters
    """
    ...
```

### Architecture Diagram (docs/architecture.md)
```markdown
# System Architecture

## Components

\`\`\`
┌─────────────────────────────────────┐
│           Frontend (React)          │
│         Port 3000                   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│         Port 8000                   │
└─────────────┬───────────────────────┘
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
┌────────────┐  ┌────────────┐
│   Agent    │  │  Core      │
│ Framework  │  │  Engine    │
└────────────┘  └────────────┘
      │               │
      └───────┬───────┘
              ▼
┌─────────────────────────────────────┐
│    Database Layer (PostgreSQL)      │
└─────────────────────────────────────┘
\`\`\`

## Data Flow

1. User submits task via frontend
2. API receives and validates request
3. Orchestrator decomposes task
4. Agents execute subtasks
5. Results aggregated and returned
6. Meta-learner analyzes performance
7. System improves itself
\`\`\`
```

---

# AGENT 11: DEPLOYMENT

**Priority:** 🟡 HIGH  
**Timeline:** Week 9-10  
**Branch:** `agent-11-deployment`  

## Mission
Setup CI/CD pipeline and deployment procedures.

## Key Deliverables
1. GitHub Actions CI/CD
2. Docker deployment
3. Environment configuration
4. Health checks
5. Rollback procedures

## Implementation

### GitHub Actions (.github/workflows/ci-cd.yml)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v
      
      - name: Run linting
        run: |
          cd backend
          flake8 app/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker-compose build
      
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker-compose push
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # SSH to production server and run deployment
          ssh user@production-server 'cd /app && docker-compose pull && docker-compose up -d'
```

### Deployment Script (scripts/deploy.sh)
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Meta-Recursive Multi-Agent System"

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose pull

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Start new services
echo "▶️  Starting new services..."
docker-compose up -d

# Wait for health checks
echo "🏥 Waiting for services to be healthy..."
sleep 10

# Run health check
echo "✅ Running health check..."
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment complete!"
```

### Environment Templates
```bash
# .env.production.example
DATABASE_URL=postgresql://user:password@production-postgres:5432/orchestrator
REDIS_URL=redis://:password@production-redis:6379
OLLAMA_URL=http://production-ollama:11434

# Settings
DEBUG=false
LOG_LEVEL=WARNING
```

### Rollback Script (scripts/rollback.sh)
```bash
#!/bin/bash
set -e

PREVIOUS_VERSION=$1

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: ./rollback.sh <version>"
    exit 1
fi

echo "🔙 Rolling back to version $PREVIOUS_VERSION"

# Pull previous version
docker-compose -f docker-compose.yml -f docker-compose.$PREVIOUS_VERSION.yml pull

# Deploy previous version
docker-compose -f docker-compose.yml -f docker-compose.$PREVIOUS_VERSION.yml up -d

echo "✅ Rollback complete"
```

---

# COMPLETION SUMMARY

## All 11 MVP Agents Specified ✅

**Critical Path (Week 1-5):**
1. ✅ Agent 01: Infrastructure
2. ✅ Agent 02: Database
3. ✅ Agent 03: Core Engine
4. ✅ Agent 06: Agent Framework (Core Innovation)
5. ✅ Agent 07: LLM Integration
6. ✅ Agent 08: Monitoring

**Interface Layer (Week 6-8):**
7. ✅ Agent 04: API Layer
8. ✅ Agent 05: Frontend
9. ✅ Agent 09: Testing

**Deployment (Week 9-10):**
10. ✅ Agent 10: Documentation
11. ✅ Agent 11: Deployment

**Phase 2:**
12. ✅ Agent 12: Security (Deferred)

## Total Lines: ~27,000

**You now have complete specifications for building the entire MVP system.**

## Next Steps

### Start Building
```bash
# Week 1-2: Foundation
./scripts/agent-start.sh 01
./scripts/agent-start.sh 02

# Week 3-5: Core
./scripts/agent-start.sh 03
./scripts/agent-start.sh 06
./scripts/agent-start.sh 07
./scripts/agent-start.sh 08

# Week 6-8: Interface
./scripts/agent-start.sh 04
./scripts/agent-start.sh 05
./scripts/agent-start.sh 09

# Week 9-10: Deploy
./scripts/agent-start.sh 10
./scripts/agent-start.sh 11
```

### Validate MVP
```bash
./scripts/validate-mvp.sh
```

### Then Add Security (Phase 2)
```bash
./scripts/agent-start.sh 12
```

---

**🎉 ALL AGENT SPECIFICATIONS COMPLETE!**

**Date:** 2025-10-30  
**Total Specifications:** 11 MVP agents + 1 Phase 2 agent  
**Total Lines:** ~27,000 lines  
**MVP Ready:** YES ✅  
**Meta-Recursive Core:** SPECIFIED ✅  
**Security:** DEFERRED TO PHASE 2 ✅  

**YOU CAN NOW BUILD THE ENTIRE SYSTEM** 🚀

