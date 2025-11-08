# Advanced Structured Logging Implementation

## Overview

This document details the advanced structured logging implementation that provides comprehensive logging, auditing, and error tracking capabilities for the multi-agent system. These features are not part of the MVP but provide enterprise-grade observability and compliance capabilities.

## Structured Logging Architecture

### Core Components

**File: `backend/app/agents/api/fastapi_app.py` (Advanced Logging Section)**

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
import asyncio
from dataclasses import dataclass, asdict

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

@dataclass
class AuditEvent:
    """Audit event data structure."""
    timestamp: str
    correlation_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    operation: str
    resource_type: str
    resource_id: Optional[str]
    action: str
    status_code: Optional[int]
    duration_ms: Optional[float]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    security_context: Optional[Dict[str, Any]]

class StructuredLogger:
    """Enhanced structured logger with context management."""

    def __init__(self):
        self.logger = structlog.get_logger(__name__)

    @contextmanager
    def operation_context(self, operation: str, correlation_id: str, **context):
        """Context manager for operation logging."""
        start_time = datetime.now()

        with structlog.contextvars.bound_contextvars(
            operation=operation,
            correlation_id=correlation_id,
            **context
        ):
            try:
                yield
                duration = (datetime.now() - start_time).total_seconds() * 1000
                self.logger.info(
                    f"Operation completed: {operation}",
                    duration_ms=duration,
                    status="success"
                )
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                self.logger.error(
                    f"Operation failed: {operation}",
                    error=str(e),
                    duration_ms=duration,
                    status="error"
                )
                raise

    async def log_performance_metric(self, metric_name: str, value: float, **context):
        """Log performance metrics."""
        self.logger.info(
            f"Performance metric: {metric_name}",
            metric_name=metric_name,
            metric_value=value,
            metric_type="performance",
            **context
        )

    async def log_security_event(self, event_type: str, severity: str, **context):
        """Log security-related events."""
        self.logger.warning(
            f"Security event: {event_type}",
            event_type=event_type,
            severity=severity,
            security_event=True,
            **context
        )

    async def log_agent_event(self, agent_id: str, event_type: str, **context):
        """Log agent-specific events."""
        self.logger.info(
            f"Agent event: {event_type}",
            agent_id=agent_id,
            event_type=event_type,
            agent_event=True,
            **context
        )

class AuditLogger:
    """Audit logging for compliance and security tracking."""

    def __init__(self):
        self.logger = structlog.get_logger("audit")
        self._audit_log_file = "/var/log/agent_system/audit.log"

    async def log_operation(self,
                           operation: str,
                           correlation_id: str,
                           status_code: Optional[int] = None,
                           duration_ms: Optional[float] = None,
                           request_data: Optional[Dict[str, Any]] = None,
                           response_data: Optional[Dict[str, Any]] = None,
                           **context):
        """Log operation for audit purposes."""

        audit_event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            correlation_id=correlation_id,
            user_id=context.get('user_id'),
            session_id=context.get('session_id'),
            operation=operation,
            resource_type=context.get('resource_type', 'unknown'),
            resource_id=context.get('resource_id'),
            action=context.get('action', 'unknown'),
            status_code=status_code,
            duration_ms=duration_ms,
            ip_address=context.get('ip_address'),
            user_agent=context.get('user_agent'),
            request_data=self._sanitize_audit_data(request_data),
            response_data=self._sanitize_audit_data(response_data),
            error_message=context.get('error_message'),
            security_context=context.get('security_context')
        )

        # Log to structured logger
        self.logger.info(
            "Audit event",
            audit_event=True,
            **asdict(audit_event)
        )

        # Write to audit log file
        await self._write_audit_log(audit_event)

    async def log_error(self,
                       operation: str,
                       error: str,
                       correlation_id: str,
                       duration_ms: Optional[float] = None,
                       request_data: Optional[Dict[str, Any]] = None,
                       **context):
        """Log error for audit purposes."""

        await self.log_operation(
            operation=operation,
            correlation_id=correlation_id,
            status_code=500,
            duration_ms=duration_ms,
            request_data=request_data,
            error_message=error,
            action="error",
            **context
        )

    def _sanitize_audit_data(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sanitize sensitive data from audit logs."""
        if not data:
            return data

        sanitized = data.copy()
        sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']

        def sanitize_dict(d):
            for key, value in d.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    d[key] = "***REDACTED***"
                elif isinstance(value, dict):
                    sanitize_dict(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            sanitize_dict(item)

        sanitize_dict(sanitized)
        return sanitized

    async def _write_audit_log(self, audit_event: AuditEvent):
        """Write audit event to log file."""
        try:
            audit_line = json.dumps(asdict(audit_event), default=str) + "\n"

            # In production, use proper async file writing
            # For now, we'll use the logging system
            self.logger.info("Audit log entry", audit_data=audit_line.strip())

        except Exception as e:
            # Don't let audit logging failures break the system
            self.logger.error("Failed to write audit log", error=str(e))

class ErrorLogger:
    """Enhanced error logging with context and recovery information."""

    def __init__(self):
        self.logger = structlog.get_logger("error")

    async def log_error(self,
                       error: Exception,
                       correlation_id: str,
                       service_name: str = "unknown",
                       function_name: str = "unknown",
                       **context):
        """Log detailed error information."""

        import traceback
        import sys

        # Get stack trace
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack_trace = traceback.format_exception(exc_type, exc_value, exc_traceback)

        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "correlation_id": correlation_id,
            "service_name": service_name,
            "function_name": function_name,
            "stack_trace": stack_trace,
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "system_info": {
                "platform": sys.platform,
                "executable": sys.executable
            }
        }

        # Add context information
        error_details.update(context)

        self.logger.error(
            f"Error in {service_name}.{function_name}",
            error_details=True,
            **error_details
        )

    async def log_recoverable_error(self,
                                   error: Exception,
                                   recovery_action: str,
                                   correlation_id: str,
                                   **context):
        """Log recoverable errors with recovery information."""

        await self.log_error(
            error=error,
            correlation_id=correlation_id,
            recovery_action=recovery_action,
            recoverable=True,
            **context
        )

# Global logger instances
structured_logger = StructuredLogger()
audit_logger = AuditLogger()
error_logger = ErrorLogger()
```

## Enhanced FastAPI Integration

### Correlation ID Middleware

**File: `backend/app/agents/api/fastapi_app.py`**

```python
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs to all requests."""

    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))

        # Add to request state
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers['X-Correlation-ID'] = correlation_id

        return response

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)
```

### Enhanced Exception Handler

**File: `backend/app/agents/api/fastapi_app.py`**

```python
# Enhanced global exception handler with structured logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured logging."""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')

    error_details = {
        "error": str(exc),
        "type": type(exc).__name__,
        "correlation_id": correlation_id,
        "timestamp": datetime.now().isoformat(),
        "endpoint": f"{request.method} {request.url.path}"
    }

    # Log structured error
    logger.error(
        "Unhandled exception",
        **error_details
    )

    # Record error metrics
    await metrics_collector.record_error(
        method=request.method,
        endpoint=request.url.path,
        error=str(exc),
        correlation_id=correlation_id
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
            "timestamp": error_details["timestamp"]
        }
    )
```

## Logging Configuration

### Loguru Integration (Alternative)

**File: `backend/app/agents/logging_config.py`**

```python
from loguru import logger
import sys
from pathlib import Path
import json
from datetime import datetime

# Remove default handler
logger.remove()

# Console logging with colors
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# File logging with JSON format
log_path = Path("/var/log/agent_system")
log_path.mkdir(parents=True, exist_ok=True)

logger.add(
    log_path / "agent_system_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {extra} | {message}",
    level="DEBUG",
    rotation="00:00",
    retention="30 days",
    serialize=True  # JSON format
)

# Audit logging
logger.add(
    log_path / "audit_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | AUDIT | {extra} | {message}",
    level="INFO",
    rotation="00:00",
    retention="1 year",
    filter=lambda record: record["extra"].get("audit_event", False)
)

# Performance logging
logger.add(
    log_path / "performance_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | PERF | {extra} | {message}",
    level="INFO",
    rotation="00:00",
    retention="90 days",
    filter=lambda record: record["extra"].get("metric_type") == "performance"
)

def log_with_context(logger_func, message: str, **context):
    """Log with structured context."""
    return logger_func(message, **context)

def audit_log(operation: str, **context):
    """Log audit event."""
    context["audit_event"] = True
    context["timestamp"] = datetime.now().isoformat()
    logger.info(f"AUDIT: {operation}", **context)

def performance_log(metric_name: str, value: float, **context):
    """Log performance metric."""
    context["metric_type"] = "performance"
    context["metric_name"] = metric_name
    context["metric_value"] = value
    context["timestamp"] = datetime.now().isoformat()
    logger.info(f"PERF: {metric_name} = {value}", **context)
```

## Usage Examples

### Operation Context Logging

```python
# In API endpoints
@app.get("/agents")
async def list_agents(request: Request):
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')

    with structured_logger.operation_context(
        "list_agents",
        correlation_id,
        user_id=request.user.id if hasattr(request, 'user') else None
    ):
        try:
            agents = await agent_service.get_agents()
            return {"agents": agents}
        except Exception as e:
            await error_logger.log_error(
                error=e,
                correlation_id=correlation_id,
                service_name="agent_api",
                function_name="list_agents"
            )
            raise
```

### Audit Logging

```python
# In task execution
await audit_logger.log_operation(
    operation="execute_agent_task",
    correlation_id=correlation_id,
    resource_type="task",
    resource_id=task_id,
    action="create",
    request_data=task.dict(),
    ip_address=request.client.host if request.client else None,
    user_agent=request.headers.get("User-Agent")
)
```

### Error Logging with Recovery

```python
# In circuit breaker scenarios
await error_logger.log_recoverable_error(
    error=circuit_breaker_error,
    recovery_action="using_cached_data",
    correlation_id=correlation_id,
    service_name="agent_service",
    function_name="get_agents"
)
```

## Log Analysis and Monitoring

### Log Aggregation Setup

```yaml
# docker-compose.yml (logging section)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

# Fluentd configuration
fluentd:
  image: fluent/fluentd:v1.14
  volumes:
    - ./fluent.conf:/fluentd/etc/fluent.conf
    - /var/log/agent_system:/var/log/agent_system
  ports:
    - "24224:24224"
```

### Kibana Dashboards

Key dashboards for monitoring:

1. **Error Rate Dashboard**: Track error rates by service and endpoint
2. **Performance Dashboard**: Monitor response times and throughput
3. **Audit Dashboard**: Security events and access patterns
4. **Agent Activity Dashboard**: Agent performance and utilization

## Compliance and Security

### GDPR Compliance Logging

```python
async def log_data_processing(activity: str, data_subjects: List[str], **context):
    """Log data processing activities for GDPR compliance."""
    await audit_logger.log_operation(
        operation="data_processing",
        correlation_id=context.get("correlation_id", "unknown"),
        resource_type="personal_data",
        action="process",
        security_context={
            "gdpr_activity": activity,
            "data_subjects": data_subjects,
            "processing_purpose": context.get("purpose"),
            "retention_period": context.get("retention_days", 2555)  # 7 years default
        }
    )
```

### Security Event Logging

```python
async def log_security_incident(incident_type: str, severity: str, **context):
    """Log security incidents."""
    await structured_logger.log_security_event(
        event_type=incident_type,
        severity=severity,
        correlation_id=context.get("correlation_id", "unknown"),
        **context
    )

    # Also log to audit
    await audit_logger.log_operation(
        operation="security_incident",
        correlation_id=context.get("correlation_id", "unknown"),
        resource_type="security",
        action="incident_detected",
        error_message=f"{incident_type}: {context.get('description', '')}"
    )
```

This structured logging implementation provides enterprise-grade observability, compliance capabilities, and debugging support that goes beyond basic MVP requirements.
