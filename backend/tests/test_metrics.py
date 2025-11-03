"""
Unit tests for metrics and analytics endpoints.

This module tests the metrics functionality including summary, performance,
algorithm metrics, aggregation, comparison, trends, and dashboard endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestMetricsEndpoints:
    """Test cases for metrics and analytics endpoints."""

    def test_metrics_summary(self, client: TestClient):
        """Test metrics summary endpoint."""
        response = client.get("/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "compression_stats" in data
        assert "performance_stats" in data
        assert "system_stats" in data
        assert "timestamp" in data
        
        # Check overview section
        overview = data["overview"]
        assert "total_requests" in overview
        assert "total_files" in overview
        assert "average_compression_ratio" in overview
        
        # Check compression stats
        compression_stats = data["compression_stats"]
        assert "total_compressions" in compression_stats
        assert "average_compression_time" in compression_stats
        assert "best_algorithm" in compression_stats

    def test_metrics_summary_with_time_range(self, client: TestClient):
        """Test metrics summary with time range filter."""
        response = client.get("/summary?time_range=last_24_hours")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "timestamp" in data

    def test_performance_metrics(self, client: TestClient):
        """Test performance metrics endpoint."""
        response = client.get("/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "system_metrics" in data
        assert "request_metrics" in data
        assert "compression_metrics" in data
        assert "timestamp" in data
        
        # Check system metrics
        system_metrics = data["system_metrics"]
        assert "cpu_usage" in system_metrics
        assert "memory_usage" in system_metrics
        assert "disk_usage" in system_metrics
        assert "network_io" in system_metrics
        
        # Check request metrics
        request_metrics = data["request_metrics"]
        assert "requests_per_second" in request_metrics
        assert "average_response_time" in request_metrics
        assert "error_rate" in request_metrics

    def test_performance_metrics_realtime(self, client: TestClient):
        """Test real-time performance metrics."""
        response = client.get("/performance?realtime=true")
        assert response.status_code == 200
        
        data = response.json()
        assert "system_metrics" in data
        assert "timestamp" in data

    def test_algorithm_metrics(self, client: TestClient):
        """Test algorithm-specific metrics endpoint."""
        response = client.get("/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert "summary" in data
        assert "timestamp" in data
        
        algorithms = data["algorithms"]
        assert isinstance(algorithms, list)
        
        if algorithms:  # If there are algorithms with metrics
            for algorithm in algorithms:
                assert "name" in algorithm
                assert "usage_count" in algorithm
                assert "average_compression_ratio" in algorithm
                assert "average_compression_time" in algorithm

    def test_algorithm_metrics_with_filter(self, client: TestClient):
        """Test algorithm metrics with specific algorithm filter."""
        response = client.get("/algorithms?algorithm=gzip")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert "summary" in data

    def test_metrics_aggregation(self, client: TestClient, metrics_request_data):
        """Test metrics aggregation endpoint."""
        response = client.post("/aggregate", json=metrics_request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "aggregated_metrics" in data
        assert "time_series" in data
        assert "summary" in data
        assert "timestamp" in data
        
        aggregated_metrics = data["aggregated_metrics"]
        assert "compression_ratio" in aggregated_metrics
        assert "compression_speed" in aggregated_metrics

    def test_metrics_aggregation_custom(self, client: TestClient):
        """Test custom metrics aggregation."""
        request_data = {
            "time_range": "last_7_days",
            "metric_types": ["compression_ratio", "compression_speed", "memory_usage"],
            "algorithms": ["gzip", "lzma"],
            "aggregation": "hourly",
            "group_by": ["algorithm", "content_type"]
        }
        
        response = client.post("/aggregate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "aggregated_metrics" in data
        assert "time_series" in data

    def test_metrics_comparison(self, client: TestClient):
        """Test metrics comparison endpoint."""
        request_data = {
            "comparison_type": "algorithm_performance",
            "algorithms": ["gzip", "lzma", "bzip2"],
            "time_range": "last_24_hours",
            "metrics": ["compression_ratio", "compression_speed"]
        }
        
        response = client.post("/compare", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "comparison_data" in data
        assert "analysis" in data
        assert "recommendations" in data
        assert "timestamp" in data
        
        comparison_data = data["comparison_data"]
        assert len(comparison_data) == 3  # Three algorithms

    def test_metrics_comparison_time_periods(self, client: TestClient):
        """Test metrics comparison across different time periods."""
        request_data = {
            "comparison_type": "time_period",
            "periods": ["last_24_hours", "last_7_days", "last_30_days"],
            "metrics": ["compression_ratio", "request_count"]
        }
        
        response = client.post("/compare", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "comparison_data" in data
        assert "analysis" in data

    def test_metrics_trends(self, client: TestClient):
        """Test metrics trends endpoint."""
        response = client.get("/trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
        assert "analysis" in data
        assert "predictions" in data
        assert "timestamp" in data
        
        trends = data["trends"]
        assert "compression_ratio_trend" in trends
        assert "performance_trend" in trends
        assert "usage_trend" in trends

    def test_metrics_trends_with_parameters(self, client: TestClient):
        """Test metrics trends with specific parameters."""
        response = client.get("/trends?metric=compression_ratio&period=last_7_days&granularity=hourly")
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
        assert "analysis" in data

    def test_dashboard_metrics(self, client: TestClient):
        """Test dashboard metrics endpoint."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "performance" in data
        assert "compression" in data
        assert "system" in data
        assert "algorithms" in data
        assert "recent_activity" in data
        assert "timestamp" in data
        
        # Check overview section
        overview = data["overview"]
        assert "total_requests" in overview
        assert "active_algorithms" in overview
        assert "system_health" in overview
        
        # Check performance section
        performance = data["performance"]
        assert "response_times" in performance
        assert "throughput" in performance
        assert "error_rates" in performance
        
        # Check compression section
        compression = data["compression"]
        assert "ratios" in compression
        assert "speeds" in compression
        assert "popular_algorithms" in compression

    def test_dashboard_metrics_with_filters(self, client: TestClient):
        """Test dashboard metrics with filters."""
        response = client.get("/dashboard?time_range=last_24_hours&include_details=true")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "performance" in data
        assert "compression" in data

    def test_metrics_invalid_request(self, client: TestClient):
        """Test metrics endpoints with invalid requests."""
        # Invalid time range
        response = client.get("/summary?time_range=invalid_range")
        assert response.status_code in [400, 422]
        
        # Invalid aggregation request
        invalid_request = {
            "time_range": "invalid",
            "metric_types": ["invalid_metric"],
            "algorithms": ["invalid_algorithm"]
        }
        response = client.post("/aggregate", json=invalid_request)
        assert response.status_code == 422

    def test_metrics_empty_data(self, client: TestClient):
        """Test metrics endpoints with no data."""
        # Test with very specific filters that might return no data
        response = client.get("/algorithms?algorithm=nonexistent_algorithm")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert len(data["algorithms"]) == 0

    def test_metrics_time_series(self, client: TestClient):
        """Test time series metrics data."""
        response = client.get("/trends?metric=compression_ratio&granularity=hourly")
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
        assert "time_series_data" in data["trends"]

    def test_metrics_performance_benchmarks(self, client: TestClient):
        """Test performance benchmark metrics."""
        response = client.get("/performance?include_benchmarks=true")
        assert response.status_code == 200
        
        data = response.json()
        assert "system_metrics" in data
        assert "benchmarks" in data

    def test_metrics_algorithm_efficiency(self, client: TestClient):
        """Test algorithm efficiency metrics."""
        response = client.get("/algorithms?include_efficiency=true")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert "efficiency_analysis" in data

    def test_metrics_system_health(self, client: TestClient):
        """Test system health metrics."""
        response = client.get("/performance?include_health=true")
        assert response.status_code == 200
        
        data = response.json()
        assert "system_metrics" in data
        assert "health_status" in data
        assert "alerts" in data

    def test_metrics_custom_time_range(self, client: TestClient):
        """Test metrics with custom time range."""
        request_data = {
            "time_range": "custom",
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-31T23:59:59Z",
            "metric_types": ["compression_ratio", "compression_speed"]
        }
        
        response = client.post("/aggregate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "aggregated_metrics" in data
        assert "time_series" in data

    def test_metrics_export(self, client: TestClient):
        """Test metrics export functionality."""
        response = client.get("/summary?format=csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        
        response = client.get("/summary?format=json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_metrics_caching(self, client: TestClient):
        """Test metrics caching behavior."""
        # First request
        response1 = client.get("/summary")
        assert response1.status_code == 200
        
        # Second request (should be cached)
        response2 = client.get("/summary")
        assert response2.status_code == 200
        
        # Both responses should be identical
        assert response1.json() == response2.json()

    def test_metrics_error_handling(self, client: TestClient):
        """Test metrics error handling."""
        # Test with invalid endpoint
        response = client.get("/metrics/invalid")
        assert response.status_code == 404
        
        # Test with malformed request
        response = client.post("/aggregate", json={"invalid": "data"})
        assert response.status_code == 422
