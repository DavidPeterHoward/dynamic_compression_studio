# Infrastructure Agent Runbook

## Purpose
Agent 01 validates environment and core dependencies, exposes health/readiness, and orchestrates base infrastructure checks.

## Location
- Code: `backend/app/agents/infrastructure/infra_agent.py`
- Tests: `backend/tests/agents/test_infrastructure_agent.py`

## Bootstrap Fail-Pass Checks
1. Required env vars present (`DATABASE_URL`)
2. Ollama health (optional, warns if not injected)
3. Self-test task executes successfully

## Usage (Programmatic)
```python
from app.agents.infrastructure.infra_agent import InfrastructureAgent
from app.services.ollama_service import OllamaService

agent = InfrastructureAgent(ollama=OllamaService())
await agent.initialize()  # runs bootstrap
res = await agent.execute({"task_id": "t2", "task_type": "check_ollama"})
```

## Commands
- Run agent tests:
  - From `backend/`: `python -m pytest tests/agents/test_infrastructure_agent.py -q`
- Run LLM integration tests:
  - From `backend/`: `python -m pytest tests/services/test_ollama_service.py -v -m "requires_ollama"`
- Coverage (HTML at `backend/coverage_reports/index.html`):
  - From `backend/`: `pytest tests/services tests/core tests/agents --cov=app --cov-report=term-missing --cov-report=html:coverage_reports`

## Health and Readiness
- Task `noop`: verifies execution path
- Task `check_ollama`: returns `{ ollama_healthy: bool }`

## Recent Test Results
- 5 tests passed for Infrastructure Agent
- 47 total tests passed across new modules (LLM + BaseAgent + Infra)
- Coverage HTML report generated

## Next Integration Steps
- Wire agent into orchestrator (Agent 06)
- Add Docker Compose healthchecks dependency on Ollama
- Add FastAPI endpoints to surface infrastructure health (Phase API work)
