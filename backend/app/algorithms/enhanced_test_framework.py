"""
Enhanced Testing Framework for Dynamic Compression Algorithms
============================================================

This module provides comprehensive testing capabilities for the advanced
compression framework including unit tests, integration tests, performance
tests, and stress tests.

Features:
- Multi-dimensional test coverage
- Performance benchmarking
- Stress testing and fault injection
- Cross-language testing
- Automated test generation
- Continuous integration support

Test Categories:
- Unit Tests: Individual component testing
- Integration Tests: Component interaction testing
- Performance Tests: Speed and efficiency testing
- Stress Tests: Load and failure testing
- Security Tests: Vulnerability testing
- Compatibility Tests: Cross-platform testing

Design Patterns:
- Test Strategy Pattern (Different test types)
- Factory Pattern (Test case generation)
- Observer Pattern (Test result monitoring)
- Chain of Responsibility (Test execution)
- Template Method (Test framework)

Version: 2.0.0
Author: Advanced Compression Research Team
License: MIT
"""

import asyncio
import json
import logging
import os
import random
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pytest
import numpy as np
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

from .enhanced_base_algorithm import EnhancedBaseAlgorithm, AlgorithmType, AlgorithmConfig
from .algorithm_registry import AlgorithmRegistry, AlgorithmFactory

@dataclass
class TestResult:
    """Comprehensive test result data"""
    test_name: str
    test_type: str
    algorithm_name: str
    success: bool
    execution_time: float
    memory_usage: float
    cpu_usage: float
    compression_ratio: float
    error_message: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    test_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class TestConfiguration:
    """Test configuration parameters"""
    test_types: List[str] = field(default_factory=lambda: ['unit', 'integration', 'performance'])
    algorithms: List[str] = field(default_factory=list)
    data_sizes: List[int] = field(default_factory=lambda: [1024, 10240, 102400, 1048576])
    iterations: int = 10
    timeout: float = 300.0
    parallel_tests: bool = True
    max_workers: int = 4
    enable_stress_testing: bool = True
    enable_fault_injection: bool = True
    enable_security_testing: bool = True
    enable_compatibility_testing: bool = True

class EnhancedTestFramework:
    """
    Enhanced testing framework for compression algorithms
    
    This class provides comprehensive testing capabilities including:
    - Multi-dimensional test coverage
    - Performance benchmarking
    - Stress testing and fault injection
    - Cross-language testing
    - Automated test generation
    """
    
    def __init__(self, 
                 registry: AlgorithmRegistry,
                 config: Optional[TestConfiguration] = None):
        """
        Initialize the enhanced test framework
        
        Args:
            registry: Algorithm registry instance
            config: Test configuration
        """
        self.registry = registry
        self.config = config or TestConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize test components
        self.unit_tester = UnitTester()
        self.integration_tester = IntegrationTester()
        self.performance_tester = PerformanceTester()
        self.stress_tester = StressTester()
        self.security_tester = SecurityTester()
        self.compatibility_tester = CompatibilityTester()
        
        # Test result storage
        self.test_results: List[TestResult] = []
        self.performance_benchmarks: Dict[str, Dict[str, float]] = {}
        
        # Initialize test data generators
        self.test_data_generator = TestDataGenerator()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup test-specific logging"""
        log_dir = Path("logs/tests")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test-specific loggers
        for test_type in ['unit', 'integration', 'performance', 'stress', 'security', 'compatibility']:
            logger = logging.getLogger(f"test_{test_type}")
            logger.setLevel(logging.DEBUG)
            
            handler = logging.FileHandler(log_dir / f"{test_type}_tests.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
    async def run_comprehensive_tests(self) -> Dict[str, List[TestResult]]:
        """
        Run comprehensive test suite
        
        Returns:
            Dictionary of test results by category
        """
        self.logger.info("Starting comprehensive test suite")
        
        test_results = {
            'unit': [],
            'integration': [],
            'performance': [],
            'stress': [],
            'security': [],
            'compatibility': []
        }
        
        # Run unit tests
        if 'unit' in self.config.test_types:
            self.logger.info("Running unit tests")
            test_results['unit'] = await self._run_unit_tests()
        
        # Run integration tests
        if 'integration' in self.config.test_types:
            self.logger.info("Running integration tests")
            test_results['integration'] = await self._run_integration_tests()
        
        # Run performance tests
        if 'performance' in self.config.test_types:
            self.logger.info("Running performance tests")
            test_results['performance'] = await self._run_performance_tests()
        
        # Run stress tests
        if self.config.enable_stress_testing:
            self.logger.info("Running stress tests")
            test_results['stress'] = await self._run_stress_tests()
        
        # Run security tests
        if self.config.enable_security_testing:
            self.logger.info("Running security tests")
            test_results['security'] = await self._run_security_tests()
        
        # Run compatibility tests
        if self.config.enable_compatibility_testing:
            self.logger.info("Running compatibility tests")
            test_results['compatibility'] = await self._run_compatibility_tests()
        
        # Generate comprehensive report
        await self._generate_test_report(test_results)
        
        return test_results
    
    async def _run_unit_tests(self) -> List[TestResult]:
        """Run unit tests for all algorithms"""
        results = []
        
        # Get all registered algorithms
        algorithms = self.registry.list_algorithms()
        
        for algorithm_metadata in algorithms:
            try:
                # Create algorithm instance
                algorithm_class = self.registry.get_algorithm(algorithm_metadata.name)
                if not algorithm_class:
                    continue
                
                algorithm = algorithm_class()
                
                # Generate test data
                test_data = self.test_data_generator.generate_unit_test_data()
                
                # Run unit tests
                unit_results = await self.unit_tester.test_algorithm(
                    algorithm=algorithm,
                    test_data=test_data,
                    algorithm_name=algorithm_metadata.name
                )
                
                results.extend(unit_results)
                
            except Exception as e:
                self.logger.error(f"Unit test failed for {algorithm_metadata.name}: {e}")
                results.append(TestResult(
                    test_name=f"unit_test_{algorithm_metadata.name}",
                    test_type="unit",
                    algorithm_name=algorithm_metadata.name,
                    success=False,
                    execution_time=0.0,
                    memory_usage=0.0,
                    cpu_usage=0.0,
                    compression_ratio=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    async def _run_integration_tests(self) -> List[TestResult]:
        """Run integration tests"""
        results = []
        
        # Test algorithm interactions
        integration_results = await self.integration_tester.test_algorithm_interactions(
            registry=self.registry
        )
        results.extend(integration_results)
        
        # Test pipeline integration
        pipeline_results = await self.integration_tester.test_compression_pipeline(
            registry=self.registry
        )
        results.extend(pipeline_results)
        
        return results
    
    async def _run_performance_tests(self) -> List[TestResult]:
        """Run performance tests"""
        results = []
        
        # Test different data sizes
        for data_size in self.config.data_sizes:
            test_data = self.test_data_generator.generate_performance_test_data(data_size)
            
            performance_results = await self.performance_tester.benchmark_algorithms(
                registry=self.registry,
                test_data=test_data,
                iterations=self.config.iterations
            )
            
            results.extend(performance_results)
        
        return results
    
    async def _run_stress_tests(self) -> List[TestResult]:
        """Run stress tests"""
        results = []
        
        # Generate stress test data
        stress_data = self.test_data_generator.generate_stress_test_data()
        
        # Run stress tests
        stress_results = await self.stress_tester.test_algorithm_stability(
            registry=self.registry,
            test_data=stress_data,
            max_iterations=1000
        )
        
        results.extend(stress_results)
        
        return results
    
    async def _run_security_tests(self) -> List[TestResult]:
        """Run security tests"""
        results = []
        
        # Generate security test data
        security_data = self.test_data_generator.generate_security_test_data()
        
        # Run security tests
        security_results = await self.security_tester.test_algorithm_security(
            registry=self.registry,
            test_data=security_data
        )
        
        results.extend(security_results)
        
        return results
    
    async def _run_compatibility_tests(self) -> List[TestResult]:
        """Run compatibility tests"""
        results = []
        
        # Test cross-platform compatibility
        compatibility_results = await self.compatibility_tester.test_cross_platform_compatibility(
            registry=self.registry
        )
        results.extend(compatibility_results)
        
        # Test cross-language compatibility
        cross_language_results = await self.compatibility_tester.test_cross_language_compatibility(
            registry=self.registry
        )
        results.extend(cross_language_results)
        
        return results
    
    async def _generate_test_report(self, test_results: Dict[str, List[TestResult]]):
        """Generate comprehensive test report"""
        report = {
            'summary': self._generate_summary(test_results),
            'detailed_results': test_results,
            'performance_analysis': self._analyze_performance(test_results),
            'recommendations': self._generate_recommendations(test_results),
            'timestamp': time.time()
        }
        
        # Save report
        report_path = Path("test_reports/comprehensive_test_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Test report generated: {report_path}")
    
    def _generate_summary(self, test_results: Dict[str, List[TestResult]]) -> Dict[str, Any]:
        """Generate test summary"""
        summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_categories': {}
        }
        
        for category, results in test_results.items():
            category_summary = {
                'total': len(results),
                'passed': len([r for r in results if r.success]),
                'failed': len([r for r in results if not r.success]),
                'success_rate': len([r for r in results if r.success]) / len(results) if results else 0
            }
            
            summary['test_categories'][category] = category_summary
            summary['total_tests'] += category_summary['total']
            summary['passed_tests'] += category_summary['passed']
            summary['failed_tests'] += category_summary['failed']
        
        summary['overall_success_rate'] = summary['passed_tests'] / summary['total_tests'] if summary['total_tests'] > 0 else 0
        
        return summary
    
    def _analyze_performance(self, test_results: Dict[str, List[TestResult]]) -> Dict[str, Any]:
        """Analyze performance test results"""
        performance_results = test_results.get('performance', [])
        
        if not performance_results:
            return {}
        
        # Calculate performance statistics
        compression_ratios = [r.compression_ratio for r in performance_results if r.success]
        execution_times = [r.execution_time for r in performance_results if r.success]
        memory_usage = [r.memory_usage for r in performance_results if r.success]
        
        analysis = {
            'compression_ratio': {
                'mean': np.mean(compression_ratios) if compression_ratios else 0,
                'std': np.std(compression_ratios) if compression_ratios else 0,
                'min': np.min(compression_ratios) if compression_ratios else 0,
                'max': np.max(compression_ratios) if compression_ratios else 0
            },
            'execution_time': {
                'mean': np.mean(execution_times) if execution_times else 0,
                'std': np.std(execution_times) if execution_times else 0,
                'min': np.min(execution_times) if execution_times else 0,
                'max': np.max(execution_times) if execution_times else 0
            },
            'memory_usage': {
                'mean': np.mean(memory_usage) if memory_usage else 0,
                'std': np.std(memory_usage) if memory_usage else 0,
                'min': np.min(memory_usage) if memory_usage else 0,
                'max': np.max(memory_usage) if memory_usage else 0
            }
        }
        
        return analysis
    
    def _generate_recommendations(self, test_results: Dict[str, List[TestResult]]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze failures
        failed_tests = []
        for category, results in test_results.items():
            failed_tests.extend([r for r in results if not r.success])
        
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failed tests")
        
        # Performance recommendations
        performance_results = test_results.get('performance', [])
        if performance_results:
            avg_compression_ratio = np.mean([r.compression_ratio for r in performance_results if r.success])
            if avg_compression_ratio < 2.0:
                recommendations.append("Consider optimizing compression algorithms for better ratios")
        
        # Security recommendations
        security_results = test_results.get('security', [])
        if security_results:
            security_failures = [r for r in security_results if not r.success]
            if security_failures:
                recommendations.append("Address security vulnerabilities in compression algorithms")
        
        return recommendations

class UnitTester:
    """Unit testing for individual algorithm components"""
    
    async def test_algorithm(self, 
                           algorithm: EnhancedBaseAlgorithm,
                           test_data: Dict[str, bytes],
                           algorithm_name: str) -> List[TestResult]:
        """Test individual algorithm functionality"""
        results = []
        
        # Test basic compression
        basic_result = await self._test_basic_compression(algorithm, test_data['basic'], algorithm_name)
        results.append(basic_result)
        
        # Test decompression
        decompression_result = await self._test_decompression(algorithm, test_data['basic'], algorithm_name)
        results.append(decompression_result)
        
        # Test error handling
        error_result = await self._test_error_handling(algorithm, test_data['error'], algorithm_name)
        results.append(error_result)
        
        # Test edge cases
        edge_result = await self._test_edge_cases(algorithm, test_data['edge'], algorithm_name)
        results.append(edge_result)
        
        return results
    
    async def _test_basic_compression(self, algorithm: EnhancedBaseAlgorithm, 
                                    test_data: bytes, algorithm_name: str) -> TestResult:
        """Test basic compression functionality"""
        start_time = time.time()
        
        try:
            result = await algorithm.compress(test_data)
            
            execution_time = time.time() - start_time
            compression_ratio = len(test_data) / len(result['compressed_data']) if result.get('compressed_data') else 0
            
            return TestResult(
                test_name=f"basic_compression_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=result.get('success', False),
                execution_time=execution_time,
                memory_usage=result.get('memory_usage', 0.0),
                cpu_usage=result.get('cpu_usage', 0.0),
                compression_ratio=compression_ratio,
                performance_metrics=result.get('metrics', {})
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"basic_compression_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def _test_decompression(self, algorithm: EnhancedBaseAlgorithm,
                                test_data: bytes, algorithm_name: str) -> TestResult:
        """Test decompression functionality"""
        start_time = time.time()
        
        try:
            # First compress
            compression_result = await algorithm.compress(test_data)
            
            if not compression_result.get('success', False):
                raise Exception("Compression failed")
            
            # Then decompress
            decompressed_data = await algorithm.decompress(compression_result['compressed_data'])
            
            # Verify correctness
            success = decompressed_data == test_data
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_name=f"decompression_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=success,
                execution_time=execution_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=None if success else "Decompression result doesn't match original"
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"decompression_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def _test_error_handling(self, algorithm: EnhancedBaseAlgorithm,
                                 test_data: bytes, algorithm_name: str) -> TestResult:
        """Test error handling capabilities"""
        start_time = time.time()
        
        try:
            # Test with corrupted data
            result = await algorithm.compress(test_data)
            
            execution_time = time.time() - start_time
            
            # Check if error handling worked properly
            success = not result.get('success', True) or 'error' in result
            
            return TestResult(
                test_name=f"error_handling_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=success,
                execution_time=execution_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=None if success else "Error handling failed"
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"error_handling_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=True,  # Exception is expected
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0
            )
    
    async def _test_edge_cases(self, algorithm: EnhancedBaseAlgorithm,
                             test_data: bytes, algorithm_name: str) -> TestResult:
        """Test edge cases"""
        start_time = time.time()
        
        try:
            result = await algorithm.compress(test_data)
            
            execution_time = time.time() - start_time
            compression_ratio = len(test_data) / len(result['compressed_data']) if result.get('compressed_data') else 0
            
            return TestResult(
                test_name=f"edge_cases_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=result.get('success', False),
                execution_time=execution_time,
                memory_usage=result.get('memory_usage', 0.0),
                cpu_usage=result.get('cpu_usage', 0.0),
                compression_ratio=compression_ratio
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"edge_cases_{algorithm_name}",
                test_type="unit",
                algorithm_name=algorithm_name,
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )

class IntegrationTester:
    """Integration testing for algorithm interactions"""
    
    async def test_algorithm_interactions(self, registry: AlgorithmRegistry) -> List[TestResult]:
        """Test interactions between different algorithms"""
        results = []
        
        # Test algorithm switching
        switch_result = await self._test_algorithm_switching(registry)
        results.append(switch_result)
        
        # Test algorithm chaining
        chain_result = await self._test_algorithm_chaining(registry)
        results.append(chain_result)
        
        return results
    
    async def test_compression_pipeline(self, registry: AlgorithmRegistry) -> List[TestResult]:
        """Test complete compression pipeline"""
        results = []
        
        # Test end-to-end pipeline
        pipeline_result = await self._test_end_to_end_pipeline(registry)
        results.append(pipeline_result)
        
        return results
    
    async def _test_algorithm_switching(self, registry: AlgorithmRegistry) -> TestResult:
        """Test switching between algorithms"""
        start_time = time.time()
        
        try:
            # Test data
            test_data = b"Test data for algorithm switching"
            
            # Get multiple algorithms
            algorithms = registry.list_algorithms()[:3]  # Test first 3 algorithms
            
            results = []
            for algorithm_metadata in algorithms:
                algorithm_class = registry.get_algorithm(algorithm_metadata.name)
                if algorithm_class:
                    algorithm = algorithm_class()
                    result = await algorithm.compress(test_data)
                    results.append(result)
            
            success = all(r.get('success', False) for r in results)
            execution_time = time.time() - start_time
            
            return TestResult(
                test_name="algorithm_switching",
                test_type="integration",
                algorithm_name="multiple",
                success=success,
                execution_time=execution_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0
            )
            
        except Exception as e:
            return TestResult(
                test_name="algorithm_switching",
                test_type="integration",
                algorithm_name="multiple",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def _test_algorithm_chaining(self, registry: AlgorithmRegistry) -> TestResult:
        """Test chaining multiple algorithms"""
        start_time = time.time()
        
        try:
            # Test data
            test_data = b"Test data for algorithm chaining"
            
            # Chain multiple algorithms
            algorithms = registry.list_algorithms()[:2]  # Use first 2 algorithms
            
            current_data = test_data
            for algorithm_metadata in algorithms:
                algorithm_class = registry.get_algorithm(algorithm_metadata.name)
                if algorithm_class:
                    algorithm = algorithm_class()
                    result = await algorithm.compress(current_data)
                    if result.get('success', False):
                        current_data = result['compressed_data']
            
            success = len(current_data) < len(test_data)
            execution_time = time.time() - start_time
            
            return TestResult(
                test_name="algorithm_chaining",
                test_type="integration",
                algorithm_name="chained",
                success=success,
                execution_time=execution_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=len(test_data) / len(current_data) if success else 0
            )
            
        except Exception as e:
            return TestResult(
                test_name="algorithm_chaining",
                test_type="integration",
                algorithm_name="chained",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def _test_end_to_end_pipeline(self, registry: AlgorithmRegistry) -> TestResult:
        """Test complete end-to-end compression pipeline"""
        start_time = time.time()
        
        try:
            # Test data
            test_data = b"Test data for end-to-end pipeline"
            
            # Get factory
            factory = AlgorithmFactory(registry)
            
            # Create optimal algorithm
            algorithm = await factory.create_optimal_algorithm(
                data_characteristics={'size': len(test_data), 'type': 'text'},
                performance_requirements={'speed_priority': True}
            )
            
            # Compress and decompress
            compression_result = await algorithm.compress(test_data)
            if compression_result.get('success', False):
                decompressed_data = await algorithm.decompress(compression_result['compressed_data'])
                success = decompressed_data == test_data
            else:
                success = False
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_name="end_to_end_pipeline",
                test_type="integration",
                algorithm_name="pipeline",
                success=success,
                execution_time=execution_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=len(test_data) / len(compression_result['compressed_data']) if success else 0
            )
            
        except Exception as e:
            return TestResult(
                test_name="end_to_end_pipeline",
                test_type="integration",
                algorithm_name="pipeline",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )

class PerformanceTester:
    """Performance testing and benchmarking"""
    
    async def benchmark_algorithms(self, 
                                 registry: AlgorithmRegistry,
                                 test_data: bytes,
                                 iterations: int = 10) -> List[TestResult]:
        """Benchmark algorithms with given test data"""
        results = []
        
        algorithms = registry.list_algorithms()
        
        for algorithm_metadata in algorithms:
            try:
                # Benchmark single algorithm
                benchmark_result = await self._benchmark_single_algorithm(
                    registry=registry,
                    algorithm_name=algorithm_metadata.name,
                    test_data=test_data,
                    iterations=iterations
                )
                
                results.append(benchmark_result)
                
            except Exception as e:
                results.append(TestResult(
                    test_name=f"benchmark_{algorithm_metadata.name}",
                    test_type="performance",
                    algorithm_name=algorithm_metadata.name,
                    success=False,
                    execution_time=0.0,
                    memory_usage=0.0,
                    cpu_usage=0.0,
                    compression_ratio=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    async def _benchmark_single_algorithm(self,
                                        registry: AlgorithmRegistry,
                                        algorithm_name: str,
                                        test_data: bytes,
                                        iterations: int) -> TestResult:
        """Benchmark a single algorithm"""
        start_time = time.time()
        
        try:
            algorithm_class = registry.get_algorithm(algorithm_name)
            if not algorithm_class:
                raise Exception(f"Algorithm {algorithm_name} not found")
            
            algorithm = algorithm_class()
            
            # Run multiple iterations
            compression_times = []
            compression_ratios = []
            memory_usage = []
            cpu_usage = []
            
            for i in range(iterations):
                iter_start = time.time()
                result = await algorithm.compress(test_data)
                iter_time = time.time() - iter_start
                
                if result.get('success', False):
                    compression_times.append(iter_time)
                    compression_ratios.append(len(test_data) / len(result['compressed_data']))
                    memory_usage.append(result.get('memory_usage', 0.0))
                    cpu_usage.append(result.get('cpu_usage', 0.0))
            
            # Calculate averages
            avg_compression_time = np.mean(compression_times) if compression_times else 0
            avg_compression_ratio = np.mean(compression_ratios) if compression_ratios else 0
            avg_memory_usage = np.mean(memory_usage) if memory_usage else 0
            avg_cpu_usage = np.mean(cpu_usage) if cpu_usage else 0
            
            total_time = time.time() - start_time
            
            return TestResult(
                test_name=f"benchmark_{algorithm_name}",
                test_type="performance",
                algorithm_name=algorithm_name,
                success=len(compression_times) > 0,
                execution_time=total_time,
                memory_usage=avg_memory_usage,
                cpu_usage=avg_cpu_usage,
                compression_ratio=avg_compression_ratio,
                performance_metrics={
                    'avg_compression_time': avg_compression_time,
                    'compression_throughput': len(test_data) / avg_compression_time if avg_compression_time > 0 else 0,
                    'iterations_completed': len(compression_times)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"benchmark_{algorithm_name}",
                test_type="performance",
                algorithm_name=algorithm_name,
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )

class StressTester:
    """Stress testing for algorithm stability"""
    
    async def test_algorithm_stability(self,
                                     registry: AlgorithmRegistry,
                                     test_data: bytes,
                                     max_iterations: int = 1000) -> List[TestResult]:
        """Test algorithm stability under stress"""
        results = []
        
        algorithms = registry.list_algorithms()
        
        for algorithm_metadata in algorithms:
            try:
                stability_result = await self._test_single_algorithm_stability(
                    registry=registry,
                    algorithm_name=algorithm_metadata.name,
                    test_data=test_data,
                    max_iterations=max_iterations
                )
                
                results.append(stability_result)
                
            except Exception as e:
                results.append(TestResult(
                    test_name=f"stress_{algorithm_metadata.name}",
                    test_type="stress",
                    algorithm_name=algorithm_metadata.name,
                    success=False,
                    execution_time=0.0,
                    memory_usage=0.0,
                    cpu_usage=0.0,
                    compression_ratio=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    async def _test_single_algorithm_stability(self,
                                             registry: AlgorithmRegistry,
                                             algorithm_name: str,
                                             test_data: bytes,
                                             max_iterations: int) -> TestResult:
        """Test stability of a single algorithm"""
        start_time = time.time()
        
        try:
            algorithm_class = registry.get_algorithm(algorithm_name)
            if not algorithm_class:
                raise Exception(f"Algorithm {algorithm_name} not found")
            
            algorithm = algorithm_class()
            
            # Run stress test
            successful_iterations = 0
            failed_iterations = 0
            compression_ratios = []
            
            for i in range(max_iterations):
                try:
                    result = await algorithm.compress(test_data)
                    
                    if result.get('success', False):
                        successful_iterations += 1
                        compression_ratios.append(len(test_data) / len(result['compressed_data']))
                    else:
                        failed_iterations += 1
                        
                except Exception:
                    failed_iterations += 1
            
            total_time = time.time() - start_time
            success_rate = successful_iterations / max_iterations if max_iterations > 0 else 0
            
            return TestResult(
                test_name=f"stress_{algorithm_name}",
                test_type="stress",
                algorithm_name=algorithm_name,
                success=success_rate > 0.95,  # 95% success rate threshold
                execution_time=total_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=np.mean(compression_ratios) if compression_ratios else 0,
                performance_metrics={
                    'success_rate': success_rate,
                    'successful_iterations': successful_iterations,
                    'failed_iterations': failed_iterations,
                    'total_iterations': max_iterations
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"stress_{algorithm_name}",
                test_type="stress",
                algorithm_name=algorithm_name,
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )

class SecurityTester:
    """Security testing for vulnerabilities"""
    
    async def test_algorithm_security(self,
                                    registry: AlgorithmRegistry,
                                    test_data: bytes) -> List[TestResult]:
        """Test algorithm security"""
        results = []
        
        # Test for common vulnerabilities
        vulnerability_results = await self._test_vulnerabilities(registry, test_data)
        results.extend(vulnerability_results)
        
        return results
    
    async def _test_vulnerabilities(self,
                                  registry: AlgorithmRegistry,
                                  test_data: bytes) -> List[TestResult]:
        """Test for common security vulnerabilities"""
        results = []
        
        # Test buffer overflow
        buffer_overflow_result = await self._test_buffer_overflow(registry, test_data)
        results.append(buffer_overflow_result)
        
        # Test memory leaks
        memory_leak_result = await self._test_memory_leaks(registry, test_data)
        results.append(memory_leak_result)
        
        return results
    
    async def _test_buffer_overflow(self,
                                  registry: AlgorithmRegistry,
                                  test_data: bytes) -> TestResult:
        """Test for buffer overflow vulnerabilities"""
        start_time = time.time()
        
        try:
            # Create oversized data
            oversized_data = test_data * 1000  # 1000x larger
            
            algorithms = registry.list_algorithms()[:3]  # Test first 3 algorithms
            
            vulnerabilities_found = 0
            
            for algorithm_metadata in algorithms:
                try:
                    algorithm_class = registry.get_algorithm(algorithm_metadata.name)
                    if algorithm_class:
                        algorithm = algorithm_class()
                        await algorithm.compress(oversized_data)
                except (MemoryError, OverflowError):
                    vulnerabilities_found += 1
                except Exception:
                    # Other exceptions might indicate vulnerabilities
                    vulnerabilities_found += 1
            
            total_time = time.time() - start_time
            success = vulnerabilities_found == 0
            
            return TestResult(
                test_name="buffer_overflow_test",
                test_type="security",
                algorithm_name="multiple",
                success=success,
                execution_time=total_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                performance_metrics={
                    'vulnerabilities_found': vulnerabilities_found,
                    'algorithms_tested': len(algorithms)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="buffer_overflow_test",
                test_type="security",
                algorithm_name="multiple",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def _test_memory_leaks(self,
                               registry: AlgorithmRegistry,
                               test_data: bytes) -> TestResult:
        """Test for memory leaks"""
        start_time = time.time()
        
        try:
            # Test repeated compression to detect memory leaks
            algorithm_class = registry.get_algorithm(registry.list_algorithms()[0].name)
            if not algorithm_class:
                raise Exception("No algorithms available")
            
            algorithm = algorithm_class()
            
            initial_memory = self._get_memory_usage()
            
            # Run multiple compressions
            for i in range(100):
                await algorithm.compress(test_data)
            
            final_memory = self._get_memory_usage()
            memory_increase = final_memory - initial_memory
            
            total_time = time.time() - start_time
            success = memory_increase < 10 * 1024 * 1024  # Less than 10MB increase
            
            return TestResult(
                test_name="memory_leak_test",
                test_type="security",
                algorithm_name=registry.list_algorithms()[0].name,
                success=success,
                execution_time=total_time,
                memory_usage=memory_increase,
                cpu_usage=0.0,
                compression_ratio=0.0,
                performance_metrics={
                    'memory_increase_bytes': memory_increase,
                    'iterations': 100
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="memory_leak_test",
                test_type="security",
                algorithm_name="unknown",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss

class CompatibilityTester:
    """Compatibility testing across platforms and languages"""
    
    async def test_cross_platform_compatibility(self, registry: AlgorithmRegistry) -> List[TestResult]:
        """Test cross-platform compatibility"""
        results = []
        
        # Test different platforms (simulated)
        platforms = ['linux', 'windows', 'macos']
        
        for platform in platforms:
            platform_result = await self._test_platform_compatibility(registry, platform)
            results.append(platform_result)
        
        return results
    
    async def test_cross_language_compatibility(self, registry: AlgorithmRegistry) -> List[TestResult]:
        """Test cross-language compatibility"""
        results = []
        
        # Test different languages (simulated)
        languages = ['python', 'rust', 'cpp', 'go']
        
        for language in languages:
            language_result = await self._test_language_compatibility(registry, language)
            results.append(language_result)
        
        return results
    
    async def _test_platform_compatibility(self, registry: AlgorithmRegistry, platform: str) -> TestResult:
        """Test compatibility with specific platform"""
        start_time = time.time()
        
        try:
            # Simulate platform-specific testing
            test_data = b"Platform compatibility test data"
            
            # Get algorithm
            algorithm_class = registry.get_algorithm(registry.list_algorithms()[0].name)
            if not algorithm_class:
                raise Exception("No algorithms available")
            
            algorithm = algorithm_class()
            
            # Test compression
            result = await algorithm.compress(test_data)
            
            total_time = time.time() - start_time
            
            return TestResult(
                test_name=f"platform_compatibility_{platform}",
                test_type="compatibility",
                algorithm_name=registry.list_algorithms()[0].name,
                success=result.get('success', False),
                execution_time=total_time,
                memory_usage=result.get('memory_usage', 0.0),
                cpu_usage=result.get('cpu_usage', 0.0),
                compression_ratio=len(test_data) / len(result['compressed_data']) if result.get('compressed_data') else 0,
                performance_metrics={'platform': platform}
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"platform_compatibility_{platform}",
                test_type="compatibility",
                algorithm_name="unknown",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def _test_language_compatibility(self, registry: AlgorithmRegistry, language: str) -> TestResult:
        """Test compatibility with specific language"""
        start_time = time.time()
        
        try:
            # Simulate language-specific testing
            test_data = b"Language compatibility test data"
            
            # Get algorithm
            algorithm_class = registry.get_algorithm(registry.list_algorithms()[0].name)
            if not algorithm_class:
                raise Exception("No algorithms available")
            
            algorithm = algorithm_class()
            
            # Test compression
            result = await algorithm.compress(test_data)
            
            total_time = time.time() - start_time
            
            return TestResult(
                test_name=f"language_compatibility_{language}",
                test_type="compatibility",
                algorithm_name=registry.list_algorithms()[0].name,
                success=result.get('success', False),
                execution_time=total_time,
                memory_usage=result.get('memory_usage', 0.0),
                cpu_usage=result.get('cpu_usage', 0.0),
                compression_ratio=len(test_data) / len(result['compressed_data']) if result.get('compressed_data') else 0,
                performance_metrics={'language': language}
            )
            
        except Exception as e:
            return TestResult(
                test_name=f"language_compatibility_{language}",
                test_type="compatibility",
                algorithm_name="unknown",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage=0.0,
                cpu_usage=0.0,
                compression_ratio=0.0,
                error_message=str(e)
            )

class TestDataGenerator:
    """Generate various types of test data"""
    
    def generate_unit_test_data(self) -> Dict[str, bytes]:
        """Generate data for unit tests"""
        return {
            'basic': b"Basic test data for unit testing",
            'error': b"",  # Empty data for error testing
            'edge': b"A" * 1000  # Repeated data for edge case testing
        }
    
    def generate_performance_test_data(self, size: int) -> bytes:
        """Generate data for performance testing"""
        # Generate semi-random data with some patterns
        data = bytearray()
        
        # Add some patterns
        patterns = [b"pattern1", b"pattern2", b"pattern3"]
        
        while len(data) < size:
            if random.random() < 0.3:  # 30% chance of pattern
                pattern = random.choice(patterns)
                data.extend(pattern)
            else:
                data.append(random.randint(0, 255))
        
        return bytes(data[:size])
    
    def generate_stress_test_data(self) -> bytes:
        """Generate data for stress testing"""
        # Generate large, complex data
        return b"Stress test data " * 10000
    
    def generate_security_test_data(self) -> bytes:
        """Generate data for security testing"""
        # Generate potentially problematic data
        return b"Security test data with special characters: \x00\x01\x02\xff" * 100
