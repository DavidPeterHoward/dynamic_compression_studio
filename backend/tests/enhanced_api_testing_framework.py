"""
Enhanced API Testing Framework for Dynamic Compression Algorithms

This module provides comprehensive automated testing capabilities including:
- Synthetic data generation for various content types
- Integration tests for all compression algorithms
- Performance benchmarking
- Meta-learning feature testing
- Advanced validation and error handling
"""

import asyncio
import json
import time
import random
import string
import base64
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import numpy as np
from PIL import Image
import io
import gzip
import lzma
import bz2
import lz4.frame
import zstandard as zstd
import brotli

from main import app
from app.core.compression_engine import CompressionEngine
from app.models.compression import (
    CompressionRequest, CompressionParameters, CompressionAlgorithm,
    CompressionLevel, ContentType, BatchCompressionRequest
)


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    success: bool
    duration: float
    algorithm: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SyntheticDataGenerator:
    """Generate synthetic test data for various content types."""
    
    def __init__(self):
        self.random_seed = 42
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
    
    def generate_text_data(self, size_kb: int = 10, content_type: str = "mixed") -> str:
        """Generate synthetic text data."""
        size_bytes = size_kb * 1024
        
        if content_type == "repetitive":
            # Highly repetitive text
            base_text = "The quick brown fox jumps over the lazy dog. "
            repetitions = size_bytes // len(base_text.encode('utf-8'))
            return base_text * repetitions
        
        elif content_type == "random":
            # Random text
            chars = string.ascii_letters + string.digits + " .,!?;:"
            return ''.join(random.choice(chars) for _ in range(size_bytes))
        
        elif content_type == "structured":
            # Structured data (JSON-like)
            data = []
            for i in range(size_bytes // 100):
                data.append({
                    "id": i,
                    "name": f"item_{i}",
                    "value": random.random(),
                    "description": f"Description for item {i} with some additional text"
                })
            return json.dumps(data, indent=2)
        
        elif content_type == "log_data":
            # Log-like data
            log_entries = []
            log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
            for i in range(size_bytes // 50):
                timestamp = f"2024-01-{random.randint(1, 31):02d} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                level = random.choice(log_levels)
                message = f"Log message {i} with some additional context and data"
                log_entries.append(f"[{timestamp}] {level}: {message}")
            return '\n'.join(log_entries)
        
        else:  # mixed
            # Mixed content
            content_parts = []
            remaining_size = size_bytes
            
            while remaining_size > 0:
                part_type = random.choice(["repetitive", "random", "structured", "log_data"])
                part_size = min(random.randint(1024, 4096), remaining_size)
                content_parts.append(self.generate_text_data(part_size // 1024, part_type))
                remaining_size -= len(content_parts[-1].encode('utf-8'))
            
            return '\n'.join(content_parts)
    
    def generate_binary_data(self, size_kb: int = 10, data_type: str = "random") -> bytes:
        """Generate synthetic binary data."""
        size_bytes = size_kb * 1024
        
        if data_type == "random":
            return bytes(random.getrandbits(8) for _ in range(size_bytes))
        
        elif data_type == "structured":
            # Structured binary data with patterns
            data = bytearray()
            for i in range(size_bytes // 4):
                # Add some structure and patterns
                data.extend(struct.pack('I', i))  # 4-byte integer
                data.extend(bytes([i % 256]))     # 1-byte pattern
            return bytes(data[:size_bytes])
        
        elif data_type == "image_like":
            # Image-like data with headers and patterns
            header = b"IMAGE_HEADER_v1.0"
            data = bytearray(header)
            data.extend(bytes(random.getrandbits(8) for _ in range(size_bytes - len(header))))
            return bytes(data)
        
        else:
            return bytes(random.getrandbits(8) for _ in range(size_bytes))
    
    def generate_json_data(self, size_kb: int = 10) -> str:
        """Generate synthetic JSON data."""
        data = {
            "metadata": {
                "version": "1.0",
                "timestamp": "2024-01-01T00:00:00Z",
                "generator": "synthetic_test_data"
            },
            "records": []
        }
        
        # Add records to reach target size
        target_size = size_kb * 1024
        current_size = len(json.dumps(data))
        
        while current_size < target_size:
            record = {
                "id": len(data["records"]),
                "name": f"record_{len(data['records'])}",
                "value": random.random(),
                "tags": [f"tag_{i}" for i in range(random.randint(1, 5))],
                "metadata": {
                    "created": "2024-01-01T00:00:00Z",
                    "updated": "2024-01-01T00:00:00Z",
                    "version": random.randint(1, 100)
                }
            }
            data["records"].append(record)
            current_size = len(json.dumps(data))
        
        return json.dumps(data, indent=2)


class CompressionAlgorithmTester:
    """Test individual compression algorithms."""
    
    def __init__(self, client: TestClient):
        self.client = client
        self.data_generator = SyntheticDataGenerator()
    
    def test_algorithm_basic(self, algorithm: str, content: str) -> TestResult:
        """Test basic compression with a specific algorithm."""
        start_time = time.time()
        
        try:
            request_data = {
                "content": content,
                "parameters": {
                    "algorithm": algorithm,
                    "level": "balanced"
                }
            }
            
            response = self.client.post("/api/v1/compression/compress", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                result = TestResult(
                    test_name=f"basic_{algorithm}",
                    success=True,
                    duration=time.time() - start_time,
                    algorithm=algorithm,
                    original_size=data["result"]["original_size"],
                    compressed_size=data["result"]["compressed_size"],
                    compression_ratio=data["result"]["compression_ratio"],
                    metadata={
                        "compression_time": data["result"]["compression_time"],
                        "quality_score": data["result"].get("quality_score", 0.0)
                    }
                )
            else:
                result = TestResult(
                    test_name=f"basic_{algorithm}",
                    success=False,
                    duration=time.time() - start_time,
                    algorithm=algorithm,
                    original_size=len(content.encode('utf-8')),
                    compressed_size=0,
                    compression_ratio=0.0,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            result = TestResult(
                test_name=f"basic_{algorithm}",
                success=False,
                duration=time.time() - start_time,
                algorithm=algorithm,
                original_size=len(content.encode('utf-8')),
                compressed_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            )
        
        return result
    
    def test_algorithm_parameters(self, algorithm: str, content: str, parameters: Dict[str, Any]) -> TestResult:
        """Test algorithm with specific parameters."""
        start_time = time.time()
        
        try:
            request_data = {
                "content": content,
                "parameters": {
                    "algorithm": algorithm,
                    **parameters
                }
            }
            
            response = self.client.post("/api/v1/compression/compress", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                result = TestResult(
                    test_name=f"parameterized_{algorithm}",
                    success=True,
                    duration=time.time() - start_time,
                    algorithm=algorithm,
                    original_size=data["result"]["original_size"],
                    compressed_size=data["result"]["compressed_size"],
                    compression_ratio=data["result"]["compression_ratio"],
                    metadata={
                        "parameters": parameters,
                        "compression_time": data["result"]["compression_time"],
                        "quality_score": data["result"].get("quality_score", 0.0)
                    }
                )
            else:
                result = TestResult(
                    test_name=f"parameterized_{algorithm}",
                    success=False,
                    duration=time.time() - start_time,
                    algorithm=algorithm,
                    original_size=len(content.encode('utf-8')),
                    compressed_size=0,
                    compression_ratio=0.0,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            result = TestResult(
                test_name=f"parameterized_{algorithm}",
                success=False,
                duration=time.time() - start_time,
                algorithm=algorithm,
                original_size=len(content.encode('utf-8')),
                compressed_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            )
        
        return result


class IntegrationTestSuite:
    """Comprehensive integration test suite."""
    
    def __init__(self, client: TestClient):
        self.client = client
        self.data_generator = SyntheticDataGenerator()
        self.algorithm_tester = CompressionAlgorithmTester(client)
        self.results: List[TestResult] = []
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests."""
        print("🚀 Starting Comprehensive Integration Tests...")
        
        test_suites = [
            self.test_health_endpoints,
            self.test_compression_algorithms,
            self.test_content_types,
            self.test_parameter_optimization,
            self.test_batch_compression,
            self.test_algorithm_comparison,
            self.test_meta_learning_features,
            self.test_error_handling,
            self.test_performance_benchmarks
        ]
        
        all_results = []
        for test_suite in test_suites:
            try:
                results = test_suite()
                all_results.extend(results)
                print(f"✅ Completed {test_suite.__name__}: {len(results)} tests")
            except Exception as e:
                print(f"❌ Failed {test_suite.__name__}: {str(e)}")
        
        return self.generate_test_report(all_results)
    
    def test_health_endpoints(self) -> List[TestResult]:
        """Test all health endpoints."""
        results = []
        
        # Test basic health
        start_time = time.time()
        response = self.client.get("/health")
        results.append(TestResult(
            test_name="health_basic",
            success=response.status_code == 200,
            duration=time.time() - start_time,
            algorithm="health",
            original_size=0,
            compressed_size=0,
            compression_ratio=0.0,
            metadata={"status_code": response.status_code}
        ))
        
        # Test detailed health
        start_time = time.time()
        response = self.client.get("/api/v1/health/detailed")
        results.append(TestResult(
            test_name="health_detailed",
            success=response.status_code == 200,
            duration=time.time() - start_time,
            algorithm="health",
            original_size=0,
            compressed_size=0,
            compression_ratio=0.0,
            metadata={"status_code": response.status_code}
        ))
        
        return results
    
    def test_compression_algorithms(self) -> List[TestResult]:
        """Test all available compression algorithms."""
        results = []
        
        # Get available algorithms
        response = self.client.get("/api/v1/compression/algorithms")
        if response.status_code != 200:
            return results
        
        algorithms_data = response.json()
        algorithms = [alg["name"] for alg in algorithms_data.get("algorithms", [])]
        
        # Test each algorithm with different content types
        content_types = ["repetitive", "random", "structured", "log_data"]
        
        for algorithm in algorithms:
            for content_type in content_types:
                content = self.data_generator.generate_text_data(5, content_type)
                result = self.algorithm_tester.test_algorithm_basic(algorithm, content)
                result.test_name = f"{algorithm}_{content_type}"
                results.append(result)
        
        return results
    
    def test_content_types(self) -> List[TestResult]:
        """Test different content types."""
        results = []
        
        # Test text content
        text_content = self.data_generator.generate_text_data(10, "mixed")
        result = self.algorithm_tester.test_algorithm_basic("content_aware", text_content)
        result.test_name = "content_type_text"
        results.append(result)
        
        # Test JSON content
        json_content = self.data_generator.generate_json_data(5)
        result = self.algorithm_tester.test_algorithm_basic("content_aware", json_content)
        result.test_name = "content_type_json"
        results.append(result)
        
        # Test binary content (base64 encoded)
        binary_content = self.data_generator.generate_binary_data(5, "random")
        binary_b64 = base64.b64encode(binary_content).decode('utf-8')
        result = self.algorithm_tester.test_algorithm_basic("content_aware", binary_b64)
        result.test_name = "content_type_binary"
        results.append(result)
        
        return results
    
    def test_parameter_optimization(self) -> List[TestResult]:
        """Test parameter optimization features."""
        results = []
        
        content = self.data_generator.generate_text_data(10, "mixed")
        
        # Test different optimization targets
        optimization_targets = ["ratio", "speed", "quality"]
        for target in optimization_targets:
            result = self.algorithm_tester.test_algorithm_parameters(
                "content_aware", 
                content, 
                {"optimization_target": target}
            )
            result.test_name = f"optimization_{target}"
            results.append(result)
        
        # Test different compression levels
        levels = ["fast", "balanced", "optimal", "maximum"]
        for level in levels:
            result = self.algorithm_tester.test_algorithm_parameters(
                "content_aware", 
                content, 
                {"level": level}
            )
            result.test_name = f"level_{level}"
            results.append(result)
        
        return results
    
    def test_batch_compression(self) -> List[TestResult]:
        """Test batch compression functionality."""
        results = []
        
        # Generate multiple content items
        contents = [
            self.data_generator.generate_text_data(2, "repetitive"),
            self.data_generator.generate_text_data(2, "random"),
            self.data_generator.generate_text_data(2, "structured"),
            self.data_generator.generate_json_data(2)
        ]
        
        start_time = time.time()
        try:
            request_data = {
                "contents": contents,
                "parameters": {
                    "algorithm": "content_aware",
                    "level": "balanced"
                }
            }
            
            response = self.client.post("/api/v1/compression/compress/batch", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                total_original = sum(item["original_size"] for item in data["results"])
                total_compressed = sum(item["compressed_size"] for item in data["results"])
                
                results.append(TestResult(
                    test_name="batch_compression",
                    success=True,
                    duration=time.time() - start_time,
                    algorithm="batch_content_aware",
                    original_size=total_original,
                    compressed_size=total_compressed,
                    compression_ratio=total_original / total_compressed if total_compressed > 0 else 0.0,
                    metadata={
                        "batch_size": len(contents),
                        "individual_results": data["results"]
                    }
                ))
            else:
                results.append(TestResult(
                    test_name="batch_compression",
                    success=False,
                    duration=time.time() - start_time,
                    algorithm="batch_content_aware",
                    original_size=sum(len(c.encode('utf-8')) for c in contents),
                    compressed_size=0,
                    compression_ratio=0.0,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                ))
        
        except Exception as e:
            results.append(TestResult(
                test_name="batch_compression",
                success=False,
                duration=time.time() - start_time,
                algorithm="batch_content_aware",
                original_size=sum(len(c.encode('utf-8')) for c in contents),
                compressed_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            ))
        
        return results
    
    def test_algorithm_comparison(self) -> List[TestResult]:
        """Test algorithm comparison functionality."""
        results = []
        
        content = self.data_generator.generate_text_data(10, "mixed")
        
        start_time = time.time()
        try:
            response = self.client.post(
                "/api/v1/compression/compare",
                params={"algorithms": ["gzip", "lzma", "zstandard"]},
                content=content
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append(TestResult(
                    test_name="algorithm_comparison",
                    success=True,
                    duration=time.time() - start_time,
                    algorithm="comparison",
                    original_size=data["results"][0]["original_size"],
                    compressed_size=min(r["compressed_size"] for r in data["results"]),
                    compression_ratio=max(r["compression_ratio"] for r in data["results"]),
                    metadata={
                        "winner": data.get("winner"),
                        "comparison_metrics": data.get("comparison_metrics"),
                        "all_results": data["results"]
                    }
                ))
            else:
                results.append(TestResult(
                    test_name="algorithm_comparison",
                    success=False,
                    duration=time.time() - start_time,
                    algorithm="comparison",
                    original_size=len(content.encode('utf-8')),
                    compressed_size=0,
                    compression_ratio=0.0,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                ))
        
        except Exception as e:
            results.append(TestResult(
                test_name="algorithm_comparison",
                success=False,
                duration=time.time() - start_time,
                algorithm="comparison",
                original_size=len(content.encode('utf-8')),
                compressed_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            ))
        
        return results
    
    def test_meta_learning_features(self) -> List[TestResult]:
        """Test meta-learning and adaptive features."""
        results = []
        
        # Test content analysis
        content = self.data_generator.generate_text_data(10, "mixed")
        
        start_time = time.time()
        try:
            response = self.client.get(
                "/api/v1/compression/analyze",
                params={"content": content}
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append(TestResult(
                    test_name="content_analysis",
                    success=True,
                    duration=time.time() - start_time,
                    algorithm="analysis",
                    original_size=len(content.encode('utf-8')),
                    compressed_size=0,
                    compression_ratio=0.0,
                    metadata={
                        "entropy": data.get("entropy"),
                        "content_type": data.get("content_type"),
                        "patterns": data.get("patterns"),
                        "recommendations": data.get("recommendations")
                    }
                ))
            else:
                results.append(TestResult(
                    test_name="content_analysis",
                    success=False,
                    duration=time.time() - start_time,
                    algorithm="analysis",
                    original_size=len(content.encode('utf-8')),
                    compressed_size=0,
                    compression_ratio=0.0,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                ))
        
        except Exception as e:
            results.append(TestResult(
                test_name="content_analysis",
                success=False,
                duration=time.time() - start_time,
                algorithm="analysis",
                original_size=len(content.encode('utf-8')),
                compressed_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            ))
        
        # Test parameter recommendations
        start_time = time.time()
        try:
            response = self.client.get("/api/v1/compression/parameters/content_aware")
            
            if response.status_code == 200:
                data = response.json()
                results.append(TestResult(
                    test_name="parameter_recommendations",
                    success=True,
                    duration=time.time() - start_time,
                    algorithm="content_aware",
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    metadata={
                        "parameters": data.get("parameters"),
                        "use_cases": data.get("use_cases")
                    }
                ))
            else:
                results.append(TestResult(
                    test_name="parameter_recommendations",
                    success=False,
                    duration=time.time() - start_time,
                    algorithm="content_aware",
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                ))
        
        except Exception as e:
            results.append(TestResult(
                test_name="parameter_recommendations",
                success=False,
                duration=time.time() - start_time,
                algorithm="content_aware",
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            ))
        
        return results
    
    def test_error_handling(self) -> List[TestResult]:
        """Test error handling and edge cases."""
        results = []
        
        # Test empty content
        result = self.algorithm_tester.test_algorithm_basic("gzip", "")
        result.test_name = "error_empty_content"
        results.append(result)
        
        # Test very large content
        large_content = self.data_generator.generate_text_data(1000, "random")
        result = self.algorithm_tester.test_algorithm_basic("gzip", large_content)
        result.test_name = "error_large_content"
        results.append(result)
        
        # Test invalid algorithm
        content = self.data_generator.generate_text_data(5, "mixed")
        result = self.algorithm_tester.test_algorithm_parameters(
            "invalid_algorithm", 
            content, 
            {"level": "balanced"}
        )
        result.test_name = "error_invalid_algorithm"
        results.append(result)
        
        # Test invalid parameters
        result = self.algorithm_tester.test_algorithm_parameters(
            "gzip", 
            content, 
            {"level": 999}  # Invalid level
        )
        result.test_name = "error_invalid_parameters"
        results.append(result)
        
        return results
    
    def test_performance_benchmarks(self) -> List[TestResult]:
        """Test performance benchmarks."""
        results = []
        
        # Test different content sizes
        sizes = [1, 5, 10, 50, 100]  # KB
        algorithms = ["gzip", "lzma", "zstandard", "content_aware"]
        
        for size in sizes:
            for algorithm in algorithms:
                content = self.data_generator.generate_text_data(size, "mixed")
                result = self.algorithm_tester.test_algorithm_basic(algorithm, content)
                result.test_name = f"benchmark_{algorithm}_{size}kb"
                results.append(result)
        
        return results
    
    def generate_test_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Calculate statistics
        successful_results = [r for r in results if r.success]
        
        if successful_results:
            avg_compression_ratio = sum(r.compression_ratio for r in successful_results) / len(successful_results)
            avg_duration = sum(r.duration for r in successful_results) / len(successful_results)
            best_compression_ratio = max(r.compression_ratio for r in successful_results)
            fastest_algorithm = min(successful_results, key=lambda x: x.duration)
        else:
            avg_compression_ratio = 0.0
            avg_duration = 0.0
            best_compression_ratio = 0.0
            fastest_algorithm = None
        
        # Group by algorithm
        algorithm_stats = {}
        for result in successful_results:
            if result.algorithm not in algorithm_stats:
                algorithm_stats[result.algorithm] = []
            algorithm_stats[result.algorithm].append(result)
        
        algorithm_summary = {}
        for alg, alg_results in algorithm_stats.items():
            algorithm_summary[alg] = {
                "count": len(alg_results),
                "avg_compression_ratio": sum(r.compression_ratio for r in alg_results) / len(alg_results),
                "avg_duration": sum(r.duration for r in alg_results) / len(alg_results),
                "best_compression_ratio": max(r.compression_ratio for r in alg_results),
                "fastest_test": min(alg_results, key=lambda x: x.duration).test_name
            }
        
        # Failed tests analysis
        failed_tests_analysis = []
        for result in results:
            if not result.success:
                failed_tests_analysis.append({
                    "test_name": result.test_name,
                    "algorithm": result.algorithm,
                    "error_message": result.error_message
                })
        
        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0.0
            },
            "performance": {
                "avg_compression_ratio": avg_compression_ratio,
                "avg_duration": avg_duration,
                "best_compression_ratio": best_compression_ratio,
                "fastest_algorithm": fastest_algorithm.algorithm if fastest_algorithm else None
            },
            "algorithm_summary": algorithm_summary,
            "failed_tests": failed_tests_analysis,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "algorithm": r.algorithm,
                    "compression_ratio": r.compression_ratio,
                    "duration": r.duration,
                    "error_message": r.error_message,
                    "metadata": r.metadata
                }
                for r in results
            ]
        }


class AutomatedTestRunner:
    """Automated test runner with reporting capabilities."""
    
    def __init__(self, client: TestClient):
        self.client = client
        self.integration_suite = IntegrationTestSuite(client)
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite."""
        print("🎯 Starting Automated Test Suite...")
        print("=" * 60)
        
        # Run comprehensive tests
        results = self.integration_suite.run_comprehensive_tests()
        
        # Generate report
        report = self.generate_final_report(results)
        
        # Save report
        self.save_test_report(report)
        
        return report
    
    def generate_final_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final test report with recommendations."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": results,
            "recommendations": self.generate_recommendations(results),
            "meta_learning_status": self.check_meta_learning_status(results),
            "api_health_status": self.check_api_health_status(results)
        }
        
        return report
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        summary = results.get("summary", {})
        success_rate = summary.get("success_rate", 0.0)
        
        if success_rate < 90.0:
            recommendations.append(f"⚠️ Test success rate is {success_rate:.1f}%. Investigate failed tests.")
        
        if summary.get("failed_tests", 0) > 0:
            recommendations.append("🔧 Review failed tests and fix underlying issues.")
        
        algorithm_summary = results.get("algorithm_summary", {})
        if len(algorithm_summary) < 5:
            recommendations.append("📈 Expand algorithm coverage - some algorithms may not be properly implemented.")
        
        performance = results.get("performance", {})
        if performance.get("avg_compression_ratio", 0.0) < 2.0:
            recommendations.append("⚡ Compression ratios are lower than expected. Review algorithm implementations.")
        
        return recommendations
    
    def check_meta_learning_status(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Check meta-learning feature status."""
        detailed_results = results.get("detailed_results", [])
        
        meta_learning_tests = [
            r for r in detailed_results 
            if "analysis" in r["test_name"] or "recommendations" in r["test_name"]
        ]
        
        successful_meta_tests = [r for r in meta_learning_tests if r["success"]]
        
        return {
            "total_meta_tests": len(meta_learning_tests),
            "successful_meta_tests": len(successful_meta_tests),
            "meta_learning_ready": len(successful_meta_tests) >= 2,
            "features_available": [
                "content_analysis" if any("analysis" in r["test_name"] and r["success"] for r in detailed_results) else None,
                "parameter_recommendations" if any("recommendations" in r["test_name"] and r["success"] for r in detailed_results) else None,
                "adaptive_selection" if any("content_aware" in r["algorithm"] and r["success"] for r in detailed_results) else None
            ]
        }
    
    def check_api_health_status(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Check overall API health status."""
        detailed_results = results.get("detailed_results", [])
        
        health_tests = [r for r in detailed_results if "health" in r["test_name"]]
        compression_tests = [r for r in detailed_results if "compression" in r["test_name"] and r["success"]]
        
        return {
            "health_endpoints_working": all(r["success"] for r in health_tests),
            "compression_endpoints_working": len(compression_tests) > 0,
            "api_ready": all(r["success"] for r in health_tests) and len(compression_tests) > 0
        }
    
    def save_test_report(self, report: Dict[str, Any]):
        """Save test report to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_reports/comprehensive_test_report_{timestamp}.json"
        
        # Ensure directory exists
        import os
        os.makedirs("test_reports", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Test report saved to: {filename}")


# Pytest test functions
def test_comprehensive_integration(client):
    """Comprehensive integration test."""
    runner = AutomatedTestRunner(client)
    report = runner.run_full_test_suite()
    
    # Assertions
    assert report["test_results"]["summary"]["success_rate"] > 80.0, "Test success rate should be above 80%"
    assert report["meta_learning_status"]["meta_learning_ready"], "Meta-learning features should be ready"
    assert report["api_health_status"]["api_ready"], "API should be ready for use"


def test_synthetic_data_generation():
    """Test synthetic data generation."""
    generator = SyntheticDataGenerator()
    
    # Test text generation
    text = generator.generate_text_data(5, "mixed")
    assert len(text.encode('utf-8')) > 4000, "Generated text should be close to 5KB"
    
    # Test JSON generation
    json_data = generator.generate_json_data(5)
    assert len(json_data.encode('utf-8')) > 4000, "Generated JSON should be close to 5KB"
    
    # Test binary generation
    binary_data = generator.generate_binary_data(5, "random")
    assert len(binary_data) > 4000, "Generated binary should be close to 5KB"


def test_algorithm_tester(client):
    """Test algorithm tester functionality."""
    tester = CompressionAlgorithmTester(client)
    generator = SyntheticDataGenerator()
    
    content = generator.generate_text_data(5, "mixed")
    result = tester.test_algorithm_basic("gzip", content)
    
    assert result.test_name == "basic_gzip"
    assert result.algorithm == "gzip"
    assert result.original_size > 0
    assert result.duration >= 0


if __name__ == "__main__":
    # Run tests directly
    import sys
    from fastapi.testclient import TestClient
    
    # Create test client
    client = TestClient(app)
    
    # Run comprehensive tests
    runner = AutomatedTestRunner(client)
    report = runner.run_full_test_suite()
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['test_results']['summary']['total_tests']}")
    print(f"Successful: {report['test_results']['summary']['successful_tests']}")
    print(f"Failed: {report['test_results']['summary']['failed_tests']}")
    print(f"Success Rate: {report['test_results']['summary']['success_rate']:.1f}%")
    print(f"Meta-Learning Ready: {report['meta_learning_status']['meta_learning_ready']}")
    print(f"API Ready: {report['api_health_status']['api_ready']}")
    
    if report['recommendations']:
        print("\n📋 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
    
    print("\n" + "=" * 60)
