"""
Background Health Monitor Service

This service runs periodic health checks in the background and provides
alerts for system issues, performance degradation, and critical failures.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from services.health_check_types import SystemHealthReport, HealthStatus, ComponentType
from utils.async_utils import async_operation_context


class AlertLevel(Enum):
    """Alert level enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """Health alert data structure."""
    level: AlertLevel
    component_name: str
    component_type: ComponentType
    message: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class BackgroundHealthMonitor:
    """Background health monitoring service."""
    
    def __init__(self, team_id: str, check_interval: int = 300):
        self.team_id = team_id
        self.check_interval = check_interval
        self.logger = logging.getLogger(__name__)
        
        # Health check service
        self.health_check_service = HealthCheckService(team_id)
        
        # Background task management
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        # Alert management
        self.active_alerts: Dict[str, HealthAlert] = {}
        self.alert_history: List[HealthAlert] = []
        self.max_alert_history = 1000
        
        # Alert handlers
        self._alert_handlers: List[Callable[[HealthAlert], None]] = []
        
        # Performance tracking
        self.performance_metrics: Dict[str, List[float]] = {
            "response_times": [],
            "check_durations": [],
            "alert_counts": []
        }
        
        self.logger.info(f"✅ BackgroundHealthMonitor initialized for team {team_id}")
    
    async def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._running:
            self.logger.warning("Health monitoring is already running")
            return
        
        self._running = True
        self._shutdown_event.clear()
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info(f"🚀 Background health monitoring started for team {self.team_id}")
    
    async def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        if not self._running:
            self.logger.warning("Health monitoring is not running")
            return
        
        self._running = False
        self._shutdown_event.set()
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info(f"🛑 Background health monitoring stopped for team {self.team_id}")
    
    @async_operation_context("background_health_monitor")
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        self.logger.info("🔄 Starting health monitoring loop")
        
        try:
            while self._running and not self._shutdown_event.is_set():
                start_time = datetime.now()
                
                try:
                    # Perform health check
                    await self._perform_health_check()
                    
                    # Process alerts
                    await self._process_alerts()
                    
                    # Update performance metrics
                    self._update_performance_metrics(start_time)
                    
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    await self._create_alert(
                        AlertLevel.ERROR,
                        "background_monitor",
                        ComponentType.SERVICE,
                        f"Monitoring loop error: {str(e)}"
                    )
                
                # Wait for next check interval
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self.check_interval
                    )
                except asyncio.TimeoutError:
                    # Continue monitoring
                    pass
                
        except asyncio.CancelledError:
            self.logger.info("Health monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Fatal error in monitoring loop: {e}")
        finally:
            self.logger.info("Health monitoring loop ended")
    
    async def _perform_health_check(self) -> None:
        """Perform health check and process results."""
        try:
            # Perform comprehensive health check
            report = await self.health_check_service.perform_comprehensive_health_check()
            
            # Process health check results
            await self._process_health_report(report)
            
        except Exception as e:
            self.logger.error(f"Error performing health check: {e}")
            await self._create_alert(
                AlertLevel.ERROR,
                "health_check_service",
                ComponentType.SERVICE,
                f"Health check failed: {str(e)}"
            )
    
    async def _process_health_report(self, report: SystemHealthReport) -> None:
        """Process health check report and create alerts."""
        # Check overall system health
        if report.overall_status == HealthStatus.UNHEALTHY:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "system_overall",
                ComponentType.SERVICE,
                f"System is unhealthy: {len(report.critical_issues)} critical issues",
                {"critical_issues": report.critical_issues}
            )
        elif report.overall_status == HealthStatus.DEGRADED:
            await self._create_alert(
                AlertLevel.WARNING,
                "system_overall",
                ComponentType.SERVICE,
                f"System is degraded: {len(report.warnings)} warnings",
                {"warnings": report.warnings}
            )
        
        # Process individual component checks
        for check in report.checks:
            if check.status == HealthStatus.UNHEALTHY:
                await self._create_alert(
                    AlertLevel.ERROR,
                    check.component_name,
                    check.component_type,
                    check.message,
                    check.details
                )
            elif check.status == HealthStatus.DEGRADED:
                await self._create_alert(
                    AlertLevel.WARNING,
                    check.component_name,
                    check.component_type,
                    check.message,
                    check.details
                )
        
        # Check for resolved issues
        await self._check_resolved_issues(report)
    
    async def _create_alert(self, level: AlertLevel, component_name: str, 
                          component_type: ComponentType, message: str, 
                          details: Optional[Dict[str, Any]] = None) -> None:
        """Create a new health alert."""
        alert_id = f"{component_type.value}_{component_name}_{datetime.now().timestamp()}"
        
        alert = HealthAlert(
            level=level,
            component_name=component_name,
            component_type=component_type,
            message=message,
            timestamp=datetime.now(),
            details=details or {}
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Maintain history size
        if len(self.alert_history) > self.max_alert_history:
            self.alert_history.pop(0)
        
        # Log alert
        log_message = f"[{level.value.upper()}] {component_type.value}:{component_name} - {message}"
        if level == AlertLevel.CRITICAL:
            self.logger.critical(log_message)
        elif level == AlertLevel.ERROR:
            self.logger.error(log_message)
        elif level == AlertLevel.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Notify alert handlers
        await self._notify_alert_handlers(alert)
    
    async def _check_resolved_issues(self, report: SystemHealthReport) -> None:
        """Check if any active alerts have been resolved."""
        resolved_alerts = []
        
        for alert_id, alert in self.active_alerts.items():
            if alert.resolved:
                continue
            
            # Check if the component is now healthy
            component_healthy = True
            for check in report.checks:
                if (check.component_name == alert.component_name and 
                    check.component_type == alert.component_type):
                    if check.status == HealthStatus.UNHEALTHY:
                        component_healthy = False
                        break
            
            if component_healthy:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                resolved_alerts.append(alert_id)
                
                self.logger.info(f"✅ Alert resolved: {alert.component_type.value}:{alert.component_name}")
        
        # Remove resolved alerts from active alerts
        for alert_id in resolved_alerts:
            del self.active_alerts[alert_id]
    
    async def _process_alerts(self) -> None:
        """Process active alerts and take actions."""
        for alert_id, alert in list(self.active_alerts.items()):
            # Check for alert escalation
            if alert.level == AlertLevel.WARNING:
                # Escalate warnings after 30 minutes
                if (datetime.now() - alert.timestamp).total_seconds() > 1800:
                    await self._escalate_alert(alert)
            
            elif alert.level == AlertLevel.ERROR:
                # Escalate errors after 10 minutes
                if (datetime.now() - alert.timestamp).total_seconds() > 600:
                    await self._escalate_alert(alert)
            
            elif alert.level == AlertLevel.CRITICAL:
                # Escalate critical alerts after 5 minutes
                if (datetime.now() - alert.timestamp).total_seconds() > 300:
                    await self._escalate_alert(alert)
    
    async def _escalate_alert(self, alert: HealthAlert) -> None:
        """Escalate an alert to a higher level."""
        if alert.level == AlertLevel.WARNING:
            new_level = AlertLevel.ERROR
        elif alert.level == AlertLevel.ERROR:
            new_level = AlertLevel.CRITICAL
        else:
            return  # Already at highest level
        
        # Create escalated alert
        await self._create_alert(
            new_level,
            alert.component_name,
            alert.component_type,
            f"ESCALATED: {alert.message}",
            {**alert.details, "escalated_from": alert.level.value}
        )
    
    async def _notify_alert_handlers(self, alert: HealthAlert) -> None:
        """Notify all registered alert handlers."""
        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")
    
    def _update_performance_metrics(self, start_time: datetime) -> None:
        """Update performance metrics."""
        duration = (datetime.now() - start_time).total_seconds()
        
        # Update check duration
        self.performance_metrics["check_durations"].append(duration)
        if len(self.performance_metrics["check_durations"]) > 100:
            self.performance_metrics["check_durations"].pop(0)
        
        # Update alert count
        self.performance_metrics["alert_counts"].append(len(self.active_alerts))
        if len(self.performance_metrics["alert_counts"]) > 100:
            self.performance_metrics["alert_counts"].pop(0)
    
    # Public API Methods
    def add_alert_handler(self, handler: Callable[[HealthAlert], None]) -> None:
        """Add an alert handler function."""
        self._alert_handlers.append(handler)
        self.logger.info(f"Alert handler added: {handler.__name__}")
    
    def remove_alert_handler(self, handler: Callable[[HealthAlert], None]) -> None:
        """Remove an alert handler function."""
        if handler in self._alert_handlers:
            self._alert_handlers.remove(handler)
            self.logger.info(f"Alert handler removed: {handler.__name__}")
    
    async def get_active_alerts(self) -> List[HealthAlert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, hours: int = 24) -> List[HealthAlert]:
        """Get alert history for the specified number of hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        check_durations = self.performance_metrics["check_durations"]
        alert_counts = self.performance_metrics["alert_counts"]
        
        return {
            "avg_check_duration_ms": sum(check_durations) / len(check_durations) * 1000 if check_durations else 0,
            "max_check_duration_ms": max(check_durations) * 1000 if check_durations else 0,
            "avg_active_alerts": sum(alert_counts) / len(alert_counts) if alert_counts else 0,
            "max_active_alerts": max(alert_counts) if alert_counts else 0,
            "total_alerts_generated": len(self.alert_history),
            "active_alerts_count": len(self.active_alerts),
            "monitoring_uptime_seconds": (datetime.now() - self.start_time).total_seconds() if hasattr(self, 'start_time') else 0
        }
    
    def set_check_interval(self, interval_seconds: int) -> None:
        """Set the health check interval."""
        self.check_interval = interval_seconds
        self.health_check_service.set_check_interval(interval_seconds)
        self.logger.info(f"Health check interval set to {interval_seconds} seconds")
    
    async def force_health_check(self) -> SystemHealthReport:
        """Force an immediate health check."""
        return await self.health_check_service.perform_comprehensive_health_check()
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is currently running."""
        return self._running
    
    async def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the monitoring status."""
        active_alerts = await self.get_active_alerts()
        performance_metrics = await self.get_performance_metrics()
        
        return {
            "monitoring_active": self._running,
            "team_id": self.team_id,
            "check_interval_seconds": self.check_interval,
            "active_alerts_count": len(active_alerts),
            "alert_summary": {
                "critical": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                "error": len([a for a in active_alerts if a.level == AlertLevel.ERROR]),
                "warning": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
                "info": len([a for a in active_alerts if a.level == AlertLevel.INFO])
            },
            "performance_metrics": performance_metrics,
            "last_check_time": self.health_check_service.last_check_time.isoformat() if self.health_check_service.last_check_time else None
        }


# Global background health monitor instances
_background_health_monitor_instances: Dict[str, BackgroundHealthMonitor] = {}


def get_background_health_monitor(team_id: str) -> BackgroundHealthMonitor:
    """Get background health monitor instance for the specified team."""
    global _background_health_monitor_instances
    
    if team_id not in _background_health_monitor_instances:
        _background_health_monitor_instances[team_id] = BackgroundHealthMonitor(team_id)
    
    return _background_health_monitor_instances[team_id]


def initialize_background_health_monitor(team_id: str, check_interval: int = 300) -> BackgroundHealthMonitor:
    """Initialize background health monitor for the specified team."""
    global _background_health_monitor_instances
    
    monitor = BackgroundHealthMonitor(team_id, check_interval)
    _background_health_monitor_instances[team_id] = monitor
    
    return monitor 