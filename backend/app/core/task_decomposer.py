"""
Task Decomposer

Intelligent task decomposition engine that breaks complex tasks into subtasks
with dependency management. Uses topological sort (Kahn's algorithm) to
determine execution order and parallel execution groups.

Key Features:
- Multiple decomposition strategies (compression, code review, data pipeline)
- Dependency graph construction (DAG)
- Topological sort for execution ordering
- Parallel execution group detection
- Cycle detection
"""

from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque, defaultdict
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Subtask:
    """Represents a decomposed subtask."""
    id: str
    type: str
    input: Dict[str, Any]
    requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    priority: int = 5  # Priority level (1-10, default 5)
    estimated_duration: float = 0.0  # Estimated execution time in seconds


class TaskDecomposer:
    """
    Decomposes complex tasks into subtasks with dependencies.
    
    Uses multiple decomposition strategies based on task type.
    Builds dependency graphs and determines optimal execution order.
    """
    
    def __init__(self):
        """Initialize task decomposer with strategies."""
        self.decomposition_strategies = {
            "compression_analysis": self._decompose_compression_analysis,
            "code_review": self._decompose_code_review,
            "data_pipeline": self._decompose_data_pipeline,
            "research_synthesis": self._decompose_research_synthesis,
            "multi_step": self._decompose_multi_step,
        }
        
        # Cache for decomposition results
        self.decomposition_cache: Dict[str, Tuple[List[Dict[str, Any]], Dict[str, Set[str]]]] = {}
        
        logger.info("TaskDecomposer initialized")
    
    async def decompose(
        self,
        task_type: str,
        task_input: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Set[str]]]:
        """
        Decompose task into subtasks with dependency graph.
        
        Args:
            task_type: Type of task to decompose
            task_input: Input data for the task
            
        Returns:
            Tuple of:
            - List of subtask dictionaries
            - Dependency graph (subtask_id -> set of prerequisite IDs)
        """
        # Check cache
        cache_key = f"{task_type}_{hash(str(task_input))}"
        if cache_key in self.decomposition_cache:
            logger.debug(f"Using cached decomposition for {task_type}")
            return self.decomposition_cache[cache_key]
        
        # Get decomposition strategy
        strategy = self.decomposition_strategies.get(task_type)
        
        if not strategy:
            # Default: single subtask (no decomposition)
            logger.info(f"No strategy for {task_type}, using default single task")
            subtask = Subtask(
                id=f"subtask_{uuid.uuid4().hex[:8]}",
                type=task_type,
                input=task_input,
                requirements={},
                dependencies=set()
            )
            subtask_dict = self._subtask_to_dict(subtask)
            dependency_graph = {}
            
            result = ([subtask_dict], dependency_graph)
            self.decomposition_cache[cache_key] = result
            return result
        
        # Decompose using strategy
        try:
            subtasks = await strategy(task_input)
        except Exception as e:
            logger.error(f"Decomposition strategy failed for {task_type}: {e}")
            # Fallback to single task
            subtask = Subtask(
                id=f"subtask_{uuid.uuid4().hex[:8]}",
                type=task_type,
                input=task_input,
                requirements={},
                dependencies=set()
            )
            subtasks = [subtask]
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(subtasks)
        
        # Validate no cycles
        if self._has_cycles(dependency_graph):
            logger.warning(f"Circular dependencies detected in {task_type}, removing cycles")
            dependency_graph = self._remove_cycles(dependency_graph)
        
        # Convert to dictionaries
        subtask_dicts = [self._subtask_to_dict(st) for st in subtasks]
        
        result = (subtask_dicts, dependency_graph)
        self.decomposition_cache[cache_key] = result
        return result
    
    def _subtask_to_dict(self, subtask: Subtask) -> Dict[str, Any]:
        """Convert Subtask to dictionary."""
        return {
            "id": subtask.id,
            "type": subtask.type,
            "input": subtask.input,
            "requirements": subtask.requirements,
            "dependencies": list(subtask.dependencies),
            "priority": subtask.priority,
            "estimated_duration": subtask.estimated_duration
        }
    
    def _build_dependency_graph(
        self,
        subtasks: List[Subtask]
    ) -> Dict[str, Set[str]]:
        """
        Build dependency graph from subtasks.
        
        Returns:
            Dictionary mapping subtask_id -> set of prerequisite IDs
        """
        graph = {}
        subtask_ids = {st.id for st in subtasks}
        
        for subtask in subtasks:
            # Validate dependencies exist
            valid_deps = {
                dep_id for dep_id in subtask.dependencies
                if dep_id in subtask_ids
            }
            
            graph[subtask.id] = valid_deps
            
            # Warn about invalid dependencies
            invalid_deps = subtask.dependencies - valid_deps
            if invalid_deps:
                logger.warning(
                    f"Subtask {subtask.id} has invalid dependencies: {invalid_deps}"
                )
        
        return graph
    
    def _topological_sort(
        self,
        dependency_graph: Dict[str, Set[str]]
    ) -> List[List[str]]:
        """
        Kahn's algorithm for topological sort.
        
        Groups tasks into generations (levels) where tasks in the same
        generation can run in parallel.
        
        Returns:
            List of generations (lists of task IDs that can run in parallel)
        """
        # Calculate in-degrees
        in_degree = defaultdict(int)
        all_nodes = set()
        
        # Collect all nodes (from graph keys and all dependencies)
        for node in dependency_graph:
            all_nodes.add(node)
            for dep in dependency_graph[node]:
                all_nodes.add(dep)
        
        # Calculate in-degrees (how many dependencies each node has)
        for node in all_nodes:
            in_degree[node] = 0
        
        for node in dependency_graph:
            for dep in dependency_graph[node]:
                in_degree[node] += 1
        
        # Find zero in-degree nodes (first generation)
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        generations = []
        processed = set()
        
        while queue:
            # Current generation
            current_gen = list(queue)
            generations.append(current_gen)
            queue.clear()
            processed.update(current_gen)
            
            # Find next generation: nodes whose dependencies are all processed
            for node in all_nodes:
                if node in processed:
                    continue
                
                # Check if all dependencies are processed
                deps = dependency_graph.get(node, set())
                if deps.issubset(processed):
                    queue.append(node)
        
        # Handle any remaining nodes (cycles would cause issues)
        unprocessed = all_nodes - processed
        if unprocessed:
            logger.warning(f"Circular dependencies detected: {unprocessed}")
            # Add remaining nodes as a final generation
            if unprocessed:
                generations.append(list(unprocessed))
        
        return generations
    
    def get_parallel_tasks(
        self,
        dependency_graph: Dict[str, Set[str]]
    ) -> List[List[str]]:
        """
        Get tasks that can be executed in parallel.
        
        Uses topological sort to group tasks by dependency level.
        
        Returns:
            List of lists, where each inner list contains task IDs
            that can run in parallel
        """
        return self._topological_sort(dependency_graph)
    
    def _has_cycles(self, dependency_graph: Dict[str, Set[str]]) -> bool:
        """
        Check if dependency graph has cycles.
        
        Uses three-color DFS algorithm.
        """
        # Three-color DFS: white (unvisited), gray (visiting), black (visited)
        color = {node: "white" for node in dependency_graph}
        
        def dfs(node: str) -> bool:
            """DFS to detect cycles."""
            color[node] = "gray"  # Mark as visiting
            
            for neighbor in dependency_graph.get(node, set()):
                if neighbor not in color:
                    color[neighbor] = "white"
                
                if color[neighbor] == "gray":  # Back edge detected
                    return True  # Cycle found
                
                if color[neighbor] == "white" and dfs(neighbor):
                    return True
            
            color[node] = "black"  # Mark as visited
            return False
        
        # Check all nodes
        for node in dependency_graph:
            if color[node] == "white":
                if dfs(node):
                    return True
        
        return False
    
    def _remove_cycles(
        self,
        dependency_graph: Dict[str, Set[str]]
    ) -> Dict[str, Set[str]]:
        """
        Remove cycles from dependency graph.
        
        Uses a simple heuristic: remove edges that create cycles.
        """
        # Simple approach: remove edges that point to nodes already in path
        cleaned_graph = {}
        
        for node, deps in dependency_graph.items():
            cleaned_deps = set()
            for dep in deps:
                # Check if adding this dependency creates a cycle
                # by checking if node is reachable from dep
                if not self._is_reachable(dep, node, dependency_graph):
                    cleaned_deps.add(dep)
                else:
                    logger.warning(f"Removing circular dependency: {node} -> {dep}")
            
            cleaned_graph[node] = cleaned_deps
        
        return cleaned_graph
    
    def _is_reachable(
        self,
        start: str,
        target: str,
        graph: Dict[str, Set[str]]
    ) -> bool:
        """
        Check if target is reachable from start using DFS.
        
        Note: Graph represents dependencies (node depends on deps in graph[node]).
        So we need to check reverse: can we reach target by following dependencies?
        """
        if start == target:
            return True
        
        visited = set()
        
        def dfs(node: str) -> bool:
            if node == target:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            # Check nodes that depend on this one (reverse traversal)
            for other_node in graph:
                if node in graph[other_node]:
                    if dfs(other_node):
                        return True
            return False
        
        return dfs(start)
    
    # Decomposition Strategies
    
    async def _decompose_compression_analysis(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """
        Decompose compression analysis task.
        
        Steps:
        1. Analyze content (NLP) - Parallel
        2. Analyze structure (NLP) - Parallel
        3. Select algorithm (depends on 1,2)
        4. Compress (depends on 3)
        """
        content = task_input.get("content", "")
        
        subtasks = [
            Subtask(
                id="analyze_content",
                type="text_analysis",
                input={"text": content},
                requirements={"required_capabilities": ["analysis"]},
                dependencies=set(),
                priority=8,
                estimated_duration=2.0
            ),
            Subtask(
                id="analyze_structure",
                type="entity_extraction",
                input={"text": content},
                requirements={"required_capabilities": ["analysis"]},
                dependencies=set(),
                priority=8,
                estimated_duration=2.5
            ),
            Subtask(
                id="select_algorithm",
                type="algorithm_selection",
                input={
                    "content_analysis": "{{analyze_content.result}}",
                    "structure_analysis": "{{analyze_structure.result}}"
                },
                requirements={},
                dependencies={"analyze_content", "analyze_structure"},
                priority=9,
                estimated_duration=1.0
            ),
            Subtask(
                id="compress",
                type="compression",
                input={
                    "content": content,
                    "algorithm": "{{select_algorithm.result.algorithm}}"
                },
                requirements={"required_capabilities": ["compression"]},
                dependencies={"select_algorithm"},
                priority=10,
                estimated_duration=5.0
            )
        ]
        
        return subtasks
    
    async def _decompose_code_review(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """
        Decompose code review task.
        
        Steps:
        1. Analyze code structure - Parallel
        2. Check patterns - Parallel
        3. Generate review (depends on 1,2)
        """
        code = task_input.get("code", "")
        
        subtasks = [
            Subtask(
                id="analyze_structure",
                type="code_analysis",
                input={"code": code},
                requirements={"required_capabilities": ["code_analysis"]},
                dependencies=set(),
                priority=8,
                estimated_duration=3.0
            ),
            Subtask(
                id="check_patterns",
                type="pattern_checking",
                input={"code": code},
                requirements={"required_capabilities": ["code_analysis"]},
                dependencies=set(),
                priority=8,
                estimated_duration=2.5
            ),
            Subtask(
                id="generate_review",
                type="code_generation",
                input={
                    "structure_analysis": "{{analyze_structure.result}}",
                    "pattern_analysis": "{{check_patterns.result}}"
                },
                requirements={"required_capabilities": ["code_generation"]},
                dependencies={"analyze_structure", "check_patterns"},
                priority=9,
                estimated_duration=4.0
            )
        ]
        
        return subtasks
    
    async def _decompose_data_pipeline(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """
        Decompose data pipeline task.
        
        Steps:
        1. Extract data
        2. Transform data (depends on 1)
        3. Load data (depends on 2)
        4. Validate (depends on 3)
        """
        data_source = task_input.get("data_source", "")
        
        subtasks = [
            Subtask(
                id="extract",
                type="data_processing",
                input={"data_source": data_source},
                requirements={"required_capabilities": ["data_processing"]},
                dependencies=set(),
                priority=8,
                estimated_duration=10.0
            ),
            Subtask(
                id="transform",
                type="data_processing",
                input={"extracted_data": "{{extract.result}}"},
                requirements={"required_capabilities": ["data_processing"]},
                dependencies={"extract"},
                priority=9,
                estimated_duration=15.0
            ),
            Subtask(
                id="load",
                type="data_processing",
                input={"transformed_data": "{{transform.result}}"},
                requirements={"required_capabilities": ["data_processing"]},
                dependencies={"transform"},
                priority=9,
                estimated_duration=5.0
            ),
            Subtask(
                id="validate",
                type="data_analysis",
                input={"loaded_data": "{{load.result}}"},
                requirements={"required_capabilities": ["data_analysis"]},
                dependencies={"load"},
                priority=10,
                estimated_duration=3.0
            )
        ]
        
        return subtasks
    
    async def _decompose_research_synthesis(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """
        Decompose research synthesis task.
        
        Steps:
        1. Research topic (parallel multiple sources)
        2. Analyze findings (depends on 1)
        3. Synthesize (depends on 2)
        """
        topic = task_input.get("topic", "")
        
        subtasks = [
            Subtask(
                id="research_source1",
                type="research",
                input={"topic": topic, "source": "source1"},
                requirements={"required_capabilities": ["research"]},
                dependencies=set(),
                priority=7,
                estimated_duration=5.0
            ),
            Subtask(
                id="research_source2",
                type="research",
                input={"topic": topic, "source": "source2"},
                requirements={"required_capabilities": ["research"]},
                dependencies=set(),
                priority=7,
                estimated_duration=5.0
            ),
            Subtask(
                id="analyze_findings",
                type="data_analysis",
                input={
                    "source1_results": "{{research_source1.result}}",
                    "source2_results": "{{research_source2.result}}"
                },
                requirements={"required_capabilities": ["data_analysis"]},
                dependencies={"research_source1", "research_source2"},
                priority=8,
                estimated_duration=8.0
            ),
            Subtask(
                id="synthesize",
                type="code_generation",
                input={"analysis": "{{analyze_findings.result}}"},
                requirements={"required_capabilities": ["code_generation"]},
                dependencies={"analyze_findings"},
                priority=9,
                estimated_duration=6.0
            )
        ]
        
        return subtasks
    
    async def _decompose_multi_step(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """
        Generic multi-step decomposition.
        
        Creates sequential subtasks based on input.
        """
        steps = task_input.get("steps", [])
        
        if not steps:
            # Default: single step
            return [
                Subtask(
                    id="step_1",
                    type=task_input.get("task_type", "unknown"),
                    input=task_input,
                    requirements={},
                    dependencies=set(),
                    priority=5
                )
            ]
        
        subtasks = []
        previous_step_id = None
        
        for i, step in enumerate(steps, 1):
            step_id = f"step_{i}"
            step_input = step.get("input", {})
            
            # If previous step exists, add dependency
            dependencies = set()
            if previous_step_id:
                dependencies.add(previous_step_id)
                # Add reference to previous result
                step_input[f"previous_result"] = f"{{{{{previous_step_id}.result}}}}"
            
            subtask = Subtask(
                id=step_id,
                type=step.get("type", "unknown"),
                input=step_input,
                requirements=step.get("requirements", {}),
                dependencies=dependencies,
                priority=step.get("priority", 5),
                estimated_duration=step.get("estimated_duration", 0.0)
            )
            
            subtasks.append(subtask)
            previous_step_id = step_id
        
        return subtasks


# Singleton instance
_task_decomposer: Optional[TaskDecomposer] = None


def get_task_decomposer() -> TaskDecomposer:
    """
    Get global task decomposer singleton.
    
    Returns:
        Global TaskDecomposer instance
    """
    global _task_decomposer
    if _task_decomposer is None:
        _task_decomposer = TaskDecomposer()
    return _task_decomposer
