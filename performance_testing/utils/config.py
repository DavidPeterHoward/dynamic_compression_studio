"""
Configuration classes for performance testing
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class TestMode(Enum):
    """Test execution modes"""
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"

class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"

@dataclass
class TestConfig:
    """Configuration for performance testing"""
    
    # Test execution settings
    mode: TestMode = TestMode.STANDARD
    timeout: int = 30
    additional_wait_time: float = 2.0
    retry_count: int = 3
    
    # Performance thresholds
    fcp_threshold: float = 1.8
    lcp_threshold: float = 2.5
    fid_threshold: float = 100.0
    cls_threshold: float = 0.1
    
    # Network settings
    simulate_slow_network: bool = False
    network_condition: str = "fast3g"  # fast3g, slow3g, offline
    
    # Browser settings
    headless: bool = True
    window_size: str = "1920x1080"
    disable_images: bool = False
    disable_javascript: bool = False
    
    # Output settings
    save_screenshots: bool = False
    save_har_files: bool = False
    output_directory: str = "./performance_results"
    
    # Advanced settings
    enable_profiling: bool = True
    collect_memory_snapshots: bool = False
    analyze_bundle_size: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'mode': self.mode.value,
            'timeout': self.timeout,
            'additional_wait_time': self.additional_wait_time,
            'retry_count': self.retry_count,
            'fcp_threshold': self.fcp_threshold,
            'lcp_threshold': self.lcp_threshold,
            'fid_threshold': self.fid_threshold,
            'cls_threshold': self.cls_threshold,
            'simulate_slow_network': self.simulate_slow_network,
            'network_condition': self.network_condition,
            'headless': self.headless,
            'window_size': self.window_size,
            'disable_images': self.disable_images,
            'disable_javascript': self.disable_javascript,
            'save_screenshots': self.save_screenshots,
            'save_har_files': self.save_har_files,
            'output_directory': self.output_directory,
            'enable_profiling': self.enable_profiling,
            'collect_memory_snapshots': self.collect_memory_snapshots,
            'analyze_bundle_size': self.analyze_bundle_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestConfig':
        """Create from dictionary"""
        return cls(
            mode=TestMode(data.get('mode', 'standard')),
            timeout=data.get('timeout', 30),
            additional_wait_time=data.get('additional_wait_time', 2.0),
            retry_count=data.get('retry_count', 3),
            fcp_threshold=data.get('fcp_threshold', 1.8),
            lcp_threshold=data.get('lcp_threshold', 2.5),
            fid_threshold=data.get('fid_threshold', 100.0),
            cls_threshold=data.get('cls_threshold', 0.1),
            simulate_slow_network=data.get('simulate_slow_network', False),
            network_condition=data.get('network_condition', 'fast3g'),
            headless=data.get('headless', True),
            window_size=data.get('window_size', '1920x1080'),
            disable_images=data.get('disable_images', False),
            disable_javascript=data.get('disable_javascript', False),
            save_screenshots=data.get('save_screenshots', False),
            save_har_files=data.get('save_har_files', False),
            output_directory=data.get('output_directory', './performance_results'),
            enable_profiling=data.get('enable_profiling', True),
            collect_memory_snapshots=data.get('collect_memory_snapshots', False),
            analyze_bundle_size=data.get('analyze_bundle_size', True)
        )

@dataclass
class BrowserConfig:
    """Browser-specific configuration"""
    
    browser_type: BrowserType = BrowserType.CHROME
    headless: bool = True
    window_size: str = "1920x1080"
    
    # Chrome-specific options
    chrome_options: List[str] = None
    
    # Performance monitoring
    enable_performance_logging: bool = True
    enable_network_logging: bool = True
    enable_console_logging: bool = True
    
    # Resource blocking
    block_images: bool = False
    block_css: bool = False
    block_javascript: bool = False
    block_fonts: bool = False
    
    # Network simulation
    network_conditions: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.chrome_options is None:
            self.chrome_options = [
                '--disable-extensions',
                '--disable-plugins',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu'
            ]
        
        if self.network_conditions is None:
            self.network_conditions = {
                'fast3g': {
                    'download_throughput': 1.5 * 1024 * 1024,  # 1.5 Mbps
                    'upload_throughput': 750 * 1024,  # 750 Kbps
                    'latency': 150  # 150ms
                },
                'slow3g': {
                    'download_throughput': 500 * 1024,  # 500 Kbps
                    'upload_throughput': 500 * 1024,  # 500 Kbps
                    'latency': 400  # 400ms
                }
            }
    
    def get_chrome_options(self) -> List[str]:
        """Get Chrome options for Selenium"""
        options = self.chrome_options.copy()
        
        if self.headless:
            options.append('--headless')
        
        if self.window_size:
            options.append(f'--window-size={self.window_size}')
        
        if self.block_images:
            options.append('--disable-images')
        
        if self.block_css:
            options.append('--disable-css')
        
        if self.block_javascript:
            options.append('--disable-javascript')
        
        if self.enable_performance_logging:
            options.append('--enable-logging')
            options.append('--log-level=0')
        
        return options
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'browser_type': self.browser_type.value,
            'headless': self.headless,
            'window_size': self.window_size,
            'chrome_options': self.chrome_options,
            'enable_performance_logging': self.enable_performance_logging,
            'enable_network_logging': self.enable_network_logging,
            'enable_console_logging': self.enable_console_logging,
            'block_images': self.block_images,
            'block_css': self.block_css,
            'block_javascript': self.block_javascript,
            'block_fonts': self.block_fonts,
            'network_conditions': self.network_conditions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrowserConfig':
        """Create from dictionary"""
        return cls(
            browser_type=BrowserType(data.get('browser_type', 'chrome')),
            headless=data.get('headless', True),
            window_size=data.get('window_size', '1920x1080'),
            chrome_options=data.get('chrome_options', []),
            enable_performance_logging=data.get('enable_performance_logging', True),
            enable_network_logging=data.get('enable_network_logging', True),
            enable_console_logging=data.get('enable_console_logging', True),
            block_images=data.get('block_images', False),
            block_css=data.get('block_css', False),
            block_javascript=data.get('block_javascript', False),
            block_fonts=data.get('block_fonts', False),
            network_conditions=data.get('network_conditions', {})
        )
