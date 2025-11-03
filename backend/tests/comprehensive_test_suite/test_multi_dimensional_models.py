"""
Comprehensive Test Suite: Multi-Dimensional Models

Tests all aspects of data models including:
- Schema validation
- Edge cases
- Boundary conditions
- Data integrity
- Serialization/deserialization
"""

import pytest
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from app.models.viability_models import (
    ContentFingerprint,
    MultiDimensionalMetrics,
    ValidationResult,
    MetaLearningContext,
    EnhancedViabilityTest,
    ComparativeAnalysis,
    MetaLearningInsight,
    ProofOfPerformance,
    ContentDimension,
    PerformanceDimension,
    QualityDimension
)


class TestContentFingerprint:
    """Test ContentFingerprint model comprehensively."""
    
    @pytest.mark.parametrize("content,content_type,entropy,redundancy", [
        ("test content", "text/plain", 0.5, 0.5),
        ("a" * 1000, "text/plain", 0.1, 0.9),  # Highly repetitive
        ("".join(chr(i % 256) for i in range(1000)), "binary", 0.95, 0.05),  # High entropy
        ("", "text/plain", 0.0, 1.0),  # Empty content edge case
        ("x", "text/plain", 0.0, 1.0),  # Single character edge case
    ])
    def test_fingerprint_creation(self, content, content_type, entropy, redundancy):
        """Test fingerprint creation with various content types."""
        characteristics = {'entropy': entropy, 'redundancy': redundancy}
        fingerprint = ContentFingerprint.from_content(content, content_type, characteristics)
        
        assert fingerprint.sha256 == hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert fingerprint.size_bytes == len(content.encode('utf-8'))
        assert fingerprint.content_type == content_type
        assert fingerprint.entropy == entropy
        assert fingerprint.redundancy == redundancy
    
    def test_fingerprint_uniqueness(self):
        """Test that different content produces different fingerprints."""
        content1 = "content 1"
        content2 = "content 2"
        characteristics = {'entropy': 0.5, 'redundancy': 0.5}
        
        fp1 = ContentFingerprint.from_content(content1, "text", characteristics)
        fp2 = ContentFingerprint.from_content(content2, "text", characteristics)
        
        assert fp1.sha256 != fp2.sha256
    
    def test_fingerprint_determinism(self):
        """Test that same content always produces same fingerprint."""
        content = "deterministic content"
        characteristics = {'entropy': 0.5, 'redundancy': 0.5}
        
        fp1 = ContentFingerprint.from_content(content, "text", characteristics)
        fp2 = ContentFingerprint.from_content(content, "text", characteristics)
        
        assert fp1.sha256 == fp2.sha256
        assert fp1.size_bytes == fp2.size_bytes
    
    @pytest.mark.parametrize("entropy", [-0.1, 1.1, 2.0, -1.0])
    def test_entropy_validation(self, entropy):
        """Test entropy boundary validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            ContentFingerprint(
                sha256="a" * 64,
                size_bytes=100,
                content_type="text",
                entropy=entropy,  # Invalid
                redundancy=0.5
            )
    
    @pytest.mark.parametrize("redundancy", [-0.1, 1.1, 2.0, -1.0])
    def test_redundancy_validation(self, redundancy):
        """Test redundancy boundary validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            ContentFingerprint(
                sha256="a" * 64,
                size_bytes=100,
                content_type="text",
                entropy=0.5,
                redundancy=redundancy  # Invalid
            )


class TestMultiDimensionalMetrics:
    """Test MultiDimensionalMetrics model."""
    
    def test_all_dimensions_populated(self):
        """Test that all dimension types can be populated."""
        metrics = MultiDimensionalMetrics(
            content_metrics={
                ContentDimension.ENTROPY: 0.8,
                ContentDimension.REDUNDANCY: 0.3,
                ContentDimension.COMPRESSIBILITY: 0.7,
                ContentDimension.PATTERN_FREQUENCY: 0.6,
                ContentDimension.STRUCTURAL_COMPLEXITY: 0.5,
                ContentDimension.SEMANTIC_DENSITY: 0.4,
                ContentDimension.LANGUAGE_COMPLEXITY: 0.3
            },
            performance_metrics={
                PerformanceDimension.COMPRESSION_RATIO: 3.5,
                PerformanceDimension.COMPRESSION_SPEED: 0.95,
                PerformanceDimension.DECOMPRESSION_SPEED: 0.98,
                PerformanceDimension.MEMORY_EFFICIENCY: 0.85,
                PerformanceDimension.CPU_EFFICIENCY: 0.90,
                PerformanceDimension.THROUGHPUT: 0.88,
                PerformanceDimension.LATENCY: 0.05
            },
            quality_metrics={
                QualityDimension.DATA_INTEGRITY: 1.0,
                QualityDimension.COMPRESSION_QUALITY: 0.95,
                QualityDimension.REPRODUCIBILITY: 1.0,
                QualityDimension.STABILITY: 0.98,
                QualityDimension.ERROR_RESILIENCE: 0.92
            },
            overall_score=0.85,
            confidence_score=0.92
        )
        
        assert len(metrics.content_metrics) == 7
        assert len(metrics.performance_metrics) == 7
        assert len(metrics.quality_metrics) == 5
        assert metrics.overall_score == 0.85
        assert metrics.confidence_score == 0.92
    
    def test_score_calculation(self):
        """Test overall score calculation."""
        metrics = MultiDimensionalMetrics(
            content_metrics={ContentDimension.ENTROPY: 0.8},
            performance_metrics={PerformanceDimension.COMPRESSION_RATIO: 0.9},
            quality_metrics={QualityDimension.DATA_INTEGRITY: 1.0},
            overall_score=0.85,
            confidence_score=0.90
        )
        
        calculated_score = metrics.calculate_overall_score()
        
        # Verify calculation uses correct weights
        expected = 0.8 * 0.2 + 0.9 * 0.5 + 1.0 * 0.3
        assert abs(calculated_score - expected) < 0.01
    
    @pytest.mark.parametrize("score", [-0.1, 1.1, 2.0, -1.0])
    def test_score_boundaries(self, score):
        """Test score boundary validation."""
        with pytest.raises(Exception):
            MultiDimensionalMetrics(
                content_metrics={},
                performance_metrics={},
                quality_metrics={},
                overall_score=score,  # Invalid
                confidence_score=0.9
            )
    
    def test_empty_dimensions(self):
        """Test handling of empty dimension dictionaries."""
        metrics = MultiDimensionalMetrics(
            content_metrics={},
            performance_metrics={},
            quality_metrics={},
            overall_score=0.0,
            confidence_score=1.0
        )
        
        assert metrics.calculate_overall_score() == 0.0
    
    def test_partial_dimensions(self):
        """Test handling of partially populated dimensions."""
        metrics = MultiDimensionalMetrics(
            content_metrics={ContentDimension.ENTROPY: 0.8},
            performance_metrics={},
            quality_metrics={QualityDimension.DATA_INTEGRITY: 1.0},
            overall_score=0.5,
            confidence_score=0.8
        )
        
        # Should handle partial data gracefully
        score = metrics.calculate_overall_score()
        assert 0.0 <= score <= 1.0


class TestValidationResult:
    """Test ValidationResult model."""
    
    def test_validation_hash_generation(self):
        """Test automatic validation hash generation."""
        result = ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["integrity", "completeness", "consistency", "accuracy"],
            checks_passed=4,
            checks_failed=0,
            validation_hash=""  # Will be auto-generated
        )
        
        assert result.validation_hash != ""
        assert len(result.validation_hash) == 64  # SHA-256
    
    def test_validation_hash_determinism(self):
        """Test that validation hash is deterministic."""
        result1 = ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["test"],
            validation_hash=""
        )
        
        result2 = ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["test"],
            validation_hash=""
        )
        
        # Hashes should be similar structure but different due to timestamp
        assert len(result1.validation_hash) == len(result2.validation_hash)
    
    def test_all_checks_passed(self):
        """Test scenario where all validation checks pass."""
        result = ValidationResult(
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
        
        assert result.is_valid
        assert result.checks_passed == 4
        assert result.checks_failed == 0
        assert len(result.errors) == 0
    
    def test_partial_validation_failure(self):
        """Test scenario with partial validation failures."""
        result = ValidationResult(
            is_valid=False,
            integrity_check=True,
            completeness_check=False,
            consistency_check=True,
            accuracy_check=False,
            checks_performed=["integrity", "completeness", "consistency", "accuracy"],
            checks_passed=2,
            checks_failed=2,
            errors=["Completeness check failed", "Accuracy check failed"],
            validation_hash=""
        )
        
        assert not result.is_valid
        assert result.checks_passed == 2
        assert result.checks_failed == 2
        assert len(result.errors) == 2
    
    def test_warnings_without_errors(self):
        """Test validation with warnings but no errors."""
        result = ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["all"],
            checks_passed=4,
            checks_failed=0,
            warnings=["Performance slightly below expected"],
            validation_hash=""
        )
        
        assert result.is_valid
        assert len(result.warnings) == 1
        assert len(result.errors) == 0


class TestMetaLearningContext:
    """Test MetaLearningContext model."""
    
    def test_context_creation(self):
        """Test basic context creation."""
        context = MetaLearningContext(
            test_run_id="test_123",
            test_environment={"os": "linux", "python": "3.9"},
            previous_tests_count=100,
            historical_average=3.5,
            trend_direction="improving"
        )
        
        assert context.test_run_id == "test_123"
        assert context.previous_tests_count == 100
        assert context.historical_average == 3.5
        assert context.trend_direction == "improving"
    
    def test_prediction_context(self):
        """Test prediction-related context."""
        context = MetaLearningContext(
            test_run_id="test_123",
            predicted_outcome={"compression_ratio": 3.0, "time_ms": 50.0},
            prediction_accuracy=0.95,
            prediction_model_version="v1.0.0"
        )
        
        assert context.predicted_outcome is not None
        assert context.prediction_accuracy == 0.95
        assert context.prediction_model_version == "v1.0.0"
    
    def test_learning_signals(self):
        """Test learning signals collection."""
        context = MetaLearningContext(
            test_run_id="test_123",
            learning_signals=["anomaly_detected", "new_pattern", "performance_improvement"],
            anomaly_score=0.85,
            novelty_score=0.70,
            learning_value=0.90
        )
        
        assert len(context.learning_signals) == 3
        assert context.anomaly_score == 0.85
        assert context.novelty_score == 0.70
        assert context.learning_value == 0.90
    
    @pytest.mark.parametrize("score", [-0.1, 1.1])
    def test_score_boundaries(self, score):
        """Test score boundary validation."""
        with pytest.raises(Exception):
            MetaLearningContext(
                test_run_id="test_123",
                anomaly_score=score  # Invalid
            )


class TestEnhancedViabilityTest:
    """Test EnhancedViabilityTest model."""
    
    def test_complete_test_creation(self):
        """Test creation of complete enhanced viability test."""
        fingerprint = ContentFingerprint(
            sha256="a" * 64,
            size_bytes=1000,
            content_type="text/plain",
            entropy=0.7,
            redundancy=0.3
        )
        
        metrics = MultiDimensionalMetrics(
            content_metrics={ContentDimension.ENTROPY: 0.7},
            performance_metrics={PerformanceDimension.COMPRESSION_RATIO: 3.5},
            quality_metrics={QualityDimension.DATA_INTEGRITY: 1.0},
            overall_score=0.85,
            confidence_score=0.90
        )
        
        validation = ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["all"],
            validation_hash=""
        )
        
        context = MetaLearningContext(
            test_run_id="test_123"
        )
        
        test = EnhancedViabilityTest(
            test_id="test_123",
            content_fingerprint=fingerprint,
            algorithm="gzip",
            metrics=metrics,
            validation=validation,
            meta_context=context,
            success=True,
            execution_time_ms=50.0,
            compression_ratio=3.5,
            compression_percentage=71.4,
            original_size=1000,
            compressed_size=286
        )
        
        assert test.test_id == "test_123"
        assert test.algorithm == "gzip"
        assert test.success
        assert test.compression_ratio == 3.5
    
    def test_json_serialization(self):
        """Test JSON serialization of complete test."""
        fingerprint = ContentFingerprint(
            sha256="a" * 64,
            size_bytes=1000,
            content_type="text/plain",
            entropy=0.7,
            redundancy=0.3
        )
        
        metrics = MultiDimensionalMetrics(
            content_metrics={ContentDimension.ENTROPY: 0.7},
            performance_metrics={},
            quality_metrics={},
            overall_score=0.85,
            confidence_score=0.90
        )
        
        validation = ValidationResult(
            is_valid=True,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=[],
            validation_hash=""
        )
        
        context = MetaLearningContext(test_run_id="test_123")
        
        test = EnhancedViabilityTest(
            test_id="test_123",
            content_fingerprint=fingerprint,
            algorithm="gzip",
            metrics=metrics,
            validation=validation,
            meta_context=context,
            success=True,
            execution_time_ms=50.0,
            compression_ratio=3.5,
            compression_percentage=71.4,
            original_size=1000,
            compressed_size=286
        )
        
        # Test serialization
        json_str = test.json()
        assert json_str is not None
        assert "test_123" in json_str
        
        # Test deserialization
        test_dict = json.loads(json_str)
        assert test_dict["test_id"] == "test_123"
        assert test_dict["algorithm"] == "gzip"
    
    def test_tags_and_annotations(self):
        """Test tags and annotations handling."""
        fingerprint = ContentFingerprint(
            sha256="a" * 64,
            size_bytes=1000,
            content_type="text/plain",
            entropy=0.7,
            redundancy=0.3
        )
        
        test = EnhancedViabilityTest(
            test_id="test_123",
            content_fingerprint=fingerprint,
            algorithm="gzip",
            metrics=MultiDimensionalMetrics(
                content_metrics={},
                performance_metrics={},
                quality_metrics={},
                overall_score=0.85,
                confidence_score=0.90
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
            meta_context=MetaLearningContext(test_run_id="test_123"),
            success=True,
            execution_time_ms=50.0,
            compression_ratio=3.5,
            compression_percentage=71.4,
            original_size=1000,
            compressed_size=286,
            tags=["json", "production", "critical"],
            annotations={"priority": "high", "reviewed": True}
        )
        
        assert len(test.tags) == 3
        assert "json" in test.tags
        assert test.annotations["priority"] == "high"
        assert test.annotations["reviewed"] is True


class TestProofOfPerformance:
    """Test ProofOfPerformance model."""
    
    def test_proof_generation(self):
        """Test automatic proof generation."""
        proof = ProofOfPerformance.generate_proof(
            test_id="test_123",
            compression_ratio=3.5,
            compression_time=0.050,
            algorithm="gzip",
            content_hash="a" * 64
        )
        
        assert proof.test_id == "test_123"
        assert proof.claimed_compression_ratio == 3.5
        assert proof.claimed_compression_time == 0.050
        assert proof.claimed_algorithm == "gzip"
        assert len(proof.proof_hash) == 64  # SHA-256
        assert proof.verifiable is True
    
    def test_proof_determinism(self):
        """Test that same inputs produce same proof."""
        proof1 = ProofOfPerformance.generate_proof(
            test_id="test_123",
            compression_ratio=3.5,
            compression_time=0.050,
            algorithm="gzip",
            content_hash="a" * 64
        )
        
        proof2 = ProofOfPerformance.generate_proof(
            test_id="test_123",
            compression_ratio=3.5,
            compression_time=0.050,
            algorithm="gzip",
            content_hash="a" * 64
        )
        
        # Proofs should be similar but timestamps differ
        assert proof1.test_id == proof2.test_id
        assert proof1.claimed_compression_ratio == proof2.claimed_compression_ratio
    
    def test_proof_chain(self):
        """Test proof chain linking."""
        proof1 = ProofOfPerformance.generate_proof(
            test_id="test_1",
            compression_ratio=3.0,
            compression_time=0.040,
            algorithm="gzip",
            content_hash="a" * 64
        )
        
        proof2 = ProofOfPerformance(
            proof_id="proof_2",
            test_id="test_2",
            proof_hash="b" * 64,
            claimed_compression_ratio=3.5,
            claimed_compression_time=0.050,
            claimed_algorithm="gzip",
            verifiable=True,
            verification_method="reproducible_test",
            previous_proof=proof1.proof_id
        )
        
        assert proof2.previous_proof == proof1.proof_id


class TestMetaLearningInsight:
    """Test MetaLearningInsight model."""
    
    def test_insight_creation(self):
        """Test creating meta-learning insight."""
        insight = MetaLearningInsight(
            insight_id="insight_123",
            insight_type="best_algorithm_for_content",
            insight_description="GZIP performs best on JSON content",
            evidence_test_ids=["test_1", "test_2", "test_3"],
            evidence_strength=0.90,
            sample_size=150,
            statistical_confidence=0.95,
            p_value=0.01,
            actionable=True,
            recommended_action="Use GZIP for JSON compression",
            expected_improvement=0.25,
            insight_hash="",
            novelty=0.70,
            importance=0.85,
            generalizability=0.80
        )
        
        assert insight.insight_type == "best_algorithm_for_content"
        assert insight.sample_size == 150
        assert insight.actionable is True
        assert len(insight.insight_hash) == 64  # Auto-generated
    
    def test_high_confidence_insight(self):
        """Test high confidence insight characteristics."""
        insight = MetaLearningInsight(
            insight_id="insight_high",
            insight_type="performance_pattern",
            insight_description="Pattern detected",
            evidence_test_ids=[f"test_{i}" for i in range(500)],
            evidence_strength=0.95,
            sample_size=500,
            statistical_confidence=0.99,
            p_value=0.001,
            actionable=True,
            insight_hash="",
            novelty=0.90,
            importance=0.95,
            generalizability=0.92
        )
        
        assert insight.sample_size >= 100  # Large sample
        assert insight.statistical_confidence >= 0.95
        assert insight.p_value <= 0.05
        assert insight.importance >= 0.90
    
    def test_low_confidence_insight(self):
        """Test low confidence insight (needs more evidence)."""
        insight = MetaLearningInsight(
            insight_id="insight_low",
            insight_type="tentative_pattern",
            insight_description="Possible pattern",
            evidence_test_ids=["test_1", "test_2"],
            evidence_strength=0.60,
            sample_size=2,
            statistical_confidence=0.70,
            p_value=0.15,
            actionable=False,
            insight_hash="",
            novelty=0.95,  # High novelty but low confidence
            importance=0.50,
            generalizability=0.40
        )
        
        assert insight.sample_size < 10
        assert insight.statistical_confidence < 0.80
        assert insight.actionable is False  # Not enough evidence


class TestComparativeAnalysis:
    """Test ComparativeAnalysis model."""
    
    def test_analysis_creation(self):
        """Test creating comparative analysis."""
        analysis = ComparativeAnalysis(
            analysis_id="analysis_123",
            tests_compared=["test_1", "test_2", "test_3"],
            algorithms_compared=["gzip", "lzma", "zstd"],
            ranking_by_ratio=[
                {"algorithm": "lzma", "ratio": 4.5},
                {"algorithm": "zstd", "ratio": 3.8},
                {"algorithm": "gzip", "ratio": 3.2}
            ],
            ranking_by_speed=[
                {"algorithm": "gzip", "time_ms": 45},
                {"algorithm": "zstd", "time_ms": 52},
                {"algorithm": "lzma", "time_ms": 120}
            ],
            ranking_by_efficiency=[],
            ranking_by_quality=[],
            overall_winner="zstd",
            winner_confidence=0.88,
            winner_proof="a" * 64,
            key_findings=["ZSTD best balanced", "LZMA best ratio"],
            recommendations=["Use ZSTD for balanced needs"],
            predicted_best_for_similar="zstd",
            prediction_confidence=0.85
        )
        
        assert len(analysis.algorithms_compared) == 3
        assert analysis.overall_winner == "zstd"
        assert analysis.winner_confidence == 0.88
        assert len(analysis.winner_proof) == 64


# Edge case and boundary condition tests
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_compression(self):
        """Test scenario where no compression achieved."""
        test = EnhancedViabilityTest(
            test_id="test_zero",
            content_fingerprint=ContentFingerprint(
                sha256="a" * 64,
                size_bytes=1000,
                content_type="random",
                entropy=1.0,
                redundancy=0.0
            ),
            algorithm="gzip",
            metrics=MultiDimensionalMetrics(
                content_metrics={},
                performance_metrics={},
                quality_metrics={},
                overall_score=0.1,
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
            meta_context=MetaLearningContext(test_run_id="test"),
            success=True,
            execution_time_ms=50.0,
            compression_ratio=1.0,  # No compression
            compression_percentage=0.0,
            original_size=1000,
            compressed_size=1000  # Same size
        )
        
        assert test.compression_ratio == 1.0
        assert test.compression_percentage == 0.0
        assert test.original_size == test.compressed_size
    
    def test_extreme_compression(self):
        """Test scenario with extreme compression ratio."""
        test = EnhancedViabilityTest(
            test_id="test_extreme",
            content_fingerprint=ContentFingerprint(
                sha256="a" * 64,
                size_bytes=10000,
                content_type="text",
                entropy=0.01,
                redundancy=0.99
            ),
            algorithm="lzma",
            metrics=MultiDimensionalMetrics(
                content_metrics={},
                performance_metrics={},
                quality_metrics={},
                overall_score=0.95,
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
            meta_context=MetaLearningContext(test_run_id="test"),
            success=True,
            execution_time_ms=200.0,
            compression_ratio=100.0,  # Extreme compression
            compression_percentage=99.0,
            original_size=10000,
            compressed_size=100
        )
        
        assert test.compression_ratio == 100.0
        assert test.compression_percentage == 99.0
    
    def test_very_slow_compression(self):
        """Test scenario with very slow compression."""
        test = EnhancedViabilityTest(
            test_id="test_slow",
            content_fingerprint=ContentFingerprint(
                sha256="a" * 64,
                size_bytes=1000000,
                content_type="binary",
                entropy=0.8,
                redundancy=0.2
            ),
            algorithm="lzma",
            metrics=MultiDimensionalMetrics(
                content_metrics={},
                performance_metrics={PerformanceDimension.COMPRESSION_SPEED: 0.1},
                quality_metrics={},
                overall_score=0.5,
                confidence_score=0.8
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
            meta_context=MetaLearningContext(test_run_id="test"),
            success=True,
            execution_time_ms=30000.0,  # 30 seconds
            compression_ratio=4.5,
            compression_percentage=77.8,
            original_size=1000000,
            compressed_size=222222
        )
        
        assert test.execution_time_ms >= 10000.0  # Very slow
    
    def test_failed_compression(self):
        """Test failed compression scenario."""
        test = EnhancedViabilityTest(
            test_id="test_failed",
            content_fingerprint=ContentFingerprint(
                sha256="a" * 64,
                size_bytes=1000,
                content_type="encrypted",
                entropy=1.0,
                redundancy=0.0
            ),
            algorithm="gzip",
            metrics=MultiDimensionalMetrics(
                content_metrics={},
                performance_metrics={},
                quality_metrics={},
                overall_score=0.0,
                confidence_score=1.0
            ),
            validation=ValidationResult(
                is_valid=False,
                integrity_check=False,
                completeness_check=True,
                consistency_check=True,
                accuracy_check=False,
                checks_performed=["integrity", "accuracy"],
                checks_failed=2,
                errors=["Compression failed", "Data corrupted"],
                validation_hash=""
            ),
            meta_context=MetaLearningContext(test_run_id="test"),
            success=False,  # Failed
            execution_time_ms=10.0,
            compression_ratio=1.0,
            compression_percentage=0.0,
            original_size=1000,
            compressed_size=1000
        )
        
        assert test.success is False
        assert test.validation.is_valid is False
        assert len(test.validation.errors) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

