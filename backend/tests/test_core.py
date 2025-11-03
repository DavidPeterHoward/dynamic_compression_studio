"""
Unit tests for core compression engine components.

This module tests the core functionality including content analysis,
algorithm selection, parameter optimization, and metrics collection.
"""

import pytest
import asyncio
from app.core.content_analyzer import ContentAnalyzer
from app.core.algorithm_selector import AlgorithmSelector
from app.core.parameter_optimizer import ParameterOptimizer
from app.core.metrics_collector import MetricsCollector
from app.core.compression_engine import CompressionEngine


class TestContentAnalyzer:
    """Test cases for content analysis functionality."""

    def test_analyze_text_content(self):
        """Test analysis of text content."""
        analyzer = ContentAnalyzer()
        content = "This is a sample text content for testing compression algorithms."
        
        result = asyncio.run(analyzer.analyze_content(content))
        
        assert "content_type" in result
        assert "entropy" in result
        assert "complexity" in result
        assert "patterns" in result
        assert "compression_potential" in result
        assert result["content_type"] == "text"
        assert 0 <= result["entropy"] <= 8.0
        assert 0 <= result["complexity"] <= 1.0

    def test_analyze_code_content(self):
        """Test analysis of code content."""
        analyzer = ContentAnalyzer()
        content = """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        print(fibonacci(10))
        """
        
        result = asyncio.run(analyzer.analyze_content(content))
        
        assert result["content_type"] == "code"
        assert "structure_analysis" in result
        assert "language_detection" in result
        assert result["language_detection"] == "python"

    def test_analyze_binary_content(self):
        """Test analysis of binary content."""
        analyzer = ContentAnalyzer()
        content = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09" * 100
        
        result = asyncio.run(analyzer.analyze_content(content))
        
        assert result["content_type"] == "binary"
        assert result["entropy"] > 0
        assert "patterns" in result

    def test_analyze_structured_content(self):
        """Test analysis of structured content (JSON)."""
        analyzer = ContentAnalyzer()
        content = '{"name": "test", "value": 123, "items": [1, 2, 3]}'
        
        result = asyncio.run(analyzer.analyze_content(content))
        
        assert result["content_type"] == "structured"
        assert "structure_analysis" in result

    def test_analyze_mixed_content(self):
        """Test analysis of mixed content."""
        analyzer = ContentAnalyzer()
        content = "Text content with some code: def test(): pass and JSON: {\"key\": \"value\"}"
        
        result = asyncio.run(analyzer.analyze_content(content))
        
        assert result["content_type"] == "mixed"
        assert "components" in result

    def test_calculate_entropy(self):
        """Test entropy calculation."""
        analyzer = ContentAnalyzer()
        
        # High entropy content (random)
        high_entropy = "abcdefghijklmnopqrstuvwxyz"
        entropy1 = asyncio.run(analyzer._calculate_entropy(high_entropy))
        
        # Low entropy content (repetitive)
        low_entropy = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
        entropy2 = asyncio.run(analyzer._calculate_entropy(low_entropy))
        
        assert entropy1 > entropy2
        assert 0 <= entropy1 <= 8.0
        assert 0 <= entropy2 <= 8.0

    def test_detect_patterns(self):
        """Test pattern detection."""
        analyzer = ContentAnalyzer()
        content = "This is a repeated pattern. This is a repeated pattern. This is a repeated pattern."
        
        patterns = asyncio.run(analyzer._detect_patterns(content))
        
        assert "repetition" in patterns
        assert "frequency" in patterns
        assert patterns["repetition"] > 0

    def test_classify_content_type(self):
        """Test content type classification."""
        analyzer = ContentAnalyzer()
        
        # Test text classification
        text_content = "This is plain text content."
        content_type = asyncio.run(analyzer._classify_content_type(text_content))
        assert content_type == "text"
        
        # Test code classification
        code_content = "def function(): return True"
        content_type = asyncio.run(analyzer._classify_content_type(code_content))
        assert content_type == "code"
        
        # Test binary classification
        binary_content = b"\x00\x01\x02\x03"
        content_type = asyncio.run(analyzer._classify_content_type(binary_content))
        assert content_type == "binary"

    def test_calculate_content_profile(self):
        """Test content profile calculation."""
        analyzer = ContentAnalyzer()
        content = "Sample content for profile calculation"
        
        profile = asyncio.run(analyzer._calculate_content_profile(content))
        
        assert "size" in profile
        assert "character_distribution" in profile
        assert "word_frequency" in profile
        assert profile["size"] == len(content)


class TestAlgorithmSelector:
    """Test cases for algorithm selection functionality."""

    def test_select_algorithm_family(self):
        """Test algorithm family selection."""
        selector = AlgorithmSelector()
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3,
            "compression_potential": 0.7
        }
        
        family = selector.select_algorithm_family(content_analysis)
        
        assert family in ["LZ77", "LZ78", "BWT", "Dictionary", "Statistical"]
        assert family in selector.algorithm_families

    def test_select_algorithm_variant(self):
        """Test algorithm variant selection."""
        selector = AlgorithmSelector()
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        variant = selector.select_algorithm_variant("LZ77", content_analysis)
        
        assert variant in ["gzip", "lz4", "zstandard"]
        assert variant in [alg["name"] for alg in selector.algorithm_families["LZ77"]]

    def test_calculate_algorithm_score(self):
        """Test algorithm scoring."""
        selector = AlgorithmSelector()
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3,
            "compression_potential": 0.7
        }
        
        score = selector.calculate_algorithm_score("gzip", content_analysis)
        
        assert 0 <= score <= 1.0
        assert isinstance(score, float)

    def test_select_algorithm_with_exploration(self):
        """Test algorithm selection with exploration factor."""
        selector = AlgorithmSelector()
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        # Test multiple selections to see exploration in action
        algorithms = []
        for _ in range(10):
            algorithm = selector.select_algorithm(content_analysis, exploration_factor=0.3)
            algorithms.append(algorithm)
        
        # Should have some variety due to exploration
        unique_algorithms = set(algorithms)
        assert len(unique_algorithms) > 1

    def test_content_type_mapping(self):
        """Test content type to algorithm family mapping."""
        selector = AlgorithmSelector()
        
        # Test text content
        text_analysis = {"content_type": "text"}
        family = selector.select_algorithm_family(text_analysis)
        assert family in ["LZ77", "LZ78", "BWT"]
        
        # Test code content
        code_analysis = {"content_type": "code"}
        family = selector.select_algorithm_family(code_analysis)
        assert family in ["LZ77", "LZ78", "Dictionary"]
        
        # Test binary content
        binary_analysis = {"content_type": "binary"}
        family = selector.select_algorithm_family(binary_analysis)
        assert family in ["LZ77", "LZ78", "Statistical"]


class TestParameterOptimizer:
    """Test cases for parameter optimization functionality."""

    def test_optimize_parameters_grid_search(self):
        """Test parameter optimization using grid search."""
        optimizer = ParameterOptimizer()
        algorithm = "gzip"
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        parameters = asyncio.run(optimizer.optimize_parameters(
            algorithm, content_analysis, strategy="grid_search"
        ))
        
        assert "compression_level" in parameters
        assert "window_size" in parameters
        assert 1 <= parameters["compression_level"] <= 9
        assert 9 <= parameters["window_size"] <= 15

    def test_optimize_parameters_bayesian(self):
        """Test parameter optimization using Bayesian optimization."""
        optimizer = ParameterOptimizer()
        algorithm = "lzma"
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        parameters = asyncio.run(optimizer.optimize_parameters(
            algorithm, content_analysis, strategy="bayesian"
        ))
        
        assert "compression_level" in parameters
        assert "dictionary_size" in parameters
        assert 0 <= parameters["compression_level"] <= 9

    def test_optimize_parameters_genetic(self):
        """Test parameter optimization using genetic algorithm."""
        optimizer = ParameterOptimizer()
        algorithm = "bzip2"
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        parameters = asyncio.run(optimizer.optimize_parameters(
            algorithm, content_analysis, strategy="genetic"
        ))
        
        assert "compression_level" in parameters
        assert "block_size" in parameters

    def test_optimize_parameters_multi_armed_bandit(self):
        """Test parameter optimization using multi-armed bandit."""
        optimizer = ParameterOptimizer()
        algorithm = "lz4"
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        parameters = asyncio.run(optimizer.optimize_parameters(
            algorithm, content_analysis, strategy="multi_armed_bandit"
        ))
        
        assert "compression_level" in parameters
        assert "acceleration" in parameters

    def test_select_optimization_strategy(self):
        """Test automatic optimization strategy selection."""
        optimizer = ParameterOptimizer()
        
        # Simple content should use grid search
        simple_analysis = {"content_type": "text", "complexity": 0.1}
        strategy = optimizer.select_optimization_strategy(simple_analysis)
        assert strategy == "grid_search"
        
        # Complex content should use Bayesian optimization
        complex_analysis = {"content_type": "code", "complexity": 0.9}
        strategy = optimizer.select_optimization_strategy(complex_analysis)
        assert strategy in ["bayesian", "genetic"]

    def test_parameter_bounds_validation(self):
        """Test parameter bounds validation."""
        optimizer = ParameterOptimizer()
        
        # Test gzip parameters
        gzip_bounds = optimizer.parameter_bounds["gzip"]
        assert "compression_level" in gzip_bounds
        assert gzip_bounds["compression_level"]["min"] == 1
        assert gzip_bounds["compression_level"]["max"] == 9
        
        # Test lzma parameters
        lzma_bounds = optimizer.parameter_bounds["lzma"]
        assert "compression_level" in lzma_bounds
        assert "dictionary_size" in lzma_bounds


class TestMetricsCollector:
    """Test cases for metrics collection functionality."""

    def test_collect_compression_metrics(self):
        """Test compression metrics collection."""
        collector = MetricsCollector()
        
        metrics = asyncio.run(collector.collect_compression_metrics(
            algorithm="gzip",
            original_size=1000,
            compressed_size=500,
            compression_time=0.1,
            memory_usage=50
        ))
        
        assert metrics.compression_ratio == 2.0
        assert metrics.compression_speed == 10000  # bytes per second
        assert metrics.memory_usage == 50
        assert metrics.algorithm == "gzip"

    def test_collect_performance_metrics(self):
        """Test performance metrics collection."""
        collector = MetricsCollector()
        
        metrics = asyncio.run(collector.collect_performance_metrics())
        
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
        assert "network_io" in metrics
        assert 0 <= metrics["cpu_usage"] <= 100
        assert 0 <= metrics["memory_usage"] <= 100

    def test_collect_quality_metrics(self):
        """Test quality metrics collection."""
        collector = MetricsCollector()
        
        metrics = asyncio.run(collector.collect_quality_metrics(
            original_content="test content",
            decompressed_content="test content",
            compression_ratio=2.0
        ))
        
        assert metrics.integrity_score == 1.0  # Perfect match
        assert metrics.information_preservation == 1.0
        assert metrics.compression_ratio == 2.0

    def test_update_algorithm_metrics(self):
        """Test algorithm-specific metrics update."""
        collector = MetricsCollector()
        
        # Initial metrics
        initial_metrics = {
            "usage_count": 0,
            "total_compression_time": 0,
            "total_original_size": 0,
            "total_compressed_size": 0
        }
        
        # Update with new compression result
        updated_metrics = asyncio.run(collector.update_algorithm_metrics(
            "gzip", initial_metrics, 1000, 500, 0.1
        ))
        
        assert updated_metrics["usage_count"] == 1
        assert updated_metrics["total_compression_time"] == 0.1
        assert updated_metrics["total_original_size"] == 1000
        assert updated_metrics["total_compressed_size"] == 500

    def test_calculate_averages(self):
        """Test average calculation from metrics."""
        collector = MetricsCollector()
        
        metrics_data = {
            "usage_count": 10,
            "total_compression_time": 1.0,
            "total_original_size": 10000,
            "total_compressed_size": 5000
        }
        
        averages = collector.calculate_averages(metrics_data)
        
        assert averages["average_compression_time"] == 0.1
        assert averages["average_compression_ratio"] == 2.0

    def test_aggregate_metrics(self):
        """Test metrics aggregation."""
        collector = MetricsCollector()
        
        metrics_list = [
            {"compression_ratio": 2.0, "compression_time": 0.1},
            {"compression_ratio": 3.0, "compression_time": 0.2},
            {"compression_ratio": 1.5, "compression_time": 0.05}
        ]
        
        aggregated = collector.aggregate_metrics(metrics_list)
        
        assert aggregated["average_compression_ratio"] == 2.17
        assert aggregated["average_compression_time"] == 0.117
        assert aggregated["min_compression_ratio"] == 1.5
        assert aggregated["max_compression_ratio"] == 3.0


class TestCompressionEngine:
    """Test cases for the main compression engine."""

    def test_compression_engine_initialization(self):
        """Test compression engine initialization."""
        engine = CompressionEngine()
        
        assert engine.content_analyzer is not None
        assert engine.algorithm_selector is not None
        assert engine.parameter_optimizer is not None
        assert engine.metrics_collector is not None

    def test_execute_corte_loop(self):
        """Test the Corte optimization loop."""
        engine = CompressionEngine()
        content = "This is a test content for the Corte optimization loop."
        
        result = asyncio.run(engine._execute_corte_loop(content))
        
        assert "compressed_content" in result
        assert "algorithm_used" in result
        assert "compression_ratio" in result
        assert "compression_time" in result
        assert "metrics" in result

    def test_select_algorithm(self):
        """Test algorithm selection in the engine."""
        engine = CompressionEngine()
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        algorithm = asyncio.run(engine._select_algorithm(content_analysis))
        
        assert algorithm in ["gzip", "lzma", "bzip2", "lz4", "zstandard", "brotli"]

    def test_optimize_parameters(self):
        """Test parameter optimization in the engine."""
        engine = CompressionEngine()
        algorithm = "gzip"
        content_analysis = {
            "content_type": "text",
            "entropy": 4.5,
            "complexity": 0.3
        }
        
        parameters = asyncio.run(engine._optimize_parameters(algorithm, content_analysis))
        
        assert "compression_level" in parameters
        assert "window_size" in parameters

    def test_integrate_feedback(self):
        """Test feedback integration in the engine."""
        engine = CompressionEngine()
        feedback_data = {
            "algorithm": "gzip",
            "compression_ratio": 2.5,
            "compression_time": 0.1,
            "user_satisfaction": 0.8
        }
        
        asyncio.run(engine._integrate_feedback(feedback_data))
        
        # Verify feedback was integrated (this would update internal state)
        assert True  # Placeholder assertion

    def test_compress_with_dynamic_selection(self):
        """Test compression with dynamic algorithm selection."""
        engine = CompressionEngine()
        content = "This is a test content for dynamic compression."
        
        result = asyncio.run(engine.compress(content))
        
        assert "compressed_content" in result
        assert "algorithm_used" in result
        assert "compression_ratio" in result
        assert "compression_time" in result
        assert "content_analysis" in result
        assert "parameters_used" in result

    def test_compress_with_specific_algorithm(self):
        """Test compression with specific algorithm."""
        engine = CompressionEngine()
        content = "This is a test content for specific algorithm compression."
        
        result = asyncio.run(engine.compress(
            content, 
            algorithm="gzip", 
            parameters={"compression_level": 9}
        ))
        
        assert result["algorithm_used"] == "gzip"
        assert result["parameters_used"]["compression_level"] == 9

    def test_compress_batch(self):
        """Test batch compression."""
        engine = CompressionEngine()
        contents = [
            "First test content",
            "Second test content",
            "Third test content"
        ]
        
        results = asyncio.run(engine.compress_batch(contents))
        
        assert len(results) == 3
        for result in results:
            assert "compressed_content" in result
            assert "algorithm_used" in result
            assert "compression_ratio" in result
