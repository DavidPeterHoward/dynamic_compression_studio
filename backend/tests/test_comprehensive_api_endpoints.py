"""
COMPREHENSIVE API ENDPOINT TESTS

This test suite covers ALL API endpoints, functionality, buttons, processes, and logic
within the backend application, including:

1. Health Check Endpoints
2. Compression API Endpoints  
3. Enhanced Compression API Endpoints
4. Files API Endpoints
5. Metrics API Endpoints
6. Evaluation API Endpoints
7. LLM Agent API Endpoints
8. Sensors API Endpoints
9. All request/response validation
10. All error scenarios and edge cases
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import get_db
from app.models.enhanced_compression import (
    ContentAnalysisRequest, AlgorithmRecommendationRequest,
    EnhancedCompressionRequest, BatchProcessRequest
)

client = TestClient(app)

class TestHealthEndpoints:
    """Test all health check endpoints"""
    
    def test_basic_health_endpoint(self):
        """Test basic health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "database" in data
        assert "version" in data

    def test_health_readiness(self):
        """Test health readiness endpoint"""
        response = client.get("/api/v1/health/health/readiness")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_health_liveness(self):
        """Test health liveness endpoint"""
        response = client.get("/api/v1/health/health/liveness")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_health_detailed(self):
        """Test detailed health endpoint"""
        response = client.get("/api/v1/health/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "metrics" in data

    def test_health_status(self):
        """Test health status endpoint"""
        response = client.get("/api/v1/health/health/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

class TestCompressionEndpoints:
    """Test all compression API endpoints"""
    
    def test_compress_endpoint(self):
        """Test basic compression endpoint"""
        response = client.post("/api/v1/compression/compress", json={
            "content": "This is test content for compression",
            "parameters": {
                "algorithm": "gzip",
                "level": 6
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "result" in data
        assert "compression_ratio" in data["result"]

    def test_batch_compress_endpoint(self):
        """Test batch compression endpoint"""
        response = client.post("/api/v1/compression/compress/batch", json={
            "items": [
                {"content": "Test content 1", "parameters": {"algorithm": "gzip"}},
                {"content": "Test content 2", "parameters": {"algorithm": "zstd"}}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "results" in data
        assert len(data["results"]) == 2

    def test_compare_algorithms_endpoint(self):
        """Test algorithm comparison endpoint"""
        response = client.post("/api/v1/compression/compare", json={
            "content": "Test content for comparison",
            "algorithms": ["gzip", "zstd", "brotli"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "comparison" in data
        assert len(data["comparison"]) == 3

    def test_get_algorithms_endpoint(self):
        """Test get algorithms endpoint"""
        response = client.get("/api/v1/compression/algorithms")
        assert response.status_code == 200
        data = response.json()
        assert "algorithms" in data
        assert len(data["algorithms"]) > 0
        assert "categories" in data
        assert "recommendations" in data

    def test_analyze_content_endpoint(self):
        """Test content analysis endpoint"""
        response = client.get("/api/v1/compression/analyze", params={
            "content": "Test content for analysis"
        })
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data

    def test_get_algorithm_parameters(self):
        """Test get algorithm parameters endpoint"""
        response = client.get("/api/v1/compression/parameters/gzip")
        assert response.status_code == 200
        data = response.json()
        assert "parameters" in data

    def test_compression_test_endpoint(self):
        """Test compression test endpoint"""
        response = client.get("/api/v1/compression/test")
        assert response.status_code == 200
        data = response.json()
        assert "test_results" in data

class TestEnhancedCompressionEndpoints:
    """Test all enhanced compression API endpoints"""
    
    def test_analyze_content_enhanced(self):
        """Test enhanced content analysis endpoint"""
        response = client.post("/api/v1/compression/enhanced/analyze-content", json={
            "content": "This is test content for enhanced analysis",
            "options": {
                "include_patterns": True,
                "include_quality": True,
                "include_predictions": True
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "analysis" in data
        assert "processing_time" in data
        assert "timestamp" in data

    def test_get_algorithm_recommendations(self):
        """Test algorithm recommendations endpoint"""
        response = client.post("/api/v1/compression/enhanced/recommendations", json={
            "content_analysis": {
                "content_type": "text",
                "entropy": 0.75,
                "redundancy": 0.25,
                "compressibility": 8.5
            },
            "user_preferences": {
                "speed_vs_compression": 0.6,
                "quality_vs_size": 0.7
            },
            "meta_learning_context": {
                "user_id": "test_user",
                "session_id": "test_session"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "recommendations" in data
        assert "meta_learning_insights" in data

    def test_compress_enhanced(self):
        """Test enhanced compression endpoint"""
        response = client.post("/api/v1/compression/enhanced/compress-enhanced", json={
            "content": "Test content for enhanced compression",
            "content_analysis": {
                "content_type": "text",
                "entropy": 0.75,
                "redundancy": 0.25
            },
            "algorithm": {
                "name": "gzip",
                "parameters": {
                    "level": 6,
                    "window_size": 32768
                }
            },
            "options": {
                "include_metrics": True,
                "include_predictions": True,
                "track_experiment": True
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "result" in data
        assert "analysis" in data
        assert "metrics" in data

    def test_batch_process_enhanced(self):
        """Test enhanced batch processing endpoint"""
        response = client.post("/api/v1/compression/enhanced/batch-process", json={
            "items": [
                {
                    "id": "item1",
                    "content": "Test content 1",
                    "content_analysis": {}
                },
                {
                    "id": "item2", 
                    "content": "Test content 2",
                    "content_analysis": {}
                }
            ],
            "options": {
                "parallel_processing": True,
                "include_comparison": True
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "results" in data
        assert "summary" in data

    def test_real_time_metrics(self):
        """Test real-time metrics endpoint"""
        response = client.get("/api/v1/compression/enhanced/metrics/real-time")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "real_time_metrics" in data
        assert "trends" in data
        assert "alerts" in data

    def test_learning_insights(self):
        """Test learning insights endpoint"""
        response = client.get("/api/v1/compression/enhanced/learning-insights")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "insights" in data
        assert "recommendations" in data

    def test_update_preferences(self):
        """Test update preferences endpoint"""
        response = client.post("/api/v1/compression/enhanced/update-preferences", json={
            "user_id": "test_user",
            "preferences": {
                "speed_vs_compression": 0.6,
                "quality_vs_size": 0.7
            },
            "learning_data": {
                "session_history": [],
                "performance_feedback": []
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "updated_preferences" in data
        assert "learning_status" in data

class TestFilesEndpoints:
    """Test all files API endpoints"""
    
    def test_upload_file(self):
        """Test file upload endpoint"""
        files = {"file": ("test.txt", "Test file content", "text/plain")}
        response = client.post("/api/v1/files/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "file_id" in data

    def test_list_files(self):
        """Test list files endpoint"""
        response = client.get("/api/v1/files/list")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "pagination" in data

    def test_get_file(self):
        """Test get file endpoint"""
        # First upload a file
        files = {"file": ("test.txt", "Test file content", "text/plain")}
        upload_response = client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        
        # Then get the file
        response = client.get(f"/api/v1/files/{file_id}")
        assert response.status_code == 200
        data = response.json()
        assert "file" in data

    def test_download_file(self):
        """Test download file endpoint"""
        # First upload a file
        files = {"file": ("test.txt", "Test file content", "text/plain")}
        upload_response = client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        
        # Then download the file
        response = client.get(f"/api/v1/files/{file_id}/download")
        assert response.status_code == 200

    def test_delete_file(self):
        """Test delete file endpoint"""
        # First upload a file
        files = {"file": ("test.txt", "Test file content", "text/plain")}
        upload_response = client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        
        # Then delete the file
        response = client.delete(f"/api/v1/files/{file_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_update_file(self):
        """Test update file endpoint"""
        # First upload a file
        files = {"file": ("test.txt", "Test file content", "text/plain")}
        upload_response = client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        
        # Then update the file
        response = client.put(f"/api/v1/files/{file_id}", json={
            "metadata": {"description": "Updated file"}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_search_files(self):
        """Test search files endpoint"""
        response = client.post("/api/v1/files/search", json={
            "query": "test",
            "filters": {
                "file_type": "text/plain"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "total" in data

    def test_get_file_metadata(self):
        """Test get file metadata endpoint"""
        # First upload a file
        files = {"file": ("test.txt", "Test file content", "text/plain")}
        upload_response = client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["file_id"]
        
        # Then get metadata
        response = client.get(f"/api/v1/files/{file_id}/metadata")
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data

class TestMetricsEndpoints:
    """Test all metrics API endpoints"""
    
    def test_get_metrics_summary(self):
        """Test metrics summary endpoint"""
        response = client.get("/api/v1/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "performance" in data
        assert "compression" in data

    def test_get_performance_metrics(self):
        """Test performance metrics endpoint"""
        response = client.get("/api/v1/metrics/performance")
        assert response.status_code == 200
        data = response.json()
        assert "performance" in data
        assert "system" in data
        assert "compression" in data

    def test_get_algorithm_metrics(self):
        """Test algorithm metrics endpoint"""
        response = client.get("/api/v1/metrics/algorithms")
        assert response.status_code == 200
        data = response.json()
        assert "algorithms" in data
        assert "performance" in data

    def test_aggregate_metrics(self):
        """Test aggregate metrics endpoint"""
        response = client.post("/api/v1/metrics/aggregate", json={
            "time_range": "24h",
            "metrics": ["compression_ratio", "processing_time"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "aggregated" in data
        assert "time_range" in data

    def test_compare_metrics(self):
        """Test compare metrics endpoint"""
        response = client.post("/api/v1/metrics/compare", json={
            "algorithms": ["gzip", "zstd"],
            "metrics": ["compression_ratio", "processing_time"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "comparison" in data
        assert "algorithms" in data

    def test_get_metrics_trends(self):
        """Test metrics trends endpoint"""
        response = client.get("/api/v1/metrics/trends")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert "time_series" in data

    def test_get_metrics_dashboard(self):
        """Test metrics dashboard endpoint"""
        response = client.get("/api/v1/metrics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "dashboard" in data
        assert "widgets" in data

class TestEvaluationEndpoints:
    """Test all evaluation API endpoints"""
    
    def test_evaluation_metrics(self):
        """Test evaluation metrics endpoint"""
        response = client.post("/api/v1/evaluation/metrics", json={
            "algorithm": "gzip",
            "test_data": "Test content for evaluation",
            "metrics": ["compression_ratio", "processing_time", "quality"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "evaluation" in data
        assert "metrics" in data

    def test_compare_algorithms_evaluation(self):
        """Test algorithm comparison evaluation endpoint"""
        response = client.post("/api/v1/evaluation/compare", json={
            "algorithms": ["gzip", "zstd", "brotli"],
            "test_data": "Test content for comparison",
            "metrics": ["compression_ratio", "processing_time"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "comparison" in data
        assert "rankings" in data

    def test_evaluation_trends(self):
        """Test evaluation trends endpoint"""
        response = client.post("/api/v1/evaluation/trends", json={
            "time_range": "7d",
            "algorithm": "gzip",
            "metrics": ["compression_ratio", "quality"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert "time_series" in data

    def test_sensor_fusion_evaluation(self):
        """Test sensor fusion evaluation endpoint"""
        response = client.post("/api/v1/evaluation/sensor-fusion", json={
            "sensors": ["cpu", "memory", "network"],
            "algorithm": "gzip",
            "fusion_method": "weighted_average"
        })
        assert response.status_code == 200
        data = response.json()
        assert "fusion" in data
        assert "results" in data

    def test_experiments_evaluation(self):
        """Test experiments evaluation endpoint"""
        response = client.post("/api/v1/evaluation/experiments", json={
            "experiment_id": "test_exp_001",
            "evaluation_metrics": ["accuracy", "precision", "recall"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "experiment" in data
        assert "evaluation" in data

class TestLLMAgentEndpoints:
    """Test all LLM agent API endpoints"""
    
    def test_get_available_models(self):
        """Test get available models endpoint"""
        response = client.get("/api/v1/llm-agent/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "capabilities" in data

    def test_get_agent_methods(self):
        """Test get agent methods endpoint"""
        response = client.get("/api/v1/llm-agent/methods")
        assert response.status_code == 200
        data = response.json()
        assert "methods" in data
        assert "categories" in data

    def test_decompress_content(self):
        """Test decompress content endpoint"""
        response = client.post("/api/v1/llm-agent/decompress", json={
            "compressed_content": "compressed_data_here",
            "algorithm": "gzip",
            "options": {
                "include_analysis": True,
                "include_quality_check": True
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "decompressed_content" in data

    def test_analyze_with_llm(self):
        """Test analyze with LLM endpoint"""
        response = client.post("/api/v1/llm-agent/analyze", json={
            "content": "Test content for LLM analysis",
            "analysis_type": "compression_optimization",
            "model": "gpt-4",
            "options": {
                "include_recommendations": True,
                "include_explanations": True
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "recommendations" in data

class TestSensorsEndpoints:
    """Test all sensors API endpoints"""
    
    def test_get_sensor_metrics(self):
        """Test get sensor metrics endpoint"""
        response = client.get("/api/v1/sensors/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "sensors" in data

    def test_post_sensor_metrics(self):
        """Test post sensor metrics endpoint"""
        response = client.post("/api/v1/sensors/metrics", json={
            "sensor_id": "cpu_sensor_001",
            "metric_name": "cpu_usage",
            "value": 45.2,
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {
                "unit": "percentage",
                "threshold": 80.0
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "metric_id" in data

    def test_get_sensor_metric_by_id(self):
        """Test get sensor metric by ID endpoint"""
        # First create a metric
        create_response = client.post("/api/v1/sensors/metrics", json={
            "sensor_id": "test_sensor",
            "metric_name": "test_metric",
            "value": 100.0,
            "timestamp": "2024-01-01T12:00:00Z"
        })
        metric_id = create_response.json()["metric_id"]
        
        # Then get the metric
        response = client.get(f"/api/v1/sensors/metrics/{metric_id}")
        assert response.status_code == 200
        data = response.json()
        assert "metric" in data

    def test_get_metric_history(self):
        """Test get metric history endpoint"""
        response = client.get("/api/v1/sensors/metrics/names/cpu_usage/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "time_series" in data

    def test_get_sensors(self):
        """Test get sensors endpoint"""
        response = client.get("/api/v1/sensors/sensors")
        assert response.status_code == 200
        data = response.json()
        assert "sensors" in data

    def test_create_sensor(self):
        """Test create sensor endpoint"""
        response = client.post("/api/v1/sensors/sensors", json={
            "name": "Test Sensor",
            "type": "cpu",
            "location": "server_01",
            "configuration": {
                "sampling_rate": 1.0,
                "thresholds": {
                    "warning": 70.0,
                    "critical": 90.0
                }
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "sensor_id" in data

    def test_get_sensor_by_id(self):
        """Test get sensor by ID endpoint"""
        # First create a sensor
        create_response = client.post("/api/v1/sensors/sensors", json={
            "name": "Test Sensor",
            "type": "cpu",
            "location": "server_01"
        })
        sensor_id = create_response.json()["sensor_id"]
        
        # Then get the sensor
        response = client.get(f"/api/v1/sensors/sensors/{sensor_id}")
        assert response.status_code == 200
        data = response.json()
        assert "sensor" in data

    def test_update_sensor(self):
        """Test update sensor endpoint"""
        # First create a sensor
        create_response = client.post("/api/v1/sensors/sensors", json={
            "name": "Test Sensor",
            "type": "cpu",
            "location": "server_01"
        })
        sensor_id = create_response.json()["sensor_id"]
        
        # Then update the sensor
        response = client.put(f"/api/v1/sensors/sensors/{sensor_id}", json={
            "name": "Updated Test Sensor",
            "configuration": {
                "sampling_rate": 2.0
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_delete_sensor(self):
        """Test delete sensor endpoint"""
        # First create a sensor
        create_response = client.post("/api/v1/sensors/sensors", json={
            "name": "Test Sensor",
            "type": "cpu",
            "location": "server_01"
        })
        sensor_id = create_response.json()["sensor_id"]
        
        # Then delete the sensor
        response = client.delete(f"/api/v1/sensors/sensors/{sensor_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_get_sensor_readings(self):
        """Test get sensor readings endpoint"""
        # First create a sensor
        create_response = client.post("/api/v1/sensors/sensors", json={
            "name": "Test Sensor",
            "type": "cpu",
            "location": "server_01"
        })
        sensor_id = create_response.json()["sensor_id"]
        
        # Then get readings
        response = client.get(f"/api/v1/sensors/sensors/{sensor_id}/readings")
        assert response.status_code == 200
        data = response.json()
        assert "readings" in data

    def test_post_sensor_readings(self):
        """Test post sensor readings endpoint"""
        # First create a sensor
        create_response = client.post("/api/v1/sensors/sensors", json={
            "name": "Test Sensor",
            "type": "cpu",
            "location": "server_01"
        })
        sensor_id = create_response.json()["sensor_id"]
        
        # Then post readings
        response = client.post(f"/api/v1/sensors/sensors/{sensor_id}/readings", json={
            "readings": [
                {
                    "value": 45.2,
                    "timestamp": "2024-01-01T12:00:00Z"
                },
                {
                    "value": 47.8,
                    "timestamp": "2024-01-01T12:01:00Z"
                }
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data

    def test_sensor_fusion_endpoints(self):
        """Test sensor fusion endpoints"""
        # Get fusion methods
        response = client.get("/api/v1/sensors/fusion")
        assert response.status_code == 200
        data = response.json()
        assert "fusion_methods" in data

        # Create fusion
        response = client.post("/api/v1/sensors/fusion", json={
            "name": "Test Fusion",
            "sensors": ["cpu_sensor", "memory_sensor"],
            "method": "weighted_average",
            "weights": {"cpu_sensor": 0.6, "memory_sensor": 0.4}
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "fusion_id" in data

    def test_sensor_health_endpoints(self):
        """Test sensor health endpoints"""
        # Get health status
        response = client.get("/api/v1/sensors/health")
        assert response.status_code == 200
        data = response.json()
        assert "health" in data

        # Post health check
        response = client.post("/api/v1/sensors/health", json={
            "sensor_id": "test_sensor",
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00Z"
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data

        # Get current health
        response = client.get("/api/v1/sensors/health/current")
        assert response.status_code == 200
        data = response.json()
        assert "current_health" in data

    def test_sensor_query_endpoint(self):
        """Test sensor query endpoint"""
        response = client.post("/api/v1/sensors/query", json={
            "query": "SELECT * FROM metrics WHERE sensor_type = 'cpu'",
            "time_range": "24h",
            "limit": 100
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_sensor_stats_endpoints(self):
        """Test sensor statistics endpoints"""
        # Get summary stats
        response = client.get("/api/v1/sensors/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data

        # Get sensor types
        response = client.get("/api/v1/sensors/types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data

        # Get sensor statuses
        response = client.get("/api/v1/sensors/statuses")
        assert response.status_code == 200
        data = response.json()
        assert "statuses" in data

        # Get metric types
        response = client.get("/api/v1/sensors/metric-type")
        assert response.status_code == 200
        data = response.json()
        assert "metric_types" in data

class TestErrorHandling:
    """Test error handling across all endpoints"""
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = client.get("/api/v1/invalid/endpoint")
        assert response.status_code == 404

    def test_invalid_method(self):
        """Test invalid HTTP method returns 405"""
        response = client.put("/health")
        assert response.status_code == 405

    def test_missing_required_fields(self):
        """Test missing required fields returns 422"""
        response = client.post("/api/v1/compression/compress", json={})
        assert response.status_code == 422

    def test_invalid_data_types(self):
        """Test invalid data types returns 422"""
        response = client.post("/api/v1/compression/compress", json={
            "content": 123,  # Should be string
            "parameters": "invalid"  # Should be object
        })
        assert response.status_code == 422

    def test_validation_errors(self):
        """Test validation errors return 422"""
        response = client.post("/api/v1/compression/compress", json={
            "content": "",  # Empty content
            "parameters": {
                "algorithm": "invalid_algorithm"  # Invalid algorithm
            }
        })
        assert response.status_code == 422

class TestPerformanceAndLoad:
    """Test performance and load handling"""
    
    def test_large_content_handling(self):
        """Test handling of large content"""
        large_content = "A" * 1000000  # 1MB content
        response = client.post("/api/v1/compression/compress", json={
            "content": large_content,
            "parameters": {"algorithm": "gzip"}
        })
        assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.post("/api/v1/compression/compress", json={
                "content": "Test content",
                "parameters": {"algorithm": "gzip"}
            })
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert all(status == 200 for status in results)

    def test_memory_usage(self):
        """Test memory usage with large requests"""
        # This test would need to be implemented with memory monitoring
        # For now, just test that large requests don't crash the server
        response = client.post("/api/v1/compression/compress", json={
            "content": "A" * 10000000,  # 10MB content
            "parameters": {"algorithm": "gzip"}
        })
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 413, 422]

class TestSecurityAndValidation:
    """Test security and validation measures"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        malicious_content = "'; DROP TABLE users; --"
        response = client.post("/api/v1/compression/compress", json={
            "content": malicious_content,
            "parameters": {"algorithm": "gzip"}
        })
        # Should handle malicious content safely
        assert response.status_code in [200, 400, 422]

    def test_xss_prevention(self):
        """Test XSS prevention"""
        xss_content = "<script>alert('xss')</script>"
        response = client.post("/api/v1/compression/compress", json={
            "content": xss_content,
            "parameters": {"algorithm": "gzip"}
        })
        # Should handle XSS content safely
        assert response.status_code in [200, 400, 422]

    def test_input_sanitization(self):
        """Test input sanitization"""
        # Test various potentially dangerous inputs
        dangerous_inputs = [
            "../../../etc/passwd",
            "\\x00\\x01\\x02",
            "null\\x00byte",
            "very\\x00long\\x00string\\x00with\\x00nulls"
        ]
        
        for dangerous_input in dangerous_inputs:
            response = client.post("/api/v1/compression/compress", json={
                "content": dangerous_input,
                "parameters": {"algorithm": "gzip"}
            })
            # Should handle dangerous inputs safely
            assert response.status_code in [200, 400, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
