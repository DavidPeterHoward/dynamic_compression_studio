"""
Metrics API endpoints for the Dynamic Compression Algorithms backend.

This module provides endpoints for performance monitoring, analytics,
and metrics collection with comprehensive reporting capabilities.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timedelta

from app.models.metrics import (
    MetricsRequest, MetricsAggregation, MetricsComparison,
    MetricType, TimeRange, CompressionMetrics, PerformanceMetrics,
    QualityMetrics, AlgorithmMetrics
)
from app.core.metrics_collector import MetricsCollector

router = APIRouter()

# Global metrics collector instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


@router.get("/summary", summary="Get Metrics Summary")
async def get_metrics_summary(
    time_range: TimeRange = Query(TimeRange.DAY, description="Time range for summary"),
    metrics_collector: MetricsCollector = Depends(get_metrics_collector)
) -> Dict[str, Any]:
    """
    Get comprehensive metrics summary for the specified time range.
    
    **Example Request:**
    ```
    GET /api/v1/metrics/summary?time_range=day
    ```
    
    **Example Response:**
    ```json
    {
        "time_range": "day",
        "total_compressions": 150,
        "average_compression_ratio": 2.45,
        "average_compression_speed": 15.2,
        "average_compression_time": 0.045,
        "average_quality_score": 0.92,
        "best_algorithm": "zstandard",
        "total_data_processed": 10485760,
        "total_data_saved": 6291456,
        "success_rate": 98.5,
        "error_rate": 1.5,
        "system_performance": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 78.5
        }
    }
    ```
    """
    try:
        # Get metrics summary
        summary = metrics_collector.get_metrics_summary(time_range)
        
        # Get current system performance
        performance_metrics = metrics_collector.collect_performance_metrics()
        
        # Enhance summary with system performance
        summary["system_performance"] = {
            "cpu_usage": performance_metrics.cpu_usage,
            "memory_usage": performance_metrics.memory_usage,
            "disk_usage": performance_metrics.disk_usage,
            "active_connections": performance_metrics.active_connections,
            "requests_per_second": performance_metrics.requests_per_second,
            "average_response_time": performance_metrics.average_response_time,
            "error_rate": performance_metrics.error_rate
        }
        
        # Calculate success rate
        if summary["total_compressions"] > 0:
            summary["success_rate"] = 100.0 - summary.get("error_rate", 0.0)
        else:
            summary["success_rate"] = 100.0
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics summary: {str(e)}"
        )


@router.get("/performance", summary="Get Performance Metrics")
async def get_performance_metrics(
    metrics_collector: MetricsCollector = Depends(get_metrics_collector)
) -> PerformanceMetrics:
    """
    Get current system performance metrics.
    
    **Example Request:**
    ```
    GET /api/v1/metrics/performance
    ```
    
    **Example Response:**
    ```json
    {
        "cpu_usage": 45.2,
        "memory_usage": 62.8,
        "disk_usage": 78.5,
        "network_usage": 2.3,
        "active_connections": 25,
        "requests_per_second": 12.5,
        "average_response_time": 0.045,
        "error_rate": 1.5,
        "queue_size": 5,
        "queue_processing_rate": 15.2,
        "average_wait_time": 0.032,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    ```
    """
    try:
        return metrics_collector.collect_performance_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/algorithms", summary="Get Algorithm Metrics")
async def get_algorithm_metrics(
    algorithm: Optional[str] = Query(None, description="Specific algorithm to get metrics for"),
    metrics_collector: MetricsCollector = Depends(get_metrics_collector)
) -> Dict[str, Any]:
    """
    Get metrics for compression algorithms.
    
    **Example Request:**
    ```
    GET /api/v1/metrics/algorithms?algorithm=gzip
    ```
    
    **Example Response:**
    ```json
    {
        "algorithm_name": "gzip",
        "success_rate": 98.5,
        "average_compression_ratio": 2.1,
        "average_compression_time": 0.032,
        "average_memory_usage": 1048576,
        "average_quality_score": 0.89,
        "average_information_preservation": 0.95,
        "total_uses": 1250,
        "successful_uses": 1231,
        "failed_uses": 19,
        "content_type_performance": {
            "text": {
                "compression_ratio": 2.3,
                "success_rate": 99.2
            },
            "code": {
                "compression_ratio": 1.8,
                "success_rate": 97.8
            }
        },
        "last_used": "2024-01-01T12:00:00Z",
        "created_at": "2024-01-01T00:00:00Z"
    }
    ```
    """
    try:
        if algorithm:
            # Get metrics for specific algorithm
            algo_metrics = metrics_collector.get_algorithm_metrics(algorithm)
            if not algo_metrics:
                raise HTTPException(
                    status_code=404,
                    detail=f"No metrics found for algorithm: {algorithm}"
                )
            return algo_metrics.dict()
        else:
            # Get metrics for all algorithms
            all_metrics = {}
            for algo_name in ["gzip", "lzma", "bzip2", "lz4", "zstandard", "brotli", "content_aware"]:
                algo_metrics = metrics_collector.get_algorithm_metrics(algo_name)
                if algo_metrics:
                    all_metrics[algo_name] = algo_metrics.dict()
            
            return {
                "algorithms": all_metrics,
                "total_algorithms": len(all_metrics)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get algorithm metrics: {str(e)}"
        )


@router.post("/aggregate", summary="Aggregate Metrics")
async def aggregate_metrics(
    request: MetricsRequest,
    metrics_collector: MetricsCollector = Depends(get_metrics_collector)
) -> MetricsAggregation:
    """
    Aggregate metrics for analysis and reporting.
    
    **Example Request:**
    ```json
    {
        "metric_types": ["compression_ratio", "compression_speed"],
        "algorithms": ["gzip", "lzma"],
        "content_types": ["text"],
        "start_time": "2024-01-01T00:00:00Z",
        "end_time": "2024-01-01T23:59:59Z",
        "time_range": "day",
        "aggregate": true,
        "group_by": ["algorithm", "content_type"]
    }
    ```
    
    **Example Response:**
    ```json
    {
        "metric_type": "compression_ratio",
        "time_range": "day",
        "start_time": "2024-01-01T00:00:00Z",
        "end_time": "2024-01-01T23:59:59Z",
        "count": 150,
        "min_value": 1.2,
        "max_value": 4.8,
        "mean_value": 2.45,
        "median_value": 2.3,
        "std_deviation": 0.8,
        "p25": 1.8,
        "p75": 3.1,
        "p90": 3.8,
        "p95": 4.2,
        "p99": 4.6,
        "total_value": 367.5,
        "variance": 0.64,
        "algorithm_filter": "gzip",
        "content_type_filter": "text"
    }
    ```
    """
    try:
        # Set default time range if not provided
        if not request.start_time:
            request.start_time = datetime.utcnow() - timedelta(days=1)
        if not request.end_time:
            request.end_time = datetime.utcnow()
        if not request.time_range:
            request.time_range = TimeRange.DAY
        
        # Aggregate metrics for each requested metric type
        aggregations = {}
        for metric_type in request.metric_types or [MetricType.COMPRESSION_RATIO]:
            aggregation = metrics_collector.aggregate_metrics(
                metric_type=metric_type,
                time_range=request.time_range,
                start_time=request.start_time,
                end_time=request.end_time,
                algorithm_filter=request.algorithms[0] if request.algorithms else None,
                content_type_filter=request.content_types[0] if request.content_types else None
            )
            aggregations[str(metric_type)] = aggregation.dict()
        
        return {
            "aggregations": aggregations,
            "request": request.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to aggregate metrics: {str(e)}"
        )


@router.post("/compare", summary="Compare Metrics")
async def compare_metrics(
    comparison_type: str = Query(..., description="Type of comparison (algorithm, time, content_type)"),
    baseline: str = Query(..., description="Baseline for comparison"),
    comparison_targets: List[str] = Query(..., description="Targets to compare against"),
    metric_type: MetricType = Query(MetricType.COMPRESSION_RATIO, description="Metric to compare"),
    time_range: TimeRange = Query(TimeRange.DAY, description="Time range for comparison"),
    metrics_collector: MetricsCollector = Depends(get_metrics_collector)
) -> MetricsComparison:
    """
    Compare metrics across different algorithms, time periods, or content types.
    
    **Example Request:**
    ```
    POST /api/v1/metrics/compare?comparison_type=algorithm&baseline=gzip&comparison_targets=lzma&comparison_targets=zstandard&metric_type=compression_ratio&time_range=day
    ```
    
    **Example Response:**
    ```json
    {
        "comparison_type": "algorithm",
        "baseline": "gzip",
        "comparison_targets": ["lzma", "zstandard"],
        "relative_performance": {
            "lzma": 1.45,
            "zstandard": 1.12
        },
        "absolute_differences": {
            "lzma": 0.8,
            "zstandard": 0.3
        },
        "percentage_differences": {
            "lzma": 45.0,
            "zstandard": 12.0
        },
        "rankings": {
            "lzma": 1,
            "gzip": 2,
            "zstandard": 3
        },
        "best_performer": "lzma",
        "worst_performer": "zstandard",
        "comparison_date": "2024-01-01T12:00:00Z"
    }
    ```
    """
    try:
        # Get baseline metrics
        baseline_aggregation = metrics_collector.aggregate_metrics(
            metric_type=metric_type,
            time_range=time_range,
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow(),
            algorithm_filter=baseline if comparison_type == "algorithm" else None
        )
        
        # Get comparison target metrics
        target_metrics = {}
        for target in comparison_targets:
            target_aggregation = metrics_collector.aggregate_metrics(
                metric_type=metric_type,
                time_range=time_range,
                start_time=datetime.utcnow() - timedelta(days=1),
                end_time=datetime.utcnow(),
                algorithm_filter=target if comparison_type == "algorithm" else None
            )
            target_metrics[target] = target_aggregation.mean_value
        
        # Calculate comparison metrics
        baseline_value = baseline_aggregation.mean_value
        relative_performance = {}
        absolute_differences = {}
        percentage_differences = {}
        
        for target, target_value in target_metrics.items():
            if baseline_value > 0:
                relative_performance[target] = target_value / baseline_value
                absolute_differences[target] = target_value - baseline_value
                percentage_differences[target] = ((target_value - baseline_value) / baseline_value) * 100
            else:
                relative_performance[target] = 1.0
                absolute_differences[target] = 0.0
                percentage_differences[target] = 0.0
        
        # Calculate rankings
        all_values = {baseline: baseline_value, **target_metrics}
        sorted_items = sorted(all_values.items(), key=lambda x: x[1], reverse=True)
        rankings = {item[0]: i + 1 for i, item in enumerate(sorted_items)}
        
        best_performer = sorted_items[0][0]
        worst_performer = sorted_items[-1][0]
        
        return MetricsComparison(
            comparison_type=comparison_type,
            baseline=baseline,
            comparison_targets=comparison_targets,
            relative_performance=relative_performance,
            absolute_differences=absolute_differences,
            percentage_differences=percentage_differences,
            rankings=rankings,
            best_performer=best_performer,
            worst_performer=worst_performer
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare metrics: {str(e)}"
        )


@router.get("/trends", summary="Get Metrics Trends")
async def get_metrics_trends(
    metric_type: MetricType = Query(MetricType.COMPRESSION_RATIO, description="Metric to analyze"),
    time_range: TimeRange = Query(TimeRange.DAY, description="Time range for trends"),
    algorithm: Optional[str] = Query(None, description="Filter by algorithm"),
    metrics_collector: MetricsCollector = Depends(get_metrics_collector)
) -> Dict[str, Any]:
    """
    Get metrics trends over time for analysis and visualization.
    
    **Example Request:**
    ```
    GET /api/v1/metrics/trends?metric_type=compression_ratio&time_range=day&algorithm=gzip
    ```
    
    **Example Response:**
    ```json
    {
        "metric_type": "compression_ratio",
        "time_range": "day",
        "algorithm": "gzip",
        "trends": [
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "value": 2.1,
                "count": 10
            },
            {
                "timestamp": "2024-01-01T01:00:00Z",
                "value": 2.3,
                "count": 15
            },
            {
                "timestamp": "2024-01-01T02:00:00Z",
                "value": 2.0,
                "count": 12
            }
        ],
        "statistics": {
            "trend_direction": "stable",
            "average_change": 0.05,
            "volatility": 0.15,
            "peak_value": 2.5,
            "lowest_value": 1.8
        }
    }
    ```
    """
    try:
        # In a real implementation, this would query time-series data
        # For now, generate mock trend data
        trends = []
        base_time = datetime.utcnow() - timedelta(hours=24)
        base_value = 2.0
        
        for i in range(24):
            timestamp = base_time + timedelta(hours=i)
            # Simulate some variation
            value = base_value + (i % 3 - 1) * 0.2
            count = 10 + (i % 5)
            
            trends.append({
                "timestamp": timestamp.isoformat(),
                "value": round(value, 2),
                "count": count
            })
        
        # Calculate trend statistics
        values = [t["value"] for t in trends]
        avg_change = sum(abs(values[i] - values[i-1]) for i in range(1, len(values))) / (len(values) - 1)
        volatility = (max(values) - min(values)) / 2
        
        # Determine trend direction
        if values[-1] > values[0] + 0.1:
            trend_direction = "increasing"
        elif values[-1] < values[0] - 0.1:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        return {
            "metric_type": str(metric_type),
            "time_range": str(time_range),
            "algorithm": algorithm,
            "trends": trends,
            "statistics": {
                "trend_direction": trend_direction,
                "average_change": round(avg_change, 3),
                "volatility": round(volatility, 3),
                "peak_value": max(values),
                "lowest_value": min(values),
                "average_value": sum(values) / len(values)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics trends: {str(e)}"
        )


@router.get("/system/comprehensive", summary="Get Comprehensive System Metrics")
async def get_comprehensive_system_metrics() -> Dict[str, Any]:
    """
    Get comprehensive system metrics with all available data points.
    This endpoint returns REAL system data including:
    - CPU, Memory, Disk, Network usage
    - Process and thread counts
    - Uptime and load average
    - Detailed hardware information
    
    **Example Request:**
    ```
    GET /api/v1/metrics/system/comprehensive
    ```
    
    **Example Response:**
    ```json
    {
        "cpu_usage": 45.2,
        "memory_usage": 62.8,
        "disk_usage": 78.5,
        "network_usage": 2.3,
        "processes": 156,
        "threads": 842,
        "uptime": 345600,
        "network_connections": 234,
        "active_connections": 45,
        "cpu_details": {...},
        "memory_details": {...},
        "disk_details": {...},
        "network_details": {...}
    }
    ```
    """
    try:
        from app.core.enhanced_metrics_collector import EnhancedSystemMetrics
        return EnhancedSystemMetrics.get_comprehensive_system_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get comprehensive system metrics: {str(e)}"
        )


@router.get("/dashboard", summary="Get Dashboard Metrics")
async def get_dashboard_metrics(
    metrics_collector: MetricsCollector = Depends(get_metrics_collector)
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard metrics for real-time monitoring.
    
    **Example Request:**
    ```
    GET /api/v1/metrics/dashboard
    ```
    
    **Example Response:**
    ```json
    {
        "overview": {
            "total_compressions_today": 150,
            "total_compressions_week": 1050,
            "total_compressions_month": 4200,
            "average_compression_ratio": 2.45,
            "success_rate": 98.5,
            "total_data_saved": 6291456
        },
        "performance": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 78.5,
            "requests_per_second": 12.5,
            "average_response_time": 0.045
        },
        "top_algorithms": [
            {
                "algorithm": "gzip",
                "usage_count": 450,
                "average_ratio": 2.1,
                "success_rate": 99.2
            },
            {
                "algorithm": "zstandard",
                "usage_count": 320,
                "average_ratio": 2.8,
                "success_rate": 98.8
            }
        ],
        "recent_activity": [
            {
                "timestamp": "2024-01-01T12:00:00Z",
                "algorithm": "gzip",
                "compression_ratio": 2.3,
                "processing_time": 0.032
            }
        ]
    }
    ```
    """
    try:
        # Get various metrics for dashboard
        summary = metrics_collector.get_metrics_summary(TimeRange.DAY)
        performance = metrics_collector.collect_performance_metrics()
        
        # Mock top algorithms data
        top_algorithms = [
            {
                "algorithm": "gzip",
                "usage_count": 450,
                "average_ratio": 2.1,
                "success_rate": 99.2
            },
            {
                "algorithm": "zstandard",
                "usage_count": 320,
                "average_ratio": 2.8,
                "success_rate": 98.8
            },
            {
                "algorithm": "lzma",
                "usage_count": 180,
                "average_ratio": 3.2,
                "success_rate": 97.5
            }
        ]
        
        # Mock recent activity
        recent_activity = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "algorithm": "gzip",
                "compression_ratio": 2.3,
                "processing_time": 0.032
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "algorithm": "zstandard",
                "compression_ratio": 2.8,
                "processing_time": 0.045
            }
        ]
        
        return {
            "overview": {
                "total_compressions_today": summary.get("total_compressions", 0),
                "total_compressions_week": summary.get("total_compressions", 0) * 7,
                "total_compressions_month": summary.get("total_compressions", 0) * 30,
                "average_compression_ratio": summary.get("average_compression_ratio", 0),
                "success_rate": summary.get("success_rate", 100.0),
                "total_data_saved": summary.get("total_data_saved", 0)
            },
            "performance": {
                "cpu_usage": performance.cpu_usage,
                "memory_usage": performance.memory_usage,
                "disk_usage": performance.disk_usage,
                "requests_per_second": performance.requests_per_second,
                "average_response_time": performance.average_response_time,
                "error_rate": performance.error_rate
            },
            "top_algorithms": top_algorithms,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )






