"""
Monitoring and observability package for Dynamic Compression Algorithms.

This package provides comprehensive monitoring, logging, metrics collection,
and observability capabilities for the application.
"""

from .logging import setup_logging, get_logger, generate_correlation_id, set_correlation_id
from .metrics import setup_metrics, get_metrics_collector
from .tracing import setup_tracing, get_tracer
from .health import HealthMonitor, setup_health_monitoring, get_health_monitor
from .alerts import AlertManager, setup_alerting, get_alert_manager

__all__ = [
    "setup_logging",
    "get_logger",
    "generate_correlation_id",
    "set_correlation_id",
    "setup_metrics",
    "get_metrics_collector",
    "setup_tracing",
    "get_tracer",
    "setup_health_monitoring",
    "get_health_monitor",
    "setup_alerting",
    "get_alert_manager",
    "HealthMonitor",
    "AlertManager"
]
