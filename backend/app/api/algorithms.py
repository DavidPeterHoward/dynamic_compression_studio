"""
Algorithm API endpoints for the Dynamic Compression Algorithms backend.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime

from ..database.connection import get_db_session
from ..models.algorithm import (
    Algorithm, AlgorithmParameterMetadata, AlgorithmBenchmark,
    AlgorithmCreate, AlgorithmUpdate, AlgorithmResponse,
    AlgorithmParameterMetadataCreate, AlgorithmParameterMetadataResponse,
    AlgorithmBenchmarkCreate, AlgorithmBenchmarkResponse,
    AlgorithmComparisonRequest, AlgorithmComparisonResponse,
    AlgorithmType, AlgorithmCategory, AlgorithmStatus
)
from ..services.algorithm_service import AlgorithmService
from ..services.benchmark_service import BenchmarkService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/algorithms", tags=["algorithms"])


@router.get("/", response_model=List[AlgorithmResponse])
async def list_algorithms(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    type: Optional[AlgorithmType] = Query(None, description="Filter by algorithm type"),
    category: Optional[AlgorithmCategory] = Query(None, description="Filter by algorithm category"),
    status: Optional[AlgorithmStatus] = Query(None, description="Filter by algorithm status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all algorithms with optional filtering and search.
    """
    try:
        # Build query
        query = select(Algorithm).options(
            selectinload(Algorithm.parameters)
        )
        
        # Apply filters
        filters = []
        if type:
            filters.append(Algorithm.type == type)
        if category:
            filters.append(Algorithm.category == category)
        if status:
            filters.append(Algorithm.status == status)
        if search:
            search_filter = or_(
                Algorithm.name.ilike(f"%{search}%"),
                Algorithm.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        algorithms = result.scalars().unique().all()
        
        return algorithms
        
    except Exception as e:
        logger.error(f"Error listing algorithms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{algorithm_id}", response_model=AlgorithmResponse)
async def get_algorithm(
    algorithm_id: int = Path(..., description="Algorithm ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get algorithm by ID with full details.
    """
    try:
        query = select(Algorithm).options(
            selectinload(Algorithm.parameters),
            selectinload(Algorithm.benchmarks)
        ).where(Algorithm.id == algorithm_id)
        
        result = await db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        return algorithm
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting algorithm {algorithm_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=AlgorithmResponse, status_code=201)
async def create_algorithm(
    algorithm_data: AlgorithmCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new algorithm.
    """
    try:
        # Check if algorithm with same name already exists
        existing_query = select(Algorithm).where(Algorithm.name == algorithm_data.name)
        result = await db.execute(existing_query)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Algorithm with this name already exists")
        
        # Create algorithm
        algorithm = Algorithm(**algorithm_data.dict(exclude={'parameter_metadata'}))
        db.add(algorithm)
        await db.flush()  # Get the ID
        
        # Create parameter metadata if provided
        if algorithm_data.parameter_metadata:
            for param_data in algorithm_data.parameter_metadata:
                param = AlgorithmParameterMetadata(**param_data.dict())
                db.add(param)
                await db.flush()
                # Add to algorithm parameters
                algorithm.parameters.append(param)
        
        await db.commit()
        await db.refresh(algorithm)
        
        return algorithm
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating algorithm: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{algorithm_id}", response_model=AlgorithmResponse)
async def update_algorithm(
    algorithm_data: AlgorithmUpdate,
    db: AsyncSession = Depends(get_db_session),
    algorithm_id: int = Path(..., description="Algorithm ID")
):
    """
    Update an existing algorithm.
    """
    try:
        # Get existing algorithm
        query = select(Algorithm).where(Algorithm.id == algorithm_id)
        result = await db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        # Update fields
        update_data = algorithm_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(algorithm, field, value)
        
        await db.commit()
        await db.refresh(algorithm)
        
        return algorithm
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating algorithm {algorithm_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{algorithm_id}", status_code=204)
async def delete_algorithm(
    algorithm_id: int = Path(..., description="Algorithm ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete an algorithm.
    """
    try:
        # Get existing algorithm
        query = select(Algorithm).where(Algorithm.id == algorithm_id)
        result = await db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        # Check if algorithm is being used in experiments
        if algorithm.experiments:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete algorithm that is being used in experiments"
            )
        
        await db.delete(algorithm)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting algorithm {algorithm_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{algorithm_id}/benchmark", response_model=AlgorithmBenchmarkResponse)
async def run_benchmark(
    benchmark_data: AlgorithmBenchmarkCreate,
    algorithm_id: int = Path(..., description="Algorithm ID"),
    db: AsyncSession = Depends(get_db_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Run a benchmark for an algorithm.
    """
    try:
        # Verify algorithm exists
        query = select(Algorithm).where(Algorithm.id == algorithm_id)
        result = await db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        # Create benchmark record
        benchmark = AlgorithmBenchmark(
            algorithm_id=algorithm_id,
            **benchmark_data.dict()
        )
        db.add(benchmark)
        await db.commit()
        await db.refresh(benchmark)
        
        # Run benchmark in background
        background_tasks.add_task(
            BenchmarkService.run_algorithm_benchmark,
            algorithm_id,
            benchmark.id,
            benchmark_data.dict()
        )
        
        return benchmark
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating benchmark for algorithm {algorithm_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{algorithm_id}/benchmarks", response_model=List[AlgorithmBenchmarkResponse])
async def list_algorithm_benchmarks(
    algorithm_id: int = Path(..., description="Algorithm ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List benchmarks for an algorithm.
    """
    try:
        # Verify algorithm exists
        query = select(Algorithm).where(Algorithm.id == algorithm_id)
        result = await db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        # Get benchmarks
        benchmark_query = select(AlgorithmBenchmark).where(
            AlgorithmBenchmark.algorithm_id == algorithm_id
        ).offset(skip).limit(limit)
        
        result = await db.execute(benchmark_query)
        benchmarks = result.scalars().all()
        
        return benchmarks
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing benchmarks for algorithm {algorithm_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/compare", response_model=AlgorithmComparisonResponse)
async def compare_algorithms(
    comparison_request: AlgorithmComparisonRequest,
    db: AsyncSession = Depends(get_db_session),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Compare multiple algorithms.
    """
    try:
        # Verify all algorithms exist
        algorithms = []
        for algo_id in comparison_request.algorithm_ids:
            query = select(Algorithm).where(Algorithm.id == algo_id)
            result = await db.execute(query)
            algorithm = result.scalar_one_or_none()
            
            if not algorithm:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Algorithm with ID {algo_id} not found"
                )
            algorithms.append(algorithm)
        
        # Create comparison
        comparison_id = f"comp_{len(comparison_request.algorithm_ids)}_{comparison_request.dataset_name}"
        
        # Run comparison in background
        background_tasks.add_task(
            BenchmarkService.run_algorithm_comparison,
            comparison_id,
            comparison_request.dict()
        )
        
        return AlgorithmComparisonResponse(
            comparison_id=comparison_id,
            algorithms=algorithms,
            benchmarks=[],
            comparison_metrics={},
            ranking=[],
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing algorithms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types", response_model=List[str])
async def get_algorithm_types():
    """
    Get all available algorithm types.
    """
    return [t.value for t in AlgorithmType]


@router.get("/categories", response_model=List[str])
async def get_algorithm_categories():
    """
    Get all available algorithm categories.
    """
    return [c.value for c in AlgorithmCategory]


@router.get("/statuses", response_model=List[str])
async def get_algorithm_statuses():
    """
    Get all available algorithm statuses.
    """
    return [s.value for s in AlgorithmStatus]


@router.get("/{algorithm_id}/parameters", response_model=List[AlgorithmParameterMetadataResponse])
async def get_algorithm_parameters(
    algorithm_id: int = Path(..., description="Algorithm ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get parameters for an algorithm.
    """
    try:
        # Get algorithm with parameters
        query = select(Algorithm).options(
            selectinload(Algorithm.parameters)
        ).where(Algorithm.id == algorithm_id)
        
        result = await db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        return algorithm.parameters
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameters for algorithm {algorithm_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{algorithm_id}/parameters", response_model=AlgorithmParameterMetadataResponse)
async def add_algorithm_parameter(
    parameter_data: AlgorithmParameterMetadataCreate,
    algorithm_id: int = Path(..., description="Algorithm ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Add a parameter to an algorithm.
    """
    try:
        # Verify algorithm exists
        query = select(Algorithm).where(Algorithm.id == algorithm_id)
        result = await db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        # Create parameter
        parameter = AlgorithmParameterMetadata(**parameter_data.dict())
        db.add(parameter)
        await db.flush()
        
        # Add to algorithm
        algorithm.parameters.append(parameter)
        await db.commit()
        await db.refresh(parameter)
        
        return parameter
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding parameter to algorithm {algorithm_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/summary")
async def get_algorithm_stats(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get algorithm statistics summary.
    """
    try:
        # Get counts by type
        type_counts = {}
        for algo_type in AlgorithmType:
            query = select(Algorithm).where(Algorithm.type == algo_type)
            result = await db.execute(query)
            type_counts[algo_type.value] = len(result.scalars().all())
        
        # Get counts by category
        category_counts = {}
        for category in AlgorithmCategory:
            query = select(Algorithm).where(Algorithm.category == category)
            result = await db.execute(query)
            category_counts[category.value] = len(result.scalars().all())
        
        # Get counts by status
        status_counts = {}
        for status in AlgorithmStatus:
            query = select(Algorithm).where(Algorithm.status == status)
            result = await db.execute(query)
            status_counts[status.value] = len(result.scalars().all())
        
        # Get total benchmarks
        benchmark_query = select(AlgorithmBenchmark)
        result = await db.execute(benchmark_query)
        total_benchmarks = len(result.scalars().all())
        
        return {
            "total_algorithms": sum(type_counts.values()),
            "type_distribution": type_counts,
            "category_distribution": category_counts,
            "status_distribution": status_counts,
            "total_benchmarks": total_benchmarks
        }
        
    except Exception as e:
        logger.error(f"Error getting algorithm stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
