# AGENT FRAMEWORK - COMPLETE IMPLEMENTATION GUIDE
## All Steps, Methods, and Implementations to Complete Agent Framework (Agent 06)

**Document Version:** 1.0  
**Created:** 2025-11-03  
**Purpose:** Comprehensive implementation guide based on documentation review  
**Status:** Complete Specification Based on Documentation Analysis

---

## 📊 EXECUTIVE SUMMARY

### Current State Analysis

| Component | Status | Implementation Level | Priority |
|-----------|--------|----------------------|----------|
| **BaseAgent Class** | ✅ Partial | 60% | 🔴 Critical |
| **Specialist Agents** | ⚠️ Partial | 40% | 🔴 Critical |
| **Orchestrator Agent** | ⚠️ Partial | 50% | 🔴 Critical |
| **Meta-Learner Agent** | ⚠️ Partial | 45% | 🔴 Critical |
| **Agent Registry** | ❌ Missing | 0% | 🔴 Critical |
| **Communication Protocol** | ✅ Partial | 70% | 🟡 High |
| **Task Decomposer** | ❌ Missing | 0% | 🔴 Critical |
| **Agent Discovery** | ❌ Missing | 0% | 🟡 High |
| **Load Balancing** | ❌ Missing | 0% | 🟡 High |
| **Meta-Recursive Loop** | ⚠️ Partial | 30% | 🔴 Critical |

**Overall Completion:** ~40%  
**Estimated Remaining Work:** 4-5 weeks

---

## 🎯 COMPLETE IMPLEMENTATION CHECKLIST

### PHASE 1: Foundation Layer (Week 1)

#### Step 1.1: Complete BaseAgent Class ✅→✅

**Current Implementation:** `backend/app/core/base_agent.py` (60% complete)

**Missing Methods/Features:**
1. ✅ `bootstrap_and_validate()` - Implemented but needs enhancement
2. ✅ `execute_task()` - Implemented
3. ✅ `self_evaluate()` - Implemented
4. ❌ `can_handle()` - Method exists but needs capability-based logic
5. ❌ `heartbeat()` - Needs implementation
6. ❌ `shutdown()` - Missing graceful shutdown
7. ❌ `get_metrics()` - Exists but needs expansion
8. ❌ `register_with_registry()` - Missing
9. ❌ `handle_communication()` - Missing
10. ❌ `update_performance_history()` - Missing

**Implementation Steps:**

```python
# backend/app/core/base_agent.py

class BaseAgent(ABC):
    """Enhanced BaseAgent with complete lifecycle management."""
    
    # ADD THESE METHODS:
    
    async def heartbeat(self) -> Dict[str, Any]:
        """
        Update heartbeat and check agent health.
        Returns health status for monitoring.
        """
        self.last_active_at = datetime.now()
        health = await self._check_health()
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "health": health,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self) -> Dict[str, Any]:
        """
        Graceful agent shutdown.
        Saves state, closes connections, notifies registry.
        """
        logger.info(f"Shutting down agent {self.agent_id}")
        self.status = AgentStatus.SHUTDOWN
        
        # Save state if needed
        await self._save_state()
        
        # Close connections
        await self._close_connections()
        
        # Notify registry
        if hasattr(self, 'registry'):
            await self.registry.unregister(self.agent_id)
        
        return {"status": "shutdown", "agent_id": self.agent_id}
    
    def can_handle(self, task_type: str, task_requirements: Dict[str, Any] = None) -> bool:
        """
        Check if agent can handle a task type.
        Enhanced with capability matching and requirements checking.
        """
        # Check capability matching
        task_capabilities = self._extract_required_capabilities(task_type)
        
        if not any(cap in [c.value for c in self.capabilities] for cap in task_capabilities):
            return False
        
        # Check requirements if provided
        if task_requirements:
            return self._meets_requirements(task_requirements)
        
        return True
    
    async def register_with_registry(self, registry: 'AgentRegistry'):
        """Register agent with the global registry."""
        self.registry = registry
        await registry.register(self)
        logger.info(f"Agent {self.agent_id} registered with registry")
    
    def _extract_required_capabilities(self, task_type: str) -> List[str]:
        """Extract required capabilities from task type."""
        # Map task types to capabilities
        task_capability_map = {
            "compression": ["compression"],
            "nlp": ["analysis"],
            "code_generation": ["code_generation"],
            "meta_learning": ["learning", "meta_learning"],
            # Add more mappings
        }
        return task_capability_map.get(task_type.lower(), [])
    
    def _meets_requirements(self, requirements: Dict[str, Any]) -> bool:
        """Check if agent meets task requirements."""
        # Check status
        if requirements.get("require_idle") and self.status != AgentStatus.IDLE:
            return False
        
        # Check minimum performance
        if requirements.get("min_success_rate"):
            success_rate = self.success_count / self.task_count if self.task_count > 0 else 0
            if success_rate < requirements["min_success_rate"]:
                return False
        
        return True
    
    async def _check_health(self) -> Dict[str, Any]:
        """Check agent health status."""
        uptime = (datetime.now() - self.created_at).total_seconds()
        last_active_ago = (datetime.now() - self.last_active_at).total_seconds()
        
        return {
            "healthy": self.status != AgentStatus.ERROR,
            "uptime_seconds": uptime,
            "last_active_seconds_ago": last_active_ago,
            "task_count": self.task_count,
            "success_rate": self.success_count / self.task_count if self.task_count > 0 else 0
        }
    
    async def _save_state(self):
        """Save agent state for recovery."""
        # Implementation depends on persistence strategy
        pass
    
    async def _close_connections(self):
        """Close all agent connections."""
        # Implementation depends on connection types
        pass
```

---

#### Step 1.2: Implement Specialist Agents ✅→✅

**Current Implementation:** `backend/app/agents/orchestrator/specialist_agents.py` (40% complete)

**Missing Implementations:**

1. **NLP Agent** - Complete Implementation
2. **Code Agent** - Complete Implementation  
3. **Data Agent** - Complete Implementation
4. **Research Agent** - Complete Implementation

**Implementation Steps:**

```python
# backend/app/agents/orchestrator/specialist_agents.py

from app.core.base_agent import BaseAgent, AgentCapability, BootstrapResult
from typing import Dict, Any, Optional, List

class NLPAgent(BaseAgent):
    """Natural Language Processing Agent."""
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id or "nlp_agent_001",
            agent_type="nlp_specialist",
            config=config
        )
        self.capabilities = [
            AgentCapability.ANALYSIS,
            AgentCapability.LEARNING
        ]
        self.supported_tasks = [
            "text_analysis",
            "sentiment_analysis",
            "entity_extraction",
            "text_generation",
            "translation",
            "summarization"
        ]
    
    async def bootstrap_and_validate(self) -> BootstrapResult:
        """Bootstrap NLP agent."""
        result = BootstrapResult()
        
        # Validate NLP libraries available
        try:
            import nltk
            result.add_validation("nltk", True)
        except ImportError:
            result.add_validation("nltk", False, "NLTK not available")
        
        # Validate LLM connection (for text generation)
        # This will be Agent 07 integration
        
        if all(result.validations.values()):
            result.success = True
            self.status = AgentStatus.IDLE
        else:
            result.success = False
            self.status = AgentStatus.ERROR
        
        return result
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NLP task."""
        task_type = task.get("operation", "")
        task_input = task.get("parameters", {})
        
        if task_type == "text_analysis":
            return await self._analyze_text(task_input)
        elif task_type == "sentiment_analysis":
            return await self._analyze_sentiment(task_input)
        elif task_type == "entity_extraction":
            return await self._extract_entities(task_input)
        elif task_type == "text_generation":
            return await self._generate_text(task_input)
        elif task_type == "summarization":
            return await self._summarize_text(task_input)
        else:
            return {"error": f"Unsupported task type: {task_type}"}
    
    async def _analyze_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text structure and content."""
        text = input_data.get("text", "")
        
        return {
            "word_count": len(text.split()),
            "character_count": len(text),
            "sentence_count": text.count(".") + text.count("!") + text.count("?"),
            "paragraph_count": text.count("\n\n") + 1,
            "average_word_length": (
                sum(len(word) for word in text.split()) / len(text.split())
                if text.split() else 0
            )
        }
    
    async def _analyze_sentiment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text sentiment."""
        text = input_data.get("text", "").lower()
        
        # Simple sentiment analysis (replace with actual model)
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "love"]
        negative_words = ["bad", "terrible", "awful", "horrible", "poor", "hate"]
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
        elif neg_count > pos_count:
            sentiment = "negative"
            score = max(0.1, 0.5 - (neg_count - pos_count) * 0.1)
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_indicators": pos_count,
            "negative_indicators": neg_count
        }
    
    async def _extract_entities(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract named entities from text."""
        text = input_data.get("text", "")
        
        # Simple entity extraction (replace with NER model)
        words = text.split()
        entities = [
            {"text": word, "type": "PROPER_NOUN", "confidence": 0.8}
            for word in words
            if word and word[0].isupper() and len(word) > 2
        ]
        
        return {
            "entities": entities,
            "count": len(entities)
        }
    
    async def _generate_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text based on prompt."""
        prompt = input_data.get("prompt", "")
        max_length = input_data.get("max_length", 100)
        
        # This will integrate with LLM service (Agent 07)
        # For now, placeholder response
        generated_text = f"Generated response to: {prompt[:50]}..."
        
        return {
            "generated_text": generated_text,
            "length": len(generated_text),
            "prompt": prompt
        }
    
    async def _summarize_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize long text."""
        text = input_data.get("text", "")
        max_length = input_data.get("max_length", 100)
        
        # Simple summarization (first N characters)
        summary = text[:max_length] + "..." if len(text) > max_length else text
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if text else 0
        }

# Similar implementations for CodeAgent, DataAgent, ResearchAgent
# See COMPLETE-AGENT-06-SPECIFICATION.md for full implementations
```

---

### PHASE 2: Orchestration Layer (Week 2-3)

#### Step 2.1: Complete Orchestrator Agent ✅→✅

**Current Implementation:** `backend/app/agents/orchestrator/orchestrator_agent.py` (50% complete)

**Missing Methods/Features:**
1. ❌ `decompose_task()` - Task decomposition logic
2. ❌ `select_agent()` - Agent selection algorithm
3. ❌ `coordinate_execution()` - Parallel execution coordination
4. ❌ `aggregate_results()` - Result aggregation
5. ❌ `handle_dependencies()` - Dependency resolution
6. ❌ `retry_failed_tasks()` - Retry logic
7. ❌ `timeout_handling()` - Timeout management

**Implementation Steps:**

```python
# backend/app/agents/orchestrator/orchestrator_agent.py

from app.core.base_agent import BaseAgent, AgentCapability, BootstrapResult
from app.core.task_decomposer import TaskDecomposer  # TO BE IMPLEMENTED
from typing import Dict, Any, Optional, List, Set
import asyncio
from datetime import datetime, timedelta

class OrchestratorAgent(BaseAgent):
    """Orchestrator Agent - Coordinates all other agents."""
    
    def __init__(
        self,
        agent_registry: 'AgentRegistry',  # TO BE IMPLEMENTED
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id or "orchestrator_001",
            agent_type="orchestrator",
            config=config
        )
        self.agent_registry = agent_registry
        self.task_decomposer = TaskDecomposer()
        self.capabilities = [AgentCapability.ORCHESTRATION]
        
        # Task tracking
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.max_parallel_tasks = config.get("max_parallel_tasks", 10)
        self.task_timeout_seconds = config.get("task_timeout_seconds", 300)
        self.max_retries = config.get("max_retries", 3)
    
    async def bootstrap_and_validate(self) -> BootstrapResult:
        """Bootstrap orchestrator agent."""
        result = BootstrapResult()
        
        # Validate agent registry available
        if self.agent_registry:
            result.add_validation("agent_registry", True)
        else:
            result.add_validation("agent_registry", False, "Agent registry not provided")
        
        # Validate task decomposer
        if self.task_decomposer:
            result.add_validation("task_decomposer", True)
        else:
            result.add_validation("task_decomposer", False, "Task decomposer not initialized")
        
        # Check for at least one specialist agent
        available_agents = len(self.agent_registry.get_all_agents()) if self.agent_registry else 0
        if available_agents > 0:
            result.add_validation("specialist_agents", True, f"{available_agents} agents available")
        else:
            result.add_validation("specialist_agents", False, "No specialist agents available")
        
        if all(result.validations.values()):
            result.success = True
            self.status = AgentStatus.IDLE
        else:
            result.success = False
            self.status = AgentStatus.ERROR
        
        return result
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrated task."""
        task_id = task.get("task_id", f"orch_{datetime.now().timestamp()}")
        task_type = task.get("operation", "")
        task_input = task.get("parameters", {})
        
        try:
            self.status = AgentStatus.WORKING
            start_time = datetime.now()
            
            # Step 1: Decompose task into subtasks
            subtasks, dependency_graph = await self.decompose_task(
                task_type, task_input
            )
            
            # Step 2: Execute subtasks in parallel (respecting dependencies)
            results = await self.coordinate_execution(
                task_id, subtasks, dependency_graph
            )
            
            # Step 3: Aggregate results
            final_result = await self.aggregate_results(results)
            
            # Step 4: Update task history
            duration = (datetime.now() - start_time).total_seconds()
            self.task_history.append({
                "task_id": task_id,
                "type": task_type,
                "subtask_count": len(subtasks),
                "duration_seconds": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            self.status = AgentStatus.IDLE
            self.task_count += 1
            self.success_count += 1
            
            return {
                "success": True,
                "task_id": task_id,
                "result": final_result,
                "subtask_count": len(subtasks),
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.task_count += 1
            self.error_count += 1
            logger.error(f"Orchestration failed: {e}")
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def decompose_task(
        self,
        task_type: str,
        task_input: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Set[str]]]:
        """
        Decompose complex task into subtasks.
        
        Returns:
            - List of subtasks
            - Dependency graph (subtask_id -> set of prerequisite subtask_ids)
        """
        return await self.task_decomposer.decompose(task_type, task_input)
    
    async def coordinate_execution(
        self,
        parent_task_id: str,
        subtasks: List[Dict[str, Any]],
        dependency_graph: Dict[str, Set[str]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Coordinate parallel execution of subtasks.
        
        Handles:
        - Dependency resolution
        - Parallel execution groups
        - Retry logic
        - Timeout handling
        """
        results = {}
        completed: Set[str] = set()
        
        # Group subtasks by dependency level (generations)
        generations = self._group_by_generation(subtasks, dependency_graph)
        
        # Execute each generation sequentially, tasks within generation in parallel
        for generation in generations:
            # Wait for prerequisites
            await self._wait_for_prerequisites(generation, dependency_graph, completed)
            
            # Execute generation in parallel
            generation_results = await asyncio.gather(
                *[
                    self._execute_subtask_with_retry(
                        parent_task_id, subtask, results
                    )
                    for subtask in generation
                ],
                return_exceptions=True
            )
            
            # Store results
            for subtask, result in zip(generation, generation_results):
                subtask_id = subtask.get("id")
                if isinstance(result, Exception):
                    results[subtask_id] = {
                        "success": False,
                        "error": str(result)
                    }
                else:
                    results[subtask_id] = result
                    completed.add(subtask_id)
        
        return results
    
    def _group_by_generation(
        self,
        subtasks: List[Dict[str, Any]],
        dependency_graph: Dict[str, Set[str]]
    ) -> List[List[Dict[str, Any]]]:
        """Group subtasks into dependency generations."""
        # TODO: Implement topological sort to group by dependency level
        # For now, simple implementation
        return [subtasks]  # Placeholder
    
    async def _wait_for_prerequisites(
        self,
        generation: List[Dict[str, Any]],
        dependency_graph: Dict[str, Set[str]],
        completed: Set[str]
    ):
        """Wait for all prerequisites of a generation to complete."""
        all_prerequisites = set()
        for subtask in generation:
            subtask_id = subtask.get("id")
            prerequisites = dependency_graph.get(subtask_id, set())
            all_prerequisites.update(prerequisites)
        
        # Wait until all prerequisites are completed
        max_wait = self.task_timeout_seconds
        wait_start = datetime.now()
        
        while not all_prerequisites.issubset(completed):
            if (datetime.now() - wait_start).total_seconds() > max_wait:
                raise TimeoutError("Prerequisites did not complete in time")
            await asyncio.sleep(0.1)
    
    async def _execute_subtask_with_retry(
        self,
        parent_task_id: str,
        subtask: Dict[str, Any],
        previous_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute subtask with retry logic."""
        subtask_id = subtask.get("id")
        retries = 0
        
        while retries <= self.max_retries:
            try:
                # Select appropriate agent
                agent = await self.select_agent(subtask)
                
                if not agent:
                    return {
                        "success": False,
                        "error": f"No agent found for subtask {subtask_id}"
                    }
                
                # Resolve input dependencies
                resolved_input = self._resolve_input_dependencies(
                    subtask.get("input", {}),
                    previous_results
                )
                
                # Execute with timeout
                task_data = {
                    "operation": subtask.get("type"),
                    "parameters": resolved_input
                }
                
                result = await asyncio.wait_for(
                    agent.execute_task(task_data),
                    timeout=self.task_timeout_seconds
                )
                
                return {
                    "success": True,
                    "subtask_id": subtask_id,
                    "agent_id": agent.agent_id,
                    "result": result
                }
                
            except asyncio.TimeoutError:
                retries += 1
                if retries > self.max_retries:
                    return {
                        "success": False,
                        "error": f"Subtask {subtask_id} timed out after {retries} retries"
                    }
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    return {
                        "success": False,
                        "error": f"Subtask {subtask_id} failed: {str(e)}"
                    }
                await asyncio.sleep(2 ** retries)  # Exponential backoff
        
        return {
            "success": False,
            "error": f"Subtask {subtask_id} failed after {self.max_retries} retries"
        }
    
    async def select_agent(self, subtask: Dict[str, Any]) -> Optional[BaseAgent]:
        """Select best agent for subtask."""
        task_type = subtask.get("type")
        requirements = subtask.get("requirements", {})
        
        # Get capable agents
        capable_agents = [
            agent for agent in self.agent_registry.get_all_agents()
            if agent.can_handle(task_type, requirements)
            and agent.status != AgentStatus.ERROR
        ]
        
        if not capable_agents:
            return None
        
        # Select agent based on:
        # 1. Availability (idle > busy)
        # 2. Success rate
        # 3. Average execution time
        # 4. Current load
        
        best_agent = max(
            capable_agents,
            key=lambda a: (
                1 if a.status == AgentStatus.IDLE else 0.5,  # Prefer idle
                a.success_count / (a.task_count + 1),  # Success rate
                -a.get_metrics().get("average_duration_ms", 0)  # Faster is better
            )
        )
        
        return best_agent
    
    def _resolve_input_dependencies(
        self,
        input_data: Dict[str, Any],
        previous_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve {{subtask_id.result}} references in input."""
        resolved = {}
        
        for key, value in input_data.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Extract reference: {{subtask_id.result}}
                import re
                matches = re.findall(r'\{\{(\w+)\.(\w+)\}\}', value)
                
                if matches:
                    replacement = value
                    for subtask_id, field in matches:
                        if subtask_id in previous_results:
                            result = previous_results[subtask_id]
                            field_value = result.get(field, "")
                            replacement = replacement.replace(
                                f"{{{{{subtask_id}.{field}}}}}",
                                str(field_value)
                            )
                    resolved[key] = replacement
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    async def aggregate_results(
        self,
        results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate subtask results into final result."""
        successful = [r for r in results.values() if r.get("success")]
        failed = [r for r in results.values() if not r.get("success")]
        
        return {
            "total_subtasks": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": results,
            "final_result": (
                successful[-1].get("result") if successful else None
            )
        }
```

---

#### Step 2.2: Implement Task Decomposer ❌→✅

**Status:** NOT IMPLEMENTED (0%)

**Required Implementation:**

```python
# backend/app/core/task_decomposer.py

from typing import Dict, Any, List, Set, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Subtask:
    """Represents a decomposed subtask."""
    id: str
    type: str
    input: Dict[str, Any]
    requirements: Dict[str, Any]
    dependencies: Set[str]  # IDs of prerequisite subtasks

class TaskDecomposer:
    """Decomposes complex tasks into subtasks with dependencies."""
    
    def __init__(self):
        self.decomposition_strategies = {
            "compression_analysis": self._decompose_compression_analysis,
            "code_review": self._decompose_code_review,
            "data_pipeline": self._decompose_data_pipeline,
            # Add more strategies
        }
    
    async def decompose(
        self,
        task_type: str,
        task_input: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Set[str]]]:
        """
        Decompose task into subtasks.
        
        Returns:
            - List of subtask dictionaries
            - Dependency graph (subtask_id -> set of prerequisite IDs)
        """
        strategy = self.decomposition_strategies.get(task_type)
        
        if not strategy:
            # Default: single subtask
            subtask = Subtask(
                id=f"subtask_001",
                type=task_type,
                input=task_input,
                requirements={},
                dependencies=set()
            )
            return [self._subtask_to_dict(subtask)], {}
        
        subtasks = await strategy(task_input)
        
        # Build dependency graph
        dependency_graph = {
            subtask.id: subtask.dependencies
            for subtask in subtasks
        }
        
        # Convert to dictionaries
        subtask_dicts = [self._subtask_to_dict(st) for st in subtasks]
        
        return subtask_dicts, dependency_graph
    
    def _subtask_to_dict(self, subtask: Subtask) -> Dict[str, Any]:
        """Convert Subtask to dictionary."""
        return {
            "id": subtask.id,
            "type": subtask.type,
            "input": subtask.input,
            "requirements": subtask.requirements,
            "dependencies": list(subtask.dependencies)
        }
    
    async def _decompose_compression_analysis(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """Decompose compression analysis task."""
        subtasks = []
        
        # 1. Analyze content (NLP)
        subtasks.append(Subtask(
            id="analyze_content",
            type="text_analysis",
            input={"text": task_input.get("content", "")},
            requirements={},
            dependencies=set()
        ))
        
        # 2. Analyze content structure (NLP)
        subtasks.append(Subtask(
            id="analyze_structure",
            type="entity_extraction",
            input={"text": task_input.get("content", "")},
            requirements={},
            dependencies=set()
        ))
        
        # 3. Select algorithm (depends on analysis results)
        subtasks.append(Subtask(
            id="select_algorithm",
            type="algorithm_selection",
            input={
                "content_analysis": "{{analyze_content.result}}",
                "structure_analysis": "{{analyze_structure.result}}"
            },
            requirements={},
            dependencies={"analyze_content", "analyze_structure"}
        ))
        
        # 4. Perform compression (depends on algorithm selection)
        subtasks.append(Subtask(
            id="compress",
            type="compression",
            input={
                "content": task_input.get("content", ""),
                "algorithm": "{{select_algorithm.result.algorithm}}"
            },
            requirements={},
            dependencies={"select_algorithm"}
        ))
        
        return subtasks
    
    async def _decompose_code_review(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """Decompose code review task."""
        # Similar pattern - analyze, check patterns, generate review
        pass
    
    async def _decompose_data_pipeline(
        self,
        task_input: Dict[str, Any]
    ) -> List[Subtask]:
        """Decompose data pipeline task."""
        # Similar pattern - extract, transform, load
        pass
```

---

### PHASE 3: Meta-Learning Layer (Week 3-4)

#### Step 3.1: Complete Meta-Learner Agent ✅→✅

**Current Implementation:** `backend/app/agents/orchestrator/meta_learner_agent.py` (45% complete)

**Missing Methods/Features:**
1. ❌ `continuous_learning_loop()` - Background learning loop
2. ✅ `_analyze_performance()` - Implemented but needs enhancement
3. ❌ `_generate_hypotheses()` - Hypothesis generation
4. ❌ `_run_experiment()` - Experiment execution
5. ❌ `_validate_improvement()` - Improvement validation
6. ❌ `_deploy_optimization()` - **CRITICAL: Meta-recursive deployment**

**Implementation Steps:**

```python
# backend/app/agents/orchestrator/meta_learner_agent.py

class MetaLearnerAgent(BaseAgent):
    """Meta-Learner Agent - Autonomous system improvement."""
    
    # ADD THESE METHODS:
    
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
        """
        learning_interval = self.config.get("learning_interval_seconds", 3600)
        iteration = 0
        
        logger.info("Meta-learning loop started")
        
        while True:
            try:
                iteration += 1
                logger.info(f"Meta-learning iteration {iteration}")
                
                # Step 1: Analyze current performance
                performance_analysis = await self._analyze_performance()
                
                if not performance_analysis.get("optimization_opportunities"):
                    logger.info("No optimization opportunities found")
                    await asyncio.sleep(learning_interval)
                    continue
                
                # Step 2: Generate improvement hypotheses
                hypotheses = await self._generate_hypotheses(performance_analysis)
                
                # Step 3: Run experiments for each hypothesis
                for hypothesis in hypotheses.get("hypotheses", []):
                    experiment_result = await self._run_experiment(hypothesis)
                    
                    # Step 4: Validate improvement
                    if experiment_result.get("success"):
                        validation = await self._validate_improvement(experiment_result)
                        
                        # Step 5: Deploy if validated ⭐ META-RECURSION
                        if validation.get("validated"):
                            deployment_result = await self._deploy_optimization(validation)
                            logger.info(f"Optimization deployed: {deployment_result}")
                
                await asyncio.sleep(learning_interval)
                
            except Exception as e:
                logger.error(f"Meta-learning loop error: {e}")
                await asyncio.sleep(learning_interval)
    
    async def _generate_hypotheses(
        self,
        performance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate improvement hypotheses based on analysis."""
        opportunities = performance_analysis.get("optimization_opportunities", [])
        hypotheses = []
        
        for opp in opportunities:
            if opp.get("type") == "slow_execution":
                hypotheses.append({
                    "id": f"hyp_{len(hypotheses)+1}",
                    "type": "caching",
                    "description": f"Cache results for {opp.get('task_type')}",
                    "expected_improvement": "40% faster for cached tasks",
                    "implementation": "Add Redis caching layer"
                })
            
            elif opp.get("type") == "high_failure_rate":
                hypotheses.append({
                    "id": f"hyp_{len(hypotheses)+1}",
                    "type": "retry_strategy",
                    "description": f"Optimize retry for {opp.get('task_type')}",
                    "expected_improvement": "20% fewer failures",
                    "implementation": "Exponential backoff with jitter"
                })
        
        return {
            "hypotheses": hypotheses,
            "count": len(hypotheses),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _run_experiment(
        self,
        hypothesis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run experiment to test hypothesis."""
        hypothesis_id = hypothesis.get("id")
        hypothesis_type = hypothesis.get("type")
        
        logger.info(f"Running experiment: {hypothesis_id}")
        
        # Implement hypothesis temporarily
        # Measure baseline
        baseline_performance = await self._measure_baseline(hypothesis)
        
        # Apply hypothesis
        await self._apply_hypothesis(hypothesis)
        
        # Measure experiment performance
        experiment_performance = await self._measure_experiment(hypothesis)
        
        # Revert hypothesis
        await self._revert_hypothesis(hypothesis)
        
        # Calculate improvement
        improvement_pct = (
            (baseline_performance - experiment_performance) / baseline_performance * 100
            if baseline_performance > 0 else 0
        )
        
        return {
            "hypothesis_id": hypothesis_id,
            "success": True,
            "baseline_performance_ms": baseline_performance,
            "experiment_performance_ms": experiment_performance,
            "improvement_percent": improvement_pct,
            "meets_expectations": improvement_pct >= 20,  # Threshold
            "timestamp": datetime.now().isoformat()
        }
    
    async def _validate_improvement(
        self,
        experiment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that improvement is real and sustainable."""
        # Run multiple validation tests
        validation_passed = experiment_result.get("meets_expectations", False)
        
        # Check for side effects
        side_effects = await self._check_side_effects(experiment_result)
        
        # Verify improvement holds over multiple runs
        consistency = await self._check_consistency(experiment_result)
        
        validated = (
            validation_passed and
            not side_effects and
            consistency > 0.8
        )
        
        return {
            "validated": validated,
            "confidence": 0.85 if validated else 0.3,
            "recommendation": "deploy" if validated else "reject",
            "side_effects": side_effects,
            "consistency": consistency,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _deploy_optimization(
        self,
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy validated optimization.
        
        ⭐ THIS IS THE META-RECURSIVE STEP:
        System modifies its own code/configuration.
        """
        logger.info("Deploying optimization (META-RECURSIVE)")
        
        # Extract optimization details
        hypothesis = validation.get("hypothesis", {})
        optimization_type = hypothesis.get("type")
        
        deployment_result = {
            "deployed": False,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if optimization_type == "caching":
                # Update configuration to enable caching
                await self._update_config("enable_caching", True)
                
            elif optimization_type == "retry_strategy":
                # Update retry configuration
                await self._update_config("retry_strategy", "exponential_backoff")
                
            elif optimization_type == "parallelization":
                # Update max parallel tasks
                new_value = validation.get("recommended_value")
                await self._update_config("max_parallel_tasks", new_value)
            
            # Reload affected services
            await self._reload_services()
            
            deployment_result["deployed"] = True
            self.improvements_deployed += 1
            
            logger.info(f"Optimization deployed successfully (Total: {self.improvements_deployed})")
            
        except Exception as e:
            deployment_result["error"] = str(e)
            logger.error(f"Optimization deployment failed: {e}")
        
        return deployment_result
    
    async def _update_config(self, key: str, value: Any):
        """Update system configuration (meta-recursive)."""
        # Implementation depends on config storage
        # Could be database, file, environment variables
        logger.info(f"Updating config: {key} = {value}")
        # TODO: Implement actual config update
    
    async def _reload_services(self):
        """Reload services after config update."""
        logger.info("Reloading services after optimization deployment")
        # TODO: Implement service reload mechanism
```

---

### PHASE 4: Infrastructure Layer (Week 4-5)

#### Step 4.1: Implement Agent Registry ❌→✅

**Status:** NOT IMPLEMENTED (0%)

**Required Implementation:**

```python
# backend/app/core/agent_registry.py

from typing import Dict, List, Optional, Set
from app.core.base_agent import BaseAgent, AgentStatus, AgentCapability
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Global registry for all agents in the system.
    
    Provides:
    - Agent registration/unregistration
    - Capability-based agent lookup
    - Load balancing
    - Health monitoring
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, List[str]] = {}  # type -> [agent_ids]
        self.capability_index: Dict[str, List[str]] = {}  # capability -> [agent_ids]
        
        # Health tracking
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def register(self, agent: BaseAgent):
        """Register an agent with the registry."""
        async with self._lock:
            agent_id = agent.agent_id
            
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already registered, updating")
            
            self.agents[agent_id] = agent
            
            # Index by type
            agent_type = agent.agent_type
            if agent_type not in self.agent_types:
                self.agent_types[agent_type] = []
            if agent_id not in self.agent_types[agent_type]:
                self.agent_types[agent_type].append(agent_id)
            
            # Index by capability
            for capability in agent.capabilities:
                cap_value = capability.value
                if cap_value not in self.capability_index:
                    self.capability_index[cap_value] = []
                if agent_id not in self.capability_index[cap_value]:
                    self.capability_index[cap_value].append(agent_id)
            
            # Initialize health tracking
            self.agent_health[agent_id] = {
                "registered_at": datetime.now().isoformat(),
                "last_heartbeat": datetime.now().isoformat(),
                "status": agent.status.value
            }
            
            logger.info(f"Agent {agent_id} ({agent_type}) registered")
    
    async def unregister(self, agent_id: str):
        """Unregister an agent."""
        async with self._lock:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not in registry")
                return
            
            agent = self.agents[agent_id]
            
            # Remove from type index
            agent_type = agent.agent_type
            if agent_type in self.agent_types:
                self.agent_types[agent_type].remove(agent_id)
            
            # Remove from capability index
            for capability in agent.capabilities:
                cap_value = capability.value
                if cap_value in self.capability_index:
                    self.capability_index[cap_value].remove(agent_id)
            
            # Remove agent
            del self.agents[agent_id]
            del self.agent_health[agent_id]
            
            logger.info(f"Agent {agent_id} unregistered")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self.agents.values())
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get all agents of a specific type."""
        agent_ids = self.agent_types.get(agent_type, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Get all agents with a specific capability."""
        agent_ids = self.capability_index.get(capability.value, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    async def get_agent_for_task(
        self,
        task_type: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseAgent]:
        """
        Get best agent for a task.
        
        Selection criteria:
        1. Agent can handle task (capability match)
        2. Agent meets requirements (status, performance)
        3. Best performance (success rate, speed)
        4. Current load
        """
        # Find capable agents
        capable_agents = []
        for agent in self.agents.values():
            if agent.can_handle(task_type, requirements or {}):
                capable_agents.append(agent)
        
        if not capable_agents:
            logger.warning(f"No agents found for task type: {task_type}")
            return None
        
        # Filter by status (prefer idle, then working)
        idle_agents = [a for a in capable_agents if a.status == AgentStatus.IDLE]
        working_agents = [a for a in capable_agents if a.status == AgentStatus.WORKING]
        
        candidates = idle_agents if idle_agents else working_agents
        
        if not candidates:
            return None
        
        # Select best based on performance metrics
        best_agent = max(
            candidates,
            key=lambda a: self._calculate_agent_score(a)
        )
        
        return best_agent
    
    def _calculate_agent_score(self, agent: BaseAgent) -> float:
        """Calculate agent performance score for selection."""
        # Factors:
        # - Success rate (0-1)
        # - Average speed (inverse, normalized)
        # - Current load (inverse)
        
        success_rate = (
            agent.success_count / agent.task_count
            if agent.task_count > 0 else 0.5
        )
        
        metrics = agent.get_metrics()
        avg_duration = metrics.get("average_duration_ms", 1000)
        speed_score = 1.0 / (1.0 + avg_duration / 1000.0)  # Normalize
        
        load_score = 1.0 / (1.0 + agent.task_count / 100.0)  # Lower is better
        
        total_score = (
            success_rate * 0.5 +
            speed_score * 0.3 +
            load_score * 0.2
        )
        
        return total_score
    
    async def update_health(self, agent_id: str, health_data: Dict[str, Any]):
        """Update agent health information."""
        if agent_id in self.agent_health:
            self.agent_health[agent_id].update({
                "last_heartbeat": datetime.now().isoformat(),
                **health_data
            })
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status summary."""
        return {
            "total_agents": len(self.agents),
            "agents_by_type": {
                agent_type: len(agent_ids)
                for agent_type, agent_ids in self.agent_types.items()
            },
            "agents_by_capability": {
                capability: len(agent_ids)
                for capability, agent_ids in self.capability_index.items()
            },
            "health_summary": {
                agent_id: {
                    "status": agent.status.value,
                    "last_heartbeat": health.get("last_heartbeat")
                }
                for agent_id, agent in self.agents.items()
                for health in [self.agent_health.get(agent_id, {})]
            }
        }

# Global singleton
_agent_registry: Optional[AgentRegistry] = None

def get_agent_registry() -> AgentRegistry:
    """Get global agent registry singleton."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry
```

---

## 📋 COMPLETE IMPLEMENTATION CHECKLIST

### Critical Path Items (Must Complete)

- [ ] **1. Complete BaseAgent enhancements** (heartbeat, shutdown, can_handle improvements)
- [ ] **2. Implement all 4 Specialist Agents** (NLP, Code, Data, Research) with full task support
- [ ] **3. Complete Orchestrator Agent** (task decomposition, coordination, aggregation)
- [ ] **4. Implement TaskDecomposer** (decomposition strategies, dependency graph)
- [ ] **5. Complete Meta-Learner Agent** (learning loop, hypothesis generation, deployment)
- [ ] **6. Implement AgentRegistry** (registration, discovery, load balancing)
- [ ] **7. Implement Communication Protocol** (enhance existing, add event broadcasting)
- [ ] **8. Implement Meta-Recursive Deployment** (system modifies itself)

### High Priority Items

- [ ] **9. Agent Discovery Mechanism** (dynamic agent registration, capability announcement)
- [ ] **10. Load Balancing Algorithm** (task distribution, queue management)
- [ ] **11. Retry and Timeout Handling** (exponential backoff, circuit breakers)
- [ ] **12. Health Monitoring** (heartbeat system, health checks, auto-recovery)
- [ ] **13. Performance Metrics Collection** (detailed metrics, aggregation, reporting)
- [ ] **14. Task Result Aggregation** (merging subtask results, error handling)

### Medium Priority Items

- [ ] **15. Agent Communication Events** (task started, completed, failed events)
- [ ] **16. Dependency Resolution** (automatic dependency detection, resolution)
- [ ] **17. Task Priority Queue** (priority-based scheduling)
- [ ] **18. Agent Scaling** (dynamic agent creation, resource management)
- [ ] **19. Experiment Framework** (A/B testing, feature flags)
- [ ] **20. Configuration Management** (runtime config updates, validation)

### Testing Requirements

- [ ] **21. Unit Tests** (all agent classes, >90% coverage)
- [ ] **22. Integration Tests** (multi-agent workflows, orchestration)
- [ ] **23. E2E Tests** (complete task execution, meta-learning loop)
- [ ] **24. Performance Tests** (load testing, scalability)
- [ ] **25. Bootstrap Tests** (fail-pass validation for all agents)

---

## 🚀 IMPLEMENTATION PRIORITY ORDER

### Week 1: Foundation
1. Complete BaseAgent (heartbeat, shutdown, can_handle)
2. Implement AgentRegistry
3. Complete 4 Specialist Agents (basic functionality)

### Week 2: Orchestration
4. Implement TaskDecomposer
5. Complete Orchestrator Agent
6. Implement task coordination logic

### Week 3: Meta-Learning
7. Complete Meta-Learner Agent
8. Implement continuous learning loop
9. Implement meta-recursive deployment

### Week 4: Integration & Testing
10. Integrate all components
11. Implement communication protocol enhancements
12. Add comprehensive tests

### Week 5: Polish & Documentation
13. Performance optimization
14. Error handling improvements
15. Complete documentation

---

## ✅ SUCCESS CRITERIA

**Agent Framework is Complete When:**

1. ✅ All agents can register and be discovered
2. ✅ Orchestrator can decompose and coordinate complex tasks
3. ✅ Meta-learner runs continuous improvement loop
4. ✅ System successfully modifies itself (meta-recursion proven)
5. ✅ All tests pass (>90% coverage)
6. ✅ Documentation complete
7. ✅ Performance meets requirements (tasks execute in parallel, <5s response time)

---

**Document Status:** ✅ COMPLETE  
**Next Steps:** Begin Phase 1 implementation  
**Estimated Completion:** 4-5 weeks
