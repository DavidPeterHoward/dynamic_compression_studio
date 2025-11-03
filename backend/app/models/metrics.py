"""
Pydantic models for metrics and analytics data structures.
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime


class MetricType(str, Enum):
    """Types of metrics."""
    
    COMPRESSION_RATIO = "compression_ratio"
    COMPRESSION_SPEED = "compression_speed"
    DECOMPRESSION_SPEED = "decompression_speed"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    QUALITY_SCORE = "quality_score"
    INFORMATION_PRESERVATION = "information_preservation"
    ENTROPY_REDUCTION = "entropy_reduction"
    PATTERN_EFFICIENCY = "pattern_efficiency"
    ALGORITHM_EFFICIENCY = "algorithm_efficiency"


class TimeRange(str, Enum):
    """Time range for metrics aggregation."""
    
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class CompressionMetrics(BaseModel):
    """Model for compression performance metrics."""
    
    # Basic compression metrics
    compression_ratio: float = Field(..., description="Compression ratio achieved")
    compression_percentage: float = Field(..., description="Compression percentage")
    original_size: int = Field(..., description="Original data size in bytes")
    compressed_size: int = Field(..., description="Compressed data size in bytes")
    
    # Speed metrics
    compression_time: float = Field(..., description="Compression time in seconds")
    compression_speed: float = Field(..., description="Compression speed in MB/s")
    decompression_time: Optional[float] = Field(default=None, description="Decompression time in seconds")
    decompression_speed: Optional[float] = Field(default=None, description="Decompression speed in MB/s")
    
    # Resource usage
    memory_usage: Optional[int] = Field(default=None, description="Memory usage in bytes")
    cpu_usage: Optional[float] = Field(default=None, description="CPU usage percentage")
    peak_memory: Optional[int] = Field(default=None, description="Peak memory usage in bytes")
    
    # Quality metrics
    quality_score: Optional[float] = Field(default=None, description="Quality preservation score (0-1)")
    information_preservation: Optional[float] = Field(default=None, description="Information preservation ratio")
    round_trip_integrity: Optional[bool] = Field(default=None, description="Round-trip integrity check")
    
    # Advanced metrics
    entropy_reduction: Optional[float] = Field(default=None, description="Entropy reduction achieved")
    pattern_efficiency: Optional[float] = Field(default=None, description="Pattern detection efficiency")
    algorithm_efficiency: Optional[float] = Field(default=None, description="Algorithm efficiency score")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When metrics were collected")
    
    @validator('compression_speed')
    def calculate_compression_speed(cls, v, values):
        if 'original_size' in values and 'compression_time' in values and values['compression_time'] > 0:
            return (values['original_size'] / 1024 / 1024) / values['compression_time']
        return v
    
    @validator('decompression_speed')
    def calculate_decompression_speed(cls, v, values):
        if 'compressed_size' in values and 'decompression_time' in values and values['decompression_time'] and values['decompression_time'] > 0:
            return (values['compressed_size'] / 1024 / 1024) / values['decompression_time']
        return v


class PerformanceMetrics(BaseModel):
    """Model for system performance metrics."""
    
    # System metrics
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_usage: Optional[float] = Field(default=None, description="Network usage in MB/s")
    
    # Application metrics
    active_connections: int = Field(..., description="Number of active connections")
    requests_per_second: float = Field(..., description="Requests per second")
    average_response_time: float = Field(..., description="Average response time in milliseconds")
    error_rate: float = Field(..., description="Error rate percentage")
    
    # Queue metrics
    queue_size: int = Field(..., description="Current queue size")
    queue_processing_rate: float = Field(..., description="Queue processing rate")
    average_wait_time: float = Field(..., description="Average wait time in seconds")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When metrics were collected")


class QualityMetrics(BaseModel):
    """Model for quality assessment metrics."""
    
    # Content quality
    content_integrity: float = Field(..., description="Content integrity score (0-1)")
    semantic_preservation: Optional[float] = Field(default=None, description="Semantic preservation score")
    structural_integrity: Optional[float] = Field(default=None, description="Structural integrity score")
    
    # Compression quality
    loss_ratio: float = Field(..., description="Information loss ratio")
    distortion_measure: Optional[float] = Field(default=None, description="Distortion measure")
    fidelity_score: Optional[float] = Field(default=None, description="Fidelity score")
    
    # Domain-specific quality
    text_quality: Optional[float] = Field(default=None, description="Text quality score")
    code_quality: Optional[float] = Field(default=None, description="Code quality score")
    binary_quality: Optional[float] = Field(default=None, description="Binary quality score")
    
    # Validation metrics
    validation_passed: bool = Field(..., description="Whether validation passed")
    validation_errors: Optional[List[str]] = Field(default=None, description="Validation errors")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When metrics were collected")


class AlgorithmMetrics(BaseModel):
    """Model for algorithm-specific metrics."""
    
    algorithm_name: str = Field(..., description="Algorithm name")
    
    # Performance metrics
    success_rate: float = Field(..., description="Success rate percentage")
    average_compression_ratio: float = Field(..., description="Average compression ratio")
    average_compression_time: float = Field(..., description="Average compression time")
    average_memory_usage: float = Field(..., description="Average memory usage")
    
    # Quality metrics
    average_quality_score: float = Field(..., description="Average quality score")
    average_information_preservation: float = Field(..., description="Average information preservation")
    
    # Usage statistics
    total_uses: int = Field(..., description="Total number of uses")
    successful_uses: int = Field(..., description="Number of successful uses")
    failed_uses: int = Field(..., description="Number of failed uses")
    
    # Content type performance
    content_type_performance: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, 
        description="Performance by content type"
    )
    
    # Timestamps
    last_used: Optional[datetime] = Field(default=None, description="Last time algorithm was used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When metrics were created")


class MetricsAggregation(BaseModel):
    """Model for aggregated metrics."""
    
    # Aggregation parameters
    metric_type: MetricType = Field(..., description="Type of metric being aggregated")
    time_range: TimeRange = Field(..., description="Time range for aggregation")
    start_time: datetime = Field(..., description="Start time of aggregation period")
    end_time: datetime = Field(..., description="End time of aggregation period")
    
    # Aggregated values
    count: int = Field(..., description="Number of data points")
    min_value: float = Field(..., description="Minimum value")
    max_value: float = Field(..., description="Maximum value")
    mean_value: float = Field(..., description="Mean value")
    median_value: float = Field(..., description="Median value")
    std_deviation: float = Field(..., description="Standard deviation")
    
    # Percentiles
    p25: float = Field(..., description="25th percentile")
    p75: float = Field(..., description="75th percentile")
    p90: float = Field(..., description="90th percentile")
    p95: float = Field(..., description="95th percentile")
    p99: float = Field(..., description="99th percentile")
    
    # Additional statistics
    total_value: float = Field(..., description="Total value")
    variance: float = Field(..., description="Variance")
    
    # Metadata
    algorithm_filter: Optional[str] = Field(default=None, description="Algorithm filter applied")
    content_type_filter: Optional[str] = Field(default=None, description="Content type filter applied")


class MetricsComparison(BaseModel):
    """Model for comparing metrics across algorithms or time periods."""
    
    # Comparison parameters
    comparison_type: str = Field(..., description="Type of comparison (algorithm, time, content_type)")
    baseline: str = Field(..., description="Baseline for comparison")
    comparison_targets: List[str] = Field(..., description="Targets to compare against")
    
    # Comparison results
    relative_performance: Dict[str, float] = Field(..., description="Relative performance compared to baseline")
    absolute_differences: Dict[str, float] = Field(..., description="Absolute differences from baseline")
    percentage_differences: Dict[str, float] = Field(..., description="Percentage differences from baseline")
    
    # Statistical significance
    confidence_intervals: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, 
        description="Confidence intervals for differences"
    )
    p_values: Dict[str, float] = Field(default_factory=dict, description="P-values for statistical tests")
    
    # Rankings
    rankings: Dict[str, int] = Field(..., description="Rankings of algorithms/periods")
    best_performer: str = Field(..., description="Best performing algorithm/period")
    worst_performer: str = Field(..., description="Worst performing algorithm/period")
    
    # Timestamps
    comparison_date: datetime = Field(default_factory=datetime.utcnow, description="When comparison was performed")


class MetricsRequest(BaseModel):
    """Request model for metrics queries."""
    
    # Query parameters
    metric_types: Optional[List[MetricType]] = Field(default=None, description="Types of metrics to retrieve")
    algorithms: Optional[List[str]] = Field(default=None, description="Algorithms to filter by")
    content_types: Optional[List[str]] = Field(default=None, description="Content types to filter by")
    
    # Time range
    start_time: Optional[datetime] = Field(default=None, description="Start time for metrics")
    end_time: Optional[datetime] = Field(default=None, description="End time for metrics")
    time_range: Optional[TimeRange] = Field(default=None, description="Time range for aggregation")
    
    # Aggregation
    aggregate: bool = Field(default=False, description="Whether to aggregate metrics")
    group_by: Optional[List[str]] = Field(default=None, description="Fields to group by")
    
    # Pagination
    page: int = Field(default=1, description="Page number")
    page_size: int = Field(default=100, description="Page size")
    
    # Sorting
    sort_by: Optional[str] = Field(default="timestamp", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc/desc)")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be at least 1')
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Page size must be between 1 and 1000')
        return v






