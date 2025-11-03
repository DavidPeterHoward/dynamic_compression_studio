"""
Test configuration for the Dynamic Compression Algorithms backend.

This module provides test-specific configuration and utilities for
comprehensive testing of all application components.
"""

import os
import pytest
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch

from app.config import settings
from app.database import get_async_db, init_db, close_db
from app.core.compression_engine import CompressionEngine
from app.core.content_analyzer import ContentAnalyzer
from app.core.algorithm_selector import AlgorithmSelector
from app.core.parameter_optimizer import ParameterOptimizer
from app.core.metrics_collector import MetricsCollector


class TestConfig:
    """Test configuration class for managing test environment."""
    
    def __init__(self):
        self.test_data_dir = "tests/test_data"
        self.test_output_dir = "tests/test_output"
        self.max_test_file_size = 1024 * 1024  # 1MB
        self.test_timeout = 30  # seconds
        
        # Test content samples
        self.sample_texts = {
            "simple": "This is a simple test text for compression testing.",
            "repetitive": "test test test test test test test test test test",
            "complex": """
            This is a more complex text with various patterns and structures.
            It contains multiple sentences, punctuation, and different character types.
            The goal is to test compression algorithms on realistic content.
            """,
            "code": """
            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            
            for i in range(10):
                print(fibonacci(i))
            """,
            "json": '{"name": "test", "value": 123, "nested": {"key": "value"}}',
            "xml": '<root><item>test</item><item>data</item></root>'
        }
        
        # Expected compression ratios (approximate)
        self.expected_ratios = {
            "simple": 0.7,
            "repetitive": 0.3,
            "complex": 0.6,
            "code": 0.5,
            "json": 0.4,
            "xml": 0.4
        }
    
    def setup_test_environment(self):
        """Set up test environment variables."""
        os.environ.setdefault('TESTING', 'true')
        os.environ.setdefault('POSTGRES_SERVER', 'localhost')
        os.environ.setdefault('POSTGRES_PORT', '5432')
        os.environ.setdefault('POSTGRES_USER', 'test_user')
        os.environ.setdefault('POSTGRES_PASSWORD', 'test_password')
        os.environ.setdefault('POSTGRES_DB', 'test_compression_db')
        os.environ.setdefault('REDIS_HOST', 'localhost')
        os.environ.setdefault('REDIS_PORT', '6379')
        os.environ.setdefault('DEBUG', 'true')
    
    def create_test_directories(self):
        """Create test directories if they don't exist."""
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
    
    def cleanup_test_files(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        os.makedirs(self.test_output_dir, exist_ok=True)


class MockDatabase:
    """Mock database for testing without real database connection."""
    
    def __init__(self):
        self.data = {}
        self.queries = []
    
    async def execute(self, query, params=None):
        """Mock execute method."""
        self.queries.append((query, params))
        return Mock()
    
    async def fetch_one(self, query, params=None):
        """Mock fetch_one method."""
        self.queries.append((query, params))
        return {"id": 1, "name": "test"}
    
    async def fetch_all(self, query, params=None):
        """Mock fetch_all method."""
        self.queries.append((query, params))
        return [{"id": 1, "name": "test"}]
    
    async def commit(self):
        """Mock commit method."""
        pass
    
    async def rollback(self):
        """Mock rollback method."""
        pass


class TestDataGenerator:
    """Generate test data for comprehensive testing."""
    
    def __init__(self):
        self.test_config = TestConfig()
    
    def generate_text_content(self, size: int = 1024) -> str:
        """Generate text content of specified size."""
        import random
        import string
        
        words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her",
            "she", "or", "an", "will", "my", "one", "all", "would", "there",
            "their", "what", "so", "up", "out", "if", "about", "who", "get",
            "which", "go", "me", "when", "make", "can", "like", "time", "no",
            "just", "him", "know", "take", "people", "into", "year", "your",
            "good", "some", "could", "them", "see", "other", "than", "then",
            "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first",
            "well", "way", "even", "new", "want", "because", "any", "these",
            "give", "day", "most", "us"
        ]
        
        content = []
        current_size = 0
        
        while current_size < size:
            word = random.choice(words)
            content.append(word)
            current_size += len(word) + 1  # +1 for space
        
        return " ".join(content)
    
    def generate_repetitive_content(self, pattern: str, repetitions: int) -> str:
        """Generate repetitive content."""
        return pattern * repetitions
    
    def generate_structured_content(self, content_type: str) -> str:
        """Generate structured content (JSON, XML, etc.)."""
        if content_type == "json":
            return self._generate_json_content()
        elif content_type == "xml":
            return self._generate_xml_content()
        elif content_type == "csv":
            return self._generate_csv_content()
        else:
            return self.generate_text_content()
    
    def _generate_json_content(self) -> str:
        """Generate JSON content."""
        import json
        import random
        
        data = {
            "id": random.randint(1, 1000),
            "name": f"test_item_{random.randint(1, 100)}",
            "values": [random.randint(1, 100) for _ in range(10)],
            "metadata": {
                "created": "2024-01-01T00:00:00Z",
                "updated": "2024-01-01T00:00:00Z",
                "tags": ["test", "compression", "data"]
            }
        }
        return json.dumps(data, indent=2)
    
    def _generate_xml_content(self) -> str:
        """Generate XML content."""
        import random
        
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item id="{random.randint(1, 100)}">
        <name>test_item_{random.randint(1, 100)}</name>
        <value>{random.randint(1, 1000)}</value>
        <description>This is a test item for compression testing</description>
    </item>
    <item id="{random.randint(1, 100)}">
        <name>test_item_{random.randint(1, 100)}</name>
        <value>{random.randint(1, 1000)}</value>
        <description>Another test item for compression testing</description>
    </item>
</root>"""
        return xml
    
    def _generate_csv_content(self) -> str:
        """Generate CSV content."""
        import random
        
        csv = "id,name,value,description\n"
        for i in range(10):
            csv += f"{i+1},test_item_{i+1},{random.randint(1, 1000)},Test item {i+1}\n"
        return csv


class PerformanceMetrics:
    """Collect and analyze performance metrics during testing."""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, test_name: str):
        """Start timing a test."""
        import time
        self.start_times[test_name] = time.time()
    
    def end_timer(self, test_name: str):
        """End timing a test and record metrics."""
        import time
        if test_name in self.start_times:
            duration = time.time() - self.start_times[test_name]
            if test_name not in self.metrics:
                self.metrics[test_name] = []
            self.metrics[test_name].append(duration)
            del self.start_times[test_name]
    
    def record_metric(self, test_name: str, metric_name: str, value: float):
        """Record a custom metric."""
        if test_name not in self.metrics:
            self.metrics[test_name] = {}
        self.metrics[test_name][metric_name] = value
    
    def get_average_time(self, test_name: str) -> float:
        """Get average execution time for a test."""
        if test_name in self.metrics and isinstance(self.metrics[test_name], list):
            return sum(self.metrics[test_name]) / len(self.metrics[test_name])
        return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {}
        for test_name, metrics in self.metrics.items():
            if isinstance(metrics, list):
                summary[test_name] = {
                    "count": len(metrics),
                    "average_time": sum(metrics) / len(metrics),
                    "min_time": min(metrics),
                    "max_time": max(metrics)
                }
            else:
                summary[test_name] = metrics
        return summary


# Global test configuration instance
test_config = TestConfig()
test_data_generator = TestDataGenerator()
performance_metrics = PerformanceMetrics()


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment for the entire test session."""
    test_config.setup_test_environment()
    test_config.create_test_directories()
    yield test_config
    test_config.cleanup_test_files()


@pytest.fixture
def mock_db():
    """Provide a mock database for testing."""
    return MockDatabase()


@pytest.fixture
def compression_engine():
    """Provide a compression engine instance for testing."""
    return CompressionEngine()


@pytest.fixture
def content_analyzer():
    """Provide a content analyzer instance for testing."""
    return ContentAnalyzer()


@pytest.fixture
def algorithm_selector():
    """Provide an algorithm selector instance for testing."""
    return AlgorithmSelector()


@pytest.fixture
def parameter_optimizer():
    """Provide a parameter optimizer instance for testing."""
    return ParameterOptimizer()


@pytest.fixture
def metrics_collector():
    """Provide a metrics collector instance for testing."""
    return MetricsCollector()
