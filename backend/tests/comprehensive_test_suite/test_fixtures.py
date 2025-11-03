"""
Comprehensive Test Fixtures and Data Factories

Provides reusable fixtures and factory functions for:
- Test data generation
- Mock objects
- Database setup
- Service initialization
- Common test scenarios
"""

import pytest
import tempfile
import os
import hashlib
import random
import string
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

from app.models.viability_models import (
    ContentFingerprint,
    MultiDimensionalMetrics,
    ValidationResult,
    MetaLearningContext,
    EnhancedViabilityTest,
    MetaLearningInsight,
    ComparativeAnalysis,
    ProofOfPerformance,
    ContentDimension,
    PerformanceDimension,
    QualityDimension
)
from app.services.enhanced_meta_learning_service import EnhancedMetaLearningService


# ==================== Database Fixtures ====================

@pytest.fixture(scope="function")
def temp_db_file():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture(scope="function")
def meta_learning_service(temp_db_file):
    """Create a meta-learning service with temporary database."""
    service = EnhancedMetaLearningService(db_path=temp_db_file)
    yield service
    service.close()


@pytest.fixture(scope="session")
def persistent_db():
    """Create a persistent database for session-wide tests."""
    fd, path = tempfile.mkstemp(suffix='_persistent.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


# ==================== Data Generation Factories ====================

class ContentFactory:
    """Factory for generating test content."""
    
    @staticmethod
    def create_text_content(size: int = 1000, pattern: str = "mixed") -> bytes:
        """Generate text content with various patterns."""
        if pattern == "repetitive":
            return (b"ABCD" * (size // 4))[:size]
        elif pattern == "random":
            return ''.join(random.choices(string.printable, k=size)).encode('utf-8')
        elif pattern == "mixed":
            text = "The quick brown fox jumps over the lazy dog. " * (size // 45)
            return text[:size].encode('utf-8')
        else:
            return b"X" * size
    
    @staticmethod
    def create_json_content(size: int = 1000) -> bytes:
        """Generate JSON-like content."""
        pattern = '{"key":"value","number":12345,"array":[1,2,3]}'
        result = pattern * (size // len(pattern) + 1)
        return result[:size].encode('utf-8')
    
    @staticmethod
    def create_xml_content(size: int = 1000) -> bytes:
        """Generate XML-like content."""
        pattern = '<root><item id="1">Data</item></root>'
        result = pattern * (size // len(pattern) + 1)
        return result[:size].encode('utf-8')
    
    @staticmethod
    def create_binary_content(size: int = 1000) -> bytes:
        """Generate binary content."""
        return bytes([random.randint(0, 255) for _ in range(size)])
    
    @staticmethod
    def create_compressed_content(size: int = 1000) -> bytes:
        """Generate already-compressed content (low redundancy)."""
        return os.urandom(size)


class FingerprintFactory:
    """Factory for generating ContentFingerprint objects."""
    
    @staticmethod
    def create(content: bytes = None, content_type: str = "text/plain", **kwargs) -> ContentFingerprint:
        """Create a ContentFingerprint."""
        if content is None:
            content = ContentFactory.create_text_content()
        
        sha256 = hashlib.sha256(content).hexdigest()
        size = len(content)
        
        # Calculate basic characteristics
        entropy = kwargs.get('entropy', 0.7)
        redundancy = kwargs.get('redundancy', 0.3)
        
        return ContentFingerprint(
            sha256=sha256,
            size_bytes=size,
            content_type=content_type,
            entropy=entropy,
            redundancy=redundancy
        )
    
    @staticmethod
    def create_batch(count: int = 10, content_type: str = "text/plain") -> List[ContentFingerprint]:
        """Create a batch of fingerprints."""
        return [
            FingerprintFactory.create(
                content=ContentFactory.create_text_content(1000 + i * 100),
                content_type=content_type,
                entropy=0.5 + i * 0.05,
                redundancy=0.5 - i * 0.05
            )
            for i in range(count)
        ]


class MetricsFactory:
    """Factory for generating MultiDimensionalMetrics objects."""
    
    @staticmethod
    def create(
        overall_score: float = 0.85,
        confidence_score: float = 0.90,
        **dimension_scores
    ) -> MultiDimensionalMetrics:
        """Create MultiDimensionalMetrics."""
        content_metrics = dimension_scores.get('content_metrics', {
            ContentDimension.ENTROPY: 0.7,
            ContentDimension.REDUNDANCY: 0.3,
            ContentDimension.COMPRESSIBILITY: 0.75
        })
        
        performance_metrics = dimension_scores.get('performance_metrics', {
            PerformanceDimension.COMPRESSION_RATIO: 3.5,
            PerformanceDimension.COMPRESSION_SPEED: 0.95,
            PerformanceDimension.MEMORY_EFFICIENCY: 0.88
        })
        
        quality_metrics = dimension_scores.get('quality_metrics', {
            QualityDimension.DATA_INTEGRITY: 1.0,
            QualityDimension.COMPRESSION_QUALITY: 0.95
        })
        
        return MultiDimensionalMetrics(
            content_metrics=content_metrics,
            performance_metrics=performance_metrics,
            quality_metrics=quality_metrics,
            overall_score=overall_score,
            confidence_score=confidence_score
        )
    
    @staticmethod
    def create_high_performance() -> MultiDimensionalMetrics:
        """Create metrics for high-performance compression."""
        return MetricsFactory.create(
            overall_score=0.95,
            confidence_score=0.98,
            performance_metrics={
                PerformanceDimension.COMPRESSION_RATIO: 4.5,
                PerformanceDimension.COMPRESSION_SPEED: 0.98,
                PerformanceDimension.DECOMPRESSION_SPEED: 0.99,
                PerformanceDimension.MEMORY_EFFICIENCY: 0.95,
                PerformanceDimension.CPU_EFFICIENCY: 0.96
            }
        )
    
    @staticmethod
    def create_low_performance() -> MultiDimensionalMetrics:
        """Create metrics for low-performance compression."""
        return MetricsFactory.create(
            overall_score=0.40,
            confidence_score=0.70,
            performance_metrics={
                PerformanceDimension.COMPRESSION_RATIO: 1.2,
                PerformanceDimension.COMPRESSION_SPEED: 0.30,
                PerformanceDimension.MEMORY_EFFICIENCY: 0.50
            }
        )


class ValidationFactory:
    """Factory for generating ValidationResult objects."""
    
    @staticmethod
    def create_valid() -> ValidationResult:
        """Create a valid validation result."""
        return ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["integrity", "completeness", "consistency", "accuracy"],
            checks_passed=4,
            checks_failed=0,
            validation_hash=""
        )
    
    @staticmethod
    def create_invalid(errors: List[str] = None) -> ValidationResult:
        """Create an invalid validation result."""
        if errors is None:
            errors = ["Data integrity check failed", "Accuracy check failed"]
        
        return ValidationResult(
            is_valid=False,
            integrity_check=False,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=False,
            checks_performed=["integrity", "completeness", "consistency", "accuracy"],
            checks_passed=2,
            checks_failed=2,
            errors=errors,
            validation_hash=""
        )
    
    @staticmethod
    def create_with_warnings() -> ValidationResult:
        """Create a valid result with warnings."""
        return ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["all"],
            checks_passed=4,
            checks_failed=0,
            warnings=["Performance slightly below expected", "Memory usage higher than optimal"],
            validation_hash=""
        )


class MetaContextFactory:
    """Factory for generating MetaLearningContext objects."""
    
    @staticmethod
    def create(test_run_id: str = None, **kwargs) -> MetaLearningContext:
        """Create a MetaLearningContext."""
        if test_run_id is None:
            test_run_id = f"run_{random.randint(1000, 9999)}"
        
        return MetaLearningContext(
            test_run_id=test_run_id,
            test_environment=kwargs.get('test_environment', {
                "os": "linux",
                "python": "3.9",
                "cpu": "x86_64"
            }),
            previous_tests_count=kwargs.get('previous_tests_count', 0),
            historical_average=kwargs.get('historical_average', None),
            trend_direction=kwargs.get('trend_direction', None),
            predicted_outcome=kwargs.get('predicted_outcome', None),
            prediction_accuracy=kwargs.get('prediction_accuracy', None),
            learning_signals=kwargs.get('learning_signals', []),
            anomaly_score=kwargs.get('anomaly_score', None),
            novelty_score=kwargs.get('novelty_score', None),
            learning_value=kwargs.get('learning_value', None)
        )
    
    @staticmethod
    def create_with_prediction() -> MetaLearningContext:
        """Create context with prediction data."""
        return MetaContextFactory.create(
            predicted_outcome={"compression_ratio": 3.5, "time_ms": 50.0},
            prediction_accuracy=0.90,
            prediction_model_version="v1.0.0"
        )
    
    @staticmethod
    def create_with_learning_signals() -> MetaLearningContext:
        """Create context with learning signals."""
        return MetaContextFactory.create(
            learning_signals=["anomaly_detected", "new_pattern", "performance_improvement"],
            anomaly_score=0.85,
            novelty_score=0.70,
            learning_value=0.90
        )


class ViabilityTestFactory:
    """Factory for generating EnhancedViabilityTest objects."""
    
    @staticmethod
    def create(
        test_id: str = None,
        algorithm: str = "gzip",
        success: bool = True,
        **kwargs
    ) -> EnhancedViabilityTest:
        """Create an EnhancedViabilityTest."""
        if test_id is None:
            test_id = f"test_{random.randint(10000, 99999)}"
        
        fingerprint = kwargs.get('fingerprint', FingerprintFactory.create())
        metrics = kwargs.get('metrics', MetricsFactory.create())
        validation = kwargs.get('validation', ValidationFactory.create_valid())
        context = kwargs.get('context', MetaContextFactory.create())
        
        compression_ratio = kwargs.get('compression_ratio', 3.5)
        original_size = kwargs.get('original_size', 1000)
        compressed_size = int(original_size / compression_ratio)
        compression_percentage = ((original_size - compressed_size) / original_size * 100)
        
        return EnhancedViabilityTest(
            test_id=test_id,
            content_fingerprint=fingerprint,
            algorithm=algorithm,
            metrics=metrics,
            validation=validation,
            meta_context=context,
            success=success,
            execution_time_ms=kwargs.get('execution_time_ms', 50.0),
            compression_ratio=compression_ratio,
            compression_percentage=compression_percentage,
            original_size=original_size,
            compressed_size=compressed_size,
            tags=kwargs.get('tags', []),
            annotations=kwargs.get('annotations', {})
        )
    
    @staticmethod
    def create_batch(
        count: int = 10,
        algorithm: str = "gzip",
        varied: bool = True
    ) -> List[EnhancedViabilityTest]:
        """Create a batch of viability tests."""
        tests = []
        for i in range(count):
            if varied:
                # Vary the parameters
                algo = random.choice(["gzip", "lzma", "zstd", "bzip2"]) if algorithm == "varied" else algorithm
                ratio = 2.5 + i * 0.2
                time_ms = 30.0 + i * 5.0
            else:
                algo = algorithm
                ratio = 3.5
                time_ms = 50.0
            
            test = ViabilityTestFactory.create(
                test_id=f"test_{i:05d}",
                algorithm=algo,
                compression_ratio=ratio,
                execution_time_ms=time_ms,
                original_size=1000 + i * 100
            )
            tests.append(test)
        
        return tests
    
    @staticmethod
    def create_for_algorithm_comparison() -> Dict[str, List[EnhancedViabilityTest]]:
        """Create tests for comparing algorithms."""
        algorithms = ["gzip", "lzma", "zstd", "bzip2"]
        results = {}
        
        for algo in algorithms:
            tests = []
            for i in range(5):
                # Give different characteristics to each algorithm
                if algo == "lzma":
                    ratio = 4.5 + i * 0.1  # Best ratio
                    time_ms = 120.0 + i * 10.0  # Slowest
                elif algo == "gzip":
                    ratio = 3.0 + i * 0.1  # Moderate ratio
                    time_ms = 50.0 + i * 5.0  # Fast
                elif algo == "zstd":
                    ratio = 3.8 + i * 0.1  # Good ratio
                    time_ms = 60.0 + i * 5.0  # Moderate speed
                else:  # bzip2
                    ratio = 3.5 + i * 0.1  # Good ratio
                    time_ms = 90.0 + i * 10.0  # Slow
                
                test = ViabilityTestFactory.create(
                    test_id=f"{algo}_test_{i:03d}",
                    algorithm=algo,
                    compression_ratio=ratio,
                    execution_time_ms=time_ms
                )
                tests.append(test)
            
            results[algo] = tests
        
        return results


class InsightFactory:
    """Factory for generating MetaLearningInsight objects."""
    
    @staticmethod
    def create(
        insight_type: str = "best_algorithm_for_content",
        sample_size: int = 100,
        **kwargs
    ) -> MetaLearningInsight:
        """Create a MetaLearningInsight."""
        insight_id = kwargs.get('insight_id', f"insight_{random.randint(1000, 9999)}")
        
        return MetaLearningInsight(
            insight_id=insight_id,
            insight_type=insight_type,
            insight_description=kwargs.get('insight_description', "Generated insight"),
            evidence_test_ids=kwargs.get('evidence_test_ids', [f"test_{i}" for i in range(sample_size)]),
            evidence_strength=kwargs.get('evidence_strength', 0.90),
            sample_size=sample_size,
            statistical_confidence=kwargs.get('statistical_confidence', 0.95),
            p_value=kwargs.get('p_value', 0.01),
            actionable=kwargs.get('actionable', True),
            recommended_action=kwargs.get('recommended_action', "Apply recommendation"),
            expected_improvement=kwargs.get('expected_improvement', 0.25),
            insight_hash="",
            novelty=kwargs.get('novelty', 0.70),
            importance=kwargs.get('importance', 0.85),
            generalizability=kwargs.get('generalizability', 0.80)
        )
    
    @staticmethod
    def create_high_confidence() -> MetaLearningInsight:
        """Create high-confidence insight."""
        return InsightFactory.create(
            insight_type="performance_pattern",
            sample_size=500,
            evidence_strength=0.98,
            statistical_confidence=0.99,
            p_value=0.001,
            novelty=0.90,
            importance=0.95,
            generalizability=0.92
        )
    
    @staticmethod
    def create_low_confidence() -> MetaLearningInsight:
        """Create low-confidence insight."""
        return InsightFactory.create(
            insight_type="tentative_pattern",
            sample_size=5,
            evidence_strength=0.60,
            statistical_confidence=0.70,
            p_value=0.15,
            actionable=False,
            novelty=0.95,
            importance=0.50,
            generalizability=0.40
        )


# ==================== Fixture Combinations ====================

@pytest.fixture
def sample_content():
    """Provide sample content for testing."""
    return ContentFactory.create_text_content(size=1000)


@pytest.fixture
def sample_fingerprint(sample_content):
    """Provide sample content fingerprint."""
    return FingerprintFactory.create(content=sample_content)


@pytest.fixture
def sample_metrics():
    """Provide sample metrics."""
    return MetricsFactory.create()


@pytest.fixture
def sample_validation():
    """Provide sample validation result."""
    return ValidationFactory.create_valid()


@pytest.fixture
def sample_context():
    """Provide sample meta-learning context."""
    return MetaContextFactory.create()


@pytest.fixture
def sample_test(sample_fingerprint, sample_metrics, sample_validation, sample_context):
    """Provide complete sample test."""
    return ViabilityTestFactory.create(
        fingerprint=sample_fingerprint,
        metrics=sample_metrics,
        validation=sample_validation,
        context=sample_context
    )


@pytest.fixture
def batch_tests():
    """Provide batch of test results."""
    return ViabilityTestFactory.create_batch(count=20, varied=True)


@pytest.fixture
def algorithm_comparison_tests():
    """Provide tests for algorithm comparison."""
    return ViabilityTestFactory.create_for_algorithm_comparison()


@pytest.fixture
def populated_meta_service(meta_learning_service, batch_tests):
    """Provide meta-learning service with test data."""
    for test in batch_tests:
        meta_learning_service.store_test_result(test)
    return meta_learning_service


# ==================== Parametrize Helpers ====================

def get_all_algorithms():
    """Get list of all supported algorithms."""
    return ["gzip", "lzma", "zstd", "bzip2", "lz4", "brotli"]


def get_all_content_types():
    """Get list of all content types."""
    return [
        "text/plain",
        "application/json",
        "application/xml",
        "text/html",
        "text/csv",
        "application/octet-stream"
    ]


def get_test_sizes():
    """Get list of test data sizes."""
    return [
        100,  # Very small
        1000,  # Small
        10000,  # Medium
        100000,  # Large
        1000000,  # Very large
    ]


def get_compression_levels():
    """Get compression levels for testing."""
    return {
        "gzip": [1, 5, 9],
        "lzma": [0, 5, 9],
        "bzip2": [1, 5, 9],
        "zstd": [1, 10, 19],
        "brotli": [1, 6, 11]
    }


# ==================== Mock Objects ====================

class MockCompressor:
    """Mock compressor for testing."""
    
    def __init__(self, algorithm: str, ratio: float = 3.0):
        self.algorithm = algorithm
        self.ratio = ratio
        self.compress_count = 0
        self.decompress_count = 0
    
    def compress(self, data: bytes) -> bytes:
        """Mock compression."""
        self.compress_count += 1
        compressed_size = int(len(data) / self.ratio)
        return b"COMPRESSED" + data[:compressed_size]
    
    def decompress(self, data: bytes) -> bytes:
        """Mock decompression."""
        self.decompress_count += 1
        return b"DECOMPRESSED" + data[10:]  # Remove "COMPRESSED" prefix


@pytest.fixture
def mock_compressor():
    """Provide mock compressor."""
    return MockCompressor("mock_algorithm", ratio=3.5)


# ==================== Utility Functions ====================

def assert_valid_test_result(test: EnhancedViabilityTest):
    """Assert that a test result is valid."""
    assert test.test_id is not None
    assert len(test.test_id) > 0
    assert test.algorithm in get_all_algorithms() or test.algorithm.startswith("mock")
    assert test.compression_ratio > 0
    assert test.original_size > 0
    assert test.compressed_size > 0
    assert test.execution_time_ms >= 0
    assert test.validation.is_valid or not test.success


def assert_valid_fingerprint(fingerprint: ContentFingerprint):
    """Assert that a fingerprint is valid."""
    assert len(fingerprint.sha256) == 64
    assert fingerprint.size_bytes >= 0
    assert 0 <= fingerprint.entropy <= 1
    assert 0 <= fingerprint.redundancy <= 1


def assert_valid_metrics(metrics: MultiDimensionalMetrics):
    """Assert that metrics are valid."""
    assert 0 <= metrics.overall_score <= 1
    assert 0 <= metrics.confidence_score <= 1
    for score in metrics.content_metrics.values():
        assert 0 <= score <= 1
    for score in metrics.performance_metrics.values():
        assert score >= 0  # Can be > 1 for ratios
    for score in metrics.quality_metrics.values():
        assert 0 <= score <= 1


if __name__ == "__main__":
    print("Test fixtures and factories loaded successfully.")
    print(f"Available algorithms: {get_all_algorithms()}")
    print(f"Available content types: {get_all_content_types()}")
    print(f"Test sizes: {get_test_sizes()}")

