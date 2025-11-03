"""
Service for managing synthetic media operations.
"""

import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database.connection import get_db_session
from app.models.synthetic_media import (
    SyntheticMedia, SyntheticMediaGeneration, SyntheticDataBatch,
    MediaType, GenerationStatus
)
from app.services.media_generator import SyntheticMediaGenerator
from app.services.audio_generator import AdvancedAudioGenerator

logger = logging.getLogger(__name__)


class SyntheticMediaService:
    """Service for managing synthetic media operations."""
    
    def __init__(self):
        self.media_storage_path = Path("/app/media")
        self.thumbnails_path = self.media_storage_path / "thumbnails"
        self.images_path = self.media_storage_path / "images"
        self.videos_path = self.media_storage_path / "videos"
        self.audio_path = self.media_storage_path / "audio"
        
        # Ensure directories exist
        for path in [self.media_storage_path, self.thumbnails_path, 
                    self.images_path, self.videos_path, self.audio_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def save_media_metadata(
        self,
        media_id: str,
        name: str,
        media_type: str,
        format: str,
        file_path: str,
        file_size: int,
        generation_parameters: Dict[str, Any],
        schema_definition: Dict[str, Any],
        analysis_results: Optional[Dict[str, Any]] = None,
        thumbnail_path: Optional[str] = None,
        experiment_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        db: AsyncSession = None
    ) -> SyntheticMedia:
        """Save synthetic media metadata to database."""
        
        if db is None:
            async with get_db_session() as db:
                return await self.save_media_metadata(
                    media_id, name, media_type, format, file_path, file_size,
                    generation_parameters, schema_definition, analysis_results,
                    thumbnail_path, experiment_id, batch_id, tags, category, db
                )
        
        try:
            # Determine MIME type
            mime_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'webp': 'image/webp',
                'svg': 'image/svg+xml',
                'mp4': 'video/mp4',
                'avi': 'video/x-msvideo',
                'mov': 'video/quicktime',
                'wav': 'audio/wav',
                'mp3': 'audio/mpeg',
                'flac': 'audio/flac',
                'ogg': 'audio/ogg'
            }
            mime_type = mime_types.get(format.lower(), 'application/octet-stream')
            
            # Extract quality metrics from analysis results
            complexity_score = None
            entropy_score = None
            redundancy_score = None
            
            if analysis_results:
                complexity_data = analysis_results.get('complexity', {})
                entropy_data = analysis_results.get('entropy', {})
                redundancy_data = analysis_results.get('redundancy', {})
                
                complexity_score = complexity_data.get('structural') or complexity_data.get('kolmogorov')
                entropy_score = entropy_data.get('shannon') or entropy_data.get('temporal')
                redundancy_score = redundancy_data.get('overall')
            
            # Create media record
            media = SyntheticMedia(
                id=uuid.UUID(media_id),
                name=name,
                media_type=media_type,
                format=format,
                mime_type=mime_type,
                file_path=file_path,
                file_size=file_size,
                thumbnail_path=thumbnail_path,
                generation_parameters=generation_parameters,
                schema_definition=schema_definition,
                analysis_results=analysis_results,
                status=GenerationStatus.COMPLETED,
                complexity_score=complexity_score,
                entropy_score=entropy_score,
                redundancy_score=redundancy_score,
                tags=tags,
                category=category,
                experiment_id=uuid.UUID(experiment_id) if experiment_id else None,
                batch_id=uuid.UUID(batch_id) if batch_id else None
            )
            
            db.add(media)
            await db.commit()
            await db.refresh(media)
            
            logger.info(f"Saved media metadata: {media_id} ({media_type})")
            return media
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to save media metadata: {e}")
            raise
    
    async def save_generation_record(
        self,
        media_id: str,
        generation_type: str,
        algorithm_used: str,
        parameters: Dict[str, Any],
        generation_time: float,
        quality_score: Optional[float] = None,
        complexity_achieved: Optional[float] = None,
        entropy_achieved: Optional[float] = None,
        memory_used: Optional[int] = None,
        cpu_usage: Optional[float] = None,
        db: AsyncSession = None
    ) -> SyntheticMediaGeneration:
        """Save generation record to database."""
        
        if db is None:
            async with get_db_session() as db:
                return await self.save_generation_record(
                    media_id, generation_type, algorithm_used, parameters,
                    generation_time, quality_score, complexity_achieved,
                    entropy_achieved, memory_used, cpu_usage, db
                )
        
        try:
            generation = SyntheticMediaGeneration(
                media_id=uuid.UUID(media_id),
                generation_type=generation_type,
                algorithm_used=algorithm_used,
                parameters=parameters,
                generation_time=generation_time,
                quality_score=quality_score,
                complexity_achieved=complexity_achieved,
                entropy_achieved=entropy_achieved,
                memory_used=memory_used,
                cpu_usage=cpu_usage
            )
            
            db.add(generation)
            await db.commit()
            await db.refresh(generation)
            
            logger.info(f"Saved generation record: {media_id} ({generation_type})")
            return generation
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to save generation record: {e}")
            raise
    
    async def create_batch(
        self,
        name: str,
        media_type: str,
        count: int,
        parameters: Dict[str, Any],
        description: Optional[str] = None,
        experiment_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> SyntheticDataBatch:
        """Create a new batch for synthetic data generation."""
        
        if db is None:
            async with get_db_session() as db:
                return await self.create_batch(
                    name, media_type, count, parameters, description, experiment_id, db
                )
        
        try:
            batch = SyntheticDataBatch(
                name=name,
                description=description,
                media_type=media_type,
                count=count,
                parameters=parameters,
                status=GenerationStatus.PENDING,
                experiment_id=uuid.UUID(experiment_id) if experiment_id else None
            )
            
            db.add(batch)
            await db.commit()
            await db.refresh(batch)
            
            logger.info(f"Created batch: {name} ({count} {media_type} items)")
            return batch
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create batch: {e}")
            raise
    
    async def update_batch_progress(
        self,
        batch_id: str,
        completed_count: int,
        failed_count: int,
        total_size: Optional[int] = None,
        average_processing_time: Optional[float] = None,
        quality_metrics: Optional[Dict[str, Any]] = None,
        status: Optional[GenerationStatus] = None,
        db: AsyncSession = None
    ):
        """Update batch generation progress."""
        
        if db is None:
            async with get_db_session() as db:
                return await self.update_batch_progress(
                    batch_id, completed_count, failed_count, total_size,
                    average_processing_time, quality_metrics, status, db
                )
        
        try:
            update_data = {
                "completed_count": completed_count,
                "failed_count": failed_count
            }
            
            if total_size is not None:
                update_data["total_size"] = total_size
            if average_processing_time is not None:
                update_data["average_processing_time"] = average_processing_time
            if quality_metrics is not None:
                update_data["quality_metrics"] = quality_metrics
            if status is not None:
                update_data["status"] = status
            
            query = update(SyntheticDataBatch).where(
                SyntheticDataBatch.id == uuid.UUID(batch_id)
            ).values(**update_data)
            
            await db.execute(query)
            await db.commit()
            
            logger.info(f"Updated batch progress: {batch_id} ({completed_count}/{completed_count + failed_count})")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update batch progress: {e}")
            raise
    
    async def generate_and_save_image(
        self,
        width: int,
        height: int,
        structure_type: str,
        complexity: float,
        entropy: float,
        redundancy: float,
        format: str = "png",
        color_space: str = "rgb",
        name: Optional[str] = None,
        experiment_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate and save an image with full metadata tracking."""
        
        media_id = f"img_{uuid.uuid4().hex[:12]}"
        name = name or f"Generated Image {media_id}"
        
        try:
            # Generate the image
            result = SyntheticMediaGenerator.generate_and_save_image(
                width=width,
                height=height,
                structure_type=structure_type,
                complexity=complexity,
                entropy=entropy,
                redundancy=redundancy,
                format=format,
                color_space=color_space,
                image_id=media_id
            )
            
            # Prepare generation parameters
            generation_parameters = {
                "width": width,
                "height": height,
                "structure_type": structure_type,
                "format": format,
                "color_space": color_space,
                "complexity": complexity,
                "entropy": entropy,
                "redundancy": redundancy
            }
            
            # Prepare schema definition
            schema_definition = {
                "complexity": complexity,
                "entropy": entropy,
                "redundancy": redundancy,
                "structure": structure_type,
                "dimensions": [
                    {
                        "id": "spatial",
                        "name": "Spatial Dimensions",
                        "type": "image",
                        "depth": 2,
                        "complexity": complexity,
                        "parameters": {
                            "width": width,
                            "height": height,
                            "color_space": color_space
                        }
                    }
                ]
            }
            
            # Save to database
            async with get_db_session() as db:
                media = await self.save_media_metadata(
                    media_id=media_id,
                    name=name,
                    media_type=MediaType.IMAGE,
                    format=format,
                    file_path=result['image_url'],
                    file_size=result['metadata']['fileSize'],
                    generation_parameters=generation_parameters,
                    schema_definition=schema_definition,
                    analysis_results=result.get('analysis'),
                    thumbnail_path=result.get('thumbnail_url'),
                    experiment_id=experiment_id,
                    batch_id=batch_id,
                    tags=tags,
                    category=category,
                    db=db
                )
                
                # Save generation record
                await self.save_generation_record(
                    media_id=media_id,
                    generation_type=structure_type,
                    algorithm_used="SyntheticMediaGenerator",
                    parameters=generation_parameters,
                    generation_time=result.get('processing_time', 0.0),
                    quality_score=result.get('analysis', {}).get('quality_score'),
                    complexity_achieved=complexity,
                    entropy_achieved=entropy,
                    db=db
                )
            
            return {
                "media_id": media_id,
                "name": name,
                "file_path": result['image_url'],
                "thumbnail_path": result.get('thumbnail_url'),
                "metadata": result['metadata'],
                "analysis": result.get('analysis'),
                "processing_time": result.get('processing_time', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate and save image: {e}")
            raise
    
    async def generate_and_save_video(
        self,
        width: int,
        height: int,
        duration: float,
        frame_rate: int,
        codec: str,
        layers: List[Dict[str, Any]],
        complexity: float,
        temporal_coherence: float,
        name: Optional[str] = None,
        experiment_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate and save a video with full metadata tracking."""
        
        media_id = f"vid_{uuid.uuid4().hex[:12]}"
        name = name or f"Generated Video {media_id}"
        
        try:
            # Generate the video
            result = SyntheticMediaGenerator.generate_and_save_video(
                width=width,
                height=height,
                duration=duration,
                frame_rate=frame_rate,
                codec=codec,
                layers=layers,
                complexity=complexity,
                temporal_coherence=temporal_coherence,
                video_id=media_id
            )
            
            # Prepare generation parameters
            generation_parameters = {
                "width": width,
                "height": height,
                "duration": duration,
                "frame_rate": frame_rate,
                "codec": codec,
                "layers": layers,
                "complexity": complexity,
                "temporal_coherence": temporal_coherence
            }
            
            # Prepare schema definition
            schema_definition = {
                "complexity": complexity,
                "entropy": complexity * 0.9,  # Estimate entropy from complexity
                "redundancy": 1.0 - complexity,  # Estimate redundancy
                "structure": "video",
                "dimensions": [
                    {
                        "id": "spatial",
                        "name": "Spatial Dimensions",
                        "type": "video",
                        "depth": 2,
                        "complexity": complexity,
                        "parameters": {
                            "width": width,
                            "height": height,
                            "frame_rate": frame_rate
                        }
                    },
                    {
                        "id": "temporal",
                        "name": "Temporal Dimension",
                        "type": "time",
                        "depth": 1,
                        "complexity": temporal_coherence,
                        "parameters": {
                            "duration": duration,
                            "frame_rate": frame_rate
                        }
                    }
                ]
            }
            
            # Save to database
            async with get_db_session() as db:
                media = await self.save_media_metadata(
                    media_id=media_id,
                    name=name,
                    media_type=MediaType.VIDEO,
                    format=codec,
                    file_path=result['video_url'],
                    file_size=result['metadata']['fileSize'],
                    generation_parameters=generation_parameters,
                    schema_definition=schema_definition,
                    analysis_results=result.get('analysis'),
                    thumbnail_path=result.get('thumbnail_url'),
                    experiment_id=experiment_id,
                    batch_id=batch_id,
                    tags=tags,
                    category=category,
                    db=db
                )
                
                # Save generation record
                await self.save_generation_record(
                    media_id=media_id,
                    generation_type="video",
                    algorithm_used="SyntheticMediaGenerator",
                    parameters=generation_parameters,
                    generation_time=result.get('processing_time', 0.0),
                    quality_score=result.get('analysis', {}).get('quality_score'),
                    complexity_achieved=complexity,
                    entropy_achieved=complexity * 0.9,
                    db=db
                )
            
            return {
                "media_id": media_id,
                "name": name,
                "file_path": result['video_url'],
                "thumbnail_path": result.get('thumbnail_url'),
                "metadata": result['metadata'],
                "analysis": result.get('analysis'),
                "processing_time": result.get('processing_time', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate and save video: {e}")
            raise
    
    async def generate_and_save_audio(
        self,
        sample_rate: int,
        bit_depth: int,
        channels: int,
        duration: float,
        format: str,
        sources: List[Dict[str, Any]],
        complexity: float,
        entropy: float,
        redundancy: float,
        name: Optional[str] = None,
        experiment_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate and save audio with full metadata tracking."""
        
        media_id = f"aud_{uuid.uuid4().hex[:12]}"
        name = name or f"Generated Audio {media_id}"
        
        try:
            # Generate the audio
            result = AdvancedAudioGenerator.generate_audio(
                audio_type=sources[0].get('waveform', 'sine'),
                duration=duration,
                sample_rate=sample_rate,
                frequency=sources[0].get('frequency', 440),
                amplitude=sources[0].get('amplitude', 0.5)
            )
            
            # Convert to WAV bytes
            wav_bytes = AdvancedAudioGenerator.to_wav_bytes(
                result,
                sample_rate=sample_rate,
                bit_depth=bit_depth,
                channels=channels
            )
            
            # Save to file
            filename = f"{media_id}.{format}"
            audio_path = self.audio_path / filename
            with open(audio_path, 'wb') as f:
                f.write(wav_bytes)
            
            file_size = len(wav_bytes)
            
            # Prepare generation parameters
            generation_parameters = {
                "sample_rate": sample_rate,
                "bit_depth": bit_depth,
                "channels": channels,
                "duration": duration,
                "format": format,
                "sources": sources,
                "complexity": complexity,
                "entropy": entropy,
                "redundancy": redundancy
            }
            
            # Prepare schema definition
            schema_definition = {
                "complexity": complexity,
                "entropy": entropy,
                "redundancy": redundancy,
                "structure": "audio",
                "dimensions": [
                    {
                        "id": "temporal",
                        "name": "Temporal Dimension",
                        "type": "audio",
                        "depth": 1,
                        "complexity": complexity,
                        "parameters": {
                            "duration": duration,
                            "sample_rate": sample_rate
                        }
                    }
                ]
            }
            
            # Prepare analysis results
            import numpy as np
            audio_std = float(np.std(result))
            audio_mean = float(np.mean(result))
            
            analysis_results = {
                "complexity": {
                    "kolmogorov": min(audio_std / 0.5, 1.0),
                    "structural": complexity
                },
                "entropy": {
                    "shannon": entropy * 0.95,
                    "temporal": entropy * 0.88
                },
                "redundancy": {
                    "overall": redundancy,
                    "patterns": []
                },
                "waveform": {
                    "mean": audio_mean,
                    "std": audio_std,
                    "peak": float(np.max(np.abs(result)))
                }
            }
            
            # Save to database
            async with get_db_session() as db:
                media = await self.save_media_metadata(
                    media_id=media_id,
                    name=name,
                    media_type=MediaType.AUDIO,
                    format=format,
                    file_path=str(audio_path),
                    file_size=file_size,
                    generation_parameters=generation_parameters,
                    schema_definition=schema_definition,
                    analysis_results=analysis_results,
                    experiment_id=experiment_id,
                    batch_id=batch_id,
                    tags=tags,
                    category=category,
                    db=db
                )
                
                # Save generation record
                await self.save_generation_record(
                    media_id=media_id,
                    generation_type="audio",
                    algorithm_used="AdvancedAudioGenerator",
                    parameters=generation_parameters,
                    generation_time=0.1,  # Estimate
                    quality_score=0.85,  # Estimate
                    complexity_achieved=complexity,
                    entropy_achieved=entropy,
                    db=db
                )
            
            return {
                "media_id": media_id,
                "name": name,
                "file_path": str(audio_path),
                "metadata": {
                    "sampleRate": sample_rate,
                    "bitDepth": bit_depth,
                    "channels": channels,
                    "duration": duration,
                    "fileSize": file_size,
                    "format": format
                },
                "analysis": analysis_results,
                "processing_time": 0.1
            }
            
        except Exception as e:
            logger.error(f"Failed to generate and save audio: {e}")
            raise
    
    @staticmethod
    async def regenerate_media(
        media_id: str,
        generation_parameters: Dict[str, Any],
        schema_definition: Dict[str, Any]
    ):
        """Regenerate media using the same parameters (background task)."""
        try:
            service = SyntheticMediaService()
            
            # Extract parameters based on media type
            media_type = generation_parameters.get('media_type', 'image')
            
            if media_type == MediaType.IMAGE:
                await service.generate_and_save_image(
                    width=generation_parameters['width'],
                    height=generation_parameters['height'],
                    structure_type=generation_parameters['structure_type'],
                    complexity=schema_definition['complexity'],
                    entropy=schema_definition['entropy'],
                    redundancy=schema_definition['redundancy'],
                    format=generation_parameters['format'],
                    color_space=generation_parameters['color_space'],
                    name=f"Regenerated {media_id}"
                )
            elif media_type == MediaType.VIDEO:
                await service.generate_and_save_video(
                    width=generation_parameters['width'],
                    height=generation_parameters['height'],
                    duration=generation_parameters['duration'],
                    frame_rate=generation_parameters['frame_rate'],
                    codec=generation_parameters['codec'],
                    layers=generation_parameters['layers'],
                    complexity=schema_definition['complexity'],
                    temporal_coherence=generation_parameters['temporal_coherence'],
                    name=f"Regenerated {media_id}"
                )
            elif media_type == MediaType.AUDIO:
                await service.generate_and_save_audio(
                    sample_rate=generation_parameters['sample_rate'],
                    bit_depth=generation_parameters['bit_depth'],
                    channels=generation_parameters['channels'],
                    duration=generation_parameters['duration'],
                    format=generation_parameters['format'],
                    sources=generation_parameters['sources'],
                    complexity=schema_definition['complexity'],
                    entropy=schema_definition['entropy'],
                    redundancy=schema_definition['redundancy'],
                    name=f"Regenerated {media_id}"
                )
            
            logger.info(f"Successfully regenerated media: {media_id}")
            
        except Exception as e:
            logger.error(f"Failed to regenerate media {media_id}: {e}")
            raise
