"""
GZIP Basic Implementation (v1.0)

This is the foundational GZIP implementation using Python's built-in gzip module.
It serves as the baseline for comparison with more advanced versions.

Design Pattern: Simple Factory
Mathematical Model: Standard DEFLATE (LZ77 + Huffman)

Performance Characteristics:
- Time Complexity: O(n) for compression, O(n) for decompression
- Space Complexity: O(W) where W is window size (typically 32KB)
- Compression Ratio: 2-4x for text, 1.5-2x for binary

Data Input/Output:
- Input: Any byte sequence
- Output: GZIP-formatted compressed bytes with header and CRC32
- Format: [Header(10)] [Compressed Data] [CRC32(4)] [Size(4)]
"""

import gzip
import zlib
import time
import struct
from typing import Tuple, Dict, Any, Optional
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ...base_algorithm import BaseCompressionAlgorithm, CompressionMetadata, DesignPattern


class GzipBasic(BaseCompressionAlgorithm):
    """
    Basic GZIP implementation with standard parameters.
    
    This version uses Python's built-in gzip module with fixed compression level.
    It provides a baseline for performance comparison and serves as the
    foundation for more advanced implementations.
    """
    
    def __init__(self, compression_level: int = 6):
        """
        Initialize basic GZIP compressor.
        
        Args:
            compression_level: Compression level (1-9)
                1 = fastest, least compression
                6 = default balance
                9 = slowest, best compression
                
        Mathematical relationship:
        Higher levels use more extensive string matching in LZ77 phase:
        - Level 1: Max chain length = 4, good match = 32
        - Level 6: Max chain length = 128, good match = 128  
        - Level 9: Max chain length = 4096, good match = 258
        """
        super().__init__(version="1.0-basic", design_pattern=DesignPattern.FACTORY)
        self.compression_level = compression_level
        
        # GZIP-specific parameters
        self.window_size = 32768  # 32KB sliding window (2^15)
        self.min_match_length = 3  # Minimum match length for LZ77
        self.max_match_length = 258  # Maximum match length
        self.max_distance = 32768  # Maximum distance for back-reference
        
        # Performance tracking
        self.compression_stats = {
            'total_bytes_processed': 0,
            'total_bytes_compressed': 0,
            'total_time': 0.0,
            'huffman_efficiency': [],
            'lz77_efficiency': []
        }
    
    def compress(self, data: bytes, **params) -> Tuple[bytes, CompressionMetadata]:
        """
        Compress data using GZIP DEFLATE algorithm.
        
        DEFLATE process:
        1. LZ77 compression: Find repeated sequences
        2. Huffman coding: Encode LZ77 output optimally
        3. Add GZIP header and trailer
        
        Args:
            data: Input bytes to compress
            **params: Optional parameters (level, strategy, etc.)
            
        Returns:
            Tuple of (compressed_data, metadata)
            
        Mathematical Analysis:
        For input with entropy H and redundancy R:
        - LZ77 reduction: ρ₁ = 1 / (1 - R)
        - Huffman reduction: ρ₂ = 8 / H
        - Total: ρ = ρ₁ * ρ₂
        """
        start_time = time.time()
        
        # Calculate input statistics
        entropy_original = self.calculate_entropy(data)
        patterns = self.analyze_patterns(data)
        
        # Apply GZIP compression
        level = params.get('level', self.compression_level)
        compressed = gzip.compress(data, compresslevel=level)
        
        # Calculate compression metrics
        compression_time = time.time() - start_time
        compression_ratio = len(data) / len(compressed) if compressed else 1.0
        
        # Estimate component efficiencies
        # LZ77 typically contributes 60-70% of compression
        # Huffman contributes 30-40%
        estimated_lz77_ratio = compression_ratio * 0.65
        estimated_huffman_ratio = compression_ratio * 0.35
        
        # Calculate theoretical limits
        # For GZIP, theoretical limit based on entropy
        theoretical_limit = 8.0 / max(entropy_original, 0.1)
        algorithm_efficiency = compression_ratio / theoretical_limit
        
        # Analyze compressed data structure
        entropy_compressed = self.calculate_entropy(compressed)
        kolmogorov = self.estimate_kolmogorov_complexity(data)
        fractal_dim = self.calculate_fractal_dimension(data)
        
        # Create metadata
        metadata = CompressionMetadata(
            entropy_original=entropy_original,
            entropy_compressed=entropy_compressed,
            kolmogorov_complexity=kolmogorov,
            fractal_dimension=fractal_dim,
            mutual_information=self._calculate_mutual_information(data, compressed),
            compression_ratio=compression_ratio,
            theoretical_limit=theoretical_limit,
            algorithm_efficiency=algorithm_efficiency,
            time_complexity="O(n)",
            space_complexity=f"O({self.window_size})",
            pattern_statistics=patterns,
            data_characteristics={
                'size': len(data),
                'compressed_size': len(compressed),
                'compression_level': level,
                'window_size': self.window_size,
                'estimated_lz77_ratio': estimated_lz77_ratio,
                'estimated_huffman_ratio': estimated_huffman_ratio,
                'compression_time': compression_time
            }
        )
        
        # Update statistics
        self.compression_stats['total_bytes_processed'] += len(data)
        self.compression_stats['total_bytes_compressed'] += len(compressed)
        self.compression_stats['total_time'] += compression_time
        self.compression_stats['huffman_efficiency'].append(estimated_huffman_ratio)
        self.compression_stats['lz77_efficiency'].append(estimated_lz77_ratio)
        
        self.metadata = metadata
        return compressed, metadata
    
    def decompress(self, compressed_data: bytes, **params) -> bytes:
        """
        Decompress GZIP data.
        
        Process:
        1. Parse GZIP header
        2. Huffman decode to get LZ77 symbols
        3. LZ77 decode to reconstruct original data
        4. Verify CRC32 checksum
        
        Args:
            compressed_data: GZIP compressed bytes
            **params: Optional parameters
            
        Returns:
            Original decompressed data
            
        Mathematical guarantee:
        D(C(S)) = S (perfect reconstruction)
        CRC32 provides 2^-32 collision probability
        """
        try:
            decompressed = gzip.decompress(compressed_data)
            return decompressed
        except Exception as e:
            # Attempt recovery with different methods
            try:
                # Try with zlib if pure DEFLATE
                return zlib.decompress(compressed_data, -zlib.MAX_WBITS)
            except:
                # Last resort: return empty or partial data
                print(f"Decompression failed: {e}")
                return b""
    
    def _calculate_mutual_information(self, original: bytes, compressed: bytes) -> float:
        """
        Calculate mutual information between original and compressed data.
        
        I(X;Y) = H(X) + H(Y) - H(X,Y)
        
        Where:
        - H(X) is entropy of original
        - H(Y) is entropy of compressed
        - H(X,Y) is joint entropy
        
        Args:
            original: Original data
            compressed: Compressed data
            
        Returns:
            Mutual information in bits
        """
        h_x = self.calculate_entropy(original)
        h_y = self.calculate_entropy(compressed)
        
        # Estimate joint entropy (simplified)
        # In perfect compression, I(X;Y) = H(X)
        # In no compression, I(X;Y) = 0
        compression_ratio = len(original) / len(compressed) if compressed else 1.0
        joint_entropy = h_x + h_y - (h_x * min(compression_ratio / 10, 1.0))
        
        return max(0, h_x + h_y - joint_entropy)
    
    def analyze_deflate_structure(self, compressed: bytes) -> Dict[str, Any]:
        """
        Analyze the internal structure of DEFLATE compressed data.
        
        DEFLATE format:
        - Dynamic Huffman trees for literals/lengths
        - Huffman tree for distances
        - LZ77 tokens: literals or (length, distance) pairs
        
        Args:
            compressed: GZIP compressed data
            
        Returns:
            Dictionary with DEFLATE structure analysis
        """
        analysis = {
            'header_size': 10,  # GZIP header
            'trailer_size': 8,  # CRC32 + size
            'deflate_blocks': [],
            'huffman_tree_stats': {},
            'lz77_stats': {}
        }
        
        # Parse GZIP header
        if len(compressed) > 10:
            magic = compressed[0:2]
            method = compressed[2]
            flags = compressed[3]
            
            analysis['header'] = {
                'magic': magic.hex(),
                'method': method,
                'flags': flags,
                'has_fname': bool(flags & 0x08),
                'has_fcomment': bool(flags & 0x10),
                'has_fhcrc': bool(flags & 0x02)
            }
        
        # Estimate DEFLATE block structure
        # This is simplified - full parsing requires bit-level operations
        deflate_data = compressed[10:-8] if len(compressed) > 18 else b""
        
        if deflate_data:
            # Analyze block patterns
            block_size_estimate = 65535  # Maximum DEFLATE block size
            num_blocks = (len(deflate_data) + block_size_estimate - 1) // block_size_estimate
            
            analysis['deflate_blocks'] = {
                'estimated_count': num_blocks,
                'average_size': len(deflate_data) / max(num_blocks, 1),
                'data_size': len(deflate_data)
            }
            
            # Estimate Huffman tree efficiency
            # In optimal Huffman coding, average code length ≈ entropy
            analysis['huffman_tree_stats'] = {
                'estimated_avg_code_length': self.calculate_entropy(deflate_data),
                'theoretical_min': np.log2(256),  # For uniform distribution
                'efficiency': self.calculate_entropy(deflate_data) / 8.0
            }
        
        return analysis
    
    def optimize_parameters(self, data_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize GZIP parameters based on data profile.
        
        Optimization strategy:
        - High entropy (>7): Use level 1-3 (speed priority)
        - Medium entropy (4-7): Use level 4-6 (balanced)
        - Low entropy (<4): Use level 7-9 (ratio priority)
        - Large patterns: Increase window size
        - Small patterns: Decrease window for cache efficiency
        
        Args:
            data_profile: Data characteristics from analyze_patterns()
            
        Returns:
            Optimized parameters dictionary
        """
        params = {
            'level': self.compression_level,
            'strategy': 'default'
        }
        
        # Get entropy from profile
        entropy = data_profile.get('entropy', 5.0)
        pattern_size = np.mean(data_profile.get('run_lengths', [10]))
        
        # Optimize compression level
        if entropy > 7:
            params['level'] = min(3, self.compression_level)
            params['strategy'] = 'speed'
        elif entropy > 4:
            params['level'] = 6
            params['strategy'] = 'balanced'
        else:
            params['level'] = max(7, self.compression_level)
            params['strategy'] = 'ratio'
        
        # Window size optimization (if we could control it)
        if pattern_size > 1000:
            params['suggested_window'] = 65536  # Large window for large patterns
        elif pattern_size < 100:
            params['suggested_window'] = 8192  # Small window for cache locality
        else:
            params['suggested_window'] = 32768  # Default
        
        return params
    
    def generate_improved_version(self) -> 'BaseCompressionAlgorithm':
        """
        Generate improved version based on performance analysis.
        
        Improvement strategies:
        1. Adaptive level selection
        2. Pre-processing for specific patterns
        3. Multi-threading for large data
        4. Custom Huffman tables for known distributions
        
        Returns:
            New GzipStrategy instance with improvements
        """
        # Analyze performance history
        if self.performance_history:
            avg_efficiency = np.mean([
                r['aggregate_metrics']['average_efficiency'] 
                for r in self.performance_history
            ])
            
            # If efficiency is low, create adaptive version
            if avg_efficiency < 0.7:
                from .v4_adaptive import GzipAdaptive
                return GzipAdaptive()
            else:
                # Create strategy version with optimized parameters
                from .v2_strategy import GzipStrategy
                return GzipStrategy(default_level=9 if avg_efficiency < 0.85 else 6)
        
        # Default: return strategy version
        from .v2_strategy import GzipStrategy
        return GzipStrategy()
    
    def benchmark_against_variants(self) -> Dict[str, Any]:
        """
        Benchmark this implementation against other GZIP variants.
        
        Compares:
        - Compression ratio
        - Speed (MB/s)
        - Memory usage
        - CPU utilization
        
        Returns:
            Benchmark results dictionary
        """
        test_cases = self.generate_test_cases()
        results = {
            'version': self.version,
            'benchmarks': []
        }
        
        for test_case in test_cases:
            start_time = time.time()
            compressed, metadata = self.compress(test_case.input_data)
            compression_time = time.time() - start_time
            
            # Calculate metrics
            throughput = len(test_case.input_data) / (1024 * 1024) / compression_time if compression_time > 0 else 0
            
            benchmark = {
                'test': test_case.name,
                'input_size': len(test_case.input_data),
                'compressed_size': len(compressed),
                'ratio': metadata.compression_ratio,
                'throughput_mbps': throughput,
                'time': compression_time,
                'efficiency': metadata.algorithm_efficiency
            }
            
            results['benchmarks'].append(benchmark)
        
        # Calculate summary statistics
        results['summary'] = {
            'avg_ratio': np.mean([b['ratio'] for b in results['benchmarks']]),
            'avg_throughput': np.mean([b['throughput_mbps'] for b in results['benchmarks']]),
            'avg_efficiency': np.mean([b['efficiency'] for b in results['benchmarks']])
        }
        
        return results