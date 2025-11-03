"""
Metrics collector for the Dynamic Compression Algorithms backend.

This module implements comprehensive metrics collection and analysis
for compression performance, quality, and system monitoring.
"""

import time
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime
# import numpy as np  # Removed for compatibility

from app.models.metrics import (
    CompressionMetrics, PerformanceMetrics, QualityMetrics,
    AlgorithmMetrics, MetricsAggregation, MetricType, TimeRange
)


class MetricsCollector:
    """
    Metrics collector that implements comprehensive performance monitoring.
    
    Collects and analyzes metrics for:
    - Compression performance (ratio, speed, memory usage)
    - Quality metrics (information preservation, fidelity)
    - System performance (CPU, memory, disk usage)
    - Algorithm-specific metrics
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics_history = []
        self.algorithm_metrics = {}
        self.system_metrics = []
        
        # Performance thresholds
        self.thresholds = {
            'compression_ratio_min': 1.0,
            'compression_speed_min': 1.0,  # MB/s
            'memory_usage_max': 1024 * 1024 * 1024,  # 1GB
            'cpu_usage_max': 80.0,  # 80%
            'quality_score_min': 0.8
        }
    
    def collect_compression_metrics(self, 
                                  original_size: int,
                                  compressed_size: int,
                                  compression_time: float,
                                  decompression_time: Optional[float] = None,
                                  memory_usage: Optional[int] = None,
                                  cpu_usage: Optional[float] = None,
                                  algorithm: str = "unknown",
                                  parameters: Dict[str, Any] = None) -> CompressionMetrics:
        """
        Collect compression performance metrics.
        
        Args:
            original_size: Original data size in bytes
            compressed_size: Compressed data size in bytes
            compression_time: Compression time in seconds
            decompression_time: Decompression time in seconds
            memory_usage: Memory usage in bytes
            cpu_usage: CPU usage percentage
            algorithm: Algorithm used
            parameters: Parameters used
            
        Returns:
            CompressionMetrics object
        """
        # Calculate basic metrics
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        compression_percentage = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0.0
        
        # Calculate speed metrics
        compression_speed = (original_size / 1024 / 1024) / compression_time if compression_time > 0 else 0.0
        decompression_speed = None
        if decompression_time and decompression_time > 0:
            decompression_speed = (compressed_size / 1024 / 1024) / decompression_time
        
        # Get system metrics if not provided
        if memory_usage is None:
            memory_usage = self._get_current_memory_usage()
        
        if cpu_usage is None:
            cpu_usage = self._get_current_cpu_usage()
        
        # Create metrics object
        metrics = CompressionMetrics(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compression_percentage=compression_percentage,
            compression_time=compression_time,
            compression_speed=compression_speed,
            decompression_time=decompression_time,
            decompression_speed=decompression_speed,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            quality_score=self._calculate_quality_score(compression_ratio, compression_speed, cpu_usage),
            information_preservation=self._calculate_information_preservation(original_size, compressed_size),
            round_trip_integrity=decompression_time is not None,
            entropy_reduction=self._calculate_entropy_reduction(original_size, compressed_size),
            pattern_efficiency=self._calculate_pattern_efficiency(compression_ratio, compression_time),
            algorithm_efficiency=self._calculate_algorithm_efficiency(algorithm, compression_ratio, compression_time)
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        
        # Update algorithm-specific metrics
        self._update_algorithm_metrics(algorithm, metrics, parameters)
        
        return metrics
    
    def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics."""
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Calculate application metrics
        active_connections = len(psutil.net_connections())
        requests_per_second = self._calculate_requests_per_second()
        average_response_time = self._calculate_average_response_time()
        error_rate = self._calculate_error_rate()
        
        # Queue metrics (simplified)
        queue_size = 0  # Would be actual queue size in real implementation
        queue_processing_rate = requests_per_second
        average_wait_time = average_response_time
        
        metrics = PerformanceMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_usage=self._get_network_usage(),
            active_connections=active_connections,
            requests_per_second=requests_per_second,
            average_response_time=average_response_time,
            error_rate=error_rate,
            queue_size=queue_size,
            queue_processing_rate=queue_processing_rate,
            average_wait_time=average_wait_time
        )
        
        # Store system metrics
        self.system_metrics.append(metrics)
        
        return metrics
    
    def collect_quality_metrics(self, 
                              original_content: str,
                              decompressed_content: str,
                              compression_algorithm: str) -> QualityMetrics:
        """
        Collect quality assessment metrics.
        
        Args:
            original_content: Original content
            decompressed_content: Decompressed content
            compression_algorithm: Algorithm used
            
        Returns:
            QualityMetrics object
        """
        # Calculate content integrity
        content_integrity = 1.0 if original_content == decompressed_content else 0.0
        
        # Calculate semantic preservation (simplified)
        semantic_preservation = self._calculate_semantic_preservation(original_content, decompressed_content)
        
        # Calculate structural integrity
        structural_integrity = self._calculate_structural_integrity(original_content, decompressed_content)
        
        # Calculate loss ratio
        loss_ratio = 1.0 - content_integrity
        
        # Calculate distortion measure
        distortion_measure = self._calculate_distortion_measure(original_content, decompressed_content)
        
        # Calculate fidelity score
        fidelity_score = self._calculate_fidelity_score(content_integrity, semantic_preservation, structural_integrity)
        
        # Domain-specific quality scores
        text_quality = self._calculate_text_quality(original_content, decompressed_content)
        code_quality = self._calculate_code_quality(original_content, decompressed_content)
        binary_quality = self._calculate_binary_quality(original_content, decompressed_content)
        
        # Validation
        validation_passed = content_integrity > 0.95
        validation_errors = [] if validation_passed else ["Content integrity below threshold"]
        
        metrics = QualityMetrics(
            content_integrity=content_integrity,
            semantic_preservation=semantic_preservation,
            structural_integrity=structural_integrity,
            loss_ratio=loss_ratio,
            distortion_measure=distortion_measure,
            fidelity_score=fidelity_score,
            text_quality=text_quality,
            code_quality=code_quality,
            binary_quality=binary_quality,
            validation_passed=validation_passed,
            validation_errors=validation_errors
        )
        
        return metrics
    
    def get_algorithm_metrics(self, algorithm: str) -> Optional[AlgorithmMetrics]:
        """Get metrics for a specific algorithm."""
        return self.algorithm_metrics.get(algorithm)
    
    def get_metrics_summary(self, time_range: TimeRange = TimeRange.DAY) -> Dict[str, Any]:
        """Get summary of metrics for the specified time range."""
        # Filter metrics by time range
        cutoff_time = self._get_cutoff_time(time_range)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return self._empty_summary()
        
        # Calculate summary statistics
        summary = {
            'total_compressions': len(recent_metrics),
                    'average_compression_ratio': self._mean([m.compression_ratio for m in recent_metrics]),
        'average_compression_speed': self._mean([m.compression_speed for m in recent_metrics]),
        'average_compression_time': self._mean([m.compression_time for m in recent_metrics]),
        'average_quality_score': self._mean([m.quality_score for m in recent_metrics if m.quality_score]),
            'best_algorithm': self._get_best_algorithm(recent_metrics),
            'total_data_processed': sum([m.original_size for m in recent_metrics]),
            'total_data_saved': sum([m.original_size - m.compressed_size for m in recent_metrics]),
            'time_range': time_range.value
        }
        
        return summary
    
    def aggregate_metrics(self, 
                         metric_type: MetricType,
                         time_range: TimeRange,
                         start_time: datetime,
                         end_time: datetime,
                         algorithm_filter: Optional[str] = None,
                         content_type_filter: Optional[str] = None) -> MetricsAggregation:
        """Aggregate metrics for analysis."""
        # Filter metrics by time range and filters
        filtered_metrics = self._filter_metrics(
            start_time, end_time, algorithm_filter, content_type_filter
        )
        
        if not filtered_metrics:
            return self._empty_aggregation(metric_type, time_range, start_time, end_time)
        
        # Extract values for the specified metric type
        values = self._extract_metric_values(filtered_metrics, metric_type)
        
        # Calculate aggregation statistics
        aggregation = MetricsAggregation(
            metric_type=metric_type,
            time_range=time_range,
            start_time=start_time,
            end_time=end_time,
            count=len(values),
            min_value=min(values) if values else 0.0,
            max_value=max(values) if values else 0.0,
            mean_value=self._mean(values) if values else 0.0,
            median_value=self._median(values) if values else 0.0,
            std_deviation=self._std(values) if values else 0.0,
            p25=self._percentile(values, 25) if values else 0.0,
            p75=self._percentile(values, 75) if values else 0.0,
            p90=self._percentile(values, 90) if values else 0.0,
            p95=self._percentile(values, 95) if values else 0.0,
            p99=self._percentile(values, 99) if values else 0.0,
            total_value=sum(values) if values else 0.0,
            variance=self._variance(values) if values else 0.0,
            algorithm_filter=algorithm_filter,
            content_type_filter=content_type_filter
        )
        
        return aggregation
    
    def _calculate_quality_score(self, compression_ratio: float, compression_speed: float, cpu_usage: float) -> float:
        """Calculate overall quality score."""
        # Normalize metrics
        ratio_score = min(compression_ratio / 10.0, 1.0)  # Cap at 10x compression
        speed_score = min(compression_speed / 100.0, 1.0)  # Cap at 100 MB/s
        cpu_score = 1.0 - (cpu_usage / 100.0)  # Lower CPU usage is better
        
        # Weighted combination
        quality_score = (
            ratio_score * 0.4 +
            speed_score * 0.3 +
            cpu_score * 0.3
        )
        
        return quality_score
    
    def _calculate_information_preservation(self, original_size: int, compressed_size: int) -> float:
        """Calculate information preservation ratio."""
        # Simplified calculation - in reality would be more complex
        if original_size == 0:
            return 0.0
        
        # Assume some information loss based on compression ratio
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        preservation = 1.0 - (1.0 / compression_ratio) * 0.1  # Small loss factor
        
        return max(0.0, min(1.0, preservation))
    
    def _calculate_entropy_reduction(self, original_size: int, compressed_size: int) -> float:
        """Calculate entropy reduction achieved."""
        if original_size == 0:
            return 0.0
        
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        # Simplified entropy reduction calculation
        entropy_reduction = (compression_ratio - 1.0) / compression_ratio
        
        return max(0.0, entropy_reduction)
    
    def _calculate_pattern_efficiency(self, compression_ratio: float, compression_time: float) -> float:
        """Calculate pattern detection efficiency."""
        # Simplified efficiency calculation
        if compression_time == 0:
            return 0.0
        
        # Efficiency based on compression ratio achieved per unit time
        efficiency = compression_ratio / compression_time
        
        # Normalize to [0, 1] range
        return min(efficiency / 10.0, 1.0)  # Cap at 10x compression per second
    
    def _calculate_algorithm_efficiency(self, algorithm: str, compression_ratio: float, compression_time: float) -> float:
        """Calculate algorithm-specific efficiency."""
        # Get historical performance for this algorithm
        historical_ratio = self._get_historical_compression_ratio(algorithm)
        historical_time = self._get_historical_compression_time(algorithm)
        
        if historical_ratio == 0 or historical_time == 0:
            return 0.5  # Default efficiency
        
        # Compare current performance to historical
        ratio_efficiency = compression_ratio / historical_ratio
        time_efficiency = historical_time / compression_time
        
        # Combined efficiency
        efficiency = (ratio_efficiency + time_efficiency) / 2
        
        return min(efficiency, 1.0)
    
    def _update_algorithm_metrics(self, algorithm: str, metrics: CompressionMetrics, parameters: Dict[str, Any]):
        """Update algorithm-specific metrics."""
        if algorithm not in self.algorithm_metrics:
            self.algorithm_metrics[algorithm] = AlgorithmMetrics(
                algorithm_name=algorithm,
                success_rate=0.0,
                average_compression_ratio=0.0,
                average_compression_time=0.0,
                average_memory_usage=0.0,
                average_quality_score=0.0,
                average_information_preservation=0.0,
                total_uses=0,
                successful_uses=0,
                failed_uses=0,
                content_type_performance={}
            )
        
        # Update metrics
        algo_metrics = self.algorithm_metrics[algorithm]
        algo_metrics.total_uses += 1
        
        if metrics.quality_score and metrics.quality_score > 0.5:
            algo_metrics.successful_uses += 1
        else:
            algo_metrics.failed_uses += 1
        
        # Update averages
        total_uses = algo_metrics.total_uses
        algo_metrics.success_rate = algo_metrics.successful_uses / total_uses
        algo_metrics.average_compression_ratio = (
            (algo_metrics.average_compression_ratio * (total_uses - 1) + metrics.compression_ratio) / total_uses
        )
        algo_metrics.average_compression_time = (
            (algo_metrics.average_compression_time * (total_uses - 1) + metrics.compression_time) / total_uses
        )
        if metrics.memory_usage:
            algo_metrics.average_memory_usage = (
                (algo_metrics.average_memory_usage * (total_uses - 1) + metrics.memory_usage) / total_uses
            )
        if metrics.quality_score:
            algo_metrics.average_quality_score = (
                (algo_metrics.average_quality_score * (total_uses - 1) + metrics.quality_score) / total_uses
            )
        if metrics.information_preservation:
            algo_metrics.average_information_preservation = (
                (algo_metrics.average_information_preservation * (total_uses - 1) + metrics.information_preservation) / total_uses
            )
        
        algo_metrics.last_used = datetime.utcnow()
    
    def _get_current_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return psutil.virtual_memory().used
    
    def _get_current_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)
    
    def _get_network_usage(self) -> float:
        """Get current network usage in MB/s."""
        # Simplified network usage calculation
        return 0.0  # Would implement actual network monitoring
    
    def _calculate_requests_per_second(self) -> float:
        """Calculate requests per second."""
        # Simplified calculation
        if len(self.metrics_history) < 2:
            return 0.0
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 metrics
        total_time = sum(m.compression_time for m in recent_metrics)
        
        return len(recent_metrics) / total_time if total_time > 0 else 0.0
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time."""
        if not self.metrics_history:
            return 0.0
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 metrics
        return self._mean([m.compression_time for m in recent_metrics])
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate."""
        if not self.metrics_history:
            return 0.0
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 metrics
        errors = sum(1 for m in recent_metrics if m.quality_score and m.quality_score < 0.5)
        
        return (errors / len(recent_metrics)) * 100
    
    def _calculate_semantic_preservation(self, original: str, decompressed: str) -> float:
        """Calculate semantic preservation score."""
        # Simplified semantic preservation calculation
        if original == decompressed:
            return 1.0
        
        # Compare word overlap
        original_words = set(original.lower().split())
        decompressed_words = set(decompressed.lower().split())
        
        if not original_words:
            return 1.0
        
        overlap = len(original_words.intersection(decompressed_words))
        return overlap / len(original_words)
    
    def _calculate_structural_integrity(self, original: str, decompressed: str) -> float:
        """Calculate structural integrity score."""
        # Simplified structural integrity calculation
        if original == decompressed:
            return 1.0
        
        # Compare line structure
        original_lines = original.split('\n')
        decompressed_lines = decompressed.split('\n')
        
        if len(original_lines) != len(decompressed_lines):
            return 0.8  # Some structural loss
        
        return 0.9  # Good structural preservation
    
    def _calculate_distortion_measure(self, original: str, decompressed: str) -> float:
        """Calculate distortion measure."""
        # Simplified distortion calculation
        if original == decompressed:
            return 0.0
        
        # Calculate character-level differences
        min_len = min(len(original), len(decompressed))
        if min_len == 0:
            return 1.0
        
        differences = sum(1 for i in range(min_len) if original[i] != decompressed[i])
        return differences / min_len
    
    def _calculate_fidelity_score(self, content_integrity: float, semantic_preservation: float, structural_integrity: float) -> float:
        """Calculate fidelity score."""
        return (content_integrity + semantic_preservation + structural_integrity) / 3
    
    def _calculate_text_quality(self, original: str, decompressed: str) -> float:
        """Calculate text quality score."""
        # Simplified text quality calculation
        return self._calculate_semantic_preservation(original, decompressed)
    
    def _calculate_code_quality(self, original: str, decompressed: str) -> float:
        """Calculate code quality score."""
        # Simplified code quality calculation
        return self._calculate_structural_integrity(original, decompressed)
    
    def _calculate_binary_quality(self, original: str, decompressed: str) -> float:
        """Calculate binary quality score."""
        # Simplified binary quality calculation
        return 1.0 if original == decompressed else 0.0
    
    def _get_cutoff_time(self, time_range: TimeRange) -> datetime:
        """Get cutoff time for the specified time range."""
        now = datetime.utcnow()
        
        if time_range == TimeRange.HOUR:
            return now.replace(minute=0, second=0, microsecond=0)
        elif time_range == TimeRange.DAY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == TimeRange.WEEK:
            # Go back 7 days
            from datetime import timedelta
            return now - timedelta(days=7)
        elif time_range == TimeRange.MONTH:
            # Go back 30 days
            from datetime import timedelta
            return now - timedelta(days=30)
        elif time_range == TimeRange.YEAR:
            # Go back 365 days
            from datetime import timedelta
            return now - timedelta(days=365)
        else:
            return now
    
    def _mean(self, values: List[float]) -> float:
        """Calculate mean of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    def _median(self, values: List[float]) -> float:
        """Calculate median of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation of values."""
        if not values:
            return 0.0
        mean_val = self._mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _variance(self, values: List[float]) -> float:
        """Calculate variance of values."""
        if not values:
            return 0.0
        mean_val = self._mean(values)
        return sum((x - mean_val) ** 2 for x in values) / len(values)
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        k = (n - 1) * percentile / 100
        f = int(k)
        c = k - f
        if f + 1 < n:
            return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
        else:
            return sorted_values[f]
    
    def _get_best_algorithm(self, metrics: List[CompressionMetrics]) -> str:
        """Get the best performing algorithm from metrics."""
        if not metrics:
            return "unknown"
        
        # Group by algorithm and calculate average quality score
        algorithm_scores = {}
        for metric in metrics:
            algo = getattr(metric, 'algorithm_used', 'unknown')
            if algo not in algorithm_scores:
                algorithm_scores[algo] = []
            
            if metric.quality_score:
                algorithm_scores[algo].append(metric.quality_score)
        
        # Find algorithm with highest average quality score
        best_algorithm = "unknown"
        best_score = 0.0
        
        for algo, scores in algorithm_scores.items():
            avg_score = self._mean(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_algorithm = algo
        
        return best_algorithm
    
    def _filter_metrics(self, start_time: datetime, end_time: datetime, 
                       algorithm_filter: Optional[str], content_type_filter: Optional[str]) -> List[CompressionMetrics]:
        """Filter metrics by time range and filters."""
        filtered = []
        
        for metric in self.metrics_history:
            if start_time <= metric.timestamp <= end_time:
                # Apply algorithm filter
                if algorithm_filter:
                    algo = getattr(metric, 'algorithm_used', 'unknown')
                    if algo != algorithm_filter:
                        continue
                
                # Apply content type filter (would need content type in metrics)
                if content_type_filter:
                    # Simplified - would need to store content type in metrics
                    pass
                
                filtered.append(metric)
        
        return filtered
    
    def _extract_metric_values(self, metrics: List[CompressionMetrics], metric_type: MetricType) -> List[float]:
        """Extract values for the specified metric type."""
        values = []
        
        for metric in metrics:
            if metric_type == MetricType.COMPRESSION_RATIO:
                values.append(metric.compression_ratio)
            elif metric_type == MetricType.COMPRESSION_SPEED:
                values.append(metric.compression_speed)
            elif metric_type == MetricType.DECOMPRESSION_SPEED:
                if metric.decompression_speed:
                    values.append(metric.decompression_speed)
            elif metric_type == MetricType.MEMORY_USAGE:
                if metric.memory_usage:
                    values.append(metric.memory_usage)
            elif metric_type == MetricType.CPU_USAGE:
                if metric.cpu_usage:
                    values.append(metric.cpu_usage)
            elif metric_type == MetricType.QUALITY_SCORE:
                if metric.quality_score:
                    values.append(metric.quality_score)
            elif metric_type == MetricType.INFORMATION_PRESERVATION:
                if metric.information_preservation:
                    values.append(metric.information_preservation)
            elif metric_type == MetricType.ENTROPY_REDUCTION:
                if metric.entropy_reduction:
                    values.append(metric.entropy_reduction)
            elif metric_type == MetricType.PATTERN_EFFICIENCY:
                if metric.pattern_efficiency:
                    values.append(metric.pattern_efficiency)
            elif metric_type == MetricType.ALGORITHM_EFFICIENCY:
                if metric.algorithm_efficiency:
                    values.append(metric.algorithm_efficiency)
        
        return values
    
    def _get_historical_compression_ratio(self, algorithm: str) -> float:
        """Get historical compression ratio for algorithm."""
        # Simplified - would query database in real implementation
        return 2.0  # Default historical ratio
    
    def _get_historical_compression_time(self, algorithm: str) -> float:
        """Get historical compression time for algorithm."""
        # Simplified - would query database in real implementation
        return 1.0  # Default historical time
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary."""
        return {
            'total_compressions': 0,
            'average_compression_ratio': 0.0,
            'average_compression_speed': 0.0,
            'average_compression_time': 0.0,
            'average_quality_score': 0.0,
            'best_algorithm': 'unknown',
            'total_data_processed': 0,
            'total_data_saved': 0,
            'time_range': 'day'
        }
    
    def _empty_aggregation(self, metric_type: MetricType, time_range: TimeRange, 
                          start_time: datetime, end_time: datetime) -> MetricsAggregation:
        """Return empty aggregation."""
        return MetricsAggregation(
            metric_type=metric_type,
            time_range=time_range,
            start_time=start_time,
            end_time=end_time,
            count=0,
            min_value=0.0,
            max_value=0.0,
            mean_value=0.0,
            median_value=0.0,
            std_deviation=0.0,
            p25=0.0,
            p75=0.0,
            p90=0.0,
            p95=0.0,
            p99=0.0,
            total_value=0.0,
            variance=0.0
        )






