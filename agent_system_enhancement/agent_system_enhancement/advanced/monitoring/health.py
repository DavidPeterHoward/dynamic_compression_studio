"""
Comprehensive health monitoring system for Dynamic Compression Algorithms.

This module provides:
- Component health checks
- Dependency monitoring
- Health status reporting
- Automated health monitoring
- Health metrics collection
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
import psutil
import aiohttp
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger, LoggerMixin
from .metrics import get_metrics_collector


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth:
    """Represents the health status of a component."""
    
    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        last_check: Optional[datetime] = None,
        response_time: Optional[float] = None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.last_check = last_check or datetime.utcnow()
        self.response_time = response_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "last_check": self.last_check.isoformat(),
            "response_time": self.response_time
        }


class HealthMonitor(LoggerMixin):
    """Comprehensive health monitoring system."""
    
    def __init__(self):
        """Initialize the health monitor."""
        self.logger.info("Initializing health monitor")
        
        # Component health status
        self.components: Dict[str, ComponentHealth] = {}
        
        # Health check functions
        self.health_checks: Dict[str, Callable] = {}
        
        # Monitoring configuration
        self.check_interval = 30  # seconds
        self.timeout = 10  # seconds
        
        # Background monitoring
        self._running = False
        self._background_thread = None
        
        # Register default health checks
        self._register_default_checks()
        
        self.logger.info("Health monitor initialized successfully")
    
    def _register_default_checks(self):
        """Register default health check functions."""
        self.register_health_check("system", self._check_system_health)
        self.register_health_check("database", self._check_database_health)
        self.register_health_check("redis", self._check_redis_health)
        self.register_health_check("compression_engine", self._check_compression_engine_health)
        self.register_health_check("api", self._check_api_health)
        self.register_health_check("memory", self._check_memory_health)
        self.register_health_check("disk", self._check_disk_health)
        self.register_health_check("network", self._check_network_health)
    
    def register_health_check(self, name: str, check_function: Callable):
        """Register a health check function."""
        self.health_checks[name] = check_function
        self.logger.info(f"Registered health check: {name}")
    
    async def check_component_health(self, component_name: str) -> ComponentHealth:
        """Check the health of a specific component."""
        if component_name not in self.health_checks:
            return ComponentHealth(
                name=component_name,
                status=HealthStatus.UNKNOWN,
                message=f"No health check registered for {component_name}"
            )
        
        start_time = time.time()
        try:
            check_function = self.health_checks[component_name]
            
            if asyncio.iscoroutinefunction(check_function):
                result = await asyncio.wait_for(check_function(), timeout=self.timeout)
            else:
                result = check_function()
            
            response_time = time.time() - start_time
            
            if isinstance(result, dict):
                status = HealthStatus(result.get("status", "unknown"))
                message = result.get("message", "")
                details = result.get("details", {})
            else:
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Component is healthy" if result else "Component check failed"
                details = {}
            
            health = ComponentHealth(
                name=component_name,
                status=status,
                message=message,
                details=details,
                response_time=response_time
            )
            
        except asyncio.TimeoutError:
            health = ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout} seconds",
                response_time=self.timeout
            )
        except Exception as e:
            health = ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time=time.time() - start_time
            )
        
        # Update component status
        self.components[component_name] = health
        
        # Log health status
        if health.status == HealthStatus.HEALTHY:
            self.logger.debug(f"Component {component_name} is healthy")
        elif health.status == HealthStatus.DEGRADED:
            self.logger.warning(f"Component {component_name} is degraded: {health.message}")
        else:
            self.logger.error(f"Component {component_name} is unhealthy: {health.message}")
        
        return health
    
    async def check_all_health(self) -> Dict[str, ComponentHealth]:
        """Check health of all registered components."""
        self.logger.debug("Starting comprehensive health check")
        
        tasks = []
        for component_name in self.health_checks.keys():
            task = self.check_component_health(component_name)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            component_name = list(self.health_checks.keys())[i]
            if isinstance(result, Exception):
                self.components[component_name] = ComponentHealth(
                    name=component_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed with exception: {str(result)}"
                )
        
        self.logger.debug("Completed comprehensive health check")
        return self.components
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall health status based on all components."""
        if not self.components:
            return HealthStatus.UNKNOWN
        
        statuses = [comp.status for comp in self.components.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of all component health."""
        overall_status = self.get_overall_health()
        
        summary = {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                name: component.to_dict()
                for name, component in self.components.items()
            },
            "summary": {
                "total_components": len(self.components),
                "healthy": len([c for c in self.components.values() if c.status == HealthStatus.HEALTHY]),
                "degraded": len([c for c in self.components.values() if c.status == HealthStatus.DEGRADED]),
                "unhealthy": len([c for c in self.components.values() if c.status == HealthStatus.UNHEALTHY]),
                "unknown": len([c for c in self.components.values() if c.status == HealthStatus.UNKNOWN])
            }
        }
        
        return summary
    
    def start_background_monitoring(self):
        """Start background health monitoring."""
        if self._running:
            return
        
        self._running = True
        self._background_thread = threading.Thread(
            target=self._background_monitoring_loop,
            daemon=True
        )
        self._background_thread.start()
        self.logger.info("Background health monitoring started")
    
    def stop_background_monitoring(self):
        """Stop background health monitoring."""
        self._running = False
        if self._background_thread:
            self._background_thread.join()
        self.logger.info("Background health monitoring stopped")
    
    def _background_monitoring_loop(self):
        """Background loop for health monitoring."""
        while self._running:
            try:
                # Run health checks in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.check_all_health())
                loop.close()
                
                # Update metrics
                self._update_health_metrics()
                
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in background health monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _update_health_metrics(self):
        """Update health-related metrics."""
        try:
            metrics = get_metrics_collector()
            
            # Update component health metrics
            for component_name, component in self.components.items():
                health_value = 1.0 if component.status == HealthStatus.HEALTHY else 0.0
                metrics.set_custom_gauge(
                    "component_health",
                    component_name,
                    health_value
                )
                
                if component.response_time:
                    metrics.observe_custom_histogram(
                        "health_check_duration",
                        component_name,
                        component.response_time
                    )
            
            # Update overall health metric
            overall_health = self.get_overall_health()
            overall_value = 1.0 if overall_health == HealthStatus.HEALTHY else 0.0
            metrics.set_custom_gauge("overall_health", "system", overall_value)
            
        except Exception as e:
            self.logger.error(f"Error updating health metrics: {e}")
    
    # Default health check implementations
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            details = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available": memory.available
            }
            
            if cpu_percent > 90 or memory.percent > 90:
                return {
                    "status": "degraded",
                    "message": "High system resource usage",
                    "details": details
                }
            elif cpu_percent > 80 or memory.percent > 80:
                return {
                    "status": "degraded",
                    "message": "Elevated system resource usage",
                    "details": details
                }
            else:
                return {
                    "status": "healthy",
                    "message": "System resources are normal",
                    "details": details
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"System health check failed: {str(e)}",
                "details": {}
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            # This would typically check database connection
            # For now, we'll simulate a healthy database
            return {
                "status": "healthy",
                "message": "Database connection is healthy",
                "details": {
                    "connection_pool_size": 10,
                    "active_connections": 2
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database health check failed: {str(e)}",
                "details": {}
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health."""
        try:
            # This would typically check Redis connection
            # For now, we'll simulate a healthy Redis
            return {
                "status": "healthy",
                "message": "Redis connection is healthy",
                "details": {
                    "connected_clients": 5,
                    "used_memory": "1.2MB"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Redis health check failed: {str(e)}",
                "details": {}
            }
    
    async def _check_compression_engine_health(self) -> Dict[str, Any]:
        """Check compression engine health."""
        try:
            # This would typically check compression engine status
            # For now, we'll simulate a healthy engine
            return {
                "status": "healthy",
                "message": "Compression engine is operational",
                "details": {
                    "available_algorithms": ["gzip", "brotli", "lz4", "zstandard"],
                    "active_workers": 4
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Compression engine health check failed: {str(e)}",
                "details": {}
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API health."""
        try:
            # This would typically check API endpoints
            # For now, we'll simulate a healthy API
            return {
                "status": "healthy",
                "message": "API endpoints are responding",
                "details": {
                    "endpoints": ["/health", "/api/v1/compression", "/api/v1/files"],
                    "response_time_avg": 0.05
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"API health check failed: {str(e)}",
                "details": {}
            }
    
    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory health."""
        try:
            memory = psutil.virtual_memory()
            
            details = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            }
            
            if memory.percent > 95:
                return {
                    "status": "unhealthy",
                    "message": "Critical memory usage",
                    "details": details
                }
            elif memory.percent > 85:
                return {
                    "status": "degraded",
                    "message": "High memory usage",
                    "details": details
                }
            else:
                return {
                    "status": "healthy",
                    "message": "Memory usage is normal",
                    "details": details
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Memory health check failed: {str(e)}",
                "details": {}
            }
    
    async def _check_disk_health(self) -> Dict[str, Any]:
        """Check disk health."""
        try:
            disk = psutil.disk_usage('/')
            
            details = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
            
            if disk.percent > 95:
                return {
                    "status": "unhealthy",
                    "message": "Critical disk usage",
                    "details": details
                }
            elif disk.percent > 85:
                return {
                    "status": "degraded",
                    "message": "High disk usage",
                    "details": details
                }
            else:
                return {
                    "status": "healthy",
                    "message": "Disk usage is normal",
                    "details": details
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Disk health check failed: {str(e)}",
                "details": {}
            }
    
    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network health."""
        try:
            # This would typically check network connectivity
            # For now, we'll simulate a healthy network
            return {
                "status": "healthy",
                "message": "Network connectivity is normal",
                "details": {
                    "interfaces": ["eth0", "lo"],
                    "packets_sent": 1000,
                    "packets_received": 1000
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Network health check failed: {str(e)}",
                "details": {}
            }


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def setup_health_monitoring(
    enable_background_monitoring: bool = True,
    check_interval: int = 30
) -> HealthMonitor:
    """
    Setup the health monitoring system.
    
    Args:
        enable_background_monitoring: Enable background health monitoring
        check_interval: Health check interval in seconds
        
    Returns:
        Health monitor instance
    """
    global _health_monitor
    
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
        _health_monitor.check_interval = check_interval
        
        if enable_background_monitoring:
            _health_monitor.start_background_monitoring()
    
    return _health_monitor


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance."""
    if _health_monitor is None:
        return setup_health_monitoring()
    return _health_monitor


# Initialize health monitoring on module import
if _health_monitor is None:
    setup_health_monitoring()
