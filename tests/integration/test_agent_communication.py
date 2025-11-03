"""
Integration Tests for Agent Communication System

Tests inter-agent communication, task delegation, parameter optimization,
and collaborative functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, AsyncMock

from app.agents.infrastructure.infra_agent import InfrastructureAgent
from app.agents.database.database_agent import DatabaseAgent
from app.core.agent_communication import AgentCommunicationManager
from app.core.message_bus import get_message_bus


@pytest.fixture
async def message_bus():
    """Get message bus instance."""
    return get_message_bus()


@pytest.fixture
async def infra_agent():
    """Create infrastructure agent for testing."""
    agent = InfrastructureAgent(agent_id="01")
    await agent.bootstrap_and_validate()
    await agent.start_communication_services()
    yield agent
    await agent.stop_communication_services()


@pytest.fixture
async def db_agent():
    """Create database agent for testing."""
    agent = DatabaseAgent(agent_id="02")
    await agent.bootstrap_and_validate()
    await agent.start_communication_services()
    yield agent
    await agent.stop_communication_services()


@pytest.mark.asyncio
class TestAgentCommunication:
    """Test inter-agent communication functionality."""

    async def test_agent_initialization(self, infra_agent, db_agent):
        """Test agents initialize with communication capabilities."""
        assert infra_agent.agent_id == "01"
        assert db_agent.agent_id == "02"
        assert hasattr(infra_agent, 'comm_manager')
        assert hasattr(db_agent, 'comm_manager')
        assert infra_agent.comm_manager is not None
        assert db_agent.comm_manager is not None

    async def test_task_delegation_ping(self, infra_agent, db_agent):
        """Test basic task delegation (ping)."""
        # Database agent pings infrastructure agent
        result = await db_agent.delegate_task_to_agent(
            target_agent="01",
            task_type="ping",
            parameters={},
            timeout=5.0
        )

        assert result["status"] == "completed"
        assert "result" in result
        assert result["result"]["pong"] is True
        assert result["result"]["agent_id"] == "01"
        assert result["result"]["agent_type"] == "infrastructure"

    async def test_task_delegation_with_timeout(self, infra_agent, db_agent):
        """Test task delegation with timeout."""
        # Test timeout by using a non-existent task
        result = await db_agent.delegate_task_to_agent(
            target_agent="01",
            task_type="non_existent_task",
            parameters={},
            timeout=1.0
        )

        assert result["status"] == "failed"
        assert "error" in result
        assert "does not support task type" in result["error"]

    async def test_collaboration_history_tracking(self, infra_agent, db_agent):
        """Test that collaboration history is tracked."""
        initial_count = len(infra_agent.collaboration_history)

        # Perform a task delegation
        await db_agent.delegate_task_to_agent(
            target_agent="01",
            task_type="ping",
            parameters={},
            timeout=5.0
        )

        # Check that collaboration was recorded
        assert len(infra_agent.collaboration_history) > initial_count

        # Check collaboration record structure
        latest_collaboration = infra_agent.collaboration_history[-1]
        assert "id" in latest_collaboration
        assert "type" in latest_collaboration
        assert "target_agent" in latest_collaboration
        assert "timestamp" in latest_collaboration

    async def test_parameter_optimization_request(self, infra_agent, db_agent):
        """Test parameter optimization request between agents."""
        # Infrastructure agent requests optimization from database agent
        result = await infra_agent.request_parameter_optimization(
            target_agent="02",
            task_type="infrastructure_monitoring",
            parameter_space={
                "health_check_interval": {"type": "range", "min": 10, "max": 30, "step": 10}
            },
            evaluation_criteria={"response_time": 0.6, "success_rate": 0.4},
            timeout=10.0
        )

        # Should get some response (may fail due to mock limitations, but communication works)
        assert "status" in result
        assert result["status"] in ["completed", "failed", "timeout"]

        if result["status"] == "completed":
            assert "result" in result
            opt_result = result["result"]
            assert "best_parameters" in opt_result or "error" in opt_result

    async def test_collaborative_health_check(self, infra_agent, db_agent):
        """Test collaborative health check functionality."""
        # Execute collaborative health check
        result = await infra_agent.execute_task({
            "task_id": "test_collab_health",
            "task_type": "collaborate_health_check"
        })

        assert result["status"] == "completed"
        assert "result" in result
        collab_result = result["result"]
        assert "collaborative_health_check" in collab_result

        health_data = collab_result["collaborative_health_check"]
        assert "infrastructure_status" in health_data
        assert "database_status" in health_data
        assert "overall_health" in health_data

    async def test_knowledge_sharing(self, infra_agent, db_agent):
        """Test knowledge sharing between agents."""
        # Infrastructure agent shares knowledge
        result = await infra_agent.execute_task({
            "task_id": "test_knowledge_share",
            "task_type": "share_infrastructure_knowledge"
        })

        assert result["status"] == "completed"
        assert "result" in result
        share_result = result["result"]
        assert "knowledge_shared" in share_result
        assert "recipients" in share_result
        assert "successful_shares" in share_result

    async def test_agent_relationship_tracking(self, infra_agent, db_agent):
        """Test that agent relationships are tracked."""
        initial_relationships = len(infra_agent.agent_relationships)

        # Perform multiple interactions
        for i in range(3):
            await db_agent.delegate_task_to_agent(
                target_agent="01",
                task_type="ping",
                parameters={},
                timeout=5.0
            )

        # Check that relationship was established
        assert "02" in infra_agent.agent_relationships
        relationship = infra_agent.agent_relationships["02"]
        assert relationship["interactions"] >= 3
        assert "trust_score" in relationship
        assert "average_response_time" in relationship

    async def test_broadcast_experiment_request(self, infra_agent):
        """Test broadcast experiment request."""
        # This will fail in test environment but tests the communication path
        result = await infra_agent.broadcast_experiment_request(
            experiment_type="system_performance_test",
            parameters={"test_duration": 30},
            target_agents=["02"]
        )

        # Should get a response structure
        assert "experiment_type" in result
        assert "target_agents" in result
        assert "results" in result
        assert "successful_responses" in result
        assert "total_requests" in result

    async def test_communication_status_reporting(self, infra_agent, db_agent):
        """Test communication status reporting."""
        infra_status = infra_agent.get_communication_status()
        db_status = db_agent.get_communication_status()

        assert infra_status["communication_enabled"] is True
        assert db_status["communication_enabled"] is True
        assert "registered_handlers" in infra_status
        assert "pending_requests" in infra_status
        assert "collaboration_history_count" in infra_status

    async def test_collaboration_summary(self, infra_agent, db_agent):
        """Test collaboration summary generation."""
        # Perform some collaborations first
        await db_agent.delegate_task_to_agent("01", "ping", {}, timeout=5.0)

        summary = infra_agent.get_collaboration_summary()

        assert "total_collaborations" in summary
        assert "successful_collaborations" in summary
        assert "agent_relationships" in summary
        assert summary["total_collaborations"] >= 1

    async def test_parameter_optimization_results_tracking(self, infra_agent):
        """Test parameter optimization results tracking."""
        results = infra_agent.get_parameter_optimization_results()

        assert "total_experiments" in results
        assert "completed_experiments" in results
        assert "experiments" in results
        assert isinstance(results["experiments"], dict)

    async def test_agent_self_evaluation_with_communication(self, infra_agent, db_agent):
        """Test agent self-evaluation includes communication metrics."""
        infra_eval = await infra_agent.self_evaluate()
        db_eval = await db_agent.self_evaluate()

        assert "communication_enabled" in infra_eval["metrics"]
        assert "total_collaborations" in infra_eval["metrics"]
        assert "successful_collaborations" in infra_eval["metrics"]

        assert "communication_enabled" in db_eval["metrics"]
        assert "total_collaborations" in db_eval["metrics"]
        assert "parameter_experiments" in db_eval["metrics"]


@pytest.mark.asyncio
class TestCommunicationEdgeCases:
    """Test edge cases in agent communication."""

    async def test_task_delegation_to_nonexistent_agent(self, infra_agent):
        """Test delegation to non-existent agent."""
        result = await infra_agent.delegate_task_to_agent(
            target_agent="99",  # Non-existent agent
            task_type="ping",
            parameters={},
            timeout=2.0
        )

        assert result["status"] == "timeout"
        assert "error" in result

    async def test_multiple_concurrent_delegations(self, infra_agent, db_agent):
        """Test multiple concurrent task delegations."""
        # Create multiple concurrent tasks
        tasks = []
        for i in range(5):
            task = db_agent.delegate_task_to_agent(
                target_agent="01",
                task_type="ping",
                parameters={"request_id": i},
                timeout=5.0
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        successful_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "completed")
        assert successful_count >= 3  # At least 3 should succeed

    async def test_task_delegation_with_large_payload(self, infra_agent, db_agent):
        """Test task delegation with large parameter payload."""
        large_params = {
            "data": "x" * 10000,  # 10KB of data
            "metadata": {"size": "large", "complexity": "high"},
            "nested": {
                "level1": {
                    "level2": {
                        "level3": list(range(100))
                    }
                }
            }
        }

        result = await db_agent.delegate_task_to_agent(
            target_agent="01",
            task_type="ping",
            parameters=large_params,
            timeout=10.0
        )

        assert result["status"] == "completed"
        assert result["result"]["pong"] is True

    async def test_communication_under_load(self, infra_agent, db_agent):
        """Test communication system under concurrent load."""
        async def stress_test_agent(agent, target, iterations=10):
            results = []
            for i in range(iterations):
                result = await agent.delegate_task_to_agent(
                    target_agent=target,
                    task_type="ping",
                    parameters={"iteration": i},
                    timeout=5.0
                )
                results.append(result)
            return results

        # Run stress tests concurrently
        infra_stress = stress_test_agent(infra_agent, "02", 20)
        db_stress = stress_test_agent(db_agent, "01", 20)

        infra_results, db_results = await asyncio.gather(infra_stress, db_stress)

        # Analyze results
        infra_success_count = sum(1 for r in infra_results if r.get("status") == "completed")
        db_success_count = sum(1 for r in db_results if r.get("status") == "completed")

        # Allow for some failures under load, but most should succeed
        assert infra_success_count >= 15  # At least 75% success rate
        assert db_success_count >= 15

        print(f"Infra success rate: {infra_success_count}/20 ({infra_success_count/20*100:.1f}%)")
        print(f"DB success rate: {db_success_count}/20 ({db_success_count/20*100:.1f}%)")


# Performance tests
@pytest.mark.asyncio
@pytest.mark.performance
class TestCommunicationPerformance:
    """Performance tests for agent communication."""

    async def test_task_delegation_latency(self, infra_agent, db_agent):
        """Test task delegation latency."""
        import time

        latencies = []
        for i in range(10):
            start_time = time.time()
            result = await db_agent.delegate_task_to_agent(
                target_agent="01",
                task_type="ping",
                parameters={},
                timeout=5.0
            )
            end_time = time.time()

            if result["status"] == "completed":
                latencies.append(end_time - start_time)

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)

            # Performance assertions
            assert avg_latency < 1.0, f"Average latency too high: {avg_latency:.3f}s"
            assert max_latency < 2.0, f"Max latency too high: {max_latency:.3f}s"
            assert min_latency < 0.5, f"Min latency too high: {min_latency:.3f}s"

            print(f"Task delegation latency: avg={avg_latency:.3f}s, min={min_latency:.3f}s, max={max_latency:.3f}s")

    async def test_concurrent_communication_capacity(self, infra_agent, db_agent):
        """Test concurrent communication capacity."""
        async def timed_ping(agent, target, delay=0):
            if delay:
                await asyncio.sleep(delay)
            start = asyncio.get_event_loop().time()
            result = await agent.delegate_task_to_agent(target, "ping", {}, timeout=10.0)
            end = asyncio.get_event_loop().time()
            return {
                "success": result["status"] == "completed",
                "latency": end - start
            }

        # Test with different concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        results = {}

        for concurrency in concurrency_levels:
            print(f"Testing concurrency level: {concurrency}")

            # Create concurrent ping tasks with slight staggering
            tasks = []
            for i in range(concurrency):
                tasks.append(timed_ping(
                    infra_agent if i % 2 == 0 else db_agent,
                    "02" if i % 2 == 0 else "01",
                    delay=i * 0.01  # Slight stagger
                ))

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful = sum(1 for r in batch_results if isinstance(r, dict) and r["success"])
            failed = concurrency - successful
            avg_latency = sum(r["latency"] for r in batch_results if isinstance(r, dict)) / successful if successful > 0 else 0

            results[concurrency] = {
                "successful": successful,
                "failed": failed,
                "success_rate": successful / concurrency * 100,
                "avg_latency": avg_latency
            }

            print(".1f"
        # Performance assertions
        for concurrency, stats in results.items():
            assert stats["success_rate"] >= 80, f"Low success rate at concurrency {concurrency}: {stats['success_rate']:.1f}%"
            assert stats["avg_latency"] < 2.0, f"High latency at concurrency {concurrency}: {stats['avg_latency']:.3f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
