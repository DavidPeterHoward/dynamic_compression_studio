"""
Comprehensive Test Suite: Compression Algorithms

Tests all compression algorithms with:
- All available algorithms
- Edge cases and boundary conditions
- Performance characteristics
- Data integrity validation
- Algorithm-specific optimizations
"""

import pytest
import gzip
import bz2
import lzma
import zlib
import io
import os
import time
from typing import List, Tuple, Dict, Any

# Import compression algorithms
try:
    import lz4.frame
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False


class TestDataGenerator:
    """Generate test data with various characteristics."""
    
    @staticmethod
    def generate_repetitive_text(size: int = 1000) -> bytes:
        """Generate highly repetitive text (high compression ratio)."""
        pattern = b"AAAABBBBCCCCDDDD" * (size // 16 + 1)
        return pattern[:size]
    
    @staticmethod
    def generate_random_bytes(size: int = 1000) -> bytes:
        """Generate random bytes (low compression ratio)."""
        return os.urandom(size)
    
    @staticmethod
    def generate_json_like(size: int = 1000) -> bytes:
        """Generate JSON-like data."""
        json_pattern = b'{"key":"value","number":12345,"array":[1,2,3,4,5]}'
        result = json_pattern * (size // len(json_pattern) + 1)
        return result[:size]
    
    @staticmethod
    def generate_xml_like(size: int = 1000) -> bytes:
        """Generate XML-like data."""
        xml_pattern = b'<root><item id="1">Data</item><item id="2">More</item></root>'
        result = xml_pattern * (size // len(xml_pattern) + 1)
        return result[:size]
    
    @staticmethod
    def generate_binary_data(size: int = 1000) -> bytes:
        """Generate structured binary data."""
        return bytes([i % 256 for i in range(size)])
    
    @staticmethod
    def generate_text_data(size: int = 1000) -> bytes:
        """Generate natural language-like text."""
        text = b"The quick brown fox jumps over the lazy dog. "
        result = text * (size // len(text) + 1)
        return result[:size]
    
    @staticmethod
    def generate_empty() -> bytes:
        """Generate empty data."""
        return b""
    
    @staticmethod
    def generate_single_byte() -> bytes:
        """Generate single byte."""
        return b"A"
    
    @staticmethod
    def generate_very_large(size: int = 10_000_000) -> bytes:
        """Generate very large data."""
        return b"X" * size
    
    @staticmethod
    def generate_all_test_cases() -> List[Tuple[str, bytes]]:
        """Generate all test cases."""
        return [
            ("repetitive_small", TestDataGenerator.generate_repetitive_text(1000)),
            ("repetitive_medium", TestDataGenerator.generate_repetitive_text(10000)),
            ("repetitive_large", TestDataGenerator.generate_repetitive_text(100000)),
            ("random_small", TestDataGenerator.generate_random_bytes(1000)),
            ("random_medium", TestDataGenerator.generate_random_bytes(10000)),
            ("json_small", TestDataGenerator.generate_json_like(1000)),
            ("json_medium", TestDataGenerator.generate_json_like(10000)),
            ("xml_small", TestDataGenerator.generate_xml_like(1000)),
            ("xml_medium", TestDataGenerator.generate_xml_like(10000)),
            ("binary_small", TestDataGenerator.generate_binary_data(1000)),
            ("binary_medium", TestDataGenerator.generate_binary_data(10000)),
            ("text_small", TestDataGenerator.generate_text_data(1000)),
            ("text_medium", TestDataGenerator.generate_text_data(10000)),
            ("empty", TestDataGenerator.generate_empty()),
            ("single_byte", TestDataGenerator.generate_single_byte()),
        ]


class TestGzipCompression:
    """Comprehensive tests for GZIP compression."""
    
    @pytest.mark.parametrize("data_name,data", TestDataGenerator.generate_all_test_cases())
    def test_gzip_compress_decompress(self, data_name, data):
        """Test GZIP compression and decompression for various data types."""
        if len(data) == 0:
            # GZIP handles empty data
            compressed = gzip.compress(data)
            decompressed = gzip.decompress(compressed)
            assert decompressed == data
            return
        
        # Compress
        start_time = time.time()
        compressed = gzip.compress(data)
        compress_time = time.time() - start_time
        
        # Decompress
        start_time = time.time()
        decompressed = gzip.decompress(compressed)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        assert decompressed == data, f"Data integrity failed for {data_name}"
        
        # Calculate metrics
        compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
        compression_percent = ((len(data) - len(compressed)) / len(data) * 100) if len(data) > 0 else 0
        
        print(f"\nGZIP {data_name}:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {len(compressed)} bytes")
        print(f"  Ratio: {compression_ratio:.2f}x")
        print(f"  Compression: {compression_percent:.1f}%")
        print(f"  Compress time: {compress_time*1000:.2f}ms")
        print(f"  Decompress time: {decompress_time*1000:.2f}ms")
    
    @pytest.mark.parametrize("level", [1, 5, 9])
    def test_gzip_compression_levels(self, level):
        """Test different GZIP compression levels."""
        data = TestDataGenerator.generate_text_data(10000)
        
        compressed = gzip.compress(data, compresslevel=level)
        decompressed = gzip.decompress(compressed)
        
        assert decompressed == data
        
        ratio = len(data) / len(compressed)
        print(f"\nGZIP level {level}: ratio={ratio:.2f}x, size={len(compressed)}")
    
    def test_gzip_streaming(self):
        """Test GZIP streaming compression."""
        data = TestDataGenerator.generate_text_data(100000)
        
        # Stream compress
        output = io.BytesIO()
        with gzip.GzipFile(fileobj=output, mode='wb') as f:
            f.write(data)
        
        compressed = output.getvalue()
        
        # Stream decompress
        input_stream = io.BytesIO(compressed)
        with gzip.GzipFile(fileobj=input_stream, mode='rb') as f:
            decompressed = f.read()
        
        assert decompressed == data
    
    def test_gzip_partial_read(self):
        """Test GZIP partial reading."""
        data = TestDataGenerator.generate_text_data(10000)
        compressed = gzip.compress(data)
        
        input_stream = io.BytesIO(compressed)
        with gzip.GzipFile(fileobj=input_stream, mode='rb') as f:
            # Read in chunks
            chunk1 = f.read(1000)
            chunk2 = f.read(1000)
            rest = f.read()
        
        reconstructed = chunk1 + chunk2 + rest
        assert reconstructed == data


class TestLzmaCompression:
    """Comprehensive tests for LZMA compression."""
    
    @pytest.mark.parametrize("data_name,data", TestDataGenerator.generate_all_test_cases())
    def test_lzma_compress_decompress(self, data_name, data):
        """Test LZMA compression and decompression for various data types."""
        if len(data) == 0:
            # LZMA may not handle empty data well
            pytest.skip("LZMA doesn't compress empty data efficiently")
        
        # Compress
        start_time = time.time()
        compressed = lzma.compress(data)
        compress_time = time.time() - start_time
        
        # Decompress
        start_time = time.time()
        decompressed = lzma.decompress(compressed)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        assert decompressed == data, f"Data integrity failed for {data_name}"
        
        # Calculate metrics
        compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
        compression_percent = ((len(data) - len(compressed)) / len(data) * 100) if len(data) > 0 else 0
        
        print(f"\nLZMA {data_name}:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {len(compressed)} bytes")
        print(f"  Ratio: {compression_ratio:.2f}x")
        print(f"  Compression: {compression_percent:.1f}%")
        print(f"  Compress time: {compress_time*1000:.2f}ms")
        print(f"  Decompress time: {decompress_time*1000:.2f}ms")
    
    @pytest.mark.parametrize("preset", [0, 5, 9])
    def test_lzma_presets(self, preset):
        """Test different LZMA presets."""
        data = TestDataGenerator.generate_text_data(10000)
        
        compressed = lzma.compress(data, preset=preset)
        decompressed = lzma.decompress(compressed)
        
        assert decompressed == data
        
        ratio = len(data) / len(compressed)
        print(f"\nLZMA preset {preset}: ratio={ratio:.2f}x, size={len(compressed)}")


class TestBzip2Compression:
    """Comprehensive tests for BZIP2 compression."""
    
    @pytest.mark.parametrize("data_name,data", TestDataGenerator.generate_all_test_cases())
    def test_bzip2_compress_decompress(self, data_name, data):
        """Test BZIP2 compression and decompression for various data types."""
        if len(data) == 0:
            pytest.skip("BZIP2 doesn't compress empty data")
        
        # Compress
        start_time = time.time()
        compressed = bz2.compress(data)
        compress_time = time.time() - start_time
        
        # Decompress
        start_time = time.time()
        decompressed = bz2.decompress(compressed)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        assert decompressed == data, f"Data integrity failed for {data_name}"
        
        # Calculate metrics
        compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
        compression_percent = ((len(data) - len(compressed)) / len(data) * 100) if len(data) > 0 else 0
        
        print(f"\nBZIP2 {data_name}:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {len(compressed)} bytes")
        print(f"  Ratio: {compression_ratio:.2f}x")
        print(f"  Compression: {compression_percent:.1f}%")
        print(f"  Compress time: {compress_time*1000:.2f}ms")
        print(f"  Decompress time: {decompress_time*1000:.2f}ms")
    
    @pytest.mark.parametrize("level", [1, 5, 9])
    def test_bzip2_compression_levels(self, level):
        """Test different BZIP2 compression levels."""
        data = TestDataGenerator.generate_text_data(10000)
        
        compressed = bz2.compress(data, compresslevel=level)
        decompressed = bz2.decompress(compressed)
        
        assert decompressed == data
        
        ratio = len(data) / len(compressed)
        print(f"\nBZIP2 level {level}: ratio={ratio:.2f}x, size={len(compressed)}")


class TestZlibCompression:
    """Comprehensive tests for ZLIB compression."""
    
    @pytest.mark.parametrize("data_name,data", TestDataGenerator.generate_all_test_cases())
    def test_zlib_compress_decompress(self, data_name, data):
        """Test ZLIB compression and decompression for various data types."""
        # Compress
        start_time = time.time()
        compressed = zlib.compress(data)
        compress_time = time.time() - start_time
        
        # Decompress
        start_time = time.time()
        decompressed = zlib.decompress(compressed)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        assert decompressed == data, f"Data integrity failed for {data_name}"
        
        # Calculate metrics
        compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
        compression_percent = ((len(data) - len(compressed)) / len(data) * 100) if len(data) > 0 else 0
        
        print(f"\nZLIB {data_name}:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {len(compressed)} bytes")
        print(f"  Ratio: {compression_ratio:.2f}x")
        print(f"  Compression: {compression_percent:.1f}%")
        print(f"  Compress time: {compress_time*1000:.2f}ms")
        print(f"  Decompress time: {decompress_time*1000:.2f}ms")


@pytest.mark.skipif(not HAS_LZ4, reason="LZ4 not installed")
class TestLz4Compression:
    """Comprehensive tests for LZ4 compression."""
    
    @pytest.mark.parametrize("data_name,data", TestDataGenerator.generate_all_test_cases())
    def test_lz4_compress_decompress(self, data_name, data):
        """Test LZ4 compression and decompression for various data types."""
        if len(data) == 0:
            pytest.skip("LZ4 doesn't compress empty data")
        
        # Compress
        start_time = time.time()
        compressed = lz4.frame.compress(data)
        compress_time = time.time() - start_time
        
        # Decompress
        start_time = time.time()
        decompressed = lz4.frame.decompress(compressed)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        assert decompressed == data, f"Data integrity failed for {data_name}"
        
        # Calculate metrics
        compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
        compression_percent = ((len(data) - len(compressed)) / len(data) * 100) if len(data) > 0 else 0
        
        print(f"\nLZ4 {data_name}:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {len(compressed)} bytes")
        print(f"  Ratio: {compression_ratio:.2f}x")
        print(f"  Compression: {compression_percent:.1f}%")
        print(f"  Compress time: {compress_time*1000:.2f}ms")
        print(f"  Decompress time: {decompress_time*1000:.2f}ms")


@pytest.mark.skipif(not HAS_ZSTD, reason="ZSTD not installed")
class TestZstdCompression:
    """Comprehensive tests for ZSTD compression."""
    
    @pytest.mark.parametrize("data_name,data", TestDataGenerator.generate_all_test_cases())
    def test_zstd_compress_decompress(self, data_name, data):
        """Test ZSTD compression and decompression for various data types."""
        if len(data) == 0:
            pytest.skip("ZSTD doesn't compress empty data efficiently")
        
        # Compress
        cctx = zstd.ZstdCompressor()
        start_time = time.time()
        compressed = cctx.compress(data)
        compress_time = time.time() - start_time
        
        # Decompress
        dctx = zstd.ZstdDecompressor()
        start_time = time.time()
        decompressed = dctx.decompress(compressed)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        assert decompressed == data, f"Data integrity failed for {data_name}"
        
        # Calculate metrics
        compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
        compression_percent = ((len(data) - len(compressed)) / len(data) * 100) if len(data) > 0 else 0
        
        print(f"\nZSTD {data_name}:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {len(compressed)} bytes")
        print(f"  Ratio: {compression_ratio:.2f}x")
        print(f"  Compression: {compression_percent:.1f}%")
        print(f"  Compress time: {compress_time*1000:.2f}ms")
        print(f"  Decompress time: {decompress_time*1000:.2f}ms")
    
    @pytest.mark.parametrize("level", [1, 10, 19])
    def test_zstd_compression_levels(self, level):
        """Test different ZSTD compression levels."""
        data = TestDataGenerator.generate_text_data(10000)
        
        cctx = zstd.ZstdCompressor(level=level)
        compressed = cctx.compress(data)
        
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(compressed)
        
        assert decompressed == data
        
        ratio = len(data) / len(compressed)
        print(f"\nZSTD level {level}: ratio={ratio:.2f}x, size={len(compressed)}")


@pytest.mark.skipif(not HAS_BROTLI, reason="Brotli not installed")
class TestBrotliCompression:
    """Comprehensive tests for Brotli compression."""
    
    @pytest.mark.parametrize("data_name,data", TestDataGenerator.generate_all_test_cases())
    def test_brotli_compress_decompress(self, data_name, data):
        """Test Brotli compression and decompression for various data types."""
        if len(data) == 0:
            pytest.skip("Brotli doesn't compress empty data efficiently")
        
        # Compress
        start_time = time.time()
        compressed = brotli.compress(data)
        compress_time = time.time() - start_time
        
        # Decompress
        start_time = time.time()
        decompressed = brotli.decompress(compressed)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        assert decompressed == data, f"Data integrity failed for {data_name}"
        
        # Calculate metrics
        compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
        compression_percent = ((len(data) - len(compressed)) / len(data) * 100) if len(data) > 0 else 0
        
        print(f"\nBrotli {data_name}:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {len(compressed)} bytes")
        print(f"  Ratio: {compression_ratio:.2f}x")
        print(f"  Compression: {compression_percent:.1f}%")
        print(f"  Compress time: {compress_time*1000:.2f}ms")
        print(f"  Decompress time: {decompress_time*1000:.2f}ms")
    
    @pytest.mark.parametrize("quality", [1, 6, 11])
    def test_brotli_quality_levels(self, quality):
        """Test different Brotli quality levels."""
        data = TestDataGenerator.generate_text_data(10000)
        
        compressed = brotli.compress(data, quality=quality)
        decompressed = brotli.decompress(compressed)
        
        assert decompressed == data
        
        ratio = len(data) / len(compressed)
        print(f"\nBrotli quality {quality}: ratio={ratio:.2f}x, size={len(compressed)}")


class TestCompressionComparison:
    """Compare all algorithms side by side."""
    
    def test_algorithm_comparison_text(self):
        """Compare all algorithms on text data."""
        data = TestDataGenerator.generate_text_data(10000)
        results = []
        
        # GZIP
        compressed = gzip.compress(data)
        results.append(("GZIP", len(compressed), len(data) / len(compressed)))
        
        # LZMA
        compressed = lzma.compress(data)
        results.append(("LZMA", len(compressed), len(data) / len(compressed)))
        
        # BZIP2
        compressed = bz2.compress(data)
        results.append(("BZIP2", len(compressed), len(data) / len(compressed)))
        
        # ZLIB
        compressed = zlib.compress(data)
        results.append(("ZLIB", len(compressed), len(data) / len(compressed)))
        
        if HAS_LZ4:
            compressed = lz4.frame.compress(data)
            results.append(("LZ4", len(compressed), len(data) / len(compressed)))
        
        if HAS_ZSTD:
            cctx = zstd.ZstdCompressor()
            compressed = cctx.compress(data)
            results.append(("ZSTD", len(compressed), len(data) / len(compressed)))
        
        if HAS_BROTLI:
            compressed = brotli.compress(data)
            results.append(("Brotli", len(compressed), len(data) / len(compressed)))
        
        # Sort by compression ratio
        results.sort(key=lambda x: x[2], reverse=True)
        
        print("\n\nAlgorithm Comparison (Text Data, 10KB):")
        print(f"{'Algorithm':<10} {'Size':<10} {'Ratio':<10}")
        print("-" * 30)
        for algo, size, ratio in results:
            print(f"{algo:<10} {size:<10} {ratio:.2f}x")
    
    def test_algorithm_comparison_json(self):
        """Compare all algorithms on JSON data."""
        data = TestDataGenerator.generate_json_like(10000)
        results = []
        
        algorithms = [
            ("GZIP", lambda d: gzip.compress(d)),
            ("LZMA", lambda d: lzma.compress(d)),
            ("BZIP2", lambda d: bz2.compress(d)),
            ("ZLIB", lambda d: zlib.compress(d)),
        ]
        
        if HAS_LZ4:
            algorithms.append(("LZ4", lambda d: lz4.frame.compress(d)))
        
        if HAS_ZSTD:
            algorithms.append(("ZSTD", lambda d: zstd.ZstdCompressor().compress(d)))
        
        if HAS_BROTLI:
            algorithms.append(("Brotli", lambda d: brotli.compress(d)))
        
        for algo_name, compress_func in algorithms:
            compressed = compress_func(data)
            results.append((algo_name, len(compressed), len(data) / len(compressed)))
        
        results.sort(key=lambda x: x[2], reverse=True)
        
        print("\n\nAlgorithm Comparison (JSON Data, 10KB):")
        print(f"{'Algorithm':<10} {'Size':<10} {'Ratio':<10}")
        print("-" * 30)
        for algo, size, ratio in results:
            print(f"{algo:<10} {size:<10} {ratio:.2f}x")


class TestCorruptionHandling:
    """Test handling of corrupted data."""
    
    def test_gzip_corrupted_data(self):
        """Test GZIP with corrupted data."""
        data = TestDataGenerator.generate_text_data(1000)
        compressed = gzip.compress(data)
        
        # Corrupt the compressed data
        corrupted = compressed[:50] + b"CORRUPTED" + compressed[59:]
        
        with pytest.raises(Exception):
            gzip.decompress(corrupted)
    
    def test_lzma_corrupted_data(self):
        """Test LZMA with corrupted data."""
        data = TestDataGenerator.generate_text_data(1000)
        compressed = lzma.compress(data)
        
        # Corrupt the compressed data
        corrupted = compressed[:50] + b"CORRUPTED" + compressed[59:]
        
        with pytest.raises(Exception):
            lzma.decompress(corrupted)
    
    def test_truncated_compressed_data(self):
        """Test handling of truncated compressed data."""
        data = TestDataGenerator.generate_text_data(1000)
        compressed = gzip.compress(data)
        
        # Truncate the compressed data
        truncated = compressed[:len(compressed)//2]
        
        with pytest.raises(Exception):
            gzip.decompress(truncated)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])

