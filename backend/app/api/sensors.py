"""
Sensor fusion and system metrics API endpoints for the Dynamic Compression Algorithms backend.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime, timedelta

from ..database.connection import get_db_session
from ..models.sensor import (
    SystemMetric, Sensor, SensorReading, SensorFusion, SensorFusionResult, SystemHealth,
    SystemMetricCreate, SystemMetricResponse,
    SensorCreate, SensorResponse, SensorReadingCreate, SensorReadingResponse,
    SensorFusionCreate, SensorFusionResponse,
    SensorFusionResultCreate, SensorFusionResultResponse,
    SystemHealthCreate, SystemHealthResponse,
    MetricsQueryRequest, MetricsQueryResponse,
    SensorType, MetricType, SensorStatus
)
from ..services.sensor_service import SensorService
from ..services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sensors", tags=["sensors"])


# System Metrics Endpoints
@router.get("/metrics", response_model=List[SystemMetricResponse])
async def list_system_metrics(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    name: Optional[str] = Query(None, description="Filter by metric name"),
    type: Optional[MetricType] = Query(None, description="Filter by metric type"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List system metrics with optional filtering.
    """
    try:
        # Build query
        query = select(SystemMetric)
        
        # Apply filters
        filters = []
        if name:
            filters.append(SystemMetric.name == name)
        if type:
            filters.append(SystemMetric.type == type)
        if start_time:
            filters.append(SystemMetric.timestamp >= start_time)
        if end_time:
            filters.append(SystemMetric.timestamp <= end_time)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(SystemMetric.timestamp))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error listing system metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/metrics", response_model=SystemMetricResponse)
async def create_system_metric(
    metric_data: SystemMetricCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new system metric.
    """
    try:
        metric = SystemMetric(**metric_data.dict())
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        
        return metric
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating system metric: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics/{metric_id}", response_model=SystemMetricResponse)
async def get_system_metric(
    metric_id: int = Path(..., description="Metric ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get system metric by ID.
    """
    try:
        query = select(SystemMetric).where(SystemMetric.id == metric_id)
        result = await db.execute(query)
        metric = result.scalar_one_or_none()
        
        if not metric:
            raise HTTPException(status_code=404, detail="System metric not found")
        
        return metric
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system metric {metric_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics/names/{metric_name}/history", response_model=List[SystemMetricResponse])
async def get_metric_history(
    metric_name: str = Path(..., description="Metric name"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get historical data for a specific metric.
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        query = select(SystemMetric).where(
            and_(
                SystemMetric.name == metric_name,
                SystemMetric.timestamp >= start_time,
                SystemMetric.timestamp <= end_time
            )
        ).order_by(SystemMetric.timestamp)
        
        result = await db.execute(query)
        metrics = result.scalars().all()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metric history for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Sensor Endpoints
@router.get("/sensors", response_model=List[SensorResponse])
async def list_sensors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    type: Optional[SensorType] = Query(None, description="Filter by sensor type"),
    status: Optional[SensorStatus] = Query(None, description="Filter by sensor status"),
    group: Optional[str] = Query(None, description="Filter by sensor group"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all sensors with optional filtering.
    """
    try:
        # Build query
        query = select(Sensor)
        
        # Apply filters
        filters = []
        if type:
            filters.append(Sensor.type == type)
        if status:
            filters.append(Sensor.status == status)
        if group:
            filters.append(Sensor.group == group)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        sensors = result.scalars().all()
        
        # Add readings count
        for sensor in sensors:
            count_query = select(func.count(SensorReading.id)).where(SensorReading.sensor_id == sensor.id)
            count_result = await db.execute(count_query)
            sensor.readings_count = count_result.scalar()
        
        return sensors
        
    except Exception as e:
        logger.error(f"Error listing sensors: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sensors", response_model=SensorResponse)
async def create_sensor(
    sensor_data: SensorCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new sensor.
    """
    try:
        # Check if sensor with same name already exists
        existing_query = select(Sensor).where(Sensor.name == sensor_data.name)
        result = await db.execute(existing_query)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Sensor with this name already exists")
        
        sensor = Sensor(**sensor_data.dict())
        db.add(sensor)
        await db.commit()
        await db.refresh(sensor)
        
        return sensor
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating sensor: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sensors/{sensor_id}", response_model=SensorResponse)
async def get_sensor(
    sensor_id: int = Path(..., description="Sensor ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get sensor by ID.
    """
    try:
        query = select(Sensor).where(Sensor.id == sensor_id)
        result = await db.execute(query)
        sensor = result.scalar_one_or_none()
        
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Add readings count
        count_query = select(func.count(SensorReading.id)).where(SensorReading.sensor_id == sensor.id)
        count_result = await db.execute(count_query)
        sensor.readings_count = count_result.scalar()
        
        return sensor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/sensors/{sensor_id}", response_model=SensorResponse)
async def update_sensor(
    sensor_data: SensorCreate,
    sensor_id: int = Path(..., description="Sensor ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update an existing sensor.
    """
    try:
        # Get existing sensor
        query = select(Sensor).where(Sensor.id == sensor_id)
        result = await db.execute(query)
        sensor = result.scalar_one_or_none()
        
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Update fields
        update_data = sensor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sensor, field, value)
        
        await db.commit()
        await db.refresh(sensor)
        
        return sensor
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/sensors/{sensor_id}", status_code=204)
async def delete_sensor(
    sensor_id: int = Path(..., description="Sensor ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a sensor.
    """
    try:
        # Get existing sensor
        query = select(Sensor).where(Sensor.id == sensor_id)
        result = await db.execute(query)
        sensor = result.scalar_one_or_none()
        
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        await db.delete(sensor)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Sensor Readings Endpoints
@router.get("/sensors/{sensor_id}/readings", response_model=List[SensorReadingResponse])
async def list_sensor_readings(
    sensor_id: int = Path(..., description="Sensor ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List readings for a specific sensor.
    """
    try:
        # Verify sensor exists
        sensor_query = select(Sensor).where(Sensor.id == sensor_id)
        sensor_result = await db.execute(sensor_query)
        if not sensor_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Build readings query
        query = select(SensorReading).where(SensorReading.sensor_id == sensor_id)
        
        # Apply time filters
        filters = []
        if start_time:
            filters.append(SensorReading.timestamp >= start_time)
        if end_time:
            filters.append(SensorReading.timestamp <= end_time)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(SensorReading.timestamp))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        readings = result.scalars().all()
        
        return readings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing readings for sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sensors/{sensor_id}/readings", response_model=SensorReadingResponse)
async def create_sensor_reading(
    reading_data: SensorReadingCreate,
    sensor_id: int = Path(..., description="Sensor ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new sensor reading.
    """
    try:
        # Verify sensor exists
        sensor_query = select(Sensor).where(Sensor.id == sensor_id)
        sensor_result = await db.execute(sensor_query)
        if not sensor_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        reading = SensorReading(sensor_id=sensor_id, **reading_data.dict())
        db.add(reading)
        await db.commit()
        await db.refresh(reading)
        
        return reading
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating sensor reading: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Sensor Fusion Endpoints
@router.get("/fusion", response_model=List[SensorFusionResponse])
async def list_sensor_fusion(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[SensorStatus] = Query(None, description="Filter by fusion status"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all sensor fusion configurations.
    """
    try:
        # Build query
        query = select(SensorFusion)
        
        # Apply filters
        if status:
            query = query.where(SensorFusion.status == status)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        fusions = result.scalars().all()
        
        return fusions
        
    except Exception as e:
        logger.error(f"Error listing sensor fusion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/fusion", response_model=SensorFusionResponse)
async def create_sensor_fusion(
    fusion_data: SensorFusionCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new sensor fusion configuration.
    """
    try:
        fusion = SensorFusion(**fusion_data.dict())
        db.add(fusion)
        await db.commit()
        await db.refresh(fusion)
        
        return fusion
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating sensor fusion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/fusion/{fusion_id}", response_model=SensorFusionResponse)
async def get_sensor_fusion(
    fusion_id: int = Path(..., description="Fusion ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get sensor fusion by ID.
    """
    try:
        query = select(SensorFusion).where(SensorFusion.id == fusion_id)
        result = await db.execute(query)
        fusion = result.scalar_one_or_none()
        
        if not fusion:
            raise HTTPException(status_code=404, detail="Sensor fusion not found")
        
        return fusion
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sensor fusion {fusion_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/fusion/{fusion_id}/execute", response_model=SensorFusionResultResponse)
async def execute_sensor_fusion(
    fusion_id: int = Path(..., description="Fusion ID"),
    db: AsyncSession = Depends(get_db_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Execute a sensor fusion algorithm.
    """
    try:
        # Verify fusion exists
        query = select(SensorFusion).where(SensorFusion.id == fusion_id)
        result = await db.execute(query)
        fusion = result.scalar_one_or_none()
        
        if not fusion:
            raise HTTPException(status_code=404, detail="Sensor fusion not found")
        
        # Execute fusion in background
        background_tasks.add_task(
            SensorService.execute_fusion,
            fusion_id
        )
        
        # Create initial result record
        result_data = {
            "fusion_id": fusion_id,
            "output_data": {},
            "processing_time": 0.0,
            "input_count": 0,
            "output_count": 0,
            "confidence": 0.0
        }
        
        fusion_result = SensorFusionResult(**result_data)
        db.add(fusion_result)
        await db.commit()
        await db.refresh(fusion_result)
        
        return fusion_result
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error executing sensor fusion {fusion_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/fusion/{fusion_id}/results", response_model=List[SensorFusionResultResponse])
async def list_fusion_results(
    fusion_id: int = Path(..., description="Fusion ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List results for a specific sensor fusion.
    """
    try:
        # Verify fusion exists
        fusion_query = select(SensorFusion).where(SensorFusion.id == fusion_id)
        fusion_result = await db.execute(fusion_query)
        if not fusion_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Sensor fusion not found")
        
        # Get results
        query = select(SensorFusionResult).where(
            SensorFusionResult.fusion_id == fusion_id
        ).order_by(desc(SensorFusionResult.timestamp)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        results = result.scalars().all()
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing fusion results for fusion {fusion_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# System Health Endpoints
@router.get("/health", response_model=List[SystemHealthResponse])
async def list_system_health(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by health status"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List system health records.
    """
    try:
        # Build query
        query = select(SystemHealth)
        
        # Apply filters
        filters = []
        if status:
            filters.append(SystemHealth.status == status)
        if start_time:
            filters.append(SystemHealth.timestamp >= start_time)
        if end_time:
            filters.append(SystemHealth.timestamp <= end_time)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(SystemHealth.timestamp))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        health_records = result.scalars().all()
        
        return health_records
        
    except Exception as e:
        logger.error(f"Error listing system health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/health", response_model=SystemHealthResponse)
async def create_system_health(
    health_data: SystemHealthCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new system health record.
    """
    try:
        health = SystemHealth(**health_data.dict())
        db.add(health)
        await db.commit()
        await db.refresh(health)
        
        return health
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating system health record: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health/current", response_model=SystemHealthResponse)
async def get_current_system_health(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get the most recent system health record.
    """
    try:
        query = select(SystemHealth).order_by(desc(SystemHealth.timestamp)).limit(1)
        result = await db.execute(query)
        health = result.scalar_one_or_none()
        
        if not health:
            raise HTTPException(status_code=404, detail="No system health records found")
        
        return health
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current system health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Query Endpoints
@router.post("/query", response_model=MetricsQueryResponse)
async def query_metrics(
    query_request: MetricsQueryRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Query metrics with advanced filtering and aggregation.
    """
    try:
        start_time = datetime.utcnow()
        
        # Build queries based on request
        metrics = []
        sensor_readings = []
        fusion_results = []
        system_health = []
        
        # Query system metrics
        if query_request.metric_names:
            metric_query = select(SystemMetric).where(
                SystemMetric.name.in_(query_request.metric_names)
            )
            
            if query_request.start_time:
                metric_query = metric_query.where(SystemMetric.timestamp >= query_request.start_time)
            if query_request.end_time:
                metric_query = metric_query.where(SystemMetric.timestamp <= query_request.end_time)
            
            metric_result = await db.execute(metric_query)
            metrics = metric_result.scalars().all()
        
        # Query sensor readings
        if query_request.sensor_ids:
            reading_query = select(SensorReading).where(
                SensorReading.sensor_id.in_(query_request.sensor_ids)
            )
            
            if query_request.start_time:
                reading_query = reading_query.where(SensorReading.timestamp >= query_request.start_time)
            if query_request.end_time:
                reading_query = reading_query.where(SensorReading.timestamp <= query_request.end_time)
            
            reading_result = await db.execute(reading_query)
            sensor_readings = reading_result.scalars().all()
        
        # Query fusion results (all if no specific filters)
        fusion_query = select(SensorFusionResult)
        if query_request.start_time:
            fusion_query = fusion_query.where(SensorFusionResult.timestamp >= query_request.start_time)
        if query_request.end_time:
            fusion_query = fusion_query.where(SensorFusionResult.timestamp <= query_request.end_time)
        
        fusion_result = await db.execute(fusion_query)
        fusion_results = fusion_result.scalars().all()
        
        # Query system health
        health_query = select(SystemHealth)
        if query_request.start_time:
            health_query = health_query.where(SystemHealth.timestamp >= query_request.start_time)
        if query_request.end_time:
            health_query = health_query.where(SystemHealth.timestamp <= query_request.end_time)
        
        health_result = await db.execute(health_query)
        system_health = health_result.scalars().all()
        
        # Calculate total count
        total_count = len(metrics) + len(sensor_readings) + len(fusion_results) + len(system_health)
        
        # Calculate query time
        query_time = (datetime.utcnow() - start_time).total_seconds()
        
        return MetricsQueryResponse(
            metrics=metrics,
            sensor_readings=sensor_readings,
            fusion_results=fusion_results,
            system_health=system_health,
            total_count=total_count,
            query_time=query_time,
            metadata={
                "aggregation": query_request.aggregation,
                "interval": query_request.interval,
                "tags": query_request.tags
            }
        )
        
    except Exception as e:
        logger.error(f"Error querying metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Statistics Endpoints
@router.get("/stats/summary")
async def get_sensor_stats(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get sensor and metrics statistics summary.
    """
    try:
        # Get counts by sensor type
        type_counts = {}
        for sensor_type in SensorType:
            query = select(Sensor).where(Sensor.type == sensor_type)
            result = await db.execute(query)
            type_counts[sensor_type.value] = len(result.scalars().all())
        
        # Get counts by sensor status
        status_counts = {}
        for status in SensorStatus:
            query = select(Sensor).where(Sensor.status == status)
            result = await db.execute(query)
            status_counts[status.value] = len(result.scalars().all())
        
        # Get total readings
        reading_query = select(func.count(SensorReading.id))
        reading_result = await db.execute(reading_query)
        total_readings = reading_result.scalar()
        
        # Get total fusion results
        fusion_query = select(func.count(SensorFusionResult.id))
        fusion_result = await db.execute(fusion_query)
        total_fusion_results = fusion_result.scalar()
        
        # Get latest system health
        health_query = select(SystemHealth).order_by(desc(SystemHealth.timestamp)).limit(1)
        health_result = await db.execute(health_query)
        latest_health = health_result.scalar_one_or_none()
        
        return {
            "total_sensors": sum(type_counts.values()),
            "type_distribution": type_counts,
            "status_distribution": status_counts,
            "total_readings": total_readings,
            "total_fusion_results": total_fusion_results,
            "latest_health": latest_health.status if latest_health else None
        }
        
    except Exception as e:
        logger.error(f"Error getting sensor stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Utility Endpoints
@router.get("/types", response_model=List[str])
async def get_sensor_types():
    """
    Get all available sensor types.
    """
    return [t.value for t in SensorType]


@router.get("/statuses", response_model=List[str])
async def get_sensor_statuses():
    """
    Get all available sensor statuses.
    """
    return [s.value for s in SensorStatus]


@router.get("/metric-types", response_model=List[str])
async def get_metric_types():
    """
    Get all available metric types.
    """
    return [t.value for t in MetricType]
