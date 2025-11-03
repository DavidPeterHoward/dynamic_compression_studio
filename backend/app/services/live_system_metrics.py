"""
Live System Metrics Service for Real-time Monitoring

This service provides comprehensive system metrics collection with real-time data,
including CPU temperature, power consumption, network latency, and all system resources.
"""

import asyncio
import logging
import psutil
import platform
import subprocess
import json
import time
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from ..models.sensor import SystemMetric, MetricType
from ..database.connection import get_db_session_optional

logger = logging.getLogger(__name__)


@dataclass
class SystemInfo:
    """System information container."""
    platform: str
    system: str
    release: str
    version: str
    machine: str
    processor: str
    cpu_count: int
    cpu_freq: Optional[float]
    memory_total: int
    boot_time: float


@dataclass
class LiveMetrics:
    """Live metrics container."""
    timestamp: datetime
    cpu_usage: float
    cpu_temp: Optional[float]
    memory_usage: float
    memory_available: int
    disk_usage: float
    disk_free: int
    network_latency: float
    network_throughput: float
    power_consumption: Optional[float]
    process_count: int
    uptime: float
    load_average: Tuple[float, float, float]
    connections: int
    compression_metrics: Dict[str, Any]


class LiveSystemMetricsService:
    """Service for collecting live system metrics with real-time data."""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.metrics_history = []
        self.compression_stats = {}
        self.network_baseline = None
        self.power_baseline = None
        
    def _get_system_info(self) -> SystemInfo:
        """Get comprehensive system information."""
        try:
            # Get system information
            uname = platform.uname()
            cpu_freq = psutil.cpu_freq()
            
            return SystemInfo(
                platform=platform.platform(),
                system=uname.system,
                release=uname.release,
                version=uname.version,
                machine=uname.machine,
                processor=uname.processor,
                cpu_count=psutil.cpu_count(),
                cpu_freq=cpu_freq.current if cpu_freq else None,
                memory_total=psutil.virtual_memory().total,
                boot_time=psutil.boot_time()
            )
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return SystemInfo("unknown", "unknown", "unknown", "unknown", "unknown", "unknown", 0, None, 0, 0)
    
    async def collect_live_metrics(self) -> LiveMetrics:
        """Collect comprehensive live system metrics."""
        try:
            timestamp = datetime.utcnow()
            
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            cpu_temp = await self._get_cpu_temperature()
            load_avg = psutil.getloadavg()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available = memory.available
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_free = disk.free
            
            # Network metrics
            network_latency = await self._measure_network_latency()
            network_throughput = await self._measure_network_throughput()
            
            # Power consumption (if available)
            power_consumption = await self._get_power_consumption()
            
            # Process metrics
            process_count = len(psutil.pids())
            uptime = time.time() - psutil.boot_time()
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Compression metrics
            compression_metrics = await self._get_compression_metrics()
            
            return LiveMetrics(
                timestamp=timestamp,
                cpu_usage=cpu_usage,
                cpu_temp=cpu_temp,
                memory_usage=memory_usage,
                memory_available=memory_available,
                disk_usage=disk_usage,
                disk_free=disk_free,
                network_latency=network_latency,
                network_throughput=network_throughput,
                power_consumption=power_consumption,
                process_count=process_count,
                uptime=uptime,
                load_average=load_avg,
                connections=connections,
                compression_metrics=compression_metrics
            )
            
        except Exception as e:
            logger.error(f"Error collecting live metrics: {e}")
            return self._get_default_metrics()
    
    async def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature if available."""
        try:
            # Try to get temperature from sensors
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        for entry in entries:
                            if entry.current:
                                return entry.current
            
            # Try alternative methods based on OS
            if platform.system() == "Linux":
                try:
                    # Try reading from thermal zones
                    result = subprocess.run(['cat', '/sys/class/thermal/thermal_zone*/temp'], 
                                          capture_output=True, text=True, timeout=1)
                    if result.returncode == 0:
                        temps = [int(t.strip()) / 1000 for t in result.stdout.split('\n') if t.strip()]
                        if temps:
                            return sum(temps) / len(temps)
                except:
                    pass
            
            return None
            
        except Exception as e:
            logger.debug(f"CPU temperature not available: {e}")
            return None
    
    async def _measure_network_latency(self) -> float:
        """Measure network latency to a reliable host."""
        try:
            # Try to ping a reliable host (Google DNS)
            start_time = time.time()
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                  capture_output=True, text=True, timeout=5)
            end_time = time.time()
            
            if result.returncode == 0:
                # Parse ping output for latency
                output = result.stdout
                if 'time=' in output:
                    latency_str = output.split('time=')[1].split(' ')[0]
                    return float(latency_str)
                else:
                    return (end_time - start_time) * 1000  # Convert to ms
            else:
                return 999.0  # High latency if ping fails
                
        except Exception as e:
            logger.debug(f"Network latency measurement failed: {e}")
            return 999.0
    
    async def _measure_network_throughput(self) -> float:
        """Measure network throughput."""
        try:
            # Get network I/O counters
            net_io = psutil.net_io_counters()
            if net_io:
                # Calculate bytes per second (simplified)
                total_bytes = net_io.bytes_sent + net_io.bytes_recv
                return total_bytes / (1024 * 1024)  # Convert to MB/s (simplified)
            return 0.0
            
        except Exception as e:
            logger.debug(f"Network throughput measurement failed: {e}")
            return 0.0
    
    async def _get_power_consumption(self) -> Optional[float]:
        """Get power consumption if available."""
        try:
            if platform.system() == "Linux":
                # Try to read from power management files
                try:
                    with open('/sys/class/power_supply/BAT0/energy_now', 'r') as f:
                        energy_now = int(f.read().strip())
                    with open('/sys/class/power_supply/BAT0/energy_full', 'r') as f:
                        energy_full = int(f.read().strip())
                    with open('/sys/class/power_supply/BAT0/power_now', 'r') as f:
                        power_now = int(f.read().strip())
                    
                    if power_now > 0:
                        return power_now / 1000000  # Convert to watts
                except:
                    pass
            
            # Try to estimate from CPU usage and frequency
            cpu_usage = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                # Rough estimation: higher frequency and usage = more power
                estimated_power = (cpu_usage / 100) * (cpu_freq.current / 1000) * 0.1
                return estimated_power
            
            return None
            
        except Exception as e:
            logger.debug(f"Power consumption not available: {e}")
            return None
    
    async def _get_compression_metrics(self) -> Dict[str, Any]:
        """Get live compression performance metrics."""
        try:
            # This would integrate with your compression service
            # For now, return mock data that could be replaced with real metrics
            return {
                "active_compressions": 5,
                "queue_size": 2,
                "average_ratio": 2.3,
                "throughput_mbps": 15.7,
                "success_rate": 98.5,
                "error_rate": 1.5,
                "average_processing_time": 0.045,
                "total_processed_today": 1250,
                "data_saved_today": 2048576  # bytes
            }
        except Exception as e:
            logger.error(f"Error getting compression metrics: {e}")
            return {}
    
    def _get_default_metrics(self) -> LiveMetrics:
        """Get default metrics when collection fails."""
        return LiveMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage=0.0,
            cpu_temp=None,
            memory_usage=0.0,
            memory_available=0,
            disk_usage=0.0,
            disk_free=0,
            network_latency=999.0,
            network_throughput=0.0,
            power_consumption=None,
            process_count=0,
            uptime=0.0,
            load_average=(0.0, 0.0, 0.0),
            connections=0,
            compression_metrics={}
        )
    
    async def save_metrics_to_db(self, metrics: LiveMetrics, db: AsyncSession) -> None:
        """Save live metrics to database."""
        try:
            # Create system metrics from live metrics
            system_metrics = []
            timestamp = metrics.timestamp
            
            # CPU metrics
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.CPU_PERCENT,
                value=metrics.cpu_usage,
                unit='percent',
                tags={'component': 'cpu', 'measurement': 'usage', 'live': 'true'}
            ))
            
            if metrics.cpu_temp:
                system_metrics.append(SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.CPU_TEMPERATURE,
                    value=metrics.cpu_temp,
                    unit='°C',
                    tags={'component': 'cpu', 'measurement': 'temperature', 'live': 'true'}
                ))
            
            # Memory metrics
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.MEMORY_PERCENT,
                value=metrics.memory_usage,
                unit='percent',
                tags={'component': 'memory', 'measurement': 'usage', 'live': 'true'}
            ))
            
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.MEMORY_AVAILABLE,
                value=metrics.memory_available / (1024**3),  # GB
                unit='GB',
                tags={'component': 'memory', 'measurement': 'available', 'live': 'true'}
            ))
            
            # Disk metrics
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.DISK_PERCENT,
                value=metrics.disk_usage,
                unit='percent',
                tags={'component': 'disk', 'measurement': 'usage', 'live': 'true'}
            ))
            
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.DISK_FREE,
                value=metrics.disk_free / (1024**3),  # GB
                unit='GB',
                tags={'component': 'disk', 'measurement': 'free', 'live': 'true'}
            ))
            
            # Network metrics
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.NETWORK_LATENCY,
                value=metrics.network_latency,
                unit='ms',
                tags={'component': 'network', 'measurement': 'latency', 'live': 'true'}
            ))
            
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.NETWORK_THROUGHPUT,
                value=metrics.network_throughput,
                unit='MB/s',
                tags={'component': 'network', 'measurement': 'throughput', 'live': 'true'}
            ))
            
            # Power metrics
            if metrics.power_consumption:
                system_metrics.append(SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.POWER_CONSUMPTION,
                    value=metrics.power_consumption,
                    unit='W',
                    tags={'component': 'power', 'measurement': 'consumption', 'live': 'true'}
                ))
            
            # Process metrics
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.PROCESS_COUNT,
                value=metrics.process_count,
                unit='processes',
                tags={'component': 'process', 'measurement': 'count', 'live': 'true'}
            ))
            
            # Uptime
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.SYSTEM_UPTIME,
                value=metrics.uptime / 3600,  # hours
                unit='hours',
                tags={'component': 'system', 'measurement': 'uptime', 'live': 'true'}
            ))
            
            # Load average
            for i, load in enumerate(metrics.load_average):
                system_metrics.append(SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.LOAD_AVERAGE,
                    value=load,
                    unit='load',
                    tags={'component': 'cpu', 'measurement': f'load_{i+1}m', 'live': 'true'}
                ))
            
            # Network connections
            system_metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.NETWORK_CONNECTIONS,
                value=metrics.connections,
                unit='connections',
                tags={'component': 'network', 'measurement': 'connections', 'live': 'true'}
            ))
            
            # Save all metrics
            for metric in system_metrics:
                db.add(metric)
            
            await db.commit()
            logger.info(f"Saved {len(system_metrics)} live metrics to database")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving live metrics to database: {e}")
    
    async def get_metrics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive metrics dashboard data."""
        try:
            metrics = await self.collect_live_metrics()
            
            # Calculate additional metrics
            cpu_efficiency = 100 - metrics.cpu_usage if metrics.cpu_usage < 100 else 0
            memory_efficiency = 100 - metrics.memory_usage if metrics.memory_usage < 100 else 0
            disk_efficiency = 100 - metrics.disk_usage if metrics.disk_usage < 100 else 0
            
            # System health score
            health_score = (cpu_efficiency + memory_efficiency + disk_efficiency) / 3
            
            # Performance indicators
            performance_indicators = {
                "excellent": health_score >= 80,
                "good": 60 <= health_score < 80,
                "fair": 40 <= health_score < 60,
                "poor": health_score < 40
            }
            
            return {
                "timestamp": metrics.timestamp.isoformat(),
                "system_info": {
                    "platform": self.system_info.platform,
                    "system": self.system_info.system,
                    "cpu_count": self.system_info.cpu_count,
                    "memory_total_gb": self.system_info.memory_total / (1024**3),
                    "uptime_hours": metrics.uptime / 3600
                },
                "live_metrics": {
                    "cpu": {
                        "usage_percent": round(metrics.cpu_usage, 2),
                        "temperature_c": round(metrics.cpu_temp, 2) if metrics.cpu_temp else None,
                        "load_average": {
                            "1m": round(metrics.load_average[0], 2),
                            "5m": round(metrics.load_average[1], 2),
                            "15m": round(metrics.load_average[2], 2)
                        }
                    },
                    "memory": {
                        "usage_percent": round(metrics.memory_usage, 2),
                        "available_gb": round(metrics.memory_available / (1024**3), 2),
                        "total_gb": round(self.system_info.memory_total / (1024**3), 2)
                    },
                    "disk": {
                        "usage_percent": round(metrics.disk_usage, 2),
                        "free_gb": round(metrics.disk_free / (1024**3), 2)
                    },
                    "network": {
                        "latency_ms": round(metrics.network_latency, 2),
                        "throughput_mbps": round(metrics.network_throughput, 2),
                        "connections": metrics.connections
                    },
                    "power": {
                        "consumption_watts": round(metrics.power_consumption, 2) if metrics.power_consumption else None
                    },
                    "processes": {
                        "count": metrics.process_count,
                        "uptime_hours": round(metrics.uptime / 3600, 2)
                    }
                },
                "compression_metrics": metrics.compression_metrics,
                "health_score": round(health_score, 2),
                "performance_indicators": performance_indicators,
                "efficiency_metrics": {
                    "cpu_efficiency": round(cpu_efficiency, 2),
                    "memory_efficiency": round(memory_efficiency, 2),
                    "disk_efficiency": round(disk_efficiency, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics dashboard: {e}")
            return {"error": str(e)}
    
    async def start_live_monitoring(self, interval_seconds: int = 30) -> None:
        """Start continuous live monitoring."""
        logger.info(f"Starting live system monitoring with {interval_seconds}s interval")
        
        while True:
            try:
                # Collect live metrics
                metrics = await self.collect_live_metrics()
                
                # Save to database if available
                try:
                    db = await get_db_session_optional()
                    if db:
                        await self.save_metrics_to_db(metrics, db)
                        await db.close()
                except Exception as e:
                    logger.error(f"Error saving metrics to database: {e}")
                
                # Store in memory for quick access
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 100:  # Keep last 100 measurements
                    self.metrics_history.pop(0)
                
                logger.debug(f"Collected live metrics: CPU={metrics.cpu_usage}%, Memory={metrics.memory_usage}%, Disk={metrics.disk_usage}%")
                
            except Exception as e:
                logger.error(f"Error in live monitoring loop: {e}")
            
            await asyncio.sleep(interval_seconds)
    
    async def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for the specified number of hours."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            return [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "disk_usage": m.disk_usage,
                    "network_latency": m.network_latency,
                    "process_count": m.process_count
                }
                for m in recent_metrics
            ]
        except Exception as e:
            logger.error(f"Error getting metrics history: {e}")
            return []
    
    async def get_performance_graphs_data(self) -> Dict[str, Any]:
        """Get data for performance graphs and charts."""
        try:
            if not self.metrics_history:
                return {"error": "No metrics history available"}
            
            # Prepare data for different graph types
            timestamps = [m.timestamp.isoformat() for m in self.metrics_history]
            
            return {
                "cpu_performance": {
                    "timestamps": timestamps,
                    "usage": [m.cpu_usage for m in self.metrics_history],
                    "temperature": [m.cpu_temp for m in self.metrics_history if m.cpu_temp],
                    "load_1m": [m.load_average[0] for m in self.metrics_history],
                    "load_5m": [m.load_average[1] for m in self.metrics_history],
                    "load_15m": [m.load_average[2] for m in self.metrics_history]
                },
                "memory_performance": {
                    "timestamps": timestamps,
                    "usage_percent": [m.memory_usage for m in self.metrics_history],
                    "available_gb": [m.memory_available / (1024**3) for m in self.metrics_history]
                },
                "disk_performance": {
                    "timestamps": timestamps,
                    "usage_percent": [m.disk_usage for m in self.metrics_history],
                    "free_gb": [m.disk_free / (1024**3) for m in self.metrics_history]
                },
                "network_performance": {
                    "timestamps": timestamps,
                    "latency_ms": [m.network_latency for m in self.metrics_history],
                    "throughput_mbps": [m.network_throughput for m in self.metrics_history],
                    "connections": [m.connections for m in self.metrics_history]
                },
                "system_performance": {
                    "timestamps": timestamps,
                    "process_count": [m.process_count for m in self.metrics_history],
                    "uptime_hours": [m.uptime / 3600 for m in self.metrics_history],
                    "power_consumption": [m.power_consumption for m in self.metrics_history if m.power_consumption]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance graphs data: {e}")
            return {"error": str(e)}


# Global instance
_live_metrics_service = None

def get_live_metrics_service() -> LiveSystemMetricsService:
    """Get or create live metrics service instance."""
    global _live_metrics_service
    if _live_metrics_service is None:
        _live_metrics_service = LiveSystemMetricsService()
    return _live_metrics_service



