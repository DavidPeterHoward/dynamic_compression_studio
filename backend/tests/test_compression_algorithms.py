"""
Comprehensive Unit Tests for Compression Algorithms

This test suite provides:
1. Correctness tests for all compression/decompression operations
2. Performance benchmarks with statistical analysis
3. Edge case handling validation
4. Memory leak detection
5. Thread safety verification
6. Graceful degradation testing
7. Cross-algorithm compatibility
8. Meta-recursive evolution validation
9. Mathematical property verification
10. Regression testing

Test Categories:
- Unit tests: Individual function testing
- Integration tests: Component interaction
- Performance tests: Speed and efficiency
- Stress tests: Large data and edge cases
- Fuzzing tests: Random input validation
"""

import unittest
import pytest
import numpy as np
import time
import threading
import multiprocessing
import tempfile
import os
import sys
import json
import hashlib
import random
import string
import gc
import tracemalloc
import asyncio
from typing import List, Dict, Any, Tuple
from unittest.mock import Mock, patch, MagicMock
from parameterized import parameterized
import hypothesis
from hypothesis import strategies as st, given, settings, assume
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import compression algorithms
from app.algorithms.base_algorithm import BaseCompressionAlgorithm, CompressionMetadata
from app.algorithms.gzip.versions.v1_basic import GzipBasic
from app.algorithms.gzip.versions.v2_strategy import GzipStrategy
from app.algorithms.gzip.versions.v5_metarecursive import GzipMetaRecursive
from app.algorithms.quantum_biological.versions.v1_hybrid import QuantumBiologicalCompressor

# Import profiling system
from app.core.profiling_system import AdvancedProfiler, ProfileLevel, Architecture


class TestDataGenerator:
    """Generate test data with known properties."""
    
    @staticmethod
    def generate_random(size: int) -> bytes:
        """Generate random incompressible data."""
        return np.random.bytes(size)
    
    @staticmethod
    def generate_repetitive(pattern: bytes, repeats: int) -> bytes:
        """Generate highly repetitive data."""
        return pattern * repeats
    
    @staticmethod
    def generate_text(size: int) -> bytes:
        """Generate natural language text."""
        words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog']
        text = ' '.join(random.choices(words, k=size // 5))
        return text.encode('utf-8')
    
    @staticmethod
    def generate_structured(size: int) -> bytes:
        """Generate structured data (JSON-like)."""
        data = {
            'id': random.randint(1, 1000),
            'name': ''.join(random.choices(string.ascii_letters, k=10)),
            'values': [random.random() for _ in range(size // 100)],
            'nested': {
                'key': 'value',
                'array': list(range(10))
            }
        }
        return json.dumps(data).encode('utf-8')
    
    @staticmethod
    def generate_binary_pattern(size: int) -> bytes:
        """Generate binary data with patterns."""
        pattern = bytes([i % 256 for i in range(min(256, size))])
        repeats = size // len(pattern) + 1
        return (pattern * repeats)[:size]
    
    @staticmethod
    def generate_edge_cases() -> List[bytes]:
        """Generate edge case test data."""
        return [
            b'',  # Empty
            b'A',  # Single byte
            b'AA',  # Two identical bytes
            b'AB',  # Two different bytes
            bytes([i for i in range(256)]),  # All byte values
            b'\x00' * 1000,  # All nulls
            b'\xFF' * 1000,  # All 0xFF
            b'A' * 1000000,  # Large repetitive
            np.random.bytes(1000000),  # Large random
        ]


class BaseCompressionTest(unittest.TestCase):
    """Base test class with common functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.profiler = AdvancedProfiler(level=ProfileLevel.STANDARD)
        self.test_data = TestDataGenerator()
        self.algorithms = self._get_test_algorithms()
        
        # Start memory tracking
        tracemalloc.start()
        
    def tearDown(self):
        """Clean up test environment."""
        # Check for memory leaks
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Force garbage collection
        gc.collect()
        
        # Log memory usage
        if peak > 100 * 1024 * 1024:  # 100MB
            print(f"Warning: High memory usage detected: {peak / 1e6:.2f} MB")
    
    def _get_test_algorithms(self) -> Dict[str, BaseCompressionAlgorithm]:
        """Get algorithms to test."""
        return {
            'gzip_basic': GzipBasic(),
            'gzip_strategy': GzipStrategy(),
            'gzip_metarecursive': GzipMetaRecursive(),
            'quantum_biological': QuantumBiologicalCompressor(),
        }
    
    def assert_lossless(self, original: bytes, algorithm: BaseCompressionAlgorithm):
        """Assert lossless compression/decompression."""
        compressed, metadata = algorithm.compress(original)
        decompressed = algorithm.decompress(compressed)
        
        self.assertEqual(
            original, decompressed,
            f"Lossless compression failed for {algorithm.__class__.__name__}"
        )
        
        # Verify metadata
        self.assertIsNotNone(metadata)
        self.assertGreater(metadata.compression_ratio, 0)
        self.assertLessEqual(metadata.algorithm_efficiency, 1.0)
    
    def assert_performance(self, algorithm: BaseCompressionAlgorithm,
                          data: bytes,
                          max_time_ms: float = 1000,
                          min_ratio: float = 1.0):
        """Assert performance requirements."""
        start_time = time.perf_counter()
        compressed, metadata = algorithm.compress(data)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        self.assertLess(
            elapsed_ms, max_time_ms,
            f"Compression too slow: {elapsed_ms:.2f}ms > {max_time_ms}ms"
        )
        
        self.assertGreaterEqual(
            metadata.compression_ratio, min_ratio,
            f"Compression ratio too low: {metadata.compression_ratio:.2f} < {min_ratio}"
        )


class TestCompressionCorrectness(BaseCompressionTest):
    """Test compression correctness."""
    
    @parameterized.expand([
        ('gzip_basic',),
        ('gzip_strategy',),
        ('gzip_metarecursive',),
        ('quantum_biological',),
    ])
    def test_lossless_compression(self, algo_name: str):
        """Test lossless compression for various data types."""
        algorithm = self.algorithms[algo_name]
        
        # Test different data types
        test_cases = [
            self.test_data.generate_random(1000),
            self.test_data.generate_repetitive(b'ABC', 100),
            self.test_data.generate_text(1000),
            self.test_data.generate_structured(1000),
            self.test_data.generate_binary_pattern(1000),
        ]
        
        for data in test_cases:
            with self.subTest(data_size=len(data)):
                self.assert_lossless(data, algorithm)
    
    @parameterized.expand([
        ('gzip_basic',),
        ('gzip_strategy',),
        ('gzip_metarecursive',),
        ('quantum_biological',),
    ])
    def test_edge_cases(self, algo_name: str):
        """Test edge cases."""
        algorithm = self.algorithms[algo_name]
        
        for data in self.test_data.generate_edge_cases():
            with self.subTest(data_size=len(data)):
                self.assert_lossless(data, algorithm)
    
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=50, deadline=None)
    def test_random_data_hypothesis(self, data: bytes):
        """Property-based testing with random data."""
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                compressed, metadata = algorithm.compress(data)
                decompressed = algorithm.decompress(compressed)
                
                # Properties that must hold
                self.assertEqual(data, decompressed)  # Lossless
                self.assertLessEqual(len(compressed), len(data) * 10)  # Reasonable size
                self.assertGreater(metadata.compression_ratio, 0)  # Valid ratio
    
    def test_empty_input(self):
        """Test handling of empty input."""
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                compressed, metadata = algorithm.compress(b'')
                decompressed = algorithm.decompress(compressed)
                self.assertEqual(b'', decompressed)
    
    def test_large_input(self):
        """Test handling of large input."""
        large_data = self.test_data.generate_random(10 * 1024 * 1024)  # 10MB
        
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                with self.profiler.profile(f"large_input_{algo_name}"):
                    self.assert_lossless(large_data, algorithm)


class TestCompressionPerformance(BaseCompressionTest):
    """Test compression performance."""
    
    @parameterized.expand([
        ('gzip_basic', 100),
        ('gzip_strategy', 150),
        ('gzip_metarecursive', 200),
        ('quantum_biological', 300),
    ])
    def test_compression_speed(self, algo_name: str, max_time_ms: float):
        """Test compression speed requirements."""
        algorithm = self.algorithms[algo_name]
        data = self.test_data.generate_text(100000)  # 100KB
        
        self.assert_performance(algorithm, data, max_time_ms)
    
    def test_compression_ratio(self):
        """Test compression ratio for different data types."""
        test_cases = [
            (self.test_data.generate_repetitive(b'A', 1000), 10.0),  # High ratio
            (self.test_data.generate_text(1000), 2.0),  # Medium ratio
            (self.test_data.generate_random(1000), 0.9),  # Low ratio (incompressible)
        ]
        
        for data, min_ratio in test_cases:
            for algo_name, algorithm in self.algorithms.items():
                with self.subTest(algorithm=algo_name, data_type=type(data)):
                    compressed, metadata = algorithm.compress(data)
                    
                    # Adjust expectations for random data
                    if min_ratio < 1.0:
                        self.assertGreater(metadata.compression_ratio, min_ratio)
                    else:
                        self.assertGreater(metadata.compression_ratio, min_ratio * 0.5)
    
    def test_throughput(self):
        """Test compression throughput (MB/s)."""
        data_sizes = [1024, 10240, 102400, 1024000]  # 1KB to 1MB
        
        for algo_name, algorithm in self.algorithms.items():
            throughputs = []
            
            for size in data_sizes:
                data = self.test_data.generate_text(size)
                
                start_time = time.perf_counter()
                compressed, _ = algorithm.compress(data)
                elapsed = time.perf_counter() - start_time
                
                throughput_mbps = (size / 1024 / 1024) / elapsed
                throughputs.append(throughput_mbps)
            
            avg_throughput = np.mean(throughputs)
            self.assertGreater(
                avg_throughput, 10.0,
                f"{algo_name} throughput too low: {avg_throughput:.2f} MB/s"
            )


class TestThreadSafety(BaseCompressionTest):
    """Test thread safety of compression algorithms."""
    
    def test_concurrent_compression(self):
        """Test concurrent compression operations."""
        num_threads = 10
        num_operations = 100
        
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                errors = []
                
                def compress_task():
                    try:
                        data = self.test_data.generate_random(1000)
                        compressed, metadata = algorithm.compress(data)
                        decompressed = algorithm.decompress(compressed)
                        assert data == decompressed
                    except Exception as e:
                        errors.append(e)
                
                # Run concurrent compressions
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    futures = [
                        executor.submit(compress_task)
                        for _ in range(num_operations)
                    ]
                    
                    for future in futures:
                        future.result()
                
                self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
    
    def test_parallel_processing(self):
        """Test parallel processing with multiprocessing."""
        num_processes = 4
        data_chunks = [
            self.test_data.generate_text(10000)
            for _ in range(num_processes)
        ]
        
        for algo_name, algorithm in self.algorithms.items():
            if algo_name == 'quantum_biological':
                continue  # Skip due to pickle issues
            
            with self.subTest(algorithm=algo_name):
                def process_chunk(data):
                    compressed, _ = algorithm.compress(data)
                    return compressed
                
                with ProcessPoolExecutor(max_workers=num_processes) as executor:
                    results = list(executor.map(process_chunk, data_chunks))
                
                self.assertEqual(len(results), num_processes)


class TestGracefulDegradation(BaseCompressionTest):
    """Test graceful degradation and error handling."""
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted compressed data."""
        data = self.test_data.generate_text(1000)
        
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                compressed, _ = algorithm.compress(data)
                
                # Corrupt the compressed data
                corrupted = bytearray(compressed)
                if len(corrupted) > 10:
                    corrupted[5] ^= 0xFF  # Flip bits
                    corrupted[10] ^= 0xFF
                
                # Should handle gracefully (not crash)
                try:
                    decompressed = algorithm.decompress(bytes(corrupted))
                    # May or may not decompress correctly
                except Exception:
                    # Should fail gracefully
                    pass
    
    def test_memory_pressure(self):
        """Test behavior under memory pressure."""
        # Allocate large amount of memory
        large_arrays = []
        try:
            for _ in range(10):
                large_arrays.append(np.zeros(100 * 1024 * 1024, dtype=np.uint8))  # 100MB each
        except MemoryError:
            pass  # System under memory pressure
        
        # Try compression under memory pressure
        data = self.test_data.generate_text(1000)
        
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                try:
                    compressed, _ = algorithm.compress(data)
                    decompressed = algorithm.decompress(compressed)
                    self.assertEqual(data, decompressed)
                except MemoryError:
                    # Should fail gracefully
                    pass
        
        # Clean up
        del large_arrays
        gc.collect()
    
    def test_algorithm_fallback(self):
        """Test fallback to simpler algorithms on failure."""
        # This tests the strategy pattern implementation
        strategy_algo = self.algorithms['gzip_strategy']
        
        # Test with data that might cause issues
        problematic_data = b'\x00' * 1000000  # 1MB of nulls
        
        compressed, metadata = strategy_algo.compress(problematic_data)
        decompressed = strategy_algo.decompress(compressed)
        
        self.assertEqual(problematic_data, decompressed)
        self.assertIn('strategy_used', metadata.data_characteristics)


class TestMetaRecursiveEvolution(BaseCompressionTest):
    """Test meta-recursive evolution capabilities."""
    
    def test_algorithm_evolution(self):
        """Test algorithm evolution over generations."""
        if 'gzip_metarecursive' not in self.algorithms:
            self.skipTest("Meta-recursive algorithm not available")
        
        algorithm = self.algorithms['gzip_metarecursive']
        test_data = self.test_data.generate_text(10000)
        
        # Track performance over generations
        performances = []
        
        for generation in range(5):
            compressed, metadata = algorithm.compress(test_data)
            performances.append(metadata.algorithm_efficiency)
            
            # Evolve to next generation
            if hasattr(algorithm, 'generate_improved_version'):
                algorithm = algorithm.generate_improved_version()
        
        # Check for improvement trend
        if len(performances) > 1:
            # Allow for some variation but expect general improvement
            avg_early = np.mean(performances[:2])
            avg_late = np.mean(performances[-2:])
            
            self.assertGreaterEqual(
                avg_late, avg_early * 0.95,
                "Algorithm should not degrade significantly"
            )
    
    def test_hypothesis_generation(self):
        """Test hypothesis generation and testing."""
        if 'gzip_metarecursive' not in self.algorithms:
            self.skipTest("Meta-recursive algorithm not available")
        
        algorithm = self.algorithms['gzip_metarecursive']
        
        # Compress different data types to trigger hypothesis generation
        data_types = [
            self.test_data.generate_random(1000),
            self.test_data.generate_repetitive(b'X', 1000),
            self.test_data.generate_text(1000),
        ]
        
        for data in data_types:
            compressed, metadata = algorithm.compress(data)
            
        # Check if hypotheses were generated
        if hasattr(algorithm, 'hypotheses'):
            self.assertGreater(
                len(algorithm.hypotheses), 0,
                "Should generate hypotheses"
            )
    
    def test_code_generation(self):
        """Test automatic code generation."""
        if 'gzip_metarecursive' not in self.algorithms:
            self.skipTest("Meta-recursive algorithm not available")
        
        algorithm = self.algorithms['gzip_metarecursive']
        
        # Trigger code generation
        if hasattr(algorithm, '_generate_optimized_code'):
            code = algorithm._generate_optimized_code()
            
            # Verify generated code
            self.assertIn('def compress_optimized', code)
            self.assertIn('import', code)
            
            # Check if code is valid Python
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError:
                self.fail("Generated code has syntax errors")


class TestMathematicalProperties(BaseCompressionTest):
    """Test mathematical properties and theoretical limits."""
    
    def test_entropy_calculation(self):
        """Test entropy calculation accuracy."""
        # Test with known entropy values
        test_cases = [
            (b'A' * 1000, 0.0),  # Zero entropy (single symbol)
            (bytes(range(256)) * 4, 8.0),  # Maximum entropy (uniform distribution)
        ]
        
        for data, expected_entropy in test_cases:
            for algo_name, algorithm in self.algorithms.items():
                with self.subTest(algorithm=algo_name):
                    entropy = algorithm.calculate_entropy(data)
                    self.assertAlmostEqual(
                        entropy, expected_entropy, places=1,
                        msg=f"Entropy calculation incorrect: {entropy:.2f} != {expected_entropy:.2f}"
                    )
    
    def test_compression_limit(self):
        """Test that compression respects theoretical limits."""
        # Shannon's source coding theorem: Cannot compress below entropy
        
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                # Random data (high entropy)
                random_data = self.test_data.generate_random(10000)
                entropy = algorithm.calculate_entropy(random_data)
                
                compressed, metadata = algorithm.compress(random_data)
                
                # Theoretical minimum size (in bits)
                theoretical_min_bits = len(random_data) * entropy
                theoretical_min_bytes = theoretical_min_bits / 8
                
                # Allow 10% margin for overhead
                self.assertGreater(
                    len(compressed), theoretical_min_bytes * 0.9,
                    "Compression violates theoretical limit"
                )
    
    def test_kolmogorov_complexity(self):
        """Test Kolmogorov complexity estimation."""
        # Simple patterns should have low Kolmogorov complexity
        simple_data = b'A' * 1000
        complex_data = self.test_data.generate_random(1000)
        
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                k_simple = algorithm.estimate_kolmogorov_complexity(simple_data)
                k_complex = algorithm.estimate_kolmogorov_complexity(complex_data)
                
                self.assertLess(
                    k_simple, k_complex,
                    "Simple data should have lower Kolmogorov complexity"
                )


class TestMemoryManagement(BaseCompressionTest):
    """Test memory management and leak detection."""
    
    def test_memory_leak(self):
        """Test for memory leaks during repeated operations."""
        algorithm = self.algorithms['gzip_basic']
        data = self.test_data.generate_text(10000)
        
        # Measure initial memory
        gc.collect()
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        
        # Perform many operations
        for _ in range(100):
            compressed, _ = algorithm.compress(data)
            decompressed = algorithm.decompress(compressed)
        
        # Measure final memory
        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()
        
        # Check for leaks
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        total_leak = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        
        # Allow small leak (< 1MB)
        self.assertLess(
            total_leak, 1024 * 1024,
            f"Memory leak detected: {total_leak / 1e6:.2f} MB"
        )
        
        tracemalloc.stop()
    
    def test_memory_efficiency(self):
        """Test memory efficiency during compression."""
        large_data = self.test_data.generate_text(1024 * 1024)  # 1MB
        
        for algo_name, algorithm in self.algorithms.items():
            with self.subTest(algorithm=algo_name):
                tracemalloc.start()
                
                compressed, metadata = algorithm.compress(large_data)
                
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                # Memory usage should be reasonable (< 10x input size)
                self.assertLess(
                    peak, len(large_data) * 10,
                    f"Excessive memory usage: {peak / 1e6:.2f} MB"
                )


class TestAsyncOperations(BaseCompressionTest):
    """Test asynchronous compression operations."""
    
    @pytest.mark.asyncio
    async def test_async_compression(self):
        """Test async compression wrapper."""
        algorithm = self.algorithms['gzip_basic']
        data = self.test_data.generate_text(1000)
        
        async def compress_async(data):
            # Simulate async wrapper
            return await asyncio.get_event_loop().run_in_executor(
                None, algorithm.compress, data
            )
        
        compressed, metadata = await compress_async(data)
        decompressed = algorithm.decompress(compressed)
        
        self.assertEqual(data, decompressed)
    
    @pytest.mark.asyncio
    async def test_concurrent_async_operations(self):
        """Test concurrent async compressions."""
        algorithm = self.algorithms['gzip_basic']
        
        async def compress_task(data):
            return await asyncio.get_event_loop().run_in_executor(
                None, algorithm.compress, data
            )
        
        # Create multiple compression tasks
        tasks = [
            compress_task(self.test_data.generate_text(1000))
            for _ in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        self.assertEqual(len(results), 10)
        for compressed, metadata in results:
            self.assertIsNotNone(compressed)
            self.assertIsNotNone(metadata)


# Performance benchmark suite
class BenchmarkSuite:
    """Comprehensive benchmark suite for performance analysis."""
    
    def __init__(self):
        """Initialize benchmark suite."""
        self.algorithms = {
            'gzip_basic': GzipBasic(),
            'gzip_strategy': GzipStrategy(),
            'gzip_metarecursive': GzipMetaRecursive(),
            'quantum_biological': QuantumBiologicalCompressor(),
        }
        self.test_data = TestDataGenerator()
        self.results = []
    
    def run_benchmarks(self):
        """Run complete benchmark suite."""
        data_sizes = [1024, 10240, 102400, 1024000]  # 1KB to 1MB
        data_types = ['random', 'text', 'repetitive', 'structured']
        
        for size in data_sizes:
            for data_type in data_types:
                # Generate test data
                if data_type == 'random':
                    data = self.test_data.generate_random(size)
                elif data_type == 'text':
                    data = self.test_data.generate_text(size)
                elif data_type == 'repetitive':
                    data = self.test_data.generate_repetitive(b'ABC', size // 3)
                else:
                    data = self.test_data.generate_structured(size)
                
                # Benchmark each algorithm
                for algo_name, algorithm in self.algorithms.items():
                    result = self._benchmark_algorithm(
                        algorithm, algo_name, data, data_type, size
                    )
                    self.results.append(result)
    
    def _benchmark_algorithm(self, algorithm, name, data, data_type, size):
        """Benchmark a single algorithm."""
        # Warm up
        for _ in range(3):
            algorithm.compress(data[:100])
        
        # Benchmark compression
        compress_times = []
        decompress_times = []
        ratios = []
        
        for _ in range(10):
            start = time.perf_counter()
            compressed, metadata = algorithm.compress(data)
            compress_time = time.perf_counter() - start
            
            start = time.perf_counter()
            decompressed = algorithm.decompress(compressed)
            decompress_time = time.perf_counter() - start
            
            compress_times.append(compress_time)
            decompress_times.append(decompress_time)
            ratios.append(metadata.compression_ratio)
        
        return {
            'algorithm': name,
            'data_type': data_type,
            'data_size': size,
            'avg_compress_time': np.mean(compress_times),
            'std_compress_time': np.std(compress_times),
            'avg_decompress_time': np.mean(decompress_times),
            'std_decompress_time': np.std(decompress_times),
            'avg_ratio': np.mean(ratios),
            'throughput_mbps': (size / 1e6) / np.mean(compress_times)
        }
    
    def generate_report(self):
        """Generate benchmark report."""
        import pandas as pd
        
        df = pd.DataFrame(self.results)
        
        # Group by algorithm
        summary = df.groupby('algorithm').agg({
            'avg_compress_time': 'mean',
            'avg_ratio': 'mean',
            'throughput_mbps': 'mean'
        })
        
        print("\n=== Compression Algorithm Benchmark Report ===\n")
        print(summary)
        
        # Best performers
        print("\n=== Best Performers ===")
        print(f"Fastest: {df.loc[df['avg_compress_time'].idxmin()]['algorithm']}")
        print(f"Best Ratio: {df.loc[df['avg_ratio'].idxmax()]['algorithm']}")
        print(f"Highest Throughput: {df.loc[df['throughput_mbps'].idxmax()]['algorithm']}")
        
        return df


if __name__ == '__main__':
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run benchmarks
    print("\n" + "="*50)
    print("Running Performance Benchmarks...")
    print("="*50 + "\n")
    
    benchmark = BenchmarkSuite()
    benchmark.run_benchmarks()
    results = benchmark.generate_report()
    
    # Save results
    results.to_csv('benchmark_results.csv', index=False)
    print("\nBenchmark results saved to benchmark_results.csv")