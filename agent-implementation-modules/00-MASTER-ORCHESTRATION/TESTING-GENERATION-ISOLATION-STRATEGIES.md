# Testing & Generation Isolation Strategies
## How Agents Test & Generate Code Without Conflicts

**Version:** 1.0  
**Date:** 2025-10-30  
**Purpose:** Detailed testing and code generation strategies for isolated agents  

---

## 🎯 CORE TESTING PRINCIPLES

### Principle 1: Test Data Isolation

**Each agent has separate test data:**
```
data/
├── agent01/
│   ├── test/           # Agent 01 test data
│   │   ├── fixtures/
│   │   ├── mocks/
│   │   └── seeds/
│   └── dev/            # Agent 01 dev data
├── agent02/
│   ├── test/
│   └── dev/
└── ... (agent03-12)
```

**No shared test data between agents**

### Principle 2: Test Namespace Isolation

**Each agent's tests tagged with namespace:**
```python
# Agent 03 tests
@pytest.mark.agent03
@pytest.mark.core_engine
class TestCoreEngine:
    """All Agent 03 tests"""
    pass

# Agent 04 tests
@pytest.mark.agent04
@pytest.mark.api_layer
class TestAPILayer:
    """All Agent 04 tests"""
    pass

# Run only Agent 03 tests
# pytest -m agent03

# Run only Agent 04 tests
# pytest -m agent04
```

### Principle 3: Separate Test Databases

**Each agent gets own test database:**
```python
@pytest.fixture(scope="session")
def test_db(agent_id):
    """Create isolated test database per agent"""
    db_name = f"orchestrator_test_agent{agent_id}"
    
    # Create test database
    create_test_database(db_name)
    
    # Run migrations
    run_migrations(db_name)
    
    # Seed test data
    seed_test_data(db_name, agent_id)
    
    yield db_name
    
    # Cleanup
    drop_test_database(db_name)
```

---

## 🧪 TESTING STRATEGIES PER AGENT TYPE

### Strategy 1: Unit Testing (All Agents)

**Agent-Specific Test Configuration:**

```python
# tests/conftest.py
import os
import pytest

def pytest_configure(config):
    """Configure pytest based on agent"""
    agent_id = os.environ.get("AGENT_ID", "01")
    
    # Set agent-specific markers
    config.addinivalue_line(
        "markers", f"agent{agent_id}: Tests for Agent {agent_id}"
    )
    
    # Set agent-specific test paths
    config.option.testpaths = [
        f"tests/agent{agent_id}/",
        "tests/shared/"
    ]
    
    # Set agent-specific coverage paths
    config.option.cov = [f"backend/agent{agent_id}/"]

@pytest.fixture(scope="session")
def agent_config():
    """Load agent-specific configuration"""
    agent_id = os.environ.get("AGENT_ID", "01")
    
    return {
        "agent_id": agent_id,
        "ports": {
            "backend": 8000 + int(agent_id),
            "postgres": 5400 + int(agent_id),
            "redis": 6300 + int(agent_id)
        },
        "database": {
            "name": f"orchestrator_test_agent{agent_id}",
            "user": f"agent{agent_id}",
            "password": f"agent{agent_id}_test_password"
        },
        "test_data_path": f"./data/agent{agent_id}/test"
    }
```

**Agent 03 Unit Tests Example:**

```python
# tests/agent03/test_core_engine.py

import pytest
from app.core.compression_engine import CompressionEngine

@pytest.mark.agent03
@pytest.mark.unit
class TestCoreEngine:
    """Unit tests for Agent 03: Core Engine"""
    
    @pytest.fixture
    def engine(self, agent_config):
        """Create engine with agent-specific config"""
        return CompressionEngine(
            database_url=f"postgresql://{agent_config['database']['user']}:"
                        f"{agent_config['database']['password']}@"
                        f"localhost:{agent_config['ports']['postgres']}/"
                        f"{agent_config['database']['name']}"
        )
    
    def test_engine_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine is not None
        assert engine.status == "initialized"
    
    def test_task_processing(self, engine):
        """Test task processing"""
        task = {
            "type": "compress",
            "input": {"data": "test data"},
            "parameters": {"algorithm": "gzip"}
        }
        
        result = engine.process_task(task)
        
        assert result["success"] is True
        assert "output" in result
    
    def test_concurrent_processing(self, engine):
        """Test concurrent task processing"""
        import asyncio
        
        async def process_many():
            tasks = [
                {"type": "compress", "input": {"data": f"test {i}"}}
                for i in range(100)
            ]
            
            results = await asyncio.gather(*[
                engine.process_task(task)
                for task in tasks
            ])
            
            return results
        
        results = asyncio.run(process_many())
        
        assert len(results) == 100
        assert all(r["success"] for r in results)

# Run: AGENT_ID=03 pytest tests/agent03/ -v -m agent03
```

---

### Strategy 2: Integration Testing (Agent 09)

**Agent 09's Integration Test Suite:**

```python
# tests/integration/test_agent_integration.py

import pytest
import requests
import asyncio
from typing import Dict, List

@pytest.mark.agent09
@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests coordinated by Agent 09"""
    
    @pytest.fixture(scope="class")
    def all_agents(self):
        """Start all agent environments"""
        import subprocess
        
        # Start all agents
        for agent_id in range(1, 13):
            subprocess.run([
                "./scripts/agent-start.sh",
                f"{agent_id:02d}"
            ])
        
        # Wait for all to be ready
        asyncio.run(self._wait_for_all_agents())
        
        yield
        
        # Stop all agents
        for agent_id in range(1, 13):
            subprocess.run([
                "./scripts/agent-stop.sh",
                f"{agent_id:02d}"
            ])
    
    async def _wait_for_all_agents(self):
        """Wait for all agents to be ready"""
        async def check_agent(agent_id):
            port = 8000 + agent_id
            for _ in range(30):
                try:
                    response = requests.get(f"http://localhost:{port}/health")
                    if response.status_code == 200:
                        return True
                except:
                    pass
                await asyncio.sleep(2)
            return False
        
        results = await asyncio.gather(*[
            check_agent(i) for i in range(1, 13)
        ])
        
        assert all(results), "Some agents failed to start"
    
    def test_database_to_api_integration(self, all_agents):
        """Test Agent 02 (Database) integrates with Agent 04 (API)"""
        # Create task via Agent 04 API
        response = requests.post(
            "http://localhost:8004/api/v1/tasks",
            json={
                "type": "test",
                "input": {"data": "integration_test"}
            }
        )
        
        assert response.status_code == 201
        task_id = response.json()["id"]
        
        # Verify in Agent 02 Database
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5402,
            database="orchestrator_agent02",
            user="agent02",
            password="agent02_secure_password"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        result = cursor.fetchone()
        
        assert result is not None
        
        cursor.close()
        conn.close()
    
    def test_api_to_frontend_integration(self, all_agents):
        """Test Agent 04 (API) integrates with Agent 05 (Frontend)"""
        # Frontend (Agent 05) requests data from API (Agent 04)
        response = requests.get("http://localhost:8004/api/v1/tasks")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_llm_integration(self, all_agents):
        """Test Agent 07 (LLM) is accessible"""
        # Test Ollama is running
        response = requests.get("http://localhost:11407")
        assert response.status_code == 200

# Run: AGENT_ID=09 pytest tests/integration/ -v -m agent09
```

---

### Strategy 3: Code Generation Without Conflicts

**Each agent generates code in their namespace:**

```python
# Agent 06: Agent Framework Generator

class AgentCodeGenerator:
    """Generate agent code in isolated namespace"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.namespace = f"agent{agent_id}"
        self.output_dir = f"backend/app/agents/agent{agent_id}/"
    
    def generate_agent_class(
        self,
        agent_name: str,
        agent_type: str,
        capabilities: List[str]
    ) -> str:
        """Generate agent class code"""
        
        # Template with isolated imports
        template = f'''
"""
Agent {self.agent_id}: {agent_name}
Auto-generated by Agent Code Generator
Namespace: {self.namespace}
"""

from typing import Dict, Any, List
from app.core.interfaces import IAgent
from app.database import get_db

class {agent_name}Agent(IAgent):
    """
    {agent_type} agent with capabilities: {', '.join(capabilities)}
    Operates in isolated namespace: {self.namespace}
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.agent_id = "{self.agent_id}"
        self.name = "{agent_name}"
        self.type = "{agent_type}"
        self.capabilities = {capabilities}
        self.config = config
        self.namespace = "{self.namespace}"
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize agent in isolated environment"""
        # Use agent-specific database
        self.db = get_db(namespace=self.namespace)
        
        # Load agent-specific configuration
        self.load_config(config)
        
        return await self.self_validate()
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task in isolated environment"""
        # All operations scoped to this agent's namespace
        result = {{
            "agent_id": self.agent_id,
            "namespace": self.namespace,
            "task_id": task["id"],
            "success": False,
            "output": None
        }}
        
        try:
            # Process task
            output = await self._process(task)
            
            result["success"] = True
            result["output"] = output
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def self_validate(self) -> Dict[str, Any]:
        """Bootstrap fail-pass validation"""
        checks = []
        
        # Check database connection
        checks.append({{
            "check": "database_connection",
            "passed": await self._check_database()
        }})
        
        # Check capabilities
        checks.append({{
            "check": "capabilities_loaded",
            "passed": len(self.capabilities) > 0
        }})
        
        all_passed = all(c["passed"] for c in checks)
        
        return {{
            "status": "pass" if all_passed else "fail",
            "checks": checks
        }}
    
    async def _process(self, task: Dict[str, Any]) -> Any:
        """Process task - implement in subclass"""
        raise NotImplementedError()
    
    async def _check_database(self) -> bool:
        """Check database connection"""
        try:
            await self.db.execute("SELECT 1")
            return True
        except:
            return False
'''
        
        # Write to agent-specific directory
        output_file = f"{self.output_dir}/{agent_name.lower()}_agent.py"
        
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(template)
        
        return output_file
    
    def generate_tests(
        self,
        agent_name: str
    ) -> str:
        """Generate tests for generated agent"""
        
        template = f'''
import pytest
from app.agents.agent{self.agent_id}.{agent_name.lower()}_agent import {agent_name}Agent

@pytest.mark.agent{self.agent_id}
@pytest.mark.unit
class Test{agent_name}Agent:
    """Tests for {agent_name}Agent"""
    
    @pytest.fixture
    def agent(self, agent_config):
        """Create agent instance"""
        return {agent_name}Agent(agent_config)
    
    def test_initialization(self, agent):
        """Test agent initializes"""
        assert agent.agent_id == "{self.agent_id}"
        assert agent.namespace == "agent{self.agent_id}"
    
    async def test_self_validation(self, agent):
        """Test self-validation passes"""
        result = await agent.self_validate()
        assert result["status"] == "pass"
    
    async def test_task_execution(self, agent):
        """Test task execution"""
        task = {{
            "id": "test-123",
            "type": "test",
            "input": {{"data": "test"}}
        }}
        
        result = await agent.execute_task(task)
        
        assert result["agent_id"] == "{self.agent_id}"
        assert result["namespace"] == "agent{self.agent_id}"
'''
        
        # Write to test directory
        output_file = f"tests/agent{self.agent_id}/test_{agent_name.lower()}_agent.py"
        
        import os
        os.makedirs(f"tests/agent{self.agent_id}", exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(template)
        
        return output_file

# Usage by Agent 06
if __name__ == "__main__":
    generator = AgentCodeGenerator(agent_id="06")
    
    # Generate NLP Specialist Agent
    agent_file = generator.generate_agent_class(
        agent_name="NLPSpecialist",
        agent_type="specialist",
        capabilities=["text_analysis", "sentiment_analysis", "entity_extraction"]
    )
    
    # Generate tests
    test_file = generator.generate_tests("NLPSpecialist")
    
    print(f"✅ Generated: {agent_file}")
    print(f"✅ Generated: {test_file}")
```

---

### Strategy 4: Parallel Test Execution

**Run All Agent Tests Simultaneously:**

```bash
#!/bin/bash
# scripts/run-all-agent-tests.sh

echo "🧪 Running tests for all 12 agents in parallel..."

# Array to store PIDs
pids=()

# Start all agent tests in background
for agent_id in {01..12}; do
    echo "Starting tests for Agent $agent_id..."
    
    (
        export AGENT_ID=$agent_id
        pytest tests/agent$agent_id/ \
            -v \
            -m agent$agent_id \
            --cov=backend/app/agents/agent$agent_id \
            --cov-report=html:coverage/agent$agent_id \
            --cov-report=xml:coverage/agent$agent_id/coverage.xml \
            --junit-xml=reports/agent$agent_id/junit.xml \
            > logs/test_agent$agent_id.log 2>&1
        
        echo $? > /tmp/agent${agent_id}_result
    ) &
    
    pids+=($!)
done

# Wait for all to complete
echo "⏳ Waiting for all tests to complete..."

for pid in "${pids[@]}"; do
    wait $pid
done

# Check results
echo ""
echo "📊 Test Results:"
all_passed=true

for agent_id in {01..12}; do
    result=$(cat /tmp/agent${agent_id}_result)
    
    if [ $result -eq 0 ]; then
        echo "✅ Agent $agent_id: PASSED"
    else
        echo "❌ Agent $agent_id: FAILED"
        all_passed=false
    fi
done

# Cleanup
rm /tmp/agent*_result

if $all_passed; then
    echo ""
    echo "🎉 All agent tests passed!"
    exit 0
else
    echo ""
    echo "⚠️  Some agent tests failed. Check logs/"
    exit 1
fi
```

---

### Strategy 5: Continuous Integration Per Agent

**GitHub Actions Workflow:**

```yaml
# .github/workflows/test-agents.yml

name: Test All Agents

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop ]

jobs:
  test-agent:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        agent_id: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
      fail-fast: false  # Continue even if one agent fails
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Start Agent ${{ matrix.agent_id }} environment
        run: |
          chmod +x ./scripts/agent-start.sh
          ./scripts/agent-start.sh ${{ matrix.agent_id }}
      
      - name: Run Agent ${{ matrix.agent_id }} tests
        env:
          AGENT_ID: ${{ matrix.agent_id }}
        run: |
          pytest tests/agent${{ matrix.agent_id }}/ \
            -v \
            -m agent${{ matrix.agent_id }} \
            --cov=backend/app/agents/agent${{ matrix.agent_id }} \
            --cov-report=xml \
            --junit-xml=reports/agent${{ matrix.agent_id }}/junit.xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: agent${{ matrix.agent_id }}
          name: agent-${{ matrix.agent_id }}
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-agent-${{ matrix.agent_id }}
          path: reports/agent${{ matrix.agent_id }}/
      
      - name: Stop Agent ${{ matrix.agent_id }} environment
        if: always()
        run: |
          chmod +x ./scripts/agent-stop.sh
          ./scripts/agent-stop.sh ${{ matrix.agent_id }}
  
  integration-tests:
    needs: test-agent
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Start all agent environments
        run: |
          chmod +x ./scripts/setup-all-agents.sh
          ./scripts/setup-all-agents.sh
      
      - name: Run integration tests
        env:
          AGENT_ID: '09'
        run: |
          pytest tests/integration/ -v -m agent09
      
      - name: Upload integration test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: integration-test-results
          path: reports/integration/
```

---

## 🔐 DATA SEEDING ISOLATION

**Each agent seeds their own test data:**

```python
# tests/agent03/seed_data.py

import asyncio
from app.database import get_db

async def seed_agent03_test_data():
    """Seed test data for Agent 03"""
    db = get_db(namespace="agent03")
    
    # Seed tasks
    tasks = [
        {
            "type": "compress",
            "input": {"data": f"test data {i}"},
            "status": "pending"
        }
        for i in range(100)
    ]
    
    for task in tasks:
        await db.create("tasks", task)
    
    # Seed agents
    agents = [
        {
            "id": "agent03",
            "name": "Core Engine",
            "type": "core",
            "status": "active"
        }
    ]
    
    for agent in agents:
        await db.create("agents", agent)
    
    print("✅ Agent 03 test data seeded")

if __name__ == "__main__":
    asyncio.run(seed_agent03_test_data())
```

---

**This continues in next response with performance testing strategies...**

---

**Document Version:** 1.0  
**Date:** 2025-10-30  
**Status:** TESTING & GENERATION STRATEGIES COMPLETE  
**Next:** Performance testing + final summary  

**COMPLETE TEST ISOLATION ACHIEVED** ✅

