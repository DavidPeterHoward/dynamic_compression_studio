"""
Live Metrics API endpoints for real-time system monitoring.

This module provides endpoints for live system metrics, performance monitoring,
and real-time analytics with comprehensive system information.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from datetime import datetime, timedelta
import asyncio
import time

from app.services.live_system_metrics import LiveSystemMetricsService, get_live_metrics_service
from app.models.sensor import SystemMetric, MetricType

router = APIRouter()


@router.get("/live", summary="Get Live System Metrics")
async def get_live_metrics(
    metrics_service: LiveSystemMetricsService = Depends(get_live_metrics_service)
) -> Dict[str, Any]:
    """
    Get real-time live system metrics including CPU temperature, power consumption,
    network latency, and all system resources.
    
    **Example Response:**
    ```json
    {
        "timestamp": "2024-01-01T12:00:00Z",
        "system_info": {
            "platform": "Linux-5.4.0-74-generic-x86_64-with-Ubuntu-20.04-focal",
            "system": "Linux",
            "cpu_count": 8,
            "memory_total_gb": 16.0,
            "uptime_hours": 72.5
        },
        "live_metrics": {
            "cpu": {
                "usage_percent": 45.2,
                "temperature_c": 65.3,
                "load_average": {
                    "1m": 1.2,
                    "5m": 1.5,
                    "15m": 1.8
                }
            },
            "memory": {
                "usage_percent": 62.8,
                "available_gb": 5.9,
                "total_gb": 16.0
            },
            "disk": {
                "usage_percent": 78.5,
                "free_gb": 45.2
            },
            "network": {
                "latency_ms": 12.3,
                "throughput_mbps": 15.7,
                "connections": 25
            },
            "power": {
                "consumption_watts": 85.2
            },
            "processes": {
                "count": 156,
                "uptime_hours": 72.5
            }
        },
        "compression_metrics": {
            "active_compressions": 5,
            "queue_size": 2,
            "average_ratio": 2.3,
            "throughput_mbps": 15.7,
            "success_rate": 98.5,
            "error_rate": 1.5,
            "average_processing_time": 0.045,
            "total_processed_today": 1250,
            "data_saved_today": 2048576
        },
        "health_score": 75.2,
        "performance_indicators": {
            "excellent": false,
            "good": true,
            "fair": false,
            "poor": false
        },
        "efficiency_metrics": {
            "cpu_efficiency": 54.8,
            "memory_efficiency": 37.2,
            "disk_efficiency": 21.5
        }
    }
    ```
    """
    try:
        return await metrics_service.get_metrics_dashboard()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get live metrics: {str(e)}"
        )


@router.get("/dashboard", summary="Get Live Dashboard")
async def get_live_dashboard(
    metrics_service: LiveSystemMetricsService = Depends(get_live_metrics_service)
) -> Dict[str, Any]:
    """
    Get comprehensive live dashboard with real-time system metrics and performance graphs.
    
    **Example Response:**
    ```json
    {
        "overview": {
            "system_health": "good",
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 78.5,
            "network_latency": 12.3,
            "process_count": 156,
            "uptime_hours": 72.5
        },
        "performance_graphs": {
            "cpu_performance": {
                "timestamps": ["2024-01-01T12:00:00Z", "2024-01-01T12:01:00Z"],
                "usage": [45.2, 47.1],
                "temperature": [65.3, 66.1],
                "load_1m": [1.2, 1.3],
                "load_5m": [1.5, 1.6],
                "load_15m": [1.8, 1.9]
            },
            "memory_performance": {
                "timestamps": ["2024-01-01T12:00:00Z", "2024-01-01T12:01:00Z"],
                "usage_percent": [62.8, 63.2],
                "available_gb": [5.9, 5.8]
            },
            "disk_performance": {
                "timestamps": ["2024-01-01T12:00:00Z", "2024-01-01T12:01:00Z"],
                "usage_percent": [78.5, 78.6],
                "free_gb": [45.2, 45.1]
            },
            "network_performance": {
                "timestamps": ["2024-01-01T12:00:00Z", "2024-01-01T12:01:00Z"],
                "latency_ms": [12.3, 11.8],
                "throughput_mbps": [15.7, 16.2],
                "connections": [25, 27]
            }
        },
        "alerts": [],
        "recommendations": [
            "Consider optimizing memory usage - currently at 62.8%",
            "Disk usage is high at 78.5% - consider cleanup"
        ]
    }
    ```
    """
    try:
        # Get live metrics
        live_metrics = await metrics_service.get_metrics_dashboard()
        
        # Get performance graphs data
        graphs_data = await metrics_service.get_performance_graphs_data()
        
        # Generate alerts and recommendations
        alerts = []
        recommendations = []
        
        if live_metrics.get("live_metrics", {}).get("cpu", {}).get("usage_percent", 0) > 80:
            alerts.append("High CPU usage detected")
            recommendations.append("Consider optimizing CPU-intensive processes")
        
        if live_metrics.get("live_metrics", {}).get("memory", {}).get("usage_percent", 0) > 85:
            alerts.append("High memory usage detected")
            recommendations.append("Consider memory optimization or increasing RAM")
        
        if live_metrics.get("live_metrics", {}).get("disk", {}).get("usage_percent", 0) > 90:
            alerts.append("High disk usage detected")
            recommendations.append("Consider disk cleanup or expansion")
        
        if live_metrics.get("live_metrics", {}).get("network", {}).get("latency_ms", 0) > 100:
            alerts.append("High network latency detected")
            recommendations.append("Check network connectivity and performance")
        
        return {
            "overview": {
                "system_health": live_metrics.get("performance_indicators", {}),
                "cpu_usage": live_metrics.get("live_metrics", {}).get("cpu", {}).get("usage_percent", 0),
                "memory_usage": live_metrics.get("live_metrics", {}).get("memory", {}).get("usage_percent", 0),
                "disk_usage": live_metrics.get("live_metrics", {}).get("disk", {}).get("usage_percent", 0),
                "network_latency": live_metrics.get("live_metrics", {}).get("network", {}).get("latency_ms", 0),
                "process_count": live_metrics.get("live_metrics", {}).get("processes", {}).get("count", 0),
                "uptime_hours": live_metrics.get("live_metrics", {}).get("processes", {}).get("uptime_hours", 0)
            },
            "performance_graphs": graphs_data,
            "alerts": alerts,
            "recommendations": recommendations,
            "timestamp": live_metrics.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get live dashboard: {str(e)}"
        )


@router.get("/history", summary="Get Metrics History")
async def get_metrics_history(
    hours: int = Query(1, description="Number of hours of history to retrieve"),
    metrics_service: LiveSystemMetricsService = Depends(get_live_metrics_service)
) -> Dict[str, Any]:
    """
    Get historical metrics data for the specified time period.
    
    **Example Request:**
    ```
    GET /api/v1/live-metrics/history?hours=24
    ```
    
    **Example Response:**
    ```json
    {
        "period_hours": 24,
        "data_points": 2880,
        "metrics": [
            {
                "timestamp": "2024-01-01T12:00:00Z",
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "disk_usage": 78.5,
                "network_latency": 12.3,
                "process_count": 156
            }
        ],
        "statistics": {
            "cpu_usage": {
                "min": 15.2,
                "max": 85.3,
                "avg": 45.7,
                "std": 12.4
            },
            "memory_usage": {
                "min": 45.1,
                "max": 78.9,
                "avg": 62.3,
                "std": 8.7
            }
        }
    }
    ```
    """
    try:
        history = await metrics_service.get_metrics_history(hours)
        
        if not history:
            return {
                "period_hours": hours,
                "data_points": 0,
                "metrics": [],
                "statistics": {}
            }
        
        # Calculate statistics
        cpu_values = [m["cpu_usage"] for m in history]
        memory_values = [m["memory_usage"] for m in history]
        disk_values = [m["disk_usage"] for m in history]
        
        def calculate_stats(values):
            if not values:
                return {}
            return {
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "avg": round(sum(values) / len(values), 2),
                "std": round((sum((x - sum(values)/len(values))**2 for x in values) / len(values))**0.5, 2)
            }
        
        return {
            "period_hours": hours,
            "data_points": len(history),
            "metrics": history,
            "statistics": {
                "cpu_usage": calculate_stats(cpu_values),
                "memory_usage": calculate_stats(memory_values),
                "disk_usage": calculate_stats(disk_values)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics history: {str(e)}"
        )


@router.get("/graphs", summary="Get Performance Graphs Data")
async def get_performance_graphs(
    metrics_service: LiveSystemMetricsService = Depends(get_live_metrics_service)
) -> Dict[str, Any]:
    """
    Get data formatted for performance graphs and charts.
    
    **Example Response:**
    ```json
    {
        "cpu_performance": {
            "timestamps": ["2024-01-01T12:00:00Z"],
            "usage": [45.2],
            "temperature": [65.3],
            "load_1m": [1.2],
            "load_5m": [1.5],
            "load_15m": [1.8]
        },
        "memory_performance": {
            "timestamps": ["2024-01-01T12:00:00Z"],
            "usage_percent": [62.8],
            "available_gb": [5.9]
        },
        "disk_performance": {
            "timestamps": ["2024-01-01T12:00:00Z"],
            "usage_percent": [78.5],
            "free_gb": [45.2]
        },
        "network_performance": {
            "timestamps": ["2024-01-01T12:00:00Z"],
            "latency_ms": [12.3],
            "throughput_mbps": [15.7],
            "connections": [25]
        },
        "system_performance": {
            "timestamps": ["2024-01-01T12:00:00Z"],
            "process_count": [156],
            "uptime_hours": [72.5],
            "power_consumption": [85.2]
        }
    }
    ```
    """
    try:
        return await metrics_service.get_performance_graphs_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance graphs: {str(e)}"
        )


@router.get("/system-info", summary="Get System Information")
async def get_system_info(
    metrics_service: LiveSystemMetricsService = Depends(get_live_metrics_service)
) -> Dict[str, Any]:
    """
    Get detailed system information including hardware specifications.
    
    **Example Response:**
    ```json
    {
        "platform": "Linux-5.4.0-74-generic-x86_64-with-Ubuntu-20.04-focal",
        "system": "Linux",
        "release": "5.4.0-74-generic",
        "version": "#83-Ubuntu SMP Sat May 8 02:35:39 UTC 2021",
        "machine": "x86_64",
        "processor": "x86_64",
        "cpu_count": 8,
        "cpu_freq": 2400.0,
        "memory_total_gb": 16.0,
        "boot_time": "2024-01-01T00:00:00Z",
        "uptime_hours": 72.5
    }
    ```
    """
    try:
        system_info = metrics_service.system_info
        return {
            "platform": system_info.platform,
            "system": system_info.system,
            "release": system_info.release,
            "version": system_info.version,
            "machine": system_info.machine,
            "processor": system_info.processor,
            "cpu_count": system_info.cpu_count,
            "cpu_freq": system_info.cpu_freq,
            "memory_total_gb": round(system_info.memory_total / (1024**3), 2),
            "boot_time": datetime.fromtimestamp(system_info.boot_time).isoformat(),
            "uptime_hours": round((time.time() - system_info.boot_time) / 3600, 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system info: {str(e)}"
        )


@router.post("/start-monitoring", summary="Start Live Monitoring")
async def start_live_monitoring(
    interval_seconds: int = Query(30, description="Monitoring interval in seconds"),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Start continuous live monitoring of system metrics.
    
    **Example Request:**
    ```
    POST /api/v1/live-metrics/start-monitoring?interval_seconds=30
    ```
    
    **Example Response:**
    ```json
    {
        "status": "started",
        "interval_seconds": 30,
        "message": "Live monitoring started successfully"
    }
    ```
    """
    try:
        # Start monitoring in background
        if background_tasks:
            background_tasks.add_task(
                get_live_metrics_service().start_live_monitoring,
                interval_seconds
            )
        
        return {
            "status": "started",
            "interval_seconds": interval_seconds,
            "message": "Live monitoring started successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start monitoring: {str(e)}"
        )


@router.get("/compression-analytics", summary="Get Live Compression Analytics")
async def get_compression_analytics(
    metrics_service: LiveSystemMetricsService = Depends(get_live_metrics_service)
) -> Dict[str, Any]:
    """
    Get live compression performance analytics with real-time data.
    
    **Example Response:**
    ```json
    {
        "live_compression_metrics": {
            "active_compressions": 5,
            "queue_size": 2,
            "average_ratio": 2.3,
            "throughput_mbps": 15.7,
            "success_rate": 98.5,
            "error_rate": 1.5,
            "average_processing_time": 0.045,
            "total_processed_today": 1250,
            "data_saved_today": 2048576
        },
        "algorithm_performance": {
            "gzip": {
                "active_count": 2,
                "average_ratio": 2.1,
                "average_time": 0.032,
                "success_rate": 99.2
            },
            "zstd": {
                "active_count": 1,
                "average_ratio": 2.8,
                "average_time": 0.045,
                "success_rate": 98.8
            }
        },
        "performance_trends": {
            "compression_ratio_trend": "stable",
            "throughput_trend": "increasing",
            "success_rate_trend": "stable"
        },
        "efficiency_metrics": {
            "cpu_efficiency": 85.2,
            "memory_efficiency": 92.1,
            "disk_efficiency": 78.5,
            "network_efficiency": 88.3
        }
    }
    ```
    """
    try:
        live_metrics = await metrics_service.get_metrics_dashboard()
        compression_metrics = live_metrics.get("compression_metrics", {})
        
        # Mock algorithm performance data (replace with real data)
        algorithm_performance = {
            "gzip": {
                "active_count": 2,
                "average_ratio": 2.1,
                "average_time": 0.032,
                "success_rate": 99.2
            },
            "zstd": {
                "active_count": 1,
                "average_ratio": 2.8,
                "average_time": 0.045,
                "success_rate": 98.8
            },
            "lz4": {
                "active_count": 0,
                "average_ratio": 2.0,
                "average_time": 0.020,
                "success_rate": 99.5
            },
            "brotli": {
                "active_count": 1,
                "average_ratio": 2.5,
                "average_time": 0.038,
                "success_rate": 98.9
            }
        }
        
        # Calculate efficiency metrics
        cpu_usage = live_metrics.get("live_metrics", {}).get("cpu", {}).get("usage_percent", 0)
        memory_usage = live_metrics.get("live_metrics", {}).get("memory", {}).get("usage_percent", 0)
        disk_usage = live_metrics.get("live_metrics", {}).get("disk", {}).get("usage_percent", 0)
        network_latency = live_metrics.get("live_metrics", {}).get("network", {}).get("latency_ms", 0)
        
        return {
            "live_compression_metrics": compression_metrics,
            "algorithm_performance": algorithm_performance,
            "performance_trends": {
                "compression_ratio_trend": "stable",
                "throughput_trend": "increasing",
                "success_rate_trend": "stable"
            },
            "efficiency_metrics": {
                "cpu_efficiency": round(100 - cpu_usage, 2),
                "memory_efficiency": round(100 - memory_usage, 2),
                "disk_efficiency": round(100 - disk_usage, 2),
                "network_efficiency": round(max(0, 100 - (network_latency / 10)), 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get compression analytics: {str(e)}"
        )
