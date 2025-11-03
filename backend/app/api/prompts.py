"""
API endpoints for prompt management, storage, and evaluation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
import uuid
import json

from app.database import get_db_session
from app.models.prompts import (
    Prompt, PromptTemplate, PromptWorkflow, PromptEvaluation, 
    PromptWorkflowExecution, PromptChain, PromptSemanticAnalysis,
    PromptUsage, PromptOptimization, PromptType, PromptCategory,
    EvaluationStatus
)
from app.schemas.prompts import (
    PromptCreate, PromptUpdate, PromptResponse, PromptListResponse,
    PromptTemplateCreate, PromptTemplateResponse,
    PromptWorkflowCreate, PromptWorkflowResponse,
    PromptEvaluationCreate, PromptEvaluationResponse,
    PromptSemanticAnalysisRequest, PromptSemanticAnalysisResponse,
    PromptOptimizationRequest, PromptOptimizationResponse,
    PromptSearchRequest, PromptSearchResponse,
    PromptWorkflowExecutionRequest, PromptWorkflowExecutionResponse
)

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])


@router.post("/", response_model=PromptResponse)
async def create_prompt(
    prompt_data: PromptCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new prompt."""
    try:
        prompt = Prompt(
            name=prompt_data.name,
            description=prompt_data.description,
            content=prompt_data.content,
            prompt_type=prompt_data.prompt_type,
            category=prompt_data.category,
            tags=prompt_data.tags,
            keywords=prompt_data.keywords,
            is_template=prompt_data.is_template,
            parent_id=prompt_data.parent_id
        )
        
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        return PromptResponse.from_orm(prompt)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PromptListResponse)
async def list_prompts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    prompt_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db_session)
):
    """List prompts with filtering and pagination."""
    try:
        query = db.query(Prompt)
        
        # Apply filters
        if category:
            query = query.filter(Prompt.category == category)
        if prompt_type:
            query = query.filter(Prompt.prompt_type == prompt_type)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            query = query.filter(Prompt.tags.contains(tag_list))
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Prompt.name.ilike(search_term),
                    Prompt.description.ilike(search_term),
                    Prompt.content.ilike(search_term)
                )
            )
        
        # Apply sorting
        if sort_by == "name":
            sort_column = Prompt.name
        elif sort_by == "created_at":
            sort_column = Prompt.created_at
        elif sort_by == "usage_count":
            sort_column = Prompt.usage_count
        elif sort_by == "success_rate":
            sort_column = Prompt.success_rate
        else:
            sort_column = Prompt.created_at
            
        if sort_order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Apply pagination
        total = query.count()
        prompts = query.offset(skip).limit(limit).all()
        
        return PromptListResponse(
            prompts=[PromptResponse.from_orm(p) for p in prompts],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    db: Session = Depends(get_db_session)
):
    """Get a specific prompt by ID."""
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return PromptResponse.from_orm(prompt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    prompt_data: PromptUpdate,
    db: Session = Depends(get_db_session)
):
    """Update a prompt."""
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Update fields
        for field, value in prompt_data.dict(exclude_unset=True).items():
            setattr(prompt, field, value)
        
        db.commit()
        db.refresh(prompt)
        
        return PromptResponse.from_orm(prompt)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    db: Session = Depends(get_db_session)
):
    """Delete a prompt."""
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        db.delete(prompt)
        db.commit()
        
        return {"message": "Prompt deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=PromptSearchResponse)
async def search_prompts(
    search_request: PromptSearchRequest,
    db: Session = Depends(get_db_session)
):
    """Advanced semantic search for prompts."""
    try:
        query = db.query(Prompt)
        
        # Text search
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.filter(
                or_(
                    Prompt.name.ilike(search_term),
                    Prompt.description.ilike(search_term),
                    Prompt.content.ilike(search_term)
                )
            )
        
        # Category filter
        if search_request.categories:
            query = query.filter(Prompt.category.in_(search_request.categories))
        
        # Type filter
        if search_request.prompt_types:
            query = query.filter(Prompt.prompt_type.in_(search_request.prompt_types))
        
        # Tag filter
        if search_request.tags:
            query = query.filter(Prompt.tags.contains(search_request.tags))
        
        # Semantic search (if vector is provided)
        if search_request.semantic_vector:
            # This would require vector similarity search implementation
            # For now, we'll use keyword matching
            pass
        
        # Apply sorting
        if search_request.sort_by == "relevance":
            # Implement relevance scoring
            pass
        elif search_request.sort_by == "usage":
            query = query.order_by(desc(Prompt.usage_count))
        elif search_request.sort_by == "success_rate":
            query = query.order_by(desc(Prompt.success_rate))
        else:
            query = query.order_by(desc(Prompt.created_at))
        
        # Apply pagination
        total = query.count()
        prompts = query.offset(search_request.skip).limit(search_request.limit).all()
        
        return PromptSearchResponse(
            prompts=[PromptResponse.from_orm(p) for p in prompts],
            total=total,
            skip=search_request.skip,
            limit=search_request.limit,
            search_metadata={
                "query": search_request.query,
                "filters_applied": {
                    "categories": search_request.categories,
                    "types": search_request.prompt_types,
                    "tags": search_request.tags
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{prompt_id}/evaluate", response_model=PromptEvaluationResponse)
async def evaluate_prompt(
    prompt_id: str,
    evaluation_data: PromptEvaluationCreate,
    db: Session = Depends(get_db_session)
):
    """Evaluate a prompt with a specific model."""
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Create evaluation record
        evaluation = PromptEvaluation(
            prompt_id=prompt_id,
            model_name=evaluation_data.model_name,
            model_version=evaluation_data.model_version,
            evaluation_type=evaluation_data.evaluation_type,
            test_cases=evaluation_data.test_cases,
            evaluator=evaluation_data.evaluator
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # TODO: Implement actual evaluation logic
        # This would involve calling the LLM API and measuring performance
        
        return PromptEvaluationResponse.from_orm(evaluation)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_id}/evaluations", response_model=List[PromptEvaluationResponse])
async def get_prompt_evaluations(
    prompt_id: str,
    model_name: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """Get all evaluations for a prompt."""
    try:
        query = db.query(PromptEvaluation).filter(PromptEvaluation.prompt_id == prompt_id)
        
        if model_name:
            query = query.filter(PromptEvaluation.model_name == model_name)
        
        evaluations = query.order_by(desc(PromptEvaluation.evaluation_date)).all()
        
        return [PromptEvaluationResponse.from_orm(e) for e in evaluations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{prompt_id}/semantic-analysis", response_model=PromptSemanticAnalysisResponse)
async def analyze_prompt_semantics(
    prompt_id: str,
    analysis_request: PromptSemanticAnalysisRequest,
    db: Session = Depends(get_db_session)
):
    """Perform semantic analysis on a prompt."""
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # TODO: Implement semantic analysis
        # This would involve:
        # 1. Generating embeddings
        # 2. Computing similarity scores
        # 3. Performing topic classification
        # 4. Analyzing sentiment and complexity
        
        # For now, return mock data
        analysis = PromptSemanticAnalysis(
            prompt_id=prompt_id,
            semantic_vector=[0.1, 0.2, 0.3],  # Mock vector
            similarity_scores={},  # Mock similarity scores
            topic_classification={"topics": ["compression", "analysis"]},
            sentiment_analysis={"sentiment": "neutral", "confidence": 0.8},
            complexity_metrics={"complexity": 0.6, "readability": 0.7},
            readability_score=0.7,
            coherence_score=0.8,
            analysis_model=analysis_request.model_name,
            analysis_version=analysis_request.model_version
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return PromptSemanticAnalysisResponse.from_orm(analysis)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{prompt_id}/optimize", response_model=PromptOptimizationResponse)
async def optimize_prompt(
    prompt_id: str,
    optimization_request: PromptOptimizationRequest,
    db: Session = Depends(get_db_session)
):
    """Optimize a prompt using AI techniques."""
    try:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # TODO: Implement prompt optimization
        # This would involve:
        # 1. Analyzing current prompt performance
        # 2. Generating optimization suggestions
        # 3. Testing optimized versions
        # 4. Providing improvement metrics
        
        # For now, return mock optimization
        optimization = PromptOptimization(
            prompt_id=prompt_id,
            optimization_type=optimization_request.optimization_type,
            optimization_algorithm=optimization_request.algorithm,
            original_content=prompt.content,
            optimized_content=f"Optimized version of: {prompt.content}",
            improvement_metrics={"clarity": 0.15, "efficiency": 0.20},
            optimization_parameters=optimization_request.parameters
        )
        
        db.add(optimization)
        db.commit()
        db.refresh(optimization)
        
        return PromptOptimizationResponse.from_orm(optimization)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/", response_model=PromptWorkflowResponse)
async def create_workflow(
    workflow_data: PromptWorkflowCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new prompt workflow."""
    try:
        workflow = PromptWorkflow(
            name=workflow_data.name,
            description=workflow_data.description,
            workflow_definition=workflow_data.workflow_definition,
            execution_order=workflow_data.execution_order,
            conditional_logic=workflow_data.conditional_logic,
            category=workflow_data.category,
            tags=workflow_data.tags
        )
        
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        
        return PromptWorkflowResponse.from_orm(workflow)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workflows/{workflow_id}/execute", response_model=PromptWorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    execution_request: PromptWorkflowExecutionRequest,
    db: Session = Depends(get_db_session)
):
    """Execute a prompt workflow."""
    try:
        workflow = db.query(PromptWorkflow).filter(PromptWorkflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Create execution record
        execution = PromptWorkflowExecution(
            workflow_id=workflow_id,
            execution_id=str(uuid.uuid4()),
            input_data=execution_request.input_data,
            status=EvaluationStatus.RUNNING
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # TODO: Implement actual workflow execution
        # This would involve:
        # 1. Parsing workflow definition
        # 2. Executing prompts in order
        # 3. Handling conditional logic
        # 4. Collecting results
        
        return PromptWorkflowExecutionResponse.from_orm(execution)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary")
async def get_prompts_analytics(
    db: Session = Depends(get_db_session)
):
    """Get analytics summary for all prompts."""
    try:
        # Get basic statistics
        total_prompts = db.query(Prompt).count()
        active_prompts = db.query(Prompt).filter(Prompt.is_active == True).count()
        
        # Get category distribution
        category_stats = db.query(
            Prompt.category,
            db.func.count(Prompt.id).label('count')
        ).group_by(Prompt.category).all()
        
        # Get type distribution
        type_stats = db.query(
            Prompt.prompt_type,
            db.func.count(Prompt.id).label('count')
        ).group_by(Prompt.prompt_type).all()
        
        # Get usage statistics
        total_usage = db.query(db.func.sum(Prompt.usage_count)).scalar() or 0
        avg_success_rate = db.query(db.func.avg(Prompt.success_rate)).scalar() or 0
        
        return {
            "total_prompts": total_prompts,
            "active_prompts": active_prompts,
            "category_distribution": {cat: count for cat, count in category_stats},
            "type_distribution": {ptype: count for ptype, count in type_stats},
            "total_usage": total_usage,
            "average_success_rate": avg_success_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
