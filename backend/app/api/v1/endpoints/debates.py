"""
Debate API Endpoints
Ollama-powered multi-agent debate system management
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.services.debate_service import (
    DebateService, DebateConfiguration, DebateRules, DebateStatus,
    get_debate_service
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models

class DebateRulesRequest(BaseModel):
    """Debate rules configuration"""
    allow_ad_hominem: bool = False
    require_evidence: bool = True
    enable_fact_checking: bool = True
    allow_creativity: bool = True
    enforce_formality: bool = True
    evidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
    creativity_weight: float = Field(0.3, ge=0.0, le=1.0)
    max_fallacies_per_argument: int = Field(1, ge=0, le=5)
    require_counter_arguments: bool = True
    allow_collaboration: bool = False
    enforce_turn_taking: bool = True


class DebateConfigurationRequest(BaseModel):
    """Create debate session request"""
    debate_topic: str = Field(..., min_length=1, max_length=500)
    problem_statement: str = Field(..., min_length=1, max_length=1000)
    premise_area: str = Field(..., min_length=1, max_length=500)
    debate_mode: str = Field("structured", pattern='^(structured|freeform|autonomous)$')
    max_rounds: int = Field(5, ge=1, le=20)
    max_iterations_per_round: int = Field(3, ge=1, le=10)
    iterations_per_agent: int = Field(2, ge=1, le=5)
    consensus_threshold: float = Field(0.8, ge=0.5, le=1.0)
    time_limit_per_argument: int = Field(60, ge=10, le=300)
    response_timeout: int = Field(30, ge=5, le=120)
    selected_agents: List[str] = Field(..., min_items=2, max_items=10)
    agent_roles: Optional[Dict[str, str]] = None
    debate_rules: DebateRulesRequest = DebateRulesRequest()
    ollama_model: str = "llama2:7b"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=50, le=2048)
    system_prompt_template: str = ""
    enable_detailed_logging: bool = True
    export_format: str = Field("json", pattern='^(json|csv|xml)$')
    real_time_updates: bool = True


class DebateSessionResponse(BaseModel):
    """Debate session response"""
    session_id: str
    status: str
    configuration: Dict[str, Any]
    participants: List[Dict[str, Any]]
    rounds: List[Dict[str, Any]]
    current_round: int
    total_arguments: int
    consensus_score: float
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class DebateArgumentResponse(BaseModel):
    """Individual debate argument response"""
    id: str
    agent_id: str
    agent_name: str
    agent_type: str
    content: str
    round_number: int
    timestamp: str
    evidence_score: float
    creativity_score: float
    fallacies_detected: int
    consensus_impact: float


class RoundSummaryResponse(BaseModel):
    """Round summary response"""
    round_number: int
    arguments_count: int
    consensus_score: float
    key_points_discussed: List[str]
    evidence_quality_avg: float
    creativity_level_avg: float


class DebateConclusionResponse(BaseModel):
    """Debate conclusion response"""
    conclusion_type: str
    winning_position: Optional[str]
    confidence_score: float
    key_insights: List[str]
    recommendations: List[str]
    summary: str
    timestamp: str


class DebateStatusResponse(BaseModel):
    """Debate status response"""
    session_id: str
    status: str
    current_round: int
    total_arguments: int
    consensus_score: float
    participants_count: int
    started_at: Optional[str]
    completed_at: Optional[str]


# Dependencies

async def get_debate_service_instance() -> DebateService:
    """Get debate service instance"""
    service = get_debate_service()
    if not await service.initialize():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Debate service initialization failed"
        )
    return service


# API Endpoints

@router.post("/sessions", response_model=DebateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_debate_session(
    request: DebateConfigurationRequest,
    background_tasks: BackgroundTasks,
    service: DebateService = Depends(get_debate_service_instance),
    db: AsyncSession = Depends(get_db_session)
) -> DebateSessionResponse:
    """
    Create a new debate session with the specified configuration.

    This endpoint initializes a debate session with the provided parameters
    and prepares it for execution.
    """
    try:
        # Convert request to DebateConfiguration
        debate_rules = DebateRules(**request.debate_rules.dict())
        config = DebateConfiguration(
            debate_topic=request.debate_topic,
            problem_statement=request.problem_statement,
            premise_area=request.premise_area,
            debate_mode=request.debate_mode,
            max_rounds=request.max_rounds,
            max_iterations_per_round=request.max_iterations_per_round,
            iterations_per_agent=request.iterations_per_agent,
            consensus_threshold=request.consensus_threshold,
            time_limit_per_argument=request.time_limit_per_argument,
            response_timeout=request.response_timeout,
            selected_agents=request.selected_agents,
            agent_roles=request.agent_roles,
            debate_rules=debate_rules,
            ollama_model=request.ollama_model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt_template=request.system_prompt_template,
            enable_detailed_logging=request.enable_detailed_logging,
            export_format=request.export_format,
            real_time_updates=request.real_time_updates
        )

        # Create debate session
        session = await service.create_debate_session(config)

        logger.info(f"Created debate session: {session.session_id}")

        # Convert to response format
        return DebateSessionResponse(
            session_id=session.session_id,
            status=session.status.value,
            configuration={
                "debate_topic": session.configuration.debate_topic,
                "problem_statement": session.configuration.problem_statement,
                "premise_area": session.configuration.premise_area,
                "debate_mode": session.configuration.debate_mode.value,
                "max_rounds": session.configuration.max_rounds,
                "consensus_threshold": session.configuration.consensus_threshold,
                "selected_agents": session.configuration.selected_agents,
                "ollama_model": session.configuration.ollama_model
            },
            participants=[
                {
                    "agent_id": p.agent_id,
                    "agent_name": p.agent_name,
                    "agent_type": p.agent_type,
                    "specialization": p.specialization,
                    "position": p.position,
                    "confidence_score": p.confidence_score,
                    "arguments_made": p.arguments_made
                } for p in session.participants
            ],
            rounds=session.rounds,
            current_round=session.current_round,
            total_arguments=session.total_arguments,
            consensus_score=session.consensus_score,
            started_at=session.started_at,
            completed_at=session.completed_at,
            created_at=session.started_at or ""
        )

    except Exception as e:
        logger.error(f"Failed to create debate session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create debate session: {str(e)}"
        )


@router.get("/sessions", response_model=List[DebateStatusResponse])
async def list_debate_sessions(
    service: DebateService = Depends(get_debate_service_instance)
) -> List[DebateStatusResponse]:
    """
    List all active debate sessions with their current status.
    """
    try:
        active_sessions = await service.list_active_sessions()

        return [
            DebateStatusResponse(
                session_id=session['session_id'],
                status=session['status'],
                current_round=session['current_round'],
                total_arguments=session['total_arguments'],
                consensus_score=session['consensus_score'],
                participants_count=session['participants_count'],
                started_at=session['started_at'],
                completed_at=session['completed_at']
            ) for session in active_sessions
        ]

    except Exception as e:
        logger.error(f"Failed to list debate sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list debate sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=DebateSessionResponse)
async def get_debate_session(
    session_id: str,
    service: DebateService = Depends(get_debate_service_instance)
) -> DebateSessionResponse:
    """
    Get detailed information about a specific debate session.
    """
    try:
        session_data = await service.get_session_status(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate session {session_id} not found"
            )

        # Get full session details (this would need enhancement in the service)
        # For now, return basic status
        return DebateSessionResponse(
            session_id=session_data['session_id'],
            status=session_data['status'],
            configuration={},  # Would need to be retrieved from service
            participants=[],
            rounds=[],
            current_round=session_data['current_round'],
            total_arguments=session_data['total_arguments'],
            consensus_score=session_data['consensus_score'],
            started_at=session_data['started_at'],
            completed_at=session_data['completed_at'],
            created_at=session_data['started_at'] or ""
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get debate session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get debate session: {str(e)}"
        )


@router.post("/sessions/{session_id}/start", status_code=status.HTTP_200_OK)
async def start_debate_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    service: DebateService = Depends(get_debate_service_instance)
) -> Dict[str, str]:
    """
    Start a debate session execution.

    This will begin the debate rounds in the background.
    """
    try:
        # Check if session exists
        session_data = await service.get_session_status(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate session {session_id} not found"
            )

        if session_data['status'] != 'initialized':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Debate session {session_id} is not in initialized state"
            )

        # Start debate execution in background
        # Note: This would need to be implemented in the service
        background_tasks.add_task(service._execute_debate_background, session_id)

        logger.info(f"Started debate session: {session_id}")

        return {"message": f"Debate session {session_id} started successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start debate session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start debate session: {str(e)}"
        )


@router.post("/sessions/{session_id}/stop", status_code=status.HTTP_200_OK)
async def stop_debate_session(
    session_id: str,
    service: DebateService = Depends(get_debate_service_instance)
) -> Dict[str, str]:
    """
    Stop a running debate session.
    """
    try:
        # Check if session exists
        session_data = await service.get_session_status(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate session {session_id} not found"
            )

        # Stop debate execution
        # Note: This would need to be implemented in the service
        success = await service.cleanup_session(session_id)

        if success:
            logger.info(f"Stopped debate session: {session_id}")
            return {"message": f"Debate session {session_id} stopped successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to stop debate session {session_id}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop debate session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop debate session: {str(e)}"
        )


@router.post("/sessions/{session_id}/round", response_model=List[DebateArgumentResponse])
async def execute_debate_round(
    session_id: str,
    service: DebateService = Depends(get_debate_service_instance)
) -> List[DebateArgumentResponse]:
    """
    Execute a single round of debate for the specified session.
    """
    try:
        # Check if session exists and is active
        session_data = await service.get_session_status(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate session {session_id} not found"
            )

        if session_data['status'] != 'active':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Debate session {session_id} is not active"
            )

        # Execute round
        arguments = await service.execute_debate_round(session_id)

        logger.info(f"Executed round for debate session: {session_id}")

        return [
            DebateArgumentResponse(
                id=arg.id,
                agent_id=arg.agent_id,
                agent_name=arg.agent_name,
                agent_type=arg.agent_type,
                content=arg.content,
                round_number=arg.round_number,
                timestamp=arg.timestamp,
                evidence_score=arg.evidence_score,
                creativity_score=arg.creativity_score,
                fallacies_detected=arg.fallacies_detected,
                consensus_impact=arg.consensus_impact
            ) for arg in arguments
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute debate round for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute debate round: {str(e)}"
        )


@router.get("/sessions/{session_id}/rounds/{round_number}/summary", response_model=RoundSummaryResponse)
async def get_round_summary(
    session_id: str,
    round_number: int,
    service: DebateService = Depends(get_debate_service_instance)
) -> RoundSummaryResponse:
    """
    Get summary for a specific round of debate.
    """
    try:
        # Check if session exists
        session_data = await service.get_session_status(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate session {session_id} not found"
            )

        # Generate round summary
        # Note: This would need to be implemented to retrieve stored round data
        summary = RoundSummaryResponse(
            round_number=round_number,
            arguments_count=0,  # Would need to be retrieved
            consensus_score=0.0,
            key_points_discussed=[],
            evidence_quality_avg=0.0,
            creativity_level_avg=0.0
        )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get round summary for session {session_id}, round {round_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get round summary: {str(e)}"
        )


@router.get("/sessions/{session_id}/conclusion", response_model=DebateConclusionResponse)
async def get_debate_conclusion(
    session_id: str,
    service: DebateService = Depends(get_debate_service_instance)
) -> DebateConclusionResponse:
    """
    Get the final conclusion for a completed debate session.
    """
    try:
        # Check if session exists and is completed
        session_data = await service.get_session_status(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate session {session_id} not found"
            )

        if session_data['status'] != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Debate session {session_id} is not completed"
            )

        # Generate conclusion
        # Note: This would need to be implemented to retrieve stored session data
        conclusion = DebateConclusionResponse(
            conclusion_type="consensus",
            winning_position="balanced",
            confidence_score=0.75,
            key_insights=["Multiple perspectives considered", "Evidence-based reasoning applied"],
            recommendations=["Implement balanced approach", "Continue monitoring outcomes"],
            summary="Debate reached consensus with balanced recommendations.",
            timestamp=""
        )

        return conclusion

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get debate conclusion for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get debate conclusion: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_debate_session(
    session_id: str,
    service: DebateService = Depends(get_debate_service_instance)
):
    """
    Delete a debate session and clean up resources.
    """
    try:
        success = await service.cleanup_session(session_id)

        if success:
            logger.info(f"Deleted debate session: {session_id}")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate session {session_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete debate session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete debate session: {str(e)}"
        )
