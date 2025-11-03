import pytest
import json
from unittest.mock import Mock, patch
from core.analyzer import WebPerformanceAnalyzer
from metrics.metrics import PerformanceMetrics, LoadingTimeMetrics


class TestPerformanceAnalyzer:
    """Test suite for PerformanceAnalyzer class"""
    
    @pytest.fixture
    def analyzer(self):
        """Create a WebPerformanceAnalyzer instance for testing"""
        from utils.config import TestConfig
        config = TestConfig()
        return WebPerformanceAnalyzer(config)
    
    @pytest.fixture
    def sample_metrics(self):
        """Sample performance metrics for testing"""
        return [
            PerformanceMetrics(
                url="http://localhost:3000/compression",
                fcp=1200,
                lcp=2500,
                fid=50,
                cls=0.1,
                ttfb=300,
                tti=2000,
                speed_index=1500,
                timestamp="2024-01-01T00:00:00Z"
            ),
            PerformanceMetrics(
                url="http://localhost:3000/experiments",
                fcp=1500,
                lcp=3000,
                fid=75,
                cls=0.15,
                ttfb=400,
                tti=2500,
                speed_index=1800,
                timestamp="2024-01-01T00:01:00Z"
            )
        ]
    
    @pytest.fixture
    def sample_network_metrics(self):
        """Sample network metrics for testing"""
        return [
            NetworkMetrics(
                url="http://localhost:3000/compression",
                total_requests=10,
                total_size=2048,
                compression_ratio=0.6,
                requests=[
                    {"url": "http://localhost:3000", "size": 1024, "duration": 100},
                    {"url": "http://localhost:3000/api", "size": 512, "duration": 50}
                ],
                timestamp="2024-01-01T00:00:00Z"
            )
        ]
    
    def test_analyze_performance_metrics(self, analyzer, sample_metrics):
        """Test performance metrics analysis"""
        analysis = analyzer.analyze_performance_metrics(sample_metrics)
        
        assert analysis is not None
        assert "summary" in analysis
        assert "recommendations" in analysis
        assert "bottlenecks" in analysis
        assert "trends" in analysis
        
        # Check summary statistics
        summary = analysis["summary"]
        assert "average_fcp" in summary
        assert "average_lcp" in summary
        assert "average_fid" in summary
        assert "average_cls" in summary
        assert "performance_score" in summary
        
        # Check recommendations
        recommendations = analysis["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_identify_bottlenecks(self, analyzer, sample_metrics):
        """Test bottleneck identification"""
        bottlenecks = analyzer.identify_bottlenecks(sample_metrics)
        
        assert isinstance(bottlenecks, list)
        
        # Check for common bottlenecks
        bottleneck_types = [b["type"] for b in bottlenecks]
        expected_types = ["slow_fcp", "slow_lcp", "high_fid", "high_cls", "slow_ttfb", "slow_tti"]
        
        for bottleneck in bottlenecks:
            assert "type" in bottleneck
            assert "severity" in bottleneck
            assert "description" in bottleneck
            assert "recommendation" in bottleneck
            assert bottleneck["severity"] in ["low", "medium", "high", "critical"]
    
    def test_generate_recommendations(self, analyzer, sample_metrics):
        """Test recommendation generation"""
        recommendations = analyzer.generate_recommendations(sample_metrics)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert "category" in rec
            assert "priority" in rec
            assert "description" in rec
            assert "implementation" in rec
            assert rec["category"] in ["performance", "optimization", "caching", "compression"]
            assert rec["priority"] in ["low", "medium", "high", "critical"]
    
    def test_calculate_performance_trends(self, analyzer, sample_metrics):
        """Test performance trend calculation"""
        trends = analyzer.calculate_performance_trends(sample_metrics)
        
        assert "fcp_trend" in trends
        assert "lcp_trend" in trends
        assert "fid_trend" in trends
        assert "cls_trend" in trends
        assert "overall_trend" in trends
        
        for trend in trends.values():
            assert trend in ["improving", "stable", "declining"]
    
    def test_analyze_network_performance(self, analyzer, sample_network_metrics):
        """Test network performance analysis"""
        analysis = analyzer.analyze_network_performance(sample_network_metrics)
        
        assert "summary" in analysis
        assert "recommendations" in analysis
        assert "compression_analysis" in analysis
        
        summary = analysis["summary"]
        assert "total_requests" in summary
        assert "total_size" in summary
        assert "average_compression_ratio" in summary
        
        compression_analysis = analysis["compression_analysis"]
        assert "efficiency_score" in compression_analysis
        assert "optimization_opportunities" in compression_analysis
    
    def test_compare_performance(self, analyzer, sample_metrics):
        """Test performance comparison"""
        baseline = sample_metrics[0]
        current = sample_metrics[1]
        
        comparison = analyzer.compare_performance(baseline, current)
        
        assert "fcp_change" in comparison
        assert "lcp_change" in comparison
        assert "fid_change" in comparison
        assert "cls_change" in comparison
        assert "overall_change" in comparison
        
        for change in comparison.values():
            if isinstance(change, (int, float)):
                assert change != 0  # Should detect some change
    
    def test_generate_report(self, analyzer, sample_metrics, sample_network_metrics):
        """Test report generation"""
        with patch('performance_testing.core.analyzer.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-01 00:00:00"
            
            report = analyzer.generate_report(sample_metrics, sample_network_metrics)
            
            assert "report_metadata" in report
            assert "executive_summary" in report
            assert "detailed_analysis" in report
            assert "recommendations" in report
            assert "appendix" in report
            
            # Check report structure
            metadata = report["report_metadata"]
            assert "generated_at" in metadata
            assert "total_tests" in metadata
            assert "analysis_duration" in metadata
    
    def test_export_report_json(self, analyzer, sample_metrics, sample_network_metrics):
        """Test JSON report export"""
        with patch('builtins.open', Mock()) as mock_open, \
             patch('json.dump') as mock_json_dump:
            
            analyzer.export_report_json(sample_metrics, sample_network_metrics, "test_report.json")
            
            mock_open.assert_called_once_with("test_report.json", "w")
            mock_json_dump.assert_called_once()
    
    def test_export_report_html(self, analyzer, sample_metrics, sample_network_metrics):
        """Test HTML report export"""
        with patch('builtins.open', Mock()) as mock_open, \
             patch('performance_testing.core.analyzer.jinja2') as mock_jinja2:
            
            mock_template = Mock()
            mock_jinja2.Template.return_value = mock_template
            mock_template.render.return_value = "<html>Test Report</html>"
            
            analyzer.export_report_html(sample_metrics, sample_network_metrics, "test_report.html")
            
            mock_open.assert_called_once_with("test_report.html", "w")
            mock_template.render.assert_called_once()
    
    def test_calculate_performance_score(self, analyzer):
        """Test performance score calculation"""
        metrics = PerformanceMetrics(
            fcp=1200,
            lcp=2500,
            fid=50,
            cls=0.1,
            ttfb=300,
            tti=2000,
            speed_index=1500
        )
        
        score = analyzer.calculate_performance_score(metrics)
        
        assert 0 <= score <= 100
        assert isinstance(score, (int, float))
    
    def test_get_performance_grade(self, analyzer):
        """Test performance grade calculation"""
        assert analyzer.get_performance_grade(95) == "A+"
        assert analyzer.get_performance_grade(85) == "A"
        assert analyzer.get_performance_grade(75) == "B"
        assert analyzer.get_performance_grade(65) == "C"
        assert analyzer.get_performance_grade(55) == "D"
        assert analyzer.get_performance_grade(45) == "F"
    
    def test_identify_optimization_opportunities(self, analyzer, sample_metrics):
        """Test optimization opportunity identification"""
        opportunities = analyzer.identify_optimization_opportunities(sample_metrics)
        
        assert isinstance(opportunities, list)
        
        for opp in opportunities:
            assert "type" in opp
            assert "impact" in opp
            assert "effort" in opp
            assert "description" in opp
            assert opp["impact"] in ["low", "medium", "high"]
            assert opp["effort"] in ["low", "medium", "high"]
    
    def test_analyze_core_web_vitals(self, analyzer, sample_metrics):
        """Test Core Web Vitals analysis"""
        analysis = analyzer.analyze_core_web_vitals(sample_metrics)
        
        assert "fcp_analysis" in analysis
        assert "lcp_analysis" in analysis
        assert "fid_analysis" in analysis
        assert "cls_analysis" in analysis
        assert "overall_cwv_score" in analysis
        
        # Check analysis structure
        for metric in ["fcp_analysis", "lcp_analysis", "fid_analysis", "cls_analysis"]:
            metric_analysis = analysis[metric]
            assert "status" in metric_analysis
            assert "score" in metric_analysis
            assert "recommendations" in metric_analysis
            assert metric_analysis["status"] in ["good", "needs_improvement", "poor"]
    
    def test_empty_metrics_handling(self, analyzer):
        """Test handling of empty metrics"""
        empty_metrics = []
        
        analysis = analyzer.analyze_performance_metrics(empty_metrics)
        
        assert analysis is not None
        assert "summary" in analysis
        assert "recommendations" in analysis
        
        # Should handle empty data gracefully
        summary = analysis["summary"]
        assert "total_tests" in summary
        assert summary["total_tests"] == 0
    
    def test_invalid_metrics_handling(self, analyzer):
        """Test handling of invalid metrics"""
        invalid_metrics = [None, "invalid", {}]
        
        with pytest.raises((ValueError, TypeError)):
            analyzer.analyze_performance_metrics(invalid_metrics)
    
    def test_large_dataset_handling(self, analyzer):
        """Test handling of large datasets"""
        # Create a large dataset
        large_metrics = []
        for i in range(1000):
            large_metrics.append(PerformanceMetrics(
                url=f"http://localhost:3000/page{i}",
                fcp=1200 + i,
                lcp=2500 + i,
                fid=50 + i,
                cls=0.1 + (i * 0.001),
                ttfb=300 + i,
                tti=2000 + i,
                speed_index=1500 + i,
                timestamp=f"2024-01-01T00:{i:02d}:00Z"
            ))
        
        # Should handle large datasets without issues
        analysis = analyzer.analyze_performance_metrics(large_metrics)
        
        assert analysis is not None
        assert "summary" in analysis
        assert "recommendations" in analysis
