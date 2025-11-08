"""
FastAPI Application for Agent API Layer

Provides REST endpoints and WebSocket support for all agent operations.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
import time
from contextlib import asynccontextmanager

from .api_agent import APIAgent
from .debate_api import debate_orchestrator, DebateConfiguration, DebateMode
from .ollama_api import ollama_api

logger = logging.getLogger(__name__)

# Global WebSocket client registry
websocket_clients: Dict[str, WebSocket] = {}

# Global API metrics
api_requests = 0
api_request_times = []
performance_metrics = {
    "total_requests": 0,
    "avg_response_time": 0.0,
    "error_count": 0,
    "uptime_seconds": 0,
    "peak_concurrent_connections": 0,
    "current_connections": 0
}
start_time = time.time()

# Performance monitoring middleware
class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to collect performance metrics."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Track concurrent connections
        performance_metrics["current_connections"] += 1
        performance_metrics["peak_concurrent_connections"] = max(
            performance_metrics["peak_concurrent_connections"],
            performance_metrics["current_connections"]
        )

        try:
            response = await call_next(request)

            # Record request metrics
            duration = time.time() - start_time
            api_request_times.append(duration)
            performance_metrics["total_requests"] += 1

            # Keep only last 1000 request times for memory efficiency
            if len(api_request_times) > 1000:
                api_request_times.pop(0)

            # Update average response time
            if api_request_times:
                performance_metrics["avg_response_time"] = sum(api_request_times) / len(api_request_times)

            # Add performance headers
            response.headers["X-Response-Time"] = ".2f"

            return response

        except Exception as e:
            performance_metrics["error_count"] += 1
            raise
        finally:
            performance_metrics["current_connections"] -= 1

# Pydantic models for request validation
class TaskRequest(BaseModel):
    """Task execution request model."""
    task_id: Optional[str] = Field(None, description="Unique task identifier")
    operation: str = Field(..., description="Operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    priority: Optional[str] = Field("normal", description="Task priority", pattern="^(low|normal|high|urgent)$")
    timeout_seconds: Optional[int] = Field(None, description="Task timeout in seconds", ge=1, le=3600)

class DebateConfigurationRequest(BaseModel):
    """Debate configuration request model."""
    debate_topic: str = Field(..., description="The main debate topic")
    problem_statement: str = Field(..., description="Detailed problem statement and context")
    debate_mode: str = Field("autonomous", description="Debate mode", pattern="^(structured|freeform|autonomous)$")
    max_rounds: int = Field(5, description="Maximum number of debate rounds", ge=1, le=20)
    max_iterations_per_round: int = Field(3, description="Maximum iterations per round", ge=1, le=10)
    consensus_threshold: float = Field(0.8, description="Consensus threshold (0.0-1.0)", ge=0.0, le=1.0)
    time_limit_per_argument: int = Field(60, description="Time limit per argument in seconds", ge=10, le=300)
    selected_agents: List[str] = Field(..., description="List of selected agent IDs")
    debate_rules: Dict[str, Any] = Field(default_factory=dict, description="Debate rules configuration")

class DebateControlRequest(BaseModel):
    """Debate control request model."""
    action: str = Field(..., description="Control action", pattern="^(start|pause|resume|stop)$")

class OllamaChatRequest(BaseModel):
    """Ollama chat request model."""
    model: str = Field(..., description="Ollama model name")
    message: str = Field(..., description="User message")
    agent_id: Optional[str] = Field(None, description="Associated agent ID")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(None, description="Recent conversation history")
    temperature: Optional[float] = Field(0.7, description="Response temperature", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(2048, description="Maximum response tokens", ge=1, le=8192)

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

# Performance monitoring middleware
app.add_middleware(PerformanceMonitoringMiddleware)

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
            "/system/status",
            # Ollama endpoints
            "/ollama/models",
            "/ollama/chat",
            "/ollama/models/{model_name}",
            "/ollama/health",
            # Debate endpoints
            "/debate/initialize",
            "/debate/{session_id}/control",
            "/debate/{session_id}/status",
            "/debate/sessions",
            "/ws/debate-updates"
        ],
        "websocket_urls": {
            "agent_updates": "ws://localhost:8000/ws/agent-updates",
            "debate_updates": "ws://localhost:8000/ws/debate-updates"
        }
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

@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get status of specific agent with graceful fallback."""
    try:
        result = await api_agent.handle_api_request(agent_id, "status", "GET", {})
        if result.get("status") == 200 and isinstance(result.get("data"), dict):
            data = result["data"]
        else:
            raise Exception(result.get("error", "Status not available"))
    except Exception as _:
        # Graceful minimal status payload
        data = {
            "agent_id": agent_id,
            "agent_type": "unknown",
            "status": "unknown",
            "capabilities": [],
            "task_count": 0,
            "success_count": 0,
            "error_count": 0,
            "success_rate": 0.0,
            "avg_task_duration": None,
            "created_at": datetime.now().isoformat(),
            "last_active_at": None,
        }

    return JSONResponse(status_code=200, content=data)

@app.post("/agents/{agent_id}/execute")
async def execute_agent_task(agent_id: str, task: TaskRequest):
    """Execute task on specific agent."""
    start_time = datetime.now()

    # Convert Pydantic model to dict for API agent
    task_dict = task.dict()

    try:
        result = await api_agent.handle_api_request(agent_id, "execute", "POST", task_dict)
    except Exception as exec_err:
        result = {
            "status": 200,
            "data": {
                "task_id": task_dict.get("task_id", f"api_task_err_{int(start_time.timestamp())}"),
                "status": "failed",
                "error": str(exec_err),
                "timestamp": datetime.now().isoformat()
            }
        }

    execution_time = (datetime.now() - start_time).total_seconds()

    if result.get("status") != 200:
        # Return graceful failed response instead of HTTP error
        failed_payload = {
            "task_id": task_dict.get("task_id", f"api_task_fail_{int(start_time.timestamp())}"),
            "status": "failed",
            "error": result.get("error", "API Error"),
            "timestamp": datetime.now().isoformat(),
        }
        return JSONResponse(status_code=200, content=failed_payload)

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

    # Ensure minimal required fields for response
    if not isinstance(response_data, dict):
        response_data = {}
    response_data.setdefault("task_id", task_dict.get("task_id", f"api_task_{int(start_time.timestamp())}"))
    response_data.setdefault("status", "completed")
    response_data.setdefault("timestamp", datetime.now().isoformat())

    return JSONResponse(status_code=200, content=response_data)

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

# Ollama API Endpoints

@app.get("/ollama/models")
async def get_ollama_models():
    """Get available Ollama models."""
    try:
        return await ollama_api.get_models()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Ollama models: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Failed to get Ollama models: {str(e)}"
        })

@app.post("/ollama/chat")
async def chat_with_ollama(chat_request: OllamaChatRequest):
    """Chat with Ollama model using streaming response."""
    try:
        return await ollama_api.chat_with_streaming(
            model=chat_request.model,
            message=chat_request.message,
            agent_id=chat_request.agent_id,
            conversation_history=chat_request.conversation_history,
            temperature=chat_request.temperature or 0.7,
            max_tokens=chat_request.max_tokens or 2048
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Ollama chat: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Ollama chat failed: {str(e)}"
        })

@app.get("/ollama/models/{model_name}")
async def get_ollama_model_info(model_name: str):
    """Get information about a specific Ollama model."""
    try:
        return await ollama_api.get_model_info(model_name)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Ollama model info: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Failed to get model info: {str(e)}"
        })

@app.get("/ollama/health")
async def check_ollama_health():
    """Check Ollama service health."""
    try:
        return await ollama_api.health_check()
    except Exception as e:
        logger.error(f"Error checking Ollama health: {e}")
        return JSONResponse(status_code=500, content={
            "health": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.get("/metrics")
async def get_performance_metrics():
    """Get system performance metrics."""
    # Update uptime
    performance_metrics["uptime_seconds"] = time.time() - start_time

    return {
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": performance_metrics["uptime_seconds"],
        "api_metrics": {
            "total_requests": performance_metrics["total_requests"],
            "avg_response_time": round(performance_metrics["avg_response_time"], 3),
            "error_count": performance_metrics["error_count"],
            "error_rate": round(performance_metrics["error_count"] / max(performance_metrics["total_requests"], 1), 3)
        },
        "connections": {
            "current": performance_metrics["current_connections"],
            "peak": performance_metrics["peak_concurrent_connections"],
            "websocket_clients": len(websocket_clients)
        },
        "system_health": {
            "status": "healthy" if performance_metrics["error_rate"] < 0.05 else "warning",
            "response_time_status": "good" if performance_metrics["avg_response_time"] < 1.0 else "slow"
        }
    }

# Debate System Endpoints

@app.post("/debate/initialize")
async def initialize_debate(debate_config: DebateConfigurationRequest):
    """Initialize a new debate session."""
    try:
        config = DebateConfiguration(
            debate_topic=debate_config.debate_topic,
            problem_statement=debate_config.problem_statement,
            debate_mode=DebateMode(debate_config.debate_mode),
            max_rounds=debate_config.max_rounds,
            max_iterations_per_round=debate_config.max_iterations_per_round,
            consensus_threshold=debate_config.consensus_threshold,
            time_limit_per_argument=debate_config.time_limit_per_argument,
            selected_agents=debate_config.selected_agents,
            debate_rules=debate_config.debate_rules
        )

        session = await debate_orchestrator.initialize_debate(config)

        return JSONResponse(status_code=200, content={
            "session": debate_orchestrator._session_to_dict(session),
            "message": "Debate session initialized successfully"
        })
    except Exception as e:
        logger.error(f"Error initializing debate: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Failed to initialize debate: {str(e)}"
        })

@app.post("/debate/{session_id}/control")
async def control_debate(session_id: str, control: DebateControlRequest):
    """Control a debate session (start, pause, resume, stop)."""
    try:
        success = await debate_orchestrator.control_debate(session_id, control.action)

        if not success:
            return JSONResponse(status_code=404, content={
                "error": f"Debate session {session_id} not found"
            })

        # Get updated session
        session = debate_orchestrator.active_sessions.get(session_id)
        if session:
            return JSONResponse(status_code=200, content={
                "session": debate_orchestrator._session_to_dict(session),
                "message": f"Debate {control.action}ed successfully"
            })
        else:
            return JSONResponse(status_code=404, content={
                "error": f"Debate session {session_id} not found"
            })
    except Exception as e:
        logger.error(f"Error controlling debate {session_id}: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Failed to control debate: {str(e)}"
        })

@app.get("/debate/{session_id}/status")
async def get_debate_status(session_id: str):
    """Get status of a specific debate session."""
    try:
        session = debate_orchestrator.active_sessions.get(session_id)
        if not session:
            return JSONResponse(status_code=404, content={
                "error": f"Debate session {session_id} not found"
            })

        return JSONResponse(status_code=200, content={
            "session": debate_orchestrator._session_to_dict(session)
        })
    except Exception as e:
        logger.error(f"Error getting debate status {session_id}: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Failed to get debate status: {str(e)}"
        })

@app.get("/debate/sessions")
async def list_debate_sessions():
    """List all active debate sessions."""
    try:
        sessions = []
        for session_id, session in debate_orchestrator.active_sessions.items():
            sessions.append(debate_orchestrator._session_to_dict(session))

        return JSONResponse(status_code=200, content={
            "sessions": sessions,
            "total": len(sessions)
        })
    except Exception as e:
        logger.error(f"Error listing debate sessions: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Failed to list debate sessions: {str(e)}"
        })

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
        system_status = await APIAgent.get_system_status()
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
                current_status = await APIAgent.get_system_status()
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

@app.websocket("/ws/debate-updates")
async def websocket_debate_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time debate updates."""
    await websocket.accept()

    # Generate client ID
    client_id = f"debate_ws_{int(datetime.now().timestamp())}_{id(websocket)}"

    # Register client with debate orchestrator
    debate_orchestrator.websocket_clients[client_id] = websocket

    logger.info(f"Debate WebSocket client connected: {client_id}")

    try:
        # Keep connection alive and listen for messages
        while True:
            try:
                # Receive message from client (if any) - timeout after 30 seconds
                try:
                    data = await websocket.receive_text()
                    # Process client messages if needed
                    logger.debug(f"Received debate WebSocket message from {client_id}: {data}")
                except Exception:
                    # No message received, connection is alive
                    pass

                # Send periodic ping to keep connection alive
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Debate WebSocket message handling error for {client_id}: {e}")
                break

    except Exception as e:
        logger.error(f"Debate WebSocket error for {client_id}: {e}")
    finally:
        # Clean up
        if client_id in debate_orchestrator.websocket_clients:
            del debate_orchestrator.websocket_clients[client_id]
