import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from main import main
from core.tester import PerformanceTester
from core.analyzer import WebPerformanceAnalyzer


class TestMain:
    """Test suite for main performance testing module"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing"""
        return {
            "base_url": "http://localhost:3000",
            "test_timeout": 30,
            "max_concurrent_tests": 5,
            "output_dir": "./test_results",
            "export_formats": ["json", "html"]
        }
    
    @pytest.fixture
    def mock_metrics(self):
        """Mock performance metrics for testing"""
        return [
            {
                "url": "http://localhost:3000/compression",
                "fcp": 1200,
                "lcp": 2500,
                "fid": 50,
                "cls": 0.1,
                "ttfb": 300,
                "tti": 2000,
                "speed_index": 1500,
                "timestamp": "2024-01-01T00:00:00Z"
            },
            {
                "url": "http://localhost:3000/experiments",
                "fcp": 1500,
                "lcp": 3000,
                "fid": 75,
                "cls": 0.15,
                "ttfb": 400,
                "tti": 2500,
                "speed_index": 1800,
                "timestamp": "2024-01-01T00:01:00Z"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_run_performance_tests_success(self, mock_config, mock_metrics):
        """Test successful performance test execution"""
        with patch('performance_testing.main.PerformanceTester') as mock_tester_class, \
             patch('performance_testing.main.PerformanceAnalyzer') as mock_analyzer_class, \
             patch('performance_testing.main.os.makedirs') as mock_makedirs, \
             patch('performance_testing.main.json.dump') as mock_json_dump, \
             patch('builtins.open', Mock()) as mock_open:
            
            # Mock tester
            mock_tester = AsyncMock()
            mock_tester.run_tab_performance_tests.return_value = mock_metrics
            mock_tester.cleanup = AsyncMock()
            mock_tester_class.return_value = mock_tester
            
            # Mock analyzer
            mock_analyzer = Mock()
            mock_analyzer.generate_report.return_value = {"summary": "Test report"}
            mock_analyzer.export_report_json = Mock()
            mock_analyzer.export_report_html = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await run_performance_tests(mock_config)
            
            assert result is not None
            assert "success" in result
            assert result["success"] is True
            assert "metrics" in result
            assert "report" in result
            
            # Verify tester was called
            mock_tester.run_tab_performance_tests.assert_called_once()
            mock_tester.cleanup.assert_called_once()
            
            # Verify analyzer was called
            mock_analyzer.generate_report.assert_called_once()
            mock_analyzer.export_report_json.assert_called_once()
            mock_analyzer.export_report_html.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_performance_tests_failure(self, mock_config):
        """Test performance test execution failure"""
        with patch('performance_testing.main.PerformanceTester') as mock_tester_class, \
             patch('performance_testing.main.PerformanceAnalyzer') as mock_analyzer_class:
            
            # Mock tester to raise exception
            mock_tester = AsyncMock()
            mock_tester.run_tab_performance_tests.side_effect = Exception("Test failed")
            mock_tester.cleanup = AsyncMock()
            mock_tester_class.return_value = mock_tester
            
            # Mock analyzer
            mock_analyzer = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await run_performance_tests(mock_config)
            
            assert result is not None
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert "Test failed" in result["error"]
            
            # Verify cleanup was called even on failure
            mock_tester.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_function_success(self, mock_config):
        """Test main function execution"""
        with patch('performance_testing.main.run_performance_tests') as mock_run_tests, \
             patch('performance_testing.main.argparse.ArgumentParser') as mock_parser, \
             patch('performance_testing.main.sys.argv', ['main.py', '--url', 'http://localhost:3000']):
            
            mock_run_tests.return_value = {
                "success": True,
                "metrics": mock_config,
                "report": {"summary": "Test report"}
            }
            
            mock_parser_instance = Mock()
            mock_parser_instance.parse_args.return_value = Mock(
                url="http://localhost:3000",
                output_dir="./test_results",
                format=["json", "html"],
                timeout=30,
                concurrent=5
            )
            mock_parser.return_value = mock_parser_instance
            
            # Mock asyncio.run
            with patch('performance_testing.main.asyncio.run') as mock_asyncio_run:
                mock_asyncio_run.return_value = {"success": True}
                
                result = main()
                
                assert result is not None
                mock_asyncio_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_function_failure(self, mock_config):
        """Test main function execution with failure"""
        with patch('performance_testing.main.run_performance_tests') as mock_run_tests, \
             patch('performance_testing.main.argparse.ArgumentParser') as mock_parser, \
             patch('performance_testing.main.sys.argv', ['main.py', '--url', 'http://localhost:3000']):
            
            mock_run_tests.return_value = {
                "success": False,
                "error": "Test failed"
            }
            
            mock_parser_instance = Mock()
            mock_parser_instance.parse_args.return_value = Mock(
                url="http://localhost:3000",
                output_dir="./test_results",
                format=["json", "html"],
                timeout=30,
                concurrent=5
            )
            mock_parser.return_value = mock_parser_instance
            
            # Mock asyncio.run
            with patch('performance_testing.main.asyncio.run') as mock_asyncio_run:
                mock_asyncio_run.return_value = {"success": False, "error": "Test failed"}
                
                result = main()
                
                assert result is not None
                mock_asyncio_run.assert_called_once()
    
    def test_argument_parsing(self):
        """Test command line argument parsing"""
        with patch('performance_testing.main.argparse.ArgumentParser') as mock_parser, \
             patch('performance_testing.main.sys.argv', [
                 'main.py',
                 '--url', 'http://localhost:3000',
                 '--output-dir', './results',
                 '--format', 'json', 'html',
                 '--timeout', '60',
                 '--concurrent', '10'
             ]):
            
            mock_parser_instance = Mock()
            mock_parser_instance.add_argument = Mock()
            mock_parser_instance.parse_args.return_value = Mock(
                url="http://localhost:3000",
                output_dir="./results",
                format=["json", "html"],
                timeout=60,
                concurrent=10
            )
            mock_parser.return_value = mock_parser_instance
            
            # Mock asyncio.run to avoid actual execution
            with patch('performance_testing.main.asyncio.run'):
                main()
                
                # Verify argument parser was configured
                mock_parser_instance.add_argument.assert_called()
                mock_parser_instance.parse_args.assert_called_once()
    
    def test_config_validation(self):
        """Test configuration validation"""
        with patch('performance_testing.main.run_performance_tests') as mock_run_tests, \
             patch('performance_testing.main.argparse.ArgumentParser') as mock_parser, \
             patch('performance_testing.main.sys.argv', ['main.py', '--url', '']):
            
            mock_parser_instance = Mock()
            mock_parser_instance.parse_args.return_value = Mock(
                url="",
                output_dir="./test_results",
                format=["json"],
                timeout=30,
                concurrent=5
            )
            mock_parser.return_value = mock_parser_instance
            
            # Mock asyncio.run
            with patch('performance_testing.main.asyncio.run') as mock_asyncio_run:
                mock_asyncio_run.side_effect = ValueError("Invalid URL")
                
                with pytest.raises(ValueError):
                    main()
    
    @pytest.mark.asyncio
    async def test_concurrent_test_execution(self, mock_config):
        """Test concurrent test execution"""
        with patch('performance_testing.main.PerformanceTester') as mock_tester_class, \
             patch('performance_testing.main.PerformanceAnalyzer') as mock_analyzer_class:
            
            # Mock tester with concurrent execution
            mock_tester = AsyncMock()
            mock_tester.run_tab_performance_tests.return_value = mock_config
            mock_tester.cleanup = AsyncMock()
            mock_tester_class.return_value = mock_tester
            
            # Mock analyzer
            mock_analyzer = Mock()
            mock_analyzer.generate_report.return_value = {"summary": "Test report"}
            mock_analyzer.export_report_json = Mock()
            mock_analyzer.export_report_html = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            
            # Test with high concurrency
            config = mock_config.copy()
            config["max_concurrent_tests"] = 10
            
            result = await run_performance_tests(config)
            
            assert result is not None
            assert "success" in result
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_output_directory_creation(self, mock_config):
        """Test output directory creation"""
        with patch('performance_testing.main.PerformanceTester') as mock_tester_class, \
             patch('performance_testing.main.PerformanceAnalyzer') as mock_analyzer_class, \
             patch('performance_testing.main.os.makedirs') as mock_makedirs, \
             patch('performance_testing.main.json.dump') as mock_json_dump, \
             patch('builtins.open', Mock()) as mock_open:
            
            # Mock tester
            mock_tester = AsyncMock()
            mock_tester.run_tab_performance_tests.return_value = mock_config
            mock_tester.cleanup = AsyncMock()
            mock_tester_class.return_value = mock_tester
            
            # Mock analyzer
            mock_analyzer = Mock()
            mock_analyzer.generate_report.return_value = {"summary": "Test report"}
            mock_analyzer.export_report_json = Mock()
            mock_analyzer.export_report_html = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await run_performance_tests(mock_config)
            
            # Verify directory was created
            mock_makedirs.assert_called()
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_export_formats(self, mock_config):
        """Test different export formats"""
        with patch('performance_testing.main.PerformanceTester') as mock_tester_class, \
             patch('performance_testing.main.PerformanceAnalyzer') as mock_analyzer_class, \
             patch('performance_testing.main.os.makedirs') as mock_makedirs, \
             patch('performance_testing.main.json.dump') as mock_json_dump, \
             patch('builtins.open', Mock()) as mock_open:
            
            # Mock tester
            mock_tester = AsyncMock()
            mock_tester.run_tab_performance_tests.return_value = mock_config
            mock_tester.cleanup = AsyncMock()
            mock_tester_class.return_value = mock_tester
            
            # Mock analyzer
            mock_analyzer = Mock()
            mock_analyzer.generate_report.return_value = {"summary": "Test report"}
            mock_analyzer.export_report_json = Mock()
            mock_analyzer.export_report_html = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            
            # Test with different export formats
            config = mock_config.copy()
            config["export_formats"] = ["json", "html"]
            
            result = await run_performance_tests(config)
            
            assert result["success"] is True
            
            # Verify both export methods were called
            mock_analyzer.export_report_json.assert_called_once()
            mock_analyzer.export_report_html.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_config):
        """Test timeout handling"""
        with patch('performance_testing.main.PerformanceTester') as mock_tester_class, \
             patch('performance_testing.main.PerformanceAnalyzer') as mock_analyzer_class:
            
            # Mock tester to simulate timeout
            mock_tester = AsyncMock()
            mock_tester.run_tab_performance_tests.side_effect = asyncio.TimeoutError("Test timeout")
            mock_tester.cleanup = AsyncMock()
            mock_tester_class.return_value = mock_tester
            
            # Mock analyzer
            mock_analyzer = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await run_performance_tests(mock_config)
            
            assert result["success"] is False
            assert "timeout" in result["error"].lower()
    
    def test_error_handling(self):
        """Test error handling in main function"""
        with patch('performance_testing.main.argparse.ArgumentParser') as mock_parser, \
             patch('performance_testing.main.sys.argv', ['main.py']):
            
            mock_parser_instance = Mock()
            mock_parser_instance.parse_args.side_effect = Exception("Argument parsing error")
            mock_parser.return_value = mock_parser_instance
            
            with pytest.raises(Exception):
                main()
