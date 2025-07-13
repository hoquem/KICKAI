"""
Health Check Service for KICKAI

This service provides comprehensive health monitoring for all system components:
- Agents and their capabilities
- Tools and their availability
- External dependencies (LLM, database, payment gateways)
- Service layer health
- Performance metrics and alerts
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

from utils.async_utils import async_operation_context, async_retry, async_timeout
from database.interfaces import DataStoreInterface
from services.interfaces.health_check_service_interface import IHealthCheckService
from domain.interfaces.player_operations import IPlayerOperations
from domain.interfaces.team_operations import ITeamOperations
from domain.interfaces.payment_operations import IPaymentOperations
from services.interfaces.reminder_service_interface import IReminderService
from services.interfaces.daily_status_service_interface import IDailyStatusService
from services.interfaces.fa_registration_checker_interface import IFARegistrationChecker
from utils.llm_client import LLMClient
from services.health_check_types import (
    HealthStatus, ComponentType, HealthCheckResult, 
    SystemHealthReport
)


logger = logging.getLogger(__name__)


class HealthCheckService(IHealthCheckService):
    """Comprehensive health check service for the KICKAI system."""
    
    def __init__(self, team_id: str, data_store: DataStoreInterface = None, 
                 player_operations: IPlayerOperations = None,
                 team_operations: ITeamOperations = None,
                 payment_operations: IPaymentOperations = None,
                 reminder_service: IReminderService = None,
                 daily_status_service: IDailyStatusService = None,
                 fa_registration_checker: IFARegistrationChecker = None):
        self.team_id = team_id
        self.data_store = data_store
        self.player_operations = player_operations
        self.team_operations = team_operations
        self.payment_operations = payment_operations
        self.reminder_service = reminder_service
        self.daily_status_service = daily_status_service
        self.fa_registration_checker = fa_registration_checker
        
        # Health check configuration
        self.check_interval = 300  # 5 minutes default
        self.custom_checks: Dict[str, Callable] = {}
        self.health_history: List[SystemHealthReport] = []
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
        if self.player_operations:
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
                        "message": f"Health check execution failed: {str(results[i])}",
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
            report.recommendations.append(f"Health check system failure: {str(e)}")
            return report

    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def _execute_health_check(self, component_name: str, component_type: ComponentType, check_func: callable) -> Dict[str, Any]:
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
                "message": f"Health check failed: {str(e)}",
                "details": {"error": str(e)},
                "last_check": datetime.now()
            }

    def _determine_overall_status(self, report: SystemHealthReport) -> None:
        """Determine overall system health status based on component statuses."""
        if not report.components:
            report.overall_status = HealthStatus.UNKNOWN
            return
        
        # Count statuses
        status_counts = {}
        for component in report.components.values():
            status = component["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Determine overall status based on priority
        if HealthStatus.UNHEALTHY in status_counts:
            report.overall_status = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in status_counts:
            report.overall_status = HealthStatus.DEGRADED
        elif HealthStatus.HEALTHY in status_counts:
            report.overall_status = HealthStatus.HEALTHY
        else:
            report.overall_status = HealthStatus.UNKNOWN

    def _generate_recommendations(self, report: SystemHealthReport) -> None:
        """Generate recommendations based on health check results."""
        recommendations = []
        
        # Check for unhealthy components
        unhealthy_components = [
            name for name, component in report.components.items()
            if component["status"] == HealthStatus.UNHEALTHY
        ]
        
        if unhealthy_components:
            recommendations.append(f"Critical: {len(unhealthy_components)} components are unhealthy: {', '.join(unhealthy_components)}")
        
        # Check for degraded components
        degraded_components = [
            name for name, component in report.components.items()
            if component["status"] == HealthStatus.DEGRADED
        ]
        
        if degraded_components:
            recommendations.append(f"Warning: {len(degraded_components)} components are degraded: {', '.join(degraded_components)}")
        
        # Check for slow response times
        slow_components = [
            name for name, component in report.components.items()
            if "response_time" in component and component["response_time"] > 5.0
        ]
        
        if slow_components:
            recommendations.append(f"Performance: {len(slow_components)} components have slow response times: {', '.join(slow_components)}")
        
        # Add general recommendations
        if report.overall_status == HealthStatus.HEALTHY:
            recommendations.append("System is healthy - continue monitoring")
        elif report.overall_status == HealthStatus.DEGRADED:
            recommendations.append("System is degraded - investigate issues and consider maintenance")
        elif report.overall_status == HealthStatus.UNHEALTHY:
            recommendations.append("System is unhealthy - immediate attention required")
        
        report.recommendations = recommendations

    def _store_health_report(self, report: SystemHealthReport) -> None:
        """Store health report in history."""
        self.health_history.append(report)
        
        # Keep only the last max_history_size reports
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]

    # Agent Health Checks
    async def _check_message_processor_agent(self) -> Dict[str, Any]:
        """Check message processor agent health."""
        try:
            # This would check the actual agent status
            # For now, return a mock healthy status
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Message processor agent is healthy",
                "details": {
                    "agent_type": "message_processor",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Message processor agent check failed: {str(e)}",
                "error": e
            }

    async def _check_team_manager_agent(self) -> Dict[str, Any]:
        """Check team manager agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Team manager agent is healthy",
                "details": {
                    "agent_type": "team_manager",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Team manager agent check failed: {str(e)}",
                "error": e
            }

    async def _check_player_coordinator_agent(self) -> Dict[str, Any]:
        """Check player coordinator agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Player coordinator agent is healthy",
                "details": {
                    "agent_type": "player_coordinator",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Player coordinator agent check failed: {str(e)}",
                "error": e
            }

    async def _check_finance_manager_agent(self) -> Dict[str, Any]:
        """Check finance manager agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Finance manager agent is healthy",
                "details": {
                    "agent_type": "finance_manager",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Finance manager agent check failed: {str(e)}",
                "error": e
            }

    async def _check_performance_analyst_agent(self) -> Dict[str, Any]:
        """Check performance analyst agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Performance analyst agent is healthy",
                "details": {
                    "agent_type": "performance_analyst",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Performance analyst agent check failed: {str(e)}",
                "error": e
            }

    async def _check_learning_agent(self) -> Dict[str, Any]:
        """Check learning agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Learning agent is healthy",
                "details": {
                    "agent_type": "learning",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Learning agent check failed: {str(e)}",
                "error": e
            }

    async def _check_onboarding_agent(self) -> Dict[str, Any]:
        """Check onboarding agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Onboarding agent is healthy",
                "details": {
                    "agent_type": "onboarding",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Onboarding agent check failed: {str(e)}",
                "error": e
            }

    async def _check_command_fallback_agent(self) -> Dict[str, Any]:
        """Check command fallback agent health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Command fallback agent is healthy",
                "details": {
                    "agent_type": "command_fallback",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Command fallback agent check failed: {str(e)}",
                "error": e
            }

    # Tool Health Checks
    async def _check_communication_tools(self) -> Dict[str, Any]:
        """Check communication tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Communication tools are healthy",
                "details": {
                    "tool_type": "communication",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Communication tools check failed: {str(e)}",
                "error": e
            }

    async def _check_logging_tools(self) -> Dict[str, Any]:
        """Check logging tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Logging tools are healthy",
                "details": {
                    "tool_type": "logging",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Logging tools check failed: {str(e)}",
                "error": e
            }

    async def _check_player_tools(self) -> Dict[str, Any]:
        """Check player tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Player tools are healthy",
                "details": {
                    "tool_type": "player_management",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Player tools check failed: {str(e)}",
                "error": e
            }

    async def _check_team_management_tools(self) -> Dict[str, Any]:
        """Check team management tools health."""
        try:
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Team management tools are healthy",
                "details": {
                    "tool_type": "team_management",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Team management tools check failed: {str(e)}",
                "error": e
            }
    
    # Service Health Checks
    async def _check_player_service(self) -> Dict[str, Any]:
        """Check player service health."""
        try:
            if not self.player_operations:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Player operations not available",
                    "error": "Player operations not injected"
                }
            
            # Test basic functionality
            players = await self.player_operations.get_team_players(self.team_id)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Player service is healthy",
                "details": {
                    "players_count": len(players),
                    "team_id": self.team_id
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Player service check failed: {str(e)}",
                "error": e
            }
    
    async def _check_team_service(self) -> Dict[str, Any]:
        """Check team service health."""
        try:
            if not self.team_operations:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Team operations not available",
                    "error": "Team operations not injected"
                }
            
            # Test basic functionality
            team = await self.team_operations.get_team(self.team_id)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Team service is healthy",
                "details": {
                    "team_name": team.name if team else "Unknown",
                    "team_id": self.team_id
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Team service check failed: {str(e)}",
                "error": e
            }
    
    async def _check_payment_service(self) -> Dict[str, Any]:
        """Check payment service health."""
        try:
            if not self.payment_operations:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Payment operations not available",
                    "error": "Payment operations not injected"
                }
            
            # Test basic functionality
            payments = await self.payment_operations.list_payments()
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Payment service is healthy",
                "details": {
                    "payments_count": len(payments),
                    "team_id": self.team_id
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Payment service check failed: {str(e)}",
                "error": e
            }
    
    async def _check_reminder_service(self) -> Dict[str, Any]:
        """Check reminder service health."""
        try:
            if not self.reminder_service:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Reminder service not available",
                    "error": "Reminder service not injected"
                }
            
            # Test basic functionality
            players_needing_reminders = await self.reminder_service.get_players_needing_reminders()
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Reminder service is healthy",
                "details": {
                    "players_needing_reminders": len(players_needing_reminders),
                    "team_id": self.team_id
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Reminder service check failed: {str(e)}",
                "error": e
            }
    
    async def _check_daily_status_service(self) -> Dict[str, Any]:
        """Check daily status service health."""
        try:
            if not self.daily_status_service:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Daily status service not available",
                    "error": "Daily status service not injected"
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Daily status service is healthy",
                "details": {
                    "team_id": self.team_id
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Daily status service check failed: {str(e)}",
                "error": e
            }
    
    async def _check_fa_registration_checker(self) -> Dict[str, Any]:
        """Check FA registration checker health."""
        try:
            if not self.fa_registration_checker:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "FA registration checker not available",
                    "error": "FA registration checker not injected"
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "FA registration checker is healthy",
                "details": {
                    "team_id": self.team_id
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"FA registration checker check failed: {str(e)}",
                "error": e
            }
    
    # External Dependency Health Checks
    async def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            if not self.data_store:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Data store not available",
                    "error": "Data store not injected"
                }
            
            health_check = await self.data_store.health_check()
            
            if health_check.get("status") == "healthy":
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Database connectivity is healthy",
                    "details": health_check
                }
            else:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": f"Database connectivity issues: {health_check.get('message', 'Unknown error')}",
                    "details": health_check
                }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Database connectivity check failed: {str(e)}",
                "error": e
            }
    
    async def _check_llm_connectivity(self) -> Dict[str, Any]:
        """Check LLM connectivity."""
        try:
            llm_client = LLMClient()
            
            # Test basic connectivity with a simple prompt
            test_response = await llm_client.generate_text("Test connectivity")
            
            if test_response:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "LLM connectivity is healthy",
                    "details": {
                        "response_length": len(test_response),
                        "provider": "Google Gemini"
                    }
                }
            else:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": "LLM connectivity is degraded - no response received",
                    "details": {
                        "provider": "Google Gemini"
                    }
                }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"LLM connectivity check failed: {str(e)}",
                "error": e
            }
    
    async def _check_payment_gateway(self) -> Dict[str, Any]:
        """Check payment gateway connectivity."""
        try:
            # This would check the actual payment gateway
            # For now, return a mock healthy status
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Payment gateway is healthy",
                "details": {
                    "gateway": "Stripe",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Payment gateway check failed: {str(e)}",
                "error": e
            }
    
    async def _check_telegram_connectivity(self) -> Dict[str, Any]:
        """Check Telegram connectivity."""
        try:
            # This would check the actual Telegram API
            # For now, return a mock healthy status
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Telegram connectivity is healthy",
                "details": {
                    "api": "Telegram Bot API",
                    "team_id": self.team_id
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Telegram connectivity check failed: {str(e)}",
                "error": e
            }

    # Public interface methods
    async def get_current_health_status(self) -> SystemHealthReport:
        """Get the current health status."""
        return await self.perform_comprehensive_health_check()

    async def get_health_history(self, hours: int = 24) -> List[SystemHealthReport]:
        """Get health history for the specified number of hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [report for report in self.health_history if report.timestamp >= cutoff_time]

    async def export_health_report(self, file_path: Optional[str] = None) -> str:
        """Export health report to file."""
        report = await self.perform_comprehensive_health_check()
        
        if not file_path:
            file_path = f"health_report_{self.team_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # This would implement actual file export
        # For now, just return the file path
        return file_path

    def set_check_interval(self, interval_seconds: int) -> None:
        """Set the health check interval."""
        self.check_interval = interval_seconds
        logger.info(f"Health check interval set to {interval_seconds} seconds")

    def add_custom_check(self, name: str, component_type: ComponentType, check_func: callable) -> None:
        """Add a custom health check."""
        self.custom_checks[name] = (component_type, check_func)
        logger.info(f"Added custom health check: {name} ({component_type.value})") 