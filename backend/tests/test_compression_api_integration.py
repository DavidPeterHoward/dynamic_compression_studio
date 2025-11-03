"""
Comprehensive Backend API Integration Tests for Compression Functionality

This module tests the complete compression API workflow including content analysis,
algorithm recommendations, compression execution, and result validation.
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from fastapi import FastAPI
from app.main import app as fastapi_app


class TestCompressionAPIIntegration:
    """Comprehensive compression API integration test suite."""
    
    @pytest.fixture(scope="class")
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
            yield client

    # ==================== CONTENT ANALYSIS TESTS ====================
    
    @pytest.mark.asyncio
    async def test_content_analysis_workflow(self, client: AsyncClient):
        """Test complete content analysis workflow."""
        test_content = "This is a sample text for compression analysis with repeated patterns for better compression results."
        
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": test_content,
                "options": {
                    "include_patterns": True,
                    "include_quality": True,
                    "include_predictions": True
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data
        
        analysis = data["analysis"]
        assert "content_type" in analysis
        assert "entropy" in analysis
        assert "compressibility" in analysis
        assert "predictions" in analysis
        
        return analysis

    @pytest.mark.asyncio
    async def test_algorithm_recommendations_workflow(self, client: AsyncClient):
        """Test algorithm recommendations workflow."""
        # First get content analysis
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": "Sample content for algorithm recommendations testing.",
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
                },
                "meta_learning_context": {
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "historical_data": True
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
        
        return data["recommendations"]

    # ==================== COMPRESSION EXECUTION TESTS ====================
    
    @pytest.mark.asyncio
    async def test_compression_execution_workflow(self, client: AsyncClient):
        """Test complete compression execution workflow."""
        test_content = "This is a comprehensive test content for compression execution with repeated patterns and structures for optimal compression results."
        
        # Step 1: Analyze content
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": test_content,
                "options": {
                    "include_patterns": True,
                    "include_quality": True,
                    "include_predictions": True
                }
            }
        )
        assert analysis_response.status_code == 200
        content_analysis = analysis_response.json()["analysis"]
        
        # Step 2: Get recommendations
        recommendations_response = await client.post(
            "/api/v1/compression/enhanced/recommendations",
            json={
                "content_analysis": content_analysis,
                "user_preferences": {
                    "speed_vs_compression": 0.6,
                    "quality_vs_size": 0.7,
                    "compatibility_vs_performance": 0.8
                }
            }
        )
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()["recommendations"]
        
        # Step 3: Execute compression with recommended algorithm
        best_algorithm = recommendations[0]["algorithm"]
        compression_response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": test_content,
                "content_analysis": content_analysis,
                "algorithm": {
                    "name": best_algorithm["name"],
                    "parameters": best_algorithm["parameters"]
                },
                "options": {
                    "include_metrics": True,
                    "include_predictions": True,
                    "include_quality": True,
                    "track_experiment": True
                }
            }
        )
        
        assert compression_response.status_code == 200
        data = compression_response.json()
        assert data["success"] is True
        assert "result" in data
        
        result = data["result"]
        assert "compressed_content" in result
        assert "compression_ratio" in result
        assert "compression_percentage" in result
        assert "processing_time" in result
        assert "algorithm_used" in result
        
        # Verify compression actually occurred
        assert result["compression_ratio"] > 1.0
        assert result["compression_percentage"] > 0
        assert len(result["compressed_content"]) < len(test_content)
        
        return result

    @pytest.mark.asyncio
    async def test_multiple_algorithm_compression(self, client: AsyncClient):
        """Test compression with multiple algorithms."""
        test_content = "Multi-algorithm test content with patterns for compression analysis."
        
        # Get content analysis
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={"content": test_content, "options": {}}
        )
        content_analysis = analysis_response.json()["analysis"]
        
        algorithms = ["gzip", "brotli", "lz4", "zstd"]
        results = []
        
        for algorithm in algorithms:
            response = await client.post(
                "/api/v1/compression/enhanced/compress-enhanced",
                json={
                    "content": test_content,
                    "content_analysis": content_analysis,
                    "algorithm": {
                        "name": algorithm,
                        "parameters": {"level": 6}
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
            results.append(data["result"])
        
        # Verify all algorithms produced different results
        assert len(set(r["algorithm_used"] for r in results)) == len(algorithms)
        
        # Verify compression ratios are reasonable
        for result in results:
            assert result["compression_ratio"] > 1.0
            assert result["compression_percentage"] > 0
        
        return results

    # ==================== REAL-TIME METRICS TESTS ====================
    
    @pytest.mark.asyncio
    async def test_real_time_metrics(self, client: AsyncClient):
        """Test real-time metrics endpoint."""
        response = await client.get("/api/v1/compression/enhanced/metrics/real-time")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "throughput" in data
        assert "active_connections" in data
        
        # Verify metrics are within reasonable ranges
        assert 0 <= data["cpu_usage"] <= 100
        assert 0 <= data["memory_usage"] <= 100
        assert data["throughput"] >= 0

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
        assert "current_iteration" in data

    # ==================== BATCH PROCESSING TESTS ====================
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, client: AsyncClient):
        """Test batch processing functionality."""
        batch_items = [
            {"id": "item1", "content": "First batch item for processing"},
            {"id": "item2", "content": "Second batch item for processing"},
            {"id": "item3", "content": "Third batch item for processing"}
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
        
        # Verify all items were processed
        for result in data["results"]:
            assert result["status"] == "completed"
            assert "result" in result or "error" in result

    # ==================== ERROR HANDLING TESTS ====================
    
    @pytest.mark.asyncio
    async def test_error_handling_empty_content(self, client: AsyncClient):
        """Test error handling for empty content."""
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={"content": "", "options": {}}
        )
        
        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_error_handling_invalid_algorithm(self, client: AsyncClient):
        """Test error handling for invalid algorithm."""
        test_content = "Test content for invalid algorithm testing."
        
        # Get content analysis
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={"content": test_content, "options": {}}
        )
        content_analysis = analysis_response.json()["analysis"]
        
        # Try compression with invalid algorithm
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": test_content,
                "content_analysis": content_analysis,
                "algorithm": {
                    "name": "invalid_algorithm",
                    "parameters": {}
                }
            }
        )
        
        # Should return error
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_error_handling_malformed_request(self, client: AsyncClient):
        """Test error handling for malformed requests."""
        response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": "Test content"
                # Missing required fields
            }
        )
        
        # Should return validation error
        assert response.status_code == 422

    # ==================== PERFORMANCE TESTS ====================
    
    @pytest.mark.asyncio
    async def test_compression_performance(self, client: AsyncClient):
        """Test compression performance with large content."""
        large_content = "A" * 10000  # 10KB of content
        
        start_time = asyncio.get_event_loop().time()
        
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
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify performance is within acceptable limits
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert data["result"]["processing_time"] < 5.0

    @pytest.mark.asyncio
    async def test_concurrent_compression_requests(self, client: AsyncClient):
        """Test handling of concurrent compression requests."""
        test_content = "Concurrent test content for multiple simultaneous compressions."
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = client.post(
                "/api/v1/compression/enhanced/compress-enhanced",
                json={
                    "content": f"{test_content} {i}",
                    "algorithm": {
                        "name": "gzip",
                        "parameters": {"level": 6}
                    }
                }
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    # ==================== INTEGRATION TESTS ====================
    
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, client: AsyncClient):
        """Test complete workflow integration from analysis to compression."""
        test_content = "Complete workflow integration test content with comprehensive analysis and compression requirements."
        
        # Step 1: Content Analysis
        analysis_response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": test_content,
                "options": {
                    "include_patterns": True,
                    "include_quality": True,
                    "include_predictions": True
                }
            }
        )
        assert analysis_response.status_code == 200
        content_analysis = analysis_response.json()["analysis"]
        
        # Step 2: Algorithm Recommendations
        recommendations_response = await client.post(
            "/api/v1/compression/enhanced/recommendations",
            json={
                "content_analysis": content_analysis,
                "user_preferences": {
                    "speed_vs_compression": 0.5,
                    "quality_vs_size": 0.7,
                    "compatibility_vs_performance": 0.8
                }
            }
        )
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()["recommendations"]
        
        # Step 3: Compression Execution
        best_algorithm = recommendations[0]["algorithm"]
        compression_response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": test_content,
                "content_analysis": content_analysis,
                "algorithm": {
                    "name": best_algorithm["name"],
                    "parameters": best_algorithm["parameters"]
                },
                "options": {
                    "include_metrics": True,
                    "include_predictions": True,
                    "include_quality": True,
                    "track_experiment": True
                }
            }
        )
        assert compression_response.status_code == 200
        compression_result = compression_response.json()["result"]
        
        # Step 4: Verify Results
        assert compression_result["compression_ratio"] > 1.0
        assert compression_result["compression_percentage"] > 0
        assert len(compression_result["compressed_content"]) < len(test_content)
        assert compression_result["algorithm_used"] == best_algorithm["name"]
        
        # Step 5: Verify Metrics
        assert "metrics" in compression_response.json()
        metrics = compression_response.json()["metrics"]
        assert "performance" in metrics
        assert "efficiency" in metrics
        assert "quality" in metrics
        
        # Step 6: Verify Analysis
        assert "analysis" in compression_response.json()
        analysis = compression_response.json()["analysis"]
        assert "predictedVsActual" in analysis
        assert "qualityAssessment" in analysis
        
        return {
            "content_analysis": content_analysis,
            "recommendations": recommendations,
            "compression_result": compression_result
        }

    # ==================== DATA VALIDATION TESTS ====================
    
    @pytest.mark.asyncio
    async def test_data_validation_and_sanitization(self, client: AsyncClient):
        """Test data validation and sanitization."""
        # Test with potentially malicious content
        malicious_content = "<script>alert('xss')</script>'; DROP TABLE users; --"
        
        response = await client.post(
            "/api/v1/compression/enhanced/analyze-content",
            json={
                "content": malicious_content,
                "options": {}
            }
        )
        
        # Should handle malicious content gracefully
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Test compression with malicious content
        compression_response = await client.post(
            "/api/v1/compression/enhanced/compress-enhanced",
            json={
                "content": malicious_content,
                "algorithm": {
                    "name": "gzip",
                    "parameters": {"level": 6}
                }
            }
        )
        
        assert compression_response.status_code == 200
        compression_data = compression_response.json()
        assert compression_data["success"] is True
        
        # Verify content was processed safely
        assert len(compression_data["result"]["compressed_content"]) > 0

    # ==================== EDGE CASE TESTS ====================
    
    @pytest.mark.asyncio
    async def test_edge_cases(self, client: AsyncClient):
        """Test various edge cases."""
        edge_cases = [
            "a",  # Single character
            "A" * 100000,  # Very long repeated content
            "🚀🌟💫✨🎉",  # Unicode emojis
            "\n\t\r " * 1000,  # Whitespace
            "null\0\x00",  # Null characters
        ]
        
        for content in edge_cases:
            response = await client.post(
                "/api/v1/compression/enhanced/compress-enhanced",
                json={
                    "content": content,
                    "algorithm": {
                        "name": "gzip",
                        "parameters": {"level": 6}
                    }
                }
            )
            
            # Should handle edge cases gracefully
            assert response.status_code in [200, 400, 422]  # Either success or appropriate error
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "result" in data
