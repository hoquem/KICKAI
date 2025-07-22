"""
Startup Validator

This module provides the main startup validator that orchestrates all health checks.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

from .checks import (
    ConfigurationCheck,
    LLMProviderCheck,
    AgentInitializationCheck,
    TelegramAdminCheck,
    ToolRegistrationCheck
)
from .reporting import ValidationReport, CheckResult, CheckStatus, CheckCategory

logger = logging.getLogger(__name__)


class StartupValidator:
    """
    Main startup validator that orchestrates all health checks.
    
    This class manages the execution of health checks and generates
    comprehensive validation reports.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.checks: List[Any] = []
        self._load_default_checks()
        logger.info(f"StartupValidator initialized with {len(self.checks)} checks")
    
    def _load_default_checks(self) -> None:
        """Load default health checks."""
        self.checks = [
            ConfigurationCheck(),
            LLMProviderCheck(),
            TelegramAdminCheck(),
            ToolRegistrationCheck(),  # Check tool registration before agent initialization
            AgentInitializationCheck()  # Enabled to catch agent initialization failures
        ]
    
    def add_check(self, check: Any) -> None:
        """Add a custom health check."""
        self.checks.append(check)
    
    def remove_check(self, check_name: str) -> None:
        """Remove a health check by name."""
        self.checks = [check for check in self.checks if check.name != check_name]
    
    async def validate(self, context: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """
        Execute all health checks and generate a validation report.
        
        Args:
            context: Optional context data for checks
            
        Returns:
            ValidationReport with all check results
        """
        if context is None:
            context = {}
        
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
                    message=f"Check execution failed: {str(result)}",
                    error=result
                )
                report.add_check(error_result)
            else:
                report.add_check(result)
        
        # Generate recommendations
        self._generate_recommendations(report)
        
        logger.info(f"Validation completed: {len(report.checks)} checks, {len(report.critical_failures)} failures")
        
        return report
    
    async def _execute_check(self, check: Any, context: Dict[str, Any]) -> CheckResult:
        """Execute a single health check."""
        try:
            logger.info(f"🔧 Executing check: {check.name}")
            result = await check.execute(context)
            logger.info(f"🔧 Check {check.name} completed: {result.status.value}")
            return result
        except Exception as e:
            logger.error(f"❌ Error executing check {check.name}: {e}")
            import traceback
            logger.error(f"❌ Check {check.name} traceback: {traceback.format_exc()}")
            return CheckResult(
                name=check.name,
                category=check.category,
                status=CheckStatus.FAILED,
                message=f"Check execution error: {str(e)}",
                error=e
            )
    
    def _generate_recommendations(self, report: ValidationReport) -> None:
        """Generate recommendations based on check results."""
        recommendations = []
        
        # Check for configuration issues
        config_failures = [check for check in report.checks 
                          if check.category == CheckCategory.CONFIGURATION and check.status == CheckStatus.FAILED]
        if config_failures:
            recommendations.append("Review and fix configuration issues before proceeding")
        
        # Check for LLM issues
        llm_failures = [check for check in report.checks 
                       if check.category == CheckCategory.LLM and check.status == CheckStatus.FAILED]
        if llm_failures:
            recommendations.append("Verify LLM provider configuration and API keys")
        
        # Check for database issues
        db_failures = [check for check in report.checks 
                      if check.category == CheckCategory.DATABASE and check.status == CheckStatus.FAILED]
        if db_failures:
            recommendations.append("Check database connectivity and credentials")
        
        # Check for agent issues
        agent_failures = [check for check in report.checks 
                         if check.category == CheckCategory.AGENT and check.status == CheckStatus.FAILED]
        if agent_failures:
            recommendations.append("Review agent configuration and tool setup")
        
        # Check for tool issues
        tool_failures = [check for check in report.checks 
                        if check.category == CheckCategory.TOOL and check.status == CheckStatus.FAILED]
        if tool_failures:
            recommendations.append("Verify tool configuration and dependencies")
        
        # Add general recommendations
        if len(report.critical_failures) > 0:
            recommendations.append("Address critical failures before starting the application")
        
        if len(report.warnings) > 0:
            recommendations.append("Review warnings to ensure optimal system performance")
        
        report.recommendations = recommendations
    
    def print_report(self, report: ValidationReport) -> None:
        """Print a formatted validation report."""
        logger.info("="*80)
        logger.info("🚀 KICKAI STARTUP VALIDATION REPORT")
        logger.info("="*80)
        
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
                CheckStatus.SKIPPED: "⏭️"
            }.get(check.status, "❓")
            
            duration_str = f" ({check.duration_ms:.1f}ms)" if check.duration_ms else ""
            logger.info(f"  {status_emoji} {check.category.value}:{check.name}{duration_str}")
            logger.info(f"      {check.message}")
        
        logger.info("="*80)


async def run_startup_validation(team_id: str = "KAI") -> ValidationReport:
    """
    Run startup validation for the system.
    
    Args:
        team_id: Team ID for validation context
        
    Returns:
        ValidationReport with results
    """
    validator = StartupValidator()
    context = {"team_id": team_id}
    
    report = await validator.validate(context)
    validator.print_report(report)
    
    return report 