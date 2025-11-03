#!/usr/bin/env python3
"""
Test suite for compression models.
Tests the fixed compression parameters validation.
"""

import pytest
from backend.app.models.compression import (
    CompressionParameters, 
    CompressionAlgorithm, 
    CompressionLevel,
    CompressionRequest,
    CompressionResult
)


class TestCompressionParameters:
    """Test compression parameters validation."""
    
    def test_enum_level_validation(self):
        """Test that enum compression levels work correctly."""
        # Test with enum values
        params = CompressionParameters(
            algorithm=CompressionAlgorithm.GZIP,
            level=CompressionLevel.BALANCED
        )
        assert params.level == CompressionLevel.BALANCED
        assert params.get_level_value() == "balanced"
        assert params.get_algorithm_specific_level() == 6  # GZIP converts to integer
    
    def test_integer_level_validation(self):
        """Test that integer compression levels work correctly."""
        # Test with integer values
        params = CompressionParameters(
            algorithm=CompressionAlgorithm.GZIP,
            level=6
        )
        assert params.level == 6
        assert params.get_level_value() == 6
        assert params.get_algorithm_specific_level() == 6
    
    def test_string_level_validation(self):
        """Test that string compression levels work correctly."""
        # Test with string values
        params = CompressionParameters(
            algorithm=CompressionAlgorithm.GZIP,
            level="balanced"
        )
        assert params.level == "balanced"
        assert params.get_level_value() == "balanced"
        assert params.get_algorithm_specific_level() == 6  # GZIP converts to integer
    
    def test_invalid_integer_level(self):
        """Test that invalid integer levels are rejected."""
        with pytest.raises(ValueError, match="Integer compression level must be between 1 and 9"):
            CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level=10  # Invalid level
            )
    
    def test_invalid_string_level(self):
        """Test that invalid string levels are rejected."""
        with pytest.raises(ValueError, match="Invalid compression level"):
            CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level="invalid_level"
            )
    
    def test_algorithm_specific_level_conversion(self):
        """Test algorithm-specific level conversion."""
        # Test GZIP with different level types
        gzip_params = CompressionParameters(
            algorithm=CompressionAlgorithm.GZIP,
            level=CompressionLevel.MAXIMUM
        )
        assert gzip_params.get_algorithm_specific_level() == 9
        
        # Test content_aware with string level
        content_aware_params = CompressionParameters(
            algorithm=CompressionAlgorithm.CONTENT_AWARE,
            level=CompressionLevel.BALANCED
        )
        assert content_aware_params.get_algorithm_specific_level() == "balanced"
        
        # Test content_aware with integer level (should convert to string)
        content_aware_params_int = CompressionParameters(
            algorithm=CompressionAlgorithm.CONTENT_AWARE,
            level=6
        )
        assert content_aware_params_int.get_algorithm_specific_level() == CompressionLevel.BALANCED
    
    def test_default_parameters(self):
        """Test default parameter values."""
        params = CompressionParameters(algorithm=CompressionAlgorithm.GZIP)
        assert params.level == CompressionLevel.BALANCED
        assert params.block_size == 8192
        assert params.threads == 1
        assert params.optimization_target == "ratio"
    
    def test_advanced_parameters(self):
        """Test advanced parameter validation."""
        params = CompressionParameters(
            algorithm=CompressionAlgorithm.QUANTUM_BIOLOGICAL,
            level=CompressionLevel.OPTIMAL,
            quantum_qubits=16,
            biological_population=200,
            neural_layers=5,
            spike_threshold=0.2
        )
        assert params.quantum_qubits == 16
        assert params.biological_population == 200
        assert params.neural_layers == 5
        assert params.spike_threshold == 0.2


class TestCompressionRequest:
    """Test compression request validation."""
    
    def test_valid_request_with_content(self):
        """Test valid request with content."""
        request = CompressionRequest(
            content="test content",
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level=6
            )
        )
        assert request.content == "test content"
        assert request.file_id is None
        assert request.parameters.algorithm == CompressionAlgorithm.GZIP
    
    def test_valid_request_with_file_id(self):
        """Test valid request with file_id."""
        request = CompressionRequest(
            file_id="test_file_123",
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.LZ4,
                level=CompressionLevel.FAST
            )
        )
        assert request.file_id == "test_file_123"
        assert request.content is None
        assert request.parameters.algorithm == CompressionAlgorithm.LZ4
    
    def test_invalid_request_no_content_or_file(self):
        """Test that request without content or file_id is rejected."""
        with pytest.raises(ValueError, match="Either content or file_id must be provided"):
            CompressionRequest(
                parameters=CompressionParameters(
                    algorithm=CompressionAlgorithm.GZIP,
                    level=6
                )
            )


class TestCompressionResult:
    """Test compression result model."""
    
    def test_valid_result(self):
        """Test valid compression result."""
        result = CompressionResult(
            original_size=1000,
            compressed_size=500,
            compression_ratio=2.0,
            compression_percentage=50.0,
            algorithm_used=CompressionAlgorithm.GZIP,
            parameters_used=CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level=6
            ),
            compression_time=0.1,
            quality_score=0.95
        )
        assert result.original_size == 1000
        assert result.compressed_size == 500
        assert result.compression_ratio == 2.0
        assert result.compression_percentage == 50.0
        assert result.algorithm_used == CompressionAlgorithm.GZIP
        assert result.compression_time == 0.1
        assert result.quality_score == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
