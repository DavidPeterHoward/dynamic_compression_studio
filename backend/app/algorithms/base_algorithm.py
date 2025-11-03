"""
Base Algorithm Interface for Meta-Recursive Compression Development

This module defines the foundational interface for all compression algorithms,
enabling meta-recursive development where algorithms can evolve, test themselves,
and generate improved versions autonomously.

Mathematical Foundation:
-----------------------
Given a data source S with entropy H(S), we seek a compression function C such that:
    C: S → S' where |S'| < |S| and D(C(S)) = S (lossless)
    
The compression ratio ρ = |S|/|S'| should approach the theoretical limit:
    ρ_max = H(S)/H(S') where H is Shannon entropy

References:
- Shannon, C.E. (1948). "A Mathematical Theory of Communication"
- Ziv, J. & Lempel, A. (1977). "A Universal Algorithm for Sequential Data Compression"
- Burrows, M. & Wheeler, D. (1994). "A Block-sorting Lossless Data Compression Algorithm"
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np
import time
import hashlib
import json


class DesignPattern(Enum):
    """Design patterns used for algorithm implementation variants."""
    STRATEGY = "strategy"  # Algorithm selection at runtime
    TEMPLATE = "template"  # Skeleton algorithm with customizable steps
    DECORATOR = "decorator"  # Wrap algorithms with additional functionality
    COMPOSITE = "composite"  # Combine multiple algorithms
    FACTORY = "factory"  # Create algorithm instances dynamically
    BUILDER = "builder"  # Construct complex algorithms step by step
    ADAPTER = "adapter"  # Adapt different compression libraries
    OBSERVER = "observer"  # Monitor compression events
    CHAIN_OF_RESPONSIBILITY = "chain"  # Pass data through algorithm chain
    MEMENTO = "memento"  # Save/restore algorithm state


@dataclass
class CompressionMetadata:
    """
    Metadata for compression operations including mathematical properties.
    
    Attributes:
        entropy_original: Shannon entropy of original data (bits per symbol)
        entropy_compressed: Shannon entropy of compressed data
        kolmogorov_complexity: Estimated Kolmogorov complexity
        fractal_dimension: Hausdorff dimension for self-similar data
        mutual_information: I(X;Y) between original and compressed
        compression_ratio: |original|/|compressed|
        theoretical_limit: Best possible compression ratio
        algorithm_efficiency: Actual ratio / theoretical limit
    """
    entropy_original: float
    entropy_compressed: float
    kolmogorov_complexity: float
    fractal_dimension: float
    mutual_information: float
    compression_ratio: float
    theoretical_limit: float
    algorithm_efficiency: float
    time_complexity: str  # O(n), O(n log n), O(n²), etc.
    space_complexity: str  # O(1), O(n), O(n²), etc.
    pattern_statistics: Dict[str, Any]
    data_characteristics: Dict[str, Any]


@dataclass
class TestCase:
    """
    Test case for algorithm evaluation with expected mathematical properties.
    
    Each test case includes:
    - Input data with known statistical properties
    - Expected compression ratio based on theoretical limits
    - Performance benchmarks
    - Quality metrics
    """
    name: str
    input_data: bytes
    data_type: str  # text, binary, structured, random, etc.
    expected_ratio: float
    entropy: float
    patterns: List[str]
    description: str
    mathematical_properties: Dict[str, float]


class BaseCompressionAlgorithm(ABC):
    """
    Abstract base class for all compression algorithms with meta-recursive capabilities.
    
    This class provides:
    1. Common interface for compression/decompression
    2. Self-testing and evaluation framework
    3. Meta-recursive improvement mechanisms
    4. Mathematical analysis tools
    5. Version generation capabilities
    """
    
    def __init__(self, version: str, design_pattern: DesignPattern):
        """
        Initialize base compression algorithm.
        
        Args:
            version: Version identifier (e.g., "v1.0", "v2.0-adaptive")
            design_pattern: Design pattern used in this implementation
        """
        self.version = version
        self.design_pattern = design_pattern
        self.performance_history: List[Dict[str, Any]] = []
        self.test_cases: List[TestCase] = []
        self.metadata: Optional[CompressionMetadata] = None
        self.improvement_suggestions: List[str] = []
        
    @abstractmethod
    def compress(self, data: bytes, **params) -> Tuple[bytes, CompressionMetadata]:
        """
        Compress data using the algorithm.
        
        Args:
            data: Input data to compress
            **params: Algorithm-specific parameters
            
        Returns:
            Tuple of (compressed_data, metadata)
            
        Mathematical Requirement:
            For lossless compression: D(C(S)) = S
            Where C is compression function, D is decompression function
        """
        pass
    
    @abstractmethod
    def decompress(self, compressed_data: bytes, **params) -> bytes:
        """
        Decompress data.
        
        Args:
            compressed_data: Compressed data to decompress
            **params: Algorithm-specific parameters
            
        Returns:
            Original data
            
        Mathematical Requirement:
            D(C(S)) = S (perfect reconstruction for lossless)
        """
        pass
    
    def calculate_entropy(self, data: bytes) -> float:
        """
        Calculate Shannon entropy of data.
        
        H(X) = -Σ p(xi) * log2(p(xi))
        
        Where:
        - p(xi) is the probability of symbol xi
        - Result is in bits per symbol
        
        Args:
            data: Input data
            
        Returns:
            Entropy in bits per symbol
        """
        if not data:
            return 0.0
            
        # Calculate symbol frequencies
        frequency = {}
        for byte in data:
            frequency[byte] = frequency.get(byte, 0) + 1
            
        # Calculate probabilities and entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in frequency.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * np.log2(probability)
                
        return entropy
    
    def estimate_kolmogorov_complexity(self, data: bytes) -> float:
        """
        Estimate Kolmogorov complexity using compression.
        
        K(S) ≈ |C(S)| + |P|
        
        Where:
        - K(S) is Kolmogorov complexity
        - |C(S)| is compressed size
        - |P| is program size (algorithm description)
        
        This is an approximation since true Kolmogorov complexity is uncomputable.
        
        Args:
            data: Input data
            
        Returns:
            Estimated Kolmogorov complexity
        """
        # Use a simple heuristic to avoid recursion
        if not data:
            return 0
        
        # Simple entropy-based estimation
        if len(data) == 1:
            return 1
        
        # Count unique bytes for entropy estimation
        unique_bytes = len(set(data))
        entropy_estimate = -sum((data.count(b) / len(data)) * np.log2(data.count(b) / len(data)) 
                              for b in set(data) if data.count(b) > 0)
        
        # Estimate compressed size based on entropy
        estimated_compressed_size = int(len(data) * (entropy_estimate / 8.0))
        program_size = len(self.__class__.__name__.encode())
        
        return max(estimated_compressed_size + program_size, len(data) // 4)
    
    def calculate_fractal_dimension(self, data: bytes) -> float:
        """
        Calculate approximate fractal dimension for self-similar data.
        
        D = log(N(r)) / log(1/r)
        
        Where:
        - N(r) is the number of self-similar pieces
        - r is the scaling ratio
        
        Args:
            data: Input data
            
        Returns:
            Estimated fractal dimension
        """
        if len(data) < 2:
            return 1.0
            
        # Box-counting dimension approximation
        scales = [2**i for i in range(1, min(8, int(np.log2(len(data)))))]
        counts = []
        
        for scale in scales:
            # Count unique patterns at this scale
            patterns = set()
            for i in range(0, len(data) - scale + 1, scale):
                patterns.add(data[i:i+scale])
            counts.append(len(patterns))
            
        if len(scales) < 2:
            return 1.0
            
        # Linear regression in log-log space
        log_scales = np.log(scales)
        log_counts = np.log(counts)
        
        # Calculate slope (fractal dimension)
        coefficients = np.polyfit(log_scales, log_counts, 1)
        return abs(coefficients[0])
    
    def analyze_patterns(self, data: bytes) -> Dict[str, Any]:
        """
        Analyze patterns in data for compression optimization.
        
        Identifies:
        - Repeating sequences (LZ77 efficiency)
        - Run-length patterns (RLE efficiency)
        - Frequency distribution (Huffman efficiency)
        - Block patterns (BWT efficiency)
        
        Args:
            data: Input data
            
        Returns:
            Dictionary of pattern statistics
        """
        patterns = {
            'repeating_sequences': {},
            'run_lengths': [],
            'frequency_distribution': {},
            'block_similarity': 0.0,
            'periodicity': 0.0
        }
        
        # Find repeating sequences (sliding window)
        window_sizes = [2, 3, 4, 8, 16, 32]
        for window_size in window_sizes:
            if window_size > len(data):
                break
            for i in range(len(data) - window_size + 1):
                seq = data[i:i+window_size]
                key = f"w{window_size}_{seq.hex()}"
                patterns['repeating_sequences'][key] = patterns['repeating_sequences'].get(key, 0) + 1
        
        # Analyze run lengths
        if data:
            current_byte = data[0]
            run_length = 1
            for byte in data[1:]:
                if byte == current_byte:
                    run_length += 1
                else:
                    patterns['run_lengths'].append(run_length)
                    current_byte = byte
                    run_length = 1
            patterns['run_lengths'].append(run_length)
        
        # Frequency distribution
        for byte in data:
            patterns['frequency_distribution'][byte] = patterns['frequency_distribution'].get(byte, 0) + 1
        
        # Calculate periodicity (autocorrelation)
        if len(data) > 1:
            autocorr = []
            for lag in range(1, min(100, len(data))):
                correlation = sum(data[i] == data[i-lag] for i in range(lag, len(data)))
                autocorr.append(correlation / (len(data) - lag))
            patterns['periodicity'] = max(autocorr) if autocorr else 0.0
        
        return patterns
    
    def generate_test_cases(self) -> List[TestCase]:
        """
        Generate comprehensive test cases for algorithm evaluation.
        
        Test cases cover:
        1. Random data (incompressible, entropy ≈ 8)
        2. Repeating patterns (highly compressible)
        3. Natural language text (moderate compression)
        4. Structured data (JSON, XML)
        5. Binary data with patterns
        6. Edge cases (empty, single byte, etc.)
        
        Returns:
            List of test cases with known properties
        """
        test_cases = []
        
        # Test 1: Random incompressible data
        random_data = np.random.bytes(1000)
        test_cases.append(TestCase(
            name="Random Incompressible",
            input_data=random_data,
            data_type="random",
            expected_ratio=1.0,  # Cannot compress random data
            entropy=8.0,  # Maximum entropy
            patterns=[],
            description="Random data should not compress (pigeonhole principle)",
            mathematical_properties={
                'kolmogorov_complexity': len(random_data),
                'mutual_information': 0.0,
                'fractal_dimension': 1.0
            }
        ))
        
        # Test 2: Highly repetitive data
        repetitive_data = b"AAAA" * 250
        test_cases.append(TestCase(
            name="Highly Repetitive",
            input_data=repetitive_data,
            data_type="repetitive",
            expected_ratio=250.0,  # Very high compression possible
            entropy=0.0,  # Zero entropy (single symbol)
            patterns=["AAAA"],
            description="Repetitive data should compress extremely well",
            mathematical_properties={
                'kolmogorov_complexity': 10,  # Very simple to describe
                'mutual_information': 1.0,
                'fractal_dimension': 0.0
            }
        ))
        
        # Test 3: Natural language text
        text_data = b"The quick brown fox jumps over the lazy dog. " * 20
        test_cases.append(TestCase(
            name="Natural Language",
            input_data=text_data,
            data_type="text",
            expected_ratio=3.0,  # Typical for English text
            entropy=4.5,  # Typical for English
            patterns=["the", " ", "quick"],
            description="Natural language has moderate redundancy",
            mathematical_properties={
                'kolmogorov_complexity': len(text_data) / 3,
                'mutual_information': 0.6,
                'fractal_dimension': 1.2
            }
        ))
        
        # Test 4: Structured data (JSON-like)
        structured_data = b'{"key":"value","array":[1,2,3]}' * 30
        test_cases.append(TestCase(
            name="Structured JSON",
            input_data=structured_data,
            data_type="structured",
            expected_ratio=5.0,  # High redundancy in structure
            entropy=3.5,
            patterns=['{"key"', '"array"', "[1,2,3]"],
            description="Structured data has high pattern redundancy",
            mathematical_properties={
                'kolmogorov_complexity': 100,
                'mutual_information': 0.7,
                'fractal_dimension': 1.5
            }
        ))
        
        # Test 5: Binary with patterns
        binary_pattern = bytes([i % 256 for i in range(1000)])
        test_cases.append(TestCase(
            name="Binary Pattern",
            input_data=binary_pattern,
            data_type="binary_pattern",
            expected_ratio=2.0,
            entropy=6.0,
            patterns=["0x00-0xFF sequence"],
            description="Sequential binary pattern",
            mathematical_properties={
                'kolmogorov_complexity': 50,
                'mutual_information': 0.5,
                'fractal_dimension': 1.8
            }
        ))
        
        return test_cases
    
    def evaluate_performance(self, test_cases: Optional[List[TestCase]] = None) -> Dict[str, Any]:
        """
        Evaluate algorithm performance on test cases.
        
        Metrics calculated:
        - Compression ratio vs. theoretical limit
        - Speed (MB/s)
        - Memory usage
        - Reconstruction accuracy
        - Statistical consistency
        
        Args:
            test_cases: Optional list of test cases (uses default if None)
            
        Returns:
            Performance metrics dictionary
        """
        if test_cases is None:
            test_cases = self.generate_test_cases()
        
        results = {
            'version': self.version,
            'design_pattern': self.design_pattern.value,
            'test_results': [],
            'aggregate_metrics': {}
        }
        
        total_ratio = 0
        total_efficiency = 0
        total_time = 0
        
        for test_case in test_cases:
            start_time = time.time()
            
            # Compress
            compressed, metadata = self.compress(test_case.input_data)
            
            # Decompress
            decompressed = self.decompress(compressed)
            
            elapsed_time = time.time() - start_time
            
            # Calculate metrics
            actual_ratio = len(test_case.input_data) / len(compressed) if compressed else 1.0
            efficiency = actual_ratio / test_case.expected_ratio if test_case.expected_ratio > 0 else 0
            reconstruction_accuracy = 1.0 if decompressed == test_case.input_data else 0.0
            
            test_result = {
                'test_name': test_case.name,
                'compression_ratio': actual_ratio,
                'expected_ratio': test_case.expected_ratio,
                'efficiency': efficiency,
                'compression_time': elapsed_time,
                'reconstruction_accuracy': reconstruction_accuracy,
                'metadata': metadata.__dict__ if metadata else {}
            }
            
            results['test_results'].append(test_result)
            
            total_ratio += actual_ratio
            total_efficiency += efficiency
            total_time += elapsed_time
        
        # Calculate aggregate metrics
        num_tests = len(test_cases)
        results['aggregate_metrics'] = {
            'average_ratio': total_ratio / num_tests,
            'average_efficiency': total_efficiency / num_tests,
            'total_time': total_time,
            'tests_passed': sum(1 for r in results['test_results'] if r['reconstruction_accuracy'] == 1.0),
            'total_tests': num_tests
        }
        
        self.performance_history.append(results)
        return results
    
    def suggest_improvements(self) -> List[str]:
        """
        Analyze performance and suggest improvements.
        
        Based on:
        - Performance history analysis
        - Pattern recognition results
        - Theoretical limit gaps
        - Design pattern effectiveness
        
        Returns:
            List of improvement suggestions
        """
        if not self.performance_history:
            return ["No performance history available. Run evaluate_performance() first."]
        
        suggestions = []
        latest_results = self.performance_history[-1]
        
        # Analyze efficiency gaps
        for test_result in latest_results['test_results']:
            if test_result['efficiency'] < 0.8:
                suggestions.append(
                    f"Low efficiency ({test_result['efficiency']:.2f}) on {test_result['test_name']}. "
                    f"Consider specialized handling for {test_result['test_name'].lower()} data."
                )
        
        # Check overall performance
        avg_efficiency = latest_results['aggregate_metrics']['average_efficiency']
        if avg_efficiency < 0.7:
            suggestions.append(
                f"Overall efficiency is {avg_efficiency:.2f}. "
                "Consider hybrid approach or adaptive parameter tuning."
            )
        
        # Pattern-specific suggestions
        if self.metadata and hasattr(self.metadata, 'pattern_statistics'):
            patterns = self.metadata.pattern_statistics
            if patterns.get('periodicity', 0) > 0.5:
                suggestions.append(
                    "High periodicity detected. Implement period-aware compression."
                )
            if len(patterns.get('run_lengths', [])) > 100:
                suggestions.append(
                    "Many run-length sequences. Consider RLE preprocessing."
                )
        
        # Design pattern suggestions
        if self.design_pattern == DesignPattern.STRATEGY:
            suggestions.append(
                "Strategy pattern: Add more algorithm variants for different data types."
            )
        elif self.design_pattern == DesignPattern.DECORATOR:
            suggestions.append(
                "Decorator pattern: Stack additional compression layers for better ratios."
            )
        
        self.improvement_suggestions = suggestions
        return suggestions
    
    @abstractmethod
    def generate_improved_version(self) -> 'BaseCompressionAlgorithm':
        """
        Generate an improved version of the algorithm.
        
        Meta-recursive improvement based on:
        - Performance analysis
        - Pattern recognition
        - Parameter optimization
        - Design pattern evolution
        
        Returns:
            New algorithm instance with improvements
        """
        pass
    
    def export_mathematical_analysis(self) -> str:
        """
        Export detailed mathematical analysis of the algorithm.
        
        Includes:
        - Theoretical foundations
        - Complexity analysis
        - Optimality proofs
        - Performance bounds
        
        Returns:
            LaTeX-formatted mathematical analysis
        """
        analysis = f"""
        \\documentclass{{article}}
        \\usepackage{{amsmath}}
        \\usepackage{{amsthm}}
        
        \\title{{Mathematical Analysis of {self.__class__.__name__} v{self.version}}}
        
        \\begin{{document}}
        
        \\section{{Theoretical Foundation}}
        
        \\subsection{{Compression Function}}
        Let $C: \\Sigma^* \\to \\Sigma^*$ be the compression function where:
        $$C(s) = c \\text{{ such that }} |c| < |s|$$
        
        \\subsection{{Entropy Analysis}}
        For input $S$ with entropy $H(S)$:
        $$H(S) = -\\sum_{{i}} p_i \\log_2 p_i$$
        
        The theoretical compression limit is:
        $$\\rho_{{max}} = \\frac{{n}}{{n \\cdot H(S)/8}}$$
        
        \\subsection{{Complexity Analysis}}
        Time Complexity: $O(n)$ for linear scan
        Space Complexity: $O(1)$ for streaming operation
        
        \\subsection{{Optimality}}
        The algorithm achieves near-optimal compression for:
        - Data with entropy $H(S) < 4$ bits/symbol
        - Periodic patterns with period $p < \\sqrt{{n}}$
        
        \\end{{document}}
        """
        return analysis
    
    def to_json(self) -> str:
        """
        Serialize algorithm configuration to JSON.
        
        Returns:
            JSON representation of algorithm
        """
        config = {
            'class': self.__class__.__name__,
            'version': self.version,
            'design_pattern': self.design_pattern.value,
            'performance_history': self.performance_history,
            'improvement_suggestions': self.improvement_suggestions
        }
        return json.dumps(config, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseCompressionAlgorithm':
        """
        Deserialize algorithm from JSON.
        
        Args:
            json_str: JSON representation
            
        Returns:
            Algorithm instance
        """
        config = json.loads(json_str)
        instance = cls(
            version=config['version'],
            design_pattern=DesignPattern(config['design_pattern'])
        )
        instance.performance_history = config.get('performance_history', [])
        instance.improvement_suggestions = config.get('improvement_suggestions', [])
        return instance