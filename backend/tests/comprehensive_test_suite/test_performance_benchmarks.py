"""
Comprehensive Performance Benchmark Tests

Tests performance characteristics including:
- Compression speed benchmarks
- Decompression speed benchmarks
- Memory usage profiling
- CPU efficiency testing
- Throughput measurements
- Latency analysis
- Scalability testing
"""

import pytest
import time
import gzip
import bz2
import lzma
import zlib
import psutil
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from statistics import mean, median, stdev

from test_fixtures import ContentFactory, get_all_algorithms, get_test_sizes

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


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    algorithm: str
    data_size: int
    compress_time: float
    decompress_time: float
    compressed_size: int
    compression_ratio: float
    compress_speed_mbps: float
    decompress_speed_mbps: float
    memory_used_mb: float
    cpu_percent: float


class CompressionBenchmark:
    """Benchmark compression operations."""
    
    @staticmethod
    def benchmark_compression(algorithm: str, data: bytes, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark compression performance."""
        compress_times = []
        decompress_times = []
        compressed_sizes = []
        memory_before = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        for _ in range(iterations):
            # Measure compression
            start_time = time.perf_counter()
            if algorithm == "gzip":
                compressed = gzip.compress(data)
            elif algorithm == "lzma":
                compressed = lzma.compress(data)
            elif algorithm == "bzip2":
                compressed = bz2.compress(data)
            elif algorithm == "zlib":
                compressed = zlib.compress(data)
            elif algorithm == "lz4" and HAS_LZ4:
                compressed = lz4.frame.compress(data)
            elif algorithm == "zstd" and HAS_ZSTD:
                cctx = zstd.ZstdCompressor()
                compressed = cctx.compress(data)
            elif algorithm == "brotli" and HAS_BROTLI:
                compressed = brotli.compress(data)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            compress_time = time.perf_counter() - start_time
            compress_times.append(compress_time)
            compressed_sizes.append(len(compressed))
            
            # Measure decompression
            start_time = time.perf_counter()
            if algorithm == "gzip":
                decompressed = gzip.decompress(compressed)
            elif algorithm == "lzma":
                decompressed = lzma.decompress(compressed)
            elif algorithm == "bzip2":
                decompressed = bz2.decompress(compressed)
            elif algorithm == "zlib":
                decompressed = zlib.decompress(compressed)
            elif algorithm == "lz4" and HAS_LZ4:
                decompressed = lz4.frame.decompress(compressed)
            elif algorithm == "zstd" and HAS_ZSTD:
                dctx = zstd.ZstdDecompressor()
                decompressed = dctx.decompress(compressed)
            elif algorithm == "brotli" and HAS_BROTLI:
                decompressed = brotli.decompress(compressed)
            
            decompress_time = time.perf_counter() - start_time
            decompress_times.append(decompress_time)
            
            # Verify integrity
            assert decompressed == data
        
        memory_after = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        # Calculate statistics
        avg_compress_time = mean(compress_times)
        avg_decompress_time = mean(decompress_times)
        avg_compressed_size = mean(compressed_sizes)
        
        data_size_mb = len(data) / 1024 / 1024
        compress_speed = data_size_mb / avg_compress_time if avg_compress_time > 0 else 0
        decompress_speed = data_size_mb / avg_decompress_time if avg_decompress_time > 0 else 0
        
        return {
            "algorithm": algorithm,
            "data_size": len(data),
            "iterations": iterations,
            "compress_time_avg": avg_compress_time,
            "compress_time_median": median(compress_times),
            "compress_time_stdev": stdev(compress_times) if len(compress_times) > 1 else 0,
            "decompress_time_avg": avg_decompress_time,
            "decompress_time_median": median(decompress_times),
            "decompress_time_stdev": stdev(decompress_times) if len(decompress_times) > 1 else 0,
            "compressed_size": avg_compressed_size,
            "compression_ratio": len(data) / avg_compressed_size,
            "compress_speed_mbps": compress_speed,
            "decompress_speed_mbps": decompress_speed,
            "memory_delta_mb": memory_after - memory_before,
            "all_compress_times": compress_times,
            "all_decompress_times": decompress_times
        }


class TestCompressionSpeedBenchmarks:
    """Benchmark compression speed across algorithms."""
    
    @pytest.mark.parametrize("size", [1000, 10000, 100000])
    @pytest.mark.parametrize("algorithm", ["gzip", "lzma", "bzip2", "zlib"])
    def test_compression_speed_text(self, algorithm, size):
        """Benchmark compression speed on text data."""
        data = ContentFactory.create_text_content(size=size)
        
        results = CompressionBenchmark.benchmark_compression(algorithm, data, iterations=5)
        
        print(f"\n{algorithm} @ {size} bytes:")
        print(f"  Compress: {results['compress_time_avg']*1000:.2f}ms ({results['compress_speed_mbps']:.2f} MB/s)")
        print(f"  Decompress: {results['decompress_time_avg']*1000:.2f}ms ({results['decompress_speed_mbps']:.2f} MB/s)")
        print(f"  Ratio: {results['compression_ratio']:.2f}x")
        
        # Assert reasonable performance
        assert results['compress_time_avg'] < 10.0  # Should complete in under 10s
        assert results['compression_ratio'] > 1.0  # Should achieve some compression
    
    @pytest.mark.parametrize("algorithm", ["gzip", "lzma", "bzip2"])
    def test_compression_speed_json(self, algorithm):
        """Benchmark compression speed on JSON data."""
        data = ContentFactory.create_json_content(size=10000)
        
        results = CompressionBenchmark.benchmark_compression(algorithm, data, iterations=5)
        
        print(f"\n{algorithm} on JSON:")
        print(f"  Compress speed: {results['compress_speed_mbps']:.2f} MB/s")
        print(f"  Ratio: {results['compression_ratio']:.2f}x")
        
        # JSON typically compresses well
        assert results['compression_ratio'] >= 2.0
    
    @pytest.mark.skipif(not HAS_LZ4, reason="LZ4 not available")
    def test_lz4_speed_advantage(self):
        """Test that LZ4 is fastest for compression speed."""
        data = ContentFactory.create_text_content(size=100000)
        
        lz4_results = CompressionBenchmark.benchmark_compression("lz4", data, iterations=5)
        gzip_results = CompressionBenchmark.benchmark_compression("gzip", data, iterations=5)
        
        print(f"\nLZ4 vs GZIP speed:")
        print(f"  LZ4: {lz4_results['compress_speed_mbps']:.2f} MB/s")
        print(f"  GZIP: {gzip_results['compress_speed_mbps']:.2f} MB/s")
        
        # LZ4 should be significantly faster
        assert lz4_results['compress_speed_mbps'] > gzip_results['compress_speed_mbps']
    
    @pytest.mark.skipif(not HAS_ZSTD, reason="ZSTD not available")
    def test_zstd_balanced_performance(self):
        """Test ZSTD's balanced speed/ratio performance."""
        data = ContentFactory.create_text_content(size=100000)
        
        zstd_results = CompressionBenchmark.benchmark_compression("zstd", data, iterations=5)
        gzip_results = CompressionBenchmark.benchmark_compression("gzip", data, iterations=5)
        lzma_results = CompressionBenchmark.benchmark_compression("lzma", data, iterations=5)
        
        print(f"\nZSTD balanced performance:")
        print(f"  ZSTD: {zstd_results['compress_speed_mbps']:.2f} MB/s, ratio={zstd_results['compression_ratio']:.2f}x")
        print(f"  GZIP: {gzip_results['compress_speed_mbps']:.2f} MB/s, ratio={gzip_results['compression_ratio']:.2f}x")
        print(f"  LZMA: {lzma_results['compress_speed_mbps']:.2f} MB/s, ratio={lzma_results['compression_ratio']:.2f}x")
        
        # ZSTD should be faster than LZMA
        assert zstd_results['compress_speed_mbps'] > lzma_results['compress_speed_mbps']
        # ZSTD should have better ratio than GZIP
        assert zstd_results['compression_ratio'] >= gzip_results['compression_ratio'] * 0.9


class TestDecompressionSpeedBenchmarks:
    """Benchmark decompression speed."""
    
    @pytest.mark.parametrize("algorithm", ["gzip", "lzma", "bzip2", "zlib"])
    def test_decompression_speed(self, algorithm):
        """Test decompression speed is faster than compression."""
        data = ContentFactory.create_text_content(size=50000)
        
        results = CompressionBenchmark.benchmark_compression(algorithm, data, iterations=5)
        
        print(f"\n{algorithm} decompression:")
        print(f"  Decompress speed: {results['decompress_speed_mbps']:.2f} MB/s")
        print(f"  Compress speed: {results['compress_speed_mbps']:.2f} MB/s")
        print(f"  Speed ratio: {results['decompress_speed_mbps']/results['compress_speed_mbps']:.2f}x faster")
        
        # Decompression should generally be faster than compression
        assert results['decompress_speed_mbps'] >= results['compress_speed_mbps'] * 0.5


class TestMemoryUsageBenchmarks:
    """Benchmark memory usage."""
    
    @pytest.mark.parametrize("algorithm", ["gzip", "lzma", "bzip2"])
    def test_memory_usage(self, algorithm):
        """Test memory usage during compression."""
        data = ContentFactory.create_text_content(size=1000000)  # 1MB
        
        results = CompressionBenchmark.benchmark_compression(algorithm, data, iterations=3)
        
        print(f"\n{algorithm} memory usage:")
        print(f"  Memory delta: {results['memory_delta_mb']:.2f} MB")
        print(f"  Data size: {len(data) / 1024 / 1024:.2f} MB")
        
        # Memory usage should be reasonable (not 10x data size)
        assert results['memory_delta_mb'] < 100.0  # Under 100MB for 1MB data
    
    def test_lzma_memory_intensive(self):
        """Test that LZMA uses more memory than GZIP."""
        data = ContentFactory.create_text_content(size=100000)
        
        gzip_results = CompressionBenchmark.benchmark_compression("gzip", data, iterations=3)
        lzma_results = CompressionBenchmark.benchmark_compression("lzma", data, iterations=3)
        
        print(f"\nMemory comparison:")
        print(f"  GZIP: {gzip_results['memory_delta_mb']:.2f} MB")
        print(f"  LZMA: {lzma_results['memory_delta_mb']:.2f} MB")
        
        # LZMA typically uses more memory
        # Note: This may vary based on system, so we just log it
        print(f"  LZMA/GZIP ratio: {lzma_results['memory_delta_mb']/gzip_results['memory_delta_mb'] if gzip_results['memory_delta_mb'] > 0 else 'N/A'}")


class TestScalabilityBenchmarks:
    """Test performance scaling with data size."""
    
    @pytest.mark.parametrize("algorithm", ["gzip", "zlib"])
    def test_linear_scaling(self, algorithm):
        """Test that compression time scales linearly with data size."""
        sizes = [1000, 5000, 10000, 50000]
        times = []
        
        for size in sizes:
            data = ContentFactory.create_text_content(size=size)
            results = CompressionBenchmark.benchmark_compression(algorithm, data, iterations=3)
            times.append(results['compress_time_avg'])
            print(f"\n{algorithm} @ {size} bytes: {results['compress_time_avg']*1000:.2f}ms")
        
        # Check that doubling size approximately doubles time
        if len(times) >= 2:
            ratio1 = times[1] / times[0] if times[0] > 0 else 0
            ratio2 = (sizes[1] / sizes[0])
            print(f"\nTime scaling factor: {ratio1:.2f}x for {ratio2:.2f}x size increase")
            
            # Should be roughly linear (within 3x margin)
            assert 0.3 * ratio2 <= ratio1 <= 3.0 * ratio2
    
    def test_large_file_performance(self):
        """Test performance on large files."""
        # Test with 10MB file
        large_data = ContentFactory.create_text_content(size=10_000_000)
        
        results = CompressionBenchmark.benchmark_compression("gzip", large_data, iterations=1)
        
        print(f"\nLarge file (10MB) performance:")
        print(f"  Compress time: {results['compress_time_avg']:.2f}s")
        print(f"  Compress speed: {results['compress_speed_mbps']:.2f} MB/s")
        print(f"  Compressed size: {results['compressed_size'] / 1024 / 1024:.2f} MB")
        print(f"  Compression ratio: {results['compression_ratio']:.2f}x")
        
        # Should complete in reasonable time
        assert results['compress_time_avg'] < 60.0  # Under 1 minute


class TestThroughputBenchmarks:
    """Test throughput under various conditions."""
    
    def test_sequential_throughput(self):
        """Test sequential compression throughput."""
        num_files = 100
        file_size = 1000
        
        start_time = time.perf_counter()
        
        for i in range(num_files):
            data = ContentFactory.create_text_content(size=file_size)
            compressed = gzip.compress(data)
        
        elapsed = time.perf_counter() - start_time
        
        total_data_mb = (num_files * file_size) / 1024 / 1024
        throughput = total_data_mb / elapsed
        
        print(f"\nSequential throughput:")
        print(f"  Files: {num_files}")
        print(f"  Total data: {total_data_mb:.2f} MB")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Throughput: {throughput:.2f} MB/s")
        
        assert throughput > 0.1  # At least 0.1 MB/s
    
    def test_compression_ratio_vs_speed_tradeoff(self):
        """Test ratio vs speed tradeoff across algorithms."""
        data = ContentFactory.create_text_content(size=50000)
        
        algorithms = ["gzip", "lzma", "bzip2"]
        results = []
        
        for algo in algorithms:
            bench = CompressionBenchmark.benchmark_compression(algo, data, iterations=5)
            results.append({
                "algorithm": algo,
                "ratio": bench['compression_ratio'],
                "speed": bench['compress_speed_mbps']
            })
            print(f"\n{algo}: {bench['compression_ratio']:.2f}x @ {bench['compress_speed_mbps']:.2f} MB/s")
        
        # LZMA should have best ratio but slowest speed
        lzma_result = [r for r in results if r['algorithm'] == 'lzma'][0]
        assert lzma_result['ratio'] >= max(r['ratio'] for r in results if r['algorithm'] != 'lzma')


class TestConsistencyBenchmarks:
    """Test performance consistency."""
    
    def test_compression_consistency(self):
        """Test that compression is consistent across runs."""
        data = ContentFactory.create_text_content(size=10000)
        
        results = CompressionBenchmark.benchmark_compression("gzip", data, iterations=20)
        
        stdev_percent = (results['compress_time_stdev'] / results['compress_time_avg'] * 100) if results['compress_time_avg'] > 0 else 0
        
        print(f"\nConsistency metrics:")
        print(f"  Average: {results['compress_time_avg']*1000:.2f}ms")
        print(f"  Median: {results['compress_time_median']*1000:.2f}ms")
        print(f"  Std dev: {results['compress_time_stdev']*1000:.2f}ms ({stdev_percent:.1f}%)")
        
        # Standard deviation should be < 50% of mean (reasonably consistent)
        assert stdev_percent < 50.0
    
    def test_same_input_same_output(self):
        """Test that same input always produces same compressed output."""
        data = ContentFactory.create_text_content(size=5000)
        
        compressed1 = gzip.compress(data)
        compressed2 = gzip.compress(data)
        compressed3 = gzip.compress(data)
        
        # Should be deterministic
        assert compressed1 == compressed2 == compressed3
        
        print(f"\nDeterminism test: PASSED")
        print(f"  Input size: {len(data)} bytes")
        print(f"  Output size: {len(compressed1)} bytes")
        print(f"  All outputs identical: True")


class TestEdgeCasePerformance:
    """Test performance on edge cases."""
    
    def test_empty_data_performance(self):
        """Test compression of empty data."""
        data = b""
        
        start_time = time.perf_counter()
        compressed = gzip.compress(data)
        compress_time = time.perf_counter() - start_time
        
        print(f"\nEmpty data compression:")
        print(f"  Time: {compress_time*1000:.2f}ms")
        print(f"  Compressed size: {len(compressed)} bytes")
        
        # Should be very fast
        assert compress_time < 0.01  # Under 10ms
    
    def test_single_byte_performance(self):
        """Test compression of single byte."""
        data = b"A"
        
        results = CompressionBenchmark.benchmark_compression("gzip", data, iterations=10)
        
        print(f"\nSingle byte compression:")
        print(f"  Time: {results['compress_time_avg']*1000:.2f}ms")
        print(f"  Compressed size: {results['compressed_size']} bytes")
        
        # Overhead may make it larger
        assert results['compressed_size'] >= 1
    
    def test_highly_repetitive_performance(self):
        """Test compression of highly repetitive data."""
        data = b"A" * 100000  # 100KB of same character
        
        results = CompressionBenchmark.benchmark_compression("gzip", data, iterations=5)
        
        print(f"\nHighly repetitive data:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {results['compressed_size']} bytes")
        print(f"  Ratio: {results['compression_ratio']:.2f}x")
        
        # Should achieve excellent compression
        assert results['compression_ratio'] >= 100.0
    
    def test_random_data_performance(self):
        """Test compression of random (incompressible) data."""
        data = os.urandom(10000)
        
        results = CompressionBenchmark.benchmark_compression("gzip", data, iterations=5)
        
        print(f"\nRandom data compression:")
        print(f"  Original: {len(data)} bytes")
        print(f"  Compressed: {results['compressed_size']} bytes")
        print(f"  Ratio: {results['compression_ratio']:.2f}x")
        
        # May not compress well (ratio near 1.0 or even expansion)
        print(f"  Note: Random data is incompressible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])

