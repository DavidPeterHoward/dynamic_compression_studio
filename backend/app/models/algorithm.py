"""
Algorithm models for the Dynamic Compression Algorithms backend.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.base import AsyncBase, TimestampMixin


class AlgorithmType(str, Enum):
    """Types of compression algorithms."""
    LOSSY = "lossy"
    LOSSLESS = "lossless"
    ADAPTIVE = "adaptive"
    NEURAL = "neural"
    QUANTUM = "quantum"
    HYBRID = "hybrid"


class AlgorithmCategory(str, Enum):
    """Categories of compression algorithms."""
    DICTIONARY_BASED = "dictionary_based"
    STATISTICAL = "statistical"
    TRANSFORM_BASED = "transform_based"
    NEURAL_NETWORK = "neural_network"
    QUANTUM_BIOLOGICAL = "quantum_biological"
    TOPOLOGICAL = "topological"
    ENHANCED = "enhanced"


class AlgorithmStatus(str, Enum):
    """Status of algorithms."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


# Association table for algorithm parameters
algorithm_parameters = Table(
    'algorithm_parameters',
    AsyncBase.metadata,
    Column('algorithm_id', Integer, ForeignKey('algorithms.id'), primary_key=True),
    Column('parameter_id', Integer, ForeignKey('algorithm_parameters_metadata.id'), primary_key=True)
)


class Algorithm(AsyncBase, TimestampMixin):
    """Algorithm model for storing compression algorithm information."""
    
    __tablename__ = "algorithms"
    
    # Basic information
    name = Column(String(255), nullable=False, unique=True, index=True)
    version = Column(String(50), nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, default=AlgorithmType.LOSSLESS)
    category = Column(String(50), nullable=False, default=AlgorithmCategory.DICTIONARY_BASED)
    status = Column(String(50), nullable=False, default=AlgorithmStatus.ACTIVE)
    
    # Implementation details
    implementation_path = Column(String(500), nullable=False)
    entry_point = Column(String(255), nullable=False, default="compress")
    dependencies = Column(JSON, nullable=True)  # List of required packages
    
    # Performance characteristics
    compression_ratio = Column(Float, nullable=True)
    compression_speed = Column(Float, nullable=True)  # MB/s
    decompression_speed = Column(Float, nullable=True)  # MB/s
    memory_usage = Column(Float, nullable=True)  # MB
    cpu_usage = Column(Float, nullable=True)  # Percentage
    
    # Quality metrics
    accuracy = Column(Float, nullable=True)
    fidelity = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    
    # Configuration
    default_parameters = Column(JSON, nullable=True)
    supported_formats = Column(JSON, nullable=True)  # List of supported file formats
    max_file_size = Column(Integer, nullable=True)  # Maximum file size in bytes
    
    # Metadata
    author = Column(String(255), nullable=True)
    license = Column(String(100), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    repository_url = Column(String(500), nullable=True)
    
    # Relationships
    parameters = relationship("AlgorithmParameterMetadata", secondary=algorithm_parameters, back_populates="algorithms")
    experiments = relationship("Experiment", back_populates="algorithm")
    benchmarks = relationship("AlgorithmBenchmark", back_populates="algorithm")
    
    def __repr__(self):
        return f"<Algorithm(name='{self.name}', version='{self.version}', type='{self.type}')>"


class AlgorithmParameterMetadata(AsyncBase, TimestampMixin):
    """Metadata for algorithm parameters."""
    
    __tablename__ = "algorithm_parameters_metadata"
    
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(String(50), nullable=False)  # int, float, string, bool, enum
    default_value = Column(Text, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    step = Column(Float, nullable=True)
    required = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)  # For enum types
    
    # Relationships
    algorithms = relationship("Algorithm", secondary=algorithm_parameters, back_populates="parameters")
    
    def __repr__(self):
        return f"<AlgorithmParameterMetadata(name='{self.name}', data_type='{self.data_type}')>"


class AlgorithmBenchmark(AsyncBase, TimestampMixin):
    """Benchmark results for algorithms."""
    
    __tablename__ = "algorithm_benchmarks"
    
    algorithm_id = Column(Integer, ForeignKey('algorithms.id'), nullable=False)
    benchmark_name = Column(String(255), nullable=False)
    dataset_name = Column(String(255), nullable=False)
    dataset_size = Column(Integer, nullable=False)  # Size in bytes
    
    # Performance results
    compression_ratio = Column(Float, nullable=False)
    compression_time = Column(Float, nullable=False)  # Seconds
    decompression_time = Column(Float, nullable=False)  # Seconds
    memory_peak = Column(Float, nullable=False)  # MB
    cpu_peak = Column(Float, nullable=False)  # Percentage
    
    # Quality results
    accuracy = Column(Float, nullable=True)
    fidelity = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    
    # Additional metrics
    throughput = Column(Float, nullable=True)  # MB/s
    efficiency_score = Column(Float, nullable=True)
    
    # Test conditions
    parameters = Column(JSON, nullable=True)  # Parameters used for this benchmark
    test_environment = Column(JSON, nullable=True)  # System specs, etc.
    
    # Relationships
    algorithm = relationship("Algorithm", back_populates="benchmarks")
    
    def __repr__(self):
        return f"<AlgorithmBenchmark(algorithm='{self.algorithm_id}', benchmark='{self.benchmark_name}')>"


# Pydantic models for API
class AlgorithmParameterMetadataCreate(BaseModel):
    """Pydantic model for creating algorithm parameter metadata."""
    
    name: str = Field(..., description="Parameter name")
    display_name: str = Field(..., description="Human-readable parameter name")
    description: Optional[str] = Field(None, description="Parameter description")
    data_type: str = Field(..., description="Data type (int, float, string, bool, enum)")
    default_value: Optional[str] = Field(None, description="Default value")
    min_value: Optional[float] = Field(None, description="Minimum value for numeric types")
    max_value: Optional[float] = Field(None, description="Maximum value for numeric types")
    step: Optional[float] = Field(None, description="Step value for numeric types")
    required: bool = Field(False, description="Whether parameter is required")
    options: Optional[List[str]] = Field(None, description="Options for enum types")


class AlgorithmParameterMetadataResponse(AlgorithmParameterMetadataCreate):
    """Pydantic model for algorithm parameter metadata response."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlgorithmCreate(BaseModel):
    """Pydantic model for creating algorithms."""
    
    name: str = Field(..., description="Algorithm name")
    version: str = Field("1.0.0", description="Algorithm version")
    description: Optional[str] = Field(None, description="Algorithm description")
    type: AlgorithmType = Field(AlgorithmType.LOSSLESS, description="Algorithm type")
    category: AlgorithmCategory = Field(AlgorithmCategory.DICTIONARY_BASED, description="Algorithm category")
    status: AlgorithmStatus = Field(AlgorithmStatus.ACTIVE, description="Algorithm status")
    implementation_path: str = Field(..., description="Path to algorithm implementation")
    entry_point: str = Field("compress", description="Entry point function name")
    dependencies: Optional[List[str]] = Field(None, description="Required dependencies")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Default parameters")
    supported_formats: Optional[List[str]] = Field(None, description="Supported file formats")
    max_file_size: Optional[int] = Field(None, description="Maximum file size in bytes")
    author: Optional[str] = Field(None, description="Algorithm author")
    license: Optional[str] = Field(None, description="Algorithm license")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    parameter_metadata: Optional[List[AlgorithmParameterMetadataCreate]] = Field(None, description="Parameter metadata")


class AlgorithmUpdate(BaseModel):
    """Pydantic model for updating algorithms."""
    
    name: Optional[str] = Field(None, description="Algorithm name")
    version: Optional[str] = Field(None, description="Algorithm version")
    description: Optional[str] = Field(None, description="Algorithm description")
    type: Optional[AlgorithmType] = Field(None, description="Algorithm type")
    category: Optional[AlgorithmCategory] = Field(None, description="Algorithm category")
    status: Optional[AlgorithmStatus] = Field(None, description="Algorithm status")
    implementation_path: Optional[str] = Field(None, description="Path to algorithm implementation")
    entry_point: Optional[str] = Field(None, description="Entry point function name")
    dependencies: Optional[List[str]] = Field(None, description="Required dependencies")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Default parameters")
    supported_formats: Optional[List[str]] = Field(None, description="Supported file formats")
    max_file_size: Optional[int] = Field(None, description="Maximum file size in bytes")
    author: Optional[str] = Field(None, description="Algorithm author")
    license: Optional[str] = Field(None, description="Algorithm license")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    repository_url: Optional[str] = Field(None, description="Repository URL")


class AlgorithmResponse(BaseModel):
    """Pydantic model for algorithm responses."""
    
    id: int
    name: str
    version: str
    description: Optional[str]
    type: AlgorithmType
    category: AlgorithmCategory
    status: AlgorithmStatus
    implementation_path: str
    entry_point: str
    dependencies: Optional[List[str]]
    compression_ratio: Optional[float]
    compression_speed: Optional[float]
    decompression_speed: Optional[float]
    memory_usage: Optional[float]
    cpu_usage: Optional[float]
    accuracy: Optional[float]
    fidelity: Optional[float]
    error_rate: Optional[float]
    default_parameters: Optional[Dict[str, Any]]
    supported_formats: Optional[List[str]]
    max_file_size: Optional[int]
    author: Optional[str]
    license: Optional[str]
    documentation_url: Optional[str]
    repository_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    parameters: List[AlgorithmParameterMetadataResponse] = []
    
    class Config:
        from_attributes = True


class AlgorithmBenchmarkCreate(BaseModel):
    """Pydantic model for creating algorithm benchmarks."""
    
    algorithm_id: int = Field(..., description="Algorithm ID")
    benchmark_name: str = Field(..., description="Benchmark name")
    dataset_name: str = Field(..., description="Dataset name")
    dataset_size: int = Field(..., description="Dataset size in bytes")
    compression_ratio: float = Field(..., description="Compression ratio achieved")
    compression_time: float = Field(..., description="Compression time in seconds")
    decompression_time: float = Field(..., description="Decompression time in seconds")
    memory_peak: float = Field(..., description="Peak memory usage in MB")
    cpu_peak: float = Field(..., description="Peak CPU usage percentage")
    accuracy: Optional[float] = Field(None, description="Accuracy metric")
    fidelity: Optional[float] = Field(None, description="Fidelity metric")
    error_rate: Optional[float] = Field(None, description="Error rate")
    throughput: Optional[float] = Field(None, description="Throughput in MB/s")
    efficiency_score: Optional[float] = Field(None, description="Efficiency score")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters used")
    test_environment: Optional[Dict[str, Any]] = Field(None, description="Test environment details")


class AlgorithmBenchmarkResponse(AlgorithmBenchmarkCreate):
    """Pydantic model for algorithm benchmark responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlgorithmComparisonRequest(BaseModel):
    """Pydantic model for algorithm comparison requests."""
    
    algorithm_ids: List[int] = Field(..., description="List of algorithm IDs to compare")
    dataset_name: str = Field(..., description="Dataset name for comparison")
    parameters: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Parameters for each algorithm")
    metrics: List[str] = Field(["compression_ratio", "speed", "memory", "accuracy"], description="Metrics to compare")


class AlgorithmComparisonResponse(BaseModel):
    """Pydantic model for algorithm comparison responses."""
    
    comparison_id: str
    algorithms: List[AlgorithmResponse]
    benchmarks: List[AlgorithmBenchmarkResponse]
    comparison_metrics: Dict[str, Dict[str, float]]
    ranking: List[Dict[str, Any]]
    created_at: datetime
