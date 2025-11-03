"""
Cloud Manager Service

This module provides the core cloud management functionality,
including multi-cloud provider integration, resource discovery,
and automated cloud operations.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from google.cloud import compute_v1
from google.cloud import storage
from google.cloud import billing_v1
from digitalocean import Manager as DigitalOceanManager
import requests
from sqlalchemy.orm import Session

from ..models.cloud_services import (
    CloudProvider, CloudAccount, CloudResource, CloudMetrics, 
    CloudCosts, CloudAlerts, CloudOptimization
)
from ..core.encryption import encrypt_data, decrypt_data
from ..utils.cloud_helpers import CloudHelpers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudManager:
    """Main cloud management service"""
    
    def __init__(self):
        self.helpers = CloudHelpers()
        self.providers = {
            'aws': AWSCloudProvider(),
            'azure': AzureCloudProvider(),
            'gcp': GCPCloudProvider(),
            'digitalocean': DigitalOceanCloudProvider()
        }
    
    async def sync_account_resources(self, account_id: int, db: Session) -> Dict[str, Any]:
        """Sync resources for a specific cloud account"""
        try:
            account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            # Update sync status
            account.sync_status = "syncing"
            account.last_sync = datetime.utcnow()
            db.commit()
            
            # Get provider
            provider = account.provider
            if not provider:
                raise ValueError(f"Provider not found for account {account_id}")
            
            # Initialize provider client
            provider_client = self.providers.get(provider.name.lower())
            if not provider_client:
                raise ValueError(f"Provider {provider.name} not supported")
            
            # Sync resources
            resources = await provider_client.discover_resources(account)
            
            # Update database
            sync_results = await self._update_resources_in_db(db, account, resources)
            
            # Update sync status
            account.sync_status = "completed"
            account.error_message = None
            db.commit()
            
            logger.info(f"Successfully synced {len(resources)} resources for account {account_id}")
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing account {account_id}: {str(e)}")
            account.sync_status = "failed"
            account.error_message = str(e)
            db.commit()
            raise
    
    async def _update_resources_in_db(
        self, 
        db: Session, 
        account: CloudAccount, 
        resources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update resources in database"""
        created_count = 0
        updated_count = 0
        errors = []
        
        for resource_data in resources:
            try:
                # Check if resource exists
                existing_resource = db.query(CloudResource).filter(
                    CloudResource.account_id == account.id,
                    CloudResource.resource_id == resource_data['resource_id']
                ).first()
                
                if existing_resource:
                    # Update existing resource
                    for key, value in resource_data.items():
                        if hasattr(existing_resource, key):
                            setattr(existing_resource, key, value)
                    existing_resource.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new resource
                    new_resource = CloudResource(
                        provider_id=account.provider_id,
                        account_id=account.id,
                        **resource_data
                    )
                    db.add(new_resource)
                    created_count += 1
                
            except Exception as e:
                errors.append(f"Error processing resource {resource_data.get('resource_id', 'unknown')}: {str(e)}")
        
        db.commit()
        
        return {
            "created": created_count,
            "updated": updated_count,
            "errors": errors,
            "total_processed": len(resources)
        }
    
    async def get_account_metrics(
        self, 
        account_id: int, 
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics for a specific account"""
        try:
            account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            # Get provider client
            provider_client = self.providers.get(account.provider.name.lower())
            if not provider_client:
                raise ValueError(f"Provider {account.provider.name} not supported")
            
            # Fetch metrics from cloud provider
            metrics = await provider_client.get_metrics(account, start_time, end_time)
            
            # Store metrics in database
            await self._store_metrics_in_db(db, account, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics for account {account_id}: {str(e)}")
            raise
    
    async def _store_metrics_in_db(
        self, 
        db: Session, 
        account: CloudAccount, 
        metrics: List[Dict[str, Any]]
    ):
        """Store metrics in database"""
        for metric_data in metrics:
            try:
                metric = CloudMetrics(
                    provider_id=account.provider_id,
                    account_id=account.id,
                    resource_id=metric_data.get('resource_id'),
                    **metric_data
                )
                db.add(metric)
            except Exception as e:
                logger.error(f"Error storing metric: {str(e)}")
        
        db.commit()
    
    async def get_account_costs(
        self, 
        account_id: int, 
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get costs for a specific account"""
        try:
            account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            # Get provider client
            provider_client = self.providers.get(account.provider.name.lower())
            if not provider_client:
                raise ValueError(f"Provider {account.provider.name} not supported")
            
            # Fetch costs from cloud provider
            costs = await provider_client.get_costs(account, start_date, end_date)
            
            # Store costs in database
            await self._store_costs_in_db(db, account, costs)
            
            return costs
            
        except Exception as e:
            logger.error(f"Error getting costs for account {account_id}: {str(e)}")
            raise
    
    async def _store_costs_in_db(
        self, 
        db: Session, 
        account: CloudAccount, 
        costs: List[Dict[str, Any]]
    ):
        """Store costs in database"""
        for cost_data in costs:
            try:
                cost = CloudCosts(
                    provider_id=account.provider_id,
                    account_id=account.id,
                    **cost_data
                )
                db.add(cost)
            except Exception as e:
                logger.error(f"Error storing cost: {str(e)}")
        
        db.commit()
    
    async def create_alert(
        self, 
        account_id: int, 
        alert_data: Dict[str, Any], 
        db: Session
    ) -> CloudAlerts:
        """Create a new cloud alert"""
        try:
            alert = CloudAlerts(
                account_id=account_id,
                **alert_data
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            logger.info(f"Created alert {alert.id} for account {account_id}")
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            db.rollback()
            raise
    
    async def check_alerts(self, account_id: int, db: Session) -> List[Dict[str, Any]]:
        """Check and trigger alerts for an account"""
        try:
            account = db.query(CloudAccount).filter(CloudAccount.id == account_id).first()
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            # Get active alerts
            alerts = db.query(CloudAlerts).filter(
                CloudAlerts.account_id == account_id,
                CloudAlerts.is_enabled == True,
                CloudAlerts.status == "active"
            ).all()
            
            triggered_alerts = []
            
            for alert in alerts:
                try:
                    # Check alert conditions
                    if await self._evaluate_alert_conditions(alert, account, db):
                        alert.triggered_at = datetime.utcnow()
                        alert.status = "triggered"
                        db.commit()
                        
                        triggered_alerts.append({
                            "alert_id": alert.id,
                            "alert_name": alert.alert_name,
                            "severity": alert.severity,
                            "message": alert.alert_description
                        })
                        
                        # Send notifications
                        await self._send_alert_notifications(alert)
                        
                except Exception as e:
                    logger.error(f"Error checking alert {alert.id}: {str(e)}")
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts for account {account_id}: {str(e)}")
            raise
    
    async def _evaluate_alert_conditions(
        self, 
        alert: CloudAlerts, 
        account: CloudAccount, 
        db: Session
    ) -> bool:
        """Evaluate alert conditions"""
        # This is a simplified implementation
        # In a real system, you would implement complex condition evaluation
        if alert.threshold_value and alert.current_value:
            if alert.current_value > alert.threshold_value:
                return True
        return False
    
    async def _send_alert_notifications(self, alert: CloudAlerts):
        """Send alert notifications"""
        # Implementation for sending notifications via various channels
        # (email, Slack, webhook, etc.)
        pass


class BaseCloudProvider:
    """Base class for cloud providers"""
    
    async def discover_resources(self, account: CloudAccount) -> List[Dict[str, Any]]:
        """Discover resources for an account"""
        raise NotImplementedError
    
    async def get_metrics(self, account: CloudAccount, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get metrics for an account"""
        raise NotImplementedError
    
    async def get_costs(self, account: CloudAccount, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get costs for an account"""
        raise NotImplementedError


class AWSCloudProvider(BaseCloudProvider):
    """AWS cloud provider implementation"""
    
    async def discover_resources(self, account: CloudAccount) -> List[Dict[str, Any]]:
        """Discover AWS resources"""
        try:
            # Decrypt credentials
            access_key = decrypt_data(account.access_key)
            secret_key = decrypt_data(account.secret_key)
            
            # Initialize AWS clients
            ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=account.region
            )
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=account.region
            )
            
            resources = []
            
            # Discover EC2 instances
            try:
                response = ec2_client.describe_instances()
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        resources.append({
                            'resource_id': instance['InstanceId'],
                            'resource_name': instance.get('Tags', [{}])[0].get('Value', instance['InstanceId']),
                            'resource_type': 'compute',
                            'service_name': 'EC2',
                            'region': instance['Placement']['AvailabilityZone'],
                            'status': instance['State']['Name'],
                            'size': instance['InstanceType'],
                            'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                            'metadata': {
                                'vpc_id': instance.get('VpcId'),
                                'subnet_id': instance.get('SubnetId'),
                                'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])]
                            }
                        })
            except Exception as e:
                logger.error(f"Error discovering EC2 instances: {str(e)}")
            
            # Discover S3 buckets
            try:
                response = s3_client.list_buckets()
                for bucket in response['Buckets']:
                    resources.append({
                        'resource_id': bucket['Name'],
                        'resource_name': bucket['Name'],
                        'resource_type': 'storage',
                        'service_name': 'S3',
                        'region': 'us-east-1',  # S3 is global
                        'status': 'active',
                        'metadata': {
                            'creation_date': bucket['CreationDate'].isoformat()
                        }
                    })
            except Exception as e:
                logger.error(f"Error discovering S3 buckets: {str(e)}")
            
            return resources
            
        except Exception as e:
            logger.error(f"Error discovering AWS resources: {str(e)}")
            raise
    
    async def get_metrics(self, account: CloudAccount, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get AWS CloudWatch metrics"""
        try:
            # Implementation for AWS CloudWatch metrics
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting AWS metrics: {str(e)}")
            raise
    
    async def get_costs(self, account: CloudAccount, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get AWS costs using Cost Explorer"""
        try:
            # Implementation for AWS Cost Explorer
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting AWS costs: {str(e)}")
            raise


class AzureCloudProvider(BaseCloudProvider):
    """Azure cloud provider implementation"""
    
    async def discover_resources(self, account: CloudAccount) -> List[Dict[str, Any]]:
        """Discover Azure resources"""
        try:
            # Implementation for Azure resource discovery
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error discovering Azure resources: {str(e)}")
            raise
    
    async def get_metrics(self, account: CloudAccount, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get Azure metrics"""
        try:
            # Implementation for Azure metrics
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting Azure metrics: {str(e)}")
            raise
    
    async def get_costs(self, account: CloudAccount, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get Azure costs"""
        try:
            # Implementation for Azure cost management
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting Azure costs: {str(e)}")
            raise


class GCPCloudProvider(BaseCloudProvider):
    """Google Cloud Platform provider implementation"""
    
    async def discover_resources(self, account: CloudAccount) -> List[Dict[str, Any]]:
        """Discover GCP resources"""
        try:
            # Implementation for GCP resource discovery
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error discovering GCP resources: {str(e)}")
            raise
    
    async def get_metrics(self, account: CloudAccount, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get GCP metrics"""
        try:
            # Implementation for GCP metrics
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting GCP metrics: {str(e)}")
            raise
    
    async def get_costs(self, account: CloudAccount, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get GCP costs"""
        try:
            # Implementation for GCP billing
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting GCP costs: {str(e)}")
            raise


class DigitalOceanCloudProvider(BaseCloudProvider):
    """DigitalOcean cloud provider implementation"""
    
    async def discover_resources(self, account: CloudAccount) -> List[Dict[str, Any]]:
        """Discover DigitalOcean resources"""
        try:
            # Implementation for DigitalOcean resource discovery
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error discovering DigitalOcean resources: {str(e)}")
            raise
    
    async def get_metrics(self, account: CloudAccount, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get DigitalOcean metrics"""
        try:
            # Implementation for DigitalOcean metrics
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting DigitalOcean metrics: {str(e)}")
            raise
    
    async def get_costs(self, account: CloudAccount, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get DigitalOcean costs"""
        try:
            # Implementation for DigitalOcean costs
            # This is a simplified version
            return []
        except Exception as e:
            logger.error(f"Error getting DigitalOcean costs: {str(e)}")
            raise
