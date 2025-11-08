# Backend API Layer Implementation

## Overview

This document details the FastAPI backend implementation for the core MVP multi-agent system. The API layer provides REST endpoints and WebSocket support for agent management, task execution, debate orchestration, and Ollama integration.

**Note:** Advanced features like authentication, circuit breakers, and enterprise monitoring are documented separately in the [`advanced/`](../advanced/) folder.

## FastAPI Application Setup

**File: `backend/app/agents/api/fastapi_app.py`**

```python
"""
FastAPI Application for Agent API Layer

Provides REST endpoints and WebSocket support for all agent operations.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
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

# FastAPI application
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

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler for unhandled errors."""
    error_details = {
        "error": str(exc),
        "type": type(exc).__name__,
        "timestamp": datetime.now().isoformat(),
        "endpoint": f"{request.method} {request.url.path}"
    }

    logger.error("Unhandled exception", **error_details)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": error_details["timestamp"]
        }
    )
```

## Pydantic Models for MVP

**File: `backend/app/agents/api/fastapi_app.py`**

```python
# Pydantic models for request validation
class TaskRequest(BaseModel):
    """Task execution request model."""
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
```

## Core API Endpoints

### Agent Management Endpoints

```python
@app.get("/agents")
async def list_agents():
    """List all registered agents with their status."""
    try:
        agents = await APIAgent.list_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agents")

@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get detailed status for a specific agent."""
    try:
        status = await APIAgent.get_agent_status(agent_id)
        if not status:
            raise HTTPException(status_code=404, detail="Agent not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent status")

@app.post("/agents/{agent_id}/execute")
async def execute_task(agent_id: str, request: TaskRequest):
    """Execute a task on the specified agent."""
    try:
        result = await APIAgent.execute_task(agent_id, request.operation, request.parameters)
        return result
    except Exception as e:
        logger.error(f"Failed to execute task: {e}")
        raise HTTPException(status_code=500, detail="Task execution failed")
```

### Task Management Endpoints

```python
@app.get("/tasks")
async def list_tasks(status: Optional[str] = None, limit: int = 50):
    """List tasks with optional status filtering."""
    try:
        tasks = await APIAgent.list_tasks(status=status, limit=limit)
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status and details for a specific task."""
    try:
        task = await APIAgent.get_task_status(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task status")
```

### Ollama Chat Endpoints

```python
@app.post("/ollama/chat")
async def chat_with_ollama(request: OllamaChatRequest):
    """Send a chat message to Ollama models."""
    try:
        response = await ollama_api.chat_with_streaming(
            model=request.model,
            message=request.message,
            agent_id=request.agent_id,
            conversation_history=request.conversation_history,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response
    except Exception as e:
        logger.error(f"Failed to chat with Ollama: {e}")
        raise HTTPException(status_code=500, detail="Chat service unavailable")

@app.get("/ollama/models")
async def get_ollama_models():
    """Get list of available Ollama models."""
    try:
        models = await ollama_api.get_models()
        return models
    except Exception as e:
        logger.error(f"Failed to get Ollama models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")
```

### Debate System Endpoints

```python
@app.post("/debate/initialize")
async def initialize_debate(request: DebateConfigurationRequest):
    """Initialize a new multi-agent debate session."""
    try:
        debate = await debate_orchestrator.initialize_debate(
            topic=request.debate_topic,
            problem_statement=request.problem_statement,
            debate_mode=request.debate_mode,
            max_rounds=request.max_rounds,
            max_iterations_per_round=request.max_iterations_per_round,
            consensus_threshold=request.consensus_threshold,
            time_limit_per_argument=request.time_limit_per_argument,
            selected_agents=request.selected_agents,
            debate_rules=request.debate_rules
        )
        return {"debate_id": debate.id, "status": "initialized"}
    except Exception as e:
        logger.error(f"Failed to initialize debate: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize debate")

@app.post("/debate/{debate_id}/control")
async def control_debate(debate_id: str, request: DebateControlRequest):
    """Control debate execution (start, pause, resume, stop)."""
    try:
        result = await debate_orchestrator.control_debate(debate_id, request.action)
        return result
    except Exception as e:
        logger.error(f"Failed to control debate: {e}")
        raise HTTPException(status_code=500, detail="Failed to control debate")

@app.get("/debates/{debate_id}")
async def get_debate_status(debate_id: str):
    """Get status and details for a specific debate."""
    try:
        debate = await debate_orchestrator.get_debate_status(debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        return debate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get debate status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve debate status")
```

### System Status Endpoints

```python
@app.get("/system/status")
async def get_system_status():
    """Get overall system status and metrics."""
    try:
        status = await APIAgent.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system status")

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

## WebSocket Endpoints

```python
@app.websocket("/ws/agent-updates")
async def websocket_agent_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates."""
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
```

This MVP API layer provides all the core functionality needed for the multi-agent system without advanced features like authentication, circuit breakers, or comprehensive monitoring. Advanced features are documented separately in the `advanced/` folder.