"""
Debate Service - Ollama-powered multi-agent debate system.

Provides comprehensive debate functionality with AI agent communication,
rule enforcement, and analytics tracking.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from app.services.ollama_service import OllamaService, get_ollama_service
from app.core.base_agent import BaseAgent
from app.core.agent_registry import get_agent_registry
from app.models.debate import (
    DebateSession, DebateParticipant, DebateRound, DebateArgument,
    DebateConclusion, DebateAnalytics, DebateStatus
)
from app.database import get_db_session


logger = logging.getLogger(__name__)


class DebateMode(Enum):
    """Debate execution modes."""
    STRUCTURED = "structured"
    FREEFORM = "freeform"
    AUTONOMOUS = "autonomous"


class DebateStatus(Enum):
    """Debate session status."""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CONSENSUS_REACHED = "consensus_reached"


@dataclass
class DebateArgument:
    """Represents a single debate argument."""
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


@dataclass
class DebateParticipant:
    """Represents a debate participant."""
    agent_id: str = ""
    agent_name: str = ""
    agent_type: str = ""
    specialization: str = ""
    position: str = "neutral"
    confidence_score: float = 0.5
    arguments_made: int = 0
    rebuttals_given: int = 0
    fallacies_identified: int = 0
    strength_score: float = 0.5


@dataclass
class DebateRules:
    """Debate rules and constraints."""
    allow_ad_hominem: bool = False
    require_evidence: bool = True
    enable_fact_checking: bool = True
    allow_creativity: bool = True
    enforce_formality: bool = True
    evidence_threshold: float = 0.7
    creativity_weight: float = 0.3
    max_fallacies_per_argument: int = 1
    require_counter_arguments: bool = True
    allow_collaboration: bool = False
    enforce_turn_taking: bool = True


@dataclass
class DebateConfiguration:
    """Complete debate configuration."""
    debate_topic: str = ""
    problem_statement: str = ""
    premise_area: str = ""
    debate_mode: DebateMode = DebateMode.STRUCTURED
    max_rounds: int = 5
    max_iterations_per_round: int = 3
    iterations_per_agent: int = 2
    consensus_threshold: float = 0.8
    time_limit_per_argument: int = 60
    response_timeout: int = 30
    selected_agents: Optional[List[str]] = None
    agent_roles: Optional[Dict[str, str]] = None
    debate_rules: Optional[DebateRules] = None
    ollama_model: str = "llama2:7b"
    temperature: float = 0.7
    max_tokens: int = 512
    system_prompt_template: str = ""
    enable_detailed_logging: bool = True
    export_format: str = "json"
    real_time_updates: bool = True

    def __post_init__(self):
        if self.selected_agents is None:
            self.selected_agents = []
        if self.agent_roles is None:
            self.agent_roles = {}
        if self.debate_rules is None:
            self.debate_rules = DebateRules()


@dataclass
class RoundSummary:
    """Summary of a debate round."""
    round_number: int
    arguments_count: int
    consensus_score: float
    key_points_discussed: List[str]
    evidence_quality_avg: float
    creativity_level_avg: float


@dataclass
class DebateConclusion:
    """Final debate conclusion."""
    conclusion_type: str
    winning_position: Optional[str]
    confidence_score: float
    key_insights: List[str]
    recommendations: List[str]
    summary: str
    timestamp: str


@dataclass
class DebateSession:
    """Complete debate session state."""
    session_id: str
    status: DebateStatus
    configuration: DebateConfiguration
    participants: List[DebateParticipant] = None
    rounds: List[Dict] = None
    current_round: int = 0
    total_arguments: int = 0
    consensus_score: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.rounds is None:
            self.rounds = []


class DebateService:
    """Main debate service with Ollama integration."""

    def __init__(self):
        self.ollama_service = get_ollama_service()
        self.agent_registry = get_agent_registry()
        self.active_sessions: Dict[str, DebateSession] = {}
        self.logger = logging.getLogger(__name__)

    async def initialize(self) -> bool:
        """Initialize the debate service."""
        try:
            # Ensure Ollama service is initialized
            ollama_ready = await self.ollama_service.initialize()
            if not ollama_ready:
                self.logger.error("Failed to initialize Ollama service")
                return False

            self.logger.info("Debate service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Debate service initialization failed: {e}")
            return False

    async def create_debate_session(self, config: DebateConfiguration) -> DebateSession:
        """Create a new debate session."""
        session_id = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(config)) % 10000}"

        # Create participants from selected agents
        participants = []
        for agent_id in config.selected_agents:
            # Try to get agent from registry first
            agent = self.agent_registry.get_agent(agent_id)
            if agent:
                participant = DebateParticipant(
                    agent_id=agent_id,
                    agent_name=getattr(agent, 'name', f'Agent {agent_id}'),
                    agent_type=getattr(agent, 'type', 'unknown'),
                    specialization=getattr(agent, 'specialization', 'General debate participant')
                )
            else:
                # Fallback for mock/test agents
                participant = DebateParticipant(
                    agent_id=agent_id,
                    agent_name=f'Agent {agent_id}',
                    agent_type='unknown',
                    specialization='General debate participant'
                )
            participants.append(participant)

        session = DebateSession(
            session_id=session_id,
            status=DebateStatus.INITIALIZED,
            configuration=config,
            participants=participants,
            started_at=datetime.now().isoformat()
        )

        self.active_sessions[session_id] = session

        # Save to database
        try:
            await self.save_debate_session(session)
        except Exception as e:
            self.logger.warning(f"Failed to save debate session to database: {e}")
            # Continue execution even if database save fails

        self.logger.info(f"Created debate session: {session_id}")
        return session

    async def execute_debate_round(self, session_id: str) -> List[DebateArgument]:
        """Execute a single debate round."""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.status != DebateStatus.ACTIVE:
            raise ValueError(f"Session {session_id} is not active")

        current_round = session.current_round + 1
        session.current_round = current_round

        round_arguments = []

        for participant in session.participants:
            try:
                # Generate agent response
                argument = await self._generate_agent_argument(
                    participant, session, current_round, round_arguments
                )
                round_arguments.append(argument)

                # Update participant stats
                participant.arguments_made += 1

            except Exception as e:
                self.logger.error(f"Failed to generate argument for {participant.agent_name}: {e}")
                # Create error argument
                error_argument = DebateArgument(
                    id=f"error_{current_round}_{participant.agent_id}",
                    agent_id=participant.agent_id,
                    agent_name=participant.agent_name,
                    agent_type=participant.agent_type,
                    content=f"Error generating response: {str(e)}",
                    round_number=current_round,
                    timestamp=datetime.now().isoformat(),
                    evidence_score=0.0,
                    creativity_score=0.0,
                    fallacies_detected=0,
                    consensus_impact=0.0
                )
                round_arguments.append(error_argument)

        # Update session stats
        session.total_arguments += len(round_arguments)

        # Calculate round consensus
        if round_arguments:
            round_consensus = sum(arg.consensus_impact for arg in round_arguments) / len(round_arguments)
            session.consensus_score = (session.consensus_score + round_consensus) / 2  # Running average

        # Save arguments to database
        for argument in round_arguments:
            try:
                await self.save_debate_argument(session_id, argument)
            except Exception as e:
                self.logger.warning(f"Failed to save argument {argument.id} to database: {e}")

        self.logger.info(f"Completed round {current_round} for session {session_id}")
        return round_arguments

    async def _generate_agent_argument(
        self,
        participant: DebateParticipant,
        session: DebateSession,
        round_number: int,
        previous_arguments: List[DebateArgument]
    ) -> DebateArgument:
        """Generate a single agent argument using Ollama."""
        config = session.configuration

        # Build system prompt
        system_prompt = self._build_system_prompt(participant, session, round_number)

        # Build user prompt
        user_prompt = self._build_user_prompt(previous_arguments, participant, round_number)

        # Generate response using Ollama
        response = await self.ollama_service.generate(
            prompt=user_prompt,
            model=config.ollama_model,
            system_prompt=system_prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        # Analyze response for scoring
        evidence_score = self._analyze_evidence_quality(response['response'], config.debate_rules)
        creativity_score = self._analyze_creativity(response['response'], config.debate_rules)
        fallacies_detected = self._analyze_fallacies(response['response'])
        consensus_impact = self._calculate_consensus_impact(response['response'], previous_arguments)

        argument = DebateArgument(
            id=f"arg_{round_number}_{participant.agent_id}_{datetime.now().strftime('%H%M%S')}",
            agent_id=participant.agent_id,
            agent_name=participant.agent_name,
            agent_type=participant.agent_type,
            content=response['response'],
            round_number=round_number,
            timestamp=datetime.now().isoformat(),
            evidence_score=evidence_score,
            creativity_score=creativity_score,
            fallacies_detected=fallacies_detected,
            consensus_impact=consensus_impact
        )

        return argument

    def _build_system_prompt(self, participant: DebateParticipant, session: DebateSession, round_number: int) -> str:
        """Build system prompt for agent."""
        config = session.configuration
        rules = config.debate_rules

        prompt = f"""You are {participant.agent_name}, a {participant.specialization}.

DEBATE CONTEXT:
- Topic: {config.debate_topic}
- Premise: {config.premise_area}
- Problem Statement: {config.problem_statement}
- Round: {round_number}
- Your Role: {config.agent_roles.get(participant.agent_id, 'Participant')}

DEBATE RULES:
- {'Must provide evidence for claims' if rules.require_evidence else 'Evidence optional'}
- {'Facts will be verified' if rules.enable_fact_checking else 'No fact checking'}
- {'Creative arguments allowed' if rules.allow_creativity else 'Stick to logical arguments'}
- {'Maintain formal tone' if rules.enforce_formality else 'Natural conversation style'}
- {'Address previous arguments' if rules.require_counter_arguments else 'Focus on your position'}

YOUR STRENGTHS: {participant.specialization}

Provide a thoughtful, well-reasoned response that advances the debate using your specialized expertise."""

        return prompt

    def _build_user_prompt(self, previous_arguments: List[DebateArgument], participant: DebateParticipant, round_number: int) -> str:
        """Build user prompt for agent."""
        if not previous_arguments:
            return f"This is round {round_number}. Present your initial position on the debate topic using your expertise as {participant.agent_name}."

        # Include previous arguments for context
        context = "\n\n".join([
            f"Argument by {arg.agent_name} ({arg.agent_type}): {arg.content[:200]}..."
            for arg in previous_arguments[-3:]  # Last 3 arguments for context
        ])

        return f"""Previous arguments in this debate:

{context}

Respond to these arguments using your expertise as {participant.agent_name}. Address key points and advance the debate."""

    def _analyze_evidence_quality(self, response: str, rules: DebateRules) -> float:
        """Analyze evidence quality in response."""
        if not rules.require_evidence:
            return 0.8  # Default good score if evidence not required

        evidence_indicators = [
            'according to', 'research shows', 'studies indicate', 'data suggests',
            'evidence', 'proven', 'demonstrated', 'empirical', 'statistics'
        ]

        evidence_count = sum(1 for indicator in evidence_indicators if indicator in response.lower())
        base_score = min(0.9, 0.5 + (evidence_count * 0.1))

        return max(rules.evidence_threshold - 0.1, min(0.95, base_score))

    def _analyze_creativity(self, response: str, rules: DebateRules) -> float:
        """Analyze creativity in response."""
        if not rules.allow_creativity:
            return 0.6  # Moderate score if creativity not allowed

        creative_indicators = [
            'imagine', 'innovative', 'novel', 'creative', 'alternative',
            'unconventional', 'unique', 'original', 'fresh perspective'
        ]

        creative_count = sum(1 for indicator in creative_indicators if indicator in response.lower())
        base_score = min(0.9, 0.4 + (creative_count * 0.15))

        return max(0.3, min(0.9, base_score))

    def _analyze_fallacies(self, response: str) -> int:
        """Detect logical fallacies in response."""
        fallacy_indicators = [
            'ad hominem', 'straw man', 'false dichotomy', 'slippery slope',
            'appeal to emotion', 'bandwagon', 'authority', 'tradition'
        ]

        detected = sum(1 for fallacy in fallacy_indicators if fallacy in response.lower())
        return min(detected, 3)  # Cap at 3 for realistic detection

    def _calculate_consensus_impact(self, response: str, previous_arguments: List[DebateArgument]) -> float:
        """Calculate consensus impact of response."""
        if not previous_arguments:
            return 0.0  # No impact for opening arguments

        # Simple consensus detection based on agreement/disagreement keywords
        agreement_words = ['agree', 'concurs', 'valid point', 'well said', 'correctly']
        disagreement_words = ['disagree', 'however', 'but', 'contrary', 'invalid']

        agreement_score = sum(1 for word in agreement_words if word in response.lower())
        disagreement_score = sum(1 for word in disagreement_words if word in response.lower())

        # Normalize to -1 to +1 scale
        total_signals = agreement_score + disagreement_score
        if total_signals == 0:
            return 0.0

        consensus_impact = (agreement_score - disagreement_score) / total_signals
        return max(-1.0, min(1.0, consensus_impact))

    async def generate_round_summary(self, session_id: str, round_number: int, arguments: List[DebateArgument]) -> RoundSummary:
        """Generate summary for a debate round."""
        if not arguments:
            return RoundSummary(
                round_number=round_number,
                arguments_count=0,
                consensus_score=0.0,
                key_points_discussed=[],
                evidence_quality_avg=0.0,
                creativity_level_avg=0.0
            )

        consensus_score = sum(arg.consensus_impact for arg in arguments) / len(arguments)
        evidence_avg = sum(arg.evidence_score for arg in arguments) / len(arguments)
        creativity_avg = sum(arg.creativity_score for arg in arguments) / len(arguments)

        key_points = []
        for arg in arguments:
            # Extract first sentence or first 50 chars as key point
            content = arg.content.strip()
            if content:
                point = content.split('.')[0] if '.' in content else content[:50]
                key_points.append(f"{point}...")

        round_summary = RoundSummary(
            round_number=round_number,
            arguments_count=len(arguments),
            consensus_score=consensus_score,
            key_points_discussed=key_points,
            evidence_quality_avg=evidence_avg,
            creativity_level_avg=creativity_avg
        )

        # Save round summary to database
        try:
            await self.save_debate_round(session_id, round_summary)
        except Exception as e:
            self.logger.warning(f"Failed to save round summary for session {session_id}, round {round_number}: {e}")

        return round_summary

    async def generate_debate_conclusion(self, session: DebateSession) -> DebateConclusion:
        """Generate final debate conclusion."""
        # Analyze all arguments for patterns
        all_arguments = []
        for round_data in session.rounds:
            if 'arguments' in round_data:
                all_arguments.extend(round_data['arguments'])

        if not all_arguments:
            return DebateConclusion(
                conclusion_type="inconclusive",
                winning_position=None,
                confidence_score=0.0,
                key_insights=["No arguments were generated"],
                recommendations=["Retry debate with proper agent configuration"],
                summary="Debate could not be completed due to technical issues.",
                timestamp=datetime.now().isoformat()
            )

        # Determine conclusion type
        if session.consensus_score > session.configuration.consensus_threshold:
            conclusion_type = "consensus"
        elif session.consensus_score > 0.5:
            conclusion_type = "majority"
        elif session.consensus_score > -0.5:
            conclusion_type = "synthesis"
        else:
            conclusion_type = "deadlock"

        # Extract key insights and recommendations using simple analysis
        key_insights = self._extract_key_insights(all_arguments)
        recommendations = self._generate_recommendations(session, all_arguments)

        # Determine winning position (simplified)
        winning_position = self._determine_winning_position(all_arguments)

        summary = self._generate_conclusion_summary(session, conclusion_type, winning_position)

        conclusion = DebateConclusion(
            conclusion_type=conclusion_type,
            winning_position=winning_position,
            confidence_score=abs(session.consensus_score),
            key_insights=key_insights,
            recommendations=recommendations,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )

        # Save conclusion to database
        try:
            await self.save_debate_conclusion(session.session_id, conclusion)
        except Exception as e:
            self.logger.warning(f"Failed to save debate conclusion for session {session.session_id}: {e}")

        return conclusion

    def _extract_key_insights(self, arguments: List[DebateArgument]) -> List[str]:
        """Extract key insights from debate arguments."""
        insights = []

        # Simple keyword-based insight extraction
        key_themes = {
            'regulation': ['regulation', 'govern', 'control', 'oversight'],
            'innovation': ['innovation', 'progress', 'development', 'advance'],
            'safety': ['safety', 'risk', 'harm', 'danger'],
            'ethics': ['ethics', 'moral', 'responsible', 'accountable'],
            'balance': ['balance', 'compromise', 'middle ground', 'hybrid']
        }

        for theme, keywords in key_themes.items():
            mentions = sum(1 for arg in arguments
                          if any(keyword in arg.content.lower() for keyword in keywords))
            if mentions >= len(arguments) * 0.4:  # Mentioned in 40%+ of arguments
                insights.append(f"Strong emphasis on {theme} throughout the debate")

        if not insights:
            insights = ["Debate covered multiple perspectives without clear dominant themes"]

        return insights[:3]  # Limit to top 3 insights

    def _generate_recommendations(self, session: DebateSession, arguments: List[DebateArgument]) -> List[str]:
        """Generate recommendations based on debate outcomes."""
        recommendations = []

        # Quality-based recommendations
        avg_evidence = sum(arg.evidence_score for arg in arguments) / len(arguments)
        if avg_evidence < 0.7:
            recommendations.append("Improve evidence quality in future debates")

        avg_creativity = sum(arg.creativity_score for arg in arguments) / len(arguments)
        if avg_creativity < 0.6:
            recommendations.append("Encourage more creative approaches to problem-solving")

        # Consensus-based recommendations
        if session.consensus_score < 0.5:
            recommendations.append("Consider additional debate rounds for better convergence")
            recommendations.append("Facilitate more direct agent-agent interactions")

        if session.consensus_score > 0.8:
            recommendations.append("High consensus achieved - implement agreed-upon solutions")

        # Agent diversity recommendations
        agent_types = set(arg.agent_type for arg in arguments)
        if len(agent_types) < 3:
            recommendations.append("Include more diverse agent perspectives in future debates")

        return recommendations[:3] if recommendations else ["Debate completed successfully with balanced outcomes"]

    def _determine_winning_position(self, arguments: List[DebateArgument]) -> Optional[str]:
        """Determine the winning position from debate arguments."""
        # Simple position detection based on keywords
        positions = {
            'pro': ['support', 'favor', 'yes', 'approve', 'positive'],
            'con': ['oppose', 'against', 'no', 'reject', 'negative'],
            'balanced': ['balance', 'compromise', 'hybrid', 'middle ground']
        }

        position_scores = {pos: 0 for pos in positions}

        for arg in arguments:
            content = arg.content.lower()
            for pos, keywords in positions.items():
                if any(keyword in content for keyword in keywords):
                    position_scores[pos] += 1

        # Return position with highest score
        winning_pos = max(position_scores.items(), key=lambda x: x[1])
        return winning_pos[0] if winning_pos[1] > 0 else None

    def _generate_conclusion_summary(self, session: DebateSession, conclusion_type: str, winning_position: Optional[str]) -> str:
        """Generate human-readable conclusion summary."""
        rounds = session.current_round
        arguments = session.total_arguments

        position_text = f" with a {winning_position} position" if winning_position else ""

        return f"After {rounds} rounds and {arguments} arguments, the debate reached a {conclusion_type}{position_text} with {abs(session.consensus_score)*100:.1f}% consensus score."

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a debate session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None

        return {
            'session_id': session.session_id,
            'status': session.status.value,
            'current_round': session.current_round,
            'total_arguments': session.total_arguments,
            'consensus_score': session.consensus_score,
            'participants_count': len(session.participants),
            'started_at': session.started_at,
            'completed_at': session.completed_at
        }

    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active debate sessions."""
        return [
            await self.get_session_status(session_id)
            for session_id in self.active_sessions.keys()
        ]

    async def cleanup_session(self, session_id: str) -> bool:
        """Clean up a completed debate session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = DebateStatus.COMPLETED
            session.completed_at = datetime.now().isoformat()

            # Could archive session data here
            del self.active_sessions[session_id]
            self.logger.info(f"Cleaned up debate session: {session_id}")
            return True

        return False

    async def save_debate_session(self, session: DebateSession) -> None:
        """Save debate session to database."""
        try:
            async with get_db_session() as db:
                # Convert dataclasses to database models
                db_session = DebateSession(
                    session_id=session.session_id,
                    status=session.status,
                    debate_topic=session.configuration.debate_topic,
                    problem_statement=session.configuration.problem_statement,
                    premise_area=session.configuration.premise_area,
                    debate_mode=session.configuration.debate_mode,
                    max_rounds=session.configuration.max_rounds,
                    max_iterations_per_round=session.configuration.max_iterations_per_round,
                    iterations_per_agent=session.configuration.iterations_per_agent,
                    consensus_threshold=session.configuration.consensus_threshold,
                    time_limit_per_argument=session.configuration.time_limit_per_argument,
                    response_timeout=session.configuration.response_timeout,
                    selected_agents=session.configuration.selected_agents,
                    agent_roles=session.configuration.agent_roles,
                    ollama_model=session.configuration.ollama_model,
                    temperature=session.configuration.temperature,
                    max_tokens=session.configuration.max_tokens,
                    system_prompt_template=session.configuration.system_prompt_template,
                    enable_detailed_logging=session.configuration.enable_detailed_logging,
                    export_format=session.configuration.export_format,
                    real_time_updates=session.configuration.real_time_updates,
                    debate_rules=asdict(session.configuration.debate_rules),
                    current_round=session.current_round,
                    total_arguments=session.total_arguments,
                    consensus_score=session.consensus_score,
                    started_at=session.started_at,
                    completed_at=session.completed_at
                )

                db.add(db_session)
                await db.commit()
                await db.refresh(db_session)

                logger.info(f"Saved debate session: {session.session_id}")

        except Exception as e:
            logger.error(f"Failed to save debate session {session.session_id}: {e}")
            raise

    async def load_debate_session(self, session_id: str) -> Optional[DebateSession]:
        """Load debate session from database."""
        try:
            async with get_db_session() as db:
                db_session = await db.get(DebateSession, session_id)
                if not db_session:
                    return None

                # Convert back to dataclasses
                configuration = DebateConfiguration(
                    debate_topic=db_session.debate_topic,
                    problem_statement=db_session.problem_statement,
                    premise_area=db_session.premise_area,
                    debate_mode=db_session.debate_mode,
                    max_rounds=db_session.max_rounds,
                    max_iterations_per_round=db_session.max_iterations_per_round,
                    iterations_per_agent=db_session.iterations_per_agent,
                    consensus_threshold=db_session.consensus_threshold,
                    time_limit_per_argument=db_session.time_limit_per_argument,
                    response_timeout=db_session.response_timeout,
                    selected_agents=db_session.selected_agents,
                    agent_roles=db_session.agent_roles,
                    ollama_model=db_session.ollama_model,
                    temperature=db_session.temperature,
                    max_tokens=db_session.max_tokens,
                    system_prompt_template=db_session.system_prompt_template,
                    enable_detailed_logging=db_session.enable_detailed_logging,
                    export_format=db_session.export_format,
                    real_time_updates=db_session.real_time_updates,
                    debate_rules=DebateRules(**db_session.debate_rules)
                )

                session = DebateSession(
                    session_id=db_session.session_id,
                    status=db_session.status,
                    configuration=configuration,
                    current_round=db_session.current_round,
                    total_arguments=db_session.total_arguments,
                    consensus_score=db_session.consensus_score,
                    started_at=db_session.started_at,
                    completed_at=db_session.completed_at
                )

                return session

        except Exception as e:
            logger.error(f"Failed to load debate session {session_id}: {e}")
            return None

    async def save_debate_argument(self, session_id: str, argument: DebateArgument) -> None:
        """Save debate argument to database."""
        try:
            async with get_db_session() as db:
                db_argument = DebateArgument(
                    session_id=session_id,
                    argument_id=argument.id,
                    round_number=argument.round_number,
                    content=argument.content,
                    timestamp=argument.timestamp.isoformat(),
                    evidence_score=argument.evidence_score,
                    creativity_score=argument.creativity_score,
                    fallacies_detected=argument.fallacies_detected,
                    consensus_impact=argument.consensus_impact
                )

                db.add(db_argument)
                await db.commit()

                logger.debug(f"Saved debate argument: {argument.id}")

        except Exception as e:
            logger.error(f"Failed to save debate argument {argument.id}: {e}")

    async def save_debate_round(self, session_id: str, round_summary: RoundSummary) -> None:
        """Save debate round summary to database."""
        try:
            async with get_db_session() as db:
                db_round = DebateRound(
                    session_id=session_id,
                    round_number=round_summary.round_number,
                    arguments_count=round_summary.arguments_count,
                    consensus_score=round_summary.consensus_score,
                    evidence_quality_avg=round_summary.evidence_quality_avg,
                    creativity_level_avg=round_summary.creativity_level_avg,
                    key_points_discussed=round_summary.key_points_discussed
                )

                db.add(db_round)
                await db.commit()

                logger.debug(f"Saved debate round: {session_id} - Round {round_summary.round_number}")

        except Exception as e:
            logger.error(f"Failed to save debate round {session_id} - Round {round_summary.round_number}: {e}")

    async def save_debate_conclusion(self, session_id: str, conclusion: DebateConclusion) -> None:
        """Save debate conclusion to database."""
        try:
            async with get_db_session() as db:
                db_conclusion = DebateConclusion(
                    session_id=session_id,
                    conclusion_type=conclusion.conclusion_type,
                    winning_position=conclusion.winning_position,
                    confidence_score=conclusion.confidence_score,
                    final_consensus_score=conclusion.confidence_score,  # Using confidence as final score
                    key_insights=conclusion.key_insights,
                    recommendations=conclusion.recommendations,
                    summary=conclusion.summary,
                    total_rounds=0,  # Would need to be calculated
                    total_arguments=0  # Would need to be calculated
                )

                db.add(db_conclusion)
                await db.commit()

                logger.info(f"Saved debate conclusion: {session_id}")

        except Exception as e:
            logger.error(f"Failed to save debate conclusion {session_id}: {e}")

    async def _execute_debate_background(self, session_id: str) -> None:
        """Execute debate rounds in background (placeholder for future implementation)"""
        logger.info(f"Background execution started for session: {session_id}")
        # TODO: Implement background debate execution
        # This would involve executing rounds asynchronously
        pass


# Global service instance
_debate_service = None

def get_debate_service() -> DebateService:
    """Get singleton debate service instance."""
    global _debate_service
    if _debate_service is None:
        _debate_service = DebateService()
    return _debate_service
