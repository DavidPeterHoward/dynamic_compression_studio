"""
Performance Tester - Core testing functionality for web performance analysis
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from metrics.metrics import PerformanceMetrics, LoadingTimeMetrics
from utils.config import TestConfig, BrowserConfig

logger = logging.getLogger(__name__)

@dataclass
class TabPerformanceResult:
    """Results for a specific tab/page performance test"""
    tab_name: str
    url: str
    load_time: float
    dom_content_loaded: float
    first_contentful_paint: float
    largest_contentful_paint: float
    first_input_delay: float
    cumulative_layout_shift: float
    total_blocking_time: float
    speed_index: float
    time_to_interactive: float
    memory_usage: float
    network_requests: int
    failed_requests: int
    total_transfer_size: int
    compression_ratio: Optional[float] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class PerformanceTester:
    """
    Comprehensive performance testing for web applications
    """
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results: List[TabPerformanceResult] = []
        self.browser_config = BrowserConfig()
        
    async def test_all_tabs(self, base_url: str, tabs: List[Dict[str, str]]) -> List[TabPerformanceResult]:
        """
        Test performance for all tabs/pages in the application
        
        Args:
            base_url: Base URL of the application
            tabs: List of tab configurations with name and path
            
        Returns:
            List of performance results for each tab
        """
        logger.info(f"Starting performance testing for {len(tabs)} tabs")
        
        # Test each tab
        for tab in tabs:
            try:
                result = await self._test_single_tab(base_url, tab)
                self.results.append(result)
                logger.info(f"Completed testing for tab: {tab['name']}")
            except Exception as e:
                logger.error(f"Failed to test tab {tab['name']}: {str(e)}")
                # Create error result
                error_result = TabPerformanceResult(
                    tab_name=tab['name'],
                    url=f"{base_url}{tab['path']}",
                    load_time=0,
                    dom_content_loaded=0,
                    first_contentful_paint=0,
                    largest_contentful_paint=0,
                    first_input_delay=0,
                    cumulative_layout_shift=0,
                    total_blocking_time=0,
                    speed_index=0,
                    time_to_interactive=0,
                    memory_usage=0,
                    network_requests=0,
                    failed_requests=0,
                    total_transfer_size=0,
                    errors=[str(e)]
                )
                self.results.append(error_result)
        
        return self.results
    
    async def _test_single_tab(self, base_url: str, tab: Dict[str, str]) -> TabPerformanceResult:
        """
        Test performance for a single tab/page
        """
        url = f"{base_url}{tab['path']}"
        logger.info(f"Testing tab: {tab['name']} at {url}")
        
        # Initialize browser
        driver = self._setup_browser()
        
        try:
            # Start performance monitoring
            performance_start = time.time()
            
            # Navigate to page
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, self.config.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for additional loading time
            await asyncio.sleep(self.config.additional_wait_time)
            
            # Get performance metrics
            metrics = self._extract_performance_metrics(driver)
            
            # Get network metrics
            network_metrics = self._extract_network_metrics(driver)
            
            # Calculate total load time
            total_load_time = time.time() - performance_start
            
            # Get memory usage
            memory_usage = self._get_memory_usage()
            
            return TabPerformanceResult(
                tab_name=tab['name'],
                url=url,
                load_time=total_load_time,
                dom_content_loaded=metrics.get('domContentLoaded', 0),
                first_contentful_paint=metrics.get('firstContentfulPaint', 0),
                largest_contentful_paint=metrics.get('largestContentfulPaint', 0),
                first_input_delay=metrics.get('firstInputDelay', 0),
                cumulative_layout_shift=metrics.get('cumulativeLayoutShift', 0),
                total_blocking_time=metrics.get('totalBlockingTime', 0),
                speed_index=metrics.get('speedIndex', 0),
                time_to_interactive=metrics.get('timeToInteractive', 0),
                memory_usage=memory_usage,
                network_requests=network_metrics.get('requests', 0),
                failed_requests=network_metrics.get('failed_requests', 0),
                total_transfer_size=network_metrics.get('total_size', 0),
                compression_ratio=network_metrics.get('compression_ratio'),
                errors=[]
            )
            
        finally:
            driver.quit()
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup Chrome browser with performance monitoring"""
        options = Options()
        
        # Performance monitoring options
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.add_argument('--enable-performance-logging')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Disable images for faster loading
        options.add_argument('--disable-javascript')  # Disable JS for initial load test
        
        if self.browser_config.headless:
            options.add_argument('--headless')
        
        if self.browser_config.window_size:
            options.add_argument(f'--window-size={self.browser_config.window_size}')
        
        # Enable performance logging
        options.set_capability('goog:loggingPrefs', {
            'performance': 'ALL',
            'browser': 'ALL'
        })
        
        return webdriver.Chrome(options=options)
    
    def _extract_performance_metrics(self, driver: webdriver.Chrome) -> Dict[str, float]:
        """Extract performance metrics from browser"""
        try:
            # Execute JavaScript to get performance metrics
            metrics_script = """
            const perfData = performance.getEntriesByType('navigation')[0];
            const paintEntries = performance.getEntriesByType('paint');
            
            const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
            const lcp = performance.getEntriesByType('largest-contentful-paint')[0];
            
            return {
                domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                firstContentfulPaint: fcp ? fcp.startTime : 0,
                largestContentfulPaint: lcp ? lcp.startTime : 0,
                firstInputDelay: 0, // Would need additional monitoring
                cumulativeLayoutShift: 0, // Would need additional monitoring
                totalBlockingTime: 0, // Would need additional monitoring
                speedIndex: 0, // Would need additional monitoring
                timeToInteractive: perfData.domInteractive - perfData.navigationStart
            };
            """
            
            metrics = driver.execute_script(metrics_script)
            return metrics or {}
            
        except Exception as e:
            logger.error(f"Failed to extract performance metrics: {str(e)}")
            return {}
    
    def _extract_network_metrics(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """Extract network metrics from browser logs"""
        try:
            logs = driver.get_log('performance')
            requests = 0
            failed_requests = 0
            total_size = 0
            compressed_size = 0
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    requests += 1
                    response = message['message']['params']['response']
                    if response.get('status') >= 400:
                        failed_requests += 1
                    
                    # Get response size
                    headers = response.get('headers', {})
                    content_length = headers.get('content-length')
                    if content_length:
                        total_size += int(content_length)
                    
                    # Check for compression
                    content_encoding = headers.get('content-encoding', '')
                    if content_encoding in ['gzip', 'deflate', 'br']:
                        compressed_size += int(content_length) if content_length else 0
            
            compression_ratio = None
            if total_size > 0 and compressed_size > 0:
                compression_ratio = total_size / compressed_size
            
            return {
                'requests': requests,
                'failed_requests': failed_requests,
                'total_size': total_size,
                'compression_ratio': compression_ratio
            }
            
        except Exception as e:
            logger.error(f"Failed to extract network metrics: {str(e)}")
            return {'requests': 0, 'failed_requests': 0, 'total_size': 0}
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    async def test_api_endpoints(self, base_url: str, endpoints: List[str]) -> Dict[str, Any]:
        """
        Test API endpoint performance
        
        Args:
            base_url: Base URL of the API
            endpoints: List of API endpoints to test
            
        Returns:
            Dictionary with endpoint performance results
        """
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                try:
                    start_time = time.time()
                    async with session.get(url) as response:
                        end_time = time.time()
                        
                        response_time = end_time - start_time
                        status_code = response.status
                        content_length = len(await response.text())
                        
                        results[endpoint] = {
                            'response_time': response_time,
                            'status_code': status_code,
                            'content_length': content_length,
                            'success': status_code < 400
                        }
                        
                except Exception as e:
                    results[endpoint] = {
                        'response_time': 0,
                        'status_code': 0,
                        'content_length': 0,
                        'success': False,
                        'error': str(e)
                    }
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.results:
            return {'error': 'No test results available'}
        
        # Calculate averages
        avg_load_time = sum(r.load_time for r in self.results) / len(self.results)
        avg_fcp = sum(r.first_contentful_paint for r in self.results) / len(self.results)
        avg_lcp = sum(r.largest_contentful_paint for r in self.results) / len(self.results)
        avg_memory = sum(r.memory_usage for r in self.results) / len(self.results)
        
        # Find slowest and fastest tabs
        slowest_tab = max(self.results, key=lambda r: r.load_time)
        fastest_tab = min(self.results, key=lambda r: r.load_time)
        
        # Performance scores
        performance_scores = []
        for result in self.results:
            score = self._calculate_performance_score(result)
            performance_scores.append({
                'tab': result.tab_name,
                'score': score,
                'grade': self._get_performance_grade(score)
            })
        
        return {
            'summary': {
                'total_tabs_tested': len(self.results),
                'average_load_time': avg_load_time,
                'average_fcp': avg_fcp,
                'average_lcp': avg_lcp,
                'average_memory_usage': avg_memory,
                'slowest_tab': {
                    'name': slowest_tab.tab_name,
                    'load_time': slowest_tab.load_time
                },
                'fastest_tab': {
                    'name': fastest_tab.tab_name,
                    'load_time': fastest_tab.load_time
                }
            },
            'performance_scores': performance_scores,
            'detailed_results': [asdict(result) for result in self.results],
            'recommendations': self._generate_recommendations()
        }
    
    def _calculate_performance_score(self, result: TabPerformanceResult) -> int:
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
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if not self.results:
            return recommendations
        
        # Check for common issues
        avg_load_time = sum(r.load_time for r in self.results) / len(self.results)
        if avg_load_time > 2.0:
            recommendations.append("Consider implementing code splitting and lazy loading")
            recommendations.append("Optimize images and use modern formats (WebP, AVIF)")
            recommendations.append("Enable gzip/brotli compression on server")
        
        avg_fcp = sum(r.first_contentful_paint for r in self.results) / len(self.results)
        if avg_fcp > 1.8:
            recommendations.append("Optimize critical rendering path")
            recommendations.append("Minimize render-blocking resources")
            recommendations.append("Use resource hints (preload, prefetch)")
        
        avg_memory = sum(r.memory_usage for r in self.results) / len(self.results)
        if avg_memory > 50:
            recommendations.append("Implement memory management and cleanup")
            recommendations.append("Use virtual scrolling for large lists")
            recommendations.append("Optimize component re-renders")
        
        # Check for failed requests
        total_failed = sum(r.failed_requests for r in self.results)
        if total_failed > 0:
            recommendations.append("Fix failed network requests and implement proper error handling")
        
        return recommendations
