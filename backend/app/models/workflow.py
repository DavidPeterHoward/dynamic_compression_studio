"""
Workflow Pipelines Data Models

Comprehensive models for workflow pipelines, scripts, helpers, and execution tracking.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class PipelineStatus(str, Enum):
    """Pipeline status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class PipelineCategory(str, Enum):
    """Pipeline categories."""
    CODEBASE = "codebase"
    ERRORS = "errors"
    TESTING = "testing"
    LOGS = "logs"
    COMPRESSION = "compression"
    CUSTOM = "custom"


class StepType(str, Enum):
    """Pipeline step types."""
    SCRIPT = "script"
    API_CALL = "api_call"
    COMPRESSION = "compression"
    CONDITION = "condition"
    LOOP = "loop"
    TRANSFORMATION = "transformation"


class ExecutionStatus(str, Enum):
    """Execution status states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionTrigger(str, Enum):
    """How execution was triggered."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    WEBHOOK = "webhook"
    EVENT = "event"


class ScriptLanguage(str, Enum):
    """Supported script languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    BASH = "bash"
    SHELL = "shell"


class LogLevel(str, Enum):
    """Log levels for execution logs."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# DATABASE MODELS (SQLAlchemy)
# ============================================================================

class WorkflowPipeline(Base):
    """Workflow pipeline database model."""
    __tablename__ = "workflow_pipelines"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default=PipelineCategory.CUSTOM.value)
    status = Column(String(20), nullable=False, default=PipelineStatus.INACTIVE.value)
    
    # Configuration
    configuration = Column(JSON, nullable=False, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(36), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    
    # Performance tracking
    total_executions = Column(Integer, default=0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    failed_executions = Column(Integer, default=0, nullable=False)
    avg_execution_time = Column(Float, default=0.0, nullable=False)
    avg_compression_ratio = Column(Float, default=0.0, nullable=True)
    
    # Relationships
    steps = relationship("WorkflowPipelineStep", back_populates="pipeline", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="pipeline", cascade="all, delete-orphan")


class WorkflowPipelineStep(Base):
    """Pipeline step database model."""
    __tablename__ = "workflow_pipeline_steps"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id = Column(String(36), ForeignKey("workflow_pipelines.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    step_type = Column(String(50), nullable=False, default=StepType.SCRIPT.value)
    order_index = Column(Integer, nullable=False)
    
    # Configuration
    configuration = Column(JSON, nullable=False, default=dict)
    
    # Dependencies (array of step IDs)
    depends_on = Column(JSON, nullable=False, default=list)
    
    # Conditional logic
    condition = Column(Text, nullable=True)
    
    # Timeout and retry
    timeout_seconds = Column(Integer, default=300, nullable=False)
    max_retries = Column(Integer, default=0, nullable=False)
    retry_delay_seconds = Column(Integer, default=10, nullable=False)
    
    # Relationships
    pipeline = relationship("WorkflowPipeline", back_populates="steps")


class WorkflowScript(Base):
    """Dynamic script database model."""
    __tablename__ = "workflow_scripts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Script details
    language = Column(String(50), nullable=False, default=ScriptLanguage.PYTHON.value)
    code = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False, default=list)
    
    # Integration
    llm_integration = Column(Boolean, default=False, nullable=False)
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(36), nullable=True)
    
    # Security
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(String(36), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    total_executions = Column(Integer, default=0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    failed_executions = Column(Integer, default=0, nullable=False)


class WorkflowHelper(Base):
    """Helper function library database model."""
    __tablename__ = "workflow_helpers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Functions definition
    functions = Column(JSON, nullable=False, default=list)
    implementation = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(36), nullable=True)
    
    # Usage tracking
    total_invocations = Column(Integer, default=0, nullable=False)


class WorkflowExecution(Base):
    """Pipeline execution record database model."""
    __tablename__ = "workflow_executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id = Column(String(36), ForeignKey("workflow_pipelines.id", ondelete="CASCADE"), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default=ExecutionStatus.PENDING.value)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Trigger
    trigger_type = Column(String(50), nullable=False, default=ExecutionTrigger.MANUAL.value)
    triggered_by = Column(String(36), nullable=True)
    
    # Results
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Progress tracking
    total_steps = Column(Integer, default=0, nullable=False)
    completed_steps = Column(Integer, default=0, nullable=False)
    failed_steps = Column(Integer, default=0, nullable=False)
    
    # Relationships
    pipeline = relationship("WorkflowPipeline", back_populates="executions")
    logs = relationship("WorkflowExecutionLog", back_populates="execution", cascade="all, delete-orphan")
    step_results = relationship("WorkflowStepResult", back_populates="execution", cascade="all, delete-orphan")


class WorkflowExecutionLog(Base):
    """Execution log entry database model."""
    __tablename__ = "workflow_execution_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False)
    
    step_id = Column(String(36), nullable=True)
    level = Column(String(20), nullable=False, default=LogLevel.INFO.value)
    message = Column(Text, nullable=False)
    log_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="logs")


class WorkflowStepResult(Base):
    """Individual step execution result database model."""
    __tablename__ = "workflow_step_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(String(36), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default=ExecutionStatus.PENDING.value)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Results
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Retries
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="step_results")


# ============================================================================
# PYDANTIC MODELS (API)
# ============================================================================

class PipelineCreate(BaseModel):
    """Create pipeline request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: PipelineCategory = PipelineCategory.CUSTOM
    status: PipelineStatus = PipelineStatus.DRAFT
    configuration: Dict[str, Any] = Field(default_factory=dict)


class PipelineUpdate(BaseModel):
    """Update pipeline request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[PipelineCategory] = None
    status: Optional[PipelineStatus] = None
    configuration: Optional[Dict[str, Any]] = None


class PipelineStepCreate(BaseModel):
    """Create pipeline step request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    step_type: StepType = StepType.SCRIPT
    order_index: int = Field(..., ge=0)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    condition: Optional[str] = None
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    max_retries: int = Field(default=0, ge=0, le=5)
    retry_delay_seconds: int = Field(default=10, ge=1, le=300)


class PipelineResponse(BaseModel):
    """Pipeline response model."""
    id: str
    name: str
    description: Optional[str]
    category: str
    status: str
    configuration: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time: float
    avg_compression_ratio: Optional[float]
    
    class Config:
        orm_mode = True


class ExecuteRequest(BaseModel):
    """Execute pipeline request."""
    pipeline_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    trigger_type: ExecutionTrigger = ExecutionTrigger.MANUAL


class ExecutionResponse(BaseModel):
    """Execution response model."""
    id: str
    pipeline_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    total_steps: int
    completed_steps: int
    failed_steps: int
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    
    class Config:
        orm_mode = True


class ScriptCreate(BaseModel):
    """Create script request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    language: ScriptLanguage = ScriptLanguage.PYTHON
    code: str = Field(..., min_length=1)
    parameters: List[str] = Field(default_factory=list)
    llm_integration: bool = False


class ScriptResponse(BaseModel):
    """Script response model."""
    id: str
    name: str
    description: Optional[str]
    language: str
    code: str
    parameters: List[str]
    llm_integration: bool
    version: int
    created_at: datetime
    updated_at: datetime
    is_approved: bool
    total_executions: int
    successful_executions: int
    failed_executions: int
    
    class Config:
        orm_mode = True


class HelperCreate(BaseModel):
    """Create helper request."""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    functions: List[str] = Field(..., min_items=1)
    implementation: Optional[str] = None


class HelperResponse(BaseModel):
    """Helper response model."""
    id: str
    name: str
    category: str
    description: Optional[str]
    functions: List[str]
    implementation: Optional[str]
    created_at: datetime
    total_invocations: int
    
    class Config:
        orm_mode = True


class LogEntry(BaseModel):
    """Log entry model."""
    level: LogLevel
    message: str
    log_metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime
    step_id: Optional[str] = None


class ExecutionLogsResponse(BaseModel):
    """Execution logs response."""
    execution_id: str
    total_logs: int
    logs: List[LogEntry]

