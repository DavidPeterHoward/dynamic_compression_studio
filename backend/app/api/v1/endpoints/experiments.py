"""
Enhanced Experiments API Endpoints
Multi-phase experiments with statistical analysis
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.services.experiment_runner import ExperimentRunner
from app.models.meta_learning import ExperimentRun
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models

class ExperimentCreateRequest(BaseModel):
    """Create experiment request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    experiment_type: str = Field(..., pattern='^(compression|meta_learning|hybrid)$')
    parameter_dimensions: Dict[str, List[Any]] = Field(...)
    statistical_methods: List[str] = Field(default=['bayesian', 'frequentist'])
    phases: List[Dict[str, Any]] = Field(..., min_items=1)
    meta_learning_trial_id: Optional[int] = None


class ExperimentResponse(BaseModel):
    """Experiment response"""
    id: int
    name: str
    description: Optional[str]
    experiment_type: str
    status: str
    current_phase: int
    parameter_dimensions: Dict[str, List[Any]]
    phases: List[Dict[str, Any]]
    results: Optional[List[Dict[str, Any]]]
    evaluation_metrics: Optional[Dict[str, Any]]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True


class RunExperimentRequest(BaseModel):
    """Run experiment request"""
    max_iterations_per_phase: int = Field(100, ge=1, le=1000)


class AddPhaseRequest(BaseModel):
    """Add phase to experiment"""
    name: str
    algorithm: str
    parameter_space: Optional[Dict[str, List[Any]]] = None
    metric_weights: Optional[Dict[str, float]] = None
    transition_criteria: Optional[Dict[str, Any]] = None
    statistical_method: str = Field('bayesian', pattern='^(bayesian|frequentist|bootstrap)$')


# Endpoints

@router.post("/", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    request: ExperimentCreateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Create new multi-phase experiment"""
    try:
        runner = ExperimentRunner(db)

        experiment = await runner.create_experiment(
            name=request.name,
            description=request.description,
            experiment_type=request.experiment_type,
            parameter_dimensions=request.parameter_dimensions,
            statistical_methods=request.statistical_methods,
            phases=request.phases,
            meta_learning_trial_id=request.meta_learning_trial_id
        )

        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            description=experiment.description,
            experiment_type=experiment.experiment_type,
            status=experiment.status,
            current_phase=experiment.current_phase,
            parameter_dimensions=experiment.parameter_dimensions,
            phases=experiment.phases,
            results=experiment.results,
            evaluation_metrics=experiment.evaluation_metrics,
            created_at=experiment.created_at.isoformat(),
            started_at=experiment.started_at.isoformat() if experiment.started_at else None,
            completed_at=experiment.completed_at.isoformat() if experiment.completed_at else None
        )

    except Exception as e:
        logger.error(f"Error creating experiment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create experiment: {str(e)}"
        )


@router.post("/{experiment_id}/run", response_model=ExperimentResponse)
async def run_experiment(
    experiment_id: int,
    request: RunExperimentRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Execute multi-phase experiment"""
    try:
        runner = ExperimentRunner(db)

        experiment = await runner.run_experiment(
            experiment_id=experiment_id,
            max_iterations_per_phase=request.max_iterations_per_phase
        )

        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            description=experiment.description,
            experiment_type=experiment.experiment_type,
            status=experiment.status,
            current_phase=experiment.current_phase,
            parameter_dimensions=experiment.parameter_dimensions,
            phases=experiment.phases,
            results=experiment.results,
            evaluation_metrics=experiment.evaluation_metrics,
            created_at=experiment.created_at.isoformat(),
            started_at=experiment.started_at.isoformat() if experiment.started_at else None,
            completed_at=experiment.completed_at.isoformat() if experiment.completed_at else None
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error running experiment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run experiment: {str(e)}"
        )


@router.get("/{experiment_id}/results")
async def get_experiment_results(
    experiment_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get experiment results and analysis"""
    try:
        runner = ExperimentRunner(db)
        results = await runner.get_experiment_results(experiment_id)
        return results

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get results: {str(e)}"
        )


@router.post("/{experiment_id}/add-phase", response_model=ExperimentResponse)
async def add_phase(
    experiment_id: int,
    request: AddPhaseRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Add new phase to experiment"""
    try:
        runner = ExperimentRunner(db)

        phase_config = {
            'name': request.name,
            'algorithm': request.algorithm,
            'parameter_space': request.parameter_space,
            'metric_weights': request.metric_weights,
            'transition_criteria': request.transition_criteria,
            'statistical_method': request.statistical_method
        }

        experiment = await runner.add_phase(experiment_id, phase_config)

        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            description=experiment.description,
            experiment_type=experiment.experiment_type,
            status=experiment.status,
            current_phase=experiment.current_phase,
            parameter_dimensions=experiment.parameter_dimensions,
            phases=experiment.phases,
            results=experiment.results,
            evaluation_metrics=experiment.evaluation_metrics,
            created_at=experiment.created_at.isoformat(),
            started_at=experiment.started_at.isoformat() if experiment.started_at else None,
            completed_at=experiment.completed_at.isoformat() if experiment.completed_at else None
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding phase: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add phase: {str(e)}"
        )


@router.get("/", response_model=List[ExperimentResponse])
async def list_experiments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """List all experiments"""
    experiments = db.query(ExperimentRun).offset(skip).limit(limit).all()

    return [
        ExperimentResponse(
            id=exp.id,
            name=exp.name,
            description=exp.description,
            experiment_type=exp.experiment_type,
            status=exp.status,
            current_phase=exp.current_phase,
            parameter_dimensions=exp.parameter_dimensions,
            phases=exp.phases,
            results=exp.results,
            evaluation_metrics=exp.evaluation_metrics,
            created_at=exp.created_at.isoformat(),
            started_at=exp.started_at.isoformat() if exp.started_at else None,
            completed_at=exp.completed_at.isoformat() if exp.completed_at else None
        )
        for exp in experiments
    ]
