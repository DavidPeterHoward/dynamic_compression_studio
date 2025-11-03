# Complete Algorithms & Data Structures Specification
## Ultra-Detailed Implementation Guide for All System Components

---

## TABLE OF CONTENTS

1. [Task Orchestration Algorithms](#1-task-orchestration-algorithms)
2. [Agent Selection Algorithms](#2-agent-selection-algorithms)
3. [Learning Algorithms](#3-learning-algorithms)
4. [Self-Improvement Algorithms](#4-self-improvement-algorithms)
5. [Complete Data Structures](#5-complete-data-structures)
6. [Graph Algorithms](#6-graph-algorithms)
7. [Optimization Algorithms](#7-optimization-algorithms)

---

## 1. TASK ORCHESTRATION ALGORITHMS

### 1.1 Task Decomposition Algorithm

```python
"""
TASK DECOMPOSITION ALGORITHM
Breaks complex tasks into hierarchical subtasks
Uses LLM-based analysis with validation
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

class TaskComplexity(Enum):
    """Task complexity levels"""
    TRIVIAL = 1      # Single step, <1min
    SIMPLE = 2       # 2-3 steps, <5min
    MODERATE = 3     # 4-10 steps, <30min
    COMPLEX = 4      # 11-50 steps, <2hr
    VERY_COMPLEX = 5 # 50+ steps, >2hr


@dataclass
class Task:
    """Task representation"""
    task_id: str
    description: str
    complexity: TaskComplexity
    required_capabilities: List[str]
    dependencies: List[str] = field(default_factory=list)
    subtasks: List['Task'] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    estimated_duration_seconds: Optional[int] = None
    parent_task_id: Optional[str] = None


class TaskDecomposer:
    """
    Decomposes tasks using multiple strategies
    """
    
    def __init__(self, ollama_client, capability_registry):
        self.ollama = ollama_client
        self.capabilities = capability_registry
        self.decomposition_history = []
        
        # Decomposition strategies
        self.strategies = {
            'llm_based': self.decompose_with_llm,
            'rule_based': self.decompose_with_rules,
            'hybrid': self.decompose_hybrid,
            'learned': self.decompose_with_learned_patterns
        }
    
    async def decompose(
        self,
        task: Task,
        strategy: str = 'hybrid',
        max_depth: int = 5,
        current_depth: int = 0
    ) -> List[Task]:
        """
        Main decomposition algorithm
        
        Algorithm:
        1. Analyze task complexity
        2. Determine if decomposition needed
        3. Select decomposition strategy
        4. Generate subtasks
        5. Validate subtasks
        6. Recursively decompose if needed
        7. Build dependency graph
        8. Optimize task order
        
        Complexity: O(n * d) where n=tasks, d=depth
        """
        
        # Step 1: Analyze complexity
        complexity_analysis = await self.analyze_complexity(task)
        
        # Step 2: Check if decomposition needed
        if not self.should_decompose(task, complexity_analysis, current_depth, max_depth):
            return [task]  # Atomic task
        
        # Step 3: Select strategy
        decomposition_func = self.strategies.get(strategy, self.decompose_hybrid)
        
        # Step 4: Generate subtasks
        subtasks = await decomposition_func(task, complexity_analysis)
        
        # Step 5: Validate subtasks
        validated_subtasks = await self.validate_subtasks(task, subtasks)
        
        # Step 6: Recursive decomposition
        all_subtasks = []
        for subtask in validated_subtasks:
            if current_depth < max_depth:
                decomposed = await self.decompose(
                    subtask,
                    strategy,
                    max_depth,
                    current_depth + 1
                )
                all_subtasks.extend(decomposed)
            else:
                all_subtasks.append(subtask)
        
        # Step 7: Build dependency graph
        dependency_graph = self.build_dependency_graph(all_subtasks)
        
        # Step 8: Optimize execution order
        optimized_tasks = self.optimize_task_order(all_subtasks, dependency_graph)
        
        # Record decomposition
        self.decomposition_history.append({
            'parent_task': task,
            'subtasks': optimized_tasks,
            'strategy': strategy,
            'depth': current_depth
        })
        
        return optimized_tasks
    
    async def analyze_complexity(self, task: Task) -> Dict[str, Any]:
        """
        Analyze task complexity using multiple dimensions
        
        Dimensions:
        - Computational: Time/space requirements
        - Cognitive: Reasoning depth required
        - Dependencies: Number and type of dependencies
        - Uncertainty: Ambiguity in requirements
        - Novelty: Similarity to known tasks
        """
        
        # Use LLM for analysis
        analysis_prompt = f"""
        Analyze the complexity of this task across multiple dimensions:
        
        Task: {task.description}
        
        Provide analysis for:
        1. Computational complexity (time/space)
        2. Cognitive complexity (reasoning depth)
        3. Number of steps required
        4. Required capabilities
        5. Dependencies on other tasks
        6. Ambiguity level (0-1)
        7. Novelty score (0-1)
        8. Estimated duration
        
        Format as JSON.
        """
        
        response = await self.ollama.generate(
            model="llama3.2",
            prompt=analysis_prompt,
            options={'temperature': 0.2}
        )
        
        # Parse response
        analysis = self.parse_complexity_analysis(response)
        
        # Add computed metrics
        analysis['description_length'] = len(task.description)
        analysis['word_count'] = len(task.description.split())
        analysis['capability_count'] = len(task.required_capabilities)
        
        # Calculate overall complexity score
        analysis['complexity_score'] = self.calculate_complexity_score(analysis)
        
        return analysis
    
    def should_decompose(
        self,
        task: Task,
        analysis: Dict,
        current_depth: int,
        max_depth: int
    ) -> bool:
        """
        Determine if task should be decomposed
        
        Decision factors:
        1. Complexity score above threshold
        2. Multiple distinct steps identified
        3. Not at max depth
        4. Task is not already atomic
        5. Decomposition would provide value
        """
        
        # Check depth limit
        if current_depth >= max_depth:
            return False
        
        # Check if already atomic
        if task.complexity == TaskComplexity.TRIVIAL:
            return False
        
        # Check complexity score
        complexity_threshold = 0.6
        if analysis['complexity_score'] < complexity_threshold:
            return False
        
        # Check step count
        if analysis.get('step_count', 0) <= 1:
            return False
        
        # Check if decomposition would help
        estimated_improvement = self.estimate_decomposition_value(task, analysis)
        
        return estimated_improvement > 0.2  # 20% improvement threshold
    
    async def decompose_with_llm(
        self,
        task: Task,
        analysis: Dict
    ) -> List[Task]:
        """
        LLM-based task decomposition
        
        Uses structured prompting to generate subtasks
        """
        
        decomposition_prompt = f"""
        Decompose this task into clear, actionable subtasks:
        
        Task: {task.description}
        Complexity Analysis: {analysis}
        
        Generate subtasks following these rules:
        1. Each subtask should be a single, clear action
        2. Subtasks should be ordered logically
        3. Identify dependencies between subtasks
        4. Each subtask needs specific capabilities
        5. Aim for 3-7 subtasks (not too many or too few)
        
        Format each subtask as:
        {{
            "description": "Subtask description",
            "required_capabilities": ["capability1", "capability2"],
            "depends_on": ["subtask_id1", "subtask_id2"],
            "estimated_duration_seconds": 60
        }}
        
        Provide JSON array of subtasks.
        """
        
        response = await self.ollama.generate(
            model="qwen2.5-coder:32b",  # Good for structured output
            prompt=decomposition_prompt,
            options={'temperature': 0.3}
        )
        
        # Parse subtasks
        subtasks_data = self.parse_subtasks_json(response)
        
        # Create Task objects
        subtasks = []
        for i, subtask_data in enumerate(subtasks_data):
            subtask = Task(
                task_id=f"{task.task_id}_sub_{i}",
                description=subtask_data['description'],
                complexity=self.estimate_subtask_complexity(subtask_data),
                required_capabilities=subtask_data['required_capabilities'],
                dependencies=subtask_data.get('depends_on', []),
                estimated_duration_seconds=subtask_data.get('estimated_duration_seconds'),
                parent_task_id=task.task_id
            )
            subtasks.append(subtask)
        
        return subtasks
    
    async def decompose_with_rules(
        self,
        task: Task,
        analysis: Dict
    ) -> List[Task]:
        """
        Rule-based task decomposition
        
        Uses predefined patterns and heuristics
        """
        
        # Identify task type
        task_type = self.classify_task_type(task)
        
        # Apply type-specific decomposition rules
        if task_type == 'data_processing':
            return self.decompose_data_processing_task(task)
        elif task_type == 'analysis':
            return self.decompose_analysis_task(task)
        elif task_type == 'generation':
            return self.decompose_generation_task(task)
        elif task_type == 'transformation':
            return self.decompose_transformation_task(task)
        else:
            # Generic decomposition
            return self.decompose_generic_task(task)
    
    def decompose_data_processing_task(self, task: Task) -> List[Task]:
        """
        Decompose data processing tasks using standard pipeline
        
        Standard pipeline:
        1. Data validation
        2. Data preprocessing
        3. Core processing
        4. Post-processing
        5. Output validation
        """
        
        subtasks = [
            Task(
                task_id=f"{task.task_id}_validate_input",
                description=f"Validate input data for: {task.description}",
                complexity=TaskComplexity.SIMPLE,
                required_capabilities=['validation'],
                parent_task_id=task.task_id
            ),
            Task(
                task_id=f"{task.task_id}_preprocess",
                description=f"Preprocess data for: {task.description}",
                complexity=TaskComplexity.SIMPLE,
                required_capabilities=['data_processing'],
                dependencies=[f"{task.task_id}_validate_input"],
                parent_task_id=task.task_id
            ),
            Task(
                task_id=f"{task.task_id}_process",
                description=f"Execute core processing: {task.description}",
                complexity=TaskComplexity.MODERATE,
                required_capabilities=['computation'],
                dependencies=[f"{task.task_id}_preprocess"],
                parent_task_id=task.task_id
            ),
            Task(
                task_id=f"{task.task_id}_postprocess",
                description=f"Post-process results: {task.description}",
                complexity=TaskComplexity.SIMPLE,
                required_capabilities=['data_processing'],
                dependencies=[f"{task.task_id}_process"],
                parent_task_id=task.task_id
            ),
            Task(
                task_id=f"{task.task_id}_validate_output",
                description=f"Validate output for: {task.description}",
                complexity=TaskComplexity.SIMPLE,
                required_capabilities=['validation'],
                dependencies=[f"{task.task_id}_postprocess"],
                parent_task_id=task.task_id
            )
        ]
        
        return subtasks
    
    async def decompose_hybrid(
        self,
        task: Task,
        analysis: Dict
    ) -> List[Task]:
        """
        Hybrid decomposition using both LLM and rules
        
        Algorithm:
        1. Generate subtasks with LLM
        2. Generate subtasks with rules
        3. Merge and deduplicate
        4. Validate and refine
        5. Select best decomposition
        """
        
        # Generate both decompositions
        llm_subtasks = await self.decompose_with_llm(task, analysis)
        rule_subtasks = await self.decompose_with_rules(task, analysis)
        
        # Compare decompositions
        llm_score = await self.score_decomposition(llm_subtasks, task)
        rule_score = await self.score_decomposition(rule_subtasks, task)
        
        # Select better decomposition or merge
        if llm_score > rule_score * 1.2:  # LLM significantly better
            return llm_subtasks
        elif rule_score > llm_score * 1.2:  # Rules significantly better
            return rule_subtasks
        else:
            # Merge both
            return await self.merge_decompositions(llm_subtasks, rule_subtasks, task)
    
    async def score_decomposition(
        self,
        subtasks: List[Task],
        parent_task: Task
    ) -> float:
        """
        Score quality of decomposition
        
        Criteria:
        1. Completeness - covers all aspects of parent task
        2. Clarity - each subtask is clear and actionable
        3. Granularity - appropriate level of detail
        4. Dependencies - properly identified
        5. Feasibility - each subtask is achievable
        """
        
        scores = {
            'completeness': await self.score_completeness(subtasks, parent_task),
            'clarity': self.score_clarity(subtasks),
            'granularity': self.score_granularity(subtasks),
            'dependencies': self.score_dependencies(subtasks),
            'feasibility': await self.score_feasibility(subtasks)
        }
        
        # Weighted average
        weights = {
            'completeness': 0.3,
            'clarity': 0.2,
            'granularity': 0.2,
            'dependencies': 0.15,
            'feasibility': 0.15
        }
        
        total_score = sum(
            scores[criterion] * weights[criterion]
            for criterion in scores
        )
        
        return total_score
    
    def build_dependency_graph(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """
        Build directed acyclic graph of task dependencies
        
        Returns: adjacency list representation
        Graph properties:
        - Nodes: task IDs
        - Edges: dependency relationships
        - Acyclic: no circular dependencies
        """
        
        graph = {task.task_id: [] for task in tasks}
        
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in graph:
                    graph[dep_id].append(task.task_id)
        
        # Validate DAG
        if self.has_cycle(graph):
            raise ValueError("Circular dependency detected in task graph")
        
        return graph
    
    def has_cycle(self, graph: Dict[str, List[str]]) -> bool:
        """
        Detect cycles in directed graph using DFS
        
        Algorithm: Three-color DFS
        - White (0): unvisited
        - Gray (1): visiting (in current path)
        - Black (2): visited (completed)
        
        Complexity: O(V + E)
        """
        
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {node: WHITE for node in graph}
        
        def has_cycle_dfs(node):
            if colors[node] == GRAY:
                return True  # Back edge found = cycle
            
            if colors[node] == BLACK:
                return False  # Already processed
            
            colors[node] = GRAY  # Mark as visiting
            
            for neighbor in graph.get(node, []):
                if has_cycle_dfs(neighbor):
                    return True
            
            colors[node] = BLACK  # Mark as completed
            return False
        
        # Check each node
        for node in graph:
            if colors[node] == WHITE:
                if has_cycle_dfs(node):
                    return True
        
        return False
    
    def optimize_task_order(
        self,
        tasks: List[Task],
        dependency_graph: Dict[str, List[str]]
    ) -> List[Task]:
        """
        Optimize task execution order using topological sort
        
        Algorithm: Kahn's algorithm
        1. Calculate in-degrees
        2. Start with zero in-degree nodes
        3. Process and remove edges
        4. Repeat until all processed
        
        Complexity: O(V + E)
        """
        
        # Calculate in-degrees
        in_degree = {task.task_id: 0 for task in tasks}
        for task_id in dependency_graph:
            for dependent in dependency_graph[task_id]:
                in_degree[dependent] += 1
        
        # Find zero in-degree tasks
        queue = [task_id for task_id in in_degree if in_degree[task_id] == 0]
        sorted_task_ids = []
        
        while queue:
            # Process task with no dependencies
            current_id = queue.pop(0)
            sorted_task_ids.append(current_id)
            
            # Update dependents
            for dependent_id in dependency_graph.get(current_id, []):
                in_degree[dependent_id] -= 1
                
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # Create ordered task list
        task_map = {task.task_id: task for task in tasks}
        ordered_tasks = [task_map[task_id] for task_id in sorted_task_ids]
        
        return ordered_tasks


### 1.2 Task Graph Representation

```python
"""
TASK GRAPH DATA STRUCTURE
Efficient representation of task dependencies and execution order
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import networkx as nx

class TaskGraph:
    """
    Directed Acyclic Graph for task dependencies
    
    Properties:
    - Vertices: Tasks
    - Edges: Dependencies (A -> B means B depends on A)
    - Acyclic: No circular dependencies
    - Weighted: Each edge has execution cost
    """
    
    def __init__(self):
        # Adjacency list: task_id -> list of dependent task_ids
        self.graph: Dict[str, List[str]] = defaultdict(list)
        
        # Reverse adjacency list: task_id -> list of prerequisite task_ids
        self.reverse_graph: Dict[str, List[str]] = defaultdict(list)
        
        # Task metadata
        self.tasks: Dict[str, Task] = {}
        
        # Edge weights (execution costs)
        self.weights: Dict[Tuple[str, str], float] = {}
        
        # Critical path cache
        self._critical_path_cache: Optional[List[str]] = None
    
    def add_task(self, task: Task):
        """Add task to graph"""
        self.tasks[task.task_id] = task
        
        if task.task_id not in self.graph:
            self.graph[task.task_id] = []
            self.reverse_graph[task.task_id] = []
        
        # Invalidate cache
        self._critical_path_cache = None
    
    def add_dependency(self, from_task_id: str, to_task_id: str, weight: float = 1.0):
        """
        Add dependency edge: to_task depends on from_task
        
        Args:
            from_task_id: Prerequisite task
            to_task_id: Dependent task
            weight: Cost/duration of from_task
        """
        self.graph[from_task_id].append(to_task_id)
        self.reverse_graph[to_task_id].append(from_task_id)
        self.weights[(from_task_id, to_task_id)] = weight
        
        # Invalidate cache
        self._critical_path_cache = None
    
    def get_execution_order(self) -> List[List[str]]:
        """
        Get tasks grouped by execution level (parallel groups)
        
        Returns:
            List of levels, where each level contains task IDs
            that can execute in parallel
        
        Algorithm: Level-order topological sort
        Complexity: O(V + E)
        """
        
        # Calculate in-degrees
        in_degree = {task_id: 0 for task_id in self.tasks}
        for task_id in self.graph:
            for dependent in self.graph[task_id]:
                in_degree[dependent] += 1
        
        # Start with zero in-degree tasks
        current_level = [t for t in in_degree if in_degree[t] == 0]
        levels = []
        
        while current_level:
            levels.append(current_level[:])
            next_level = []
            
            for task_id in current_level:
                # Process dependents
                for dependent_id in self.graph[task_id]:
                    in_degree[dependent_id] -= 1
                    
                    if in_degree[dependent_id] == 0:
                        next_level.append(dependent_id)
            
            current_level = next_level
        
        return levels
    
    def get_critical_path(self) -> Tuple[List[str], float]:
        """
        Find critical path (longest path) in task graph
        
        Critical path determines minimum completion time
        
        Algorithm: Dynamic programming on DAG
        Complexity: O(V + E)
        """
        
        if self._critical_path_cache:
            return self._critical_path_cache
        
        # Get topological order
        topo_order = self.topological_sort()
        
        # Initialize distances
        dist = {task_id: 0.0 for task_id in self.tasks}
        parent = {task_id: None for task_id in self.tasks}
        
        # Process in topological order
        for task_id in topo_order:
            # Update distances to all dependents
            for dependent_id in self.graph[task_id]:
                edge_weight = self.weights.get((task_id, dependent_id), 1.0)
                new_dist = dist[task_id] + edge_weight
                
                if new_dist > dist[dependent_id]:
                    dist[dependent_id] = new_dist
                    parent[dependent_id] = task_id
        
        # Find task with maximum distance (end of critical path)
        end_task = max(dist, key=dist.get)
        total_time = dist[end_task]
        
        # Reconstruct critical path
        path = []
        current = end_task
        while current is not None:
            path.append(current)
            current = parent[current]
        
        path.reverse()
        
        self._critical_path_cache = (path, total_time)
        return path, total_time
    
    def topological_sort(self) -> List[str]:
        """
        Topological sort using DFS
        
        Complexity: O(V + E)
        """
        
        visited = set()
        stack = []
        
        def dfs(task_id):
            visited.add(task_id)
            
            for dependent in self.graph[task_id]:
                if dependent not in visited:
                    dfs(dependent)
            
            stack.append(task_id)
        
        # Visit all nodes
        for task_id in self.tasks:
            if task_id not in visited:
                dfs(task_id)
        
        return stack[::-1]
    
    def get_parallel_tasks(self) -> Dict[int, List[str]]:
        """
        Get tasks that can execute in parallel at each level
        
        Returns:
            Dictionary: level -> list of parallel task IDs
        """
        
        levels = self.get_execution_order()
        return {i: level for i, level in enumerate(levels)}
    
    def estimate_completion_time(self, agent_speeds: Dict[str, float]) -> float:
        """
        Estimate total completion time given agent speeds
        
        Args:
            agent_speeds: task_id -> execution time in seconds
        
        Returns:
            Total estimated time considering parallelism
        """
        
        levels = self.get_execution_order()
        total_time = 0.0
        
        for level in levels:
            # For parallel tasks, time is max of all in level
            level_time = max(
                agent_speeds.get(task_id, 1.0)
                for task_id in level
            )
            total_time += level_time
        
        return total_time
    
    def to_networkx(self) -> nx.DiGraph:
        """
        Convert to NetworkX graph for visualization/analysis
        """
        G = nx.DiGraph()
        
        # Add nodes
        for task_id, task in self.tasks.items():
            G.add_node(task_id, task=task)
        
        # Add edges
        for from_id in self.graph:
            for to_id in self.graph[from_id]:
                weight = self.weights.get((from_id, to_id), 1.0)
                G.add_edge(from_id, to_id, weight=weight)
        
        return G
```

This is Part 1 of the ultra-detailed algorithms specification. Should I continue with agent selection algorithms, learning algorithms, and more complete implementations?


