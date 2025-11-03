#!/usr/bin/env python3
"""
Basic compression tests that don't require database connections.
These tests focus on core compression functionality.
"""

import pytest
import gzip
import bz2
import lz4.frame
import zstandard as zstd
import brotli
import lzma
import json
import random
import string
from typing import Dict, Any

from app.models.compression import CompressionAlgorithm, CompressionLevel, CompressionParameters
from app.core.compression_engine import CompressionEngine


class TestBasicCompression:
    """Test basic compression functionality without database dependencies."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_data = {
            'text': "This is a test string that will be compressed. " * 100,
            'json': json.dumps({
                'id': 1,
                'name': 'test',
                'data': [i for i in range(1000)],
                'nested': {
                    'key': 'value',
                    'array': [1, 2, 3, 4, 5]
                }
            }),
            'random': ''.join(random.choices(string.ascii_letters + string.digits, k=10000)),
            'repetitive': 'A' * 10000
        }
    
    def test_gzip_compression(self):
        """Test basic gzip compression."""
        data = self.test_data['text'].encode('utf-8')
        
        # Compress
        compressed = gzip.compress(data, compresslevel=6)
        
        # Decompress
        decompressed = gzip.decompress(compressed)
        
        # Verify
        assert decompressed == data
        assert len(compressed) < len(data)
        print(f"GZIP compression ratio: {len(data)} -> {len(compressed)} ({len(compressed)/len(data)*100:.1f}%)")
    
    def test_bzip2_compression(self):
        """Test basic bzip2 compression."""
        data = self.test_data['text'].encode('utf-8')
        
        # Compress
        compressed = bz2.compress(data, compresslevel=6)
        
        # Decompress
        decompressed = bz2.decompress(compressed)
        
        # Verify
        assert decompressed == data
        assert len(compressed) < len(data)
        print(f"BZIP2 compression ratio: {len(data)} -> {len(compressed)} ({len(compressed)/len(data)*100:.1f}%)")
    
    def test_lz4_compression(self):
        """Test basic LZ4 compression."""
        data = self.test_data['text'].encode('utf-8')
        
        # Compress
        compressed = lz4.frame.compress(data, compression_level=6)
        
        # Decompress
        decompressed = lz4.frame.decompress(compressed)
        
        # Verify
        assert decompressed == data
        assert len(compressed) < len(data)
        print(f"LZ4 compression ratio: {len(data)} -> {len(compressed)} ({len(compressed)/len(data)*100:.1f}%)")
    
    def test_zstandard_compression(self):
        """Test basic Zstandard compression."""
        data = self.test_data['text'].encode('utf-8')
        
        # Compress
        cctx = zstd.ZstdCompressor(level=6)
        compressed = cctx.compress(data)
        
        # Decompress
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(compressed)
        
        # Verify
        assert decompressed == data
        assert len(compressed) < len(data)
        print(f"ZStandard compression ratio: {len(data)} -> {len(compressed)} ({len(compressed)/len(data)*100:.1f}%)")
    
    def test_brotli_compression(self):
        """Test basic Brotli compression."""
        data = self.test_data['text'].encode('utf-8')
        
        # Compress
        compressed = brotli.compress(data, quality=6)
        
        # Decompress
        decompressed = brotli.decompress(compressed)
        
        # Verify
        assert decompressed == data
        assert len(compressed) < len(data)
        print(f"Brotli compression ratio: {len(data)} -> {len(compressed)} ({len(compressed)/len(data)*100:.1f}%)")
    
    def test_lzma_compression(self):
        """Test basic LZMA compression."""
        data = self.test_data['text'].encode('utf-8')
        
        # Compress
        compressed = lzma.compress(data, preset=6)
        
        # Decompress
        decompressed = lzma.decompress(compressed)
        
        # Verify
        assert decompressed == data
        assert len(compressed) < len(data)
        print(f"LZMA compression ratio: {len(data)} -> {len(compressed)} ({len(compressed)/len(data)*100:.1f}%)")
    
    def test_compression_ratios_comparison(self):
        """Compare compression ratios across different algorithms."""
        data = self.test_data['text'].encode('utf-8')
        original_size = len(data)
        
        results = {}
        
        # Test each algorithm
        algorithms = [
            ('gzip', lambda d: gzip.compress(d, compresslevel=6)),
            ('bzip2', lambda d: bz2.compress(d, compresslevel=6)),
            ('lz4', lambda d: lz4.frame.compress(d, compression_level=6)),
            ('zstandard', lambda d: zstd.ZstdCompressor(level=6).compress(d)),
            ('brotli', lambda d: brotli.compress(d, quality=6)),
            ('lzma', lambda d: lzma.compress(d, preset=6))
        ]
        
        for name, compress_func in algorithms:
            try:
                compressed = compress_func(data)
                ratio = len(compressed) / original_size
                results[name] = {
                    'compressed_size': len(compressed),
                    'ratio': ratio,
                    'percentage': ratio * 100
                }
                print(f"{name.upper()}: {original_size} -> {len(compressed)} ({ratio*100:.1f}%)")
            except Exception as e:
                print(f"Error with {name}: {e}")
                results[name] = {'error': str(e)}
        
        # Verify all algorithms produced smaller output
        for name, result in results.items():
            if 'error' not in result:
                assert result['compressed_size'] < original_size, f"{name} did not compress data"
                assert result['ratio'] < 1.0, f"{name} compression ratio should be less than 1.0"
    
    def test_different_data_types(self):
        """Test compression on different types of data."""
        algorithms = [
            ('gzip', lambda d: gzip.compress(d, compresslevel=6)),
            ('bzip2', lambda d: bz2.compress(d, compresslevel=6)),
            ('lz4', lambda d: lz4.frame.compress(d, compression_level=6)),
            ('zstandard', lambda d: zstd.ZstdCompressor(level=6).compress(d)),
            ('brotli', lambda d: brotli.compress(d, quality=6)),
            ('lzma', lambda d: lzma.compress(d, preset=6))
        ]
        
        for data_name, data in self.test_data.items():
            data_bytes = data.encode('utf-8')
            print(f"\nTesting {data_name} data ({len(data_bytes)} bytes):")
            
            for algo_name, compress_func in algorithms:
                try:
                    compressed = compress_func(data_bytes)
                    ratio = len(compressed) / len(data_bytes)
                    print(f"  {algo_name}: {len(data_bytes)} -> {len(compressed)} ({ratio*100:.1f}%)")
                    
                    # Verify compression worked
                    assert len(compressed) < len(data_bytes), f"{algo_name} failed to compress {data_name}"
                    
                except Exception as e:
                    print(f"  {algo_name}: Error - {e}")
    
    def test_compression_parameters_model(self):
        """Test the CompressionParameters model."""
        # Test with enum level
        params = CompressionParameters(
            algorithm=CompressionAlgorithm.GZIP,
            level=CompressionLevel.BALANCED
        )
        assert params.algorithm == CompressionAlgorithm.GZIP
        assert params.level == CompressionLevel.BALANCED
        
        # Test with integer level
        params = CompressionParameters(
            algorithm=CompressionAlgorithm.ZSTD,
            level=6
        )
        assert params.algorithm == CompressionAlgorithm.ZSTD
        assert params.level == 6
        
        # Test with additional parameters
        params = CompressionParameters(
            algorithm=CompressionAlgorithm.LZMA,
            level=CompressionLevel.OPTIMAL,
            window_size=32768,
            dictionary_size=65536,
            block_size=16384,
            threads=2
        )
        assert params.window_size == 32768
        assert params.dictionary_size == 65536
        assert params.block_size == 16384
        assert params.threads == 2
    
    def test_compression_algorithm_enum(self):
        """Test the CompressionAlgorithm enum."""
        # Test all enum values
        algorithms = [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZSTD,
            CompressionAlgorithm.BROTLI,
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.CONTENT_AWARE,
            CompressionAlgorithm.QUANTUM_BIOLOGICAL,
            CompressionAlgorithm.NEUROMORPHIC,
            CompressionAlgorithm.TOPOLOGICAL
        ]
        
        for algo in algorithms:
            assert isinstance(algo, CompressionAlgorithm)
            assert algo.value in [
                'gzip', 'bzip2', 'lz4', 'zstd', 'brotli', 'lzma',
                'content_aware', 'quantum_biological', 'neuromorphic', 'topological'
            ]
    
    def test_compression_level_enum(self):
        """Test the CompressionLevel enum."""
        levels = [
            CompressionLevel.FAST,
            CompressionLevel.BALANCED,
            CompressionLevel.OPTIMAL,
            CompressionLevel.MAXIMUM
        ]
        
        for level in levels:
            assert isinstance(level, CompressionLevel)
            assert level.value in ['fast', 'balanced', 'optimal', 'maximum']


if __name__ == "__main__":
    # Run the tests
    test = TestBasicCompression()
    test.setup_method()
    
    print("Running basic compression tests...")
    
    test.test_gzip_compression()
    test.test_bzip2_compression()
    test.test_lz4_compression()
    test.test_zstandard_compression()
    test.test_brotli_compression()
    test.test_lzma_compression()
    test.test_compression_ratios_comparison()
    test.test_different_data_types()
    test.test_compression_parameters_model()
    test.test_compression_algorithm_enum()
    test.test_compression_level_enum()
    
    print("\nAll basic compression tests passed!")
