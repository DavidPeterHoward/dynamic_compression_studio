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
        response = client.post("/api/v1/compression/compress", json=compression_request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "compressed_content" in data
        assert "success" in data
        assert data["success"] == True
        
        # Check if result is present and has the expected fields
        if "result" in data and data["result"]:
            result = data["result"]
            assert "algorithm_used" in result
            assert "compression_ratio" in result
            assert "compression_time" in result
            assert "original_size" in result
            assert "compressed_size" in result

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
            
            response = client.post("/api/v1/compression/compress", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["algorithm_used"] == algorithm
            assert data["result"]["compression_ratio"] > 0
            assert data["result"]["compression_time"] > 0

    def test_compress_with_different_content_types(self, client: TestClient):
        """Test compression with different content types."""
        content_types = ["text", "json", "xml", "html", "css", "javascript"]
        
        for content_type in content_types:
            request_data = {
                "content": f"This is {content_type} content for testing compression",
                "content_type": content_type,
                "parameters": {
                    "algorithm": "gzip",
                    "level": "balanced",
                    "window_size": 32768,
                    "content_type": content_type
                }
            }
            
            response = client.post("/api/v1/compression/compress", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["result"]["compression_ratio"] > 0
            assert data["result"]["compression_time"] > 0

    def test_compress_with_parameters(self, client: TestClient):
        """Test compression with different parameters."""
        request_data = {
            "content": "This is a test content for compression with parameters",
            "content_type": "text",
            "parameters": {
                "algorithm": "gzip",
                "level": 9,
                "window_size": 32768,
                "content_type": "text"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["result"]["compression_ratio"] > 0
        assert data["result"]["compression_time"] > 0

    def test_compress_batch(self, client: TestClient):
        """Test batch compression endpoint."""
        batch_request = {
            "items": [
                {
                    "content": "First item for batch compression",
                    "content_type": "text",
                    "parameters": {
                        "algorithm": "gzip",
                        "level": "balanced",
                        "window_size": 32768,
                        "content_type": "text"
                    }
                },
                {
                    "content": "Second item for batch compression",
                    "content_type": "text",
                    "parameters": {
                        "algorithm": "lz4",
                        "level": "balanced",
                        "window_size": 32768,
                        "content_type": "text"
                    }
                },
                {
                    "content": "Third item for batch compression",
                    "content_type": "text",
                    "parameters": {
                        "algorithm": "brotli",
                        "level": "balanced",
                        "window_size": 32768,
                        "content_type": "text"
                    }
                }
            ]
        }
        
        response = client.post("/api/v1/compression/compress/batch", json=batch_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3
        assert "total_compression_time" in data
        assert "average_compression_ratio" in data

    def test_compress_batch_large(self, client: TestClient):
        """Test batch compression with large number of items."""
        items = []
        for i in range(100):
            items.append({
                "content": f"Item {i} for large batch compression test",
                "content_type": "text",
                "parameters": {
                    "algorithm": "gzip",
                    "level": "balanced",
                    "window_size": 32768,
                    "content_type": "text"
                }
            })
        
        batch_request = {"items": items}
        
        response = client.post("/api/v1/compression/compress/batch", json=batch_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 100

    def test_compare_algorithms(self, client: TestClient):
        """Test algorithm comparison endpoint."""
        request_data = {
            "content": "This is content for algorithm comparison testing",
            "content_type": "text",
            "algorithms": ["gzip", "lz4", "brotli", "zstandard"]
        }
        
        response = client.post("/api/v1/compression/compare", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "comparison_results" in data
        assert "best_algorithm" in data
        assert "recommendations" in data
        assert len(data["comparison_results"]) == 4

    def test_compare_algorithms_with_different_content(self, client: TestClient):
        """Test algorithm comparison with different content types."""
        content_types = ["text", "json", "xml"]
        
        for content_type in content_types:
            request_data = {
                "content": f"This is {content_type} content for comparison",
                "content_type": content_type,
                "algorithms": ["gzip", "lz4", "brotli"]
            }
            
            response = client.post("/api/v1/compression/compare", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "comparison_results" in data
            assert "best_algorithm" in data

    def test_algorithms_list(self, client: TestClient):
        """Test getting list of available algorithms."""
        response = client.get("/api/v1/compression/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert isinstance(data["algorithms"], list)
        assert len(data["algorithms"]) > 0

    def test_algorithm_parameters(self, client: TestClient):
        """Test getting algorithm parameters."""
        algorithms = ["gzip", "lz4", "brotli"]
        
        for algorithm in algorithms:
            response = client.get(f"/api/v1/compression/parameters/{algorithm}")
            assert response.status_code == 200
            
            data = response.json()
            assert "algorithm" in data
            assert "parameters" in data
            assert data["algorithm"] == algorithm

    def test_analyze_content(self, client: TestClient):
        """Test content analysis endpoint."""
        request_data = {
            "content": "This is sample content for analysis",
            "content_type": "text"
        }
        
        response = client.get("/api/v1/compression/analyze", params=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "content_analysis" in data
        assert "recommended_algorithms" in data
        assert "complexity_score" in data

    def test_analyze_code_content(self, client: TestClient):
        """Test content analysis with code content."""
        code_content = """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        """
        
        request_data = {
            "content": code_content,
            "content_type": "code"
        }
        
        response = client.get("/api/v1/compression/analyze", params=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "content_analysis" in data
        assert "recommended_algorithms" in data

    def test_analyze_binary_content(self, client: TestClient):
        """Test content analysis with binary content."""
        import base64
        
        # Create some binary data
        binary_data = b"Binary content for testing compression analysis"
        encoded_data = base64.b64encode(binary_data).decode('utf-8')
        
        request_data = {
            "content": encoded_data,
            "content_type": "binary"
        }
        
        response = client.get("/api/v1/compression/analyze", params=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "content_analysis" in data
        assert "recommended_algorithms" in data

    def test_compress_invalid_request(self, client: TestClient):
        """Test compression with invalid request data."""
        # Missing required fields
        response = client.post("/api/v1/compression/compress", json={})
        assert response.status_code == 422

    def test_compress_large_content(self, client: TestClient):
        """Test compression with large content."""
        large_content = "A" * 100000  # 100KB of repeated content

        request_data = {
            "content": large_content,
            "content_type": "text",
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced",
                "window_size": 32768,
                "content_type": "text"
            }
        }

        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["result"]["compression_ratio"] > 0
        assert data["result"]["original_size"] == len(large_content)

    def test_compress_empty_content(self, client: TestClient):
        """Test compression with empty content."""
        request_data = {
            "content": "",
            "content_type": "text",
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced",
                "window_size": 32768,
                "content_type": "text"
            }
        }

        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["result"]["original_size"] == 0

    def test_compress_unicode_content(self, client: TestClient):
        """Test compression with Unicode content."""
        unicode_content = "Hello 世界! 🌍 This is Unicode content with emojis 🚀"

        request_data = {
            "content": unicode_content,
            "content_type": "text",
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced",
                "window_size": 32768,
                "content_type": "text"
            }
        }

        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["result"]["compression_ratio"] > 0
        assert data["result"]["original_size"] == len(unicode_content.encode('utf-8'))

    def test_compress_with_metadata(self, client: TestClient):
        """Test compression with metadata preservation."""
        request_data = {
            "content": "Test content with metadata",
            "content_type": "text",
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced",
                "window_size": 32768,
                "content_type": "text"
            }
        }

        response = client.post("/api/v1/compression/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["result"]["compression_ratio"] > 0
