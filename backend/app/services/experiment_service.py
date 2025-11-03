"""
Experiment service for the Dynamic Compression Algorithms backend.
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil
import json

from ..database.connection import get_db_session_optional
from ..models.experiment import (
    Experiment, ExperimentLog, ContentAnalysis, CompressionProgress, GenerativeContent,
    ExperimentStatus, ExperimentPhase, GenerationType
)
from ..services.algorithm_service import AlgorithmService
from ..services.content_analysis_service import ContentAnalysisService
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ExperimentService:
    """Service for managing experiment operations."""
    
    @staticmethod
    async def run_experiment(experiment_id: int, start_request: Dict[str, Any]):
        """
        Run an experiment asynchronously.
        
        Args:
            experiment_id: Experiment ID
            start_request: Start request data
        """
        try:
            logger.info(f"Starting experiment {experiment_id}")
            
            # Get experiment
            db = await get_db_session_optional()
            if not db:
                raise Exception("Database connection not available")
            
            query = select(Experiment).where(Experiment.id == experiment_id)
            result = await db.execute(query)
            experiment = result.scalar_one_or_none()
            
            if not experiment:
                raise Exception(f"Experiment {experiment_id} not found")
            
            # Get content data
            content_data = start_request.get('content_data')
            content_file_path = start_request.get('content_file_path')
            
            if content_file_path:
                with open(content_file_path, 'rb') as f:
                    content_data = f.read()
            
            if not content_data:
                raise Exception("No content data provided")
            
            # Update experiment with content info
            experiment.content_size = len(content_data)
            experiment.content_hash = hashlib.sha256(content_data).hexdigest()
            experiment.total_bytes = len(content_data)
            
            # Start experiment phases
            await ExperimentService._run_experiment_phases(experiment, content_data, db)
            
        except Exception as e:
            logger.error(f"Error running experiment {experiment_id}: {e}")
            await ExperimentService._handle_experiment_error(experiment_id, str(e))
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def _run_experiment_phases(experiment: Experiment, content_data: bytes, db: AsyncSession):
        """
        Run experiment phases sequentially.
        
        Args:
            experiment: Experiment instance
            content_data: Content data to process
            db: Database session
        """
        phases = [
            ExperimentPhase.ANALYSIS,
            ExperimentPhase.COMPRESSION,
            ExperimentPhase.DECOMPRESSION,
            ExperimentPhase.VALIDATION,
            ExperimentPhase.OPTIMIZATION
        ]
        
        total_phases = len(phases)
        
        for phase_index, phase in enumerate(phases):
            try:
                # Update current phase
                experiment.current_phase = phase
                experiment.phase_progress = 0.0
                experiment.overall_progress = (phase_index / total_phases) * 100
                
                await db.commit()
                
                # Log phase start
                await ExperimentService._add_experiment_log(
                    experiment.id, "info", f"Starting phase: {phase}", phase, db
                )
                
                # Execute phase
                if phase == ExperimentPhase.ANALYSIS:
                    await ExperimentService._execute_analysis_phase(experiment, content_data, db)
                elif phase == ExperimentPhase.COMPRESSION:
                    await ExperimentService._execute_compression_phase(experiment, content_data, db)
                elif phase == ExperimentPhase.DECOMPRESSION:
                    await ExperimentService._execute_decompression_phase(experiment, content_data, db)
                elif phase == ExperimentPhase.VALIDATION:
                    await ExperimentService._execute_validation_phase(experiment, content_data, db)
                elif phase == ExperimentPhase.OPTIMIZATION:
                    await ExperimentService._execute_optimization_phase(experiment, content_data, db)
                
                # Update progress
                experiment.phase_progress = 100.0
                experiment.overall_progress = ((phase_index + 1) / total_phases) * 100
                
                await db.commit()
                
                # Log phase completion
                await ExperimentService._add_experiment_log(
                    experiment.id, "info", f"Completed phase: {phase}", phase, db
                )
                
                # Check if experiment was stopped
                await db.refresh(experiment)
                if experiment.status != ExperimentStatus.RUNNING:
                    logger.info(f"Experiment {experiment.id} stopped during phase {phase}")
                    return
                
            except Exception as e:
                logger.error(f"Error in phase {phase} for experiment {experiment.id}: {e}")
                await ExperimentService._add_experiment_log(
                    experiment.id, "error", f"Phase {phase} failed: {str(e)}", phase, db
                )
                raise
        
        # Experiment completed successfully
        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.utcnow()
        experiment.overall_progress = 100.0
        
        await db.commit()
        
        await ExperimentService._add_experiment_log(
            experiment.id, "info", "Experiment completed successfully", None, db
        )
        
        logger.info(f"Experiment {experiment.id} completed successfully")
    
    @staticmethod
    async def _execute_analysis_phase(experiment: Experiment, content_data: bytes, db: AsyncSession):
        """Execute content analysis phase."""
        try:
            # Simulate analysis progress
            for progress in range(0, 101, 10):
                experiment.phase_progress = progress
                await db.commit()
                await asyncio.sleep(0.1)  # Simulate work
            
            # Perform content analysis
            analysis_result = await ContentAnalysisService.analyze_content(content_data)
            
            # Create content analysis record
            content_analysis = ContentAnalysis(
                experiment_id=experiment.id,
                content_type=analysis_result.get('content_type', 'unknown'),
                content_size=len(content_data),
                content_patterns=analysis_result.get('patterns', []),
                entropy=analysis_result.get('entropy', 0.0),
                redundancy=analysis_result.get('redundancy', 0.0),
                structure=analysis_result.get('structure', 'unknown'),
                language=analysis_result.get('language', 'unknown'),
                encoding=analysis_result.get('encoding', 'unknown'),
                byte_frequency=analysis_result.get('byte_frequency', {}),
                pattern_frequency=analysis_result.get('pattern_frequency', {}),
                compression_potential=analysis_result.get('compression_potential', 0.0),
                metadata=analysis_result.get('metadata', {})
            )
            
            db.add(content_analysis)
            await db.commit()
            
            # Update experiment with analysis results
            experiment.content_type = content_analysis.content_type
            experiment.content_metadata = {
                'entropy': content_analysis.entropy,
                'redundancy': content_analysis.redundancy,
                'compression_potential': content_analysis.compression_potential
            }
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error in analysis phase: {e}")
            raise
    
    @staticmethod
    async def _execute_compression_phase(experiment: Experiment, content_data: bytes, db: AsyncSession):
        """Execute compression phase."""
        try:
            # Create compression progress record
            compression_progress = CompressionProgress(
                experiment_id=experiment.id,
                current_phase=ExperimentPhase.COMPRESSION,
                phase_progress=0.0,
                processed_bytes=0,
                total_bytes=len(content_data),
                compression_history=[]
            )
            
            db.add(compression_progress)
            await db.commit()
            
            # Simulate compression with progress updates
            chunk_size = len(content_data) // 10
            for i in range(10):
                # Simulate processing chunk
                await asyncio.sleep(0.2)
                
                # Update progress
                processed_bytes = (i + 1) * chunk_size
                progress = ((i + 1) / 10) * 100
                
                compression_progress.processed_bytes = min(processed_bytes, len(content_data))
                compression_progress.phase_progress = progress
                experiment.processed_bytes = compression_progress.processed_bytes
                
                # Add compression history entry
                history_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'algorithm': experiment.algorithm.name if experiment.algorithm else 'unknown',
                    'ratio': 2.5 + (i * 0.1),  # Simulated compression ratio
                    'speed': 100 + (i * 10),  # Simulated speed MB/s
                    'quality': 0.95 - (i * 0.01)  # Simulated quality
                }
                
                if compression_progress.compression_history is None:
                    compression_progress.compression_history = []
                compression_progress.compression_history.append(history_entry)
                
                await db.commit()
                
                # Check if experiment was stopped
                await db.refresh(experiment)
                if experiment.status != ExperimentStatus.RUNNING:
                    return
            
            # Final compression results
            compression_progress.compression_ratio = 2.8
            compression_progress.processing_speed = 150.0
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error in compression phase: {e}")
            raise
    
    @staticmethod
    async def _execute_decompression_phase(experiment: Experiment, content_data: bytes, db: AsyncSession):
        """Execute decompression phase."""
        try:
            # Simulate decompression progress
            for progress in range(0, 101, 20):
                experiment.phase_progress = progress
                await db.commit()
                await asyncio.sleep(0.1)
                
                # Check if experiment was stopped
                await db.refresh(experiment)
                if experiment.status != ExperimentStatus.RUNNING:
                    return
            
            # Simulate decompression validation
            await ExperimentService._add_experiment_log(
                experiment.id, "info", "Decompression validation completed", ExperimentPhase.DECOMPRESSION, db
            )
            
        except Exception as e:
            logger.error(f"Error in decompression phase: {e}")
            raise
    
    @staticmethod
    async def _execute_validation_phase(experiment: Experiment, content_data: bytes, db: AsyncSession):
        """Execute validation phase."""
        try:
            # Simulate validation progress
            for progress in range(0, 101, 25):
                experiment.phase_progress = progress
                await db.commit()
                await asyncio.sleep(0.1)
                
                # Check if experiment was stopped
                await db.refresh(experiment)
                if experiment.status != ExperimentStatus.RUNNING:
                    return
            
            # Simulate validation results
            validation_results = {
                'integrity_check': True,
                'quality_score': 0.98,
                'error_rate': 0.001,
                'validation_time': 0.5
            }
            
            experiment.results = validation_results
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error in validation phase: {e}")
            raise
    
    @staticmethod
    async def _execute_optimization_phase(experiment: Experiment, content_data: bytes, db: AsyncSession):
        """Execute optimization phase."""
        try:
            # Simulate optimization progress
            for progress in range(0, 101, 33):
                experiment.phase_progress = progress
                await db.commit()
                await asyncio.sleep(0.1)
                
                # Check if experiment was stopped
                await db.refresh(experiment)
                if experiment.status != ExperimentStatus.RUNNING:
                    return
            
            # Simulate optimization results
            optimization_results = {
                'optimization_gain': 0.15,
                'final_compression_ratio': 3.2,
                'optimization_time': 0.3
            }
            
            if experiment.results is None:
                experiment.results = {}
            experiment.results.update(optimization_results)
            
            # Update final metrics
            experiment.metrics = {
                'compression_ratio': optimization_results['final_compression_ratio'],
                'processing_time': 2.5,
                'memory_usage': 150.0,
                'accuracy': 0.98,
                'throughput': 200.0,
                'error_rate': 0.001
            }
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error in optimization phase: {e}")
            raise
    
    @staticmethod
    async def resume_experiment(experiment_id: int, resume_request: Dict[str, Any]):
        """
        Resume a paused experiment.
        
        Args:
            experiment_id: Experiment ID
            resume_request: Resume request data
        """
        try:
            logger.info(f"Resuming experiment {experiment_id}")
            
            # Get experiment
            db = await get_db_session_optional()
            if not db:
                raise Exception("Database connection not available")
            
            query = select(Experiment).where(Experiment.id == experiment_id)
            result = await db.execute(query)
            experiment = result.scalar_one_or_none()
            
            if not experiment:
                raise Exception(f"Experiment {experiment_id} not found")
            
            if experiment.status != ExperimentStatus.PAUSED:
                raise Exception(f"Experiment {experiment_id} is not paused")
            
            # Update experiment status
            experiment.status = ExperimentStatus.RUNNING
            
            # Get content data (would need to be stored or retrieved)
            content_data = b"simulated_content_data"  # In real implementation, get from storage
            
            # Continue experiment phases
            await ExperimentService._run_experiment_phases(experiment, content_data, db)
            
        except Exception as e:
            logger.error(f"Error resuming experiment {experiment_id}: {e}")
            await ExperimentService._handle_experiment_error(experiment_id, str(e))
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def _handle_experiment_error(experiment_id: int, error_message: str):
        """Handle experiment errors."""
        try:
            db = await get_db_session_optional()
            if not db:
                return
            
            # Update experiment status
            query = update(Experiment).where(Experiment.id == experiment_id).values(
                status=ExperimentStatus.FAILED,
                error_message=error_message,
                completed_at=datetime.utcnow()
            )
            await db.execute(query)
            await db.commit()
            
            # Add error log
            await ExperimentService._add_experiment_log(
                experiment_id, "error", f"Experiment failed: {error_message}", None, db
            )
            
        except Exception as e:
            logger.error(f"Error handling experiment error: {e}")
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def _add_experiment_log(
        experiment_id: int,
        level: str,
        message: str,
        phase: Optional[str],
        db: AsyncSession
    ):
        """Add a log entry to an experiment."""
        try:
            log = ExperimentLog(
                experiment_id=experiment_id,
                level=level,
                message=message,
                phase=phase
            )
            db.add(log)
            await db.commit()
        except Exception as e:
            logger.error(f"Error adding experiment log: {e}")
    
    @staticmethod
    async def get_experiment_progress(experiment_id: int) -> Dict[str, Any]:
        """
        Get experiment progress information.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Dict[str, Any]: Progress information
        """
        try:
            db = await get_db_session_optional()
            if not db:
                return {}
            
            query = select(Experiment).where(Experiment.id == experiment_id)
            result = await db.execute(query)
            experiment = result.scalar_one_or_none()
            
            if not experiment:
                return {}
            
            return {
                'id': experiment.id,
                'name': experiment.name,
                'status': experiment.status,
                'current_phase': experiment.current_phase,
                'phase_progress': experiment.phase_progress,
                'overall_progress': experiment.overall_progress,
                'processed_bytes': experiment.processed_bytes,
                'total_bytes': experiment.total_bytes,
                'started_at': experiment.started_at,
                'estimated_duration': experiment.estimated_duration,
                'actual_duration': experiment.actual_duration
            }
            
        except Exception as e:
            logger.error(f"Error getting experiment progress {experiment_id}: {e}")
            return {}
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def generate_content(
        experiment_id: int,
        generation_type: GenerationType,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content for an experiment.
        
        Args:
            experiment_id: Experiment ID
            generation_type: Type of content generation
            parameters: Generation parameters
            
        Returns:
            Dict[str, Any]: Generation results
        """
        try:
            # Create generative content record
            db = await get_db_session_optional()
            if not db:
                raise Exception("Database connection not available")
            
            generative_content = GenerativeContent(
                experiment_id=experiment_id,
                is_generating=True,
                generation_type=generation_type,
                generation_progress=0.0,
                patterns=[],
                complexity=0.0,
                volume=0,
                quality=0.0,
                diversity=0.0,
                generated_samples=[]
            )
            
            db.add(generative_content)
            await db.commit()
            
            # Simulate content generation
            total_samples = parameters.get('num_samples', 100)
            
            for i in range(total_samples):
                # Update progress
                progress = ((i + 1) / total_samples) * 100
                generative_content.generation_progress = progress
                
                # Simulate sample generation
                sample = {
                    'id': f"sample_{i}",
                    'type': generation_type.value,
                    'size': 1024 + (i * 100),
                    'quality': 0.8 + (i * 0.002),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                if generative_content.generated_samples is None:
                    generative_content.generated_samples = []
                generative_content.generated_samples.append(sample)
                
                await db.commit()
                await asyncio.sleep(0.01)  # Simulate generation time
            
            # Finalize generation
            generative_content.is_generating = False
            generative_content.generation_progress = 100.0
            generative_content.volume = total_samples
            generative_content.quality = 0.95
            generative_content.diversity = 0.85
            generative_content.complexity = 0.75
            
            await db.commit()
            
            return {
                'experiment_id': experiment_id,
                'generation_type': generation_type.value,
                'total_samples': total_samples,
                'quality': generative_content.quality,
                'diversity': generative_content.diversity,
                'complexity': generative_content.complexity
            }
            
        except Exception as e:
            logger.error(f"Error generating content for experiment {experiment_id}: {e}")
            raise
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def get_experiment_metrics(experiment_id: int) -> Dict[str, Any]:
        """
        Get experiment metrics.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Dict[str, Any]: Experiment metrics
        """
        try:
            db = await get_db_session_optional()
            if not db:
                return {}
            
            query = select(Experiment).where(Experiment.id == experiment_id)
            result = await db.execute(query)
            experiment = result.scalar_one_or_none()
            
            if not experiment:
                return {}
            
            return {
                'metrics': experiment.metrics or {},
                'custom_metrics': experiment.custom_metrics or {},
                'results': experiment.results or {},
                'content_metadata': experiment.content_metadata or {}
            }
            
        except Exception as e:
            logger.error(f"Error getting experiment metrics {experiment_id}: {e}")
            return {}
        finally:
            if db:
                await db.close()
