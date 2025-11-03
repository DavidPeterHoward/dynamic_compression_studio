"""
Cloud Services Pydantic Schemas

This module defines the Pydantic schemas for cloud services API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class CloudProviderType(str, Enum):
    """Cloud provider types"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    LINODE = "linode"
    VULTR = "vultr"


class ResourceType(str, Enum):
    """Cloud resource types"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    MONITORING = "monitoring"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OptimizationPriority(str, Enum):
    """Optimization priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImplementationEffort(str, Enum):
    """Implementation effort levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Cloud Provider Schemas
class CloudProviderBase(BaseModel):
    """Base cloud provider schema"""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    api_endpoint: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    supported_regions: Optional[Dict[str, Any]] = None
    supported_services: Optional[Dict[str, Any]] = None
    pricing_model: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class CloudProviderCreate(CloudProviderBase):
    """Schema for creating a cloud provider"""
    pass


class CloudProviderUpdate(BaseModel):
    """Schema for updating a cloud provider"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    api_endpoint: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    supported_regions: Optional[Dict[str, Any]] = None
    supported_services: Optional[Dict[str, Any]] = None
    pricing_model: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class CloudProviderResponse(CloudProviderBase):
    """Schema for cloud provider response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Cloud Account Schemas
class CloudAccountBase(BaseModel):
    """Base cloud account schema"""
    provider_id: int
    account_name: str = Field(..., min_length=1, max_length=200)
    account_id: str = Field(..., min_length=1, max_length=200)
    access_key: Optional[str] = Field(None, max_length=500)
    secret_key: Optional[str] = Field(None, max_length=500)
    region: str = Field(default="us-east-1", max_length=100)
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


class CloudAccountCreate(CloudAccountBase):
    """Schema for creating a cloud account"""
    pass


class CloudAccountUpdate(BaseModel):
    """Schema for updating a cloud account"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=200)
    access_key: Optional[str] = Field(None, max_length=500)
    secret_key: Optional[str] = Field(None, max_length=500)
    region: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class CloudAccountResponse(CloudAccountBase):
    """Schema for cloud account response"""
    id: int
    last_sync: Optional[datetime] = None
    sync_status: str = "pending"
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Cloud Resource Schemas
class CloudResourceBase(BaseModel):
    """Base cloud resource schema"""
    provider_id: int
    account_id: int
    resource_id: str = Field(..., min_length=1, max_length=200)
    resource_name: str = Field(..., min_length=1, max_length=200)
    resource_type: str = Field(..., min_length=1, max_length=100)
    service_name: str = Field(..., min_length=1, max_length=100)
    region: str = Field(..., min_length=1, max_length=100)
    status: str = Field(..., min_length=1, max_length=50)
    size: Optional[str] = Field(None, max_length=100)
    cost_per_hour: Optional[float] = Field(None, ge=0)
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_monitored: bool = True


class CloudResourceCreate(CloudResourceBase):
    """Schema for creating a cloud resource"""
    pass


class CloudResourceUpdate(BaseModel):
    """Schema for updating a cloud resource"""
    resource_name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    size: Optional[str] = Field(None, max_length=100)
    cost_per_hour: Optional[float] = Field(None, ge=0)
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_monitored: Optional[bool] = None


class CloudResourceResponse(CloudResourceBase):
    """Schema for cloud resource response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Cloud Metrics Schemas
class CloudMetricsBase(BaseModel):
    """Base cloud metrics schema"""
    provider_id: int
    account_id: int
    resource_id: Optional[int] = None
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    metric_unit: str = Field(..., min_length=1, max_length=50)
    timestamp: datetime
    dimensions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CloudMetricsCreate(CloudMetricsBase):
    """Schema for creating cloud metrics"""
    pass


class CloudMetricsResponse(CloudMetricsBase):
    """Schema for cloud metrics response"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Cloud Costs Schemas
class CloudCostsBase(BaseModel):
    """Base cloud costs schema"""
    provider_id: int
    account_id: int
    resource_id: Optional[int] = None
    cost_date: datetime
    service_name: str = Field(..., min_length=1, max_length=100)
    cost_amount: float = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=10)
    cost_category: Optional[str] = Field(None, max_length=100)
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CloudCostsCreate(CloudCostsBase):
    """Schema for creating cloud costs"""
    pass


class CloudCostsResponse(CloudCostsBase):
    """Schema for cloud costs response"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Cloud Alerts Schemas
class CloudAlertsBase(BaseModel):
    """Base cloud alerts schema"""
    account_id: int
    alert_type: str = Field(..., min_length=1, max_length=100)
    alert_name: str = Field(..., min_length=1, max_length=200)
    alert_description: Optional[str] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    severity: AlertSeverity
    status: str = Field(default="active", max_length=20)
    is_enabled: bool = True
    notification_channels: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CloudAlertsCreate(CloudAlertsBase):
    """Schema for creating cloud alerts"""
    pass


class CloudAlertsUpdate(BaseModel):
    """Schema for updating cloud alerts"""
    alert_name: Optional[str] = Field(None, min_length=1, max_length=200)
    alert_description: Optional[str] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[str] = Field(None, max_length=20)
    is_enabled: Optional[bool] = None
    notification_channels: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CloudAlertsResponse(CloudAlertsBase):
    """Schema for cloud alerts response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Cloud Optimization Schemas
class CloudOptimizationBase(BaseModel):
    """Base cloud optimization schema"""
    account_id: int
    optimization_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    potential_savings: Optional[float] = Field(None, ge=0)
    implementation_effort: Optional[ImplementationEffort] = None
    priority: OptimizationPriority
    status: str = Field(default="pending", max_length=20)
    recommendations: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CloudOptimizationCreate(CloudOptimizationBase):
    """Schema for creating cloud optimization"""
    pass


class CloudOptimizationUpdate(BaseModel):
    """Schema for updating cloud optimization"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    potential_savings: Optional[float] = Field(None, ge=0)
    implementation_effort: Optional[ImplementationEffort] = None
    priority: Optional[OptimizationPriority] = None
    status: Optional[str] = Field(None, max_length=20)
    recommendations: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CloudOptimizationResponse(CloudOptimizationBase):
    """Schema for cloud optimization response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Analytics Schemas
class CloudDashboardData(BaseModel):
    """Cloud dashboard data schema"""
    total_cost: float
    cost_trend: float  # Percentage change
    total_resources: int
    active_resources: int
    alerts_count: int
    critical_alerts: int
    optimization_opportunities: int
    potential_savings: float
    top_services_by_cost: List[Dict[str, Any]]
    recent_alerts: List[CloudAlertsResponse]
    recent_optimizations: List[CloudOptimizationResponse]


class CloudCostTrends(BaseModel):
    """Cloud cost trends schema"""
    daily_costs: List[Dict[str, Any]]
    monthly_costs: List[Dict[str, Any]]
    cost_by_service: List[Dict[str, Any]]
    cost_by_region: List[Dict[str, Any]]
    cost_prediction: List[Dict[str, Any]]


class CloudPerformanceAnalytics(BaseModel):
    """Cloud performance analytics schema"""
    cpu_utilization: List[Dict[str, Any]]
    memory_utilization: List[Dict[str, Any]]
    network_utilization: List[Dict[str, Any]]
    storage_utilization: List[Dict[str, Any]]
    performance_metrics: List[Dict[str, Any]]
    resource_efficiency: List[Dict[str, Any]]


# LLM Integration Schemas
class CloudLLMRequest(BaseModel):
    """Schema for LLM cloud management requests"""
    query: str = Field(..., min_length=1, max_length=1000)
    account_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class CloudLLMResponse(BaseModel):
    """Schema for LLM cloud management responses"""
    response: str
    actions: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    confidence: float = Field(..., ge=0, le=1)


# Helper Functions Integration Schemas
class CloudWorkflowRequest(BaseModel):
    """Schema for cloud workflow requests"""
    workflow_type: str = Field(..., min_length=1, max_length=100)
    account_id: int
    parameters: Dict[str, Any]
    schedule: Optional[str] = None  # Cron expression


class CloudWorkflowResponse(BaseModel):
    """Schema for cloud workflow responses"""
    workflow_id: str
    status: str
    message: str
    execution_time: Optional[float] = None
    results: Optional[Dict[str, Any]] = None


# Validation functions
@validator('cost_amount')
def validate_cost_amount(cls, v):
    """Validate cost amount is non-negative"""
    if v is not None and v < 0:
        raise ValueError('Cost amount must be non-negative')
    return v


@validator('metric_value')
def validate_metric_value(cls, v):
    """Validate metric value is a valid number"""
    if not isinstance(v, (int, float)):
        raise ValueError('Metric value must be a number')
    return v


@validator('threshold_value')
def validate_threshold_value(cls, v):
    """Validate threshold value is non-negative"""
    if v is not None and v < 0:
        raise ValueError('Threshold value must be non-negative')
    return v
