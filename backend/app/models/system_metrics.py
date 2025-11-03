"""
System Metrics Model

Based on COMPLETE-SCHEMA-DESIGN-ALIGNMENT.md
"""

from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, BIGINT, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database.base import Base
import uuid


class SystemMetrics(Base):
    """
    System metrics for monitoring and analytics.

    Partitioned by recorded_at for efficient time-series queries.
    Corresponds to frontend SystemMetrics interface.
    """

    __tablename__ = "system_monitoring_metrics"
    __table_args__ = {'postgresql_partition_by': 'RANGE (recorded_at)'}

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recorded_at = Column(TIMESTAMP, nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)

    # System Resources
    cpu_percent = Column(DECIMAL(5, 2))
    memory_percent = Column(DECIMAL(5, 2))
    disk_percent = Column(DECIMAL(5, 2))
    network_bytes_per_sec = Column(BIGINT)

    # Compression Metrics
    compression_efficiency = Column(DECIMAL(5, 2))
    throughput_bytes_per_sec = Column(BIGINT)
    success_rate = Column(DECIMAL(5, 2))
    error_rate = Column(DECIMAL(5, 2))

    # Performance Metrics
    avg_compression_ratio = Column(DECIMAL(10, 4))
    avg_response_time_ms = Column(Integer)
    p50_response_time_ms = Column(Integer)
    p95_response_time_ms = Column(Integer)
    p99_response_time_ms = Column(Integer)

    # System Health
    system_health = Column(String(20), nullable=False, default='healthy')
    active_connections = Column(Integer)
    queue_length = Column(Integer)

    # Algorithm-specific
    algorithm_performance = Column(JSON, default=dict)

    # Metadata
    host_name = Column(String(255))
    instance_id = Column(String(100))

    def to_dict(self) -> dict:
        """Convert to dictionary matching frontend SystemMetrics interface."""
        return {
            "cpu": float(self.cpu_percent) if self.cpu_percent else 0,
            "memory": float(self.memory_percent) if self.memory_percent else 0,
            "disk": float(self.disk_percent) if self.disk_percent else 0,
            "network": int(self.network_bytes_per_sec) if self.network_bytes_per_sec else 0,
            "compressionEfficiency": float(self.compression_efficiency) if self.compression_efficiency else 0,
            "throughput": int(self.throughput_bytes_per_sec) if self.throughput_bytes_per_sec else 0,
            "successRate": float(self.success_rate) if self.success_rate else 0,
            "errorRate": float(self.error_rate) if self.error_rate else 0,
            "averageCompressionRatio": float(self.avg_compression_ratio) if self.avg_compression_ratio else 0,
            "responseTime": self.avg_response_time_ms or 0,
            "systemHealth": self.system_health,
            "activeConnections": self.active_connections or 0,
            "queueLength": self.queue_length or 0,
            "algorithmPerformance": self.algorithm_performance or {},
            "recordedAt": self.recorded_at.isoformat()
        }

    def __repr__(self):
        return f"<SystemMetrics(id='{self.id}', type='{self.metric_type}', health='{self.system_health}')>"
