"""
Performance metrics data structures and calculations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

@dataclass
class LoadingTimeMetrics:
    """Core web vitals and loading time metrics"""
    
    # Core Web Vitals
    first_contentful_paint: float = 0.0
    largest_contentful_paint: float = 0.0
    first_input_delay: float = 0.0
    cumulative_layout_shift: float = 0.0
    
    # Additional Performance Metrics
    dom_content_loaded: float = 0.0
    load_complete: float = 0.0
    time_to_interactive: float = 0.0
    speed_index: float = 0.0
    total_blocking_time: float = 0.0
    
    # Network Metrics
    network_requests: int = 0
    failed_requests: int = 0
    total_transfer_size: int = 0
    compression_ratio: Optional[float] = None
    
    # Resource Metrics
    images_loaded: int = 0
    css_files_loaded: int = 0
    js_files_loaded: int = 0
    font_files_loaded: int = 0
    
    # Memory Metrics
    memory_usage_mb: float = 0.0
    memory_peak_mb: float = 0.0
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'first_contentful_paint': self.first_contentful_paint,
            'largest_contentful_paint': self.largest_contentful_paint,
            'first_input_delay': self.first_input_delay,
            'cumulative_layout_shift': self.cumulative_layout_shift,
            'dom_content_loaded': self.dom_content_loaded,
            'load_complete': self.load_complete,
            'time_to_interactive': self.time_to_interactive,
            'speed_index': self.speed_index,
            'total_blocking_time': self.total_blocking_time,
            'network_requests': self.network_requests,
            'failed_requests': self.failed_requests,
            'total_transfer_size': self.total_transfer_size,
            'compression_ratio': self.compression_ratio,
            'images_loaded': self.images_loaded,
            'css_files_loaded': self.css_files_loaded,
            'js_files_loaded': self.js_files_loaded,
            'font_files_loaded': self.font_files_loaded,
            'memory_usage_mb': self.memory_usage_mb,
            'memory_peak_mb': self.memory_peak_mb,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoadingTimeMetrics':
        """Create from dictionary"""
        return cls(
            first_contentful_paint=data.get('first_contentful_paint', 0.0),
            largest_contentful_paint=data.get('largest_contentful_paint', 0.0),
            first_input_delay=data.get('first_input_delay', 0.0),
            cumulative_layout_shift=data.get('cumulative_layout_shift', 0.0),
            dom_content_loaded=data.get('dom_content_loaded', 0.0),
            load_complete=data.get('load_complete', 0.0),
            time_to_interactive=data.get('time_to_interactive', 0.0),
            speed_index=data.get('speed_index', 0.0),
            total_blocking_time=data.get('total_blocking_time', 0.0),
            network_requests=data.get('network_requests', 0),
            failed_requests=data.get('failed_requests', 0),
            total_transfer_size=data.get('total_transfer_size', 0),
            compression_ratio=data.get('compression_ratio'),
            images_loaded=data.get('images_loaded', 0),
            css_files_loaded=data.get('css_files_loaded', 0),
            js_files_loaded=data.get('js_files_loaded', 0),
            font_files_loaded=data.get('font_files_loaded', 0),
            memory_usage_mb=data.get('memory_usage_mb', 0.0),
            memory_peak_mb=data.get('memory_peak_mb', 0.0),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        )
    
    def calculate_performance_score(self) -> int:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Core Web Vitals scoring
        if self.first_contentful_paint > 2.5:
            score -= 25
        elif self.first_contentful_paint > 1.8:
            score -= 15
        elif self.first_contentful_paint > 1.0:
            score -= 10
        
        if self.largest_contentful_paint > 4.0:
            score -= 20
        elif self.largest_contentful_paint > 2.5:
            score -= 10
        
        if self.first_input_delay > 300:
            score -= 15
        elif self.first_input_delay > 100:
            score -= 10
        
        if self.cumulative_layout_shift > 0.25:
            score -= 15
        elif self.cumulative_layout_shift > 0.1:
            score -= 10
        
        # Additional metrics
        if self.time_to_interactive > 5.0:
            score -= 15
        elif self.time_to_interactive > 3.0:
            score -= 10
        
        if self.total_blocking_time > 300:
            score -= 10
        elif self.total_blocking_time > 200:
            score -= 5
        
        # Network and resource penalties
        if self.failed_requests > 0:
            score -= min(self.failed_requests * 5, 20)
        
        if self.memory_usage_mb > 100:
            score -= 10
        elif self.memory_usage_mb > 50:
            score -= 5
        
        return max(0, score)
    
    def get_performance_grade(self) -> str:
        """Get performance grade based on score"""
        score = self.calculate_performance_score()
        
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
    
    def get_core_web_vitals_status(self) -> Dict[str, str]:
        """Get Core Web Vitals status (Good, Needs Improvement, Poor)"""
        status = {}
        
        # FCP
        if self.first_contentful_paint <= 1.8:
            status['first_contentful_paint'] = 'Good'
        elif self.first_contentful_paint <= 3.0:
            status['first_contentful_paint'] = 'Needs Improvement'
        else:
            status['first_contentful_paint'] = 'Poor'
        
        # LCP
        if self.largest_contentful_paint <= 2.5:
            status['largest_contentful_paint'] = 'Good'
        elif self.largest_contentful_paint <= 4.0:
            status['largest_contentful_paint'] = 'Needs Improvement'
        else:
            status['largest_contentful_paint'] = 'Poor'
        
        # FID
        if self.first_input_delay <= 100:
            status['first_input_delay'] = 'Good'
        elif self.first_input_delay <= 300:
            status['first_input_delay'] = 'Needs Improvement'
        else:
            status['first_input_delay'] = 'Poor'
        
        # CLS
        if self.cumulative_layout_shift <= 0.1:
            status['cumulative_layout_shift'] = 'Good'
        elif self.cumulative_layout_shift <= 0.25:
            status['cumulative_layout_shift'] = 'Needs Improvement'
        else:
            status['cumulative_layout_shift'] = 'Poor'
        
        return status

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for a page/tab"""
    
    # Basic Information
    page_name: str
    url: str
    
    # Loading Time Metrics
    loading_metrics: LoadingTimeMetrics
    
    # Performance Scores
    performance_score: int = 0
    performance_grade: str = 'F'
    
    # Core Web Vitals Status
    core_web_vitals_status: Dict[str, str] = field(default_factory=dict)
    
    # Additional Analysis
    optimization_opportunities: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate derived metrics after initialization"""
        self.performance_score = self.loading_metrics.calculate_performance_score()
        self.performance_grade = self.loading_metrics.get_performance_grade()
        self.core_web_vitals_status = self.loading_metrics.get_core_web_vitals_status()
        
        # Identify optimization opportunities
        self.optimization_opportunities = self._identify_optimization_opportunities()
        
        # Identify critical issues
        self.critical_issues = self._identify_critical_issues()
    
    def _identify_optimization_opportunities(self) -> List[str]:
        """Identify optimization opportunities based on metrics"""
        opportunities = []
        
        if self.loading_metrics.first_contentful_paint > 1.8:
            opportunities.append("Optimize First Contentful Paint - consider critical CSS inlining")
        
        if self.loading_metrics.largest_contentful_paint > 2.5:
            opportunities.append("Optimize Largest Contentful Paint - optimize images and fonts")
        
        if self.loading_metrics.first_input_delay > 100:
            opportunities.append("Reduce First Input Delay - minimize JavaScript execution time")
        
        if self.loading_metrics.cumulative_layout_shift > 0.1:
            opportunities.append("Reduce Cumulative Layout Shift - reserve space for dynamic content")
        
        if self.loading_metrics.total_blocking_time > 200:
            opportunities.append("Reduce Total Blocking Time - code splitting and lazy loading")
        
        if self.loading_metrics.failed_requests > 0:
            opportunities.append("Fix failed network requests")
        
        if self.loading_metrics.memory_usage_mb > 50:
            opportunities.append("Optimize memory usage - implement cleanup and lazy loading")
        
        if self.loading_metrics.compression_ratio and self.loading_metrics.compression_ratio < 0.7:
            opportunities.append("Improve compression ratio - enable gzip/brotli compression")
        
        return opportunities
    
    def _identify_critical_issues(self) -> List[str]:
        """Identify critical performance issues"""
        issues = []
        
        if self.loading_metrics.first_contentful_paint > 3.0:
            issues.append("Critical: First Contentful Paint is too slow (>3.0s)")
        
        if self.loading_metrics.largest_contentful_paint > 4.0:
            issues.append("Critical: Largest Contentful Paint is too slow (>4.0s)")
        
        if self.loading_metrics.first_input_delay > 300:
            issues.append("Critical: First Input Delay is too high (>300ms)")
        
        if self.loading_metrics.cumulative_layout_shift > 0.25:
            issues.append("Critical: Cumulative Layout Shift is too high (>0.25)")
        
        if self.loading_metrics.failed_requests > 5:
            issues.append("Critical: Too many failed network requests")
        
        if self.loading_metrics.memory_usage_mb > 100:
            issues.append("Critical: Memory usage is too high (>100MB)")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'page_name': self.page_name,
            'url': self.url,
            'loading_metrics': self.loading_metrics.to_dict(),
            'performance_score': self.performance_score,
            'performance_grade': self.performance_grade,
            'core_web_vitals_status': self.core_web_vitals_status,
            'optimization_opportunities': self.optimization_opportunities,
            'critical_issues': self.critical_issues,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        """Create from dictionary"""
        return cls(
            page_name=data.get('page_name', ''),
            url=data.get('url', ''),
            loading_metrics=LoadingTimeMetrics.from_dict(data.get('loading_metrics', {})),
            performance_score=data.get('performance_score', 0),
            performance_grade=data.get('performance_grade', 'F'),
            core_web_vitals_status=data.get('core_web_vitals_status', {}),
            optimization_opportunities=data.get('optimization_opportunities', []),
            critical_issues=data.get('critical_issues', []),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'page_name': self.page_name,
            'performance_score': self.performance_score,
            'performance_grade': self.performance_grade,
            'core_web_vitals': {
                'fcp': {
                    'value': self.loading_metrics.first_contentful_paint,
                    'status': self.core_web_vitals_status.get('first_contentful_paint', 'Unknown')
                },
                'lcp': {
                    'value': self.loading_metrics.largest_contentful_paint,
                    'status': self.core_web_vitals_status.get('largest_contentful_paint', 'Unknown')
                },
                'fid': {
                    'value': self.loading_metrics.first_input_delay,
                    'status': self.core_web_vitals_status.get('first_input_delay', 'Unknown')
                },
                'cls': {
                    'value': self.loading_metrics.cumulative_layout_shift,
                    'status': self.core_web_vitals_status.get('cumulative_layout_shift', 'Unknown')
                }
            },
            'loading_times': {
                'dom_content_loaded': self.loading_metrics.dom_content_loaded,
                'load_complete': self.loading_metrics.load_complete,
                'time_to_interactive': self.loading_metrics.time_to_interactive
            },
            'network': {
                'requests': self.loading_metrics.network_requests,
                'failed_requests': self.loading_metrics.failed_requests,
                'transfer_size': self.loading_metrics.total_transfer_size,
                'compression_ratio': self.loading_metrics.compression_ratio
            },
            'resources': {
                'images': self.loading_metrics.images_loaded,
                'css_files': self.loading_metrics.css_files_loaded,
                'js_files': self.loading_metrics.js_files_loaded,
                'font_files': self.loading_metrics.font_files_loaded
            },
            'memory': {
                'usage_mb': self.loading_metrics.memory_usage_mb,
                'peak_mb': self.loading_metrics.memory_peak_mb
            },
            'issues': {
                'critical_count': len(self.critical_issues),
                'optimization_count': len(self.optimization_opportunities)
            }
        }
