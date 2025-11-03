"""
Database models for prompt storage, management, and evaluation.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid

from app.database.base import AsyncBase, TimestampMixin


class PromptType(str, Enum):
    """Types of prompts."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TEMPLATE = "template"
    WORKFLOW = "workflow"
    CHAIN = "chain"


class PromptCategory(str, Enum):
    """Categories for prompt organization."""
    COMPRESSION = "compression"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    OPTIMIZATION = "optimization"
    EVALUATION = "evaluation"
    WORKFLOW = "workflow"
    CUSTOM = "custom"


class EvaluationStatus(str, Enum):
    """Status of prompt evaluation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Prompt(AsyncBase, TimestampMixin):
    """Main table for storing prompts."""
    
    __tablename__ = "prompts"
    
    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Prompt content and metadata
    content = Column(Text, nullable=False)
    prompt_type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    
    # Versioning and organization
    version = Column(String(20), default="1.0.0")
    parent_id = Column(String(36), ForeignKey("prompts.id"), nullable=True)
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Tags and categorization
    tags = Column(JSON, nullable=True)  # List of tags
    keywords = Column(JSON, nullable=True)  # List of keywords for semantic search
    
    # Usage and performance metrics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    average_response_time = Column(Float, nullable=True)
    token_efficiency = Column(Float, nullable=True)
    
    # Semantic analysis
    semantic_vector = Column(JSON, nullable=True)  # Embedding vector
    complexity_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    
    # Relationships
    parent = relationship("Prompt", remote_side=[id])
    children = relationship("Prompt", back_populates="parent")
    evaluations = relationship("PromptEvaluation", back_populates="prompt", cascade="all, delete-orphan")
    workflows = relationship("PromptWorkflow", back_populates="prompts", secondary="prompt_workflow_associations")
    
    def __repr__(self):
        return f"<Prompt(id='{self.id}', name='{self.name}', type='{self.prompt_type}')>"


class PromptTemplate(AsyncBase, TimestampMixin):
    """Templates for prompt generation."""
    
    __tablename__ = "prompt_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content with placeholders
    template_content = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)  # Parameter definitions
    default_values = Column(JSON, nullable=True)
    
    # Template metadata
    category = Column(String(50), nullable=False)
    tags = Column(JSON, nullable=True)
    is_public = Column(Boolean, default=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<PromptTemplate(id='{self.id}', name='{self.name}')>"


class PromptWorkflow(AsyncBase, TimestampMixin):
    """Workflows that combine multiple prompts."""
    
    __tablename__ = "prompt_workflows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Workflow definition
    workflow_definition = Column(JSON, nullable=False)  # Workflow steps and logic
    execution_order = Column(JSON, nullable=False)  # Order of prompt execution
    conditional_logic = Column(JSON, nullable=True)  # Conditional branching
    
    # Workflow metadata
    category = Column(String(50), nullable=False)
    tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Performance metrics
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    average_execution_time = Column(Float, nullable=True)
    
    # Relationships
    prompts = relationship("Prompt", secondary="prompt_workflow_associations", back_populates="workflows")
    executions = relationship("PromptWorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PromptWorkflow(id='{self.id}', name='{self.name}')>"


class PromptWorkflowAssociation(AsyncBase):
    """Association table for prompts and workflows."""
    
    __tablename__ = "prompt_workflow_associations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("prompt_workflows.id"), nullable=False)
    prompt_id = Column(String(36), ForeignKey("prompts.id"), nullable=False)
    
    # Association metadata
    step_order = Column(Integer, nullable=False)
    is_conditional = Column(Boolean, default=False)
    condition_expression = Column(Text, nullable=True)
    
    # Relationships
    workflow = relationship("PromptWorkflow")
    prompt = relationship("Prompt")
    
    def __repr__(self):
        return f"<PromptWorkflowAssociation(workflow_id='{self.workflow_id}', prompt_id='{self.prompt_id}')>"


class PromptEvaluation(AsyncBase, TimestampMixin):
    """Evaluation results for prompts across different models."""
    
    __tablename__ = "prompt_evaluations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id = Column(String(36), ForeignKey("prompts.id"), nullable=False)
    
    # Model and evaluation metadata
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=True)
    evaluation_type = Column(String(50), nullable=False)  # automated, human, hybrid
    
    # Evaluation metrics
    accuracy_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    creativity_score = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)
    efficiency_score = Column(Float, nullable=True)
    
    # Performance metrics
    response_time = Column(Float, nullable=True)
    token_usage = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    
    # Evaluation details
    test_cases = Column(JSON, nullable=True)  # Test cases used
    evaluation_results = Column(JSON, nullable=True)  # Detailed results
    feedback = Column(Text, nullable=True)
    
    # Status and metadata
    status = Column(String(20), default=EvaluationStatus.PENDING)
    evaluator = Column(String(100), nullable=True)  # Who/what performed evaluation
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prompt = relationship("Prompt", back_populates="evaluations")
    
    def __repr__(self):
        return f"<PromptEvaluation(id='{self.id}', prompt_id='{self.prompt_id}', model='{self.model_name}')>"


class PromptWorkflowExecution(AsyncBase, TimestampMixin):
    """Execution logs for prompt workflows."""
    
    __tablename__ = "prompt_workflow_executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("prompt_workflows.id"), nullable=False)
    
    # Execution metadata
    execution_id = Column(String(36), nullable=False, index=True)
    status = Column(String(20), default=EvaluationStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Execution results
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    intermediate_results = Column(JSON, nullable=True)
    
    # Performance metrics
    total_execution_time = Column(Float, nullable=True)
    step_execution_times = Column(JSON, nullable=True)
    token_usage = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_step = Column(String(100), nullable=True)
    
    # Relationships
    workflow = relationship("PromptWorkflow", back_populates="executions")
    
    def __repr__(self):
        return f"<PromptWorkflowExecution(id='{self.id}', workflow_id='{self.workflow_id}')>"


class PromptChain(AsyncBase, TimestampMixin):
    """Chains of prompts for complex workflows."""
    
    __tablename__ = "prompt_chains"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Chain definition
    chain_definition = Column(JSON, nullable=False)  # Chain structure and logic
    execution_strategy = Column(String(50), nullable=False)  # sequential, parallel, conditional
    
    # Chain metadata
    category = Column(String(50), nullable=False)
    tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Performance metrics
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    average_execution_time = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<PromptChain(id='{self.id}', name='{self.name}')>"


class PromptSemanticAnalysis(AsyncBase, TimestampMixin):
    """Semantic analysis results for prompts."""
    
    __tablename__ = "prompt_semantic_analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id = Column(String(36), ForeignKey("prompts.id"), nullable=False)
    
    # Semantic analysis results
    semantic_vector = Column(JSON, nullable=False)  # Embedding vector
    similarity_scores = Column(JSON, nullable=True)  # Similarity to other prompts
    topic_classification = Column(JSON, nullable=True)  # Topic classification results
    sentiment_analysis = Column(JSON, nullable=True)  # Sentiment analysis results
    
    # Language analysis
    complexity_metrics = Column(JSON, nullable=True)  # Complexity analysis
    readability_score = Column(Float, nullable=True)
    coherence_score = Column(Float, nullable=True)
    
    # Analysis metadata
    analysis_model = Column(String(100), nullable=False)
    analysis_version = Column(String(50), nullable=True)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prompt = relationship("Prompt")
    
    def __repr__(self):
        return f"<PromptSemanticAnalysis(id='{self.id}', prompt_id='{self.prompt_id}')>"


class PromptUsage(AsyncBase, TimestampMixin):
    """Usage tracking for prompts."""
    
    __tablename__ = "prompt_usages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id = Column(String(36), ForeignKey("prompts.id"), nullable=False)
    
    # Usage metadata
    user_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)
    context = Column(JSON, nullable=True)  # Usage context
    
    # Usage metrics
    response_time = Column(Float, nullable=True)
    token_usage = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=True)
    quality_score = Column(Float, nullable=True)
    
    # Usage details
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    
    # Relationships
    prompt = relationship("Prompt")
    
    def __repr__(self):
        return f"<PromptUsage(id='{self.id}', prompt_id='{self.prompt_id}')>"


class PromptOptimization(AsyncBase, TimestampMixin):
    """Optimization suggestions and results for prompts."""
    
    __tablename__ = "prompt_optimizations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id = Column(String(36), ForeignKey("prompts.id"), nullable=False)
    
    # Optimization metadata
    optimization_type = Column(String(50), nullable=False)  # performance, clarity, efficiency
    optimization_algorithm = Column(String(100), nullable=False)
    
    # Optimization results
    original_content = Column(Text, nullable=False)
    optimized_content = Column(Text, nullable=False)
    improvement_metrics = Column(JSON, nullable=True)  # Improvement measurements
    
    # Optimization details
    optimization_parameters = Column(JSON, nullable=True)
    optimization_date = Column(DateTime, default=datetime.utcnow)
    is_applied = Column(Boolean, default=False)
    
    # Relationships
    prompt = relationship("Prompt")
    
    def __repr__(self):
        return f"<PromptOptimization(id='{self.id}', prompt_id='{self.prompt_id}')>"
