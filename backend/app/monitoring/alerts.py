"""
Comprehensive alerting system for Dynamic Compression Algorithms.

This module provides:
- Intelligent alert rules
- Multiple notification channels
- Automated incident response
- Alert escalation
- Alert history and management
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
import json
import smtplib
import requests
import psutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .logging import get_logger, LoggerMixin
from .metrics import get_metrics_collector
from .health import get_health_monitor, HealthStatus


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertRule:
    """Represents an alert rule."""
    
    def __init__(
        self,
        name: str,
        condition: Callable,
        severity: AlertSeverity,
        message_template: str,
        notification_channels: List[str],
        cooldown_period: int = 300,  # 5 minutes
        enabled: bool = True
    ):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message_template = message_template
        self.notification_channels = notification_channels
        self.cooldown_period = cooldown_period
        self.enabled = enabled
        self.last_triggered = None


class Alert:
    """Represents an alert instance."""
    
    def __init__(
        self,
        rule_name: str,
        severity: AlertSeverity,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.id = f"{rule_name}_{int(time.time())}"
        self.rule_name = rule_name
        self.severity = severity
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow()
        self.status = AlertStatus.ACTIVE
        self.acknowledged_by = None
        self.acknowledged_at = None
        self.resolved_at = None
        self.notifications_sent = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "notifications_sent": self.notifications_sent
        }


class NotificationChannel:
    """Base class for notification channels."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = get_logger(f"alerting.{name}")
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send notification for an alert."""
        raise NotImplementedError("Subclasses must implement send_notification")


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel."""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send email notification."""
        try:
            smtp_server = self.config.get("smtp_server", "localhost")
            smtp_port = self.config.get("smtp_port", 587)
            username = self.config.get("username")
            password = self.config.get("password")
            from_email = self.config.get("from_email")
            to_emails = self.config.get("to_emails", [])
            
            if not all([username, password, from_email, to_emails]):
                self.logger.error("Missing email configuration")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.rule_name}"
            
            # Create message body
            body = f"""
Alert Details:
- Rule: {alert.rule_name}
- Severity: {alert.severity.value}
- Message: {alert.message}
- Timestamp: {alert.timestamp.isoformat()}
- Details: {json.dumps(alert.details, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
            
            self.logger.info(f"Email notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel."""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send Slack notification."""
        try:
            webhook_url = self.config.get("webhook_url")
            channel = self.config.get("channel", "#alerts")
            
            if not webhook_url:
                self.logger.error("Missing Slack webhook URL")
                return False
            
            # Create message
            color_map = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9500",
                AlertSeverity.CRITICAL: "#ff0000",
                AlertSeverity.EMERGENCY: "#8b0000"
            }
            
            payload = {
                "channel": channel,
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#36a64f"),
                        "title": f"Alert: {alert.rule_name}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.isoformat(),
                                "short": True
                            },
                            {
                                "title": "Details",
                                "value": json.dumps(alert.details, indent=2),
                                "short": False
                            }
                        ],
                        "footer": "Dynamic Compression Algorithms Alerting System"
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Slack notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Webhook notification channel."""
    
    async def send_notification(self, alert: Alert) -> bool:
        """Send webhook notification."""
        try:
            webhook_url = self.config.get("webhook_url")
            headers = self.config.get("headers", {})
            
            if not webhook_url:
                self.logger.error("Missing webhook URL")
                return False
            
            # Create payload
            payload = {
                "alert": alert.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "dynamic-compression-algorithms"
            }
            
            # Send webhook
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            self.logger.info(f"Webhook notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            return False


class AlertManager(LoggerMixin):
    """Comprehensive alert management system."""
    
    def __init__(self):
        """Initialize the alert manager."""
        self.logger.info("Initializing alert manager")
        
        # Alert rules
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Active alerts
        self.active_alerts: Dict[str, Alert] = {}
        
        # Alert history
        self.alert_history: List[Alert] = []
        
        # Notification channels
        self.notification_channels: Dict[str, NotificationChannel] = {}
        
        # Background monitoring
        self._running = False
        self._background_thread = None
        self.check_interval = 30  # seconds
        
        # Register default alert rules
        self._register_default_rules()
        
        self.logger.info("Alert manager initialized successfully")
    
    def _register_default_rules(self):
        """Register default alert rules."""
        # High error rate alert
        self.register_alert_rule(
            name="high_error_rate",
            condition=self._check_high_error_rate,
            severity=AlertSeverity.CRITICAL,
            message_template="High error rate detected: {error_rate}% over the last 5 minutes",
            notification_channels=["email", "slack"],
            cooldown_period=300
        )
        
        # High CPU usage alert
        self.register_alert_rule(
            name="high_cpu_usage",
            condition=self._check_high_cpu_usage,
            severity=AlertSeverity.WARNING,
            message_template="High CPU usage detected: {cpu_usage}%",
            notification_channels=["email"],
            cooldown_period=600
        )
        
        # High memory usage alert
        self.register_alert_rule(
            name="high_memory_usage",
            condition=self._check_high_memory_usage,
            severity=AlertSeverity.WARNING,
            message_template="High memory usage detected: {memory_usage}%",
            notification_channels=["email"],
            cooldown_period=600
        )
        
        # Database connection issues
        self.register_alert_rule(
            name="database_connection_issues",
            condition=self._check_database_health,
            severity=AlertSeverity.CRITICAL,
            message_template="Database connection issues detected",
            notification_channels=["email", "slack", "webhook"],
            cooldown_period=300
        )
        
        # Compression engine failures
        self.register_alert_rule(
            name="compression_engine_failures",
            condition=self._check_compression_engine_health,
            severity=AlertSeverity.CRITICAL,
            message_template="Compression engine failures detected",
            notification_channels=["email", "slack"],
            cooldown_period=300
        )
        
        # High response time alert
        self.register_alert_rule(
            name="high_response_time",
            condition=self._check_high_response_time,
            severity=AlertSeverity.WARNING,
            message_template="High response time detected: {response_time}ms",
            notification_channels=["email"],
            cooldown_period=300
        )
    
    def register_alert_rule(
        self,
        name: str,
        condition: Callable,
        severity: AlertSeverity,
        message_template: str,
        notification_channels: List[str],
        cooldown_period: int = 300,
        enabled: bool = True
    ):
        """Register an alert rule."""
        rule = AlertRule(
            name=name,
            condition=condition,
            severity=severity,
            message_template=message_template,
            notification_channels=notification_channels,
            cooldown_period=cooldown_period,
            enabled=enabled
        )
        
        self.alert_rules[name] = rule
        self.logger.info(f"Registered alert rule: {name}")
    
    def register_notification_channel(
        self,
        name: str,
        channel: NotificationChannel
    ):
        """Register a notification channel."""
        self.notification_channels[name] = channel
        self.logger.info(f"Registered notification channel: {name}")
    
    async def check_alert_rules(self):
        """Check all alert rules."""
        self.logger.debug("Checking alert rules")
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown period
            if (rule.last_triggered and 
                datetime.utcnow() - rule.last_triggered < timedelta(seconds=rule.cooldown_period)):
                continue
            
            try:
                # Check condition
                if asyncio.iscoroutinefunction(rule.condition):
                    result = await rule.condition()
                else:
                    result = rule.condition()
                
                if result:
                    # Alert condition met
                    if isinstance(result, dict):
                        message = rule.message_template.format(**result)
                        details = result
                    else:
                        message = rule.message_template
                        details = {}
                    
                    await self.trigger_alert(rule, message, details)
                    rule.last_triggered = datetime.utcnow()
                
            except Exception as e:
                self.logger.error(f"Error checking alert rule {rule_name}: {e}")
    
    async def trigger_alert(
        self,
        rule: AlertRule,
        message: str,
        details: Dict[str, Any]
    ):
        """Trigger an alert."""
        alert = Alert(
            rule_name=rule.name,
            severity=rule.severity,
            message=message,
            details=details
        )
        
        # Add to active alerts
        self.active_alerts[alert.id] = alert
        
        # Add to history
        self.alert_history.append(alert)
        
        # Keep history size manageable
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        self.logger.warning(f"Alert triggered: {alert.id} - {message}")
        
        # Send notifications
        await self.send_notifications(alert, rule.notification_channels)
    
    async def send_notifications(
        self,
        alert: Alert,
        channel_names: List[str]
    ):
        """Send notifications for an alert."""
        for channel_name in channel_names:
            if channel_name in self.notification_channels:
                channel = self.notification_channels[channel_name]
                try:
                    success = await channel.send_notification(alert)
                    if success:
                        alert.notifications_sent.append({
                            "channel": channel_name,
                            "timestamp": datetime.utcnow().isoformat(),
                            "status": "sent"
                        })
                    else:
                        alert.notifications_sent.append({
                            "channel": channel_name,
                            "timestamp": datetime.utcnow().isoformat(),
                            "status": "failed"
                        })
                except Exception as e:
                    self.logger.error(f"Error sending notification via {channel_name}: {e}")
                    alert.notifications_sent.append({
                        "channel": channel_name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "error",
                        "error": str(e)
                    })
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            del self.active_alerts[alert_id]
            self.logger.info(f"Alert {alert_id} resolved")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_alert_history(
        self,
        limit: int = 100,
        severity: Optional[AlertSeverity] = None,
        status: Optional[AlertStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get alert history with optional filtering."""
        alerts = self.alert_history
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        return [alert.to_dict() for alert in alerts[-limit:]]
    
    def start_background_monitoring(self):
        """Start background alert monitoring."""
        if self._running:
            return
        
        self._running = True
        self._background_thread = threading.Thread(
            target=self._background_monitoring_loop,
            daemon=True
        )
        self._background_thread.start()
        self.logger.info("Background alert monitoring started")
    
    def stop_background_monitoring(self):
        """Stop background alert monitoring."""
        self._running = False
        if self._background_thread:
            self._background_thread.join()
        self.logger.info("Background alert monitoring stopped")
    
    def _background_monitoring_loop(self):
        """Background loop for alert monitoring."""
        while self._running:
            try:
                # Run alert checks in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.check_alert_rules())
                loop.close()
                
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in background alert monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    # Default alert condition implementations
    async def _check_high_error_rate(self) -> Optional[Dict[str, Any]]:
        """Check for high error rate."""
        try:
            metrics = get_metrics_collector()
            # This would typically calculate error rate from metrics
            # For now, we'll simulate a check
            error_rate = 2.5  # Simulated error rate
            
            if error_rate > 5.0:
                return {
                    "error_rate": error_rate,
                    "threshold": 5.0
                }
            return None
        except Exception as e:
            self.logger.error(f"Error checking high error rate: {e}")
            return None
    
    async def _check_high_cpu_usage(self) -> Optional[Dict[str, Any]]:
        """Check for high CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 80:
                return {
                    "cpu_usage": cpu_percent,
                    "threshold": 80
                }
            return None
        except Exception as e:
            self.logger.error(f"Error checking high CPU usage: {e}")
            return None
    
    async def _check_high_memory_usage(self) -> Optional[Dict[str, Any]]:
        """Check for high memory usage."""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 85:
                return {
                    "memory_usage": memory.percent,
                    "threshold": 85
                }
            return None
        except Exception as e:
            self.logger.error(f"Error checking high memory usage: {e}")
            return None
    
    async def _check_database_health(self) -> Optional[Dict[str, Any]]:
        """Check database health."""
        try:
            health_monitor = get_health_monitor()
            components = await health_monitor.check_all_health()
            
            db_component = components.get("database")
            if db_component and db_component.status != HealthStatus.HEALTHY:
                return {
                    "status": db_component.status.value,
                    "message": db_component.message
                }
            return None
        except Exception as e:
            self.logger.error(f"Error checking database health: {e}")
            return None
    
    async def _check_compression_engine_health(self) -> Optional[Dict[str, Any]]:
        """Check compression engine health."""
        try:
            health_monitor = get_health_monitor()
            components = await health_monitor.check_all_health()
            
            engine_component = components.get("compression_engine")
            if engine_component and engine_component.status != HealthStatus.HEALTHY:
                return {
                    "status": engine_component.status.value,
                    "message": engine_component.message
                }
            return None
        except Exception as e:
            self.logger.error(f"Error checking compression engine health: {e}")
            return None
    
    async def _check_high_response_time(self) -> Optional[Dict[str, Any]]:
        """Check for high response time."""
        try:
            # This would typically check response time metrics
            # For now, we'll simulate a check
            response_time = 150  # Simulated response time in ms
            
            if response_time > 100:
                return {
                    "response_time": response_time,
                    "threshold": 100
                }
            return None
        except Exception as e:
            self.logger.error(f"Error checking high response time: {e}")
            return None


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def setup_alerting(
    enable_background_monitoring: bool = True,
    check_interval: int = 30
) -> AlertManager:
    """
    Setup the alerting system.
    
    Args:
        enable_background_monitoring: Enable background alert monitoring
        check_interval: Alert check interval in seconds
        
    Returns:
        Alert manager instance
    """
    global _alert_manager
    
    if _alert_manager is None:
        _alert_manager = AlertManager()
        _alert_manager.check_interval = check_interval
        
        if enable_background_monitoring:
            _alert_manager.start_background_monitoring()
    
    return _alert_manager


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    if _alert_manager is None:
        return setup_alerting()
    return _alert_manager


# Initialize alerting on module import
if _alert_manager is None:
    setup_alerting()
