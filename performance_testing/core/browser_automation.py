# Browser automation utilities for performance testing

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class BrowserAutomation:
    """Browser automation utilities for performance testing"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome driver with performance monitoring"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        
        # Performance monitoring
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.add_argument('--v=1')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def navigate_to_url(self, url, timeout=30):
        """Navigate to URL and wait for page load"""
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        except TimeoutException:
            logger.error(f"Timeout waiting for page load: {url}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def get_performance_metrics(self):
        """Get browser performance metrics"""
        if not self.driver:
            return None
        
        try:
            # Get navigation timing
            navigation_timing = self.driver.execute_script("""
                return window.performance.timing;
            """)
            
            # Get resource timing
            resource_timing = self.driver.execute_script("""
                return window.performance.getEntriesByType('resource');
            """)
            
            return {
                'navigation_timing': navigation_timing,
                'resource_timing': resource_timing
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            finally:
                self.driver = None
