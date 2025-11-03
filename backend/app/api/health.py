"""
Health check API endpoints for the Dynamic Compression Algorithms backend.

This module provides health check and system status endpoints.
"""

from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
import psutil
import asyncio

from app.config import settings
from app.database import check_db_connection

router = APIRouter()


@router.get("/", summary="Health Check")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Checks the health of all system components including:
    - Database connection
    - System resources (CPU, memory, disk)
    - Application status
    
    Returns:
        Detailed health status information
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api.version,
        "environment": settings.environment,
        "components": {}
    }
    
    # Check database connection
    try:
        db_healthy = await check_db_connection()
        health_status["components"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "connected": db_healthy
        }
        if not db_healthy:
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["components"]["system"] = {
            "status": "healthy",
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "memory_available": memory.available,
            "disk_free": disk.free
        }
        
        # Check if system resources are within acceptable limits
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status["components"]["system"]["status"] = "warning"
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"
                
    except Exception as e:
        health_status["components"]["system"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check application status
    health_status["components"]["application"] = {
        "status": "healthy",
        "name": settings.app_name,
        "version": settings.api.version,
        "debug": settings.api.debug
    }
    
    return health_status


@router.get("/readiness", summary="Readiness Check")
@router.get("/health/readiness", summary="Readiness Check (Alt)")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes/container orchestration.

    This endpoint checks if the application is ready to receive traffic.
    It performs lighter checks than the full health check.

    Returns:
        Readiness status
    """
    readiness_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Check database connection (critical for readiness)
    try:
        db_ready = await check_db_connection()
        if not db_ready:
            readiness_status["status"] = "not_ready"
            readiness_status["reason"] = "Database connection failed"
    except Exception as e:
        readiness_status["status"] = "not_ready"
        readiness_status["reason"] = f"Database error: {str(e)}"

    return readiness_status


@router.get("/liveness", summary="Liveness Check")
@router.get("/health/liveness", summary="Liveness Check (Alt)")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint for Kubernetes/container orchestration.

    This endpoint checks if the application is alive and responsive.
    It performs minimal checks to avoid overhead.

    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api.version
    }


@router.get("/detailed", summary="Detailed Health Check")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with comprehensive system information.
    
    Provides detailed information about all system components,
    including performance metrics and resource usage.
    
    Returns:
        Detailed health and system information
    """
    detailed_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api.version,
        "environment": settings.environment,
        "system_info": {},
        "performance_metrics": {},
        "resource_usage": {}
    }
    
    try:
        # System information
        detailed_status["system_info"] = {
            "platform": psutil.sys.platform,
            "python_version": psutil.sys.version,
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total
        }
        
        # Performance metrics
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        detailed_status["performance_metrics"] = {
            "cpu_usage_per_core": cpu_percent,
            "cpu_usage_total": sum(cpu_percent) / len(cpu_percent),
            "memory_usage_percent": memory.percent,
            "memory_available": memory.available,
            "memory_used": memory.used,
            "disk_usage_percent": disk.percent,
            "disk_free": disk.free,
            "disk_used": disk.used
        }
        
        # Resource usage
        detailed_status["resource_usage"] = {
            "cpu_load": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            "memory_swap": psutil.swap_memory()._asdict(),
            "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
            "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
        }
        
        # Check thresholds and update status
        if detailed_status["performance_metrics"]["cpu_usage_total"] > 90:
            detailed_status["status"] = "warning"
            detailed_status["warnings"] = ["High CPU usage"]
            
        if detailed_status["performance_metrics"]["memory_usage_percent"] > 90:
            detailed_status["status"] = "warning"
            if "warnings" not in detailed_status:
                detailed_status["warnings"] = []
            detailed_status["warnings"].append("High memory usage")
            
        if detailed_status["performance_metrics"]["disk_usage_percent"] > 90:
            detailed_status["status"] = "warning"
            if "warnings" not in detailed_status:
                detailed_status["warnings"] = []
            detailed_status["warnings"].append("High disk usage")
            
    except Exception as e:
        detailed_status["status"] = "error"
        detailed_status["error"] = str(e)
    
    return detailed_status


@router.get("/status", summary="Status Check")
@router.get("/health/status", summary="Status Check (Alt)")
async def status_check() -> Dict[str, Any]:
    """
    Simple status check endpoint.

    Returns basic application status information.

    Returns:
        Basic status information
    """
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api.version,
        "environment": settings.environment,
        "app_name": settings.app_name
    }






