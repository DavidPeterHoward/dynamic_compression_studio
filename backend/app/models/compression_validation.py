"""
Comprehensive Compression Validation Models

Database schema and validation models for storing and verifying
compression algorithm test results across all content types with
multi-dimensional parameter tracking and accuracy validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    JSON, Text, ForeignKey, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
try:
    from app.database.base import Base
except ImportError:
    from app.database import Base
import hashlib
import json


# ============================================================================
# ENUMS
# ============================================================================

class ContentCategory(str, Enum):
    """Content category types."""
    TEXT = "text"
    DATA = "data"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    BINARY = "binary"
    MIXED = "mixed"


class DataOrigin(str, Enum):
    """Origin of test data."""
    SYNTHETIC = "synthetic"
    REAL_WORLD = "real_world"
    BENCHMARK = "benchmark"
    USER_PROVIDED = "user_provided"


class ValidationStatus(str, Enum):
    """Validation result status."""
    VERIFIED = "verified"
    FAILED = "failed"
    PENDING = "pending"
    SUSPICIOUS = "suspicious"


# ============================================================================
# DATABASE MODELS
# ============================================================================

class CompressionTestResult(Base):
    """
    Comprehensive compression test result storage.
    Tracks all datapoints for compression algorithm performance.
    """
    __tablename__ = "compression_test_results"
    
    # Primary identification
    id = Column(String(36), primary_key=True)
    test_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Algorithm details
    algorithm = Column(String(50), nullable=False, index=True)
    algorithm_version = Column(String(20), default="1.0.0")
    parameters = Column(JSON, nullable=False, default=dict)
    
    # Content identification
    content_sha256 = Column(String(64), nullable=False, index=True)
    content_category = Column(String(20), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    content_subtype = Column(String(50), nullable=True)
    data_origin = Column(String(20), nullable=False, index=True)
    
    # Size metrics
    original_size = Column(Integer, nullable=False)
    compressed_size = Column(Integer, nullable=False)
    compression_ratio = Column(Float, nullable=False)
    compression_percentage = Column(Float, nullable=False)
    
    # Performance metrics
    compression_time_ms = Column(Float, nullable=False)
    decompression_time_ms = Column(Float, nullable=True)
    throughput_mbps = Column(Float, nullable=False)
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    
    # Quality metrics
    quality_score = Column(Float, nullable=False)
    efficiency_score = Column(Float, nullable=False)
    data_integrity_score = Column(Float, default=1.0)
    
    # Content characteristics
    entropy = Column(Float, nullable=True)
    redundancy = Column(Float, nullable=True)
    pattern_complexity = Column(Float, nullable=True)
    
    # Validation
    validation_status = Column(String(20), default=ValidationStatus.PENDING.value)
    validation_hash = Column(String(64), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Success/failure tracking
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Multi-dimensional parameters
    dimensions = Column(JSON, nullable=False, default=dict)
    
    # Metadata
    tags = Column(JSON, default=list)
    annotations = Column(JSON, default=dict)
    
    # Relationships
    content_samples = relationship("ContentSample", back_populates="test_result")
    dimensional_metrics = relationship("DimensionalMetric", back_populates="test_result")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('original_size >= 0', name='check_original_size_positive'),
        CheckConstraint('compressed_size >= 0', name='check_compressed_size_positive'),
        CheckConstraint('compression_ratio >= 1.0', name='check_ratio_min'),
        CheckConstraint('compression_percentage >= 0 AND compression_percentage <= 100', 
                       name='check_percentage_range'),
        Index('idx_algorithm_category', 'algorithm', 'content_category'),
        Index('idx_origin_timestamp', 'data_origin', 'test_timestamp'),
    )


class ContentSample(Base):
    """
    Stores actual content samples or references for verification.
    """
    __tablename__ = "content_samples"
    
    id = Column(String(36), primary_key=True)
    test_result_id = Column(String(36), ForeignKey("compression_test_results.id"), nullable=False)
    
    # Content data
    content_sha256 = Column(String(64), nullable=False, index=True)
    sample_size = Column(Integer, nullable=False)
    sample_preview = Column(Text, nullable=True)  # First 1KB for text content
    
    # Storage reference
    storage_path = Column(String(500), nullable=True)  # For large files
    is_stored = Column(Boolean, default=False)
    
    # Content properties
    mime_type = Column(String(100), nullable=True)
    encoding = Column(String(50), nullable=True)
    language = Column(String(20), nullable=True)
    
    # Media-specific properties (for video/audio/image)
    resolution = Column(String(50), nullable=True)  # e.g., "1920x1080" for video/image
    duration_seconds = Column(Float, nullable=True)  # For video/audio
    bitrate = Column(Integer, nullable=True)  # For video/audio
    codec = Column(String(50), nullable=True)
    color_space = Column(String(50), nullable=True)  # For video/image
    sample_rate = Column(Integer, nullable=True)  # For audio
    channels = Column(Integer, nullable=True)  # For audio
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    test_result = relationship("CompressionTestResult", back_populates="content_samples")


class DimensionalMetric(Base):
    """
    Stores multi-dimensional performance metrics.
    """
    __tablename__ = "dimensional_metrics"
    
    id = Column(String(36), primary_key=True)
    test_result_id = Column(String(36), ForeignKey("compression_test_results.id"), nullable=False)
    
    dimension_name = Column(String(100), nullable=False)
    dimension_category = Column(String(50), nullable=False)  # content, performance, quality
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    
    # Statistical validation
    confidence_level = Column(Float, default=0.95)
    standard_deviation = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    
    # Relationship
    test_result = relationship("CompressionTestResult", back_populates="dimensional_metrics")
    
    __table_args__ = (
        Index('idx_dimension_category', 'dimension_name', 'dimension_category'),
    )


class AlgorithmPerformanceBaseline(Base):
    """
    Stores baseline performance metrics for each algorithm and content type.
    Used for comparative analysis and anomaly detection.
    """
    __tablename__ = "algorithm_performance_baselines"
    
    id = Column(String(36), primary_key=True)
    algorithm = Column(String(50), nullable=False, index=True)
    content_category = Column(String(20), nullable=False, index=True)
    
    # Aggregated metrics
    test_count = Column(Integer, default=0)
    avg_compression_ratio = Column(Float, nullable=False)
    avg_compression_time_ms = Column(Float, nullable=False)
    avg_throughput_mbps = Column(Float, nullable=False)
    avg_quality_score = Column(Float, nullable=False)
    
    # Statistical measures
    std_compression_ratio = Column(Float, nullable=True)
    min_compression_ratio = Column(Float, nullable=True)
    max_compression_ratio = Column(Float, nullable=True)
    
    # Performance percentiles
    percentile_25_ratio = Column(Float, nullable=True)
    percentile_50_ratio = Column(Float, nullable=True)
    percentile_75_ratio = Column(Float, nullable=True)
    percentile_90_ratio = Column(Float, nullable=True)
    percentile_95_ratio = Column(Float, nullable=True)
    
    # Last update
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_algo_category_baseline', 'algorithm', 'content_category'),
    )


class DataIntegrityCheck(Base):
    """
    Tracks data integrity verification results.
    """
    __tablename__ = "data_integrity_checks"
    
    id = Column(String(36), primary_key=True)
    test_result_id = Column(String(36), ForeignKey("compression_test_results.id"), nullable=False)
    
    # Verification details
    check_timestamp = Column(DateTime, default=datetime.utcnow)
    check_type = Column(String(50), nullable=False)  # hash, byte_comparison, decompression
    
    # Results
    passed = Column(Boolean, nullable=False)
    confidence_score = Column(Float, default=1.0)
    
    # Hash comparisons
    original_hash = Column(String(64), nullable=True)
    decompressed_hash = Column(String(64), nullable=True)
    hash_match = Column(Boolean, nullable=True)
    
    # Byte-level verification
    bytes_verified = Column(Integer, nullable=True)
    bytes_matched = Column(Integer, nullable=True)
    match_percentage = Column(Float, nullable=True)
    
    # Additional details
    details = Column(JSON, default=dict)


# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class ContentCharacteristics(BaseModel):
    """Content analysis characteristics."""
    entropy: float = Field(ge=0.0, le=1.0, description="Content entropy")
    redundancy: float = Field(ge=0.0, le=1.0, description="Data redundancy")
    pattern_complexity: float = Field(ge=0.0, le=1.0, description="Pattern complexity")
    compressibility_score: float = Field(ge=0.0, le=10.0, description="Estimated compressibility")
    
    # Optional media-specific characteristics
    resolution: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None


class CompressionMetrics(BaseModel):
    """Comprehensive compression metrics."""
    original_size: int = Field(ge=0, description="Original size in bytes")
    compressed_size: int = Field(ge=0, description="Compressed size in bytes")
    compression_ratio: float = Field(ge=1.0, description="Compression ratio")
    compression_percentage: float = Field(ge=0.0, le=100.0, description="Size reduction %")
    
    # Performance
    compression_time_ms: float = Field(ge=0.0, description="Compression time")
    decompression_time_ms: Optional[float] = Field(None, ge=0.0, description="Decompression time")
    throughput_mbps: float = Field(ge=0.0, description="Throughput MB/s")
    memory_usage_mb: Optional[float] = Field(None, ge=0.0, description="Memory usage")
    cpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage")
    
    # Quality
    quality_score: float = Field(ge=0.0, le=1.0, description="Quality score")
    efficiency_score: float = Field(ge=0.0, description="Efficiency score")
    data_integrity_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Integrity score")


class ValidationResult(BaseModel):
    """Validation result for compression test."""
    validation_status: ValidationStatus
    validation_hash: str
    verified_at: datetime
    
    # Verification details
    hash_verified: bool
    decompression_verified: bool
    byte_match_percentage: float = Field(ge=0.0, le=100.0)
    
    # Confidence
    overall_confidence: float = Field(ge=0.0, le=1.0)
    
    # Anomalies detected
    anomalies_detected: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ComprehensiveTestRecord(BaseModel):
    """Complete compression test record."""
    # Identification
    test_id: str
    test_timestamp: datetime
    
    # Algorithm
    algorithm: str
    algorithm_version: str = "1.0.0"
    parameters: Dict[str, Any]
    
    # Content
    content_sha256: str
    content_category: ContentCategory
    content_type: str
    content_subtype: Optional[str] = None
    data_origin: DataOrigin
    content_characteristics: ContentCharacteristics
    
    # Metrics
    metrics: CompressionMetrics
    
    # Validation
    validation: ValidationResult
    
    # Multi-dimensional data
    dimensions: Dict[str, float]
    
    # Status
    success: bool
    error_message: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    annotations: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content_sha256')
    def validate_sha256(cls, v):
        if len(v) != 64 or not all(c in '0123456789abcdef' for c in v.lower()):
            raise ValueError("Invalid SHA-256 hash")
        return v.lower()
    
    @validator('metrics')
    def validate_metrics(cls, v):
        if v and v.compression_ratio < 1.0:
            raise ValueError("Compression ratio must be >= 1.0")
        return v


class VerificationRequest(BaseModel):
    """Request to verify compression results."""
    test_id: str
    verification_type: str = Field(..., description="hash, decompression, or full")
    include_statistical_analysis: bool = False


class VerificationResponse(BaseModel):
    """Response from verification."""
    test_id: str
    verified: bool
    verification_timestamp: datetime
    validation_result: ValidationResult
    
    # Statistical analysis (if requested)
    statistical_summary: Optional[Dict[str, Any]] = None
    baseline_comparison: Optional[Dict[str, Any]] = None
    anomaly_score: Optional[float] = None


class AccuracyReport(BaseModel):
    """Comprehensive accuracy report."""
    report_id: str
    generated_at: datetime
    
    # Scope
    algorithm: Optional[str] = None
    content_category: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    
    # Statistics
    total_tests: int
    verified_tests: int
    failed_tests: int
    accuracy_percentage: float
    
    # Detailed metrics
    average_compression_ratio: float
    average_throughput: float
    average_quality_score: float
    
    # Anomalies
    anomalies_detected: List[Dict[str, Any]]
    suspicious_results: List[Dict[str, Any]]
    
    # Confidence
    overall_confidence: float
    data_quality_score: float


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compute_validation_hash(test_record: ComprehensiveTestRecord) -> str:
    """Compute validation hash for test record."""
    data = {
        'test_id': test_record.test_id,
        'algorithm': test_record.algorithm,
        'content_sha256': test_record.content_sha256,
        'original_size': test_record.metrics.original_size,
        'compressed_size': test_record.metrics.compressed_size,
        'compression_ratio': round(test_record.metrics.compression_ratio, 6),
        'timestamp': test_record.test_timestamp.isoformat()
    }
    
    hash_input = json.dumps(data, sort_keys=True)
    return hashlib.sha256(hash_input.encode()).hexdigest()


def validate_compression_ratio(original_size: int, compressed_size: int, 
                               reported_ratio: float, tolerance: float = 0.01) -> bool:
    """
    Validate that reported compression ratio matches actual sizes.
    
    Args:
        original_size: Original content size
        compressed_size: Compressed content size
        reported_ratio: Reported compression ratio
        tolerance: Acceptable error margin
    
    Returns:
        True if ratio is accurate within tolerance
    """
    if compressed_size == 0:
        return False
    
    calculated_ratio = original_size / compressed_size
    error = abs(calculated_ratio - reported_ratio) / calculated_ratio
    
    return error <= tolerance


def validate_compression_percentage(original_size: int, compressed_size: int,
                                   reported_percentage: float, tolerance: float = 0.5) -> bool:
    """
    Validate that reported compression percentage matches actual sizes.
    
    Args:
        original_size: Original content size
        compressed_size: Compressed content size
        reported_percentage: Reported compression percentage
        tolerance: Acceptable error margin in percentage points
    
    Returns:
        True if percentage is accurate within tolerance
    """
    if original_size == 0:
        return False
    
    calculated_percentage = ((original_size - compressed_size) / original_size) * 100
    error = abs(calculated_percentage - reported_percentage)
    
    return error <= tolerance

