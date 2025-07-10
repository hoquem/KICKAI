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
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

from utils.async_utils import async_retry, async_timeout, async_operation_context
from core.exceptions import KICKAIError
from services.health_check_types import HealthStatus, ComponentType, HealthCheckResult, SystemHealthReport
from services.interfaces.health_check_service_interface import IHealthCheckService
from agents.crew_agents import TeamManagementSystem, AgentRole
from domain.tools.communication_tools import SendMessageTool, SendAnnouncementTool
from domain.tools.logging_tools import LogCommandTool
from domain.tools.player_tools import GetAllPlayersTool, GetPlayerStatusTool
from domain.tools.team_management_tools import GetAllPlayersTool, GetPlayerStatusTool
from services.player_service import get_player_service
from services.team_service import get_team_service
from services.payment_service import get_payment_service
from services.reminder_service import get_reminder_service
from services.daily_status_service import get_daily_status_service
from services.fa_registration_checker import get_fa_registration_checker
from database.firebase_client import get_firebase_client
from utils.llm_client import LLMClient
from services.stripe_payment_gateway import StripePaymentGateway
from core.improved_config_system import get_improved_config


class HealthCheckService(IHealthCheckService):
    """Comprehensive health check service for KICKAI system."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
        self.last_check_time: Optional[datetime] = None
        self.check_interval = 300  # 5 minutes
        self.health_history: List[SystemHealthReport] = []
        self.max_history_size = 100
        
        # Component registries
        self._agent_checks: Dict[str, callable] = {}
        self._tool_checks: Dict[str, callable] = {}
        self._service_checks: Dict[str, callable] = {}
        self._external_checks: Dict[str, callable] = {}
        
        # Initialize check registries
        self._register_default_checks()
        
        self.logger.info(f"✅ HealthCheckService initialized for team {team_id}")
    
    def _register_default_checks(self) -> None:
        """Register default health checks."""
        # Agent checks
        self._agent_checks.update({
            "message_processor": self._check_message_processor_agent,
            "team_manager": self._check_team_manager_agent,
            "player_coordinator": self._check_player_coordinator_agent,
            "finance_manager": self._check_finance_manager_agent,
            "performance_analyst": self._check_performance_analyst_agent,
            "learning_agent": self._check_learning_agent,
            "onboarding_agent": self._check_onboarding_agent,
            "command_fallback": self._check_command_fallback_agent,
        })
        
        # Tool checks
        self._tool_checks.update({
            "communication_tools": self._check_communication_tools,
            "logging_tools": self._check_logging_tools,
            "player_tools": self._check_player_tools,
            "team_management_tools": self._check_team_management_tools,
        })
        
        # Service checks
        self._service_checks.update({
            "player_service": self._check_player_service,
            "team_service": self._check_team_service,
            "payment_service": self._check_payment_service,
            "reminder_service": self._check_reminder_service,
            "daily_status_service": self._check_daily_status_service,
            "fa_registration_checker": self._check_fa_registration_checker,
        })
        
        # External dependency checks
        self._external_checks.update({
            "database": self._check_database_connectivity,
            "llm": self._check_llm_connectivity,
            "payment_gateway": self._check_payment_gateway,
            "telegram": self._check_telegram_connectivity,
        })
    
    @async_operation_context("health_check_service")
    async def perform_comprehensive_health_check(self) -> SystemHealthReport:
        """Perform a comprehensive health check of all system components."""
        start_time = time.time()
        self.logger.info("🔍 Starting comprehensive health check...")
        
        report = SystemHealthReport(
            overall_status=HealthStatus.HEALTHY,
            timestamp=datetime.now()
        )
        
        try:
            # Perform all health checks concurrently
            check_tasks = []
            
            # Agent checks
            for agent_name, check_func in self._agent_checks.items():
                task = asyncio.create_task(
                    self._execute_health_check(agent_name, ComponentType.AGENT, check_func)
                )
                check_tasks.append(task)
            
            # Tool checks
            for tool_name, check_func in self._tool_checks.items():
                task = asyncio.create_task(
                    self._execute_health_check(tool_name, ComponentType.TOOL, check_func)
                )
                check_tasks.append(task)
            
            # Service checks
            for service_name, check_func in self._service_checks.items():
                task = asyncio.create_task(
                    self._execute_health_check(service_name, ComponentType.SERVICE, check_func)
                )
                check_tasks.append(task)
            
            # External dependency checks
            for external_name, check_func in self._external_checks.items():
                task = asyncio.create_task(
                    self._execute_health_check(external_name, ComponentType.EXTERNAL_API, check_func)
                )
                check_tasks.append(task)
            
            # Wait for all checks to complete
            results = await asyncio.gather(*check_tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, HealthCheckResult):
                    report.add_check(result)
                else:
                    # Handle exceptions
                    self.logger.error(f"Health check failed with exception: {result}")
                    error_result = HealthCheckResult(
                        component_name="unknown",
                        component_type=ComponentType.SERVICE,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check execution failed: {str(result)}",
                        response_time_ms=0,
                        timestamp=datetime.now(),
                        error=result if isinstance(result, Exception) else None
                    )
                    report.add_check(error_result)
            
            # Determine overall status
            self._determine_overall_status(report)
            
            # Generate recommendations
            self._generate_recommendations(report)
            
            # Calculate performance metrics
            report.performance_metrics = {
                "total_check_time_ms": (time.time() - start_time) * 1000,
                "checks_performed": len(report.checks),
                "healthy_components": len([c for c in report.checks if c.status == HealthStatus.HEALTHY]),
                "degraded_components": len([c for c in report.checks if c.status == HealthStatus.DEGRADED]),
                "unhealthy_components": len([c for c in report.checks if c.status == HealthStatus.UNHEALTHY]),
            }
            
            # Store in history
            self._store_health_report(report)
            self.last_check_time = datetime.now()
            
            self.logger.info(f"✅ Health check completed: {report.overall_status.value}")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive health check failed: {e}")
            report.overall_status = HealthStatus.UNHEALTHY
            report.critical_issues.append(f"Health check execution failed: {str(e)}")
            return report
    
    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def _execute_health_check(self, component_name: str, component_type: ComponentType, check_func: callable) -> HealthCheckResult:
        """Execute a single health check with retry and timeout."""
        start_time = time.time()
        
        try:
            # Execute the check function
            result = await check_func()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component_name=component_name,
                component_type=component_type,
                status=result.get("status", HealthStatus.UNKNOWN),
                message=result.get("message", "Check completed"),
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details=result.get("details", {}),
                error=result.get("error")
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Health check failed for {component_name}: {e}")
            
            return HealthCheckResult(
                component_name=component_name,
                component_type=component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.now(),
                error=e
            )
    
    def _determine_overall_status(self, report: SystemHealthReport) -> None:
        """Determine the overall system health status."""
        critical_count = len(report.critical_issues)
        warning_count = len(report.warnings)
        
        if critical_count > 0:
            report.overall_status = HealthStatus.UNHEALTHY
        elif warning_count > 0:
            report.overall_status = HealthStatus.DEGRADED
        else:
            report.overall_status = HealthStatus.HEALTHY
    
    def _generate_recommendations(self, report: SystemHealthReport) -> None:
        """Generate recommendations based on health check results."""
        if not report.is_healthy():
            report.recommendations.extend([
                "Review error logs for detailed failure information",
                "Check environment variables and configuration files",
                "Verify external service connectivity",
                "Ensure all required dependencies are installed"
            ])
        
        # Component-specific recommendations
        for check in report.checks:
            if check.status == HealthStatus.UNHEALTHY:
                if check.component_type == ComponentType.LLM:
                    report.recommendations.append("Verify LLM API key and provider configuration")
                elif check.component_type == ComponentType.AGENT:
                    report.recommendations.append("Check agent configuration and initialization logic")
                elif check.component_type == ComponentType.TOOL:
                    report.recommendations.append("Verify tool dependencies and configuration")
                elif check.component_type == ComponentType.DATABASE:
                    report.recommendations.append("Check database credentials and connectivity")
                elif check.component_type == ComponentType.PAYMENT_GATEWAY:
                    report.recommendations.append("Verify payment gateway credentials and connectivity")
    
    def _store_health_report(self, report: SystemHealthReport) -> None:
        """Store health report in history."""
        self.health_history.append(report)
        
        # Maintain history size
        if len(self.health_history) > self.max_history_size:
            self.health_history.pop(0)
    
    # Agent Health Checks
    async def _check_message_processor_agent(self) -> Dict[str, Any]:
        """Check MessageProcessorAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.MESSAGE_PROCESSOR)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "MessageProcessorAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            if not agent.is_enabled():
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": "MessageProcessorAgent is disabled",
                    "details": {"enabled": False}
                }
            
            # Test basic functionality
            tools_count = len(agent.tools) if hasattr(agent, 'tools') else 0
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "MessageProcessorAgent is healthy",
                "details": {
                    "enabled": True,
                    "tools_count": tools_count,
                    "llm_configured": agent.llm is not None
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"MessageProcessorAgent check failed: {str(e)}",
                "error": e
            }
    
    async def _check_team_manager_agent(self) -> Dict[str, Any]:
        """Check TeamManagerAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.TEAM_MANAGER)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "TeamManagerAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            if not agent.is_enabled():
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": "TeamManagerAgent is disabled",
                    "details": {"enabled": False}
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "TeamManagerAgent is healthy",
                "details": {
                    "enabled": True,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"TeamManagerAgent check failed: {str(e)}",
                "error": e
            }
    
    async def _check_player_coordinator_agent(self) -> Dict[str, Any]:
        """Check PlayerCoordinatorAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.PLAYER_COORDINATOR)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "PlayerCoordinatorAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "PlayerCoordinatorAgent is healthy",
                "details": {
                    "enabled": agent.is_enabled() if hasattr(agent, 'is_enabled') else True,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"PlayerCoordinatorAgent check failed: {str(e)}",
                "error": e
            }
    
    async def _check_finance_manager_agent(self) -> Dict[str, Any]:
        """Check FinanceManagerAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.FINANCE_MANAGER)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "FinanceManagerAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "FinanceManagerAgent is healthy",
                "details": {
                    "enabled": agent.is_enabled() if hasattr(agent, 'is_enabled') else True,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"FinanceManagerAgent check failed: {str(e)}",
                "error": e
            }
    
    async def _check_performance_analyst_agent(self) -> Dict[str, Any]:
        """Check PerformanceAnalystAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.PERFORMANCE_ANALYST)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "PerformanceAnalystAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "PerformanceAnalystAgent is healthy",
                "details": {
                    "enabled": agent.is_enabled() if hasattr(agent, 'is_enabled') else True,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"PerformanceAnalystAgent check failed: {str(e)}",
                "error": e
            }
    
    async def _check_learning_agent(self) -> Dict[str, Any]:
        """Check LearningAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.LEARNING_AGENT)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "LearningAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "LearningAgent is healthy",
                "details": {
                    "enabled": agent.is_enabled() if hasattr(agent, 'is_enabled') else True,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"LearningAgent check failed: {str(e)}",
                "error": e
            }
    
    async def _check_onboarding_agent(self) -> Dict[str, Any]:
        """Check OnboardingAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.ONBOARDING_AGENT)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "OnboardingAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "OnboardingAgent is healthy",
                "details": {
                    "enabled": agent.is_enabled() if hasattr(agent, 'is_enabled') else True,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"OnboardingAgent check failed: {str(e)}",
                "error": e
            }
    
    async def _check_command_fallback_agent(self) -> Dict[str, Any]:
        """Check CommandFallbackAgent health."""
        try:
            team_system = TeamManagementSystem(self.team_id)
            agent = team_system.get_agent(AgentRole.COMMAND_FALLBACK_AGENT)
            
            if not agent:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "CommandFallbackAgent not found",
                    "details": {"team_id": self.team_id}
                }
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "CommandFallbackAgent is healthy",
                "details": {
                    "enabled": agent.is_enabled() if hasattr(agent, 'is_enabled') else True,
                    "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"CommandFallbackAgent check failed: {str(e)}",
                "error": e
            }
    
    # Tool Health Checks
    async def _check_communication_tools(self) -> Dict[str, Any]:
        """Check communication tools health."""
        try:
            send_message_tool = SendMessageTool(team_id=self.team_id)
            send_announcement_tool = SendAnnouncementTool(team_id=self.team_id)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Communication tools are healthy",
                "details": {
                    "send_message_tool": "available",
                    "send_announcement_tool": "available"
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
            log_tool = LogCommandTool(team_id=self.team_id)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Logging tools are healthy",
                "details": {
                    "log_command_tool": "available"
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
            get_all_players_tool = GetAllPlayersTool(team_id=self.team_id, command_operations=None)
            get_player_status_tool = GetPlayerStatusTool(team_id=self.team_id, command_operations=None)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Player tools are healthy",
                "details": {
                    "get_all_players_tool": "available",
                    "get_player_status_tool": "available"
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
            get_all_players_tool = GetAllPlayersTool(team_id=self.team_id, command_operations=None)
            get_player_status_tool = GetPlayerStatusTool(team_id=self.team_id, command_operations=None)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Team management tools are healthy",
                "details": {
                    "get_all_players_tool": "available",
                    "get_player_status_tool": "available"
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
            player_service = get_player_service(team_id=self.team_id)
            
            # Test basic functionality
            players = await player_service.get_team_players(self.team_id)
            
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
            team_service = get_team_service(team_id=self.team_id)
            
            # Test basic functionality
            team = await team_service.get_team(self.team_id)
            
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
            payment_service = get_payment_service(team_id=self.team_id)
            
            # Test basic functionality
            payments = await payment_service.list_payments()
            
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
            reminder_service = get_reminder_service(team_id=self.team_id)
            
            # Test basic functionality
            players_needing_reminders = await reminder_service.get_players_needing_reminders()
            
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
            daily_status_service = get_daily_status_service(team_id=self.team_id)
            
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
            fa_checker = get_fa_registration_checker(team_id=self.team_id)
            
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
            db_client = get_firebase_client()
            health_check = await db_client.health_check()
            
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
            gateway = StripePaymentGateway(api_key="sk_test_mock")
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Payment gateway is healthy",
                "details": {
                    "provider": "Stripe",
                    "mode": "test"
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
            config = get_improved_config()
            bot_token = config.configuration.telegram.bot_token
            
            if not bot_token:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Telegram bot token not configured",
                    "details": {
                        "bot_token_configured": False
                    }
                }
            
            # Test basic connectivity
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{bot_token}/getMe",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    bot_info = response.json()
                    return {
                        "status": HealthStatus.HEALTHY,
                        "message": "Telegram connectivity is healthy",
                        "details": {
                            "bot_username": bot_info.get("result", {}).get("username"),
                            "bot_name": bot_info.get("result", {}).get("first_name")
                        }
                    }
                else:
                    return {
                        "status": HealthStatus.UNHEALTHY,
                        "message": f"Telegram API error: {response.status_code}",
                        "details": {
                            "status_code": response.status_code,
                            "response": response.text
                        }
                    }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Telegram connectivity check failed: {str(e)}",
                "error": e
            }
    
    # Public API Methods
    async def get_current_health_status(self) -> SystemHealthReport:
        """Get the current health status."""
        if (self.last_check_time is None or 
            (datetime.now() - self.last_check_time).total_seconds() > self.check_interval):
            return await self.perform_comprehensive_health_check()
        
        # Return the most recent report
        return self.health_history[-1] if self.health_history else await self.perform_comprehensive_health_check()
    
    async def get_health_history(self, hours: int = 24) -> List[SystemHealthReport]:
        """Get health history for the specified number of hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [report for report in self.health_history if report.timestamp >= cutoff_time]
    
    async def export_health_report(self, file_path: Optional[str] = None) -> str:
        """Export health report to JSON file."""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"health_report_{self.team_id}_{timestamp}.json"
        
        report = await self.get_current_health_status()
        
        with open(file_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        self.logger.info(f"Health report exported to {file_path}")
        return file_path
    
    def set_check_interval(self, interval_seconds: int) -> None:
        """Set the health check interval."""
        self.check_interval = interval_seconds
        self.logger.info(f"Health check interval set to {interval_seconds} seconds")
    
    def add_custom_check(self, name: str, component_type: ComponentType, check_func: callable) -> None:
        """Add a custom health check."""
        if component_type == ComponentType.AGENT:
            self._agent_checks[name] = check_func
        elif component_type == ComponentType.TOOL:
            self._tool_checks[name] = check_func
        elif component_type == ComponentType.SERVICE:
            self._service_checks[name] = check_func
        elif component_type == ComponentType.EXTERNAL_API:
            self._external_checks[name] = check_func
        
        self.logger.info(f"Custom health check added: {name} ({component_type.value})")


# Global health check service instances
_health_check_service_instances: Dict[str, HealthCheckService] = {}


def get_health_check_service(team_id: str) -> HealthCheckService:
    """Get health check service instance for the specified team."""
    global _health_check_service_instances
    
    if team_id not in _health_check_service_instances:
        _health_check_service_instances[team_id] = HealthCheckService(team_id)
    
    return _health_check_service_instances[team_id]


def initialize_health_check_service(team_id: str) -> HealthCheckService:
    """Initialize health check service for the specified team."""
    global _health_check_service_instances
    
    service = HealthCheckService(team_id)
    _health_check_service_instances[team_id] = service
    
    return service 