import pytest
from core.tester import PerformanceTester
from core.analyzer import WebPerformanceAnalyzer
from metrics.metrics import PerformanceMetrics, LoadingTimeMetrics
from utils.config import TestConfig

class TestSimple:
    """Simple test suite to validate basic functionality"""
    
    def test_config_creation(self):
        """Test that TestConfig can be created"""
        config = TestConfig()
        assert config.timeout == 30
        assert config.mode.value == "standard"
    
    def test_loading_metrics_creation(self):
        """Test that LoadingTimeMetrics can be created"""
        metrics = LoadingTimeMetrics()
        assert metrics.first_contentful_paint == 0.0
        assert metrics.largest_contentful_paint == 0.0
    
    def test_performance_metrics_creation(self):
        """Test that PerformanceMetrics can be created"""
        loading_metrics = LoadingTimeMetrics()
        metrics = PerformanceMetrics(
            page_name="test_page",
            url="http://localhost:3000",
            loading_metrics=loading_metrics
        )
        assert metrics.page_name == "test_page"
        assert metrics.url == "http://localhost:3000"
    
    def test_tester_creation(self):
        """Test that PerformanceTester can be created"""
        config = TestConfig()
        tester = PerformanceTester(config)
        assert tester.config == config
    
    def test_analyzer_creation(self):
        """Test that WebPerformanceAnalyzer can be created"""
        config = TestConfig()
        analyzer = WebPerformanceAnalyzer(config)
        assert analyzer.config == config
