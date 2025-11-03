"""
Unit tests for compression endpoints.

This module tests the compression functionality including single compression,
batch compression, algorithm comparison, and content analysis.
"""

import pytest
from fastapi.testclient import TestClient


class TestCompressionEndpoints:
    """Test cases for compression endpoints."""

    def test_compress_basic(self, client: TestClient, compression_request_data):
        """Test basic compression endpoint."""
        response = client.post("/compress", json=compression_request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "compressed_content" in data
        assert "algorithm_used" in data
        assert "compression_ratio" in data
        assert "compression_time" in data
        assert "original_size" in data
        assert "compressed_size" in data
        assert "metrics" in data

    def test_compress_with_different_algorithms(self, client: TestClient):
        """Test compression with different algorithms."""
        algorithms = ["gzip", "lzma", "bzip2", "lz4", "zstandard", "brotli"]
        
        for algorithm in algorithms:
            request_data = {
                "content": "This is a test content for compression with " + algorithm,
                "content_type": "text",
                "algorithm": algorithm,
                "parameters": {
                    "compression_level": 6
                }
            }
            
            response = client.post("/compress", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["algorithm_used"] == algorithm
            assert data["compression_ratio"] > 0
            assert data["compression_time"] > 0

    def test_compress_with_different_content_types(self, client: TestClient):
        """Test compression with different content types."""
        content_types = ["text", "code", "binary", "structured", "mixed"]
        
        for content_type in content_types:
            request_data = {
                "content": f"Test content for {content_type} type",
                "content_type": content_type,
                "algorithm": "gzip"
            }
            
            response = client.post("/compress", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "compressed_content" in data
            assert data["content_analysis"]["content_type"] == content_type

    def test_compress_with_parameters(self, client: TestClient):
        """Test compression with different parameters."""
        request_data = {
            "content": "This is a test content for compression with parameters",
            "content_type": "text",
            "algorithm": "gzip",
            "parameters": {
                "compression_level": 9,
                "window_size": 15,
                "dictionary_size": 32768
            }
        }
        
        response = client.post("/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "compressed_content" in data
        assert data["parameters_used"]["compression_level"] == 9

    def test_compress_batch(self, client: TestClient, batch_compression_request_data):
        """Test batch compression endpoint."""
        response = client.post("/compress/batch", json=batch_compression_request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "summary" in data
        assert "total_time" in data
        assert len(data["results"]) == 2
        
        for result in data["results"]:
            assert "compressed_content" in result
            assert "algorithm_used" in result
            assert "compression_ratio" in result

    def test_compress_batch_large(self, client: TestClient):
        """Test batch compression with many items."""
        items = []
        for i in range(10):
            items.append({
                "content": f"Test content item {i} for batch compression",
                "content_type": "text",
                "algorithm": "gzip"
            })
        
        request_data = {
            "items": items,
            "options": {
                "parallel_processing": True,
                "calculate_metrics": True
            }
        }
        
        response = client.post("/compress/batch", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["results"]) == 10
        assert data["summary"]["total_items"] == 10

    def test_compare_algorithms(self, client: TestClient):
        """Test algorithm comparison endpoint."""
        request_data = {
            "content": "This is a test content for comparing compression algorithms",
            "content_type": "text",
            "algorithms": ["gzip", "lzma", "bzip2", "lz4"],
            "parameters": {
                "compression_level": 6
            }
        }
        
        response = client.post("/compare", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "comparison" in data
        assert "recommendation" in data
        assert "summary" in data
        
        comparison = data["comparison"]
        assert len(comparison) == 4
        
        for result in comparison:
            assert "algorithm" in result
            assert "compression_ratio" in result
            assert "compression_time" in result
            assert "compressed_size" in result

    def test_compare_algorithms_with_different_content(self, client: TestClient):
        """Test algorithm comparison with different content types."""
        content_types = ["text", "code", "binary"]
        
        for content_type in content_types:
            request_data = {
                "content": f"Test content for {content_type} comparison",
                "content_type": content_type,
                "algorithms": ["gzip", "lzma", "bzip2"]
            }
            
            response = client.post("/compare", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "recommendation" in data
            assert data["recommendation"]["reasoning"] is not None

    def test_algorithms_list(self, client: TestClient):
        """Test algorithms listing endpoint."""
        response = client.get("/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert "categories" in data
        
        algorithms = data["algorithms"]
        assert len(algorithms) > 0
        
        for algorithm in algorithms:
            assert "name" in algorithm
            assert "category" in algorithm
            assert "description" in algorithm
            assert "parameters" in algorithm

    def test_algorithm_parameters(self, client: TestClient):
        """Test algorithm parameters endpoint."""
        algorithms = ["gzip", "lzma", "bzip2"]
        
        for algorithm in algorithms:
            response = client.get(f"/parameters/{algorithm}")
            assert response.status_code == 200
            
            data = response.json()
            assert "algorithm" in data
            assert "parameters" in data
            assert "defaults" in data
            assert "ranges" in data
            
            assert data["algorithm"] == algorithm

    def test_analyze_content(self, client: TestClient, sample_text_content):
        """Test content analysis endpoint."""
        request_data = {
            "content": sample_text_content,
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "content_type" in data
        assert "entropy" in data
        assert "complexity" in data
        assert "patterns" in data
        assert "compression_potential" in data
        assert "recommendations" in data

    def test_analyze_code_content(self, client: TestClient, sample_code_content):
        """Test content analysis with code."""
        request_data = {
            "content": sample_code_content,
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "code"
        assert "structure_analysis" in data
        assert "language_detection" in data

    def test_analyze_binary_content(self, client: TestClient, sample_binary_content):
        """Test content analysis with binary content."""
        request_data = {
            "content": sample_binary_content.decode('latin-1'),
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["content_type"] == "binary"
        assert "entropy" in data
        assert "patterns" in data

    def test_compress_invalid_request(self, client: TestClient):
        """Test compression with invalid request data."""
        # Missing required fields
        response = client.post("/compress", json={})
        assert response.status_code == 422
        
        # Invalid algorithm
        response = client.post("/compress", json={
            "content": "test",
            "algorithm": "invalid_algorithm"
        })
        assert response.status_code == 422
        
        # Invalid content type
        response = client.post("/compress", json={
            "content": "test",
            "content_type": "invalid_type",
            "algorithm": "gzip"
        })
        assert response.status_code == 422

    def test_compress_large_content(self, client: TestClient):
        """Test compression with large content."""
        large_content = "A" * 100000  # 100KB of repeated content
        
        request_data = {
            "content": large_content,
            "content_type": "text",
            "algorithm": "gzip"
        }
        
        response = client.post("/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["compression_ratio"] > 1.0  # Should compress well
        assert data["original_size"] == 100000

    def test_compress_empty_content(self, client: TestClient):
        """Test compression with empty content."""
        request_data = {
            "content": "",
            "content_type": "text",
            "algorithm": "gzip"
        }
        
        response = client.post("/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["original_size"] == 0
        assert data["compressed_size"] == 0

    def test_compress_unicode_content(self, client: TestClient):
        """Test compression with Unicode content."""
        unicode_content = "Hello 世界! 🌍 This is Unicode content with emojis 🚀"
        
        request_data = {
            "content": unicode_content,
            "content_type": "text",
            "algorithm": "gzip"
        }
        
        response = client.post("/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "compressed_content" in data
        assert data["original_size"] > 0

    def test_compress_with_metadata(self, client: TestClient):
        """Test compression with metadata preservation."""
        request_data = {
            "content": "Test content with metadata",
            "content_type": "text",
            "algorithm": "gzip",
            "options": {
                "preserve_metadata": True,
                "metadata": {
                    "source": "test",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            }
        }
        
        response = client.post("/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "metadata" in data
        assert data["metadata"]["source"] == "test"
