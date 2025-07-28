"""
Validation Reporting

This module provides reporting structures for startup validation results.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from kickai.core.enums import CheckStatus, CheckCategory

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Result of a health check."""

    name: str
    category: CheckCategory
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error: Optional[Exception] = None


@dataclass
class ValidationReport:
    """Complete validation report."""

    overall_status: CheckStatus
    checks: List[CheckResult] = field(default_factory=list)
    summary: Dict[CheckCategory, dict[CheckStatus, int]] = field(default_factory=dict)
    critical_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def add_check(self, check: CheckResult) -> None:
        """Add a check result to the report."""
        self.checks.append(check)

        # Update summary
        if check.category not in self.summary:
            self.summary[check.category] = dict.fromkeys(CheckStatus, 0)
        self.summary[check.category][check.status] += 1

        # Track critical failures and warnings
        if check.status == CheckStatus.FAILED:
            self.critical_failures.append(f"{check.category.value}: {check.name} - {check.message}")
        elif check.status == CheckStatus.WARNING:
            self.warnings.append(f"{check.category.value}: {check.name} - {check.message}")

    def is_healthy(self) -> bool:
        """Check if the system is healthy (no critical failures)."""
        return len(self.critical_failures) == 0

    def get_failure_count(self) -> int:
        """Get the number of failed checks."""
        return len([check for check in self.checks if check.status == CheckStatus.FAILED])

    def get_warning_count(self) -> int:
        """Get the number of warning checks."""
        return len([check for check in self.checks if check.status == CheckStatus.WARNING])

    def get_passed_count(self) -> int:
        """Get the number of passed checks."""
        return len([check for check in self.checks if check.status == CheckStatus.PASSED])

    def get_total_count(self) -> int:
        """Get the total number of checks."""
        return len(self.checks)

    def get_success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self.get_total_count() == 0:
            return 0.0
        return (self.get_passed_count() / self.get_total_count()) * 100

    def get_failures_by_category(self) -> Dict[CheckCategory, List[CheckResult]]:
        """Get failed checks grouped by category."""
        failures = {}
        for check in self.checks:
            if check.status == CheckStatus.FAILED:
                if check.category not in failures:
                    failures[check.category] = []
                failures[check.category].append(check)
        return failures

    def get_warnings_by_category(self) -> Dict[CheckCategory, List[CheckResult]]:
        """Get warning checks grouped by category."""
        warnings = {}
        for check in self.checks:
            if check.status == CheckStatus.WARNING:
                if check.category not in warnings:
                    warnings[check.category] = []
                warnings[check.category].append(check)
        return warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "overall_status": self.overall_status.value,
            "checks": [
                {
                    "name": check.name,
                    "category": check.category.value,
                    "status": check.status.value,
                    "message": check.message,
                    "details": check.details,
                    "duration_ms": check.duration_ms,
                    "error": str(check.error) if check.error else None,
                }
                for check in self.checks
            ],
            "summary": {
                category.value: {status.value: count for status, count in status_counts.items()}
                for category, status_counts in self.summary.items()
            },
            "critical_failures": self.critical_failures,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "statistics": {
                "total_checks": self.get_total_count(),
                "passed_checks": self.get_passed_count(),
                "failed_checks": self.get_failure_count(),
                "warning_checks": self.get_warning_count(),
                "success_rate": self.get_success_rate(),
            },
        }

    def to_json(self) -> str:
        """Convert report to JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=2)

    def to_markdown(self) -> str:
        """Convert report to markdown format."""
        markdown = "# KICKAI Startup Validation Report\n\n"

        # Overall status
        status_emoji = "✅" if self.is_healthy() else "❌"
        markdown += f"{status_emoji} Overall Status: {self.overall_status.value}\n\n"

        # Statistics
        markdown += "## Statistics\n\n"
        markdown += f"- Total Checks: {self.get_total_count()}\n"
        markdown += f"- Passed: {self.get_passed_count()}\n"
        markdown += f"- Failed: {self.get_failure_count()}\n"
        markdown += f"- Warnings: {self.get_warning_count()}\n"
        markdown += f"- Success Rate: {self.get_success_rate():.1f}%\n\n"

        # Summary by category
        markdown += "## Summary by Category\n\n"
        for category, counts in self.summary.items():
            total = sum(counts.values())
            passed = counts.get(CheckStatus.PASSED, 0)
            failed = counts.get(CheckStatus.FAILED, 0)
            warnings = counts.get(CheckStatus.WARNING, 0)

            status_str = f"✅ {passed} | ❌ {failed} | ⚠️ {warnings}"
            markdown += f"### {category.value}\n"
            markdown += f"{status_str}\n\n"

        # Critical failures
        if self.critical_failures:
            markdown += "## Critical Failures\n\n"
            for failure in self.critical_failures:
                markdown += f"- ❌ {failure}\n"
            markdown += "\n"

        # Warnings
        if self.warnings:
            markdown += "## Warnings\n\n"
            for warning in self.warnings:
                markdown += f"- ⚠️ {warning}\n"
            markdown += "\n"

        # Recommendations
        if self.recommendations:
            markdown += "## Recommendations\n\n"
            for recommendation in self.recommendations:
                markdown += f"- 💡 {recommendation}\n"
            markdown += "\n"

        # Detailed results
        markdown += "## Detailed Results\n\n"
        for check in self.checks:
            status_emoji = {
                CheckStatus.PASSED: "✅",
                CheckStatus.FAILED: "❌",
                CheckStatus.WARNING: "⚠️",
                CheckStatus.SKIPPED: "⏭️",
            }.get(check.status, "❓")

            duration_str = f" ({check.duration_ms:.1f}ms)" if check.duration_ms else ""
            markdown += f"### {status_emoji} {check.category.value}: {check.name}{duration_str}\n\n"
            markdown += f"Message: {check.message}\n\n"

            if check.details:
                markdown += "Details:\n"
                for key, value in check.details.items():
                    markdown += f"- {key}: {value}\n"
                markdown += "\n"

            if check.error:
                markdown += f"Error: {check.error!s}\n\n"

        return markdown
