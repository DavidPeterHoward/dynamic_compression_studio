"""
Base Agent Framework with Bootstrap Fail-Pass Methodology.

This is the foundation for all agents in the meta-recursive system.
Every agent must inherit from BaseAgent and implement bootstrap validation.

Key Principles:
1. Every agent validates itself before becoming operational
2. Agents track their own performance
3. Agents can self-evaluate and suggest improvements
4. Agents report metrics for meta-learning
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent operational status."""
    INITIALIZING = "initializing"
    VALIDATING = "validating"
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    DEGRADED = "degraded"
    SHUTDOWN = "shutdown"


class AgentCapability(Enum):
    """Standard agent capabilities."""
    COMPRESSION = "compression"
    DECOMPRESSION = "decompression"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    LEARNING = "learning"
    CODE_GENERATION = "code_generation"
    MONITORING = "monitoring"
    ORCHESTRATION = "orchestration"


class BootstrapResult:
    """
    Result of bootstrap validation.
    
    Contains:
    - Success/failure status
    - Validation results for each component
    - Error messages
    - Performance metrics
    """
    
    def __init__(self):
        """Initialize bootstrap result."""
        self.success: bool = False
        self.validations: Dict[str, bool] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.timestamp: datetime = datetime.now()
    
    def add_validation(self, component: str, passed: bool, message: str = ""):
        """
        Add validation result for a component.
        
        Args:
            component: Component name
            passed: Whether validation passed
            message: Optional message
        """
        self.validations[component] = passed
        if not passed:
            self.errors.append(f"{component}: {message}")
        
        # Update overall success
        self.success = all(self.validations.values())
    
    def add_warning(self, message: str):
        """Add warning message."""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "validations": self.validations,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """
    Base class for all agents in the meta-recursive system.
    
    CRITICAL: This implements the bootstrap fail-pass methodology.
    Every agent MUST validate itself before becoming operational.
    
    Lifecycle:
    1. __init__ - Create agent
    2. bootstrap_and_validate() - Self-validate
    3. If validation passes → IDLE
    4. If validation fails → ERROR
    5. execute_task() - Perform work
    6. self_evaluate() - Analyze own performance
    7. shutdown() - Clean shutdown
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_type: str = "base",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (e.g., "compression", "meta_learner")
            config: Agent configuration
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = agent_type
        self.config = config or {}
        self.status = AgentStatus.INITIALIZING
        self.capabilities: List[AgentCapability] = []
        self.performance_history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.last_active_at = datetime.now()
        self.task_count = 0
        self.error_count = 0
        self.success_count = 0
        
        logger.info(f"Agent {self.agent_id} ({self.agent_type}) initializing...")
    
    @abstractmethod
    async def bootstrap_and_validate(self) -> BootstrapResult:
        """
        Bootstrap and validate agent.
        
        CRITICAL: This is the core of the bootstrap fail-pass methodology.
        
        Must validate:
        1. Configuration is valid
        2. Required dependencies are available
        3. Connections to services work
        4. Self-tests pass
        5. Capabilities are functional
        
        Returns:
            BootstrapResult with validation status
        """
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute assigned task.
        
        Args:
            task: Task specification with:
                - task_id: Unique task identifier
                - task_type: Type of task
                - parameters: Task parameters
                - deadline: Optional deadline
                
        Returns:
            Task result with:
                - task_id: Original task ID
                - status: "completed" | "failed" | "partial"
                - result: Task output
                - metrics: Performance metrics
                - errors: Any errors encountered
        """
        pass
    
    @abstractmethod
    async def self_evaluate(self) -> Dict[str, Any]:
        """
        Evaluate own performance.
        
        CRITICAL for meta-recursion.
        
        Returns:
            Evaluation with:
                - performance_score: 0.0 - 1.0
                - strengths: List of strengths
                - weaknesses: List of weaknesses
                - improvement_suggestions: List of suggestions
                - metrics: Performance metrics
        """
        pass
    
    async def initialize(self) -> bool:
        """
        Initialize agent with bootstrap validation.
        
        Returns:
            True if initialization and validation succeed
        """
        try:
            self.status = AgentStatus.VALIDATING
            
            # Run bootstrap validation
            bootstrap_result = await self.bootstrap_and_validate()
            
            if bootstrap_result.success:
                self.status = AgentStatus.IDLE
                logger.info(f"Agent {self.agent_id} initialized successfully")
                return True
            else:
                self.status = AgentStatus.ERROR
                logger.error(
                    f"Agent {self.agent_id} bootstrap failed: "
                    f"{bootstrap_result.errors}"
                )
                return False
        
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_id} initialization failed: {e}")
            return False
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task with error handling and metrics tracking.
        
        Args:
            task: Task specification
            
        Returns:
            Task result
        """
        if self.status not in [AgentStatus.IDLE, AgentStatus.DEGRADED]:
            return {
                "task_id": task.get("task_id"),
                "status": "failed",
                "error": f"Agent not ready (status: {self.status.value})"
            }
        
        self.status = AgentStatus.WORKING
        self.last_active_at = datetime.now()
        self.task_count += 1
        
        start_time = datetime.now()
        
        try:
            # Execute task
            result = await self.execute_task(task)
            
            # Track success
            if result.get("status") == "completed":
                self.success_count += 1
            else:
                self.error_count += 1
            
            # Calculate metrics
            duration = (datetime.now() - start_time).total_seconds()
            
            # Record performance
            self.performance_history.append({
                "task_id": task.get("task_id"),
                "task_type": task.get("task_type"),
                "duration": duration,
                "status": result.get("status"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update status
            self.status = AgentStatus.IDLE
            
            return result
        
        except Exception as e:
            self.error_count += 1
            self.status = AgentStatus.ERROR
            
            logger.error(f"Agent {self.agent_id} task execution failed: {e}")
            
            return {
                "task_id": task.get("task_id"),
                "status": "failed",
                "error": str(e)
            }
    
    async def report_metrics(self) -> Dict[str, Any]:
        """
        Report agent metrics.
        
        Returns:
            Current agent metrics
        """
        success_rate = (
            self.success_count / self.task_count 
            if self.task_count > 0 
            else 0.0
        )
        
        avg_duration = 0.0
        if self.performance_history:
            durations = [p["duration"] for p in self.performance_history]
            avg_duration = sum(durations) / len(durations)
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "task_count": self.task_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "avg_task_duration": avg_duration,
            "created_at": self.created_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status (synchronous version for compatibility).

        Returns:
            Current agent status and metrics
        """
        success_rate = (
            self.success_count / self.task_count
            if self.task_count > 0
            else 0.0
        )

        avg_duration = 0.0
        if self.performance_history:
            durations = [p["duration"] for p in self.performance_history]
            avg_duration = sum(durations) / len(durations)

        uptime = (datetime.now() - self.created_at).total_seconds()

        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "uptime_seconds": uptime,
            "task_count": self.task_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "avg_task_duration": avg_duration,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "uptime_seconds": (datetime.now() - self.created_at).total_seconds()
        }
    
    async def health_check(self) -> bool:
        """
        Perform health check.
        
        Returns:
            True if agent is healthy
        """
        # Basic health check
        if self.status == AgentStatus.ERROR:
            return False
        
        # Check error rate
        if self.task_count > 10:
            error_rate = self.error_count / self.task_count
            if error_rate > 0.5:  # >50% error rate
                logger.warning(
                    f"Agent {self.agent_id} has high error rate: "
                    f"{error_rate:.2%}"
                )
                return False
        
        return True
    
    async def shutdown(self):
        """
        Graceful shutdown.
        
        Performs cleanup and reports final metrics.
        """
        logger.info(f"Agent {self.agent_id} shutting down...")
        
        self.status = AgentStatus.SHUTDOWN
        
        # Report final metrics
        final_metrics = await self.report_metrics()
        logger.info(f"Final metrics for {self.agent_id}: {final_metrics}")
        
        # Cleanup (override in subclasses as needed)
        await self._cleanup()
    
    async def _cleanup(self):
        """
        Cleanup resources.
        
        Override in subclasses to clean up specific resources.
        """
        pass
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<{self.__class__.__name__} "
            f"id={self.agent_id} "
            f"type={self.agent_type} "
            f"status={self.status.value}>"
        )


class SimpleAgent(BaseAgent):
    """
    Simple agent implementation for testing.
    
    This is a concrete implementation that can be used for testing
    the base agent framework.
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize simple agent."""
        super().__init__(agent_id=agent_id, agent_type="simple", config=config)
        self.capabilities = [AgentCapability.ANALYSIS]
    
    async def bootstrap_and_validate(self) -> BootstrapResult:
        """Bootstrap and validate simple agent."""
        result = BootstrapResult()
        
        # Validate configuration
        result.add_validation(
            "configuration",
            True,
            "Configuration valid"
        )
        
        # Validate capabilities
        result.add_validation(
            "capabilities",
            len(self.capabilities) > 0,
            "At least one capability required"
        )
        
        # Self-test
        try:
            test_result = await self.self_test()
            result.add_validation(
                "self_test",
                test_result,
                "Self-test passed"
            )
        except Exception as e:
            result.add_validation(
                "self_test",
                False,
                f"Self-test failed: {e}"
            )
        
        return result
    
    async def self_test(self) -> bool:
        """
        Run self-test.
        
        Returns:
            True if self-test passes
        """
        # Simple self-test: verify we can execute a basic task
        try:
            test_task = {
                "task_id": "self-test",
                "task_type": "test",
                "parameters": {}
            }
            result = await self.execute_task(test_task)
            return result.get("status") == "completed"
        except Exception:
            return False
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple task."""
        # Simulate work
        await asyncio.sleep(0.1)
        
        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "message": "Task completed successfully",
                "task_type": task.get("task_type")
            },
            "metrics": {
                "execution_time": 0.1
            }
        }
    
    async def self_evaluate(self) -> Dict[str, Any]:
        """Evaluate simple agent performance."""
        metrics = await self.report_metrics()
        
        performance_score = metrics["success_rate"]
        
        strengths = []
        if performance_score > 0.9:
            strengths.append("High success rate")
        if metrics["avg_task_duration"] < 1.0:
            strengths.append("Fast task execution")
        
        weaknesses = []
        if performance_score < 0.7:
            weaknesses.append("Low success rate")
        if metrics["error_count"] > 10:
            weaknesses.append("High error count")
        
        improvement_suggestions = []
        if performance_score < 0.9:
            improvement_suggestions.append("Improve error handling")
        if metrics["avg_task_duration"] > 2.0:
            improvement_suggestions.append("Optimize task execution")
        
        return {
            "agent_id": self.agent_id,
            "performance_score": performance_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": improvement_suggestions,
            "metrics": metrics
        }

