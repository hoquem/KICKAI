#!/usr/bin/env python3
"""
Environment Variable Validation Check

This module validates that all required environment variables are present
and properly configured for the KICKAI system.
"""

import os
from dataclasses import dataclass

from loguru import logger


@dataclass
class EnvironmentValidationResult:
    """Result of environment validation."""

    success: bool
    errors: list[str]
    warnings: list[str]
    missing_vars: list[str]
    invalid_vars: list[str]


class EnvironmentValidator:
    """Validates environment variables for the KICKAI system."""

    def __init__(self):
        self.required_vars = [
            "KICKAI_INVITE_SECRET_KEY",
            "AI_PROVIDER",
            "OLLAMA_BASE_URL",
            "FIREBASE_PROJECT_ID"
        ]

        self.optional_vars = [
            "USE_MOCK_DATASTORE",
            "MOCK_TELEGRAM_BASE_URL",
            "MOCK_TELEGRAM_PORT",
            "OLLAMA_MODEL"
        ]

        self.validation_rules = {
            "KICKAI_INVITE_SECRET_KEY": {
                "min_length": 10,
                "description": "Secret key for secure invite link generation"
            },
            "AI_PROVIDER": {
                "allowed_values": ["ollama", "openai", "google", "mock"],
                "description": "AI provider for the system"
            },
            "OLLAMA_BASE_URL": {
                "pattern": r"^https?://",
                "description": "Base URL for Ollama service"
            },
            "FIREBASE_PROJECT_ID": {
                "min_length": 5,
                "description": "Firebase project identifier"
            }
        }

    def validate_environment(self) -> EnvironmentValidationResult:
        """Validate all environment variables."""
        errors = []
        warnings = []
        missing_vars = []
        invalid_vars = []

        try:
            # Check required variables
            for var_name in self.required_vars:
                value = os.getenv(var_name)

                if not value:
                    missing_vars.append(var_name)
                    errors.append(f"Required environment variable {var_name} is not set")
                    continue

                # Validate specific rules
                validation_error = self._validate_variable(var_name, value)
                if validation_error:
                    invalid_vars.append(var_name)
                    errors.append(validation_error)

            # Check optional variables
            for var_name in self.optional_vars:
                value = os.getenv(var_name)

                if value:
                    validation_error = self._validate_variable(var_name, value)
                    if validation_error:
                        warnings.append(f"Optional environment variable {var_name}: {validation_error}")

            # Check for critical security issues
            security_issues = self._check_security_issues()
            errors.extend(security_issues)

            return EnvironmentValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                missing_vars=missing_vars,
                invalid_vars=invalid_vars
            )

        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return EnvironmentValidationResult(
                success=False,
                errors=[f"Environment validation failed: {e}"],
                warnings=[],
                missing_vars=[],
                invalid_vars=[]
            )

    def _validate_variable(self, var_name: str, value: str) -> str | None:
        """Validate a specific environment variable."""
        if var_name not in self.validation_rules:
            return None

        rules = self.validation_rules[var_name]

        # Check minimum length
        if "min_length" in rules and len(value) < rules["min_length"]:
            return f"{var_name} must be at least {rules['min_length']} characters long"

        # Check allowed values
        if "allowed_values" in rules and value not in rules["allowed_values"]:
            return f"{var_name} must be one of: {', '.join(rules['allowed_values'])}"

        # Check pattern
        if "pattern" in rules:
            import re
            if not re.match(rules["pattern"], value):
                return f"{var_name} must match pattern: {rules['pattern']}"

        return None

    def _check_security_issues(self) -> list[str]:
        """Check for security-related issues."""
        issues = []

        # Check for weak secret keys
        secret_key = os.getenv("KICKAI_INVITE_SECRET_KEY")
        if secret_key and len(secret_key) < 20:
            issues.append("KICKAI_INVITE_SECRET_KEY is too short for production use")

        # Check for default/development values in production
        ai_provider = os.getenv("AI_PROVIDER")
        if ai_provider == "mock" and os.getenv("NODE_ENV") == "production":
            issues.append("Mock AI provider should not be used in production")

        # Check for exposed credentials
        firebase_creds = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if firebase_creds and "test" in firebase_creds.lower():
            issues.append("Test Firebase credentials detected - check production configuration")

        return issues

    def get_validation_report(self) -> str:
        """Generate a validation report."""
        result = self.validate_environment()

        report = ["🔧 Environment Validation Report", ""]

        status = "✅ PASS" if result.success else "❌ FAIL"
        report.append(f"**Status**: {status}")
        report.append("")

        if result.errors:
            report.append("**Errors**:")
            for error in result.errors:
                report.append(f"  - {error}")
            report.append("")

        if result.warnings:
            report.append("**Warnings**:")
            for warning in result.warnings:
                report.append(f"  - {warning}")
            report.append("")

        if result.missing_vars:
            report.append("**Missing Variables**:")
            for var in result.missing_vars:
                report.append(f"  - {var}")
            report.append("")

        if result.invalid_vars:
            report.append("**Invalid Variables**:")
            for var in result.invalid_vars:
                report.append(f"  - {var}")
            report.append("")

        return "\n".join(report)


def validate_environment() -> EnvironmentValidationResult:
    """Convenience function to validate environment."""
    validator = EnvironmentValidator()
    return validator.validate_environment()
