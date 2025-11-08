"""
Multi-Agent Debate System API

Provides REST endpoints and WebSocket support for autonomous multi-agent debates
with specialized argumentation agents.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pydantic import BaseModel, Field

from app.core.base_agent import BaseAgent, AgentCapability
from app.models.messaging import TaskEnvelope, create_task_result_envelope

logger = logging.getLogger(__name__)


class DebateMode(Enum):
    """Debate operational modes."""
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


class ArgumentType(Enum):
    """Types of arguments in debate."""
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    COUNTER = "counter"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"


class DebateArgument(BaseModel):
    """Represents a single argument in the debate."""
    argument_id: str
    participant_id: str
    participant_name: str
    content: str
    argument_type: ArgumentType
    logical_strength: float = Field(ge=0.0, le=1.0, description="Logical strength score (0.0-1.0)")
    rhetorical_strength: float = Field(ge=0.0, le=1.0, description="Rhetorical strength score (0.0-1.0)")
    evidence_quality: float = Field(ge=0.0, le=1.0, description="Evidence quality score (0.0-1.0)")
    fallacies: List[str] = Field(default_factory=list, description="Identified logical fallacies")
    responses: List[str] = Field(default_factory=list, description="Response argument IDs")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Argument timestamp")


@dataclass
class DebateRound:
    """Represents a single round of debate."""
    round_number: int
    timestamp: str
    arguments: List[DebateArgument] = field(default_factory=list)
    consensus_metrics: Dict[str, Any] = field(default_factory=lambda: {
        "agreement_level": 0.0,
        "convergence_trend": "stable",
        "dominant_viewpoints": []
    })


@dataclass
class DebateParticipant:
    """Represents a participant in the debate."""
    agent_id: str
    agent_name: str
    agent_type: str
    specialization: str
    position: str = "neutral"
    confidence_score: float = 0.5
    arguments_made: int = 0
    rebuttals_given: int = 0
    fallacies_identified: int = 0
    strength_score: float = 0.5


@dataclass
class DebateConfiguration:
    """Configuration for a debate session."""
    debate_topic: str
    problem_statement: str
    debate_mode: DebateMode
    max_rounds: int
    max_iterations_per_round: int
    consensus_threshold: float
    time_limit_per_argument: int
    selected_agents: List[str]
    debate_rules: Dict[str, Any]


@dataclass
class DebateSession:
    """Represents an active debate session."""
    session_id: str
    status: DebateStatus
    configuration: DebateConfiguration
    participants: List[DebateParticipant] = field(default_factory=list)
    rounds: List[DebateRound] = field(default_factory=list)
    current_round: int = 0
    total_arguments: int = 0
    consensus_score: float = 0.0
    winning_position: Optional[str] = None
    conclusion: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class DebateOrchestrator:
    """
    Orchestrates multi-agent debate sessions with specialized argumentation agents.
    """

    def __init__(self):
        self.active_sessions: Dict[str, DebateSession] = {}
        self.websocket_clients: Dict[str, Any] = {}

        # Debate agent specializations and their capabilities
        self.agent_specializations = {
            "11": {
                "name": "Logical Analyst",
                "type": "logical_analyst",
                "specialization": "Logical validity, formal reasoning, identifying fallacies",
                "strengths": ["formal_logic", "syllogisms", "fallacy_detection", "proof_theory"],
                "position_bias": "neutral"
            },
            "12": {
                "name": "Argumentation Specialist",
                "type": "argumentation_specialist",
                "specialization": "Argumentation, persuasive techniques, rhetorical analysis",
                "strengths": ["rhetorical_devices", "persuasive_appeals", "debate_structure", "audience_analysis"],
                "position_bias": "adaptive"
            },
            "13": {
                "name": "Conceptual Analyst",
                "type": "conceptual_analyst",
                "specialization": "Conceptual analysis, assumptions, philosophical frameworks",
                "strengths": ["philosophical_analysis", "conceptual_clarity", "assumption_testing", "framework_evaluation"],
                "position_bias": "neutral"
            },
            "14": {
                "name": "Critical Thinker",
                "type": "critical_thinker",
                "specialization": "Critical thinking, devil's advocate, identifying weaknesses",
                "strengths": ["problem_identification", "counter_argumentation", "risk_assessment", "gap_analysis"],
                "position_bias": "oppositional"
            },
            "15": {
                "name": "Linguistic Analyst",
                "type": "linguistic_analyst",
                "specialization": "Linguistic structure, semantics, wordplay, etymology",
                "strengths": ["language_precision", "semantic_analysis", "etymological_insights", "linguistic_ambiguity"],
                "position_bias": "neutral"
            },
            "16": {
                "name": "Mathematical Thinker",
                "type": "mathematical_thinker",
                "specialization": "Mathematical relationships, formal structures, patterns",
                "strengths": ["pattern_recognition", "formal_structures", "quantitative_analysis", "logical_consistency"],
                "position_bias": "neutral"
            },
            "17": {
                "name": "Creative Innovator",
                "type": "creative_innovator",
                "specialization": "Creative solutions, unconventional thinking, associations",
                "strengths": ["creative_synthesis", "unconventional_approaches", "association_mapping", "innovative_solutions"],
                "position_bias": "creative"
            },
            "18": {
                "name": "Integration Specialist",
                "type": "integration_specialist",
                "specialization": "Integration, synthesis, reconciling viewpoints",
                "strengths": ["viewpoint_synthesis", "consensus_building", "perspective_integration", "balanced_analysis"],
                "position_bias": "synthetic"
            },
            "19": {
                "name": "Strategic Planner",
                "type": "strategic_planner",
                "specialization": "Long-term thinking, adaptability, scenario planning",
                "strengths": ["strategic_foresight", "scenario_planning", "adaptive_strategies", "long_term_consequences"],
                "position_bias": "strategic"
            }
        }

    async def initialize_debate(self, configuration: DebateConfiguration) -> DebateSession:
        """
        Initialize a new debate session with selected agents.
        """
        session_id = str(uuid.uuid4())

        # Create participants from selected agents
        participants = []
        for agent_id in configuration.selected_agents:
            if agent_id in self.agent_specializations:
                spec = self.agent_specializations[agent_id]
                participant = DebateParticipant(
                    agent_id=agent_id,
                    agent_name=spec["name"],
                    agent_type=spec["type"],
                    specialization=spec["specialization"]
                )
                participants.append(participant)

        session = DebateSession(
            session_id=session_id,
            status=DebateStatus.INITIALIZED,
            configuration=configuration,
            participants=participants
        )

        self.active_sessions[session_id] = session

        # Broadcast session initialization
        await self._broadcast_debate_event("debate_started", {
            "session": self._session_to_dict(session)
        })

        logger.info(f"Initialized debate session {session_id} with {len(participants)} participants")
        return session

    async def start_debate(self, session_id: str) -> bool:
        """
        Start an initialized debate session.
        """
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        session.status = DebateStatus.ACTIVE
        session.started_at = datetime.now().isoformat()

        # Start debate execution in background
        asyncio.create_task(self._execute_debate(session))

        return True

    async def control_debate(self, session_id: str, action: str) -> bool:
        """
        Control debate session (pause, resume, stop).
        """
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]

        if action == "pause" and session.status == DebateStatus.ACTIVE:
            session.status = DebateStatus.PAUSED
        elif action == "resume" and session.status == DebateStatus.PAUSED:
            session.status = DebateStatus.ACTIVE
        elif action == "stop":
            session.status = DebateStatus.COMPLETED
            session.completed_at = datetime.now().isoformat()

        return True

    async def _execute_debate(self, session: DebateSession):
        """
        Execute the debate rounds autonomously.
        """
        try:
            while (session.status == DebateStatus.ACTIVE and
                   session.current_round < session.configuration.max_rounds):

                session.current_round += 1
                round_arguments = await self._execute_round(session)

                # Create round summary
                round_summary = DebateRound(
                    round_number=session.current_round,
                    timestamp=datetime.now().isoformat(),
                    arguments=round_arguments
                )

                # Calculate consensus metrics
                round_summary.consensus_metrics = self._calculate_consensus_metrics(round_arguments)

                session.rounds.append(round_summary)
                session.total_arguments += len(round_arguments)

                # Broadcast round completion
                await self._broadcast_debate_event("round_completed", {
                    "round": self._round_to_dict(round_summary)
                })

                # Check for consensus
                if round_summary.consensus_metrics["agreement_level"] >= session.configuration.consensus_threshold:
                    session.status = DebateStatus.CONSENSUS_REACHED
                    session.consensus_score = round_summary.consensus_metrics["agreement_level"]
                    session.conclusion = await self._generate_conclusion(session)
                    session.completed_at = datetime.now().isoformat()

                    await self._broadcast_debate_event("consensus_reached", {
                        "consensus_score": session.consensus_score,
                        "winning_position": session.winning_position,
                        "conclusion": session.conclusion
                    })
                    break

                # Wait between rounds
                await asyncio.sleep(2)

            # Debate completed normally
            if session.status == DebateStatus.ACTIVE:
                session.status = DebateStatus.COMPLETED
                session.completed_at = datetime.now().isoformat()
                session.conclusion = await self._generate_conclusion(session)

                await self._broadcast_debate_event("debate_completed", {})

        except Exception as e:
            logger.error(f"Error executing debate {session.session_id}: {e}")
            session.status = DebateStatus.COMPLETED
            session.completed_at = datetime.now().isoformat()

    async def _execute_round(self, session: DebateSession) -> List[DebateArgument]:
        """
        Execute a single round of debate.
        """
        arguments = []

        # Each participant makes an argument based on their specialization
        for participant in session.participants:
            if session.status != DebateStatus.ACTIVE:
                break

            try:
                argument = await self._generate_argument(participant, session, len(arguments))
                arguments.append(argument)

                # Update participant statistics
                participant.arguments_made += 1

                # Broadcast argument
                await self._broadcast_debate_event("argument_made", {
                    "argument": self._argument_to_dict(argument)
                })

                # Simulate processing time
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error generating argument for {participant.agent_id}: {e}")

        return arguments

    async def _generate_argument(self, participant: DebateParticipant, session: DebateSession,
                                argument_index: int) -> DebateArgument:
        """
        Generate an argument based on participant's specialization.
        """
        # Determine argument type based on position in round
        if argument_index == 0:
            arg_type = ArgumentType.OPENING
        elif argument_index < len(session.participants) // 2:
            arg_type = ArgumentType.REBUTTAL
        elif argument_index < len(session.participants) - 1:
            arg_type = ArgumentType.COUNTER
        else:
            arg_type = ArgumentType.SYNTHESIS

        # Generate argument content based on specialization
        content = await self._generate_argument_content(participant, session, arg_type)

        # Evaluate argument quality
        logical_strength, rhetorical_strength, evidence_quality, fallacies = await self._evaluate_argument(content)

        argument = DebateArgument(
            argument_id=str(uuid.uuid4()),
            participant_id=participant.agent_id,
            participant_name=participant.agent_name,
            content=content,
            argument_type=arg_type,
            logical_strength=logical_strength,
            rhetorical_strength=rhetorical_strength,
            evidence_quality=evidence_quality,
            fallacies=fallacies
        )

        return argument

    async def _generate_argument_content(self, participant: DebateParticipant,
                                       session: DebateSession, arg_type: ArgumentType) -> str:
        """
        Generate argument content based on participant's specialization.
        """
        agent_spec = self.agent_specializations[participant.agent_id]
        specialization = agent_spec["specialization"].lower()

        # Generate content based on specialization type
        if "logical" in specialization:
            content = self._generate_logical_argument(session.configuration, arg_type)
        elif "argumentation" in specialization or "persuasive" in specialization:
            content = self._generate_rhetorical_argument(session.configuration, arg_type)
        elif "conceptual" in specialization or "philosophical" in specialization:
            content = self._generate_conceptual_argument(session.configuration, arg_type)
        elif "critical" in specialization or "devil" in specialization:
            content = self._generate_critical_argument(session.configuration, arg_type)
        elif "linguistic" in specialization or "semantic" in specialization:
            content = self._generate_linguistic_argument(session.configuration, arg_type)
        elif "mathematical" in specialization or "formal" in specialization:
            content = self._generate_mathematical_argument(session.configuration, arg_type)
        elif "creative" in specialization or "unconventional" in specialization:
            content = self._generate_creative_argument(session.configuration, arg_type)
        elif "integration" in specialization or "synthesis" in specialization:
            content = self._generate_integration_argument(session.configuration, arg_type)
        elif "strategic" in specialization or "long-term" in specialization:
            content = self._generate_strategic_argument(session.configuration, arg_type)
        else:
            content = self._generate_general_argument(session.configuration, arg_type)

        return content

    def _generate_logical_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate logical argument with formal reasoning."""
        return f"As a logical analyst, I examine the formal structure of this debate. The proposition '{config.debate_topic}' can be analyzed through deductive reasoning. If we accept the premises stated in the problem statement, then the conclusion follows necessarily. However, I identify potential logical fallacies in assuming that correlation implies causation in the given context."

    def _generate_rhetorical_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate persuasive rhetorical argument."""
        return f"From a rhetorical perspective, the debate topic '{config.debate_topic}' requires careful consideration of audience appeal. Using ethos, pathos, and logos, I argue that the most persuasive position considers both emotional resonance and logical consistency. The problem statement reveals opportunities for compelling narrative construction."

    def _generate_conceptual_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate conceptual/philosophical argument."""
        return f"Philosophically examining '{config.debate_topic}', I identify key conceptual frameworks that shape our understanding. The problem statement reveals underlying assumptions about reality, knowledge, and value. A phenomenological approach suggests that multiple valid perspectives can coexist within different conceptual paradigms."

    def _generate_critical_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate critical analysis argument."""
        return f"Applying critical thinking to '{config.debate_topic}', I identify several potential weaknesses in the current framing. The problem statement contains unexamined assumptions that could undermine the entire argument. Specifically, I question the validity of the evidence presented and identify gaps in the reasoning chain."

    def _generate_linguistic_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate linguistic analysis argument."""
        return f"Linguistically analyzing '{config.debate_topic}', I note the semantic precision required for accurate discourse. The problem statement employs specific terminology that carries etymological weight. Word choice here reveals underlying cognitive frameworks, and alternative semantic framings could reveal previously obscured perspectives."

    def _generate_mathematical_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate mathematical/formal argument."""
        return f"Applying mathematical reasoning to '{config.debate_topic}', I identify formal structures and patterns. The problem can be modeled as a decision tree with probabilistic outcomes. Using set theory, we can see that the solution space contains multiple valid intersections, suggesting that partial resolutions may be mathematically optimal."

    def _generate_creative_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate creative/unconventional argument."""
        return f"Thinking unconventionally about '{config.debate_topic}', I propose an innovative synthesis that transcends traditional binary thinking. What if we consider the problem as a fractal pattern, where each level of analysis reveals new creative possibilities? The problem statement becomes a canvas for associative leaps that conventional logic might reject."

    def _generate_integration_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate integrative synthesis argument."""
        return f"Synthesizing perspectives on '{config.debate_topic}', I find that seemingly opposing viewpoints contain complementary truths. The problem statement reveals a false dichotomy that integration can resolve. By reconciling these perspectives, we arrive at a more comprehensive understanding that honors the validity of multiple approaches."

    def _generate_strategic_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate strategic long-term argument."""
        return f"Strategically evaluating '{config.debate_topic}' from a long-term perspective, I consider future implications and adaptive capacity. The problem statement addresses immediate concerns but may overlook emergent properties that develop over time. A strategic approach requires scenario planning that anticipates multiple future trajectories."

    def _generate_general_argument(self, config: DebateConfiguration, arg_type: ArgumentType) -> str:
        """Generate general balanced argument."""
        return f"Considering '{config.debate_topic}' comprehensively, I weigh multiple factors from the problem statement. Each perspective offers valuable insights, and the optimal approach likely involves balancing competing priorities while maintaining flexibility for future adjustments."

    async def _evaluate_argument(self, content: str) -> tuple[float, float, float, List[str]]:
        """
        Evaluate argument quality and identify fallacies.
        """
        # Simple heuristic evaluation (in real implementation, this would use ML models)
        logical_strength = min(1.0, len(content.split()) / 100)  # Based on length/complexity
        rhetorical_strength = 0.7  # Placeholder
        evidence_quality = 0.6  # Placeholder

        # Identify common fallacies (simplified)
        fallacies = []
        if "everyone" in content.lower() and "thinks" in content.lower():
            fallacies.append("ad populum")
        if "because" in content.lower() and len(content.split()) < 20:
            fallacies.append("post hoc ergo propter hoc")

        return logical_strength, rhetorical_strength, evidence_quality, fallacies

    def _calculate_consensus_metrics(self, arguments: List[DebateArgument]) -> Dict[str, Any]:
        """
        Calculate consensus metrics for a round.
        """
        if not arguments:
            return {"agreement_level": 0.0, "convergence_trend": "stable", "dominant_viewpoints": []}

        # Simple consensus calculation based on argument types and strengths
        synthesis_count = sum(1 for arg in arguments if arg.argument_type == ArgumentType.SYNTHESIS)
        counter_count = sum(1 for arg in arguments if arg.argument_type == ArgumentType.COUNTER)

        agreement_level = synthesis_count / len(arguments)
        convergence_trend = "increasing" if agreement_level > 0.5 else "stable"

        # Identify dominant viewpoints (simplified)
        dominant_viewpoints = ["synthesis"] if synthesis_count > counter_count else ["debate"]

        return {
            "agreement_level": agreement_level,
            "convergence_trend": convergence_trend,
            "dominant_viewpoints": dominant_viewpoints
        }

    async def _generate_conclusion(self, session: DebateSession) -> str:
        """
        Generate final conclusion based on debate results.
        """
        total_rounds = len(session.rounds)
        final_agreement = session.rounds[-1].consensus_metrics["agreement_level"] if session.rounds else 0

        if final_agreement >= session.configuration.consensus_threshold:
            return f"After {total_rounds} rounds of debate, the participants reached consensus with {final_agreement:.1%} agreement. The integrated perspective synthesizes multiple viewpoints into a comprehensive solution."
        else:
            return f"After {total_rounds} rounds of debate, no consensus was reached (final agreement: {final_agreement:.1%}). The debate revealed fundamental differences that require further exploration."

    def _session_to_dict(self, session: DebateSession) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": session.session_id,
            "status": session.status.value,
            "configuration": {
                "debate_topic": session.configuration.debate_topic,
                "problem_statement": session.configuration.problem_statement,
                "debate_mode": session.configuration.debate_mode.value,
                "max_rounds": session.configuration.max_rounds,
                "consensus_threshold": session.configuration.consensus_threshold,
                "selected_agents": session.configuration.selected_agents
            },
            "participants": [{
                "agent_id": p.agent_id,
                "agent_name": p.agent_name,
                "agent_type": p.agent_type,
                "specialization": p.specialization,
                "arguments_made": p.arguments_made,
                "strength_score": p.strength_score
            } for p in session.participants],
            "current_round": session.current_round,
            "total_arguments": session.total_arguments,
            "consensus_score": session.consensus_score,
            "started_at": session.started_at
        }

    def _round_to_dict(self, round_obj: DebateRound) -> Dict[str, Any]:
        """Convert round to dictionary."""
        return {
            "round_number": round_obj.round_number,
            "timestamp": round_obj.timestamp,
            "arguments": [self._argument_to_dict(arg) for arg in round_obj.arguments],
            "consensus_metrics": round_obj.consensus_metrics
        }

    def _argument_to_dict(self, argument: DebateArgument) -> Dict[str, Any]:
        """Convert argument to dictionary."""
        return {
            "argument_id": argument.argument_id,
            "participant_id": argument.participant_id,
            "participant_name": argument.participant_name,
            "content": argument.content,
            "argument_type": argument.argument_type.value,
            "logical_strength": argument.logical_strength,
            "rhetorical_strength": argument.rhetorical_strength,
            "evidence_quality": argument.evidence_quality,
            "fallacies": argument.fallacies,
            "timestamp": argument.timestamp
        }

    async def _broadcast_debate_event(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast debate events to WebSocket clients.
        """
        message = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        # Send to all connected WebSocket clients
        disconnected_clients = []
        for client_id, client in self.websocket_clients.items():
            try:
                await client.send_json(message)
            except Exception:
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del self.websocket_clients[client_id]


# Global debate orchestrator instance
debate_orchestrator = DebateOrchestrator()
