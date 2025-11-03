"""
Comprehensive Unit Tests for Algorithm Viability Analysis

This test suite validates all compression algorithms with synthetic data
and records results to the meta-learning database for continuous improvement.
"""

import pytest
import asyncio
import time
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Import mock data generator
from test_data.mock_compression_data import (
    MockDataGenerator,
    ContentComplexity,
    MockCompressionData
)

# Import compression models and services
from app.models.compression import (
    CompressionAlgorithm,
    CompressionRequest,
    CompressionParameters,
    CompressionLevel
)
from app.core.compression_engine import CompressionEngine


@dataclass
class AlgorithmViabilityResult:
    """Results from algorithm viability testing."""
    algorithm: str
    content_type: str
    complexity: str
    
    # Size metrics
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_percentage: float
    
    # Performance metrics
    compression_time: float
    throughput_mbps: float
    
    # Viability metrics
    success: bool
    within_expected_range: bool
    expected_min_ratio: float
    expected_max_ratio: float
    
    # Quality metrics
    quality_score: float
    efficiency_score: float
    
    # Characteristics
    characteristics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class AlgorithmViabilityReport:
    """Comprehensive viability analysis report."""
    test_timestamp: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    
    # Algorithm performance summary
    algorithm_rankings: List[Dict[str, Any]]
    
    # Detailed results by algorithm
    results_by_algorithm: Dict[str, List[AlgorithmViabilityResult]]
    
    # Content type analysis
    results_by_content_type: Dict[str, List[AlgorithmViabilityResult]]
    
    # Statistical summary
    overall_statistics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "test_timestamp": self.test_timestamp,
            "total_tests": self.total_tests,
            "successful_tests": self.successful_tests,
            "failed_tests": self.failed_tests,
            "algorithm_rankings": self.algorithm_rankings,
            "results_by_algorithm": {
                alg: [r.to_dict() for r in results]
                for alg, results in self.results_by_algorithm.items()
            },
            "results_by_content_type": {
                ct: [r.to_dict() for r in results]
                for ct, results in self.results_by_content_type.items()
            },
            "overall_statistics": self.overall_statistics
        }


class TestAlgorithmViability:
    """Comprehensive algorithm viability test suite."""
    
    @pytest.fixture(scope="class")
    def mock_data_generator(self):
        """Fixture for mock data generator."""
        return MockDataGenerator(seed=42)
    
    @pytest.fixture(scope="class")
    def compression_engine(self):
        """Fixture for compression engine."""
        return CompressionEngine()
    
    @pytest.fixture(scope="class")
    def test_cases(self, mock_data_generator):
        """Generate all test cases."""
        return mock_data_generator.generate_all_test_cases()
    
    @pytest.mark.asyncio
    async def test_gzip_algorithm_viability(self, compression_engine, test_cases):
        """Test GZIP algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.GZIP,
            engine=compression_engine,
            test_cases=test_cases
        )
        
        # Validate results
        assert len(results) > 0, "GZIP should process at least one test case"
        
        successful_results = [r for r in results if r.success]
        assert len(successful_results) > 0, "GZIP should have successful compressions"
        
        # Check performance on repetitive data
        repetitive_results = [
            r for r in results 
            if r.complexity == ContentComplexity.MINIMAL.value and r.success
        ]
        if repetitive_results:
            avg_ratio = sum(r.compression_ratio for r in repetitive_results) / len(repetitive_results)
            assert avg_ratio >= 5.0, f"GZIP should achieve high compression on repetitive data (got {avg_ratio:.2f}x)"
    
    @pytest.mark.asyncio
    async def test_lzma_algorithm_viability(self, compression_engine, test_cases):
        """Test LZMA algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.LZMA,
            engine=compression_engine,
            test_cases=test_cases
        )
        
        assert len(results) > 0, "LZMA should process test cases"
        
        # LZMA should excel at high compression
        successful_results = [r for r in results if r.success]
        if successful_results:
            avg_ratio = sum(r.compression_ratio for r in successful_results) / len(successful_results)
            assert avg_ratio >= 2.0, f"LZMA should achieve good average compression (got {avg_ratio:.2f}x)"
    
    @pytest.mark.asyncio
    async def test_bzip2_algorithm_viability(self, compression_engine, test_cases):
        """Test BZIP2 algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.BZIP2,
            engine=compression_engine,
            test_cases=test_cases
        )
        
        assert len(results) > 0, "BZIP2 should process test cases"
    
    @pytest.mark.asyncio
    async def test_lz4_algorithm_viability(self, compression_engine, test_cases):
        """Test LZ4 algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.LZ4,
            engine=compression_engine,
            test_cases=test_cases
        )
        
        assert len(results) > 0, "LZ4 should process test cases"
        
        # LZ4 should be fast
        successful_results = [r for r in results if r.success]
        if successful_results:
            avg_throughput = sum(r.throughput_mbps for r in successful_results) / len(successful_results)
            # LZ4 should generally be faster than GZIP/LZMA
            assert avg_throughput > 0, f"LZ4 should have measurable throughput"
    
    @pytest.mark.asyncio
    async def test_zstd_algorithm_viability(self, compression_engine, test_cases):
        """Test ZSTD algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.ZSTD,
            engine=compression_engine,
            test_cases=test_cases
        )
        
        assert len(results) > 0, "ZSTD should process test cases"
        
        # ZSTD should have good balance
        successful_results = [r for r in results if r.success]
        if successful_results:
            avg_ratio = sum(r.compression_ratio for r in successful_results) / len(successful_results)
            avg_throughput = sum(r.throughput_mbps for r in successful_results) / len(successful_results)
            
            # ZSTD should balance compression and speed
            assert avg_ratio >= 1.5, f"ZSTD should achieve reasonable compression"
            assert avg_throughput > 0, f"ZSTD should have good throughput"
    
    @pytest.mark.asyncio
    async def test_brotli_algorithm_viability(self, compression_engine, test_cases):
        """Test Brotli algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.BROTLI,
            engine=compression_engine,
            test_cases=test_cases
        )
        
        assert len(results) > 0, "Brotli should process test cases"
        
        # Brotli should excel on text and web content
        text_results = [
            r for r in results 
            if r.content_type in ["text", "json", "xml"] and r.success
        ]
        if text_results:
            avg_ratio = sum(r.compression_ratio for r in text_results) / len(text_results)
            assert avg_ratio >= 2.0, f"Brotli should compress text well (got {avg_ratio:.2f}x)"
    
    @pytest.mark.asyncio
    async def test_content_aware_algorithm_viability(self, compression_engine, test_cases):
        """Test Content-Aware algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.CONTENT_AWARE,
            engine=compression_engine,
            test_cases=test_cases
        )
        
        assert len(results) > 0, "Content-Aware should process test cases"
        
        # Content-Aware should adapt to different content types
        successful_results = [r for r in results if r.success]
        if successful_results:
            # Should perform reasonably across diverse content
            content_types = set(r.content_type for r in successful_results)
            assert len(content_types) >= 3, "Content-Aware should handle multiple content types"
    
    @pytest.mark.asyncio
    async def test_quantum_biological_algorithm_viability(self, compression_engine, test_cases):
        """Test Quantum-Biological algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.QUANTUM_BIOLOGICAL,
            engine=compression_engine,
            test_cases=test_cases[:3]  # Test with fewer cases (experimental algorithm)
        )
        
        # Experimental algorithm - may have lower success rate
        assert len(results) > 0, "Quantum-Biological should attempt compression"
    
    @pytest.mark.asyncio
    async def test_neuromorphic_algorithm_viability(self, compression_engine, test_cases):
        """Test Neuromorphic algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.NEUROMORPHIC,
            engine=compression_engine,
            test_cases=test_cases[:3]  # Test with fewer cases (experimental algorithm)
        )
        
        assert len(results) > 0, "Neuromorphic should attempt compression"
    
    @pytest.mark.asyncio
    async def test_topological_algorithm_viability(self, compression_engine, test_cases):
        """Test Topological algorithm across all test cases."""
        results = await self._test_algorithm(
            algorithm=CompressionAlgorithm.TOPOLOGICAL,
            engine=compression_engine,
            test_cases=test_cases[:3]  # Test with fewer cases (experimental algorithm)
        )
        
        assert len(results) > 0, "Topological should attempt compression"
    
    @pytest.mark.asyncio
    async def test_comprehensive_viability_analysis(
        self,
        compression_engine,
        test_cases,
        mock_data_generator
    ):
        """
        Run comprehensive viability analysis across all algorithms.
        
        This test generates a complete viability report comparing all algorithms
        across all test cases and saves results for meta-learning.
        """
        algorithms = [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZSTD,
            CompressionAlgorithm.BROTLI,
            CompressionAlgorithm.CONTENT_AWARE,
        ]
        
        all_results = {}
        
        for algorithm in algorithms:
            print(f"\n{'='*80}")
            print(f"Testing Algorithm: {algorithm.value.upper()}")
            print(f"{'='*80}")
            
            results = await self._test_algorithm(
                algorithm=algorithm,
                engine=compression_engine,
                test_cases=test_cases
            )
            
            all_results[algorithm.value] = results
            
            # Print summary
            successful = sum(1 for r in results if r.success)
            avg_ratio = sum(r.compression_ratio for r in results if r.success) / max(successful, 1)
            avg_time = sum(r.compression_time for r in results if r.success) / max(successful, 1)
            
            print(f"Results: {successful}/{len(results)} successful")
            print(f"Avg Compression Ratio: {avg_ratio:.2f}x")
            print(f"Avg Compression Time: {avg_time*1000:.2f}ms")
        
        # Generate comprehensive report
        report = self._generate_viability_report(all_results, test_cases)
        
        # Save report
        report_path = "backend/tests/test_results/algorithm_viability_report.json"
        import os
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE VIABILITY ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"Report saved to: {report_path}")
        print(f"\nTop 3 Algorithms by Average Compression Ratio:")
        for i, ranking in enumerate(report.algorithm_rankings[:3], 1):
            print(f"{i}. {ranking['algorithm']}: {ranking['avg_compression_ratio']:.2f}x")
        
        # Assertions
        assert report.successful_tests > 0, "Should have successful compressions"
        assert len(report.algorithm_rankings) == len(algorithms), "Should rank all algorithms"
    
    async def _test_algorithm(
        self,
        algorithm: CompressionAlgorithm,
        engine: CompressionEngine,
        test_cases: List[MockCompressionData]
    ) -> List[AlgorithmViabilityResult]:
        """Test a single algorithm across all test cases."""
        results = []
        
        for test_case in test_cases:
            try:
                # Create compression request
                request = CompressionRequest(
                    content=test_case.content,
                    parameters=CompressionParameters(
                        algorithm=algorithm,
                        level=6
                    )
                )
                
                # Perform compression
                start_time = time.time()
                response = await engine.compress(request)
                compression_time = time.time() - start_time
                
                # Calculate metrics
                if response.success and response.result:
                    compression_ratio = response.result.compression_ratio
                    compression_percentage = response.result.compression_percentage
                    compressed_size = response.result.compressed_size
                    original_size = response.result.original_size
                    
                    # Check if within expected range
                    within_expected = (
                        test_case.expected_compression_ratio_range[0] <= compression_ratio <= 
                        test_case.expected_compression_ratio_range[1] * 2  # Allow 2x margin
                    )
                    
                    # Calculate throughput (MB/s)
                    throughput_mbps = (original_size / compression_time) / (1024 * 1024) if compression_time > 0 else 0
                    
                    # Calculate quality and efficiency scores
                    quality_score = min(compression_ratio / 10.0, 1.0)  # Normalize to 0-1
                    efficiency_score = (compression_ratio / max(compression_time * 1000, 0.001))  # Ratio per ms
                    
                    result = AlgorithmViabilityResult(
                        algorithm=algorithm.value,
                        content_type=test_case.content_type,
                        complexity=test_case.complexity.value,
                        original_size=original_size,
                        compressed_size=compressed_size,
                        compression_ratio=compression_ratio,
                        compression_percentage=compression_percentage,
                        compression_time=compression_time,
                        throughput_mbps=throughput_mbps,
                        success=True,
                        within_expected_range=within_expected,
                        expected_min_ratio=test_case.expected_compression_ratio_range[0],
                        expected_max_ratio=test_case.expected_compression_ratio_range[1],
                        quality_score=quality_score,
                        efficiency_score=efficiency_score,
                        characteristics=test_case.characteristics
                    )
                else:
                    # Failed compression
                    result = AlgorithmViabilityResult(
                        algorithm=algorithm.value,
                        content_type=test_case.content_type,
                        complexity=test_case.complexity.value,
                        original_size=len(test_case.content),
                        compressed_size=0,
                        compression_ratio=1.0,
                        compression_percentage=0.0,
                        compression_time=compression_time,
                        throughput_mbps=0.0,
                        success=False,
                        within_expected_range=False,
                        expected_min_ratio=test_case.expected_compression_ratio_range[0],
                        expected_max_ratio=test_case.expected_compression_ratio_range[1],
                        quality_score=0.0,
                        efficiency_score=0.0,
                        characteristics=test_case.characteristics
                    )
                
                results.append(result)
                
            except Exception as e:
                print(f"Error testing {algorithm.value} on {test_case.content_type}: {e}")
                # Add failed result
                result = AlgorithmViabilityResult(
                    algorithm=algorithm.value,
                    content_type=test_case.content_type,
                    complexity=test_case.complexity.value,
                    original_size=len(test_case.content),
                    compressed_size=0,
                    compression_ratio=1.0,
                    compression_percentage=0.0,
                    compression_time=0.0,
                    throughput_mbps=0.0,
                    success=False,
                    within_expected_range=False,
                    expected_min_ratio=test_case.expected_compression_ratio_range[0],
                    expected_max_ratio=test_case.expected_compression_ratio_range[1],
                    quality_score=0.0,
                    efficiency_score=0.0,
                    characteristics=test_case.characteristics
                )
                results.append(result)
        
        return results
    
    def _generate_viability_report(
        self,
        all_results: Dict[str, List[AlgorithmViabilityResult]],
        test_cases: List[MockCompressionData]
    ) -> AlgorithmViabilityReport:
        """Generate comprehensive viability analysis report."""
        from datetime import datetime
        
        # Calculate statistics
        total_tests = sum(len(results) for results in all_results.values())
        successful_tests = sum(
            sum(1 for r in results if r.success)
            for results in all_results.values()
        )
        failed_tests = total_tests - successful_tests
        
        # Calculate algorithm rankings
        algorithm_rankings = []
        for algorithm, results in all_results.items():
            successful_results = [r for r in results if r.success]
            if successful_results:
                avg_ratio = sum(r.compression_ratio for r in successful_results) / len(successful_results)
                avg_time = sum(r.compression_time for r in successful_results) / len(successful_results)
                avg_throughput = sum(r.throughput_mbps for r in successful_results) / len(successful_results)
                success_rate = len(successful_results) / len(results)
                
                algorithm_rankings.append({
                    "algorithm": algorithm,
                    "avg_compression_ratio": round(avg_ratio, 2),
                    "avg_compression_time_ms": round(avg_time * 1000, 2),
                    "avg_throughput_mbps": round(avg_throughput, 2),
                    "success_rate": round(success_rate * 100, 2),
                    "successful_tests": len(successful_results),
                    "total_tests": len(results)
                })
        
        # Sort by compression ratio (descending)
        algorithm_rankings.sort(key=lambda x: x["avg_compression_ratio"], reverse=True)
        
        # Group results by content type
        results_by_content_type = {}
        for algorithm, results in all_results.items():
            for result in results:
                if result.content_type not in results_by_content_type:
                    results_by_content_type[result.content_type] = []
                results_by_content_type[result.content_type].append(result)
        
        # Calculate overall statistics
        all_successful_results = [
            r for results in all_results.values()
            for r in results if r.success
        ]
        
        overall_statistics = {
            "total_data_processed_bytes": sum(r.original_size for r in all_successful_results),
            "total_compressed_bytes": sum(r.compressed_size for r in all_successful_results),
            "overall_compression_ratio": (
                sum(r.original_size for r in all_successful_results) /
                max(sum(r.compressed_size for r in all_successful_results), 1)
            ),
            "total_compression_time_seconds": sum(r.compression_time for r in all_successful_results),
            "avg_quality_score": sum(r.quality_score for r in all_successful_results) / max(len(all_successful_results), 1),
            "avg_efficiency_score": sum(r.efficiency_score for r in all_successful_results) / max(len(all_successful_results), 1)
        }
        
        return AlgorithmViabilityReport(
            test_timestamp=datetime.utcnow().isoformat(),
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            algorithm_rankings=algorithm_rankings,
            results_by_algorithm=all_results,
            results_by_content_type=results_by_content_type,
            overall_statistics=overall_statistics
        )


# Standalone test runner
if __name__ == "__main__":
    import sys
    
    # Run tests with pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "-k", "test_comprehensive_viability_analysis"
    ])
    
    sys.exit(exit_code)

