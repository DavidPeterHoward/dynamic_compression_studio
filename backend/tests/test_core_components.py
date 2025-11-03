"""
Comprehensive unit tests for core components of the Dynamic Compression Algorithms backend.

This module tests all core functionality including:
- Content analysis
- Algorithm selection
- Parameter optimization
- Compression engine
- Metrics collection
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

from app.core.content_analyzer import ContentAnalyzer
from app.core.algorithm_selector import AlgorithmSelector
from app.core.parameter_optimizer import ParameterOptimizer
from app.core.compression_engine import CompressionEngine
from app.core.metrics_collector import MetricsCollector
from app.models.compression import (
    CompressionRequest, CompressionParameters, CompressionAlgorithm,
    ContentType, CompressionLevel
)
from tests.test_config import test_config, test_data_generator, performance_metrics


class TestContentAnalyzer:
    """Test suite for ContentAnalyzer component."""
    
    def test_analyze_content_basic(self, content_analyzer):
        """Test basic content analysis functionality."""
        content = "This is a test content for analysis."
        
        result = content_analyzer.analyze_content(content)
        
        assert isinstance(result, dict)
        assert "entropy" in result
        assert "content_type" in result
        assert "compression_potential" in result
        assert "patterns" in result
    
    def test_analyze_content_empty(self, content_analyzer):
        """Test content analysis with empty content."""
        result = content_analyzer.analyze_content("")
        
        assert isinstance(result, dict)
        assert result["entropy"] == 0.0
        assert result["content_type"]["type"] == "empty"
    
    def test_analyze_content_large(self, content_analyzer):
        """Test content analysis with large content."""
        large_content = test_data_generator.generate_text_content(10000)
        
        result = content_analyzer.analyze_content(large_content)
        
        assert isinstance(result, dict)
        assert result["entropy"] > 0.0
        assert result["content_type"]["type"] == "text"
    
    def test_analyze_content_repetitive(self, content_analyzer):
        """Test content analysis with repetitive content."""
        repetitive_content = "test " * 100
        
        result = content_analyzer.analyze_content(repetitive_content)
        
        assert isinstance(result, dict)
        assert result["redundancy_ratio"] > 0.5  # Should detect high redundancy
        assert result["compression_potential"] > 0.7  # Should have high compression potential
    
    def test_analyze_content_code(self, content_analyzer):
        """Test content analysis with code content."""
        code_content = """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        """
        
        result = content_analyzer.analyze_content(code_content)
        
        assert isinstance(result, dict)
        assert result["content_type"]["type"] == "code"
        assert result["language_complexity"] > 0.0
    
    def test_analyze_content_json(self, content_analyzer):
        """Test content analysis with JSON content."""
        json_content = '{"name": "test", "value": 123}'
        
        result = content_analyzer.analyze_content(json_content)
        
        assert isinstance(result, dict)
        assert result["content_type"]["type"] == "structured"
    
    def test_calculate_entropy(self, content_analyzer):
        """Test entropy calculation."""
        # Test with random content
        random_content = "abcdefghijklmnopqrstuvwxyz"
        entropy = content_analyzer._calculate_entropy(random_content)
        assert 4.0 < entropy < 5.0  # Expected entropy for random letters
        
        # Test with repetitive content
        repetitive_content = "aaaa"
        entropy = content_analyzer._calculate_entropy(repetitive_content)
        assert entropy == 0.0  # No entropy for uniform content
    
    def test_detect_patterns(self, content_analyzer):
        """Test pattern detection."""
        content = "test test test test test"
        
        patterns = content_analyzer._detect_patterns(content)
        
        assert isinstance(patterns, dict)
        assert "repetitive_patterns" in patterns
        assert len(patterns["repetitive_patterns"]) > 0
    
    def test_classify_content_type(self, content_analyzer):
        """Test content type classification."""
        # Test text classification
        text_content = "This is a normal text content."
        result = content_analyzer._classify_content_type(text_content)
        assert result["type"] == "text"
        
        # Test code classification
        code_content = "def test(): return True"
        result = content_analyzer._classify_content_type(code_content)
        assert result["type"] == "code"
        
        # Test structured classification
        json_content = '{"key": "value"}'
        result = content_analyzer._classify_content_type(json_content)
        assert result["type"] == "structured"


class TestAlgorithmSelector:
    """Test suite for AlgorithmSelector component."""
    
    def test_select_algorithm_basic(self, algorithm_selector):
        """Test basic algorithm selection."""
        content_analysis = {
            "entropy": 4.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.6
        }
        
        algorithm = algorithm_selector.select_algorithm(content_analysis)
        
        assert isinstance(algorithm, CompressionAlgorithm)
        assert algorithm in [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZSTD,
            CompressionAlgorithm.BROTLI
        ]
    
    def test_select_algorithm_text_content(self, algorithm_selector):
        """Test algorithm selection for text content."""
        content_analysis = {
            "entropy": 4.5,
            "content_type": {"type": "text"},
            "compression_potential": 0.7,
            "redundancy_ratio": 0.3
        }
        
        algorithm = algorithm_selector.select_algorithm(content_analysis)
        
        # Should select a good general-purpose algorithm for text
        assert algorithm in [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.ZSTD
        ]
    
    def test_select_algorithm_repetitive_content(self, algorithm_selector):
        """Test algorithm selection for repetitive content."""
        content_analysis = {
            "entropy": 1.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.9,
            "redundancy_ratio": 0.8
        }
        
        algorithm = algorithm_selector.select_algorithm(content_analysis)
        
        # Should select an algorithm good for repetitive content
        assert algorithm in [
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.ZSTD
        ]
    
    def test_select_algorithm_code_content(self, algorithm_selector):
        """Test algorithm selection for code content."""
        content_analysis = {
            "entropy": 3.5,
            "content_type": {"type": "code"},
            "compression_potential": 0.6,
            "language_complexity": 0.7
        }
        
        algorithm = algorithm_selector.select_algorithm(content_analysis)
        
        # Should select an algorithm good for structured content
        assert algorithm in [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZSTD
        ]
    
    def test_get_algorithm_recommendations(self, algorithm_selector):
        """Test getting algorithm recommendations."""
        content_analysis = {
            "entropy": 4.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.6
        }
        
        recommendations = algorithm_selector.get_algorithm_recommendations(
            content_analysis, num_recommendations=3
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 3
        for rec in recommendations:
            assert "algorithm" in rec
            assert "score" in rec
            assert "reason" in rec


class TestParameterOptimizer:
    """Test suite for ParameterOptimizer component."""
    
    def test_optimize_parameters_basic(self, parameter_optimizer):
        """Test basic parameter optimization."""
        algorithm = CompressionAlgorithm.GZIP
        content_analysis = {
            "entropy": 4.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.6
        }
        base_parameters = CompressionParameters(
            algorithm=algorithm,
            level="balanced"
        )
        
        optimized_params = parameter_optimizer.optimize_parameters(
            algorithm, content_analysis, base_parameters
        )
        
        assert isinstance(optimized_params, dict)
        assert "level" in optimized_params
        assert "window_size" in optimized_params
    
    def test_optimize_parameters_gzip(self, parameter_optimizer):
        """Test parameter optimization for GZIP."""
        algorithm = CompressionAlgorithm.GZIP
        content_analysis = {
            "entropy": 4.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.6
        }
        base_parameters = CompressionParameters(
            algorithm=algorithm,
            level="balanced"
        )
        
        optimized_params = parameter_optimizer.optimize_parameters(
            algorithm, content_analysis, base_parameters
        )
        
        assert optimized_params["level"] in [1, 6, 9]  # Valid GZIP levels
    
    def test_optimize_parameters_lzma(self, parameter_optimizer):
        """Test parameter optimization for LZMA."""
        algorithm = CompressionAlgorithm.LZMA
        content_analysis = {
            "entropy": 4.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.6
        }
        base_parameters = CompressionParameters(
            algorithm=algorithm,
            level="balanced"
        )
        
        optimized_params = parameter_optimizer.optimize_parameters(
            algorithm, content_analysis, base_parameters
        )
        
        assert optimized_params["level"] in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # Valid LZMA levels
    
    def test_optimize_parameters_high_compression(self, parameter_optimizer):
        """Test parameter optimization for high compression scenarios."""
        algorithm = CompressionAlgorithm.GZIP
        content_analysis = {
            "entropy": 2.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.9,
            "redundancy_ratio": 0.7
        }
        base_parameters = CompressionParameters(
            algorithm=algorithm,
            level="balanced"
        )
        
        optimized_params = parameter_optimizer.optimize_parameters(
            algorithm, content_analysis, base_parameters
        )
        
        # Should optimize for maximum compression
        assert optimized_params["level"] == 9
    
    def test_optimize_parameters_fast_compression(self, parameter_optimizer):
        """Test parameter optimization for fast compression scenarios."""
        algorithm = CompressionAlgorithm.GZIP
        content_analysis = {
            "entropy": 5.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.3,
            "redundancy_ratio": 0.1
        }
        base_parameters = CompressionParameters(
            algorithm=algorithm,
            level="balanced"
        )
        
        optimized_params = parameter_optimizer.optimize_parameters(
            algorithm, content_analysis, base_parameters
        )
        
        # Should optimize for speed
        assert optimized_params["level"] == 1


class TestCompressionEngine:
    """Test suite for CompressionEngine component."""
    
    @pytest.mark.asyncio
    async def test_compress_basic(self, compression_engine):
        """Test basic compression functionality."""
        request = CompressionRequest(
            content="This is a test content for compression.",
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level="balanced"
            )
        )
        
        response = await compression_engine.compress(request)
        
        assert response.success is True
        assert response.result is not None
        assert response.result.original_size > 0
        assert response.result.compressed_size > 0
        assert response.result.compression_ratio > 1.0
        assert response.result.algorithm_used == CompressionAlgorithm.GZIP
    
    @pytest.mark.asyncio
    async def test_compress_empty_content(self, compression_engine):
        """Test compression with empty content."""
        request = CompressionRequest(
            content="",
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level="balanced"
            )
        )
        
        response = await compression_engine.compress(request)
        
        assert response.success is False
        assert "No content provided" in response.message
    
    @pytest.mark.asyncio
    async def test_compress_different_algorithms(self, compression_engine):
        """Test compression with different algorithms."""
        content = "This is a test content for compression testing with different algorithms."
        
        algorithms = [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.BROTLI
        ]
        
        results = {}
        for algorithm in algorithms:
            request = CompressionRequest(
                content=content,
                parameters=CompressionParameters(
                    algorithm=algorithm,
                    level="balanced"
                )
            )
            
            response = await compression_engine.compress(request)
            assert response.success is True
            results[algorithm] = response.result
        
        # All algorithms should produce valid results
        assert len(results) == len(algorithms)
        
        # Compression ratios should be reasonable
        for result in results.values():
            assert result.compression_ratio > 1.0
            assert result.compression_ratio < 10.0  # Shouldn't be unreasonably high
    
    @pytest.mark.asyncio
    async def test_compress_content_aware(self, compression_engine):
        """Test content-aware compression."""
        request = CompressionRequest(
            content="This is a test content for content-aware compression.",
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.CONTENT_AWARE,
                level="balanced"
            )
        )
        
        response = await compression_engine.compress(request)
        
        assert response.success is True
        assert response.result is not None
        assert response.result.algorithm_used != CompressionAlgorithm.CONTENT_AWARE
        # Should have selected a specific algorithm
    
    @pytest.mark.asyncio
    async def test_compress_large_content(self, compression_engine):
        """Test compression with large content."""
        large_content = test_data_generator.generate_text_content(50000)
        
        request = CompressionRequest(
            content=large_content,
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level="balanced"
            )
        )
        
        response = await compression_engine.compress(request)
        
        assert response.success is True
        assert response.result is not None
        assert response.result.original_size > 10000
        assert response.result.compression_ratio > 1.0
    
    @pytest.mark.asyncio
    async def test_compress_repetitive_content(self, compression_engine):
        """Test compression with repetitive content."""
        repetitive_content = "test " * 1000
        
        request = CompressionRequest(
            content=repetitive_content,
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level="balanced"
            )
        )
        
        response = await compression_engine.compress(request)
        
        assert response.success is True
        assert response.result is not None
        # Repetitive content should compress well
        assert response.result.compression_ratio > 2.0
    
    def test_get_compression_level(self, compression_engine):
        """Test compression level conversion."""
        assert compression_engine._get_compression_level("fast") == 1
        assert compression_engine._get_compression_level("balanced") == 6
        assert compression_engine._get_compression_level("optimal") == 9
        assert compression_engine._get_compression_level("maximum") == 9
        assert compression_engine._get_compression_level("unknown") == 6  # Default


class TestMetricsCollector:
    """Test suite for MetricsCollector component."""
    
    def test_collect_compression_metrics(self, metrics_collector):
        """Test compression metrics collection."""
        original_size = 1000
        compressed_size = 400
        compression_time = 0.1
        
        metrics = metrics_collector.collect_compression_metrics(
            original_size, compressed_size, compression_time
        )
        
        assert isinstance(metrics, dict)
        assert metrics["compression_ratio"] == 2.5
        assert metrics["compression_percentage"] == 60.0
        assert metrics["compression_speed_mbps"] > 0
    
    def test_collect_performance_metrics(self, metrics_collector):
        """Test performance metrics collection."""
        metrics = metrics_collector.collect_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
    
    def test_collect_quality_metrics(self, metrics_collector):
        """Test quality metrics collection."""
        original_content = "This is a test content."
        compressed_data = b"compressed_data"
        
        metrics = metrics_collector.collect_quality_metrics(
            original_content, compressed_data
        )
        
        assert isinstance(metrics, dict)
        assert "information_preservation" in metrics
        assert "entropy_reduction" in metrics
    
    def test_update_algorithm_metrics(self, metrics_collector):
        """Test algorithm metrics update."""
        algorithm = CompressionAlgorithm.GZIP
        metrics = {
            "compression_ratio": 2.5,
            "compression_time": 0.1,
            "quality_score": 0.9
        }
        
        metrics_collector.update_algorithm_metrics(algorithm, metrics)
        
        # Should update internal metrics storage
        assert algorithm in metrics_collector.algorithm_metrics
    
    def test_get_metrics_summary(self, metrics_collector):
        """Test metrics summary generation."""
        # Add some test metrics
        metrics_collector.update_algorithm_metrics(
            CompressionAlgorithm.GZIP,
            {"compression_ratio": 2.5, "compression_time": 0.1}
        )
        
        summary = metrics_collector.get_metrics_summary()
        
        assert isinstance(summary, dict)
        assert "compression_metrics" in summary
        assert "performance_metrics" in summary
        assert "quality_metrics" in summary


class TestIntegration:
    """Integration tests for the complete compression pipeline."""
    
    @pytest.mark.asyncio
    async def test_complete_compression_pipeline(self, compression_engine, content_analyzer, algorithm_selector, parameter_optimizer):
        """Test the complete compression pipeline."""
        content = "This is a comprehensive test of the complete compression pipeline."
        
        # Step 1: Content Analysis
        content_analysis = content_analyzer.analyze_content(content)
        assert isinstance(content_analysis, dict)
        
        # Step 2: Algorithm Selection
        algorithm = algorithm_selector.select_algorithm(content_analysis)
        assert isinstance(algorithm, CompressionAlgorithm)
        
        # Step 3: Parameter Optimization
        base_parameters = CompressionParameters(
            algorithm=algorithm,
            level="balanced"
        )
        optimized_params = parameter_optimizer.optimize_parameters(
            algorithm, content_analysis, base_parameters
        )
        assert isinstance(optimized_params, dict)
        
        # Step 4: Compression
        request = CompressionRequest(
            content=content,
            parameters=CompressionParameters(
                algorithm=algorithm,
                level="balanced"
            )
        )
        response = await compression_engine.compress(request)
        
        assert response.success is True
        assert response.result is not None
        assert response.result.algorithm_used == algorithm
    
    @pytest.mark.asyncio
    async def test_error_handling(self, compression_engine):
        """Test error handling in the compression pipeline."""
        # Test with invalid algorithm
        request = CompressionRequest(
            content="Test content",
            parameters=CompressionParameters(
                algorithm="INVALID_ALGORITHM",  # This should cause an error
                level="balanced"
            )
        )
        
        response = await compression_engine.compress(request)
        
        # Should handle the error gracefully
        assert response.success is False
        assert "error" in response.__dict__


class TestPerformance:
    """Performance tests for the compression system."""
    
    @pytest.mark.asyncio
    async def test_compression_performance(self, compression_engine):
        """Test compression performance with different content sizes."""
        sizes = [100, 1000, 10000, 50000]
        
        for size in sizes:
            content = test_data_generator.generate_text_content(size)
            
            performance_metrics.start_timer(f"compress_{size}")
            
            request = CompressionRequest(
                content=content,
                parameters=CompressionParameters(
                    algorithm=CompressionAlgorithm.GZIP,
                    level="balanced"
                )
            )
            
            response = await compression_engine.compress(request)
            performance_metrics.end_timer(f"compress_{size}")
            
            assert response.success is True
            assert response.result.compression_time < 5.0  # Should complete within 5 seconds
    
    def test_content_analysis_performance(self, content_analyzer):
        """Test content analysis performance."""
        sizes = [100, 1000, 10000, 50000]
        
        for size in sizes:
            content = test_data_generator.generate_text_content(size)
            
            performance_metrics.start_timer(f"analyze_{size}")
            result = content_analyzer.analyze_content(content)
            performance_metrics.end_timer(f"analyze_{size}")
            
            assert isinstance(result, dict)
            assert "entropy" in result
    
    def test_algorithm_selection_performance(self, algorithm_selector):
        """Test algorithm selection performance."""
        content_analysis = {
            "entropy": 4.0,
            "content_type": {"type": "text"},
            "compression_potential": 0.6
        }
        
        performance_metrics.start_timer("algorithm_selection")
        algorithm = algorithm_selector.select_algorithm(content_analysis)
        performance_metrics.end_timer("algorithm_selection")
        
        assert isinstance(algorithm, CompressionAlgorithm)


# Run performance summary after all tests
def pytest_sessionfinish(session, exitstatus):
    """Generate performance summary after test session."""
    summary = performance_metrics.get_summary()
    print("\n" + "="*50)
    print("PERFORMANCE SUMMARY")
    print("="*50)
    for test_name, metrics in summary.items():
        if isinstance(metrics, dict) and "average_time" in metrics:
            print(f"{test_name}: {metrics['average_time']:.4f}s avg ({metrics['count']} runs)")
    print("="*50)
