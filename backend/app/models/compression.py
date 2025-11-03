"""
Pydantic models for compression-related data structures.
"""

from typing import Optional, Union, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, field_validator
import json


class CompressionAlgorithm(str, Enum):
    """Supported compression algorithms."""
    
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"
    LZMA = "lzma"
    CONTENT_AWARE = "content_aware"
    QUANTUM_BIOLOGICAL = "quantum_biological"
    NEUROMORPHIC = "neuromorphic"
    TOPOLOGICAL = "topological"


class CompressionLevel(str, Enum):
    """Compression level options."""
    
    FAST = "fast"
    BALANCED = "balanced"
    OPTIMAL = "optimal"
    MAXIMUM = "maximum"


class ContentType(str, Enum):
    """Content type classifications."""
    
    TEXT = "text"
    BINARY = "binary"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    UNKNOWN = "unknown"


class CompressionParameters(BaseModel):
    """Parameters for compression algorithms."""
    
    algorithm: CompressionAlgorithm = Field(..., description="Compression algorithm to use")
    level: Union[CompressionLevel, int] = Field(default=CompressionLevel.BALANCED, description="Compression level (enum or integer)")
    window_size: Optional[int] = Field(default=None, description="Window size for sliding window algorithms")
    dictionary_size: Optional[int] = Field(default=None, description="Dictionary size for dictionary-based algorithms")
    block_size: Optional[int] = Field(default=8192, description="Block size for processing")
    threads: Optional[int] = Field(default=1, description="Number of threads to use")
    
    # Advanced parameters
    content_type: Optional[ContentType] = Field(default=None, description="Content type classification")
    optimization_target: Optional[str] = Field(default="ratio", description="Optimization target (ratio, speed, quality)")
    max_iterations: Optional[int] = Field(default=10, description="Maximum optimization iterations")
    
    # Quantum-biological parameters
    quantum_qubits: Optional[int] = Field(default=8, description="Number of quantum qubits")
    biological_population: Optional[int] = Field(default=100, description="Biological population size")
    
    # Neuromorphic parameters
    neural_layers: Optional[int] = Field(default=3, description="Number of neural layers")
    spike_threshold: Optional[float] = Field(default=0.1, description="Spike threshold")
    
    # Topological parameters
    persistence_threshold: Optional[float] = Field(default=0.01, description="Persistence threshold")
    homology_dimension: Optional[int] = Field(default=2, description="Maximum homology dimension")
    
    @validator('level')
    def validate_level(cls, v):
        """Validate compression level based on algorithm."""
        if isinstance(v, int):
            # Integer validation - allow higher levels for some algorithms
            if v < 1 or v > 22:  # ZSTD supports up to level 22
                raise ValueError('Integer compression level must be between 1 and 22')
        elif isinstance(v, str):
            # String validation for enum values
            try:
                CompressionLevel(v)
            except ValueError:
                raise ValueError(f'Invalid compression level: {v}')
        return v
    
    @validator('window_size')
    def validate_window_size(cls, v):
        if v is not None and (v < 1024 or v > 65536):
            raise ValueError('Window size must be between 1024 and 65536')
        return v
    
    @validator('dictionary_size')
    def validate_dictionary_size(cls, v):
        if v is not None and (v < 1024 or v > 1048576):
            raise ValueError('Dictionary size must be between 1024 and 1048576')
        return v
    
    def get_level_value(self) -> Union[str, int]:
        """Get the level value in the appropriate format for the algorithm."""
        if isinstance(self.level, int):
            return self.level
        elif isinstance(self.level, str):
            return self.level
        else:
            return self.level.value if hasattr(self.level, 'value') else str(self.level)
    
    def get_algorithm_specific_level(self) -> Union[str, int]:
        """Get algorithm-specific level format."""
        algorithm = self.algorithm
        
        if algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.BZIP2, CompressionAlgorithm.ZSTD]:
            # These algorithms support integer levels
            if isinstance(self.level, int):
                return self.level
            elif isinstance(self.level, str):
                # Convert enum to integer
                level_map = {
                    CompressionLevel.FAST: 1,
                    CompressionLevel.BALANCED: 6,
                    CompressionLevel.OPTIMAL: 8,
                    CompressionLevel.MAXIMUM: 9
                }
                return level_map.get(self.level, 6)
            else:
                return 6  # Default
        else:
            # Other algorithms use string levels
            if isinstance(self.level, int):
                # Convert integer to string level
                if self.level <= 3:
                    return CompressionLevel.FAST
                elif self.level <= 6:
                    return CompressionLevel.BALANCED
                elif self.level <= 8:
                    return CompressionLevel.OPTIMAL
                else:
                    return CompressionLevel.MAXIMUM
            else:
                return self.get_level_value()


class CompressionRequest(BaseModel):
    """Request model for compression operations."""
    
    content: Optional[str] = Field(default=None, description="Text content to compress")
    file_id: Optional[str] = Field(default=None, description="ID of uploaded file to compress")
    parameters: CompressionParameters = Field(..., description="Compression parameters")
    
    # Optional metadata
    content_type: Optional[ContentType] = Field(default=None, description="Content type classification")
    priority: Optional[str] = Field(default="normal", description="Processing priority")
    callback_url: Optional[str] = Field(default=None, description="Callback URL for async operations")
    
    @field_validator('content', 'file_id')
    @classmethod
    def validate_content_source(cls, v, info):
        # Get the other field value
        other_field = 'file_id' if info.field_name == 'content' else 'content'
        other_value = info.data.get(other_field) if info.data else None
        
        # If this field is None and the other field is also None, raise error
        if v is None and other_value is None:
            raise ValueError('Either content or file_id must be provided')
        return v


class CompressionResult(BaseModel):
    """Result of a compression operation."""
    
    # Basic information
    original_size: int = Field(..., description="Original data size in bytes")
    compressed_size: int = Field(..., description="Compressed data size in bytes")
    compression_ratio: float = Field(..., description="Compression ratio (original/compressed)")
    compression_percentage: float = Field(..., description="Compression percentage")
    
    # Algorithm information
    algorithm_used: CompressionAlgorithm = Field(..., description="Algorithm that was used")
    parameters_used: CompressionParameters = Field(..., description="Parameters that were used")
    
    # Performance metrics
    compression_time: float = Field(..., description="Compression time in seconds")
    decompression_time: Optional[float] = Field(default=None, description="Decompression time in seconds")
    memory_usage: Optional[int] = Field(default=None, description="Memory usage in bytes")
    
    # Quality metrics
    quality_score: Optional[float] = Field(default=None, description="Quality preservation score")
    information_preservation: Optional[float] = Field(default=None, description="Information preservation ratio")
    
    # Advanced metrics
    entropy_reduction: Optional[float] = Field(default=None, description="Entropy reduction achieved")
    pattern_efficiency: Optional[float] = Field(default=None, description="Pattern detection efficiency")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When compression was performed")
    status: str = Field(default="completed", description="Compression status")
    
    @validator('compression_ratio', 'compression_percentage')
    def calculate_metrics(cls, v, values):
        if 'original_size' in values and 'compressed_size' in values:
            ratio = values['original_size'] / values['compressed_size']
            percentage = (1 - values['compressed_size'] / values['original_size']) * 100
            return ratio if v == 'compression_ratio' else percentage
        return v


class CompressionResponse(BaseModel):
    """Response model for compression operations."""
    
    model_config = {"json_schema_extra": {"exclude_none": False}}
    
    # Basic response
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    
    # Results
    result: Optional[CompressionResult] = Field(default=None, description="Compression result")
    compressed_content: Optional[str] = Field(default=None, description="Base64 encoded compressed content")
    
    # Error information
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_code: Optional[str] = Field(default=None, description="Error code if failed")
    
    # Metadata
    request_id: Optional[str] = Field(default=None, description="Unique request ID")
    processing_time: Optional[float] = Field(default=None, description="Total processing time")
    
    # Additional data
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CompressionComparison(BaseModel):
    """Comparison of multiple compression algorithms."""
    
    algorithms: List[CompressionAlgorithm] = Field(..., description="Algorithms compared")
    results: List[CompressionResult] = Field(..., description="Results for each algorithm")
    winner: Optional[CompressionAlgorithm] = Field(default=None, description="Best performing algorithm")
    comparison_metrics: Dict[str, Any] = Field(default_factory=dict, description="Comparison metrics")
    
    @validator('results')
    def validate_results_count(cls, v, values):
        if 'algorithms' in values and len(v) != len(values['algorithms']):
            raise ValueError('Number of results must match number of algorithms')
        return v


class BatchCompressionRequest(BaseModel):
    """Request model for batch compression operations."""
    
    requests: List[CompressionRequest] = Field(..., description="List of compression requests")
    batch_id: Optional[str] = Field(default=None, description="Batch identifier")
    parallel: bool = Field(default=True, description="Whether to process in parallel")
    max_workers: Optional[int] = Field(default=None, description="Maximum parallel workers")


class BatchCompressionResponse(BaseModel):
    """Response model for batch compression operations."""
    
    batch_id: str = Field(..., description="Batch identifier")
    total_requests: int = Field(..., description="Total number of requests")
    successful: int = Field(..., description="Number of successful compressions")
    failed: int = Field(..., description="Number of failed compressions")
    results: List[CompressionResponse] = Field(..., description="Results for each request")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Batch summary statistics")






