"""
Workflow Pipelines API Endpoints

RESTful API for workflow pipeline management, execution, and monitoring.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.workflow import (
    PipelineCreate, PipelineUpdate, PipelineStepCreate, ExecuteRequest,
    PipelineResponse, ExecutionResponse, ScriptCreate, ScriptResponse,
    HelperCreate, HelperResponse, ExecutionLogsResponse,
    PipelineStatus, ExecutionStatus, LogLevel
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflow Pipelines"])

# Global workflow service instance
_workflow_service = None

def get_workflow_service() -> WorkflowService:
    """Get or create workflow service instance."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService()
    return _workflow_service


# ============================================================================
# PIPELINE ENDPOINTS
# ============================================================================

@router.post("/pipelines", response_model=PipelineResponse, status_code=201)
async def create_pipeline(
    pipeline_create: PipelineCreate,
    service: WorkflowService = Depends(get_workflow_service)
) -> PipelineResponse:
    """
    Create a new workflow pipeline.
    
    Creates a new pipeline with the specified configuration.
    """
    return await service.create_pipeline(pipeline_create)


@router.get("/pipelines", response_model=List[PipelineResponse])
async def list_pipelines(
    status: Optional[PipelineStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: WorkflowService = Depends(get_workflow_service)
) -> List[PipelineResponse]:
    """
    List all workflow pipelines.
    
    Returns a list of pipelines with optional filtering by status and category.
    """
    return await service.list_pipelines(status, category, limit, offset)


@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: str,
    service: WorkflowService = Depends(get_workflow_service)
) -> PipelineResponse:
    """
    Get a specific pipeline by ID.
    
    Returns detailed information about a single pipeline.
    """
    pipeline = await service.get_pipeline(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
    
    return pipeline


@router.put("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: str,
    pipeline_update: PipelineUpdate,
    service: WorkflowService = Depends(get_workflow_service)
) -> PipelineResponse:
    """
    Update a pipeline.
    
    Updates pipeline configuration, status, or metadata.
    """
    pipeline = await service.update_pipeline(pipeline_id, pipeline_update)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
    
    return pipeline


@router.delete("/pipelines/{pipeline_id}", status_code=204)
async def delete_pipeline(
    pipeline_id: str,
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Delete a pipeline.
    
    Permanently deletes a pipeline and all its steps.
    """
    success = await service.delete_pipeline(pipeline_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
    
    return None


# ============================================================================
# PIPELINE STEP ENDPOINTS
# ============================================================================

@router.post("/pipelines/{pipeline_id}/steps", status_code=201)
async def add_pipeline_step(
    pipeline_id: str,
    step_create: PipelineStepCreate,
    service: WorkflowService = Depends(get_workflow_service)
) -> Dict[str, Any]:
    """
    Add a step to a pipeline.
    
    Adds a new step to the pipeline workflow.
    """
    step = await service.add_step(pipeline_id, step_create)
    
    if not step:
        raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
    
    return step


@router.get("/pipelines/{pipeline_id}/steps")
async def get_pipeline_steps(
    pipeline_id: str,
    service: WorkflowService = Depends(get_workflow_service)
) -> List[Dict[str, Any]]:
    """
    Get all steps for a pipeline.
    
    Returns the complete workflow steps in execution order.
    """
    return await service.get_pipeline_steps(pipeline_id)


# ============================================================================
# EXECUTION ENDPOINTS
# ============================================================================

@router.post("/pipelines/{pipeline_id}/execute", response_model=ExecutionResponse)
async def execute_pipeline(
    pipeline_id: str,
    parameters: Dict[str, Any] = {},
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: WorkflowService = Depends(get_workflow_service)
) -> ExecutionResponse:
    """
    Execute a pipeline.
    
    Starts pipeline execution with the provided parameters.
    """
    execute_request = ExecuteRequest(
        pipeline_id=pipeline_id,
        parameters=parameters
    )
    
    try:
        return await service.execute_pipeline(execute_request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/executions", response_model=List[ExecutionResponse])
async def list_executions(
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline"),
    status: Optional[ExecutionStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: WorkflowService = Depends(get_workflow_service)
) -> List[ExecutionResponse]:
    """
    List pipeline executions.
    
    Returns execution history with optional filtering.
    """
    return await service.list_executions(pipeline_id, status, limit, offset)


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    service: WorkflowService = Depends(get_workflow_service)
) -> ExecutionResponse:
    """
    Get execution details.
    
    Returns detailed information about a specific execution.
    """
    execution = await service.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    return execution


@router.get("/executions/{execution_id}/logs", response_model=ExecutionLogsResponse)
async def get_execution_logs(
    execution_id: str,
    level: Optional[LogLevel] = Query(None, description="Filter by log level"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of logs"),
    service: WorkflowService = Depends(get_workflow_service)
) -> ExecutionLogsResponse:
    """
    Get execution logs.
    
    Returns logs generated during pipeline execution.
    """
    return await service.get_execution_logs(execution_id, level, limit)


@router.post("/executions/{execution_id}/cancel", status_code=200)
async def cancel_execution(
    execution_id: str,
    service: WorkflowService = Depends(get_workflow_service)
) -> Dict[str, Any]:
    """
    Cancel a running execution.
    
    Attempts to cancel an in-progress pipeline execution.
    """
    success = await service.cancel_execution(execution_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Execution cannot be cancelled (not found or not running)"
        )
    
    return {"message": "Execution cancelled successfully", "execution_id": execution_id}


# ============================================================================
# SCRIPT ENDPOINTS
# ============================================================================

@router.post("/scripts", response_model=ScriptResponse, status_code=201)
async def create_script(
    script_create: ScriptCreate,
    service: WorkflowService = Depends(get_workflow_service)
) -> ScriptResponse:
    """
    Create a new dynamic script.
    
    Creates a script that can be used in pipeline steps.
    """
    return await service.create_script(script_create)


@router.get("/scripts", response_model=List[ScriptResponse])
async def list_scripts(
    language: Optional[str] = Query(None, description="Filter by language"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: WorkflowService = Depends(get_workflow_service)
) -> List[ScriptResponse]:
    """
    List all dynamic scripts.
    
    Returns available scripts with optional filtering.
    """
    return await service.list_scripts(language, limit, offset)


# ============================================================================
# HELPER ENDPOINTS
# ============================================================================

@router.post("/helpers", response_model=HelperResponse, status_code=201)
async def create_helper(
    helper_create: HelperCreate,
    service: WorkflowService = Depends(get_workflow_service)
) -> HelperResponse:
    """
    Create a new helper function library.
    
    Creates a library of helper functions for use in pipelines.
    """
    return await service.create_helper(helper_create)


@router.get("/helpers", response_model=List[HelperResponse])
async def list_helpers(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: WorkflowService = Depends(get_workflow_service)
) -> List[HelperResponse]:
    """
    List all helper function libraries.
    
    Returns available helper libraries with optional filtering.
    """
    return await service.list_helpers(category, limit, offset)


# ============================================================================
# STATISTICS AND ANALYTICS
# ============================================================================

@router.get("/pipelines/{pipeline_id}/statistics")
async def get_pipeline_statistics(
    pipeline_id: str,
    service: WorkflowService = Depends(get_workflow_service)
) -> Dict[str, Any]:
    """
    Get pipeline execution statistics.
    
    Returns performance metrics and execution history.
    """
    pipeline = await service.get_pipeline(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
    
    executions = await service.list_executions(pipeline_id=pipeline_id, limit=1000)
    
    # Calculate statistics
    total_time = sum(e.execution_time_ms or 0 for e in executions)
    completed_count = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED.value)
    
    return {
        "pipeline_id": pipeline_id,
        "pipeline_name": pipeline.name,
        "total_executions": pipeline.total_executions,
        "successful_executions": pipeline.successful_executions,
        "failed_executions": pipeline.failed_executions,
        "success_rate": (
            pipeline.successful_executions / pipeline.total_executions
            if pipeline.total_executions > 0 else 0
        ),
        "avg_execution_time_ms": pipeline.avg_execution_time * 1000,
        "avg_compression_ratio": pipeline.avg_compression_ratio,
        "recent_executions": len(executions),
        "total_execution_time_ms": total_time
    }


@router.get("/statistics")
async def get_overall_statistics(
    service: WorkflowService = Depends(get_workflow_service)
) -> Dict[str, Any]:
    """
    Get overall workflow system statistics.
    
    Returns system-wide metrics and performance data.
    """
    pipelines = await service.list_pipelines(limit=10000)
    executions = await service.list_executions(limit=10000)
    scripts = await service.list_scripts(limit=10000)
    helpers = await service.list_helpers(limit=10000)
    
    return {
        "total_pipelines": len(pipelines),
        "active_pipelines": sum(1 for p in pipelines if p.status == PipelineStatus.ACTIVE.value),
        "total_scripts": len(scripts),
        "total_helpers": len(helpers),
        "total_executions": len(executions),
        "running_executions": sum(1 for e in executions if e.status == ExecutionStatus.RUNNING.value),
        "completed_executions": sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED.value),
        "failed_executions": sum(1 for e in executions if e.status == ExecutionStatus.FAILED.value),
        "success_rate": (
            sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED.value) / len(executions)
            if len(executions) > 0 else 0
        )
    }

