"""
Smoke tests for the Dynamic Compression Algorithms backend.

These tests verify basic functionality and ensure the application
can start and respond to basic requests.
"""

import pytest
from fastapi.testclient import TestClient


class TestSmokeTests:
    """Smoke tests for basic application functionality."""

    def test_application_starts(self, client: TestClient):
        """Test that the application starts and responds to basic requests."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data

    def test_health_endpoint_responds(self, client: TestClient):
        """Test that the health endpoint responds correctly."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_documentation_accessible(self, client: TestClient):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_schema_accessible(self, client: TestClient):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_compression_endpoint_responds(self, client: TestClient):
        """Test that compression endpoint responds to basic request."""
        request_data = {
            "content": "Test content for compression",
            "content_type": "text",
            "algorithm": "gzip"
        }
        
        response = client.post("/compress", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "compressed_content" in data
        assert "algorithm_used" in data
        assert "compression_ratio" in data

    def test_algorithms_endpoint_responds(self, client: TestClient):
        """Test that algorithms endpoint responds."""
        response = client.get("/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert "categories" in data

    def test_metrics_endpoint_responds(self, client: TestClient):
        """Test that metrics endpoint responds."""
        response = client.get("/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "timestamp" in data

    def test_database_initialization(self, client: TestClient):
        """Test database initialization endpoint."""
        response = client.post("/init-db")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "status" in data

    def test_configuration_endpoint(self, client: TestClient):
        """Test configuration endpoint."""
        response = client.get("/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "database" in data
        assert "api" in data
        assert "compression" in data

    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are properly set."""
        response = client.options("/health")
        assert response.status_code == 200
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    def test_error_handling(self, client: TestClient):
        """Test that error handling works correctly."""
        # Test 404 for non-existent endpoint
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
        
        # Test 422 for invalid request
        response = client.post("/compress", json={})
        assert response.status_code == 422

    def test_basic_compression_workflow(self, client: TestClient):
        """Test a basic compression workflow."""
        # 1. Analyze content
        analyze_data = {
            "content": "This is a test content for analysis",
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/analyze", json=analyze_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "content_type" in data
        assert "entropy" in data
        
        # 2. Compress content
        compress_data = {
            "content": "This is a test content for compression",
            "content_type": "text",
            "algorithm": "gzip"
        }
        
        response = client.post("/compress", json=compress_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "compressed_content" in data
        assert data["compression_ratio"] > 0

        # 3. Compare algorithms
        compare_data = {
            "content": "This is a test content for comparison",
            "content_type": "text",
            "algorithms": ["gzip", "lzma", "bzip2"]
        }
        
        response = client.post("/compare", json=compare_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "comparison" in data
        assert "recommendation" in data

    def test_file_upload_workflow(self, client: TestClient):
        """Test a basic file upload workflow."""
        import io
        
        # Upload a file
        file_content = "Test file content for upload"
        files = {
            "file": ("test_file.txt", io.StringIO(file_content), "text/plain")
        }
        
        response = client.post("/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test_file.txt"
        
        file_id = data["file_id"]
        
        # Get file info
        response = client.get(f"/{file_id}")
        assert response.status_code == 200
        
        # Download file
        response = client.get(f"/{file_id}/download")
        assert response.status_code == 200
        assert response.content.decode() == file_content

    def test_metrics_workflow(self, client: TestClient):
        """Test a basic metrics workflow."""
        # Get summary metrics
        response = client.get("/summary")
        assert response.status_code == 200
        
        # Get performance metrics
        response = client.get("/performance")
        assert response.status_code == 200
        
        # Get algorithm metrics
        response = client.get("/algorithms")
        assert response.status_code == 200
        
        # Get dashboard metrics
        response = client.get("/dashboard")
        assert response.status_code == 200

    def test_batch_compression(self, client: TestClient):
        """Test batch compression functionality."""
        batch_data = {
            "items": [
                {
                    "content": "First test content",
                    "content_type": "text",
                    "algorithm": "gzip"
                },
                {
                    "content": "Second test content",
                    "content_type": "text",
                    "algorithm": "lzma"
                }
            ]
        }
        
        response = client.post("/compress/batch", json=batch_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 2

    def test_parameter_optimization(self, client: TestClient):
        """Test parameter optimization functionality."""
        # Get algorithm parameters
        response = client.get("/parameters/gzip")
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithm" in data
        assert "parameters" in data
        assert "defaults" in data

    def test_content_analysis(self, client: TestClient):
        """Test content analysis functionality."""
        analyze_data = {
            "content": "def test_function(): return True",
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/analyze", json=analyze_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "content_type" in data
        assert "entropy" in data
        assert "complexity" in data
        assert "patterns" in data
        assert "compression_potential" in data

    def test_system_resources(self, client: TestClient):
        """Test that system resource endpoints respond."""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "system" in data
        
        system_info = data["system"]
        assert "cpu_usage" in system_info
        assert "memory_usage" in system_info
        assert "disk_usage" in system_info

    def test_application_lifecycle(self, client: TestClient):
        """Test application lifecycle endpoints."""
        # Test readiness
        response = client.get("/health/readiness")
        assert response.status_code == 200
        
        # Test liveness
        response = client.get("/health/liveness")
        assert response.status_code == 200
        
        # Test status
        response = client.get("/health/status")
        assert response.status_code == 200

    def test_api_versioning(self, client: TestClient):
        """Test API versioning information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert "api_version" in data

    def test_error_responses(self, client: TestClient):
        """Test various error response scenarios."""
        # Test invalid JSON
        response = client.post("/compress", data="invalid json")
        assert response.status_code == 422
        
        # Test missing required fields
        response = client.post("/compress", json={"content": "test"})
        assert response.status_code == 422
        
        # Test invalid algorithm
        response = client.post("/compress", json={
            "content": "test",
            "algorithm": "invalid_algorithm"
        })
        assert response.status_code == 422

    def test_response_headers(self, client: TestClient):
        """Test that response headers are properly set."""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check for standard headers
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
        
        # Check for custom headers
        assert "x-request-id" in response.headers or "x-correlation-id" in response.headers
