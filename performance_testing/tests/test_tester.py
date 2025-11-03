import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from core.tester import PerformanceTester
from metrics.metrics import PerformanceMetrics
from utils.config import TestConfig


class TestPerformanceTester:
    """Test suite for PerformanceTester class"""
    
    @pytest.fixture
    def tester(self):
        """Create a PerformanceTester instance for testing"""
        config = TestConfig(
            timeout=30
        )
        return PerformanceTester(config)
    
    @pytest.fixture
    def mock_browser(self):
        """Mock browser for testing"""
        browser = Mock()
        browser.new_page = AsyncMock()
        return browser
    
    @pytest.fixture
    def mock_page(self):
        """Mock page for testing"""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.wait_for_load_state = AsyncMock()
        page.evaluate = AsyncMock()
        page.metrics = AsyncMock()
        page.close = AsyncMock()
        return page
    
    @pytest.mark.asyncio
    async def test_initialize_browser(self, tester):
        """Test browser initialization"""
        with patch('performance_testing.core.tester.async_playwright') as mock_playwright:
            mock_playwright.return_value.__aenter__.return_value.chromium.launch = AsyncMock()
            
            await tester.initialize_browser()
            
            assert tester.browser is not None
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_navigate_to_page(self, tester, mock_browser, mock_page):
        """Test page navigation"""
        tester.browser = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        result = await tester.navigate_to_page("http://localhost:3000")
        
        assert result == mock_page
        mock_page.goto.assert_called_once_with("http://localhost:3000")
        mock_page.wait_for_load_state.assert_called_once_with("networkidle")
    
    @pytest.mark.asyncio
    async def test_measure_core_web_vitals(self, tester, mock_page):
        """Test Core Web Vitals measurement"""
        mock_page.evaluate.side_effect = [
            {"fcp": 1200, "lcp": 2500, "fid": 50, "cls": 0.1},  # First call
            {"ttfb": 300, "tti": 2000, "speed_index": 1500}     # Second call
        ]
        
        metrics = await tester.measure_core_web_vitals(mock_page)
        
        assert metrics.fcp == 1200
        assert metrics.lcp == 2500
        assert metrics.fid == 50
        assert metrics.cls == 0.1
        assert metrics.ttfb == 300
        assert metrics.tti == 2000
        assert metrics.speed_index == 1500
    
    @pytest.mark.asyncio
    async def test_measure_network_performance(self, tester, mock_page):
        """Test network performance measurement"""
        mock_page.evaluate.return_value = {
            "requests": [
                {"url": "http://localhost:3000", "size": 1024, "duration": 100},
                {"url": "http://localhost:3000/api", "size": 512, "duration": 50}
            ],
            "total_size": 1536,
            "total_requests": 2,
            "compression_ratio": 0.6
        }
        
        network_metrics = await tester.measure_network_performance(mock_page)
        
        assert network_metrics.total_requests == 2
        assert network_metrics.total_size == 1536
        assert network_metrics.compression_ratio == 0.6
        assert len(network_metrics.requests) == 2
    
    @pytest.mark.asyncio
    async def test_measure_memory_usage(self, tester, mock_page):
        """Test memory usage measurement"""
        mock_page.evaluate.return_value = {
            "used_js_heap_size": 50 * 1024 * 1024,  # 50MB
            "total_js_heap_size": 100 * 1024 * 1024,  # 100MB
            "js_heap_size_limit": 200 * 1024 * 1024   # 200MB
        }
        
        memory_metrics = await tester.measure_memory_usage(mock_page)
        
        assert memory_metrics.used_js_heap_size == 50 * 1024 * 1024
        assert memory_metrics.total_js_heap_size == 100 * 1024 * 1024
        assert memory_metrics.js_heap_size_limit == 200 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_run_performance_test(self, tester, mock_browser, mock_page):
        """Test complete performance test execution"""
        tester.browser = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Mock all measurement methods
        with patch.object(tester, 'measure_core_web_vitals') as mock_vitals, \
             patch.object(tester, 'measure_network_performance') as mock_network, \
             patch.object(tester, 'measure_memory_usage') as mock_memory:
            
            mock_vitals.return_value = Mock(fcp=1200, lcp=2500, fid=50, cls=0.1)
            mock_network.return_value = Mock(total_requests=5, total_size=2048, compression_ratio=0.7)
            mock_memory.return_value = Mock(used_js_heap_size=50*1024*1024)
            
            result = await tester.run_performance_test("http://localhost:3000")
            
            assert result is not None
            assert result.url == "http://localhost:3000"
            mock_vitals.assert_called_once_with(mock_page)
            mock_network.assert_called_once_with(mock_page)
            mock_memory.assert_called_once_with(mock_page)
    
    @pytest.mark.asyncio
    async def test_run_tab_performance_tests(self, tester):
        """Test tab-specific performance tests"""
        tabs = ["compression", "experiments", "metrics", "synthetic", "llm-agent", "evaluation"]
        
        with patch.object(tester, 'run_performance_test') as mock_test:
            mock_test.return_value = Mock(url="http://localhost:3000", fcp=1200)
            
            results = await tester.run_tab_performance_tests("http://localhost:3000", tabs)
            
            assert len(results) == 6
            assert mock_test.call_count == 6
    
    @pytest.mark.asyncio
    async def test_cleanup(self, tester, mock_browser):
        """Test cleanup functionality"""
        tester.browser = mock_browser
        mock_browser.close = AsyncMock()
        
        await tester.cleanup()
        
        mock_browser.close.assert_called_once()
    
    def test_calculate_performance_score(self, tester):
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
        
        score = tester.calculate_performance_score(metrics)
        
        assert 0 <= score <= 100
        assert isinstance(score, (int, float))
    
    def test_get_performance_grade(self, tester):
        """Test performance grade calculation"""
        assert tester.get_performance_grade(95) == "A+"
        assert tester.get_performance_grade(85) == "A"
        assert tester.get_performance_grade(75) == "B"
        assert tester.get_performance_grade(65) == "C"
        assert tester.get_performance_grade(55) == "D"
        assert tester.get_performance_grade(45) == "F"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, tester):
        """Test error handling in performance tests"""
        with patch('performance_testing.core.tester.async_playwright') as mock_playwright:
            mock_playwright.return_value.__aenter__.side_effect = Exception("Browser error")
            
            with pytest.raises(Exception):
                await tester.initialize_browser()
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, tester, mock_browser, mock_page):
        """Test timeout handling"""
        tester.browser = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.goto.side_effect = asyncio.TimeoutError("Navigation timeout")
        
        with pytest.raises(asyncio.TimeoutError):
            await tester.navigate_to_page("http://localhost:3000")
    
    def test_config_validation(self):
        """Test configuration validation"""
        with pytest.raises(ValueError):
            TestConfig(timeout=-1)
        
        with pytest.raises(ValueError):
            TestConfig(timeout=0)
        
        with pytest.raises(ValueError):
            TestConfig(retry_count=-1)
