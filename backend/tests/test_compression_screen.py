"""
Comprehensive tests for the compression screen functionality.

This module tests all aspects of the compression screen including:
- Content analysis
- Algorithm recommendations
- Compression execution
- Results display
- Error handling
- Performance metrics
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the main app and services
from app.main import app
from app.services.content_analysis import ContentAnalysisService
from app.services.algorithm_recommender import AlgorithmRecommender
from app.services.meta_learning import MetaLearningService

class TestCompressionScreen:
    """Test class for compression screen functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return {
            "short_text": "This is a short test text.",
            "long_text": "This is a much longer test text that contains more content for compression testing. " * 50,
            "json_content": '{"name": "test", "value": 123, "data": [1, 2, 3, 4, 5]}',
            "xml_content": "<root><item>test</item><item>data</item></root>",
            "code_content": """
def test_function():
    '''This is a test function'''
    result = 0
    for i in range(100):
        result += i
    return result
            """.strip()
        }
    
    @pytest.fixture
    def content_analysis_service(self):
        """Content analysis service fixture."""
        return ContentAnalysisService()
    
    @pytest.fixture
    def algorithm_recommender(self):
        """Algorithm recommender service fixture."""
        return AlgorithmRecommender()
    
    @pytest.fixture
    def meta_learning_service(self):
        """Meta-learning service fixture."""
        return MetaLearningService()

    @pytest.mark.asyncio
    async def test_content_analysis_endpoint(self, client, sample_content):
        """Test content analysis API endpoint."""
        # Test with short text
        response = client.post("/api/v1/compression/enhanced/analyze-content", json={
            "content": sample_content["short_text"],
            "options": {
                "include_patterns": True,
                "include_quality": True,
                "include_predictions": True
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data
        assert "content_type" in data["analysis"]
        assert "entropy" in data["analysis"]
        assert "compressibility" in data["analysis"]
    
    @pytest.mark.asyncio
    async def test_content_analysis_different_types(self, client, sample_content):
        """Test content analysis with different content types."""
        content_types = ["short_text", "long_text", "json_content", "xml_content", "code_content"]
        
        for content_type in content_types:
            response = client.post("/api/v1/compression/enhanced/analyze-content", json={
                "content": sample_content[content_type],
                "options": {
                    "include_patterns": True,
                    "include_quality": True,
                    "include_predictions": True
                }
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["analysis"]["content_size"] > 0
    
    @pytest.mark.asyncio
    async def test_algorithm_recommendations_endpoint(self, client, sample_content):
        """Test algorithm recommendations API endpoint."""
        # First analyze content
        analysis_response = client.post("/api/v1/compression/enhanced/analyze-content", json={
            "content": sample_content["long_text"],
            "options": {
                "include_patterns": True,
                "include_quality": True,
                "include_predictions": True
            }
        })
        
        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()
        
        # Get recommendations
        response = client.post("/api/v1/compression/enhanced/recommendations", json={
            "content_analysis": analysis_data["analysis"],
            "user_preferences": {
                "speed_vs_compression": 0.6,
                "quality_vs_size": 0.7,
                "compatibility_vs_performance": 0.5
            },
            "meta_learning_context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "historical_data": True
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
        
        # Check recommendation structure
        recommendation = data["recommendations"][0]
        assert "algorithm" in recommendation
        assert "confidence" in recommendation
        assert "reasoning" in recommendation
        assert "expected_performance" in recommendation
    
    @pytest.mark.asyncio
    async def test_enhanced_compression_endpoint(self, client, sample_content):
        """Test enhanced compression API endpoint."""
        # First analyze content
        analysis_response = client.post("/api/v1/compression/enhanced/analyze-content", json={
            "content": sample_content["long_text"],
            "options": {
                "include_patterns": True,
                "include_quality": True,
                "include_predictions": True
            }
        })
        
        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()
        
        # Get recommendations
        recommendations_response = client.post("/api/v1/compression/enhanced/recommendations", json={
            "content_analysis": analysis_data["analysis"],
            "user_preferences": {
                "speed_vs_compression": 0.6,
                "quality_vs_size": 0.7,
                "compatibility_vs_performance": 0.5
            },
            "meta_learning_context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "historical_data": True
            }
        })
        
        assert recommendations_response.status_code == 200
        recommendations_data = recommendations_response.json()
        
        # Perform compression
        response = client.post("/api/v1/compression/enhanced/compress-enhanced", json={
            "content": sample_content["long_text"],
            "content_analysis": analysis_data["analysis"],
            "algorithm": {
                "name": recommendations_data["recommendations"][0]["algorithm"]["name"],
                "parameters": {
                    "level": 6
                }
            },
            "options": {
                "include_metrics": True,
                "include_predictions": True,
                "include_quality": True,
                "track_experiment": True
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "analysis" in data
        assert "metrics" in data
        
        # Check result structure
        result = data["result"]
        assert "compressed_content" in result
        assert "compression_ratio" in result
        assert "compression_percentage" in result
        assert "processing_time" in result
        assert "algorithm_used" in result
        
        # Check metrics
        metrics = data["metrics"]
        assert "performance" in metrics
        assert "efficiency" in metrics
        assert "quality" in metrics
    
    @pytest.mark.asyncio
    async def test_real_time_metrics_endpoint(self, client):
        """Test real-time metrics API endpoint."""
        response = client.get("/api/v1/compression/enhanced/metrics/real-time")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "real_time_metrics" in data
        
        metrics = data["real_time_metrics"]
        assert "system" in metrics
        assert "performance" in metrics
        assert "algorithms" in metrics
        
        # Check system metrics
        system_metrics = metrics["system"]
        assert "cpu_usage" in system_metrics
        assert "memory_usage" in system_metrics
        assert "disk_usage" in system_metrics
        
        # Check performance metrics
        performance_metrics = metrics["performance"]
        assert "throughput" in performance_metrics
        assert "success_rate" in performance_metrics
        assert "active_compressions" in performance_metrics
    
    @pytest.mark.asyncio
    async def test_health_endpoints(self, client):
        """Test health check endpoints."""
        # Test basic health
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        
        # Test detailed health
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "system_info" in data
        assert "performance_metrics" in data
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for various scenarios."""
        # Test empty content
        response = client.post("/api/v1/compression/enhanced/analyze-content", json={
            "content": "",
            "options": {}
        })
        assert response.status_code == 422
        
        # Test invalid algorithm
        response = client.post("/api/v1/compression/enhanced/compress-enhanced", json={
            "content": "test content",
            "content_analysis": {},
            "algorithm": {
                "name": "invalid_algorithm",
                "parameters": {}
            },
            "options": {}
        })
        # Should handle gracefully
        assert response.status_code in [200, 400, 500]
    
    @pytest.mark.asyncio
    async def test_compression_performance(self, client, sample_content):
        """Test compression performance with different content sizes."""
        content_sizes = [100, 1000, 10000, 100000]
        
        for size in content_sizes:
            content = sample_content["long_text"] * (size // len(sample_content["long_text"]) + 1)
            
            start_time = time.time()
            
            # Analyze content
            analysis_response = client.post("/api/v1/compression/enhanced/analyze-content", json={
                "content": content,
                "options": {
                    "include_patterns": True,
                    "include_quality": True,
                    "include_predictions": True
                }
            })
            
            assert analysis_response.status_code == 200
            analysis_data = analysis_response.json()
            
            # Get recommendations
            recommendations_response = client.post("/api/v1/compression/enhanced/recommendations", json={
                "content_analysis": analysis_data["analysis"],
                "user_preferences": {
                    "speed_vs_compression": 0.5,
                    "quality_vs_size": 0.5,
                    "compatibility_vs_performance": 0.5
                },
                "meta_learning_context": {}
            })
            
            assert recommendations_response.status_code == 200
            recommendations_data = recommendations_response.json()
            
            # Compress content
            compression_response = client.post("/api/v1/compression/enhanced/compress-enhanced", json={
                "content": content,
                "content_analysis": analysis_data["analysis"],
                "algorithm": {
                    "name": recommendations_data["recommendations"][0]["algorithm"]["name"],
                    "parameters": {"level": 6}
                },
                "options": {
                    "include_metrics": True,
                    "include_predictions": True,
                    "include_quality": True,
                    "track_experiment": True
                }
            })
            
            total_time = time.time() - start_time
            
            assert compression_response.status_code == 200
            compression_data = compression_response.json()
            
            # Verify compression results
            result = compression_data["result"]
            assert result["compression_ratio"] > 1.0
            assert result["compression_percentage"] > 0
            assert result["processing_time"] > 0
            
            # Performance should be reasonable
            assert total_time < 10.0  # Should complete within 10 seconds
    
    @pytest.mark.asyncio
    async def test_meta_learning_integration(self, client, sample_content):
        """Test meta-learning integration."""
        user_id = "test_user_ml"
        
        # Perform multiple compressions to build learning data
        for i in range(3):
            # Analyze content
            analysis_response = client.post("/api/v1/compression/enhanced/analyze-content", json={
                "content": sample_content["long_text"],
                "options": {
                    "include_patterns": True,
                    "include_quality": True,
                    "include_predictions": True
                }
            })
            
            assert analysis_response.status_code == 200
            analysis_data = analysis_response.json()
            
            # Get recommendations
            recommendations_response = client.post("/api/v1/compression/enhanced/recommendations", json={
                "content_analysis": analysis_data["analysis"],
                "user_preferences": {
                    "speed_vs_compression": 0.6,
                    "quality_vs_size": 0.7,
                    "compatibility_vs_performance": 0.5
                },
                "meta_learning_context": {
                    "user_id": user_id,
                    "session_id": f"session_{i}",
                    "historical_data": True
                }
            })
            
            assert recommendations_response.status_code == 200
            recommendations_data = recommendations_response.json()
            
            # Compress content
            compression_response = client.post("/api/v1/compression/enhanced/compress-enhanced", json={
                "content": sample_content["long_text"],
                "content_analysis": analysis_data["analysis"],
                "algorithm": {
                    "name": recommendations_data["recommendations"][0]["algorithm"]["name"],
                    "parameters": {"level": 6}
                },
                "options": {
                    "include_metrics": True,
                    "include_predictions": True,
                    "include_quality": True,
                    "track_experiment": True
                }
            })
            
            assert compression_response.status_code == 200
        
        # Get learning insights
        insights_response = client.get(f"/api/v1/compression/enhanced/learning-insights?user_id={user_id}")
        assert insights_response.status_code == 200
        insights_data = insights_response.json()
        assert insights_data["success"] is True
        assert "insights" in insights_data
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, client, sample_content):
        """Test batch processing functionality."""
        batch_items = [
            {
                "id": "item1",
                "content": sample_content["short_text"],
                "content_analysis": {}
            },
            {
                "id": "item2", 
                "content": sample_content["json_content"],
                "content_analysis": {}
            },
            {
                "id": "item3",
                "content": sample_content["code_content"],
                "content_analysis": {}
            }
        ]
        
        response = client.post("/api/v1/compression/enhanced/batch-process", json={
            "batch_id": "test_batch_001",
            "items": batch_items,
            "options": {
                "parallel_processing": True,
                "include_comparison": True,
                "save_results": True
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert "batch_analysis" in data
        
        # Check batch results
        results = data["results"]
        assert len(results) == len(batch_items)
        
        # Check batch analysis
        batch_analysis = data["batch_analysis"]
        assert "total_items" in batch_analysis
        assert "successful_items" in batch_analysis
        assert "failed_items" in batch_analysis
        assert batch_analysis["total_items"] == len(batch_items)
    
    @pytest.mark.asyncio
    async def test_content_copying_functionality(self, client, sample_content):
        """Test that compressed content can be copied."""
        # Analyze content
        analysis_response = client.post("/api/v1/compression/enhanced/analyze-content", json={
            "content": sample_content["long_text"],
            "options": {
                "include_patterns": True,
                "include_quality": True,
                "include_predictions": True
            }
        })
        
        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()
        
        # Get recommendations
        recommendations_response = client.post("/api/v1/compression/enhanced/recommendations", json={
            "content_analysis": analysis_data["analysis"],
            "user_preferences": {
                "speed_vs_compression": 0.6,
                "quality_vs_size": 0.7,
                "compatibility_vs_performance": 0.5
            },
            "meta_learning_context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "historical_data": True
            }
        })
        
        assert recommendations_response.status_code == 200
        recommendations_data = recommendations_response.json()
        
        # Compress content
        compression_response = client.post("/api/v1/compression/enhanced/compress-enhanced", json={
            "content": sample_content["long_text"],
            "content_analysis": analysis_data["analysis"],
            "algorithm": {
                "name": recommendations_data["recommendations"][0]["algorithm"]["name"],
                "parameters": {"level": 6}
            },
            "options": {
                "include_metrics": True,
                "include_predictions": True,
                "include_quality": True,
                "track_experiment": True
            }
        })
        
        assert compression_response.status_code == 200
        compression_data = compression_response.json()
        
        # Verify compressed content is available for copying
        result = compression_data["result"]
        assert "compressed_content" in result
        assert result["compressed_content"] is not None
        assert len(result["compressed_content"]) > 0
        
        # The compressed content should be in a format that can be copied
        # (hex string or base64 encoded)
        compressed_content = result["compressed_content"]
        assert isinstance(compressed_content, str)
        
        # Verify it's a valid hex string (if hex encoded)
        try:
            bytes.fromhex(compressed_content)
            is_valid_hex = True
        except ValueError:
            is_valid_hex = False
        
        # Should be either hex or base64 encoded
        assert is_valid_hex or compressed_content.isalnum() or '+' in compressed_content or '/' in compressed_content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
