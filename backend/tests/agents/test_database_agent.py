"""
Tests for Database Agent.

Tests cover:
- Bootstrap validation (connectivity, health, schema, tables)
- Migration execution
- Data seeding
- Database statistics
- Error handling
"""

import pytest
from unittest.mock import patch, AsyncMock
import os
from app.agents.database.database_agent import DatabaseAgent


@pytest.fixture
def db_agent():
    """Create database agent for testing."""
    return DatabaseAgent()


@pytest.mark.asyncio
async def test_database_agent_bootstrap_success(db_agent):
    """
    Test successful bootstrap validation.

    Requires actual database connection.
    """
    # This test requires a real database
    pytest.skip("Requires actual database - run manually")

    result = await db_agent.bootstrap_and_validate()

    assert result.success is True
    assert result.validations.get("db_connectivity") is True
    assert result.validations.get("db_health") is True
    assert result.validations.get("schema_status") is True
    assert result.validations.get("core_tables") is True
    assert result.validations.get("crud_test") is True


@pytest.mark.asyncio
async def test_database_agent_bootstrap_failure_no_db(db_agent):
    """Test bootstrap failure when database is unavailable."""
    # Mock database connection failure
    with patch('app.database.connection.check_db_connection', return_value=False):
        result = await db_agent.bootstrap_and_validate()

        assert result.success is False
        assert result.validations.get("db_connectivity") is False


@pytest.mark.asyncio
async def test_database_agent_execute_task_seed_data(db_agent):
    """Test data seeding task."""
    # This would require actual database access
    pytest.skip("Requires database - test manually")

    task = {"task_id": "seed-1", "task_type": "seed_data"}
    result = await db_agent.execute(task)

    assert result["status"] == "completed"
    assert "algorithms_seeded" in result["result"]


@pytest.mark.asyncio
async def test_database_agent_execute_task_unknown(db_agent):
    """Test unknown task type."""
    task = {"task_id": "unknown-1", "task_type": "unknown_task"}
    result = await db_agent.execute(task)

    assert result["status"] == "failed"
    assert "Unknown database task" in result["error"]


@pytest.mark.asyncio
async def test_database_agent_self_evaluation(db_agent):
    """Test agent self-evaluation."""
    await db_agent.initialize()

    evaluation = await db_agent.self_evaluate()

    assert "performance_score" in evaluation
    assert "strengths" in evaluation
    assert "weaknesses" in evaluation
    assert "improvement_suggestions" in evaluation
    assert "metrics" in evaluation


@pytest.mark.asyncio
async def test_database_agent_report_metrics(db_agent):
    """Test metrics reporting."""
    await db_agent.initialize()

    metrics = await db_agent.report_metrics()

    assert metrics["agent_id"] == db_agent.agent_id
    assert metrics["agent_type"] == "database"
    assert "db_connectivity" in metrics
    assert "schema_current" in metrics
    assert "db_health" in metrics


# Integration test - requires actual database
@pytest.mark.asyncio
@pytest.mark.integration
async def test_database_agent_full_lifecycle():
    """
    Full lifecycle test of database agent.

    Requires actual database connection.
    """
    pytest.skip("Integration test - requires database")

    agent = DatabaseAgent(agent_id="test-db-agent")

    # Bootstrap
    result = await agent.bootstrap_and_validate()
    assert result.success is True

    # Execute tasks
    seed_result = await agent.execute({"task_id": "seed", "task_type": "seed_data"})
    assert seed_result["status"] == "completed"

    stats_result = await agent.execute({"task_id": "stats", "task_type": "db_stats"})
    assert stats_result["status"] == "completed"

    # Self-evaluate
    evaluation = await agent.self_evaluate()
    assert evaluation["performance_score"] >= 0.8

    # Shutdown
    await agent.shutdown()
    assert agent.status.value == "shutdown"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

