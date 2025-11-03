#!/usr/bin/env python3
"""
Comprehensive Algorithm Viability Test Runner

This script runs complete algorithm viability tests, including:
1. Mock data generation across all content types
2. Testing all compression algorithms
3. Recording results to meta-learning database
4. Generating comprehensive reports
5. Providing continuous feedback for system improvement
"""

import asyncio
import sys
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test_data.mock_compression_data import MockDataGenerator, ContentComplexity
from app.core.compression_engine import CompressionEngine
from app.models.compression import (
    CompressionAlgorithm,
    CompressionRequest,
    CompressionParameters
)
from app.services.meta_learning_service import get_meta_learning_service


class ComprehensiveTestRunner:
    """
    Comprehensive test runner for algorithm viability analysis.
    
    Orchestrates complete testing workflow:
    1. Generate synthetic test data
    2. Test all algorithms
    3. Record results to database
    4. Generate reports
    5. Provide recommendations
    """
    
    def __init__(self):
        self.data_generator = MockDataGenerator(seed=42)
        self.compression_engine = CompressionEngine()
        self.meta_learning_service = get_meta_learning_service()
        self.test_run_id = str(uuid.uuid4())
        self.results = []
        
        print("=" * 80)
        print("COMPREHENSIVE ALGORITHM VIABILITY TEST RUNNER")
        print("=" * 80)
        print(f"Test Run ID: {self.test_run_id}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print()
    
    async def run_complete_test_suite(self):
        """Run the complete test suite."""
        print("Step 1: Generating Synthetic Test Data")
        print("-" * 80)
        test_cases = self.data_generator.generate_all_test_cases()
        summary = self.data_generator.get_test_case_summary()
        print(f"Generated {len(test_cases)} test cases")
        print(f"Total size: {summary['total_size_bytes']:,} bytes")
        print(f"Content types: {list(summary['content_type_distribution'].keys())}")
        print()
        
        print("Step 2: Testing Compression Algorithms")
        print("-" * 80)
        
        # Test traditional algorithms
        traditional_algorithms = [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZSTD,
            CompressionAlgorithm.BROTLI,
            CompressionAlgorithm.CONTENT_AWARE,
        ]
        
        # Test experimental algorithms (limited)
        experimental_algorithms = [
            CompressionAlgorithm.QUANTUM_BIOLOGICAL,
            CompressionAlgorithm.NEUROMORPHIC,
            CompressionAlgorithm.TOPOLOGICAL,
        ]
        
        all_results = {}
        
        # Test traditional algorithms on all test cases
        for algorithm in traditional_algorithms:
            print(f"\nTesting: {algorithm.value.upper()}")
            results = await self._test_algorithm_on_all_cases(
                algorithm, test_cases
            )
            all_results[algorithm.value] = results
            
            successful = sum(1 for r in results if r['success'])
            avg_ratio = sum(r['compression_ratio'] for r in results if r['success']) / max(successful, 1)
            print(f"  Success rate: {successful}/{len(results)}")
            print(f"  Avg compression ratio: {avg_ratio:.2f}x")
        
        # Test experimental algorithms on subset
        experimental_test_cases = test_cases[:3]  # Test on first 3 cases only
        for algorithm in experimental_algorithms:
            print(f"\nTesting (Experimental): {algorithm.value.upper()}")
            results = await self._test_algorithm_on_all_cases(
                algorithm, experimental_test_cases
            )
            all_results[algorithm.value] = results
            
            successful = sum(1 for r in results if r['success'])
            print(f"  Success rate: {successful}/{len(results)}")
        
        print()
        print("Step 3: Recording Results to Meta-Learning Database")
        print("-" * 80)
        
        total_recorded = 0
        for algorithm, results in all_results.items():
            for result in results:
                success = self.meta_learning_service.record_compression_test(
                    test_id=f"{self.test_run_id}_{algorithm}_{result['test_case_id']}",
                    algorithm=algorithm,
                    content_type=result['content_type'],
                    content_size=result['original_size'],
                    compressed_size=result['compressed_size'],
                    compression_ratio=result['compression_ratio'],
                    compression_percentage=result['compression_percentage'],
                    compression_time=result['compression_time'],
                    throughput_mbps=result['throughput_mbps'],
                    quality_score=result['quality_score'],
                    efficiency_score=result['efficiency_score'],
                    success=result['success'],
                    content_characteristics=result['characteristics'],
                    parameters_used=result['parameters_used'],
                    metadata={
                        'test_run_id': self.test_run_id,
                        'complexity': result['complexity']
                    }
                )
                if success:
                    total_recorded += 1
        
        print(f"Recorded {total_recorded} test results to database")
        
        # Record viability analysis
        analysis_summary = self._generate_analysis_summary(all_results)
        self.meta_learning_service.record_viability_analysis(
            analysis_id=f"analysis_{self.test_run_id}",
            content_size=sum(tc.size_bytes for tc in test_cases),
            total_algorithms_tested=len(all_results),
            successful_tests=sum(
                sum(1 for r in results if r['success'])
                for results in all_results.values()
            ),
            recommended_algorithm=analysis_summary['recommended_algorithm'],
            recommendation_reasoning=analysis_summary['reasoning'],
            test_results=analysis_summary['summary']
        )
        
        print()
        print("Step 4: Generating Comprehensive Report")
        print("-" * 80)
        
        report = self._generate_comprehensive_report(all_results, test_cases)
        
        # Save report to file
        report_path = f"backend/tests/test_results/viability_report_{self.test_run_id}.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to: {report_path}")
        
        print()
        print("Step 5: Meta-Learning Database Statistics")
        print("-" * 80)
        
        db_stats = self.meta_learning_service.get_database_statistics()
        print(f"Total tests in database: {db_stats['total_tests']:,}")
        print(f"Successful tests: {db_stats['successful_tests']:,}")
        print(f"Success rate: {db_stats['success_rate']:.1f}%")
        print(f"Unique algorithms: {db_stats['unique_algorithms']}")
        print(f"Unique content types: {db_stats['unique_content_types']}")
        
        print()
        print("=" * 80)
        print("TEST RUN COMPLETE")
        print("=" * 80)
        print()
        print("Top 5 Algorithms by Average Compression Ratio:")
        for i, (algo, data) in enumerate(sorted(
            report['algorithm_rankings'].items(),
            key=lambda x: x[1]['avg_compression_ratio'],
            reverse=True
        )[:5], 1):
            print(f"{i}. {algo.upper()}: {data['avg_compression_ratio']:.2f}x "
                  f"({data['success_rate']:.1f}% success)")
        
        return report
    
    async def _test_algorithm_on_all_cases(self, algorithm, test_cases):
        """Test a single algorithm on all test cases."""
        results = []
        
        for i, test_case in enumerate(test_cases):
            test_case_id = f"case_{i}"
            
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
                import time
                start_time = time.time()
                response = await self.compression_engine.compress(request)
                compression_time = time.time() - start_time
                
                if response.success and response.result:
                    # Calculate metrics
                    compression_ratio = response.result.compression_ratio
                    compression_percentage = response.result.compression_percentage
                    compressed_size = response.result.compressed_size
                    original_size = response.result.original_size
                    
                    throughput_mbps = (original_size / compression_time) / (1024 * 1024) if compression_time > 0 else 0
                    quality_score = min(compression_ratio / 10.0, 1.0)
                    efficiency_score = compression_ratio / max(compression_time * 1000, 0.001)
                    
                    results.append({
                        'test_case_id': test_case_id,
                        'success': True,
                        'algorithm': algorithm.value,
                        'content_type': test_case.content_type,
                        'complexity': test_case.complexity.value,
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'compression_ratio': compression_ratio,
                        'compression_percentage': compression_percentage,
                        'compression_time': compression_time,
                        'throughput_mbps': throughput_mbps,
                        'quality_score': quality_score,
                        'efficiency_score': efficiency_score,
                        'characteristics': test_case.characteristics,
                        'parameters_used': {'algorithm': algorithm.value, 'level': 6}
                    })
                else:
                    # Failed compression
                    results.append({
                        'test_case_id': test_case_id,
                        'success': False,
                        'algorithm': algorithm.value,
                        'content_type': test_case.content_type,
                        'complexity': test_case.complexity.value,
                        'original_size': len(test_case.content),
                        'compressed_size': 0,
                        'compression_ratio': 1.0,
                        'compression_percentage': 0.0,
                        'compression_time': compression_time,
                        'throughput_mbps': 0.0,
                        'quality_score': 0.0,
                        'efficiency_score': 0.0,
                        'characteristics': test_case.characteristics,
                        'parameters_used': {'algorithm': algorithm.value, 'level': 6}
                    })
            
            except Exception as e:
                print(f"  Error on test case {i}: {str(e)}")
                results.append({
                    'test_case_id': test_case_id,
                    'success': False,
                    'algorithm': algorithm.value,
                    'content_type': test_case.content_type,
                    'complexity': test_case.complexity.value,
                    'original_size': len(test_case.content),
                    'compressed_size': 0,
                    'compression_ratio': 1.0,
                    'compression_percentage': 0.0,
                    'compression_time': 0.0,
                    'throughput_mbps': 0.0,
                    'quality_score': 0.0,
                    'efficiency_score': 0.0,
                    'characteristics': test_case.characteristics,
                    'parameters_used': {'algorithm': algorithm.value, 'level': 6}
                })
        
        return results
    
    def _generate_analysis_summary(self, all_results):
        """Generate analysis summary for database."""
        # Calculate overall statistics
        algorithm_scores = {}
        
        for algorithm, results in all_results.items():
            successful_results = [r for r in results if r['success']]
            if successful_results:
                avg_ratio = sum(r['compression_ratio'] for r in successful_results) / len(successful_results)
                avg_time = sum(r['compression_time'] for r in successful_results) / len(successful_results)
                avg_efficiency = sum(r['efficiency_score'] for r in successful_results) / len(successful_results)
                
                # Weighted score
                score = avg_ratio * 0.4 + (1 / max(avg_time, 0.001)) * 0.3 + avg_efficiency * 0.3
                algorithm_scores[algorithm] = score
        
        # Find best algorithm
        if algorithm_scores:
            recommended = max(algorithm_scores.items(), key=lambda x: x[1])[0]
        else:
            recommended = "gzip"  # fallback
        
        return {
            'recommended_algorithm': recommended,
            'reasoning': [
                f"Best overall performance across {len(all_results)} algorithms",
                f"Tested on {sum(len(r) for r in all_results.values())} test cases",
                f"Balanced compression ratio, speed, and efficiency"
            ],
            'summary': {
                algo: {
                    'total_tests': len(results),
                    'successful_tests': sum(1 for r in results if r['success']),
                    'avg_compression_ratio': sum(r['compression_ratio'] for r in results if r['success']) / max(sum(1 for r in results if r['success']), 1)
                }
                for algo, results in all_results.items()
            }
        }
    
    def _generate_comprehensive_report(self, all_results, test_cases):
        """Generate comprehensive test report."""
        report = {
            'test_run_id': self.test_run_id,
            'timestamp': datetime.utcnow().isoformat(),
            'test_cases': {
                'total': len(test_cases),
                'total_size_bytes': sum(tc.size_bytes for tc in test_cases),
                'content_types': list(set(tc.content_type for tc in test_cases)),
                'complexity_distribution': {
                    complexity.value: sum(1 for tc in test_cases if tc.complexity == complexity)
                    for complexity in ContentComplexity
                }
            },
            'algorithm_rankings': {},
            'overall_statistics': {},
            'recommendations': {}
        }
        
        # Calculate algorithm rankings
        for algorithm, results in all_results.items():
            successful_results = [r for r in results if r['success']]
            
            if successful_results:
                report['algorithm_rankings'][algorithm] = {
                    'total_tests': len(results),
                    'successful_tests': len(successful_results),
                    'success_rate': (len(successful_results) / len(results)) * 100,
                    'avg_compression_ratio': sum(r['compression_ratio'] for r in successful_results) / len(successful_results),
                    'avg_compression_time_ms': (sum(r['compression_time'] for r in successful_results) / len(successful_results)) * 1000,
                    'avg_throughput_mbps': sum(r['throughput_mbps'] for r in successful_results) / len(successful_results),
                    'avg_quality_score': sum(r['quality_score'] for r in successful_results) / len(successful_results),
                    'avg_efficiency_score': sum(r['efficiency_score'] for r in successful_results) / len(successful_results),
                    'best_compression_ratio': max(r['compression_ratio'] for r in successful_results),
                    'worst_compression_ratio': min(r['compression_ratio'] for r in successful_results)
                }
            else:
                report['algorithm_rankings'][algorithm] = {
                    'total_tests': len(results),
                    'successful_tests': 0,
                    'success_rate': 0.0,
                    'avg_compression_ratio': 0.0,
                    'avg_compression_time_ms': 0.0,
                    'avg_throughput_mbps': 0.0,
                    'avg_quality_score': 0.0,
                    'avg_efficiency_score': 0.0,
                    'best_compression_ratio': 0.0,
                    'worst_compression_ratio': 0.0
                }
        
        # Overall statistics
        all_successful_results = [
            r for results in all_results.values()
            for r in results if r['success']
        ]
        
        if all_successful_results:
            report['overall_statistics'] = {
                'total_tests': sum(len(r) for r in all_results.values()),
                'total_successful': len(all_successful_results),
                'overall_success_rate': (len(all_successful_results) / sum(len(r) for r in all_results.values())) * 100,
                'avg_compression_ratio': sum(r['compression_ratio'] for r in all_successful_results) / len(all_successful_results),
                'avg_compression_time_ms': (sum(r['compression_time'] for r in all_successful_results) / len(all_successful_results)) * 1000,
                'total_data_processed_bytes': sum(r['original_size'] for r in all_successful_results),
                'total_compressed_bytes': sum(r['compressed_size'] for r in all_successful_results)
            }
        
        return report


async def main():
    """Main entry point."""
    runner = ComprehensiveTestRunner()
    
    try:
        report = await runner.run_complete_test_suite()
        return 0
    except Exception as e:
        print(f"\nERROR: Test run failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

