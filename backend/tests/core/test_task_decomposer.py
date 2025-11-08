"""
Comprehensive Test Suite for TaskDecomposer

Tests all decomposition strategies, dependency graph building,
topological sort, cycle detection, and parallel task extraction.
"""

import pytest
import asyncio
from typing import Dict, Any, Set

from app.core.task_decomposer import (
    TaskDecomposer, Subtask, get_task_decomposer
)


class TestSubtask:
    """Test Subtask dataclass."""
    
    def test_subtask_creation(self):
        """Test basic subtask creation."""
        subtask = Subtask(
            id="test_1",
            type="test_type",
            input={"data": "test"},
            requirements={"capability": "test"},
            dependencies={"dep_1"},
            priority=8,
            estimated_duration=5.0
        )
        
        assert subtask.id == "test_1"
        assert subtask.type == "test_type"
        assert subtask.input == {"data": "test"}
        assert subtask.requirements == {"capability": "test"}
        assert subtask.dependencies == {"dep_1"}
        assert subtask.priority == 8
        assert subtask.estimated_duration == 5.0
    
    def test_subtask_defaults(self):
        """Test subtask with default values."""
        subtask = Subtask(
            id="test_2",
            type="test_type",
            input={}
        )
        
        assert subtask.requirements == {}
        assert subtask.dependencies == set()
        assert subtask.priority == 5
        assert subtask.estimated_duration == 0.0


class TestTaskDecomposer:
    """Test TaskDecomposer class."""
    
    @pytest.fixture
    def decomposer(self):
        """Create TaskDecomposer instance."""
        return TaskDecomposer()
    
    @pytest.mark.asyncio
    async def test_decompose_unknown_task(self, decomposer):
        """Test decomposition of unknown task type (default behavior)."""
        subtasks, graph = await decomposer.decompose("unknown_task", {"data": "test"})
        
        assert len(subtasks) == 1
        assert subtasks[0]["type"] == "unknown_task"
        assert subtasks[0]["input"] == {"data": "test"}
        assert graph == {}
    
    @pytest.mark.asyncio
    async def test_decompose_compression_analysis(self, decomposer):
        """Test compression analysis decomposition."""
        subtasks, graph = await decomposer.decompose(
            "compression_analysis",
            {"content": "test content to compress"}
        )
        
        # Should have 4 subtasks
        assert len(subtasks) == 4
        
        # Check subtask IDs
        subtask_ids = [st["id"] for st in subtasks]
        assert "analyze_content" in subtask_ids
        assert "analyze_structure" in subtask_ids
        assert "select_algorithm" in subtask_ids
        assert "compress" in subtask_ids
        
        # Check dependencies
        assert "select_algorithm" in graph
        assert "analyze_content" in graph["select_algorithm"]
        assert "analyze_structure" in graph["select_algorithm"]
        assert "compress" in graph
        assert "select_algorithm" in graph["compress"]
    
    @pytest.mark.asyncio
    async def test_decompose_code_review(self, decomposer):
        """Test code review decomposition."""
        subtasks, graph = await decomposer.decompose(
            "code_review",
            {"code": "def test(): pass"}
        )
        
        assert len(subtasks) == 3
        subtask_ids = [st["id"] for st in subtasks]
        assert "analyze_structure" in subtask_ids
        assert "check_patterns" in subtask_ids
        assert "generate_review" in subtask_ids
    
    @pytest.mark.asyncio
    async def test_decompose_data_pipeline(self, decomposer):
        """Test data pipeline decomposition."""
        subtasks, graph = await decomposer.decompose(
            "data_pipeline",
            {"data_source": "test_source"}
        )
        
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
    
    @pytest.mark.asyncio
    async def test_decompose_research_synthesis(self, decomposer):
        """Test research synthesis decomposition."""
        subtasks, graph = await decomposer.decompose(
            "research_synthesis",
            {"topic": "test topic"}
        )
        
        assert len(subtasks) == 4
        subtask_ids = [st["id"] for st in subtasks]
        assert "research_source1" in subtask_ids
        assert "research_source2" in subtask_ids
        assert "analyze_findings" in subtask_ids
        assert "synthesize" in subtask_ids
        
        # Check parallel research tasks (they have no dependencies)
        assert graph.get("research_source1", set()) == set()
        assert graph.get("research_source2", set()) == set()
        # Both research tasks should be dependencies of analyze_findings
        assert "research_source1" in graph["analyze_findings"]
        assert "research_source2" in graph["analyze_findings"]
    
    @pytest.mark.asyncio
    async def test_decompose_multi_step(self, decomposer):
        """Test multi-step decomposition."""
        subtasks, graph = await decomposer.decompose(
            "multi_step",
            {
                "steps": [
                    {"type": "step1", "input": {"data": "test1"}},
                    {"type": "step2", "input": {"data": "test2"}},
                    {"type": "step3", "input": {"data": "test3"}}
                ]
            }
        )
        
        assert len(subtasks) == 3
        assert subtasks[0]["id"] == "step_1"
        assert subtasks[1]["id"] == "step_2"
        assert subtasks[2]["id"] == "step_3"
        
        # Check sequential dependencies
        assert "step_1" in graph["step_2"]
        assert "step_2" in graph["step_3"]
    
    @pytest.mark.asyncio
    async def test_decompose_multi_step_empty(self, decomposer):
        """Test multi-step with empty steps."""
        subtasks, graph = await decomposer.decompose(
            "multi_step",
            {}
        )
        
        assert len(subtasks) == 1
        assert subtasks[0]["id"] == "step_1"
    
    def test_build_dependency_graph(self, decomposer):
        """Test dependency graph building."""
        subtasks = [
            Subtask(id="task1", type="type1", input={}, dependencies=set()),
            Subtask(id="task2", type="type2", input={}, dependencies={"task1"}),
            Subtask(id="task3", type="type3", input={}, dependencies={"task1", "task2"})
        ]
        
        graph = decomposer._build_dependency_graph(subtasks)
        
        assert "task1" in graph
        assert graph["task1"] == set()
        assert graph["task2"] == {"task1"}
        assert graph["task3"] == {"task1", "task2"}
    
    def test_build_dependency_graph_invalid_deps(self, decomposer):
        """Test dependency graph with invalid dependencies."""
        subtasks = [
            Subtask(id="task1", type="type1", input={}, dependencies={"invalid_task"})
        ]
        
        graph = decomposer._build_dependency_graph(subtasks)
        
        # Invalid dependency should be removed
        assert graph["task1"] == set()
    
    def test_topological_sort_simple(self, decomposer):
        """Test topological sort with simple graph."""
        graph = {
            "task1": set(),
            "task2": {"task1"},
            "task3": {"task2"}
        }
        
        generations = decomposer._topological_sort(graph)
        
        assert len(generations) == 3
        assert generations[0] == ["task1"]
        assert generations[1] == ["task2"]
        assert generations[2] == ["task3"]
    
    def test_topological_sort_parallel(self, decomposer):
        """Test topological sort with parallel tasks."""
        graph = {
            "task1": set(),
            "task2": set(),
            "task3": {"task1", "task2"}
        }
        
        generations = decomposer._topological_sort(graph)
        
        assert len(generations) == 2
        # First generation should have both independent tasks
        assert set(generations[0]) == {"task1", "task2"}
        assert generations[1] == ["task3"]
    
    def test_topological_sort_complex(self, decomposer):
        """Test topological sort with complex graph."""
        graph = {
            "analyze_content": set(),
            "analyze_structure": set(),
            "select_algorithm": {"analyze_content", "analyze_structure"},
            "compress": {"select_algorithm"}
        }
        
        generations = decomposer._topological_sort(graph)
        
        assert len(generations) == 3
        assert set(generations[0]) == {"analyze_content", "analyze_structure"}
        assert generations[1] == ["select_algorithm"]
        assert generations[2] == ["compress"]
    
    def test_get_parallel_tasks(self, decomposer):
        """Test parallel task extraction."""
        graph = {
            "task1": set(),
            "task2": set(),
            "task3": {"task1", "task2"}
        }
        
        parallel_groups = decomposer.get_parallel_tasks(graph)
        
        assert len(parallel_groups) == 2
        assert set(parallel_groups[0]) == {"task1", "task2"}
        assert parallel_groups[1] == ["task3"]
    
    def test_has_cycles_no_cycles(self, decomposer):
        """Test cycle detection with no cycles."""
        graph = {
            "task1": set(),
            "task2": {"task1"},
            "task3": {"task2"}
        }
        
        assert not decomposer._has_cycles(graph)
    
    def test_has_cycles_with_cycles(self, decomposer):
        """Test cycle detection with cycles."""
        graph = {
            "task1": {"task2"},
            "task2": {"task1"}
        }
        
        assert decomposer._has_cycles(graph)
    
    def test_remove_cycles(self, decomposer):
        """Test cycle removal."""
        graph = {
            "task1": {"task2"},
            "task2": {"task1"}
        }
        
        cleaned = decomposer._remove_cycles(graph)
        
        # At least one edge should be removed
        assert len(cleaned) == 2
        # Check that cycles are removed
        assert not decomposer._has_cycles(cleaned)
    
    def test_is_reachable(self, decomposer):
        """Test reachability check."""
        graph = {
            "task1": set(),
            "task2": {"task1"},
            "task3": {"task2"}
        }
        
        assert decomposer._is_reachable("task1", "task3", graph)
        assert not decomposer._is_reachable("task3", "task1", graph)
    
    def test_subtask_to_dict(self, decomposer):
        """Test subtask to dictionary conversion."""
        subtask = Subtask(
            id="test_id",
            type="test_type",
            input={"data": "test"},
            requirements={"cap": "val"},
            dependencies={"dep1", "dep2"},
            priority=9,
            estimated_duration=10.0
        )
        
        result = decomposer._subtask_to_dict(subtask)
        
        assert result["id"] == "test_id"
        assert result["type"] == "test_type"
        assert result["input"] == {"data": "test"}
        assert result["requirements"] == {"cap": "val"}
        assert isinstance(result["dependencies"], list)
        assert set(result["dependencies"]) == {"dep1", "dep2"}
        assert result["priority"] == 9
        assert result["estimated_duration"] == 10.0
    
    @pytest.mark.asyncio
    async def test_decomposition_caching(self, decomposer):
        """Test that decomposition results are cached."""
        task_input = {"content": "test"}
        
        # First call
        result1 = await decomposer.decompose("compression_analysis", task_input)
        
        # Second call (should use cache)
        result2 = await decomposer.decompose("compression_analysis", task_input)
        
        # Results should be identical
        assert len(result1[0]) == len(result2[0])
        assert result1[0][0]["id"] == result2[0][0]["id"]


class TestTaskDecomposerSingleton:
    """Test singleton get_task_decomposer function."""
    
    def test_get_task_decomposer_singleton(self):
        """Test that get_task_decomposer returns singleton."""
        decomposer1 = get_task_decomposer()
        decomposer2 = get_task_decomposer()
        
        assert decomposer1 is decomposer2
    
    @pytest.mark.asyncio
    async def test_singleton_decomposition(self):
        """Test decomposition using singleton."""
        decomposer = get_task_decomposer()
        
        subtasks, graph = await decomposer.decompose(
            "compression_analysis",
            {"content": "test"}
        )
        
        assert len(subtasks) == 4
        assert "analyze_content" in [st["id"] for st in subtasks]


class TestTaskDecomposerIntegration:
    """Integration tests for TaskDecomposer."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete decomposition workflow."""
        decomposer = TaskDecomposer()
        
        # Decompose task
        subtasks, graph = await decomposer.decompose(
            "compression_analysis",
            {"content": "This is test content for compression analysis"}
        )
        
        # Verify structure
        assert len(subtasks) > 0
        assert isinstance(graph, dict)
        
        # Get parallel execution groups
        parallel_groups = decomposer.get_parallel_tasks(graph)
        
        # Verify groups
        assert len(parallel_groups) > 0
        assert all(isinstance(group, list) for group in parallel_groups)
        
        # Verify no cycles
        assert not decomposer._has_cycles(graph)
    
    @pytest.mark.asyncio
    async def test_all_decomposition_strategies(self):
        """Test all decomposition strategies work."""
        decomposer = TaskDecomposer()
        
        strategies = [
            ("compression_analysis", {"content": "test"}),
            ("code_review", {"code": "def test(): pass"}),
            ("data_pipeline", {"data_source": "source"}),
            ("research_synthesis", {"topic": "topic"}),
            ("multi_step", {"steps": [{"type": "step1", "input": {}}]})
        ]
        
        for strategy_name, task_input in strategies:
            subtasks, graph = await decomposer.decompose(strategy_name, task_input)
            
            assert len(subtasks) > 0
            assert isinstance(graph, dict)
            
            # Verify no cycles
            assert not decomposer._has_cycles(graph)
            
            # Verify parallel groups can be extracted
            parallel_groups = decomposer.get_parallel_tasks(graph)
            assert len(parallel_groups) > 0
