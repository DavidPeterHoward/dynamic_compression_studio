"""
Compression Algorithms Model

Based on COMPLETE-SCHEMA-DESIGN-ALIGNMENT.md
"""

from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.database.base import Base


class CompressionAlgorithm(Base):
    """
    Core compression algorithms table.

    Stores algorithm metadata, characteristics, and performance data.
    """

    __tablename__ = "compression_algorithms"

    # Primary key
    id = Column(String(50), primary_key=True)  # e.g., "gzip", "zstd"

    # Basic info
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # "traditional", "experimental", etc.
    description = Column(Text)
    version = Column(String(20), default="1.0.0")

    # Capabilities
    is_enabled = Column(Boolean, default=True)
    supported_levels = Column(JSON)  # [1,2,3,4,5,6,7,8,9]
    best_for = Column(JSON)  # ["text", "binary", "mixed"]

    # Characteristics
    speed_rating = Column(String(20))  # "very_fast", "fast", "medium", "slow"
    compression_efficiency = Column(String(20))  # "excellent", "good", "fair", "poor"
    memory_usage = Column(String(20))  # "low", "medium", "high"
    cpu_intensity = Column(String(20))  # "low", "medium", "high"

    # Performance metrics (rolling averages)
    avg_compression_ratio = Column(DECIMAL(5, 3))
    avg_compression_speed_mbps = Column(DECIMAL(10, 2))
    avg_decompression_speed_mbps = Column(DECIMAL(10, 2))
    success_rate_percent = Column(DECIMAL(5, 2))

    # Metadata
    parameters_schema = Column(JSON)  # JSON schema for algorithm parameters
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CompressionAlgorithm(id='{self.id}', name='{self.name}', enabled={self.is_enabled})>"
