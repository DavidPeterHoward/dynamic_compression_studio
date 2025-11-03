"""
Base Algorithm Interface - Foundation for all compression algorithms.
Implements software design patterns for extensibility, performance, and maintainability.
"""

import abc
import asyncio
import time
import logging
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import psutil
import threading
from contextlib import asynccontextmanager

from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


class AlgorithmState(Enum):
    """Algorithm execution states for monitoring and debugging."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    COMPRESSING = "compressing"
    DECOMPRESSING = "decompressing"
    ERROR = "error"
    OPTIMIZING = "optimizing"


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for algorithm evaluation."""
    compression_time: float
    decompression_time: float
    compression_ratio: float
    memory_usage_mb: float
    cpu_usage_percent: float
    throughput_mbps: float
    error_count: int
    success_count: int
    total_operations: int
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.success_count / self.total_operations) * 100
    
    @property
    def average_compression_time(self) -> float:
        """Calculate average compression time."""
        if self.success_count == 0:
            return 0.0
        return self.compression_time / self.success_count


@dataclass
class AlgorithmContext:
    """Context information for algorithm execution."""
    content_size: int
    content_type: str
    compression_level: CompressionLevel
    target_throughput: Optional[float] = None
    memory_limit_mb: Optional[float] = None
    timeout_seconds: Optional[float] = None
    optimization_mode: bool = False


class AlgorithmRegistry:
    """Registry pattern for managing algorithm implementations."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._algorithms = {}
                    cls._instance._performance_cache = {}
        return cls._instance
    
    def register(self, algorithm: CompressionAlgorithm, implementation: 'BaseCompressor'):
        """Register an algorithm implementation."""
        self._algorithms[algorithm] = implementation
        logger.info(f"Registered algorithm: {algorithm}")
    
    def get(self, algorithm: CompressionAlgorithm) -> Optional['BaseCompressor']:
        """Get algorithm implementation."""
        return self._algorithms.get(algorithm)
    
    def list_available(self) -> list[CompressionAlgorithm]:
        """List all available algorithms."""
        return list(self._algorithms.keys())
    
    def get_performance_cache(self, algorithm: CompressionAlgorithm) -> Optional[PerformanceMetrics]:
        """Get cached performance metrics."""
        return self._performance_cache.get(algorithm)
    
    def update_performance_cache(self, algorithm: CompressionAlgorithm, metrics: PerformanceMetrics):
        """Update performance cache."""
        self._performance_cache[algorithm] = metrics


class BaseCompressor(abc.ABC):
    """
    Abstract base class for all compression algorithms.
    
    Implements:
    - Template Method Pattern: Defines algorithm structure
    - Strategy Pattern: Allows algorithm switching
    - Observer Pattern: Performance monitoring
    - Factory Pattern: Algorithm creation
    - Decorator Pattern: Performance tracking
    """
    
    def __init__(self, algorithm: CompressionAlgorithm):
        self.algorithm = algorithm
        self.state = AlgorithmState.IDLE
        self.performance_metrics = PerformanceMetrics(
            compression_time=0.0,
            decompression_time=0.0,
            compression_ratio=1.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            throughput_mbps=0.0,
            error_count=0,
            success_count=0,
            total_operations=0
        )
        self._observers = []
        self._lock = threading.Lock()
        
        # Register with global registry
        AlgorithmRegistry().register(algorithm, self)
    
    @abc.abstractmethod
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """Implementation-specific compression logic."""
        pass
    
    @abc.abstractmethod
    async def _decompress_impl(self, data: bytes) -> bytes:
        """Implementation-specific decompression logic."""
        pass
    
    @abc.abstractmethod
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """Determine optimal compression level based on content characteristics."""
        pass
    
    @abc.abstractmethod
    def _validate_input(self, data: bytes) -> bool:
        """Validate input data for algorithm compatibility."""
        pass
    
    async def compress(self, content: str, level: Optional[CompressionLevel] = None) -> bytes:
        """
        Compress content with performance monitoring and error handling.
        
        Args:
            content: Content to compress
            level: Compression level (auto-determined if None)
            
        Returns:
            Compressed data
            
        Raises:
            CompressionError: If compression fails
        """
        try:
            self._set_state(AlgorithmState.COMPRESSING)
            self._notify_observers("compression_started", {"content_size": len(content)})
            
            # Convert to bytes
            data = content.encode('utf-8')
            
            # Validate input
            if not self._validate_input(data):
                raise ValueError(f"Invalid input for algorithm {self.algorithm}")
            
            # Determine optimal level if not specified
            if level is None:
                level = self._get_optimal_level(len(data), "text")
            
            # Monitor system resources
            start_memory = psutil.virtual_memory().used
            start_cpu = psutil.cpu_percent()
            start_time = time.time()
            
            # Perform compression
            compressed_data = await self._compress_impl(data, level)
            
            # Calculate metrics
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            end_cpu = psutil.cpu_percent()
            
            compression_time = end_time - start_time
            memory_usage = (end_memory - start_memory) / (1024 * 1024)  # MB
            cpu_usage = (start_cpu + end_cpu) / 2
            compression_ratio = len(data) / len(compressed_data) if len(compressed_data) > 0 else 1.0
            throughput = (len(data) / compression_time) / (1024 * 1024) if compression_time > 0 else 0.0
            
            # Update performance metrics
            with self._lock:
                self.performance_metrics.compression_time += compression_time
                self.performance_metrics.memory_usage_mb = max(
                    self.performance_metrics.memory_usage_mb, memory_usage
                )
                self.performance_metrics.cpu_usage_percent = max(
                    self.performance_metrics.cpu_usage_percent, cpu_usage
                )
                self.performance_metrics.compression_ratio = max(
                    self.performance_metrics.compression_ratio, compression_ratio
                )
                self.performance_metrics.throughput_mbps = max(
                    self.performance_metrics.throughput_mbps, throughput
                )
                self.performance_metrics.success_count += 1
                self.performance_metrics.total_operations += 1
            
            # Update registry cache
            AlgorithmRegistry().update_performance_cache(self.algorithm, self.performance_metrics)
            
            self._notify_observers("compression_completed", {
                "compression_time": compression_time,
                "compression_ratio": compression_ratio,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage
            })
            
            logger.info(f"Compression completed: {self.algorithm} - "
                       f"Ratio: {compression_ratio:.2f}x, "
                       f"Time: {compression_time:.3f}s, "
                       f"Throughput: {throughput:.2f} MB/s")
            
            return compressed_data
            
        except Exception as e:
            self._handle_error(e, "compression")
            raise CompressionError(f"Compression failed: {str(e)}") from e
        finally:
            self._set_state(AlgorithmState.IDLE)
    
    async def decompress(self, compressed_data: bytes) -> str:
        """
        Decompress data with performance monitoring and error handling.
        
        Args:
            compressed_data: Compressed data to decompress
            
        Returns:
            Decompressed content
            
        Raises:
            CompressionError: If decompression fails
        """
        try:
            self._set_state(AlgorithmState.DECOMPRESSING)
            self._notify_observers("decompression_started", {"data_size": len(compressed_data)})
            
            # Validate input
            if not self._validate_input(compressed_data):
                raise ValueError(f"Invalid compressed data for algorithm {self.algorithm}")
            
            # Monitor system resources
            start_memory = psutil.virtual_memory().used
            start_cpu = psutil.cpu_percent()
            start_time = time.time()
            
            # Perform decompression
            decompressed_data = await self._decompress_impl(compressed_data)
            
            # Calculate metrics
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            end_cpu = psutil.cpu_percent()
            
            decompression_time = end_time - start_time
            memory_usage = (end_memory - start_memory) / (1024 * 1024)  # MB
            cpu_usage = (start_cpu + end_cpu) / 2
            throughput = (len(decompressed_data) / decompression_time) / (1024 * 1024) if decompression_time > 0 else 0.0
            
            # Update performance metrics
            with self._lock:
                self.performance_metrics.decompression_time += decompression_time
                self.performance_metrics.memory_usage_mb = max(
                    self.performance_metrics.memory_usage_mb, memory_usage
                )
                self.performance_metrics.cpu_usage_percent = max(
                    self.performance_metrics.cpu_usage_percent, cpu_usage
                )
                self.performance_metrics.throughput_mbps = max(
                    self.performance_metrics.throughput_mbps, throughput
                )
                self.performance_metrics.success_count += 1
                self.performance_metrics.total_operations += 1
            
            # Update registry cache
            AlgorithmRegistry().update_performance_cache(self.algorithm, self.performance_metrics)
            
            self._notify_observers("decompression_completed", {
                "decompression_time": decompression_time,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage
            })
            
            logger.info(f"Decompression completed: {self.algorithm} - "
                       f"Time: {decompression_time:.3f}s, "
                       f"Throughput: {throughput:.2f} MB/s")
            
            return decompressed_data.decode('utf-8')
            
        except Exception as e:
            self._handle_error(e, "decompression")
            raise CompressionError(f"Decompression failed: {str(e)}") from e
        finally:
            self._set_state(AlgorithmState.IDLE)
    
    def add_observer(self, observer):
        """Add performance observer (Observer pattern)."""
        self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Remove performance observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, event: str, data: Dict[str, Any]):
        """Notify all observers of performance events."""
        for observer in self._observers:
            try:
                observer.on_algorithm_event(self.algorithm, event, data)
            except Exception as e:
                logger.warning(f"Observer notification failed: {e}")
    
    def _set_state(self, state: AlgorithmState):
        """Set algorithm state with thread safety."""
        with self._lock:
            self.state = state
    
    def _handle_error(self, error: Exception, operation: str):
        """Handle errors with proper logging and metrics update."""
        with self._lock:
            self.performance_metrics.error_count += 1
            self.performance_metrics.total_operations += 1
        
        logger.error(f"Algorithm {self.algorithm} {operation} error: {error}")
        self._set_state(AlgorithmState.ERROR)
        self._notify_observers("error", {"operation": operation, "error": str(error)})
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        with self._lock:
            return {
                "algorithm": self.algorithm,
                "state": self.state,
                "metrics": {
                    "compression_time": self.performance_metrics.compression_time,
                    "decompression_time": self.performance_metrics.decompression_time,
                    "compression_ratio": self.performance_metrics.compression_ratio,
                    "memory_usage_mb": self.performance_metrics.memory_usage_mb,
                    "cpu_usage_percent": self.performance_metrics.cpu_usage_percent,
                    "throughput_mbps": self.performance_metrics.throughput_mbps,
                    "success_rate": self.performance_metrics.success_rate,
                    "total_operations": self.performance_metrics.total_operations,
                    "error_count": self.performance_metrics.error_count
                }
            }
    
    @asynccontextmanager
    async def performance_context(self, operation: str):
        """Context manager for performance monitoring."""
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        start_cpu = psutil.cpu_percent()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            end_cpu = psutil.cpu_percent()
            
            duration = end_time - start_time
            memory_usage = (end_memory - start_memory) / (1024 * 1024)
            cpu_usage = (start_cpu + end_cpu) / 2
            
            logger.debug(f"Performance context {operation}: "
                        f"Duration: {duration:.3f}s, "
                        f"Memory: {memory_usage:.2f}MB, "
                        f"CPU: {cpu_usage:.1f}%")


class CompressionError(Exception):
    """Custom exception for compression-related errors."""
    pass


class AlgorithmFactory:
    """Factory pattern for creating algorithm instances."""
    
    @staticmethod
    def create(algorithm: CompressionAlgorithm) -> BaseCompressor:
        """Create algorithm instance based on type."""
        registry = AlgorithmRegistry()
        implementation = registry.get(algorithm)
        
        if implementation is None:
            raise ValueError(f"Algorithm {algorithm} not implemented")
        
        return implementation
    
    @staticmethod
    def create_optimal_algorithm(content_size: int, content_type: str, 
                               target_throughput: Optional[float] = None) -> BaseCompressor:
        """Create optimal algorithm based on content characteristics."""
        # This will be implemented with machine learning later
        # For now, use simple heuristics
        
        if content_size < 1024:  # Small content
            return AlgorithmFactory.create(CompressionAlgorithm.LZ4)
        elif target_throughput and target_throughput > 100:  # High throughput required
            return AlgorithmFactory.create(CompressionAlgorithm.LZ4)
        elif content_size > 1024 * 1024:  # Large content
            return AlgorithmFactory.create(CompressionAlgorithm.ZSTANDARD)
        else:  # Default
            return AlgorithmFactory.create(CompressionAlgorithm.GZIP)


class PerformanceObserver(abc.ABC):
    """Abstract base class for performance observers."""
    
    @abc.abstractmethod
    def on_algorithm_event(self, algorithm: CompressionAlgorithm, event: str, data: Dict[str, Any]):
        """Handle algorithm performance events."""
        pass


class PerformanceLogger(PerformanceObserver):
    """Observer that logs performance events."""
    
    def on_algorithm_event(self, algorithm: CompressionAlgorithm, event: str, data: Dict[str, Any]):
        """Log performance events."""
        logger.info(f"Algorithm {algorithm} event: {event} - {data}")


class PerformanceAggregator(PerformanceObserver):
    """Observer that aggregates performance metrics."""
    
    def __init__(self):
        self.aggregated_metrics = {}
    
    def on_algorithm_event(self, algorithm: CompressionAlgorithm, event: str, data: Dict[str, Any]):
        """Aggregate performance metrics."""
        if algorithm not in self.aggregated_metrics:
            self.aggregated_metrics[algorithm] = {}
        
        if event not in self.aggregated_metrics[algorithm]:
            self.aggregated_metrics[algorithm][event] = []
        
        self.aggregated_metrics[algorithm][event].append(data)
    
    def get_aggregated_summary(self) -> Dict[str, Any]:
        """Get aggregated performance summary."""
        return self.aggregated_metrics
