"""
Unit tests for health check endpoints.

This module tests the health check functionality including basic health,
readiness, liveness, detailed health, and status endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    def test_health_basic(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"

    def test_health_readiness(self, client: TestClient):
        """Test readiness health check endpoint."""
        response = client.get("/api/v1/health/readiness")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] in ["ready", "not_ready"]

    def test_health_liveness(self, client: TestClient):
        """Test liveness health check endpoint."""
        response = client.get("/api/v1/health/liveness")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "alive"

    def test_health_detailed(self, client: TestClient):
        """Test detailed health check endpoint."""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "system_info" in data
        assert "performance_metrics" in data
        assert "resource_usage" in data

    def test_health_status(self, client: TestClient):
        """Test status health check endpoint."""
        response = client.get("/api/v1/health/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "app_name" in data

    def test_health_endpoints_content_type(self, client: TestClient):
        """Test that all health endpoints return JSON content type."""
        endpoints = [
            "/health",
            "/api/v1/health/readiness",
            "/api/v1/health/liveness",
            "/api/v1/health/detailed",
            "/api/v1/health/status"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"

    def test_health_endpoints_response_time(self, client: TestClient):
        """Test that health endpoints respond quickly."""
        import time
        
        endpoints = [
            "/health",
            "/api/v1/health/readiness",
            "/api/v1/health/liveness",
            "/api/v1/health/status"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 1.0  # Should respond within 1 second

    def test_health_detailed_response_time(self, client: TestClient):
        """Test that detailed health endpoint responds within reasonable time."""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/health/detailed")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds

    def test_health_endpoints_method_not_allowed(self, client: TestClient):
        """Test that health endpoints only accept GET requests."""
        endpoints = [
            "/health",
            "/api/v1/health/readiness",
            "/api/v1/health/liveness",
            "/api/v1/health/detailed",
            "/api/v1/health/status"
        ]
        
        for endpoint in endpoints:
            # Test POST
            response = client.post(endpoint)
            assert response.status_code == 405
            
            # Test PUT
            response = client.put(endpoint)
            assert response.status_code == 405
            
            # Test DELETE
            response = client.delete(endpoint)
            assert response.status_code == 405

    def test_health_endpoints_with_headers(self, client: TestClient):
        """Test health endpoints with various headers."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "test-client"
        }
        
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_endpoints_error_handling(self, client: TestClient):
        """Test health endpoints handle errors gracefully."""
        # Test with invalid endpoint
        response = client.get("/api/v1/health/invalid")
        assert response.status_code == 404
        
        # Test with malformed request (should still work for GET)
        response = client.get("/health", headers={"Invalid-Header": "invalid"})
        assert response.status_code == 200
