"""
Startup Validator

This module provides the main startup validator that orchestrates all health checks.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from loguru import logger

from .checks import (
    AgentInitializationCheck,
    CleanArchitectureCheck,
    CommandRegistryCheck,
    ConfigurationCheck,
    CrewAIAgentHealthCheck,
    EnhancedRegistryCheck,
    InitializationSequenceCheck,
    LLMProviderCheck,
    StubDetectionCheck,
    TelegramAdminCheck,
    ToolRegistrationCheck,
)
from .registry_validator import RegistryStartupValidator
from .reporting import CheckCategory, CheckResult, CheckStatus, ValidationReport


class StartupValidator:
    """
    Main startup validator that orchestrates all health checks.

    This class manages the execution of health checks and generates
    comprehensive validation reports with fail-fast enterprise patterns.
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the startup validator.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.checks: List[Any] = []
        self.start_time: float = 0.0
        self._load_default_checks()
        logger.info(f"StartupValidator initialized with {len(self.checks)} checks")

    def _load_default_checks(self) -> None:
        """Load default health checks following fail-fast enterprise patterns."""
        self.checks = [
            # Phase 1: Critical Prerequisites (fail-fast)
            InitializationSequenceCheck(),  # Comprehensive initialization validation
            ConfigurationCheck(),           # Basic configuration validation

            # Phase 2: Architecture Compliance
            CleanArchitectureCheck(),       # Clean Architecture compliance validation

            # Phase 3: Core Infrastructure
            LLMProviderCheck(),             # LLM connectivity and configuration
            StubDetectionCheck(),           # Check for placeholder implementations

            # Phase 4: Registry and Discovery
            EnhancedRegistryCheck(),        # Comprehensive registry validation
            ToolRegistrationCheck(),        # Tool discovery and registration
            CommandRegistryCheck(),         # Command registry initialization

            # Phase 5: Agent System Health
            CrewAIAgentHealthCheck(),       # CrewAI agent health and performance
            AgentInitializationCheck(),     # Agent creation and configuration

            # Phase 6: External Dependencies
            TelegramAdminCheck(),           # Telegram integration validation
        ]

        # Add registry validation (legacy support)
        self.registry_validator = RegistryStartupValidator()

    def add_check(self, check: Any) -> None:
        """
        Add a custom health check.
        
        Args:
            check: Health check instance to add
        """
        self.checks.append(check)
        logger.info(f"Added custom check: {check.name}")

    def remove_check(self, check_name: str) -> None:
        """
        Remove a health check by name.
        
        Args:
            check_name: Name of the check to remove
        """
        original_count = len(self.checks)
        self.checks = [check for check in self.checks if check.name != check_name]
        removed_count = original_count - len(self.checks)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} check(s) with name: {check_name}")
        else:
            logger.warning(f"No check found with name: {check_name}")

    async def _load_bot_configuration(self, context: Dict[str, Any]) -> None:
        """
        Load bot configuration from Firestore.
        
        Args:
            context: Context dictionary to update with bot configuration
        """
        try:
            from kickai.core.config import get_settings
            from kickai.database.firebase_client import FirebaseClient
            
            settings = get_settings()
            firebase_client = FirebaseClient(settings)
            
            # Get the first available team from Firestore
            team_id = await self._get_first_team_id(firebase_client)
            if not team_id:
                logger.warning("⚠️ No teams found in Firestore")
                context["bot_config"] = None
                return
            
            # Get the specific team configuration
            bot_config = await self._get_team_configuration(firebase_client, team_id)
            context["bot_config"] = bot_config
            
            if bot_config:
                logger.info("✅ Bot configuration loaded from Firestore")
            else:
                logger.warning(f"⚠️ No team configuration found for team_id: {team_id}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not load bot configuration from Firestore: {e}")
            context["bot_config"] = None

    async def _get_first_team_id(self, firebase_client: Any) -> Optional[str]:
        """
        Get the first available team ID from Firestore.
        
        Args:
            firebase_client: Firebase client instance
            
        Returns:
            Team ID if found, None otherwise
        """
        try:
            teams = await firebase_client.get_all_teams()
            if teams:
                team_id = teams[0].id if hasattr(teams[0], 'id') else teams[0].get('id')
                logger.info(f"✅ Found team_id from Firestore: {team_id}")
                return team_id
            else:
                logger.warning("⚠️ No teams found in Firestore")
                return None
        except Exception as e:
            logger.warning(f"⚠️ Could not get team_id from Firestore: {e}")
            return None

    async def _get_team_configuration(self, firebase_client: Any, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get team configuration from Firestore.
        
        Args:
            firebase_client: Firebase client instance
            team_id: Team ID to get configuration for
            
        Returns:
            Team configuration dictionary if found, None otherwise
        """
        try:
            team_doc = await firebase_client.get_document(
                collection_name="kickai_teams",
                document_id=team_id
            )
            
            if team_doc:
                return {
                    "bot_token": team_doc.get("bot_token"),
                    "main_chat_id": team_doc.get("main_chat_id"),
                    "leadership_chat_id": team_doc.get("leadership_chat_id"),
                }
            else:
                logger.warning(f"⚠️ No team configuration found for team_id: {team_id}")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting team configuration for {team_id}: {e}")
            return None

    async def validate(self, context: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """
        Execute all health checks and generate a validation report.

        Args:
            context: Optional context data for checks

        Returns:
            ValidationReport with all check results
        """
        self.start_time = time.time()
        
        if context is None:
            context = {}

        # Load bot configuration from Firestore
        await self._load_bot_configuration(context)

        logger.info(f"🔧 Starting validation with {len(self.checks)} checks")
        logger.info(f"🔧 Checks to run: {[check.name for check in self.checks]}")

        report = ValidationReport(overall_status=CheckStatus.PASSED)

        # Execute checks in parallel for better performance
        check_tasks = []
        for check in self.checks:
            task = asyncio.create_task(self._execute_check(check, context))
            check_tasks.append(task)

        # Wait for all checks to complete
        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle check execution errors
                check = self.checks[i]
                error_result = CheckResult(
                    name=check.name,
                    category=check.category,
                    status=CheckStatus.FAILED,
                    message=f"Check execution failed: {result!s}",
                    error=result,
                )
                report.add_check(error_result)
                logger.error(f"❌ Check {check.name} failed with exception: {result}")
            else:
                report.add_check(result)

        # Validate registries (integrated into async flow)
        registry_result = await self._validate_registries()
        if not registry_result.success:
            report.overall_status = CheckStatus.FAILED
            logger.error("❌ Registry validation failed - this is critical for system operation")

        # Generate recommendations
        self._generate_recommendations(report)

        total_duration = time.time() - self.start_time
        logger.info(
            f"Validation completed in {total_duration:.2f}s: {len(report.checks)} checks, "
            f"{len(report.critical_failures)} failures"
        )

        return report

    async def _validate_registries(self) -> Any:
        """
        Validate registries asynchronously.
        
        Returns:
            Registry validation result
        """
        try:
            # Run registry validation in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.registry_validator.validate_all_registries
            )
            return result
        except Exception as e:
            logger.error(f"❌ Registry validation failed: {e}")
            return type('RegistryResult', (), {'success': False})()

    async def _execute_check(self, check: Any, context: Dict[str, Any]) -> CheckResult:
        """
        Execute a single health check.
        
        Args:
            check: Health check instance to execute
            context: Context data for the check
            
        Returns:
            CheckResult with execution results
        """
        start_time = time.time()
        try:
            logger.info(f"🔧 Executing check: {check.name}")
            result = await check.execute(context)
            
            # Add timing information
            duration_ms = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms
            
            logger.info(f"🔧 Check {check.name} completed: {result.status.value} ({duration_ms:.1f}ms)")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ Error executing check {check.name}: {e}")
            
            # Create error result with timing
            error_result = CheckResult(
                name=check.name,
                category=check.category,
                status=CheckStatus.FAILED,
                message=f"Check execution error: {e!s}",
                error=e,
                duration_ms=duration_ms
            )
            return error_result

    def _generate_recommendations(self, report: ValidationReport) -> None:
        """
        Generate recommendations based on check results.
        
        Args:
            report: Validation report to add recommendations to
        """
        recommendations = []

        # Check for configuration issues
        config_failures = [
            check
            for check in report.checks
            if check.category == CheckCategory.CONFIGURATION and check.status == CheckStatus.FAILED
        ]
        if config_failures:
            recommendations.append("Review and fix configuration issues before proceeding")

        # Check for LLM issues
        llm_failures = [
            check
            for check in report.checks
            if check.category == CheckCategory.LLM and check.status == CheckStatus.FAILED
        ]
        if llm_failures:
            recommendations.append("Verify LLM provider configuration and API keys")

        # Check for database issues
        db_failures = [
            check
            for check in report.checks
            if check.category == CheckCategory.DATABASE and check.status == CheckStatus.FAILED
        ]
        if db_failures:
            recommendations.append("Check database connectivity and credentials")

        # Check for agent issues
        agent_failures = [
            check
            for check in report.checks
            if check.category == CheckCategory.AGENT and check.status == CheckStatus.FAILED
        ]
        if agent_failures:
            recommendations.append("Review agent configuration and tool setup")

        # Check for tool issues
        tool_failures = [
            check
            for check in report.checks
            if check.category == CheckCategory.TOOL and check.status == CheckStatus.FAILED
        ]
        if tool_failures:
            recommendations.append("Verify tool configuration and dependencies")

        # Check for registry issues
        registry_failures = [
            check
            for check in report.checks
            if check.category == CheckCategory.REGISTRY and check.status == CheckStatus.FAILED
        ]
        if registry_failures:
            recommendations.append("Review registry initialization and service discovery")

        # Add general recommendations
        if len(report.critical_failures) > 0:
            recommendations.append("Address critical failures before starting the application")

        if len(report.warnings) > 0:
            recommendations.append("Review warnings to ensure optimal system performance")

        # Add performance recommendations
        slow_checks = [
            check for check in report.checks 
            if check.duration_ms and check.duration_ms > 5000  # 5 seconds threshold
        ]
        if slow_checks:
            recommendations.append("Consider optimizing slow checks for better startup performance")

        report.recommendations = recommendations

    def print_report(self, report: ValidationReport) -> None:
        """
        Print a formatted validation report.
        
        Args:
            report: Validation report to print
        """
        logger.info("=" * 80)
        logger.info("🚀 KICKAI STARTUP VALIDATION REPORT")
        logger.info("=" * 80)

        # Overall status
        status_emoji = "✅" if report.is_healthy() else "❌"
        logger.info(f"{status_emoji} Overall Status: {report.overall_status.value}")

        # Summary by category
        logger.info("📊 Summary by Category:")
        for category, counts in report.summary.items():
            total = sum(counts.values())
            passed = counts.get(CheckStatus.PASSED, 0)
            failed = counts.get(CheckStatus.FAILED, 0)
            warnings = counts.get(CheckStatus.WARNING, 0)

            status_str = f"✅ {passed} | ❌ {failed} | ⚠️ {warnings}"
            logger.info(f"  {category.value}: {status_str}")

        # Critical failures
        if report.critical_failures:
            logger.error(f"❌ Critical Failures ({len(report.critical_failures)}):")
            for failure in report.critical_failures:
                logger.error(f"  • {failure}")

        # Warnings
        if report.warnings:
            logger.warning(f"⚠️ Warnings ({len(report.warnings)}):")
            for warning in report.warnings:
                logger.warning(f"  • {warning}")

        # Recommendations
        if report.recommendations:
            logger.info(f"💡 Recommendations ({len(report.recommendations)}):")
            for recommendation in report.recommendations:
                logger.info(f"  • {recommendation}")

        # Detailed results
        logger.info(f"🔍 Detailed Results ({len(report.checks)} checks):")
        for check in report.checks:
            status_emoji = {
                CheckStatus.PASSED: "✅",
                CheckStatus.FAILED: "❌",
                CheckStatus.WARNING: "⚠️",
                CheckStatus.SKIPPED: "⏭️",
            }.get(check.status, "❓")

            duration_str = f" ({check.duration_ms:.1f}ms)" if check.duration_ms else ""
            logger.info(f"  {status_emoji} {check.category.value}:{check.name}{duration_str}")
            logger.info(f"      {check.message}")

        logger.info("=" * 80)


async def run_startup_validation(team_id: Optional[str] = None) -> ValidationReport:
    """
    Run startup validation for the system.

    Args:
        team_id: Team ID for validation context

    Returns:
        ValidationReport with results
    """
    validator = StartupValidator()

    # Initialize dependency container to access services
    from kickai.core.dependency_container import initialize_container
    from kickai.features.team_administration.domain.interfaces.team_service_interface import (
        ITeamService,
    )

    initialize_container()

    # Get team service to fetch bot configuration from Firestore
    from kickai.core.dependency_container import get_service

    team_service = get_service(ITeamService)

    context = {"team_id": team_id}

    # If team_id is provided, fetch bot configuration from Firestore
    if team_id:
        try:
            team = await team_service.get_team(team_id=team_id)
            if team:
                bot_config = {
                    "bot_token": team.bot_token,
                    "main_chat_id": team.main_chat_id,
                    "leadership_chat_id": team.leadership_chat_id,
                    "bot_id": team.bot_id,
                }
                context["bot_config"] = bot_config
                logger.info(f"✅ Bot configuration loaded from Firestore for team {team_id}")
            else:
                logger.warning(
                    f"⚠️ Team {team_id} not found in Firestore, bot configuration unavailable"
                )
        except Exception as e:
            logger.error(
                f"❌ Failed to load bot configuration from Firestore for team {team_id}: {e}"
            )
    else:
        logger.warning(
            "⚠️ No team_id provided, bot configuration unavailable - bot config is stored in Firestore teams collection"
        )

    report = await validator.validate(context)
    validator.print_report(report)

    return report
