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
    StartupValidator,
    run_startup_validation,
    ValidationReport,
    CheckResult,
    CheckStatus,
    CheckCategory
)

from .startup_validation.checks import (
    ConfigurationCheck,
    LLMProviderCheck,
    AgentInitializationCheck,
    ToolConfigurationCheck,
    DatabaseConnectivityCheck,
    TeamMappingCheck,
    CrewValidationCheck,
    TelegramBotCheck
)

# Re-export for backward compatibility
__all__ = [
    'StartupValidator',
    'run_startup_validation',
    'ValidationReport',
    'CheckResult',
    'CheckStatus',
    'CheckCategory',
    'ConfigurationCheck',
    'LLMProviderCheck',
    'AgentInitializationCheck',
    'ToolConfigurationCheck',
    'DatabaseConnectivityCheck',
    'TeamMappingCheck',
    'CrewValidationCheck',
    'TelegramBotCheck'
] 