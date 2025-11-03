"""
Comprehensive Testing Framework for Meta-Recursive Compression Algorithms

This framework provides:
1. Automated testing of all algorithm variants
2. Performance benchmarking and comparison
3. Mathematical correctness verification
4. Meta-recursive improvement validation
5. Cross-algorithm compatibility testing

Test Categories:
- Correctness: Lossless compression/decompression
- Performance: Speed, ratio, memory usage
- Adaptability: Performance on different data types
- Evolution: Improvement over generations
- Mathematical: Theoretical limit adherence
"""

import time
import json
import numpy as np
import hashlib
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import pandas as pd

# Import all algorithm families
from gzip.versions.v1_basic import GzipBasic
from gzip.versions.v2_strategy import GzipStrategy
from gzip.versions.v5_metarecursive import GzipMetaRecursive
from quantum_biological.versions.v1_hybrid import QuantumBiologicalCompressor


class DataType(Enum):
    """Types of test data."""
    RANDOM = "random"
    TEXT = "text"
    CODE = "code"
    BINARY = "binary"
    STRUCTURED = "structured"
    REPETITIVE = "repetitive"
    MIXED = "mixed"


@dataclass
class TestResult:
    """Result of a single test."""
    algorithm: str
    version: str
    test_name: str
    data_type: DataType
    input_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    decompression_time: float
    throughput_mbps: float
    memory_usage: float
    correctness: bool
    efficiency: float
    theoretical_limit: float
    metadata: Dict[str, Any]


class CompressionTestFramework:
    """
    Comprehensive testing framework for compression algorithms.
    
    Features:
    - Automated test generation
    - Performance profiling
    - Statistical analysis
    - Visualization
    - Report generation
    """
    
    def __init__(self):
        """Initialize test framework."""
        self.test_results: List[TestResult] = []
        self.algorithms = self._load_algorithms()
        self.test_data = self._generate_test_data()
        
    def _load_algorithms(self) -> Dict[str, Any]:
        """
        Load all available compression algorithms.
        
        Returns:
            Dictionary of algorithm instances
        """
        algorithms = {
            # GZIP family
            'gzip_v1_basic': GzipBasic(),
            'gzip_v2_strategy': GzipStrategy(),
            'gzip_v5_metarecursive': GzipMetaRecursive(),
            
            # Quantum-Biological family
            'quantum_biological_v1': QuantumBiologicalCompressor(),
            
            # Add more algorithm families here
        }
        
        return algorithms
    
    def _generate_test_data(self) -> Dict[DataType, List[bytes]]:
        """
        Generate comprehensive test data sets.
        
        Returns:
            Dictionary of test data by type
        """
        test_data = {}
        
        # Random incompressible data
        test_data[DataType.RANDOM] = [
            np.random.bytes(size) 
            for size in [100, 1000, 10000, 100000]
        ]
        
        # Natural language text
        test_data[DataType.TEXT] = [
            b"The quick brown fox jumps over the lazy dog. " * n
            for n in [10, 100, 1000]
        ]
        
        # Source code
        test_data[DataType.CODE] = [
            b"""
def compress(data):
    # This is a sample function
    result = []
    for byte in data:
        result.append(byte)
    return bytes(result)
""" * n
            for n in [5, 50, 500]
        ]
        
        # Binary with patterns
        test_data[DataType.BINARY] = [
            bytes([i % 256 for i in range(size)])
            for size in [1000, 10000, 100000]
        ]
        
        # Structured data (JSON-like)
        test_data[DataType.STRUCTURED] = [
            (b'{"key": "value", "array": [1, 2, 3], "nested": {"a": "b"}}' * n)
            for n in [10, 100, 1000]
        ]
        
        # Highly repetitive
        test_data[DataType.REPETITIVE] = [
            b"A" * size
            for size in [1000, 10000, 100000]
        ]
        
        # Mixed content
        test_data[DataType.MIXED] = [
            b"Text" + np.random.bytes(50) + b"0" * 100 + b'{"json": true}'
            for _ in range(3)
        ]
        
        return test_data
    
    def run_correctness_tests(self) -> Dict[str, Any]:
        """
        Test compression/decompression correctness.
        
        Verifies:
        - Lossless compression (D(C(S)) = S)
        - Header/trailer integrity
        - Edge cases handling
        
        Returns:
            Correctness test results
        """
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'failures': []
        }
        
        for algo_name, algorithm in self.algorithms.items():
            for data_type, test_cases in self.test_data.items():
                for i, test_data in enumerate(test_cases):
                    results['total_tests'] += 1
                    
                    try:
                        # Compress
                        compressed, metadata = algorithm.compress(test_data)
                        
                        # Decompress
                        decompressed = algorithm.decompress(compressed)
                        
                        # Verify correctness
                        if decompressed == test_data:
                            results['passed'] += 1
                        else:
                            results['failed'] += 1
                            results['failures'].append({
                                'algorithm': algo_name,
                                'data_type': data_type.value,
                                'test_case': i,
                                'error': 'Decompression mismatch'
                            })
                    
                    except Exception as e:
                        results['failed'] += 1
                        results['failures'].append({
                            'algorithm': algo_name,
                            'data_type': data_type.value,
                            'test_case': i,
                            'error': str(e)
                        })
        
        results['success_rate'] = results['passed'] / results['total_tests']
        return results
    
    def run_performance_benchmarks(self) -> pd.DataFrame:
        """
        Run comprehensive performance benchmarks.
        
        Measures:
        - Compression ratio
        - Speed (MB/s)
        - Memory usage
        - CPU utilization
        
        Returns:
            DataFrame with benchmark results
        """
        benchmark_results = []
        
        for algo_name, algorithm in self.algorithms.items():
            for data_type, test_cases in self.test_data.items():
                for test_data in test_cases[:2]:  # Limit for performance
                    # Run compression
                    start_time = time.time()
                    compressed, metadata = algorithm.compress(test_data)
                    compression_time = time.time() - start_time
                    
                    # Run decompression
                    start_time = time.time()
                    decompressed = algorithm.decompress(compressed)
                    decompression_time = time.time() - start_time
                    
                    # Calculate metrics
                    compression_ratio = len(test_data) / len(compressed) if compressed else 1.0
                    throughput = (len(test_data) / (1024 * 1024)) / compression_time if compression_time > 0 else 0
                    
                    # Create test result
                    result = TestResult(
                        algorithm=algo_name,
                        version=algorithm.version,
                        test_name=f"{data_type.value}_{len(test_data)}",
                        data_type=data_type,
                        input_size=len(test_data),
                        compressed_size=len(compressed),
                        compression_ratio=compression_ratio,
                        compression_time=compression_time,
                        decompression_time=decompression_time,
                        throughput_mbps=throughput,
                        memory_usage=0,  # Would need memory profiling
                        correctness=decompressed == test_data,
                        efficiency=metadata.algorithm_efficiency if metadata else 0,
                        theoretical_limit=metadata.theoretical_limit if metadata else 1,
                        metadata=metadata.__dict__ if metadata else {}
                    )
                    
                    self.test_results.append(result)
                    benchmark_results.append({
                        'Algorithm': algo_name,
                        'Data Type': data_type.value,
                        'Size': len(test_data),
                        'Ratio': compression_ratio,
                        'Speed (MB/s)': throughput,
                        'Efficiency': result.efficiency
                    })
        
        return pd.DataFrame(benchmark_results)
    
    def test_meta_recursive_evolution(self, algorithm, generations: int = 10) -> Dict[str, Any]:
        """
        Test meta-recursive improvement over generations.
        
        Args:
            algorithm: Meta-recursive algorithm instance
            generations: Number of generations to evolve
            
        Returns:
            Evolution test results
        """
        evolution_data = {
            'generations': [],
            'compression_ratios': [],
            'efficiencies': [],
            'times': []
        }
        
        test_data = b"Sample test data for evolution. " * 100
        current_algo = algorithm
        
        for gen in range(generations):
            # Test current generation
            start_time = time.time()
            compressed, metadata = current_algo.compress(test_data)
            compression_time = time.time() - start_time
            
            compression_ratio = len(test_data) / len(compressed) if compressed else 1.0
            
            evolution_data['generations'].append(gen)
            evolution_data['compression_ratios'].append(compression_ratio)
            evolution_data['efficiencies'].append(metadata.algorithm_efficiency if metadata else 0)
            evolution_data['times'].append(compression_time)
            
            # Evolve to next generation
            if hasattr(current_algo, 'generate_improved_version'):
                current_algo = current_algo.generate_improved_version()
        
        # Calculate improvement
        if len(evolution_data['efficiencies']) > 1:
            improvement = (
                (evolution_data['efficiencies'][-1] - evolution_data['efficiencies'][0]) 
                / evolution_data['efficiencies'][0] * 100
            )
        else:
            improvement = 0
        
        evolution_data['improvement_percentage'] = improvement
        
        return evolution_data
    
    def test_mathematical_properties(self) -> Dict[str, Any]:
        """
        Test mathematical properties and theoretical limits.
        
        Tests:
        - Shannon entropy calculations
        - Kolmogorov complexity estimates
        - Compression ratio vs theoretical limits
        - Statistical consistency
        
        Returns:
            Mathematical test results
        """
        math_results = {
            'entropy_tests': [],
            'limit_adherence': [],
            'statistical_tests': []
        }
        
        for algo_name, algorithm in self.algorithms.items():
            for data_type, test_cases in self.test_data.items():
                for test_data in test_cases[:1]:  # One test per type
                    # Calculate theoretical properties
                    entropy = algorithm.calculate_entropy(test_data)
                    kolmogorov = algorithm.estimate_kolmogorov_complexity(test_data)
                    fractal_dim = algorithm.calculate_fractal_dimension(test_data)
                    
                    # Compress and check against limits
                    compressed, metadata = algorithm.compress(test_data)
                    
                    if metadata:
                        # Check if compression respects entropy limit
                        theoretical_min = len(test_data) * entropy / 8
                        actual_size = len(compressed)
                        
                        math_results['entropy_tests'].append({
                            'algorithm': algo_name,
                            'data_type': data_type.value,
                            'entropy': entropy,
                            'theoretical_min': theoretical_min,
                            'actual_size': actual_size,
                            'violation': actual_size < theoretical_min * 0.9  # 10% margin
                        })
                        
                        # Check limit adherence
                        math_results['limit_adherence'].append({
                            'algorithm': algo_name,
                            'efficiency': metadata.algorithm_efficiency,
                            'within_limit': metadata.algorithm_efficiency <= 1.0
                        })
        
        # Statistical tests
        math_results['statistical_summary'] = {
            'avg_entropy_violation_rate': np.mean([
                t['violation'] for t in math_results['entropy_tests']
            ]),
            'avg_efficiency': np.mean([
                t['efficiency'] for t in math_results['limit_adherence']
            ])
        }
        
        return math_results
    
    def generate_comparison_matrix(self) -> pd.DataFrame:
        """
        Generate algorithm comparison matrix.
        
        Returns:
            DataFrame comparing all algorithms
        """
        if not self.test_results:
            self.run_performance_benchmarks()
        
        # Group by algorithm
        comparison_data = {}
        
        for result in self.test_results:
            if result.algorithm not in comparison_data:
                comparison_data[result.algorithm] = {
                    'avg_ratio': [],
                    'avg_speed': [],
                    'avg_efficiency': [],
                    'correctness_rate': []
                }
            
            comparison_data[result.algorithm]['avg_ratio'].append(result.compression_ratio)
            comparison_data[result.algorithm]['avg_speed'].append(result.throughput_mbps)
            comparison_data[result.algorithm]['avg_efficiency'].append(result.efficiency)
            comparison_data[result.algorithm]['correctness_rate'].append(float(result.correctness))
        
        # Calculate averages
        comparison_matrix = []
        for algo, metrics in comparison_data.items():
            comparison_matrix.append({
                'Algorithm': algo,
                'Avg Compression Ratio': np.mean(metrics['avg_ratio']),
                'Avg Speed (MB/s)': np.mean(metrics['avg_speed']),
                'Avg Efficiency': np.mean(metrics['avg_efficiency']),
                'Correctness Rate': np.mean(metrics['correctness_rate'])
            })
        
        return pd.DataFrame(comparison_matrix)
    
    def visualize_results(self, save_path: Optional[str] = None):
        """
        Create visualization of test results.
        
        Args:
            save_path: Optional path to save figures
        """
        if not self.test_results:
            self.run_performance_benchmarks()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Compression Ratio by Algorithm and Data Type
        ax1 = axes[0, 0]
        ratio_data = {}
        for result in self.test_results:
            key = f"{result.algorithm}_{result.data_type.value}"
            if key not in ratio_data:
                ratio_data[key] = []
            ratio_data[key].append(result.compression_ratio)
        
        ax1.boxplot(ratio_data.values(), labels=[k.split('_')[0][:10] for k in ratio_data.keys()])
        ax1.set_title('Compression Ratio Distribution')
        ax1.set_ylabel('Compression Ratio')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # 2. Speed vs Compression Ratio
        ax2 = axes[0, 1]
        for algo in set(r.algorithm for r in self.test_results):
            algo_results = [r for r in self.test_results if r.algorithm == algo]
            ratios = [r.compression_ratio for r in algo_results]
            speeds = [r.throughput_mbps for r in algo_results]
            ax2.scatter(ratios, speeds, label=algo[:15], alpha=0.6)
        
        ax2.set_title('Speed vs Compression Trade-off')
        ax2.set_xlabel('Compression Ratio')
        ax2.set_ylabel('Speed (MB/s)')
        ax2.legend(loc='best', fontsize=8)
        
        # 3. Efficiency by Data Type
        ax3 = axes[1, 0]
        efficiency_by_type = {}
        for result in self.test_results:
            if result.data_type not in efficiency_by_type:
                efficiency_by_type[result.data_type] = []
            efficiency_by_type[result.data_type].append(result.efficiency)
        
        ax3.bar(
            [dt.value for dt in efficiency_by_type.keys()],
            [np.mean(effs) for effs in efficiency_by_type.values()]
        )
        ax3.set_title('Average Efficiency by Data Type')
        ax3.set_xlabel('Data Type')
        ax3.set_ylabel('Efficiency')
        ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
        
        # 4. Algorithm Performance Heatmap
        ax4 = axes[1, 1]
        comparison_matrix = self.generate_comparison_matrix()
        if not comparison_matrix.empty:
            metrics = ['Avg Compression Ratio', 'Avg Speed (MB/s)', 'Avg Efficiency']
            heatmap_data = comparison_matrix[metrics].values.T
            
            im = ax4.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
            ax4.set_xticks(range(len(comparison_matrix)))
            ax4.set_xticklabels([a[:10] for a in comparison_matrix['Algorithm']], rotation=45, ha='right')
            ax4.set_yticks(range(len(metrics)))
            ax4.set_yticklabels(metrics)
            ax4.set_title('Algorithm Performance Heatmap')
            
            # Add colorbar
            plt.colorbar(im, ax=ax4)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.show()
    
    def generate_report(self) -> str:
        """
        Generate comprehensive test report.
        
        Returns:
            Formatted report string
        """
        # Run all tests if not already done
        if not self.test_results:
            self.run_performance_benchmarks()
        
        correctness_results = self.run_correctness_tests()
        math_results = self.test_mathematical_properties()
        comparison_matrix = self.generate_comparison_matrix()
        
        report = """
# Compression Algorithm Test Report

## Executive Summary
"""
        
        report += f"""
- Total Algorithms Tested: {len(self.algorithms)}
- Total Test Cases: {len(self.test_results)}
- Overall Correctness Rate: {correctness_results['success_rate']:.2%}

## Correctness Tests
- Passed: {correctness_results['passed']}
- Failed: {correctness_results['failed']}
"""
        
        if correctness_results['failures']:
            report += "\n### Failures:\n"
            for failure in correctness_results['failures'][:5]:
                report += f"- {failure['algorithm']}: {failure['error']}\n"
        
        report += """

## Performance Summary

### Top Performers by Metric:
"""
        
        if not comparison_matrix.empty:
            # Best compression ratio
            best_ratio = comparison_matrix.loc[comparison_matrix['Avg Compression Ratio'].idxmax()]
            report += f"- **Best Compression Ratio**: {best_ratio['Algorithm']} ({best_ratio['Avg Compression Ratio']:.2f}x)\n"
            
            # Fastest
            best_speed = comparison_matrix.loc[comparison_matrix['Avg Speed (MB/s)'].idxmax()]
            report += f"- **Fastest**: {best_speed['Algorithm']} ({best_speed['Avg Speed (MB/s)']:.2f} MB/s)\n"
            
            # Most efficient
            best_efficiency = comparison_matrix.loc[comparison_matrix['Avg Efficiency'].idxmax()]
            report += f"- **Most Efficient**: {best_efficiency['Algorithm']} ({best_efficiency['Avg Efficiency']:.3f})\n"
        
        report += f"""

## Mathematical Properties
- Average Entropy Violation Rate: {math_results['statistical_summary']['avg_entropy_violation_rate']:.2%}
- Average Algorithm Efficiency: {math_results['statistical_summary']['avg_efficiency']:.3f}

## Algorithm Comparison Matrix

"""
        
        if not comparison_matrix.empty:
            report += comparison_matrix.to_string()
        
        report += """

## Recommendations

1. **For Maximum Compression**: Use algorithms with highest compression ratio
2. **For Speed-Critical Applications**: Use fastest algorithms
3. **For Balanced Performance**: Consider efficiency metric
4. **For Specific Data Types**: Match algorithm to data characteristics

## Test Configuration
- Test Data Types: Random, Text, Code, Binary, Structured, Repetitive, Mixed
- Test Sizes: 100 bytes to 100KB
- Metrics: Compression Ratio, Speed, Efficiency, Correctness

---
Generated: """ + time.strftime("%Y-%m-%d %H:%M:%S")
        
        return report


# Example usage
if __name__ == "__main__":
    # Create test framework
    framework = CompressionTestFramework()
    
    # Run tests
    print("Running correctness tests...")
    correctness = framework.run_correctness_tests()
    print(f"Correctness rate: {correctness['success_rate']:.2%}")
    
    print("\nRunning performance benchmarks...")
    benchmarks = framework.run_performance_benchmarks()
    print(benchmarks.head())
    
    print("\nGenerating comparison matrix...")
    comparison = framework.generate_comparison_matrix()
    print(comparison)
    
    print("\nGenerating report...")
    report = framework.generate_report()
    
    # Save report
    with open("compression_test_report.md", "w") as f:
        f.write(report)
    
    print("Report saved to compression_test_report.md")
    
    # Visualize results
    print("\nGenerating visualizations...")
    framework.visualize_results("compression_test_results.png")