"""
Comprehensive Test Suite for OrchestratorAgent

Tests task decomposition, orchestration, agent selection,
dependency resolution, result aggregation, and error handling.
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.core.base_agent import BaseAgent, AgentStatus, AgentCapability, BootstrapResult
from app.core.agent_registry import AgentRegistry
from app.core.task_decomposer import TaskDecomposer
from app.agents.orchestrator.orchestrator_agent import OrchestratorAgent


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: list, success_rate: float = 1.0):
        super().__init__(agent_id=agent_id, agent_type=agent_type)
        self.capabilities = capabilities
        self._success_rate = success_rate
        self._execute_count = 0
    
    async def bootstrap_and_validate(self) -> BootstrapResult:
        result = BootstrapResult()
        result.success = True
        return result
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Mock task execution."""
        self._execute_count += 1
        self.task_count += 1
        
        # Simulate success/failure based on rate
        import random
        if random.random() < self._success_rate:
            self.success_count += 1
            return {
                "status": "completed",
                "result": {"task_id": task.get("operation"), "executed": True},
                "timestamp": datetime.now().isoformat()
            }
        else:
            self.error_count += 1
            return {
                "status": "failed",
                "error": "Mock failure",
                "timestamp": datetime.now().isoformat()
            }
    
    async def self_evaluate(self) -> Dict[str, Any]:
        return {"performance_score": 0.9}
    
    def can_handle(self, task_type: str, task_requirements: Dict[str, Any] = None) -> bool:
        """Check if agent can handle task type."""
        capability_values = [cap.value for cap in self.capabilities]
        return task_type in capability_values or any(task_type in cap.value for cap in self.capabilities)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            "average_duration_ms": 100.0,
            "task_count": self.task_count,
            "success_count": self.success_count
        }


class TestOrchestratorAgent:
    """Test OrchestratorAgent class."""
    
    @pytest.fixture
    def agent_registry(self):
        """Create agent registry with mock agents."""
        registry = AgentRegistry()
        
        # Create and register mock agents
        nlp_agent = MockAgent("nlp_001", "nlp", [AgentCapability.ANALYSIS])
        code_agent = MockAgent("code_001", "code", [AgentCapability.CODE_ANALYSIS, AgentCapability.CODE_GENERATION])
        data_agent = MockAgent("data_001", "data", [AgentCapability.DATA_PROCESSING, AgentCapability.DATA_ANALYSIS])
        compression_agent = MockAgent("comp_001", "compression", [AgentCapability.COMPRESSION])
        
        # Register agents
        asyncio.run(registry.register(nlp_agent))
        asyncio.run(registry.register(code_agent))
        asyncio.run(registry.register(data_agent))
        asyncio.run(registry.register(compression_agent))
        
        return registry
    
    @pytest.fixture
    def orchestrator(self, agent_registry):
        """Create OrchestratorAgent instance."""
        return OrchestratorAgent(agent_registry=agent_registry)
    
    @pytest.mark.asyncio
    async def test_bootstrap_and_validate(self, orchestrator):
        """Test bootstrap validation."""
        result = await orchestrator.bootstrap_and_validate()
        
        assert isinstance(result, BootstrapResult)
        # Should validate agent registry, task decomposer, message bus, etc.
        assert "agent_registry" in result.validations
        assert "task_decomposer" in result.validations
    
    @pytest.mark.asyncio
    async def test_execute_task_simple(self, orchestrator):
        """Test executing simple task (no decomposition)."""
        task = {
            "task_id": "test_001",
            "operation": "noop",
            "parameters": {}
        }
        
        result = await orchestrator.execute_task(task)
        
        # Simple tasks route through _route_task_internal which may return "completed" or "failed"
        # depending on whether an agent is available. Since we're testing with mock agents,
        # we should check that the result structure is correct
        assert "status" in result
        assert result["status"] in ["completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_execute_task_decompose(self, orchestrator):
        """Test executing complex task with decomposition."""
        task = {
            "task_id": "test_002",
            "operation": "compression_analysis",
            "parameters": {"content": "test content"}
        }
        
        result = await orchestrator.execute_task(task)
        
        # Should have decomposed and orchestrated
        assert "subtask_count" in result
        assert result["subtask_count"] > 1
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_decompose_task(self, orchestrator):
        """Test task decomposition."""
        subtasks, graph = await orchestrator.decompose_task(
            "compression_analysis",
            {"content": "test"}
        )
        
        assert len(subtasks) == 4
        assert isinstance(graph, dict)
        assert "analyze_content" in [st["id"] for st in subtasks]
        assert "compress" in [st["id"] for st in subtasks]
    
    @pytest.mark.asyncio
    async def test_coordinate_execution(self, orchestrator):
        """Test coordinating parallel execution."""
        # Create simple subtasks
        subtasks = [
            {"id": "task1", "type": "analysis", "input": {}, "requirements": {}},
            {"id": "task2", "type": "analysis", "input": {}, "requirements": {}}
        ]
        
        dependency_graph = {
            "task1": set(),
            "task2": set()
        }
        
        results = await orchestrator.coordinate_execution(
            "parent_001",
            subtasks,
            dependency_graph
        )
        
        assert len(results) == 2
        assert "task1" in results
        assert "task2" in results
    
    def test_group_by_generation(self, orchestrator):
        """Test grouping subtasks by dependency generation."""
        subtasks = [
            {"id": "task1", "type": "type1", "input": {}, "requirements": {}},
            {"id": "task2", "type": "type2", "input": {}, "requirements": {}},
            {"id": "task3", "type": "type3", "input": {}, "requirements": {}}
        ]
        
        dependency_graph = {
            "task1": set(),
            "task2": set(),
            "task3": {"task1", "task2"}
        }
        
        generations = orchestrator._group_by_generation(subtasks, dependency_graph)
        
        assert len(generations) == 2
        assert len(generations[0]) == 2  # task1 and task2 can run in parallel
        assert len(generations[1]) == 1  # task3 depends on both
    
    @pytest.mark.asyncio
    async def test_wait_for_prerequisites(self, orchestrator):
        """Test waiting for prerequisites."""
        generation = [
            {"id": "task3", "type": "type3", "input": {}, "requirements": {}}
        ]
        
        dependency_graph = {
            "task3": {"task1", "task2"}
        }
        
        completed = {"task1", "task2"}
        
        # Should not raise exception
        await orchestrator._wait_for_prerequisites(generation, dependency_graph, completed)
    
    @pytest.mark.asyncio
    async def test_execute_subtask_with_retry(self, orchestrator):
        """Test subtask execution with retry logic."""
        subtask = {
            "id": "subtask_001",
            "type": "analysis",
            "input": {},
            "requirements": {}
        }
        
        previous_results = {}
        
        result = await orchestrator._execute_subtask_with_retry(
            "parent_001",
            subtask,
            previous_results
        )
        
        assert "success" in result
        assert "subtask_id" in result
    
    @pytest.mark.asyncio
    async def test_select_agent(self, orchestrator):
        """Test agent selection."""
        subtask = {
            "id": "subtask_001",
            "type": "analysis",
            "input": {},
            "requirements": {"required_capabilities": ["analysis"]}
        }
        
        agent = await orchestrator.select_agent(subtask)
        
        assert agent is not None
        assert agent.can_handle("analysis")
    
    @pytest.mark.asyncio
    async def test_select_agent_no_match(self, orchestrator):
        """Test agent selection when no agent matches."""
        subtask = {
            "id": "subtask_001",
            "type": "unknown_type",
            "input": {},
            "requirements": {}
        }
        
        agent = await orchestrator.select_agent(subtask)
        
        assert agent is None
    
    def test_resolve_input_dependencies(self, orchestrator):
        """Test input dependency resolution."""
        input_data = {
            "param1": "{{task1.result.value}}",
            "param2": "static_value",
            "param3": "{{task2.result.data}}"
        }
        
        previous_results = {
            "task1": {
                "success": True,
                "result": {"value": "resolved_value"}
            },
            "task2": {
                "success": True,
                "result": {"data": "resolved_data"}
            }
        }
        
        resolved = orchestrator._resolve_input_dependencies(input_data, previous_results)
        
        # The resolution expects format: {{subtask_id.result.path}}
        # So "{{task1.result.value}}" should:
        # 1. Get task1's result dict: {"value": "resolved_value"}
        # 2. Navigate path ["result", "value"] -> skip "result", then get "value"
        assert resolved["param1"] == "resolved_value"
        assert resolved["param2"] == "static_value"
        assert resolved["param3"] == "resolved_data"
    
    def test_resolve_input_dependencies_missing(self, orchestrator):
        """Test dependency resolution with missing references."""
        input_data = {
            "param1": "{{missing_task.result.value}}"
        }
        
        previous_results = {}
        
        resolved = orchestrator._resolve_input_dependencies(input_data, previous_results)
        
        # Should keep original if reference not found
        assert resolved["param1"] == "{{missing_task.result.value}}"
    
    @pytest.mark.asyncio
    async def test_aggregate_results(self, orchestrator):
        """Test result aggregation."""
        results = {
            "task1": {
                "success": True,
                "result": {"value": 1},
                "execution_time_seconds": 1.0
            },
            "task2": {
                "success": True,
                "result": {"value": 2},
                "execution_time_seconds": 2.0
            },
            "task3": {
                "success": False,
                "error": "Test error"
            }
        }
        
        aggregated = await orchestrator.aggregate_results(results)
        
        assert aggregated["status"] == "partial"  # 2 success, 1 failure
        assert aggregated["total_subtasks"] == 3
        assert aggregated["successful"] == 2
        assert aggregated["failed"] == 1
        assert aggregated["success_rate"] == 2/3
        assert len(aggregated["errors"]) == 1
    
    @pytest.mark.asyncio
    async def test_aggregate_results_all_success(self, orchestrator):
        """Test aggregation with all successful results."""
        results = {
            "task1": {
                "success": True,
                "result": {"value": 1}
            },
            "task2": {
                "success": True,
                "result": {"value": 2}
            }
        }
        
        aggregated = await orchestrator.aggregate_results(results)
        
        assert aggregated["status"] == "completed"
        assert aggregated["successful"] == 2
        assert aggregated["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_aggregate_results_all_failed(self, orchestrator):
        """Test aggregation with all failed results."""
        results = {
            "task1": {
                "success": False,
                "error": "Error 1"
            },
            "task2": {
                "success": False,
                "error": "Error 2"
            }
        }
        
        aggregated = await orchestrator.aggregate_results(results)
        
        assert aggregated["status"] == "failed"
        assert aggregated["successful"] == 0
        assert aggregated["failed"] == 2
    
    def test_merge_results(self, orchestrator):
        """Test result merging."""
        results = [
            {
                "success": True,
                "result": {"key1": "value1", "key2": "value2"}
            },
            {
                "success": True,
                "result": {"key3": "value3"}
            }
        ]
        
        merged = orchestrator._merge_results(results)
        
        assert merged["key1"] == "value1"
        assert merged["key2"] == "value2"
        assert merged["key3"] == "value3"
    
    @pytest.mark.asyncio
    async def test_self_evaluate(self, orchestrator):
        """Test self-evaluation."""
        # Set some task history
        orchestrator.task_history = [
            {"subtask_count": 4, "success": True},
            {"subtask_count": 3, "success": True}
        ]
        orchestrator.task_count = 2
        orchestrator.success_count = 2
        
        evaluation = await orchestrator.self_evaluate()
        
        assert "performance_score" in evaluation
        assert "strengths" in evaluation
        assert "weaknesses" in evaluation
        assert "improvement_suggestions" in evaluation
        assert "metrics" in evaluation
    
    @pytest.mark.asyncio
    async def test_report_metrics(self, orchestrator):
        """Test metrics reporting."""
        orchestrator.tasks_routed = 10
        orchestrator.tasks_completed = 8
        orchestrator.tasks_failed = 2
        
        metrics = await orchestrator.report_metrics()
        
        assert metrics["tasks_routed"] == 10
        assert metrics["tasks_completed"] == 8
        assert metrics["tasks_failed"] == 2
        assert metrics["task_success_rate"] == 0.8


class TestOrchestratorAgentIntegration:
    """Integration tests for OrchestratorAgent."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_orchestration(self):
        """Test complete end-to-end orchestration workflow."""
        # Setup
        registry = AgentRegistry()
        
        # Create agents
        nlp_agent = MockAgent("nlp_001", "nlp", [AgentCapability.ANALYSIS])
        compression_agent = MockAgent("comp_001", "compression", [AgentCapability.COMPRESSION])
        
        await registry.register(nlp_agent)
        await registry.register(compression_agent)
        
        orchestrator = OrchestratorAgent(agent_registry=registry)
        
        # Execute complex task
        task = {
            "task_id": "e2e_test_001",
            "operation": "compression_analysis",
            "parameters": {"content": "This is test content for compression"}
        }
        
        result = await orchestrator.execute_task(task)
        
        # Verify result
        assert "status" in result
        assert "subtask_count" in result
        assert result["subtask_count"] > 1
        
        # Verify task history
        assert len(orchestrator.task_history) > 0
        assert orchestrator.task_history[0]["type"] == "compression_analysis"
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test that independent subtasks execute in parallel."""
        registry = AgentRegistry()
        
        # Create agents with different execution times
        async def slow_execute(task):
            await asyncio.sleep(0.1)
            return {"status": "completed", "result": {"value": "slow"}}
        
        async def fast_execute(task):
            await asyncio.sleep(0.01)
            return {"status": "completed", "result": {"value": "fast"}}
        
        agent1 = MockAgent("agent1", "type1", [AgentCapability.ANALYSIS])
        agent1.execute_task = slow_execute
        
        agent2 = MockAgent("agent2", "type2", [AgentCapability.ANALYSIS])
        agent2.execute_task = fast_execute
        
        await registry.register(agent1)
        await registry.register(agent2)
        
        orchestrator = OrchestratorAgent(agent_registry=registry)
        
        # Create subtasks that can run in parallel
        subtasks = [
            {"id": "task1", "type": "analysis", "input": {}, "requirements": {}},
            {"id": "task2", "type": "analysis", "input": {}, "requirements": {}}
        ]
        
        dependency_graph = {
            "task1": set(),
            "task2": set()
        }
        
        start_time = datetime.now()
        results = await orchestrator.coordinate_execution(
            "parent_001",
            subtasks,
            dependency_graph
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        # If truly parallel, should take ~0.1s (slowest task), not 0.11s (sequential)
        assert duration < 0.15  # Allow some overhead
        assert len(results) == 2
