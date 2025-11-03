"""
Agent Communication Layer

Enhanced inter-agent communication system built on the message bus.
Provides high-level communication patterns for agent collaboration.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime

from app.core.message_bus import get_message_bus

logger = logging.getLogger(__name__)

class AgentCommunicationManager:
    """High-level communication manager for inter-agent collaboration."""

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.message_bus = get_message_bus()
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.event_listeners: Dict[str, List[Callable]] = {}
        self._running = False
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        """Set up message bus subscriptions."""
        self.message_bus.subscribe(f"tasks.{self.agent_id}", self._handle_task_request)
        self.message_bus.subscribe(f"tasks.{self.agent_id}.result", self._handle_task_result)
        self.message_bus.subscribe("agents.event", self._handle_agent_event)

    async def start(self):
        """Start the communication manager."""
        self._running = True
        logger.info(f"Agent {self.agent_id} communication manager started")

    async def stop(self):
        """Stop the communication manager."""
        self._running = False
        logger.info(f"Agent {self.agent_id} communication manager stopped")

    def register_task_handler(self, task_type: str, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]):
        """Register a handler for a specific task type."""
        self.task_handlers[task_type] = handler
        logger.info(f"Agent {self.agent_id} registered handler for task type: {task_type}")

    async def delegate_task(self, target_agent: str, task_type: str, parameters: Dict[str, Any], priority: int = 1, timeout: float = 30.0) -> Dict[str, Any]:
        """Delegate a task to another agent."""
        task_id = f"{self.agent_id}_{int(asyncio.get_event_loop().time() * 1000)}"
        future = asyncio.Future()
        self.pending_requests[task_id] = future

        envelope = {
            "message_id": task_id,
            "task_id": task_id,
            "task_type": task_type,
            "parameters": parameters,
            "priority": priority,
            "reply_topic": f"tasks.{self.agent_id}.result"
        }

        await self.message_bus.publish(f"tasks.{target_agent}", envelope)

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            if task_id in self.pending_requests:
                del self.pending_requests[task_id]
            return {"task_id": task_id, "status": "timeout", "error": f"Task delegation to {target_agent} timed out"}
        except Exception as e:
            if task_id in self.pending_requests:
                del self.pending_requests[task_id]
            return {"task_id": task_id, "status": "error", "error": str(e)}

    async def _handle_task_request(self, envelope: Dict[str, Any]):
        """Handle incoming task request."""
        task_type = envelope.get("task_type")
        if task_type not in self.task_handlers:
            error_result = {
                "task_id": envelope.get("task_id"),
                "status": "failed",
                "error": f"Agent {self.agent_id} does not support task type: {task_type}"
            }
            await self.message_bus.publish(envelope.get("reply_topic", f"tasks.{envelope.get('message_id')}.result"), error_result)
            return

        try:
            handler = self.task_handlers[task_type]
            result = await handler(envelope.get("parameters", {}))

            success_result = {
                "task_id": envelope.get("task_id"),
                "status": "completed",
                "result": result,
                "metrics": {"execution_time": 0.1}
            }
            await self.message_bus.publish(envelope.get("reply_topic", f"tasks.{envelope.get('message_id')}.result"), success_result)
        except Exception as e:
            error_result = {
                "task_id": envelope.get("task_id"),
                "status": "failed",
                "error": f"Task execution failed: {e}"
            }
            await self.message_bus.publish(envelope.get("reply_topic", f"tasks.{envelope.get('message_id')}.result"), error_result)
            logger.error(f"Task execution failed for {envelope.get('task_id')}: {e}")

    async def _handle_task_result(self, envelope: Dict[str, Any]):
        """Handle incoming task result."""
        task_id = envelope.get("task_id")
        if task_id in self.pending_requests:
            future = self.pending_requests[task_id]
            del self.pending_requests[task_id]
            future.set_result(envelope)

    async def _handle_agent_event(self, envelope: Dict[str, Any]):
        """Handle agent event notifications."""
        logger.debug(f"Agent {self.agent_id} received event: {envelope}")

    def get_pending_request_count(self) -> int:
        """Get count of pending requests."""
        return len(self.pending_requests)

    def get_active_connections(self) -> int:
        """Get count of active agent connections."""
        return len([r for r in self.pending_requests.values() if not r.done()])

_communication_managers: Dict[str, AgentCommunicationManager] = {}

def get_communication_manager(agent_id: str, agent_type: str = "unknown") -> AgentCommunicationManager:
    """Get or create communication manager for an agent."""
    if agent_id not in _communication_managers:
        _communication_managers[agent_id] = AgentCommunicationManager(agent_id, agent_type)
    return _communication_managers[agent_id]
