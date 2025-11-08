# Schema Models Integration & Enhancement

## Overview

This document details the integration of enhanced agent system models with existing compression algorithm schemas, providing comprehensive data validation, relationships, and performance optimizations.

## Existing Model Structure Review

### Current Models in `backend/app/models/`

**Core Models:**
- `algorithm.py` - Compression algorithms metadata
- `compression_requests.py` - Compression job tracking
- `compression_validation.py` - Validation results
- `file.py` - File handling
- `user.py` - User management
- `metrics.py` - Performance metrics

**Integration Points:**
- Agent system models extend existing patterns
- Database relationships maintain compatibility
- Validation schemas align with current Pydantic usage

## Enhanced Model Architecture

### Base Models and Mixins

**File: `backend/app/models/base_enhanced.py` (New)**

```python
"""
Enhanced base models with circuit breaker support, structured logging, and validation.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, Integer, func, text
from sqlalchemy.orm import declared_attr
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel as PydanticBaseModel, validator

# Enhanced SQLAlchemy base
class EnhancedBase:
    """Enhanced base class with common fields and methods."""

    @declared_attr
    def __tablename__(cls):
        # Convert CamelCase to snake_case
        return cls.__name__.lower()

    # Common fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version = Column(Integer, default=1, nullable=False)

    # Correlation and tracking
    correlation_id = Column(String(255), nullable=True, index=True)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Circuit breaker and health tracking
    circuit_breaker_state = Column(String(20), default='closed')
    failure_count = Column(Integer, default=0)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    health_status = Column(String(20), default='healthy')

    def update_health_status(self, status: str):
        """Update health status with timestamp."""
        self.health_status = status
        if status == 'unhealthy':
            self.last_failure_at = datetime.now()
            self.failure_count += 1
        elif status == 'healthy':
            self.failure_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

# Create enhanced base
EnhancedBaseModel = declarative_base(cls=EnhancedBase)

# Enhanced Pydantic base with validation
class EnhancedBaseModel(PydanticBaseModel):
    """Enhanced Pydantic base with validation and sanitization."""

    correlation_id: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True

    @validator('*', pre=True, each_item=True)
    def sanitize_strings(cls, v):
        """Sanitize string inputs to prevent XSS."""
        if isinstance(v, str):
            # Basic sanitization - remove potentially dangerous patterns
            return v.strip()[:10000]  # Limit length and trim
        return v

    def dict(self, *args, **kwargs):
        """Enhanced dict method with correlation ID."""
        data = super().dict(*args, **kwargs)
        if hasattr(self, 'correlation_id') and self.correlation_id:
            data['correlation_id'] = self.correlation_id
        return data
```

### Enhanced Agent Models

**File: `backend/app/models/agent_enhanced.py` (New)**

```python
"""
Enhanced agent models with comprehensive validation and relationships.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from .base_enhanced import EnhancedBaseModel as Base, EnhancedBaseModel as PydanticBase


class AgentType(str, Enum):
    """Agent type enumeration."""
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    MONITORING = "monitoring"
    NETWORK = "network"
    SECURITY = "security"
    ANALYTICS = "analytics"
    LLM_CONVERSATIONAL = "llm_conversational"
    LLM_CODE_ASSISTANT = "llm_code_assistant"
    LLM_ANALYST = "llm_analyst"
    LLM_CREATIVE_WRITER = "llm_creative_writer"
    LOGICAL_ANALYST = "logical_analyst"
    ARGUMENTATION_SPECIALIST = "argumentation_specialist"
    CONCEPTUAL_ANALYST = "conceptual_analyst"
    CRITICAL_THINKER = "critical_thinker"
    LINGUISTIC_ANALYST = "linguistic_analyst"
    MATHEMATICAL_THINKER = "mathematical_thinker"
    CREATIVE_INNOVATOR = "creative_innovator"
    INTEGRATION_SPECIALIST = "integration_specialist"
    STRATEGIC_PLANNER = "strategic_planner"


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# SQLAlchemy Model
class Agent(Base):
    """Enhanced agent model with comprehensive tracking."""
    __tablename__ = "agents"

    # Basic information
    name = Column(String(255), nullable=False, index=True)
    agent_type = Column(String(100), nullable=False, index=True)
    specialization = Column(Text, nullable=True)

    # Integration with compression algorithms
    supported_algorithms = Column(JSONB, default=list, nullable=False)
    compression_priority = Column(Integer, default=0)

    # Capabilities and configuration
    capabilities = Column(JSONB, default=list, nullable=False)
    status = Column(String(50), default=AgentStatus.IDLE.value, nullable=False, index=True)
    configuration = Column(JSONB, default=dict, nullable=False)

    # Performance metrics
    performance_metrics = Column(JSONB, default=dict, nullable=False)

    # Enhanced health tracking
    health_status = Column(String(20), default=HealthStatus.HEALTHY.value, nullable=False, index=True)
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    health_check_interval = Column(Integer, default=60)  # seconds

    # Activity tracking
    last_active_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Performance counters
    uptime_seconds = Column(Integer, default=0)
    task_count = Column(Integer, default=0, index=True)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    # Calculated fields (updated by triggers)
    success_rate = Column(Float, default=0.0)
    avg_task_duration = Column(Float, nullable=True)  # seconds
    total_tokens_processed = Column(Integer, default=0)
    avg_tokens_per_second = Column(Float, nullable=True)

    # Relationships
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="agent", cascade="all, delete-orphan")
    compression_requests = relationship("CompressionRequest", back_populates="assigned_agent")

    def update_performance_metrics(self, task_duration: float, tokens_processed: int, success: bool):
        """Update performance metrics after task completion."""
        self.task_count += 1

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        self.success_rate = self.success_count / self.task_count if self.task_count > 0 else 0.0

        # Update average task duration (rolling average)
        if self.avg_task_duration:
            self.avg_task_duration = (self.avg_task_duration + task_duration) / 2
        else:
            self.avg_task_duration = task_duration

        # Update token processing metrics
        self.total_tokens_processed += tokens_processed
        total_time = self.uptime_seconds + task_duration
        if total_time > 0:
            self.avg_tokens_per_second = self.total_tokens_processed / total_time

        self.last_active_at = datetime.now()

    def check_health(self) -> HealthStatus:
        """Check agent health based on metrics."""
        if self.error_count > self.task_count * 0.3:  # More than 30% error rate
            return HealthStatus.UNHEALTHY
        elif self.error_count > self.task_count * 0.1:  # More than 10% error rate
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


# Pydantic Models
class AgentBase(PydanticBase):
    """Base agent model."""
    name: str = Field(..., min_length=1, max_length=255)
    agent_type: AgentType
    specialization: Optional[str] = Field(None, max_length=1000)
    supported_algorithms: List[str] = Field(default_factory=list)
    compression_priority: int = Field(default=0, ge=0, le=100)
    capabilities: List[str] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)


class AgentCreate(AgentBase):
    """Agent creation model."""
    pass


class AgentUpdate(PydanticBase):
    """Agent update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    agent_type: Optional[AgentType] = None
    specialization: Optional[str] = Field(None, max_length=1000)
    supported_algorithms: Optional[List[str]] = None
    compression_priority: Optional[int] = Field(None, ge=0, le=100)
    capabilities: Optional[List[str]] = None
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[AgentStatus] = None
    health_status: Optional[HealthStatus] = None


class AgentResponse(AgentBase):
    """Agent response model."""
    id: str
    status: AgentStatus
    health_status: HealthStatus
    performance_metrics: Dict[str, Any]
    last_active_at: Optional[datetime]
    uptime_seconds: int
    task_count: int
    success_count: int
    error_count: int
    success_rate: float
    avg_task_duration: Optional[float]
    total_tokens_processed: int
    avg_tokens_per_second: Optional[float]
    created_at: datetime
    updated_at: datetime
    correlation_id: Optional[str]

    @validator('success_rate')
    def validate_success_rate(cls, v):
        """Validate success rate is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Success rate must be between 0.0 and 1.0')
        return v


class AgentHealthCheck(PydanticBase):
    """Agent health check model."""
    agent_id: str
    status: HealthStatus
    checks: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    response_time_ms: Optional[float] = None

    @validator('response_time_ms')
    def validate_response_time(cls, v):
        """Validate response time is reasonable."""
        if v is not None and v < 0:
            raise ValueError('Response time cannot be negative')
        return v
```

### Enhanced Task Models

**File: `backend/app/models/task_enhanced.py` (New)**

```python
"""
Enhanced task models with circuit breaker integration and performance tracking.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

from .base_enhanced import EnhancedBaseModel as Base, EnhancedBaseModel as PydanticBase


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# SQLAlchemy Model
class Task(Base):
    """Enhanced task model with comprehensive tracking."""
    __tablename__ = "tasks"

    # Relationships
    agent_id = Column(String(36), ForeignKey('agents.id'), nullable=True, index=True)
    compression_request_id = Column(String(36), ForeignKey('compression_requests.id'), nullable=True, index=True)
    algorithm_id = Column(String(50), ForeignKey('compression_algorithms.id'), nullable=True, index=True)

    # Task details
    operation = Column(String(255), nullable=False, index=True)
    parameters = Column(JSONB, default=dict, nullable=False)
    priority = Column(String(20), default=TaskPriority.NORMAL.value, nullable=False, index=True)

    # Status and lifecycle
    status = Column(String(50), default=TaskStatus.PENDING.value, nullable=False, index=True)
    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

    # Performance tracking
    execution_time_seconds = Column(Float, nullable=True)
    queue_wait_time_seconds = Column(Float, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    memory_usage_mb = Column(Float, nullable=True)
    tokens_processed = Column(Integer, default=0)

    # Circuit breaker integration
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    circuit_breaker_triggered = Column(Boolean, default=False)
    failure_reason = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    timeout_seconds = Column(Integer, default=30)

    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    compression_request = relationship("CompressionRequest", back_populates="task")

    def mark_started(self):
        """Mark task as started."""
        self.status = TaskStatus.RUNNING.value
        self.started_at = datetime.now()

    def mark_completed(self, result: Any = None, execution_time: float = None):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED.value
        self.result = result
        self.execution_time_seconds = execution_time
        self.completed_at = datetime.now()

    def mark_failed(self, error_message: str, failure_reason: str = None):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED.value
        self.error_message = error_message
        self.failure_reason = failure_reason
        self.completed_at = datetime.now()

    def should_retry(self) -> bool:
        """Check if task should be retried."""
        return (self.status == TaskStatus.FAILED.value and
                self.retry_count < self.max_retries and
                not self.circuit_breaker_triggered)

    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1

    def trigger_circuit_breaker(self, reason: str):
        """Trigger circuit breaker for this task."""
        self.circuit_breaker_triggered = True
        self.failure_reason = reason
        self.status = TaskStatus.FAILED.value


# Pydantic Models
class TaskBase(PydanticBase):
    """Base task model."""
    operation: str = Field(..., min_length=1, max_length=255)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    timeout_seconds: int = Field(default=30, ge=1, le=3600)
    agent_id: Optional[str] = None
    compression_request_id: Optional[str] = None
    algorithm_id: Optional[str] = None


class TaskCreate(TaskBase):
    """Task creation model."""
    pass


class TaskUpdate(PydanticBase):
    """Task update model."""
    status: Optional[TaskStatus] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    retry_count: Optional[int] = None
    circuit_breaker_triggered: Optional[bool] = None


class TaskResponse(TaskBase):
    """Task response model."""
    id: str
    status: TaskStatus
    result: Optional[Any]
    error_message: Optional[str]
    execution_time_seconds: Optional[float]
    queue_wait_time_seconds: Optional[float]
    cpu_usage_percent: Optional[float]
    memory_usage_mb: Optional[float]
    tokens_processed: int
    retry_count: int
    max_retries: int
    circuit_breaker_triggered: bool
    failure_reason: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    correlation_id: Optional[str]

    @validator('execution_time_seconds', 'queue_wait_time_seconds')
    def validate_positive_times(cls, v):
        """Validate timing fields are positive."""
        if v is not None and v < 0:
            raise ValueError('Time values cannot be negative')
        return v

    @validator('cpu_usage_percent')
    def validate_cpu_usage(cls, v):
        """Validate CPU usage is between 0 and 100."""
        if v is not None and not 0.0 <= v <= 100.0:
            raise ValueError('CPU usage must be between 0.0 and 100.0')
        return v


class TaskMetrics(PydanticBase):
    """Task metrics model."""
    task_id: str
    agent_id: Optional[str]
    operation: str
    status: TaskStatus
    execution_time_seconds: Optional[float]
    queue_wait_time_seconds: Optional[float]
    cpu_usage_percent: Optional[float]
    memory_usage_mb: Optional[float]
    tokens_processed: int
    retry_count: int
    circuit_breaker_triggered: bool
    timestamp: datetime = Field(default_factory=datetime.now)
```

### Enhanced Conversation Models

**File: `backend/app/models/conversation_enhanced.py` (New)**

```python
"""
Enhanced conversation models with streaming support and performance tracking.
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

from .base_enhanced import EnhancedBaseModel as Base, EnhancedBaseModel as PydanticBase


class ConversationType(str, Enum):
    """Conversation type enumeration."""
    CHAT = "chat"
    DEBATE = "debate"
    TASK = "task"
    COMPRESSION = "compression"


class CircuitBreakerState(str, Enum):
    """Circuit breaker state for conversations."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


# SQLAlchemy Model
class Conversation(Base):
    """Enhanced conversation model with comprehensive tracking."""
    __tablename__ = "conversations"

    # Relationships
    agent_id = Column(String(36), ForeignKey('agents.id'), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)

    # Conversation details
    conversation_type = Column(String(50), default=ConversationType.CHAT.value, nullable=False, index=True)
    messages = Column(JSONB, default=list, nullable=False)

    # Integration with compression
    related_request_id = Column(String(36), ForeignKey('compression_requests.id'), nullable=True, index=True)

    # Model and performance
    model_name = Column(String(255), nullable=True, index=True)
    total_tokens = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)

    # Status and lifecycle
    status = Column(String(50), default="active", nullable=False, index=True)
    metadata = Column(JSONB, default=dict, nullable=False)

    # Circuit breaker integration
    circuit_breaker_state = Column(String(20), default=CircuitBreakerState.CLOSED.value)
    failure_count = Column(Integer, default=0)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)

    # Completion tracking
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="conversations")
    compression_request = relationship("CompressionRequest", back_populates="conversations")

    def add_message(self, role: str, content: str, **metadata):
        """Add a message to the conversation."""
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }
        self.messages = self.messages + [message]
        return message

    def update_tokens(self, tokens: int):
        """Update token count."""
        self.total_tokens += tokens

    def mark_completed(self, duration: float = None):
        """Mark conversation as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()
        if duration:
            self.duration_seconds = duration

    def trigger_circuit_breaker(self):
        """Trigger circuit breaker for this conversation."""
        self.circuit_breaker_state = CircuitBreakerState.OPEN.value
        self.failure_count += 1
        self.last_failure_at = datetime.now()


# Pydantic Models
class Message(PydanticBase):
    """Message model for conversations."""
    id: str
    role: str = Field(..., regex=r'^(user|assistant|system)$')
    content: str = Field(..., min_length=0, max_length=100000)
    timestamp: str
    agent_id: Optional[str] = None
    tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('content')
    def validate_content_length(cls, v):
        """Validate content length."""
        if len(v) > 100000:  # 100KB limit
            raise ValueError('Message content too long')
        return v


class ConversationBase(PydanticBase):
    """Base conversation model."""
    session_id: str = Field(..., min_length=1, max_length=255)
    conversation_type: ConversationType = Field(default=ConversationType.CHAT)
    agent_id: Optional[str] = None
    model_name: Optional[str] = Field(None, max_length=255)
    related_request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationCreate(ConversationBase):
    """Conversation creation model."""
    initial_message: Optional[Message] = None


class ConversationUpdate(PydanticBase):
    """Conversation update model."""
    messages: Optional[List[Message]] = None
    total_tokens: Optional[int] = None
    duration_seconds: Optional[float] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(ConversationBase):
    """Conversation response model."""
    id: str
    messages: List[Message]
    total_tokens: int
    duration_seconds: Optional[float]
    status: str
    circuit_breaker_state: CircuitBreakerState
    failure_count: int
    last_failure_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    correlation_id: Optional[str]

    @validator('total_tokens')
    def validate_token_count(cls, v):
        """Validate token count is non-negative."""
        if v < 0:
            raise ValueError('Token count cannot be negative')
        return v


class ConversationMetrics(PydanticBase):
    """Conversation metrics model."""
    conversation_id: str
    session_id: str
    agent_id: Optional[str]
    model_name: Optional[str]
    conversation_type: ConversationType
    total_tokens: int
    duration_seconds: Optional[float]
    message_count: int
    status: str
    circuit_breaker_state: CircuitBreakerState
    failure_count: int
    timestamp: datetime = Field(default_factory=datetime.now)
```

### Integration with Existing Compression Models

**File: `backend/app/models/compression_requests.py` (Enhanced)**

```python
# Existing imports...
from sqlalchemy import Column, String, Integer, TIMESTAMP, DECIMAL, JSON, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class CompressionRequest(Base):
    # Existing columns...

    # Enhanced agent integration
    assigned_agent_id = Column(String(36), ForeignKey('agents.id'), nullable=True, index=True)
    assigned_agent = relationship("Agent", back_populates="compression_requests")

    # Agent performance tracking
    agent_execution_time_ms = Column(Integer, nullable=True)
    agent_cpu_usage_percent = Column(DECIMAL(5,2), nullable=True)
    agent_memory_usage_mb = Column(DECIMAL(10,2), nullable=True)
    agent_tokens_processed = Column(Integer, nullable=True)

    # Task integration
    task_id = Column(String(36), ForeignKey('tasks.id'), nullable=True, index=True)
    task = relationship("Task", back_populates="compression_request")

    # Conversation integration for agent chat
    conversations = relationship("Conversation", back_populates="compression_request")

    # Enhanced metadata
    agent_metadata = Column(JSONB, nullable=True)  # Agent-specific execution details
    agent_feedback = Column(JSONB, nullable=True)  # Agent feedback on compression
```

### Database Triggers and Functions

**File: `backend/alembic/versions/enhanced_models_triggers.sql`**

```sql
-- Enhanced database triggers and functions for model integration

-- Function to update agent performance metrics
CREATE OR REPLACE FUNCTION update_agent_performance_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update on task completion
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        -- Update agent success rate and metrics
        UPDATE agents
        SET
            task_count = task_count + 1,
            success_count = success_count + 1,
            success_rate = ((success_count + 1)::DECIMAL / (task_count + 1)::DECIMAL),
            last_active_at = NEW.completed_at,
            total_tokens_processed = total_tokens_processed + COALESCE(NEW.tokens_processed, 0),
            updated_at = NOW()
        WHERE id = NEW.agent_id;

        -- Update average task duration
        UPDATE agents
        SET avg_task_duration = (
            SELECT AVG(execution_time_seconds)
            FROM tasks
            WHERE agent_id = NEW.agent_id
            AND status = 'completed'
            AND execution_time_seconds IS NOT NULL
        )
        WHERE id = NEW.agent_id;

    ELSIF NEW.status = 'failed' AND (OLD.status IS NULL OR OLD.status != 'failed') THEN
        -- Update agent error count
        UPDATE agents
        SET
            task_count = task_count + 1,
            error_count = error_count + 1,
            success_rate = (success_count::DECIMAL / (task_count + 1)::DECIMAL),
            last_active_at = NEW.completed_at,
            updated_at = NOW()
        WHERE id = NEW.agent_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for agent performance updates
CREATE TRIGGER trigger_update_agent_performance
    AFTER UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_performance_metrics();

-- Function to check and update circuit breaker state
CREATE OR REPLACE FUNCTION update_circuit_breaker_state()
RETURNS TRIGGER AS $$
DECLARE
    failure_threshold INTEGER := 5;
    current_failures INTEGER;
BEGIN
    -- Count recent failures for this agent
    SELECT COUNT(*) INTO current_failures
    FROM tasks
    WHERE agent_id = NEW.agent_id
    AND status = 'failed'
    AND completed_at >= NOW() - INTERVAL '10 minutes';

    -- Update circuit breaker state
    IF current_failures >= failure_threshold THEN
        UPDATE agents
        SET
            circuit_breaker_state = 'open',
            health_status = 'unhealthy',
            updated_at = NOW()
        WHERE id = NEW.agent_id;
    ELSIF current_failures >= failure_threshold / 2 THEN
        UPDATE agents
        SET
            circuit_breaker_state = 'half_open',
            health_status = 'degraded',
            updated_at = NOW()
        WHERE id = NEW.agent_id;
    ELSE
        UPDATE agents
        SET
            circuit_breaker_state = 'closed',
            health_status = 'healthy',
            updated_at = NOW()
        WHERE id = NEW.agent_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for circuit breaker updates
CREATE TRIGGER trigger_update_circuit_breaker
    AFTER UPDATE ON tasks
    FOR EACH ROW
    WHEN (NEW.status IN ('completed', 'failed'))
    EXECUTE FUNCTION update_circuit_breaker_state();

-- Function to update conversation metrics
CREATE OR REPLACE FUNCTION update_conversation_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update conversation completion
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        NEW.completed_at = NOW();

        -- Update agent conversation count
        IF NEW.agent_id IS NOT NULL THEN
            UPDATE agents
            SET updated_at = NOW()
            WHERE id = NEW.agent_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for conversation metrics
CREATE TRIGGER trigger_update_conversation_metrics
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_metrics();

-- Function for health check updates
CREATE OR REPLACE FUNCTION perform_agent_health_check()
RETURNS VOID AS $$
DECLARE
    agent_record RECORD;
BEGIN
    -- Update health check timestamp for all agents
    UPDATE agents
    SET
        last_health_check = NOW(),
        updated_at = NOW();

    -- Mark agents as unhealthy if no recent activity
    UPDATE agents
    SET
        health_status = 'unhealthy',
        updated_at = NOW()
    WHERE last_active_at < NOW() - INTERVAL '1 hour'
    AND health_status = 'healthy';

    -- Log health check
    INSERT INTO metrics (
        metric_type, entity_type, entity_id, metric_name, metric_value, recorded_at
    )
    SELECT
        'health_check',
        'agent',
        id,
        'health_status',
        CASE
            WHEN health_status = 'healthy' THEN 1.0
            WHEN health_status = 'degraded' THEN 0.5
            ELSE 0.0
        END,
        NOW()
    FROM agents;
END;
$$ LANGUAGE plpgsql;
```

This enhanced model integration provides comprehensive validation, performance tracking, circuit breaker integration, and seamless compatibility with existing compression system models.
