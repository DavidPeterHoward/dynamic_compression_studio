"""
Sensor fusion and system metrics models for the Dynamic Compression Algorithms backend.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.base import AsyncBase, TimestampMixin


class SensorType(str, Enum):
    """Types of sensors."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    TEMPERATURE = "temperature"
    POWER = "power"
    CUSTOM = "custom"


class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class SensorStatus(str, Enum):
    """Status of sensors."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SystemMetric(AsyncBase, TimestampMixin):
    """System metrics for monitoring."""
    
    __tablename__ = "system_metrics"
    
    # Metric identification
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, default=MetricType.GAUGE)
    unit = Column(String(50), nullable=True)  # MB, %, °C, etc.
    
    # Metric values
    value = Column(Float, nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    avg_value = Column(Float, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Key-value pairs for filtering
    meta_data = Column(JSON, nullable=True)  # Additional metadata
    
    # Timestamp for time-series data
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Index for efficient time-series queries
    __table_args__ = (
        Index('idx_system_metrics_timestamp', 'timestamp'),
        Index('idx_system_metrics_name_timestamp', 'name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemMetric(name='{self.name}', value={self.value}, timestamp='{self.timestamp}')>"


class Sensor(AsyncBase, TimestampMixin):
    """Sensor configuration and metadata."""
    
    __tablename__ = "sensors"
    
    # Basic information
    name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default=SensorStatus.ACTIVE)
    
    # Configuration
    configuration = Column(JSON, nullable=True)  # Sensor-specific configuration
    sampling_rate = Column(Float, nullable=True)  # Samples per second
    precision = Column(Integer, nullable=True)  # Decimal places
    
    # Location and grouping
    location = Column(String(255), nullable=True)
    group = Column(String(255), nullable=True)
    
    # Calibration and limits
    calibration_data = Column(JSON, nullable=True)
    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)
    warning_threshold = Column(Float, nullable=True)
    critical_threshold = Column(Float, nullable=True)
    
    # Relationships
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sensor(name='{self.name}', type='{self.type}', status='{self.status}')>"


class SensorReading(AsyncBase, TimestampMixin):
    """Individual sensor readings."""
    
    __tablename__ = "sensor_readings"
    
    sensor_id = Column(Integer, ForeignKey('sensors.id'), nullable=False)
    
    # Reading values
    value = Column(Float, nullable=False)
    raw_value = Column(Float, nullable=True)  # Raw sensor value before calibration
    unit = Column(String(50), nullable=True)
    
    # Quality indicators
    quality = Column(Float, nullable=True)  # 0-1 quality score
    confidence = Column(Float, nullable=True)  # 0-1 confidence score
    error_margin = Column(Float, nullable=True)
    
    # Metadata
    meta_data = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Timestamp for time-series data
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    sensor = relationship("Sensor", back_populates="readings")
    
    # Indexes for efficient time-series queries
    __table_args__ = (
        Index('idx_sensor_readings_timestamp', 'timestamp'),
        Index('idx_sensor_readings_sensor_timestamp', 'sensor_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SensorReading(sensor='{self.sensor_id}', value={self.value}, timestamp='{self.timestamp}')>"


class SensorFusion(AsyncBase, TimestampMixin):
    """Sensor fusion algorithms and results."""
    
    __tablename__ = "sensor_fusion"
    
    # Fusion configuration
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    algorithm = Column(String(255), nullable=False)  # Fusion algorithm name
    configuration = Column(JSON, nullable=True)  # Algorithm configuration
    
    # Input sensors
    input_sensors = Column(JSON, nullable=False)  # List of sensor IDs
    output_metrics = Column(JSON, nullable=False)  # List of output metric names
    
    # Status
    status = Column(String(50), nullable=False, default=SensorStatus.ACTIVE)
    last_execution = Column(DateTime(timezone=True), nullable=True)
    execution_count = Column(Integer, default=0)
    
    # Performance
    processing_time = Column(Float, nullable=True)  # Average processing time
    accuracy = Column(Float, nullable=True)  # Fusion accuracy
    
    # Relationships
    results = relationship("SensorFusionResult", back_populates="fusion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SensorFusion(name='{self.name}', algorithm='{self.algorithm}')>"


class SensorFusionResult(AsyncBase, TimestampMixin):
    """Results from sensor fusion algorithms."""
    
    __tablename__ = "sensor_fusion_results"
    
    fusion_id = Column(Integer, ForeignKey('sensor_fusion.id'), nullable=False)
    
    # Fusion results
    input_data = Column(JSON, nullable=True)  # Input sensor data
    output_data = Column(JSON, nullable=False)  # Fused output data
    confidence = Column(Float, nullable=True)  # Fusion confidence
    
    # Performance metrics
    processing_time = Column(Float, nullable=True)
    input_count = Column(Integer, nullable=True)
    output_count = Column(Integer, nullable=True)
    
    # Quality metrics
    quality_score = Column(Float, nullable=True)
    error_estimate = Column(Float, nullable=True)
    
    # Metadata
    meta_data = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Relationships
    fusion = relationship("SensorFusion", back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index('idx_sensor_fusion_results_timestamp', 'timestamp'),
        Index('idx_sensor_fusion_results_fusion_timestamp', 'fusion_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SensorFusionResult(fusion='{self.fusion_id}', timestamp='{self.timestamp}')>"


class SystemHealth(AsyncBase, TimestampMixin):
    """System health status and alerts."""
    
    __tablename__ = "system_health"
    
    # Health status
    status = Column(String(50), nullable=False)  # healthy, warning, critical, offline
    overall_score = Column(Float, nullable=True)  # 0-100 health score
    
    # Component health
    cpu_health = Column(Float, nullable=True)
    memory_health = Column(Float, nullable=True)
    disk_health = Column(Float, nullable=True)
    network_health = Column(Float, nullable=True)
    gpu_health = Column(Float, nullable=True)
    
    # Alerts and issues
    active_alerts = Column(JSON, nullable=True)  # List of active alerts
    resolved_alerts = Column(JSON, nullable=True)  # List of recently resolved alerts
    
    # Performance indicators
    response_time = Column(Float, nullable=True)
    throughput = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    
    # Metadata
    meta_data = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_system_health_timestamp', 'timestamp'),
        Index('idx_system_health_status_timestamp', 'status', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemHealth(status='{self.status}', score={self.overall_score})>"


# Pydantic models for API
class SystemMetricCreate(BaseModel):
    """Pydantic model for creating system metrics."""
    
    name: str = Field(..., description="Metric name")
    type: MetricType = Field(MetricType.GAUGE, description="Metric type")
    unit: Optional[str] = Field(None, description="Metric unit")
    value: float = Field(..., description="Metric value")
    min_value: Optional[float] = Field(None, description="Minimum value")
    max_value: Optional[float] = Field(None, description="Maximum value")
    avg_value: Optional[float] = Field(None, description="Average value")
    description: Optional[str] = Field(None, description="Metric description")
    tags: Optional[Dict[str, str]] = Field(None, description="Metric tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: Optional[datetime] = Field(None, description="Metric timestamp")


class SystemMetricResponse(SystemMetricCreate):
    """Pydantic model for system metric responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SensorCreate(BaseModel):
    """Pydantic model for creating sensors."""
    
    name: str = Field(..., description="Sensor name")
    type: SensorType = Field(..., description="Sensor type")
    description: Optional[str] = Field(None, description="Sensor description")
    status: SensorStatus = Field(SensorStatus.ACTIVE, description="Sensor status")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Sensor configuration")
    sampling_rate: Optional[float] = Field(None, description="Sampling rate")
    precision: Optional[int] = Field(None, description="Precision")
    location: Optional[str] = Field(None, description="Sensor location")
    group: Optional[str] = Field(None, description="Sensor group")
    calibration_data: Optional[Dict[str, Any]] = Field(None, description="Calibration data")
    min_threshold: Optional[float] = Field(None, description="Minimum threshold")
    max_threshold: Optional[float] = Field(None, description="Maximum threshold")
    warning_threshold: Optional[float] = Field(None, description="Warning threshold")
    critical_threshold: Optional[float] = Field(None, description="Critical threshold")


class SensorResponse(SensorCreate):
    """Pydantic model for sensor responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    readings_count: int = 0
    
    class Config:
        from_attributes = True


class SensorReadingCreate(BaseModel):
    """Pydantic model for creating sensor readings."""
    
    sensor_id: int = Field(..., description="Sensor ID")
    value: float = Field(..., description="Reading value")
    raw_value: Optional[float] = Field(None, description="Raw sensor value")
    unit: Optional[str] = Field(None, description="Value unit")
    quality: Optional[float] = Field(None, description="Quality score")
    confidence: Optional[float] = Field(None, description="Confidence score")
    error_margin: Optional[float] = Field(None, description="Error margin")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[Dict[str, str]] = Field(None, description="Reading tags")
    timestamp: Optional[datetime] = Field(None, description="Reading timestamp")


class SensorReadingResponse(SensorReadingCreate):
    """Pydantic model for sensor reading responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SensorFusionCreate(BaseModel):
    """Pydantic model for creating sensor fusion."""
    
    name: str = Field(..., description="Fusion name")
    description: Optional[str] = Field(None, description="Fusion description")
    algorithm: str = Field(..., description="Fusion algorithm")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Algorithm configuration")
    input_sensors: List[int] = Field(..., description="Input sensor IDs")
    output_metrics: List[str] = Field(..., description="Output metric names")
    status: SensorStatus = Field(SensorStatus.ACTIVE, description="Fusion status")


class SensorFusionResponse(SensorFusionCreate):
    """Pydantic model for sensor fusion responses."""
    
    id: int
    last_execution: Optional[datetime]
    execution_count: int
    processing_time: Optional[float]
    accuracy: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SensorFusionResultCreate(BaseModel):
    """Pydantic model for creating sensor fusion results."""
    
    fusion_id: int = Field(..., description="Fusion ID")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input sensor data")
    output_data: Dict[str, Any] = Field(..., description="Fused output data")
    confidence: Optional[float] = Field(None, description="Fusion confidence")
    processing_time: Optional[float] = Field(None, description="Processing time")
    input_count: Optional[int] = Field(None, description="Input data count")
    output_count: Optional[int] = Field(None, description="Output data count")
    quality_score: Optional[float] = Field(None, description="Quality score")
    error_estimate: Optional[float] = Field(None, description="Error estimate")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[Dict[str, str]] = Field(None, description="Result tags")
    timestamp: Optional[datetime] = Field(None, description="Result timestamp")


class SensorFusionResultResponse(SensorFusionResultCreate):
    """Pydantic model for sensor fusion result responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SystemHealthCreate(BaseModel):
    """Pydantic model for creating system health."""
    
    status: str = Field(..., description="System status")
    overall_score: Optional[float] = Field(None, description="Overall health score")
    cpu_health: Optional[float] = Field(None, description="CPU health score")
    memory_health: Optional[float] = Field(None, description="Memory health score")
    disk_health: Optional[float] = Field(None, description="Disk health score")
    network_health: Optional[float] = Field(None, description="Network health score")
    gpu_health: Optional[float] = Field(None, description="GPU health score")
    active_alerts: Optional[List[Dict[str, Any]]] = Field(None, description="Active alerts")
    resolved_alerts: Optional[List[Dict[str, Any]]] = Field(None, description="Resolved alerts")
    response_time: Optional[float] = Field(None, description="System response time")
    throughput: Optional[float] = Field(None, description="System throughput")
    error_rate: Optional[float] = Field(None, description="Error rate")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: Optional[datetime] = Field(None, description="Health timestamp")


class SystemHealthResponse(SystemHealthCreate):
    """Pydantic model for system health responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MetricsQueryRequest(BaseModel):
    """Pydantic model for metrics query requests."""
    
    metric_names: Optional[List[str]] = Field(None, description="Metric names to query")
    sensor_ids: Optional[List[int]] = Field(None, description="Sensor IDs to query")
    start_time: Optional[datetime] = Field(None, description="Start time for query")
    end_time: Optional[datetime] = Field(None, description="End time for query")
    aggregation: Optional[str] = Field("raw", description="Aggregation method (raw, avg, min, max, sum)")
    interval: Optional[str] = Field(None, description="Time interval for aggregation")
    tags: Optional[Dict[str, str]] = Field(None, description="Tags filter")
    limit: Optional[int] = Field(1000, description="Maximum number of results")


class MetricsQueryResponse(BaseModel):
    """Pydantic model for metrics query responses."""
    
    metrics: List[SystemMetricResponse]
    sensor_readings: List[SensorReadingResponse]
    fusion_results: List[SensorFusionResultResponse]
    system_health: List[SystemHealthResponse]
    total_count: int
    query_time: float
    metadata: Dict[str, Any]
