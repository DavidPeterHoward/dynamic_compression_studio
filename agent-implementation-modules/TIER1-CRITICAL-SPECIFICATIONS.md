# TIER 1: CRITICAL COMPONENT SPECIFICATIONS
## Ultra-Detailed Specifications for Core System Components

**Document Purpose:** Maximum detail for critical system components  
**Date:** 2025-10-30  
**Coverage:** Complete specifications with all parameters, schemas, validation  
**Detail Level:** ULTRA (400-600 lines per attribute)  

---

## 📋 TABLE OF CONTENTS

1. [TaskNode Complete Specification](#tasknode-complete-specification)
2. [Agent Complete Specification](#agent-complete-specification)
3. [MetaImprovementMetric Specification](#metaimprovementmetric-specification)
4. [Database Schema Complete](#database-schema-complete)
5. [API Endpoints Complete](#api-endpoints-complete)

---

## TASKNODE COMPLETE SPECIFICATION

### Overview

**Purpose:** Fundamental unit of work in the system  
**Usage:** Every task, subtask, and work item  
**Lifecycle:** Created → Decomposed? → Executed → Completed  
**Storage:** PostgreSQL tasks table  

### Class Definition

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
import time

@dataclass
class TaskNode:
    """
    Represents a task in the decomposition tree.
    
    TaskNode is the fundamental unit of work in the Meta-Recursive
    Multi-Agent Orchestration System. Every piece of work, whether a
    top-level task or a subtask, is represented as a TaskNode.
    
    Attributes:
        id: Unique identifier (UUID format)
        type: Task category for agent routing
        description: Human-readable task description
        complexity: Computational complexity (0.0-1.0)
        estimated_time: Expected execution time (seconds)
        dependencies: IDs of prerequisite tasks
        resources_required: Required computational resources
        parallelizable: Can execute in parallel with siblings
        priority: Execution priority (1=highest, 10=lowest)
        metadata: Additional task-specific data
    
    Example:
        >>> task = TaskNode(
        ...     id="task_12345678",
        ...     type="data_processing",
        ...     description="Process 10k customer records",
        ...     complexity=0.6,
        ...     estimated_time=15.0,
        ...     dependencies=[],
        ...     resources_required={"cpu": 2, "memory_mb": 4096},
        ...     parallelizable=True,
        ...     priority=3
        ... )
    """
    
    # Core Identity
    id: str
    type: str
    description: str
    
    # Computational Characteristics
    complexity: float
    estimated_time: float
    
    # Execution Control
    dependencies: List[str] = field(default_factory=list)
    resources_required: Dict[str, Any] = field(default_factory=dict)
    parallelizable: bool = True
    priority: int = 5
    
    # Extensibility
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

### Attribute: dependencies

**Type:** `List[str]`  
**Required:** No  
**Default:** `[]` (empty list)  
**Nullable:** No (use empty list instead of None)  

**Description:**
List of task IDs that must complete before this task can start.
Defines the execution order in the task dependency graph.

**Format:**
```python
dependencies: List[str] = [
    "task_001",  # Must complete first
    "task_002",  # Must complete first
    "task_003"   # Must complete first
]

# All dependencies must complete before this task starts
# Order within list doesn't matter (parallel completion)
```

**Constraints:**

**Length Constraints:**
```python
MIN_DEPENDENCIES = 0
MAX_DEPENDENCIES = 100  # Prevent circular dependency issues

def validate_dependency_count(dependencies: List[str]) -> bool:
    """Validate dependency count."""
    if len(dependencies) > MAX_DEPENDENCIES:
        raise ValueError(
            f"Too many dependencies: {len(dependencies)} (max {MAX_DEPENDENCIES})"
        )
    return True
```

**Format Constraints:**
```python
def validate_dependency_format(dependencies: List[str]) -> bool:
    """Validate each dependency ID format."""
    for dep_id in dependencies:
        if not isinstance(dep_id, str):
            raise TypeError(f"Dependency ID must be string, got {type(dep_id)}")
        
        if not dep_id:
            raise ValueError("Dependency ID cannot be empty string")
        
        if len(dep_id) < 8 or len(dep_id) > 128:
            raise ValueError(
                f"Dependency ID length must be 8-128 chars: {dep_id}"
            )
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', dep_id):
            raise ValueError(
                f"Dependency ID contains invalid characters: {dep_id}"
            )
    
    return True
```

**Circular Dependency Prevention:**
```python
def check_circular_dependencies(
    task_id: str,
    dependencies: List[str],
    all_tasks: Dict[str, TaskNode]
) -> bool:
    """
    Check for circular dependencies using DFS.
    
    Args:
        task_id: Current task ID
        dependencies: Dependencies to check
        all_tasks: All tasks in system
        
    Returns:
        True if no circular dependencies
        
    Raises:
        ValueError: If circular dependency detected
        
    Algorithm:
        Uses depth-first search to detect cycles in dependency graph.
        Time Complexity: O(V + E) where V = tasks, E = dependencies
    """
    visited = set()
    rec_stack = set()
    
    def dfs(current_id: str) -> bool:
        """DFS to detect cycle."""
        if current_id in rec_stack:
            return False  # Cycle detected
        
        if current_id in visited:
            return True  # Already processed
        
        visited.add(current_id)
        rec_stack.add(current_id)
        
        # Check dependencies of current task
        if current_id in all_tasks:
            for dep_id in all_tasks[current_id].dependencies:
                if not dfs(dep_id):
                    return False
        
        rec_stack.remove(current_id)
        return True
    
    # Add new task temporarily
    temp_task = TaskNode(
        id=task_id,
        type="temp",
        description="temp",
        complexity=0.5,
        estimated_time=1.0,
        dependencies=dependencies
    )
    all_tasks[task_id] = temp_task
    
    # Check for cycles
    result = dfs(task_id)
    
    # Remove temp task
    del all_tasks[task_id]
    
    if not result:
        cycle_path = find_cycle_path(task_id, all_tasks)
        raise ValueError(
            f"Circular dependency detected: {' -> '.join(cycle_path)}"
        )
    
    return True

def find_cycle_path(
    start_id: str,
    all_tasks: Dict[str, TaskNode]
) -> List[str]:
    """Find and return the cycle path for error reporting."""
    path = []
    visited = set()
    
    def dfs_path(current_id: str) -> bool:
        if current_id in visited:
            # Found cycle, return path from here
            cycle_start = path.index(current_id)
            return path[cycle_start:] + [current_id]
        
        visited.add(current_id)
        path.append(current_id)
        
        if current_id in all_tasks:
            for dep_id in all_tasks[current_id].dependencies:
                result = dfs_path(dep_id)
                if result:
                    return result
        
        path.pop()
        return None
    
    return dfs_path(start_id) or []
```

**Existence Validation:**
```python
def validate_dependencies_exist(
    dependencies: List[str],
    available_tasks: Set[str]
) -> Tuple[bool, List[str]]:
    """
    Validate all dependency tasks exist.
    
    Args:
        dependencies: List of dependency IDs
        available_tasks: Set of valid task IDs
        
    Returns:
        Tuple of (all_exist, missing_ids)
    """
    missing = []
    
    for dep_id in dependencies:
        if dep_id not in available_tasks:
            missing.append(dep_id)
    
    if missing:
        return False, missing
    
    return True, []

# Usage in task creation
def create_task(task: TaskNode, existing_tasks: Dict[str, TaskNode]):
    """Create task with dependency validation."""
    available_ids = set(existing_tasks.keys())
    
    exists, missing = validate_dependencies_exist(
        task.dependencies,
        available_ids
    )
    
    if not exists:
        raise ValueError(
            f"Task {task.id} has missing dependencies: {missing}"
        )
    
    # Also check circular dependencies
    check_circular_dependencies(task.id, task.dependencies, existing_tasks)
    
    # Store task
    existing_tasks[task.id] = task
```

**Execution Order Calculation:**
```python
def calculate_execution_order(
    tasks: Dict[str, TaskNode]
) -> List[List[str]]:
    """
    Calculate execution order respecting dependencies.
    
    Returns list of lists where each inner list contains task IDs
    that can execute in parallel (no dependencies between them).
    
    Args:
        tasks: Dictionary of all tasks
        
    Returns:
        List of execution levels (parallel groups)
        
    Algorithm:
        Topological sort with level identification.
        
    Example:
        Input tasks:
            A: no dependencies
            B: depends on A
            C: depends on A
            D: depends on B, C
        
        Output:
            [[A], [B, C], [D]]
            
        Meaning:
            - Level 0: Execute A
            - Level 1: Execute B and C in parallel
            - Level 2: Execute D
    
    Complexity: O(V + E) where V = tasks, E = dependencies
    """
    import networkx as nx
    
    # Build dependency graph
    graph = nx.DiGraph()
    
    for task_id, task in tasks.items():
        graph.add_node(task_id)
        for dep_id in task.dependencies:
            graph.add_edge(dep_id, task_id)  # dep must complete before task
    
    # Check for cycles
    if not nx.is_directed_acyclic_graph(graph):
        cycles = list(nx.simple_cycles(graph))
        raise ValueError(f"Circular dependencies detected: {cycles}")
    
    # Calculate levels
    levels = []
    remaining_nodes = set(graph.nodes())
    
    while remaining_nodes:
        # Find nodes with no remaining dependencies
        current_level = []
        for node in remaining_nodes:
            predecessors = set(graph.predecessors(node))
            if not predecessors.intersection(remaining_nodes):
                current_level.append(node)
        
        if not current_level:
            raise ValueError("Unresolvable dependencies")
        
        levels.append(sorted(current_level))  # Sort for deterministic order
        remaining_nodes -= set(current_level)
    
    return levels
```

**Usage Examples:**

**Example 1: Simple Linear Dependencies**
```python
# Task chain: A → B → C
task_a = TaskNode(
    id="task_a",
    type="data_ingestion",
    description="Load data from source",
    complexity=0.3,
    estimated_time=5.0,
    dependencies=[]  # No dependencies, can start immediately
)

task_b = TaskNode(
    id="task_b",
    type="data_processing",
    description="Clean and transform data",
    complexity=0.5,
    estimated_time=10.0,
    dependencies=["task_a"]  # Must wait for task_a
)

task_c = TaskNode(
    id="task_c",
    type="data_export",
    description="Export processed data",
    complexity=0.2,
    estimated_time=3.0,
    dependencies=["task_b"]  # Must wait for task_b
)

# Execution order: [[task_a], [task_b], [task_c]]
```

**Example 2: Parallel with Join**
```python
# Diamond pattern:
#     A
#    / \
#   B   C
#    \ /
#     D

task_a = TaskNode(
    id="task_a",
    type="data_fetch",
    description="Fetch raw data",
    complexity=0.3,
    estimated_time=5.0,
    dependencies=[]
)

task_b = TaskNode(
    id="task_b",
    type="analysis",
    description="Statistical analysis",
    complexity=0.6,
    estimated_time=15.0,
    dependencies=["task_a"]
)

task_c = TaskNode(
    id="task_c",
    type="analysis",
    description="ML analysis",
    complexity=0.7,
    estimated_time=20.0,
    dependencies=["task_a"]
)

task_d = TaskNode(
    id="task_d",
    type="reporting",
    description="Generate combined report",
    complexity=0.4,
    estimated_time=8.0,
    dependencies=["task_b", "task_c"]  # Waits for both B and C
)

# Execution order: [[task_a], [task_b, task_c], [task_d]]
# task_b and task_c execute in parallel after task_a
```

**Example 3: Complex Multi-Level**
```python
# Complex graph:
#      A
#     / \
#    B   C
#   / \ / \
#  D   E   F
#   \ / \ /
#    G   H

tasks = {
    "A": TaskNode(id="A", dependencies=[], ...),
    "B": TaskNode(id="B", dependencies=["A"], ...),
    "C": TaskNode(id="C", dependencies=["A"], ...),
    "D": TaskNode(id="D", dependencies=["B"], ...),
    "E": TaskNode(id="E", dependencies=["B", "C"], ...),
    "F": TaskNode(id="F", dependencies=["C"], ...),
    "G": TaskNode(id="G", dependencies=["D", "E"], ...),
    "H": TaskNode(id="H", dependencies=["E", "F"], ...)
}

# Execution order:
# Level 0: [A]
# Level 1: [B, C]
# Level 2: [D, E, F]
# Level 3: [G, H]
```

**Database Storage:**

**PostgreSQL Schema:**
```sql
-- Dependencies stored in separate table for flexibility
CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id VARCHAR(128) NOT NULL,
    dependency_id VARCHAR(128) NOT NULL,
    
    -- Order doesn't matter but we track when added
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary key prevents duplicates
    PRIMARY KEY (task_id, dependency_id),
    
    -- Foreign keys ensure referential integrity
    CONSTRAINT fk_task FOREIGN KEY (task_id) 
        REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_dependency FOREIGN KEY (dependency_id) 
        REFERENCES tasks(id) ON DELETE RESTRICT,
    
    -- Prevent self-dependency
    CONSTRAINT chk_no_self_dependency CHECK (task_id != dependency_id)
);

-- Index for fast dependency lookup
CREATE INDEX idx_task_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_task_deps_dependency ON task_dependencies(dependency_id);

-- Index for reverse lookup (what depends on this task)
CREATE INDEX idx_task_deps_dependent_tasks ON task_dependencies(dependency_id);
```

**Query Patterns:**
```sql
-- Get all dependencies for a task
SELECT dependency_id 
FROM task_dependencies 
WHERE task_id = $1;

-- Get all tasks that depend on this task (reverse)
SELECT task_id 
FROM task_dependencies 
WHERE dependency_id = $1;

-- Check if task has any dependencies
SELECT EXISTS(
    SELECT 1 FROM task_dependencies WHERE task_id = $1
);

-- Get tasks ready to execute (no remaining dependencies)
SELECT DISTINCT t.id
FROM tasks t
LEFT JOIN task_dependencies td ON t.id = td.task_id
LEFT JOIN tasks dt ON td.dependency_id = dt.id
WHERE t.status = 'pending'
  AND (dt.id IS NULL OR dt.status = 'completed')
GROUP BY t.id
HAVING COUNT(dt.id) = 0 OR 
       COUNT(CASE WHEN dt.status = 'completed' THEN 1 END) = COUNT(dt.id);
```

**ORM Representation (SQLAlchemy):**
```python
from sqlalchemy import Table, Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Association table for many-to-many
task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('task_id', String(128), ForeignKey('tasks.id'), primary_key=True),
    Column('dependency_id', String(128), ForeignKey('tasks.id'), primary_key=True),
    Column('added_at', DateTime, default=datetime.utcnow)
)

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String(128), primary_key=True)
    # ... other columns ...
    
    # Dependencies (tasks this task depends on)
    dependencies = relationship(
        'Task',
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.dependency_id,
        backref='dependent_tasks',
        foreign_keys=[task_dependencies.c.task_id, task_dependencies.c.dependency_id]
    )
    
    def add_dependency(self, dependency: 'Task'):
        """Add a dependency with validation."""
        if dependency.id == self.id:
            raise ValueError("Cannot depend on self")
        
        if dependency in self.dependencies:
            raise ValueError(f"Dependency {dependency.id} already exists")
        
        # Check for circular dependency
        if self._would_create_cycle(dependency):
            raise ValueError(f"Would create circular dependency with {dependency.id}")
        
        self.dependencies.append(dependency)
    
    def _would_create_cycle(self, new_dependency: 'Task') -> bool:
        """Check if adding dependency would create cycle."""
        visited = set()
        
        def dfs(task: 'Task') -> bool:
            if task.id == self.id:
                return True
            if task.id in visited:
                return False
            
            visited.add(task.id)
            
            for dep in task.dependencies:
                if dfs(dep):
                    return True
            
            return False
        
        return dfs(new_dependency)
    
    def can_start(self) -> bool:
        """Check if all dependencies are completed."""
        return all(dep.status == 'completed' for dep in self.dependencies)
    
    def get_dependency_status(self) -> Dict[str, str]:
        """Get status of all dependencies."""
        return {
            dep.id: dep.status
            for dep in self.dependencies
        }
```

**Monitoring & Metrics:**

```python
class DependencyMetrics:
    """Track dependency-related metrics."""
    
    def __init__(self):
        self.dependency_depths: List[int] = []
        self.dependency_counts: List[int] = []
        self.blocked_durations: List[float] = []
    
    def record_task_dependencies(self, task: TaskNode, all_tasks: Dict[str, TaskNode]):
        """Record metrics for task's dependencies."""
        # Dependency count
        dep_count = len(task.dependencies)
        self.dependency_counts.append(dep_count)
        
        # Dependency depth (longest chain to root)
        depth = self._calculate_dependency_depth(task, all_tasks)
        self.dependency_depths.append(depth)
    
    def _calculate_dependency_depth(
        self, 
        task: TaskNode, 
        all_tasks: Dict[str, TaskNode]
    ) -> int:
        """Calculate max depth of dependency chain."""
        if not task.dependencies:
            return 0
        
        max_depth = 0
        for dep_id in task.dependencies:
            if dep_id in all_tasks:
                dep_task = all_tasks[dep_id]
                depth = 1 + self._calculate_dependency_depth(dep_task, all_tasks)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def record_blocked_duration(self, duration_seconds: float):
        """Record how long task was blocked waiting for dependencies."""
        self.blocked_durations.append(duration_seconds)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated dependency metrics."""
        if not self.dependency_counts:
            return {"status": "no_data"}
        
        return {
            "avg_dependency_count": np.mean(self.dependency_counts),
            "max_dependency_count": np.max(self.dependency_counts),
            "avg_dependency_depth": np.mean(self.dependency_depths),
            "max_dependency_depth": np.max(self.dependency_depths),
            "avg_blocked_duration": np.mean(self.blocked_durations) if self.blocked_durations else 0,
            "total_tasks_with_deps": len([c for c in self.dependency_counts if c > 0]),
            "total_independent_tasks": len([c for c in self.dependency_counts if c == 0])
        }
```

**Performance Considerations:**

**Optimization 1: Dependency Resolution Cache**
```python
class DependencyCache:
    """Cache dependency resolution results."""
    
    def __init__(self):
        self.cache: Dict[str, List[List[str]]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_execution_order(
        self, 
        tasks: Dict[str, TaskNode]
    ) -> List[List[str]]:
        """Get execution order with caching."""
        # Create cache key from task graph structure
        cache_key = self._create_cache_key(tasks)
        
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        # Calculate execution order
        order = calculate_execution_order(tasks)
        
        # Cache result
        self.cache[cache_key] = order
        
        # Limit cache size
        if len(self.cache) > 1000:
            self._evict_oldest()
        
        return order
    
    def _create_cache_key(self, tasks: Dict[str, TaskNode]) -> str:
        """Create deterministic cache key from task graph."""
        # Sort tasks by ID for consistency
        sorted_tasks = sorted(tasks.items())
        
        # Create key from dependencies
        key_parts = []
        for task_id, task in sorted_tasks:
            deps = sorted(task.dependencies)
            key_parts.append(f"{task_id}:{','.join(deps)}")
        
        return '|'.join(key_parts)
    
    def _evict_oldest(self):
        """Remove oldest 20% of cache entries."""
        remove_count = len(self.cache) // 5
        keys_to_remove = list(self.cache.keys())[:remove_count]
        for key in keys_to_remove:
            del self.cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_pct": hit_rate
        }
```

**Optimization 2: Incremental Update**
```python
class IncrementalDependencyResolver:
    """Incrementally update execution order when tasks change."""
    
    def __init__(self):
        self.current_order: List[List[str]] = []
        self.task_levels: Dict[str, int] = {}
    
    def add_task(self, task: TaskNode, all_tasks: Dict[str, TaskNode]):
        """Add new task and update execution order incrementally."""
        # Calculate level for new task
        if not task.dependencies:
            level = 0
        else:
            # Level = max(dependency levels) + 1
            max_dep_level = max(
                self.task_levels.get(dep_id, 0)
                for dep_id in task.dependencies
            )
            level = max_dep_level + 1
        
        # Update task levels
        self.task_levels[task.id] = level
        
        # Insert task into appropriate level
        while len(self.current_order) <= level:
            self.current_order.append([])
        
        self.current_order[level].append(task.id)
        self.current_order[level].sort()  # Keep sorted
    
    def remove_task(self, task_id: str):
        """Remove task and update execution order."""
        if task_id not in self.task_levels:
            return
        
        level = self.task_levels[task_id]
        
        # Remove from level
        if level < len(self.current_order):
            if task_id in self.current_order[level]:
                self.current_order[level].remove(task_id)
        
        # Remove from task levels
        del self.task_levels[task_id]
    
    def get_execution_order(self) -> List[List[str]]:
        """Get current execution order."""
        # Filter out empty levels
        return [level for level in self.current_order if level]
```

---

**[Continuing with remaining TaskNode attributes and other components in the document...]**

Due to the massive scope, I'm creating this as the first tier. Would you like me to:

1. Continue with remaining TaskNode attributes (resources_required, parallelizable, priority, metadata)?
2. Move to Agent complete specification?
3. Move to database schemas?
4. Continue expanding all sections in parallel?

This document will ultimately be 15,000+ lines for Tier 1 critical components alone.

