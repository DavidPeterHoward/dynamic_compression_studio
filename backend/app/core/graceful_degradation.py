"""
Advanced Graceful Degradation and Fallback System

This system provides intelligent fallback mechanisms for compression operations:
1. Multi-level fallback hierarchy
2. Automatic algorithm switching on failure
3. Resource-aware degradation
4. Circuit breaker pattern implementation
5. Retry with exponential backoff
6. Health monitoring and recovery
7. Performance-based routing
8. Load shedding under pressure
9. Predictive failure detection
10. Self-healing capabilities

Mathematical Model:
------------------
Failure Probability: P(F) = 1 - e^(-λt)
Where λ is failure rate, t is time

Recovery Time: R(t) = R₀ * (1 - e^(-μt))
Where μ is recovery rate

Algorithm Selection Score:
S(a) = w₁*P(success) + w₂*Performance + w₃*Resources

Circuit Breaker States:
CLOSED → OPEN (failures > threshold)
OPEN → HALF_OPEN (after timeout)
HALF_OPEN → CLOSED (success) or OPEN (failure)

References:
- Nygard, M. (2007). "Release It!: Design and Deploy Production-Ready Software"
- Bulkhead Pattern: https://docs.microsoft.com/en-us/azure/architecture/patterns/bulkhead
- Circuit Breaker Pattern: https://martinfowler.com/bliki/CircuitBreaker.html
"""

import time
import threading
import queue
import logging
import traceback
import functools
import random
import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import numpy as np
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import psutil
import gc
import warnings

# Import compression algorithms
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.base_algorithm import BaseCompressionAlgorithm


class HealthStatus(Enum):
    """Health status of algorithm/system."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class AlgorithmHealth:
    """Health metrics for an algorithm."""
    algorithm_name: str
    status: HealthStatus = HealthStatus.HEALTHY
    success_count: int = 0
    failure_count: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    error_messages: List[str] = field(default_factory=list)
    performance_history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 1.0
        return self.success_count / self.total_requests
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        return 1.0 - self.success_rate
    
    def update_status(self):
        """Update health status based on metrics."""
        if self.failure_rate > 0.5:
            self.status = HealthStatus.CRITICAL
        elif self.failure_rate > 0.2:
            self.status = HealthStatus.UNHEALTHY
        elif self.failure_rate > 0.05:
            self.status = HealthStatus.DEGRADED
        else:
            self.status = HealthStatus.HEALTHY


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for an algorithm.
    
    Prevents cascading failures by failing fast when an algorithm
    is experiencing issues.
    """
    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_requests: int = 3
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    half_open_successes: int = 0
    
    def record_success(self):
        """Record successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            if self.half_open_successes >= self.half_open_requests:
                self.close()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.open()
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.open()
    
    def open(self):
        """Open circuit (stop requests)."""
        self.state = CircuitState.OPEN
        self.half_open_successes = 0
        logging.warning(f"Circuit breaker {self.name} OPENED")
    
    def close(self):
        """Close circuit (allow requests)."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_successes = 0
        logging.info(f"Circuit breaker {self.name} CLOSED")
    
    def half_open(self):
        """Enter half-open state (test recovery)."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_successes = 0
        logging.info(f"Circuit breaker {self.name} HALF-OPEN")
    
    def can_execute(self) -> bool:
        """Check if request can be executed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.half_open()
                    return True
            return False
        
        # HALF_OPEN state
        return True


@dataclass
class RetryPolicy:
    """Retry policy configuration."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            # Add random jitter to prevent thundering herd
            delay *= (0.5 + random.random())
        
        return delay


class ResourceMonitor:
    """
    Monitor system resources for adaptive degradation.
    
    Tracks:
    - CPU usage
    - Memory usage
    - I/O throughput
    - Network bandwidth
    - Thread/process count
    """
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize resource monitor.
        
        Args:
            thresholds: Resource thresholds for degradation
        """
        self.thresholds = thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_io_percent': 90.0,
            'thread_count': 1000
        }
        
        self.current_metrics = {}
        self.history = deque(maxlen=60)  # 1 minute of history
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 1.0):
        """Start resource monitoring."""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                metrics = self.get_current_metrics()
                self.current_metrics = metrics
                self.history.append(metrics)
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current resource metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / 1e6,
                'thread_count': threading.active_count(),
                'timestamp': time.time()
            }
            
            if disk_io:
                # Calculate I/O rate
                if hasattr(self, '_last_disk_io'):
                    time_delta = time.time() - self._last_io_time
                    read_rate = (disk_io.read_bytes - self._last_disk_io.read_bytes) / time_delta
                    write_rate = (disk_io.write_bytes - self._last_disk_io.write_bytes) / time_delta
                    metrics['io_read_mbps'] = read_rate / 1e6
                    metrics['io_write_mbps'] = write_rate / 1e6
                
                self._last_disk_io = disk_io
                self._last_io_time = time.time()
            
            return metrics
            
        except Exception as e:
            logging.error(f"Error getting resource metrics: {e}")
            return {}
    
    def should_degrade(self) -> bool:
        """Check if system should degrade based on resources."""
        if not self.current_metrics:
            return False
        
        for metric, threshold in self.thresholds.items():
            if metric in self.current_metrics:
                if self.current_metrics[metric] > threshold:
                    return True
        
        return False
    
    def get_degradation_level(self) -> float:
        """
        Get degradation level (0.0 = no degradation, 1.0 = maximum).
        
        Returns:
            Degradation level between 0 and 1
        """
        if not self.current_metrics:
            return 0.0
        
        max_excess = 0.0
        
        for metric, threshold in self.thresholds.items():
            if metric in self.current_metrics:
                value = self.current_metrics[metric]
                if value > threshold:
                    # Calculate how much over threshold
                    excess = (value - threshold) / threshold
                    max_excess = max(max_excess, excess)
        
        return min(max_excess, 1.0)


class GracefulDegradationSystem:
    """
    Advanced graceful degradation and fallback system.
    
    Features:
    - Multi-level fallback hierarchy
    - Circuit breaker pattern
    - Retry with backoff
    - Resource-aware degradation
    - Health monitoring
    - Predictive failure detection
    - Self-healing
    """
    
    def __init__(self, algorithms: Dict[str, BaseCompressionAlgorithm]):
        """
        Initialize degradation system.
        
        Args:
            algorithms: Dictionary of available algorithms
        """
        self.algorithms = algorithms
        self.primary_algorithm = list(algorithms.keys())[0] if algorithms else None
        
        # Health tracking
        self.health_status: Dict[str, AlgorithmHealth] = {}
        for name in algorithms:
            self.health_status[name] = AlgorithmHealth(name)
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        for name in algorithms:
            self.circuit_breakers[name] = CircuitBreaker(name)
        
        # Retry policies
        self.retry_policy = RetryPolicy()
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.start_monitoring()
        
        # Fallback hierarchy
        self.fallback_chain = self._build_fallback_chain()
        
        # Performance cache
        self.performance_cache = {}
        
        # Logging
        self.logger = logging.getLogger('degradation')
        
    def _build_fallback_chain(self) -> List[str]:
        """
        Build fallback chain based on algorithm characteristics.
        
        Order from most complex to simplest.
        """
        # Default ordering (can be customized)
        chain = []
        
        # Add algorithms in order of complexity
        if 'quantum_biological' in self.algorithms:
            chain.append('quantum_biological')
        if 'gzip_metarecursive' in self.algorithms:
            chain.append('gzip_metarecursive')
        if 'gzip_strategy' in self.algorithms:
            chain.append('gzip_strategy')
        if 'gzip_basic' in self.algorithms:
            chain.append('gzip_basic')
        
        # Add any remaining algorithms
        for name in self.algorithms:
            if name not in chain:
                chain.append(name)
        
        return chain
    
    def compress_with_fallback(self, data: bytes, **params) -> Tuple[bytes, Any]:
        """
        Compress with automatic fallback on failure.
        
        Args:
            data: Data to compress
            **params: Compression parameters
            
        Returns:
            Tuple of (compressed_data, metadata)
        """
        errors = []
        
        # Check resource availability
        if self.resource_monitor.should_degrade():
            self.logger.warning("System under resource pressure, using degraded mode")
            # Skip to simpler algorithms
            fallback_chain = self.fallback_chain[-2:] if len(self.fallback_chain) > 2 else self.fallback_chain
        else:
            fallback_chain = self.fallback_chain
        
        # Try each algorithm in fallback chain
        for algo_name in fallback_chain:
            # Check circuit breaker
            if not self.circuit_breakers[algo_name].can_execute():
                self.logger.info(f"Circuit breaker open for {algo_name}, skipping")
                continue
            
            # Try compression with retry
            try:
                result = self._compress_with_retry(
                    algo_name, data, **params
                )
                
                if result:
                    # Success - update health
                    self.health_status[algo_name].success_count += 1
                    self.health_status[algo_name].total_requests += 1
                    self.health_status[algo_name].last_success_time = datetime.now()
                    self.health_status[algo_name].update_status()
                    
                    # Record success in circuit breaker
                    self.circuit_breakers[algo_name].record_success()
                    
                    return result
                    
            except Exception as e:
                # Failure - update health
                self.health_status[algo_name].failure_count += 1
                self.health_status[algo_name].total_requests += 1
                self.health_status[algo_name].last_failure_time = datetime.now()
                self.health_status[algo_name].error_messages.append(str(e))
                self.health_status[algo_name].update_status()
                
                # Record failure in circuit breaker
                self.circuit_breakers[algo_name].record_failure()
                
                errors.append({
                    'algorithm': algo_name,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
                
                self.logger.error(f"Algorithm {algo_name} failed: {e}")
        
        # All algorithms failed - last resort fallback
        self.logger.critical("All algorithms failed, using emergency fallback")
        return self._emergency_fallback(data, errors)
    
    def _compress_with_retry(self, algo_name: str, data: bytes, **params) -> Optional[Tuple[bytes, Any]]:
        """
        Compress with retry logic.
        
        Args:
            algo_name: Algorithm name
            data: Data to compress
            **params: Compression parameters
            
        Returns:
            Compression result or None on failure
        """
        algorithm = self.algorithms.get(algo_name)
        if not algorithm:
            return None
        
        last_exception = None
        
        for attempt in range(self.retry_policy.max_attempts):
            try:
                # Set timeout based on data size
                timeout = max(10, len(data) / 1e6 * 5)  # 5 seconds per MB
                
                # Execute with timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(algorithm.compress, data, **params)
                    result = future.result(timeout=timeout)
                    
                    return result
                    
            except TimeoutError:
                last_exception = TimeoutError(f"Compression timeout after {timeout}s")
                self.logger.warning(f"Attempt {attempt + 1} timed out for {algo_name}")
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Attempt {attempt + 1} failed for {algo_name}: {e}")
            
            # Wait before retry (except for last attempt)
            if attempt < self.retry_policy.max_attempts - 1:
                delay = self.retry_policy.get_delay(attempt)
                time.sleep(delay)
        
        # All retries failed
        if last_exception:
            raise last_exception
        
        return None
    
    def _emergency_fallback(self, data: bytes, errors: List[Dict]) -> Tuple[bytes, Dict]:
        """
        Emergency fallback when all algorithms fail.
        
        Uses simplest possible compression or returns uncompressed.
        
        Args:
            data: Data to compress
            errors: List of errors from failed attempts
            
        Returns:
            Tuple of (data, metadata)
        """
        import zlib
        
        try:
            # Try basic zlib compression
            compressed = zlib.compress(data, level=1)
            
            metadata = {
                'algorithm': 'emergency_zlib',
                'compression_ratio': len(data) / len(compressed) if compressed else 1.0,
                'errors': errors,
                'emergency_fallback': True
            }
            
            return compressed, metadata
            
        except:
            # Return uncompressed as last resort
            self.logger.critical("Emergency compression failed, returning uncompressed")
            
            metadata = {
                'algorithm': 'uncompressed',
                'compression_ratio': 1.0,
                'errors': errors,
                'emergency_fallback': True,
                'uncompressed': True
            }
            
            return data, metadata
    
    def predict_failure_probability(self, algo_name: str) -> float:
        """
        Predict probability of algorithm failure.
        
        Uses historical data and current system state.
        
        Args:
            algo_name: Algorithm name
            
        Returns:
            Failure probability between 0 and 1
        """
        if algo_name not in self.health_status:
            return 0.5  # Unknown algorithm
        
        health = self.health_status[algo_name]
        
        # Base probability from historical failure rate
        base_prob = health.failure_rate
        
        # Adjust based on recent failures
        if health.last_failure_time:
            time_since_failure = (datetime.now() - health.last_failure_time).total_seconds()
            # Exponential decay of failure impact
            recent_failure_factor = np.exp(-time_since_failure / 3600)  # 1 hour decay
            base_prob = base_prob * 0.7 + recent_failure_factor * 0.3
        
        # Adjust based on resource availability
        resource_factor = self.resource_monitor.get_degradation_level()
        base_prob = base_prob * 0.8 + resource_factor * 0.2
        
        # Adjust based on circuit breaker state
        breaker = self.circuit_breakers[algo_name]
        if breaker.state == CircuitState.OPEN:
            base_prob = 0.95
        elif breaker.state == CircuitState.HALF_OPEN:
            base_prob = base_prob * 0.5 + 0.25
        
        return min(max(base_prob, 0.0), 1.0)
    
    def select_best_algorithm(self, data: bytes) -> str:
        """
        Select best algorithm based on current conditions.
        
        Considers:
        - Algorithm health
        - Resource availability
        - Data characteristics
        - Historical performance
        
        Args:
            data: Data to compress
            
        Returns:
            Best algorithm name
        """
        scores = {}
        
        for algo_name in self.algorithms:
            # Skip if circuit breaker is open
            if self.circuit_breakers[algo_name].state == CircuitState.OPEN:
                continue
            
            # Calculate score
            health = self.health_status[algo_name]
            
            # Success rate component
            success_score = health.success_rate
            
            # Performance component (inverse of average response time)
            perf_score = 1.0 / (1.0 + health.avg_response_time)
            
            # Resource availability component
            resource_score = 1.0 - self.resource_monitor.get_degradation_level()
            
            # Failure prediction component
            failure_prob = self.predict_failure_probability(algo_name)
            reliability_score = 1.0 - failure_prob
            
            # Combined score
            score = (
                success_score * 0.3 +
                perf_score * 0.2 +
                resource_score * 0.2 +
                reliability_score * 0.3
            )
            
            scores[algo_name] = score
        
        if not scores:
            return self.primary_algorithm
        
        # Return algorithm with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def heal_algorithm(self, algo_name: str):
        """
        Attempt to heal a failing algorithm.
        
        Recovery strategies:
        - Clear error state
        - Reset circuit breaker
        - Garbage collection
        - Resource cleanup
        
        Args:
            algo_name: Algorithm to heal
        """
        self.logger.info(f"Attempting to heal algorithm {algo_name}")
        
        # Reset health metrics
        health = self.health_status[algo_name]
        health.error_messages.clear()
        health.failure_count = max(0, health.failure_count - 5)
        health.update_status()
        
        # Reset circuit breaker if in half-open state
        breaker = self.circuit_breakers[algo_name]
        if breaker.state == CircuitState.HALF_OPEN:
            if health.success_rate > 0.8:
                breaker.close()
        
        # Force garbage collection
        gc.collect()
        
        # Clear performance cache
        self.performance_cache.pop(algo_name, None)
        
        self.logger.info(f"Healing complete for {algo_name}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health report.
        
        Returns:
            System health dictionary
        """
        healthy_count = sum(
            1 for h in self.health_status.values()
            if h.status == HealthStatus.HEALTHY
        )
        
        total_count = len(self.health_status)
        
        return {
            'overall_status': self._calculate_overall_status(),
            'healthy_algorithms': healthy_count,
            'total_algorithms': total_count,
            'health_percentage': (healthy_count / total_count * 100) if total_count else 0,
            'resource_usage': self.resource_monitor.current_metrics,
            'algorithm_health': {
                name: {
                    'status': health.status.value,
                    'success_rate': health.success_rate,
                    'avg_response_time': health.avg_response_time,
                    'circuit_breaker': self.circuit_breakers[name].state.value
                }
                for name, health in self.health_status.items()
            },
            'degradation_level': self.resource_monitor.get_degradation_level(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_overall_status(self) -> str:
        """Calculate overall system status."""
        statuses = [h.status for h in self.health_status.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return "healthy"
        elif any(s == HealthStatus.CRITICAL for s in statuses):
            return "critical"
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return "unhealthy"
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return "degraded"
        else:
            return "healthy"
    
    def auto_recover(self):
        """
        Automatic recovery process.
        
        Runs periodically to heal failing algorithms and
        reset circuit breakers when appropriate.
        """
        for algo_name, health in self.health_status.items():
            # Check if algorithm needs healing
            if health.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
                # Check if enough time has passed since last failure
                if health.last_failure_time:
                    time_since_failure = (datetime.now() - health.last_failure_time).total_seconds()
                    
                    if time_since_failure > 300:  # 5 minutes
                        self.heal_algorithm(algo_name)
            
            # Check circuit breakers
            breaker = self.circuit_breakers[algo_name]
            if breaker.state == CircuitState.OPEN:
                if breaker.last_failure_time:
                    elapsed = (datetime.now() - breaker.last_failure_time).total_seconds()
                    if elapsed >= breaker.recovery_timeout:
                        breaker.half_open()
    
    def shutdown(self):
        """Shutdown degradation system."""
        self.resource_monitor.stop_monitoring()
        self.logger.info("Graceful degradation system shutdown")


# Example usage and integration
def create_resilient_compression_system(algorithms: Dict[str, BaseCompressionAlgorithm]) -> GracefulDegradationSystem:
    """
    Create a resilient compression system with graceful degradation.
    
    Args:
        algorithms: Dictionary of compression algorithms
        
    Returns:
        Configured degradation system
    """
    system = GracefulDegradationSystem(algorithms)
    
    # Start auto-recovery thread
    def recovery_loop():
        while True:
            time.sleep(60)  # Check every minute
            system.auto_recover()
    
    recovery_thread = threading.Thread(target=recovery_loop)
    recovery_thread.daemon = True
    recovery_thread.start()
    
    return system