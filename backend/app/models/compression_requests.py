"""
Compression Requests Model

Based on COMPLETE-SCHEMA-DESIGN-ALIGNMENT.md
"""

from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, Text, JSON, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database.base import Base
import uuid


class CompressionRequest(Base):
    """
    Compression job requests table.

    Tracks compression jobs from submission to completion.
    """

    __tablename__ = "compression_requests"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Request metadata
    request_id = Column(String(100), unique=True, nullable=False)
    algorithm_id = Column(String(50), ForeignKey('compression_algorithms.id'), nullable=False)
    compression_level = Column(Integer, default=6)

    # Input data (references, not stored here)
    input_content_hash = Column(String(64), nullable=False)  # SHA-256 of input
    input_size_bytes = Column(Integer, nullable=False)

    # Status
    status = Column(String(20), default="pending")  # "pending", "processing", "completed", "failed"
    priority = Column(Integer, default=1)  # 1=low, 10=high

    # Result data
    output_content_hash = Column(String(64))
    output_size_bytes = Column(Integer)
    compression_ratio = Column(DECIMAL(8, 4))
    compression_time_ms = Column(Integer)

    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Timing
    submitted_at = Column(TIMESTAMP, server_default=func.now())
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)

    # Request parameters
    parameters = Column(JSON)  # Additional algorithm-specific parameters

    # Metadata
    user_id = Column(String(100))  # For future auth integration
    request_source = Column(String(50))  # "api", "agent", "test"

    # Indexes for performance
    __table_args__ = (
        Index('ix_compression_requests_status', 'status'),
        Index('ix_compression_requests_algorithm', 'algorithm_id'),
        Index('ix_compression_requests_submitted', 'submitted_at'),
        Index('ix_compression_requests_priority', 'priority'),
    )

    def __repr__(self):
        return f"<CompressionRequest(id='{self.id}', status='{self.status}', algorithm='{self.algorithm_id}')>"
