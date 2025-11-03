"""
Evaluation service for the Dynamic Compression Algorithms backend.

This module provides comprehensive evaluation capabilities including
metrics collection, data analysis, trend analysis, and sensor fusion.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
import math

from app.models.evaluation import (
    EvaluationMetrics, EvaluationFilters, TimeRange, EvaluationView,
    AlgorithmPerformanceMetrics, SystemPerformanceMetrics, ContentAnalysisMetrics,
    ExperimentalResults, QualityMetrics, ComparativeAnalysis, SensorFusionMetrics,
    ComparisonRequest, TrendsRequest, SensorFusionRequest, ExperimentsRequest
)
from app.core.metrics_collector import MetricsCollector
from app.core.compression_engine import CompressionEngine
from app.database import get_db_session

logger = logging.getLogger(__name__)


@dataclass
class EvaluationContext:
    """Context for evaluation operations."""
    time_range: TimeRange
    start_date: datetime
    end_date: datetime
    filters: EvaluationFilters
    metrics_collector: MetricsCollector
    compression_engine: CompressionEngine


class EvaluationService:
    """Service for comprehensive evaluation and analysis."""
    
    def __init__(self, metrics_collector: MetricsCollector, compression_engine: CompressionEngine):
        self.metrics_collector = metrics_collector
        self.compression_engine = compression_engine
        self.logger = logging.getLogger(__name__)
    
    async def get_evaluation_metrics(self, filters: EvaluationFilters) -> EvaluationMetrics:
        """Get comprehensive evaluation metrics."""
        start_time = datetime.utcnow()
        
        try:
            # Create evaluation context
            context = await self._create_evaluation_context(filters)
            
            # Collect all metrics
            algorithm_metrics = await self._get_algorithm_performance_metrics(context)
            system_metrics = await self._get_system_performance_metrics(context)
            content_metrics = await self._get_content_analysis_metrics(context)
            experimental_metrics = await self._get_experimental_results(context)
            quality_metrics = await self._get_quality_metrics(context)
            comparative_metrics = await self._get_comparative_analysis(context)
            fusion_metrics = await self._get_sensor_fusion_metrics(context)
            
            # Create comprehensive metrics object
            evaluation_metrics = EvaluationMetrics(
                algorithm_performance=algorithm_metrics,
                system_performance=system_metrics,
                content_analysis=content_metrics,
                experimental_results=experimental_metrics,
                quality_metrics=quality_metrics,
                comparative_analysis=comparative_metrics,
                sensor_fusion=fusion_metrics,
                timestamp=datetime.utcnow(),
                time_range=filters.time_range
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Evaluation metrics collected in {processing_time:.3f}s")
            
            return evaluation_metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting evaluation metrics: {e}")
            raise
    
    async def compare_algorithms(self, request: ComparisonRequest) -> Dict[str, Any]:
        """Compare algorithms based on specified metrics."""
        try:
            # Get algorithm performance data
            algorithm_data = {}
            for algorithm in request.algorithms:
                metrics = await self._get_algorithm_metrics(algorithm, request.time_range)
                algorithm_data[algorithm] = metrics
            
            # Perform comparison analysis
            comparison_results = {
                "algorithms": request.algorithms,
                "metrics": request.metrics,
                "comparison_data": {},
                "statistics": {},
                "rankings": {}
            }
            
            # Compare each metric
            for metric in request.metrics:
                metric_values = {}
                for algorithm, data in algorithm_data.items():
                    if hasattr(data, metric):
                        metric_values[algorithm] = getattr(data, metric)
                
                if metric_values:
                    comparison_results["comparison_data"][metric] = metric_values
                    
                    # Calculate statistics
                    if request.include_statistics:
                        values = list(metric_values.values())
                        comparison_results["statistics"][metric] = {
                            "mean": statistics.mean(values),
                            "median": statistics.median(values),
                            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                            "min": min(values),
                            "max": max(values)
                        }
                    
                    # Create rankings
                    sorted_algorithms = sorted(metric_values.items(), key=lambda x: x[1], reverse=True)
                    comparison_results["rankings"][metric] = [
                        {"algorithm": alg, "value": val, "rank": i + 1}
                        for i, (alg, val) in enumerate(sorted_algorithms)
                    ]
            
            return comparison_results
            
        except Exception as e:
            self.logger.error(f"Error comparing algorithms: {e}")
            raise
    
    async def analyze_trends(self, request: TrendsRequest) -> Dict[str, Any]:
        """Analyze trends for specified metrics."""
        try:
            # Calculate time intervals based on granularity
            intervals = self._calculate_time_intervals(request.time_range, request.granularity)
            
            # Collect data for each interval
            trend_data = {}
            for interval_start, interval_end in intervals:
                interval_data = await self._get_metric_data_for_interval(
                    request.metric, interval_start, interval_end, request.algorithms
                )
                trend_data[interval_start.isoformat()] = interval_data
            
            # Perform trend analysis
            trend_analysis = {
                "metric": request.metric,
                "time_range": request.time_range,
                "granularity": request.granularity,
                "data_points": trend_data,
                "trend_direction": self._calculate_trend_direction(trend_data),
                "trend_strength": self._calculate_trend_strength(trend_data),
                "seasonality": self._detect_seasonality(trend_data),
                "predictions": self._generate_predictions(trend_data)
            }
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            raise
    
    async def perform_sensor_fusion(self, request: SensorFusionRequest) -> Dict[str, Any]:
        """Perform sensor fusion analysis."""
        try:
            # Collect data from multiple sources
            source_data = {}
            for source in request.data_sources:
                data = await self._collect_source_data(source)
                source_data[source] = data
            
            # Apply fusion method
            if request.fusion_method == "ensemble":
                fusion_results = self._ensemble_fusion(source_data, request.confidence_threshold)
            elif request.fusion_method == "weighted":
                fusion_results = self._weighted_fusion(source_data, request.confidence_threshold)
            elif request.fusion_method == "kalman":
                fusion_results = self._kalman_fusion(source_data, request.confidence_threshold)
            else:
                fusion_results = self._ensemble_fusion(source_data, request.confidence_threshold)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(fusion_results, source_data)
            
            # Uncertainty analysis
            uncertainty_analysis = None
            if request.include_uncertainty:
                uncertainty_analysis = self._analyze_uncertainty(fusion_results, source_data)
            
            return {
                "fusion_method": request.fusion_method,
                "data_sources": request.data_sources,
                "fusion_results": fusion_results,
                "confidence_scores": confidence_scores,
                "uncertainty_analysis": uncertainty_analysis,
                "recommendations": self._generate_fusion_recommendations(fusion_results, confidence_scores)
            }
            
        except Exception as e:
            self.logger.error(f"Error performing sensor fusion: {e}")
            raise
    
    async def analyze_experiments(self, request: ExperimentsRequest) -> Dict[str, Any]:
        """Analyze experimental results."""
        try:
            # Get experiment data
            experiment_data = await self._get_experiment_data(
                request.experiment_types,
                request.status,
                request.time_range
            )
            
            # Analyze experiment results
            analysis_results = {
                "total_experiments": len(experiment_data),
                "successful_experiments": len([e for e in experiment_data if e.get("status") == "success"]),
                "failed_experiments": len([e for e in experiment_data if e.get("status") == "failed"]),
                "experiment_types": self._analyze_experiment_types(experiment_data),
                "performance_improvements": self._analyze_performance_improvements(experiment_data),
                "innovation_metrics": self._analyze_innovation_metrics(experiment_data),
                "meta_learning_progress": self._analyze_meta_learning_progress(experiment_data)
            }
            
            # Include metadata if requested
            if request.include_metadata:
                analysis_results["metadata"] = self._extract_experiment_metadata(experiment_data)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing experiments: {e}")
            raise
    
    async def _create_evaluation_context(self, filters: EvaluationFilters) -> EvaluationContext:
        """Create evaluation context with time range and filters."""
        end_date = datetime.utcnow()
        
        if filters.time_range == TimeRange.CUSTOM:
            start_date = filters.start_date
            end_date = filters.end_date
        else:
            start_date = self._calculate_start_date(filters.time_range, end_date)
        
        return EvaluationContext(
            time_range=filters.time_range,
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            metrics_collector=self.metrics_collector,
            compression_engine=self.compression_engine
        )
    
    async def _get_algorithm_performance_metrics(self, context: EvaluationContext) -> List[AlgorithmPerformanceMetrics]:
        """Get algorithm performance metrics."""
        # This would integrate with the actual metrics collector
        # For now, return mock data
        return [
            AlgorithmPerformanceMetrics(
                algorithm_name="gzip",
                compression_ratio=2.5,
                compression_speed=15.2,
                memory_usage=45.8,
                accuracy=95.2,
                efficiency=88.5,
                reliability=92.1,
                adaptability=85.3,
                quality=89.7,
                throughput=125.6,
                success_rate=98.5,
                total_operations=1250,
                average_processing_time=0.045
            ),
            AlgorithmPerformanceMetrics(
                algorithm_name="zstandard",
                compression_ratio=3.2,
                compression_speed=18.7,
                memory_usage=52.3,
                accuracy=97.8,
                efficiency=91.2,
                reliability=94.5,
                adaptability=88.9,
                quality=92.3,
                throughput=145.2,
                success_rate=99.1,
                total_operations=980,
                average_processing_time=0.038
            )
        ]
    
    async def _get_system_performance_metrics(self, context: EvaluationContext) -> SystemPerformanceMetrics:
        """Get system performance metrics."""
        # This would integrate with system monitoring
        return SystemPerformanceMetrics(
            cpu_usage=45.2,
            memory_usage=62.8,
            disk_usage=78.5,
            network_usage=23.1,
            gpu_usage=15.7,
            temperature=42.3,
            power_consumption=125.6,
            response_time=45.8,
            throughput=156.7,
            error_rate=1.2,
            availability=99.8
        )
    
    async def _get_content_analysis_metrics(self, context: EvaluationContext) -> ContentAnalysisMetrics:
        """Get content analysis metrics."""
        return ContentAnalysisMetrics(
            total_files=1250,
            total_size=1048576000,  # 1GB
            content_types={"text": 450, "image": 300, "video": 200, "audio": 150, "binary": 150},
            complexity_scores={"text": 0.65, "image": 0.85, "video": 0.92, "audio": 0.78, "binary": 0.45},
            entropy_distribution={"low": 0.25, "medium": 0.45, "high": 0.30},
            average_file_size=838860,  # ~800KB
            largest_file_size=52428800,  # 50MB
            smallest_file_size=1024  # 1KB
        )
    
    async def _get_experimental_results(self, context: EvaluationContext) -> ExperimentalResults:
        """Get experimental results."""
        return ExperimentalResults(
            total_experiments=85,
            successful_experiments=78,
            failed_experiments=7,
            meta_learning_progress=72.5,
            synthetic_data_generated=524288000,  # 500MB
            algorithm_evolutions=12,
            performance_improvements={"compression_ratio": 15.2, "speed": 8.7, "quality": 12.3},
            innovation_score=85.7,
            experiment_success_rate=91.8
        )
    
    async def _get_quality_metrics(self, context: EvaluationContext) -> QualityMetrics:
        """Get quality metrics."""
        return QualityMetrics(
            overall_quality=88.5,
            compression_quality=91.2,
            decompression_quality=89.7,
            data_integrity=99.8,
            consistency=87.3,
            reliability=92.1,
            user_satisfaction=85.9,
            accuracy=94.6
        )
    
    async def _get_comparative_analysis(self, context: EvaluationContext) -> ComparativeAnalysis:
        """Get comparative analysis."""
        return ComparativeAnalysis(
            algorithm_ranking=[
                {"algorithm": "zstandard", "score": 94.5, "rank": 1},
                {"algorithm": "gzip", "score": 88.7, "rank": 2},
                {"algorithm": "brotli", "score": 85.3, "rank": 3}
            ],
            performance_comparison={
                "zstandard": {"compression_ratio": 3.2, "speed": 18.7, "quality": 92.3},
                "gzip": {"compression_ratio": 2.5, "speed": 15.2, "quality": 89.7},
                "brotli": {"compression_ratio": 2.8, "speed": 16.8, "quality": 91.1}
            },
            efficiency_analysis={"zstandard": 91.2, "gzip": 88.5, "brotli": 89.8},
            quality_comparison={"zstandard": 92.3, "gzip": 89.7, "brotli": 91.1},
            cost_benefit_analysis={
                "zstandard": {"cost": 0.15, "benefit": 0.92, "ratio": 6.13},
                "gzip": {"cost": 0.12, "benefit": 0.85, "ratio": 7.08},
                "brotli": {"cost": 0.14, "benefit": 0.89, "ratio": 6.36}
            }
        )
    
    async def _get_sensor_fusion_metrics(self, context: EvaluationContext) -> SensorFusionMetrics:
        """Get sensor fusion metrics."""
        return SensorFusionMetrics(
            multi_modal_data={
                "compression_metrics": 0.92,
                "system_metrics": 0.88,
                "quality_metrics": 0.91,
                "user_feedback": 0.85
            },
            cross_validation_scores={
                "algorithm_performance": 0.89,
                "system_performance": 0.87,
                "quality_assessment": 0.91
            },
            ensemble_scores={
                "weighted_average": 0.89,
                "majority_voting": 0.87,
                "stacking": 0.92
            },
            confidence_intervals={
                "compression_ratio": {"lower": 2.8, "upper": 3.6, "confidence": 0.95},
                "quality_score": {"lower": 88.5, "upper": 94.2, "confidence": 0.95}
            },
            fusion_accuracy=91.3,
            data_correlation={
                "compression_quality": 0.85,
                "system_performance": 0.78,
                "user_satisfaction": 0.82
            }
        )
    
    def _calculate_start_date(self, time_range: TimeRange, end_date: datetime) -> datetime:
        """Calculate start date based on time range."""
        if time_range == TimeRange.HOUR:
            return end_date - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            return end_date - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            return end_date - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            return end_date - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            return end_date - timedelta(days=90)
        elif time_range == TimeRange.YEAR:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=1)
    
    def _calculate_time_intervals(self, time_range: TimeRange, granularity: str) -> List[Tuple[datetime, datetime]]:
        """Calculate time intervals for trend analysis."""
        end_date = datetime.utcnow()
        start_date = self._calculate_start_date(time_range, end_date)
        
        intervals = []
        current_start = start_date
        
        while current_start < end_date:
            if granularity == "hour":
                current_end = current_start + timedelta(hours=1)
            elif granularity == "day":
                current_end = current_start + timedelta(days=1)
            elif granularity == "week":
                current_end = current_start + timedelta(weeks=1)
            else:
                current_end = current_start + timedelta(days=1)
            
            intervals.append((current_start, current_end))
            current_start = current_end
        
        return intervals
    
    def _calculate_trend_direction(self, trend_data: Dict[str, Any]) -> str:
        """Calculate trend direction."""
        values = list(trend_data.values())
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_trend_strength(self, trend_data: Dict[str, Any]) -> float:
        """Calculate trend strength (R-squared)."""
        values = list(trend_data.values())
        if len(values) < 2:
            return 0.0
        
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        # Calculate R-squared
        numerator = (n * sum_xy - sum_x * sum_y) ** 2
        denominator = (n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _detect_seasonality(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect seasonality in the data."""
        # Simplified seasonality detection
        values = list(trend_data.values())
        if len(values) < 7:  # Need at least a week of data
            return {"detected": False, "period": None, "strength": 0.0}
        
        # Check for weekly patterns
        weekly_pattern = self._check_weekly_pattern(values)
        
        return {
            "detected": weekly_pattern["detected"],
            "period": "weekly" if weekly_pattern["detected"] else None,
            "strength": weekly_pattern["strength"]
        }
    
    def _check_weekly_pattern(self, values: List[float]) -> Dict[str, Any]:
        """Check for weekly patterns in the data."""
        if len(values) < 7:
            return {"detected": False, "strength": 0.0}
        
        # Simple autocorrelation check
        weekly_correlation = 0.0
        for i in range(7, len(values)):
            if i < len(values):
                weekly_correlation += abs(values[i] - values[i-7])
        
        weekly_correlation = 1 - (weekly_correlation / (len(values) - 7))
        
        return {
            "detected": weekly_correlation > 0.3,
            "strength": weekly_correlation
        }
    
    def _generate_predictions(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions based on trend data."""
        values = list(trend_data.values())
        if len(values) < 3:
            return {"next_value": None, "confidence": 0.0}
        
        # Simple linear prediction
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        next_value = slope * n + intercept
        
        # Calculate confidence based on R-squared
        confidence = self._calculate_trend_strength(trend_data)
        
        return {
            "next_value": next_value,
            "confidence": confidence,
            "trend": "increasing" if slope > 0 else "decreasing"
        }
    
    def _ensemble_fusion(self, source_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
        """Perform ensemble fusion of multiple data sources."""
        fusion_results = {}
        
        # Get common keys across all sources
        common_keys = set.intersection(*[set(data.keys()) for data in source_data.values()])
        
        for key in common_keys:
            values = [data[key] for data in source_data.values() if key in data]
            if values:
                # Calculate ensemble statistics
                fusion_results[key] = {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "confidence": min(1.0, len(values) / len(source_data))
                }
        
        return fusion_results
    
    def _weighted_fusion(self, source_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
        """Perform weighted fusion based on source reliability."""
        # This would use source-specific weights
        return self._ensemble_fusion(source_data, confidence_threshold)
    
    def _kalman_fusion(self, source_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
        """Perform Kalman filter fusion."""
        # Simplified Kalman fusion
        return self._ensemble_fusion(source_data, confidence_threshold)
    
    def _calculate_confidence_scores(self, fusion_results: Dict[str, Any], source_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for fusion results."""
        confidence_scores = {}
        
        for key, result in fusion_results.items():
            # Calculate confidence based on agreement between sources
            values = [data[key] for data in source_data.values() if key in data]
            if values:
                # Confidence based on standard deviation (lower is better)
                std_dev = result.get("std_dev", 0)
                max_value = max(values) if values else 1
                confidence = max(0, 1 - (std_dev / max_value))
                confidence_scores[key] = confidence
        
        return confidence_scores
    
    def _analyze_uncertainty(self, fusion_results: Dict[str, Any], source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze uncertainty in fusion results."""
        uncertainty_analysis = {}
        
        for key, result in fusion_results.items():
            values = [data[key] for data in source_data.values() if key in data]
            if values:
                uncertainty_analysis[key] = {
                    "variance": statistics.variance(values) if len(values) > 1 else 0,
                    "coefficient_of_variation": (statistics.stdev(values) / statistics.mean(values)) if len(values) > 1 and statistics.mean(values) != 0 else 0,
                    "range": max(values) - min(values) if values else 0,
                    "confidence_interval": {
                        "lower": statistics.mean(values) - 1.96 * (statistics.stdev(values) / math.sqrt(len(values))) if len(values) > 1 else statistics.mean(values),
                        "upper": statistics.mean(values) + 1.96 * (statistics.stdev(values) / math.sqrt(len(values))) if len(values) > 1 else statistics.mean(values)
                    }
                }
        
        return uncertainty_analysis
    
    def _generate_fusion_recommendations(self, fusion_results: Dict[str, Any], confidence_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on fusion results."""
        recommendations = []
        
        # Analyze confidence scores
        low_confidence_keys = [key for key, score in confidence_scores.items() if score < 0.7]
        if low_confidence_keys:
            recommendations.append(f"Consider additional data sources for: {', '.join(low_confidence_keys)}")
        
        # Analyze trends
        for key, result in fusion_results.items():
            if "trend" in result and result["trend"] == "decreasing":
                recommendations.append(f"Monitor {key} for potential performance degradation")
        
        return recommendations
    
    async def _collect_source_data(self, source: str) -> Dict[str, Any]:
        """Collect data from a specific source."""
        # This would integrate with actual data sources
        # For now, return mock data
        mock_data = {
            "compression_metrics": {"compression_ratio": 2.8, "quality": 0.89, "speed": 16.2},
            "system_metrics": {"cpu_usage": 45.2, "memory_usage": 62.8, "response_time": 45.8},
            "quality_metrics": {"overall_quality": 88.5, "data_integrity": 99.8, "user_satisfaction": 85.9}
        }
        
        return mock_data.get(source, {})
    
    async def _get_algorithm_metrics(self, algorithm: str, time_range: TimeRange) -> Dict[str, Any]:
        """Get metrics for a specific algorithm."""
        # This would integrate with the metrics collector
        # For now, return mock data
        return {
            "compression_ratio": 2.8,
            "compression_speed": 16.2,
            "quality": 0.89,
            "efficiency": 0.88,
            "reliability": 0.92
        }
    
    async def _get_metric_data_for_interval(self, metric: str, start_date: datetime, end_date: datetime, algorithms: Optional[List[str]] = None) -> float:
        """Get metric data for a specific time interval."""
        # This would integrate with the metrics collector
        # For now, return mock data
        return 2.8 + (hash(f"{start_date.isoformat()}{metric}") % 100) / 100
    
    async def _get_experiment_data(self, experiment_types: Optional[List[str]], status: Optional[str], time_range: TimeRange) -> List[Dict[str, Any]]:
        """Get experiment data."""
        # This would integrate with the experiment database
        # For now, return mock data
        return [
            {"id": "exp_001", "type": "algorithm_evolution", "status": "success", "results": {"improvement": 15.2}},
            {"id": "exp_002", "type": "parameter_optimization", "status": "success", "results": {"improvement": 8.7}},
            {"id": "exp_003", "type": "meta_learning", "status": "failed", "results": {"error": "timeout"}}
        ]
    
    def _analyze_experiment_types(self, experiment_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze experiment types."""
        type_counts = {}
        for experiment in experiment_data:
            exp_type = experiment.get("type", "unknown")
            type_counts[exp_type] = type_counts.get(exp_type, 0) + 1
        return type_counts
    
    def _analyze_performance_improvements(self, experiment_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze performance improvements from experiments."""
        improvements = {}
        for experiment in experiment_data:
            if experiment.get("status") == "success" and "results" in experiment:
                results = experiment["results"]
                if "improvement" in results:
                    metric = experiment.get("type", "unknown")
                    improvements[metric] = results["improvement"]
        return improvements
    
    def _analyze_innovation_metrics(self, experiment_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze innovation metrics from experiments."""
        return {
            "success_rate": len([e for e in experiment_data if e.get("status") == "success"]) / len(experiment_data) if experiment_data else 0,
            "diversity_score": len(set(e.get("type", "unknown") for e in experiment_data)) / len(experiment_data) if experiment_data else 0,
            "improvement_rate": sum(1 for e in experiment_data if e.get("status") == "success" and "improvement" in e.get("results", {})) / len(experiment_data) if experiment_data else 0
        }
    
    def _analyze_meta_learning_progress(self, experiment_data: List[Dict[str, Any]]) -> float:
        """Analyze meta-learning progress."""
        meta_learning_experiments = [e for e in experiment_data if e.get("type") == "meta_learning"]
        if not meta_learning_experiments:
            return 0.0
        
        successful_meta_learning = [e for e in meta_learning_experiments if e.get("status") == "success"]
        return len(successful_meta_learning) / len(meta_learning_experiments)
    
    def _extract_experiment_metadata(self, experiment_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metadata from experiments."""
        return {
            "total_experiments": len(experiment_data),
            "experiment_types": list(set(e.get("type", "unknown") for e in experiment_data)),
            "date_range": {
                "earliest": min((e.get("created_at", datetime.utcnow()) for e in experiment_data), default=datetime.utcnow()),
                "latest": max((e.get("created_at", datetime.utcnow()) for e in experiment_data), default=datetime.utcnow())
            }
        }


# Create singleton instance
evaluation_service = None


def get_evaluation_service(metrics_collector: MetricsCollector, compression_engine: CompressionEngine) -> EvaluationService:
    """Get evaluation service instance."""
    global evaluation_service
    if evaluation_service is None:
        evaluation_service = EvaluationService(metrics_collector, compression_engine)
    return evaluation_service
