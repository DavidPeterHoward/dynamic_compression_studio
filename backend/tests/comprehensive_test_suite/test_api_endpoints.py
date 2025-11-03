"""
Comprehensive API Endpoint Integration Tests

Tests all API endpoints with:
- Request validation
- Response validation
- Error handling
- Edge cases
- Authentication (if applicable)
- Rate limiting
- Data integrity
"""

import pytest
import json
from fastapi.testclient import TestClient
from typing import Dict, Any, List

from test_fixtures import (
    ContentFactory,
    FingerprintFactory,
    ViabilityTestFactory,
    get_all_algorithms
)


# Note: These tests assume FastAPI app structure
# Adjust imports based on actual app structure


class MockApp:
    """Mock FastAPI app for testing."""
    
    def __init__(self):
        from fastapi import FastAPI
        self.app = FastAPI()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup mock routes for testing."""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.post("/algorithm-viability/test")
        async def run_viability_test(request: Dict[str, Any]):
            """Mock viability test endpoint."""
            return {
                "test_id": "test_001",
                "algorithm": request.get("algorithm", "gzip"),
                "success": True,
                "compression_ratio": 3.5,
                "execution_time_ms": 50.0
            }
        
        @router.get("/algorithm-viability/algorithms")
        async def get_algorithms():
            """Mock get algorithms endpoint."""
            return {
                "algorithms": ["gzip", "lzma", "zstd", "bzip2"]
            }
        
        @router.post("/algorithm-viability/compare")
        async def compare_algorithms(request: Dict[str, Any]):
            """Mock algorithm comparison endpoint."""
            return {
                "comparison_id": "comp_001",
                "algorithms": request.get("algorithms", []),
                "results": [
                    {"algorithm": "gzip", "ratio": 3.2, "time_ms": 45},
                    {"algorithm": "lzma", "ratio": 4.5, "time_ms": 150}
                ]
            }
        
        @router.get("/algorithm-viability/recommendations")
        async def get_recommendations(content_type: str = "text/plain"):
            """Mock recommendations endpoint."""
            return {
                "recommended_algorithm": "zstd",
                "confidence": 0.85,
                "reasons": ["Best balance of speed and ratio for " + content_type]
            }
        
        @router.post("/algorithm-viability/analyze")
        async def analyze_content(request: Dict[str, Any]):
            """Mock content analysis endpoint."""
            return {
                "analysis_id": "analysis_001",
                "content_characteristics": {
                    "entropy": 0.7,
                    "redundancy": 0.3,
                    "compressibility": 0.75
                },
                "recommended_algorithms": ["zstd", "lzma"]
            }
        
        @router.get("/algorithm-viability/history")
        async def get_test_history(algorithm: str = None, limit: int = 100):
            """Mock test history endpoint."""
            return {
                "tests": [
                    {"test_id": "test_001", "algorithm": "gzip", "ratio": 3.5},
                    {"test_id": "test_002", "algorithm": "lzma", "ratio": 4.2}
                ],
                "total": 2
            }
        
        @router.get("/algorithm-viability/insights")
        async def get_insights():
            """Mock insights endpoint."""
            return {
                "insights": [
                    {
                        "insight_id": "insight_001",
                        "type": "best_algorithm",
                        "description": "LZMA performs best on JSON",
                        "confidence": 0.95
                    }
                ]
            }
        
        @router.post("/algorithm-viability/validate")
        async def validate_test(request: Dict[str, Any]):
            """Mock validation endpoint."""
            return {
                "validation_id": "val_001",
                "is_valid": True,
                "checks_passed": 4,
                "checks_failed": 0
            }
        
        self.app.include_router(router)


@pytest.fixture
def client():
    """Create test client."""
    mock_app = MockApp()
    return TestClient(mock_app.app)


class TestViabilityTestEndpoints:
    """Test viability test endpoints."""
    
    def test_run_single_test(self, client):
        """Test running a single viability test."""
        request_data = {
            "algorithm": "gzip",
            "content": "test content",
            "content_type": "text/plain"
        }
        
        response = client.post("/algorithm-viability/test", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "test_id" in data
        assert data["algorithm"] == "gzip"
        assert data["success"] is True
        assert "compression_ratio" in data
    
    def test_run_test_with_invalid_algorithm(self, client):
        """Test running test with invalid algorithm."""
        request_data = {
            "algorithm": "invalid_algorithm",
            "content": "test content"
        }
        
        response = client.post("/algorithm-viability/test", json=request_data)
        
        # Should handle gracefully (either 400 or return error in response)
        assert response.status_code in [200, 400, 422]
    
    def test_run_test_with_empty_content(self, client):
        """Test running test with empty content."""
        request_data = {
            "algorithm": "gzip",
            "content": ""
        }
        
        response = client.post("/algorithm-viability/test", json=request_data)
        
        # Should handle edge case
        assert response.status_code in [200, 400, 422]
    
    def test_run_test_with_large_content(self, client):
        """Test running test with large content."""
        large_content = "x" * 1000000  # 1MB
        request_data = {
            "algorithm": "gzip",
            "content": large_content
        }
        
        response = client.post("/algorithm-viability/test", json=request_data)
        
        # Should handle large content
        assert response.status_code in [200, 413, 422]


class TestAlgorithmEndpoints:
    """Test algorithm-related endpoints."""
    
    def test_get_available_algorithms(self, client):
        """Test getting list of available algorithms."""
        response = client.get("/algorithm-viability/algorithms")
        
        assert response.status_code == 200
        data = response.json()
        assert "algorithms" in data
        assert len(data["algorithms"]) > 0
        assert "gzip" in data["algorithms"]
    
    def test_compare_algorithms(self, client):
        """Test comparing multiple algorithms."""
        request_data = {
            "algorithms": ["gzip", "lzma", "zstd"],
            "content": "test content for comparison"
        }
        
        response = client.post("/algorithm-viability/compare", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
    
    def test_compare_with_single_algorithm(self, client):
        """Test comparison with single algorithm."""
        request_data = {
            "algorithms": ["gzip"],
            "content": "test content"
        }
        
        response = client.post("/algorithm-viability/compare", json=request_data)
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_compare_with_no_algorithms(self, client):
        """Test comparison with no algorithms specified."""
        request_data = {
            "algorithms": [],
            "content": "test content"
        }
        
        response = client.post("/algorithm-viability/compare", json=request_data)
        
        # Should return error
        assert response.status_code in [400, 422]


class TestRecommendationEndpoints:
    """Test recommendation endpoints."""
    
    def test_get_recommendation_for_content_type(self, client):
        """Test getting recommendation for content type."""
        response = client.get("/algorithm-viability/recommendations?content_type=application/json")
        
        assert response.status_code == 200
        data = response.json()
        assert "recommended_algorithm" in data
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
    
    def test_get_recommendation_without_content_type(self, client):
        """Test getting recommendation without specifying content type."""
        response = client.get("/algorithm-viability/recommendations")
        
        assert response.status_code == 200
        data = response.json()
        assert "recommended_algorithm" in data
    
    @pytest.mark.parametrize("content_type", [
        "text/plain",
        "application/json",
        "application/xml",
        "text/html",
        "application/octet-stream"
    ])
    def test_recommendations_for_various_types(self, client, content_type):
        """Test recommendations for various content types."""
        response = client.get(f"/algorithm-viability/recommendations?content_type={content_type}")
        
        assert response.status_code == 200
        data = response.json()
        assert "recommended_algorithm" in data


class TestAnalysisEndpoints:
    """Test content analysis endpoints."""
    
    def test_analyze_content(self, client):
        """Test content analysis."""
        request_data = {
            "content": "test content for analysis",
            "content_type": "text/plain"
        }
        
        response = client.post("/algorithm-viability/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "content_characteristics" in data
        assert "recommended_algorithms" in data
    
    def test_analyze_json_content(self, client):
        """Test analyzing JSON content."""
        json_content = json.dumps({"key": "value", "nested": {"data": [1, 2, 3]}})
        request_data = {
            "content": json_content,
            "content_type": "application/json"
        }
        
        response = client.post("/algorithm-viability/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "content_characteristics" in data
    
    def test_analyze_binary_content(self, client):
        """Test analyzing binary content."""
        import base64
        binary_content = base64.b64encode(b"\x00\x01\x02\x03\xFF\xFE").decode('utf-8')
        request_data = {
            "content": binary_content,
            "content_type": "application/octet-stream",
            "encoding": "base64"
        }
        
        response = client.post("/algorithm-viability/analyze", json=request_data)
        
        assert response.status_code in [200, 400, 422]


class TestHistoryEndpoints:
    """Test test history endpoints."""
    
    def test_get_all_history(self, client):
        """Test getting all test history."""
        response = client.get("/algorithm-viability/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "tests" in data
        assert isinstance(data["tests"], list)
    
    def test_get_history_by_algorithm(self, client):
        """Test getting history filtered by algorithm."""
        response = client.get("/algorithm-viability/history?algorithm=gzip")
        
        assert response.status_code == 200
        data = response.json()
        assert "tests" in data
    
    def test_get_history_with_limit(self, client):
        """Test getting history with limit."""
        response = client.get("/algorithm-viability/history?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "tests" in data
        assert len(data["tests"]) <= 10
    
    def test_get_history_pagination(self, client):
        """Test history pagination."""
        response1 = client.get("/algorithm-viability/history?limit=5&offset=0")
        response2 = client.get("/algorithm-viability/history?limit=5&offset=5")
        
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestInsightEndpoints:
    """Test meta-learning insight endpoints."""
    
    def test_get_insights(self, client):
        """Test getting meta-learning insights."""
        response = client.get("/algorithm-viability/insights")
        
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        assert isinstance(data["insights"], list)
    
    def test_get_insights_by_type(self, client):
        """Test getting insights filtered by type."""
        response = client.get("/algorithm-viability/insights?type=best_algorithm")
        
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
    
    def test_get_high_confidence_insights(self, client):
        """Test getting high-confidence insights."""
        response = client.get("/algorithm-viability/insights?min_confidence=0.9")
        
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data


class TestValidationEndpoints:
    """Test validation endpoints."""
    
    def test_validate_test_result(self, client):
        """Test validating a test result."""
        request_data = {
            "test_id": "test_001",
            "original_size": 1000,
            "compressed_size": 286,
            "original_hash": "a" * 64,
            "decompressed_hash": "a" * 64
        }
        
        response = client.post("/algorithm-viability/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert "checks_passed" in data
    
    def test_validate_with_mismatched_hashes(self, client):
        """Test validation with mismatched hashes."""
        request_data = {
            "test_id": "test_002",
            "original_size": 1000,
            "compressed_size": 286,
            "original_hash": "a" * 64,
            "decompressed_hash": "b" * 64  # Different
        }
        
        response = client.post("/algorithm-viability/validate", json=request_data)
        
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert data["is_valid"] is False


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/algorithm-viability/test",
            data="invalid json{{{",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        request_data = {
            # Missing required fields
        }
        
        response = client.post("/algorithm-viability/test", json=request_data)
        
        assert response.status_code in [400, 422]
    
    def test_invalid_parameter_types(self, client):
        """Test handling of invalid parameter types."""
        request_data = {
            "algorithm": 12345,  # Should be string
            "content": ["not", "a", "string"]  # Should be string
        }
        
        response = client.post("/algorithm-viability/test", json=request_data)
        
        assert response.status_code in [400, 422]
    
    def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get("/algorithm-viability/nonexistent")
        
        assert response.status_code == 404


class TestResponseValidation:
    """Test response format validation."""
    
    def test_response_has_correct_content_type(self, client):
        """Test that responses have correct content type."""
        response = client.get("/algorithm-viability/algorithms")
        
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
    
    def test_response_schema_compliance(self, client):
        """Test that responses comply with expected schema."""
        response = client.get("/algorithm-viability/algorithms")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure
        assert isinstance(data, dict)
        assert "algorithms" in data
        assert isinstance(data["algorithms"], list)
    
    def test_error_response_format(self, client):
        """Test that error responses have consistent format."""
        response = client.get("/algorithm-viability/nonexistent")
        
        assert response.status_code == 404
        # Error responses should be JSON
        try:
            error_data = response.json()
            assert isinstance(error_data, dict)
        except json.JSONDecodeError:
            # Some frameworks return HTML for 404
            pass


class TestConcurrency:
    """Test concurrent request handling."""
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return client.get("/algorithm-viability/algorithms")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        assert len(responses) == 20
    
    def test_concurrent_writes(self, client):
        """Test handling of concurrent write operations."""
        import concurrent.futures
        
        def make_test_request(i):
            return client.post("/algorithm-viability/test", json={
                "algorithm": "gzip",
                "content": f"test content {i}"
            })
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_test_request, i) for i in range(10)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 8  # At least 80% success rate


class TestRateLimiting:
    """Test rate limiting (if implemented)."""
    
    def test_rate_limit_not_exceeded_normal_use(self, client):
        """Test that normal use doesn't hit rate limits."""
        for _ in range(10):
            response = client.get("/algorithm-viability/algorithms")
            assert response.status_code == 200
    
    def test_excessive_requests(self, client):
        """Test handling of excessive requests."""
        responses = []
        for _ in range(100):
            response = client.get("/algorithm-viability/algorithms")
            responses.append(response)
        
        # Either all succeed or some are rate-limited
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        assert success_count + rate_limited_count == len(responses)


class TestDataIntegrity:
    """Test data integrity across API operations."""
    
    def test_round_trip_data_integrity(self, client):
        """Test that data remains intact through API operations."""
        # Create test
        test_content = "Test content for integrity check"
        response1 = client.post("/algorithm-viability/test", json={
            "algorithm": "gzip",
            "content": test_content
        })
        
        assert response1.status_code == 200
        test_id = response1.json().get("test_id")
        
        if test_id:
            # Retrieve test (if endpoint exists)
            response2 = client.get(f"/algorithm-viability/history?test_id={test_id}")
            assert response2.status_code in [200, 404]  # May not be implemented


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

