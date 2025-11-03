"""
Tests for CompressionEngine.

Tests cover:
- All compression algorithms
- Roundtrip correctness
- Performance metrics
- Caching functionality
- Error handling
"""

import pytest
import asyncio
from app.core.compression_engine import CompressionEngine, CompressionResult


@pytest.fixture
def engine():
    """Create compression engine for testing."""
    return CompressionEngine(cache_size=10)


@pytest.fixture
def test_data():
    """Test data fixtures."""
    return {
        "small": b"Hello, World!",
        "repetitive": b"abcd" * 1000,  # Should compress well
        "random": bytes(range(256)) * 4,  # Random data, poor compression
        "text": b"This is a sample text for compression testing. " * 50,
        "empty": b"",
        "single_byte": b"x"
    }


@pytest.mark.asyncio
async def test_engine_initialization(engine):
    """Test compression engine initializes correctly."""
    algorithms = engine.get_available_algorithms()
    assert len(algorithms) >= 1  # At least gzip should be available
    
    # Check basic algorithms are registered
    assert "gzip" in algorithms
    
    cache_stats = engine.get_cache_stats()
    assert cache_stats["cache_size"] == 0
    assert cache_stats["total_operations"] == 0


@pytest.mark.asyncio
async def test_gzip_compression_roundtrip(engine, test_data):
    """Test GZIP compression and decompression roundtrip."""
    original = test_data["text"]
    
    # Compress
    result = await engine.compress(original, algorithm="gzip", level=6)
    
    assert result.success is True
    assert result.algorithm == "gzip"
    assert result.original_size == len(original)
    assert result.compressed_size > 0
    assert result.compression_ratio > 1.0  # Should compress text
    assert result.compression_time > 0
    
    # Decompress
    decompressed = await engine.decompress(result.compressed_data, "gzip")
    assert decompressed == original


@pytest.mark.asyncio
async def test_all_algorithms_roundtrip(engine, test_data):
    """Test roundtrip for all available algorithms."""
    data = test_data["text"]
    
    algorithms = engine.get_available_algorithms()
    
    for algorithm in algorithms:
        # Compress
        result = await engine.compress(data, algorithm=algorithm, level=6)
        
        assert result.success is True, f"{algorithm} compression failed"
        assert result.algorithm == algorithm
        assert result.original_size == len(data)
        assert result.compressed_size > 0
        
        # Decompress
        try:
            decompressed = await engine.decompress(result.compressed_data, algorithm)
            assert decompressed == data, f"{algorithm} roundtrip failed"
        except Exception as e:
            pytest.fail(f"{algorithm} decompression failed: {e}")


@pytest.mark.asyncio
async def test_compression_levels(engine, test_data):
    """Test different compression levels."""
    data = test_data["repetitive"]  # Should compress well
    
    for level in [1, 6, 9]:
        result = await engine.compress(data, algorithm="gzip", level=level)
        
        assert result.success is True
        assert result.compression_ratio > 2.0  # Good compression for repetitive data
        
        # Higher levels should generally compress better (but not guaranteed)
        # Just verify the operation completes


@pytest.mark.asyncio
async def test_cache_functionality(engine, test_data):
    """Test content-hash caching."""
    data = test_data["text"]
    
    # First compression (cache miss)
    result1 = await engine.compress(data, algorithm="gzip", level=6, use_cache=True)
    assert result1.success is True
    
    cache_stats = engine.get_cache_stats()
    assert cache_stats["cache_misses"] == 1
    assert cache_stats["cache_hits"] == 0
    
    # Second compression (cache hit)
    result2 = await engine.compress(data, algorithm="gzip", level=6, use_cache=True)
    assert result2.success is True
    
    cache_stats = engine.get_cache_stats()
    assert cache_stats["cache_misses"] == 1
    assert cache_stats["cache_hits"] == 1
    
    # Results should be identical
    assert result1.compressed_size == result2.compressed_size
    assert result1.compression_ratio == result2.compression_ratio


@pytest.mark.asyncio
async def test_cache_disabled(engine, test_data):
    """Test that caching can be disabled."""
    data = test_data["text"]

    # Compress with cache disabled
    result1 = await engine.compress(data, algorithm="gzip", level=6, use_cache=False)
    result2 = await engine.compress(data, algorithm="gzip", level=6, use_cache=False)

    # Both should succeed but no cache operations recorded (cache not checked)
    cache_stats = engine.get_cache_stats()
    assert cache_stats["cache_hits"] == 0
    assert cache_stats["cache_misses"] == 0  # Cache not checked when disabled
    assert cache_stats["total_operations"] == 2  # But operations are counted


@pytest.mark.asyncio
async def test_unknown_algorithm(engine, test_data):
    """Test error handling for unknown algorithms."""
    data = test_data["text"]
    
    result = await engine.compress(data, algorithm="unknown", level=6)
    
    assert result.success is False
    assert "not available" in result.error
    assert result.compressed_size == 0


@pytest.mark.asyncio
async def test_decompression_with_wrong_algorithm(engine, test_data):
    """Test decompression with wrong algorithm."""
    data = test_data["text"]
    
    # Compress with gzip
    gzip_result = await engine.compress(data, algorithm="gzip", level=6)
    assert gzip_result.success is True
    
    # Try to decompress with different algorithm
    with pytest.raises(Exception):
        await engine.decompress(gzip_result.compressed_data, "zstd")


@pytest.mark.asyncio
async def test_empty_data_compression(engine):
    """Test compression of empty data."""
    result = await engine.compress(b"", algorithm="gzip", level=6)
    
    assert result.success is True
    assert result.original_size == 0
    assert result.compressed_size >= 0  # Empty data may still have header
    
    # Decompress
    decompressed = await engine.decompress(result.compressed_data, "gzip")
    assert decompressed == b""


@pytest.mark.asyncio
async def test_large_data_compression(engine):
    """Test compression of larger data."""
    # Create 1MB of repetitive data
    large_data = b"ABCDEFGH" * (1024 * 128)  # ~1MB
    
    result = await engine.compress(large_data, algorithm="gzip", level=6)
    
    assert result.success is True
    assert result.original_size == len(large_data)
    assert result.compressed_size < len(large_data)  # Should compress
    assert result.compression_ratio > 1.0
    
    # Roundtrip
    decompressed = await engine.decompress(result.compressed_data, "gzip")
    assert decompressed == large_data


@pytest.mark.asyncio
async def test_performance_metrics(engine, test_data):
    """Test that performance metrics are collected."""
    data = test_data["text"]
    
    result = await engine.compress(data, algorithm="gzip", level=6)
    
    assert result.compression_time > 0
    assert result.compression_ratio > 0
    assert result.space_saved_percent >= 0
    
    # For text data, should achieve some compression
    assert result.compression_ratio > 1.0


@pytest.mark.asyncio
async def test_cache_stats_tracking(engine, test_data):
    """Test cache statistics tracking."""
    data1 = test_data["text"]
    data2 = test_data["small"]
    
    # Multiple operations
    await engine.compress(data1, algorithm="gzip", level=6)
    await engine.compress(data1, algorithm="gzip", level=6)  # Cache hit
    await engine.compress(data2, algorithm="gzip", level=6)  # Cache miss
    
    stats = engine.get_cache_stats()
    
    assert stats["total_operations"] == 3
    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 2
    assert stats["hit_rate"] == pytest.approx(1/3, rel=0.1)


@pytest.mark.asyncio
async def test_cache_size_management(engine, test_data):
    """Test cache size management."""
    engine = CompressionEngine(cache_size=2)  # Small cache
    
    # Fill cache with different data
    for i in range(5):
        data = f"test data {i}".encode()
        await engine.compress(data, algorithm="gzip", level=6)
    
    stats = engine.get_cache_stats()
    
    # Cache should be at or below max size
    assert stats["cache_size"] <= 2


@pytest.mark.asyncio
async def test_clear_cache(engine, test_data):
    """Test cache clearing functionality."""
    data = test_data["text"]
    
    await engine.compress(data, algorithm="gzip", level=6)
    await engine.compress(data, algorithm="gzip", level=6)  # Hit
    
    stats_before = engine.get_cache_stats()
    assert stats_before["cache_hits"] > 0
    
    engine.clear_cache()
    
    stats_after = engine.get_cache_stats()
    assert stats_after["cache_size"] == 0
    assert stats_after["cache_hits"] == 0
    assert stats_after["cache_misses"] == 0


# Integration test
@pytest.mark.asyncio
@pytest.mark.integration
async def test_compression_engine_integration():
    """
    Integration test: Compress various data types and verify metrics.
    
    Tests the full compression pipeline.
    """
    engine = CompressionEngine()
    
    test_cases = [
        ("repetitive", b"AAAA" * 1000, True),  # Should compress very well
        ("text", b"This is sample text. " * 100, True),  # Should compress moderately
        ("random", bytes(range(256)) * 10, False),  # Should not compress well
    ]
    
    algorithms = engine.get_available_algorithms()
    
    for data_name, data, should_compress_well in test_cases:
        for algorithm in algorithms[:2]:  # Test first 2 algorithms to keep test fast
            
            result = await engine.compress(data, algorithm=algorithm, level=6)
            
            assert result.success, f"{algorithm} failed on {data_name}"
            assert result.compression_ratio > 0
            
            # Verify decompression
            decompressed = await engine.decompress(result.compressed_data, algorithm)
            assert decompressed == data, f"Roundtrip failed for {algorithm} on {data_name}"
            
            # Check compression quality expectations
            if should_compress_well:
                # For compressible data, expect at least 1.5x compression
                assert result.compression_ratio >= 1.5, \
                    f"Poor compression for {data_name} with {algorithm}: {result.compression_ratio}"
    
    print(f"\nIntegration test completed: {len(algorithms)} algorithms tested on {len(test_cases)} data types")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

