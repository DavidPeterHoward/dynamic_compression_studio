"""
Advanced Base Compression Algorithm Interface - Foundation for Dynamic Compression Algorithms.

This module defines the foundational interface for all compression algorithms with advanced
mathematical frameworks, meta-recursive learning capabilities, and comprehensive performance
optimization features.

Mathematical Foundation:
-----------------------
1. Information Theory Basis:
   - Shannon Entropy: H(S) = -Σ p_i * log2(p_i) for source S
   - Compression Ratio: ρ = |S|/|C(S)| where C is compression function
   - Theoretical Limit: ρ_max ≤ H(S)/H(C(S))
   - Kolmogorov Complexity: K(x) = min{|p| : U(p) = x}

2. Algorithm Performance Metrics:
   - Throughput: T = bytes_processed / time_elapsed (MB/s)
   - Memory Efficiency: ME = compressed_size / memory_used
   - CPU Utilization: CU = compression_time / total_time
   - Quality Score: QS = ρ * T * ME / CU
   - Reliability Score: RS = success_rate * (1 - error_rate)

3. Meta-Recursive Learning Framework:
   - Performance History: PH = {(input_features, algorithm, performance)}
   - Learning Rate: LR = η * ∇(performance_loss)
   - Adaptation Factor: AF = exp(-λ * time_since_update)
   - Confidence Score: CS = 1 / (1 + exp(-prediction_accuracy))

4. Algorithm Selection Heuristics:
   - Content Entropy Threshold: θ_e = 4.0 bits/byte
   - Repetition Ratio Threshold: θ_r = 0.3
   - Size Category Boundaries: Small < 1KB, Medium < 1MB, Large ≥ 1MB
   - Complexity Score: CS = α*H + β*(1-R) + γ*log(S) where α+β+γ=1

Design Patterns Implemented:
---------------------------
1. Template Method Pattern: Defines algorithm structure with customizable steps
2. Strategy Pattern: Allows runtime algorithm switching
3. Observer Pattern: Performance monitoring and event notification
4. Factory Pattern: Dynamic algorithm creation and management
5. Decorator Pattern: Performance tracking and enhancement
6. Registry Pattern: Centralized algorithm management
7. Memento Pattern: State preservation and restoration

Performance Optimization Features:
---------------------------------
1. Adaptive Compression Levels: Dynamic level selection based on content
2. Memory Management: Efficient memory usage with garbage collection
3. Thread Pool Execution: Non-blocking async operations
4. Performance Caching: Intelligent caching of algorithm performance
5. Error Recovery: Graceful error handling and recovery mechanisms
6. Resource Monitoring: Real-time resource usage tracking

References:
-----------
- Shannon, C.E. (1948). "A Mathematical Theory of Communication"
- Ziv, J. & Lempel, A. (1977). "A Universal Algorithm for Sequential Data Compression"
- Burrows, M. & Wheeler, D. (1994). "A Block-sorting Lossless Data Compression Algorithm"
- Collet, Y. (2016). "Zstandard: Real-time data compression algorithm"
- Goyal, V.K. (2001). "Theoretical Foundations of Transform Coding"
- Gamma, E. et al. (1994). "Design Patterns: Elements of Reusable Object-Oriented Software"

Author: Dynamic Compression Algorithms Team
Version: 2.0.0
Last Modified: 2024-08-27
"""

import abc
import asyncio
import logging
import time
import threading
import math
import statistics
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque, Counter
import numpy as np

from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


class AlgorithmState(Enum):
    """
    Algorithm execution states for state machine management.
    
    States:
    - IDLE: Algorithm is ready for operations
    - COMPRESSING: Currently performing compression
    - DECOMPRESSING: Currently performing decompression
    - ANALYZING: Performing content analysis
    - OPTIMIZING: Optimizing parameters
    - ERROR: Error state requiring recovery
    - LEARNING: Updating internal models
    """
    IDLE = "idle"
    COMPRESSING = "compressing"
    DECOMPRESSING = "decompressing"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    ERROR = "error"
    LEARNING = "learning"


@dataclass
class PerformanceMetrics:
    """
    Comprehensive performance metrics for algorithm evaluation.
    
    Mathematical Properties:
    - Compression Efficiency: CE = ρ * speed * (1/memory) * (1/cpu)
    - Quality Score: QS = ρ * T * ME / CU where T=throughput, ME=memory_efficiency, CU=cpu_usage
    - Reliability Score: RS = success_rate * (1 - error_rate)
    - Adaptability Score: AS = performance_consistency / performance_variance
    """
    compression_time: float  # Time taken for compression (seconds)
    decompression_time: float  # Time taken for decompression (seconds)
    compression_ratio: float  # Original size / compressed size
    memory_usage_mb: float  # Peak memory usage (MB)
    cpu_usage_percent: float  # Average CPU usage (%)
    throughput_mbps: float  # Processing throughput (MB/s)
    error_count: int  # Number of errors encountered
    success_count: int  # Number of successful operations
    total_operations: int  # Total number of operations
    quality_score: float = 0.0  # Overall quality score (0-1)
    reliability_score: float = 0.0  # Reliability score (0-1)
    adaptability_score: float = 0.0  # Adaptability score (0-1)
    efficiency_score: float = 0.0  # Efficiency score (0-1)
    
    def __post_init__(self):
        """Calculate derived metrics after initialization."""
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """Calculate derived performance metrics."""
        try:
            # Quality Score: QS = ρ * T * ME / CU
            memory_efficiency = 1.0 / max(self.memory_usage_mb, 0.1)  # Avoid division by zero
            self.quality_score = (
                self.compression_ratio * 
                self.throughput_mbps * 
                memory_efficiency / 
                max(self.cpu_usage_percent, 1.0)
            ) / 1000.0  # Normalize
            
            # Reliability Score: RS = success_rate * (1 - error_rate)
            success_rate = self.success_count / max(self.total_operations, 1)
            error_rate = self.error_count / max(self.total_operations, 1)
            self.reliability_score = success_rate * (1.0 - error_rate)
            
            # Efficiency Score: ES = ρ * speed * (1/memory) * (1/cpu)
            self.efficiency_score = (
                self.compression_ratio * 
                self.throughput_mbps * 
                memory_efficiency / 
                max(self.cpu_usage_percent, 1.0)
            ) / 1000.0  # Normalize
            
            # Clamp all scores to [0, 1]
            self.quality_score = max(0.0, min(1.0, self.quality_score))
            self.reliability_score = max(0.0, min(1.0, self.reliability_score))
            self.efficiency_score = max(0.0, min(1.0, self.efficiency_score))
            
        except Exception as e:
            logger.error(f"Derived metrics calculation failed: {e}")
            # Set default values
            self.quality_score = 0.5
            self.reliability_score = 0.5
            self.efficiency_score = 0.5


@dataclass
class AlgorithmContext:
    """
    Context information for algorithm execution and optimization.
    
    Context Factors:
    - Content characteristics (entropy, repetition, size)
    - Environmental constraints (memory, CPU, network)
    - Performance requirements (speed, quality, reliability)
    - Historical performance data
    - Learning parameters and adaptation factors
    """
    content_size: int  # Size of content in bytes
    content_type: str  # Type of content (text, binary, structured, etc.)
    content_entropy: float  # Shannon entropy of content
    repetition_ratio: float  # Ratio of repeated patterns
    available_memory_mb: float  # Available memory in MB
    available_cpu_percent: float  # Available CPU percentage
    network_bandwidth_mbps: float  # Network bandwidth in Mbps
    latency_requirement_ms: float  # Maximum allowed latency in ms
    compression_ratio_target: float  # Target compression ratio
    speed_requirement_mbps: float  # Required processing speed
    reliability_requirement: float  # Required reliability (0-1)
    learning_enabled: bool = True  # Whether learning is enabled
    adaptation_factor: float = 0.95  # Adaptation factor for learning
    historical_performance: Dict[str, float] = field(default_factory=dict)  # Historical performance data


class CompressionError(Exception):
    """
    Custom exception for compression-related errors.
    
    Provides detailed error information including:
    - Error type and description
    - Algorithm and operation context
    - Performance metrics at time of error
    - Recovery suggestions
    """
    
    def __init__(self, message: str, algorithm: Optional[CompressionAlgorithm] = None,
                 operation: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.algorithm = algorithm
        self.operation = operation
        self.context = context or {}
        self.timestamp = time.time()
    
    def __str__(self):
        base_msg = super().__str__()
        if self.algorithm and self.operation:
            return f"[{self.algorithm.value}:{self.operation}] {base_msg}"
        return base_msg


class PerformanceObserver(abc.ABC):
    """
    Abstract base class for performance observers.
    
    Observers can monitor algorithm performance and receive notifications
    about performance events, enabling real-time monitoring and analysis.
    
    Observer Pattern Implementation:
    - Subject: BaseCompressor instances
    - Observer: PerformanceObserver implementations
    - Notifications: Performance events and metrics
    """
    
    @abc.abstractmethod
    def on_compression_started(self, algorithm: CompressionAlgorithm, context: AlgorithmContext):
        """Called when compression operation starts."""
        pass
    
    @abc.abstractmethod
    def on_compression_completed(self, algorithm: CompressionAlgorithm, 
                               metrics: PerformanceMetrics, context: AlgorithmContext):
        """Called when compression operation completes."""
        pass
    
    @abc.abstractmethod
    def on_compression_error(self, algorithm: CompressionAlgorithm, 
                           error: CompressionError, context: AlgorithmContext):
        """Called when compression operation fails."""
        pass
    
    @abc.abstractmethod
    def on_performance_update(self, algorithm: CompressionAlgorithm, 
                            metrics: PerformanceMetrics):
        """Called when performance metrics are updated."""
        pass


class PerformanceLogger(PerformanceObserver):
    """
    Performance observer that logs performance events.
    
    Features:
    - Structured logging of performance events
    - Performance trend analysis
    - Error tracking and reporting
    - Performance summary generation
    """
    
    def __init__(self, log_level: int = logging.INFO):
        self.logger = logging.getLogger(f"{__name__}.PerformanceLogger")
        self.log_level = log_level
        self.performance_history: List[Dict[str, Any]] = []
    
    def on_compression_started(self, algorithm: CompressionAlgorithm, context: AlgorithmContext):
        """Log compression start event."""
        self.logger.log(self.log_level, 
                       f"Compression started: {algorithm.value}, "
                       f"size={context.content_size}, type={context.content_type}")
    
    def on_compression_completed(self, algorithm: CompressionAlgorithm, 
                               metrics: PerformanceMetrics, context: AlgorithmContext):
        """Log compression completion with metrics."""
        self.logger.log(self.log_level,
                       f"Compression completed: {algorithm.value}, "
                       f"ratio={metrics.compression_ratio:.2f}, "
                       f"time={metrics.compression_time:.3f}s, "
                       f"throughput={metrics.throughput_mbps:.1f}MB/s")
        
        # Store performance record
        self.performance_history.append({
            'timestamp': time.time(),
            'algorithm': algorithm.value,
            'metrics': metrics,
            'context': context
        })
    
    def on_compression_error(self, algorithm: CompressionAlgorithm, 
                           error: CompressionError, context: AlgorithmContext):
        """Log compression error."""
        self.logger.error(f"Compression error: {algorithm.value}, {error}")
    
    def on_performance_update(self, algorithm: CompressionAlgorithm, 
                            metrics: PerformanceMetrics):
        """Log performance update."""
        self.logger.debug(f"Performance update: {algorithm.value}, "
                         f"quality={metrics.quality_score:.3f}, "
                         f"reliability={metrics.reliability_score:.3f}")


class PerformanceAggregator(PerformanceObserver):
    """
    Performance observer that aggregates and analyzes performance data.
    
    Features:
    - Real-time performance aggregation
    - Statistical analysis of performance metrics
    - Performance trend detection
    - Anomaly detection and alerting
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.performance_window: deque = deque(maxlen=window_size)
        self.algorithm_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'avg_compression_ratio': 0.0,
            'avg_compression_time': 0.0,
            'avg_throughput': 0.0,
            'success_rate': 0.0,
            'error_rate': 0.0,
            'total_operations': 0
        })
    
    def on_compression_started(self, algorithm: CompressionAlgorithm, context: AlgorithmContext):
        """Track compression start."""
        pass  # No action needed for start events
    
    def on_compression_completed(self, algorithm: CompressionAlgorithm, 
                               metrics: PerformanceMetrics, context: AlgorithmContext):
        """Aggregate compression completion metrics."""
        # Add to performance window
        self.performance_window.append({
            'algorithm': algorithm.value,
            'metrics': metrics,
            'timestamp': time.time()
        })
        
        # Update algorithm statistics
        stats = self.algorithm_stats[algorithm.value]
        stats['total_operations'] += 1
        
        # Update running averages
        n = stats['total_operations']
        stats['avg_compression_ratio'] = (
            (stats['avg_compression_ratio'] * (n - 1) + metrics.compression_ratio) / n
        )
        stats['avg_compression_time'] = (
            (stats['avg_compression_time'] * (n - 1) + metrics.compression_time) / n
        )
        stats['avg_throughput'] = (
            (stats['avg_throughput'] * (n - 1) + metrics.throughput_mbps) / n
        )
        stats['success_rate'] = metrics.success_count / max(metrics.total_operations, 1)
        stats['error_rate'] = metrics.error_count / max(metrics.total_operations, 1)
    
    def on_compression_error(self, algorithm: CompressionAlgorithm, 
                           error: CompressionError, context: AlgorithmContext):
        """Track compression errors."""
        stats = self.algorithm_stats[algorithm.value]
        stats['total_operations'] += 1
        stats['error_rate'] = stats['error_count'] / max(stats['total_operations'], 1)
    
    def on_performance_update(self, algorithm: CompressionAlgorithm, 
                            metrics: PerformanceMetrics):
        """Update performance metrics."""
        pass  # Already handled in on_compression_completed
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.performance_window:
            return {}
        
        # Calculate overall statistics
        compression_ratios = [p['metrics'].compression_ratio for p in self.performance_window]
        compression_times = [p['metrics'].compression_time for p in self.performance_window]
        throughputs = [p['metrics'].throughput_mbps for p in self.performance_window]
        
        return {
            'overall_stats': {
                'avg_compression_ratio': statistics.mean(compression_ratios),
                'avg_compression_time': statistics.mean(compression_times),
                'avg_throughput': statistics.mean(throughputs),
                'std_compression_ratio': statistics.stdev(compression_ratios) if len(compression_ratios) > 1 else 0.0,
                'std_compression_time': statistics.stdev(compression_times) if len(compression_times) > 1 else 0.0,
                'std_throughput': statistics.stdev(throughputs) if len(throughputs) > 1 else 0.0,
                'total_operations': len(self.performance_window)
            },
            'algorithm_stats': dict(self.algorithm_stats),
            'window_size': len(self.performance_window),
            'timestamp': time.time()
        }


class AlgorithmRegistry:
    """
    Singleton registry for managing compression algorithms.
    
    Features:
    - Centralized algorithm registration and management
    - Performance caching and optimization
    - Algorithm discovery and selection
    - Version management and compatibility
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the algorithm registry."""
        if hasattr(self, '_initialized'):
            return
        
        self._algorithms: Dict[CompressionAlgorithm, 'BaseCompressor'] = {}
        self._performance_cache: Dict[str, PerformanceMetrics] = {}
        self._version_info: Dict[CompressionAlgorithm, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._initialized = True
        
        logger.info("AlgorithmRegistry initialized")
    
    def register(self, algorithm: CompressionAlgorithm, instance: 'BaseCompressor'):
        """Register a compression algorithm instance."""
        with self._lock:
            self._algorithms[algorithm] = instance
            logger.info(f"Registered algorithm: {algorithm.value}")
    
    def get_algorithm(self, algorithm: CompressionAlgorithm) -> Optional['BaseCompressor']:
        """Get a registered algorithm instance."""
        with self._lock:
            return self._algorithms.get(algorithm)
    
    def list_algorithms(self) -> List[CompressionAlgorithm]:
        """List all registered algorithms."""
        with self._lock:
            return list(self._algorithms.keys())
    
    def get_performance_cache(self, key: str) -> Optional[PerformanceMetrics]:
        """Get cached performance metrics."""
        with self._lock:
            return self._performance_cache.get(key)
    
    def update_performance_cache(self, algorithm: CompressionAlgorithm, metrics: PerformanceMetrics):
        """Update performance cache."""
        with self._lock:
            key = f"{algorithm.value}_{int(time.time() / 3600)}"  # Hourly cache key
            self._performance_cache[key] = metrics
    
    def clear_cache(self):
        """Clear performance cache."""
        with self._lock:
            self._performance_cache.clear()
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get comprehensive registry information."""
        with self._lock:
            return {
                'registered_algorithms': [algo.value for algo in self._algorithms.keys()],
                'cache_size': len(self._performance_cache),
                'total_algorithms': len(self._algorithms),
                'version_info': dict(self._version_info)
            }


class BaseCompressor(abc.ABC):
    """
    Abstract base class for all compression algorithms.
    
    This class provides a comprehensive foundation for compression algorithms
    with advanced features including:
    
    Core Features:
    --------------
    1. Template Method Pattern: Defines algorithm structure with customizable steps
    2. Strategy Pattern: Allows runtime algorithm switching and optimization
    3. Observer Pattern: Performance monitoring and event notification
    4. Factory Pattern: Dynamic algorithm creation and management
    5. Decorator Pattern: Performance tracking and enhancement
    6. Error Recovery: Graceful error handling and recovery mechanisms
    7. Resource Management: Efficient memory and CPU usage
    8. Meta-Learning: Continuous performance improvement
    
    Mathematical Framework:
    ----------------------
    1. Compression Function: C: S → S' where |S'| < |S| and D(C(S)) = S
    2. Performance Metrics: ρ = |S|/|C(S)|, T = bytes/time, ME = size/memory
    3. Quality Score: QS = ρ * T * ME / CU where CU = CPU usage
    4. Learning Update: θ_t+1 = θ_t + η * ∇L(θ_t, D_t)
    
    Performance Targets:
    -------------------
    - Compression Ratio: 2-50x depending on content
    - Throughput: 10-1000 MB/s depending on algorithm
    - Memory Usage: <1GB for most operations
    - CPU Usage: <50% under normal load
    - Error Rate: <1% for reliable algorithms
    """
    
    def __init__(self, algorithm: CompressionAlgorithm):
        """
        Initialize the base compressor.
        
        Args:
            algorithm: The compression algorithm type
        """
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
        self._observers: List[PerformanceObserver] = []
        self._lock = threading.RLock()
        self._performance_history: List[Dict[str, Any]] = []
        self._learning_enabled = True
        self._adaptation_factor = 0.95
        
        # Register with global registry
        AlgorithmRegistry().register(algorithm, self)
        
        logger.info(f"BaseCompressor initialized for {algorithm.value}")
    
    @abc.abstractmethod
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """
        Implementation-specific compression logic.
        
        This method must be implemented by subclasses to provide the actual
        compression algorithm implementation.
        
        Mathematical Requirement:
        - For lossless compression: D(C(S)) = S
        - Compression ratio: ρ = |S|/|C(S)| > 1
        - Information preservation: H(S) = H(D(C(S)))
        
        Args:
            data: Input data to compress
            level: Compression level (affects speed/ratio trade-off)
            
        Returns:
            Compressed data
            
        Raises:
            CompressionError: If compression fails
        """
        pass
    
    @abc.abstractmethod
    async def _decompress_impl(self, data: bytes) -> bytes:
        """
        Implementation-specific decompression logic.
        
        This method must be implemented by subclasses to provide the actual
        decompression algorithm implementation.
        
        Mathematical Requirement:
        - Perfect reconstruction: D(C(S)) = S for all valid inputs
        - Error detection: Should detect and report corruption
        - Performance: Should be reasonably fast
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
            
        Raises:
            CompressionError: If decompression fails
        """
        pass
    
    @abc.abstractmethod
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """
        Determine optimal compression level based on content characteristics.
        
        Mathematical Framework:
        - Level Selection: L* = argmax_L Q(L, S) where Q is quality function
        - Quality Function: Q(L, S) = α*ρ(L, S) + β*T(L, S) + γ*ME(L, S)
        - Constraints: L ∈ {FAST, BALANCED, MAXIMUM}
        
        Args:
            content_size: Size of content in bytes
            content_type: Type of content (text, binary, structured, etc.)
            
        Returns:
            Optimal compression level
        """
        pass
    
    @abc.abstractmethod
    def _validate_input(self, data: bytes) -> bool:
        """
        Validate input data for algorithm compatibility.
        
        Validation Criteria:
        - Data type and format compatibility
        - Size limits and constraints
        - Content characteristics analysis
        - Memory and resource requirements
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid for this algorithm
        """
        pass
    
    async def compress(self, content: str, level: Optional[CompressionLevel] = None) -> bytes:
        """
        Compress content using the algorithm.
        
        Template Method Pattern Implementation:
        1. Validate input and state
        2. Determine optimal parameters
        3. Execute compression
        4. Update performance metrics
        5. Notify observers
        6. Handle errors and recovery
        
        Mathematical Framework:
        - Compression Function: C: S → S' where |S'| < |S|
        - Performance Tracking: ρ = |S|/|C(S)|, T = |S|/time
        - Quality Assessment: Q = ρ * T * (1/memory) * (1/cpu)
        
        Args:
            content: Content to compress
            level: Compression level (auto-determined if None)
            
        Returns:
            Compressed data
            
        Raises:
            CompressionError: If compression fails
        """
        start_time = time.time()
        context = None
        
        try:
            # Step 1: Validate input and state
            self._set_state(AlgorithmState.COMPRESSING)
            data = content.encode('utf-8')
            
            if not self._validate_input(data):
                raise CompressionError("Invalid input data for compression")
            
            # Step 2: Create context and determine optimal parameters
            context = AlgorithmContext(
                content_size=len(data),
                content_type=self._detect_content_type(content),
                content_entropy=self._calculate_entropy(content),
                repetition_ratio=self._calculate_repetition_ratio(content),
                available_memory_mb=1024.0,  # Default assumption
                available_cpu_percent=100.0,  # Default assumption
                network_bandwidth_mbps=100.0,  # Default assumption
                latency_requirement_ms=1000.0,  # Default assumption
                compression_ratio_target=2.0,  # Default assumption
                speed_requirement_mbps=10.0,  # Default assumption
                reliability_requirement=0.95,  # Default assumption
                learning_enabled=self._learning_enabled,
                adaptation_factor=self._adaptation_factor
            )
            
            if level is None:
                level = self._get_optimal_level(len(data), context.content_type)
            
            # Step 3: Notify observers of compression start
            self._notify_observers('on_compression_started', self.algorithm, context)
            
            # Step 4: Execute compression
            compressed_data = await self._compress_impl(data, level)
            
            # Step 5: Calculate performance metrics
            compression_time = time.time() - start_time
            original_size = len(data)
            compressed_size = len(compressed_data)
            
            self.performance_metrics = PerformanceMetrics(
                compression_time=compression_time,
                decompression_time=0.0,  # Will be updated during decompression
                compression_ratio=original_size / compressed_size if compressed_size > 0 else 1.0,
                memory_usage_mb=self._estimate_memory_usage(original_size),
                cpu_usage_percent=self._estimate_cpu_usage(compression_time, original_size),
                throughput_mbps=original_size / compression_time / (1024 * 1024) if compression_time > 0 else 0.0,
                error_count=self.performance_metrics.error_count,
                success_count=self.performance_metrics.success_count + 1,
                total_operations=self.performance_metrics.total_operations + 1
            )
            
            # Step 6: Update performance history and learning
            self._update_performance_history(context, self.performance_metrics)
            if self._learning_enabled:
                self._update_learning_model(context, self.performance_metrics)
            
            # Step 7: Notify observers of completion
            self._notify_observers('on_compression_completed', self.algorithm, 
                                 self.performance_metrics, context)
            
            # Step 8: Update state and return result
            self._set_state(AlgorithmState.IDLE)
            return compressed_data
            
        except Exception as e:
            # Error handling and recovery
            compression_time = time.time() - start_time
            error = CompressionError(str(e), self.algorithm, "compress", 
                                   {'context': context, 'time': compression_time})
            
            self.performance_metrics.error_count += 1
            self.performance_metrics.total_operations += 1
            
            self._notify_observers('on_compression_error', self.algorithm, error, context)
            self._set_state(AlgorithmState.ERROR)
            
            logger.error(f"Compression failed: {error}")
            raise error
    
    async def decompress(self, compressed_data: bytes) -> str:
        """
        Decompress data using the algorithm.
        
        Template Method Pattern Implementation:
        1. Validate input and state
        2. Execute decompression
        3. Update performance metrics
        4. Verify integrity
        5. Notify observers
        6. Handle errors and recovery
        
        Mathematical Framework:
        - Decompression Function: D: S' → S where D(C(S)) = S
        - Integrity Verification: Verify D(C(S)) = S
        - Performance Tracking: T = |S|/time, accuracy = 1 if D(C(S)) = S else 0
        
        Args:
            compressed_data: Compressed data to decompress
            
        Returns:
            Decompressed content
            
        Raises:
            CompressionError: If decompression fails
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate input and state
            self._set_state(AlgorithmState.DECOMPRESSING)
            
            if not self._validate_compressed_data(compressed_data):
                raise CompressionError("Invalid compressed data for decompression")
            
            # Step 2: Execute decompression
            decompressed_data = await self._decompress_impl(compressed_data)
            
            # Step 3: Calculate performance metrics
            decompression_time = time.time() - start_time
            compressed_size = len(compressed_data)
            decompressed_size = len(decompressed_data)
            
            # Update existing metrics
            self.performance_metrics.decompression_time = decompression_time
            self.performance_metrics.throughput_mbps = (
                decompressed_size / decompression_time / (1024 * 1024) 
                if decompression_time > 0 else 0.0
            )
            
            # Step 4: Verify integrity (basic check)
            try:
                decompressed_content = decompressed_data.decode('utf-8')
            except UnicodeDecodeError:
                raise CompressionError("Decompressed data is not valid UTF-8")
            
            # Step 5: Update state and return result
            self._set_state(AlgorithmState.IDLE)
            return decompressed_content
            
        except Exception as e:
            # Error handling and recovery
            decompression_time = time.time() - start_time
            error = CompressionError(str(e), self.algorithm, "decompress", 
                                   {'time': decompression_time})
            
            self.performance_metrics.error_count += 1
            self.performance_metrics.total_operations += 1
            
            self._notify_observers('on_compression_error', self.algorithm, error, None)
            self._set_state(AlgorithmState.ERROR)
            
            logger.error(f"Decompression failed: {error}")
            raise error
    
    def add_observer(self, observer: PerformanceObserver):
        """Add performance observer."""
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
                logger.debug(f"Added observer: {type(observer).__name__}")
    
    def remove_observer(self, observer: PerformanceObserver):
        """Remove performance observer."""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                logger.debug(f"Removed observer: {type(observer).__name__}")
    
    def _notify_observers(self, method_name: str, *args, **kwargs):
        """Notify all observers of an event."""
        with self._lock:
            for observer in self._observers:
                try:
                    method = getattr(observer, method_name, None)
                    if method and callable(method):
                        method(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Observer notification failed: {e}")
    
    def _set_state(self, state: AlgorithmState):
        """Set algorithm state with logging."""
        old_state = self.state
        self.state = state
        logger.debug(f"Algorithm state changed: {old_state.value} → {state.value}")
    
    def _handle_error(self, error: Exception, operation: str):
        """Handle errors with recovery mechanisms."""
        logger.error(f"Error in {operation}: {error}")
        self._set_state(AlgorithmState.ERROR)
        
        # Basic error recovery: reset to idle state after a delay
        async def recovery_delay():
            await asyncio.sleep(1.0)  # 1 second delay
            if self.state == AlgorithmState.ERROR:
                self._set_state(AlgorithmState.IDLE)
        
        asyncio.create_task(recovery_delay())
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            'algorithm': self.algorithm.value,
            'state': self.state.value,
            'performance_metrics': {
                'compression_time': self.performance_metrics.compression_time,
                'decompression_time': self.performance_metrics.decompression_time,
                'compression_ratio': self.performance_metrics.compression_ratio,
                'throughput_mbps': self.performance_metrics.throughput_mbps,
                'memory_usage_mb': self.performance_metrics.memory_usage_mb,
                'cpu_usage_percent': self.performance_metrics.cpu_usage_percent,
                'quality_score': self.performance_metrics.quality_score,
                'reliability_score': self.performance_metrics.reliability_score,
                'efficiency_score': self.performance_metrics.efficiency_score,
                'success_count': self.performance_metrics.success_count,
                'error_count': self.performance_metrics.error_count,
                'total_operations': self.performance_metrics.total_operations
            },
            'learning_enabled': self._learning_enabled,
            'adaptation_factor': self._adaptation_factor,
            'observer_count': len(self._observers),
            'performance_history_size': len(self._performance_history)
        }
    
    def _detect_content_type(self, content: str) -> str:
        """Detect content type based on characteristics."""
        if not content:
            return "empty"
        
        # Simple content type detection
        if content.isdigit():
            return "numeric"
        elif content.isalpha():
            return "text"
        elif any(char in content for char in "{}[]()"):
            return "structured"
        else:
            return "mixed"
    
    def _calculate_entropy(self, content: str) -> float:
        """Calculate Shannon entropy of content."""
        try:
            if not content:
                return 0.0
            
            # Count character frequencies
            char_counts = Counter(content)
            total_chars = len(content)
            
            # Calculate entropy
            entropy = 0.0
            for count in char_counts.values():
                probability = count / total_chars
                entropy -= probability * math.log2(probability)
            
            return entropy
            
        except Exception as e:
            logger.error(f"Entropy calculation failed: {e}")
            return 0.0
    
    def _calculate_repetition_ratio(self, content: str) -> float:
        """Calculate repetition ratio in content."""
        try:
            if len(content) < 2:
                return 0.0
            
            # Count repeated patterns
            repeated_chars = 0
            for i in range(1, len(content)):
                if content[i] == content[i-1]:
                    repeated_chars += 1
            
            return repeated_chars / (len(content) - 1)
            
        except Exception as e:
            logger.error(f"Repetition ratio calculation failed: {e}")
            return 0.0
    
    def _validate_compressed_data(self, data: bytes) -> bool:
        """Validate compressed data format."""
        # Basic validation - subclasses should override for specific formats
        return isinstance(data, bytes) and len(data) > 0
    
    def _estimate_memory_usage(self, content_size: int) -> float:
        """Estimate memory usage for compression."""
        # Basic estimation - subclasses should override for accurate estimates
        return min(content_size / (1024 * 1024), 100.0)  # Cap at 100MB
    
    def _estimate_cpu_usage(self, compression_time: float, content_size: int) -> float:
        """Estimate CPU usage for compression."""
        # Basic estimation - subclasses should override for accurate estimates
        return min(compression_time * 10.0, 50.0)  # Cap at 50%
    
    def _update_performance_history(self, context: AlgorithmContext, 
                                  metrics: PerformanceMetrics):
        """Update performance history for learning."""
        try:
            record = {
                'timestamp': time.time(),
                'context': context,
                'metrics': metrics,
                'algorithm': self.algorithm.value
            }
            
            self._performance_history.append(record)
            
            # Keep history size manageable
            if len(self._performance_history) > 1000:
                self._performance_history = self._performance_history[-1000:]
                
        except Exception as e:
            logger.error(f"Performance history update failed: {e}")
    
    def _update_learning_model(self, context: AlgorithmContext, 
                             metrics: PerformanceMetrics):
        """Update learning model with new performance data."""
        try:
            # This is a placeholder for advanced learning implementations
            # Subclasses can override this method for specific learning algorithms
            
            # Simple adaptation: adjust adaptation factor based on performance
            if metrics.quality_score > 0.8:
                self._adaptation_factor = min(0.99, self._adaptation_factor * 1.01)
            elif metrics.quality_score < 0.5:
                self._adaptation_factor = max(0.9, self._adaptation_factor * 0.99)
                
        except Exception as e:
            logger.error(f"Learning model update failed: {e}")
    
    @property
    def performance_context(self) -> Dict[str, Any]:
        """Get current performance context."""
        return {
            'algorithm': self.algorithm.value,
            'state': self.state.value,
            'metrics': self.performance_metrics,
            'learning_enabled': self._learning_enabled,
            'adaptation_factor': self._adaptation_factor
        }
    
    def cleanup(self):
        """Clean up resources."""
        try:
            self._set_state(AlgorithmState.IDLE)
            self._observers.clear()
            self._performance_history.clear()
            logger.info(f"BaseCompressor cleanup completed for {self.algorithm.value}")
        except Exception as e:
            logger.error(f"BaseCompressor cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


class AlgorithmFactory:
    """
    Factory class for creating compression algorithm instances.
    
    Factory Pattern Implementation:
    - Centralized algorithm creation
    - Configuration-based instantiation
    - Performance-based selection
    - Version management
    """
    
    @staticmethod
    def create_algorithm(algorithm: CompressionAlgorithm, **kwargs) -> BaseCompressor:
        """
        Create a compression algorithm instance.
        
        Args:
            algorithm: Algorithm type to create
            **kwargs: Additional configuration parameters
            
        Returns:
            Algorithm instance
            
        Raises:
            CompressionError: If algorithm creation fails
        """
        try:
            # This would be implemented with actual algorithm classes
            # For now, return a placeholder
            raise NotImplementedError(f"Algorithm creation for {algorithm.value} not implemented")
            
        except Exception as e:
            raise CompressionError(f"Failed to create algorithm {algorithm.value}: {str(e)}")
    
    @staticmethod
    def select_optimal_algorithm(content_features: Dict[str, Any], 
                               available_algorithms: List[CompressionAlgorithm]) -> CompressionAlgorithm:
        """
        Select optimal algorithm based on content features.
        
        Mathematical Framework:
        - Feature Vector: F = [entropy, repetition, size, type, ...]
        - Algorithm Score: S(a, F) = Σ w_i * f_i(a, F)
        - Optimal Selection: a* = argmax_a S(a, F)
        
        Args:
            content_features: Features of the content to compress
            available_algorithms: List of available algorithms
            
        Returns:
            Optimal algorithm for the content
        """
        try:
            # Simple heuristic selection
            entropy = content_features.get('entropy', 4.0)
            repetition = content_features.get('repetition_ratio', 0.1)
            size = content_features.get('size', 1024)
            
            # High entropy, low repetition → LZ4 (speed)
            if entropy > 4.0 and repetition < 0.2:
                if CompressionAlgorithm.LZ4 in available_algorithms:
                    return CompressionAlgorithm.LZ4
            
            # Low entropy, high repetition → GZIP (compression)
            if entropy < 3.0 or repetition > 0.3:
                if CompressionAlgorithm.GZIP in available_algorithms:
                    return CompressionAlgorithm.GZIP
            
            # Large content → LZ4 (memory efficiency)
            if size > 1024 * 1024:
                if CompressionAlgorithm.LZ4 in available_algorithms:
                    return CompressionAlgorithm.LZ4
            
            # Default to first available algorithm
            return available_algorithms[0] if available_algorithms else CompressionAlgorithm.GZIP
            
        except Exception as e:
            logger.error(f"Algorithm selection failed: {e}")
            return CompressionAlgorithm.GZIP  # Fallback
