# AGENT FRAMEWORK - DETAILED NEXT STEPS
## Comprehensive Implementation Roadmap Based on Documentation Review

**Date:** 2025-11-03  
**Current Status:** Week 1 Complete ✅ | Week 2-3 In Progress  
**Completion:** ~45% Overall

---

## 📋 EXECUTIVE SUMMARY

### Completed ✅
- **Week 1 Foundation:** BaseAgent, AgentRegistry, Specialist Agents (100%)

### Current Priority 🔴
- **Week 2-3 Orchestration:** TaskDecomposer, Orchestrator completion, Meta-Learner completion

### Critical Path Items
1. **TaskDecomposer** (0% → 100%) - **BLOCKING**
2. **Orchestrator Topological Sort** (50% → 100%) - **BLOCKING**
3. **Meta-Learner Continuous Loop** (45% → 100%) - **CRITICAL INNOVATION**

---

## 🎯 PHASE 2: ORCHESTRATION LAYER (Week 2-3)

### STEP 2.1: Implement TaskDecomposer ❌→✅ (CRITICAL - BLOCKING)

**Status:** NOT IMPLEMENTED (0%)  
**Priority:** 🔴 **CRITICAL - BLOCKS ORCHESTRATOR**  
**Estimated Time:** 2-3 days  
**Dependencies:** None (uses existing BaseAgent)

#### Detailed Requirements

**File to Create:** `backend/app/core/task_decomposer.py`

**Core Components Needed:**

##### 1. Subtask Data Structure
```python
@dataclass
class Subtask:
    """Represents a decomposed subtask."""
    id: str  # Unique identifier (e.g., "analyze_content_001")
    type: str  # Task type (e.g., "text_analysis")
    input: Dict[str, Any]  # Input data with {{reference}} placeholders
    requirements: Dict[str, Any]  # Agent requirements (capabilities, status)
    dependencies: Set[str]  # IDs of prerequisite subtasks
    priority: int = 5  # Priority level (1-10, default 5)
    estimated_duration: float = 0.0  # Estimated execution time in seconds
```

##### 2. TaskDecomposer Class Structure

**Required Methods:**
1. `__init__()` - Initialize with decomposition strategies
2. `decompose()` - Main decomposition method
3. `_subtask_to_dict()` - Convert Subtask to dictionary
4. `_group_by_generation()` - Topological sort to group by dependency level
5. `_build_dependency_graph()` - Construct dependency DAG
6. `_analyze_task_complexity()` - Determine if decomposition needed
7. `_decompose_compression_analysis()` - Strategy for compression tasks
8. `_decompose_code_review()` - Strategy for code review tasks
9. `_decompose_data_pipeline()` - Strategy for data pipeline tasks
10. `_decompose_multi_step()` - Generic multi-step decomposition
11. `get_parallel_tasks()` - Extract parallel execution groups from graph

**Decomposition Strategies Required:**
- `compression_analysis` - Content analysis → Algorithm selection → Compression
- `code_review` - Code analysis → Pattern checking → Review generation
- `data_pipeline` - Extract → Transform → Load → Validate
- `multi_step` - Generic sequential decomposition
- `research_synthesis` - Research → Analysis → Synthesis

**Algorithm Requirements:**
- **Topological Sort:** Kahn's algorithm (O(V + E))
- **Dependency Graph:** Directed Acyclic Graph (DAG)
- **Parallel Group Detection:** Level-order traversal
- **Cycle Detection:** Three-color DFS algorithm

#### Implementation Checklist

- [ ] **2.1.1** Create `Subtask` dataclass with all fields
- [ ] **2.1.2** Create `TaskDecomposer` class with `__init__`
- [ ] **2.1.3** Implement `decompose()` method (main entry point)
- [ ] **2.1.4** Implement `_subtask_to_dict()` converter
- [ ] **2.1.5** Implement `_build_dependency_graph()` (DAG construction)
- [ ] **2.1.6** Implement `_group_by_generation()` (Kahn's topological sort)
- [ ] **2.1.7** Implement `get_parallel_tasks()` (parallel execution groups)
- [ ] **2.1.8** Implement `_decompose_compression_analysis()` strategy
- [ ] **2.1.9** Implement `_decompose_code_review()` strategy
- [ ] **2.1.10** Implement `_decompose_data_pipeline()` strategy
- [ ] **2.1.11** Implement `_decompose_multi_step()` generic strategy
- [ ] **2.1.12** Add cycle detection algorithm
- [ ] **2.1.13** Add complexity analysis method
- [ ] **2.1.14** Add unit tests for decomposition
- [ ] **2.1.15** Add integration tests with Orchestrator

#### Detailed Implementation Steps

**Step 2.1.1: Create File Structure**
```python
# backend/app/core/task_decomposer.py
from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque, defaultdict
import logging
import uuid

logger = logging.getLogger(__name__)
```

**Step 2.1.2: Implement Subtask Dataclass**
- All fields as specified
- Default values for optional fields
- Type hints complete

**Step 2.1.3: Implement Topological Sort (Kahn's Algorithm)**
```python
def _topological_sort(
    self,
    dependency_graph: Dict[str, Set[str]]
) -> List[List[str]]:
    """
    Kahn's algorithm for topological sort.
    
    Returns:
        List of generations (lists of task IDs that can run in parallel)
    """
    # Calculate in-degrees
    in_degree = defaultdict(int)
    all_nodes = set()
    
    # Collect all nodes
    for node in dependency_graph:
        all_nodes.add(node)
        for dep in dependency_graph[node]:
            all_nodes.add(dep)
            in_degree[dep] += 1
    
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
        
        # Find next generation
        for node in current_gen:
            # Check all nodes that depend on this one
            for other_node in all_nodes:
                if other_node in processed:
                    continue
                if node in dependency_graph.get(other_node, set()):
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0:
                        queue.append(other_node)
    
    # Handle any remaining nodes (cycles would cause issues)
    unprocessed = all_nodes - processed
    if unprocessed:
        logger.warning(f"Circular dependencies detected: {unprocessed}")
    
    return generations
```

**Step 2.1.4: Implement Dependency Graph Builder**
```python
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
```

**Step 2.1.5: Implement Compression Analysis Decomposition**
```python
async def _decompose_compression_analysis(
    self,
    task_input: Dict[str, Any]
) -> List[Subtask]:
    """
    Decompose compression analysis into:
    1. Content analysis (NLP) - Parallel
    2. Structure analysis (NLP) - Parallel
    3. Algorithm selection (depends on 1,2)
    4. Compression execution (depends on 3)
    """
    content = task_input.get("content", "")
    
    subtasks = [
        Subtask(
            id="analyze_content",
            type="text_analysis",
            input={"text": content},
            requirements={"required_capabilities": ["analysis"]},
            dependencies=set(),
            priority=8
        ),
        Subtask(
            id="analyze_structure",
            type="entity_extraction",
            input={"text": content},
            requirements={"required_capabilities": ["analysis"]},
            dependencies=set(),
            priority=8
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
            priority=9
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
            priority=10
        )
    ]
    
    return subtasks
```

#### Testing Requirements

**Unit Tests:**
- Test `decompose()` with simple task
- Test `decompose()` with complex task
- Test `_topological_sort()` with various graphs
- Test `_build_dependency_graph()` validation
- Test cycle detection
- Test parallel group extraction

**Integration Tests:**
- Test with OrchestratorAgent
- Test end-to-end task decomposition → execution
- Test dependency resolution

---

### STEP 2.2: Complete Orchestrator Agent ✅→✅ (50% → 100%)

**Status:** PARTIALLY IMPLEMENTED (50%)  
**Priority:** 🔴 **CRITICAL**  
**Estimated Time:** 1-2 days  
**Dependencies:** TaskDecomposer (Step 2.1)

**Current File:** `backend/app/agents/orchestrator/orchestrator_agent.py`

#### Missing Components Analysis

**Already Implemented ✅:**
- `bootstrap_and_validate()` - ✅ Complete
- `execute_task()` - ✅ Structure complete
- `decompose_task()` - ✅ Delegates to TaskDecomposer
- `coordinate_execution()` - ✅ Structure complete
- `_execute_subtask_with_retry()` - ✅ Complete
- `select_agent()` - ✅ Complete (uses registry)
- `_resolve_input_dependencies()` - ✅ Complete

**Missing/Incomplete ❌:**
1. **`_group_by_generation()`** - Currently placeholder, needs topological sort
2. **TaskDecomposer integration** - Needs to import and use TaskDecomposer
3. **`aggregate_results()`** - Needs enhancement
4. **Error handling** - Needs improvement
5. **`self_evaluate()`** - Needs implementation
6. **Agent registry integration** - Needs to use get_agent_registry()

#### Detailed Implementation Steps

##### 2.2.1: Fix Orchestrator Imports and Dependencies

**Required Changes:**
```python
# Add imports
from app.core.task_decomposer import TaskDecomposer
from app.core.agent_registry import get_agent_registry
from app.core.base_agent import AgentStatus
```

##### 2.2.2: Fix `_group_by_generation()` Method

**Current (Placeholder):**
```python
def _group_by_generation(...) -> List[List[Dict[str, Any]]]:
    return [subtasks]  # Placeholder
```

**Required Implementation:**
```python
def _group_by_generation(
    self,
    subtasks: List[Dict[str, Any]],
    dependency_graph: Dict[str, Set[str]]
) -> List[List[Dict[str, Any]]]:
    """
    Group subtasks into dependency generations using topological sort.
    
    Returns:
        List of generations, where each generation can execute in parallel
    """
    # Use TaskDecomposer's topological sort
    generations = self.task_decomposer._topological_sort(dependency_graph)
    
    # Convert generation IDs to full subtask dictionaries
    subtask_dict = {st["id"]: st for st in subtasks}
    result_generations = []
    
    for gen_ids in generations:
        generation = [
            subtask_dict[task_id]
            for task_id in gen_ids
            if task_id in subtask_dict
        ]
        if generation:
            result_generations.append(generation)
    
    return result_generations
```

##### 2.2.3: Enhance `aggregate_results()` Method

**Current:** Basic aggregation  
**Required:** Enhanced with error handling, partial results, metrics

```python
async def aggregate_results(
    self,
    results: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aggregate subtask results into final result.
    
    Enhanced with:
    - Partial success handling
    - Error aggregation
    - Performance metrics
    - Result merging strategies
    """
    successful = [r for r in results.values() if r.get("success")]
    failed = [r for r in results.values() if not r.get("success")]
    
    # Calculate metrics
    total_duration = sum(
        r.get("execution_time_seconds", 0)
        for r in successful
    )
    
    avg_duration = (
        total_duration / len(successful)
        if successful else 0
    )
    
    # Determine final status
    if len(failed) == 0:
        final_status = "completed"
    elif len(successful) > len(failed):
        final_status = "partial"
    else:
        final_status = "failed"
    
    # Aggregate results based on task type
    aggregated_result = self._merge_results(successful)
    
    return {
        "status": final_status,
        "total_subtasks": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": len(successful) / len(results) if results else 0,
        "total_duration_seconds": total_duration,
        "avg_duration_seconds": avg_duration,
        "results": results,
        "aggregated_result": aggregated_result,
        "errors": [r.get("error") for r in failed if r.get("error")]
    }

def _merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple results into single result."""
    # Strategy depends on result structure
    if not results:
        return {}
    
    # For now, return last result or combine intelligently
    if len(results) == 1:
        return results[0].get("result", {})
    
    # Merge multiple results
    merged = {}
    for result_dict in results:
        result_data = result_dict.get("result", {})
        if isinstance(result_data, dict):
            merged.update(result_data)
    
    return merged
```

##### 2.2.4: Fix Orchestrator Initialization

**Current:** Uses message bus pattern  
**Required:** Integrate with AgentRegistry

```python
def __init__(
    self,
    agent_registry=None,  # Make optional, use singleton if None
    agent_id: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
):
    super().__init__(
        agent_id=agent_id or "orchestrator_001",
        agent_type="orchestrator",
        config=config
    )
    
    # Use provided registry or get singleton
    self.agent_registry = agent_registry or get_agent_registry()
    
    # Initialize TaskDecomposer
    self.task_decomposer = TaskDecomposer()
    
    self.capabilities = [AgentCapability.ORCHESTRATION]
    
    # Configuration
    self.max_parallel_tasks = config.get("max_parallel_tasks", 10)
    self.task_timeout_seconds = config.get("task_timeout_seconds", 300)
    self.max_retries = config.get("max_retries", 3)
    
    # Task tracking
    self.active_tasks: Dict[str, Dict[str, Any]] = {}
    self.task_history: List[Dict[str, Any]] = []
```

##### 2.2.5: Implement `self_evaluate()` Method

```python
async def self_evaluate(self) -> Dict[str, Any]:
    """Evaluate orchestrator performance."""
    metrics = await self.report_metrics()
    
    success_rate = (
        self.success_count / self.task_count
        if self.task_count > 0
        else 0.0
    )
    
    strengths = []
    if success_rate > 0.95:
        strengths.append("High orchestration success rate")
    if len(self.agent_registry.get_all_agents()) > 0:
        strengths.append("Agent registry populated")
    if len(self.task_history) > 0:
        avg_subtasks = sum(
            t.get("subtask_count", 0) for t in self.task_history
        ) / len(self.task_history)
        if avg_subtasks > 1:
            strengths.append(f"Effective task decomposition (avg {avg_subtasks:.1f} subtasks)")
    
    weaknesses = []
    if success_rate < 0.7:
        weaknesses.append("Low orchestration success rate")
    if self.error_count > 10:
        weaknesses.append("High error count in orchestration")
    
    improvement_suggestions = [
        "Add task priority queue",
        "Implement circuit breaker for failed agents",
        "Add task caching for repeated tasks",
        "Implement adaptive timeout based on task history"
    ]
    
    return {
        "agent_id": self.agent_id,
        "performance_score": success_rate,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvement_suggestions": improvement_suggestions,
        "metrics": metrics
    }
```

#### Implementation Checklist

- [ ] **2.2.1** Fix imports (TaskDecomposer, get_agent_registry)
- [ ] **2.2.2** Fix `_group_by_generation()` with topological sort
- [ ] **2.2.3** Enhance `aggregate_results()` with error handling
- [ ] **2.2.4** Fix `__init__()` to use AgentRegistry singleton
- [ ] **2.2.5** Implement `self_evaluate()` method
- [ ] **2.2.6** Update `bootstrap_and_validate()` to check TaskDecomposer
- [ ] **2.2.7** Add error recovery for failed subtasks
- [ ] **2.2.8** Add metrics collection for orchestration
- [ ] **2.2.9** Add unit tests for orchestration
- [ ] **2.2.10** Add integration tests with TaskDecomposer

---

### STEP 2.3: Integration Testing ✅

**Status:** NOT STARTED  
**Priority:** 🟡 **HIGH**  
**Estimated Time:** 1 day

#### Test Scenarios Required

1. **Simple Task Decomposition**
   - Single-step task → No decomposition
   - Verify returns single subtask

2. **Complex Task Decomposition**
   - Compression analysis → 4 subtasks with dependencies
   - Verify dependency graph correct

3. **Parallel Execution**
   - Multiple independent subtasks → Execute in parallel
   - Verify all complete successfully

4. **Sequential Execution**
   - Dependent subtasks → Execute in order
   - Verify dependencies respected

5. **Error Handling**
   - Failed subtask → Retry logic works
   - Partial failure → Partial results returned

6. **End-to-End Workflow**
   - Task → Decomposition → Execution → Aggregation
   - Verify complete flow works

---

## 🎯 PHASE 3: META-LEARNING LAYER (Week 3-4)

### STEP 3.1: Complete Meta-Learner Agent ✅→✅ (45% → 100%)

**Status:** PARTIALLY IMPLEMENTED (45%)  
**Priority:** 🔴 **CRITICAL INNOVATION**  
**Estimated Time:** 2-3 days  
**Dependencies:** Orchestrator (for performance data)

**Current File:** `backend/app/agents/orchestrator/meta_learner_agent.py`

#### Missing Components Analysis

**Already Implemented ✅:**
- `execute()` - ✅ Complete (uses TaskEnvelope pattern)
- `_learn_from_experience()` - ✅ Complete
- `_generate_insights()` - ✅ Complete
- `_analyze_performance()` - ⚠️ Partial (needs enhancement)
- ExperienceMemory, InsightGenerator, AdaptiveStrategyEngine - ✅ Complete

**Missing/Incomplete ❌:**
1. **`execute_task()`** - Needs to match BaseAgent pattern (not just `execute()`)
2. **`bootstrap_and_validate()`** - Missing
3. **`self_evaluate()`** - Missing
4. **`continuous_learning_loop()`** - **CRITICAL: Missing**
5. **`_generate_hypotheses()`** - Missing
6. **`_run_experiment()`** - Missing
7. **`_validate_improvement()`** - Missing
8. **`_deploy_optimization()`** - **CRITICAL: Meta-recursive deployment missing**

#### Detailed Implementation Steps

##### 3.1.1: Add `bootstrap_and_validate()` Method

```python
async def bootstrap_and_validate(self) -> BootstrapResult:
    """Bootstrap and validate Meta-Learner agent."""
    result = BootstrapResult()
    
    # Validate learning components
    result.add_validation(
        "experience_memory",
        self.experience_memory is not None,
        "Experience memory initialized"
    )
    
    result.add_validation(
        "insight_generator",
        self.insight_generator is not None,
        "Insight generator initialized"
    )
    
    result.add_validation(
        "adaptive_engine",
        self.adaptive_engine is not None,
        "Adaptive strategy engine initialized"
    )
    
    # Validate capabilities
    result.add_validation(
        "capabilities",
        len(self.capabilities) > 0,
        f"Agent has {len(self.capabilities)} capabilities"
    )
    
    # Self-test: Try to generate an insight
    try:
        test_insight = self.insight_generator.generate_strategy_improvements([])
        result.add_validation("self_test", True, "Insight generation works")
    except Exception as e:
        result.add_validation("self_test", False, f"Self-test failed: {e}")
    
    if all(result.validations.values()):
        result.success = True
        self.status = AgentStatus.IDLE
    else:
        result.success = False
        self.status = AgentStatus.ERROR
    
    return result
```

##### 3.1.2: Add `execute_task()` Method (BaseAgent Pattern)

```python
async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute meta-learning task (BaseAgent pattern)."""
    task_id = task.get("task_id", "unknown")
    operation = task.get("operation", "")
    parameters = task.get("parameters", {})
    
    try:
        if operation == "learn_from_experience":
            result_data = await self._learn_from_experience(parameters)
        elif operation == "generate_insights":
            result_data = await self._generate_insights(parameters)
        elif operation == "adapt_strategy":
            result_data = await self._adapt_strategy(parameters)
        elif operation == "analyze_performance":
            result_data = await self._analyze_performance(parameters)
        elif operation == "generate_hypotheses":
            result_data = await self._generate_hypotheses(parameters)
        elif operation == "run_experiment":
            result_data = await self._run_experiment(parameters)
        elif operation == "validate_improvement":
            result_data = await self._validate_improvement(parameters)
        elif operation == "deploy_optimization":
            result_data = await self._deploy_optimization(parameters)
        else:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": f"Unsupported meta-learning operation: {operation}"
            }
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result_data,
            "operation": operation
        }
        
    except Exception as e:
        logger.error(f"Meta-learning task {task_id} failed: {e}")
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
            "operation": operation
        }
```

##### 3.1.3: Implement `continuous_learning_loop()` ⭐ CRITICAL

```python
async def continuous_learning_loop(self):
    """
    THE CORE META-RECURSIVE LOOP.
    
    Continuously:
    1. Analyze performance
    2. Generate improvement hypotheses
    3. Run experiments
    4. Validate improvements
    5. Deploy optimizations ⭐ META-RECURSION
    6. Monitor impact
    7. Repeat
    
    This is the KEY INNOVATION of the system.
    """
    learning_interval = self.config.get("learning_interval_seconds", 3600)
    iteration = 0
    
    logger.info("🔄 Meta-learning continuous loop started")
    
    while True:
        try:
            iteration += 1
            logger.info(f"🔄 Meta-learning iteration {iteration}")
            
            # Step 1: Analyze current performance
            performance_analysis = await self._analyze_performance({})
            
            if not performance_analysis.get("optimization_opportunities"):
                logger.info("No optimization opportunities found")
                await asyncio.sleep(learning_interval)
                continue
            
            # Step 2: Generate improvement hypotheses
            hypotheses = await self._generate_hypotheses(performance_analysis)
            
            logger.info(f"Generated {len(hypotheses.get('hypotheses', []))} hypotheses")
            
            # Step 3: Run experiments for each hypothesis
            for hypothesis in hypotheses.get("hypotheses", []):
                logger.info(f"🧪 Running experiment: {hypothesis.get('id')}")
                
                experiment_result = await self._run_experiment({"hypothesis": hypothesis})
                
                # Step 4: Validate improvement
                if experiment_result.get("success"):
                    validation = await self._validate_improvement({
                        "experiment_result": experiment_result,
                        "hypothesis": hypothesis
                    })
                    
                    # Step 5: Deploy if validated ⭐ META-RECURSION
                    if validation.get("validated"):
                        logger.info(f"🚀 Deploying optimization: {hypothesis.get('id')}")
                        deployment_result = await self._deploy_optimization({
                            "validation": validation,
                            "hypothesis": hypothesis
                        })
                        
                        if deployment_result.get("deployed"):
                            logger.info(
                                f"✅ Optimization deployed successfully "
                                f"(Total: {self.improvements_deployed})"
                            )
                        else:
                            logger.warning(
                                f"⚠️ Optimization deployment failed: "
                                f"{deployment_result.get('error')}"
                            )
            
            await asyncio.sleep(learning_interval)
            
        except Exception as e:
            logger.error(f"💥 Meta-learning loop error: {e}", exc_info=True)
            await asyncio.sleep(learning_interval)
```

##### 3.1.4: Implement `_generate_hypotheses()` Method

```python
async def _generate_hypotheses(
    self,
    performance_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate improvement hypotheses based on performance analysis.
    
    Analyzes:
    - Slow execution patterns
    - High failure rates
    - Resource inefficiencies
    - Optimization opportunities
    """
    opportunities = performance_analysis.get("optimization_opportunities", [])
    hypotheses = []
    
    for opp in opportunities:
        opp_type = opp.get("type")
        task_type = opp.get("task_type", "unknown")
        
        if opp_type == "slow_execution":
            # Hypothesis: Caching will improve performance
            hypotheses.append({
                "id": f"hyp_caching_{len(hypotheses)+1}",
                "type": "caching",
                "description": f"Cache results for {task_type} tasks",
                "expected_improvement": "40% faster for cached tasks",
                "implementation": "Add Redis caching layer",
                "target_metric": "execution_time",
                "target_value": opp.get("current_duration_ms", 0) * 0.6,
                "confidence": 0.8
            })
            
            # Hypothesis: Parallelization will improve performance
            hypotheses.append({
                "id": f"hyp_parallel_{len(hypotheses)+1}",
                "type": "parallelization",
                "description": f"Increase parallel execution for {task_type}",
                "expected_improvement": "30% faster with more parallelism",
                "implementation": "Increase max_parallel_tasks",
                "target_metric": "execution_time",
                "target_value": opp.get("current_duration_ms", 0) * 0.7,
                "confidence": 0.7
            })
        
        elif opp_type == "high_failure_rate":
            # Hypothesis: Retry strategy will reduce failures
            hypotheses.append({
                "id": f"hyp_retry_{len(hypotheses)+1}",
                "type": "retry_strategy",
                "description": f"Optimize retry strategy for {task_type}",
                "expected_improvement": "20% fewer failures",
                "implementation": "Exponential backoff with jitter",
                "target_metric": "failure_rate",
                "target_value": opp.get("failure_rate", 0) * 0.8,
                "confidence": 0.75
            })
        
        elif opp_type == "resource_inefficiency":
            # Hypothesis: Resource optimization
            hypotheses.append({
                "id": f"hyp_resource_{len(hypotheses)+1}",
                "type": "resource_optimization",
                "description": f"Optimize resource usage for {task_type}",
                "expected_improvement": "25% resource reduction",
                "implementation": "Adjust resource allocation",
                "target_metric": "resource_usage",
                "target_value": opp.get("current_usage", 0) * 0.75,
                "confidence": 0.7
            })
    
    return {
        "hypotheses": hypotheses,
        "count": len(hypotheses),
        "timestamp": datetime.now().isoformat(),
        "generation_method": "pattern_analysis"
    }
```

##### 3.1.5: Implement `_run_experiment()` Method

```python
async def _run_experiment(
    self,
    task_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run experiment to test hypothesis.
    
    Steps:
    1. Measure baseline performance
    2. Apply hypothesis temporarily
    3. Measure experiment performance
    4. Revert hypothesis
    5. Calculate improvement
    """
    hypothesis = task_data.get("hypothesis", {})
    hypothesis_id = hypothesis.get("id")
    hypothesis_type = hypothesis.get("type")
    
    logger.info(f"🧪 Running experiment: {hypothesis_id}")
    
    try:
        # Step 1: Measure baseline
        baseline_performance = await self._measure_baseline(hypothesis)
        
        # Step 2: Apply hypothesis temporarily
        await self._apply_hypothesis(hypothesis)
        
        # Step 3: Measure experiment performance
        experiment_performance = await self._measure_experiment(hypothesis)
        
        # Step 4: Revert hypothesis
        await self._revert_hypothesis(hypothesis)
        
        # Step 5: Calculate improvement
        improvement_pct = (
            (baseline_performance - experiment_performance) / baseline_performance * 100
            if baseline_performance > 0 else 0
        )
        
        meets_expectations = (
            improvement_pct >= hypothesis.get("expected_improvement_pct", 20)
        )
        
        return {
            "hypothesis_id": hypothesis_id,
            "success": True,
            "baseline_performance_ms": baseline_performance,
            "experiment_performance_ms": experiment_performance,
            "improvement_percent": improvement_pct,
            "meets_expectations": meets_expectations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Experiment {hypothesis_id} failed: {e}")
        return {
            "hypothesis_id": hypothesis_id,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def _measure_baseline(self, hypothesis: Dict[str, Any]) -> float:
    """Measure baseline performance before applying hypothesis."""
    # Run sample tasks and measure performance
    # For now, simulated
    return 5000.0  # milliseconds

async def _apply_hypothesis(self, hypothesis: Dict[str, Any]):
    """Temporarily apply hypothesis (without persisting)."""
    # Store original config
    # Apply hypothesis changes
    # For now, log the application
    logger.info(f"Applying hypothesis: {hypothesis.get('id')}")

async def _revert_hypothesis(self, hypothesis: Dict[str, Any]):
    """Revert hypothesis changes."""
    # Restore original config
    logger.info(f"Reverting hypothesis: {hypothesis.get('id')}")

async def _measure_experiment(self, hypothesis: Dict[str, Any]) -> float:
    """Measure performance with hypothesis applied."""
    # Run same sample tasks and measure
    # For now, simulated improvement
    return 3000.0  # milliseconds (40% improvement)
```

##### 3.1.6: Implement `_validate_improvement()` Method

```python
async def _validate_improvement(
    self,
    task_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate that improvement is real and sustainable.
    
    Checks:
    - Improvement meets expectations
    - No side effects
    - Consistency across multiple runs
    - Statistical significance
    """
    experiment_result = task_data.get("experiment_result", {})
    hypothesis = task_data.get("hypothesis", {})
    
    # Check if improvement meets expectations
    validation_passed = experiment_result.get("meets_expectations", False)
    
    # Check for side effects
    side_effects = await self._check_side_effects(experiment_result, hypothesis)
    
    # Verify consistency (would run multiple times in production)
    consistency = await self._check_consistency(experiment_result, hypothesis)
    
    # Check statistical significance (simplified)
    statistical_significance = (
        experiment_result.get("improvement_percent", 0) > 10
    )
    
    validated = (
        validation_passed and
        not side_effects and
        consistency > 0.8 and
        statistical_significance
    )
    
    return {
        "validated": validated,
        "confidence": 0.85 if validated else 0.3,
        "recommendation": "deploy" if validated else "reject",
        "side_effects": side_effects,
        "consistency": consistency,
        "statistical_significance": statistical_significance,
        "hypothesis": hypothesis,
        "timestamp": datetime.now().isoformat()
    }

async def _check_side_effects(
    self,
    experiment_result: Dict[str, Any],
    hypothesis: Dict[str, Any]
) -> bool:
    """Check if hypothesis has negative side effects."""
    # Would check:
    # - Error rate changes
    # - Resource usage changes
    # - Other metrics degradation
    # For now, simplified
    return False  # No side effects detected

async def _check_consistency(
    self,
    experiment_result: Dict[str, Any],
    hypothesis: Dict[str, Any]
) -> float:
    """Check if improvement is consistent across runs."""
    # Would run multiple times and check variance
    # For now, simulated
    return 0.9  # 90% consistency
```

##### 3.1.7: Implement `_deploy_optimization()` ⭐ META-RECURSIVE

```python
async def _deploy_optimization(
    self,
    task_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deploy validated optimization.
    
    ⭐ THIS IS THE META-RECURSIVE STEP:
    System modifies its own code/configuration.
    
    This is the CORE INNOVATION that enables self-improvement.
    """
    validation = task_data.get("validation", {})
    hypothesis = validation.get("hypothesis", task_data.get("hypothesis", {}))
    
    optimization_type = hypothesis.get("type")
    hypothesis_id = hypothesis.get("id")
    
    logger.info(f"🚀 Deploying optimization: {hypothesis_id} (META-RECURSIVE)")
    
    deployment_result = {
        "deployed": False,
        "error": None,
        "deployment_id": f"deploy_{int(time.time())}",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        if optimization_type == "caching":
            # Update configuration to enable caching
            await self._update_config("enable_caching", True)
            await self._update_config("cache_ttl_seconds", 3600)
            
        elif optimization_type == "retry_strategy":
            # Update retry configuration
            await self._update_config("retry_strategy", "exponential_backoff")
            await self._update_config("max_retries", 5)
            await self._update_config("retry_backoff_base", 2)
            
        elif optimization_type == "parallelization":
            # Update max parallel tasks
            new_value = hypothesis.get("target_value", 20)
            await self._update_config("max_parallel_tasks", int(new_value))
            
        elif optimization_type == "resource_optimization":
            # Update resource allocation
            await self._update_config("resource_allocation", "optimized")
            
        # Reload affected services
        await self._reload_services()
        
        deployment_result["deployed"] = True
        self.improvements_deployed += 1
        
        logger.info(
            f"✅ Optimization deployed successfully "
            f"(Total improvements: {self.improvements_deployed})"
        )
        
    except Exception as e:
        deployment_result["error"] = str(e)
        logger.error(f"💥 Optimization deployment failed: {e}")
    
    return deployment_result

async def _update_config(self, key: str, value: Any):
    """
    Update system configuration (meta-recursive).
    
    This is where the system modifies itself.
    
    Options:
    1. Update environment variables
    2. Update config file
    3. Update database config table
    4. Update runtime configuration
    """
    logger.info(f"🔧 Updating config: {key} = {value} (META-RECURSIVE)")
    
    # For MVP: Store in agent's config
    # In production: Update persistent config storage
    self.config[key] = value
    
    # Could also update global config
    # import os
    # os.environ[f"AGENT_CONFIG_{key}"] = str(value)

async def _reload_services(self):
    """
    Reload services after config update.
    
    This triggers the system to use new configuration.
    """
    logger.info("🔄 Reloading services after optimization deployment")
    
    # For MVP: Notify agents of config change
    # In production: Restart services, reload configs, etc.
    
    # Could use message bus to notify agents
    # await self.bus.publish("config.updated", {"timestamp": datetime.now().isoformat()})
```

##### 3.1.8: Implement `self_evaluate()` Method

```python
async def self_evaluate(self) -> Dict[str, Any]:
    """Evaluate Meta-Learner agent performance."""
    metrics = await self.report_metrics()
    
    performance_score = metrics.get("success_rate", 0.0)
    
    strengths = []
    if self.learning_cycles_completed > 0:
        strengths.append(f"Completed {self.learning_cycles_completed} learning cycles")
    if self.improvements_deployed > 0:
        strengths.append(f"Deployed {self.improvements_deployed} improvements")
    if len(self.experience_memory.experiences) > 100:
        strengths.append("Large experience memory")
    
    weaknesses = []
    if performance_score < 0.7:
        weaknesses.append("Low meta-learning success rate")
    if self.improvements_deployed == 0:
        weaknesses.append("No improvements deployed yet")
    
    improvement_suggestions = [
        "Integrate with database for persistent experience storage",
        "Add more sophisticated hypothesis generation",
        "Implement A/B testing framework",
        "Add rollback mechanism for failed optimizations"
    ]
    
    return {
        "agent_id": self.agent_id,
        "performance_score": performance_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvement_suggestions": improvement_suggestions,
        "metrics": metrics,
        "learning_statistics": {
            "cycles_completed": self.learning_cycles_completed,
            "improvements_deployed": self.improvements_deployed,
            "experiences_stored": len(self.experience_memory.experiences),
            "insights_generated": len(self.insight_generator.generated_insights)
        }
    }
```

#### Implementation Checklist

- [ ] **3.1.1** Add `bootstrap_and_validate()` method
- [ ] **3.1.2** Add `execute_task()` method (BaseAgent pattern)
- [ ] **3.1.3** Implement `continuous_learning_loop()` ⭐ CRITICAL
- [ ] **3.1.4** Implement `_generate_hypotheses()` method
- [ ] **3.1.5** Implement `_run_experiment()` method
- [ ] **3.1.6** Implement `_validate_improvement()` method
- [ ] **3.1.7** Implement `_deploy_optimization()` ⭐ META-RECURSIVE
- [ ] **3.1.8** Implement `_update_config()` method
- [ ] **3.1.9** Implement `_reload_services()` method
- [ ] **3.1.10** Implement `self_evaluate()` method
- [ ] **3.1.11** Enhance `_analyze_performance()` to use registry
- [ ] **3.1.12** Add helper methods (_measure_baseline, _apply_hypothesis, etc.)
- [ ] **3.1.13** Add unit tests for meta-learning
- [ ] **3.1.14** Add integration tests for continuous loop
- [ ] **3.1.15** Add tests for meta-recursive deployment

---

## 📋 PHASE 4: INTEGRATION & TESTING (Week 4)

### STEP 4.1: Agent Integration ✅

**Status:** NOT STARTED  
**Priority:** 🟡 **HIGH**  
**Estimated Time:** 1 day

#### Required Integration Steps

1. **Register All Agents with Registry**
   - NLPAgent, CodeAgent, DataAgent, ResearchAgent
   - OrchestratorAgent
   - MetaLearnerAgent

2. **Initialize Agent System**
   - Bootstrap all agents
   - Register with registry
   - Verify all agents operational

3. **Create Agent Initialization Script**
   - `scripts/initialize_agent_system.py`
   - Handles startup sequence
   - Error recovery

#### Implementation Checklist

- [ ] **4.1.1** Create agent initialization script
- [ ] **4.1.2** Register all specialist agents
- [ ] **4.1.3** Register OrchestratorAgent
- [ ] **4.1.4** Register MetaLearnerAgent
- [ ] **4.1.5** Start continuous learning loop (background task)
- [ ] **4.1.6** Verify all agents can communicate
- [ ] **4.1.7** Test end-to-end task flow

---

### STEP 4.2: Comprehensive Testing ✅

**Status:** NOT STARTED  
**Priority:** 🟡 **HIGH**  
**Estimated Time:** 2-3 days

#### Test Categories

##### 4.2.1: Unit Tests

**TaskDecomposer Tests:**
- Test decomposition strategies
- Test topological sort
- Test dependency graph building
- Test cycle detection
- Test parallel group extraction

**Orchestrator Tests:**
- Test task decomposition
- Test agent selection
- Test parallel execution
- Test dependency resolution
- Test result aggregation
- Test error handling

**Meta-Learner Tests:**
- Test hypothesis generation
- Test experiment execution
- Test validation logic
- Test deployment process
- Test continuous loop

##### 4.2.2: Integration Tests

**Multi-Agent Workflows:**
- Test complete task orchestration
- Test agent communication
- Test registry discovery
- Test load balancing

**Meta-Learning Integration:**
- Test performance analysis
- Test improvement deployment
- Test system self-modification

##### 4.2.3: End-to-End Tests

**Complete Workflows:**
- Compression analysis workflow
- Code review workflow
- Data pipeline workflow
- Meta-learning cycle

#### Implementation Checklist

- [ ] **4.2.1** Create unit test suite for TaskDecomposer
- [ ] **4.2.2** Create unit test suite for Orchestrator
- [ ] **4.2.3** Create unit test suite for Meta-Learner
- [ ] **4.2.4** Create integration test suite
- [ ] **4.2.5** Create E2E test suite
- [ ] **4.2.6** Achieve >90% code coverage
- [ ] **4.2.7** Add performance benchmarks

---

## 🎯 PRIORITY ORDER OF IMPLEMENTATION

### Week 2 (Days 1-3): TaskDecomposer & Orchestrator

**Day 1:**
- ✅ Step 2.1.1-2.1.7: Core TaskDecomposer implementation
- ✅ Step 2.1.8-2.1.11: Decomposition strategies

**Day 2:**
- ✅ Step 2.2.1-2.2.5: Complete OrchestratorAgent
- ✅ Step 2.2.6-2.2.10: Integration and testing

**Day 3:**
- ✅ Step 2.3: Integration testing
- ✅ Step 4.1: Agent integration

### Week 3 (Days 4-7): Meta-Learner

**Day 4:**
- ✅ Step 3.1.1-3.1.3: Bootstrap and continuous loop

**Day 5:**
- ✅ Step 3.1.4-3.1.6: Hypothesis generation and experiments

**Day 6:**
- ✅ Step 3.1.7-3.1.9: Meta-recursive deployment

**Day 7:**
- ✅ Step 3.1.10-3.1.15: Testing and validation

### Week 4 (Days 8-10): Testing & Polish

**Day 8-9:**
- ✅ Step 4.2: Comprehensive testing

**Day 10:**
- ✅ Documentation and final polish

---

## 📊 DETAILED TASK BREAKDOWN

### TaskDecomposer Implementation (Step 2.1)

| Task | Description | Lines | Priority | Dependencies |
|------|-------------|-------|----------|--------------|
| 2.1.1 | Create Subtask dataclass | ~20 | 🔴 Critical | None |
| 2.1.2 | Create TaskDecomposer class | ~30 | 🔴 Critical | 2.1.1 |
| 2.1.3 | Implement decompose() | ~50 | 🔴 Critical | 2.1.2 |
| 2.1.4 | Implement _subtask_to_dict() | ~15 | 🔴 Critical | 2.1.1 |
| 2.1.5 | Implement _build_dependency_graph() | ~40 | 🔴 Critical | 2.1.3 |
| 2.1.6 | Implement _topological_sort() | ~60 | 🔴 Critical | 2.1.5 |
| 2.1.7 | Implement get_parallel_tasks() | ~30 | 🔴 Critical | 2.1.6 |
| 2.1.8 | Compression analysis strategy | ~50 | 🟡 High | 2.1.3 |
| 2.1.9 | Code review strategy | ~40 | 🟡 High | 2.1.3 |
| 2.1.10 | Data pipeline strategy | ~40 | 🟡 High | 2.1.3 |
| 2.1.11 | Multi-step generic strategy | ~30 | 🟡 High | 2.1.3 |
| 2.1.12 | Cycle detection | ~30 | 🟡 High | 2.1.5 |
| 2.1.13 | Complexity analysis | ~40 | 🟢 Medium | 2.1.2 |
| **Total** | **~475 lines** | | | |

### Orchestrator Completion (Step 2.2)

| Task | Description | Lines | Priority | Dependencies |
|------|-------------|-------|----------|--------------|
| 2.2.1 | Fix imports | ~10 | 🔴 Critical | None |
| 2.2.2 | Fix _group_by_generation() | ~40 | 🔴 Critical | 2.1.6 |
| 2.2.3 | Enhance aggregate_results() | ~60 | 🔴 Critical | None |
| 2.2.4 | Fix __init__() | ~20 | 🔴 Critical | None |
| 2.2.5 | Implement self_evaluate() | ~50 | 🟡 High | None |
| 2.2.6 | Update bootstrap | ~15 | 🟡 High | None |
| 2.2.7 | Error recovery | ~40 | 🟡 High | None |
| 2.2.8 | Metrics collection | ~30 | 🟢 Medium | None |
| **Total** | **~265 lines** | | | |

### Meta-Learner Completion (Step 3.1)

| Task | Description | Lines | Priority | Dependencies |
|------|-------------|-------|----------|--------------|
| 3.1.1 | bootstrap_and_validate() | ~40 | 🔴 Critical | None |
| 3.1.2 | execute_task() | ~50 | 🔴 Critical | None |
| 3.1.3 | continuous_learning_loop() ⭐ | ~80 | 🔴 Critical | 3.1.4-3.1.7 |
| 3.1.4 | _generate_hypotheses() | ~60 | 🔴 Critical | None |
| 3.1.5 | _run_experiment() | ~80 | 🔴 Critical | None |
| 3.1.6 | _validate_improvement() | ~50 | 🔴 Critical | 3.1.5 |
| 3.1.7 | _deploy_optimization() ⭐ | ~70 | 🔴 Critical | None |
| 3.1.8 | _update_config() | ~30 | 🔴 Critical | 3.1.7 |
| 3.1.9 | _reload_services() | ~20 | 🔴 Critical | 3.1.7 |
| 3.1.10 | self_evaluate() | ~50 | 🟡 High | None |
| 3.1.11 | Enhance _analyze_performance() | ~40 | 🟡 High | None |
| 3.1.12 | Helper methods | ~60 | 🟡 High | 3.1.5 |
| **Total** | **~570 lines** | | | |

### Testing (Step 4.2)

| Task | Description | Files | Priority |
|------|-------------|-------|----------|
| 4.2.1 | TaskDecomposer unit tests | 1 | 🔴 Critical |
| 4.2.2 | Orchestrator unit tests | 1 | 🔴 Critical |
| 4.2.3 | Meta-Learner unit tests | 1 | 🔴 Critical |
| 4.2.4 | Integration tests | 1 | 🟡 High |
| 4.2.5 | E2E tests | 1 | 🟡 High |
| **Total** | **~5 test files, ~500 lines** | | |

---

## 📈 ESTIMATED EFFORT

### Total Implementation

| Phase | Components | Lines | Days | Status |
|-------|-----------|-------|------|--------|
| Week 1 | BaseAgent, Registry, Specialists | ~1,180 | 5 | ✅ Complete |
| Week 2-3 | TaskDecomposer, Orchestrator | ~740 | 3 | ⏳ In Progress |
| Week 3-4 | Meta-Learner | ~570 | 3 | ⏳ Pending |
| Week 4 | Testing & Integration | ~500 | 2 | ⏳ Pending |
| **Total** | **All Components** | **~2,990** | **13** | **45%** |

---

## 🚀 IMMEDIATE NEXT STEPS (Priority Order)

### Step 1: Implement TaskDecomposer (CRITICAL - BLOCKING)
**File:** `backend/app/core/task_decomposer.py` (NEW)  
**Time:** 2-3 days  
**Blocks:** Orchestrator completion

**Specific Tasks:**
1. Create Subtask dataclass
2. Create TaskDecomposer class
3. Implement Kahn's topological sort algorithm
4. Implement dependency graph builder
5. Implement 4+ decomposition strategies
6. Add cycle detection
7. Add unit tests

### Step 2: Complete Orchestrator Agent
**File:** `backend/app/agents/orchestrator/orchestrator_agent.py`  
**Time:** 1-2 days  
**Depends:** TaskDecomposer

**Specific Tasks:**
1. Fix imports (TaskDecomposer, AgentRegistry)
2. Implement proper _group_by_generation() with topological sort
3. Enhance aggregate_results() method
4. Add self_evaluate() method
5. Integration testing

### Step 3: Complete Meta-Learner Agent
**File:** `backend/app/agents/orchestrator/meta_learner_agent.py`  
**Time:** 2-3 days  
**Depends:** Orchestrator (for performance data)

**Specific Tasks:**
1. Add bootstrap_and_validate()
2. Add execute_task() (BaseAgent pattern)
3. Implement continuous_learning_loop() ⭐
4. Implement hypothesis generation
5. Implement experiment execution
6. Implement validation
7. Implement meta-recursive deployment ⭐

---

## ✅ SUCCESS CRITERIA

**Agent Framework is Complete When:**

1. ✅ All agents can register and be discovered
2. ✅ Orchestrator can decompose and coordinate complex tasks
3. ✅ Tasks execute in parallel respecting dependencies
4. ✅ Meta-learner runs continuous improvement loop
5. ✅ System successfully modifies itself (meta-recursion proven)
6. ✅ All tests pass (>90% coverage)
7. ✅ End-to-end workflows work correctly
8. ✅ Documentation complete

---

**Current Status:** Ready to begin Step 2.1 (TaskDecomposer)  
**Next Action:** Implement TaskDecomposer with topological sort algorithm  
**Estimated Completion:** 13 days total (Week 1 complete, 8 days remaining)
