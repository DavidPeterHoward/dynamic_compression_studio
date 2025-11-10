"""
Debate system database models for Ollama-powered multi-agent debates.

This module provides SQLAlchemy models for storing debate sessions,
participants, arguments, and analytics.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.database.base import AsyncBase, TimestampMixin


class DebateStatus(PyEnum):
    """Debate session status enumeration."""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CONSENSUS_REACHED = "consensus_reached"


class DebateMode(PyEnum):
    """Debate execution mode enumeration."""
    STRUCTURED = "structured"
    FREEFORM = "freeform"
    AUTONOMOUS = "autonomous"


class DebateSession(AsyncBase, TimestampMixin):
    """Database model for debate sessions."""

    __tablename__ = "debate_sessions"

    # Basic session information
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(Enum(DebateStatus), default=DebateStatus.INITIALIZED, nullable=False)

    # Debate configuration
    debate_topic = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=False)
    premise_area = Column(Text, nullable=False)
    debate_mode = Column(Enum(DebateMode), default=DebateMode.STRUCTURED, nullable=False)
    max_rounds = Column(Integer, default=5, nullable=False)
    max_iterations_per_round = Column(Integer, default=3, nullable=False)
    iterations_per_agent = Column(Integer, default=2, nullable=False)
    consensus_threshold = Column(Float, default=0.8, nullable=False)
    time_limit_per_argument = Column(Integer, default=60, nullable=False)
    response_timeout = Column(Integer, default=30, nullable=False)
    selected_agents = Column(JSON, nullable=False)  # List of agent IDs
    agent_roles = Column(JSON, nullable=True)  # Dict mapping agent_id to role
    ollama_model = Column(String(100), default="llama2:7b", nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, default=512, nullable=False)
    system_prompt_template = Column(Text, nullable=True)
    enable_detailed_logging = Column(Boolean, default=True, nullable=False)
    export_format = Column(String(10), default="json", nullable=False)
    real_time_updates = Column(Boolean, default=True, nullable=False)

    # Debate rules (stored as JSON)
    debate_rules = Column(JSON, nullable=False)

    # Execution state
    current_round = Column(Integer, default=0, nullable=False)
    total_arguments = Column(Integer, default=0, nullable=False)
    consensus_score = Column(Float, default=0.0, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    participants = relationship("DebateParticipant", back_populates="session", cascade="all, delete-orphan")
    rounds = relationship("DebateRound", back_populates="session", cascade="all, delete-orphan")
    arguments = relationship("DebateArgument", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DebateSession(session_id='{self.session_id}', status='{self.status.value}', topic='{self.debate_topic[:50]}...')>"


class DebateParticipant(AsyncBase, TimestampMixin):
    """Database model for debate participants."""

    __tablename__ = "debate_participants"

    # Foreign key to session
    session_id = Column(String(255), ForeignKey("debate_sessions.session_id"), nullable=False)

    # Agent information
    agent_id = Column(String(255), nullable=False)
    agent_name = Column(String(255), nullable=False)
    agent_type = Column(String(100), nullable=False)
    specialization = Column(Text, nullable=True)
    position = Column(String(50), default="neutral", nullable=False)

    # Performance metrics
    confidence_score = Column(Float, default=0.5, nullable=False)
    arguments_made = Column(Integer, default=0, nullable=False)
    rebuttals_given = Column(Integer, default=0, nullable=False)
    fallacies_identified = Column(Integer, default=0, nullable=False)
    strength_score = Column(Float, default=0.5, nullable=False)

    # Relationships
    session = relationship("DebateSession", back_populates="participants")
    arguments = relationship("DebateArgument", back_populates="participant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DebateParticipant(agent_id='{self.agent_id}', name='{self.agent_name}', session='{self.session_id}')>"


class DebateRound(AsyncBase, TimestampMixin):
    """Database model for debate rounds."""

    __tablename__ = "debate_rounds"

    # Foreign key to session
    session_id = Column(String(255), ForeignKey("debate_sessions.session_id"), nullable=False)

    # Round information
    round_number = Column(Integer, nullable=False)
    arguments_count = Column(Integer, default=0, nullable=False)
    consensus_score = Column(Float, default=0.0, nullable=False)
    evidence_quality_avg = Column(Float, default=0.0, nullable=False)
    creativity_level_avg = Column(Float, default=0.0, nullable=False)

    # Round summary
    key_points_discussed = Column(JSON, nullable=True)  # List of key points
    round_summary = Column(Text, nullable=True)

    # Relationships
    session = relationship("DebateSession", back_populates="rounds")
    arguments = relationship("DebateArgument", back_populates="round_info", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DebateRound(session='{self.session_id}', round={self.round_number}, consensus={self.consensus_score:.2f})>"


class DebateArgument(AsyncBase, TimestampMixin):
    """Database model for individual debate arguments."""

    __tablename__ = "debate_arguments"

    # Foreign keys
    session_id = Column(String(255), ForeignKey("debate_sessions.session_id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("debate_participants.id"), nullable=False)
    round_id = Column(Integer, ForeignKey("debate_rounds.id"), nullable=True)

    # Argument information
    argument_id = Column(String(255), unique=True, index=True, nullable=False)
    round_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Quality metrics
    evidence_score = Column(Float, default=0.0, nullable=False)
    creativity_score = Column(Float, default=0.0, nullable=False)
    fallacies_detected = Column(Integer, default=0, nullable=False)
    consensus_impact = Column(Float, default=0.0, nullable=False)

    # Additional metadata
    word_count = Column(Integer, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    argument_type = Column(String(50), nullable=True)  # e.g., "proposition", "counter", "rebuttal"

    # Relationships
    session = relationship("DebateSession", back_populates="arguments")
    participant = relationship("DebateParticipant", back_populates="arguments")
    round_info = relationship("DebateRound", back_populates="arguments")

    def __repr__(self):
        return f"<DebateArgument(id='{self.argument_id}', participant='{self.participant.agent_name if self.participant else 'Unknown'}', round={self.round_number})>"


class DebateConclusion(AsyncBase, TimestampMixin):
    """Database model for debate conclusions."""

    __tablename__ = "debate_conclusions"

    # Foreign key to session
    session_id = Column(String(255), ForeignKey("debate_sessions.session_id"), unique=True, nullable=False)

    # Conclusion results
    conclusion_type = Column(String(50), nullable=False)  # consensus, majority, deadlock, synthesis
    winning_position = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=False)
    final_consensus_score = Column(Float, nullable=False)

    # Analysis results
    key_insights = Column(JSON, nullable=True)  # List of key insights
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    summary = Column(Text, nullable=False)

    # Performance metrics
    total_rounds = Column(Integer, nullable=False)
    total_arguments = Column(Integer, nullable=False)
    average_evidence_score = Column(Float, nullable=True)
    average_creativity_score = Column(Float, nullable=True)
    dominant_agent = Column(String(255), nullable=True)

    # Relationships
    session = relationship("DebateSession", back_populates="conclusion")

    def __repr__(self):
        return f"<DebateConclusion(session='{self.session_id}', type='{self.conclusion_type}', confidence={self.confidence_score:.2f})>"


class DebateAnalytics(AsyncBase, TimestampMixin):
    """Database model for debate analytics and statistics."""

    __tablename__ = "debate_analytics"

    # Foreign key to session
    session_id = Column(String(255), ForeignKey("debate_sessions.session_id"), nullable=False)

    # Analytics type
    analytics_type = Column(String(50), nullable=False)  # e.g., "participation", "quality", "consensus"
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)

    # Additional metadata
    round_number = Column(Integer, nullable=True)
    agent_id = Column(String(255), nullable=True)
    time_window = Column(String(50), nullable=True)  # e.g., "round", "session", "cumulative"

    # Relationships
    session = relationship("DebateSession", back_populates="analytics")

    def __repr__(self):
        return f"<DebateAnalytics(session='{self.session_id}', type='{self.analytics_type}', metric='{self.metric_name}', value={self.metric_value})>"


# Update DebateSession to include the new relationships
DebateSession.conclusion = relationship("DebateConclusion", back_populates="session", cascade="all, delete-orphan")
DebateSession.analytics = relationship("DebateAnalytics", back_populates="session", cascade="all, delete-orphan")


# Export all models
__all__ = [
    "DebateSession",
    "DebateParticipant",
    "DebateRound",
    "DebateArgument",
    "DebateConclusion",
    "DebateAnalytics",
    "DebateStatus",
    "DebateMode"
]
