"""
Pydantic models for Enhanced Compression API endpoints.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis."""
    content: str = Field(..., description="Content to analyze", min_length=1)
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")


class AlgorithmRecommendationRequest(BaseModel):
    """Request model for algorithm recommendations."""
    content_analysis: Dict[str, Any] = Field(..., description="Content analysis results")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    meta_learning_context: Dict[str, Any] = Field(default_factory=dict, description="Meta-learning context")


class EnhancedCompressionRequest(BaseModel):
    """Request model for enhanced compression."""
    content: str = Field(..., description="Content to compress", min_length=1)
    content_analysis: Dict[str, Any] = Field(..., description="Content analysis results")
    algorithm: Dict[str, Any] = Field(..., description="Algorithm configuration")
    options: Dict[str, Any] = Field(default_factory=dict, description="Compression options")


class BatchProcessRequest(BaseModel):
    """Request model for batch processing."""
    items: List[Dict[str, Any]] = Field(..., description="List of items to process", min_items=1)
    options: Dict[str, Any] = Field(default_factory=dict, description="Processing options")


class UpdatePreferencesRequest(BaseModel):
    """Request model for updating user preferences."""
    user_id: str = Field(..., description="User ID")
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    learning_data: Dict[str, Any] = Field(default_factory=dict, description="Learning data")


class ContentAnalysisResponse(BaseModel):
    """Response model for content analysis."""
    success: bool
    analysis: Dict[str, Any]
    processing_time: float
    timestamp: str


class AlgorithmRecommendationResponse(BaseModel):
    """Response model for algorithm recommendations."""
    success: bool
    recommendations: List[Dict[str, Any]]
    meta_learning_insights: Dict[str, Any]
    processing_time: float
    timestamp: str


class EnhancedCompressionResponse(BaseModel):
    """Response model for enhanced compression."""
    success: bool
    result: Dict[str, Any]
    analysis: Dict[str, Any]
    metrics: Dict[str, Any]
    request_id: str
    processing_time: float
    timestamp: str


class BatchProcessResponse(BaseModel):
    """Response model for batch processing."""
    success: bool
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    processing_time: float
    timestamp: str


class RealTimeMetricsResponse(BaseModel):
    """Response model for real-time metrics."""
    success: bool
    real_time_metrics: Dict[str, Any]
    trends: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    timestamp: str


class LearningInsightsResponse(BaseModel):
    """Response model for learning insights."""
    success: bool
    insights: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    processing_time: float
    timestamp: str


class UpdatePreferencesResponse(BaseModel):
    """Response model for updating preferences."""
    success: bool
    updated_preferences: Dict[str, Any]
    learning_status: Dict[str, Any]
    processing_time: float
    timestamp: str
