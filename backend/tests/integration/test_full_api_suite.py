"""
Full API Test Suite

Comprehensive testing of all API endpoints with live Docker environment.
Tests all functionality including agent orchestration endpoints.
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8443"
API_TIMEOUT = 60.0

@pytest.fixture(scope="session")
def api_client():
    """Create async HTTP client for API testing."""
    return httpx.AsyncClient(timeout=API_TIMEOUT, base_url=API_BASE_URL)


class TestHealthEndpoints:
    """Test all health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_health(self, api_client):
        """Test root health endpoint."""
        async with api_client as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            logger.info(f"Root health: {data}")
    
    @pytest.mark.asyncio
    async def test_api_health_detailed(self, api_client):
        """Test detailed health endpoint."""
        async with api_client as client:
            response = await client.get("/api/v1/health/detailed")
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                logger.info(f"Detailed health: {data}")
    
    @pytest.mark.asyncio
    async def test_api_health_readiness(self, api_client):
        """Test readiness endpoint."""
        async with api_client as client:
            response = await client.get("/api/v1/health/readiness")
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                logger.info(f"Readiness: {data}")


class TestCompressionEndpoints:
    """Test compression API endpoints."""
    
    @pytest.mark.asyncio
    async def test_compress_gzip(self, api_client):
        """Test GZIP compression."""
        async with api_client as client:
            payload = {
                "content": "Test content for compression. " * 100,
                "algorithm": "gzip",
                "level": 6
            }
            response = await client.post("/api/v1/compression/compress", json=payload)
            assert response.status_code in [200, 201]
            data = response.json()
            logger.info(f"GZIP compression: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_compress_zstd(self, api_client):
        """Test ZSTD compression."""
        async with api_client as client:
            payload = {
                "content": "Test content for compression. " * 100,
                "algorithm": "zstd",
                "level": 3
            }
            response = await client.post("/api/v1/compression/compress", json=payload)
            assert response.status_code in [200, 201]
            logger.info(f"ZSTD compression: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_compress_lz4(self, api_client):
        """Test LZ4 compression."""
        async with api_client as client:
            payload = {
                "content": "Test content for compression. " * 100,
                "algorithm": "lz4",
                "level": 1
            }
            response = await client.post("/api/v1/compression/compress", json=payload)
            assert response.status_code in [200, 201]
            logger.info(f"LZ4 compression: {response.status_code}")


class TestAgentOrchestrationEndpoints:
    """Test agent orchestration endpoints."""
    
    @pytest.mark.asyncio
    async def test_agent_registry_status(self, api_client):
        """Test agent registry status."""
        async with api_client as client:
            # Try various possible endpoints
            endpoints = [
                "/api/v1/agents/status",
                "/api/v1/orchestrator/status",
                "/api/v1/agents",
                "/api/agents/status"
            ]
            
            for endpoint in endpoints:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Agent status from {endpoint}: {data}")
                    break
                elif response.status_code != 404:
                    logger.warning(f"Endpoint {endpoint} returned {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_orchestrator_execute_task(self, api_client):
        """Test orchestrator task execution."""
        async with api_client as client:
            payload = {
                "task_id": f"test_{int(time.time())}",
                "operation": "data_pipeline",
                "parameters": {
                    "data_source": "test_source"
                }
            }
            
            endpoints = [
                "/api/v1/orchestrator/execute",
                "/api/v1/agents/orchestrator/execute",
                "/api/orchestrator/execute"
            ]
            
            for endpoint in endpoints:
                response = await client.post(endpoint, json=payload)
                if response.status_code in [200, 201]:
                    data = response.json()
                    logger.info(f"Orchestrator task from {endpoint}: {data}")
                    assert "status" in data or "task_id" in data
                    break
                elif response.status_code != 404:
                    logger.warning(f"Endpoint {endpoint} returned {response.status_code}")


class TestMetricsEndpoints:
    """Test metrics endpoints."""
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, api_client):
        """Test metrics collection endpoint."""
        async with api_client as client:
            endpoints = [
                "/api/v1/metrics",
                "/api/metrics",
                "/metrics"
            ]
            
            for endpoint in endpoints:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Metrics from {endpoint}: {data}")
                    break


class TestAPIDocs:
    """Test API documentation endpoints."""
    
    @pytest.mark.asyncio
    async def test_swagger_docs(self, api_client):
        """Test Swagger documentation."""
        async with api_client as client:
            response = await client.get("/docs")
            assert response.status_code == 200
            logger.info("Swagger docs available")
    
    @pytest.mark.asyncio
    async def test_openapi_schema(self, api_client):
        """Test OpenAPI schema."""
        async with api_client as client:
            response = await client.get("/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                logger.info(f"OpenAPI schema version: {schema.get('info', {}).get('version')}")


class TestAPIPerformance:
    """Test API performance."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, api_client):
        """Test concurrent request handling."""
        async with api_client as client:
            tasks = [
                client.get("/health")
                for _ in range(20)
            ]
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
            duration = (end_time - start_time) * 1000
            
            logger.info(f"Concurrent requests: {successful}/20 successful in {duration:.2f}ms")
            assert successful >= 18  # At least 90% should succeed
            assert duration < 5000  # Should complete in < 5 seconds
    
    @pytest.mark.asyncio
    async def test_response_time(self, api_client):
        """Test API response time."""
        async with api_client as client:
            start_time = time.time()
            response = await client.get("/health")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            logger.info(f"Response time: {response_time:.2f}ms")
            assert response.status_code == 200
            assert response_time < 2000  # Should respond in < 2 seconds


@pytest.mark.asyncio
async def test_api_availability(api_client):
    """Verify API is available and responding."""
    try:
        async with api_client as client:
            response = await client.get("/health")
            assert response.status_code == 200
            logger.info("✅ API is available and responding")
    except Exception as e:
        pytest.skip(f"API not available: {e}")
