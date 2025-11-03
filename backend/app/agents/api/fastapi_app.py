"""
FastAPI Application for Agent API Layer

Provides REST endpoints and WebSocket support for all agent operations.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .api_agent import APIAgent

logger = logging.getLogger(__name__)

# Pydantic models for request validation
class TaskRequest(BaseModel):
    """Task execution request model."""
    task_id: Optional[str] = Field(None, description="Unique task identifier")
    operation: str = Field(..., description="Operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    priority: Optional[str] = Field("normal", description="Task priority", regex="^(low|normal|high|urgent)$")
    timeout_seconds: Optional[int] = Field(None, description="Task timeout in seconds", ge=1, le=3600)

class AgentStatusResponse(BaseModel):
    """Agent status response model."""
    agent_id: str
    agent_type: str
    status: str
    capabilities: List[str]
    task_count: int
    success_count: int
    error_count: int
    success_rate: float
    avg_task_duration: Optional[float]
    created_at: str
    last_active_at: Optional[str]

class SystemStatusResponse(BaseModel):
    """System status response model."""
    system_status: str
    timestamp: str
    agents: Dict[str, Dict[str, Any]]
    api_metrics: Dict[str, int]

class TaskResult(BaseModel):
    """Task execution result model."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_used: Optional[str] = None
    timestamp: str
    execution_time_seconds: Optional[float] = None

# Create FastAPI app
app = FastAPI(
    title="Meta-Recursive Multi-Agent API",
    description="REST API and WebSocket interface for agent orchestration",
    version="1.0.0"
)

# CORS middleware (will be secured in Phase 2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Secure in Phase 2
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API agent instance
api_agent = APIAgent()

# Connected WebSocket clients
websocket_clients: Dict[str, WebSocket] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize API agent on startup."""
    logger.info("Starting Meta-Recursive Multi-Agent API")

    # Bootstrap the API agent
    bootstrap_result = await api_agent.bootstrap_and_validate()
    if bootstrap_result.success:
        logger.info(f"✅ API Agent bootstrap successful - {len(api_agent.agent_registry)} agents registered")
    else:
        logger.error(f"❌ API Agent bootstrap failed: {bootstrap_result.errors}")

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Meta-Recursive Multi-Agent API",
        "version": "1.0.0",
        "agents": list(api_agent.agent_registry.keys()),
        "endpoints": [
            "/agents/{agent_id}/status",
            "/agents/{agent_id}/execute",
            "/agents/{agent_id}/health",
            "/ws/agent-updates",
            "/system/status"
        ],
        "websocket_url": "ws://localhost:8000/ws/agent-updates"
    }

@app.get("/agents")
async def list_agents():
    """List all registered agents."""
    return {
        "agents": [
            {
                "id": agent_id,
                "type": agent.agent_type if hasattr(agent, 'agent_type') else 'unknown',
                "capabilities": [cap.value for cap in agent.capabilities] if hasattr(agent, 'capabilities') else []
            }
            for agent_id, agent in api_agent.agent_registry.items()
        ]
    }

@app.get("/agents/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    """Get status of specific agent."""
    result = await api_agent.handle_api_request(agent_id, "status", "GET", {})

    if result.get("status") != 200:
        raise HTTPException(status_code=result["status"], detail=result.get("error", "API Error"))

    return AgentStatusResponse(**result["data"])

@app.post("/agents/{agent_id}/execute", response_model=TaskResult)
async def execute_agent_task(agent_id: str, task: TaskRequest):
    """Execute task on specific agent."""
    start_time = datetime.now()

    # Convert Pydantic model to dict for API agent
    task_dict = task.dict()

    result = await api_agent.handle_api_request(agent_id, "execute", "POST", task_dict)

    execution_time = (datetime.now() - start_time).total_seconds()

    if result.get("status") != 200:
        raise HTTPException(status_code=result["status"], detail=result.get("error", "API Error"))

    # Broadcast task completion to WebSocket clients
    await api_agent.broadcast_websocket_update("task_completed", {
        "agent_id": agent_id,
        "task": task_dict,
        "result": result["data"],
        "execution_time_seconds": execution_time
    })

    # Add execution time to response
    response_data = result["data"]
    if isinstance(response_data, dict):
        response_data["execution_time_seconds"] = execution_time

    return TaskResult(**response_data)

@app.get("/agents/{agent_id}/health")
async def get_agent_health(agent_id: str):
    """Get health status of specific agent."""
    result = await api_agent.handle_api_request(agent_id, "health", "GET", {})

    if result.get("status") != 200:
        raise HTTPException(status_code=result["status"], detail=result.get("error", "API Error"))

    return result["data"]

@app.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get overall system status."""
    return await api_agent.get_system_status()

@app.websocket("/ws/agent-updates")
async def websocket_agent_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates."""
    await websocket.accept()

    # Generate client ID
    client_id = f"ws_{int(datetime.now().timestamp())}_{id(websocket)}"
    websocket_clients[client_id] = websocket

    logger.info(f"WebSocket client connected: {client_id}")

    try:
        # Send initial system status
        system_status = await get_system_status()
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
                current_status = await get_system_status()
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
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        # Clean up
        if client_id in websocket_clients:
            del websocket_clients[client_id]

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Meta-Recursive Multi-Agent API")

    # Close all WebSocket connections
    for client_id, websocket in websocket_clients.items():
        try:
            await websocket.close()
        except Exception:
            pass

    websocket_clients.clear()
