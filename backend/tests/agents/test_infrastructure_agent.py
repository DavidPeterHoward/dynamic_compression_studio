import pytest
from unittest.mock import AsyncMock
import os

from app.agents.infrastructure.infra_agent import InfrastructureAgent


@pytest.fixture(autouse=True)
def ensure_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")


@pytest.mark.asyncio
async def test_infrastructure_agent_bootstrap_success(monkeypatch):
    ollama = AsyncMock()
    ollama.health_check = AsyncMock(return_value=True)

    agent = InfrastructureAgent(ollama=ollama)
    result = await agent.bootstrap_and_validate()

    assert result.success is True
    assert result.validations.get("env_vars") is True
    assert result.validations.get("ollama_health") is True
    assert result.validations.get("self_test") is True


@pytest.mark.asyncio
async def test_infrastructure_agent_bootstrap_warn_without_ollama(monkeypatch):
    agent = InfrastructureAgent(ollama=None)
    result = await agent.bootstrap_and_validate()

    # Env present; ollama skipped but not failing
    assert result.validations.get("env_vars") is True
    assert result.validations.get("ollama_health") is True
    assert any("OllamaService not injected" in w for w in result.warnings)
    assert result.success is True


@pytest.mark.asyncio
async def test_infrastructure_agent_bootstrap_fail_env_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    ollama = AsyncMock()
    ollama.health_check = AsyncMock(return_value=True)

    agent = InfrastructureAgent(ollama=ollama)
    result = await agent.bootstrap_and_validate()

    assert result.validations.get("env_vars") is False
    assert result.success is False


@pytest.mark.asyncio
async def test_infrastructure_agent_ollama_unhealthy(monkeypatch):
    ollama = AsyncMock()
    ollama.health_check = AsyncMock(return_value=False)

    agent = InfrastructureAgent(ollama=ollama)
    result = await agent.bootstrap_and_validate()

    assert result.validations.get("ollama_health") is False
    assert result.success is False


@pytest.mark.asyncio
async def test_infrastructure_agent_execute_tasks(monkeypatch):
    ollama = AsyncMock()
    ollama.health_check = AsyncMock(return_value=True)

    agent = InfrastructureAgent(ollama=ollama)
    await agent.initialize()

    # noop
    res1 = await agent.execute({"task_id": "t1", "task_type": "noop"})
    assert res1["status"] == "completed"

    # check_ollama
    res2 = await agent.execute({"task_id": "t2", "task_type": "check_ollama"})
    assert res2["status"] == "completed"
    assert res2["result"]["ollama_healthy"] is True

    # unknown
    res3 = await agent.execute({"task_id": "t3", "task_type": "unknown"})
    assert res3["status"] == "failed"
