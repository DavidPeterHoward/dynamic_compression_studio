"""
Experiment models for the Dynamic Compression Algorithms backend.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.base import AsyncBase, TimestampMixin


class ExperimentType(str, Enum):
    """Types of experiments."""
    ALGORITHM = "algorithm"
    PARAMETER = "parameter"
    META_LEARNING = "meta_learning"
    SYNTHETIC = "synthetic"
    COMPARISON = "comparison"
    OPTIMIZATION = "optimization"
    CONTENT_ANALYSIS = "content_analysis"
    GENERATIVE = "generative"


class ExperimentStatus(str, Enum):
    """Status of experiments."""
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExperimentPhase(str, Enum):
    """Phases of experiment execution."""
    ANALYSIS = "analysis"
    COMPRESSION = "compression"
    DECOMPRESSION = "decompression"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"


class GenerationType(str, Enum):
    """Types of generative content."""
    SYNTHETIC = "synthetic"
    AUGMENTED = "augmented"
    TRANSFORMED = "transformed"
    ADAPTIVE = "adaptive"


class ExperimentPriority(str, Enum):
    """Priority levels for experiments."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Experiment(AsyncBase, TimestampMixin):
    """Experiment model for storing experiment information."""
    
    __tablename__ = "experiments"
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, default=ExperimentType.ALGORITHM)
    status = Column(String(50), nullable=False, default=ExperimentStatus.QUEUED)
    priority = Column(String(50), nullable=False, default=ExperimentPriority.MEDIUM)
    
    # Experiment configuration
    algorithm_id = Column(Integer, ForeignKey('algorithms.id'), nullable=True)
    parameters = Column(JSON, nullable=True)  # Algorithm parameters
    configuration = Column(JSON, nullable=True)  # Experiment configuration
    
    # Progress tracking
    current_phase = Column(String(50), nullable=True)
    phase_progress = Column(Float, default=0.0)  # 0-100
    overall_progress = Column(Float, default=0.0)  # 0-100
    processed_bytes = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)
    
    # Timing
    estimated_duration = Column(Integer, nullable=True)  # Seconds
    actual_duration = Column(Integer, nullable=True)  # Seconds
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results and metrics
    results = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    custom_metrics = Column(JSON, nullable=True)
    
    # Content information
    content_type = Column(String(100), nullable=True)
    content_size = Column(Integer, nullable=True)
    content_hash = Column(String(64), nullable=True)
    content_metadata = Column(JSON, nullable=True)
    
    # Generative content
    is_generating = Column(Boolean, default=False)
    generation_type = Column(String(50), nullable=True)
    generation_progress = Column(Float, default=0.0)
    generated_samples_count = Column(Integer, default=0)
    
    # System resources
    memory_usage = Column(Float, nullable=True)  # MB
    cpu_usage = Column(Float, nullable=True)  # Percentage
    gpu_usage = Column(Float, nullable=True)  # Percentage
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Relationships
    algorithm = relationship("Algorithm", back_populates="experiments")
    logs = relationship("ExperimentLog", back_populates="experiment", cascade="all, delete-orphan")
    content_analysis = relationship("ContentAnalysis", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    compression_progress = relationship("CompressionProgress", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    generative_content = relationship("GenerativeContent", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Experiment(name='{self.name}', type='{self.type}', status='{self.status}')>"


class ExperimentLog(AsyncBase, TimestampMixin):
    """Log entries for experiments."""
    
    __tablename__ = "experiment_logs"
    
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    level = Column(String(20), nullable=False)  # info, warning, error, debug
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    phase = Column(String(50), nullable=True)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="logs")
    
    def __repr__(self):
        return f"<ExperimentLog(experiment='{self.experiment_id}', level='{self.level}')>"


class ContentAnalysis(AsyncBase, TimestampMixin):
    """Content analysis results for experiments."""
    
    __tablename__ = "content_analysis"
    
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    
    # Content characteristics
    content_type = Column(String(100), nullable=False)
    content_size = Column(Integer, nullable=False)
    content_patterns = Column(JSON, nullable=True)  # List of detected patterns
    entropy = Column(Float, nullable=True)
    redundancy = Column(Float, nullable=True)
    structure = Column(String(100), nullable=True)
    language = Column(String(50), nullable=True)
    encoding = Column(String(50), nullable=True)
    
    # Statistical analysis
    byte_frequency = Column(JSON, nullable=True)  # Byte frequency distribution
    pattern_frequency = Column(JSON, nullable=True)  # Pattern frequency
    compression_potential = Column(Float, nullable=True)
    
    # Metadata
    content_metadata = Column(JSON, nullable=True)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="content_analysis")
    
    def __repr__(self):
        return f"<ContentAnalysis(experiment='{self.experiment_id}', type='{self.content_type}')>"


class CompressionProgress(AsyncBase, TimestampMixin):
    """Real-time compression progress tracking."""
    
    __tablename__ = "compression_progress"
    
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    
    # Current state
    current_phase = Column(String(50), nullable=False, default=ExperimentPhase.ANALYSIS)
    phase_progress = Column(Float, default=0.0)
    current_algorithm = Column(String(255), nullable=True)
    
    # Processing metrics
    processed_bytes = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)
    compression_ratio = Column(Float, nullable=True)
    processing_speed = Column(Float, nullable=True)  # MB/s
    
    # History
    compression_history = Column(JSON, nullable=True)  # List of compression attempts
    
    # Relationships
    experiment = relationship("Experiment", back_populates="compression_progress")
    
    def __repr__(self):
        return f"<CompressionProgress(experiment='{self.experiment_id}', phase='{self.current_phase}')>"


class GenerativeContent(AsyncBase, TimestampMixin):
    """Generative content information for experiments."""
    
    __tablename__ = "generative_content"
    
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    
    # Generation settings
    is_generating = Column(Boolean, default=False)
    generation_type = Column(String(50), nullable=True)
    generation_progress = Column(Float, default=0.0)
    
    # Content characteristics
    patterns = Column(JSON, nullable=True)  # Generated patterns
    complexity = Column(Float, nullable=True)
    volume = Column(Integer, default=0)  # Number of samples
    quality = Column(Float, nullable=True)
    diversity = Column(Float, nullable=True)
    
    # Generated samples
    generated_samples = Column(JSON, nullable=True)  # List of sample metadata
    
    # Relationships
    experiment = relationship("Experiment", back_populates="generative_content")
    
    def __repr__(self):
        return f"<GenerativeContent(experiment='{self.experiment_id}', type='{self.generation_type}')>"


# Pydantic models for API
class ExperimentLogCreate(BaseModel):
    """Pydantic model for creating experiment logs."""
    
    level: str = Field(..., description="Log level (info, warning, error, debug)")
    message: str = Field(..., description="Log message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional log data")
    phase: Optional[str] = Field(None, description="Current experiment phase")


class ExperimentLogResponse(ExperimentLogCreate):
    """Pydantic model for experiment log responses."""
    
    id: int
    experiment_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentAnalysisCreate(BaseModel):
    """Pydantic model for creating content analysis."""
    
    content_type: str = Field(..., description="Content type")
    content_size: int = Field(..., description="Content size in bytes")
    content_patterns: Optional[List[str]] = Field(None, description="Detected patterns")
    entropy: Optional[float] = Field(None, description="Content entropy")
    redundancy: Optional[float] = Field(None, description="Content redundancy")
    structure: Optional[str] = Field(None, description="Content structure")
    language: Optional[str] = Field(None, description="Content language")
    encoding: Optional[str] = Field(None, description="Content encoding")
    byte_frequency: Optional[Dict[str, int]] = Field(None, description="Byte frequency distribution")
    pattern_frequency: Optional[Dict[str, int]] = Field(None, description="Pattern frequency")
    compression_potential: Optional[float] = Field(None, description="Compression potential")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ContentAnalysisResponse(ContentAnalysisCreate):
    """Pydantic model for content analysis responses."""
    
    id: int
    experiment_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompressionProgressCreate(BaseModel):
    """Pydantic model for creating compression progress."""
    
    current_phase: ExperimentPhase = Field(..., description="Current compression phase")
    phase_progress: float = Field(0.0, description="Phase progress (0-100)")
    current_algorithm: Optional[str] = Field(None, description="Current algorithm being used")
    processed_bytes: int = Field(0, description="Processed bytes")
    total_bytes: int = Field(0, description="Total bytes to process")
    compression_ratio: Optional[float] = Field(None, description="Current compression ratio")
    processing_speed: Optional[float] = Field(None, description="Processing speed in MB/s")
    compression_history: Optional[List[Dict[str, Any]]] = Field(None, description="Compression history")


class CompressionProgressResponse(CompressionProgressCreate):
    """Pydantic model for compression progress responses."""
    
    id: int
    experiment_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GenerativeContentCreate(BaseModel):
    """Pydantic model for creating generative content."""
    
    is_generating: bool = Field(False, description="Whether content is being generated")
    generation_type: Optional[GenerationType] = Field(None, description="Generation type")
    generation_progress: float = Field(0.0, description="Generation progress (0-100)")
    patterns: Optional[List[str]] = Field(None, description="Generated patterns")
    complexity: Optional[float] = Field(None, description="Content complexity")
    volume: int = Field(0, description="Number of generated samples")
    quality: Optional[float] = Field(None, description="Content quality")
    diversity: Optional[float] = Field(None, description="Content diversity")
    generated_samples: Optional[List[Dict[str, Any]]] = Field(None, description="Generated samples metadata")


class GenerativeContentResponse(GenerativeContentCreate):
    """Pydantic model for generative content responses."""
    
    id: int
    experiment_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExperimentCreate(BaseModel):
    """Pydantic model for creating experiments."""
    
    name: str = Field(..., description="Experiment name")
    description: Optional[str] = Field(None, description="Experiment description")
    type: ExperimentType = Field(ExperimentType.ALGORITHM, description="Experiment type")
    priority: ExperimentPriority = Field(ExperimentPriority.MEDIUM, description="Experiment priority")
    algorithm_id: Optional[int] = Field(None, description="Algorithm ID")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Algorithm parameters")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Experiment configuration")
    content_type: Optional[str] = Field(None, description="Content type")
    content_size: Optional[int] = Field(None, description="Content size in bytes")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")


class ExperimentUpdate(BaseModel):
    """Pydantic model for updating experiments."""
    
    name: Optional[str] = Field(None, description="Experiment name")
    description: Optional[str] = Field(None, description="Experiment description")
    type: Optional[ExperimentType] = Field(None, description="Experiment type")
    priority: Optional[ExperimentPriority] = Field(None, description="Experiment priority")
    algorithm_id: Optional[int] = Field(None, description="Algorithm ID")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Algorithm parameters")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Experiment configuration")
    status: Optional[ExperimentStatus] = Field(None, description="Experiment status")
    current_phase: Optional[ExperimentPhase] = Field(None, description="Current phase")
    phase_progress: Optional[float] = Field(None, description="Phase progress")
    overall_progress: Optional[float] = Field(None, description="Overall progress")
    processed_bytes: Optional[int] = Field(None, description="Processed bytes")
    total_bytes: Optional[int] = Field(None, description="Total bytes")
    results: Optional[Dict[str, Any]] = Field(None, description="Experiment results")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Experiment metrics")
    error_message: Optional[str] = Field(None, description="Error message")


class ExperimentResponse(BaseModel):
    """Pydantic model for experiment responses."""
    
    id: int
    name: str
    description: Optional[str]
    type: ExperimentType
    status: ExperimentStatus
    priority: ExperimentPriority
    algorithm_id: Optional[int]
    parameters: Optional[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]]
    current_phase: Optional[str]
    phase_progress: float
    overall_progress: float
    processed_bytes: int
    total_bytes: int
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    results: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    custom_metrics: Optional[Dict[str, Any]]
    content_type: Optional[str]
    content_size: Optional[int]
    content_hash: Optional[str]
    content_metadata: Optional[Dict[str, Any]]
    is_generating: bool
    generation_type: Optional[str]
    generation_progress: float
    generated_samples_count: int
    memory_usage: Optional[float]
    cpu_usage: Optional[float]
    gpu_usage: Optional[float]
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    content_analysis: Optional[ContentAnalysisResponse] = None
    compression_progress: Optional[CompressionProgressResponse] = None
    generative_content: Optional[GenerativeContentResponse] = None
    logs: List[ExperimentLogResponse] = []
    
    class Config:
        from_attributes = True


class ExperimentStartRequest(BaseModel):
    """Pydantic model for starting experiments."""
    
    content_data: Optional[bytes] = Field(None, description="Content data to process")
    content_file_path: Optional[str] = Field(None, description="Path to content file")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class ExperimentPauseRequest(BaseModel):
    """Pydantic model for pausing experiments."""
    
    reason: Optional[str] = Field(None, description="Reason for pausing")


class ExperimentResumeRequest(BaseModel):
    """Pydantic model for resuming experiments."""
    
    parameters: Optional[Dict[str, Any]] = Field(None, description="Updated parameters")


class ExperimentStopRequest(BaseModel):
    """Pydantic model for stopping experiments."""
    
    reason: Optional[str] = Field(None, description="Reason for stopping")
    save_results: bool = Field(True, description="Whether to save results")


class ExperimentListResponse(BaseModel):
    """Pydantic model for experiment list responses."""
    
    experiments: List[ExperimentResponse]
    total: int
    page: int
    size: int
    pages: int
