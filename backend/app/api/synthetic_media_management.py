"""
API endpoints for synthetic media management and retrieval.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, Path as PathParam, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
import json
import os
from pathlib import Path
import uuid

from app.database.connection import get_db_session
from app.models.synthetic_media import (
    SyntheticMedia, SyntheticMediaGeneration, SyntheticMediaCompression,
    SyntheticDataBatch, SyntheticDataSchema, SyntheticDataExperiment,
    MediaType, GenerationStatus
)
from app.services.synthetic_media_service import SyntheticMediaService

router = APIRouter(prefix="/api/v1/synthetic-media", tags=["Synthetic Media Management"])


# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

from pydantic import BaseModel, Field
from typing import Literal


class SyntheticMediaResponse(BaseModel):
    """Response model for synthetic media items."""
    id: str
    name: str
    description: Optional[str]
    media_type: str
    format: str
    mime_type: str
    file_size: int
    thumbnail_path: Optional[str]
    generation_parameters: Dict[str, Any]
    schema_definition: Dict[str, Any]
    analysis_results: Optional[Dict[str, Any]]
    compression_metrics: Optional[Dict[str, Any]]
    status: str
    processing_time: Optional[float]
    complexity_score: Optional[float]
    entropy_score: Optional[float]
    redundancy_score: Optional[float]
    tags: Optional[List[str]]
    category: Optional[str]
    experiment_id: Optional[str]
    batch_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class SyntheticMediaListResponse(BaseModel):
    """Response model for paginated synthetic media list."""
    items: List[SyntheticMediaResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SyntheticMediaFilter(BaseModel):
    """Filter model for synthetic media queries."""
    media_types: Optional[List[str]] = None
    formats: Optional[List[str]] = None
    status: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    experiment_ids: Optional[List[str]] = None
    batch_ids: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_file_size: Optional[int] = None
    max_file_size: Optional[int] = None
    min_complexity: Optional[float] = None
    max_complexity: Optional[float] = None


class BatchResponse(BaseModel):
    """Response model for batch operations."""
    batch_id: str
    name: str
    media_type: str
    count: int
    status: str
    completed_count: int
    failed_count: int
    total_size: Optional[int]
    average_processing_time: Optional[float]
    created_at: datetime


class SchemaResponse(BaseModel):
    """Response model for schema definitions."""
    id: str
    name: str
    description: Optional[str]
    media_type: str
    schema_definition: Dict[str, Any]
    usage_count: int
    last_used: Optional[datetime]
    tags: Optional[List[str]]
    category: Optional[str]
    version: str
    is_active: bool
    created_at: datetime


# ============================================================================
# SYNTHETIC MEDIA LISTING AND FILTERING
# ============================================================================

@router.get("/", response_model=SyntheticMediaListResponse)
async def list_synthetic_media(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    format: Optional[str] = Query(None, description="Filter by format"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    experiment_id: Optional[str] = Query(None, description="Filter by experiment ID"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List synthetic media with filtering and pagination.
    
    Supports filtering by:
    - Media type (image, video, audio, text, data)
    - Format (png, mp4, wav, etc.)
    - Status (pending, generating, completed, failed)
    - Tags (comma-separated)
    - Category
    - Experiment ID
    - Batch ID
    - Date range
    - File size range
    - Complexity range
    
    Supports sorting by any field and searching in name/description.
    """
    try:
        # Build query
        query = select(SyntheticMedia)
        
        # Apply filters
        filters = []
        
        if media_type:
            filters.append(SyntheticMedia.media_type == media_type)
        
        if format:
            filters.append(SyntheticMedia.format == format)
        
        if status:
            filters.append(SyntheticMedia.status == status)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            filters.append(SyntheticMedia.tags.op("?")(tag_list))
        
        if category:
            filters.append(SyntheticMedia.category == category)
        
        if experiment_id:
            filters.append(SyntheticMedia.experiment_id == experiment_id)
        
        if batch_id:
            filters.append(SyntheticMedia.batch_id == batch_id)
        
        if search:
            search_filter = or_(
                SyntheticMedia.name.ilike(f"%{search}%"),
                SyntheticMedia.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(SyntheticMedia, sort_by, SyntheticMedia.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Convert to response models
        media_items = []
        for item in items:
            media_items.append(SyntheticMediaResponse(
                id=str(item.id),
                name=item.name,
                description=item.description,
                media_type=item.media_type,
                format=item.format,
                mime_type=item.mime_type,
                file_size=item.file_size,
                thumbnail_path=item.thumbnail_path,
                generation_parameters=item.generation_parameters,
                schema_definition=item.schema_definition,
                analysis_results=item.analysis_results,
                compression_metrics=item.compression_metrics,
                status=item.status,
                processing_time=item.processing_time,
                complexity_score=item.complexity_score,
                entropy_score=item.entropy_score,
                redundancy_score=item.redundancy_score,
                tags=item.tags,
                category=item.category,
                experiment_id=str(item.experiment_id) if item.experiment_id else None,
                batch_id=str(item.batch_id) if item.batch_id else None,
                created_at=item.created_at,
                updated_at=item.updated_at
            ))
        
        total_pages = (total + page_size - 1) // page_size
        
        return SyntheticMediaListResponse(
            items=media_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list synthetic media: {str(e)}")


@router.get("/{media_id}", response_model=SyntheticMediaResponse)
async def get_synthetic_media(
    media_id: str = PathParam(..., description="Media ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get detailed information about a specific synthetic media item."""
    try:
        query = select(SyntheticMedia).where(SyntheticMedia.id == media_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Synthetic media not found")
        
        return SyntheticMediaResponse(
            id=str(item.id),
            name=item.name,
            description=item.description,
            media_type=item.media_type,
            format=item.format,
            mime_type=item.mime_type,
            file_size=item.file_size,
            thumbnail_path=item.thumbnail_path,
            generation_parameters=item.generation_parameters,
            schema_definition=item.schema_definition,
            analysis_results=item.analysis_results,
            compression_metrics=item.compression_metrics,
            status=item.status,
            processing_time=item.processing_time,
            complexity_score=item.complexity_score,
            entropy_score=item.entropy_score,
            redundancy_score=item.redundancy_score,
            tags=item.tags,
            category=item.category,
            experiment_id=str(item.experiment_id) if item.experiment_id else None,
            batch_id=str(item.batch_id) if item.batch_id else None,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get synthetic media: {str(e)}")


# ============================================================================
# FILE SERVING
# ============================================================================

@router.get("/{media_id}/file")
async def serve_media_file(
    media_id: str = PathParam(..., description="Media ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """Serve the actual media file."""
    try:
        query = select(SyntheticMedia).where(SyntheticMedia.id == media_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Synthetic media not found")
        
        if not os.path.exists(item.file_path):
            raise HTTPException(status_code=404, detail="Media file not found on disk")
        
        return FileResponse(
            path=item.file_path,
            media_type=item.mime_type,
            filename=f"{item.name}.{item.format}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve media file: {str(e)}")


@router.get("/{media_id}/thumbnail")
async def serve_thumbnail(
    media_id: str = PathParam(..., description="Media ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """Serve the thumbnail for the media file."""
    try:
        query = select(SyntheticMedia).where(SyntheticMedia.id == media_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Synthetic media not found")
        
        if not item.thumbnail_path or not os.path.exists(item.thumbnail_path):
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        return FileResponse(
            path=item.thumbnail_path,
            media_type="image/jpeg",
            filename=f"{item.name}_thumb.jpg"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve thumbnail: {str(e)}")


# ============================================================================
# BATCH MANAGEMENT
# ============================================================================

@router.get("/batches/", response_model=List[BatchResponse])
async def list_batches(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    experiment_id: Optional[str] = Query(None, description="Filter by experiment ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """List synthetic data batches."""
    try:
        query = select(SyntheticDataBatch)
        
        filters = []
        if media_type:
            filters.append(SyntheticDataBatch.media_type == media_type)
        if status:
            filters.append(SyntheticDataBatch.status == status)
        if experiment_id:
            filters.append(SyntheticDataBatch.experiment_id == experiment_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(SyntheticDataBatch.created_at))
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        batches = result.scalars().all()
        
        batch_responses = []
        for batch in batches:
            batch_responses.append(BatchResponse(
                batch_id=str(batch.id),
                name=batch.name,
                media_type=batch.media_type,
                count=batch.count,
                status=batch.status,
                completed_count=batch.completed_count,
                failed_count=batch.failed_count,
                total_size=batch.total_size,
                average_processing_time=batch.average_processing_time,
                created_at=batch.created_at
            ))
        
        return batch_responses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list batches: {str(e)}")


@router.get("/batches/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: str = PathParam(..., description="Batch ID"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get detailed information about a specific batch."""
    try:
        query = select(SyntheticDataBatch).where(SyntheticDataBatch.id == batch_id)
        result = await db.execute(query)
        batch = result.scalar_one_or_none()
        
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return BatchResponse(
            batch_id=str(batch.id),
            name=batch.name,
            media_type=batch.media_type,
            count=batch.count,
            status=batch.status,
            completed_count=batch.completed_count,
            failed_count=batch.failed_count,
            total_size=batch.total_size,
            average_processing_time=batch.average_processing_time,
            created_at=batch.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch: {str(e)}")


@router.get("/batches/{batch_id}/media", response_model=List[SyntheticMediaResponse])
async def get_batch_media(
    batch_id: str = PathParam(..., description="Batch ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all media items in a specific batch."""
    try:
        query = select(SyntheticMedia).where(SyntheticMedia.batch_id == batch_id)
        query = query.order_by(desc(SyntheticMedia.created_at))
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        media_items = []
        for item in items:
            media_items.append(SyntheticMediaResponse(
                id=str(item.id),
                name=item.name,
                description=item.description,
                media_type=item.media_type,
                format=item.format,
                mime_type=item.mime_type,
                file_size=item.file_size,
                thumbnail_path=item.thumbnail_path,
                generation_parameters=item.generation_parameters,
                schema_definition=item.schema_definition,
                analysis_results=item.analysis_results,
                compression_metrics=item.compression_metrics,
                status=item.status,
                processing_time=item.processing_time,
                complexity_score=item.complexity_score,
                entropy_score=item.entropy_score,
                redundancy_score=item.redundancy_score,
                tags=item.tags,
                category=item.category,
                experiment_id=str(item.experiment_id) if item.experiment_id else None,
                batch_id=str(item.batch_id) if item.batch_id else None,
                created_at=item.created_at,
                updated_at=item.updated_at
            ))
        
        return media_items
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch media: {str(e)}")


# ============================================================================
# SCHEMA MANAGEMENT
# ============================================================================

@router.get("/schemas/", response_model=List[SchemaResponse])
async def list_schemas(
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    active_only: bool = Query(True, description="Show only active schemas"),
    db: AsyncSession = Depends(get_db_session)
):
    """List available schema definitions."""
    try:
        query = select(SyntheticDataSchema)
        
        filters = []
        if media_type:
            filters.append(SyntheticDataSchema.media_type == media_type)
        if category:
            filters.append(SyntheticDataSchema.category == category)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            filters.append(SyntheticDataSchema.tags.op("?")(tag_list))
        if active_only:
            filters.append(SyntheticDataSchema.is_active == True)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(desc(SyntheticDataSchema.usage_count), desc(SyntheticDataSchema.created_at))
        
        result = await db.execute(query)
        schemas = result.scalars().all()
        
        schema_responses = []
        for schema in schemas:
            schema_responses.append(SchemaResponse(
                id=str(schema.id),
                name=schema.name,
                description=schema.description,
                media_type=schema.media_type,
                schema_definition=schema.schema_definition,
                usage_count=schema.usage_count,
                last_used=schema.last_used,
                tags=schema.tags,
                category=schema.category,
                version=schema.version,
                is_active=schema.is_active,
                created_at=schema.created_at
            ))
        
        return schema_responses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list schemas: {str(e)}")


# ============================================================================
# ANALYTICS AND STATISTICS
# ============================================================================

@router.get("/analytics/overview")
async def get_analytics_overview(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get analytics overview of synthetic media."""
    try:
        # Base query with date filters
        base_query = select(SyntheticMedia)
        if date_from:
            base_query = base_query.where(SyntheticMedia.created_at >= date_from)
        if date_to:
            base_query = base_query.where(SyntheticMedia.created_at <= date_to)
        
        # Total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()
        
        # Count by media type
        type_query = select(
            SyntheticMedia.media_type,
            func.count().label('count')
        ).select_from(base_query.subquery()).group_by(SyntheticMedia.media_type)
        type_result = await db.execute(type_query)
        type_counts = {row.media_type: row.count for row in type_result}
        
        # Count by status
        status_query = select(
            SyntheticMedia.status,
            func.count().label('count')
        ).select_from(base_query.subquery()).group_by(SyntheticMedia.status)
        status_result = await db.execute(status_query)
        status_counts = {row.status: row.count for row in status_result}
        
        # Total file size
        size_query = select(func.sum(SyntheticMedia.file_size)).select_from(base_query.subquery())
        size_result = await db.execute(size_query)
        total_size = size_result.scalar() or 0
        
        # Average complexity
        complexity_query = select(func.avg(SyntheticMedia.complexity_score)).select_from(base_query.subquery())
        complexity_result = await db.execute(complexity_query)
        avg_complexity = complexity_result.scalar() or 0
        
        return {
            "total_count": total_count,
            "type_counts": type_counts,
            "status_counts": status_counts,
            "total_size": total_size,
            "average_complexity": avg_complexity,
            "date_range": {
                "from": date_from,
                "to": date_to
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


# ============================================================================
# MEDIA MANAGEMENT OPERATIONS
# ============================================================================

@router.delete("/{media_id}")
async def delete_synthetic_media(
    media_id: str = PathParam(..., description="Media ID"),
    delete_files: bool = Query(True, description="Delete associated files from disk"),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete synthetic media and optionally its files."""
    try:
        query = select(SyntheticMedia).where(SyntheticMedia.id == media_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Synthetic media not found")
        
        # Delete files if requested
        if delete_files:
            if os.path.exists(item.file_path):
                os.remove(item.file_path)
            if item.thumbnail_path and os.path.exists(item.thumbnail_path):
                os.remove(item.thumbnail_path)
        
        # Delete from database
        await db.delete(item)
        await db.commit()
        
        return {"message": "Synthetic media deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete synthetic media: {str(e)}")


@router.post("/{media_id}/regenerate")
async def regenerate_media(
    media_id: str = PathParam(..., description="Media ID"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db_session)
):
    """Regenerate synthetic media using the same parameters."""
    try:
        query = select(SyntheticMedia).where(SyntheticMedia.id == media_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Synthetic media not found")
        
        # Add regeneration task to background
        background_tasks.add_task(
            SyntheticMediaService.regenerate_media,
            str(item.id),
            item.generation_parameters,
            item.schema_definition
        )
        
        return {"message": "Media regeneration started", "media_id": media_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start regeneration: {str(e)}")
