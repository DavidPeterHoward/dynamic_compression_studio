"""
Comprehensive Test Suite: Meta-Learning Service

Tests the meta-learning service with:
- Database operations (CRUD)
- Schema validation
- Pattern detection
- Insight generation
- Historical analysis
- Prediction accuracy
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.services.enhanced_meta_learning_service import EnhancedMetaLearningService
from app.models.viability_models import (
    ContentFingerprint,
    MultiDimensionalMetrics,
    ValidationResult,
    MetaLearningContext,
    EnhancedViabilityTest,
    MetaLearningInsight,
    ContentDimension,
    PerformanceDimension,
    QualityDimension
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def meta_service(temp_db):
    """Create a meta-learning service with temporary database."""
    service = EnhancedMetaLearningService(db_path=temp_db)
    yield service
    service.close()


@pytest.fixture
def sample_test_result() -> EnhancedViabilityTest:
    """Create a sample test result."""
    return EnhancedViabilityTest(
        test_id="test_sample_001",
        content_fingerprint=ContentFingerprint(
            sha256="a" * 64,
            size_bytes=1000,
            content_type="text/plain",
            entropy=0.7,
            redundancy=0.3
        ),
        algorithm="gzip",
        metrics=MultiDimensionalMetrics(
            content_metrics={
                ContentDimension.ENTROPY: 0.7,
                ContentDimension.REDUNDANCY: 0.3,
                ContentDimension.COMPRESSIBILITY: 0.75
            },
            performance_metrics={
                PerformanceDimension.COMPRESSION_RATIO: 3.5,
                PerformanceDimension.COMPRESSION_SPEED: 0.95,
                PerformanceDimension.MEMORY_EFFICIENCY: 0.88
            },
            quality_metrics={
                QualityDimension.DATA_INTEGRITY: 1.0,
                QualityDimension.COMPRESSION_QUALITY: 0.95
            },
            overall_score=0.85,
            confidence_score=0.92
        ),
        validation=ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["integrity", "completeness", "consistency", "accuracy"],
            checks_passed=4,
            checks_failed=0,
            validation_hash=""
        ),
        meta_context=MetaLearningContext(
            test_run_id="run_001",
            test_environment={"os": "linux", "python": "3.9"},
            previous_tests_count=50
        ),
        success=True,
        execution_time_ms=50.0,
        compression_ratio=3.5,
        compression_percentage=71.4,
        original_size=1000,
        compressed_size=286,
        tags=["text", "production"]
    )


class TestDatabaseOperations:
    """Test basic database operations."""
    
    def test_store_single_test_result(self, meta_service, sample_test_result):
        """Test storing a single test result."""
        result = meta_service.store_test_result(sample_test_result)
        
        assert result is True
    
    def test_retrieve_test_result(self, meta_service, sample_test_result):
        """Test retrieving a stored test result."""
        meta_service.store_test_result(sample_test_result)
        
        retrieved = meta_service.get_test_result(sample_test_result.test_id)
        
        assert retrieved is not None
        assert retrieved.test_id == sample_test_result.test_id
        assert retrieved.algorithm == sample_test_result.algorithm
        assert retrieved.compression_ratio == sample_test_result.compression_ratio
    
    def test_store_multiple_test_results(self, meta_service):
        """Test storing multiple test results."""
        results = []
        for i in range(10):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000 + i * 100,
                    content_type="text/plain",
                    entropy=0.7 + i * 0.01,
                    redundancy=0.3 - i * 0.01
                ),
                algorithm="gzip",
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={},
                    quality_metrics={},
                    overall_score=0.8 + i * 0.01,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0 + i * 5,
                compression_ratio=3.0 + i * 0.1,
                compression_percentage=70.0,
                original_size=1000,
                compressed_size=300
            )
            meta_service.store_test_result(test)
            results.append(test)
        
        # Verify all stored
        for test in results:
            retrieved = meta_service.get_test_result(test.test_id)
            assert retrieved is not None
            assert retrieved.test_id == test.test_id
    
    def test_query_by_algorithm(self, meta_service):
        """Test querying results by algorithm."""
        # Store results for different algorithms
        algorithms = ["gzip", "lzma", "zstd", "gzip", "lzma"]
        for i, algo in enumerate(algorithms):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type="text/plain",
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm=algo,
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={},
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=3.5,
                compression_percentage=71.4,
                original_size=1000,
                compressed_size=286
            )
            meta_service.store_test_result(test)
        
        # Query GZIP results
        gzip_results = meta_service.query_by_algorithm("gzip")
        assert len(gzip_results) == 2
        
        # Query LZMA results
        lzma_results = meta_service.query_by_algorithm("lzma")
        assert len(lzma_results) == 2
        
        # Query ZSTD results
        zstd_results = meta_service.query_by_algorithm("zstd")
        assert len(zstd_results) == 1
    
    def test_query_by_content_type(self, meta_service):
        """Test querying results by content type."""
        content_types = ["text/plain", "application/json", "text/plain", "text/xml"]
        for i, ct in enumerate(content_types):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type=ct,
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm="gzip",
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={},
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=3.5,
                compression_percentage=71.4,
                original_size=1000,
                compressed_size=286
            )
            meta_service.store_test_result(test)
        
        # Query text/plain results
        text_results = meta_service.query_by_content_type("text/plain")
        assert len(text_results) == 2
        
        # Query JSON results
        json_results = meta_service.query_by_content_type("application/json")
        assert len(json_results) == 1
    
    def test_query_by_date_range(self, meta_service):
        """Test querying results by date range."""
        # Store results with different timestamps
        for i in range(5):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type="text/plain",
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm="gzip",
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={},
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=3.5,
                compression_percentage=71.4,
                original_size=1000,
                compressed_size=286
            )
            meta_service.store_test_result(test)
        
        # Query recent results
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_results = meta_service.query_by_date_range(one_hour_ago, now)
        assert len(recent_results) == 5


class TestStatisticalAnalysis:
    """Test statistical analysis capabilities."""
    
    def test_calculate_average_compression_ratio(self, meta_service):
        """Test calculating average compression ratio."""
        ratios = [3.0, 3.5, 4.0, 3.2, 3.8]
        for i, ratio in enumerate(ratios):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type="text/plain",
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm="gzip",
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={
                        PerformanceDimension.COMPRESSION_RATIO: ratio
                    },
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=ratio,
                compression_percentage=70.0,
                original_size=1000,
                compressed_size=int(1000 / ratio)
            )
            meta_service.store_test_result(test)
        
        stats = meta_service.get_algorithm_statistics("gzip")
        
        assert stats is not None
        assert "average_ratio" in stats
        expected_avg = sum(ratios) / len(ratios)
        assert abs(stats["average_ratio"] - expected_avg) < 0.1
    
    def test_identify_best_algorithm_for_content_type(self, meta_service):
        """Test identifying best algorithm for content type."""
        # Store results for different algorithms on JSON content
        test_data = [
            ("gzip", 3.0),
            ("gzip", 3.2),
            ("lzma", 4.5),
            ("lzma", 4.8),
            ("zstd", 3.8),
            ("zstd", 4.0)
        ]
        
        for i, (algo, ratio) in enumerate(test_data):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type="application/json",
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm=algo,
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={
                        PerformanceDimension.COMPRESSION_RATIO: ratio
                    },
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=ratio,
                compression_percentage=70.0,
                original_size=1000,
                compressed_size=int(1000 / ratio)
            )
            meta_service.store_test_result(test)
        
        best_algo = meta_service.get_best_algorithm_for_content_type("application/json")
        
        assert best_algo is not None
        assert best_algo["algorithm"] == "lzma"  # LZMA has highest average ratio
    
    def test_detect_performance_trends(self, meta_service):
        """Test detecting performance trends over time."""
        # Store results with improving performance
        for i in range(10):
            ratio = 3.0 + i * 0.1  # Improving ratio
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type="text/plain",
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm="gzip",
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={
                        PerformanceDimension.COMPRESSION_RATIO: ratio
                    },
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=ratio,
                compression_percentage=70.0,
                original_size=1000,
                compressed_size=int(1000 / ratio)
            )
            meta_service.store_test_result(test)
        
        trend = meta_service.detect_trend("gzip", "compression_ratio")
        
        assert trend is not None
        assert trend["direction"] == "improving"


class TestInsightGeneration:
    """Test insight generation from historical data."""
    
    def test_generate_insight_from_pattern(self, meta_service):
        """Test generating insights from detected patterns."""
        # Store results showing clear pattern
        for i in range(20):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type="application/json",
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm="zstd",
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={
                        PerformanceDimension.COMPRESSION_RATIO: 4.0 + (i % 3) * 0.1
                    },
                    quality_metrics={},
                    overall_score=0.9,
                    confidence_score=0.95
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext("test_run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=4.0,
                compression_percentage=75.0,
                original_size=1000,
                compressed_size=250
            )
            meta_service.store_test_result(test)
        
        insights = meta_service.generate_insights()
        
        assert insights is not None
        assert len(insights) > 0
    
    def test_store_and_retrieve_insight(self, meta_service):
        """Test storing and retrieving insights."""
        insight = MetaLearningInsight(
            insight_id="insight_001",
            insight_type="best_algorithm_for_content",
            insight_description="ZSTD performs best on JSON content",
            evidence_test_ids=[f"test_{i:03d}" for i in range(10)],
            evidence_strength=0.95,
            sample_size=10,
            statistical_confidence=0.95,
            p_value=0.01,
            actionable=True,
            recommended_action="Use ZSTD for JSON compression",
            expected_improvement=0.30,
            insight_hash="",
            novelty=0.80,
            importance=0.90,
            generalizability=0.85
        )
        
        meta_service.store_insight(insight)
        
        retrieved = meta_service.get_insight(insight.insight_id)
        assert retrieved is not None
        assert retrieved.insight_id == insight.insight_id
        assert retrieved.insight_type == insight.insight_type


class TestPrediction:
    """Test prediction capabilities."""
    
    def test_predict_compression_ratio(self, meta_service):
        """Test predicting compression ratio for new content."""
        # Train with historical data
        for i in range(50):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000 + i * 10,
                    content_type="text/plain",
                    entropy=0.7 + i * 0.001,
                    redundancy=0.3 - i * 0.001
                ),
                algorithm="gzip",
                metrics=MultiDimensionalMetrics(
                    content_metrics={
                        ContentDimension.ENTROPY: 0.7 + i * 0.001,
                        ContentDimension.REDUNDANCY: 0.3 - i * 0.001
                    },
                    performance_metrics={
                        PerformanceDimension.COMPRESSION_RATIO: 3.0 + i * 0.01
                    },
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=3.0 + i * 0.01,
                compression_percentage=70.0,
                original_size=1000,
                compressed_size=333
            )
            meta_service.store_test_result(test)
        
        # Predict for new content
        new_fingerprint = ContentFingerprint(
            sha256="new" * 21 + "a",
            size_bytes=1250,
            content_type="text/plain",
            entropy=0.75,
            redundancy=0.25
        )
        
        prediction = meta_service.predict_compression_ratio("gzip", new_fingerprint)
        
        assert prediction is not None
        assert "predicted_ratio" in prediction
        assert "confidence" in prediction
        assert 2.0 <= prediction["predicted_ratio"] <= 5.0
    
    def test_recommend_algorithm(self, meta_service):
        """Test recommending best algorithm for content."""
        # Store diverse test results
        test_data = [
            ("gzip", "text/plain", 3.2),
            ("lzma", "text/plain", 4.5),
            ("zstd", "text/plain", 3.8),
            ("gzip", "application/json", 3.5),
            ("lzma", "application/json", 5.0),
            ("zstd", "application/json", 4.2),
        ]
        
        for i, (algo, ct, ratio) in enumerate(test_data):
            test = EnhancedViabilityTest(
                test_id=f"test_{i:03d}",
                content_fingerprint=ContentFingerprint(
                    sha256=f"{i}" * 64,
                    size_bytes=1000,
                    content_type=ct,
                    entropy=0.7,
                    redundancy=0.3
                ),
                algorithm=algo,
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={
                        PerformanceDimension.COMPRESSION_RATIO: ratio
                    },
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=ratio,
                compression_percentage=70.0,
                original_size=1000,
                compressed_size=int(1000 / ratio)
            )
            meta_service.store_test_result(test)
        
        # Get recommendation
        new_fingerprint = ContentFingerprint(
            sha256="new" * 21 + "a",
            size_bytes=1000,
            content_type="application/json",
            entropy=0.7,
            redundancy=0.3
        )
        
        recommendation = meta_service.recommend_algorithm(new_fingerprint)
        
        assert recommendation is not None
        assert "recommended_algorithm" in recommendation
        assert recommendation["recommended_algorithm"] == "lzma"  # Best for JSON


class TestDataIntegrity:
    """Test data integrity and validation."""
    
    def test_duplicate_test_id_handling(self, meta_service, sample_test_result):
        """Test handling of duplicate test IDs."""
        meta_service.store_test_result(sample_test_result)
        
        # Try to store duplicate
        duplicate = sample_test_result.copy()
        result = meta_service.store_test_result(duplicate)
        
        # Should handle gracefully (update or skip)
        assert result is not None
    
    def test_invalid_test_data_handling(self, meta_service):
        """Test handling of invalid test data."""
        # This should be caught by Pydantic validation
        with pytest.raises(Exception):
            invalid_test = EnhancedViabilityTest(
                test_id="",  # Empty test ID - invalid
                content_fingerprint=ContentFingerprint(
                    sha256="invalid",  # Invalid SHA256
                    size_bytes=-1,  # Negative size - invalid
                    content_type="text/plain",
                    entropy=2.0,  # Out of range - invalid
                    redundancy=0.3
                ),
                algorithm="gzip",
                metrics=MultiDimensionalMetrics(
                    content_metrics={},
                    performance_metrics={},
                    quality_metrics={},
                    overall_score=0.8,
                    confidence_score=0.9
                ),
                validation=ValidationResult(
                    is_valid=True,
                    integrity_check=True,
                    completeness_check=True,
                    consistency_check=True,
                    accuracy_check=True,
                    checks_performed=[],
                    validation_hash=""
                ),
                meta_context=MetaLearningContext(test_run_id="run_001"),
                success=True,
                execution_time_ms=50.0,
                compression_ratio=3.5,
                compression_percentage=71.4,
                original_size=1000,
                compressed_size=286
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

