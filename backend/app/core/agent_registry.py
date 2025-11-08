"""
Agent Registry

Global registry for all agents in the system. Provides:
- Agent registration/unregistration
- Capability-based agent lookup
- Load balancing
- Health monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime

from app.core.base_agent import BaseAgent, AgentStatus, AgentCapability

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
        """Initialize agent registry."""
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, List[str]] = {}  # type -> [agent_ids]
        self.capability_index: Dict[str, List[str]] = {}  # capability -> [agent_ids]
        
        # Health tracking
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        logger.info("AgentRegistry initialized")
    
    async def register(self, agent: BaseAgent):
        """
        Register an agent with the registry.
        
        Args:
            agent: BaseAgent instance to register
        """
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
            
            logger.info(
                f"Agent {agent_id} ({agent_type}) registered with "
                f"{len(agent.capabilities)} capabilities"
            )
    
    async def unregister(self, agent_id: str):
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: ID of agent to unregister
        """
        async with self._lock:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not in registry")
                return
            
            agent = self.agents[agent_id]
            
            # Remove from type index
            agent_type = agent.agent_type
            if agent_type in self.agent_types:
                if agent_id in self.agent_types[agent_type]:
                    self.agent_types[agent_type].remove(agent_id)
            
            # Remove from capability index
            for capability in agent.capabilities:
                cap_value = capability.value
                if cap_value in self.capability_index:
                    if agent_id in self.capability_index[cap_value]:
                        self.capability_index[cap_value].remove(agent_id)
            
            # Remove agent
            del self.agents[agent_id]
            if agent_id in self.agent_health:
                del self.agent_health[agent_id]
            
            logger.info(f"Agent {agent_id} unregistered")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            BaseAgent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[BaseAgent]:
        """
        Get all registered agents.
        
        Returns:
            List of all registered agents
        """
        return list(self.agents.values())
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: Type of agent to find
            
        Returns:
            List of agents of the specified type
        """
        agent_ids = self.agent_types.get(agent_type, [])
        return [
            self.agents[aid]
            for aid in agent_ids
            if aid in self.agents
        ]
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """
        Get all agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the capability
        """
        agent_ids = self.capability_index.get(capability.value, [])
        return [
            self.agents[aid]
            for aid in agent_ids
            if aid in self.agents
        ]
    
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
        
        Args:
            task_type: Type of task
            requirements: Optional task requirements
            
        Returns:
            Best agent for the task or None if no suitable agent
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
        idle_agents = [
            a for a in capable_agents
            if a.status == AgentStatus.IDLE
        ]
        working_agents = [
            a for a in capable_agents
            if a.status == AgentStatus.WORKING
        ]
        
        candidates = idle_agents if idle_agents else working_agents
        
        if not candidates:
            return None
        
        # Select best based on performance metrics
        best_agent = max(
            candidates,
            key=lambda a: self._calculate_agent_score(a)
        )
        
        logger.debug(
            f"Selected agent {best_agent.agent_id} for task type {task_type}"
        )
        
        return best_agent
    
    def _calculate_agent_score(self, agent: BaseAgent) -> float:
        """
        Calculate agent performance score for selection.
        
        Factors:
        - Success rate (0-1)
        - Average speed (inverse, normalized)
        - Current load (inverse)
        
        Args:
            agent: Agent to score
            
        Returns:
            Performance score (higher is better)
        """
        # Success rate (0-1)
        success_rate = (
            agent.success_count / agent.task_count
            if agent.task_count > 0
            else 0.5  # Default for new agents
        )
        
        # Speed score (normalized, inverse of duration)
        metrics = agent.get_status()
        avg_duration = metrics.get("avg_task_duration", 1.0)
        speed_score = 1.0 / (1.0 + avg_duration)  # Normalize to 0-1
        
        # Load score (lower load is better)
        load_score = 1.0 / (1.0 + agent.task_count / 100.0)
        
        # Weighted total score
        total_score = (
            success_rate * 0.5 +
            speed_score * 0.3 +
            load_score * 0.2
        )
        
        return total_score
    
    async def update_health(self, agent_id: str, health_data: Dict[str, Any]):
        """
        Update agent health information.
        
        Args:
            agent_id: Agent identifier
            health_data: Health information dictionary
        """
        if agent_id in self.agent_health:
            self.agent_health[agent_id].update({
                "last_heartbeat": datetime.now().isoformat(),
                **health_data
            })
    
    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get registry status summary.
        
        Returns:
            Dictionary with registry statistics
        """
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
                    "last_heartbeat": (
                        self.agent_health.get(agent_id, {}).get("last_heartbeat")
                    )
                }
                for agent_id, agent in self.agents.items()
            }
        }


# Global singleton
_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """
    Get global agent registry singleton.
    
    Returns:
        Global AgentRegistry instance
    """
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry

