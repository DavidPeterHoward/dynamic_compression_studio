"""
Enhanced Metrics Collector with Real System Data
Collects ALL system metrics with accurate, live data.
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.models.metrics import PerformanceMetrics


class EnhancedSystemMetrics:
    """Collect comprehensive system metrics with real data."""
    
    @staticmethod
    def get_comprehensive_system_metrics() -> Dict[str, Any]:
        """
        Collect all available system metrics with real data.
        Works in Docker containers on Windows, Linux, and macOS.
        """
        try:
            return {
                # Basic system metrics
                "cpu_usage": psutil.cpu_percent(interval=0.1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_usage": EnhancedSystemMetrics._get_network_usage_percent(),
                
                # Process information
                "processes": len(psutil.pids()),
                "threads": sum([p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info.get('num_threads')]),
                "open_files": EnhancedSystemMetrics._get_open_files_count(),
                
                # System uptime
                "uptime": int(time.time() - psutil.boot_time()),
                
                # Network connections
                "network_connections": len(psutil.net_connections(kind='inet')),
                "active_connections": len([c for c in psutil.net_connections(kind='inet') if c.status == 'ESTABLISHED']),
                
                # CPU details
                "cpu_details": EnhancedSystemMetrics._get_cpu_details(),
                
                # Memory details
                "memory_details": EnhancedSystemMetrics._get_memory_details(),
                
                # Disk details
                "disk_details": EnhancedSystemMetrics._get_disk_details(),
                
                # Network details
                "network_details": EnhancedSystemMetrics._get_network_details(),
                
                # Load average (Unix-like systems)
                "load_average": EnhancedSystemMetrics._get_load_average(),
                
                # Additional metrics
                "swap_usage": psutil.swap_memory().percent,
                "disk_io": EnhancedSystemMetrics._get_disk_io_stats(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return EnhancedSystemMetrics._get_fallback_metrics()
    
    @staticmethod
    def _get_network_usage_percent() -> float:
        """Calculate network usage as a percentage."""
        try:
            # Get network I/O stats
            net_io1 = psutil.net_io_counters()
            time.sleep(0.1)
            net_io2 = psutil.net_io_counters()
            
            # Calculate bytes per second
            bytes_sent_per_sec = (net_io2.bytes_sent - net_io1.bytes_sent) / 0.1
            bytes_recv_per_sec = (net_io2.bytes_recv - net_io1.bytes_recv) / 0.1
            total_bytes_per_sec = bytes_sent_per_sec + bytes_recv_per_sec
            
            # Assume 1 Gbps connection (125 MB/s), calculate percentage
            # Adjust this value based on your actual network capacity
            max_bandwidth = 125 * 1024 * 1024  # 125 MB/s in bytes
            usage_percent = (total_bytes_per_sec / max_bandwidth) * 100
            
            return min(usage_percent, 100.0)
        except Exception:
            return 0.0
    
    @staticmethod
    def _get_open_files_count() -> int:
        """Get total number of open files across all processes."""
        try:
            total_files = 0
            for proc in psutil.process_iter(['open_files']):
                try:
                    files = proc.info.get('open_files')
                    if files:
                        total_files += len(files)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            return total_files
        except Exception:
            return 0
    
    @staticmethod
    def _get_cpu_details() -> Dict[str, Any]:
        """Get detailed CPU information."""
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_percent_per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Try to get temperature (works on some systems)
            temperature = 0.0
            try:
                temps = psutil.sensors_temperatures()
                if temps and 'coretemp' in temps:
                    temperature = temps['coretemp'][0].current
            except (AttributeError, KeyError):
                temperature = 0.0
            
            return {
                "cores": psutil.cpu_count(logical=False) or psutil.cpu_count(),
                "threads": psutil.cpu_count(logical=True),
                "frequency": cpu_freq.current if cpu_freq else 0.0,
                "frequency_max": cpu_freq.max if cpu_freq else 0.0,
                "frequency_min": cpu_freq.min if cpu_freq else 0.0,
                "temperature": temperature,
                "usage_per_cpu": cpu_percent_per_cpu,
                "load": [x / psutil.cpu_count() * 100 for x in EnhancedSystemMetrics._get_load_average()]
            }
        except Exception as e:
            print(f"Error getting CPU details: {e}")
            return {
                "cores": psutil.cpu_count(logical=False) or 0,
                "threads": psutil.cpu_count(logical=True) or 0,
                "frequency": 0.0,
                "temperature": 0.0,
                "usage_per_cpu": [],
                "load": [0, 0, 0]
            }
    
    @staticmethod
    def _get_memory_details() -> Dict[str, Any]:
        """Get detailed memory information."""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "percent": mem.percent,
                "cached": getattr(mem, 'cached', 0),
                "buffers": getattr(mem, 'buffers', 0),
                "shared": getattr(mem, 'shared', 0),
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free,
                "swap_percent": swap.percent
            }
        except Exception as e:
            print(f"Error getting memory details: {e}")
            return {
                "total": 0,
                "available": 0,
                "used": 0,
                "free": 0,
                "percent": 0.0,
                "cached": 0,
                "buffers": 0,
                "swap_total": 0,
                "swap_used": 0,
                "swap_free": 0,
                "swap_percent": 0.0
            }
    
    @staticmethod
    def _get_disk_details() -> Dict[str, Any]:
        """Get detailed disk information."""
        try:
            disk = psutil.disk_usage('/')
            io_counters = psutil.disk_io_counters()
            
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "read_bytes": io_counters.read_bytes if io_counters else 0,
                "write_bytes": io_counters.write_bytes if io_counters else 0,
                "read_count": io_counters.read_count if io_counters else 0,
                "write_count": io_counters.write_count if io_counters else 0
            }
        except Exception as e:
            print(f"Error getting disk details: {e}")
            return {
                "total": 0,
                "used": 0,
                "free": 0,
                "percent": 0.0,
                "read_bytes": 0,
                "write_bytes": 0,
                "read_count": 0,
                "write_count": 0
            }
    
    @staticmethod
    def _get_network_details() -> Dict[str, Any]:
        """Get detailed network information."""
        try:
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections(kind='inet')
            
            # Count connections by status
            connection_stats = {}
            for conn in connections:
                status = conn.status
                connection_stats[status] = connection_stats.get(status, 0) + 1
            
            # Get per-interface stats
            interfaces = {}
            try:
                net_if_stats = psutil.net_if_stats()
                net_if_addrs = psutil.net_if_addrs()
                per_nic = psutil.net_io_counters(pernic=True)
                
                for iface_name, stats in net_if_stats.items():
                    if iface_name in per_nic:
                        nic_io = per_nic[iface_name]
                        interfaces[iface_name] = {
                            "is_up": stats.isup,
                            "speed": stats.speed,
                            "mtu": stats.mtu,
                            "bytes_sent": nic_io.bytes_sent,
                            "bytes_recv": nic_io.bytes_recv,
                            "packets_sent": nic_io.packets_sent,
                            "packets_recv": nic_io.packets_recv,
                            "errors_in": nic_io.errin,
                            "errors_out": nic_io.errout,
                            "drops_in": nic_io.dropin,
                            "drops_out": nic_io.dropout
                        }
            except Exception:
                interfaces = {}
            
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errors_in": net_io.errin,
                "errors_out": net_io.errout,
                "drops_in": net_io.dropin,
                "drops_out": net_io.dropout,
                "total_connections": len(connections),
                "established_connections": connection_stats.get('ESTABLISHED', 0),
                "listen_connections": connection_stats.get('LISTEN', 0),
                "time_wait_connections": connection_stats.get('TIME_WAIT', 0),
                "connection_stats": connection_stats,
                "interfaces": interfaces
            }
        except Exception as e:
            print(f"Error getting network details: {e}")
            return {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0,
                "errors_in": 0,
                "errors_out": 0,
                "drops_in": 0,
                "drops_out": 0,
                "total_connections": 0,
                "connection_stats": {},
                "interfaces": {}
            }
    
    @staticmethod
    def _get_load_average() -> List[float]:
        """Get system load average (Unix-like systems only)."""
        try:
            if hasattr(psutil, 'getloadavg'):
                return list(psutil.getloadavg())
            else:
                # Fallback for Windows - estimate from CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                return [cpu_percent / 100.0] * 3
        except Exception:
            return [0.0, 0.0, 0.0]
    
    @staticmethod
    def _get_disk_io_stats() -> Dict[str, Any]:
        """Get disk I/O statistics."""
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                return {
                    "read_mb_per_sec": 0.0,  # Would need sampling
                    "write_mb_per_sec": 0.0,  # Would need sampling
                    "total_read_mb": io_counters.read_bytes / (1024 * 1024),
                    "total_write_mb": io_counters.write_bytes / (1024 * 1024)
                }
            return {"read_mb_per_sec": 0.0, "write_mb_per_sec": 0.0, "total_read_mb": 0.0, "total_write_mb": 0.0}
        except Exception:
            return {"read_mb_per_sec": 0.0, "write_mb_per_sec": 0.0, "total_read_mb": 0.0, "total_write_mb": 0.0}
    
    @staticmethod
    def _get_fallback_metrics() -> Dict[str, Any]:
        """Return fallback metrics when collection fails."""
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_usage": 0.0,
            "processes": 0,
            "threads": 0,
            "open_files": 0,
            "uptime": 0,
            "network_connections": 0,
            "active_connections": 0,
            "cpu_details": {},
            "memory_details": {},
            "disk_details": {},
            "network_details": {},
            "load_average": [0.0, 0.0, 0.0],
            "swap_usage": 0.0,
            "disk_io": {},
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Failed to collect metrics"
        }


# Integrate with existing PerformanceMetrics model
def get_enhanced_performance_metrics() -> PerformanceMetrics:
    """Get performance metrics using enhanced collector."""
    system_metrics = EnhancedSystemMetrics.get_comprehensive_system_metrics()
    
    return PerformanceMetrics(
        cpu_usage=system_metrics["cpu_usage"],
        memory_usage=system_metrics["memory_usage"],
        disk_usage=system_metrics["disk_usage"],
        network_usage=system_metrics["network_usage"],
        active_connections=system_metrics["active_connections"],
        requests_per_second=0.0,  # Application-specific, calculated elsewhere
        average_response_time=0.0,  # Application-specific, calculated elsewhere
        error_rate=0.0,  # Application-specific, calculated elsewhere
        queue_size=0,  # Application-specific, calculated elsewhere
        queue_processing_rate=0.0,  # Application-specific, calculated elsewhere
        average_wait_time=0.0  # Application-specific, calculated elsewhere
    )

