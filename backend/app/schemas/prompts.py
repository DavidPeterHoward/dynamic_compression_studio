"""
Pydantic schemas for prompt management and evaluation.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class PromptTypeEnum(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TEMPLATE = "template"
    WORKFLOW = "workflow"
    CHAIN = "chain"


class PromptCategoryEnum(str, Enum):
    COMPRESSION = "compression"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    OPTIMIZATION = "optimization"
    EVALUATION = "evaluation"
    WORKFLOW = "workflow"
    CUSTOM = "custom"


class EvaluationStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Base schemas
class PromptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    prompt_type: PromptTypeEnum
    category: PromptCategoryEnum
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    is_template: bool = False
    parent_id: Optional[str] = None


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    prompt_type: Optional[PromptTypeEnum] = None
    category: Optional[PromptCategoryEnum] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    is_template: Optional[bool] = None
    is_active: Optional[bool] = None


class PromptResponse(PromptBase):
    id: str
    version: str
    is_active: bool
    usage_count: int
    success_rate: Optional[float] = None
    average_response_time: Optional[float] = None
    token_efficiency: Optional[float] = None
    complexity_score: Optional[float] = None
    clarity_score: Optional[float] = None
    effectiveness_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    prompts: List[PromptResponse]
    total: int
    skip: int
    limit: int


# Template schemas
class PromptTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_content: str = Field(..., min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    default_values: Optional[Dict[str, Any]] = None
    category: PromptCategoryEnum
    tags: Optional[List[str]] = None
    is_public: bool = True


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateResponse(PromptTemplateBase):
    id: str
    usage_count: int
    success_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workflow schemas
class PromptWorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    workflow_definition: Dict[str, Any] = Field(..., description="Workflow structure and logic")
    execution_order: List[str] = Field(..., description="Order of prompt execution")
    conditional_logic: Optional[Dict[str, Any]] = None
    category: PromptCategoryEnum
    tags: Optional[List[str]] = None


class PromptWorkflowCreate(PromptWorkflowBase):
    pass


class PromptWorkflowResponse(PromptWorkflowBase):
    id: str
    is_active: bool
    execution_count: int
    success_rate: Optional[float] = None
    average_execution_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Evaluation schemas
class PromptEvaluationBase(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=100)
    model_version: Optional[str] = None
    evaluation_type: str = Field(..., description="automated, human, hybrid")
    test_cases: Optional[List[Dict[str, Any]]] = None
    evaluator: Optional[str] = None


class PromptEvaluationCreate(PromptEvaluationBase):
    pass


class PromptEvaluationResponse(PromptEvaluationBase):
    id: str
    prompt_id: str
    accuracy_score: Optional[float] = None
    relevance_score: Optional[float] = None
    clarity_score: Optional[float] = None
    creativity_score: Optional[float] = None
    consistency_score: Optional[float] = None
    efficiency_score: Optional[float] = None
    response_time: Optional[float] = None
    token_usage: Optional[int] = None
    cost: Optional[float] = None
    evaluation_results: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    status: EvaluationStatusEnum
    evaluation_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Semantic analysis schemas
class PromptSemanticAnalysisRequest(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=100)
    model_version: Optional[str] = None
    include_similarity: bool = True
    include_topic_classification: bool = True
    include_sentiment_analysis: bool = True
    include_complexity_analysis: bool = True


class PromptSemanticAnalysisResponse(BaseModel):
    id: str
    prompt_id: str
    semantic_vector: List[float]
    similarity_scores: Optional[Dict[str, float]] = None
    topic_classification: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    complexity_metrics: Optional[Dict[str, float]] = None
    readability_score: Optional[float] = None
    coherence_score: Optional[float] = None
    analysis_model: str
    analysis_version: Optional[str] = None
    analysis_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Optimization schemas
class PromptOptimizationRequest(BaseModel):
    optimization_type: str = Field(..., description="performance, clarity, efficiency")
    algorithm: str = Field(..., min_length=1, max_length=100)
    parameters: Optional[Dict[str, Any]] = None
    target_metrics: Optional[Dict[str, float]] = None


class PromptOptimizationResponse(BaseModel):
    id: str
    prompt_id: str
    optimization_type: str
    optimization_algorithm: str
    original_content: str
    optimized_content: str
    improvement_metrics: Optional[Dict[str, float]] = None
    optimization_parameters: Optional[Dict[str, Any]] = None
    optimization_date: datetime
    is_applied: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Search schemas
class PromptSearchRequest(BaseModel):
    query: Optional[str] = None
    categories: Optional[List[str]] = None
    prompt_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    semantic_vector: Optional[List[float]] = None
    sort_by: str = "created_at"  # relevance, usage, success_rate, created_at
    sort_order: str = "desc"  # asc, desc
    skip: int = 0
    limit: int = 100

    @validator('limit')
    def validate_limit(cls, v):
        if v > 1000:
            raise ValueError('Limit cannot exceed 1000')
        return v


class PromptSearchResponse(BaseModel):
    prompts: List[PromptResponse]
    total: int
    skip: int
    limit: int
    search_metadata: Optional[Dict[str, Any]] = None


# Workflow execution schemas
class PromptWorkflowExecutionRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None


class PromptWorkflowExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    execution_id: str
    status: EvaluationStatusEnum
    started_at: datetime
    completed_at: Optional[datetime] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    intermediate_results: Optional[Dict[str, Any]] = None
    total_execution_time: Optional[float] = None
    step_execution_times: Optional[Dict[str, float]] = None
    token_usage: Optional[int] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None
    error_step: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Usage tracking schemas
class PromptUsageCreate(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None


class PromptUsageResponse(BaseModel):
    id: str
    prompt_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    response_time: Optional[float] = None
    token_usage: Optional[int] = None
    success: Optional[bool] = None
    quality_score: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics schemas
class PromptAnalyticsResponse(BaseModel):
    total_prompts: int
    active_prompts: int
    category_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    total_usage: int
    average_success_rate: float
    top_performing_prompts: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


# Multi-dimensional evaluation schemas
class MultiDimensionalEvaluationRequest(BaseModel):
    prompt_ids: List[str]
    models: List[str]
    evaluation_criteria: List[str]  # accuracy, relevance, creativity, etc.
    meta_recursive: bool = False
    self_iterative: bool = False
    perspectives: List[str] = ["technical", "user", "business"]
    methods: List[str] = ["automated", "human", "hybrid"]


class MultiDimensionalEvaluationResponse(BaseModel):
    evaluation_id: str
    prompt_evaluations: List[PromptEvaluationResponse]
    meta_analysis: Dict[str, Any]
    recursive_insights: Optional[Dict[str, Any]] = None
    perspective_analysis: Dict[str, Any]
    method_comparison: Dict[str, Any]
    overall_scores: Dict[str, float]
    recommendations: List[str]
    created_at: datetime


# Prompt chain schemas
class PromptChainBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    chain_definition: Dict[str, Any] = Field(..., description="Chain structure and logic")
    execution_strategy: str = Field(..., description="sequential, parallel, conditional")
    category: PromptCategoryEnum
    tags: Optional[List[str]] = None


class PromptChainCreate(PromptChainBase):
    pass


class PromptChainResponse(PromptChainBase):
    id: str
    is_active: bool
    execution_count: int
    success_rate: Optional[float] = None
    average_execution_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
