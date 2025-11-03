"""
Experiment API endpoints for the Dynamic Compression Algorithms backend.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
import logging
import json
from datetime import datetime

from ..database.connection import get_db_session
from ..models.experiment import (
    Experiment, ExperimentLog, ContentAnalysis, CompressionProgress, GenerativeContent,
    ExperimentCreate, ExperimentUpdate, ExperimentResponse,
    ExperimentLogCreate, ExperimentLogResponse,
    ContentAnalysisCreate, ContentAnalysisResponse,
    CompressionProgressCreate, CompressionProgressResponse,
    GenerativeContentCreate, GenerativeContentResponse,
    ExperimentStartRequest, ExperimentPauseRequest, ExperimentResumeRequest, ExperimentStopRequest,
    ExperimentListResponse,
    ExperimentType, ExperimentStatus, ExperimentPhase, GenerationType, ExperimentPriority
)
from ..services.experiment_service import ExperimentService
from ..services.content_analysis_service import ContentAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/", response_model=ExperimentListResponse)
async def list_experiments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    type: Optional[ExperimentType] = Query(None, description="Filter by experiment type"),
    status: Optional[ExperimentStatus] = Query(None, description="Filter by experiment status"),
    priority: Optional[ExperimentPriority] = Query(None, description="Filter by experiment priority"),
    algorithm_id: Optional[int] = Query(None, description="Filter by algorithm ID"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all experiments with optional filtering and search.
    """
    try:
        # Build query
        query = select(Experiment).options(
            selectinload(Experiment.content_analysis),
            selectinload(Experiment.compression_progress),
            selectinload(Experiment.generative_content),
            selectinload(Experiment.logs)
        )
        
        # Apply filters
        filters = []
        if type:
            filters.append(Experiment.type == type)
        if status:
            filters.append(Experiment.status == status)
        if priority:
            filters.append(Experiment.priority == priority)
        if algorithm_id:
            filters.append(Experiment.algorithm_id == algorithm_id)
        if search:
            search_filter = or_(
                Experiment.name.ilike(f"%{search}%"),
                Experiment.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by creation date (newest first)
        query = query.order_by(desc(Experiment.created_at))
        
        # Get total count
        count_query = select(Experiment)
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        experiments = result.scalars().unique().all()
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return ExperimentListResponse(
            experiments=experiments,
            total=total,
            page=page,
            size=limit,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get experiment by ID with full details.
    """
    try:
        query = select(Experiment).options(
            selectinload(Experiment.content_analysis),
            selectinload(Experiment.compression_progress),
            selectinload(Experiment.generative_content),
            selectinload(Experiment.logs),
            selectinload(Experiment.algorithm)
        ).where(Experiment.id == experiment_id)
        
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    experiment_data: ExperimentCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new experiment.
    """
    try:
        # Create experiment
        experiment = Experiment(**experiment_data.dict())
        db.add(experiment)
        await db.commit()
        await db.refresh(experiment)
        
        # Create initial log entry
        log = ExperimentLog(
            experiment_id=experiment.id,
            level="info",
            message="Experiment created",
            phase="initialization"
        )
        db.add(log)
        await db.commit()
        
        return experiment
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating experiment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_data: ExperimentUpdate,
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update an existing experiment.
    """
    try:
        # Get existing experiment
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        # Update fields
        update_data = experiment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(experiment, field, value)
        
        await db.commit()
        await db.refresh(experiment)
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete an experiment.
    """
    try:
        # Get existing experiment
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        # Check if experiment is running
        if experiment.status == ExperimentStatus.RUNNING:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete running experiment. Stop it first."
            )
        
        await db.delete(experiment)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{experiment_id}/start", response_model=ExperimentResponse)
async def start_experiment(
    start_request: ExperimentStartRequest,
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Start an experiment.
    """
    try:
        # Get experiment
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        if experiment.status == ExperimentStatus.RUNNING:
            raise HTTPException(status_code=400, detail="Experiment is already running")
        
        # Start experiment in background
        background_tasks.add_task(
            ExperimentService.run_experiment,
            experiment_id,
            start_request.dict()
        )
        
        # Update experiment status
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.utcnow()
        experiment.current_phase = ExperimentPhase.ANALYSIS
        
        # Add log entry
        log = ExperimentLog(
            experiment_id=experiment.id,
            level="info",
            message="Experiment started",
            phase=experiment.current_phase
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(experiment)
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error starting experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{experiment_id}/pause", response_model=ExperimentResponse)
async def pause_experiment(
    pause_request: ExperimentPauseRequest,
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Pause an experiment.
    """
    try:
        # Get experiment
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        if experiment.status != ExperimentStatus.RUNNING:
            raise HTTPException(status_code=400, detail="Experiment is not running")
        
        # Pause experiment
        experiment.status = ExperimentStatus.PAUSED
        
        # Add log entry
        log = ExperimentLog(
            experiment_id=experiment.id,
            level="info",
            message=f"Experiment paused: {pause_request.reason or 'User request'}",
            phase=experiment.current_phase
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(experiment)
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error pausing experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{experiment_id}/resume", response_model=ExperimentResponse)
async def resume_experiment(
    resume_request: ExperimentResumeRequest,
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Resume a paused experiment.
    """
    try:
        # Get experiment
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        if experiment.status != ExperimentStatus.PAUSED:
            raise HTTPException(status_code=400, detail="Experiment is not paused")
        
        # Resume experiment in background
        background_tasks.add_task(
            ExperimentService.resume_experiment,
            experiment_id,
            resume_request.dict()
        )
        
        # Update experiment status
        experiment.status = ExperimentStatus.RUNNING
        
        # Add log entry
        log = ExperimentLog(
            experiment_id=experiment.id,
            level="info",
            message="Experiment resumed",
            phase=experiment.current_phase
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(experiment)
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error resuming experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{experiment_id}/stop", response_model=ExperimentResponse)
async def stop_experiment(
    stop_request: ExperimentStopRequest,
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Stop an experiment.
    """
    try:
        # Get experiment
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        if experiment.status not in [ExperimentStatus.RUNNING, ExperimentStatus.PAUSED]:
            raise HTTPException(status_code=400, detail="Experiment is not running or paused")
        
        # Stop experiment
        experiment.status = ExperimentStatus.CANCELLED
        experiment.completed_at = datetime.utcnow()
        
        # Add log entry
        log = ExperimentLog(
            experiment_id=experiment.id,
            level="info",
            message=f"Experiment stopped: {stop_request.reason or 'User request'}",
            phase=experiment.current_phase
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(experiment)
        
        return experiment
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error stopping experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{experiment_id}/logs", response_model=List[ExperimentLogResponse])
async def get_experiment_logs(
    experiment_id: int = Path(..., description="Experiment ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get logs for an experiment.
    """
    try:
        # Verify experiment exists
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        # Build log query
        log_query = select(ExperimentLog).where(ExperimentLog.experiment_id == experiment_id)
        
        if level:
            log_query = log_query.where(ExperimentLog.level == level)
        
        # Order by timestamp (newest first)
        log_query = log_query.order_by(desc(ExperimentLog.created_at))
        
        # Apply pagination
        log_query = log_query.offset(skip).limit(limit)
        
        result = await db.execute(log_query)
        logs = result.scalars().all()
        
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting logs for experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{experiment_id}/logs", response_model=ExperimentLogResponse)
async def add_experiment_log(
    log_data: ExperimentLogCreate,
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Add a log entry to an experiment.
    """
    try:
        # Verify experiment exists
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        # Create log entry
        log = ExperimentLog(
            experiment_id=experiment_id,
            **log_data.dict()
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        return log
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding log to experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{experiment_id}/content-analysis", response_model=ContentAnalysisResponse)
async def get_experiment_content_analysis(
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get content analysis for an experiment.
    """
    try:
        # Get content analysis
        query = select(ContentAnalysis).where(ContentAnalysis.experiment_id == experiment_id)
        result = await db.execute(query)
        content_analysis = result.scalar_one_or_none()
        
        if not content_analysis:
            raise HTTPException(status_code=404, detail="Content analysis not found")
        
        return content_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content analysis for experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{experiment_id}/content-analysis", response_model=ContentAnalysisResponse)
async def create_experiment_content_analysis(
    content_analysis_data: ContentAnalysisCreate,
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create content analysis for an experiment.
    """
    try:
        # Verify experiment exists
        query = select(Experiment).where(Experiment.id == experiment_id)
        result = await db.execute(query)
        experiment = result.scalar_one_or_none()
        
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        # Create content analysis
        content_analysis = ContentAnalysis(
            experiment_id=experiment_id,
            **content_analysis_data.dict()
        )
        db.add(content_analysis)
        await db.commit()
        await db.refresh(content_analysis)
        
        return content_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating content analysis for experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{experiment_id}/compression-progress", response_model=CompressionProgressResponse)
async def get_experiment_compression_progress(
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get compression progress for an experiment.
    """
    try:
        # Get compression progress
        query = select(CompressionProgress).where(CompressionProgress.experiment_id == experiment_id)
        result = await db.execute(query)
        compression_progress = result.scalar_one_or_none()
        
        if not compression_progress:
            raise HTTPException(status_code=404, detail="Compression progress not found")
        
        return compression_progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compression progress for experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{experiment_id}/generative-content", response_model=GenerativeContentResponse)
async def get_experiment_generative_content(
    experiment_id: int = Path(..., description="Experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get generative content for an experiment.
    """
    try:
        # Get generative content
        query = select(GenerativeContent).where(GenerativeContent.experiment_id == experiment_id)
        result = await db.execute(query)
        generative_content = result.scalar_one_or_none()
        
        if not generative_content:
            raise HTTPException(status_code=404, detail="Generative content not found")
        
        return generative_content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generative content for experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types", response_model=List[str])
async def get_experiment_types():
    """
    Get all available experiment types.
    """
    return [t.value for t in ExperimentType]


@router.get("/statuses", response_model=List[str])
async def get_experiment_statuses():
    """
    Get all available experiment statuses.
    """
    return [s.value for s in ExperimentStatus]


@router.get("/phases", response_model=List[str])
async def get_experiment_phases():
    """
    Get all available experiment phases.
    """
    return [p.value for p in ExperimentPhase]


@router.get("/priorities", response_model=List[str])
async def get_experiment_priorities():
    """
    Get all available experiment priorities.
    """
    return [p.value for p in ExperimentPriority]


@router.get("/stats/summary")
async def get_experiment_stats(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get experiment statistics summary.
    """
    try:
        # Get counts by status
        status_counts = {}
        for status in ExperimentStatus:
            query = select(Experiment).where(Experiment.status == status)
            result = await db.execute(query)
            status_counts[status.value] = len(result.scalars().all())
        
        # Get counts by type
        type_counts = {}
        for exp_type in ExperimentType:
            query = select(Experiment).where(Experiment.type == exp_type)
            result = await db.execute(query)
            type_counts[exp_type.value] = len(result.scalars().all())
        
        # Get counts by priority
        priority_counts = {}
        for priority in ExperimentPriority:
            query = select(Experiment).where(Experiment.priority == priority)
            result = await db.execute(query)
            priority_counts[priority.value] = len(result.scalars().all())
        
        # Get total logs
        log_query = select(ExperimentLog)
        result = await db.execute(log_query)
        total_logs = len(result.scalars().all())
        
        return {
            "total_experiments": sum(status_counts.values()),
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "priority_distribution": priority_counts,
            "total_logs": total_logs
        }
        
    except Exception as e:
        logger.error(f"Error getting experiment stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# WebSocket endpoint for real-time experiment updates
@router.websocket("/{experiment_id}/ws")
async def experiment_websocket(
    websocket: WebSocket,
    experiment_id: int = Path(..., description="Experiment ID")
):
    """
    WebSocket endpoint for real-time experiment updates.
    """
    await websocket.accept()
    
    try:
        # Get experiment
        async with AsyncSessionLocal() as db:
            query = select(Experiment).where(Experiment.id == experiment_id)
            result = await db.execute(query)
            experiment = result.scalar_one_or_none()
            
            if not experiment:
                await websocket.send_text(json.dumps({
                    "error": "Experiment not found"
                }))
                return
        
        # Send initial state
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "experiment": {
                "id": experiment.id,
                "name": experiment.name,
                "status": experiment.status,
                "current_phase": experiment.current_phase,
                "progress": experiment.overall_progress
            }
        }))
        
        # Keep connection alive and send updates
        while True:
            try:
                # Wait for client message (ping/pong)
                data = await websocket.receive_text()
                
                # Send current experiment state
                async with AsyncSessionLocal() as db:
                    query = select(Experiment).where(Experiment.id == experiment_id)
                    result = await db.execute(query)
                    experiment = result.scalar_one_or_none()
                    
                    if experiment:
                        await websocket.send_text(json.dumps({
                            "type": "update",
                            "experiment": {
                                "id": experiment.id,
                                "status": experiment.status,
                                "current_phase": experiment.current_phase,
                                "progress": experiment.overall_progress,
                                "processed_bytes": experiment.processed_bytes,
                                "total_bytes": experiment.total_bytes
                            }
                        }))
                
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for experiment {experiment_id}: {e}")
        try:
            await websocket.send_text(json.dumps({
                "error": "Internal server error"
            }))
        except:
            pass
