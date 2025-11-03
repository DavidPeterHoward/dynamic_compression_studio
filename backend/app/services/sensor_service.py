"""
Sensor service for the Dynamic Compression Algorithms backend.
"""

import logging
import asyncio
import psutil
import random
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from ..models.sensor import (
    Sensor, SensorReading, SensorFusion, SensorFusionResult, SystemHealth,
    SensorType, MetricType, SensorStatus
)
from ..database.connection import get_db_session_optional

logger = logging.getLogger(__name__)


class SensorService:
    """Service for managing sensors and sensor data."""
    
    @staticmethod
    async def create_sensor(sensor_data: Dict[str, Any], db: AsyncSession) -> Sensor:
        """
        Create a new sensor.
        
        Args:
            sensor_data: Sensor data
            db: Database session
            
        Returns:
            Sensor: Created sensor
        """
        try:
            sensor = Sensor(**sensor_data)
            db.add(sensor)
            await db.commit()
            await db.refresh(sensor)
            logger.info(f"Created sensor: {sensor.name}")
            return sensor
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating sensor: {e}")
            raise
    
    @staticmethod
    async def get_sensor(sensor_id: int, db: AsyncSession) -> Optional[Sensor]:
        """
        Get sensor by ID.
        
        Args:
            sensor_id: Sensor ID
            db: Database session
            
        Returns:
            Optional[Sensor]: Sensor or None
        """
        try:
            query = select(Sensor).where(Sensor.id == sensor_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting sensor {sensor_id}: {e}")
            return None
    
    @staticmethod
    async def get_active_sensors(db: AsyncSession) -> List[Sensor]:
        """
        Get all active sensors.
        
        Args:
            db: Database session
            
        Returns:
            List[Sensor]: List of active sensors
        """
        try:
            query = select(Sensor).where(Sensor.status == SensorStatus.ACTIVE)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting active sensors: {e}")
            return []
    
    @staticmethod
    async def update_sensor(sensor_id: int, update_data: Dict[str, Any], db: AsyncSession) -> Optional[Sensor]:
        """
        Update sensor.
        
        Args:
            sensor_id: Sensor ID
            update_data: Update data
            db: Database session
            
        Returns:
            Optional[Sensor]: Updated sensor or None
        """
        try:
            query = select(Sensor).where(Sensor.id == sensor_id)
            result = await db.execute(query)
            sensor = result.scalar_one_or_none()
            
            if not sensor:
                return None
            
            for key, value in update_data.items():
                if hasattr(sensor, key):
                    setattr(sensor, key, value)
            
            await db.commit()
            await db.refresh(sensor)
            logger.info(f"Updated sensor: {sensor.name}")
            return sensor
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating sensor {sensor_id}: {e}")
            return None
    
    @staticmethod
    async def delete_sensor(sensor_id: int, db: AsyncSession) -> bool:
        """
        Delete sensor.
        
        Args:
            sensor_id: Sensor ID
            db: Database session
            
        Returns:
            bool: True if deleted
        """
        try:
            query = select(Sensor).where(Sensor.id == sensor_id)
            result = await db.execute(query)
            sensor = result.scalar_one_or_none()
            
            if not sensor:
                return False
            
            await db.delete(sensor)
            await db.commit()
            logger.info(f"Deleted sensor: {sensor.name}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting sensor {sensor_id}: {e}")
            return False
    
    @staticmethod
    async def collect_sensor_reading(sensor: Sensor) -> Dict[str, Any]:
        """
        Collect reading from a sensor.
        
        Args:
            sensor: Sensor to read from
            
        Returns:
            Dict[str, Any]: Sensor reading data
        """
        try:
            reading_data = {
                'sensor_id': sensor.id,
                'timestamp': datetime.utcnow(),
                'value': 0.0,
                'unit': sensor.configuration.get('unit', 'unknown'),
                'quality': 'good',
                'metadata': {}
            }
            
            if sensor.type == SensorType.SYSTEM:
                reading_data.update(await SensorService._collect_system_reading(sensor))
            elif sensor.type == SensorType.COMPRESSION:
                reading_data.update(await SensorService._collect_compression_reading(sensor))
            elif sensor.type == SensorType.ENVIRONMENTAL:
                reading_data.update(await SensorService._collect_environmental_reading(sensor))
            elif sensor.type == SensorType.CUSTOM:
                reading_data.update(await SensorService._collect_custom_reading(sensor))
            else:
                # Default to simulated reading
                reading_data.update(await SensorService._collect_simulated_reading(sensor))
            
            return reading_data
            
        except Exception as e:
            logger.error(f"Error collecting reading from sensor {sensor.name}: {e}")
            return {
                'sensor_id': sensor.id,
                'timestamp': datetime.utcnow(),
                'value': 0.0,
                'unit': 'unknown',
                'quality': 'error',
                'metadata': {'error': str(e)}
            }
    
    @staticmethod
    async def _collect_system_reading(sensor: Sensor) -> Dict[str, Any]:
        """
        Collect system sensor reading.
        
        Args:
            sensor: System sensor
            
        Returns:
            Dict[str, Any]: System reading data
        """
        metric_type = sensor.configuration.get('metric_type', 'cpu_percent')
        
        if metric_type == 'cpu_percent':
            value = psutil.cpu_percent(interval=1)
            unit = 'percent'
        elif metric_type == 'memory_percent':
            memory = psutil.virtual_memory()
            value = memory.percent
            unit = 'percent'
        elif metric_type == 'memory_available':
            memory = psutil.virtual_memory()
            value = memory.available / (1024 * 1024 * 1024)  # GB
            unit = 'GB'
        elif metric_type == 'disk_usage':
            disk = psutil.disk_usage('/')
            value = disk.percent
            unit = 'percent'
        elif metric_type == 'network_io':
            net_io = psutil.net_io_counters()
            value = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            unit = 'MB'
        elif metric_type == 'load_average':
            load_avg = psutil.getloadavg()
            value = load_avg[0]  # 1-minute load average
            unit = 'load'
        else:
            value = random.uniform(0, 100)
            unit = 'unknown'
        
        return {
            'value': round(value, 2),
            'unit': unit,
            'quality': 'good',
            'metadata': {
                'metric_type': metric_type,
                'collection_method': 'system_monitoring'
            }
        }
    
    @staticmethod
    async def _collect_compression_reading(sensor: Sensor) -> Dict[str, Any]:
        """
        Collect compression sensor reading.
        
        Args:
            sensor: Compression sensor
            
        Returns:
            Dict[str, Any]: Compression reading data
        """
        metric_type = sensor.configuration.get('metric_type', 'compression_ratio')
        
        # Simulate compression metrics
        if metric_type == 'compression_ratio':
            value = random.uniform(0.1, 0.9)
            unit = 'ratio'
        elif metric_type == 'compression_speed':
            value = random.uniform(1, 1000)  # MB/s
            unit = 'MB/s'
        elif metric_type == 'decompression_speed':
            value = random.uniform(10, 5000)  # MB/s
            unit = 'MB/s'
        elif metric_type == 'memory_usage':
            value = random.uniform(10, 500)  # MB
            unit = 'MB'
        elif metric_type == 'error_rate':
            value = random.uniform(0, 0.01)  # 0-1%
            unit = 'percent'
        else:
            value = random.uniform(0, 100)
            unit = 'unknown'
        
        return {
            'value': round(value, 4),
            'unit': unit,
            'quality': 'good',
            'metadata': {
                'metric_type': metric_type,
                'collection_method': 'compression_monitoring'
            }
        }
    
    @staticmethod
    async def _collect_environmental_reading(sensor: Sensor) -> Dict[str, Any]:
        """
        Collect environmental sensor reading.
        
        Args:
            sensor: Environmental sensor
            
        Returns:
            Dict[str, Any]: Environmental reading data
        """
        metric_type = sensor.configuration.get('metric_type', 'temperature')
        
        # Simulate environmental metrics
        if metric_type == 'temperature':
            value = random.uniform(15, 35)  # Celsius
            unit = '°C'
        elif metric_type == 'humidity':
            value = random.uniform(30, 80)  # Percent
            unit = 'percent'
        elif metric_type == 'pressure':
            value = random.uniform(980, 1020)  # hPa
            unit = 'hPa'
        elif metric_type == 'noise_level':
            value = random.uniform(30, 80)  # dB
            unit = 'dB'
        else:
            value = random.uniform(0, 100)
            unit = 'unknown'
        
        return {
            'value': round(value, 2),
            'unit': unit,
            'quality': 'good',
            'metadata': {
                'metric_type': metric_type,
                'collection_method': 'environmental_monitoring'
            }
        }
    
    @staticmethod
    async def _collect_custom_reading(sensor: Sensor) -> Dict[str, Any]:
        """
        Collect custom sensor reading.
        
        Args:
            sensor: Custom sensor
            
        Returns:
            Dict[str, Any]: Custom reading data
        """
        # Use sensor configuration for custom readings
        config = sensor.configuration or {}
        min_value = config.get('min_value', 0)
        max_value = config.get('max_value', 100)
        unit = config.get('unit', 'unknown')
        metric_type = config.get('metric_type', 'custom')
        
        # Generate value based on configuration
        if config.get('random_walk', False):
            # Simulate random walk
            last_value = config.get('last_value', (min_value + max_value) / 2)
            step = random.uniform(-1, 1) * (max_value - min_value) * 0.1
            value = max(min_value, min(max_value, last_value + step))
            config['last_value'] = value
        else:
            value = random.uniform(min_value, max_value)
        
        return {
            'value': round(value, 4),
            'unit': unit,
            'quality': 'good',
            'metadata': {
                'metric_type': metric_type,
                'collection_method': 'custom_monitoring',
                'configuration': config
            }
        }
    
    @staticmethod
    async def _collect_simulated_reading(sensor: Sensor) -> Dict[str, Any]:
        """
        Collect simulated sensor reading.
        
        Args:
            sensor: Sensor to simulate
            
        Returns:
            Dict[str, Any]: Simulated reading data
        """
        # Generate realistic simulated data
        base_value = sensor.configuration.get('base_value', 50)
        variance = sensor.configuration.get('variance', 10)
        trend = sensor.configuration.get('trend', 0)  # -1 to 1
        
        # Add trend and noise
        time_factor = datetime.utcnow().timestamp() / 3600  # Hours since epoch
        trend_component = trend * time_factor * 0.1
        noise = random.uniform(-variance, variance)
        
        value = base_value + trend_component + noise
        
        return {
            'value': round(value, 2),
            'unit': sensor.configuration.get('unit', 'units'),
            'quality': 'good',
            'metadata': {
                'metric_type': 'simulated',
                'collection_method': 'simulation',
                'base_value': base_value,
                'variance': variance,
                'trend': trend
            }
        }
    
    @staticmethod
    async def save_sensor_reading(reading_data: Dict[str, Any], db: AsyncSession) -> Optional[SensorReading]:
        """
        Save sensor reading to database.
        
        Args:
            reading_data: Reading data
            db: Database session
            
        Returns:
            Optional[SensorReading]: Saved reading or None
        """
        try:
            reading = SensorReading(**reading_data)
            db.add(reading)
            await db.commit()
            await db.refresh(reading)
            return reading
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving sensor reading: {e}")
            return None
    
    @staticmethod
    async def get_sensor_readings(
        sensor_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
        db: AsyncSession = None
    ) -> List[SensorReading]:
        """
        Get sensor readings with filters.
        
        Args:
            sensor_id: Filter by sensor ID
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of readings
            db: Database session
            
        Returns:
            List[SensorReading]: List of sensor readings
        """
        try:
            if db is None:
                db = await get_db_session_optional()
                if db is None:
                    return []
            
            query = select(SensorReading).options(selectinload(SensorReading.sensor))
            
            conditions = []
            if sensor_id:
                conditions.append(SensorReading.sensor_id == sensor_id)
            if start_time:
                conditions.append(SensorReading.timestamp >= start_time)
            if end_time:
                conditions.append(SensorReading.timestamp <= end_time)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(SensorReading.timestamp.desc()).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting sensor readings: {e}")
            return []
    
    @staticmethod
    async def create_sensor_fusion(fusion_data: Dict[str, Any], db: AsyncSession) -> Optional[SensorFusion]:
        """
        Create sensor fusion configuration.
        
        Args:
            fusion_data: Fusion configuration data
            db: Database session
            
        Returns:
            Optional[SensorFusion]: Created fusion or None
        """
        try:
            fusion = SensorFusion(**fusion_data)
            db.add(fusion)
            await db.commit()
            await db.refresh(fusion)
            logger.info(f"Created sensor fusion: {fusion.name}")
            return fusion
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating sensor fusion: {e}")
            return None
    
    @staticmethod
    async def execute_sensor_fusion(fusion: SensorFusion, db: AsyncSession) -> Optional[SensorFusionResult]:
        """
        Execute sensor fusion algorithm.
        
        Args:
            fusion: Sensor fusion configuration
            db: Database session
            
        Returns:
            Optional[SensorFusionResult]: Fusion result or None
        """
        try:
            # Get recent readings from all sensors in the fusion
            sensor_ids = fusion.sensor_ids
            if not sensor_ids:
                logger.warning(f"No sensors configured for fusion {fusion.name}")
                return None
            
            # Get readings from the last hour
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            all_readings = []
            for sensor_id in sensor_ids:
                readings = await SensorService.get_sensor_readings(
                    sensor_id=sensor_id,
                    start_time=start_time,
                    end_time=end_time,
                    limit=100,
                    db=db
                )
                all_readings.extend(readings)
            
            if not all_readings:
                logger.warning(f"No readings available for fusion {fusion.name}")
                return None
            
            # Execute fusion algorithm
            fusion_result = await SensorService._execute_fusion_algorithm(fusion, all_readings)
            
            # Save result
            result_data = {
                'fusion_id': fusion.id,
                'timestamp': datetime.utcnow(),
                'result': fusion_result,
                'metadata': {
                    'sensor_count': len(sensor_ids),
                    'reading_count': len(all_readings),
                    'algorithm': fusion.algorithm,
                    'parameters': fusion.parameters
                }
            }
            
            result = SensorFusionResult(**result_data)
            db.add(result)
            await db.commit()
            await db.refresh(result)
            
            logger.info(f"Executed sensor fusion: {fusion.name}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error executing sensor fusion {fusion.name}: {e}")
            return None
    
    @staticmethod
    async def _execute_fusion_algorithm(fusion: SensorFusion, readings: List[SensorReading]) -> Dict[str, Any]:
        """
        Execute fusion algorithm on sensor readings.
        
        Args:
            fusion: Sensor fusion configuration
            readings: List of sensor readings
            
        Returns:
            Dict[str, Any]: Fusion result
        """
        algorithm = fusion.algorithm
        parameters = fusion.parameters or {}
        
        # Group readings by sensor
        readings_by_sensor = {}
        for reading in readings:
            sensor_id = reading.sensor_id
            if sensor_id not in readings_by_sensor:
                readings_by_sensor[sensor_id] = []
            readings_by_sensor[sensor_id].append(reading)
        
        if algorithm == 'weighted_average':
            return await SensorService._weighted_average_fusion(readings_by_sensor, parameters)
        elif algorithm == 'kalman_filter':
            return await SensorService._kalman_filter_fusion(readings_by_sensor, parameters)
        elif algorithm == 'bayesian_fusion':
            return await SensorService._bayesian_fusion(readings_by_sensor, parameters)
        elif algorithm == 'ensemble_method':
            return await SensorService._ensemble_fusion(readings_by_sensor, parameters)
        else:
            # Default to simple average
            return await SensorService._simple_average_fusion(readings_by_sensor, parameters)
    
    @staticmethod
    async def _simple_average_fusion(readings_by_sensor: Dict[int, List[SensorReading]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple average fusion algorithm.
        
        Args:
            readings_by_sensor: Readings grouped by sensor
            parameters: Fusion parameters
            
        Returns:
            Dict[str, Any]: Fusion result
        """
        all_values = []
        all_timestamps = []
        
        for sensor_readings in readings_by_sensor.values():
            for reading in sensor_readings:
                all_values.append(reading.value)
                all_timestamps.append(reading.timestamp)
        
        if not all_values:
            return {'value': 0.0, 'confidence': 0.0, 'method': 'simple_average'}
        
        avg_value = sum(all_values) / len(all_values)
        confidence = min(1.0, len(all_values) / 10.0)  # Higher confidence with more readings
        
        return {
            'value': round(avg_value, 4),
            'confidence': round(confidence, 3),
            'method': 'simple_average',
            'reading_count': len(all_values),
            'timestamp': max(all_timestamps) if all_timestamps else datetime.utcnow()
        }
    
    @staticmethod
    async def _weighted_average_fusion(readings_by_sensor: Dict[int, List[SensorReading]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Weighted average fusion algorithm.
        
        Args:
            readings_by_sensor: Readings grouped by sensor
            parameters: Fusion parameters
            
        Returns:
            Dict[str, Any]: Fusion result
        """
        weights = parameters.get('weights', {})
        default_weight = parameters.get('default_weight', 1.0)
        
        total_weighted_value = 0.0
        total_weight = 0.0
        all_timestamps = []
        
        for sensor_id, sensor_readings in readings_by_sensor.items():
            weight = weights.get(str(sensor_id), default_weight)
            
            for reading in sensor_readings:
                total_weighted_value += reading.value * weight
                total_weight += weight
                all_timestamps.append(reading.timestamp)
        
        if total_weight == 0:
            return {'value': 0.0, 'confidence': 0.0, 'method': 'weighted_average'}
        
        weighted_avg = total_weighted_value / total_weight
        confidence = min(1.0, len(all_timestamps) / 10.0)
        
        return {
            'value': round(weighted_avg, 4),
            'confidence': round(confidence, 3),
            'method': 'weighted_average',
            'reading_count': len(all_timestamps),
            'timestamp': max(all_timestamps) if all_timestamps else datetime.utcnow(),
            'weights_used': weights
        }
    
    @staticmethod
    async def _kalman_filter_fusion(readings_by_sensor: Dict[int, List[SensorReading]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kalman filter fusion algorithm.
        
        Args:
            readings_by_sensor: Readings grouped by sensor
            parameters: Fusion parameters
            
        Returns:
            Dict[str, Any]: Fusion result
        """
        # Simplified Kalman filter implementation
        process_noise = parameters.get('process_noise', 0.1)
        measurement_noise = parameters.get('measurement_noise', 1.0)
        
        # Initialize state
        state = 0.0
        covariance = 1.0
        
        all_timestamps = []
        
        for sensor_readings in readings_by_sensor.values():
            for reading in sensor_readings:
                # Prediction step
                predicted_state = state
                predicted_covariance = covariance + process_noise
                
                # Update step
                kalman_gain = predicted_covariance / (predicted_covariance + measurement_noise)
                state = predicted_state + kalman_gain * (reading.value - predicted_state)
                covariance = (1 - kalman_gain) * predicted_covariance
                
                all_timestamps.append(reading.timestamp)
        
        confidence = min(1.0, 1.0 / (1.0 + covariance))
        
        return {
            'value': round(state, 4),
            'confidence': round(confidence, 3),
            'method': 'kalman_filter',
            'reading_count': len(all_timestamps),
            'timestamp': max(all_timestamps) if all_timestamps else datetime.utcnow(),
            'final_covariance': round(covariance, 6)
        }
    
    @staticmethod
    async def _bayesian_fusion(readings_by_sensor: Dict[int, List[SensorReading]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bayesian fusion algorithm.
        
        Args:
            readings_by_sensor: Readings grouped by sensor
            parameters: Fusion parameters
            
        Returns:
            Dict[str, Any]: Fusion result
        """
        # Simplified Bayesian fusion
        prior_mean = parameters.get('prior_mean', 0.0)
        prior_variance = parameters.get('prior_variance', 1.0)
        measurement_variance = parameters.get('measurement_variance', 1.0)
        
        posterior_mean = prior_mean
        posterior_variance = prior_variance
        
        all_timestamps = []
        
        for sensor_readings in readings_by_sensor.values():
            for reading in sensor_readings:
                # Bayesian update
                measurement = reading.value
                
                # Update posterior
                kalman_gain = posterior_variance / (posterior_variance + measurement_variance)
                posterior_mean = posterior_mean + kalman_gain * (measurement - posterior_mean)
                posterior_variance = (1 - kalman_gain) * posterior_variance
                
                all_timestamps.append(reading.timestamp)
        
        confidence = min(1.0, 1.0 / (1.0 + posterior_variance))
        
        return {
            'value': round(posterior_mean, 4),
            'confidence': round(confidence, 3),
            'method': 'bayesian_fusion',
            'reading_count': len(all_timestamps),
            'timestamp': max(all_timestamps) if all_timestamps else datetime.utcnow(),
            'posterior_variance': round(posterior_variance, 6)
        }
    
    @staticmethod
    async def _ensemble_fusion(readings_by_sensor: Dict[int, List[SensorReading]], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensemble fusion algorithm.
        
        Args:
            readings_by_sensor: Readings grouped by sensor
            parameters: Fusion parameters
            
        Returns:
            Dict[str, Any]: Fusion result
        """
        # Apply multiple fusion methods and combine results
        methods = ['simple_average', 'weighted_average', 'kalman_filter']
        results = []
        
        for method in methods:
            if method == 'simple_average':
                result = await SensorService._simple_average_fusion(readings_by_sensor, {})
            elif method == 'weighted_average':
                result = await SensorService._weighted_average_fusion(readings_by_sensor, parameters)
            elif method == 'kalman_filter':
                result = await SensorService._kalman_filter_fusion(readings_by_sensor, parameters)
            
            results.append(result)
        
        # Combine results using weighted average based on confidence
        total_weighted_value = 0.0
        total_weight = 0.0
        all_timestamps = []
        
        for result in results:
            weight = result.get('confidence', 0.0)
            total_weighted_value += result['value'] * weight
            total_weight += weight
            all_timestamps.extend([result.get('timestamp', datetime.utcnow())])
        
        if total_weight == 0:
            return {'value': 0.0, 'confidence': 0.0, 'method': 'ensemble'}
        
        ensemble_value = total_weighted_value / total_weight
        ensemble_confidence = min(1.0, total_weight / len(methods))
        
        return {
            'value': round(ensemble_value, 4),
            'confidence': round(ensemble_confidence, 3),
            'method': 'ensemble',
            'reading_count': sum(r.get('reading_count', 0) for r in results),
            'timestamp': max(all_timestamps) if all_timestamps else datetime.utcnow(),
            'sub_methods': [r['method'] for r in results],
            'sub_results': results
        }
    
    @staticmethod
    async def monitor_system_health(db: AsyncSession) -> Optional[SystemHealth]:
        """
        Monitor overall system health.
        
        Args:
            db: Database session
            
        Returns:
            Optional[SystemHealth]: System health status
        """
        try:
            # Collect system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine health status
            health_score = 100.0
            
            # CPU health (penalty for high usage)
            if cpu_percent > 90:
                health_score -= 30
            elif cpu_percent > 80:
                health_score -= 20
            elif cpu_percent > 70:
                health_score -= 10
            
            # Memory health
            if memory.percent > 90:
                health_score -= 30
            elif memory.percent > 80:
                health_score -= 20
            elif memory.percent > 70:
                health_score -= 10
            
            # Disk health
            if disk.percent > 90:
                health_score -= 20
            elif disk.percent > 80:
                health_score -= 10
            
            health_score = max(0.0, health_score)
            
            # Determine status
            if health_score >= 80:
                status = 'healthy'
            elif health_score >= 60:
                status = 'warning'
            elif health_score >= 40:
                status = 'degraded'
            else:
                status = 'critical'
            
            health_data = {
                'timestamp': datetime.utcnow(),
                'status': status,
                'health_score': round(health_score, 2),
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3)
                },
                'alerts': []
            }
            
            # Add alerts for critical conditions
            if cpu_percent > 90:
                health_data['alerts'].append('High CPU usage')
            if memory.percent > 90:
                health_data['alerts'].append('High memory usage')
            if disk.percent > 90:
                health_data['alerts'].append('Low disk space')
            
            health = SystemHealth(**health_data)
            db.add(health)
            await db.commit()
            await db.refresh(health)
            
            logger.info(f"System health monitored: {status} (score: {health_score})")
            return health
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error monitoring system health: {e}")
            return None
    
    @staticmethod
    async def start_sensor_monitoring(interval_seconds: int = 60):
        """
        Start continuous sensor monitoring.
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        logger.info(f"Starting sensor monitoring with {interval_seconds}s interval")
        
        while True:
            try:
                db = await get_db_session_optional()
                if db is None:
                    logger.error("Could not get database session for monitoring")
                    await asyncio.sleep(interval_seconds)
                    continue
                
                # Get active sensors
                sensors = await SensorService.get_active_sensors(db)
                
                # Collect readings from all sensors
                for sensor in sensors:
                    try:
                        reading_data = await SensorService.collect_sensor_reading(sensor)
                        await SensorService.save_sensor_reading(reading_data, db)
                    except Exception as e:
                        logger.error(f"Error collecting reading from sensor {sensor.name}: {e}")
                
                # Monitor system health
                await SensorService.monitor_system_health(db)
                
                # Execute sensor fusions
                fusions_query = select(SensorFusion).where(SensorFusion.status == 'active')
                result = await db.execute(fusions_query)
                fusions = result.scalars().all()
                
                for fusion in fusions:
                    try:
                        await SensorService.execute_sensor_fusion(fusion, db)
                    except Exception as e:
                        logger.error(f"Error executing fusion {fusion.name}: {e}")
                
                await db.close()
                
            except Exception as e:
                logger.error(f"Error in sensor monitoring loop: {e}")
            
            await asyncio.sleep(interval_seconds)
