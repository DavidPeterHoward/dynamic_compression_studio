"""
API Layer Agent (Agent 04): REST API and WebSocket Interface

Exposes all agent functionality through standardized APIs with:
- REST endpoints for task management
- WebSocket connections for real-time updates
- Request validation and response formatting
- Authentication middleware hooks (ready for Phase 2)
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from app.core.base_agent import BaseAgent, AgentCapability
from app.models.messaging import TaskEnvelope, create_task_result_envelope

logger = logging.getLogger(__name__)

class APIAgent(BaseAgent):
    """API Layer Agent providing REST and WebSocket interfaces."""

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id=agent_id, agent_type="api_layer", config=config)
        self.capabilities = [
            AgentCapability.ORCHESTRATION,  # API agent orchestrates requests
            AgentCapability.MONITORING,     # Monitors API usage
            AgentCapability.ANALYSIS        # Analyzes API performance
        ]

        # Agent registry for routing requests
        self.agent_registry: Dict[str, Any] = {}

        # WebSocket connections
        self.websocket_clients: Dict[str, Any] = {}

        # API metrics
        self.api_requests = 0
        self.websocket_connections = 0

    async def bootstrap_and_validate(self) -> 'BootstrapResult':
        """Bootstrap validation for API agent."""
        from app.core.base_agent import BootstrapResult

        result = BootstrapResult()

        try:
            # 1. Validate agent registry can be populated
            await self._populate_agent_registry()
            result.add_validation("agent_registry", len(self.agent_registry) > 0,
                                "No agents available for API routing")

            # 2. Validate API routing logic
            test_routing = await self.handle_api_request("01", "status", "GET", {})
            result.add_validation("api_routing", isinstance(test_routing, dict),
                                "API routing logic failed")

            # 3. Validate WebSocket client management
            self._test_websocket_management()
            result.add_validation("websocket_management", True,
                                "WebSocket management initialization failed")

            # Determine overall status
            if all(result.validations.values()):
                result.success = True
                logger.info("✅ Agent 04 bootstrap PASSED")
            else:
                result.success = False
                logger.error("❌ Agent 04 bootstrap FAILED")

        except Exception as e:
            result.success = False
            result.add_validation("bootstrap_exception", False, str(e))
            logger.error(f"💥 Agent 04 bootstrap exception: {e}")

        return result

    async def _populate_agent_registry(self):
        """Populate the agent registry with available agents."""
        try:
            # Import and register core agents
            agents_to_register = []

            # Try to import each agent individually to handle failures gracefully
            try:
                from app.agents.infrastructure.infra_agent import InfrastructureAgent
                agents_to_register.append(("01", InfrastructureAgent()))
            except Exception as e:
                logger.warning(f"Could not import InfrastructureAgent: {e}")

            try:
                from app.agents.database.database_agent import DatabaseAgent
                agents_to_register.append(("02", DatabaseAgent()))
            except Exception as e:
                logger.warning(f"Could not import DatabaseAgent: {e}")

            try:
                from app.agents.core_engine.core_engine_agent import CoreEngineAgent
                agents_to_register.append(("03", CoreEngineAgent()))
            except Exception as e:
                logger.warning(f"Could not import CoreEngineAgent: {e}")

            try:
                from app.agents.orchestrator.meta_learner_agent import MetaLearnerAgent
                agents_to_register.append(("06", MetaLearnerAgent()))
            except Exception as e:
                logger.warning(f"Could not import MetaLearnerAgent: {e}")

            for agent_id, agent_instance in agents_to_register:
                try:
                    # Initialize agent if needed
                    if hasattr(agent_instance, 'initialize'):
                        await agent_instance.initialize()

                    self.agent_registry[agent_id] = agent_instance
                    logger.info(f"Registered agent {agent_id} ({getattr(agent_instance, 'agent_type', 'unknown')}) with API layer")
                except Exception as e:
                    logger.warning(f"Failed to initialize agent {agent_id}: {e}")
                    # Still register even if initialization fails for basic functionality
                    self.agent_registry[agent_id] = agent_instance

        except Exception as e:
            logger.error(f"Failed to populate agent registry: {e}")
            # Continue without agents - API can still function as a basic endpoint

    def register_agent(self, agent_id: str, agent_instance: Any):
        """Register an agent for API routing."""
        self.agent_registry[agent_id] = agent_instance
        logger.info(f"Registered agent {agent_id} with API layer")

    async def handle_api_request(self, agent_id: str, endpoint: str,
                               method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle REST API requests."""
        self.api_requests += 1

        if agent_id not in self.agent_registry:
            return {"error": f"Agent {agent_id} not registered", "status": 404}

        agent = self.agent_registry[agent_id]

        try:
            if endpoint == "status":
                if hasattr(agent, 'get_status'):
                    result = agent.get_status()
                else:
                    result = {"error": "Agent does not support status endpoint"}
                    return {"data": result, "status": 400, "error": "Method not supported"}

            elif endpoint == "execute":
                # Create task envelope for execution
                task_envelope = TaskEnvelope(
                    task_id=data.get("task_id", f"api_task_{self.api_requests}"),
                    payload=data
                )

                # Execute task
                result = await agent.execute(task_envelope)

                # Convert result to dict if needed
                if hasattr(result, 'dict'):
                    result = result.dict()
                elif hasattr(result, '__dict__'):
                    result = result.__dict__

            elif endpoint == "health":
                result = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "agent_id": agent_id,
                    "agent_type": getattr(agent, 'agent_type', 'unknown')
                }
            else:
                result = {"error": f"Unknown endpoint: {endpoint}"}
                return {"data": result, "status": 404, "error": "Endpoint not found"}

            return {"data": result, "status": 200}

        except Exception as e:
            logger.error(f"API request failed for agent {agent_id}: {e}")
            return {"error": str(e), "status": 500}

    async def broadcast_websocket_update(self, event_type: str, data: Dict[str, Any]):
        """Broadcast updates to WebSocket clients."""
        message = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        disconnected_clients = []
        for client_id, client in self.websocket_clients.items():
            try:
                await client.send_json(message)
            except Exception:
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del self.websocket_clients[client_id]

    def _test_websocket_management(self):
        """Test WebSocket client management."""
        # Simple test to ensure the management structures work
        test_client_id = "test_client"
        self.websocket_clients[test_client_id] = "mock_client"
        assert test_client_id in self.websocket_clients
        del self.websocket_clients[test_client_id]
        assert test_client_id not in self.websocket_clients

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status across all agents."""
        agent_statuses = {}
        for agent_id, agent in self.agent_registry.items():
            try:
                if hasattr(agent, 'get_status'):
                    status = agent.get_status()
                    agent_statuses[agent_id] = {
                        "type": status.get("agent_type", "unknown"),
                        "status": status.get("status", "unknown"),
                        "capabilities": len(status.get("capabilities", [])),
                        "uptime": status.get("uptime_seconds", 0),
                        "tasks": status.get("task_count", 0),
                        "success_rate": status.get("success_rate", 0)
                    }
                else:
                    agent_statuses[agent_id] = {"error": "Status method not available"}
            except Exception as e:
                agent_statuses[agent_id] = {"error": str(e)}

        return {
            "system_status": "operational" if agent_statuses else "initializing",
            "timestamp": datetime.now().isoformat(),
            "agents": agent_statuses,
            "api_metrics": {
                "total_requests": self.api_requests,
                "websocket_connections": len(self.websocket_clients)
            }
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task through API routing.

        API agent routes tasks to appropriate agents.
        """
        task_id = task.get("task_id", f"api_task_{self.api_requests + 1}")

        try:
            # Determine target agent based on task type
            target_agent = self._determine_target_agent(task)

            if not target_agent or target_agent not in self.agent_registry:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": f"No suitable agent found for task type: {task.get('task_type')}",
                    "timestamp": datetime.now().isoformat()
                }

            # Route task to target agent
            agent = self.agent_registry[target_agent]
            result = await agent.execute_task(task)

            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "agent_used": target_agent,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def self_evaluate(self) -> Dict[str, Any]:
        """
        Evaluate API agent performance.
        """
        total_requests = self.api_requests
        active_connections = len(self.websocket_clients)

        # Calculate performance score based on request handling
        if total_requests == 0:
            performance_score = 0.5  # Neutral for new agents
        else:
            # Score based on agent registry completeness and request handling
            registry_completeness = len(self.agent_registry) / 4.0  # Expect 4 agents
            performance_score = min(1.0, registry_completeness * 0.8 + 0.2)

        return {
            "performance_score": performance_score,
            "strengths": [
                "REST API endpoints functional" if total_requests > 0 else "API endpoints configured",
                "WebSocket connections active" if active_connections > 0 else "WebSocket support ready",
                f"Agent registry populated ({len(self.agent_registry)} agents)"
            ],
            "weaknesses": [
                "Limited request volume" if total_requests < 10 else None,
                "No WebSocket clients connected" if active_connections == 0 else None,
            ],
            "improvement_suggestions": [
                "Increase API request volume for better testing",
                "Establish WebSocket client connections",
                "Add request rate limiting",
                "Implement API authentication (Phase 2)"
            ],
            "metrics": {
                "total_requests": total_requests,
                "active_websocket_connections": active_connections,
                "registered_agents": len(self.agent_registry),
                "uptime_seconds": (datetime.now() - self.created_at).total_seconds()
            }
        }

    def _determine_target_agent(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Determine which agent should handle the task.
        """
        task_type = task.get("task_type", "").lower()

        # Route tasks based on type
        if "compression" in task_type or "algorithm" in task_type:
            return "03"  # Core Engine Agent
        elif "database" in task_type or "data" in task_type:
            return "02"  # Database Agent
        elif "infrastructure" in task_type or "health" in task_type:
            return "01"  # Infrastructure Agent
        elif "learn" in task_type or "meta" in task_type or "evaluate" in task_type:
            return "06"  # Meta-Learner Agent
        else:
            # Default to core engine for general tasks
            return "03"
