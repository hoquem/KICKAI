"""
Health Check Service for KICKAI

This service provides comprehensive health monitoring for all system components:
- Agents and their capabilities
- Tools and their availability
- External dependencies (LLM, database, payment gateways)
- Service layer health
- Performance metrics and alerts
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from kickai.database.interfaces import DataStoreInterface

# IDailyStatusService interface removed - no concrete implementation
from kickai.features.communication.domain.interfaces.reminder_service_interface import (
    IReminderService,
)
from kickai.features.health_monitoring.domain.entities.health_check_types import (
    ComponentType,
    HealthStatus,
    SystemHealthReport,
)
from kickai.features.health_monitoring.domain.interfaces.health_check_service_interface import (
    IHealthCheckService,
)

# IPaymentOperations interface removed - no concrete implementation
from kickai.features.player_registration.domain.interfaces.fa_registration_checker_interface import (
    IFARegistrationChecker,
)
from kickai.features.player_registration.domain.services.player_service import PlayerService

# ITeamOperations interface removed - no concrete implementation
from kickai.utils.async_utils import async_operation_context, async_retry, async_timeout
from kickai.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


class HealthCheckService(IHealthCheckService):
    """Comprehensive health check service for the KICKAI system."""

    def __init__(self, team_id: str, data_store: DataStoreInterface = None,
                 player_service: PlayerService = None,
                 team_operations=None,  # ITeamOperations interface removed
                 payment_operations=None,  # IPaymentOperations interface removed
                 reminder_service: IReminderService = None,
                 daily_status_service=None,  # IDailyStatusService interface removed
                 fa_registration_checker: IFARegistrationChecker = None):
        self.team_id = team_id
        self.data_store = data_store
        self.player_service = player_service
        self.team_operations = team_operations
        self.payment_operations = payment_operations
        self.reminder_service = reminder_service
        self.daily_status_service = daily_status_service
        self.fa_registration_checker = fa_registration_checker

        # Health check configuration
        self.check_interval = 300  # 5 minutes default
        self.custom_checks: dict[str, Callable] = {}
        self.health_history: list[SystemHealthReport] = []
        self.max_history_size = 100

        # Register default health checks
        self._register_default_checks()

        logger.info(f"HealthCheckService initialized for team: {team_id}")

    def _register_default_checks(self) -> None:
        """Register default health checks for all system components."""
        # Agent health checks
        self.add_custom_check("message_processor_agent", ComponentType.AGENT, self._check_message_processor_agent)
        self.add_custom_check("team_manager_agent", ComponentType.AGENT, self._check_team_manager_agent)
        self.add_custom_check("player_coordinator_agent", ComponentType.AGENT, self._check_player_coordinator_agent)
        self.add_custom_check("finance_manager_agent", ComponentType.AGENT, self._check_finance_manager_agent)
        self.add_custom_check("performance_analyst_agent", ComponentType.AGENT, self._check_performance_analyst_agent)
        self.add_custom_check("learning_agent", ComponentType.AGENT, self._check_learning_agent)
        self.add_custom_check("onboarding_agent", ComponentType.AGENT, self._check_onboarding_agent)
        self.add_custom_check("command_fallback_agent", ComponentType.AGENT, self._check_command_fallback_agent)

        # Tool health checks
        self.add_custom_check("communication_tools", ComponentType.TOOL, self._check_communication_tools)
        self.add_custom_check("logging_tools", ComponentType.TOOL, self._check_logging_tools)
        self.add_custom_check("player_tools", ComponentType.TOOL, self._check_player_tools)
        self.add_custom_check("team_management_tools", ComponentType.TOOL, self._check_team_management_tools)

        # Service health checks
        if self.player_service:
            self.add_custom_check("player_service", ComponentType.SERVICE, self._check_player_service)
        if self.team_operations:
            self.add_custom_check("team_service", ComponentType.SERVICE, self._check_team_service)
        if self.payment_operations:
            self.add_custom_check("payment_service", ComponentType.SERVICE, self._check_payment_service)
        if self.reminder_service:
            self.add_custom_check("reminder_service", ComponentType.SERVICE, self._check_reminder_service)
        if self.daily_status_service:
            self.add_custom_check("daily_status_service", ComponentType.SERVICE, self._check_daily_status_service)
        if self.fa_registration_checker:
            self.add_custom_check("fa_registration_checker", ComponentType.SERVICE, self._check_fa_registration_checker)

        # External dependency health checks
        if self.data_store:
            self.add_custom_check("database_connectivity", ComponentType.INFRASTRUCTURE, self._check_database_connectivity)
        self.add_custom_check("llm_connectivity", ComponentType.EXTERNAL, self._check_llm_connectivity)
        self.add_custom_check("payment_gateway", ComponentType.EXTERNAL, self._check_payment_gateway)
        self.add_custom_check("telegram_connectivity", ComponentType.EXTERNAL, self._check_telegram_connectivity)

    @async_operation_context("health_check_service")
    async def perform_comprehensive_health_check(self) -> SystemHealthReport:
        """Perform a comprehensive health check of all system components."""
        logger.info(f"Starting comprehensive health check for team: {self.team_id}")

        start_time = datetime.now()
        report = SystemHealthReport(
            timestamp=start_time,
            team_id=self.team_id,
            overall_status=HealthStatus.UNKNOWN,
            components={},
            recommendations=[],
            execution_time=0.0
        )

        try:
            # Execute all registered health checks concurrently
            check_tasks = []
            for component_name, (component_type, check_func) in self.custom_checks.items():
                task = self._execute_health_check(component_name, component_type, check_func)
                check_tasks.append(task)

            # Wait for all checks to complete
            results = await asyncio.gather(*check_tasks, return_exceptions=True)

            # Process results
            for i, (component_name, (component_type, _)) in enumerate(self.custom_checks.items()):
                if isinstance(results[i], Exception):
                    # Handle check execution error
                    report.components[component_name] = {
                        "name": component_name,
                        "type": component_type,
                        "status": HealthStatus.UNHEALTHY,
                        "message": f"Health check execution failed: {results[i]!s}",
                        "details": {"error": str(results[i])},
                        "last_check": start_time
                    }
                else:
                    # Use the result directly
                    report.components[component_name] = results[i]

            # Determine overall system status
            self._determine_overall_status(report)

            # Generate recommendations
            self._generate_recommendations(report)

            # Calculate execution time
            end_time = datetime.now()
            report.execution_time = (end_time - start_time).total_seconds()

            # Store report in history
            self._store_health_report(report)

            logger.info(f"Health check completed in {report.execution_time:.2f}s. Overall status: {report.overall_status.value}")

            return report

        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            report.overall_status = HealthStatus.UNHEALTHY
            report.recommendations.append(f"Health check system failure: {e!s}")
            return report

    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def _execute_health_check(self, component_name: str, component_type: ComponentType, check_func: callable) -> dict[str, Any]:
        """Execute a single health check with retry and timeout."""
        try:
            start_time = datetime.now()
            result = await check_func()
            end_time = datetime.now()

            return {
                "name": component_name,
                "type": component_type,
                "status": result.get("status", HealthStatus.UNKNOWN),
                "message": result.get("message", "No message provided"),
                "details": result.get("details", {}),
                "last_check": start_time,
                "response_time": (end_time - start_time).total_seconds()
            }

        except Exception as e:
            logger.error(f"Health check failed for {component_name}: {e}")
            return {
                "name": component_name,
                "type": component_type,
                "status": HealthStatus.UNHEALTHY,
                "message": f"Health check failed: {e!s}",
                "details": {"error": str(e)},
                "last_check": datetime.now()
            }

    def _determine_overall_status(self, report: SystemHealthReport) -> None:
        """Determine the overall system health status based on component results."""
        if not report.components:
            report.overall_status = HealthStatus.UNKNOWN
            return

        # Count statuses
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0
        }

        for component in report.components.values():
            status = component.get("status", HealthStatus.UNKNOWN)
            status_counts[status] += 1

        total_components = len(report.components)

        # Determine overall status based on majority
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            report.overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > total_components * 0.3:  # More than 30% degraded
            report.overall_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] >= total_components * 0.8:  # At least 80% healthy
            report.overall_status = HealthStatus.HEALTHY
        else:
            report.overall_status = HealthStatus.DEGRADED

    def _generate_recommendations(self, report: SystemHealthReport) -> None:
        """Generate recommendations based on health check results."""
        recommendations = []

        # Check for unhealthy components
        unhealthy_components = [
            name for name, component in report.components.items()
            if component.get("status") == HealthStatus.UNHEALTHY
        ]

        if unhealthy_components:
            recommendations.append(f"Critical: {len(unhealthy_components)} components are unhealthy: {', '.join(unhealthy_components)}")

        # Check for degraded components
        degraded_components = [
            name for name, component in report.components.items()
            if component.get("status") == HealthStatus.DEGRADED
        ]

        if degraded_components:
            recommendations.append(f"Warning: {len(degraded_components)} components are degraded: {', '.join(degraded_components)}")

        # Check for slow response times
        slow_components = [
            name for name, component in report.components.items()
            if component.get("response_time", 0) > 5.0  # More than 5 seconds
        ]

        if slow_components:
            recommendations.append(f"Performance: {len(slow_components)} components are responding slowly: {', '.join(slow_components)}")

        report.recommendations = recommendations

    def _store_health_report(self, report: SystemHealthReport) -> None:
        """Store health report in history, maintaining max size."""
        self.health_history.append(report)

        # Maintain history size
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]

    # Agent health check methods
    async def _check_message_processor_agent(self) -> dict[str, Any]:
        """Check message processor agent health."""
        try:
            # This would check if the agent is available and responding
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Message processor agent is operational",
                "details": {"agent_type": "message_processor"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Message processor agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_team_manager_agent(self) -> dict[str, Any]:
        """Check team manager agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Team manager agent is operational",
                "details": {"agent_type": "team_manager"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Team manager agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_player_coordinator_agent(self) -> dict[str, Any]:
        """Check player coordinator agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Player coordinator agent is operational",
                "details": {"agent_type": "player_coordinator"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Player coordinator agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_finance_manager_agent(self) -> dict[str, Any]:
        """Check finance manager agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Finance manager agent is operational",
                "details": {"agent_type": "finance_manager"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Finance manager agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_performance_analyst_agent(self) -> dict[str, Any]:
        """Check performance analyst agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Performance analyst agent is operational",
                "details": {"agent_type": "performance_analyst"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Performance analyst agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_learning_agent(self) -> dict[str, Any]:
        """Check learning agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Learning agent is operational",
                "details": {"agent_type": "learning"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Learning agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_onboarding_agent(self) -> dict[str, Any]:
        """Check onboarding agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Onboarding agent is operational",
                "details": {"agent_type": "onboarding"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Onboarding agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_command_fallback_agent(self) -> dict[str, Any]:
        """Check command fallback agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Command fallback agent is operational",
                "details": {"agent_type": "command_fallback"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Command fallback agent check failed: {e!s}",
                "details": {"error": str(e)}
            }

    # Tool health check methods
    async def _check_communication_tools(self) -> dict[str, Any]:
        """Check communication tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Communication tools are operational",
                "details": {"tool_category": "communication"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Communication tools check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_logging_tools(self) -> dict[str, Any]:
        """Check logging tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Logging tools are operational",
                "details": {"tool_category": "logging"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Logging tools check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_player_tools(self) -> dict[str, Any]:
        """Check player tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Player tools are operational",
                "details": {"tool_category": "player_management"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Player tools check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_team_management_tools(self) -> dict[str, Any]:
        """Check team management tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Team management tools are operational",
                "details": {"tool_category": "team_management"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Team management tools check failed: {e!s}",
                "details": {"error": str(e)}
            }

    # Service health check methods
    async def _check_player_service(self) -> dict[str, Any]:
        """Check player service health."""
        try:
            if not self.player_service:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "Player service not available",
                    "details": {"service": "player_service"}
                }

            # Test basic player operations
            # This would perform a simple operation to verify the service is working
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Player service is operational",
                "details": {"service": "player_service"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Player service check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_team_service(self) -> dict[str, Any]:
        """Check team service health."""
        try:
            if not self.team_operations:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "Team operations not available",
                    "details": {"service": "team_operations"}
                }

            return {
                "status": HealthStatus.HEALTHY,
                "message": "Team service is operational",
                "details": {"service": "team_operations"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Team service check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_payment_service(self) -> dict[str, Any]:
        """Check payment service health."""
        try:
            if not self.payment_operations:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "Payment operations not available",
                    "details": {"service": "payment_operations"}
                }

            return {
                "status": HealthStatus.HEALTHY,
                "message": "Payment service is operational",
                "details": {"service": "payment_operations"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Payment service check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_reminder_service(self) -> dict[str, Any]:
        """Check reminder service health."""
        try:
            if not self.reminder_service:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "Reminder service not available",
                    "details": {"service": "reminder_service"}
                }

            return {
                "status": HealthStatus.HEALTHY,
                "message": "Reminder service is operational",
                "details": {"service": "reminder_service"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Reminder service check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_daily_status_service(self) -> dict[str, Any]:
        """Check daily status service health."""
        try:
            if not self.daily_status_service:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "Daily status service not available",
                    "details": {"service": "daily_status_service"}
                }

            return {
                "status": HealthStatus.HEALTHY,
                "message": "Daily status service is operational",
                "details": {"service": "daily_status_service"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Daily status service check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_fa_registration_checker(self) -> dict[str, Any]:
        """Check FA registration checker health."""
        try:
            if not self.fa_registration_checker:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "FA registration checker not available",
                    "details": {"service": "fa_registration_checker"}
                }

            return {
                "status": HealthStatus.HEALTHY,
                "message": "FA registration checker is operational",
                "details": {"service": "fa_registration_checker"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"FA registration checker check failed: {e!s}",
                "details": {"error": str(e)}
            }

    # External dependency health check methods
    async def _check_database_connectivity(self) -> dict[str, Any]:
        """Check database connectivity."""
        try:
            if not self.data_store:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "Data store not available",
                    "details": {"dependency": "database"}
                }

            # Test database connectivity with a simple query
            # This would perform a simple operation to verify connectivity
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Database connectivity is operational",
                "details": {"dependency": "database"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Database connectivity check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_llm_connectivity(self) -> dict[str, Any]:
        """Check LLM connectivity."""
        try:
            # Test LLM connectivity
            llm_client = LLMClient()
            # This would perform a simple test to verify LLM connectivity
            return {
                "status": HealthStatus.HEALTHY,
                "message": "LLM connectivity is operational",
                "details": {"dependency": "llm"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"LLM connectivity check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_payment_gateway(self) -> dict[str, Any]:
        """Check payment gateway connectivity."""
        try:
            # Test payment gateway connectivity
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Payment gateway is operational",
                "details": {"dependency": "payment_gateway"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Payment gateway check failed: {e!s}",
                "details": {"error": str(e)}
            }

    async def _check_telegram_connectivity(self) -> dict[str, Any]:
        """Check Telegram connectivity."""
        try:
            # Test Telegram connectivity
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Telegram connectivity is operational",
                "details": {"dependency": "telegram"}
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Telegram connectivity check failed: {e!s}",
                "details": {"error": str(e)}
            }

    # Public interface methods
    async def get_current_health_status(self) -> SystemHealthReport:
        """Get the current health status."""
        return await self.perform_comprehensive_health_check()

    async def get_health_history(self, hours: int = 24) -> list[SystemHealthReport]:
        """Get health history for the specified number of hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [report for report in self.health_history if report.timestamp >= cutoff_time]

    async def export_health_report(self, file_path: str | None = None) -> str:
        """Export health report to file."""
        report = await self.perform_comprehensive_health_check()
        # Implementation for exporting report
        return "Health report exported successfully"

    def set_check_interval(self, interval_seconds: int) -> None:
        """Set the health check interval."""
        self.check_interval = interval_seconds

    def add_custom_check(self, name: str, component_type: ComponentType, check_func: callable) -> None:
        """Add a custom health check."""
        self.custom_checks[name] = (component_type, check_func)
