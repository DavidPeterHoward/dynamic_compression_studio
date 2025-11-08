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

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
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
        
        # Seed default prompts and templates
        try:
            from app.services.prompt_seed_service import get_prompt_seed_service
            from app.database.connection import AsyncSessionLocal
            
            seed_service = get_prompt_seed_service()
            async with AsyncSessionLocal() as db:
                seed_result = await seed_service.seed_all(db)
                logger.info(f"✅ Prompts/Templates seeded: {seed_result['total_seeded']} new, {seed_result['total_skipped']} existing")
                if seed_result['total_errors'] > 0:
                    logger.warning(f"⚠️ Seeding had {seed_result['total_errors']} errors")
        except Exception as e:
            logger.warning(f"⚠️ Prompt/template seeding failed (non-critical): {e}")
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

    # Initialize API Agent and register agents
    try:
        from app.agents.api.fastapi_app import api_agent
        logger.info("🚀 Initializing API Agent and registering agents...")
        bootstrap_result = await api_agent.bootstrap_and_validate()
        if bootstrap_result.success:
            logger.info(f"✅ API Agent bootstrap successful - {len(api_agent.agent_registry)} agents registered")
            for agent_id, agent in api_agent.agent_registry.items():
                agent_type = getattr(agent, 'agent_type', 'unknown')
                logger.info(f"  ✓ Agent {agent_id}: {agent_type}")
        else:
            logger.warning(f"⚠️ API Agent bootstrap had issues: {bootstrap_result.errors}")
            logger.warning(f"   Registered agents: {len(api_agent.agent_registry)}")
    except Exception as e:
        logger.error(f"❌ API Agent initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

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
# Define key agent endpoints directly in main app
from app.agents.api.api_agent import APIAgent
from app.agents.api.fastapi_app import app as agents_api_app

# Initialize API agent
api_agent = APIAgent()

# Mount the agents API app
app.mount("/api/v1", agents_api_app)

@app.get("/agents")
async def list_agents():
    """List all registered agents."""
    try:
        agents = await api_agent.get_registered_agents()
        return {"agents": agents, "count": len(agents)}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoints must be defined directly on the main app
# Copy WebSocket endpoints from api_agent_app to main app
from app.agents.api.fastapi_app import websocket_clients

@app.websocket("/ws/agent-updates")
async def websocket_agent_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates."""
    client_id = f"ws_{int(datetime.now().timestamp())}_{id(websocket)}"
    websocket_clients[client_id] = websocket

    logger.info(f"WebSocket client connected: {client_id}")

    try:
        # Send initial system status
        from app.agents.api.fastapi_app import api_agent
        system_status = await api_agent.get_system_status()
        await websocket.send_json({
            "event_type": "system_status",
            "data": system_status
        })

        # Keep connection alive and listen for messages
        while True:
            try:
                # Receive message from client (if any) - timeout after 30 seconds
                try:
                    data = await websocket.receive_text()
                    # Process client messages if needed
                    logger.debug(f"Received WebSocket message from {client_id}: {data}")
                except Exception:
                    # No message received, send periodic updates
                    pass

                # Send periodic status updates (every 30 seconds)
                await asyncio.sleep(30)
                current_status = await api_agent.get_system_status()
                await websocket.send_json({
                    "event_type": "status_update",
                    "data": current_status
                })

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket message handling error for {client_id}: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        # Clean up WebSocket client
        if client_id in websocket_clients:
            del websocket_clients[client_id]
            logger.debug(f"Cleaned up WebSocket client {client_id}")

@app.websocket("/ws/debate-updates")
async def websocket_debate_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time debate updates."""
    await websocket.accept()

    try:
        while True:
            try:
                # Keep connection alive for debate updates
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat"})
    except Exception as e:
        logger.error(f"Debate WebSocket error: {e}")

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
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level="info"
    )






