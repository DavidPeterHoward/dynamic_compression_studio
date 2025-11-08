"""
Comprehensive metrics collection system for Dynamic Compression Algorithms.

This module provides:
- Prometheus metrics collection
- Business metrics tracking
- Performance metrics
- Custom metrics
- Metrics aggregation and reporting
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from collections import defaultdict, deque
import asyncio
import json

from prometheus_client import (
    Counter, Gauge, Histogram, Summary, Info, Enum,
    generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry,
    multiprocess, start_http_server
)
from prometheus_client.metrics_core import Metric
import psutil

from .logging import get_logger, LoggerMixin


class MetricsCollector(LoggerMixin):
    """Comprehensive metrics collector for the application."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.logger.info("Initializing metrics collector")
        
        # Create custom registry
        self.registry = CollectorRegistry()
        
        # Initialize metrics
        self._init_prometheus_metrics()
        self._init_business_metrics()
        self._init_performance_metrics()
        self._init_custom_metrics()
        
        # Metrics storage
        self.custom_metrics = defaultdict(dict)
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Background tasks
        self._running = False
        self._background_thread = None
        
        self.logger.info("Metrics collector initialized successfully")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # API Metrics
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.api_errors_total = Counter(
            'api_errors_total',
            'Total API errors',
            ['method', 'endpoint', 'error_type'],
            registry=self.registry
        )
        
        # Compression Metrics
        self.compression_requests_total = Counter(
            'compression_requests_total',
            'Total compression requests',
            ['algorithm', 'status', 'user_id'],
            registry=self.registry
        )
        
        self.compression_ratio = Histogram(
            'compression_ratio',
            'Compression ratio achieved',
            ['algorithm', 'content_type'],
            buckets=[1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0],
            registry=self.registry
        )
        
        self.compression_throughput = Gauge(
            'compression_throughput_mbps',
            'Compression throughput in MB/s',
            ['algorithm'],
            registry=self.registry
        )
        
        self.compression_duration = Histogram(
            'compression_duration_seconds',
            'Compression operation duration',
            ['algorithm', 'content_type'],
            registry=self.registry
        )
        
        # System Metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_bytes',
            'System disk usage in bytes',
            registry=self.registry
        )
        
        # Database Metrics
        self.database_connections = Gauge(
            'database_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.database_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration',
            ['operation'],
            registry=self.registry
        )
        
        # Cache Metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # Application Info
        self.app_info = Info(
            'app_info',
            'Application information',
            registry=self.registry
        )
        self.app_info.info({
            'name': 'dynamic-compression-algorithms',
            'version': '1.0.0',
            'environment': 'development'
        })
    
    def _init_business_metrics(self):
        """Initialize business metrics."""
        # User Metrics
        self.active_users = Gauge(
            'active_users_total',
            'Total active users',
            registry=self.registry
        )
        
        self.user_sessions = Counter(
            'user_sessions_total',
            'Total user sessions',
            ['user_type'],
            registry=self.registry
        )
        
        # File Processing Metrics
        self.files_processed_total = Counter(
            'files_processed_total',
            'Total files processed',
            ['file_type', 'status'],
            registry=self.registry
        )
        
        self.file_processing_duration = Histogram(
            'file_processing_duration_seconds',
            'File processing duration',
            ['file_type', 'size_category'],
            registry=self.registry
        )
        
        # Algorithm Performance Metrics
        self.algorithm_performance = Gauge(
            'algorithm_performance_score',
            'Algorithm performance score',
            ['algorithm', 'content_type'],
            registry=self.registry
        )
        
        # Cost Metrics
        self.processing_cost = Counter(
            'processing_cost_total',
            'Total processing cost',
            ['cost_type', 'algorithm'],
            registry=self.registry
        )
    
    def _init_performance_metrics(self):
        """Initialize performance metrics."""
        # Response Time Metrics
        self.response_time_p95 = Gauge(
            'response_time_p95_seconds',
            '95th percentile response time',
            ['endpoint'],
            registry=self.registry
        )
        
        self.response_time_p99 = Gauge(
            'response_time_p99_seconds',
            '99th percentile response time',
            ['endpoint'],
            registry=self.registry
        )
        
        # Throughput Metrics
        self.requests_per_second = Gauge(
            'requests_per_second',
            'Requests per second',
            ['endpoint'],
            registry=self.registry
        )
        
        # Error Rate Metrics
        self.error_rate = Gauge(
            'error_rate_percent',
            'Error rate percentage',
            ['endpoint'],
            registry=self.registry
        )
        
        # Resource Utilization
        self.memory_usage_percent = Gauge(
            'memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.cpu_usage_percent = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
    
    def _init_custom_metrics(self):
        """Initialize custom metrics."""
        # Custom counters
        self.custom_counters = defaultdict(lambda: Counter(
            'custom_counter',
            'Custom counter metric',
            ['name', 'label'],
            registry=self.registry
        ))
        
        # Custom gauges
        self.custom_gauges = defaultdict(lambda: Gauge(
            'custom_gauge',
            'Custom gauge metric',
            ['name', 'label'],
            registry=self.registry
        ))
        
        # Custom histograms
        self.custom_histograms = defaultdict(lambda: Histogram(
            'custom_histogram',
            'Custom histogram metric',
            ['name', 'label'],
            registry=self.registry
        ))
    
    def start_background_collection(self):
        """Start background metrics collection."""
        if self._running:
            return
        
        self._running = True
        self._background_thread = threading.Thread(
            target=self._background_collection_loop,
            daemon=True
        )
        self._background_thread.start()
        self.logger.info("Background metrics collection started")
    
    def stop_background_collection(self):
        """Stop background metrics collection."""
        self._running = False
        if self._background_thread:
            self._background_thread.join()
        self.logger.info("Background metrics collection stopped")
    
    def _background_collection_loop(self):
        """Background loop for collecting system metrics."""
        while self._running:
            try:
                self._collect_system_metrics()
                self._collect_performance_metrics()
                time.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in background metrics collection: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self):
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            self.cpu_usage_percent.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            self.memory_usage_percent.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_disk_usage.set(disk.used)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_performance_metrics(self):
        """Collect performance metrics."""
        # This would typically involve analyzing recent request data
        # For now, we'll just log that we're collecting
        self.logger.debug("Collecting performance metrics")
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record an API request."""
        self.api_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        
        if status_code >= 400:
            self.api_errors_total.labels(method=method, endpoint=endpoint, error_type="http_error").inc()
    
    def record_compression_request(
        self,
        algorithm: str,
        status: str,
        user_id: str,
        compression_ratio: float,
        duration: float,
        throughput: float,
        content_type: str = "unknown"
    ):
        """Record a compression request."""
        self.compression_requests_total.labels(
            algorithm=algorithm,
            status=status,
            user_id=user_id
        ).inc()
        
        self.compression_ratio.labels(
            algorithm=algorithm,
            content_type=content_type
        ).observe(compression_ratio)
        
        self.compression_duration.labels(
            algorithm=algorithm,
            content_type=content_type
        ).observe(duration)
        
        self.compression_throughput.labels(algorithm=algorithm).set(throughput)
    
    def record_database_query(self, operation: str, duration: float):
        """Record a database query."""
        self.database_query_duration.labels(operation=operation).observe(duration)
    
    def record_cache_access(self, cache_type: str, hit: bool):
        """Record a cache access."""
        if hit:
            self.cache_hits.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses.labels(cache_type=cache_type).inc()
    
    def record_file_processing(
        self,
        file_type: str,
        status: str,
        duration: float,
        size_category: str = "unknown"
    ):
        """Record file processing."""
        self.files_processed_total.labels(file_type=file_type, status=status).inc()
        self.file_processing_duration.labels(
            file_type=file_type,
            size_category=size_category
        ).observe(duration)
    
    def set_algorithm_performance(self, algorithm: str, content_type: str, score: float):
        """Set algorithm performance score."""
        self.algorithm_performance.labels(
            algorithm=algorithm,
            content_type=content_type
        ).set(score)
    
    def record_processing_cost(self, cost_type: str, algorithm: str, cost: float):
        """Record processing cost."""
        self.processing_cost.labels(cost_type=cost_type, algorithm=algorithm).inc(cost)
    
    def set_active_users(self, count: int):
        """Set active users count."""
        self.active_users.set(count)
    
    def record_user_session(self, user_type: str):
        """Record a user session."""
        self.user_sessions.labels(user_type=user_type).inc()
    
    def set_response_time_percentiles(self, endpoint: str, p95: float, p99: float):
        """Set response time percentiles."""
        self.response_time_p95.labels(endpoint=endpoint).set(p95)
        self.response_time_p99.labels(endpoint=endpoint).set(p99)
    
    def set_requests_per_second(self, endpoint: str, rps: float):
        """Set requests per second."""
        self.requests_per_second.labels(endpoint=endpoint).set(rps)
    
    def set_error_rate(self, endpoint: str, rate: float):
        """Set error rate."""
        self.error_rate.labels(endpoint=endpoint).set(rate)
    
    def increment_custom_counter(self, name: str, label: str, value: float = 1.0):
        """Increment a custom counter."""
        self.custom_counters[name].labels(name=name, label=label).inc(value)
    
    def set_custom_gauge(self, name: str, label: str, value: float):
        """Set a custom gauge."""
        self.custom_gauges[name].labels(name=name, label=label).set(value)
    
    def observe_custom_histogram(self, name: str, label: str, value: float):
        """Observe a custom histogram."""
        self.custom_histograms[name].labels(name=name, label=label).observe(value)
    
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        return generate_latest(self.registry)
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as a dictionary for JSON response."""
        metrics_data = {}
        
        # Collect all metrics from registry
        for metric in self.registry.collect():
            metric_name = metric.name
            metric_type = metric.type
            
            if metric_type == 'counter':
                metrics_data[metric_name] = {
                    'type': 'counter',
                    'samples': [
                        {
                            'labels': dict(sample.labels),
                            'value': sample.value
                        }
                        for sample in metric.samples
                    ]
                }
            elif metric_type == 'gauge':
                metrics_data[metric_name] = {
                    'type': 'gauge',
                    'samples': [
                        {
                            'labels': dict(sample.labels),
                            'value': sample.value
                        }
                        for sample in metric.samples
                    ]
                }
            elif metric_type == 'histogram':
                metrics_data[metric_name] = {
                    'type': 'histogram',
                    'samples': [
                        {
                            'labels': dict(sample.labels),
                            'value': sample.value,
                            'bucket': getattr(sample, 'bucket', None)
                        }
                        for sample in metric.samples
                    ]
                }
        
        return metrics_data
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of key metrics."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_api_requests': self._get_counter_value(self.api_requests_total),
            'total_compression_requests': self._get_counter_value(self.compression_requests_total),
            'total_errors': self._get_counter_value(self.api_errors_total),
            'system_cpu_usage': self.system_cpu_usage._value.get(),
            'system_memory_usage': self.system_memory_usage._value.get(),
            'active_users': self.active_users._value.get(),
            'files_processed': self._get_counter_value(self.files_processed_total)
        }
    
    def _get_counter_value(self, counter: Counter) -> float:
        """Get the total value of a counter."""
        try:
            return sum(sample.value for sample in counter._metrics.values())
        except:
            return 0.0


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def setup_metrics(
    enable_background_collection: bool = True,
    metrics_port: int = 8000
) -> MetricsCollector:
    """
    Setup the metrics collection system.
    
    Args:
        enable_background_collection: Enable background metrics collection
        metrics_port: Port for metrics HTTP server
        
    Returns:
        Metrics collector instance
    """
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
        
        if enable_background_collection:
            _metrics_collector.start_background_collection()
        
        # Start metrics HTTP server
        try:
            start_http_server(metrics_port, registry=_metrics_collector.registry)
            logger = get_logger("metrics")
            logger.info(f"Metrics server started on port {metrics_port}")
        except Exception as e:
            logger = get_logger("metrics")
            logger.error(f"Failed to start metrics server: {e}")
    
    return _metrics_collector


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    if _metrics_collector is None:
        return setup_metrics()
    return _metrics_collector


# Metrics decorators for easy usage
def track_api_request(method: str, endpoint: str):
    """Decorator to track API requests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status_code = 200
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()
                collector.record_api_request(method, endpoint, status_code, duration)
        return wrapper
    return decorator


def track_compression_request(algorithm: str, user_id: str = "anonymous"):
    """Decorator to track compression requests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()
                # Note: compression_ratio and throughput would need to be calculated
                # from the actual result data
                collector.record_compression_request(
                    algorithm=algorithm,
                    status=status,
                    user_id=user_id,
                    compression_ratio=1.0,  # Default value
                    duration=duration,
                    throughput=0.0  # Default value
                )
        return wrapper
    return decorator


def track_database_query(operation: str):
    """Decorator to track database queries."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()
                collector.record_database_query(operation, duration)
        return wrapper
    return decorator


# Initialize metrics on module import
if _metrics_collector is None:
    setup_metrics()
