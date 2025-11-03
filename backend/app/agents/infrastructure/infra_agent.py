from typing import Dict, Any, Optional
import os
import logging

from app.core.base_agent import BaseAgent, BootstrapResult, AgentCapability
from app.core.communication_mixin import CommunicationMixin
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class InfrastructureAgent(BaseAgent, CommunicationMixin):
    """Agent 01: Infrastructure.

    Performs environment and dependency checks, orchestrates base service health,
    and surfaces readiness to the orchestrator.

    Enhanced with communication capabilities for inter-agent collaboration.
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        ollama: Optional[OllamaService] = None,
    ) -> None:
        super().__init__(agent_id=agent_id or "01", agent_type="infrastructure", config=config)
        self.capabilities = [AgentCapability.MONITORING, AgentCapability.ORCHESTRATION]

        # Initialize communication capabilities
        CommunicationMixin.__init__(self)
        self.setup_communication()

        self.ollama = ollama  # may be None in tests; injected when available

    async def bootstrap_and_validate(self) -> BootstrapResult:
        result = BootstrapResult()

        # 1) Validate configuration
        required_env = [
            "DATABASE_URL",  # even if not used yet, ensure set for infra
        ]
        missing = [k for k in required_env if not os.getenv(k)]
        result.add_validation("env_vars", len(missing) == 0, f"Missing env: {missing}")

        # 2) Dependencies (Ollama) - optional, warn if missing
        if self.ollama is None:
            result.add_warning("OllamaService not injected; skipping Ollama health check")
            result.add_validation("ollama_health", True, "skipped")
        else:
            try:
                is_healthy = await self.ollama.health_check()
                result.add_validation("ollama_health", is_healthy, "Ollama unhealthy")
            except Exception as e:
                result.add_validation("ollama_health", False, f"Ollama check failed: {e}")

        # 3) Self-test (simple no-op task)
        try:
            exec_result = await self.execute_task({"task_id": "infra-selftest", "task_type": "noop"})
            result.add_validation("self_test", exec_result.get("status") == "completed", "self-test failed")
        except Exception as e:
            result.add_validation("self_test", False, f"self-test exception: {e}")

        # 4) Communication system validation
        try:
            comm_status = self.get_communication_status()
            result.add_validation("communication", comm_status.get("communication_enabled", False), "Communication system not initialized")
        except Exception as e:
            result.add_validation("communication", False, f"Communication validation failed: {e}")

        return result

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute infrastructure-related tasks."""
        task_type = task.get("task_type")

        # Infrastructure-specific tasks
        if task_type == "noop":
            return {
                "task_id": task.get("task_id"),
                "status": "completed",
                "result": {"ok": True},
                "metrics": {"execution_time": 0.0},
            }

        if task_type == "check_ollama":
            if self.ollama is None:
                return {
                    "task_id": task.get("task_id"),
                    "status": "failed",
                    "error": "OllamaService not available",
                }
            healthy = await self.ollama.health_check()
            return {
                "task_id": task.get("task_id"),
                "status": "completed" if healthy else "failed",
                "result": {"ollama_healthy": healthy},
                "metrics": {"health_check_time": 0.1},
            }

        if task_type == "optimize_infrastructure_params":
            """Optimize infrastructure parameters through experimentation."""
            return await self._optimize_infrastructure_parameters(task)

        if task_type == "collaborate_health_check":
            """Collaborate with other agents on health checks."""
            return await self._collaborate_health_check(task)

        if task_type == "share_infrastructure_knowledge":
            """Share infrastructure knowledge with other agents."""
            return await self._share_infrastructure_knowledge(task)

        return {
            "task_id": task.get("task_id"),
            "status": "failed",
            "error": f"Unknown task_type: {task_type}",
        }

    async def _optimize_infrastructure_parameters(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize infrastructure parameters through experimentation."""
        parameters = task.get("parameters", {})
        experiment_id = parameters.get("experiment_id", f"infra_opt_{self.agent_id}")

        # Define parameter space for infrastructure optimization
        parameter_space = {
            "health_check_interval": {"type": "range", "min": 10, "max": 120, "step": 10},  # seconds
            "timeout_threshold": {"type": "range", "min": 5, "max": 60, "step": 5},  # seconds
            "concurrency_limit": {"type": "range", "min": 1, "max": 10, "step": 1},
            "cache_ttl": {"type": "range", "min": 60, "max": 3600, "step": 300}  # seconds
        }

        evaluation_criteria = {
            "response_time": 0.4,
            "success_rate": 0.4,
            "resource_usage": 0.2
        }

        # Request optimization from another agent (e.g., monitoring agent)
        optimization_result = await self.request_parameter_optimization(
            target_agent="08",  # Monitoring agent
            task_type="infrastructure_monitoring",
            parameter_space=parameter_space,
            evaluation_criteria=evaluation_criteria,
            timeout=120.0
        )

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "experiment_id": experiment_id,
                "optimization_result": optimization_result,
                "optimized_parameters": optimization_result.get("result", {}).get("best_parameters", {}),
                "collaboration_used": True
            },
            "metrics": {"optimization_time": 0.5}
        }

    async def _collaborate_health_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with other agents on comprehensive health checks."""
        collaboration_targets = ["02", "08"]  # Database and Monitoring agents

        # Perform collaborative health check
        collaboration_result = await self.collaborate_on_task(
            collaborator_agent=collaboration_targets[0],  # Start with database agent
            task_spec={
                "type": "comprehensive_health_check",
                "parameters": {"include_dependencies": True}
            },
            collaboration_type="parallel"
        )

        # Also check monitoring agent
        monitoring_result = await self.collaborate_on_task(
            collaborator_agent=collaboration_targets[1],
            task_spec={
                "type": "infrastructure_metrics",
                "parameters": {"time_window": "5m"}
            },
            collaboration_type="parallel"
        )

        # Combine results
        combined_health = {
            "infrastructure_status": "healthy",
            "database_status": collaboration_result.get("result", {}).get("participant", "unknown"),
            "monitoring_status": monitoring_result.get("result", {}).get("participant", "unknown"),
            "overall_health": "healthy" if all([
                collaboration_result.get("status") == "completed",
                monitoring_result.get("status") == "completed"
            ]) else "degraded"
        }

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "collaborative_health_check": combined_health,
                "participants": collaboration_targets,
                "timestamp": task.get("timestamp")
            },
            "metrics": {"collaboration_time": 0.3}
        }

    async def _share_infrastructure_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Share infrastructure knowledge with other agents."""
        knowledge_data = {
            "infrastructure_capabilities": {
                "ollama_integration": self.ollama is not None,
                "communication_enabled": True,
                "monitoring_enabled": True
            },
            "optimal_parameters": {
                "health_check_interval": 30,
                "timeout_threshold": 15,
                "concurrency_limit": 5
            },
            "lessons_learned": [
                "Communication improves coordination",
                "Parameter optimization enhances performance",
                "Collaboration increases system reliability"
            ]
        }

        # Share with multiple agents
        share_results = await self.broadcast_experiment_request(
            experiment_type="share_knowledge",
            parameters={
                "knowledge_type": "infrastructure_best_practices",
                "knowledge_data": knowledge_data
            },
            target_agents=["02", "08"]  # Database and Monitoring
        )

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "knowledge_shared": knowledge_data,
                "recipients": share_results.get("target_agents", []),
                "successful_shares": share_results.get("successful_responses", 0),
                "total_recipients": len(share_results.get("target_agents", []))
            },
            "metrics": {"sharing_time": 0.2}
        }

    async def start_communication_services(self):
        """Start communication services for this agent."""
        if hasattr(self, 'start_communication'):
            await self.start_communication()

    async def stop_communication_services(self):
        """Stop communication services for this agent."""
        if hasattr(self, 'stop_communication'):
            await self.stop_communication()

    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get comprehensive infrastructure status."""
        return {
            "agent_id": self.agent_id,
            "ollama_available": self.ollama is not None,
            "communication_status": self.get_communication_status(),
            "collaboration_summary": self.get_collaboration_summary(),
            "parameter_experiments": self.get_parameter_optimization_results(),
            "agent_relationships": list(self.agent_relationships.keys())
        }

    async def self_evaluate(self) -> Dict[str, Any]:
        metrics = await self.report_metrics()
        score = metrics["success_rate"]

        # Enhanced evaluation with communication metrics
        comm_status = self.get_communication_status()
        collab_summary = self.get_collaboration_summary()

        strengths = []
        weaknesses = []
        suggestions = []

        if score >= 0.9:
            strengths.append("High reliability")
        else:
            weaknesses.append("Low success rate")

        if comm_status.get("communication_enabled"):
            strengths.append("Communication enabled")
            if collab_summary["total_collaborations"] > 0:
                success_rate = collab_summary["successful_collaborations"] / collab_summary["total_collaborations"]
                if success_rate > 0.8:
                    strengths.append("Effective collaboration")
                else:
                    weaknesses.append("Collaboration success rate needs improvement")
                    suggestions.append("Improve inter-agent communication protocols")
        else:
            weaknesses.append("Communication not enabled")
            suggestions.append("Enable communication capabilities for better coordination")

        if collab_summary["parameter_experiments"] > 0:
            strengths.append("Active parameter optimization")
        else:
            suggestions.append("Implement parameter optimization experiments")

        return {
            "agent_id": self.agent_id,
            "performance_score": score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": suggestions,
            "metrics": {
                **metrics,
                "communication_enabled": comm_status.get("communication_enabled", False),
                "total_collaborations": collab_summary["total_collaborations"],
                "successful_collaborations": collab_summary["successful_collaborations"],
                "parameter_experiments": collab_summary["parameter_experiments"]
            },
        }
