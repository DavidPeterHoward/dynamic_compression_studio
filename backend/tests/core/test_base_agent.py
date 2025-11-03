"""
Tests for Base Agent Framework.

Tests cover:
- Bootstrap fail-pass methodology
- Agent lifecycle
- Task execution
- Self-evaluation
- Performance tracking
- Health checks
"""

import pytest
import asyncio
from app.core.base_agent import (
    BaseAgent,
    SimpleAgent,
    AgentStatus,
    AgentCapability,
    BootstrapResult
)


class TestBootstrapResult:
    """Test BootstrapResult class."""
    
    def test_bootstrap_result_initialization(self):
        """Test bootstrap result initialization."""
        result = BootstrapResult()
        
        assert result.success is False
        assert result.validations == {}
        assert result.errors == []
        assert result.warnings == []
        assert result.metrics == {}
        assert result.timestamp is not None
    
    def test_add_validation_passing(self):
        """Test adding passing validation."""
        result = BootstrapResult()
        result.add_validation("component1", True, "All good")
        
        assert result.validations["component1"] is True
        assert len(result.errors) == 0
        assert result.success is True
    
    def test_add_validation_failing(self):
        """Test adding failing validation."""
        result = BootstrapResult()
        result.add_validation("component1", False, "Failed")
        
        assert result.validations["component1"] is False
        assert len(result.errors) == 1
        assert "component1: Failed" in result.errors
        assert result.success is False
    
    def test_multiple_validations(self):
        """Test multiple validations."""
        result = BootstrapResult()
        result.add_validation("comp1", True)
        result.add_validation("comp2", True)
        result.add_validation("comp3", False, "Error")
        
        assert result.success is False  # One failed
        assert len(result.validations) == 3
        assert len(result.errors) == 1
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = BootstrapResult()
        result.add_warning("This is a warning")
        
        assert len(result.warnings) == 1
        assert result.warnings[0] == "This is a warning"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = BootstrapResult()
        result.add_validation("test", True)
        result.add_warning("warning")
        result.metrics = {"metric1": 100}
        
        data = result.to_dict()
        
        assert "success" in data
        assert "validations" in data
        assert "errors" in data
        assert "warnings" in data
        assert "metrics" in data
        assert "timestamp" in data


class TestAgentStatus:
    """Test AgentStatus enum."""
    
    def test_agent_statuses_defined(self):
        """Test all agent statuses are defined."""
        assert AgentStatus.INITIALIZING
        assert AgentStatus.VALIDATING
        assert AgentStatus.IDLE
        assert AgentStatus.WORKING
        assert AgentStatus.ERROR
        assert AgentStatus.DEGRADED
        assert AgentStatus.SHUTDOWN
    
    def test_agent_status_values(self):
        """Test agent status string values."""
        assert AgentStatus.INITIALIZING.value == "initializing"
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.WORKING.value == "working"
        assert AgentStatus.ERROR.value == "error"


class TestAgentCapability:
    """Test AgentCapability enum."""
    
    def test_capabilities_defined(self):
        """Test standard capabilities are defined."""
        assert AgentCapability.COMPRESSION
        assert AgentCapability.ANALYSIS
        assert AgentCapability.OPTIMIZATION
        assert AgentCapability.LEARNING


class TestSimpleAgent:
    """Test SimpleAgent implementation."""
    
    @pytest.fixture
    def simple_agent(self):
        """Create simple agent for testing."""
        return SimpleAgent()
    
    def test_agent_initialization(self, simple_agent):
        """Test agent initializes correctly."""
        assert simple_agent.agent_id is not None
        assert simple_agent.agent_type == "simple"
        assert simple_agent.status == AgentStatus.INITIALIZING
        assert len(simple_agent.capabilities) == 1
        assert AgentCapability.ANALYSIS in simple_agent.capabilities
        assert simple_agent.task_count == 0
        assert simple_agent.success_count == 0
        assert simple_agent.error_count == 0
    
    def test_agent_initialization_with_custom_id(self):
        """Test agent with custom ID."""
        agent = SimpleAgent(agent_id="custom-123")
        
        assert agent.agent_id == "custom-123"
    
    def test_agent_initialization_with_config(self):
        """Test agent with custom configuration."""
        config = {"param1": "value1", "param2": 42}
        agent = SimpleAgent(config=config)
        
        assert agent.config == config
        assert agent.config["param1"] == "value1"
    
    @pytest.mark.asyncio
    async def test_bootstrap_and_validate_success(self, simple_agent):
        """
        Test bootstrap validation succeeds for valid agent.
        
        CRITICAL TEST: Validates bootstrap fail-pass methodology.
        """
        result = await simple_agent.bootstrap_and_validate()
        
        assert isinstance(result, BootstrapResult)
        assert result.success is True
        assert "configuration" in result.validations
        assert "capabilities" in result.validations
        assert "self_test" in result.validations
        assert len(result.errors) == 0
        
        print(f"\nBootstrap validations: {result.validations}")
    
    @pytest.mark.asyncio
    async def test_agent_initialization_lifecycle(self, simple_agent):
        """
        Test complete agent initialization lifecycle.
        
        Lifecycle:
        1. Agent created (INITIALIZING)
        2. Bootstrap validation runs (VALIDATING)
        3. If passes → IDLE
        4. Ready for work
        """
        # Initial status
        assert simple_agent.status == AgentStatus.INITIALIZING
        
        # Initialize (includes bootstrap validation)
        success = await simple_agent.initialize()
        
        assert success is True
        assert simple_agent.status == AgentStatus.IDLE
        
        print(f"\nAgent {simple_agent.agent_id} initialized successfully")
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self, simple_agent):
        """Test successful task execution."""
        # Initialize agent
        await simple_agent.initialize()
        
        # Create task
        task = {
            "task_id": "test-task-1",
            "task_type": "analysis",
            "parameters": {}
        }
        
        # Execute
        result = await simple_agent.execute(task)
        
        assert result["status"] == "completed"
        assert result["task_id"] == "test-task-1"
        assert "result" in result
        assert simple_agent.task_count == 1
        assert simple_agent.success_count == 1
        assert simple_agent.status == AgentStatus.IDLE
        
        print(f"\nTask result: {result}")
    
    @pytest.mark.asyncio
    async def test_execute_multiple_tasks(self, simple_agent):
        """Test executing multiple tasks."""
        await simple_agent.initialize()
        
        # Execute 5 tasks
        for i in range(5):
            task = {
                "task_id": f"task-{i}",
                "task_type": "test",
                "parameters": {}
            }
            result = await simple_agent.execute(task)
            assert result["status"] == "completed"
        
        assert simple_agent.task_count == 5
        assert simple_agent.success_count == 5
        assert simple_agent.error_count == 0
        assert len(simple_agent.performance_history) == 5
    
    @pytest.mark.asyncio
    async def test_execute_without_initialization(self, simple_agent):
        """Test that task execution fails if agent not initialized."""
        # Don't initialize agent
        assert simple_agent.status == AgentStatus.INITIALIZING
        
        task = {"task_id": "test", "task_type": "test"}
        result = await simple_agent.execute(task)
        
        assert result["status"] == "failed"
        assert "not ready" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_self_evaluation(self, simple_agent):
        """
        Test agent self-evaluation.
        
        CRITICAL TEST: Validates meta-recursive capability.
        """
        await simple_agent.initialize()
        
        # Execute some tasks to have data
        for i in range(10):
            task = {"task_id": f"task-{i}", "task_type": "test"}
            await simple_agent.execute(task)
        
        # Self-evaluate
        evaluation = await simple_agent.self_evaluate()
        
        assert "performance_score" in evaluation
        assert "strengths" in evaluation
        assert "weaknesses" in evaluation
        assert "improvement_suggestions" in evaluation
        assert "metrics" in evaluation
        
        # Should have good performance (all tasks succeeded)
        assert evaluation["performance_score"] == 1.0
        assert len(evaluation["strengths"]) > 0
        
        print(f"\nSelf-evaluation: {evaluation}")
    
    @pytest.mark.asyncio
    async def test_report_metrics(self, simple_agent):
        """Test agent metrics reporting."""
        await simple_agent.initialize()
        
        # Execute tasks
        for i in range(3):
            task = {"task_id": f"task-{i}", "task_type": "test"}
            await simple_agent.execute(task)
        
        # Get metrics
        metrics = await simple_agent.report_metrics()
        
        assert metrics["agent_id"] == simple_agent.agent_id
        assert metrics["agent_type"] == "simple"
        assert metrics["status"] == "idle"
        assert metrics["task_count"] == 3
        assert metrics["success_count"] == 3
        assert metrics["error_count"] == 0
        assert metrics["success_rate"] == 1.0
        assert "avg_task_duration" in metrics
        assert "uptime_seconds" in metrics
        
        print(f"\nAgent metrics: {metrics}")
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, simple_agent):
        """Test health check for healthy agent."""
        await simple_agent.initialize()
        
        # Execute successful tasks
        for i in range(10):
            task = {"task_id": f"task-{i}", "task_type": "test"}
            await simple_agent.execute(task)
        
        is_healthy = await simple_agent.health_check()
        
        assert is_healthy is True
    
    @pytest.mark.asyncio
    async def test_health_check_error_state(self, simple_agent):
        """Test health check detects error state."""
        simple_agent.status = AgentStatus.ERROR
        
        is_healthy = await simple_agent.health_check()
        
        assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_shutdown(self, simple_agent):
        """Test graceful shutdown."""
        await simple_agent.initialize()
        
        # Execute some tasks
        for i in range(3):
            task = {"task_id": f"task-{i}", "task_type": "test"}
            await simple_agent.execute(task)
        
        # Shutdown
        await simple_agent.shutdown()
        
        assert simple_agent.status == AgentStatus.SHUTDOWN
    
    def test_agent_repr(self, simple_agent):
        """Test agent string representation."""
        repr_str = repr(simple_agent)
        
        assert "SimpleAgent" in repr_str
        assert simple_agent.agent_id in repr_str
        assert "simple" in repr_str


class TestAgentPerformanceTracking:
    """Test agent performance tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_performance_history_tracking(self):
        """Test that performance history is tracked correctly."""
        agent = SimpleAgent()
        await agent.initialize()
        
        # Execute tasks
        task_ids = []
        for i in range(5):
            task_id = f"task-{i}"
            task_ids.append(task_id)
            task = {"task_id": task_id, "task_type": "test"}
            await agent.execute(task)
        
        # Check performance history
        assert len(agent.performance_history) == 5
        
        for i, perf in enumerate(agent.performance_history):
            assert perf["task_id"] == task_ids[i]
            assert perf["status"] == "completed"
            assert "duration" in perf
            assert "timestamp" in perf
    
    @pytest.mark.asyncio
    async def test_success_rate_calculation(self):
        """Test success rate calculation."""
        agent = SimpleAgent()
        await agent.initialize()
        
        # Execute 10 tasks (all will succeed with SimpleAgent)
        for i in range(10):
            task = {"task_id": f"task-{i}", "task_type": "test"}
            await agent.execute(task)
        
        metrics = await agent.report_metrics()
        
        assert metrics["task_count"] == 10
        assert metrics["success_count"] == 10
        assert metrics["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_average_duration_calculation(self):
        """Test average task duration calculation."""
        agent = SimpleAgent()
        await agent.initialize()
        
        # Execute multiple tasks
        for i in range(5):
            task = {"task_id": f"task-{i}", "task_type": "test"}
            await agent.execute(task)
        
        metrics = await agent.report_metrics()
        
        assert metrics["avg_task_duration"] > 0
        assert metrics["avg_task_duration"] < 1.0  # Should be fast


# Integration test
@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_complete_lifecycle():
    """
    Test complete agent lifecycle from creation to shutdown.
    
    This is the GOLDEN PATH test that validates the entire
    bootstrap fail-pass methodology works end-to-end.
    """
    print("\n=== Agent Complete Lifecycle Test ===\n")
    
    # 1. Create agent
    agent = SimpleAgent(agent_id="test-agent-001")
    assert agent.status == AgentStatus.INITIALIZING
    print(f"1. Agent created: {agent.agent_id}")
    
    # 2. Initialize with bootstrap validation
    success = await agent.initialize()
    assert success is True
    assert agent.status == AgentStatus.IDLE
    print(f"2. Agent initialized: status={agent.status.value}")
    
    # 3. Execute tasks
    print("3. Executing tasks...")
    for i in range(10):
        task = {
            "task_id": f"task-{i}",
            "task_type": "analysis",
            "parameters": {"data": f"test-data-{i}"}
        }
        result = await agent.execute(task)
        assert result["status"] == "completed"
    print(f"   Completed {agent.task_count} tasks")
    
    # 4. Check metrics
    metrics = await agent.report_metrics()
    print(f"4. Metrics: success_rate={metrics['success_rate']:.2%}, "
          f"avg_duration={metrics['avg_task_duration']:.3f}s")
    
    # 5. Self-evaluate
    evaluation = await agent.self_evaluate()
    print(f"5. Self-evaluation: score={evaluation['performance_score']:.2f}")
    print(f"   Strengths: {evaluation['strengths']}")
    print(f"   Suggestions: {evaluation['improvement_suggestions']}")
    
    # 6. Health check
    is_healthy = await agent.health_check()
    assert is_healthy is True
    print(f"6. Health check: {'HEALTHY' if is_healthy else 'UNHEALTHY'}")
    
    # 7. Shutdown
    await agent.shutdown()
    assert agent.status == AgentStatus.SHUTDOWN
    print(f"7. Agent shutdown complete")
    
    print("\n=== Lifecycle Test PASSED ✅ ===\n")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

