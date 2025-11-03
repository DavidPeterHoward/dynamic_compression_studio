#!/usr/bin/env python3
"""
Integration: Synthetic Data + Algorithm Viability Testing Workflow

This script demonstrates the complete workflow integration:
1. Generate synthetic data using SyntheticContentTab parameters
2. Run algorithm viability tests
3. Record results to meta-learning database
4. Provide continuous improvement feedback
5. Export results for visualization in frontend
"""

import asyncio
import sys
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

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


class SyntheticDataIntegrationWorkflow:
    """
    Integrated workflow connecting synthetic data generation with
    algorithm viability testing and meta-learning.
    """
    
    def __init__(self):
        self.data_generator = MockDataGenerator()
        self.compression_engine = CompressionEngine()
        self.meta_learning_service = get_meta_learning_service()
        self.workflow_id = str(uuid.uuid4())
    
    async def run_workflow(
        self,
        content_types: List[str] = None,
        complexity_levels: List[ContentComplexity] = None,
        algorithms: List[str] = None,
        export_for_frontend: bool = True
    ):
        """
        Run the complete integrated workflow.
        
        Args:
            content_types: Types of content to generate (default: all)
            complexity_levels: Complexity levels to test (default: all)
            algorithms: Algorithms to test (default: all traditional)
            export_for_frontend: Export results in frontend-compatible format
        """
        
        print("=" * 100)
        print("SYNTHETIC DATA + ALGORITHM VIABILITY INTEGRATION WORKFLOW")
        print("=" * 100)
        print(f"Workflow ID: {self.workflow_id}")
        print(f"Started: {datetime.utcnow().isoformat()}")
        print()
        
        # Step 1: Generate synthetic data
        print("STEP 1: Generating Synthetic Test Data")
        print("-" * 100)
        
        test_data = self._generate_synthetic_data(
            content_types=content_types or ['text', 'json', 'xml', 'log', 'code', 'csv', 'mixed'],
            complexity_levels=complexity_levels or list(ContentComplexity)
        )
        
        print(f"✓ Generated {len(test_data)} synthetic test cases")
        print(f"  Total size: {sum(tc.size_bytes for tc in test_data):,} bytes")
        print(f"  Content types: {set(tc.content_type for tc in test_data)}")
        print(f"  Complexity levels: {set(tc.complexity.value for tc in test_data)}")
        print()
        
        # Step 2: Run algorithm viability tests
        print("STEP 2: Running Algorithm Viability Tests")
        print("-" * 100)
        
        algorithm_list = algorithms or [
            'gzip', 'lzma', 'bzip2', 'lz4', 'zstd', 'brotli', 'content_aware'
        ]
        
        viability_results = await self._run_viability_tests(
            test_data=test_data,
            algorithms=algorithm_list
        )
        
        print(f"✓ Completed {sum(len(r) for r in viability_results.values())} compression tests")
        print(f"  Algorithms tested: {len(viability_results)}")
        print()
        
        # Step 3: Record to meta-learning database
        print("STEP 3: Recording Results to Meta-Learning Database")
        print("-" * 100)
        
        recorded_count = self._record_to_database(viability_results)
        print(f"✓ Recorded {recorded_count} test results to database")
        print()
        
        # Step 4: Generate insights and recommendations
        print("STEP 4: Generating Insights and Recommendations")
        print("-" * 100)
        
        insights = self._generate_insights(viability_results, test_data)
        self._record_insights(insights)
        
        print(f"✓ Generated {len(insights)} learning insights")
        for insight in insights[:5]:  # Show first 5
            print(f"  • {insight['type']}: {insight['summary']}")
        print()
        
        # Step 5: Export for frontend
        if export_for_frontend:
            print("STEP 5: Exporting Results for Frontend Visualization")
            print("-" * 100)
            
            export_path = self._export_for_frontend(viability_results, insights)
            print(f"✓ Exported results to: {export_path}")
            print()
        
        # Step 6: Database statistics
        print("STEP 6: Meta-Learning Database Statistics")
        print("-" * 100)
        
        db_stats = self.meta_learning_service.get_database_statistics()
        print(f"Total tests in database: {db_stats['total_tests']:,}")
        print(f"Success rate: {db_stats['success_rate']:.1f}%")
        print(f"Unique algorithms: {db_stats['unique_algorithms']}")
        print(f"Total learning insights: {db_stats['total_learning_insights']}")
        print()
        
        # Summary
        print("=" * 100)
        print("WORKFLOW COMPLETE - SUMMARY")
        print("=" * 100)
        
        self._print_summary(viability_results, insights)
        
        return {
            'workflow_id': self.workflow_id,
            'test_data_count': len(test_data),
            'viability_results': viability_results,
            'insights': insights,
            'database_stats': db_stats
        }
    
    def _generate_synthetic_data(
        self,
        content_types: List[str],
        complexity_levels: List[ContentComplexity]
    ):
        """Generate synthetic test data based on specifications."""
        test_data = []
        
        # Generate data for each content type and complexity combination
        for content_type in content_types:
            if content_type == 'text':
                test_data.append(self.data_generator.generate_natural_language_text(10))
            elif content_type == 'json':
                test_data.append(self.data_generator.generate_json_data(10))
            elif content_type == 'xml':
                test_data.append(self.data_generator.generate_xml_data(10))
            elif content_type == 'log':
                test_data.append(self.data_generator.generate_log_data(10))
            elif content_type == 'code':
                test_data.append(self.data_generator.generate_source_code(10))
            elif content_type == 'csv':
                test_data.append(self.data_generator.generate_numeric_data(10))
            elif content_type == 'mixed':
                test_data.append(self.data_generator.generate_mixed_content(10))
        
        # Add some high-entropy data
        test_data.append(self.data_generator.generate_high_entropy_data(5))
        
        # Add highly repetitive data
        test_data.append(self.data_generator.generate_highly_repetitive_text(5))
        
        return test_data
    
    async def _run_viability_tests(
        self,
        test_data: List,
        algorithms: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Run viability tests on all algorithms."""
        results = {}
        
        for algorithm_name in algorithms:
            try:
                algorithm = CompressionAlgorithm(algorithm_name)
            except ValueError:
                print(f"  ⚠ Skipping invalid algorithm: {algorithm_name}")
                continue
            
            print(f"  Testing: {algorithm.value.upper()}...", end=" ")
            
            algo_results = []
            successful = 0
            
            for i, test_case in enumerate(test_data):
                try:
                    request = CompressionRequest(
                        content=test_case.content,
                        parameters=CompressionParameters(
                            algorithm=algorithm,
                            level=6
                        )
                    )
                    
                    import time
                    start_time = time.time()
                    response = await self.compression_engine.compress(request)
                    compression_time = time.time() - start_time
                    
                    if response.success and response.result:
                        successful += 1
                        algo_results.append({
                            'test_case_index': i,
                            'content_type': test_case.content_type,
                            'complexity': test_case.complexity.value,
                            'success': True,
                            'compression_ratio': response.result.compression_ratio,
                            'compression_percentage': response.result.compression_percentage,
                            'compression_time': compression_time,
                            'original_size': response.result.original_size,
                            'compressed_size': response.result.compressed_size,
                            'throughput_mbps': (response.result.original_size / compression_time) / (1024 * 1024) if compression_time > 0 else 0,
                            'quality_score': min(response.result.compression_ratio / 10.0, 1.0),
                            'efficiency_score': response.result.compression_ratio / max(compression_time * 1000, 0.001),
                            'characteristics': test_case.characteristics,
                            'parameters': {'algorithm': algorithm.value, 'level': 6}
                        })
                    else:
                        algo_results.append({
                            'test_case_index': i,
                            'content_type': test_case.content_type,
                            'complexity': test_case.complexity.value,
                            'success': False,
                            'compression_ratio': 1.0,
                            'characteristics': test_case.characteristics
                        })
                
                except Exception as e:
                    algo_results.append({
                        'test_case_index': i,
                        'content_type': test_case.content_type,
                        'complexity': test_case.complexity.value,
                        'success': False,
                        'error': str(e)
                    })
            
            results[algorithm.value] = algo_results
            print(f"✓ ({successful}/{len(test_data)} successful)")
        
        return results
    
    def _record_to_database(self, viability_results: Dict[str, List[Dict[str, Any]]]) -> int:
        """Record results to meta-learning database."""
        recorded_count = 0
        
        for algorithm, results in viability_results.items():
            for result in results:
                if result['success']:
                    success = self.meta_learning_service.record_compression_test(
                        test_id=f"{self.workflow_id}_{algorithm}_{result['test_case_index']}",
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
                        success=True,
                        content_characteristics=result['characteristics'],
                        parameters_used=result['parameters'],
                        metadata={'workflow_id': self.workflow_id}
                    )
                    if success:
                        recorded_count += 1
        
        return recorded_count
    
    def _generate_insights(
        self,
        viability_results: Dict[str, List[Dict[str, Any]]],
        test_data: List
    ) -> List[Dict[str, Any]]:
        """Generate learning insights from test results."""
        insights = []
        
        # Insight 1: Best algorithm by content type
        content_type_performance = {}
        for algorithm, results in viability_results.items():
            for result in results:
                if result['success']:
                    ct = result['content_type']
                    if ct not in content_type_performance:
                        content_type_performance[ct] = {}
                    if algorithm not in content_type_performance[ct]:
                        content_type_performance[ct][algorithm] = []
                    content_type_performance[ct][algorithm].append(result['compression_ratio'])
        
        for content_type, algo_ratios in content_type_performance.items():
            best_algorithm = max(
                algo_ratios.items(),
                key=lambda x: sum(x[1]) / len(x[1])
            )[0]
            avg_ratio = sum(algo_ratios[best_algorithm]) / len(algo_ratios[best_algorithm])
            
            insights.append({
                'type': 'best_algorithm_for_content_type',
                'content_type': content_type,
                'algorithm': best_algorithm,
                'avg_compression_ratio': avg_ratio,
                'confidence': 0.9,
                'summary': f"{best_algorithm.upper()} performs best on {content_type} content with {avg_ratio:.2f}x compression"
            })
        
        # Insight 2: Speed vs compression tradeoff
        speed_compression_data = []
        for algorithm, results in viability_results.items():
            successful = [r for r in results if r['success']]
            if successful:
                avg_time = sum(r['compression_time'] for r in successful) / len(successful)
                avg_ratio = sum(r['compression_ratio'] for r in successful) / len(successful)
                speed_compression_data.append({
                    'algorithm': algorithm,
                    'avg_time': avg_time,
                    'avg_ratio': avg_ratio
                })
        
        if speed_compression_data:
            fastest = min(speed_compression_data, key=lambda x: x['avg_time'])
            best_compression = max(speed_compression_data, key=lambda x: x['avg_ratio'])
            
            insights.append({
                'type': 'speed_vs_compression_tradeoff',
                'fastest_algorithm': fastest['algorithm'],
                'fastest_time_ms': fastest['avg_time'] * 1000,
                'best_compression_algorithm': best_compression['algorithm'],
                'best_compression_ratio': best_compression['avg_ratio'],
                'confidence': 0.95,
                'summary': f"Speed/compression tradeoff: {fastest['algorithm'].upper()} fastest ({fastest['avg_time']*1000:.1f}ms), {best_compression['algorithm'].upper()} best ratio ({best_compression['avg_ratio']:.2f}x)"
            })
        
        # Insight 3: Overall algorithm ranking
        algorithm_scores = {}
        for algorithm, results in viability_results.items():
            successful = [r for r in results if r['success']]
            if successful:
                avg_ratio = sum(r['compression_ratio'] for r in successful) / len(successful)
                avg_efficiency = sum(r['efficiency_score'] for r in successful) / len(successful)
                success_rate = len(successful) / len(results)
                
                # Weighted score
                score = avg_ratio * 0.4 + avg_efficiency * 0.3 + success_rate * 0.3
                algorithm_scores[algorithm] = {
                    'score': score,
                    'avg_ratio': avg_ratio,
                    'success_rate': success_rate
                }
        
        if algorithm_scores:
            ranked = sorted(algorithm_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            insights.append({
                'type': 'algorithm_ranking',
                'rankings': [
                    {
                        'rank': i + 1,
                        'algorithm': algo,
                        'score': data['score'],
                        'avg_ratio': data['avg_ratio'],
                        'success_rate': data['success_rate']
                    }
                    for i, (algo, data) in enumerate(ranked)
                ],
                'confidence': 0.85,
                'summary': f"Top 3 algorithms: {', '.join(r[0].upper() for r in ranked[:3])}"
            })
        
        return insights
    
    def _record_insights(self, insights: List[Dict[str, Any]]):
        """Record insights to meta-learning database."""
        for insight in insights:
            if insight['type'] == 'best_algorithm_for_content_type':
                self.meta_learning_service.record_learning_insight(
                    insight_type='best_algorithm_for_content_type',
                    algorithm=insight['algorithm'],
                    content_type=insight['content_type'],
                    insight_data={
                        'avg_compression_ratio': insight['avg_compression_ratio']
                    },
                    confidence_score=insight['confidence']
                )
    
    def _export_for_frontend(
        self,
        viability_results: Dict[str, List[Dict[str, Any]]],
        insights: List[Dict[str, Any]]
    ) -> str:
        """Export results in frontend-compatible format."""
        export_data = {
            'workflow_id': self.workflow_id,
            'timestamp': datetime.utcnow().isoformat(),
            'algorithm_results': {},
            'insights': insights,
            'summary': {
                'total_algorithms': len(viability_results),
                'total_tests': sum(len(r) for r in viability_results.values()),
                'successful_tests': sum(
                    sum(1 for r in results if r.get('success', False))
                    for results in viability_results.values()
                )
            }
        }
        
        # Format algorithm results for frontend
        for algorithm, results in viability_results.items():
            successful = [r for r in results if r.get('success', False)]
            export_data['algorithm_results'][algorithm] = {
                'total_tests': len(results),
                'successful_tests': len(successful),
                'success_rate': (len(successful) / len(results)) * 100 if results else 0,
                'avg_compression_ratio': sum(r['compression_ratio'] for r in successful) / len(successful) if successful else 0,
                'avg_compression_time_ms': (sum(r['compression_time'] for r in successful) / len(successful)) * 1000 if successful else 0,
                'results': successful[:10]  # Include sample results
            }
        
        # Save to file
        export_path = f"backend/tests/test_results/frontend_export_{self.workflow_id}.json"
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return export_path
    
    def _print_summary(
        self,
        viability_results: Dict[str, List[Dict[str, Any]]],
        insights: List[Dict[str, Any]]
    ):
        """Print workflow summary."""
        print("Algorithm Performance Summary:")
        print()
        
        for algorithm, results in sorted(viability_results.items()):
            successful = [r for r in results if r.get('success', False)]
            if successful:
                avg_ratio = sum(r['compression_ratio'] for r in successful) / len(successful)
                avg_time = sum(r['compression_time'] for r in successful) / len(successful)
                success_rate = (len(successful) / len(results)) * 100
                
                print(f"  {algorithm.upper():20s} | "
                      f"Success: {success_rate:5.1f}% | "
                      f"Ratio: {avg_ratio:5.2f}x | "
                      f"Time: {avg_time*1000:6.1f}ms")
        
        print()
        print("Key Insights:")
        for i, insight in enumerate(insights[:5], 1):
            print(f"  {i}. {insight['summary']}")


async def main():
    """Main entry point."""
    workflow = SyntheticDataIntegrationWorkflow()
    
    try:
        result = await workflow.run_workflow(
            content_types=['text', 'json', 'xml', 'log', 'code', 'csv'],
            algorithms=['gzip', 'lzma', 'bzip2', 'lz4', 'zstd', 'brotli', 'content_aware'],
            export_for_frontend=True
        )
        return 0
    except Exception as e:
        print(f"\nERROR: Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

