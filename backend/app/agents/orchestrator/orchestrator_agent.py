"""
Orchestrator Agent (Agent 06): Coordinates all agents and tasks.

Manages:
- Task routing to appropriate agents
- Agent lifecycle monitoring
- Meta-learning coordination
- System health aggregation
"""

from typing import Dict, Any, Optional, List, Set, Tuple
import asyncio
import logging
from datetime import datetime

from app.core.base_agent import BaseAgent, BootstrapResult, AgentCapability, AgentStatus
from app.core.agent_registry import get_agent_registry
from app.core.task_decomposer import get_task_decomposer
from app.core.message_bus import get_message_bus
from app.models.messaging import (
    TaskEnvelope, TaskResultEnvelope, AgentEventEnvelope, MetricEnvelope,
    create_task_result_envelope, create_metric_envelope
)

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator for the meta-recursive system.
    
    Responsibilities:
    - Route tasks to appropriate agents
    - Monitor agent health and status
    - Coordinate meta-learning cycles
    - Aggregate system metrics
    - Manage task queues and dependencies
    """
    
    def __init__(
        self,
        agent_registry=None,  # Optional, will use singleton if None
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(agent_id=agent_id or "orchestrator_001", agent_type="orchestrator", config=config)
        self.capabilities = [
            AgentCapability.ORCHESTRATION,
            AgentCapability.MONITORING,
            AgentCapability.LEARNING
        ]
        
        # Agent registry (use provided or get singleton)
        self.agent_registry = agent_registry or get_agent_registry()
        
        # Task decomposer
        self.task_decomposer = get_task_decomposer()
        
        # Agent metadata (for backward compatibility with message bus pattern)
        self.agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> metadata
        
        # Task routing table
        self.task_routes: Dict[str, str] = {  # task_type -> agent_type
            "compress": "core_engine",
            "decompress": "core_engine",
            "analyze": "core_engine",
            "optimize": "core_engine",
            "compression_analysis": "orchestrator",  # Decompose this
            "code_review": "orchestrator",  # Decompose this
            "data_pipeline": "orchestrator",  # Decompose this
            "check_ollama": "infrastructure",
            "noop": "infrastructure"  # For testing
        }
        
        # Message bus
        self.bus = get_message_bus()
        
        # Configuration
        self.max_parallel_tasks = config.get("max_parallel_tasks", 10) if config else 10
        self.task_timeout_seconds = config.get("task_timeout_seconds", 300) if config else 300
        self.max_retries = config.get("max_retries", 3) if config else 3
        
        # Task tracking
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
        
        # Metrics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
    
    async def bootstrap_and_validate(self) -> BootstrapResult:
        result = BootstrapResult()
        
        # Validate agent registry
        try:
            if self.agent_registry:
                agent_count = len(self.agent_registry.get_all_agents())
                result.add_validation("agent_registry", True, f"Registry has {agent_count} agents")
            else:
                result.add_validation("agent_registry", False, "Agent registry not available")
        except Exception as e:
            result.add_validation("agent_registry", False, f"Registry error: {e}")
        
        # Validate task decomposer
        try:
            if self.task_decomposer:
                # Test decomposition
                test_subtasks, test_graph = await self.task_decomposer.decompose("noop", {})
                result.add_validation("task_decomposer", True, "Task decomposer functional")
            else:
                result.add_validation("task_decomposer", False, "Task decomposer not initialized")
        except Exception as e:
            result.add_validation("task_decomposer", False, f"Decomposer error: {e}")
        
        # Validate message bus
        try:
            topics = self.bus.list_topics()
            result.add_validation("message_bus", True, f"Topics available: {topics}")
        except Exception as e:
            result.add_validation("message_bus", False, f"Message bus error: {e}")
        
        # Subscribe to topics
        try:
            await self._setup_subscriptions()
            result.add_validation("subscriptions", True, "Subscriptions set up")
        except Exception as e:
            result.add_validation("subscriptions", False, f"Subscription error: {e}")
        
        # Self-test (route a test task)
        try:
            test_result = await self._route_task_internal("test-task", "noop", {})
            if test_result.get("status") == "completed":
                result.add_validation("self_test", True, "Internal routing works")
            else:
                result.add_validation("self_test", False, f"Internal routing failed: {test_result}")
        except Exception as e:
            result.add_validation("self_test", False, f"Self-test error: {e}")
        
        if all(result.validations.values()):
            result.success = True
            self.status = AgentStatus.IDLE
        else:
            result.success = False
            self.status = AgentStatus.ERROR
        
        return result
    
    async def _setup_subscriptions(self):
        """Set up message bus subscriptions."""
        # Task submissions
        self.bus.subscribe("tasks.submit", self._handle_task_submit)
        
        # Task results
        self.bus.subscribe("tasks.result", self._handle_task_result)
        
        # Agent events
        self.bus.subscribe("agents.event", self._handle_agent_event)
        
        # Metrics
        self.bus.subscribe("metrics.update", self._handle_metric_update)
        
        # Meta-learning
        self.bus.subscribe("meta.hypothesis", self._handle_hypothesis)
    
    async def _handle_task_submit(self, envelope: TaskEnvelope):
        """Handle incoming task submissions."""
        logger.info(f"Received task: {envelope.task_id} ({envelope.task_type})")
        
        try:
            result = await self._route_task_internal(
                envelope.task_id,
                envelope.task_type,
                envelope.parameters
            )
            
            # Publish result if reply topic specified
            if envelope.reply_topic:
                result_envelope = create_task_result_envelope(
                    task_id=envelope.task_id,
                    status=result.get("status", "unknown"),
                    result=result.get("result"),
                    error=result.get("error"),
                    metrics=result.get("metrics", {})
                )
                await self.bus.publish(envelope.reply_topic, result_envelope)
            
            self.tasks_routed += 1
            
        except Exception as e:
            logger.error(f"Task routing error for {envelope.task_id}: {e}")
            self.tasks_failed += 1
    
    async def _handle_task_result(self, envelope: TaskResultEnvelope):
        """Handle task completion results."""
        logger.info(f"Task completed: {envelope.task_id} ({envelope.status})")
        
        if envelope.status == "completed":
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        
        # Could trigger meta-learning analysis here
    
    async def _handle_agent_event(self, envelope: AgentEventEnvelope):
        """Handle agent lifecycle events."""
        logger.info(f"Agent event: {envelope.agent_id} ({envelope.event_type})")
        
        # Update agent registry
        if envelope.event_type == "initialized":
            self.agents[envelope.agent_id] = {
                "agent_type": envelope.agent_type,
                "status": envelope.status,
                "last_seen": envelope.timestamp
            }
        elif envelope.event_type in ["shutdown", "error"]:
            if envelope.agent_id in self.agents:
                self.agents[envelope.agent_id]["status"] = envelope.status
                self.agents[envelope.agent_id]["last_seen"] = envelope.timestamp
    
    async def _handle_metric_update(self, envelope: MetricEnvelope):
        """Handle metrics updates."""
        logger.debug(f"Metric: {envelope.metric_name} = {envelope.value}")
        
        # Aggregate metrics (could publish system health)
    
    async def _handle_hypothesis(self, envelope):
        """Handle meta-learning hypotheses."""
        logger.info(f"Hypothesis received: {envelope.hypothesis_id}")
        
        # Could trigger experiment execution
    
    async def _route_task_internal(self, task_id: str, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate agent (internal implementation)."""
        target_agent_type = self.task_routes.get(task_type)
        
        if not target_agent_type:
            return {
                "status": "failed",
                "error": f"No route for task_type: {task_type}"
            }
        
        # Find agent of target type
        target_agent = None
        for agent_id, metadata in self.agents.items():
            if metadata["agent_type"] == target_agent_type and metadata["status"] == "idle":
                target_agent = agent_id
                break
        
        if not target_agent:
            return {
                "status": "failed",
                "error": f"No available agent for type: {target_agent_type}"
            }
        
        # For now, simulate execution (in real impl, send to agent's queue)
        logger.info(f"Routing {task_id} to {target_agent}")
        
        # Simulate task execution (replace with real agent call)
        if task_type == "noop":
            return {"status": "completed", "result": {"ok": True}}
        elif task_type == "compress":
            # Would call compression engine
            return {"status": "completed", "result": {"compressed": True}}
        else:
            return {"status": "completed", "result": {"simulated": True}}
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestration tasks.
        
        Supports:
        - Simple task routing (existing pattern)
        - Complex task decomposition and orchestration (new pattern)
        """
        task_id = task.get("task_id", f"orch_{datetime.now().timestamp()}")
        task_type = task.get("operation") or task.get("task_type", "")
        task_input = task.get("parameters", {})
        
        # Handle simple status queries
        if task_type == "get_agent_status":
            return {
                "status": "completed",
                "result": {
                    "agents": self.agents,
                    "tasks_routed": self.tasks_routed,
                    "tasks_completed": self.tasks_completed
                }
            }
        
        # Check if task should be decomposed
        should_decompose = task_type in self.task_decomposer.decomposition_strategies
        
        if should_decompose:
            # Complex task: decompose and orchestrate
            return await self._orchestrate_complex_task(task_id, task_type, task_input)
        else:
            # Simple task: route directly
            if task_type == "route_task":
                sub_task_id = task.get("task_id")
                sub_task_type = task.get("parameters", {}).get("task_type")
                sub_params = task.get("parameters", {}).get("parameters", {})
                
                if sub_task_id and sub_task_type:
                    return await self._route_task_internal(sub_task_id, sub_task_type, sub_params)
            
            # Fallback to simple routing
            return await self._route_task_internal(task_id, task_type, task_input)
    
    async def _orchestrate_complex_task(
        self,
        task_id: str,
        task_type: str,
        task_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate complex task with decomposition.
        
        Steps:
        1. Decompose task into subtasks
        2. Execute subtasks in parallel (respecting dependencies)
        3. Aggregate results
        4. Return final result
        """
        try:
            self.status = AgentStatus.WORKING
            start_time = datetime.now()
            
            # Step 1: Decompose task into subtasks
            subtasks, dependency_graph = await self.decompose_task(task_type, task_input)
            
            # Step 2: Execute subtasks in parallel (respecting dependencies)
            results = await self.coordinate_execution(task_id, subtasks, dependency_graph)
            
            # Step 3: Aggregate results
            final_result = await self.aggregate_results(results)
            
            # Step 4: Update task history
            duration = (datetime.now() - start_time).total_seconds()
            self.task_history.append({
                "task_id": task_id,
                "type": task_type,
                "subtask_count": len(subtasks),
                "duration_seconds": duration,
                "success": final_result.get("status") != "failed",
                "timestamp": datetime.now().isoformat()
            })
            
            self.status = AgentStatus.IDLE
            self.task_count += 1
            if final_result.get("status") != "failed":
                self.success_count += 1
            else:
                self.error_count += 1
            
            return {
                "task_id": task_id,
                "status": final_result.get("status", "completed"),
                "result": final_result.get("aggregated_result"),
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
                "task_id": task_id,
                "status": "failed",
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
        """
        Group subtasks into dependency generations using topological sort.
        
        Returns:
            List of generations, where each generation can execute in parallel
        """
        # Use TaskDecomposer's topological sort
        generations = self.task_decomposer.get_parallel_tasks(dependency_graph)
        
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
        """Resolve {{subtask_id.result.path}} references in input."""
        resolved = {}
        
        for key, value in input_data.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Extract reference
                ref_match = value.split("{{")[1].split("}}")[0].strip()
                parts = ref_match.split(".")
                
                if len(parts) >= 2:
                    subtask_id = parts[0]
                    # The path starts after subtask_id (e.g., "result.value" or "result.algorithm")
                    path_parts = parts[1:]
                    
                    # Get result from previous subtask
                    if subtask_id in previous_results:
                        subtask_result = previous_results[subtask_id].get("result", {})
                        
                        # Navigate path (e.g., "result.value" -> navigate to result["value"])
                        # But if path starts with "result", skip it since we already have result
                        resolved_value = subtask_result
                        path_to_follow = path_parts
                        
                        # If path starts with "result", skip it
                        if path_to_follow and path_to_follow[0] == "result":
                            path_to_follow = path_to_follow[1:]
                        
                        # Navigate through the path
                        for path_part in path_to_follow:
                            if isinstance(resolved_value, dict):
                                resolved_value = resolved_value.get(path_part)
                            else:
                                resolved_value = None
                                break
                        
                        resolved[key] = resolved_value if resolved_value is not None else value
                    else:
                        resolved[key] = value  # Keep original if reference not found
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
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
    
    async def self_evaluate(self) -> Dict[str, Any]:
        """Evaluate orchestration performance."""
        metrics = await self.report_metrics()
        
        success_rate = metrics.get("task_success_rate", 0.0)
        if self.task_count > 0:
            success_rate = self.success_count / self.task_count
        
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
        if len(self.agent_registry.get_all_agents()) == 0:
            weaknesses.append("No agents registered")
        
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
    
    async def report_metrics(self) -> Dict[str, Any]:
        """Report orchestration metrics."""
        total_tasks = self.tasks_routed
        success_rate = (self.tasks_completed / total_tasks) if total_tasks > 0 else 0.0
        
        return {
            "agent_id": self.agent_id,
            "agent_type": "orchestrator",
            "registered_agents": len(self.agents),
            "tasks_routed": self.tasks_routed,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "task_success_rate": success_rate,
            "active_topics": self.bus.list_topics(),
            "uptime_seconds": (asyncio.get_event_loop().time() - getattr(self, '_start_time', asyncio.get_event_loop().time()))
        }

