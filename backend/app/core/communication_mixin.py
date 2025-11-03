"""
Communication Mixin for BaseAgent

Adds inter-agent communication capabilities to any agent.
Provides task delegation, event handling, and collaboration features.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime

from app.core.agent_communication import get_communication_manager
from app.core.message_bus import get_message_bus

logger = logging.getLogger(__name__)


class CommunicationMixin:
    """
    Mixin class that adds communication capabilities to agents.

    This mixin provides:
    - Task delegation between agents
    - Event broadcasting
    - Collaborative task execution
    - Parameter optimization through agent collaboration
    - Performance tracking and reporting

    Usage:
        class MyAgent(BaseAgent, CommunicationMixin):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.setup_communication()
    """

    def __init__(self):
        # Communication components will be initialized in setup_communication()
        self.comm_manager = None
        self.collaboration_history: List[Dict[str, Any]] = []
        self.parameter_experiments: Dict[str, Dict[str, Any]] = {}
        self.agent_relationships: Dict[str, Dict[str, Any]] = {}

    def setup_communication(self):
        """Initialize communication capabilities."""
        if not hasattr(self, 'agent_id'):
            raise ValueError("CommunicationMixin requires agent_id to be set")

        if not hasattr(self, 'agent_type'):
            raise ValueError("CommunicationMixin requires agent_type to be set")

        self.comm_manager = get_communication_manager(self.agent_id, self.agent_type)

        # Register common task handlers
        self.comm_manager.register_task_handler("ping", self._handle_ping)
        self.comm_manager.register_task_handler("collaborate", self._handle_collaborate)
        self.comm_manager.register_task_handler("optimize_parameters", self._handle_optimize_parameters)
        self.comm_manager.register_task_handler("share_knowledge", self._handle_share_knowledge)

        logger.info(f"Communication setup complete for agent {self.agent_id}")

    async def start_communication(self):
        """Start communication services."""
        if self.comm_manager:
            await self.comm_manager.start()

    async def stop_communication(self):
        """Stop communication services."""
        if self.comm_manager:
            await self.comm_manager.stop()

    # Task Delegation Methods

    async def delegate_task_to_agent(
        self,
        target_agent: str,
        task_type: str,
        parameters: Dict[str, Any],
        priority: int = 1,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Delegate a task to another agent.

        Args:
            target_agent: Agent ID to delegate to
            task_type: Type of task to execute
            parameters: Task parameters
            priority: Task priority (1-10)
            timeout: Timeout in seconds

        Returns:
            Task result from target agent
        """
        if not self.comm_manager:
            return {
                "status": "error",
                "error": "Communication not initialized"
            }

        # Record collaboration attempt
        collaboration_id = f"{self.agent_id}_{target_agent}_{int(asyncio.get_event_loop().time() * 1000)}"
        self.collaboration_history.append({
            "id": collaboration_id,
            "type": "task_delegation",
            "target_agent": target_agent,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        })

        result = await self.comm_manager.delegate_task(
            target_agent, task_type, parameters, priority, timeout
        )

        # Update collaboration record
        for record in self.collaboration_history:
            if record["id"] == collaboration_id:
                record["status"] = result.get("status", "unknown")
                record["result"] = result
                break

        # Update agent relationships
        self._update_agent_relationship(target_agent, result)

        return result

    async def request_parameter_optimization(
        self,
        target_agent: str,
        task_type: str,
        parameter_space: Dict[str, Any],
        evaluation_criteria: Dict[str, Any],
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Request parameter optimization from another agent.

        Args:
            target_agent: Agent to optimize parameters for
            task_type: Task type to optimize
            parameter_space: Parameter ranges to explore
            evaluation_criteria: How to evaluate parameter combinations
            timeout: Optimization timeout

        Returns:
            Optimization results with best parameters found
        """
        experiment_id = f"param_opt_{self.agent_id}_{target_agent}_{task_type}_{int(asyncio.get_event_loop().time() * 1000)}"

        # Record experiment
        self.parameter_experiments[experiment_id] = {
            "id": experiment_id,
            "task_type": task_type,
            "target_agent": target_agent,
            "parameter_space": parameter_space,
            "evaluation_criteria": evaluation_criteria,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }

        parameters = {
            "experiment_id": experiment_id,
            "task_type": task_type,
            "parameter_space": parameter_space,
            "evaluation_criteria": evaluation_criteria
        }

        result = await self.delegate_task_to_agent(
            target_agent, "optimize_parameters", parameters, timeout=timeout
        )

        # Update experiment record
        if experiment_id in self.parameter_experiments:
            self.parameter_experiments[experiment_id]["completed_at"] = datetime.now().isoformat()
            self.parameter_experiments[experiment_id]["status"] = result.get("status", "unknown")
            self.parameter_experiments[experiment_id]["results"] = result

        return result

    async def collaborate_on_task(
        self,
        collaborator_agent: str,
        task_spec: Dict[str, Any],
        collaboration_type: str = "parallel"
    ) -> Dict[str, Any]:
        """
        Collaborate with another agent on a task.

        Args:
            collaborator_agent: Agent to collaborate with
            task_spec: Task specification
            collaboration_type: "parallel", "sequential", "iterative"

        Returns:
            Collaboration results
        """
        collaboration_id = f"collab_{self.agent_id}_{collaborator_agent}_{int(asyncio.get_event_loop().time() * 1000)}"

        parameters = {
            "collaboration_id": collaboration_id,
            "task_spec": task_spec,
            "collaboration_type": collaboration_type,
            "initiator": self.agent_id
        }

        result = await self.delegate_task_to_agent(
            collaborator_agent, "collaborate", parameters
        )

        # Record collaboration
        self.collaboration_history.append({
            "id": collaboration_id,
            "type": collaboration_type,
            "collaborator": collaborator_agent,
            "task_type": task_spec.get("type"),
            "timestamp": datetime.now().isoformat(),
            "result": result
        })

        return result

    async def broadcast_experiment_request(
        self,
        experiment_type: str,
        parameters: Dict[str, Any],
        target_agents: List[str] = None
    ) -> Dict[str, Any]:
        """
        Broadcast an experiment request to multiple agents.

        Args:
            experiment_type: Type of experiment
            parameters: Experiment parameters
            target_agents: Specific agents to target (None = broadcast to all)

        Returns:
            Results from all responding agents
        """
        if not self.comm_manager:
            return {"status": "error", "error": "Communication not initialized"}

        # This would use broadcast_task if implemented in communication manager
        # For now, delegate to each agent individually
        tasks = []
        for agent_id in target_agents or ["01", "02", "03"]:  # Default agents
            task = self.delegate_task_to_agent(
                agent_id, experiment_type, parameters, timeout=45.0
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "experiment_type": experiment_type,
            "target_agents": target_agents or ["01", "02", "03"],
            "results": results,
            "successful_responses": sum(1 for r in results if isinstance(r, dict) and r.get("status") == "completed"),
            "total_requests": len(results)
        }

    # Built-in Task Handlers

    async def _handle_ping(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping requests from other agents."""
        return {
            "pong": True,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": datetime.now().isoformat(),
            "capabilities": [cap.value for cap in getattr(self, 'capabilities', [])],
            "status": getattr(self, 'status', None)
        }

    async def _handle_collaborate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        collaboration_id = parameters.get("collaboration_id")
        task_spec = parameters.get("task_spec", {})
        collaboration_type = parameters.get("collaboration_type", "parallel")

        # Execute collaboration based on type
        if collaboration_type == "parallel":
            # Execute task in parallel with collaborator
            result = await self._execute_parallel_collaboration(task_spec, parameters.get("initiator"))
        elif collaboration_type == "sequential":
            # Execute task after collaborator
            result = await self._execute_sequential_collaboration(task_spec, parameters.get("initiator"))
        else:
            result = {"error": f"Unknown collaboration type: {collaboration_type}"}

        return {
            "collaboration_id": collaboration_id,
            "collaboration_type": collaboration_type,
            "result": result,
            "collaborator": self.agent_id
        }

    async def _handle_optimize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parameter optimization requests."""
        experiment_id = parameters.get("experiment_id")
        task_type = parameters.get("task_type")
        parameter_space = parameters.get("parameter_space", {})
        evaluation_criteria = parameters.get("evaluation_criteria", {})

        # Perform parameter optimization
        optimization_result = await self._perform_parameter_optimization(
            task_type, parameter_space, evaluation_criteria
        )

        return {
            "experiment_id": experiment_id,
            "task_type": task_type,
            "optimization_result": optimization_result,
            "optimized_by": self.agent_id
        }

    async def _handle_share_knowledge(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge sharing requests."""
        knowledge_type = parameters.get("knowledge_type")
        knowledge_data = parameters.get("knowledge_data", {})

        # Store knowledge
        self._store_shared_knowledge(knowledge_type, knowledge_data, parameters.get("sender"))

        return {
            "knowledge_received": True,
            "knowledge_type": knowledge_type,
            "stored_by": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }

    # Collaboration Execution Methods

    async def _execute_parallel_collaboration(self, task_spec: Dict[str, Any], initiator: str) -> Dict[str, Any]:
        """Execute parallel collaboration on a task."""
        # Execute the task locally
        local_result = await self.execute_task(task_spec)

        # Return result for initiator to combine
        return {
            "participant": self.agent_id,
            "local_result": local_result,
            "collaboration_type": "parallel"
        }

    async def _execute_sequential_collaboration(self, task_spec: Dict[str, Any], initiator: str) -> Dict[str, Any]:
        """Execute sequential collaboration on a task."""
        # Wait for initiator to complete their part (signaled via task spec)
        # For now, just execute locally
        result = await self.execute_task(task_spec)

        return {
            "participant": self.agent_id,
            "result": result,
            "collaboration_type": "sequential"
        }

    async def _perform_parameter_optimization(
        self,
        task_type: str,
        parameter_space: Dict[str, Any],
        evaluation_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform parameter optimization for a task type."""
        # Simple grid search optimization
        # In practice, this would use more sophisticated optimization algorithms

        best_params = {}
        best_score = float('-inf')
        evaluations = []

        # Generate parameter combinations (simplified)
        param_combinations = self._generate_parameter_combinations(parameter_space)

        for params in param_combinations:
            # Evaluate parameter combination
            score = await self._evaluate_parameters(task_type, params, evaluation_criteria)
            evaluations.append({
                "parameters": params,
                "score": score
            })

            if score > best_score:
                best_score = score
                best_params = params

        return {
            "best_parameters": best_params,
            "best_score": best_score,
            "evaluations": evaluations,
            "total_evaluations": len(evaluations),
            "optimization_method": "grid_search"
        }

    def _generate_parameter_combinations(self, parameter_space: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate parameter combinations for optimization."""
        # Simplified parameter generation
        combinations = []

        # For each parameter, try a few values
        for param_name, param_config in parameter_space.items():
            if isinstance(param_config, dict):
                param_type = param_config.get("type", "range")
                if param_type == "range":
                    min_val = param_config.get("min", 0)
                    max_val = param_config.get("max", 10)
                    step = param_config.get("step", 1)

                    values = list(range(min_val, max_val + 1, step))
                elif param_type == "choice":
                    values = param_config.get("values", [])
                else:
                    values = [param_config.get("default", 1)]
            else:
                # Simple list or single value
                values = param_config if isinstance(param_config, list) else [param_config]

            # For simplicity, create combinations with just a few values
            for value in values[:3]:  # Limit to 3 values per parameter
                combinations.append({param_name: value})

        return combinations

    async def _evaluate_parameters(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        evaluation_criteria: Dict[str, Any]
    ) -> float:
        """Evaluate a parameter combination."""
        # Create a test task with the parameters
        test_task = {
            "task_id": f"param_eval_{int(asyncio.get_event_loop().time() * 1000)}",
            "task_type": task_type,
            "parameters": parameters
        }

        # Execute the task
        result = await self.execute_task(test_task)

        # Evaluate based on criteria
        score = self._calculate_evaluation_score(result, evaluation_criteria)

        return score

    def _calculate_evaluation_score(self, result: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate evaluation score based on criteria."""
        if result.get("status") != "completed":
            return 0.0

        score = 0.0
        metrics = result.get("metrics", {})

        # Simple scoring based on common metrics
        if "execution_time" in metrics:
            # Lower execution time is better
            exec_time = metrics["execution_time"]
            time_score = max(0, 1.0 - (exec_time / 10.0))  # Normalize to 10 seconds
            score += time_score * 0.4

        if "success_rate" in metrics:
            success_rate = metrics["success_rate"]
            score += success_rate * 0.6

        # Add other criteria as needed
        for criterion, weight in criteria.items():
            if criterion in metrics:
                value = metrics[criterion]
                # Normalize value (assuming higher is better)
                normalized_value = min(1.0, max(0.0, value / 100.0 if value > 1 else value))
                score += normalized_value * weight

        return min(1.0, score)  # Cap at 1.0

    def _update_agent_relationship(self, agent_id: str, interaction_result: Dict[str, Any]):
        """Update relationship data with another agent."""
        if agent_id not in self.agent_relationships:
            self.agent_relationships[agent_id] = {
                "interactions": 0,
                "successful_interactions": 0,
                "average_response_time": 0,
                "last_interaction": None,
                "trust_score": 0.5  # Start neutral
            }

        relationship = self.agent_relationships[agent_id]
        relationship["interactions"] += 1
        relationship["last_interaction"] = datetime.now().isoformat()

        if interaction_result.get("status") == "completed":
            relationship["successful_interactions"] += 1

        # Update trust score based on success rate
        success_rate = relationship["successful_interactions"] / relationship["interactions"]
        relationship["trust_score"] = success_rate

        # Update average response time
        if "metrics" in interaction_result and "execution_time" in interaction_result["metrics"]:
            exec_time = interaction_result["metrics"]["execution_time"]
            current_avg = relationship["average_response_time"]
            interaction_count = relationship["interactions"]

            # Running average
            relationship["average_response_time"] = (
                (current_avg * (interaction_count - 1)) + exec_time
            ) / interaction_count

    def _store_shared_knowledge(self, knowledge_type: str, knowledge_data: Dict[str, Any], sender: str):
        """Store knowledge shared by another agent."""
        # This would integrate with the agent's knowledge base
        # For now, just log it
        logger.info(f"Agent {self.agent_id} received knowledge from {sender}: {knowledge_type}")

        # Could store in a knowledge graph, database, or local knowledge base
        # self.knowledge_base.store(knowledge_type, knowledge_data, sender)

    # Communication Status and Monitoring

    def get_communication_status(self) -> Dict[str, Any]:
        """Get communication status."""
        if not self.comm_manager:
            return {"status": "not_initialized"}

        return {
            "agent_id": self.agent_id,
            "communication_enabled": True,
            "registered_handlers": list(self.comm_manager.task_handlers.keys()),
            "pending_requests": self.comm_manager.get_pending_request_count(),
            "collaboration_history_count": len(self.collaboration_history),
            "parameter_experiments_count": len(self.parameter_experiments),
            "agent_relationships_count": len(self.agent_relationships)
        }

    def get_collaboration_summary(self) -> Dict[str, Any]:
        """Get summary of collaboration activities."""
        return {
            "total_collaborations": len(self.collaboration_history),
            "successful_collaborations": sum(
                1 for c in self.collaboration_history
                if c.get("result", {}).get("status") == "completed"
            ),
            "parameter_experiments": len(self.parameter_experiments),
            "agent_relationships": {
                agent_id: {
                    "interactions": rel["interactions"],
                    "success_rate": rel["successful_interactions"] / rel["interactions"] if rel["interactions"] > 0 else 0,
                    "trust_score": rel["trust_score"]
                }
                for agent_id, rel in self.agent_relationships.items()
            }
        }

    def get_parameter_optimization_results(self) -> Dict[str, Any]:
        """Get results from parameter optimization experiments."""
        return {
            "total_experiments": len(self.parameter_experiments),
            "completed_experiments": sum(
                1 for exp in self.parameter_experiments.values()
                if exp["status"] == "completed"
            ),
            "experiments": self.parameter_experiments
        }
