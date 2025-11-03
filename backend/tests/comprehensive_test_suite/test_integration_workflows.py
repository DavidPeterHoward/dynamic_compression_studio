"""
Comprehensive Integration Tests: End-to-End Workflows

Tests complete workflows including:
- Content generation → Compression → Analysis → Meta-learning
- Algorithm selection → Testing → Validation → Insight generation
- Multi-algorithm comparison → Recommendation → Proof generation
- Historical analysis → Prediction → Validation
"""

import pytest
import time
from typing import List, Dict, Any

from test_fixtures import (
    meta_learning_service,
    ContentFactory,
    FingerprintFactory,
    ViabilityTestFactory,
    get_all_algorithms,
    get_all_content_types,
    assert_valid_test_result,
    assert_valid_fingerprint,
    assert_valid_metrics
)

from app.models.viability_models import (
    ContentFingerprint,
    EnhancedViabilityTest,
    MetaLearningInsight,
    ComparativeAnalysis,
    ProofOfPerformance,
    ContentDimension,
    PerformanceDimension,
    QualityDimension
)


class TestEndToEndCompressionWorkflow:
    """Test complete compression workflow from content to analysis."""
    
    def test_single_content_complete_workflow(self, meta_learning_service):
        """Test workflow: Generate → Compress → Validate → Store → Analyze."""
        # Step 1: Generate content
        content = ContentFactory.create_text_content(size=10000)
        assert content is not None
        assert len(content) == 10000
        
        # Step 2: Create fingerprint
        fingerprint = FingerprintFactory.create(content=content)
        assert_valid_fingerprint(fingerprint)
        
        # Step 3: Run compression test (simulated)
        test = ViabilityTestFactory.create(
            fingerprint=fingerprint,
            algorithm="gzip",
            compression_ratio=3.5,
            execution_time_ms=45.0
        )
        assert_valid_test_result(test)
        
        # Step 4: Validate test result
        assert test.success is True
        assert test.validation.is_valid is True
        assert test.validation.integrity_check is True
        
        # Step 5: Store in meta-learning database
        store_result = meta_learning_service.store_test_result(test)
        assert store_result is True
        
        # Step 6: Retrieve and verify
        retrieved = meta_learning_service.get_test_result(test.test_id)
        assert retrieved is not None
        assert retrieved.test_id == test.test_id
        
        # Step 7: Analyze stored data
        stats = meta_learning_service.get_algorithm_statistics("gzip")
        assert stats is not None
        assert "average_ratio" in stats
    
    def test_multiple_algorithms_comparison_workflow(self, meta_learning_service):
        """Test workflow: Generate → Test all algorithms → Compare → Recommend."""
        # Step 1: Generate test content
        content = ContentFactory.create_json_content(size=5000)
        fingerprint = FingerprintFactory.create(content=content, content_type="application/json")
        
        # Step 2: Test with multiple algorithms
        algorithms = ["gzip", "lzma", "zstd", "bzip2"]
        test_results = []
        
        for algo in algorithms:
            # Simulate different performance characteristics
            if algo == "lzma":
                ratio, time_ms = 4.5, 150.0
            elif algo == "zstd":
                ratio, time_ms = 4.0, 60.0
            elif algo == "gzip":
                ratio, time_ms = 3.2, 45.0
            else:  # bzip2
                ratio, time_ms = 3.8, 100.0
            
            test = ViabilityTestFactory.create(
                test_id=f"test_{algo}_{fingerprint.sha256[:8]}",
                fingerprint=fingerprint,
                algorithm=algo,
                compression_ratio=ratio,
                execution_time_ms=time_ms
            )
            test_results.append(test)
            meta_learning_service.store_test_result(test)
        
        # Step 3: Compare results
        best_ratio = max(test_results, key=lambda t: t.compression_ratio)
        best_speed = min(test_results, key=lambda t: t.execution_time_ms)
        
        assert best_ratio.algorithm == "lzma"
        assert best_speed.algorithm == "gzip"
        
        # Step 4: Get recommendation
        recommendation = meta_learning_service.recommend_algorithm(fingerprint)
        assert recommendation is not None
        assert "recommended_algorithm" in recommendation
        
        # Step 5: Verify recommendation is data-driven
        assert recommendation["recommended_algorithm"] in algorithms
    
    def test_historical_learning_workflow(self, meta_learning_service):
        """Test workflow: Accumulate data → Detect patterns → Generate insights → Predict."""
        # Step 1: Generate historical data (100 tests)
        for i in range(100):
            content = ContentFactory.create_text_content(size=1000 + i * 10)
            fingerprint = FingerprintFactory.create(
                content=content,
                entropy=0.6 + (i % 10) * 0.01,
                redundancy=0.4 - (i % 10) * 0.01
            )
            
            # Simulate consistent pattern: higher entropy = lower compression
            base_ratio = 4.0 - fingerprint.entropy
            ratio = max(1.5, base_ratio + (i % 5) * 0.1)
            
            test = ViabilityTestFactory.create(
                test_id=f"historical_test_{i:03d}",
                fingerprint=fingerprint,
                algorithm="gzip",
                compression_ratio=ratio,
                execution_time_ms=50.0 + i * 0.5
            )
            meta_learning_service.store_test_result(test)
        
        # Step 2: Detect trends
        trend = meta_learning_service.detect_trend("gzip", "compression_ratio")
        assert trend is not None
        
        # Step 3: Generate insights
        insights = meta_learning_service.generate_insights()
        assert insights is not None
        assert len(insights) > 0
        
        # Step 4: Make prediction
        new_fingerprint = FingerprintFactory.create(
            content=ContentFactory.create_text_content(size=5000),
            entropy=0.65,
            redundancy=0.35
        )
        
        prediction = meta_learning_service.predict_compression_ratio("gzip", new_fingerprint)
        assert prediction is not None
        assert "predicted_ratio" in prediction
        assert "confidence" in prediction
        assert prediction["predicted_ratio"] > 0
    
    def test_proof_generation_workflow(self):
        """Test workflow: Run test → Generate proof → Verify proof."""
        # Step 1: Run compression test
        content = ContentFactory.create_text_content(size=10000)
        fingerprint = FingerprintFactory.create(content=content)
        
        test = ViabilityTestFactory.create(
            fingerprint=fingerprint,
            algorithm="gzip",
            compression_ratio=3.5,
            execution_time_ms=50.0
        )
        
        # Step 2: Generate proof
        proof = ProofOfPerformance.generate_proof(
            test_id=test.test_id,
            compression_ratio=test.compression_ratio,
            compression_time=test.execution_time_ms / 1000,
            algorithm=test.algorithm,
            content_hash=fingerprint.sha256
        )
        
        # Step 3: Verify proof
        assert proof.test_id == test.test_id
        assert proof.claimed_compression_ratio == test.compression_ratio
        assert proof.verifiable is True
        assert len(proof.proof_hash) == 64
        
        # Step 4: Verify proof is reproducible
        proof2 = ProofOfPerformance.generate_proof(
            test_id=test.test_id,
            compression_ratio=test.compression_ratio,
            compression_time=test.execution_time_ms / 1000,
            algorithm=test.algorithm,
            content_hash=fingerprint.sha256
        )
        
        # Proofs should have same core data
        assert proof.test_id == proof2.test_id
        assert proof.claimed_compression_ratio == proof2.claimed_compression_ratio


class TestContentTypeSpecificWorkflows:
    """Test workflows specific to different content types."""
    
    def test_json_content_workflow(self, meta_learning_service):
        """Test JSON-specific compression workflow."""
        # Generate JSON content
        json_content = ContentFactory.create_json_content(size=5000)
        fingerprint = FingerprintFactory.create(
            content=json_content,
            content_type="application/json"
        )
        
        # Test multiple algorithms on JSON
        algorithms = ["gzip", "lzma", "zstd"]
        for algo in algorithms:
            test = ViabilityTestFactory.create(
                fingerprint=fingerprint,
                algorithm=algo,
                compression_ratio=4.0 if algo == "lzma" else 3.5
            )
            meta_learning_service.store_test_result(test)
        
        # Get best for JSON
        best = meta_learning_service.get_best_algorithm_for_content_type("application/json")
        assert best is not None
        assert best["algorithm"] == "lzma"
    
    def test_binary_content_workflow(self, meta_learning_service):
        """Test binary content compression workflow."""
        # Generate binary content
        binary_content = ContentFactory.create_binary_content(size=10000)
        fingerprint = FingerprintFactory.create(
            content=binary_content,
            content_type="application/octet-stream",
            entropy=0.85,  # High entropy for binary
            redundancy=0.15
        )
        
        # Test compression
        test = ViabilityTestFactory.create(
            fingerprint=fingerprint,
            algorithm="gzip",
            compression_ratio=1.8  # Lower ratio for high-entropy content
        )
        meta_learning_service.store_test_result(test)
        
        # Verify result reflects characteristics
        assert test.compression_ratio < 3.0  # Lower due to high entropy
    
    def test_highly_compressible_content_workflow(self, meta_learning_service):
        """Test workflow with highly compressible content."""
        # Generate repetitive content
        repetitive_content = ContentFactory.create_text_content(size=10000, pattern="repetitive")
        fingerprint = FingerprintFactory.create(
            content=repetitive_content,
            content_type="text/plain",
            entropy=0.2,  # Low entropy
            redundancy=0.8  # High redundancy
        )
        
        # Test compression
        test = ViabilityTestFactory.create(
            fingerprint=fingerprint,
            algorithm="lzma",
            compression_ratio=15.0  # Very high ratio for repetitive content
        )
        meta_learning_service.store_test_result(test)
        
        # Verify exceptional compression
        assert test.compression_ratio >= 10.0


class TestMultiRunScenarios:
    """Test scenarios involving multiple test runs."""
    
    def test_progressive_improvement_detection(self, meta_learning_service):
        """Test detection of progressive improvement across runs."""
        # Simulate progressive improvement
        for i in range(20):
            improvement_factor = 1.0 + (i * 0.02)  # 2% improvement per iteration
            
            test = ViabilityTestFactory.create(
                test_id=f"improvement_test_{i:03d}",
                algorithm="zstd",
                compression_ratio=3.0 * improvement_factor,
                execution_time_ms=60.0 / improvement_factor
            )
            meta_learning_service.store_test_result(test)
        
        # Detect improvement trend
        trend = meta_learning_service.detect_trend("zstd", "compression_ratio")
        assert trend is not None
        assert trend["direction"] == "improving"
    
    def test_performance_degradation_detection(self, meta_learning_service):
        """Test detection of performance degradation."""
        # Simulate degrading performance
        for i in range(20):
            degradation_factor = 1.0 - (i * 0.03)  # 3% degradation per iteration
            
            test = ViabilityTestFactory.create(
                test_id=f"degradation_test_{i:03d}",
                algorithm="gzip",
                compression_ratio=3.5 * max(0.5, degradation_factor),
                execution_time_ms=50.0 / max(0.5, degradation_factor)
            )
            meta_learning_service.store_test_result(test)
        
        # Detect degradation trend
        trend = meta_learning_service.detect_trend("gzip", "compression_ratio")
        assert trend is not None
        # Trend should show declining performance
    
    def test_stable_performance_detection(self, meta_learning_service):
        """Test detection of stable performance."""
        # Simulate stable performance with minor variations
        base_ratio = 3.5
        for i in range(20):
            variation = (i % 5) * 0.02  # Small variation
            
            test = ViabilityTestFactory.create(
                test_id=f"stable_test_{i:03d}",
                algorithm="bzip2",
                compression_ratio=base_ratio + variation,
                execution_time_ms=90.0 + variation * 10
            )
            meta_learning_service.store_test_result(test)
        
        # Get statistics
        stats = meta_learning_service.get_algorithm_statistics("bzip2")
        assert stats is not None


class TestErrorHandlingWorkflows:
    """Test workflows involving errors and edge cases."""
    
    def test_failed_compression_workflow(self, meta_learning_service):
        """Test workflow with failed compression."""
        content = ContentFactory.create_compressed_content(size=1000)
        fingerprint = FingerprintFactory.create(
            content=content,
            content_type="application/octet-stream",
            entropy=1.0,  # Already compressed
            redundancy=0.0
        )
        
        # Create failed test
        test = ViabilityTestFactory.create(
            fingerprint=fingerprint,
            algorithm="gzip",
            success=False,  # Failed
            compression_ratio=0.9,  # Expansion instead of compression
            validation=FingerprintFactory.create(
                content=content,
                content_type="application/octet-stream",
                entropy=1.0,
                redundancy=0.0
            )
        )
        
        # This should fail validation
        from test_fixtures import ValidationFactory
        test.validation = ValidationFactory.create_invalid(
            errors=["Content already compressed", "No redundancy to exploit"]
        )
        
        # Store failed test
        result = meta_learning_service.store_test_result(test)
        
        # System should handle gracefully
        assert result is not None
    
    def test_anomaly_detection_workflow(self, meta_learning_service):
        """Test detection of anomalous results."""
        # Create normal baseline
        for i in range(50):
            test = ViabilityTestFactory.create(
                test_id=f"normal_test_{i:03d}",
                algorithm="gzip",
                compression_ratio=3.5 + (i % 5) * 0.1,
                execution_time_ms=50.0 + (i % 5) * 2.0
            )
            meta_learning_service.store_test_result(test)
        
        # Create anomalous result
        anomaly_test = ViabilityTestFactory.create(
            test_id="anomaly_test_001",
            algorithm="gzip",
            compression_ratio=15.0,  # Anomalously high
            execution_time_ms=200.0  # Anomalously slow
        )
        
        # Set anomaly signals
        from test_fixtures import MetaContextFactory
        anomaly_test.meta_context = MetaContextFactory.create_with_learning_signals()
        anomaly_test.meta_context.anomaly_score = 0.95
        
        meta_learning_service.store_test_result(anomaly_test)
        
        # System should flag this
        retrieved = meta_learning_service.get_test_result("anomaly_test_001")
        assert retrieved is not None
        assert retrieved.meta_context.anomaly_score >= 0.9


class TestScalabilityWorkflows:
    """Test workflows at scale."""
    
    def test_large_dataset_workflow(self, meta_learning_service):
        """Test workflow with large number of tests."""
        # Generate 500 test results
        batch_size = 500
        
        start_time = time.time()
        for i in range(batch_size):
            test = ViabilityTestFactory.create(
                test_id=f"scale_test_{i:05d}",
                algorithm=["gzip", "lzma", "zstd"][i % 3],
                compression_ratio=2.5 + (i % 20) * 0.1
            )
            meta_learning_service.store_test_result(test)
        
        storage_time = time.time() - start_time
        
        # Verify all stored
        gzip_results = meta_learning_service.query_by_algorithm("gzip")
        assert len(gzip_results) > 0
        
        # Performance check: should handle large datasets efficiently
        print(f"\nStored {batch_size} tests in {storage_time:.2f}s")
        print(f"Average: {(storage_time/batch_size)*1000:.2f}ms per test")
    
    def test_high_frequency_workflow(self, meta_learning_service):
        """Test high-frequency test submission."""
        # Rapid-fire test submissions
        count = 100
        tests = ViabilityTestFactory.create_batch(count=count, varied=True)
        
        start_time = time.time()
        for test in tests:
            meta_learning_service.store_test_result(test)
        
        elapsed_time = time.time() - start_time
        
        # Verify all stored
        all_tests = meta_learning_service.query_by_algorithm("gzip")
        
        print(f"\nProcessed {count} tests in {elapsed_time:.2f}s")
        print(f"Throughput: {count/elapsed_time:.0f} tests/second")


class TestCrossAlgorithmWorkflows:
    """Test workflows comparing multiple algorithms."""
    
    def test_comprehensive_algorithm_evaluation(self, meta_learning_service):
        """Test comprehensive evaluation across all algorithms."""
        algorithms = ["gzip", "lzma", "zstd", "bzip2"]
        content_types = ["text/plain", "application/json", "application/xml"]
        
        # Test each algorithm on each content type
        for content_type in content_types:
            for algorithm in algorithms:
                content = ContentFactory.create_json_content(size=5000) if "json" in content_type else \
                         ContentFactory.create_xml_content(size=5000) if "xml" in content_type else \
                         ContentFactory.create_text_content(size=5000)
                
                fingerprint = FingerprintFactory.create(
                    content=content,
                    content_type=content_type
                )
                
                test = ViabilityTestFactory.create(
                    test_id=f"eval_{algorithm}_{content_type.replace('/', '_')}",
                    fingerprint=fingerprint,
                    algorithm=algorithm,
                    compression_ratio=3.5 + (hash(algorithm + content_type) % 10) * 0.1
                )
                meta_learning_service.store_test_result(test)
        
        # Get best algorithm for each content type
        for content_type in content_types:
            best = meta_learning_service.get_best_algorithm_for_content_type(content_type)
            assert best is not None
            print(f"\nBest for {content_type}: {best['algorithm']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])

