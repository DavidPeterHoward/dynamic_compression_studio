"""
Comprehensive API endpoint tests for the Dynamic Compression Algorithms backend.

This module tests all API endpoints including:
- Health checks
- Compression endpoints
- File management
- Metrics endpoints
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.main import app
from app.core.compression_engine import CompressionEngine
from app.models.compression import (
    CompressionRequest, CompressionParameters, CompressionAlgorithm
)
from tests.test_config import test_config, test_data_generator


class TestHealthEndpoints:
    """Test suite for health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_health_detailed(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "system" in data
        assert "application" in data
    
    def test_health_readiness(self, client):
        """Test readiness check endpoint."""
        response = client.get("/api/v1/health/readiness")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ready", "not_ready"]
    
    def test_health_liveness(self, client):
        """Test liveness check endpoint."""
        response = client.get("/api/v1/health/liveness")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["alive", "dead"]


class TestCompressionEndpoints:
    """Test suite for compression endpoints."""
    
    def test_compress_basic(self, client):
        """Test basic compression endpoint."""
        request_data = {
            "content": "This is a test content for compression.",
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert data["result"]["original_size"] > 0
        assert data["result"]["compressed_size"] > 0
        assert data["result"]["compression_ratio"] > 1.0
    
    def test_compress_empty_content(self, client):
        """Test compression with empty content."""
        request_data = {
            "content": "",
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "No content provided" in data["message"]
    
    def test_compress_different_algorithms(self, client):
        """Test compression with different algorithms."""
        content = "This is a test content for compression testing with different algorithms."
        algorithms = ["gzip", "lzma", "bzip2", "lz4", "brotli"]
        
        for algorithm in algorithms:
            request_data = {
                "content": content,
                "parameters": {
                    "algorithm": algorithm,
                    "level": "balanced"
                }
            }
            
            response = client.post("/api/v1/compression/compress", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["result"]["algorithm_used"] == algorithm
    
    def test_compress_content_aware(self, client):
        """Test content-aware compression."""
        request_data = {
            "content": "This is a test content for content-aware compression.",
            "parameters": {
                "algorithm": "content_aware",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["result"]["algorithm_used"] != "content_aware"
    
    def test_compress_large_content(self, client):
        """Test compression with large content."""
        large_content = test_data_generator.generate_text_content(10000)
        
        request_data = {
            "content": large_content,
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["result"]["original_size"] > 1000
    
    def test_compress_batch(self, client):
        """Test batch compression endpoint."""
        request_data = {
            "items": [
                {
                    "content": "First test content.",
                    "parameters": {
                        "algorithm": "gzip",
                        "level": "balanced"
                    }
                },
                {
                    "content": "Second test content.",
                    "parameters": {
                        "algorithm": "lzma",
                        "level": "optimal"
                    }
                }
            ]
        }
        
        response = client.post("/api/v1/compression/compress/batch", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["results"]) == 2
        
        for result in data["results"]:
            assert result["success"] is True
            assert result["result"]["original_size"] > 0
    
    def test_compare_algorithms(self, client):
        """Test algorithm comparison endpoint."""
        content = "This is a test content for algorithm comparison."
        
        response = client.post(
            "/api/v1/compression/compare",
            params={
                "content": content,
                "algorithms": ["gzip", "lzma", "bzip2"]
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "comparison" in data
        assert len(data["comparison"]) == 3
        
        for comp in data["comparison"]:
            assert "algorithm" in comp
            assert "compression_ratio" in comp
            assert "compression_time" in comp
    
    def test_get_algorithms(self, client):
        """Test get available algorithms endpoint."""
        response = client.get("/api/v1/compression/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert len(data["algorithms"]) > 0
        
        for algorithm in data["algorithms"]:
            assert "name" in algorithm
            assert "description" in algorithm
            assert "capabilities" in algorithm
    
    def test_analyze_content(self, client):
        """Test content analysis endpoint."""
        content = "This is a test content for analysis."
        
        response = client.get(
            "/api/v1/compression/analyze",
            params={"content": content}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "entropy" in data
        assert "content_type" in data
        assert "compression_potential" in data
        assert "patterns" in data
    
    def test_get_algorithm_parameters(self, client):
        """Test get algorithm parameters endpoint."""
        algorithms = ["gzip", "lzma", "bzip2"]
        
        for algorithm in algorithms:
            response = client.get(f"/api/v1/compression/parameters/{algorithm}")
            assert response.status_code == 200
            
            data = response.json()
            assert "algorithm" in data
            assert "parameters" in data
            assert "defaults" in data


class TestFileEndpoints:
    """Test suite for file management endpoints."""
    
    def test_upload_file(self, client):
        """Test file upload endpoint."""
        # Create a test file
        test_content = "This is a test file content."
        files = {"file": ("test.txt", test_content, "text/plain")}
        data = {"description": "Test file", "tags": "test,compression"}
        
        response = client.post("/api/v1/files/upload", files=files, data=data)
        assert response.status_code == 200
        
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "size" in data
    
    def test_list_files(self, client):
        """Test list files endpoint."""
        response = client.get("/api/v1/files/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    def test_get_file_info(self, client):
        """Test get file info endpoint."""
        # First upload a file
        test_content = "Test file content."
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        upload_response = client.post("/api/v1/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["file_id"]
        
        # Then get file info
        response = client.get(f"/api/v1/files/{file_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "size" in data
    
    def test_download_file(self, client):
        """Test file download endpoint."""
        # First upload a file
        test_content = "Test file content for download."
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        upload_response = client.post("/api/v1/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["file_id"]
        
        # Then download the file
        response = client.get(f"/api/v1/files/{file_id}/download")
        assert response.status_code == 200
        assert response.content.decode() == test_content
    
    def test_delete_file(self, client):
        """Test file deletion endpoint."""
        # First upload a file
        test_content = "Test file content for deletion."
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        upload_response = client.post("/api/v1/files/upload", files=files)
        assert upload_response.status_code == 200
        
        file_id = upload_response.json()["file_id"]
        
        # Then delete the file
        response = client.delete(f"/api/v1/files/{file_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    def test_search_files(self, client):
        """Test file search endpoint."""
        request_data = {
            "query": "test",
            "file_type": "txt",
            "page": 1,
            "page_size": 10
        }
        
        response = client.post("/api/v1/files/search", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert "total" in data


class TestMetricsEndpoints:
    """Test suite for metrics endpoints."""
    
    def test_get_metrics_summary(self, client):
        """Test get metrics summary endpoint."""
        response = client.get("/api/v1/metrics/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "compression_metrics" in data
        assert "performance_metrics" in data
        assert "quality_metrics" in data
    
    def test_get_performance_metrics(self, client):
        """Test get performance metrics endpoint."""
        response = client.get("/api/v1/metrics/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "disk_usage" in data
    
    def test_get_algorithm_metrics(self, client):
        """Test get algorithm metrics endpoint."""
        response = client.get("/api/v1/metrics/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        
        # Test specific algorithm
        response = client.get("/api/v1/metrics/algorithms?algorithm=gzip")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithm" in data
        assert "metrics" in data
    
    def test_aggregate_metrics(self, client):
        """Test aggregate metrics endpoint."""
        request_data = {
            "metric_type": "compression_ratio",
            "time_range": "day",
            "algorithm": "gzip"
        }
        
        response = client.post("/api/v1/metrics/aggregate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "aggregation" in data
        assert "statistics" in data
    
    def test_compare_metrics(self, client):
        """Test compare metrics endpoint."""
        response = client.post(
            "/api/v1/metrics/compare",
            params={
                "comparison_type": "algorithm",
                "baseline": "gzip",
                "comparison_targets": ["lzma", "bzip2"],
                "metric_type": "compression_ratio",
                "time_range": "day"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "comparison" in data
        assert "baseline" in data
        assert "targets" in data
    
    def test_get_metrics_trends(self, client):
        """Test get metrics trends endpoint."""
        response = client.get(
            "/api/v1/metrics/trends",
            params={
                "metric_type": "compression_ratio",
                "time_range": "day",
                "algorithm": "gzip"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
        assert "data_points" in data
    
    def test_get_dashboard_metrics(self, client):
        """Test get dashboard metrics endpoint."""
        response = client.get("/api/v1/metrics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "performance" in data
        assert "algorithms" in data


class TestErrorHandling:
    """Test suite for error handling."""
    
    def test_invalid_algorithm(self, client):
        """Test handling of invalid algorithm."""
        request_data = {
            "content": "Test content",
            "parameters": {
                "algorithm": "invalid_algorithm",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200  # Should handle gracefully
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_missing_content(self, client):
        """Test handling of missing content."""
        request_data = {
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_file_upload(self, client):
        """Test handling of invalid file upload."""
        # Try to upload without file
        response = client.post("/api/v1/files/upload")
        assert response.status_code == 422  # Validation error
    
    def test_nonexistent_file(self, client):
        """Test handling of nonexistent file."""
        response = client.get("/api/v1/files/nonexistent_id")
        assert response.status_code == 404
    
    def test_invalid_metrics_request(self, client):
        """Test handling of invalid metrics request."""
        response = client.post(
            "/api/v1/metrics/compare",
            params={
                "comparison_type": "invalid_type",
                "baseline": "gzip",
                "comparison_targets": ["lzma"],
                "metric_type": "compression_ratio",
                "time_range": "day"
            }
        )
        assert response.status_code == 400  # Bad request


class TestPerformance:
    """Performance tests for API endpoints."""
    
    def test_compression_endpoint_performance(self, client):
        """Test compression endpoint performance."""
        import time
        
        content = test_data_generator.generate_text_content(5000)
        request_data = {
            "content": content,
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced"
            }
        }
        
        start_time = time.time()
        response = client.post("/api/v1/compression/compress", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    def test_batch_compression_performance(self, client):
        """Test batch compression endpoint performance."""
        import time
        
        items = []
        for i in range(10):
            content = test_data_generator.generate_text_content(1000)
            items.append({
                "content": content,
                "parameters": {
                    "algorithm": "gzip",
                    "level": "balanced"
                }
            })
        
        request_data = {"items": items}
        
        start_time = time.time()
        response = client.post("/api/v1/compression/compress/batch", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 10.0  # Should complete within 10 seconds
    
    def test_content_analysis_performance(self, client):
        """Test content analysis endpoint performance."""
        import time
        
        content = test_data_generator.generate_text_content(10000)
        
        start_time = time.time()
        response = client.get(
            "/api/v1/compression/analyze",
            params={"content": content}
        )
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 2.0  # Should complete within 2 seconds


# Fixtures
@pytest.fixture
def client():
    """Provide a test client for API testing."""
    return TestClient(app)


@pytest.fixture
def mock_compression_engine():
    """Provide a mock compression engine for testing."""
    with patch('app.main.compression_engine') as mock:
        mock.compress = AsyncMock()
        mock.compress.return_value.success = True
        mock.compress.return_value.result.original_size = 100
        mock.compress.return_value.result.compressed_size = 50
        mock.compress.return_value.result.compression_ratio = 2.0
        yield mock


@pytest.fixture
def mock_metrics_collector():
    """Provide a mock metrics collector for testing."""
    with patch('app.main.metrics_collector') as mock:
        mock.get_metrics_summary.return_value = {
            "compression_metrics": {},
            "performance_metrics": {},
            "quality_metrics": {}
        }
        yield mock
