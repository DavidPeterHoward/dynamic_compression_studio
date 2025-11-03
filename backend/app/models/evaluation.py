"""
Evaluation models for the Dynamic Compression Algorithms backend.

This module defines Pydantic models for evaluation data structures,
including metrics, filters, and response schemas for the evaluation API.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class TimeRange(str, Enum):
    """Time range options for evaluation queries."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


class MetricType(str, Enum):
    """Types of metrics for evaluation."""
    ALGORITHM_PERFORMANCE = "algorithm_performance"
    SYSTEM_PERFORMANCE = "system_performance"
    CONTENT_ANALYSIS = "content_analysis"
    EXPERIMENTAL_RESULTS = "experimental_results"
    QUALITY_METRICS = "quality_metrics"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    SENSOR_FUSION = "sensor_fusion"


class EvaluationView(str, Enum):
    """Available evaluation views."""
    OVERVIEW = "overview"
    ALGORITHMS = "algorithms"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    EXPERIMENTS = "experiments"
    COMPARISON = "comparison"
    TRENDS = "trends"
    FUSION = "fusion"


class AlgorithmPerformanceMetrics(BaseModel):
    """Algorithm performance metrics."""
    algorithm_name: str = Field(..., description="Name of the algorithm")
    compression_ratio: float = Field(..., description="Average compression ratio")
    compression_speed: float = Field(..., description="Compression speed in MB/s")
    memory_usage: float = Field(..., description="Memory usage in MB")
    accuracy: float = Field(..., description="Compression accuracy percentage")
    efficiency: float = Field(..., description="Overall efficiency score")
    reliability: float = Field(..., description="Reliability score")
    adaptability: float = Field(..., description="Adaptability score")
    quality: float = Field(..., description="Quality score")
    throughput: float = Field(..., description="Throughput in operations/second")
    success_rate: float = Field(..., description="Success rate percentage")
    total_operations: int = Field(..., description="Total number of operations")
    average_processing_time: float = Field(..., description="Average processing time in seconds")


class SystemPerformanceMetrics(BaseModel):
    """System performance metrics."""
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_usage: float = Field(..., description="Network usage percentage")
    gpu_usage: Optional[float] = Field(None, description="GPU usage percentage")
    temperature: Optional[float] = Field(None, description="System temperature in Celsius")
    power_consumption: Optional[float] = Field(None, description="Power consumption in watts")
    response_time: float = Field(..., description="Average response time in milliseconds")
    throughput: float = Field(..., description="System throughput in requests/second")
    error_rate: float = Field(..., description="Error rate percentage")
    availability: float = Field(..., description="System availability percentage")


class ContentAnalysisMetrics(BaseModel):
    """Content analysis metrics."""
    total_files: int = Field(..., description="Total number of files processed")
    total_size: int = Field(..., description="Total size in bytes")
    content_types: Dict[str, int] = Field(..., description="Distribution of content types")
    complexity_scores: Dict[str, float] = Field(..., description="Complexity scores by type")
    entropy_distribution: Dict[str, float] = Field(..., description="Entropy distribution")
    average_file_size: float = Field(..., description="Average file size in bytes")
    largest_file_size: int = Field(..., description="Largest file size in bytes")
    smallest_file_size: int = Field(..., description="Smallest file size in bytes")


class ExperimentalResults(BaseModel):
    """Experimental results metrics."""
    total_experiments: int = Field(..., description="Total number of experiments")
    successful_experiments: int = Field(..., description="Number of successful experiments")
    failed_experiments: int = Field(..., description="Number of failed experiments")
    meta_learning_progress: float = Field(..., description="Meta-learning progress percentage")
    synthetic_data_generated: int = Field(..., description="Amount of synthetic data generated")
    algorithm_evolutions: int = Field(..., description="Number of algorithm evolutions")
    performance_improvements: Dict[str, float] = Field(..., description="Performance improvements by metric")
    innovation_score: float = Field(..., description="Overall innovation score")
    experiment_success_rate: float = Field(..., description="Experiment success rate percentage")


class QualityMetrics(BaseModel):
    """Quality metrics."""
    overall_quality: float = Field(..., description="Overall quality score")
    compression_quality: float = Field(..., description="Compression quality score")
    decompression_quality: float = Field(..., description="Decompression quality score")
    data_integrity: float = Field(..., description="Data integrity score")
    consistency: float = Field(..., description="Consistency score")
    reliability: float = Field(..., description="Reliability score")
    user_satisfaction: float = Field(..., description="User satisfaction score")
    accuracy: float = Field(..., description="Accuracy score")


class ComparativeAnalysis(BaseModel):
    """Comparative analysis results."""
    algorithm_ranking: List[Dict[str, Any]] = Field(..., description="Ranked list of algorithms")
    performance_comparison: Dict[str, Dict[str, float]] = Field(..., description="Performance comparison matrix")
    efficiency_analysis: Dict[str, float] = Field(..., description="Efficiency analysis by algorithm")
    quality_comparison: Dict[str, float] = Field(..., description="Quality comparison by algorithm")
    cost_benefit_analysis: Dict[str, Dict[str, float]] = Field(..., description="Cost-benefit analysis")


class SensorFusionMetrics(BaseModel):
    """Sensor fusion metrics."""
    multi_modal_data: Dict[str, Any] = Field(..., description="Multi-modal data integration")
    cross_validation_scores: Dict[str, float] = Field(..., description="Cross-validation scores")
    ensemble_scores: Dict[str, float] = Field(..., description="Ensemble method scores")
    confidence_intervals: Dict[str, Dict[str, float]] = Field(..., description="Confidence intervals")
    fusion_accuracy: float = Field(..., description="Fusion accuracy score")
    data_correlation: Dict[str, float] = Field(..., description="Data correlation scores")


class EvaluationMetrics(BaseModel):
    """Comprehensive evaluation metrics."""
    algorithm_performance: List[AlgorithmPerformanceMetrics] = Field(..., description="Algorithm performance metrics")
    system_performance: SystemPerformanceMetrics = Field(..., description="System performance metrics")
    content_analysis: ContentAnalysisMetrics = Field(..., description="Content analysis metrics")
    experimental_results: ExperimentalResults = Field(..., description="Experimental results")
    quality_metrics: QualityMetrics = Field(..., description="Quality metrics")
    comparative_analysis: ComparativeAnalysis = Field(..., description="Comparative analysis")
    sensor_fusion: SensorFusionMetrics = Field(..., description="Sensor fusion metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of evaluation")
    time_range: TimeRange = Field(..., description="Time range for evaluation")


class EvaluationFilters(BaseModel):
    """Filters for evaluation queries."""
    time_range: TimeRange = Field(TimeRange.DAY, description="Time range for evaluation")
    start_date: Optional[datetime] = Field(None, description="Custom start date")
    end_date: Optional[datetime] = Field(None, description="Custom end date")
    algorithms: Optional[List[str]] = Field(None, description="Filter by specific algorithms")
    content_types: Optional[List[str]] = Field(None, description="Filter by content types")
    min_compression_ratio: Optional[float] = Field(None, description="Minimum compression ratio")
    max_compression_ratio: Optional[float] = Field(None, description="Maximum compression ratio")
    min_quality_score: Optional[float] = Field(None, description="Minimum quality score")
    max_quality_score: Optional[float] = Field(None, description="Maximum quality score")
    experiment_types: Optional[List[str]] = Field(None, description="Filter by experiment types")
    system_components: Optional[List[str]] = Field(None, description="Filter by system components")

    @validator('start_date', 'end_date')
    def validate_custom_dates(cls, v, values):
        """Validate custom date range."""
        if 'time_range' in values and values['time_range'] == TimeRange.CUSTOM:
            if not v:
                raise ValueError("Custom date range requires both start_date and end_date")
        return v


class EvaluationRequest(BaseModel):
    """Request model for evaluation queries."""
    filters: EvaluationFilters = Field(..., description="Evaluation filters")
    view: EvaluationView = Field(EvaluationView.OVERVIEW, description="Evaluation view to return")
    include_details: bool = Field(False, description="Include detailed metrics")
    format: str = Field("json", description="Response format")


class EvaluationResponse(BaseModel):
    """Response model for evaluation queries."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[EvaluationMetrics] = Field(None, description="Evaluation data")
    view_data: Optional[Dict[str, Any]] = Field(None, description="View-specific data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time: float = Field(..., description="Processing time in seconds")


class ComparisonRequest(BaseModel):
    """Request model for algorithm comparison."""
    algorithms: List[str] = Field(..., description="Algorithms to compare")
    metrics: List[str] = Field(..., description="Metrics to compare")
    time_range: TimeRange = Field(TimeRange.DAY, description="Time range for comparison")
    include_statistics: bool = Field(True, description="Include statistical analysis")


class ComparisonResponse(BaseModel):
    """Response model for algorithm comparison."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    comparison_data: Dict[str, Any] = Field(..., description="Comparison data")
    statistics: Optional[Dict[str, Any]] = Field(None, description="Statistical analysis")
    recommendations: List[str] = Field(..., description="Recommendations based on comparison")


class TrendsRequest(BaseModel):
    """Request model for trend analysis."""
    metric: str = Field(..., description="Metric to analyze")
    time_range: TimeRange = Field(TimeRange.MONTH, description="Time range for trend analysis")
    granularity: str = Field("day", description="Time granularity for analysis")
    algorithms: Optional[List[str]] = Field(None, description="Filter by algorithms")


class TrendsResponse(BaseModel):
    """Response model for trend analysis."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    trends_data: Dict[str, Any] = Field(..., description="Trend analysis data")
    predictions: Optional[Dict[str, Any]] = Field(None, description="Predictions based on trends")
    insights: List[str] = Field(..., description="Insights from trend analysis")


class SensorFusionRequest(BaseModel):
    """Request model for sensor fusion analysis."""
    data_sources: List[str] = Field(..., description="Data sources to fuse")
    fusion_method: str = Field("ensemble", description="Fusion method to use")
    confidence_threshold: float = Field(0.8, description="Confidence threshold")
    include_uncertainty: bool = Field(True, description="Include uncertainty analysis")


class SensorFusionResponse(BaseModel):
    """Response model for sensor fusion analysis."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    fusion_results: Dict[str, Any] = Field(..., description="Fusion analysis results")
    confidence_scores: Dict[str, float] = Field(..., description="Confidence scores")
    uncertainty_analysis: Optional[Dict[str, Any]] = Field(None, description="Uncertainty analysis")
    recommendations: List[str] = Field(..., description="Recommendations based on fusion")


class ExperimentsRequest(BaseModel):
    """Request model for experiments analysis."""
    experiment_types: Optional[List[str]] = Field(None, description="Filter by experiment types")
    status: Optional[str] = Field(None, description="Filter by experiment status")
    time_range: TimeRange = Field(TimeRange.MONTH, description="Time range for analysis")
    include_metadata: bool = Field(True, description="Include experiment metadata")


class ExperimentsResponse(BaseModel):
    """Response model for experiments analysis."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    experiments_data: Dict[str, Any] = Field(..., description="Experiments analysis data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Experiment metadata")
    insights: List[str] = Field(..., description="Insights from experiments analysis")
