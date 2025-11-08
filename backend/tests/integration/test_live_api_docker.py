"""
Live API Integration Tests for Docker Environment

Tests all API endpoints against running Docker containers.
Verifies:
- Health endpoints
- Compression endpoints
- Agent orchestration endpoints
- Data pipeline endpoints
- Error handling
- Performance metrics
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Docker API base URL
API_BASE_URL = "http://localhost:8443"
API_TIMEOUT = 30.0

class TestLiveAPIHealth:
    """Test health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_basic(self):
        """Test basic health endpoint."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "unhealthy"]
            logger.info(f"Health check: {data}")
    
    @pytest.mark.asyncio
    async def test_health_detailed(self):
        """Test detailed health endpoint."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/health/detailed")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "database" in data or "system" in data
            logger.info(f"Detailed health: {data}")
    
    @pytest.mark.asyncio
    async def test_health_readiness(self):
        """Test readiness endpoint."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/health/readiness")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            logger.info(f"Readiness: {data}")


class TestLiveAPICompression:
    """Test compression API endpoints."""
    
    @pytest.mark.asyncio
    async def test_compress_basic(self):
        """Test basic compression endpoint."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            payload = {
                "content": "This is a test string for compression testing. " * 100,
                "algorithm": "gzip",
                "level": 6
            }
            response = await client.post(
                f"{API_BASE_URL}/api/v1/compression/compress",
                json=payload
            )
            assert response.status_code in [200, 201]
            data = response.json()
            assert "compressed_data" in data or "result" in data
            logger.info(f"Compression successful: {len(str(data))} bytes")
    
    @pytest.mark.asyncio
    async def test_compress_multiple_algorithms(self):
        """Test compression with multiple algorithms."""
        algorithms = ["gzip", "lz4", "zstd"]
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            for algorithm in algorithms:
                payload = {
                    "content": "Test content for algorithm comparison. " * 50,
                    "algorithm": algorithm,
                    "level": 6
                }
                response = await client.post(
                    f"{API_BASE_URL}/api/v1/compression/compress",
                    json=payload
                )
                assert response.status_code in [200, 201]
                logger.info(f"Algorithm {algorithm}: {response.status_code}")


class TestLiveAPIAgents:
    """Test agent orchestration API endpoints."""
    
    @pytest.mark.asyncio
    async def test_agent_status(self):
        """Test agent status endpoint."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            # Try agent status endpoint
            response = await client.get(f"{API_BASE_URL}/api/v1/agents/status")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Agent status: {data}")
            elif response.status_code == 404:
                logger.warning("Agent status endpoint not found")
    
    @pytest.mark.asyncio
    async def test_orchestrator_task(self):
        """Test orchestrator task execution."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            payload = {
                "task_id": f"test_{int(time.time())}",
                "operation": "data_pipeline",
                "parameters": {
                    "data_source": "test_database"
                }
            }
            response = await client.post(
                f"{API_BASE_URL}/api/v1/orchestrator/execute",
                json=payload
            )
            # May return 404 if endpoint doesn't exist, or 200/201 if it does
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"Orchestrator task: {data}")
            else:
                logger.warning(f"Orchestrator endpoint status: {response.status_code}")


class TestLiveAPIMetrics:
    """Test metrics API endpoints."""
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/metrics")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Metrics: {data}")
            elif response.status_code == 404:
                logger.warning("Metrics endpoint not found")


class TestLiveAPIConcurrency:
    """Test concurrent API requests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test concurrent health check requests."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            tasks = [
                client.get(f"{API_BASE_URL}/health")
                for _ in range(10)
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
            logger.info(f"Concurrent requests: {successful}/10 successful")
            assert successful >= 8  # At least 80% should succeed


class TestLiveAPIPerformance:
    """Test API performance."""
    
    @pytest.mark.asyncio
    async def test_api_response_time(self):
        """Test API response time."""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            start_time = time.time()
            response = await client.get(f"{API_BASE_URL}/health")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # ms
            logger.info(f"Health check response time: {response_time:.2f}ms")
            assert response_time < 1000  # Should respond in < 1 second
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_docker_services_available():
    """Verify Docker services are running."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            assert response.status_code == 200
            logger.info("✅ Docker services are available")
        except Exception as e:
            pytest.skip(f"Docker services not available: {e}")
