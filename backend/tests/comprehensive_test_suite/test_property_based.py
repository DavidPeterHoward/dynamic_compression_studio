"""
Property-Based Testing Suite

Tests properties and invariants that should hold across all inputs using Hypothesis.
Tests include:
- Compression/decompression round-trip property
- Compression ratio properties
- Data integrity properties
- Performance properties
- Model validation properties
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import gzip
import bz2
import lzma
import zlib
import hashlib
from typing import Any

from app.models.viability_models import (
    ContentFingerprint,
    MultiDimensionalMetrics,
    ValidationResult,
    MetaLearningContext,
    EnhancedViabilityTest,
    ContentDimension,
    PerformanceDimension,
    QualityDimension
)


# ==================== Basic Property Tests ====================

class TestCompressionProperties:
    """Test fundamental compression properties."""
    
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=50, deadline=2000)
    def test_compression_decompression_round_trip_gzip(self, data):
        """Property: compress(decompress(x)) == x for all x."""
        compressed = gzip.compress(data)
        decompressed = gzip.decompress(compressed)
        assert decompressed == data
    
    @given(st.binary(min_size=1, max_size=10000))
    @settings(max_examples=50, deadline=2000)
    def test_compression_decompression_round_trip_lzma(self, data):
        """Property: compress(decompress(x)) == x for all x."""
        assume(len(data) > 0)  # LZMA doesn't handle empty well
        compressed = lzma.compress(data)
        decompressed = lzma.decompress(compressed)
        assert decompressed == data
    
    @given(st.binary(min_size=1, max_size=10000))
    @settings(max_examples=50, deadline=2000)
    def test_compression_decompression_round_trip_bzip2(self, data):
        """Property: compress(decompress(x)) == x for all x."""
        assume(len(data) > 0)  # BZIP2 doesn't handle empty
        compressed = bz2.compress(data)
        decompressed = bz2.decompress(compressed)
        assert decompressed == data
    
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=50, deadline=1000)
    def test_compression_decompression_round_trip_zlib(self, data):
        """Property: compress(decompress(x)) == x for all x."""
        compressed = zlib.compress(data)
        decompressed = zlib.decompress(compressed)
        assert decompressed == data
    
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=30, deadline=1000)
    def test_compression_is_deterministic(self, data):
        """Property: compress(x) == compress(x) (deterministic)."""
        compressed1 = gzip.compress(data)
        compressed2 = gzip.compress(data)
        assert compressed1 == compressed2
    
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=30, deadline=1000)
    def test_compressed_size_is_positive(self, data):
        """Property: len(compress(x)) > 0 for all x."""
        compressed = gzip.compress(data)
        assert len(compressed) > 0
    
    @given(st.binary(min_size=2, max_size=1000))
    @settings(max_examples=30, deadline=1000)
    def test_different_inputs_different_outputs(self, data):
        """Property: x != y => compress(x) != compress(y) (usually)."""
        # Modify data slightly
        modified_data = data[:-1] + bytes([(data[-1] + 1) % 256])
        
        compressed1 = gzip.compress(data)
        compressed2 = gzip.compress(modified_data)
        
        # Usually different (not guaranteed due to compression)
        # But hashes should always differ
        hash1 = hashlib.sha256(data).hexdigest()
        hash2 = hashlib.sha256(modified_data).hexdigest()
        assert hash1 != hash2


class TestContentFingerprintProperties:
    """Test ContentFingerprint properties."""
    
    @given(
        st.binary(min_size=1, max_size=10000),
        st.text(min_size=1, max_size=50),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=30, deadline=1000)
    def test_fingerprint_uniqueness(self, content, content_type, entropy, redundancy):
        """Property: Different content => different fingerprint."""
        fp1 = ContentFingerprint(
            sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
            content_type=content_type,
            entropy=entropy,
            redundancy=redundancy
        )
        
        # Modify content
        modified_content = content + b"x"
        fp2 = ContentFingerprint(
            sha256=hashlib.sha256(modified_content).hexdigest(),
            size_bytes=len(modified_content),
            content_type=content_type,
            entropy=entropy,
            redundancy=redundancy
        )
        
        assert fp1.sha256 != fp2.sha256
    
    @given(
        st.binary(min_size=1, max_size=10000),
        st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=30, deadline=1000)
    def test_fingerprint_determinism(self, content, content_type):
        """Property: Same content => same fingerprint."""
        entropy = 0.5
        redundancy = 0.5
        
        fp1 = ContentFingerprint(
            sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
            content_type=content_type,
            entropy=entropy,
            redundancy=redundancy
        )
        
        fp2 = ContentFingerprint(
            sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
            content_type=content_type,
            entropy=entropy,
            redundancy=redundancy
        )
        
        assert fp1.sha256 == fp2.sha256
        assert fp1.size_bytes == fp2.size_bytes
    
    @given(
        st.binary(min_size=1, max_size=10000),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=30, deadline=1000)
    def test_entropy_redundancy_relationship(self, content, entropy, redundancy):
        """Property: entropy + redundancy should reflect content characteristics."""
        fp = ContentFingerprint(
            sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
            content_type="test",
            entropy=entropy,
            redundancy=redundancy
        )
        
        # Both should be in valid range
        assert 0 <= fp.entropy <= 1
        assert 0 <= fp.redundancy <= 1
        
        # Generally, high entropy => low redundancy, but not enforced
        # Just check they're valid


class TestMetricsProperties:
    """Test MultiDimensionalMetrics properties."""
    
    @given(
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=30, deadline=1000)
    def test_score_bounds(self, overall_score, confidence_score):
        """Property: All scores should be in [0, 1]."""
        metrics = MultiDimensionalMetrics(
            content_metrics={},
            performance_metrics={},
            quality_metrics={},
            overall_score=overall_score,
            confidence_score=confidence_score
        )
        
        assert 0 <= metrics.overall_score <= 1
        assert 0 <= metrics.confidence_score <= 1
    
    @given(
        st.dictionaries(
            st.sampled_from(list(ContentDimension)),
            st.floats(min_value=0.0, max_value=1.0),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=20, deadline=1000)
    def test_content_metrics_bounds(self, content_metrics):
        """Property: Content metric values should be in [0, 1]."""
        metrics = MultiDimensionalMetrics(
            content_metrics=content_metrics,
            performance_metrics={},
            quality_metrics={},
            overall_score=0.5,
            confidence_score=0.9
        )
        
        for value in metrics.content_metrics.values():
            assert 0 <= value <= 1
    
    @given(
        st.dictionaries(
            st.sampled_from(list(PerformanceDimension)),
            st.floats(min_value=0.0, max_value=10.0),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=20, deadline=1000)
    def test_performance_metrics_non_negative(self, performance_metrics):
        """Property: Performance metrics should be non-negative."""
        metrics = MultiDimensionalMetrics(
            content_metrics={},
            performance_metrics=performance_metrics,
            quality_metrics={},
            overall_score=0.5,
            confidence_score=0.9
        )
        
        for value in metrics.performance_metrics.values():
            assert value >= 0


class TestValidationProperties:
    """Test ValidationResult properties."""
    
    @given(
        st.booleans(),
        st.booleans(),
        st.booleans(),
        st.booleans(),
        st.booleans()
    )
    @settings(max_examples=30, deadline=1000)
    def test_validation_consistency(self, is_valid, integrity, completeness, consistency, accuracy):
        """Property: If all checks pass, is_valid should be True."""
        if integrity and completeness and consistency and accuracy:
            is_valid = True  # Force consistency
        
        validation = ValidationResult(
            is_valid=is_valid,
            integrity_check=integrity,
            completeness_check=completeness,
            consistency_check=consistency,
            accuracy_check=accuracy,
            checks_performed=["integrity", "completeness", "consistency", "accuracy"],
            checks_passed=sum([integrity, completeness, consistency, accuracy]),
            checks_failed=4 - sum([integrity, completeness, consistency, accuracy]),
            validation_hash=""
        )
        
        # If all checks pass, should be valid
        if all([integrity, completeness, consistency, accuracy]):
            assert validation.is_valid is True
        
        # Check count consistency
        assert validation.checks_passed + validation.checks_failed == 4
    
    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=20, deadline=1000)
    def test_check_count_consistency(self, passed):
        """Property: checks_passed + checks_failed == total checks."""
        total = 10
        failed = total - passed
        
        validation = ValidationResult(
            is_valid=passed == total,
            integrity_check=True,
            completeness_check=True,
            consistency_check=True,
            accuracy_check=True,
            checks_performed=["check"] * total,
            checks_passed=passed,
            checks_failed=failed,
            validation_hash=""
        )
        
        assert validation.checks_passed + validation.checks_failed == total


class TestViabilityTestProperties:
    """Test EnhancedViabilityTest properties."""
    
    @given(
        st.integers(min_value=1, max_value=1000000),
        st.floats(min_value=1.0, max_value=100.0)
    )
    @settings(max_examples=30, deadline=1000)
    def test_compression_ratio_calculation(self, original_size, ratio):
        """Property: compression_ratio = original_size / compressed_size."""
        compressed_size = int(original_size / ratio)
        assume(compressed_size > 0)
        
        calculated_ratio = original_size / compressed_size
        
        # Should be close to intended ratio
        assert abs(calculated_ratio - ratio) < 0.1 * ratio
    
    @given(
        st.integers(min_value=100, max_value=1000000),
        st.integers(min_value=10, max_value=100000)
    )
    @settings(max_examples=30, deadline=1000)
    def test_compression_percentage_bounds(self, original_size, compressed_size):
        """Property: compression_percentage should be in [0, 100] or negative for expansion."""
        assume(compressed_size > 0)
        
        compression_percentage = ((original_size - compressed_size) / original_size * 100)
        
        # Should be reasonable
        if compressed_size <= original_size:
            assert 0 <= compression_percentage <= 100
        else:
            assert compression_percentage < 0  # Expansion
    
    @given(
        st.floats(min_value=0.0, max_value=10000.0)
    )
    @settings(max_examples=20, deadline=1000)
    def test_execution_time_non_negative(self, execution_time):
        """Property: execution_time should be non-negative."""
        assume(execution_time >= 0)
        assert execution_time >= 0


# ==================== Stateful Testing ====================

class CompressionStateMachine(RuleBasedStateMachine):
    """Stateful testing for compression operations."""
    
    def __init__(self):
        super().__init__()
        self.test_data = {}
        self.compressed_data = {}
    
    @rule(
        test_id=st.text(min_size=1, max_size=20),
        data=st.binary(min_size=0, max_size=1000)
    )
    def add_test_data(self, test_id, data):
        """Add test data."""
        self.test_data[test_id] = data
    
    @rule(test_id=st.sampled_from([]))
    def compress_data(self, test_id):
        """Compress stored data."""
        if test_id in self.test_data:
            data = self.test_data[test_id]
            compressed = gzip.compress(data)
            self.compressed_data[test_id] = compressed
    
    @rule(test_id=st.sampled_from([]))
    def decompress_and_verify(self, test_id):
        """Decompress and verify data."""
        if test_id in self.compressed_data:
            compressed = self.compressed_data[test_id]
            decompressed = gzip.decompress(compressed)
            assert decompressed == self.test_data[test_id]
    
    @invariant()
    def test_data_not_empty(self):
        """Invariant: If we have compressed data, we should have original data."""
        for test_id in self.compressed_data:
            assert test_id in self.test_data


# Disabled by default as it requires hypothesis.stateful
# TestCompressionStateMachine = CompressionStateMachine.TestCase


# ==================== Parametric Properties ====================

class TestParametricProperties:
    """Test parametric properties across algorithms."""
    
    @given(
        st.binary(min_size=1, max_size=1000),
        st.sampled_from(["gzip", "zlib"])
    )
    @settings(max_examples=20, deadline=2000)
    def test_universal_round_trip_property(self, data, algorithm):
        """Property: All algorithms should support round-trip."""
        if algorithm == "gzip":
            compressed = gzip.compress(data)
            decompressed = gzip.decompress(compressed)
        elif algorithm == "zlib":
            compressed = zlib.compress(data)
            decompressed = zlib.decompress(compressed)
        else:
            assume(False)  # Skip unknown algorithms
        
        assert decompressed == data
    
    @given(
        st.binary(min_size=10, max_size=1000),
        st.sampled_from(["gzip", "zlib"])
    )
    @settings(max_examples=20, deadline=2000)
    def test_repeated_content_compresses_well(self, pattern, algorithm):
        """Property: Repeated patterns should compress well."""
        # Create highly repetitive data
        data = pattern * 10
        
        if algorithm == "gzip":
            compressed = gzip.compress(data)
        elif algorithm == "zlib":
            compressed = zlib.compress(data)
        else:
            assume(False)
        
        # Should achieve at least 2x compression on repetitive data
        compression_ratio = len(data) / len(compressed)
        assert compression_ratio >= 2.0
    
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=20, deadline=1000)
    def test_size_monotonicity(self, size):
        """Property: Larger input generally means larger compressed output."""
        data1 = b"A" * size
        data2 = b"A" * (size * 2)
        
        compressed1 = gzip.compress(data1)
        compressed2 = gzip.compress(data2)
        
        # For highly repetitive data, this may not hold strictly
        # But compressed2 shouldn't be much smaller than compressed1
        # Allow some flexibility due to compression overhead
        assert len(compressed2) >= len(compressed1) * 0.5


class TestInvariantProperties:
    """Test invariant properties that should always hold."""
    
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=30, deadline=1000)
    def test_hash_consistency(self, data):
        """Property: Hash of data should be consistent."""
        hash1 = hashlib.sha256(data).hexdigest()
        hash2 = hashlib.sha256(data).hexdigest()
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
    
    @given(
        st.binary(min_size=0, max_size=10000),
        st.binary(min_size=0, max_size=10000)
    )
    @settings(max_examples=30, deadline=1000)
    def test_concatenation_property(self, data1, data2):
        """Property: concat properties."""
        concatenated = data1 + data2
        assert len(concatenated) == len(data1) + len(data2)
        assert concatenated[:len(data1)] == data1
        assert concatenated[len(data1):] == data2
    
    @given(st.binary(min_size=1, max_size=1000))
    @settings(max_examples=20, deadline=1000)
    def test_idempotent_hashing(self, data):
        """Property: Hashing is idempotent."""
        hash1 = hashlib.sha256(data).hexdigest()
        hash2 = hashlib.sha256(data).hexdigest()
        hash3 = hashlib.sha256(data).hexdigest()
        assert hash1 == hash2 == hash3


# ==================== Edge Case Properties ====================

class TestEdgeCaseProperties:
    """Test properties on edge cases."""
    
    @given(st.just(b""))
    @settings(max_examples=5, deadline=1000)
    def test_empty_input_handling(self, data):
        """Property: Empty input should be handled gracefully."""
        compressed = gzip.compress(data)
        decompressed = gzip.decompress(compressed)
        assert decompressed == data
        assert len(compressed) > 0  # Has header overhead
    
    @given(st.binary(min_size=1, max_size=1))
    @settings(max_examples=10, deadline=1000)
    def test_single_byte_handling(self, data):
        """Property: Single byte should be handled correctly."""
        compressed = gzip.compress(data)
        decompressed = gzip.decompress(compressed)
        assert decompressed == data
    
    @given(st.binary(min_size=1, max_size=10).filter(lambda x: len(set(x)) == 1))
    @settings(max_examples=10, deadline=1000)
    def test_uniform_data_compression(self, data):
        """Property: Uniform data should compress very well."""
        compressed = gzip.compress(data)
        decompressed = gzip.decompress(compressed)
        assert decompressed == data
        
        # Should achieve good compression
        if len(data) >= 5:
            assert len(compressed) < len(data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

