"""
Orchestrator Agent (Agent 06): Coordinates all agents and tasks.

Manages:
- Task routing to appropriate agents
- Agent lifecycle monitoring
- Meta-learning coordination
- System health aggregation
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging

from app.core.base_agent import BaseAgent, BootstrapResult, AgentCapability
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
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(agent_id=agent_id, agent_type="orchestrator", config=config)
        self.capabilities = [
            AgentCapability.ORCHESTRATION,
            AgentCapability.MONITORING,
            AgentCapability.LEARNING
        ]
        
        # Agent registry
        self.agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> metadata
        
        # Task routing table
        self.task_routes: Dict[str, str] = {  # task_type -> agent_type
            "compress": "core_engine",
            "decompress": "core_engine",
            "analyze": "core_engine",
            "optimize": "core_engine",
            "check_ollama": "infrastructure",
            "noop": "infrastructure"  # For testing
        }
        
        # Message bus
        self.bus = get_message_bus()
        
        # Metrics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
    
    async def bootstrap_and_validate(self) -> BootstrapResult:
        result = BootstrapResult()
        
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
            # We'll test by sending a task to ourselves (meta!)
            test_result = await self._route_task_internal("test-task", "noop", {})
            if test_result.get("status") == "completed":
                result.add_validation("self_test", True, "Internal routing works")
            else:
                result.add_validation("self_test", False, f"Internal routing failed: {test_result}")
        except Exception as e:
            result.add_validation("self_test", False, f"Self-test error: {e}")
        
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
        """Execute orchestration tasks."""
        task_type = task.get("task_type")
        
        if task_type == "get_agent_status":
            return {
                "status": "completed",
                "result": {
                    "agents": self.agents,
                    "tasks_routed": self.tasks_routed,
                    "tasks_completed": self.tasks_completed
                }
            }
        
        if task_type == "route_task":
            # Manual task routing
            sub_task_id = task.get("task_id")
            sub_task_type = task.get("parameters", {}).get("task_type")
            sub_params = task.get("parameters", {}).get("parameters", {})
            
            if sub_task_id and sub_task_type:
                return await self._route_task_internal(sub_task_id, sub_task_type, sub_params)
        
        return {
            "status": "failed",
            "error": f"Unknown orchestration task: {task_type}"
        }
    
    async def self_evaluate(self) -> Dict[str, Any]:
        """Evaluate orchestration performance."""
        metrics = await self.report_metrics()
        
        success_rate = metrics.get("task_success_rate", 0.0)
        
        strengths = []
        weaknesses = []
        if success_rate > 0.95:
            strengths.append("High task routing success")
        if len(self.agents) > 0:
            strengths.append("Agent registry populated")
        else:
            weaknesses.append("No agents registered")
        
        if self.tasks_failed > 10:
            weaknesses.append("High task failure rate")
        
        return {
            "agent_id": self.agent_id,
            "performance_score": success_rate,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": [
                "Add load balancing across agents",
                "Implement task dependency resolution",
                "Add circuit breaker for failed agents"
            ],
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

