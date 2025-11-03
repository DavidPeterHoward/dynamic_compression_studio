"""
Structured logging system for Dynamic Compression Algorithms.

This module provides comprehensive logging capabilities with:
- Structured JSON logging
- Correlation ID tracking
- Multiple log levels and formats
- Error handling and reporting
- Performance logging
- Security event logging
"""

import logging
import sys
import os
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar
import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import TimeStamper, StackInfoRenderer
import traceback

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

# Global logger instance
_logger: Optional[structlog.BoundLogger] = None


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracking."""
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context."""
    return correlation_id.get()


def set_correlation_id(corr_id: str) -> None:
    """Set the correlation ID in the current context."""
    correlation_id.set(corr_id)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = False,
    enable_syslog: bool = False,
    syslog_host: str = "localhost",
    syslog_port: int = 514
) -> structlog.BoundLogger:
    """
    Setup structured logging system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, text, syslog)
        log_file: Path to log file
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_syslog: Enable syslog logging
        syslog_host: Syslog server host
        syslog_port: Syslog server port
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        TimeStamper(fmt="iso"),
        StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_correlation_id,
        add_timestamp,
        add_service_info,
    ]
    
    # Add format-specific processors
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    elif log_format == "text":
        processors.append(structlog.dev.ConsoleRenderer())
    elif log_format == "syslog":
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Add file handler if enabled
    if enable_file and log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(file_handler)
    
    # Add syslog handler if enabled
    if enable_syslog:
        try:
            from logging.handlers import SysLogHandler
            syslog_handler = SysLogHandler(address=(syslog_host, syslog_port))
            syslog_handler.setFormatter(logging.Formatter("%(message)s"))
            logging.getLogger().addHandler(syslog_handler)
        except ImportError:
            print("Warning: SysLogHandler not available")
    
    # Create global logger instance
    _logger = structlog.get_logger()
    
    # Log startup message
    _logger.info(
        "Logging system initialized",
        log_level=log_level,
        log_format=log_format,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_syslog=enable_syslog
    )
    
    return _logger


def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to log entries."""
    corr_id = get_correlation_id()
    if corr_id:
        event_dict["correlation_id"] = corr_id
    return event_dict


def add_timestamp(logger, method_name, event_dict):
    """Add timestamp to log entries."""
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict


def add_service_info(logger, method_name, event_dict):
    """Add service information to log entries."""
    event_dict["service"] = "dynamic-compression-algorithms"
    event_dict["version"] = "1.0.0"
    event_dict["environment"] = os.getenv("ENVIRONMENT", "development")
    return event_dict


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Structured logger instance
    """
    if _logger is None:
        setup_logging()
    
    if name:
        return structlog.get_logger(name)
    return _logger


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func):
    """Decorator to log function calls with parameters and timing."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        corr_id = get_correlation_id()
        
        # Log function entry
        logger.info(
            "Function call started",
            function=func.__name__,
            module=func.__module__,
            correlation_id=corr_id,
            args_count=len(args),
            kwargs_count=len(kwargs)
        )
        
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful completion
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                "Function call completed",
                function=func.__name__,
                correlation_id=corr_id,
                duration_seconds=duration,
                status="success"
            )
            
            return result
            
        except Exception as e:
            # Log error
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(
                "Function call failed",
                function=func.__name__,
                correlation_id=corr_id,
                duration_seconds=duration,
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc(),
                status="error"
            )
            raise
    
    return wrapper


def log_performance(operation: str, duration: float, **kwargs):
    """
    Log performance metrics.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional performance metrics
    """
    logger = get_logger("performance")
    logger.info(
        "Performance metric",
        operation=operation,
        duration_seconds=duration,
        correlation_id=get_correlation_id(),
        **kwargs
    )


def log_security_event(
    event_type: str,
    severity: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log security events.
    
    Args:
        event_type: Type of security event
        severity: Event severity (low, medium, high, critical)
        user_id: User ID (if applicable)
        ip_address: IP address (if applicable)
        details: Additional event details
    """
    logger = get_logger("security")
    logger.warning(
        "Security event",
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        correlation_id=get_correlation_id(),
        details=details or {}
    )


def log_business_event(
    event_type: str,
    user_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
):
    """
    Log business events.
    
    Args:
        event_type: Type of business event
        user_id: User ID (if applicable)
        data: Event data
    """
    logger = get_logger("business")
    logger.info(
        "Business event",
        event_type=event_type,
        user_id=user_id,
        correlation_id=get_correlation_id(),
        data=data or {}
    )


# Initialize logging on module import
if _logger is None:
    setup_logging()
