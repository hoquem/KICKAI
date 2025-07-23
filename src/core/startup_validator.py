"""
Pre-flight Checks / Health Checks Module - Modular Architecture

This module has been refactored to use a modular architecture with separate
components for different types of health checks and reporting.

The monolithic StartupValidator has been split into focused components:
- checks/: Individual health check implementations
- reporting/: Validation report structures and formatting
- validator.py: Main orchestrator class

This refactoring follows the single responsibility principle and improves
maintainability and testability.
"""

# Import from the new modular structure
from .startup_validation import (
    CheckCategory,
    CheckResult,
    CheckStatus,
    StartupValidator,
    ValidationReport,
    run_startup_validation,
)
from .startup_validation.checks import (
    AgentInitializationCheck,
    ConfigurationCheck,
    LLMProviderCheck,
)

# Re-export for backward compatibility
__all__ = [
    'AgentInitializationCheck',
    'CheckCategory',
    'CheckResult',
    'CheckStatus',
    'ConfigurationCheck',
    'LLMProviderCheck',
    'StartupValidator',
    'ValidationReport',
    'run_startup_validation'
]
