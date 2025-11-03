"""
Meta-Learning API Endpoints
Provides endpoints for trial creation, iteration execution, and recursive improvement
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.services.meta_learning_engine import MetaLearningEngine
from app.models.meta_learning import MetaLearningTrial, MetaLearningIteration
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models

class TrialCreateRequest(BaseModel):
    """Create meta-learning trial request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    algorithm_family: str = Field(..., pattern='^(compression|prediction|optimization)$')
    target_metric: str = Field(..., min_length=1)
    learning_rate: float = Field(0.01, gt=0, le=1.0)
    max_iterations: int = Field(100, ge=1, le=10000)
    convergence_threshold: float = Field(0.001, gt=0, le=1.0)
    parameter_space: Dict[str, List[Any]] = Field(...)
    inference_method: str = Field('bayesian', pattern='^(bayesian|frequentist|bootstrap)$')
    self_modification_enabled: bool = False


class TrialResponse(BaseModel):
    """Meta-learning trial response"""
    id: int
    name: str
    description: Optional[str]
    algorithm_family: str
    target_metric: str
    learning_rate: float
    iteration_count: int
    max_iterations: int
    convergence_threshold: float
    parameter_space: Dict[str, List[Any]]
    current_parameters: Dict[str, Any]
    inference_method: str
    best_score: Optional[float]
    current_score: Optional[float]
    improvement_rate: Optional[float]
    status: str
    self_modification_enabled: bool
    recursion_depth: int
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True


class IterationRunRequest(BaseModel):
    """Run iteration request"""
    use_synthetic_data: bool = True
    synthetic_config: Optional[Dict[str, Any]] = Field(
        default={
            'complexity': 0.7,
            'entropy': 0.6,
            'redundancy': 0.3,
            'pattern': 'perlin'
        }
    )


class IterationResponse(BaseModel):
    """Iteration response"""
    id: int
    trial_id: int
    iteration_number: int
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    score: float
    confidence_interval: Optional[Dict[str, float]]
    statistical_significance: Optional[float]
    synthetic_data_config: Optional[Dict[str, Any]]
    phase: Optional[str]
    duration_seconds: float
    throughput: Optional[float]
    created_at: str

    class Config:
        from_attributes = True


class RecursiveImproveRequest(BaseModel):
    """Recursive improvement request"""
    trial_id: int = Field(..., gt=0)


class PerformanceResponse(BaseModel):
    """Trial performance metrics response"""
    trial_id: int
    iteration_count: int
    best_score: Optional[float]
    current_score: Optional[float]
    improvement_rate: Optional[float]
    status: str
    iterations: List[Dict[str, Any]]
    convergence_analysis: Dict[str, Any]


# Endpoints

@router.post("/trials", response_model=TrialResponse, status_code=status.HTTP_201_CREATED)
async def create_trial(
    request: TrialCreateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create new meta-learning trial

    Creates a trial with configured parameter space, learning rate, and inference method.
    The trial will optimize parameters to maximize the target metric.
    """
    try:
        engine = MetaLearningEngine(db)

        trial = await engine.create_trial(
            name=request.name,
            description=request.description,
            algorithm_family=request.algorithm_family,
            target_metric=request.target_metric,
            parameter_space=request.parameter_space,
            learning_rate=request.learning_rate,
            max_iterations=request.max_iterations,
            convergence_threshold=request.convergence_threshold,
            inference_method=request.inference_method,
            self_modification_enabled=request.self_modification_enabled
        )

        return TrialResponse(
            id=trial.id,
            name=trial.name,
            description=trial.description,
            algorithm_family=trial.algorithm_family,
            target_metric=trial.target_metric,
            learning_rate=trial.learning_rate,
            iteration_count=trial.iteration_count,
            max_iterations=trial.max_iterations,
            convergence_threshold=trial.convergence_threshold,
            parameter_space=trial.parameter_space,
            current_parameters=trial.current_parameters,
            inference_method=trial.inference_method,
            best_score=trial.best_score,
            current_score=trial.current_score,
            improvement_rate=trial.improvement_rate,
            status=trial.status,
            self_modification_enabled=trial.self_modification_enabled,
            recursion_depth=trial.recursion_depth,
            created_at=trial.created_at.isoformat(),
            started_at=trial.started_at.isoformat() if trial.started_at else None,
            completed_at=trial.completed_at.isoformat() if trial.completed_at else None
        )

    except Exception as e:
        logger.error(f"Error creating trial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trial: {str(e)}"
        )


@router.get("/trials/{trial_id}", response_model=TrialResponse)
async def get_trial(
    trial_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get meta-learning trial by ID

    Returns complete trial information including current status and parameters.
    """
    trial = db.query(MetaLearningTrial).filter(MetaLearningTrial.id == trial_id).first()

    if not trial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trial {trial_id} not found"
        )

    return TrialResponse(
        id=trial.id,
        name=trial.name,
        description=trial.description,
        algorithm_family=trial.algorithm_family,
        target_metric=trial.target_metric,
        learning_rate=trial.learning_rate,
        iteration_count=trial.iteration_count,
        max_iterations=trial.max_iterations,
        convergence_threshold=trial.convergence_threshold,
        parameter_space=trial.parameter_space,
        current_parameters=trial.current_parameters,
        inference_method=trial.inference_method,
        best_score=trial.best_score,
        current_score=trial.current_score,
        improvement_rate=trial.improvement_rate,
        status=trial.status,
        self_modification_enabled=trial.self_modification_enabled,
        recursion_depth=trial.recursion_depth,
        created_at=trial.created_at.isoformat(),
        started_at=trial.started_at.isoformat() if trial.started_at else None,
        completed_at=trial.completed_at.isoformat() if trial.completed_at else None
    )


@router.get("/trials", response_model=List[TrialResponse])
async def list_trials(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all meta-learning trials

    Optionally filter by status (created, running, completed, failed).
    """
    query = db.query(MetaLearningTrial)

    if status_filter:
        query = query.filter(MetaLearningTrial.status == status_filter)

    trials = query.offset(skip).limit(limit).all()

    return [
        TrialResponse(
            id=trial.id,
            name=trial.name,
            description=trial.description,
            algorithm_family=trial.algorithm_family,
            target_metric=trial.target_metric,
            learning_rate=trial.learning_rate,
            iteration_count=trial.iteration_count,
            max_iterations=trial.max_iterations,
            convergence_threshold=trial.convergence_threshold,
            parameter_space=trial.parameter_space,
            current_parameters=trial.current_parameters,
            inference_method=trial.inference_method,
            best_score=trial.best_score,
            current_score=trial.current_score,
            improvement_rate=trial.improvement_rate,
            status=trial.status,
            self_modification_enabled=trial.self_modification_enabled,
            recursion_depth=trial.recursion_depth,
            created_at=trial.created_at.isoformat(),
            started_at=trial.started_at.isoformat() if trial.started_at else None,
            completed_at=trial.completed_at.isoformat() if trial.completed_at else None
        )
        for trial in trials
    ]


@router.post("/trials/{trial_id}/iterate", response_model=IterationResponse)
async def run_iteration(
    trial_id: int,
    request: IterationRunRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Run single iteration of meta-learning trial

    Executes one iteration with current parameters, evaluates performance,
    and optimizes parameters for next iteration using configured inference method.
    """
    try:
        engine = MetaLearningEngine(db)

        iteration = await engine.run_iteration(
            trial_id=trial_id,
            use_synthetic_data=request.use_synthetic_data,
            synthetic_config=request.synthetic_config
        )

        return IterationResponse(
            id=iteration.id,
            trial_id=iteration.trial_id,
            iteration_number=iteration.iteration_number,
            parameters=iteration.parameters,
            metrics=iteration.metrics,
            score=iteration.score,
            confidence_interval=iteration.confidence_interval,
            statistical_significance=iteration.statistical_significance,
            synthetic_data_config=iteration.synthetic_data_config,
            phase=iteration.phase,
            duration_seconds=iteration.duration_seconds,
            throughput=iteration.throughput,
            created_at=iteration.created_at.isoformat()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error running iteration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run iteration: {str(e)}"
        )


@router.get("/trials/{trial_id}/performance", response_model=PerformanceResponse)
async def get_trial_performance(
    trial_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get trial performance metrics and iteration history

    Returns comprehensive performance analysis including convergence metrics,
    score progression, and iteration details.
    """
    trial = db.query(MetaLearningTrial).filter(MetaLearningTrial.id == trial_id).first()

    if not trial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trial {trial_id} not found"
        )

    # Get iterations
    iterations = db.query(MetaLearningIteration).filter(
        MetaLearningIteration.trial_id == trial_id
    ).order_by(MetaLearningIteration.iteration_number).all()

    iteration_data = [
        {
            'iteration_number': it.iteration_number,
            'score': it.score,
            'parameters': it.parameters,
            'metrics': it.metrics,
            'phase': it.phase,
            'throughput': it.throughput,
            'duration_seconds': it.duration_seconds
        }
        for it in iterations
    ]

    # Convergence analysis
    convergence_analysis = {}
    if len(iterations) > 0:
        scores = [it.score for it in iterations]

        convergence_analysis = {
            'total_iterations': len(iterations),
            'best_score': float(max(scores)),
            'worst_score': float(min(scores)),
            'mean_score': float(sum(scores) / len(scores)),
            'score_progression': scores,
            'is_improving': scores[-1] > scores[0] if len(scores) > 1 else False,
            'total_improvement': float(scores[-1] - scores[0]) if len(scores) > 1 else 0.0,
            'average_throughput': float(sum(it.throughput or 0 for it in iterations) / len(iterations))
        }

        # Check convergence
        if len(scores) >= 10:
            recent_scores = scores[-10:]
            score_variance = sum((s - sum(recent_scores) / len(recent_scores)) ** 2 for s in recent_scores) / len(recent_scores)
            convergence_analysis['converged'] = score_variance < trial.convergence_threshold
            convergence_analysis['score_variance'] = float(score_variance)

    return PerformanceResponse(
        trial_id=trial.id,
        iteration_count=trial.iteration_count,
        best_score=trial.best_score,
        current_score=trial.current_score,
        improvement_rate=trial.improvement_rate,
        status=trial.status,
        iterations=iteration_data,
        convergence_analysis=convergence_analysis
    )


@router.post("/recursive-improve", response_model=TrialResponse)
async def recursive_improve(
    request: RecursiveImproveRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create recursive child trial with refined parameter space

    Analyzes parent trial results and creates child trial with optimized
    parameter space for further improvement.
    """
    try:
        engine = MetaLearningEngine(db)

        child_trial = await engine.recursive_improve(trial_id=request.trial_id)

        return TrialResponse(
            id=child_trial.id,
            name=child_trial.name,
            description=child_trial.description,
            algorithm_family=child_trial.algorithm_family,
            target_metric=child_trial.target_metric,
            learning_rate=child_trial.learning_rate,
            iteration_count=child_trial.iteration_count,
            max_iterations=child_trial.max_iterations,
            convergence_threshold=child_trial.convergence_threshold,
            parameter_space=child_trial.parameter_space,
            current_parameters=child_trial.current_parameters,
            inference_method=child_trial.inference_method,
            best_score=child_trial.best_score,
            current_score=child_trial.current_score,
            improvement_rate=child_trial.improvement_rate,
            status=child_trial.status,
            self_modification_enabled=child_trial.self_modification_enabled,
            recursion_depth=child_trial.recursion_depth,
            created_at=child_trial.created_at.isoformat(),
            started_at=child_trial.started_at.isoformat() if child_trial.started_at else None,
            completed_at=child_trial.completed_at.isoformat() if child_trial.completed_at else None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in recursive improvement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recursive trial: {str(e)}"
        )


@router.delete("/trials/{trial_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trial(
    trial_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete meta-learning trial and all associated iterations

    Permanently removes trial and iteration data.
    """
    trial = db.query(MetaLearningTrial).filter(MetaLearningTrial.id == trial_id).first()

    if not trial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trial {trial_id} not found"
        )

    db.delete(trial)
    db.commit()

    logger.info(f"Deleted trial {trial_id}")
    return None
