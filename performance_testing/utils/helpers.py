# Helper utilities for performance testing

import logging
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class PerformanceHelpers:
    """Helper utilities for performance testing"""
    
    @staticmethod
    def calculate_loading_time(navigation_timing: Dict[str, Any]) -> float:
        """Calculate total loading time from navigation timing"""
        try:
            if not navigation_timing:
                return 0.0
            
            # Calculate total loading time
            load_time = navigation_timing.get('loadEventEnd', 0) - navigation_timing.get('navigationStart', 0)
            return max(0.0, load_time)
        except Exception as e:
            logger.error(f"Error calculating loading time: {e}")
            return 0.0
    
    @staticmethod
    def calculate_dom_content_loaded_time(navigation_timing: Dict[str, Any]) -> float:
        """Calculate DOM content loaded time"""
        try:
            if not navigation_timing:
                return 0.0
            
            dom_ready_time = navigation_timing.get('domContentLoadedEventEnd', 0) - navigation_timing.get('navigationStart', 0)
            return max(0.0, dom_ready_time)
        except Exception as e:
            logger.error(f"Error calculating DOM content loaded time: {e}")
            return 0.0
    
    @staticmethod
    def calculate_first_paint_time(performance_entries: Dict[str, Any]) -> float:
        """Calculate first paint time"""
        try:
            if not performance_entries or 'paint' not in performance_entries:
                return 0.0
            
            paint_entries = performance_entries['paint']
            for entry in paint_entries:
                if entry.get('name') == 'first-paint':
                    return entry.get('startTime', 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating first paint time: {e}")
            return 0.0
    
    @staticmethod
    def calculate_first_contentful_paint_time(performance_entries: Dict[str, Any]) -> float:
        """Calculate first contentful paint time"""
        try:
            if not performance_entries or 'paint' not in performance_entries:
                return 0.0
            
            paint_entries = performance_entries['paint']
            for entry in paint_entries:
                if entry.get('name') == 'first-contentful-paint':
                    return entry.get('startTime', 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating first contentful paint time: {e}")
            return 0.0
    
    @staticmethod
    def calculate_largest_contentful_paint_time(performance_entries: Dict[str, Any]) -> float:
        """Calculate largest contentful paint time"""
        try:
            if not performance_entries or 'paint' not in performance_entries:
                return 0.0
            
            paint_entries = performance_entries['paint']
            for entry in paint_entries:
                if entry.get('name') == 'largest-contentful-paint':
                    return entry.get('startTime', 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating largest contentful paint time: {e}")
            return 0.0
    
    @staticmethod
    def calculate_cumulative_layout_shift(performance_entries: Dict[str, Any]) -> float:
        """Calculate cumulative layout shift"""
        try:
            if not performance_entries or 'measure' not in performance_entries:
                return 0.0
            
            measure_entries = performance_entries['measure']
            cls_score = 0.0
            for entry in measure_entries:
                if entry.get('name') == 'cumulative-layout-shift':
                    cls_score += entry.get('value', 0.0)
            return cls_score
        except Exception as e:
            logger.error(f"Error calculating cumulative layout shift: {e}")
            return 0.0
    
    @staticmethod
    def calculate_first_input_delay(performance_entries: Dict[str, Any]) -> float:
        """Calculate first input delay"""
        try:
            if not performance_entries or 'measure' not in performance_entries:
                return 0.0
            
            measure_entries = performance_entries['measure']
            for entry in measure_entries:
                if entry.get('name') == 'first-input-delay':
                    return entry.get('value', 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating first input delay: {e}")
            return 0.0
    
    @staticmethod
    def calculate_time_to_interactive(performance_entries: Dict[str, Any]) -> float:
        """Calculate time to interactive"""
        try:
            if not performance_entries or 'measure' not in performance_entries:
                return 0.0
            
            measure_entries = performance_entries['measure']
            for entry in measure_entries:
                if entry.get('name') == 'time-to-interactive':
                    return entry.get('value', 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating time to interactive: {e}")
            return 0.0
    
    @staticmethod
    def calculate_speed_index(performance_entries: Dict[str, Any]) -> float:
        """Calculate speed index"""
        try:
            if not performance_entries or 'measure' not in performance_entries:
                return 0.0
            
            measure_entries = performance_entries['measure']
            for entry in measure_entries:
                if entry.get('name') == 'speed-index':
                    return entry.get('value', 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating speed index: {e}")
            return 0.0
    
    @staticmethod
    def calculate_total_blocking_time(performance_entries: Dict[str, Any]) -> float:
        """Calculate total blocking time"""
        try:
            if not performance_entries or 'measure' not in performance_entries:
                return 0.0
            
            measure_entries = performance_entries['measure']
            for entry in measure_entries:
                if entry.get('name') == 'total-blocking-time':
                    return entry.get('value', 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating total blocking time: {e}")
            return 0.0
    
    @staticmethod
    def calculate_network_requests(performance_entries: Dict[str, Any]) -> int:
        """Calculate number of network requests"""
        try:
            if not performance_entries or 'resource' not in performance_entries:
                return 0
            
            resource_entries = performance_entries['resource']
            return len(resource_entries)
        except Exception as e:
            logger.error(f"Error calculating network requests: {e}")
            return 0
    
    @staticmethod
    def calculate_total_transfer_size(performance_entries: Dict[str, Any]) -> int:
        """Calculate total transfer size in bytes"""
        try:
            if not performance_entries or 'resource' not in performance_entries:
                return 0
            
            resource_entries = performance_entries['resource']
            total_size = 0
            for entry in resource_entries:
                total_size += entry.get('transferSize', 0)
            return total_size
        except Exception as e:
            logger.error(f"Error calculating total transfer size: {e}")
            return 0
    
    @staticmethod
    def calculate_dom_elements_count(performance_entries: Dict[str, Any]) -> int:
        """Calculate number of DOM elements"""
        try:
            if not performance_entries or 'measure' not in performance_entries:
                return 0
            
            measure_entries = performance_entries['measure']
            for entry in measure_entries:
                if entry.get('name') == 'dom-elements-count':
                    return entry.get('value', 0)
            return 0
        except Exception as e:
            logger.error(f"Error calculating DOM elements count: {e}")
            return 0
    
    @staticmethod
    def calculate_memory_usage(memory_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate memory usage metrics"""
        try:
            if not memory_info:
                return {}
            
            used_heap = memory_info.get('usedJSHeapSize', 0)
            total_heap = memory_info.get('totalJSHeapSize', 0)
            heap_limit = memory_info.get('jsHeapSizeLimit', 0)
            
            return {
                'used_heap_mb': used_heap / (1024 * 1024) if used_heap else 0,
                'total_heap_mb': total_heap / (1024 * 1024) if total_heap else 0,
                'heap_limit_mb': heap_limit / (1024 * 1024) if heap_limit else 0,
                'heap_usage_percentage': (used_heap / heap_limit * 100) if heap_limit and used_heap else 0
            }
        except Exception as e:
            logger.error(f"Error calculating memory usage: {e}")
            return {}
    
    @staticmethod
    def calculate_network_connection_info(network_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate network connection information"""
        try:
            if not network_info or 'connection' not in network_info:
                return {}
            
            connection = network_info['connection']
            return {
                'effective_type': connection.get('effectiveType', 'unknown'),
                'downlink_mbps': connection.get('downlink', 0),
                'rtt_ms': connection.get('rtt', 0)
            }
        except Exception as e:
            logger.error(f"Error calculating network connection info: {e}")
            return {}
    
    @staticmethod
    def calculate_performance_score(metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            if not metrics:
                return 0.0
            
            # Weight different metrics
            weights = {
                'loading_time': 0.3,
                'dom_content_loaded_time': 0.2,
                'first_paint_time': 0.2,
                'first_contentful_paint_time': 0.15,
                'largest_contentful_paint_time': 0.1,
                'cumulative_layout_shift': 0.05
            }
            
            score = 0.0
            total_weight = 0.0
            
            for metric, weight in weights.items():
                if metric in metrics:
                    value = metrics[metric]
                    if value > 0:
                        # Normalize score (lower is better for most metrics)
                        normalized_score = max(0, 100 - (value / 1000))  # Simple normalization
                        score += normalized_score * weight
                        total_weight += weight
            
            return score / total_weight if total_weight > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 0.0

@dataclass
class DataProcessor:
    """Data processing utilities for performance testing"""
    
    @staticmethod
    def process_performance_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw performance data into structured format"""
        try:
            processed_data = {}
            
            # Process navigation timing
            if 'navigation_timing' in raw_data:
                navigation_timing = raw_data['navigation_timing']
                processed_data['loading_time'] = PerformanceHelpers.calculate_loading_time(navigation_timing)
                processed_data['dom_content_loaded_time'] = PerformanceHelpers.calculate_dom_content_loaded_time(navigation_timing)
            
            # Process performance entries
            if 'performance_entries' in raw_data:
                performance_entries = raw_data['performance_entries']
                processed_data['first_paint_time'] = PerformanceHelpers.calculate_first_paint_time(performance_entries)
                processed_data['first_contentful_paint_time'] = PerformanceHelpers.calculate_first_contentful_paint_time(performance_entries)
                processed_data['largest_contentful_paint_time'] = PerformanceHelpers.calculate_largest_contentful_paint_time(performance_entries)
                processed_data['cumulative_layout_shift'] = PerformanceHelpers.calculate_cumulative_layout_shift(performance_entries)
                processed_data['first_input_delay'] = PerformanceHelpers.calculate_first_input_delay(performance_entries)
                processed_data['time_to_interactive'] = PerformanceHelpers.calculate_time_to_interactive(performance_entries)
                processed_data['speed_index'] = PerformanceHelpers.calculate_speed_index(performance_entries)
                processed_data['total_blocking_time'] = PerformanceHelpers.calculate_total_blocking_time(performance_entries)
                processed_data['network_requests'] = PerformanceHelpers.calculate_network_requests(performance_entries)
                processed_data['total_transfer_size'] = PerformanceHelpers.calculate_total_transfer_size(performance_entries)
                processed_data['dom_elements_count'] = PerformanceHelpers.calculate_dom_elements_count(performance_entries)
            
            # Process memory info
            if 'memory_info' in raw_data:
                memory_info = raw_data['memory_info']
                processed_data['memory_usage'] = PerformanceHelpers.calculate_memory_usage(memory_info)
            
            # Process network info
            if 'network_info' in raw_data:
                network_info = raw_data['network_info']
                processed_data['network_connection'] = PerformanceHelpers.calculate_network_connection_info(network_info)
            
            # Calculate overall performance score
            processed_data['performance_score'] = PerformanceHelpers.calculate_performance_score(processed_data)
            
            return processed_data
        except Exception as e:
            logger.error(f"Error processing performance data: {e}")
            return {}
    
    @staticmethod
    def generate_performance_report(processed_data: Dict[str, Any]) -> str:
        """Generate a human-readable performance report"""
        try:
            report = []
            report.append("=== Performance Test Report ===")
            report.append("")
            
            # Core Web Vitals
            report.append("Core Web Vitals:")
            report.append(f"  First Contentful Paint: {processed_data.get('first_contentful_paint_time', 0):.2f}ms")
            report.append(f"  Largest Contentful Paint: {processed_data.get('largest_contentful_paint_time', 0):.2f}ms")
            report.append(f"  Cumulative Layout Shift: {processed_data.get('cumulative_layout_shift', 0):.4f}")
            report.append("")
            
            # Loading Performance
            report.append("Loading Performance:")
            report.append(f"  Total Loading Time: {processed_data.get('loading_time', 0):.2f}ms")
            report.append(f"  DOM Content Loaded: {processed_data.get('dom_content_loaded_time', 0):.2f}ms")
            report.append(f"  First Paint: {processed_data.get('first_paint_time', 0):.2f}ms")
            report.append("")
            
            # Interactive Performance
            report.append("Interactive Performance:")
            report.append(f"  Time to Interactive: {processed_data.get('time_to_interactive', 0):.2f}ms")
            report.append(f"  First Input Delay: {processed_data.get('first_input_delay', 0):.2f}ms")
            report.append(f"  Total Blocking Time: {processed_data.get('total_blocking_time', 0):.2f}ms")
            report.append("")
            
            # Resource Performance
            report.append("Resource Performance:")
            report.append(f"  Network Requests: {processed_data.get('network_requests', 0)}")
            report.append(f"  Total Transfer Size: {processed_data.get('total_transfer_size', 0)} bytes")
            report.append(f"  DOM Elements: {processed_data.get('dom_elements_count', 0)}")
            report.append("")
            
            # Memory Usage
            if 'memory_usage' in processed_data:
                memory_usage = processed_data['memory_usage']
                report.append("Memory Usage:")
                report.append(f"  Used Heap: {memory_usage.get('used_heap_mb', 0):.2f} MB")
                report.append(f"  Total Heap: {memory_usage.get('total_heap_mb', 0):.2f} MB")
                report.append(f"  Heap Usage: {memory_usage.get('heap_usage_percentage', 0):.2f}%")
                report.append("")
            
            # Network Connection
            if 'network_connection' in processed_data:
                network_connection = processed_data['network_connection']
                report.append("Network Connection:")
                report.append(f"  Effective Type: {network_connection.get('effective_type', 'unknown')}")
                report.append(f"  Downlink: {network_connection.get('downlink_mbps', 0):.2f} Mbps")
                report.append(f"  RTT: {network_connection.get('rtt_ms', 0):.2f} ms")
                report.append("")
            
            # Overall Score
            report.append(f"Overall Performance Score: {processed_data.get('performance_score', 0):.2f}/100")
            
            return "\n".join(report)
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return "Error generating performance report"
    
    @staticmethod
    def save_performance_data(processed_data: Dict[str, Any], filename: str) -> bool:
        """Save performance data to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(processed_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")
            return False
    
    @staticmethod
    def load_performance_data(filename: str) -> Dict[str, Any]:
        """Load performance data from file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading performance data: {e}")
            return {}
    
    @staticmethod
    def compare_performance_data(baseline_data: Dict[str, Any], current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two performance datasets"""
        try:
            comparison = {}
            
            # Compare key metrics
            key_metrics = [
                'loading_time', 'dom_content_loaded_time', 'first_paint_time',
                'first_contentful_paint_time', 'largest_contentful_paint_time',
                'cumulative_layout_shift', 'time_to_interactive', 'performance_score'
            ]
            
            for metric in key_metrics:
                baseline_value = baseline_data.get(metric, 0)
                current_value = current_data.get(metric, 0)
                
                if baseline_value > 0:
                    change_percentage = ((current_value - baseline_value) / baseline_value) * 100
                    comparison[metric] = {
                        'baseline': baseline_value,
                        'current': current_value,
                        'change_percentage': change_percentage,
                        'improvement': change_percentage < 0  # Negative change is improvement for most metrics
                    }
                else:
                    comparison[metric] = {
                        'baseline': baseline_value,
                        'current': current_value,
                        'change_percentage': 0,
                        'improvement': False
                    }
            
            return comparison
        except Exception as e:
            logger.error(f"Error comparing performance data: {e}")
            return {}
    
    @staticmethod
    def generate_comparison_report(comparison_data: Dict[str, Any]) -> str:
        """Generate a comparison report between two performance datasets"""
        try:
            report = []
            report.append("=== Performance Comparison Report ===")
            report.append("")
            
            for metric, data in comparison_data.items():
                report.append(f"{metric.replace('_', ' ').title()}:")
                report.append(f"  Baseline: {data['baseline']:.2f}")
                report.append(f"  Current: {data['current']:.2f}")
                report.append(f"  Change: {data['change_percentage']:.2f}%")
                report.append(f"  Improvement: {'Yes' if data['improvement'] else 'No'}")
                report.append("")
            
            return "\n".join(report)
        except Exception as e:
            logger.error(f"Error generating comparison report: {e}")
            return "Error generating comparison report"
