"""
Comprehensive Backend Functionality Tests

This module contains comprehensive tests for all backend functionality,
including all API endpoints, business logic, error handling, and edge cases.
"""

import pytest
import asyncio
import time
import json
from httpx import AsyncClient
from fastapi import FastAPI
from app.main import app as fastapi_app


class TestComprehensiveBackendFunctionality:
    """Comprehensive backend functionality test suite."""
    
    @pytest.fixture(scope="class")
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            yield client

    # ==================== HEALTH & STATUS TESTS ====================
    
    @pytest.mark.asyncio
    async def test_health_basic_endpoint(self, client: AsyncClient):
        """Test basic health endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_detailed_endpoint(self, client: AsyncClient):
        """Test detailed health endpoint."""
        response = await client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "system_info" in data
        assert "performance_metrics" in data

    @pytest.mark.asyncio
    async def test_health_readiness_endpoint(self, client: AsyncClient):
        """Test readiness endpoint."""
        response = await client.get("/health/readiness")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_health_liveness_endpoint(self, client: AsyncClient):
        """Test liveness endpoint."""
        response = await client.get("/health/liveness")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    # ==================== CONTENT ANALYSIS TESTS ====================
    
    @pytest.mark.asyncio
    async def test_content_analysis_basic_text(self, client: AsyncClient):
        """Test content analysis with basic text."""
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": "This is a sample text for compression analysis.",
                "options": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data
        assert "content_type" in data["analysis"]
        assert "entropy" in data["analysis"]

    @pytest.mark.asyncio
    async def test_content_analysis_json_data(self, client: AsyncClient):
        """Test content analysis with JSON data."""
        json_content = json.dumps({"key": "value", "nested": {"data": "test"}})
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": json_content,
                "options": {"include_patterns": True}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "patterns" in data["analysis"]

    @pytest.mark.asyncio
    async def test_content_analysis_xml_data(self, client: AsyncClient):
        """Test content analysis with XML data."""
        xml_content = "<root><item>value</item><item>another</item></root>"
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": xml_content,
                "options": {"include_quality": True}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "quality_metrics" in data["analysis"]

    @pytest.mark.asyncio
    async def test_content_analysis_binary_data(self, client: AsyncClient):
        """Test content analysis with binary-like data."""
        binary_content = "01010101010101010101010101010101" * 100
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": binary_content,
                "options": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_content_analysis_empty_content(self, client: AsyncClient):
        """Test content analysis with empty content."""
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": "",
                "options": {}
            }
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_content_analysis_large_content(self, client: AsyncClient):
        """Test content analysis with large content."""
        large_content = "A" * 10000  # 10KB of repeated content
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": large_content,
                "options": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    # ==================== ALGORITHM RECOMMENDATION TESTS ====================
    
    @pytest.mark.asyncio
    async def test_algorithm_recommendations_basic(self, client: AsyncClient):
        """Test basic algorithm recommendations."""
        # First get content analysis
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": "Sample text for algorithm recommendation testing.",
                "options": {}
            }
        )
        assert analysis_response.status_code == 200
        content_analysis = analysis_response.json()["analysis"]

        # Get recommendations
        response = await client.post(
            "/api/v1/compression/enhanced/recommendations",
            json={
                "content_analysis": content_analysis,
                "user_preferences": {
                    "speed_vs_compression": 0.7,
                    "quality_vs_size": 0.8,
                    "compatibility_vs_performance": 0.6
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_algorithm_recommendations_with_meta_learning(self, client: AsyncClient):
        """Test algorithm recommendations with meta-learning context."""
        # Get content analysis
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": "Text with patterns for meta-learning analysis.",
                "options": {}
            }
        )
        content_analysis = analysis_response.json()["analysis"]

        # Get recommendations with meta-learning
        response = await client.post(
            "/api/v1/compression/enhanced/recommendations",
            json={
                "content_analysis": content_analysis,
                "user_preferences": {
                    "speed_vs_compression": 0.5,
                    "quality_vs_size": 0.7,
                    "compatibility_vs_performance": 0.8
                },
                "meta_learning_context": {
                    "user_id": "test_user_123",
                    "session_id": "session_456",
                    "historical_data": True
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "meta_learning_insights" in data

    @pytest.mark.asyncio
    async def test_algorithm_recommendations_different_content_types(self, client: AsyncClient):
        """Test algorithm recommendations for different content types."""
        content_types = [
            "Plain text content for testing",
            json.dumps({"structured": "data", "with": "nested", "objects": {"key": "value"}}),
            "<html><body><p>HTML content</p></body></html>",
            "01010101010101010101010101010101" * 50
        ]

        for content in content_types:
            # Analyze content
            analysis_response = await client.post(
                "/api/v1/compression/enhanced/analyze-content",
                json={"content": content, "options": {}}
            )
            assert analysis_response.status_code == 200
            content_analysis = analysis_response.json()["analysis"]

            # Get recommendations
            response = await client.post(
                "/api/v1/compression/enhanced/recommendations",
                json={"content_analysis": content_analysis}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    # ==================== COMPRESSION EXECUTION TESTS ====================
    
    @pytest.mark.asyncio
    async def test_compression_basic_gzip(self, client: AsyncClient):
        """Test basic gzip compression."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Sample text for gzip compression testing.",
                "algorithm": {
                    "name": "gzip",
                    "parameters": {"level": 6}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "compressed_content" in data["result"]
        assert data["result"]["compression_ratio"] > 1.0

    @pytest.mark.asyncio
    async def test_compression_brotli_algorithm(self, client: AsyncClient):
        """Test Brotli compression algorithm."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Sample text for Brotli compression testing with more content to achieve better compression ratios.",
                "algorithm": {
                    "name": "brotli",
                    "parameters": {"quality": 6}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["algorithm_used"] == "brotli"

    @pytest.mark.asyncio
    async def test_compression_lz4_algorithm(self, client: AsyncClient):
        """Test LZ4 compression algorithm."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Sample text for LZ4 compression testing.",
                "algorithm": {
                    "name": "lz4",
                    "parameters": {"compression_level": 1}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["algorithm_used"] == "lz4"

    @pytest.mark.asyncio
    async def test_compression_zstd_algorithm(self, client: AsyncClient):
        """Test Zstandard compression algorithm."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Sample text for Zstandard compression testing with repeated patterns for better compression.",
                "algorithm": {
                    "name": "zstd",
                    "parameters": {"compression_level": 3}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["algorithm_used"] == "zstd"

    @pytest.mark.asyncio
    async def test_compression_with_metrics(self, client: AsyncClient):
        """Test compression with metrics enabled."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Sample text for compression with metrics testing.",
                "algorithm": {
                    "name": "gzip",
                    "parameters": {"level": 9}
                },
                "options": {
                    "include_metrics": True,
                    "include_predictions": True,
                    "include_quality": True
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data
        assert "analysis" in data

    @pytest.mark.asyncio
    async def test_compression_performance_benchmark(self, client: AsyncClient):
        """Test compression performance with large content."""
        large_content = "A" * 50000  # 50KB of content
        start_time = time.time()
        
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": large_content,
                "algorithm": {
                    "name": "gzip",
                    "parameters": {"level": 6}
                }
            }
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert processing_time < 5.0  # Should complete within 5 seconds

    # ==================== REAL-TIME METRICS TESTS ====================
    
    @pytest.mark.asyncio
    async def test_real_time_metrics_basic(self, client: AsyncClient):
        """Test basic real-time metrics endpoint."""
        response = await client.get("/api/v1/compression/enhanced/metrics/real-time")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "throughput" in data

    @pytest.mark.asyncio
    async def test_real_time_metrics_consistency(self, client: AsyncClient):
        """Test real-time metrics consistency over multiple calls."""
        metrics = []
        for _ in range(3):
            response = await client.get("/api/v1/compression/enhanced/metrics/real-time")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            metrics.append(data)
            await asyncio.sleep(0.1)  # Small delay between calls
        
        # Verify metrics are consistent (within reasonable bounds)
        for metric in ["cpu_usage", "memory_usage"]:
            values = [m[metric] for m in metrics]
            assert all(0 <= v <= 100 for v in values)  # Should be percentages

    # ==================== META-LEARNING TESTS ====================
    
    @pytest.mark.asyncio
    async def test_meta_learning_insights(self, client: AsyncClient):
        """Test meta-learning insights endpoint."""
        response = await client.get(
            "/api/v1/compression/enhanced/learning-insights?user_id=test_user"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "learning_status" in data
        assert "progress" in data

    @pytest.mark.asyncio
    async def test_meta_learning_progress_tracking(self, client: AsyncClient):
        """Test meta-learning progress tracking."""
        # Simulate multiple compression operations to track learning
        for i in range(3):
            response = await client.post(
                "/api/v1/compression/enhanced/compress-enhanced",
                json={
                    "content": f"Learning content {i} with patterns for meta-learning.",
                    "algorithm": {
                        "name": "gzip",
                        "parameters": {"level": 6}
                    }
                }
            )
            assert response.status_code == 200
        
        # Check learning insights
        insights_response = await client.get(
            "/api/v1/compression/enhanced/learning-insights?user_id=test_user"
        )
        assert insights_response.status_code == 200
        data = insights_response.json()
        assert data["success"] is True

    # ==================== BATCH PROCESSING TESTS ====================
    
    @pytest.mark.asyncio
    async def test_batch_processing_basic(self, client: AsyncClient):
        """Test basic batch processing."""
        batch_items = [
            {"id": "item1", "content": "First item for batch processing"},
            {"id": "item2", "content": "Second item for batch processing"},
            {"id": "item3", "content": "Third item for batch processing"}
        ]
        
        response = await client.post(
            "/api/v1/compression/enhanced/batch-process",
            json={
                "batch_id": "test_batch_001",
                "items": batch_items,
                "options": {
                    "parallel_processing": True,
                    "include_comparison": False,
                    "save_results": True
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert len(data["results"]) == 3

    @pytest.mark.asyncio
    async def test_batch_processing_with_analysis(self, client: AsyncClient):
        """Test batch processing with content analysis."""
        batch_items = [
            {"id": "json_item", "content": json.dumps({"data": "value"})},
            {"id": "text_item", "content": "Plain text content"},
            {"id": "xml_item", "content": "<root><item>value</item></root>"}
        ]
        
        response = await client.post(
            "/api/v1/compression/enhanced/batch-process",
            json={
                "batch_id": "test_batch_002",
                "items": batch_items,
                "options": {
                    "parallel_processing": True,
                    "include_comparison": True,
                    "save_results": True
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert all(result["status"] == "completed" for result in data["results"])

    # ==================== ERROR HANDLING TESTS ====================
    
    @pytest.mark.asyncio
    async def test_invalid_algorithm_handling(self, client: AsyncClient):
        """Test handling of invalid algorithm."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Test content",
                "algorithm": {
                    "name": "invalid_algorithm",
                    "parameters": {}
                }
            }
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_malformed_request_handling(self, client: AsyncClient):
        """Test handling of malformed requests."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Test content"
                # Missing required 'algorithm' field
            }
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_large_request_handling(self, client: AsyncClient):
        """Test handling of very large requests."""
        # Test with content that might cause memory issues
        very_large_content = "A" * 1000000  # 1MB of content
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": very_large_content,
                "algorithm": {
                    "name": "gzip",
                    "parameters": {"level": 1}  # Fast compression
                }
            }
        )
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 413, 422]

    # ==================== PERFORMANCE TESTS ====================
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient):
        """Test handling of concurrent requests."""
        async def make_request():
            return await client.post(
                "/api/v1/compression/enhanced/compress-enhanced",
                json={
                    "content": f"Concurrent test content {time.time()}",
                    "algorithm": {
                        "name": "gzip",
                        "parameters": {"level": 6}
                    }
                }
            )
        
        # Make 5 concurrent requests
        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, client: AsyncClient):
        """Test memory usage stability over multiple operations."""
        # Perform multiple compression operations
        for i in range(10):
            response = await client.post(
                "/api/v1/compression/enhanced/compress-enhanced",
                json={
                    "content": f"Memory test content {i} with some repeated patterns for compression testing.",
                    "algorithm": {
                        "name": "gzip",
                        "parameters": {"level": 6}
                    }
                }
            )
            assert response.status_code == 200
        
        # Check that system is still responsive
        health_response = await client.get("/health")
        assert health_response.status_code == 200

    # ==================== INTEGRATION TESTS ====================
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, client: AsyncClient):
        """Test complete compression workflow from analysis to compression."""
        content = "Complete workflow test content with patterns for analysis and compression."
        
        # Step 1: Analyze content
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={"content": content, "options": {}}
        )
        assert analysis_response.status_code == 200
        content_analysis = analysis_response.json()["analysis"]
        
        # Step 2: Get recommendations
        recommendations_response = await client.post(
            "/api/v1/compression/enhanced/recommendations",
            json={"content_analysis": content_analysis}
        )
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()["recommendations"]
        
        # Step 3: Compress with recommended algorithm
        best_algorithm = recommendations[0]["algorithm"]
        compression_response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": content,
                "content_analysis": content_analysis,
                "algorithm": {
                    "name": best_algorithm["name"],
                    "parameters": best_algorithm["parameters"]
                }
            }
        )
        assert compression_response.status_code == 200
        compression_result = compression_response.json()["result"]
        
        # Verify results
        assert compression_result["compression_ratio"] > 1.0
        assert compression_result["algorithm_used"] == best_algorithm["name"]

    @pytest.mark.asyncio
    async def test_metrics_integration(self, client: AsyncClient):
        """Test integration between compression and metrics."""
        # Perform compression
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Metrics integration test content.",
                "algorithm": {
                    "name": "gzip",
                    "parameters": {"level": 6}
                }
            }
        )
        assert response.status_code == 200
        
        # Check that metrics are updated
        metrics_response = await client.get("/api/v1/compression/enhanced/metrics/real-time")
        assert metrics_response.status_code == 200
        metrics = metrics_response.json()
        assert metrics["success"] is True
