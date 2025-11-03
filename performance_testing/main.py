#!/usr/bin/env python3
"""
Main performance testing script for Dynamic Compression Algorithms frontend
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse
from datetime import datetime

# Add the performance_testing directory to the path
sys.path.append(str(Path(__file__).parent))

from core.tester import PerformanceTester
from core.analyzer import WebPerformanceAnalyzer
from utils.config import TestConfig, TestMode
from metrics.metrics import PerformanceMetrics, LoadingTimeMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class FrontendPerformanceTester:
    """
    Main class for testing frontend performance
    """
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.tester = PerformanceTester(config)
        self.analyzer = WebPerformanceAnalyzer(config)
        
    async def test_compression_dashboard(self, base_url: str = "http://localhost:3000") -> Dict[str, Any]:
        """
        Test the Dynamic Compression Algorithms dashboard performance
        
        Args:
            base_url: Base URL of the frontend application
            
        Returns:
            Comprehensive test results
        """
        logger.info("Starting Dynamic Compression Algorithms dashboard performance testing")
        
        # Define tabs to test
        tabs = [
            {"name": "Compression", "path": "/"},
            {"name": "Experiments", "path": "/?tab=experiments"},
            {"name": "System Metrics", "path": "/?tab=metrics"},
            {"name": "Synthetic Data", "path": "/?tab=synthetic"},
            {"name": "LLM Agent", "path": "/?tab=llm-agent"},
            {"name": "Evaluation", "path": "/?tab=evaluation"}
        ]
        
        # Test all tabs
        logger.info(f"Testing {len(tabs)} tabs")
        tab_results = await self.tester.test_all_tabs(base_url, tabs)
        
        # Perform comprehensive analysis
        logger.info("Performing comprehensive analysis")
        analysis_results = await self.analyzer.analyze_application(base_url, tabs)
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(tab_results, analysis_results)
        
        # Save results
        self._save_results(report)
        
        return report
    
    def _generate_comprehensive_report(self, tab_results: List, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        # Calculate overall statistics
        total_tabs = len(tab_results)
        successful_tests = len([r for r in tab_results if not r.errors])
        failed_tests = total_tabs - successful_tests
        
        # Calculate averages
        if successful_tests > 0:
            avg_load_time = sum(r.load_time for r in tab_results if not r.errors) / successful_tests
            avg_fcp = sum(r.first_contentful_paint for r in tab_results if not r.errors) / successful_tests
            avg_lcp = sum(r.largest_contentful_paint for r in tab_results if not r.errors) / successful_tests
            avg_memory = sum(r.memory_usage for r in tab_results if not r.errors) / successful_tests
        else:
            avg_load_time = avg_fcp = avg_lcp = avg_memory = 0
        
        # Find best and worst performing tabs
        successful_results = [r for r in tab_results if not r.errors]
        if successful_results:
            best_tab = min(successful_results, key=lambda r: r.load_time)
            worst_tab = max(successful_results, key=lambda r: r.load_time)
        else:
            best_tab = worst_tab = None
        
        # Generate performance scores
        performance_scores = []
        for result in tab_results:
            if not result.errors:
                score = self._calculate_performance_score(result)
                performance_scores.append({
                    'tab': result.tab_name,
                    'score': score,
                    'grade': self._get_performance_grade(score),
                    'load_time': result.load_time,
                    'fcp': result.first_contentful_paint,
                    'lcp': result.largest_contentful_paint
                })
        
        # Sort by performance score
        performance_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(tab_results, analysis_results)
        
        return {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_tabs_tested': total_tabs,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': (successful_tests / total_tabs * 100) if total_tabs > 0 else 0
            },
            'performance_overview': {
                'average_load_time': avg_load_time,
                'average_fcp': avg_fcp,
                'average_lcp': avg_lcp,
                'average_memory_usage': avg_memory,
                'best_performing_tab': {
                    'name': best_tab.tab_name if best_tab else 'N/A',
                    'load_time': best_tab.load_time if best_tab else 0
                },
                'worst_performing_tab': {
                    'name': worst_tab.tab_name if worst_tab else 'N/A',
                    'load_time': worst_tab.load_time if worst_tab else 0
                }
            },
            'performance_scores': performance_scores,
            'detailed_results': [
                {
                    'tab_name': r.tab_name,
                    'url': r.url,
                    'load_time': r.load_time,
                    'first_contentful_paint': r.first_contentful_paint,
                    'largest_contentful_paint': r.largest_contentful_paint,
                    'first_input_delay': r.first_input_delay,
                    'cumulative_layout_shift': r.cumulative_layout_shift,
                    'memory_usage': r.memory_usage,
                    'network_requests': r.network_requests,
                    'failed_requests': r.failed_requests,
                    'compression_ratio': r.compression_ratio,
                    'errors': r.errors
                }
                for r in tab_results
            ],
            'analysis_results': analysis_results,
            'recommendations': recommendations,
            'optimization_priority': self._prioritize_optimizations(recommendations)
        }
    
    def _calculate_performance_score(self, result) -> int:
        """Calculate performance score (0-100)"""
        score = 100
        
        # Deduct points for slow loading
        if result.load_time > 3.0:
            score -= 30
        elif result.load_time > 2.0:
            score -= 20
        elif result.load_time > 1.0:
            score -= 10
        
        # Deduct points for slow FCP
        if result.first_contentful_paint > 2.5:
            score -= 25
        elif result.first_contentful_paint > 1.8:
            score -= 15
        elif result.first_contentful_paint > 1.0:
            score -= 10
        
        # Deduct points for slow LCP
        if result.largest_contentful_paint > 4.0:
            score -= 20
        elif result.largest_contentful_paint > 2.5:
            score -= 10
        
        # Deduct points for high memory usage
        if result.memory_usage > 100:
            score -= 15
        elif result.memory_usage > 50:
            score -= 10
        
        # Deduct points for failed requests
        if result.failed_requests > 0:
            score -= result.failed_requests * 5
        
        return max(0, score)
    
    def _get_performance_grade(self, score: int) -> str:
        """Get performance grade based on score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, tab_results: List, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Analyze tab results
        if tab_results:
            avg_load_time = sum(r.load_time for r in tab_results if not r.errors) / len([r for r in tab_results if not r.errors])
            avg_fcp = sum(r.first_contentful_paint for r in tab_results if not r.errors) / len([r for r in tab_results if not r.errors])
            avg_memory = sum(r.memory_usage for r in tab_results if not r.errors) / len([r for r in tab_results if not r.errors])
            
            if avg_load_time > 2.0:
                recommendations.append({
                    'category': 'Loading Performance',
                    'priority': 'high',
                    'title': 'Optimize Page Load Times',
                    'description': f'Average load time is {avg_load_time:.2f}s, which is above the recommended 2.0s threshold',
                    'impact': 'High - Significant improvement in user experience',
                    'effort': 'Medium - Requires code optimization',
                    'implementation': [
                        'Implement code splitting and lazy loading',
                        'Optimize images and use modern formats (WebP, AVIF)',
                        'Enable gzip/brotli compression on server',
                        'Minimize render-blocking resources'
                    ],
                    'expected_improvement': '30-50% reduction in load time'
                })
            
            if avg_fcp > 1.8:
                recommendations.append({
                    'category': 'Core Web Vitals',
                    'priority': 'high',
                    'title': 'Improve First Contentful Paint',
                    'description': f'Average FCP is {avg_fcp:.2f}s, which is above the recommended 1.8s threshold',
                    'impact': 'High - Better Core Web Vitals score',
                    'effort': 'Medium - Requires critical path optimization',
                    'implementation': [
                        'Inline critical CSS',
                        'Optimize critical rendering path',
                        'Use resource hints (preload, prefetch)',
                        'Minimize render-blocking JavaScript'
                    ],
                    'expected_improvement': '20-40% improvement in FCP'
                })
            
            if avg_memory > 50:
                recommendations.append({
                    'category': 'Memory Optimization',
                    'priority': 'medium',
                    'title': 'Reduce Memory Usage',
                    'description': f'Average memory usage is {avg_memory:.2f}MB, which is above the recommended 50MB threshold',
                    'impact': 'Medium - Better performance on low-end devices',
                    'effort': 'Medium - Requires code refactoring',
                    'implementation': [
                        'Implement memory cleanup in components',
                        'Use virtual scrolling for large lists',
                        'Optimize component re-renders',
                        'Implement proper event listener cleanup'
                    ],
                    'expected_improvement': '30-50% reduction in memory usage'
                })
        
        # Add analysis-based recommendations
        if 'recommendations' in analysis_results:
            for rec in analysis_results['recommendations']:
                recommendations.append({
                    'category': rec.category,
                    'priority': rec.priority,
                    'title': rec.title,
                    'description': rec.description,
                    'impact': rec.impact,
                    'effort': rec.effort,
                    'implementation': [rec.implementation],
                    'expected_improvement': rec.expected_improvement
                })
        
        return recommendations
    
    def _prioritize_optimizations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Prioritize optimizations by impact and effort"""
        high_impact_low_effort = []
        high_impact_high_effort = []
        medium_impact_low_effort = []
        medium_impact_high_effort = []
        low_impact = []
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            impact = rec.get('impact', 'Medium')
            
            if priority == 'high' and 'Low' in impact:
                high_impact_low_effort.append(rec)
            elif priority == 'high' and 'High' in impact:
                high_impact_high_effort.append(rec)
            elif priority == 'medium' and 'Low' in impact:
                medium_impact_low_effort.append(rec)
            elif priority == 'medium' and 'High' in impact:
                medium_impact_high_effort.append(rec)
            else:
                low_impact.append(rec)
        
        return {
            'quick_wins': high_impact_low_effort,
            'major_projects': high_impact_high_effort,
            'incremental_improvements': medium_impact_low_effort,
            'long_term_goals': medium_impact_high_effort,
            'nice_to_have': low_impact
        }
    
    def _save_results(self, report: Dict[str, Any]):
        """Save test results to file"""
        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed report
        report_file = output_dir / f"performance_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save summary report
        summary_file = output_dir / f"performance_summary_{timestamp}.json"
        summary = {
            'test_summary': report['test_summary'],
            'performance_overview': report['performance_overview'],
            'performance_scores': report['performance_scores'],
            'optimization_priority': report['optimization_priority']
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Results saved to {output_dir}")
        logger.info(f"Detailed report: {report_file}")
        logger.info(f"Summary report: {summary_file}")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Frontend Performance Testing')
    parser.add_argument('--url', default='http://localhost:3000', help='Base URL of the frontend application')
    parser.add_argument('--mode', choices=['quick', 'standard', 'comprehensive'], default='standard', help='Test mode')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--output-dir', default='./performance_results', help='Output directory for results')
    parser.add_argument('--timeout', type=int, default=30, help='Test timeout in seconds')
    
    args = parser.parse_args()
    
    # Create test configuration
    config = TestConfig(
        mode=TestMode(args.mode),
        timeout=args.timeout,
        headless=args.headless,
        output_directory=args.output_dir
    )
    
    # Create tester
    tester = FrontendPerformanceTester(config)
    
    try:
        # Run tests
        results = await tester.test_compression_dashboard(args.url)
        
        # Print summary
        print("\n" + "="*80)
        print("PERFORMANCE TESTING SUMMARY")
        print("="*80)
        
        summary = results['test_summary']
        overview = results['performance_overview']
        
        print(f"Total tabs tested: {summary['total_tabs_tested']}")
        print(f"Successful tests: {summary['successful_tests']}")
        print(f"Failed tests: {summary['failed_tests']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print()
        
        print("PERFORMANCE OVERVIEW:")
        print(f"Average load time: {overview['average_load_time']:.2f}s")
        print(f"Average FCP: {overview['average_fcp']:.2f}s")
        print(f"Average LCP: {overview['average_lcp']:.2f}s")
        print(f"Average memory usage: {overview['average_memory_usage']:.2f}MB")
        print()
        
        print("PERFORMANCE SCORES:")
        for score in results['performance_scores']:
            print(f"{score['tab']}: {score['grade']} ({score['score']}/100) - {score['load_time']:.2f}s")
        print()
        
        print("OPTIMIZATION PRIORITIES:")
        priorities = results['optimization_priority']
        
        if priorities['quick_wins']:
            print("QUICK WINS (High Impact, Low Effort):")
            for rec in priorities['quick_wins']:
                print(f"  - {rec['title']}")
        
        if priorities['major_projects']:
            print("MAJOR PROJECTS (High Impact, High Effort):")
            for rec in priorities['major_projects']:
                print(f"  - {rec['title']}")
        
        print("\n" + "="*80)
        print("Detailed results saved to:", config.output_directory)
        print("="*80)
        
    except Exception as e:
        logger.error(f"Performance testing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
