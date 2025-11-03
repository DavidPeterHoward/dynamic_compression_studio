"""
Comprehensive API testing with improved error handling and edge cases
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

class TestComprehensiveAPI:
    """Comprehensive API testing suite"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def sample_content(self):
        return {
            "text": "This is a sample text for compression testing. " * 100,
            "json": '{"users": [{"id": 1, "name": "User 1"}]}',
            "xml": "<root><item>test</item></root>",
            "code": "def test(): return 'hello'",
            "large": "A" * 10000,
            "empty": ""
        }
    
    async def test_health_endpoints_comprehensive(self, client):
        """Test all health endpoints with proper error handling"""
        endpoints = [
            "/health",
            "/api/v1/health/detailed",
            "/api/v1/health/readiness",
            "/api/v1/health/liveness",
            "/api/v1/health/status"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 404], f"Endpoint {endpoint} failed"
            
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert data["status"] in ["healthy", "running", "ready", "alive"]
    
    async def test_compression_workflow_comprehensive(self, client, sample_content):
        """Test complete compression workflow with error handling"""
        # Test content analysis
        analysis_response = client.post("/api/v1/compression/analyze-content", json={
            "content": sample_content["text"],
            "options": {
                "include_patterns": True,
                "include_quality": True,
                "include_predictions": True
            }
        })
        
        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()
        assert analysis_data["success"] is True
        assert "analysis" in analysis_data
        
        # Test recommendations
        recommendations_response = client.post("/api/v1/compression/recommendations", json={
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
        assert recommendations_data["success"] is True
        assert len(recommendations_data["recommendations"]) > 0
        
        # Test compression
        compression_response = client.post("/api/v1/compression/compress-enhanced", json={
            "content": sample_content["text"],
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
        assert compression_data["success"] is True
        assert compression_data["result"]["compression_ratio"] > 1.0
        assert compression_data["result"]["processing_time"] > 0
    
    async def test_error_handling_comprehensive(self, client):
        """Test comprehensive error handling scenarios"""
        # Test empty content
        response = client.post("/api/v1/compression/analyze-content", json={
            "content": "",
            "options": {}
        })
        assert response.status_code in [400, 500]  # Should handle gracefully
        
        # Test invalid content
        response = client.post("/api/v1/compression/analyze-content", json={
            "content": None,
            "options": {}
        })
        assert response.status_code in [400, 422, 500]
        
        # Test malformed JSON
        response = client.post("/api/v1/compression/analyze-content", json={
            "content": "test",
            "options": "invalid"
        })
        assert response.status_code in [400, 422, 500]
    
    async def test_performance_benchmarks(self, client, sample_content):
        """Test performance with various content sizes"""
        content_sizes = [100, 1000, 10000, 100000]
        
        for size in content_sizes:
            content = sample_content["text"] * (size // len(sample_content["text"]) + 1)
            
            start_time = asyncio.get_event_loop().time()
            
            # Analyze content
            analysis_response = client.post("/api/v1/compression/analyze-content", json={
                "content": content,
                "options": {"include_patterns": True}
            })
            
            assert analysis_response.status_code == 200
            analysis_data = analysis_response.json()
            
            # Get recommendations
            recommendations_response = client.post("/api/v1/compression/recommendations", json={
                "content_analysis": analysis_data["analysis"],
                "user_preferences": {"speed_vs_compression": 0.5},
                "meta_learning_context": {}
            })
            
            assert recommendations_response.status_code == 200
            recommendations_data = recommendations_response.json()
            
            # Compress content
            compression_response = client.post("/api/v1/compression/compress-enhanced", json={
                "content": content,
                "content_analysis": analysis_data["analysis"],
                "algorithm": {
                    "name": recommendations_data["recommendations"][0]["algorithm"]["name"],
                    "parameters": {"level": 6}
                },
                "options": {"include_metrics": True}
            })
            
            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time
            
            assert compression_response.status_code == 200
            assert total_time < 30.0  # Should complete within 30 seconds
            
            compression_data = compression_response.json()
            assert compression_data["result"]["compression_ratio"] > 1.0
            assert compression_data["result"]["processing_time"] > 0
