"""
Main FastAPI application for the Dynamic Compression Algorithms backend.

This is the entry point for the FastAPI application that provides
the REST API for compression operations, file management, and metrics.
"""

import os
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import init_db, close_db, check_db_connection
from app.api import compression, files, metrics, health, evaluation, synthetic_media_management, live_metrics, algorithm_docs
from app.api.v1.endpoints import synthetic_media, uploads
from app.agents.api.fastapi_app import app as api_agent_app
# Import all models to ensure they are registered with SQLAlchemy
from app.models import *
# TODO: Fix async compatibility for meta_learning, experiments
from app.core.compression_engine import CompressionEngine

# Simplified logging setup
import logging

def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Setup basic logging
    logger = setup_logging()
    logger.info("🚀 Starting Dynamic Compression Algorithms Backend...")

    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # Initialize compression engine
    try:
        compression_engine = CompressionEngine()
        app.state.compression_engine = compression_engine
        logger.info("✅ Compression engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Compression engine initialization failed: {e}")
        raise

    logger.info("🎉 Backend startup completed successfully")
    yield

    # Cleanup
    logger.info("🔄 Shutting down backend...")
    await close_db()
    logger.info("✅ Backend shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="Dynamic Compression Algorithms API",
    description="Advanced compression algorithms with AI-powered optimization",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins_list,
    allow_credentials=True,
    allow_methods=settings.api.cors_methods_list,
    allow_headers=settings.api.cors_headers_list,
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Include API routers
app.include_router(compression.router, prefix="/api/v1/compression", tags=["Compression"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(live_metrics.router, prefix="/api/v1/live-metrics", tags=["Live Metrics"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(synthetic_media.router, prefix="/api/v1", tags=["Synthetic Media"])
app.include_router(synthetic_media_management.router, tags=["Synthetic Media Management"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"])
app.include_router(algorithm_docs.router, tags=["Algorithm Documentation"])

# New Meta-Learning & Experiments routers
# TODO: Fix async database session compatibility
# app.include_router(meta_learning.router, prefix="/api/v1/meta-learning", tags=["Meta-Learning"])
# app.include_router(experiments.router, prefix="/api/v1/experiments", tags=["Experiments"])
app.include_router(uploads.router, prefix="/api/v1/upload", tags=["Uploads"])

# Include Agent API Layer (Agent 04)
app.include_router(api_agent_app.router, prefix="", tags=["Agent API"])

# Mount static files for media serving
# In Docker, media is at /app/media
MEDIA_DIR = "/app/media"
if not os.path.exists(MEDIA_DIR):
    MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")
    os.makedirs(MEDIA_DIR, exist_ok=True)

# Ensure subdirectories exist
for subdir in ["videos", "images", "audio", "thumbnails", "uploads"]:
    os.makedirs(os.path.join(MEDIA_DIR, subdir), exist_ok=True)

app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dynamic Compression Algorithms API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "compression": "/api/v1/compression",
            "files": "/api/v1/files",
            "metrics": "/api/v1/metrics",
            "health": "/api/v1/health",
            "synthetic-media": "/api/v1/synthetic-media",
            "evaluation": "/api/v1/evaluation",
            "docs": "/docs"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    try:
        # Check database connection
        db_status = await check_db_connection()
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": "connected" if db_status else "disconnected",
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )






