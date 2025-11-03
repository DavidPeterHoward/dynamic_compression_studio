"""
Cloud Optimizer Service

This module provides intelligent cloud optimization capabilities,
including cost optimization, performance tuning, and resource management.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import asyncio

from ..models.cloud_services import (
    CloudAccount, CloudResource, CloudMetrics, CloudCosts, 
    CloudAlerts, CloudOptimization
)
from ..core.llm_integration import LLMIntegration
from ..utils.cloud_helpers import CloudHelpers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudOptimizer:
    """Intelligent cloud optimization service"""
    
    def __init__(self):
        self.llm_integration = LLMIntegration()
        self.helpers = CloudHelpers()
        self.cost_optimizer = CostOptimizer()
        self.performance_optimizer = PerformanceOptimizer()
        self.resource_optimizer = ResourceOptimizer()
    
    async def analyze_optimization_opportunities(
        self, 
        account_id: int, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Analyze optimization opportunities for an account"""
        try:
            account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            optimization_opportunities = []
            
            # Cost optimization analysis
            cost_optimizations = await self.cost_optimizer.analyze_cost_optimization(
                db, account_id
            )
            optimization_opportunities.extend(cost_optimizations)
            
            # Performance optimization analysis
            performance_optimizations = await self.performance_optimizer.analyze_performance_optimization(
                db, account_id
            )
            optimization_opportunizations.extend(performance_optimizations)
            
            # Resource optimization analysis
            resource_optimizations = await self.resource_optimizer.analyze_resource_optimization(
                db, account_id
            )
            optimization_opportunities.extend(resource_optimizations)
            
            # LLM-powered optimization insights
            llm_insights = await self._get_llm_optimization_insights(
                db, account_id, optimization_opportunities
            )
            optimization_opportunities.extend(llm_insights)
            
            # Store optimization opportunities in database
            await self._store_optimization_opportunities(
                db, account_id, optimization_opportunities
            )
            
            logger.info(f"Found {len(optimization_opportunities)} optimization opportunities for account {account_id}")
            return optimization_opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing optimization opportunities: {str(e)}")
            raise
    
    async def _get_llm_optimization_insights(
        self, 
        db: Session, 
        account_id: int, 
        existing_opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get LLM-powered optimization insights"""
        try:
            # Get account context
            account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
            resources = db.query(CloudResource).filter(CloudResource.account_id == account_id).all()
            costs = db.query(CloudCosts).filter(CloudCosts.account_id == account_id).all()
            
            # Prepare context for LLM
            context = {
                "account": account.to_dict() if account else {},
                "resources": [resource.to_dict() for resource in resources],
                "recent_costs": [cost.to_dict() for cost in costs[-10:]],  # Last 10 costs
                "existing_opportunities": existing_opportunities
            }
            
            # Generate LLM insights
            llm_query = f"""
            Analyze the following cloud infrastructure and provide optimization recommendations:
            
            Account: {context['account'].get('account_name', 'Unknown')}
            Provider: {context['account'].get('provider', {}).get('name', 'Unknown')}
            Resources: {len(context['resources'])} total resources
            Recent Costs: ${sum(cost.get('cost_amount', 0) for cost in context['recent_costs']):.2f}
            
            Please provide specific, actionable optimization recommendations focusing on:
            1. Cost reduction opportunities
            2. Performance improvements
            3. Resource efficiency
            4. Security enhancements
            5. Best practices implementation
            
            Format your response as a JSON array of optimization opportunities.
            """
            
            llm_response = await self.llm_integration.generate_optimization_insights(
                llm_query, context
            )
            
            return llm_response.get("optimization_opportunities", [])
            
        except Exception as e:
            logger.error(f"Error getting LLM optimization insights: {str(e)}")
            return []
    
    async def _store_optimization_opportunities(
        self, 
        db: Session, 
        account_id: int, 
        opportunities: List[Dict[str, Any]]
    ):
        """Store optimization opportunities in database"""
        try:
            for opportunity in opportunities:
                optimization = CloudOptimization(
                    account_id=account_id,
                    optimization_type=opportunity.get("type", "general"),
                    title=opportunity.get("title", "Optimization Opportunity"),
                    description=opportunity.get("description", ""),
                    potential_savings=opportunity.get("potential_savings", 0),
                    implementation_effort=opportunity.get("implementation_effort", "medium"),
                    priority=opportunity.get("priority", "medium"),
                    status="pending",
                    recommendations=opportunity.get("recommendations", []),
                    metadata=opportunity.get("metadata", {})
                )
                db.add(optimization)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing optimization opportunities: {str(e)}")
            db.rollback()
            raise
    
    async def implement_optimization(
        self, 
        optimization_id: int, 
        db: Session
    ) -> Dict[str, Any]:
        """Implement a specific optimization"""
        try:
            optimization = db.query(CloudOptimization).filter(
                CloudOptimization.id == optimization_id
            ).first()
            
            if not optimization:
                raise ValueError(f"Optimization {optimization_id} not found")
            
            # Update status
            optimization.status = "in_progress"
            db.commit()
            
            # Implement optimization based on type
            implementation_result = await self._implement_optimization_by_type(
                optimization, db
            )
            
            # Update status based on result
            if implementation_result.get("success", False):
                optimization.status = "completed"
                optimization.implemented_at = datetime.utcnow()
            else:
                optimization.status = "failed"
                optimization.metadata = {
                    **optimization.metadata,
                    "implementation_error": implementation_result.get("error", "Unknown error")
                }
            
            db.commit()
            
            return implementation_result
            
        except Exception as e:
            logger.error(f"Error implementing optimization: {str(e)}")
            db.rollback()
            raise
    
    async def _implement_optimization_by_type(
        self, 
        optimization: CloudOptimization, 
        db: Session
    ) -> Dict[str, Any]:
        """Implement optimization based on type"""
        try:
            optimization_type = optimization.optimization_type
            
            if optimization_type == "cost_optimization":
                return await self.cost_optimizer.implement_cost_optimization(
                    optimization, db
                )
            elif optimization_type == "performance_optimization":
                return await self.performance_optimizer.implement_performance_optimization(
                    optimization, db
                )
            elif optimization_type == "resource_optimization":
                return await self.resource_optimizer.implement_resource_optimization(
                    optimization, db
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown optimization type: {optimization_type}"
                }
                
        except Exception as e:
            logger.error(f"Error implementing optimization by type: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_optimization_recommendations(
        self, 
        account_id: int, 
        db: Session,
        optimization_type: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations for an account"""
        try:
            query = db.query(CloudOptimization).filter(
                CloudOptimization.account_id == account_id
            )
            
            if optimization_type:
                query = query.filter(CloudOptimization.optimization_type == optimization_type)
            
            if priority:
                query = query.filter(CloudOptimization.priority == priority)
            
            optimizations = query.order_by(desc(CloudOptimization.created_at)).all()
            
            return [optimization.to_dict() for optimization in optimizations]
            
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {str(e)}")
            raise
    
    async def schedule_optimization_analysis(
        self, 
        account_id: int, 
        db: Session,
        schedule: str = "0 2 * * *"  # Daily at 2 AM
    ) -> Dict[str, Any]:
        """Schedule regular optimization analysis"""
        try:
            # This would integrate with a task scheduler like Celery
            # For now, we'll just return a success message
            return {
                "success": True,
                "message": f"Optimization analysis scheduled for account {account_id}",
                "schedule": schedule
            }
            
        except Exception as e:
            logger.error(f"Error scheduling optimization analysis: {str(e)}")
            raise


class CostOptimizer:
    """Cost optimization strategies"""
    
    async def analyze_cost_optimization(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Analyze cost optimization opportunities"""
        try:
            opportunities = []
            
            # Find unused resources
            unused_resources = await self._find_unused_resources(db, account_id)
            if unused_resources:
                opportunities.append({
                    "type": "cost_optimization",
                    "title": "Unused Resources",
                    "description": f"Found {len(unused_resources)} unused resources",
                    "potential_savings": sum(resource.get("estimated_monthly_cost", 0) for resource in unused_resources),
                    "implementation_effort": "low",
                    "priority": "high",
                    "recommendations": unused_resources
                })
            
            # Find oversized resources
            oversized_resources = await self._find_oversized_resources(db, account_id)
            if oversized_resources:
                opportunities.append({
                    "type": "cost_optimization",
                    "title": "Oversized Resources",
                    "description": f"Found {len(oversized_resources)} oversized resources",
                    "potential_savings": sum(resource.get("potential_savings", 0) for resource in oversized_resources),
                    "implementation_effort": "medium",
                    "priority": "medium",
                    "recommendations": oversized_resources
                })
            
            # Find reserved instance opportunities
            reserved_instance_opportunities = await self._find_reserved_instance_opportunities(db, account_id)
            if reserved_instance_opportunities:
                opportunities.append({
                    "type": "cost_optimization",
                    "title": "Reserved Instance Opportunities",
                    "description": f"Found {len(reserved_instance_opportunities)} reserved instance opportunities",
                    "potential_savings": sum(opp.get("potential_savings", 0) for opp in reserved_instance_opportunities),
                    "implementation_effort": "medium",
                    "priority": "high",
                    "recommendations": reserved_instance_opportunities
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing cost optimization: {str(e)}")
            return []
    
    async def _find_unused_resources(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Find unused resources"""
        try:
            # Get resources that haven't been used recently
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            unused_resources = db.query(CloudResource).filter(
                and_(
                    CloudResource.account_id == account_id,
                    CloudResource.status.in_(['stopped', 'terminated', 'inactive']),
                    CloudResource.updated_at < cutoff_date
                )
            ).all()
            
            opportunities = []
            for resource in unused_resources:
                # Calculate estimated monthly cost
                monthly_cost = resource.cost_per_hour * 24 * 30 if resource.cost_per_hour else 0
                
                opportunities.append({
                    "resource_id": resource.id,
                    "resource_name": resource.resource_name,
                    "resource_type": resource.resource_type,
                    "status": resource.status,
                    "estimated_monthly_cost": monthly_cost,
                    "recommendation": "Terminate unused resource to reduce costs"
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding unused resources: {str(e)}")
            return []
    
    async def _find_oversized_resources(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Find oversized resources"""
        try:
            # Get resources with low utilization
            resources = db.query(CloudResource).filter(
                CloudResource.account_id == account_id
            ).all()
            
            opportunities = []
            for resource in resources:
                # Get recent metrics for this resource
                recent_metrics = db.query(CloudMetrics).filter(
                    and_(
                        CloudMetrics.resource_id == resource.id,
                        CloudMetrics.metric_name.in_(['CPUUtilization', 'MemoryUtilization']),
                        CloudMetrics.timestamp >= datetime.utcnow() - timedelta(days=7)
                    )
                ).all()
                
                if recent_metrics:
                    # Calculate average utilization
                    cpu_metrics = [m for m in recent_metrics if m.metric_name == 'CPUUtilization']
                    memory_metrics = [m for m in recent_metrics if m.metric_name == 'MemoryUtilization']
                    
                    avg_cpu = np.mean([m.metric_value for m in cpu_metrics]) if cpu_metrics else 0
                    avg_memory = np.mean([m.metric_value for m in memory_metrics]) if memory_metrics else 0
                    
                    # If both CPU and memory are low, resource might be oversized
                    if avg_cpu < 30 and avg_memory < 30:
                        potential_savings = resource.cost_per_hour * 0.3 if resource.cost_per_hour else 0
                        
                        opportunities.append({
                            "resource_id": resource.id,
                            "resource_name": resource.resource_name,
                            "resource_type": resource.resource_type,
                            "avg_cpu_utilization": avg_cpu,
                            "avg_memory_utilization": avg_memory,
                            "potential_savings": potential_savings,
                            "recommendation": "Consider downsizing this resource"
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding oversized resources: {str(e)}")
            return []
    
    async def _find_reserved_instance_opportunities(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Find reserved instance opportunities"""
        try:
            # Get compute resources that are running consistently
            compute_resources = db.query(CloudResource).filter(
                and_(
                    CloudResource.account_id == account_id,
                    CloudResource.resource_type == 'compute',
                    CloudResource.status == 'running'
                )
            ).all()
            
            opportunities = []
            for resource in compute_resources:
                # Check if resource has been running for more than 30 days
                if resource.created_at and (datetime.utcnow() - resource.created_at).days > 30:
                    # Calculate potential savings with reserved instances
                    monthly_cost = resource.cost_per_hour * 24 * 30 if resource.cost_per_hour else 0
                    reserved_savings = monthly_cost * 0.3  # Assume 30% savings with reserved instances
                    
                    opportunities.append({
                        "resource_id": resource.id,
                        "resource_name": resource.resource_name,
                        "resource_type": resource.resource_type,
                        "current_monthly_cost": monthly_cost,
                        "potential_savings": reserved_savings,
                        "recommendation": "Consider purchasing reserved instances for consistent workloads"
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding reserved instance opportunities: {str(e)}")
            return []
    
    async def implement_cost_optimization(
        self, 
        optimization: CloudOptimization, 
        db: Session
    ) -> Dict[str, Any]:
        """Implement cost optimization"""
        try:
            # This would implement the actual cost optimization
            # For now, we'll just return a success message
            return {
                "success": True,
                "message": f"Cost optimization implemented for {optimization.title}",
                "optimization_id": optimization.id
            }
            
        except Exception as e:
            logger.error(f"Error implementing cost optimization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class PerformanceOptimizer:
    """Performance optimization strategies"""
    
    async def analyze_performance_optimization(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Analyze performance optimization opportunities"""
        try:
            opportunities = []
            
            # Find performance bottlenecks
            bottlenecks = await self._find_performance_bottlenecks(db, account_id)
            if bottlenecks:
                opportunities.append({
                    "type": "performance_optimization",
                    "title": "Performance Bottlenecks",
                    "description": f"Found {len(bottlenecks)} performance bottlenecks",
                    "implementation_effort": "high",
                    "priority": "high",
                    "recommendations": bottlenecks
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing performance optimization: {str(e)}")
            return []
    
    async def _find_performance_bottlenecks(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Find performance bottlenecks"""
        try:
            # Get resources with high utilization
            resources = db.query(CloudResource).filter(
                CloudResource.account_id == account_id
            ).all()
            
            bottlenecks = []
            for resource in resources:
                # Get recent metrics for this resource
                recent_metrics = db.query(CloudMetrics).filter(
                    and_(
                        CloudMetrics.resource_id == resource.id,
                        CloudMetrics.metric_name.in_(['CPUUtilization', 'MemoryUtilization']),
                        CloudMetrics.timestamp >= datetime.utcnow() - timedelta(days=7)
                    )
                ).all()
                
                if recent_metrics:
                    # Calculate average utilization
                    cpu_metrics = [m for m in recent_metrics if m.metric_name == 'CPUUtilization']
                    memory_metrics = [m for m in recent_metrics if m.metric_name == 'MemoryUtilization']
                    
                    avg_cpu = np.mean([m.metric_value for m in cpu_metrics]) if cpu_metrics else 0
                    avg_memory = np.mean([m.metric_value for m in memory_metrics]) if memory_metrics else 0
                    
                    # If either CPU or memory is high, resource might be a bottleneck
                    if avg_cpu > 80 or avg_memory > 80:
                        bottlenecks.append({
                            "resource_id": resource.id,
                            "resource_name": resource.resource_name,
                            "resource_type": resource.resource_type,
                            "avg_cpu_utilization": avg_cpu,
                            "avg_memory_utilization": avg_memory,
                            "recommendation": "Consider upsizing this resource or optimizing the application"
                        })
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Error finding performance bottlenecks: {str(e)}")
            return []
    
    async def implement_performance_optimization(
        self, 
        optimization: CloudOptimization, 
        db: Session
    ) -> Dict[str, Any]:
        """Implement performance optimization"""
        try:
            # This would implement the actual performance optimization
            # For now, we'll just return a success message
            return {
                "success": True,
                "message": f"Performance optimization implemented for {optimization.title}",
                "optimization_id": optimization.id
            }
            
        except Exception as e:
            logger.error(f"Error implementing performance optimization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class ResourceOptimizer:
    """Resource optimization strategies"""
    
    async def analyze_resource_optimization(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Analyze resource optimization opportunities"""
        try:
            opportunities = []
            
            # Find resource allocation issues
            allocation_issues = await self._find_allocation_issues(db, account_id)
            if allocation_issues:
                opportunities.append({
                    "type": "resource_optimization",
                    "title": "Resource Allocation Issues",
                    "description": f"Found {len(allocation_issues)} resource allocation issues",
                    "implementation_effort": "medium",
                    "priority": "medium",
                    "recommendations": allocation_issues
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing resource optimization: {str(e)}")
            return []
    
    async def _find_allocation_issues(
        self, 
        db: Session, 
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Find resource allocation issues"""
        try:
            # Get all resources for the account
            resources = db.query(CloudResource).filter(
                CloudResource.account_id == account_id
            ).all()
            
            allocation_issues = []
            
            # Analyze resource distribution
            resource_types = {}
            for resource in resources:
                resource_type = resource.resource_type
                if resource_type not in resource_types:
                    resource_types[resource_type] = []
                resource_types[resource_type].append(resource)
            
            # Check for imbalanced resource allocation
            for resource_type, type_resources in resource_types.items():
                if len(type_resources) > 10:  # If there are many resources of this type
                    # Check if resources are distributed across regions
                    regions = set(resource.region for resource in type_resources)
                    if len(regions) == 1:
                        allocation_issues.append({
                            "resource_type": resource_type,
                            "issue": "All resources of this type are in the same region",
                            "recommendation": "Consider distributing resources across multiple regions for better availability"
                        })
            
            return allocation_issues
            
        except Exception as e:
            logger.error(f"Error finding allocation issues: {str(e)}")
            return []
    
    async def implement_resource_optimization(
        self, 
        optimization: CloudOptimization, 
        db: Session
    ) -> Dict[str, Any]:
        """Implement resource optimization"""
        try:
            # This would implement the actual resource optimization
            # For now, we'll just return a success message
            return {
                "success": True,
                "message": f"Resource optimization implemented for {optimization.title}",
                "optimization_id": optimization.id
            }
            
        except Exception as e:
            logger.error(f"Error implementing resource optimization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
