"""
API module for the Dynamic Compression Algorithms backend.

This module provides REST API endpoints for compression operations,
file management, metrics, and health monitoring.
"""

from fastapi import APIRouter
from . import compression, files, metrics, health, evaluation, sensors, enhanced_compression, synthetic_media_management, prompts, live_metrics, algorithm_viability, workflow_pipelines, compression_validation
from .v1.endpoints import synthetic_media

# Create main API router
api_router = APIRouter()

# Include all API modules
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(compression.router, prefix="/compression", tags=["Compression"])
api_router.include_router(enhanced_compression.router, prefix="/compression/enhanced", tags=["Enhanced Compression"])
api_router.include_router(algorithm_viability.router, prefix="/compression", tags=["Algorithm Viability"])
api_router.include_router(compression_validation.router, prefix="/compression", tags=["Compression Validation"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(live_metrics.router, prefix="/live-metrics", tags=["Live Metrics"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["Evaluation"])
api_router.include_router(sensors.router, tags=["Sensors"])
api_router.include_router(synthetic_media.router, tags=["Synthetic Media"])
api_router.include_router(synthetic_media_management.router, tags=["Synthetic Media Management"])
api_router.include_router(prompts.router, tags=["Prompts"])
api_router.include_router(workflow_pipelines.router, tags=["Workflow Pipelines"])

__all__ = ["api_router", "compression", "files", "metrics", "health", "evaluation", "workflow_pipelines", "compression_validation"]






