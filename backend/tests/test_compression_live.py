"""
Live Compression Tests - Real Data Testing Suite
Tests compression algorithms with actual data and real-world scenarios.
"""

import pytest
import asyncio
import time
import json
import random
import string
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.compression_engine import CompressionEngine
from app.models.compression import CompressionAlgorithm, CompressionLevel
from app.database.connection import get_db_session
from app.services.compression_service import CompressionService


class TestLiveCompression:
    """Live compression tests using real data and algorithms."""
    
    @pytest.fixture
    def client(self):
        """Test client for FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    def compression_engine(self):
        """Compression engine instance."""
        return CompressionEngine()
    
    @pytest.fixture
    def sample_texts(self):
        """Various types of text data for testing."""
        return {
            "lorem_ipsum": """
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
                Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
                Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
                nisi ut aliquip ex ea commodo consequat.
            """,
            "json_data": json.dumps({
                "users": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
                ],
                "settings": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": True
                }
            }, indent=2),
            "repetitive_text": "Hello World! " * 1000,
            "random_data": ''.join(random.choices(string.ascii_letters + string.digits, k=10000)),
            "code_sample": """
                def fibonacci(n):
                    if n <= 1:
                        return n
                    return fibonacci(n-1) + fibonacci(n-2)
                
                def factorial(n):
                    if n == 0:
                        return 1
                    return n * factorial(n-1)
                
                # Test the functions
                for i in range(10):
                    print(f"fibonacci({i}) = {fibonacci(i)}")
                    print(f"factorial({i}) = {factorial(i)}")
            """
        }
    
    @pytest.fixture
    def compression_algorithms(self):
        """Available compression algorithms."""
        return [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZSTANDARD,
            CompressionAlgorithm.LZMA
        ]
    
    @pytest.mark.asyncio
    async def test_live_compression_basic(self, compression_engine, sample_texts):
        """Test basic compression with real data."""
        text = sample_texts["lorem_ipsum"]
        
        for algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.LZ4]:
            # Compress
            compressed_data = await compression_engine.compress(
                content=text,
                algorithm=algorithm,
                level=CompressionLevel.BALANCED
            )
            
            # Verify compression occurred
            assert len(compressed_data) < len(text.encode('utf-8'))
            assert len(compressed_data) > 0
            
            # Decompress
            decompressed_data = await compression_engine.decompress(
                compressed_data=compressed_data,
                algorithm=algorithm
            )
            
            # Verify data integrity
            assert decompressed_data == text
    
    @pytest.mark.asyncio
    async def test_live_compression_algorithms_comparison(self, compression_engine, sample_texts):
        """Compare compression ratios across different algorithms."""
        text = sample_texts["json_data"]
        results = {}
        
        for algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.BZIP2, CompressionAlgorithm.LZ4]:
            start_time = time.time()
            
            compressed_data = await compression_engine.compress(
                content=text,
                algorithm=algorithm,
                level=CompressionLevel.MAXIMUM
            )
            
            compression_time = time.time() - start_time
            
            # Calculate metrics
            original_size = len(text.encode('utf-8'))
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            results[algorithm] = {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "compression_time": compression_time,
                "space_saved_percent": ((original_size - compressed_size) / original_size) * 100
            }
            
            # Verify data integrity
            decompressed_data = await compression_engine.decompress(
                compressed_data=compressed_data,
                algorithm=algorithm
            )
            assert decompressed_data == text
        
        # Verify compression ratios are reasonable
        for algorithm, result in results.items():
            assert result["compression_ratio"] >= 1.0  # Should compress or at least not expand
            assert result["compression_time"] < 5.0  # Should complete within reasonable time
            print(f"{algorithm}: {result['compression_ratio']:.2f}x compression, "
                  f"{result['space_saved_percent']:.1f}% space saved")
    
    @pytest.mark.asyncio
    async def test_live_compression_levels(self, compression_engine, sample_texts):
        """Test different compression levels with real data."""
        text = sample_texts["repetitive_text"]
        algorithm = CompressionAlgorithm.GZIP
        
        results = {}
        
        for level in [CompressionLevel.FAST, CompressionLevel.BALANCED, CompressionLevel.MAXIMUM]:
            start_time = time.time()
            
            compressed_data = await compression_engine.compress(
                content=text,
                algorithm=algorithm,
                level=level
            )
            
            compression_time = time.time() - start_time
            
            results[level] = {
                "compressed_size": len(compressed_data),
                "compression_time": compression_time
            }
            
            # Verify data integrity
            decompressed_data = await compression_engine.decompress(
                compressed_data=compressed_data,
                algorithm=algorithm
            )
            assert decompressed_data == text
        
        # Verify compression levels behave as expected
        assert results[CompressionLevel.FAST]["compression_time"] <= results[CompressionLevel.BALANCED]["compression_time"]
        assert results[CompressionLevel.BALANCED]["compression_time"] <= results[CompressionLevel.MAXIMUM]["compression_time"]
        
        # Higher compression levels should generally produce smaller output
        # (though this isn't always guaranteed for all data types)
        print(f"Compression levels comparison:")
        for level, result in results.items():
            print(f"  {level}: {result['compressed_size']} bytes, {result['compression_time']:.3f}s")
    
    @pytest.mark.asyncio
    async def test_live_compression_edge_cases(self, compression_engine):
        """Test compression with edge cases and unusual data."""
        edge_cases = {
            "empty_string": "",
            "single_character": "a",
            "very_long_string": "x" * 100000,
            "unicode_text": "Hello 世界! 🌍 Привет! こんにちは!",
            "binary_like": bytes([i % 256 for i in range(1000)]).decode('latin-1'),
            "newlines": "\n" * 1000,
            "spaces": " " * 1000,
            "mixed": "".join([chr(i) for i in range(32, 127)]) * 100
        }
        
        for case_name, data in edge_cases.items():
            print(f"Testing edge case: {case_name}")
            
            compressed_data = await compression_engine.compress(
                content=data,
                algorithm=CompressionAlgorithm.GZIP,
                level=CompressionLevel.BALANCED
            )
            
            decompressed_data = await compression_engine.decompress(
                compressed_data=compressed_data,
                algorithm=CompressionAlgorithm.GZIP
            )
            
            assert decompressed_data == data
    
    @pytest.mark.asyncio
    async def test_live_compression_performance(self, compression_engine, sample_texts):
        """Test compression performance with larger datasets."""
        large_text = sample_texts["random_data"] * 10  # ~100KB of data
        
        performance_results = {}
        
        for algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.LZ4, CompressionAlgorithm.ZSTANDARD]:
            # Warm up
            await compression_engine.compress(
                content=large_text[:1000],
                algorithm=algorithm,
                level=CompressionLevel.BALANCED
            )
            
            # Performance test
            start_time = time.time()
            
            compressed_data = await compression_engine.compress(
                content=large_text,
                algorithm=algorithm,
                level=CompressionLevel.BALANCED
            )
            
            compression_time = time.time() - start_time
            
            # Decompression test
            start_time = time.time()
            decompressed_data = await compression_engine.decompress(
                compressed_data=compressed_data,
                algorithm=algorithm
            )
            decompression_time = time.time() - start_time
            
            # Verify integrity
            assert decompressed_data == large_text
            
            performance_results[algorithm] = {
                "compression_time": compression_time,
                "decompression_time": decompression_time,
                "compression_speed_mbps": (len(large_text) / compression_time) / (1024 * 1024),
                "decompression_speed_mbps": (len(large_text) / decompression_time) / (1024 * 1024),
                "compression_ratio": len(large_text) / len(compressed_data)
            }
        
        # Print performance results
        print("\nPerformance Results:")
        for algorithm, results in performance_results.items():
            print(f"{algorithm}:")
            print(f"  Compression: {results['compression_speed_mbps']:.2f} MB/s")
            print(f"  Decompression: {results['decompression_speed_mbps']:.2f} MB/s")
            print(f"  Ratio: {results['compression_ratio']:.2f}x")
    
    @pytest.mark.asyncio
    async def test_live_api_endpoints(self, client, sample_texts):
        """Test compression API endpoints with live data."""
        # Test compression endpoint
        compression_data = {
            "content": sample_texts["json_data"],
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=compression_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "compressed_data" in result
        assert "metrics" in result
        assert result["metrics"]["compression_ratio"] > 1.0
        
        # Test decompression endpoint
        decompression_data = {
            "compressed_data": result["compressed_data"],
            "algorithm": "gzip"
        }
        
        response = client.post("/api/v1/compression/decompress", json=decompression_data)
        assert response.status_code == 200
        
        decompressed_result = response.json()
        assert decompressed_result["decompressed_data"] == sample_texts["json_data"]
    
    @pytest.mark.asyncio
    async def test_live_compression_analysis(self, client, sample_texts):
        """Test compression analysis endpoint with live data."""
        analysis_data = {
            "content": sample_texts["code_sample"],
            "algorithms": ["gzip", "bzip2", "lz4"]
        }
        
        response = client.post("/api/v1/compression/analyze", json=analysis_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "analysis" in result
        assert "recommendations" in result
        assert len(result["analysis"]) > 0
        
        # Verify analysis contains expected metrics
        for algo_analysis in result["analysis"]:
            assert "algorithm" in algo_analysis
            assert "compression_ratio" in algo_analysis
            assert "compression_time" in algo_analysis
            assert "decompression_time" in algo_analysis
    
    @pytest.mark.asyncio
    async def test_live_batch_compression(self, client, sample_texts):
        """Test batch compression with multiple data types."""
        batch_data = {
            "items": [
                {
                    "id": "item1",
                    "content": sample_texts["lorem_ipsum"],
                    "parameters": {"algorithm": "gzip", "level": "balanced"}
                },
                {
                    "id": "item2", 
                    "content": sample_texts["json_data"],
                    "parameters": {"algorithm": "lz4", "level": "fast"}
                },
                {
                    "id": "item3",
                    "content": sample_texts["repetitive_text"],
                    "parameters": {"algorithm": "bzip2", "level": "maximum"}
                }
            ]
        }
        
        response = client.post("/api/v1/compression/compress/batch", json=batch_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "results" in result
        assert len(result["results"]) == 3
        
        # Verify each item was processed
        for item_result in result["results"]:
            assert "id" in item_result
            assert "compressed_data" in item_result
            assert "metrics" in item_result
            assert item_result["metrics"]["compression_ratio"] > 1.0
    
    @pytest.mark.asyncio
    async def test_live_error_handling(self, client):
        """Test error handling with invalid data."""
        # Test invalid algorithm
        invalid_data = {
            "content": "test content",
            "parameters": {
                "algorithm": "invalid_algorithm",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=invalid_data)
        assert response.status_code == 400
        
        # Test invalid compression level
        invalid_level_data = {
            "content": "test content",
            "parameters": {
                "algorithm": "gzip",
                "level": "invalid_level"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=invalid_level_data)
        assert response.status_code == 400
        
        # Test empty content
        empty_data = {
            "content": "",
            "parameters": {
                "algorithm": "gzip",
                "level": "balanced"
            }
        }
        
        response = client.post("/api/v1/compression/compress", json=empty_data)
        # Should handle empty content gracefully
        assert response.status_code in [200, 400]  # Depending on implementation


class TestLiveProtocolOptimization:
    """Live tests for protocol-aware optimization features."""
    
    @pytest.mark.asyncio
    async def test_live_protocol_analysis(self, client, sample_texts):
        """Test protocol-aware compression analysis."""
        protocol_data = {
            "content": sample_texts["json_data"],
            "protocol_context": {
                "protocol": "http",
                "transport_layer": "tcp",
                "application_layer": "http2",
                "delivery_method": "streaming",
                "network_conditions": {
                    "bandwidth": "high",
                    "latency": "low",
                    "packet_loss": "low"
                }
            }
        }
        
        response = client.post("/api/v1/compression/analyze/advanced", json=protocol_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "protocol_analysis" in result
        assert "optimization_recommendations" in result
        assert "performance_predictions" in result
    
    @pytest.mark.asyncio
    async def test_live_network_simulation(self, client, sample_texts):
        """Test compression under simulated network conditions."""
        network_scenarios = [
            {"bandwidth": "low", "latency": "high", "packet_loss": "high"},
            {"bandwidth": "high", "latency": "low", "packet_loss": "low"},
            {"bandwidth": "medium", "latency": "medium", "packet_loss": "medium"}
        ]
        
        for scenario in network_scenarios:
            simulation_data = {
                "content": sample_texts["json_data"],
                "network_conditions": scenario,
                "algorithms": ["gzip", "lz4", "zstandard"]
            }
            
            response = client.post("/api/v1/compression/simulate/network", json=simulation_data)
            assert response.status_code == 200
            
            result = response.json()
            assert "simulation_results" in result
            assert "optimal_algorithm" in result
            assert "performance_metrics" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
