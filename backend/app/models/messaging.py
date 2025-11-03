"""
Messaging schemas for inter-agent communication.

Defines Pydantic models for messages exchanged between agents via the message bus.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4


class MessageEnvelope(BaseModel):
    """Base envelope for all messages."""
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    topic: str  # e.g., "tasks.submit", "agents.status", "metrics.update"


class TaskEnvelope(MessageEnvelope):
    """Envelope for task-related messages."""
    topic: str = "tasks.submit"
    task_id: str
    task_type: str  # e.g., "compress", "analyze", "optimize"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=10)  # 1=low, 10=high
    deadline: Optional[datetime] = None
    reply_topic: Optional[str] = None  # Where to send result


class TaskResultEnvelope(MessageEnvelope):
    """Envelope for task completion results."""
    topic: str = "tasks.result"
    task_id: str
    status: str  # "completed", "failed", "partial"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class AgentEventEnvelope(MessageEnvelope):
    """Envelope for agent lifecycle events."""
    topic: str = "agents.event"
    agent_id: str
    event_type: str  # "initialized", "error", "shutdown", "heartbeat"
    agent_type: str
    status: str  # AgentStatus value
    data: Dict[str, Any] = Field(default_factory=dict)  # Extra event data


class MetricEnvelope(MessageEnvelope):
    """Envelope for metrics updates."""
    topic: str = "metrics.update"
    metric_type: str  # "performance", "system", "agent"
    metric_name: str
    value: Any
    tags: Dict[str, Any] = Field(default_factory=dict)  # Dimensions/tags


class HypothesisEnvelope(MessageEnvelope):
    """Envelope for meta-learning hypotheses."""
    topic: str = "meta.hypothesis"
    hypothesis_id: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    experiment_plan: Dict[str, Any] = Field(default_factory=dict)


# Convenience functions
def create_task_envelope(task_id: str, task_type: str, parameters: Dict[str, Any] = None, priority: int = 1, reply_topic: Optional[str] = None) -> TaskEnvelope:
    return TaskEnvelope(
        task_id=task_id,
        task_type=task_type,
        parameters=parameters or {},
        priority=priority,
        reply_topic=reply_topic
    )


def create_task_result_envelope(task_id: str, status: str, result: Dict[str, Any] = None, error: str = None, metrics: Dict[str, Any] = None) -> TaskResultEnvelope:
    return TaskResultEnvelope(
        task_id=task_id,
        status=status,
        result=result,
        error=error,
        metrics=metrics or {}
    )


def create_agent_event_envelope(agent_id: str, event_type: str, agent_type: str, status: str, data: Dict[str, Any] = None) -> AgentEventEnvelope:
    return AgentEventEnvelope(
        agent_id=agent_id,
        event_type=event_type,
        agent_type=agent_type,
        status=status,
        data=data or {}
    )


def create_metric_envelope(metric_type: str, metric_name: str, value: Any, tags: Dict[str, Any] = None) -> MetricEnvelope:
    return MetricEnvelope(
        metric_type=metric_type,
        metric_name=metric_name,
        value=value,
        tags=tags or {}
    )

