"""
Database models for synthetic media storage and management.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
import uuid

from app.database.base import AsyncBase, TimestampMixin


class MediaType(str, Enum):
    """Types of synthetic media."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DATA = "data"


class GenerationStatus(str, Enum):
    """Status of media generation."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyntheticMedia(AsyncBase, TimestampMixin):
    """Main table for storing synthetic media metadata."""
    
    __tablename__ = "synthetic_media"
    
    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Media type and format
    media_type = Column(String(50), nullable=False, index=True)
    format = Column(String(20), nullable=False)  # png, mp4, wav, etc.
    mime_type = Column(String(100), nullable=False)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    
    # Generation parameters
    generation_parameters = Column(JSON, nullable=False)
    schema_definition = Column(JSON, nullable=False)
    
    # Analysis and metrics
    analysis_results = Column(JSON, nullable=True)
    compression_metrics = Column(JSON, nullable=True)
    
    # Status and metadata
    status = Column(String(20), default=GenerationStatus.PENDING)
    processing_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Experiment linkage
    experiment_id = Column(String(36), nullable=True, index=True)
    batch_id = Column(String(36), nullable=True, index=True)
    
    # Tags and categorization
    tags = Column(JSON, nullable=True)  # List of tags
    category = Column(String(100), nullable=True, index=True)
    
    # Quality and complexity metrics
    complexity_score = Column(Float, nullable=True)
    entropy_score = Column(Float, nullable=True)
    redundancy_score = Column(Float, nullable=True)
    
    # Relationships
    generations = relationship("SyntheticMediaGeneration", back_populates="media", cascade="all, delete-orphan")
    compressions = relationship("SyntheticMediaCompression", back_populates="media", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_synthetic_media_type_status', 'media_type', 'status'),
        Index('idx_synthetic_media_experiment', 'experiment_id', 'created_at'),
        Index('idx_synthetic_media_batch', 'batch_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SyntheticMedia(id='{self.id}', name='{self.name}', type='{self.media_type}')>"


class SyntheticMediaGeneration(AsyncBase, TimestampMixin):
    """Track generation history and parameters."""
    
    __tablename__ = "synthetic_media_generations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id = Column(String(36), ForeignKey("synthetic_media.id"), nullable=False)
    
    # Generation details
    generation_type = Column(String(50), nullable=False)  # fractal, noise, etc.
    algorithm_used = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=False)
    
    # Performance metrics
    generation_time = Column(Float, nullable=False)
    memory_used = Column(Integer, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    
    # Quality metrics
    quality_score = Column(Float, nullable=True)
    complexity_achieved = Column(Float, nullable=True)
    entropy_achieved = Column(Float, nullable=True)
    
    # Relationships
    media = relationship("SyntheticMedia", back_populates="generations")
    
    def __repr__(self):
        return f"<SyntheticMediaGeneration(id='{self.id}', media_id='{self.media_id}', type='{self.generation_type}')>"


class SyntheticMediaCompression(AsyncBase, TimestampMixin):
    """Track compression experiments on synthetic media."""
    
    __tablename__ = "synthetic_media_compressions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id = Column(String(36), ForeignKey("synthetic_media.id"), nullable=False)
    
    # Compression details
    algorithm = Column(String(50), nullable=False)
    compression_level = Column(Integer, nullable=False)
    parameters = Column(JSON, nullable=False)
    
    # Results
    original_size = Column(Integer, nullable=False)
    compressed_size = Column(Integer, nullable=False)
    compression_ratio = Column(Float, nullable=False)
    compression_percentage = Column(Float, nullable=False)
    
    # Performance
    compression_time = Column(Float, nullable=False)
    decompression_time = Column(Float, nullable=True)
    
    # Quality preservation
    quality_preserved = Column(Float, nullable=True)
    information_preserved = Column(Float, nullable=True)
    
    # Relationships
    media = relationship("SyntheticMedia", back_populates="compressions")
    
    def __repr__(self):
        return f"<SyntheticMediaCompression(id='{self.id}', media_id='{self.media_id}', algorithm='{self.algorithm}')>"


class SyntheticDataBatch(AsyncBase, TimestampMixin):
    """Track batches of synthetic data generation."""
    
    __tablename__ = "synthetic_data_batches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Batch parameters
    media_type = Column(String(50), nullable=False)
    count = Column(Integer, nullable=False)
    parameters = Column(JSON, nullable=False)
    
    # Status tracking
    status = Column(String(20), default=GenerationStatus.PENDING)
    completed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Results summary
    total_size = Column(Integer, nullable=True)
    average_processing_time = Column(Float, nullable=True)
    quality_metrics = Column(JSON, nullable=True)
    
    # Experiment linkage
    experiment_id = Column(String(36), nullable=True, index=True)
    
    def __repr__(self):
        return f"<SyntheticDataBatch(id='{self.id}', name='{self.name}', count='{self.count}')>"


class SyntheticDataSchema(AsyncBase, TimestampMixin):
    """Store reusable schema definitions for synthetic data generation."""
    
    __tablename__ = "synthetic_data_schemas"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Schema definition
    media_type = Column(String(50), nullable=False)
    schema_definition = Column(JSON, nullable=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Tags and categorization
    tags = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Versioning
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<SyntheticDataSchema(id='{self.id}', name='{self.name}', type='{self.media_type}')>"


class SyntheticDataExperiment(AsyncBase, TimestampMixin):
    """Link synthetic data to experiments and track usage."""
    
    __tablename__ = "synthetic_data_experiments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), nullable=False, index=True)
    media_id = Column(String(36), ForeignKey("synthetic_media.id"), nullable=False)
    
    # Usage context
    usage_type = Column(String(50), nullable=False)  # training, testing, validation
    phase = Column(String(50), nullable=False)  # baseline, optimization, comparison
    
    # Results and metrics
    performance_metrics = Column(JSON, nullable=True)
    contribution_score = Column(Float, nullable=True)
    
    # Relationships
    media = relationship("SyntheticMedia")
    
    def __repr__(self):
        return f"<SyntheticDataExperiment(id='{self.id}', experiment_id='{self.experiment_id}', media_id='{self.media_id}')>"
