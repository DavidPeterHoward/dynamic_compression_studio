"""
Metrics service for the Dynamic Compression Algorithms backend.
"""

import logging
import asyncio
import psutil
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
import numpy as np

from ..models.sensor import SystemMetric, MetricType
from ..database.connection import get_db_session_optional

logger = logging.getLogger(__name__)


class MetricsService:
    """Service for managing system metrics and performance analytics."""
    
    @staticmethod
    async def collect_system_metrics(db: AsyncSession) -> List[SystemMetric]:
        """
        Collect comprehensive system metrics.
        
        Args:
            db: Database session
            
        Returns:
            List[SystemMetric]: List of collected metrics
        """
        try:
            metrics = []
            timestamp = datetime.utcnow()
            
            # CPU metrics
            cpu_metrics = await MetricsService._collect_cpu_metrics(timestamp)
            metrics.extend(cpu_metrics)
            
            # Memory metrics
            memory_metrics = await MetricsService._collect_memory_metrics(timestamp)
            metrics.extend(memory_metrics)
            
            # Disk metrics
            disk_metrics = await MetricsService._collect_disk_metrics(timestamp)
            metrics.extend(disk_metrics)
            
            # Network metrics
            network_metrics = await MetricsService._collect_network_metrics(timestamp)
            metrics.extend(network_metrics)
            
            # Process metrics
            process_metrics = await MetricsService._collect_process_metrics(timestamp)
            metrics.extend(process_metrics)
            
            # Save all metrics
            for metric in metrics:
                db.add(metric)
            
            await db.commit()
            logger.info(f"Collected {len(metrics)} system metrics")
            return metrics
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error collecting system metrics: {e}")
            return []
    
    @staticmethod
    async def _collect_cpu_metrics(timestamp: datetime) -> List[SystemMetric]:
        """
        Collect CPU-related metrics.
        
        Args:
            timestamp: Metric timestamp
            
        Returns:
            List[SystemMetric]: CPU metrics
        """
        metrics = []
        
        try:
            # CPU percentage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.CPU_PERCENT,
                value=cpu_percent,
                unit='percent',
                tags={'component': 'cpu', 'measurement': 'usage'}
            ))
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                metrics.append(SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.CPU_FREQUENCY,
                    value=cpu_freq.current,
                    unit='MHz',
                    tags={'component': 'cpu', 'measurement': 'frequency'}
                ))
            
            # CPU count
            cpu_count = psutil.cpu_count()
            metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.CPU_COUNT,
                value=cpu_count,
                unit='cores',
                tags={'component': 'cpu', 'measurement': 'count'}
            ))
            
            # Load average
            load_avg = psutil.getloadavg()
            for i, load in enumerate(load_avg):
                metrics.append(SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.LOAD_AVERAGE,
                    value=load,
                    unit='load',
                    tags={'component': 'cpu', 'measurement': f'load_{i+1}m'}
                ))
            
            # CPU temperature (if available)
            try:
                cpu_temp = psutil.sensors_temperatures()
                if cpu_temp:
                    for name, entries in cpu_temp.items():
                        for entry in entries:
                            metrics.append(SystemMetric(
                                timestamp=timestamp,
                                metric_type=MetricType.CPU_TEMPERATURE,
                                value=entry.current,
                                unit='°C',
                                tags={'component': 'cpu', 'sensor': name, 'measurement': 'temperature'}
                            ))
            except Exception:
                pass  # CPU temperature not available
            
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
        
        return metrics
    
    @staticmethod
    async def _collect_memory_metrics(timestamp: datetime) -> List[SystemMetric]:
        """
        Collect memory-related metrics.
        
        Args:
            timestamp: Metric timestamp
            
        Returns:
            List[SystemMetric]: Memory metrics
        """
        metrics = []
        
        try:
            # Virtual memory
            virtual_memory = psutil.virtual_memory()
            metrics.extend([
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.MEMORY_TOTAL,
                    value=virtual_memory.total / (1024**3),  # GB
                    unit='GB',
                    tags={'component': 'memory', 'measurement': 'total'}
                ),
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.MEMORY_AVAILABLE,
                    value=virtual_memory.available / (1024**3),  # GB
                    unit='GB',
                    tags={'component': 'memory', 'measurement': 'available'}
                ),
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.MEMORY_USED,
                    value=virtual_memory.used / (1024**3),  # GB
                    unit='GB',
                    tags={'component': 'memory', 'measurement': 'used'}
                ),
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.MEMORY_PERCENT,
                    value=virtual_memory.percent,
                    unit='percent',
                    tags={'component': 'memory', 'measurement': 'usage'}
                )
            ])
            
            # Swap memory
            swap_memory = psutil.swap_memory()
            metrics.extend([
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.SWAP_TOTAL,
                    value=swap_memory.total / (1024**3),  # GB
                    unit='GB',
                    tags={'component': 'swap', 'measurement': 'total'}
                ),
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.SWAP_USED,
                    value=swap_memory.used / (1024**3),  # GB
                    unit='GB',
                    tags={'component': 'swap', 'measurement': 'used'}
                ),
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.SWAP_PERCENT,
                    value=swap_memory.percent,
                    unit='percent',
                    tags={'component': 'swap', 'measurement': 'usage'}
                )
            ])
            
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
        
        return metrics
    
    @staticmethod
    async def _collect_disk_metrics(timestamp: datetime) -> List[SystemMetric]:
        """
        Collect disk-related metrics.
        
        Args:
            timestamp: Metric timestamp
            
        Returns:
            List[SystemMetric]: Disk metrics
        """
        metrics = []
        
        try:
            # Disk partitions
            disk_partitions = psutil.disk_partitions()
            
            for partition in disk_partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    
                    metrics.extend([
                        SystemMetric(
                            timestamp=timestamp,
                            metric_type=MetricType.DISK_TOTAL,
                            value=disk_usage.total / (1024**3),  # GB
                            unit='GB',
                            tags={'component': 'disk', 'device': partition.device, 'mountpoint': partition.mountpoint}
                        ),
                        SystemMetric(
                            timestamp=timestamp,
                            metric_type=MetricType.DISK_USED,
                            value=disk_usage.used / (1024**3),  # GB
                            unit='GB',
                            tags={'component': 'disk', 'device': partition.device, 'mountpoint': partition.mountpoint}
                        ),
                        SystemMetric(
                            timestamp=timestamp,
                            metric_type=MetricType.DISK_FREE,
                            value=disk_usage.free / (1024**3),  # GB
                            unit='GB',
                            tags={'component': 'disk', 'device': partition.device, 'mountpoint': partition.mountpoint}
                        ),
                        SystemMetric(
                            timestamp=timestamp,
                            metric_type=MetricType.DISK_PERCENT,
                            value=disk_usage.percent,
                            unit='percent',
                            tags={'component': 'disk', 'device': partition.device, 'mountpoint': partition.mountpoint}
                        )
                    ])
                except Exception:
                    continue  # Skip partitions that can't be accessed
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.extend([
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.DISK_READ_BYTES,
                        value=disk_io.read_bytes / (1024**2),  # MB
                        unit='MB',
                        tags={'component': 'disk_io', 'measurement': 'read'}
                    ),
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.DISK_WRITE_BYTES,
                        value=disk_io.write_bytes / (1024**2),  # MB
                        unit='MB',
                        tags={'component': 'disk_io', 'measurement': 'write'}
                    ),
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.DISK_READ_COUNT,
                        value=disk_io.read_count,
                        unit='operations',
                        tags={'component': 'disk_io', 'measurement': 'read_ops'}
                    ),
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.DISK_WRITE_COUNT,
                        value=disk_io.write_count,
                        unit='operations',
                        tags={'component': 'disk_io', 'measurement': 'write_ops'}
                    )
                ])
            
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
        
        return metrics
    
    @staticmethod
    async def _collect_network_metrics(timestamp: datetime) -> List[SystemMetric]:
        """
        Collect network-related metrics.
        
        Args:
            timestamp: Metric timestamp
            
        Returns:
            List[SystemMetric]: Network metrics
        """
        metrics = []
        
        try:
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.extend([
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.NETWORK_BYTES_SENT,
                        value=net_io.bytes_sent / (1024**2),  # MB
                        unit='MB',
                        tags={'component': 'network', 'measurement': 'bytes_sent'}
                    ),
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.NETWORK_BYTES_RECV,
                        value=net_io.bytes_recv / (1024**2),  # MB
                        unit='MB',
                        tags={'component': 'network', 'measurement': 'bytes_recv'}
                    ),
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.NETWORK_PACKETS_SENT,
                        value=net_io.packets_sent,
                        unit='packets',
                        tags={'component': 'network', 'measurement': 'packets_sent'}
                    ),
                    SystemMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.NETWORK_PACKETS_RECV,
                        value=net_io.packets_recv,
                        unit='packets',
                        tags={'component': 'network', 'measurement': 'packets_recv'}
                    )
                ])
            
            # Network connections
            net_connections = psutil.net_connections()
            metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.NETWORK_CONNECTIONS,
                value=len(net_connections),
                unit='connections',
                tags={'component': 'network', 'measurement': 'active_connections'}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
        
        return metrics
    
    @staticmethod
    async def _collect_process_metrics(timestamp: datetime) -> List[SystemMetric]:
        """
        Collect process-related metrics.
        
        Args:
            timestamp: Metric timestamp
            
        Returns:
            List[SystemMetric]: Process metrics
        """
        metrics = []
        
        try:
            # Process count
            process_count = len(psutil.pids())
            metrics.append(SystemMetric(
                timestamp=timestamp,
                metric_type=MetricType.PROCESS_COUNT,
                value=process_count,
                unit='processes',
                tags={'component': 'process', 'measurement': 'count'}
            ))
            
            # Current process metrics
            current_process = psutil.Process()
            metrics.extend([
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.PROCESS_CPU_PERCENT,
                    value=current_process.cpu_percent(),
                    unit='percent',
                    tags={'component': 'process', 'measurement': 'cpu_usage'}
                ),
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.PROCESS_MEMORY_PERCENT,
                    value=current_process.memory_percent(),
                    unit='percent',
                    tags={'component': 'process', 'measurement': 'memory_usage'}
                ),
                SystemMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.PROCESS_MEMORY_RSS,
                    value=current_process.memory_info().rss / (1024**2),  # MB
                    unit='MB',
                    tags={'component': 'process', 'measurement': 'memory_rss'}
                )
            ])
            
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
        
        return metrics
    
    @staticmethod
    async def get_metrics(
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: int = 1000,
        db: AsyncSession = None
    ) -> List[SystemMetric]:
        """
        Get metrics with filters.
        
        Args:
            metric_type: Filter by metric type
            start_time: Start time filter
            end_time: End time filter
            tags: Tag filters
            limit: Maximum number of metrics
            db: Database session
            
        Returns:
            List[SystemMetric]: List of metrics
        """
        try:
            if db is None:
                db = await get_db_session_optional()
                if db is None:
                    return []
            
            query = select(SystemMetric)
            
            conditions = []
            if metric_type:
                conditions.append(SystemMetric.metric_type == metric_type)
            if start_time:
                conditions.append(SystemMetric.timestamp >= start_time)
            if end_time:
                conditions.append(SystemMetric.timestamp <= end_time)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(desc(SystemMetric.timestamp)).limit(limit)
            
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            # Filter by tags if provided
            if tags:
                filtered_metrics = []
                for metric in metrics:
                    metric_tags = metric.tags or {}
                    if all(metric_tags.get(k) == v for k, v in tags.items()):
                        filtered_metrics.append(metric)
                metrics = filtered_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []
    
    @staticmethod
    async def aggregate_metrics(
        metric_type: str,
        aggregation: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """
        Aggregate metrics over time intervals.
        
        Args:
            metric_type: Metric type to aggregate
            aggregation: Aggregation function (avg, sum, min, max, count)
            interval: Time interval (1m, 5m, 1h, 1d)
            start_time: Start time
            end_time: End time
            tags: Tag filters
            db: Database session
            
        Returns:
            List[Dict[str, Any]]: Aggregated metrics
        """
        try:
            if db is None:
                db = await get_db_session_optional()
                if db is None:
                    return []
            
            # Get raw metrics
            metrics = await MetricsService.get_metrics(
                metric_type=metric_type,
                start_time=start_time,
                end_time=end_time,
                tags=tags,
                limit=10000,
                db=db
            )
            
            if not metrics:
                return []
            
            # Parse interval
            interval_seconds = MetricsService._parse_interval(interval)
            if interval_seconds is None:
                logger.error(f"Invalid interval: {interval}")
                return []
            
            # Group metrics by time intervals
            grouped_metrics = {}
            for metric in metrics:
                interval_start = MetricsService._get_interval_start(metric.timestamp, interval_seconds)
                if interval_start not in grouped_metrics:
                    grouped_metrics[interval_start] = []
                grouped_metrics[interval_start].append(metric.value)
            
            # Aggregate each group
            aggregated = []
            for interval_start, values in grouped_metrics.items():
                if aggregation == 'avg':
                    agg_value = sum(values) / len(values)
                elif aggregation == 'sum':
                    agg_value = sum(values)
                elif aggregation == 'min':
                    agg_value = min(values)
                elif aggregation == 'max':
                    agg_value = max(values)
                elif aggregation == 'count':
                    agg_value = len(values)
                else:
                    continue
                
                aggregated.append({
                    'timestamp': interval_start,
                    'value': round(agg_value, 4),
                    'count': len(values),
                    'aggregation': aggregation,
                    'interval': interval
                })
            
            # Sort by timestamp
            aggregated.sort(key=lambda x: x['timestamp'])
            return aggregated
            
        except Exception as e:
            logger.error(f"Error aggregating metrics: {e}")
            return []
    
    @staticmethod
    def _parse_interval(interval: str) -> Optional[int]:
        """
        Parse time interval string to seconds.
        
        Args:
            interval: Interval string (e.g., '1m', '5m', '1h', '1d')
            
        Returns:
            Optional[int]: Interval in seconds
        """
        try:
            if interval.endswith('m'):
                return int(interval[:-1]) * 60
            elif interval.endswith('h'):
                return int(interval[:-1]) * 3600
            elif interval.endswith('d'):
                return int(interval[:-1]) * 86400
            else:
                return int(interval)
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def _get_interval_start(timestamp: datetime, interval_seconds: int) -> datetime:
        """
        Get the start of the interval containing the timestamp.
        
        Args:
            timestamp: Timestamp
            interval_seconds: Interval in seconds
            
        Returns:
            datetime: Interval start timestamp
        """
        timestamp_seconds = int(timestamp.timestamp())
        interval_start_seconds = (timestamp_seconds // interval_seconds) * interval_seconds
        return datetime.fromtimestamp(interval_start_seconds)
    
    @staticmethod
    async def calculate_statistics(
        metric_type: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Calculate statistical summary for metrics.
        
        Args:
            metric_type: Metric type
            start_time: Start time
            end_time: End time
            tags: Tag filters
            db: Database session
            
        Returns:
            Dict[str, Any]: Statistical summary
        """
        try:
            metrics = await MetricsService.get_metrics(
                metric_type=metric_type,
                start_time=start_time,
                end_time=end_time,
                tags=tags,
                limit=10000,
                db=db
            )
            
            if not metrics:
                return {
                    'count': 0,
                    'min': None,
                    'max': None,
                    'mean': None,
                    'median': None,
                    'std': None,
                    'percentiles': {}
                }
            
            values = [metric.value for metric in metrics]
            
            # Calculate basic statistics
            count = len(values)
            min_val = min(values)
            max_val = max(values)
            mean_val = sum(values) / count
            
            # Calculate standard deviation
            variance = sum((x - mean_val) ** 2 for x in values) / count
            std_val = math.sqrt(variance)
            
            # Calculate median
            sorted_values = sorted(values)
            if count % 2 == 0:
                median_val = (sorted_values[count // 2 - 1] + sorted_values[count // 2]) / 2
            else:
                median_val = sorted_values[count // 2]
            
            # Calculate percentiles
            percentiles = {}
            for p in [10, 25, 50, 75, 90, 95, 99]:
                index = int((p / 100) * count)
                if index < count:
                    percentiles[f'p{p}'] = sorted_values[index]
            
            return {
                'count': count,
                'min': round(min_val, 4),
                'max': round(max_val, 4),
                'mean': round(mean_val, 4),
                'median': round(median_val, 4),
                'std': round(std_val, 4),
                'percentiles': {k: round(v, 4) for k, v in percentiles.items()}
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {'error': str(e)}
    
    @staticmethod
    async def detect_anomalies(
        metric_type: str,
        window_size: int = 100,
        threshold: float = 2.0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metrics using statistical methods.
        
        Args:
            metric_type: Metric type to analyze
            window_size: Size of sliding window for baseline calculation
            threshold: Number of standard deviations for anomaly detection
            start_time: Start time
            end_time: End time
            tags: Tag filters
            db: Database session
            
        Returns:
            List[Dict[str, Any]]: Detected anomalies
        """
        try:
            metrics = await MetricsService.get_metrics(
                metric_type=metric_type,
                start_time=start_time,
                end_time=end_time,
                tags=tags,
                limit=10000,
                db=db
            )
            
            if len(metrics) < window_size:
                return []
            
            # Sort metrics by timestamp
            metrics.sort(key=lambda x: x.timestamp)
            values = [metric.value for metric in metrics]
            
            anomalies = []
            
            # Use sliding window to detect anomalies
            for i in range(window_size, len(values)):
                window_values = values[i - window_size:i]
                current_value = values[i]
                current_metric = metrics[i]
                
                # Calculate baseline statistics
                window_mean = sum(window_values) / len(window_values)
                window_variance = sum((x - window_mean) ** 2 for x in window_values) / len(window_values)
                window_std = math.sqrt(window_variance)
                
                # Check if current value is anomalous
                if window_std > 0:
                    z_score = abs(current_value - window_mean) / window_std
                    if z_score > threshold:
                        anomalies.append({
                            'timestamp': current_metric.timestamp,
                            'value': current_value,
                            'baseline_mean': round(window_mean, 4),
                            'baseline_std': round(window_std, 4),
                            'z_score': round(z_score, 4),
                            'severity': 'high' if z_score > threshold * 1.5 else 'medium'
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    @staticmethod
    async def generate_performance_report(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            start_time: Start time for report
            end_time: End time for report
            db: Database session
            
        Returns:
            Dict[str, Any]: Performance report
        """
        try:
            if end_time is None:
                end_time = datetime.utcnow()
            if start_time is None:
                start_time = end_time - timedelta(hours=1)
            
            report = {
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'duration_hours': (end_time - start_time).total_seconds() / 3600
                },
                'summary': {},
                'metrics': {},
                'anomalies': {},
                'recommendations': []
            }
            
            # Collect statistics for key metrics
            key_metrics = [
                MetricType.CPU_PERCENT,
                MetricType.MEMORY_PERCENT,
                MetricType.DISK_PERCENT,
                MetricType.NETWORK_BYTES_SENT,
                MetricType.NETWORK_BYTES_RECV
            ]
            
            for metric_type in key_metrics:
                stats = await MetricsService.calculate_statistics(
                    metric_type=metric_type,
                    start_time=start_time,
                    end_time=end_time,
                    db=db
                )
                report['metrics'][metric_type] = stats
                
                # Check for performance issues
                if metric_type == MetricType.CPU_PERCENT and stats.get('mean', 0) > 80:
                    report['recommendations'].append('High CPU usage detected - consider optimizing processes')
                elif metric_type == MetricType.MEMORY_PERCENT and stats.get('mean', 0) > 85:
                    report['recommendations'].append('High memory usage detected - consider memory optimization')
                elif metric_type == MetricType.DISK_PERCENT and stats.get('mean', 0) > 90:
                    report['recommendations'].append('High disk usage detected - consider cleanup or expansion')
            
            # Detect anomalies
            for metric_type in key_metrics:
                anomalies = await MetricsService.detect_anomalies(
                    metric_type=metric_type,
                    start_time=start_time,
                    end_time=end_time,
                    db=db
                )
                report['anomalies'][metric_type] = anomalies
            
            # Generate summary
            total_anomalies = sum(len(anomalies) for anomalies in report['anomalies'].values())
            report['summary'] = {
                'total_metrics_analyzed': len(key_metrics),
                'total_anomalies_detected': total_anomalies,
                'overall_health': 'good' if total_anomalies < 5 else 'warning' if total_anomalies < 10 else 'critical'
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    @staticmethod
    async def start_metrics_collection(interval_seconds: int = 60):
        """
        Start continuous metrics collection.
        
        Args:
            interval_seconds: Collection interval in seconds
        """
        logger.info(f"Starting metrics collection with {interval_seconds}s interval")
        
        while True:
            try:
                db = await get_db_session_optional()
                if db is None:
                    logger.error("Could not get database session for metrics collection")
                    await asyncio.sleep(interval_seconds)
                    continue
                
                # Collect system metrics
                await MetricsService.collect_system_metrics(db)
                
                await db.close()
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
            
            await asyncio.sleep(interval_seconds)
