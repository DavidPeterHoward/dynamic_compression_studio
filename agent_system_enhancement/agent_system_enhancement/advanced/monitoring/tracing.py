"""
Distributed tracing system for Dynamic Compression Algorithms.

This module provides:
- Distributed tracing with correlation IDs
- Span tracking and performance monitoring
- Trace context propagation
- Trace sampling and filtering
- Integration with monitoring systems
"""

import time
import uuid
import json
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from contextlib import contextmanager
from contextvars import ContextVar
import asyncio
import functools
from enum import Enum

from .logging import get_logger, LoggerMixin, get_correlation_id, set_correlation_id


class SpanStatus(Enum):
    """Span status enumeration."""
    OK = "ok"
    ERROR = "error"
    UNKNOWN = "unknown"


class Span:
    """Represents a span in a distributed trace."""
    
    def __init__(
        self,
        trace_id: str,
        span_id: str,
        name: str,
        parent_id: Optional[str] = None,
        start_time: Optional[datetime] = None
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.name = name
        self.parent_id = parent_id
        self.start_time = start_time or datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.duration: Optional[float] = None
        self.status = SpanStatus.UNKNOWN
        self.error_message: Optional[str] = None
        self.tags: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []
    
    def finish(self, status: SpanStatus = SpanStatus.OK, error_message: Optional[str] = None):
        """Finish the span."""
        self.end_time = datetime.utcnow()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = status
        self.error_message = error_message
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span."""
        self.tags[key] = value
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to the span."""
        event = {
            "name": name,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes or {}
        }
        self.events.append(event)
    
    def add_log(self, message: str, level: str = "info", attributes: Optional[Dict[str, Any]] = None):
        """Add a log entry to the span."""
        log_entry = {
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes or {}
        }
        self.logs.append(log_entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "status": self.status.value,
            "error_message": self.error_message,
            "tags": self.tags,
            "events": self.events,
            "logs": self.logs
        }


class Trace:
    """Represents a complete distributed trace."""
    
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.spans: List[Span] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.root_span: Optional[Span] = None
    
    def add_span(self, span: Span):
        """Add a span to the trace."""
        self.spans.append(span)
        
        if not self.start_time or span.start_time < self.start_time:
            self.start_time = span.start_time
        
        if not self.end_time or (span.end_time and span.end_time > self.end_time):
            self.end_time = span.end_time
        
        if not span.parent_id:
            self.root_span = span
    
    def get_duration(self) -> Optional[float]:
        """Get the total duration of the trace."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def get_span_tree(self) -> Dict[str, Any]:
        """Get the span tree structure."""
        span_map = {span.span_id: span for span in self.spans}
        root_spans = [span for span in self.spans if not span.parent_id]
        
        def build_tree(span: Span) -> Dict[str, Any]:
            children = [build_tree(child) for child in self.spans if child.parent_id == span.span_id]
            return {
                "span": span.to_dict(),
                "children": children
            }
        
        return {
            "trace_id": self.trace_id,
            "duration": self.get_duration(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "root_spans": [build_tree(span) for span in root_spans]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "duration": self.get_duration(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "spans": [span.to_dict() for span in self.spans],
            "span_count": len(self.spans)
        }


class TraceContext:
    """Manages trace context for the current execution."""
    
    def __init__(self):
        self.trace_id: Optional[str] = None
        self.span_id: Optional[str] = None
        self.parent_id: Optional[str] = None
        self.sampled: bool = True
        self.baggage: Dict[str, str] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "sampled": self.sampled,
            "baggage": self.baggage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceContext':
        """Create trace context from dictionary."""
        context = cls()
        context.trace_id = data.get("trace_id")
        context.span_id = data.get("span_id")
        context.parent_id = data.get("parent_id")
        context.sampled = data.get("sampled", True)
        context.baggage = data.get("baggage", {})
        return context


# Context variables for trace context
trace_context: ContextVar[Optional[TraceContext]] = ContextVar('trace_context', default=None)
current_span: ContextVar[Optional[Span]] = ContextVar('current_span', default=None)


class Tracer(LoggerMixin):
    """Distributed tracer implementation."""
    
    def __init__(self):
        """Initialize the tracer."""
        self.logger.info("Initializing distributed tracer")
        
        # Trace storage
        self.traces: Dict[str, Trace] = {}
        self.completed_traces: List[Trace] = []
        
        # Configuration
        self.sampling_rate = 1.0  # 100% sampling
        self.max_traces = 1000
        self.max_spans_per_trace = 100
        
        # Background processing
        self._running = False
        self._background_thread = None
        
        self.logger.info("Distributed tracer initialized successfully")
    
    def start_trace(self, name: str, trace_id: Optional[str] = None) -> Span:
        """Start a new trace."""
        if not self._should_sample():
            return self._create_noop_span()
        
        trace_id = trace_id or str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        # Create trace if it doesn't exist
        if trace_id not in self.traces:
            self.traces[trace_id] = Trace(trace_id)
        
        # Create span
        span = Span(trace_id, span_id, name)
        self.traces[trace_id].add_span(span)
        
        # Set context
        context = TraceContext()
        context.trace_id = trace_id
        context.span_id = span_id
        context.sampled = True
        trace_context.set(context)
        current_span.set(span)
        
        # Set correlation ID for logging
        set_correlation_id(trace_id)
        
        self.logger.debug(f"Started trace: {trace_id}, span: {span_id}, name: {name}")
        return span
    
    def start_span(self, name: str, parent_span: Optional[Span] = None) -> Span:
        """Start a new span."""
        if not self._should_sample():
            return self._create_noop_span()
        
        # Get current context
        context = trace_context.get()
        if not context or not context.trace_id:
            return self.start_trace(name)
        
        span_id = str(uuid.uuid4())
        parent_id = parent_span.span_id if parent_span else context.span_id
        
        # Create span
        span = Span(context.trace_id, span_id, name, parent_id)
        self.traces[context.trace_id].add_span(span)
        
        # Update context
        context.span_id = span_id
        context.parent_id = parent_id
        trace_context.set(context)
        current_span.set(span)
        
        self.logger.debug(f"Started span: {span_id}, name: {name}, parent: {parent_id}")
        return span
    
    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.OK, error_message: Optional[str] = None):
        """Finish a span."""
        if span is None or not hasattr(span, 'trace_id'):
            return  # No-op span
        
        span.finish(status, error_message)
        
        # Update context
        context = trace_context.get()
        if context and context.span_id == span.span_id:
            context.span_id = span.parent_id
            current_span.set(None)
        
        self.logger.debug(f"Finished span: {span.span_id}, duration: {span.duration}s")
    
    def finish_trace(self, trace_id: str):
        """Finish a trace."""
        if trace_id not in self.traces:
            return
        
        trace = self.traces[trace_id]
        
        # Finish any unfinished spans
        for span in trace.spans:
            if not span.end_time:
                span.finish()
        
        # Move to completed traces
        self.completed_traces.append(trace)
        del self.traces[trace_id]
        
        # Clean up old traces
        if len(self.completed_traces) > self.max_traces:
            self.completed_traces = self.completed_traces[-self.max_traces:]
        
        # Clear context
        trace_context.set(None)
        current_span.set(None)
        
        self.logger.info(f"Finished trace: {trace_id}, duration: {trace.get_duration()}s, spans: {len(trace.spans)}")
    
    def get_current_span(self) -> Optional[Span]:
        """Get the current active span."""
        return current_span.get()
    
    def get_current_context(self) -> Optional[TraceContext]:
        """Get the current trace context."""
        return trace_context.get()
    
    def inject_context(self, headers: Dict[str, str]):
        """Inject trace context into headers."""
        context = trace_context.get()
        if context and context.trace_id:
            headers["X-Trace-ID"] = context.trace_id
            headers["X-Span-ID"] = context.span_id or ""
            headers["X-Parent-ID"] = context.parent_id or ""
            headers["X-Sampled"] = "1" if context.sampled else "0"
            if context.baggage:
                headers["X-Baggage"] = json.dumps(context.baggage)
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[TraceContext]:
        """Extract trace context from headers."""
        trace_id = headers.get("X-Trace-ID")
        if not trace_id:
            return None
        
        context = TraceContext()
        context.trace_id = trace_id
        context.span_id = headers.get("X-Span-ID")
        context.parent_id = headers.get("X-Parent-ID")
        context.sampled = headers.get("X-Sampled", "1") == "1"
        
        baggage_str = headers.get("X-Baggage")
        if baggage_str:
            try:
                context.baggage = json.loads(baggage_str)
            except json.JSONDecodeError:
                pass
        
        return context
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID."""
        return self.traces.get(trace_id) or next(
            (trace for trace in self.completed_traces if trace.trace_id == trace_id),
            None
        )
    
    def get_traces(self, limit: int = 100) -> List[Trace]:
        """Get recent traces."""
        all_traces = list(self.traces.values()) + self.completed_traces
        return sorted(all_traces, key=lambda t: t.start_time or datetime.min, reverse=True)[:limit]
    
    def _should_sample(self) -> bool:
        """Determine if the current request should be sampled."""
        return self.sampling_rate >= 1.0 or (self.sampling_rate > 0 and uuid.uuid4().int % 100 < self.sampling_rate * 100)
    
    def _create_noop_span(self) -> Span:
        """Create a no-op span for unsampled traces."""
        span = Span("", "", "")
        span.finish()
        return span
    
    def start_background_processing(self):
        """Start background trace processing."""
        if self._running:
            return
        
        self._running = True
        self._background_thread = threading.Thread(
            target=self._background_processing_loop,
            daemon=True
        )
        self._background_thread.start()
        self.logger.info("Background trace processing started")
    
    def stop_background_processing(self):
        """Stop background trace processing."""
        self._running = False
        if self._background_thread:
            self._background_thread.join()
        self.logger.info("Background trace processing stopped")
    
    def _background_processing_loop(self):
        """Background loop for trace processing."""
        while self._running:
            try:
                # Process completed traces
                self._process_completed_traces()
                time.sleep(10)  # Process every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in background trace processing: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _process_completed_traces(self):
        """Process completed traces."""
        # This would typically send traces to a trace collector
        # For now, we'll just log some statistics
        if self.completed_traces:
            recent_traces = [t for t in self.completed_traces 
                           if t.end_time and t.end_time > datetime.utcnow() - timedelta(minutes=5)]
            
            if recent_traces:
                avg_duration = sum(t.get_duration() or 0 for t in recent_traces) / len(recent_traces)
                avg_spans = sum(len(t.spans) for t in recent_traces) / len(recent_traces)
                
                self.logger.debug(f"Recent traces: {len(recent_traces)}, avg duration: {avg_duration:.3f}s, avg spans: {avg_spans:.1f}")


# Global tracer instance
_tracer: Optional[Tracer] = None


def setup_tracing(
    sampling_rate: float = 1.0,
    enable_background_processing: bool = True
) -> Tracer:
    """
    Setup the distributed tracing system.
    
    Args:
        sampling_rate: Trace sampling rate (0.0 to 1.0)
        enable_background_processing: Enable background trace processing
        
    Returns:
        Tracer instance
    """
    global _tracer
    
    if _tracer is None:
        _tracer = Tracer()
        _tracer.sampling_rate = sampling_rate
        
        if enable_background_processing:
            _tracer.start_background_processing()
    
    return _tracer


def get_tracer() -> Tracer:
    """Get the global tracer instance."""
    if _tracer is None:
        return setup_tracing()
    return _tracer


# Tracing decorators and context managers
def trace_function(name: Optional[str] = None):
    """Decorator to trace function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            span = tracer.start_span(span_name)
            try:
                result = func(*args, **kwargs)
                tracer.finish_span(span, SpanStatus.OK)
                return result
            except Exception as e:
                tracer.finish_span(span, SpanStatus.ERROR, str(e))
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            span = tracer.start_span(span_name)
            try:
                result = await func(*args, **kwargs)
                tracer.finish_span(span, SpanStatus.OK)
                return result
            except Exception as e:
                tracer.finish_span(span, SpanStatus.ERROR, str(e))
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


@contextmanager
def trace_span(name: str):
    """Context manager for tracing spans."""
    tracer = get_tracer()
    span = tracer.start_span(name)
    
    try:
        yield span
        tracer.finish_span(span, SpanStatus.OK)
    except Exception as e:
        tracer.finish_span(span, SpanStatus.ERROR, str(e))
        raise


@contextmanager
def trace_operation(name: str):
    """Context manager for tracing operations."""
    tracer = get_tracer()
    span = tracer.start_span(name)
    
    try:
        yield span
        tracer.finish_span(span, SpanStatus.OK)
    except Exception as e:
        tracer.finish_span(span, SpanStatus.ERROR, str(e))
        raise


# Initialize tracing on module import
if _tracer is None:
    setup_tracing()
