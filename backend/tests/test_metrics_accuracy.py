"""
Comprehensive Metrics Accuracy Test Suite
Tests every datapoint in the System Metrics tab to ensure accuracy.
"""

import pytest
import psutil
import time
from datetime import datetime
from typing import Dict, Any

from app.core.metrics_collector import MetricsCollector
from app.models.metrics import PerformanceMetrics


class TestMetricsAccuracy:
    """Test suite to verify accuracy of all system metrics."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create a metrics collector instance."""
        return MetricsCollector()
    
    def test_cpu_usage_accuracy(self, metrics_collector):
        """Test CPU usage metric is within acceptable range."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # CPU usage should be between 0 and 100
        assert 0 <= metrics.cpu_usage <= 100, f"CPU usage {metrics.cpu_usage}% is out of range"
        
        # Verify it matches psutil reading (with tolerance)
        actual_cpu = psutil.cpu_percent(interval=1)
        tolerance = 15  # Allow 15% difference due to timing
        assert abs(metrics.cpu_usage - actual_cpu) <= tolerance, \
            f"CPU metric {metrics.cpu_usage}% differs too much from actual {actual_cpu}%"
        
        print(f"✓ CPU Usage: {metrics.cpu_usage}% (actual: {actual_cpu}%)")
    
    def test_memory_usage_accuracy(self, metrics_collector):
        """Test memory usage metric is accurate."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # Memory usage should be between 0 and 100
        assert 0 <= metrics.memory_usage <= 100, f"Memory usage {metrics.memory_usage}% is out of range"
        
        # Verify it matches psutil reading
        actual_memory = psutil.virtual_memory().percent
        tolerance = 5  # Allow 5% difference
        assert abs(metrics.memory_usage - actual_memory) <= tolerance, \
            f"Memory metric {metrics.memory_usage}% differs from actual {actual_memory}%"
        
        print(f"✓ Memory Usage: {metrics.memory_usage}% (actual: {actual_memory}%)")
    
    def test_disk_usage_accuracy(self, metrics_collector):
        """Test disk usage metric is accurate."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # Disk usage should be between 0 and 100
        assert 0 <= metrics.disk_usage <= 100, f"Disk usage {metrics.disk_usage}% is out of range"
        
        # Verify it matches psutil reading
        actual_disk = psutil.disk_usage('/').percent
        tolerance = 5  # Allow 5% difference
        assert abs(metrics.disk_usage - actual_disk) <= tolerance, \
            f"Disk metric {metrics.disk_usage}% differs from actual {actual_disk}%"
        
        print(f"✓ Disk Usage: {metrics.disk_usage}% (actual: {actual_disk}%)")
    
    def test_network_usage_accuracy(self, metrics_collector):
        """Test network usage metric exists and is reasonable."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # Network usage should be between 0 and 100
        assert 0 <= metrics.network_usage <= 100, f"Network usage {metrics.network_usage}% is out of range"
        
        print(f"✓ Network Usage: {metrics.network_usage}%")
    
    def test_active_connections_accuracy(self, metrics_collector):
        """Test active connections count is accurate."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # Get actual connections count
        actual_connections = len(psutil.net_connections())
        
        # Verify the metric
        assert metrics.active_connections >= 0, "Active connections cannot be negative"
        
        # Allow some variance since connections can change quickly
        tolerance_ratio = 0.5  # Allow 50% difference
        min_expected = actual_connections * (1 - tolerance_ratio)
        max_expected = actual_connections * (1 + tolerance_ratio)
        
        assert min_expected <= metrics.active_connections <= max_expected or \
               abs(metrics.active_connections - actual_connections) <= 50, \
            f"Active connections {metrics.active_connections} differs significantly from actual {actual_connections}"
        
        print(f"✓ Active Connections: {metrics.active_connections} (actual: {actual_connections})")
    
    def test_queue_metrics_accuracy(self, metrics_collector):
        """Test queue-related metrics."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # Queue size should be non-negative
        assert metrics.queue_size >= 0, "Queue size cannot be negative"
        
        # Queue processing rate should be non-negative
        assert metrics.queue_processing_rate >= 0, "Queue processing rate cannot be negative"
        
        # Average wait time should be non-negative
        assert metrics.average_wait_time >= 0, "Average wait time cannot be negative"
        
        print(f"✓ Queue Size: {metrics.queue_size}")
        print(f"✓ Queue Processing Rate: {metrics.queue_processing_rate}")
        print(f"✓ Average Wait Time: {metrics.average_wait_time}s")
    
    def test_requests_per_second_accuracy(self, metrics_collector):
        """Test requests per second metric."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # RPS should be non-negative
        assert metrics.requests_per_second >= 0, "RPS cannot be negative"
        
        print(f"✓ Requests Per Second: {metrics.requests_per_second}")
    
    def test_response_time_accuracy(self, metrics_collector):
        """Test average response time metric."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # Response time should be non-negative
        assert metrics.average_response_time >= 0, "Response time cannot be negative"
        
        # Response time should be reasonable (less than 60 seconds)
        assert metrics.average_response_time < 60, \
            f"Response time {metrics.average_response_time}s seems unreasonably high"
        
        print(f"✓ Average Response Time: {metrics.average_response_time}s")
    
    def test_error_rate_accuracy(self, metrics_collector):
        """Test error rate metric."""
        metrics = metrics_collector.collect_performance_metrics()
        
        # Error rate should be between 0 and 100
        assert 0 <= metrics.error_rate <= 100, f"Error rate {metrics.error_rate}% is out of range"
        
        print(f"✓ Error Rate: {metrics.error_rate}%")
    
    def test_compression_metrics_accuracy(self, metrics_collector):
        """Test compression-related metrics."""
        # Test a compression operation
        original_size = 1000
        compressed_size = 400
        compression_time = 0.05
        
        metrics = metrics_collector.collect_compression_metrics(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_time=compression_time,
            algorithm="gzip"
        )
        
        # Verify compression ratio calculation
        expected_ratio = original_size / compressed_size
        assert abs(metrics.compression_ratio - expected_ratio) < 0.01, \
            f"Compression ratio {metrics.compression_ratio} doesn't match expected {expected_ratio}"
        
        # Verify compression speed calculation
        expected_speed = (original_size / 1024 / 1024) / compression_time
        assert abs(metrics.compression_speed - expected_speed) < 0.1, \
            f"Compression speed {metrics.compression_speed} doesn't match expected {expected_speed}"
        
        print(f"✓ Compression Ratio: {metrics.compression_ratio}x")
        print(f"✓ Compression Speed: {metrics.compression_speed} MB/s")
    
    def test_system_info_availability(self):
        """Test that all required system information is available."""
        # CPU info
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        assert cpu_count > 0, "CPU count should be positive"
        print(f"✓ CPU Cores: {cpu_count}")
        print(f"✓ CPU Frequency: {cpu_freq.current if cpu_freq else 0} MHz")
        
        # Memory info
        mem = psutil.virtual_memory()
        assert mem.total > 0, "Memory total should be positive"
        print(f"✓ Total Memory: {mem.total / (1024**3):.2f} GB")
        print(f"✓ Available Memory: {mem.available / (1024**3):.2f} GB")
        
        # Disk info
        disk = psutil.disk_usage('/')
        assert disk.total > 0, "Disk total should be positive"
        print(f"✓ Total Disk: {disk.total / (1024**3):.2f} GB")
        print(f"✓ Free Disk: {disk.free / (1024**3):.2f} GB")
        
        # Network info
        net_io = psutil.net_io_counters()
        assert net_io.bytes_sent >= 0, "Bytes sent should be non-negative"
        assert net_io.bytes_recv >= 0, "Bytes received should be non-negative"
        print(f"✓ Bytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB")
        print(f"✓ Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB")
        
        # Process info
        process_count = len(psutil.pids())
        assert process_count > 0, "Process count should be positive"
        print(f"✓ Process Count: {process_count}")
        
        # Boot time / uptime
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        assert uptime > 0, "Uptime should be positive"
        print(f"✓ System Uptime: {uptime / 3600:.2f} hours")


class TestMetricsEndpoints:
    """Test that API endpoints return accurate data."""
    
    @pytest.mark.asyncio
    async def test_performance_endpoint_accuracy(self):
        """Test /api/v1/metrics/performance endpoint."""
        from app.api.metrics import get_performance_metrics, get_metrics_collector
        
        collector = get_metrics_collector()
        metrics = await get_performance_metrics(metrics_collector=collector)
        
        # Verify all required fields are present
        assert hasattr(metrics, 'cpu_usage'), "Missing cpu_usage"
        assert hasattr(metrics, 'memory_usage'), "Missing memory_usage"
        assert hasattr(metrics, 'disk_usage'), "Missing disk_usage"
        assert hasattr(metrics, 'network_usage'), "Missing network_usage"
        assert hasattr(metrics, 'active_connections'), "Missing active_connections"
        assert hasattr(metrics, 'requests_per_second'), "Missing requests_per_second"
        assert hasattr(metrics, 'average_response_time'), "Missing average_response_time"
        assert hasattr(metrics, 'error_rate'), "Missing error_rate"
        
        print("✓ Performance endpoint returns all required fields")
    
    @pytest.mark.asyncio
    async def test_dashboard_endpoint_accuracy(self):
        """Test /api/v1/metrics/dashboard endpoint."""
        from app.api.metrics import get_dashboard_metrics, get_metrics_collector
        
        collector = get_metrics_collector()
        dashboard = await get_dashboard_metrics(metrics_collector=collector)
        
        # Verify structure
        assert 'overview' in dashboard, "Missing overview section"
        assert 'performance' in dashboard, "Missing performance section"
        
        # Verify overview fields
        overview = dashboard['overview']
        assert 'total_compressions_today' in overview
        assert 'average_compression_ratio' in overview
        assert 'success_rate' in overview
        
        # Verify performance fields
        performance = dashboard['performance']
        assert 'cpu_usage' in performance
        assert 'memory_usage' in performance
        assert 'disk_usage' in performance
        
        print("✓ Dashboard endpoint returns all required fields")


def run_comprehensive_test():
    """Run all tests and generate a report."""
    print("\n" + "="*80)
    print("COMPREHENSIVE METRICS ACCURACY TEST SUITE")
    print("="*80 + "\n")
    
    collector = MetricsCollector()
    test = TestMetricsAccuracy()
    
    tests = [
        ("CPU Usage", lambda: test.test_cpu_usage_accuracy(collector)),
        ("Memory Usage", lambda: test.test_memory_usage_accuracy(collector)),
        ("Disk Usage", lambda: test.test_disk_usage_accuracy(collector)),
        ("Network Usage", lambda: test.test_network_usage_accuracy(collector)),
        ("Active Connections", lambda: test.test_active_connections_accuracy(collector)),
        ("Queue Metrics", lambda: test.test_queue_metrics_accuracy(collector)),
        ("Requests Per Second", lambda: test.test_requests_per_second_accuracy(collector)),
        ("Response Time", lambda: test.test_response_time_accuracy(collector)),
        ("Error Rate", lambda: test.test_error_rate_accuracy(collector)),
        ("Compression Metrics", lambda: test.test_compression_metrics_accuracy(collector)),
        ("System Information", lambda: test.test_system_info_availability()),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        print("-" * 80)
        try:
            test_func()
            passed += 1
            print(f"✓ {test_name} PASSED\n")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} FAILED: {e}\n")
    
    print("\n" + "="*80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*80 + "\n")
    
    return passed, failed


if __name__ == "__main__":
    run_comprehensive_test()

