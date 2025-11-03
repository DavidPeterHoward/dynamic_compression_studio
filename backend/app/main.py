"""
Main FastAPI application for the Dynamic Compression Algorithms backend.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .database.connection import init_db, close_db, check_db_health
from .api import api_router
from .services import (
    AlgorithmService, ExperimentService, ContentAnalysisService,
    SensorService, MetricsService
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.api.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background tasks
background_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Dynamic Compression Algorithms API...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        
        # Check database health
        health_status = await check_db_health()
        logger.info(f"Database health: {health_status['status']}")
        
        # Start background services
        logger.info("Starting background services...")
        
        # Start metrics collection
        metrics_task = asyncio.create_task(
            MetricsService.start_metrics_collection(interval_seconds=60)
        )
        background_tasks.append(metrics_task)
        
        # Start sensor monitoring
        sensor_task = asyncio.create_task(
            SensorService.start_sensor_monitoring(interval_seconds=60)
        )
        background_tasks.append(sensor_task)
        
        logger.info("Background services started successfully")
        logger.info("Dynamic Compression Algorithms API started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Dynamic Compression Algorithms API...")
    
    try:
        # Cancel background tasks
        for task in background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if background_tasks:
            await asyncio.gather(*background_tasks, return_exceptions=True)
        
        # Close database connections
        await close_db()
        
        logger.info("Dynamic Compression Algorithms API shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.api.title,
    description=settings.api.description,
    version=settings.api.version,
    debug=settings.api.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static file directories for media serving
MEDIA_DIR = Path("/app/media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Ensure subdirectories exist
for subdir in ['videos', 'images', 'audio', 'thumbnails']:
    (MEDIA_DIR / subdir).mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
logger.info(f"Media files mounted at /media from {MEDIA_DIR}")


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: API information
    """
    return {
        "message": "Dynamic Compression Algorithms API",
        "version": settings.api.version,
        "status": "running",
        "documentation": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    try:
        # Check database health
        db_health = await check_db_health()
        
        # Check background tasks
        tasks_health = {
            "metrics_collection": any(
                not task.done() for task in background_tasks 
                if "metrics" in str(task)
            ),
            "sensor_monitoring": any(
                not task.done() for task in background_tasks 
                if "sensor" in str(task)
            )
        }
        
        overall_status = "healthy"
        if db_health["status"] != "healthy":
            overall_status = "unhealthy"
        elif not all(tasks_health.values()):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": "2024-01-01T00:00:00Z",  # Would be actual timestamp
            "database": db_health,
            "background_tasks": tasks_health,
            "version": settings.api.version
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.api.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.api.debug,
        log_level="info" if not settings.api.debug else "debug"
    )
