"""
Cloud Analytics Service

This module provides comprehensive analytics for cloud services,
including cost analysis, performance metrics, and optimization insights.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from ..models.cloud_services import (
    CloudAccount, CloudResource, CloudMetrics, CloudCosts, 
    CloudAlerts, CloudOptimization
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudAnalytics:
    """Cloud analytics service for comprehensive cloud insights"""
    
    def __init__(self):
        self.cost_analyzer = CostAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.optimization_analyzer = OptimizationAnalyzer()
    
    async def get_dashboard_data(
        self, 
        db: Session, 
        account_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Base query
            base_query = db.query(CloudCosts)
            if account_id:
                base_query = base_query.filter(CloudCosts.account_id == account_id)
            
            # Total cost
            total_cost = base_query.filter(
                CloudCosts.cost_date >= start_date
            ).with_entities(func.sum(CloudCosts.cost_amount)).scalar() or 0
            
            # Cost trend (comparing with previous period)
            previous_start = start_date - timedelta(days=days)
            previous_cost = base_query.filter(
                and_(
                    CloudCosts.cost_date >= previous_start,
                    CloudCosts.cost_date < start_date
                )
            ).with_entities(func.sum(CloudCosts.cost_amount)).scalar() or 0
            
            cost_trend = 0
            if previous_cost > 0:
                cost_trend = ((total_cost - previous_cost) / previous_cost) * 100
            
            # Resource counts
            resource_query = db.query(CloudResource)
            if account_id:
                resource_query = resource_query.filter(CloudResource.account_id == account_id)
            
            total_resources = resource_query.count()
            active_resources = resource_query.filter(
                CloudResource.status.in_(['running', 'active', 'available'])
            ).count()
            
            # Alerts
            alert_query = db.query(CloudAlerts)
            if account_id:
                alert_query = alert_query.filter(CloudAlerts.account_id == account_id)
            
            alerts_count = alert_query.filter(CloudAlerts.is_enabled == True).count()
            critical_alerts = alert_query.filter(
                and_(
                    CloudAlerts.is_enabled == True,
                    CloudAlerts.severity == 'critical'
                )
            ).count()
            
            # Optimization opportunities
            optimization_query = db.query(CloudOptimization)
            if account_id:
                optimization_query = optimization_query.filter(CloudOptimization.account_id == account_id)
            
            optimization_opportunities = optimization_query.filter(
                CloudOptimization.status == 'pending'
            ).count()
            
            potential_savings = optimization_query.filter(
                CloudOptimization.status == 'pending'
            ).with_entities(func.sum(CloudOptimization.potential_savings)).scalar() or 0
            
            # Top services by cost
            top_services = base_query.filter(
                CloudCosts.cost_date >= start_date
            ).with_entities(
                CloudCosts.service_name,
                func.sum(CloudCosts.cost_amount).label('total_cost')
            ).group_by(CloudCosts.service_name).order_by(
                desc('total_cost')
            ).limit(10).all()
            
            top_services_data = [
                {"service": service, "cost": float(total_cost)}
                for service, total_cost in top_services
            ]
            
            # Recent alerts
            recent_alerts = alert_query.filter(
                CloudAlerts.is_enabled == True
            ).order_by(desc(CloudAlerts.created_at)).limit(5).all()
            
            recent_alerts_data = [alert.to_dict() for alert in recent_alerts]
            
            # Recent optimizations
            recent_optimizations = optimization_query.filter(
                CloudOptimization.status == 'pending'
            ).order_by(desc(CloudOptimization.created_at)).limit(5).all()
            
            recent_optimizations_data = [opt.to_dict() for opt in recent_optimizations]
            
            return {
                "total_cost": float(total_cost),
                "cost_trend": cost_trend,
                "total_resources": total_resources,
                "active_resources": active_resources,
                "alerts_count": alerts_count,
                "critical_alerts": critical_alerts,
                "optimization_opportunities": optimization_opportunities,
                "potential_savings": float(potential_savings),
                "top_services_by_cost": top_services_data,
                "recent_alerts": recent_alerts_data,
                "recent_optimizations": recent_optimizations_data
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise
    
    async def get_cost_trends(
        self, 
        db: Session, 
        account_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get detailed cost trends analysis"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Base query
            base_query = db.query(CloudCosts)
            if account_id:
                base_query = base_query.filter(CloudCosts.account_id == account_id)
            
            # Daily costs
            daily_costs = base_query.filter(
                CloudCosts.cost_date >= start_date
            ).with_entities(
                CloudCosts.cost_date,
                func.sum(CloudCosts.cost_amount).label('daily_cost')
            ).group_by(CloudCosts.cost_date).order_by(CloudCosts.cost_date).all()
            
            daily_costs_data = [
                {
                    "date": cost_date.strftime("%Y-%m-%d"),
                    "cost": float(daily_cost)
                }
                for cost_date, daily_cost in daily_costs
            ]
            
            # Monthly costs
            monthly_costs = base_query.filter(
                CloudCosts.cost_date >= start_date
            ).with_entities(
                func.date_trunc('month', CloudCosts.cost_date).label('month'),
                func.sum(CloudCosts.cost_amount).label('monthly_cost')
            ).group_by('month').order_by('month').all()
            
            monthly_costs_data = [
                {
                    "month": month.strftime("%Y-%m"),
                    "cost": float(monthly_cost)
                }
                for month, monthly_cost in monthly_costs
            ]
            
            # Cost by service
            cost_by_service = base_query.filter(
                CloudCosts.cost_date >= start_date
            ).with_entities(
                CloudCosts.service_name,
                func.sum(CloudCosts.cost_amount).label('service_cost')
            ).group_by(CloudCosts.service_name).order_by(
                desc('service_cost')
            ).all()
            
            cost_by_service_data = [
                {"service": service, "cost": float(service_cost)}
                for service, service_cost in cost_by_service
            ]
            
            # Cost by region
            cost_by_region = base_query.filter(
                CloudCosts.cost_date >= start_date
            ).join(CloudResource, CloudCosts.resource_id == CloudResource.id).with_entities(
                CloudResource.region,
                func.sum(CloudCosts.cost_amount).label('region_cost')
            ).group_by(CloudResource.region).order_by(
                desc('region_cost')
            ).all()
            
            cost_by_region_data = [
                {"region": region, "cost": float(region_cost)}
                for region, region_cost in cost_by_region
            ]
            
            # Cost prediction using linear regression
            cost_prediction = await self._predict_future_costs(daily_costs_data)
            
            return {
                "daily_costs": daily_costs_data,
                "monthly_costs": monthly_costs_data,
                "cost_by_service": cost_by_service_data,
                "cost_by_region": cost_by_region_data,
                "cost_prediction": cost_prediction
            }
            
        except Exception as e:
            logger.error(f"Error getting cost trends: {str(e)}")
            raise
    
    async def get_performance_analytics(
        self, 
        db: Session, 
        account_id: Optional[int] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get performance analytics"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            # Base query
            base_query = db.query(CloudMetrics)
            if account_id:
                base_query = base_query.filter(CloudMetrics.account_id == account_id)
            
            # CPU utilization
            cpu_metrics = base_query.filter(
                and_(
                    CloudMetrics.metric_name == 'CPUUtilization',
                    CloudMetrics.timestamp >= start_time
                )
            ).order_by(CloudMetrics.timestamp).all()
            
            cpu_utilization_data = [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "value": metric.metric_value,
                    "resource_id": metric.resource_id
                }
                for metric in cpu_metrics
            ]
            
            # Memory utilization
            memory_metrics = base_query.filter(
                and_(
                    CloudMetrics.metric_name == 'MemoryUtilization',
                    CloudMetrics.timestamp >= start_time
                )
            ).order_by(CloudMetrics.timestamp).all()
            
            memory_utilization_data = [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "value": metric.metric_value,
                    "resource_id": metric.resource_id
                }
                for metric in memory_metrics
            ]
            
            # Network utilization
            network_metrics = base_query.filter(
                and_(
                    CloudMetrics.metric_name.in_(['NetworkIn', 'NetworkOut']),
                    CloudMetrics.timestamp >= start_time
                )
            ).order_by(CloudMetrics.timestamp).all()
            
            network_utilization_data = [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "metric_name": metric.metric_name,
                    "value": metric.metric_value,
                    "resource_id": metric.resource_id
                }
                for metric in network_metrics
            ]
            
            # Storage utilization
            storage_metrics = base_query.filter(
                and_(
                    CloudMetrics.metric_name == 'DiskUtilization',
                    CloudMetrics.timestamp >= start_time
                )
            ).order_by(CloudMetrics.timestamp).all()
            
            storage_utilization_data = [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "value": metric.metric_value,
                    "resource_id": metric.resource_id
                }
                for metric in storage_metrics
            ]
            
            # Performance metrics summary
            performance_metrics = await self._calculate_performance_summary(
                cpu_utilization_data, memory_utilization_data, 
                network_utilization_data, storage_utilization_data
            )
            
            # Resource efficiency analysis
            resource_efficiency = await self._analyze_resource_efficiency(
                db, account_id, start_time
            )
            
            return {
                "cpu_utilization": cpu_utilization_data,
                "memory_utilization": memory_utilization_data,
                "network_utilization": network_utilization_data,
                "storage_utilization": storage_utilization_data,
                "performance_metrics": performance_metrics,
                "resource_efficiency": resource_efficiency
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analytics: {str(e)}")
            raise
    
    async def _predict_future_costs(self, daily_costs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict future costs using linear regression"""
        try:
            if len(daily_costs_data) < 7:  # Need at least a week of data
                return []
            
            # Prepare data for regression
            dates = [datetime.strptime(item["date"], "%Y-%m-%d") for item in daily_costs_data]
            costs = [item["cost"] for item in daily_costs_data]
            
            # Convert dates to numeric values
            x = np.array([(date - dates[0]).days for date in dates]).reshape(-1, 1)
            y = np.array(costs)
            
            # Fit linear regression
            model = LinearRegression()
            model.fit(x, y)
            
            # Predict next 7 days
            last_date = dates[-1]
            predictions = []
            
            for i in range(1, 8):
                future_date = last_date + timedelta(days=i)
                future_x = np.array([(future_date - dates[0]).days]).reshape(-1, 1)
                predicted_cost = model.predict(future_x)[0]
                
                predictions.append({
                    "date": future_date.strftime("%Y-%m-%d"),
                    "predicted_cost": max(0, predicted_cost)  # Ensure non-negative
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting future costs: {str(e)}")
            return []
    
    async def _calculate_performance_summary(
        self, 
        cpu_data: List[Dict[str, Any]], 
        memory_data: List[Dict[str, Any]],
        network_data: List[Dict[str, Any]], 
        storage_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate performance metrics summary"""
        try:
            summary = {}
            
            # CPU metrics
            if cpu_data:
                cpu_values = [item["value"] for item in cpu_data]
                summary["cpu"] = {
                    "average": float(np.mean(cpu_values)),
                    "max": float(np.max(cpu_values)),
                    "min": float(np.min(cpu_values)),
                    "std": float(np.std(cpu_values))
                }
            
            # Memory metrics
            if memory_data:
                memory_values = [item["value"] for item in memory_data]
                summary["memory"] = {
                    "average": float(np.mean(memory_values)),
                    "max": float(np.max(memory_values)),
                    "min": float(np.min(memory_values)),
                    "std": float(np.std(memory_values))
                }
            
            # Network metrics
            if network_data:
                network_in = [item["value"] for item in network_data if item["metric_name"] == "NetworkIn"]
                network_out = [item["value"] for item in network_data if item["metric_name"] == "NetworkOut"]
                
                summary["network"] = {
                    "in_average": float(np.mean(network_in)) if network_in else 0,
                    "out_average": float(np.mean(network_out)) if network_out else 0,
                    "total_average": float(np.mean(network_in + network_out)) if network_in and network_out else 0
                }
            
            # Storage metrics
            if storage_data:
                storage_values = [item["value"] for item in storage_data]
                summary["storage"] = {
                    "average": float(np.mean(storage_values)),
                    "max": float(np.max(storage_values)),
                    "min": float(np.min(storage_values)),
                    "std": float(np.std(storage_values))
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating performance summary: {str(e)}")
            return {}
    
    async def _analyze_resource_efficiency(
        self, 
        db: Session, 
        account_id: Optional[int], 
        start_time: datetime
    ) -> List[Dict[str, Any]]:
        """Analyze resource efficiency"""
        try:
            # Get resources with their metrics
            resource_query = db.query(CloudResource)
            if account_id:
                resource_query = resource_query.filter(CloudResource.account_id == account_id)
            
            resources = resource_query.filter(CloudResource.is_monitored == True).all()
            
            efficiency_analysis = []
            
            for resource in resources:
                # Get recent metrics for this resource
                metrics = db.query(CloudMetrics).filter(
                    and_(
                        CloudMetrics.resource_id == resource.id,
                        CloudMetrics.timestamp >= start_time
                    )
                ).all()
                
                if metrics:
                    # Calculate efficiency metrics
                    cpu_metrics = [m for m in metrics if m.metric_name == 'CPUUtilization']
                    memory_metrics = [m for m in metrics if m.metric_name == 'MemoryUtilization']
                    
                    avg_cpu = np.mean([m.metric_value for m in cpu_metrics]) if cpu_metrics else 0
                    avg_memory = np.mean([m.metric_value for m in memory_metrics]) if memory_metrics else 0
                    
                    # Determine efficiency status
                    efficiency_status = "optimal"
                    if avg_cpu < 20 and avg_memory < 20:
                        efficiency_status = "underutilized"
                    elif avg_cpu > 80 or avg_memory > 80:
                        efficiency_status = "overutilized"
                    
                    efficiency_analysis.append({
                        "resource_id": resource.id,
                        "resource_name": resource.resource_name,
                        "resource_type": resource.resource_type,
                        "avg_cpu": float(avg_cpu),
                        "avg_memory": float(avg_memory),
                        "efficiency_status": efficiency_status,
                        "recommendation": self._get_efficiency_recommendation(efficiency_status, avg_cpu, avg_memory)
                    })
            
            return efficiency_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing resource efficiency: {str(e)}")
            return []
    
    def _get_efficiency_recommendation(
        self, 
        status: str, 
        avg_cpu: float, 
        avg_memory: float
    ) -> str:
        """Get efficiency recommendation based on metrics"""
        if status == "underutilized":
            return "Consider downsizing this resource to reduce costs"
        elif status == "overutilized":
            return "Consider upsizing this resource to improve performance"
        else:
            return "Resource utilization is optimal"
    
    async def generate_optimization_insights(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Generate optimization insights"""
        try:
            insights = []
            
            # Cost optimization insights
            cost_insights = await self.cost_analyzer.analyze_cost_optimization(db, account_id)
            insights.extend(cost_insights)
            
            # Performance optimization insights
            performance_insights = await self.performance_analyzer.analyze_performance_optimization(db, account_id)
            insights.extend(performance_insights)
            
            # Resource optimization insights
            resource_insights = await self.optimization_analyzer.analyze_resource_optimization(db, account_id)
            insights.extend(resource_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating optimization insights: {str(e)}")
            raise


class CostAnalyzer:
    """Cost analysis and optimization"""
    
    async def analyze_cost_optimization(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Analyze cost optimization opportunities"""
        try:
            insights = []
            
            # Analyze unused resources
            unused_resources = await self._find_unused_resources(db, account_id)
            if unused_resources:
                insights.append({
                    "type": "cost_optimization",
                    "title": "Unused Resources",
                    "description": f"Found {len(unused_resources)} unused resources that could be terminated",
                    "potential_savings": sum(resource.get("estimated_cost", 0) for resource in unused_resources),
                    "recommendations": unused_resources
                })
            
            # Analyze oversized resources
            oversized_resources = await self._find_oversized_resources(db, account_id)
            if oversized_resources:
                insights.append({
                    "type": "cost_optimization",
                    "title": "Oversized Resources",
                    "description": f"Found {len(oversized_resources)} resources that could be downsized",
                    "potential_savings": sum(resource.get("potential_savings", 0) for resource in oversized_resources),
                    "recommendations": oversized_resources
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing cost optimization: {str(e)}")
            return []
    
    async def _find_unused_resources(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find unused resources"""
        # Implementation for finding unused resources
        return []
    
    async def _find_oversized_resources(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find oversized resources"""
        # Implementation for finding oversized resources
        return []


class PerformanceAnalyzer:
    """Performance analysis and optimization"""
    
    async def analyze_performance_optimization(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Analyze performance optimization opportunities"""
        try:
            insights = []
            
            # Analyze performance bottlenecks
            bottlenecks = await self._find_performance_bottlenecks(db, account_id)
            if bottlenecks:
                insights.append({
                    "type": "performance_optimization",
                    "title": "Performance Bottlenecks",
                    "description": f"Found {len(bottlenecks)} performance bottlenecks",
                    "recommendations": bottlenecks
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing performance optimization: {str(e)}")
            return []
    
    async def _find_performance_bottlenecks(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find performance bottlenecks"""
        # Implementation for finding performance bottlenecks
        return []


class OptimizationAnalyzer:
    """Resource optimization analysis"""
    
    async def analyze_resource_optimization(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Analyze resource optimization opportunities"""
        try:
            insights = []
            
            # Analyze resource allocation
            allocation_issues = await self._find_allocation_issues(db, account_id)
            if allocation_issues:
                insights.append({
                    "type": "resource_optimization",
                    "title": "Resource Allocation Issues",
                    "description": f"Found {len(allocation_issues)} resource allocation issues",
                    "recommendations": allocation_issues
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing resource optimization: {str(e)}")
            return []
    
    async def _find_allocation_issues(
        self, 
        db: Session, 
        account_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find resource allocation issues"""
        # Implementation for finding allocation issues
        return []
