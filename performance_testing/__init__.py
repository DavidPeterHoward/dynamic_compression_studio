# Performance Testing Framework for Dynamic Compression Algorithms
# Comprehensive web performance testing and optimization tools

__version__ = "1.0.0"
__author__ = "Dynamic Compression Team"

from .core import PerformanceTester, WebPerformanceAnalyzer
from .metrics import PerformanceMetrics, LoadingTimeMetrics
from .reports import PerformanceReport, OptimizationRecommendations
from .utils import TestConfig, BrowserConfig

__all__ = [
    "PerformanceTester",
    "WebPerformanceAnalyzer", 
    "PerformanceMetrics",
    "LoadingTimeMetrics",
    "PerformanceReport",
    "OptimizationRecommendations",
    "TestConfig",
    "BrowserConfig"
]
