"""
Live Data Pipeline Integration Test

Tests the complete data pipeline workflow:
1. Extract → Transform → Load → Validate

This test verifies:
- Task decomposition for data_pipeline
- Sequential dependency execution
- Result aggregation
- End-to-end workflow
"""

import pytest
import asyncio
from typing import Dict, Any

from app.core.task_decomposer import get_task_decomposer
from app.core.agent_registry import get_agent_registry
from app.agents.orchestrator.orchestrator_agent import OrchestratorAgent
from app.core.base_agent import BaseAgent, AgentStatus, AgentCapability, BootstrapResult


class MockDataProcessingAgent(BaseAgent):
    """Mock agent for data processing tasks."""
    
    def __init__(self, agent_id: str, capability: AgentCapability):
        super().__init__(agent_id=agent_id, agent_type="data_processing")
        self.capabilities = [capability]
        self.status = AgentStatus.IDLE
    
    async def bootstrap_and_validate(self) -> BootstrapResult:
        result = BootstrapResult()
        result.success = True
        return result
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate data processing task execution."""
        operation = task.get("operation", "")
        parameters = task.get("parameters", {})
        
        self.task_count += 1
        self.status = AgentStatus.WORKING
        
        # Simulate processing time
        await asyncio.sleep(0.01)
        
        if operation == "data_processing":
            # Extract, Transform, Load operations
            data_source = parameters.get("data_source") or parameters.get("extracted_data") or parameters.get("transformed_data", "")
            
            if "extract" in operation.lower() or "extracted_data" not in parameters:
                # Extract operation
                result_data = {
                    "status": "extracted",
                    "records": 100,
                    "data": f"Extracted from {data_source}"
                }
            elif "transformed_data" not in parameters:
                # Transform operation
                extracted = parameters.get("extracted_data", {})
                result_data = {
                    "status": "transformed",
                    "records": extracted.get("records", 0),
                    "transformed_fields": ["field1", "field2", "field3"],
                    "data": f"Transformed: {extracted.get('data', '')}"
                }
            else:
                # Load operation
                transformed = parameters.get("transformed_data", {})
                result_data = {
                    "status": "loaded",
                    "records": transformed.get("records", 0),
                    "data": f"Loaded: {transformed.get('data', '')}"
                }
        elif operation == "data_analysis":
            # Validate operation
            loaded = parameters.get("loaded_data", {})
            result_data = {
                "status": "validated",
                "records": loaded.get("records", 0),
                "validation_passed": True,
                "errors": [],
                "data": f"Validated: {loaded.get('data', '')}"
            }
        else:
            result_data = {"status": "unknown", "operation": operation}
        
        self.status = AgentStatus.IDLE
        self.success_count += 1
        
        return {
            "status": "completed",
            "result": result_data,
            "timestamp": "2025-11-04T12:00:00"
        }
    
    async def self_evaluate(self) -> Dict[str, Any]:
        return {"performance_score": 0.95}
    
    def can_handle(self, task_type: str, task_requirements: Dict[str, Any] = None) -> bool:
        capability_values = [cap.value for cap in self.capabilities]
        return task_type in capability_values or any(task_type in cap.value for cap in self.capabilities)
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "average_duration_ms": 10.0,
            "task_count": self.task_count,
            "success_count": self.success_count
        }


@pytest.mark.asyncio
class TestDataPipelineLive:
    """Live data pipeline integration tests."""
    
    @pytest.fixture
    def setup_agents(self):
        """Set up agents for data pipeline testing."""
        async def _setup():
            registry = get_agent_registry()
            
            # Create and register data processing agents
            extract_agent = MockDataProcessingAgent("extract_001", AgentCapability.DATA_PROCESSING)
            transform_agent = MockDataProcessingAgent("transform_001", AgentCapability.DATA_PROCESSING)
            load_agent = MockDataProcessingAgent("load_001", AgentCapability.DATA_PROCESSING)
            validate_agent = MockDataProcessingAgent("validate_001", AgentCapability.DATA_ANALYSIS)
            
            await registry.register(extract_agent)
            await registry.register(transform_agent)
            await registry.register(load_agent)
            await registry.register(validate_agent)
            
            # Create orchestrator
            orchestrator = OrchestratorAgent(agent_registry=registry)
            
            return {
                "registry": registry,
                "orchestrator": orchestrator,
                "agents": {
                    "extract": extract_agent,
                    "transform": transform_agent,
                    "load": load_agent,
                    "validate": validate_agent
                }
            }
        
        return _setup
    
    async def test_data_pipeline_decomposition(self, setup_agents):
        """Test that data pipeline task is correctly decomposed."""
        decomposer = get_task_decomposer()
        
        subtasks, graph = await decomposer.decompose(
            "data_pipeline",
            {"data_source": "test_database"}
        )
        
        # Should have 4 subtasks: extract, transform, load, validate
        assert len(subtasks) == 4
        
        subtask_ids = [st["id"] for st in subtasks]
        assert "extract" in subtask_ids
        assert "transform" in subtask_ids
        assert "load" in subtask_ids
        assert "validate" in subtask_ids
        
        # Check sequential dependencies
        assert "extract" in graph["transform"]
        assert "transform" in graph["load"]
        assert "load" in graph["validate"]
        
        # Extract should have no dependencies
        assert graph.get("extract", set()) == set()
    
    async def test_data_pipeline_parallel_groups(self, setup_agents):
        """Test that data pipeline has correct parallel execution groups."""
        decomposer = get_task_decomposer()
        
        subtasks, graph = await decomposer.decompose(
            "data_pipeline",
            {"data_source": "test_database"}
        )
        
        # Get parallel execution groups
        parallel_groups = decomposer.get_parallel_tasks(graph)
        
        # Should have 4 generations (each step depends on previous)
        assert len(parallel_groups) == 4
        
        # First generation should only have extract
        assert parallel_groups[0] == ["extract"]
        
        # Second generation should only have transform
        assert parallel_groups[1] == ["transform"]
        
        # Third generation should only have load
        assert parallel_groups[2] == ["load"]
        
        # Fourth generation should only have validate
        assert parallel_groups[3] == ["validate"]
    
    async def test_data_pipeline_end_to_end(self, setup_agents):
        """Test complete data pipeline execution end-to-end."""
        setup_func = setup_agents
        setup = await setup_func()
        orchestrator = setup["orchestrator"]
        
        # Execute data pipeline task
        task = {
            "task_id": "pipeline_test_001",
            "operation": "data_pipeline",
            "parameters": {
                "data_source": "production_database"
            }
        }
        
        result = await orchestrator.execute_task(task)
        
        # Verify result
        assert result["status"] in ["completed", "partial"]
        assert "subtask_count" in result
        assert result["subtask_count"] == 4
        
        # Verify task was added to history
        assert len(orchestrator.task_history) > 0
        assert orchestrator.task_history[0]["type"] == "data_pipeline"
        assert orchestrator.task_history[0]["subtask_count"] == 4
    
    async def test_data_pipeline_sequential_execution(self, setup_agents):
        """Test that data pipeline steps execute in correct order."""
        setup_func = setup_agents
        setup = await setup_func()
        decomposer = get_task_decomposer()
        
        # Decompose task
        subtasks, graph = await decomposer.decompose(
            "data_pipeline",
            {"data_source": "test_source"}
        )
        
        # Get execution order
        parallel_groups = decomposer.get_parallel_tasks(graph)
        
        # Verify sequential order
        execution_order = [task_id for group in parallel_groups for task_id in group]
        
        assert execution_order[0] == "extract"
        assert execution_order[1] == "transform"
        assert execution_order[2] == "load"
        assert execution_order[3] == "validate"
    
    async def test_data_pipeline_dependency_resolution(self, setup_agents):
        """Test that dependency references are correctly resolved."""
        setup_func = setup_agents
        setup = await setup_func()
        orchestrator = setup["orchestrator"]
        
        # Simulate previous results
        previous_results = {
            "extract": {
                "success": True,
                "result": {
                    "status": "extracted",
                    "records": 100,
                    "data": "Extracted data"
                }
            }
        }
        
        # Test dependency resolution for transform step
        transform_subtask = {
            "id": "transform",
            "type": "data_processing",
            "input": {
                "extracted_data": "{{extract.result}}"
            },
            "requirements": {}
        }
        
        resolved = orchestrator._resolve_input_dependencies(
            transform_subtask["input"],
            previous_results
        )
        
        # Should resolve to the actual result
        assert "extracted_data" in resolved
        assert resolved["extracted_data"]["status"] == "extracted"
        assert resolved["extracted_data"]["records"] == 100
    
    async def test_data_pipeline_result_aggregation(self, setup_agents):
        """Test that data pipeline results are correctly aggregated."""
        setup_func = setup_agents
        setup = await setup_func()
        orchestrator = setup["orchestrator"]
        
        # Simulate results from all pipeline steps
        results = {
            "extract": {
                "success": True,
                "result": {"status": "extracted", "records": 100},
                "execution_time_seconds": 1.0
            },
            "transform": {
                "success": True,
                "result": {"status": "transformed", "records": 100},
                "execution_time_seconds": 2.0
            },
            "load": {
                "success": True,
                "result": {"status": "loaded", "records": 100},
                "execution_time_seconds": 1.5
            },
            "validate": {
                "success": True,
                "result": {"status": "validated", "records": 100, "validation_passed": True},
                "execution_time_seconds": 0.5
            }
        }
        
        aggregated = await orchestrator.aggregate_results(results)
        
        # Verify aggregation
        assert aggregated["status"] == "completed"
        assert aggregated["total_subtasks"] == 4
        assert aggregated["successful"] == 4
        assert aggregated["failed"] == 0
        assert aggregated["success_rate"] == 1.0
        assert aggregated["total_duration_seconds"] == 5.0
        assert aggregated["avg_duration_seconds"] == 1.25
        
        # Verify aggregated result contains final validation
        assert "aggregated_result" in aggregated
        assert aggregated["aggregated_result"]["status"] == "validated"
    
    async def test_data_pipeline_with_failure(self, setup_agents):
        """Test data pipeline handling when a step fails."""
        setup_func = setup_agents
        setup = await setup_func()
        orchestrator = setup["orchestrator"]
        
        # Simulate results with one failure
        results = {
            "extract": {
                "success": True,
                "result": {"status": "extracted", "records": 100},
                "execution_time_seconds": 1.0
            },
            "transform": {
                "success": False,
                "error": "Transformation failed: Invalid data format",
                "execution_time_seconds": 0.5
            },
            "load": {
                "success": False,
                "error": "Cannot load: No transformed data",
                "execution_time_seconds": 0.0
            },
            "validate": {
                "success": False,
                "error": "Cannot validate: No loaded data",
                "execution_time_seconds": 0.0
            }
        }
        
        aggregated = await orchestrator.aggregate_results(results)
        
        # Should show partial or failed status
        assert aggregated["status"] in ["partial", "failed"]
        assert aggregated["successful"] == 1
        assert aggregated["failed"] == 3
        assert len(aggregated["errors"]) == 3
    
    async def test_data_pipeline_bootstrap(self, setup_agents):
        """Test that orchestrator bootstrap works with data pipeline."""
        setup_func = setup_agents
        setup = await setup_func()
        orchestrator = setup["orchestrator"]
        
        # Bootstrap orchestrator
        result = await orchestrator.bootstrap_and_validate()
        
        # Should validate successfully
        assert isinstance(result, BootstrapResult)
        assert "agent_registry" in result.validations
        assert "task_decomposer" in result.validations
    
    async def test_data_pipeline_agent_selection(self, setup_agents):
        """Test that correct agents are selected for each pipeline step."""
        setup_func = setup_agents
        setup = await setup_func()
        orchestrator = setup["orchestrator"]
        
        # Decompose task
        subtasks, graph = await orchestrator.decompose_task(
            "data_pipeline",
            {"data_source": "test"}
        )
        
        # Test agent selection for each step
        for subtask in subtasks:
            agent = await orchestrator.select_agent(subtask)
            
            # Should find an agent for each step
            assert agent is not None
            assert agent.can_handle(subtask["type"])
