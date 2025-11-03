"""
Cloud Services Models

This module defines the database models for cloud services management,
including cloud providers, accounts, resources, metrics, and costs.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

Base = declarative_base()


class CloudProvider(Base):
    """Model for cloud service providers"""
    
    __tablename__ = "cloud_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    api_endpoint = Column(String(500))
    documentation_url = Column(String(500))
    logo_url = Column(String(500))
    supported_regions = Column(JSON)
    supported_services = Column(JSON)
    pricing_model = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    accounts = relationship("CloudAccount", back_populates="provider")
    resources = relationship("CloudResource", back_populates="provider")
    metrics = relationship("CloudMetrics", back_populates="provider")
    costs = relationship("CloudCosts", back_populates="provider")
    
    def __repr__(self):
        return f"<CloudProvider(name='{self.name}', display_name='{self.display_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "api_endpoint": self.api_endpoint,
            "documentation_url": self.documentation_url,
            "logo_url": self.logo_url,
            "supported_regions": self.supported_regions,
            "supported_services": self.supported_services,
            "pricing_model": self.pricing_model,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CloudAccount(Base):
    """Model for cloud service accounts"""
    
    __tablename__ = "cloud_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("cloud_providers.id"), nullable=False)
    account_name = Column(String(200), nullable=False)
    account_id = Column(String(200), nullable=False)  # Cloud provider account ID
    access_key = Column(String(500))  # Encrypted access key
    secret_key = Column(String(500))  # Encrypted secret key
    region = Column(String(100), nullable=False, default="us-east-1")
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default="pending")  # pending, syncing, completed, failed
    error_message = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="accounts")
    resources = relationship("CloudResource", back_populates="account")
    metrics = relationship("CloudMetrics", back_populates="account")
    costs = relationship("CloudCosts", back_populates="account")
    alerts = relationship("CloudAlerts", back_populates="account")
    
    def __repr__(self):
        return f"<CloudAccount(provider='{self.provider.name if self.provider else 'Unknown'}', account_name='{self.account_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "account_name": self.account_name,
            "account_id": self.account_id,
            "region": self.region,
            "is_active": self.is_active,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_status": self.sync_status,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CloudResource(Base):
    """Model for cloud resources"""
    
    __tablename__ = "cloud_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("cloud_providers.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("cloud_accounts.id"), nullable=False)
    resource_id = Column(String(200), nullable=False)  # Cloud provider resource ID
    resource_name = Column(String(200), nullable=False)
    resource_type = Column(String(100), nullable=False)  # instance, storage, database, etc.
    service_name = Column(String(100), nullable=False)  # EC2, S3, RDS, etc.
    region = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # running, stopped, terminated, etc.
    size = Column(String(100))  # instance size, storage size, etc.
    cost_per_hour = Column(Float)
    tags = Column(JSON)
    metadata = Column(JSON)
    is_monitored = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="resources")
    account = relationship("CloudAccount", back_populates="resources")
    metrics = relationship("CloudMetrics", back_populates="resource")
    costs = relationship("CloudCosts", back_populates="resource")
    
    def __repr__(self):
        return f"<CloudResource(name='{self.resource_name}', type='{self.resource_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "account_id": self.account_id,
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "resource_type": self.resource_type,
            "service_name": self.service_name,
            "region": self.region,
            "status": self.status,
            "size": self.size,
            "cost_per_hour": self.cost_per_hour,
            "tags": self.tags,
            "metadata": self.metadata,
            "is_monitored": self.is_monitored,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CloudMetrics(Base):
    """Model for cloud resource metrics"""
    
    __tablename__ = "cloud_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("cloud_providers.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("cloud_accounts.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"), nullable=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    dimensions = Column(JSON)  # Additional metric dimensions
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="metrics")
    account = relationship("CloudAccount", back_populates="metrics")
    resource = relationship("CloudResource", back_populates="metrics")
    
    def __repr__(self):
        return f"<CloudMetrics(name='{self.metric_name}', value={self.metric_value}, timestamp='{self.timestamp}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "account_id": self.account_id,
            "resource_id": self.resource_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "dimensions": self.dimensions,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CloudCosts(Base):
    """Model for cloud cost tracking"""
    
    __tablename__ = "cloud_costs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("cloud_providers.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("cloud_accounts.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("cloud_resources.id"), nullable=True)
    cost_date = Column(DateTime(timezone=True), nullable=False, index=True)
    service_name = Column(String(100), nullable=False)
    cost_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    cost_category = Column(String(100))  # compute, storage, network, etc.
    tags = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="costs")
    account = relationship("CloudAccount", back_populates="costs")
    resource = relationship("CloudResource", back_populates="costs")
    
    def __repr__(self):
        return f"<CloudCosts(amount={self.cost_amount}, date='{self.cost_date}', service='{self.service_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "account_id": self.account_id,
            "resource_id": self.resource_id,
            "cost_date": self.cost_date.isoformat() if self.cost_date else None,
            "service_name": self.service_name,
            "cost_amount": self.cost_amount,
            "currency": self.currency,
            "cost_category": self.cost_category,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CloudAlerts(Base):
    """Model for cloud alerts and notifications"""
    
    __tablename__ = "cloud_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cloud_accounts.id"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # cost, performance, security, etc.
    alert_name = Column(String(200), nullable=False)
    alert_description = Column(Text)
    threshold_value = Column(Float)
    current_value = Column(Float)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    status = Column(String(20), default="active")  # active, resolved, dismissed
    is_enabled = Column(Boolean, default=True)
    notification_channels = Column(JSON)  # email, slack, webhook, etc.
    conditions = Column(JSON)  # Alert conditions and logic
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    triggered_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    account = relationship("CloudAccount", back_populates="alerts")
    
    def __repr__(self):
        return f"<CloudAlerts(name='{self.alert_name}', type='{self.alert_type}', severity='{self.severity}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "alert_type": self.alert_type,
            "alert_name": self.alert_name,
            "alert_description": self.alert_description,
            "threshold_value": self.threshold_value,
            "current_value": self.current_value,
            "severity": self.severity,
            "status": self.status,
            "is_enabled": self.is_enabled,
            "notification_channels": self.notification_channels,
            "conditions": self.conditions,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class CloudOptimization(Base):
    """Model for cloud optimization recommendations"""
    
    __tablename__ = "cloud_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cloud_accounts.id"), nullable=False)
    optimization_type = Column(String(100), nullable=False)  # cost, performance, security, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text)
    potential_savings = Column(Float)  # Potential cost savings
    implementation_effort = Column(String(20))  # low, medium, high
    priority = Column(String(20), nullable=False)  # low, medium, high, critical
    status = Column(String(20), default="pending")  # pending, in_progress, completed, dismissed
    recommendations = Column(JSON)  # Detailed recommendations
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    implemented_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<CloudOptimization(title='{self.title}', type='{self.optimization_type}', priority='{self.priority}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "optimization_type": self.optimization_type,
            "title": self.title,
            "description": self.description,
            "potential_savings": self.potential_savings,
            "implementation_effort": self.implementation_effort,
            "priority": self.priority,
            "status": self.status,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "implemented_at": self.implemented_at.isoformat() if self.implemented_at else None
        }
