"""
Evaluation API endpoints for the Dynamic Compression Algorithms backend.

This module provides comprehensive evaluation endpoints for metrics analysis,
algorithm comparison, trend analysis, sensor fusion, and experimental results.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.evaluation import (
    EvaluationRequest, EvaluationResponse, EvaluationFilters, TimeRange, EvaluationView,
    ComparisonRequest, ComparisonResponse, TrendsRequest, TrendsResponse,
    SensorFusionRequest, SensorFusionResponse, ExperimentsRequest, ExperimentsResponse
)
from app.services.evaluation_service import get_evaluation_service
from app.core.metrics_collector import MetricsCollector
from app.core.compression_engine import CompressionEngine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/metrics", summary="Get Evaluation Metrics", response_model=EvaluationResponse)
async def get_evaluation_metrics(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    metrics_collector: MetricsCollector = Depends(),
    compression_engine: CompressionEngine = Depends()
) -> EvaluationResponse:
    """
    Get comprehensive evaluation metrics for the specified time range and filters.
    
    This endpoint provides a complete evaluation overview including algorithm performance,
    system metrics, content analysis, experimental results, quality metrics, comparative
    analysis, and sensor fusion data.
    
    **Example Request:**
    ```json
    {
        "filters": {
            "time_range": "day",
            "algorithms": ["gzip", "zstandard", "brotli"],
            "content_types": ["text", "image"],
            "min_compression_ratio": 2.0,
            "max_compression_ratio": 5.0
        },
        "view": "overview",
        "include_details": true,
        "format": "json"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Evaluation metrics collected successfully",
        "data": {
            "algorithm_performance": [
                {
                    "algorithm_name": "zstandard",
                    "compression_ratio": 3.2,
                    "compression_speed": 18.7,
                    "memory_usage": 52.3,
                    "accuracy": 97.8,
                    "efficiency": 91.2,
                    "reliability": 94.5,
                    "adaptability": 88.9,
                    "quality": 92.3,
                    "throughput": 145.2,
                    "success_rate": 99.1,
                    "total_operations": 980,
                    "average_processing_time": 0.038
                }
            ],
            "system_performance": {
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "disk_usage": 78.5,
                "network_usage": 23.1,
                "gpu_usage": 15.7,
                "temperature": 42.3,
                "power_consumption": 125.6,
                "response_time": 45.8,
                "throughput": 156.7,
                "error_rate": 1.2,
                "availability": 99.8
            },
            "content_analysis": {
                "total_files": 1250,
                "total_size": 1048576000,
                "content_types": {"text": 450, "image": 300, "video": 200},
                "complexity_scores": {"text": 0.65, "image": 0.85, "video": 0.92},
                "entropy_distribution": {"low": 0.25, "medium": 0.45, "high": 0.30},
                "average_file_size": 838860,
                "largest_file_size": 52428800,
                "smallest_file_size": 1024
            },
            "experimental_results": {
                "total_experiments": 85,
                "successful_experiments": 78,
                "failed_experiments": 7,
                "meta_learning_progress": 72.5,
                "synthetic_data_generated": 524288000,
                "algorithm_evolutions": 12,
                "performance_improvements": {"compression_ratio": 15.2, "speed": 8.7},
                "innovation_score": 85.7,
                "experiment_success_rate": 91.8
            },
            "quality_metrics": {
                "overall_quality": 88.5,
                "compression_quality": 91.2,
                "decompression_quality": 89.7,
                "data_integrity": 99.8,
                "consistency": 87.3,
                "reliability": 92.1,
                "user_satisfaction": 85.9,
                "accuracy": 94.6
            },
            "comparative_analysis": {
                "algorithm_ranking": [
                    {"algorithm": "zstandard", "score": 94.5, "rank": 1},
                    {"algorithm": "gzip", "score": 88.7, "rank": 2}
                ],
                "performance_comparison": {
                    "zstandard": {"compression_ratio": 3.2, "speed": 18.7, "quality": 92.3},
                    "gzip": {"compression_ratio": 2.5, "speed": 15.2, "quality": 89.7}
                },
                "efficiency_analysis": {"zstandard": 91.2, "gzip": 88.5},
                "quality_comparison": {"zstandard": 92.3, "gzip": 89.7},
                "cost_benefit_analysis": {
                    "zstandard": {"cost": 0.15, "benefit": 0.92, "ratio": 6.13},
                    "gzip": {"cost": 0.12, "benefit": 0.85, "ratio": 7.08}
                }
            },
            "sensor_fusion": {
                "multi_modal_data": {
                    "compression_metrics": 0.92,
                    "system_metrics": 0.88,
                    "quality_metrics": 0.91,
                    "user_feedback": 0.85
                },
                "cross_validation_scores": {
                    "algorithm_performance": 0.89,
                    "system_performance": 0.87,
                    "quality_assessment": 0.91
                },
                "ensemble_scores": {
                    "weighted_average": 0.89,
                    "majority_voting": 0.87,
                    "stacking": 0.92
                },
                "confidence_intervals": {
                    "compression_ratio": {"lower": 2.8, "upper": 3.6, "confidence": 0.95},
                    "quality_score": {"lower": 88.5, "upper": 94.2, "confidence": 0.95}
                },
                "fusion_accuracy": 91.3,
                "data_correlation": {
                    "compression_quality": 0.85,
                    "system_performance": 0.78,
                    "user_satisfaction": 0.82
                }
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "time_range": "day"
        },
        "view_data": {
            "overview": {
                "key_metrics": {
                    "performance": 91.2,
                    "efficiency": 88.5,
                    "reliability": 92.1,
                    "innovation": 85.7
                },
                "top_algorithms": [
                    {"name": "zstandard", "score": 94.5},
                    {"name": "gzip", "score": 88.7}
                ],
                "system_health": {
                    "status": "healthy",
                    "score": 95.2,
                    "alerts": []
                }
            }
        },
        "timestamp": "2024-01-01T12:00:00Z",
        "processing_time": 0.245
    }
    ```
    """
    start_time = time.time()
    
    try:
        # Get evaluation service
        evaluation_service = get_evaluation_service(metrics_collector, compression_engine)
        
        # Get evaluation metrics
        evaluation_metrics = await evaluation_service.get_evaluation_metrics(request.filters)
        
        # Generate view-specific data
        view_data = await _generate_view_data(request.view, evaluation_metrics, request.include_details)
        
        processing_time = time.time() - start_time
        
        return EvaluationResponse(
            success=True,
            message="Evaluation metrics collected successfully",
            data=evaluation_metrics,
            view_data=view_data,
            timestamp=datetime.utcnow(),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error getting evaluation metrics: {e}")
        processing_time = time.time() - start_time
        
        return EvaluationResponse(
            success=False,
            message=f"Error collecting evaluation metrics: {str(e)}",
            data=None,
            view_data=None,
            timestamp=datetime.utcnow(),
            processing_time=processing_time
        )


@router.post("/compare", summary="Compare Algorithms", response_model=ComparisonResponse)
async def compare_algorithms(
    request: ComparisonRequest,
    metrics_collector: MetricsCollector = Depends(),
    compression_engine: CompressionEngine = Depends()
) -> ComparisonResponse:
    """
    Compare algorithms based on specified metrics and time range.
    
    This endpoint provides detailed comparison analysis including rankings,
    statistical analysis, and recommendations.
    
    **Example Request:**
    ```json
    {
        "algorithms": ["gzip", "zstandard", "brotli"],
        "metrics": ["compression_ratio", "compression_speed", "quality"],
        "time_range": "day",
        "include_statistics": true
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Algorithm comparison completed successfully",
        "comparison_data": {
            "compression_ratio": {
                "zstandard": 3.2,
                "brotli": 2.8,
                "gzip": 2.5
            },
            "compression_speed": {
                "zstandard": 18.7,
                "brotli": 16.8,
                "gzip": 15.2
            },
            "quality": {
                "zstandard": 92.3,
                "brotli": 91.1,
                "gzip": 89.7
            }
        },
        "statistics": {
            "compression_ratio": {
                "mean": 2.83,
                "median": 2.8,
                "std_dev": 0.35,
                "min": 2.5,
                "max": 3.2
            }
        },
        "rankings": {
            "compression_ratio": [
                {"algorithm": "zstandard", "value": 3.2, "rank": 1},
                {"algorithm": "brotli", "value": 2.8, "rank": 2},
                {"algorithm": "gzip", "value": 2.5, "rank": 3}
            ]
        },
        "recommendations": [
            "zstandard provides the best compression ratio and speed",
            "Consider using brotli for web content due to its quality/speed balance",
            "gzip remains a reliable choice for general-purpose compression"
        ]
    }
    ```
    """
    try:
        # Get evaluation service
        evaluation_service = get_evaluation_service(metrics_collector, compression_engine)
        
        # Perform comparison
        comparison_results = await evaluation_service.compare_algorithms(request)
        
        # Generate recommendations
        recommendations = _generate_comparison_recommendations(comparison_results)
        
        return ComparisonResponse(
            success=True,
            message="Algorithm comparison completed successfully",
            comparison_data=comparison_results,
            statistics=comparison_results.get("statistics"),
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error comparing algorithms: {e}")
        raise HTTPException(status_code=500, detail=f"Error comparing algorithms: {str(e)}")


@router.post("/trends", summary="Analyze Trends", response_model=TrendsResponse)
async def analyze_trends(
    request: TrendsRequest,
    metrics_collector: MetricsCollector = Depends(),
    compression_engine: CompressionEngine = Depends()
) -> TrendsResponse:
    """
    Analyze trends for specified metrics over time.
    
    This endpoint provides trend analysis including direction, strength,
    seasonality detection, and predictions.
    
    **Example Request:**
    ```json
    {
        "metric": "compression_ratio",
        "time_range": "month",
        "granularity": "day",
        "algorithms": ["zstandard", "gzip"]
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Trend analysis completed successfully",
        "trends_data": {
            "metric": "compression_ratio",
            "time_range": "month",
            "granularity": "day",
            "data_points": {
                "2024-01-01T00:00:00": 2.8,
                "2024-01-02T00:00:00": 2.9,
                "2024-01-03T00:00:00": 3.1
            },
            "trend_direction": "increasing",
            "trend_strength": 0.85,
            "seasonality": {
                "detected": true,
                "period": "weekly",
                "strength": 0.45
            },
            "predictions": {
                "next_value": 3.2,
                "confidence": 0.85,
                "trend": "increasing"
            }
        },
        "predictions": {
            "short_term": [3.2, 3.3, 3.4],
            "long_term": [3.5, 3.6, 3.7],
            "confidence_intervals": {
                "lower": [3.0, 3.1, 3.2],
                "upper": [3.4, 3.5, 3.6]
            }
        },
        "insights": [
            "Compression ratio shows a strong upward trend",
            "Weekly seasonality detected with 45% strength",
            "Predicted to reach 3.2 in the next period with 85% confidence"
        ]
    }
    ```
    """
    try:
        # Get evaluation service
        evaluation_service = get_evaluation_service(metrics_collector, compression_engine)
        
        # Analyze trends
        trends_data = await evaluation_service.analyze_trends(request)
        
        # Generate predictions and insights
        predictions = _generate_trend_predictions(trends_data)
        insights = _generate_trend_insights(trends_data)
        
        return TrendsResponse(
            success=True,
            message="Trend analysis completed successfully",
            trends_data=trends_data,
            predictions=predictions,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")


@router.post("/sensor-fusion", summary="Perform Sensor Fusion", response_model=SensorFusionResponse)
async def perform_sensor_fusion(
    request: SensorFusionRequest,
    metrics_collector: MetricsCollector = Depends(),
    compression_engine: CompressionEngine = Depends()
) -> SensorFusionResponse:
    """
    Perform sensor fusion analysis on multiple data sources.
    
    This endpoint combines data from multiple sources to provide
    more accurate and reliable evaluation results.
    
    **Example Request:**
    ```json
    {
        "data_sources": ["compression_metrics", "system_metrics", "quality_metrics"],
        "fusion_method": "ensemble",
        "confidence_threshold": 0.8,
        "include_uncertainty": true
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Sensor fusion analysis completed successfully",
        "fusion_results": {
            "compression_ratio": {
                "mean": 2.85,
                "median": 2.8,
                "std_dev": 0.15,
                "confidence": 0.92
            },
            "quality_score": {
                "mean": 89.5,
                "median": 89.7,
                "std_dev": 2.1,
                "confidence": 0.88
            }
        },
        "confidence_scores": {
            "compression_ratio": 0.92,
            "quality_score": 0.88
        },
        "uncertainty_analysis": {
            "compression_ratio": {
                "variance": 0.0225,
                "coefficient_of_variation": 0.053,
                "range": 0.6,
                "confidence_interval": {
                    "lower": 2.7,
                    "upper": 3.0
                }
            }
        },
        "recommendations": [
            "High confidence in compression ratio measurements",
            "Consider additional data sources for quality score validation",
            "System performance shows stable patterns"
        ]
    }
    ```
    """
    try:
        # Get evaluation service
        evaluation_service = get_evaluation_service(metrics_collector, compression_engine)
        
        # Perform sensor fusion
        fusion_results = await evaluation_service.perform_sensor_fusion(request)
        
        return SensorFusionResponse(
            success=True,
            message="Sensor fusion analysis completed successfully",
            fusion_results=fusion_results["fusion_results"],
            confidence_scores=fusion_results["confidence_scores"],
            uncertainty_analysis=fusion_results.get("uncertainty_analysis"),
            recommendations=fusion_results["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Error performing sensor fusion: {e}")
        raise HTTPException(status_code=500, detail=f"Error performing sensor fusion: {str(e)}")


@router.post("/experiments", summary="Analyze Experiments", response_model=ExperimentsResponse)
async def analyze_experiments(
    request: ExperimentsRequest,
    metrics_collector: MetricsCollector = Depends(),
    compression_engine: CompressionEngine = Depends()
) -> ExperimentsResponse:
    """
    Analyze experimental results and performance improvements.
    
    This endpoint provides comprehensive analysis of experimental data
    including success rates, performance improvements, and innovation metrics.
    
    **Example Request:**
    ```json
    {
        "experiment_types": ["algorithm_evolution", "parameter_optimization"],
        "status": "success",
        "time_range": "month",
        "include_metadata": true
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Experiment analysis completed successfully",
        "experiments_data": {
            "total_experiments": 85,
            "successful_experiments": 78,
            "failed_experiments": 7,
            "experiment_types": {
                "algorithm_evolution": 25,
                "parameter_optimization": 35,
                "meta_learning": 25
            },
            "performance_improvements": {
                "algorithm_evolution": 15.2,
                "parameter_optimization": 8.7
            },
            "innovation_metrics": {
                "success_rate": 0.918,
                "diversity_score": 0.353,
                "improvement_rate": 0.847
            },
            "meta_learning_progress": 0.725
        },
        "metadata": {
            "total_experiments": 85,
            "experiment_types": ["algorithm_evolution", "parameter_optimization", "meta_learning"],
            "date_range": {
                "earliest": "2024-01-01T00:00:00Z",
                "latest": "2024-01-31T23:59:59Z"
            }
        },
        "insights": [
            "91.8% of experiments were successful",
            "Algorithm evolution experiments show the highest improvement rate (15.2%)",
            "Meta-learning progress is at 72.5% completion",
            "Parameter optimization experiments are most common (35 total)"
        ]
    }
    ```
    """
    try:
        # Get evaluation service
        evaluation_service = get_evaluation_service(metrics_collector, compression_engine)
        
        # Analyze experiments
        experiments_data = await evaluation_service.analyze_experiments(request)
        
        # Generate insights
        insights = _generate_experiment_insights(experiments_data)
        
        return ExperimentsResponse(
            success=True,
            message="Experiment analysis completed successfully",
            experiments_data=experiments_data,
            metadata=experiments_data.get("metadata"),
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Error analyzing experiments: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing experiments: {str(e)}")


# Helper functions for generating view data and insights

async def _generate_view_data(view: EvaluationView, metrics: Any, include_details: bool) -> Dict[str, Any]:
    """Generate view-specific data for the evaluation metrics."""
    if view == EvaluationView.OVERVIEW:
        return {
            "overview": {
                "key_metrics": {
                    "performance": metrics.algorithm_performance[0].efficiency if metrics.algorithm_performance else 0,
                    "efficiency": metrics.system_performance.availability,
                    "reliability": metrics.quality_metrics.reliability,
                    "innovation": metrics.experimental_results.innovation_score
                },
                "top_algorithms": [
                    {"name": alg.algorithm_name, "score": alg.efficiency}
                    for alg in sorted(metrics.algorithm_performance, key=lambda x: x.efficiency, reverse=True)[:3]
                ],
                "system_health": {
                    "status": "healthy" if metrics.system_performance.availability > 95 else "warning",
                    "score": metrics.system_performance.availability,
                    "alerts": []
                }
            }
        }
    elif view == EvaluationView.ALGORITHMS:
        return {
            "algorithms": {
                "performance_ranking": [
                    {
                        "name": alg.algorithm_name,
                        "compression_ratio": alg.compression_ratio,
                        "speed": alg.compression_speed,
                        "quality": alg.quality,
                        "efficiency": alg.efficiency
                    }
                    for alg in sorted(metrics.algorithm_performance, key=lambda x: x.efficiency, reverse=True)
                ],
                "statistics": {
                    "total_algorithms": len(metrics.algorithm_performance),
                    "average_efficiency": sum(alg.efficiency for alg in metrics.algorithm_performance) / len(metrics.algorithm_performance),
                    "best_algorithm": max(metrics.algorithm_performance, key=lambda x: x.efficiency).algorithm_name
                }
            }
        }
    else:
        return {"view": view.value, "data": "View-specific data not yet implemented"}


def _generate_comparison_recommendations(comparison_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on comparison results."""
    recommendations = []
    
    # Analyze rankings
    for metric, rankings in comparison_results.get("rankings", {}).items():
        if rankings:
            best_algorithm = rankings[0]["algorithm"]
            best_value = rankings[0]["value"]
            recommendations.append(f"{best_algorithm} provides the best {metric} ({best_value})")
    
    # Analyze performance gaps
    for metric, values in comparison_results.get("comparison_data", {}).items():
        if len(values) > 1:
            max_val = max(values.values())
            min_val = min(values.values())
            gap = max_val - min_val
            if gap > max_val * 0.2:  # 20% gap
                recommendations.append(f"Significant performance gap in {metric} ({gap:.2f})")
    
    return recommendations


def _generate_trend_predictions(trends_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate predictions based on trend data."""
    predictions = trends_data.get("predictions", {})
    
    # Generate short-term predictions
    if predictions.get("next_value"):
        current_value = predictions["next_value"]
        trend = predictions.get("trend", "stable")
        
        short_term = []
        for i in range(1, 4):
            if trend == "increasing":
                short_term.append(current_value + (i * 0.1))
            elif trend == "decreasing":
                short_term.append(current_value - (i * 0.1))
            else:
                short_term.append(current_value)
        
        return {
            "short_term": short_term,
            "long_term": [current_value + (i * 0.2) for i in range(1, 4)] if trend == "increasing" else [current_value - (i * 0.2) for i in range(1, 4)],
            "confidence_intervals": {
                "lower": [v * 0.95 for v in short_term],
                "upper": [v * 1.05 for v in short_term]
            }
        }
    
    return {}


def _generate_trend_insights(trends_data: Dict[str, Any]) -> List[str]:
    """Generate insights from trend analysis."""
    insights = []
    
    # Trend direction insights
    direction = trends_data.get("trend_direction", "stable")
    strength = trends_data.get("trend_strength", 0)
    metric = trends_data.get("metric", "metric")
    
    if direction == "increasing" and strength > 0.7:
        insights.append(f"{metric} shows a strong upward trend")
    elif direction == "decreasing" and strength > 0.7:
        insights.append(f"{metric} shows a strong downward trend")
    elif strength < 0.3:
        insights.append(f"{metric} shows minimal trend variation")
    
    # Seasonality insights
    seasonality = trends_data.get("seasonality", {})
    if seasonality.get("detected"):
        period = seasonality.get("period", "unknown")
        strength = seasonality.get("strength", 0)
        insights.append(f"Seasonal pattern detected with {period} periodicity ({strength:.1%} strength)")
    
    # Prediction insights
    predictions = trends_data.get("predictions", {})
    if predictions.get("next_value"):
        next_value = predictions["next_value"]
        confidence = predictions.get("confidence", 0)
        insights.append(f"Predicted to reach {next_value:.2f} in the next period with {confidence:.1%} confidence")
    
    return insights


def _generate_experiment_insights(experiments_data: Dict[str, Any]) -> List[str]:
    """Generate insights from experiment analysis."""
    insights = []
    
    # Success rate insights
    total = experiments_data.get("total_experiments", 0)
    successful = experiments_data.get("successful_experiments", 0)
    if total > 0:
        success_rate = successful / total
        insights.append(f"{success_rate:.1%} of experiments were successful")
    
    # Performance improvement insights
    improvements = experiments_data.get("performance_improvements", {})
    if improvements:
        best_improvement = max(improvements.items(), key=lambda x: x[1])
        insights.append(f"{best_improvement[0]} experiments show the highest improvement rate ({best_improvement[1]:.1f}%)")
    
    # Meta-learning insights
    meta_learning_progress = experiments_data.get("meta_learning_progress", 0)
    insights.append(f"Meta-learning progress is at {meta_learning_progress:.1%} completion")
    
    # Experiment type insights
    experiment_types = experiments_data.get("experiment_types", {})
    if experiment_types:
        most_common = max(experiment_types.items(), key=lambda x: x[1])
        insights.append(f"{most_common[0]} experiments are most common ({most_common[1]} total)")
    
    return insights
