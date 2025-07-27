import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# These should be updated to the correct feature-based paths
# from kickai.features.health_monitoring.domain.entities.health_check_types import SystemHealthReport, HealthStatus, ComponentType
# from kickai.features.health_monitoring.domain.services.health_check_service import HealthCheckService
from kickai.utils.async_utils import async_operation_context


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    level: AlertLevel
    component_name: str
    component_type: str  # Use str for now; update to ComponentType if available
    message: str
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: datetime | None = None


class BackgroundHealthMonitor:
    def __init__(self, team_id: str, check_interval: int = 300):
        self.team_id = team_id
        self.check_interval = check_interval
        self.logger = logging.getLogger(__name__)
        # self.health_check_service = HealthCheckService(team_id)
        self._monitoring_task: asyncio.Union[Task, None] = None
        self._running = False
        self._shutdown_event = asyncio.Event()
        self.active_alerts: dict[str, HealthAlert] = {}
        self.alert_history: list[HealthAlert] = []
        self.max_alert_history = 1000
        self._alert_handlers: list[Callable[[HealthAlert], None]] = []
        self.performance_metrics: dict[str, list[float]] = {
            "response_times": [],
            "check_durations": [],
            "alert_counts": [],
        }
        self.logger.info(f"✅ BackgroundHealthMonitor initialized for team {team_id}")

    async def start_monitoring(self) -> None:
        if self._running:
            self.logger.warning("Health monitoring is already running")
            return
        self._running = True
        self._shutdown_event.clear()
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info(f"🚀 Background health monitoring started for team {self.team_id}")

    async def stop_monitoring(self) -> None:
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
        self.logger.info("🔄 Starting health monitoring loop")
        try:
            while self._running and not self._shutdown_event.is_set():
                start_time = datetime.now()
                try:
                    # report = await self.health_check_service.perform_comprehensive_health_check()
                    # await self._process_health_report(report)
                    pass  # Placeholder for health check logic
                    await asyncio.sleep(0.1)  # Simulate work
                    await self._process_alerts()
                    self._update_performance_metrics(start_time)
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    await self._create_alert(
                        AlertLevel.ERROR,
                        "background_monitor",
                        "SERVICE",
                        f"Monitoring loop error: {e!s}",
                    )
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=self.check_interval)
                except TimeoutError:
                    pass
        except asyncio.CancelledError:
            self.logger.info("Health monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Fatal error in monitoring loop: {e}")
        finally:
            self.logger.info("Health monitoring loop ended")

    async def _process_alerts(self) -> None:
        # Placeholder for alert processing logic
        pass

    def _update_performance_metrics(self, start_time: datetime) -> None:
        duration = (datetime.now() - start_time).total_seconds()
        self.performance_metrics["check_durations"].append(duration)
        self.performance_metrics["alert_counts"].append(len(self.active_alerts))

    async def _create_alert(
        self,
        level: AlertLevel,
        component_name: str,
        component_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        alert_id = f"{component_type}_{component_name}_{datetime.now().timestamp()}"
        alert = HealthAlert(
            level=level,
            component_name=component_name,
            component_type=component_type,
            message=message,
            timestamp=datetime.now(),
            details=details or {},
        )
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_alert_history:
            self.alert_history.pop(0)
        log_message = f"[{level.value.upper()}] {component_type}:{component_name} - {message}"
        if level == AlertLevel.CRITICAL:
            self.logger.critical(log_message)
        elif level == AlertLevel.ERROR:
            self.logger.error(log_message)
        elif level == AlertLevel.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        await self._notify_alert_handlers(alert)

    async def _notify_alert_handlers(self, alert: HealthAlert) -> None:
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")

    def add_alert_handler(self, handler: Callable[[HealthAlert], None]) -> None:
        self._alert_handlers.append(handler)

    def remove_alert_handler(self, handler: Callable[[HealthAlert], None]) -> None:
        self._alert_handlers.remove(handler)

    async def get_active_alerts(self) -> list[HealthAlert]:
        return list(self.active_alerts.values())

    async def get_alert_history(self, hours: int = 24) -> list[HealthAlert]:
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff]

    async def get_performance_metrics(self) -> dict[str, Any]:
        return self.performance_metrics

    def set_check_interval(self, interval_seconds: int) -> None:
        self.check_interval = interval_seconds

    def is_monitoring(self) -> bool:
        return self._running

    async def get_status_summary(self) -> dict[str, Any]:
        return {
            "active_alerts": len(self.active_alerts),
            "alert_history": len(self.alert_history),
            "performance_metrics": self.performance_metrics,
            "is_monitoring": self._running,
        }
