# Metrics collection utilities

import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

@dataclass
class MetricsCollector:
    """Base metrics collector"""
    
    def collect_metrics(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """Collect basic performance metrics"""
        try:
            # Get navigation timing
            navigation_timing = driver.execute_script("""
                return window.performance.timing;
            """)
            
            # Get resource timing
            resource_timing = driver.execute_script("""
                return window.performance.getEntriesByType('resource');
            """)
            
            return {
                'navigation_timing': navigation_timing,
                'resource_timing': resource_timing
            }
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}
    
    def collect_memory_metrics(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """Collect memory usage metrics"""
        try:
            memory_info = driver.execute_script("""
                return {
                    usedJSHeapSize: performance.memory ? performance.memory.usedJSHeapSize : null,
                    totalJSHeapSize: performance.memory ? performance.memory.totalJSHeapSize : null,
                    jsHeapSizeLimit: performance.memory ? performance.memory.jsHeapSizeLimit : null
                };
            """)
            return memory_info
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
            return {}
    
    def collect_network_metrics(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """Collect network performance metrics"""
        try:
            network_info = driver.execute_script("""
                return {
                    connection: navigator.connection ? {
                        effectiveType: navigator.connection.effectiveType,
                        downlink: navigator.connection.downlink,
                        rtt: navigator.connection.rtt
                    } : null
                };
            """)
            return network_info
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
            return {}

@dataclass
class BrowserMetricsCollector(MetricsCollector):
    """Browser-specific metrics collector"""
    
    def collect_browser_metrics(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """Collect browser-specific metrics"""
        try:
            # Get browser info
            browser_info = {
                'user_agent': driver.execute_script("return navigator.userAgent;"),
                'language': driver.execute_script("return navigator.language;"),
                'platform': driver.execute_script("return navigator.platform;"),
                'cookie_enabled': driver.execute_script("return navigator.cookieEnabled;"),
                'on_line': driver.execute_script("return navigator.onLine;")
            }
            
            # Get viewport info
            viewport_info = driver.execute_script("""
                return {
                    width: window.innerWidth,
                    height: window.innerHeight,
                    devicePixelRatio: window.devicePixelRatio
                };
            """)
            
            return {
                'browser_info': browser_info,
                'viewport_info': viewport_info
            }
        except Exception as e:
            logger.error(f"Error collecting browser metrics: {e}")
            return {}
    
    def collect_performance_metrics(self, driver: webdriver.Chrome) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        try:
            # Get performance entries
            performance_entries = driver.execute_script("""
                return {
                    navigation: performance.getEntriesByType('navigation'),
                    resource: performance.getEntriesByType('resource'),
                    paint: performance.getEntriesByType('paint'),
                    measure: performance.getEntriesByType('measure'),
                    mark: performance.getEntriesByType('mark')
                };
            """)
            
            # Get timing marks
            timing_marks = driver.execute_script("""
                return {
                    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.domContentLoadedEventStart,
                    loadComplete: performance.timing.loadEventEnd - performance.timing.loadEventStart,
                    firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || null,
                    firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || null
                };
            """)
            
            return {
                'performance_entries': performance_entries,
                'timing_marks': timing_marks
            }
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return {}
