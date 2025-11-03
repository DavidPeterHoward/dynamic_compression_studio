"""
Comprehensive tests for monitoring systems.

This module tests all monitoring components:
- Logging system
- Metrics collection
- Health monitoring
- Alerting system
- Distributed tracing
"""

import pytest
import asyncio
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.monitoring.logging import (
    setup_logging, get_logger, generate_correlation_id,
    get_correlation_id, set_correlation_id, LoggerMixin,
    log_function_call, log_performance, log_security_event,
    log_business_event
)

from app.monitoring.metrics import (
    setup_metrics, get_metrics_collector, MetricsCollector,
    track_api_request, track_compression_request, track_database_query
)

from app.monitoring.health import (
    setup_health_monitoring, get_health_monitor, HealthMonitor,
    HealthStatus, ComponentHealth
)

from app.monitoring.alerts import (
    setup_alerting, get_alert_manager, AlertManager,
    AlertSeverity, AlertStatus, Alert, AlertRule
)

from app.monitoring.tracing import (
    setup_tracing, get_tracer, Tracer, Span, Trace, TraceContext,
    SpanStatus, trace_function, trace_span, trace_operation
)


class TestLoggingSystem:
    """Test the logging system."""
    
    def test_setup_logging(self):
        """Test logging system setup."""
        setup_logging(log_level="DEBUG", log_format="json")
        logger = get_logger("test")
        assert logger is not None
    
    def test_correlation_id_generation(self):
        """Test correlation ID generation and management."""
        # Generate correlation ID
        corr_id = generate_correlation_id()
        assert corr_id is not None
        assert len(corr_id) > 0
        
        # Set and get correlation ID
        set_correlation_id(corr_id)
        retrieved_id = get_correlation_id()
        assert retrieved_id == corr_id
    
    def test_logger_mixin(self):
        """Test LoggerMixin class."""
        class TestClass(LoggerMixin):
            def test_method(self):
                self.logger.info("Test message")
        
        obj = TestClass()
        assert obj.logger is not None
        obj.test_method()  # Should not raise exception
    
    def test_log_function_call_decorator(self):
        """Test log_function_call decorator."""
        @log_function_call
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_log_performance(self):
        """Test performance logging."""
        log_performance("test_operation", 1.5, additional_info="test")
        # Should not raise exception
    
    def test_log_security_event(self):
        """Test security event logging."""
        log_security_event(
            event_type="login_attempt",
            severity="medium",
            user_id="test_user",
            ip_address="127.0.0.1"
        )
        # Should not raise exception
    
    def test_log_business_event(self):
        """Test business event logging."""
        log_business_event(
            event_type="compression_request",
            user_id="test_user",
            data={"algorithm": "gzip", "size": 1024}
        )
        # Should not raise exception


class TestMetricsSystem:
    """Test the metrics collection system."""
    
    def test_setup_metrics(self):
        """Test metrics system setup."""
        collector = setup_metrics(enable_background_collection=False)
        assert collector is not None
        assert isinstance(collector, MetricsCollector)
    
    def test_metrics_collector_initialization(self):
        """Test metrics collector initialization."""
        collector = MetricsCollector()
        assert collector.registry is not None
        assert collector.api_requests_total is not None
        assert collector.compression_requests_total is not None
    
    def test_record_api_request(self):
        """Test API request recording."""
        collector = get_metrics_collector()
        collector.record_api_request("GET", "/test", 200, 0.1)
        
        # Check that metrics were recorded
        metrics = collector.get_metrics()
        assert "api_requests_total" in metrics
    
    def test_record_compression_request(self):
        """Test compression request recording."""
        collector = get_metrics_collector()
        collector.record_compression_request(
            algorithm="gzip",
            status="success",
            user_id="test_user",
            compression_ratio=2.5,
            duration=0.5,
            throughput=10.0
        )
        
        # Check that metrics were recorded
        metrics = collector.get_metrics()
        assert "compression_requests_total" in metrics
    
    def test_record_database_query(self):
        """Test database query recording."""
        collector = get_metrics_collector()
        collector.record_database_query("SELECT", 0.05)
        
        # Check that metrics were recorded
        metrics = collector.get_metrics()
        assert "database_query_duration_seconds" in metrics
    
    def test_metrics_decorators(self):
        """Test metrics decorators."""
        @track_api_request("GET", "/test")
        def test_api_function():
            return "success"
        
        @track_compression_request("gzip", "test_user")
        def test_compression_function():
            return "compressed"
        
        @track_database_query("SELECT")
        def test_db_function():
            return "data"
        
        # Test function calls
        result1 = test_api_function()
        result2 = test_compression_function()
        result3 = test_db_function()
        
        assert result1 == "success"
        assert result2 == "compressed"
        assert result3 == "data"
    
    def test_get_metrics_summary(self):
        """Test metrics summary generation."""
        collector = get_metrics_collector()
        summary = collector.get_metrics_summary()
        
        assert "timestamp" in summary
        assert "total_api_requests" in summary
        assert "total_compression_requests" in summary


class TestHealthMonitoring:
    """Test the health monitoring system."""
    
    def test_setup_health_monitoring(self):
        """Test health monitoring setup."""
        monitor = setup_health_monitoring(enable_background_monitoring=False)
        assert monitor is not None
        assert isinstance(monitor, HealthMonitor)
    
    def test_health_monitor_initialization(self):
        """Test health monitor initialization."""
        monitor = HealthMonitor()
        assert len(monitor.health_checks) > 0
        assert "system" in monitor.health_checks
        assert "database" in monitor.health_checks
    
    def test_component_health(self):
        """Test ComponentHealth class."""
        health = ComponentHealth(
            name="test_component",
            status=HealthStatus.HEALTHY,
            message="Component is healthy",
            details={"cpu_usage": 50}
        )
        
        health_dict = health.to_dict()
        assert health_dict["name"] == "test_component"
        assert health_dict["status"] == "healthy"
        assert health_dict["message"] == "Component is healthy"
    
    @pytest.mark.asyncio
    async def test_check_component_health(self):
        """Test component health checking."""
        monitor = get_health_monitor()
        
        # Test system health check
        health = await monitor.check_component_health("system")
        assert health is not None
        assert health.name == "system"
        assert health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
    
    @pytest.mark.asyncio
    async def test_check_all_health(self):
        """Test checking all component health."""
        monitor = get_health_monitor()
        components = await monitor.check_all_health()
        
        assert isinstance(components, dict)
        assert len(components) > 0
    
    def test_get_overall_health(self):
        """Test overall health calculation."""
        monitor = get_health_monitor()
        overall_health = monitor.get_overall_health()
        assert overall_health in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
    
    def test_get_health_summary(self):
        """Test health summary generation."""
        monitor = get_health_monitor()
        summary = monitor.get_health_summary()
        
        assert "status" in summary
        assert "timestamp" in summary
        assert "components" in summary
        assert "summary" in summary


class TestAlertingSystem:
    """Test the alerting system."""
    
    def test_setup_alerting(self):
        """Test alerting system setup."""
        manager = setup_alerting(enable_background_monitoring=False)
        assert manager is not None
        assert isinstance(manager, AlertManager)
    
    def test_alert_manager_initialization(self):
        """Test alert manager initialization."""
        manager = AlertManager()
        assert len(manager.alert_rules) > 0
        assert "high_error_rate" in manager.alert_rules
        assert "high_cpu_usage" in manager.alert_rules
    
    def test_alert_creation(self):
        """Test alert creation."""
        alert = Alert(
            rule_name="test_rule",
            severity=AlertSeverity.WARNING,
            message="Test alert message",
            details={"test_key": "test_value"}
        )
        
        assert alert.id is not None
        assert alert.rule_name == "test_rule"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.status == AlertStatus.ACTIVE
    
    def test_alert_to_dict(self):
        """Test alert serialization."""
        alert = Alert(
            rule_name="test_rule",
            severity=AlertSeverity.CRITICAL,
            message="Test alert"
        )
        
        alert_dict = alert.to_dict()
        assert "id" in alert_dict
        assert "rule_name" in alert_dict
        assert "severity" in alert_dict
        assert "status" in alert_dict
    
    def test_alert_acknowledgment(self):
        """Test alert acknowledgment."""
        manager = get_alert_manager()
        
        # Create a test alert
        alert = Alert(
            rule_name="test_rule",
            severity=AlertSeverity.WARNING,
            message="Test alert"
        )
        manager.active_alerts[alert.id] = alert
        
        # Acknowledge alert
        manager.acknowledge_alert(alert.id, "test_user")
        
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "test_user"
        assert alert.acknowledged_at is not None
    
    def test_alert_resolution(self):
        """Test alert resolution."""
        manager = get_alert_manager()
        
        # Create a test alert
        alert = Alert(
            rule_name="test_rule",
            severity=AlertSeverity.WARNING,
            message="Test alert"
        )
        manager.active_alerts[alert.id] = alert
        
        # Resolve alert
        manager.resolve_alert(alert.id)
        
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
        assert alert.id not in manager.active_alerts
    
    def test_get_active_alerts(self):
        """Test getting active alerts."""
        manager = get_alert_manager()
        active_alerts = manager.get_active_alerts()
        assert isinstance(active_alerts, list)
    
    def test_get_alert_history(self):
        """Test getting alert history."""
        manager = get_alert_manager()
        history = manager.get_alert_history(limit=10)
        assert isinstance(history, list)


class TestTracingSystem:
    """Test the distributed tracing system."""
    
    def test_setup_tracing(self):
        """Test tracing system setup."""
        tracer = setup_tracing(enable_background_processing=False)
        assert tracer is not None
        assert isinstance(tracer, Tracer)
    
    def test_tracer_initialization(self):
        """Test tracer initialization."""
        tracer = Tracer()
        assert tracer.sampling_rate == 1.0
        assert tracer.max_traces == 1000
    
    def test_span_creation(self):
        """Test span creation and management."""
        span = Span("trace_123", "span_456", "test_operation")
        
        assert span.trace_id == "trace_123"
        assert span.span_id == "span_456"
        assert span.name == "test_operation"
        assert span.status == SpanStatus.UNKNOWN
    
    def test_span_finishing(self):
        """Test span finishing."""
        span = Span("trace_123", "span_456", "test_operation")
        span.finish(SpanStatus.OK)
        
        assert span.end_time is not None
        assert span.duration is not None
        assert span.status == SpanStatus.OK
    
    def test_span_tags_and_events(self):
        """Test span tags and events."""
        span = Span("trace_123", "span_456", "test_operation")
        
        # Add tags
        span.add_tag("test_key", "test_value")
        span.add_tag("numeric_key", 42)
        
        # Add events
        span.add_event("test_event", {"event_data": "value"})
        
        # Add logs
        span.add_log("Test log message", "info", {"log_data": "value"})
        
        assert span.tags["test_key"] == "test_value"
        assert span.tags["numeric_key"] == 42
        assert len(span.events) == 1
        assert len(span.logs) == 1
    
    def test_trace_creation(self):
        """Test trace creation and management."""
        trace = Trace("trace_123")
        span1 = Span("trace_123", "span_1", "operation_1")
        span2 = Span("trace_123", "span_2", "operation_2")
        
        trace.add_span(span1)
        trace.add_span(span2)
        
        assert len(trace.spans) == 2
        assert trace.trace_id == "trace_123"
    
    def test_trace_duration(self):
        """Test trace duration calculation."""
        trace = Trace("trace_123")
        span = Span("trace_123", "span_1", "operation_1")
        
        # Simulate some time passing
        time.sleep(0.1)
        span.finish()
        
        trace.add_span(span)
        duration = trace.get_duration()
        
        assert duration is not None
        assert duration > 0
    
    def test_trace_context(self):
        """Test trace context management."""
        context = TraceContext()
        context.trace_id = "trace_123"
        context.span_id = "span_456"
        context.sampled = True
        context.baggage = {"key": "value"}
        
        context_dict = context.to_dict()
        assert context_dict["trace_id"] == "trace_123"
        assert context_dict["span_id"] == "span_456"
        assert context_dict["sampled"] is True
        assert context_dict["baggage"]["key"] == "value"
        
        # Test from_dict
        new_context = TraceContext.from_dict(context_dict)
        assert new_context.trace_id == "trace_123"
        assert new_context.span_id == "span_456"
    
    def test_tracer_span_management(self):
        """Test tracer span management."""
        tracer = get_tracer()
        
        # Start a trace
        span = tracer.start_trace("test_trace")
        assert span is not None
        assert span.trace_id is not None
        assert span.span_id is not None
        
        # Start a child span
        child_span = tracer.start_span("child_operation", span)
        assert child_span.parent_id == span.span_id
        
        # Finish spans
        tracer.finish_span(child_span)
        tracer.finish_span(span)
        
        # Finish trace
        tracer.finish_trace(span.trace_id)
    
    def test_trace_context_injection_extraction(self):
        """Test trace context injection and extraction."""
        tracer = get_tracer()
        
        # Start a trace
        span = tracer.start_trace("test_trace")
        
        # Inject context into headers
        headers = {}
        tracer.inject_context(headers)
        
        assert "X-Trace-ID" in headers
        assert "X-Span-ID" in headers
        assert headers["X-Trace-ID"] == span.trace_id
        
        # Extract context from headers
        extracted_context = tracer.extract_context(headers)
        assert extracted_context is not None
        assert extracted_context.trace_id == span.trace_id
        
        tracer.finish_span(span)
        tracer.finish_trace(span.trace_id)
    
    def test_tracing_decorators(self):
        """Test tracing decorators."""
        @trace_function("test_function")
        def test_function():
            return "success"
        
        @trace_function("test_async_function")
        async def test_async_function():
            return "async_success"
        
        # Test sync function
        result = test_function()
        assert result == "success"
        
        # Test async function
        result = asyncio.run(test_async_function())
        assert result == "async_success"
    
    def test_trace_context_managers(self):
        """Test trace context managers."""
        tracer = get_tracer()
        
        with trace_span("test_span") as span:
            assert span is not None
            span.add_tag("test_tag", "test_value")
        
        with trace_operation("test_operation") as span:
            assert span is not None
            span.add_event("test_event")


class TestMonitoringIntegration:
    """Test integration between monitoring systems."""
    
    def test_monitoring_systems_initialization(self):
        """Test that all monitoring systems can be initialized together."""
        # Setup all systems
        logger = setup_logging(log_level="INFO", log_format="json")
        metrics = setup_metrics(enable_background_collection=False)
        health = setup_health_monitoring(enable_background_monitoring=False)
        alerts = setup_alerting(enable_background_monitoring=False)
        tracer = setup_tracing(enable_background_processing=False)
        
        assert logger is not None
        assert metrics is not None
        assert health is not None
        assert alerts is not None
        assert tracer is not None
    
    def test_correlation_id_propagation(self):
        """Test correlation ID propagation across systems."""
        # Generate correlation ID
        corr_id = generate_correlation_id()
        set_correlation_id(corr_id)
        
        # Verify it's available in logging
        logger = get_logger("test")
        logger.info("Test message")
        
        # Verify it's available in tracing
        tracer = get_tracer()
        context = tracer.get_current_context()
        # Note: This might be None if no trace is active
        
        # Verify it's available in metrics
        metrics = get_metrics_collector()
        # Metrics should be able to access correlation ID through logging context
    
    def test_metrics_and_health_integration(self):
        """Test integration between metrics and health monitoring."""
        metrics = get_metrics_collector()
        health = get_health_monitor()
        
        # Record some metrics
        metrics.record_api_request("GET", "/test", 200, 0.1)
        
        # Check health (should not be affected by metrics recording)
        overall_health = health.get_overall_health()
        assert overall_health in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
    
    def test_health_and_alerting_integration(self):
        """Test integration between health monitoring and alerting."""
        health = get_health_monitor()
        alerts = get_alert_manager()
        
        # Check health
        overall_health = health.get_overall_health()
        
        # Alerts should be able to check health status
        # This is tested in the alert manager's health check methods
    
    def test_tracing_and_metrics_integration(self):
        """Test integration between tracing and metrics."""
        tracer = get_tracer()
        metrics = get_metrics_collector()
        
        # Start a trace
        span = tracer.start_trace("test_trace")
        
        # Record metrics
        metrics.record_api_request("GET", "/test", 200, 0.1)
        
        # Add metrics info to span
        span.add_tag("metrics.recorded", True)
        
        # Finish trace
        tracer.finish_span(span)
        tracer.finish_trace(span.trace_id)
        
        # Both systems should work together without conflicts


if __name__ == "__main__":
    pytest.main([__file__])
