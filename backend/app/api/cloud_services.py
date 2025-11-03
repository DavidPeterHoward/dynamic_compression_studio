"""
Cloud Services API Endpoints

This module provides REST API endpoints for cloud services management,
including cloud providers, accounts, resources, metrics, costs, and optimization.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..database import get_db_session_session
from ..models.cloud_services import (
    CloudProvider, CloudAccount, CloudResource, CloudMetrics, 
    CloudCosts, CloudAlerts, CloudOptimization
)
from ..schemas.cloud_services import (
    CloudProviderCreate, CloudProviderResponse,
    CloudAccountCreate, CloudAccountResponse,
    CloudResourceResponse, CloudMetricsResponse,
    CloudCostsResponse, CloudAlertsResponse,
    CloudOptimizationResponse
)
from ..services.cloud_manager import CloudManager
from ..services.cloud_analytics import CloudAnalytics
from ..services.cloud_optimizer import CloudOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cloud-services", tags=["cloud-services"])

# Initialize services
cloud_manager = CloudManager()
cloud_analytics = CloudAnalytics()
cloud_optimizer = CloudOptimizer()


@router.get("/providers", response_model=List[CloudProviderResponse])
async def get_cloud_providers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db_session)
):
    """Get list of cloud providers"""
    try:
        query = db.query(CloudProvider)
        if active_only:
            query = query.filter(CloudProvider.is_active == True)
        
        providers = query.offset(skip).limit(limit).all()
        return [provider.to_dict() for provider in providers]
    except Exception as e:
        logger.error(f"Error fetching cloud providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud providers")


@router.post("/providers", response_model=CloudProviderResponse)
async def create_cloud_provider(
    provider: CloudProviderCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new cloud provider"""
    try:
        db_provider = CloudProvider(**provider.dict())
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        return db_provider.to_dict()
    except Exception as e:
        logger.error(f"Error creating cloud provider: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create cloud provider")


@router.get("/accounts", response_model=List[CloudAccountResponse])
async def get_cloud_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    provider_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db_session)
):
    """Get list of cloud accounts"""
    try:
        query = db.query(CloudAccount)
        if active_only:
            query = query.filter(CloudAccount.is_active == True)
        if provider_id:
            query = query.filter(CloudAccount.provider_id == provider_id)
        
        accounts = query.offset(skip).limit(limit).all()
        return [account.to_dict() for account in accounts]
    except Exception as e:
        logger.error(f"Error fetching cloud accounts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud accounts")


@router.post("/accounts", response_model=CloudAccountResponse)
async def create_cloud_account(
    account: CloudAccountCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Create a new cloud account and sync resources"""
    try:
        db_account = CloudAccount(**account.dict())
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Schedule background sync
        background_tasks.add_task(
            cloud_manager.sync_account_resources,
            db_account.id
        )
        
        return db_account.to_dict()
    except Exception as e:
        logger.error(f"Error creating cloud account: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create cloud account")


@router.post("/accounts/{account_id}/sync")
async def sync_account_resources(
    account_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Sync resources for a specific cloud account"""
    try:
        account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Cloud account not found")
        
        # Schedule background sync
        background_tasks.add_task(
            cloud_manager.sync_account_resources,
            account_id
        )
        
        return {"message": "Account sync initiated", "account_id": account_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing account resources: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to sync account resources")


@router.get("/resources", response_model=List[CloudResourceResponse])
async def get_cloud_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = Query(None),
    provider_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    monitored_only: bool = Query(False),
    db: Session = Depends(get_db_session)
):
    """Get list of cloud resources"""
    try:
        query = db.query(CloudResource)
        
        if account_id:
            query = query.filter(CloudResource.account_id == account_id)
        if provider_id:
            query = query.filter(CloudResource.provider_id == provider_id)
        if resource_type:
            query = query.filter(CloudResource.resource_type == resource_type)
        if status:
            query = query.filter(CloudResource.status == status)
        if monitored_only:
            query = query.filter(CloudResource.is_monitored == True)
        
        resources = query.offset(skip).limit(limit).all()
        return [resource.to_dict() for resource in resources]
    except Exception as e:
        logger.error(f"Error fetching cloud resources: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud resources")


@router.get("/metrics", response_model=List[CloudMetricsResponse])
async def get_cloud_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = Query(None),
    resource_id: Optional[int] = Query(None),
    metric_name: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: Session = Depends(get_db_session)
):
    """Get cloud metrics"""
    try:
        query = db.query(CloudMetrics)
        
        if account_id:
            query = query.filter(CloudMetrics.account_id == account_id)
        if resource_id:
            query = query.filter(CloudMetrics.resource_id == resource_id)
        if metric_name:
            query = query.filter(CloudMetrics.metric_name == metric_name)
        if start_time:
            query = query.filter(CloudMetrics.timestamp >= start_time)
        if end_time:
            query = query.filter(CloudMetrics.timestamp <= end_time)
        
        # Default to last 24 hours if no time range specified
        if not start_time and not end_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
            query = query.filter(CloudMetrics.timestamp >= start_time)
        
        metrics = query.order_by(CloudMetrics.timestamp.desc()).offset(skip).limit(limit).all()
        return [metric.to_dict() for metric in metrics]
    except Exception as e:
        logger.error(f"Error fetching cloud metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud metrics")


@router.get("/costs", response_model=List[CloudCostsResponse])
async def get_cloud_costs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    service_name: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """Get cloud costs"""
    try:
        query = db.query(CloudCosts)
        
        if account_id:
            query = query.filter(CloudCosts.account_id == account_id)
        if start_date:
            query = query.filter(CloudCosts.cost_date >= start_date)
        if end_date:
            query = query.filter(CloudCosts.cost_date <= end_date)
        if service_name:
            query = query.filter(CloudCosts.service_name == service_name)
        
        # Default to last 30 days if no date range specified
        if not start_date and not end_date:
            start_date = datetime.utcnow() - timedelta(days=30)
            query = query.filter(CloudCosts.cost_date >= start_date)
        
        costs = query.order_by(CloudCosts.cost_date.desc()).offset(skip).limit(limit).all()
        return [cost.to_dict() for cost in costs]
    except Exception as e:
        logger.error(f"Error fetching cloud costs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud costs")


@router.get("/alerts", response_model=List[CloudAlertsResponse])
async def get_cloud_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = Query(None),
    alert_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """Get cloud alerts"""
    try:
        query = db.query(CloudAlerts)
        
        if account_id:
            query = query.filter(CloudAlerts.account_id == account_id)
        if alert_type:
            query = query.filter(CloudAlerts.alert_type == alert_type)
        if severity:
            query = query.filter(CloudAlerts.severity == severity)
        if status:
            query = query.filter(CloudAlerts.status == status)
        
        alerts = query.order_by(CloudAlerts.created_at.desc()).offset(skip).limit(limit).all()
        return [alert.to_dict() for alert in alerts]
    except Exception as e:
        logger.error(f"Error fetching cloud alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud alerts")


@router.get("/optimizations", response_model=List[CloudOptimizationResponse])
async def get_cloud_optimizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = Query(None),
    optimization_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """Get cloud optimization recommendations"""
    try:
        query = db.query(CloudOptimization)
        
        if account_id:
            query = query.filter(CloudOptimization.account_id == account_id)
        if optimization_type:
            query = query.filter(CloudOptimization.optimization_type == optimization_type)
        if priority:
            query = query.filter(CloudOptimization.priority == priority)
        if status:
            query = query.filter(CloudOptimization.status == status)
        
        optimizations = query.order_by(CloudOptimization.created_at.desc()).offset(skip).limit(limit).all()
        return [optimization.to_dict() for optimization in optimizations]
    except Exception as e:
        logger.error(f"Error fetching cloud optimizations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud optimizations")


@router.get("/analytics/dashboard")
async def get_cloud_dashboard(
    account_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db_session)
):
    """Get cloud dashboard analytics"""
    try:
        dashboard_data = await cloud_analytics.get_dashboard_data(
            db, account_id, days
        )
        return dashboard_data
    except Exception as e:
        logger.error(f"Error fetching cloud dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cloud dashboard")


@router.get("/analytics/cost-trends")
async def get_cost_trends(
    account_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db_session)
):
    """Get cloud cost trends"""
    try:
        cost_trends = await cloud_analytics.get_cost_trends(
            db, account_id, days
        )
        return cost_trends
    except Exception as e:
        logger.error(f"Error fetching cost trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cost trends")


@router.get("/analytics/performance")
async def get_performance_analytics(
    account_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db_session)
):
    """Get cloud performance analytics"""
    try:
        performance_data = await cloud_analytics.get_performance_analytics(
            db, account_id, days
        )
        return performance_data
    except Exception as e:
        logger.error(f"Error fetching performance analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance analytics")


@router.post("/optimize")
async def run_optimization_analysis(
    account_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Run optimization analysis for a cloud account"""
    try:
        account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Cloud account not found")
        
        # Schedule background optimization analysis
        background_tasks.add_task(
            cloud_optimizer.analyze_optimization_opportunities,
            account_id
        )
        
        return {"message": "Optimization analysis initiated", "account_id": account_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running optimization analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to run optimization analysis")


@router.get("/health")
async def health_check():
    """Health check endpoint for cloud services"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "cloud_manager": "active",
            "cloud_analytics": "active",
            "cloud_optimizer": "active"
        }
    }
