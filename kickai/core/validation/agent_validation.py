#!/usr/bin/env python3
"""
Agent Validation Module

This module provides comprehensive validation for agent components to catch
runtime issues during development and testing.
"""

import inspect
import sys
from dataclasses import dataclass
from typing import Any

from loguru import logger

# CONSTANTS
REQUIRED_AGENT_METHODS = {
    "execute",
    "add_tool",
    "remove_tool",
    "get_tools",
    "is_enabled",
    "get_config_summary",
}

REQUIRED_FACTORY_METHODS = {
    "create_agent",
    "create_all_agents",
    "get_agent",
}

# MODULE PATHS
CONFIGURABLE_AGENT_MODULE = "kickai.agents.configurable_agent"
CREWAI_AGENT_MODULE = "crewai"

# CLASS NAMES
CONFIGURABLE_AGENT_CLASS = "ConfigurableAgent"
AGENT_FACTORY_CLASS = "AgentFactory"
CREWAI_AGENT_CLASS = "Agent"

# METHOD NAMES
EXECUTE_METHOD = "execute"
KICKOFF_METHOD = "kickoff"

# VALIDATION PATTERNS
PROBLEMATIC_EXECUTE_PATTERN = "self._crew_agent.execute("
CORRECT_CREW_PATTERN = "crew.kickoff()"

# ERROR MESSAGES
ERROR_MESSAGES = {
    "IMPORT_ERROR": "Could not import {module}: {error}",
    "VALIDATION_ERROR": "Error validating {component}: {error}",
    "MISSING_METHODS": "{class_name} missing methods: {methods}",
    "MISSING_MRO": "{class_name} does not have method resolution order",
    "PROBLEMATIC_EXECUTE": "{class_name}.execute() calls self._crew_agent.execute() - this will fail",
}

# WARNING MESSAGES
WARNING_MESSAGES = {
    "CREWAI_NO_EXECUTE": "CrewAI Agent class does not have 'execute' method - should use Crew.kickoff() instead",
    "CREWAI_NO_KICKOFF": "CrewAI Agent class does not have 'kickoff' method - this is expected",
    "CREWAI_IMPORT_ERROR": "Could not import CrewAI Agent for method validation",
}

# LOG MESSAGES
LOG_MESSAGES = {
    "VALIDATION_STARTED": "Starting comprehensive agent validation",
    "VALIDATION_PASSED": "{name}: PASSED",
    "VALIDATION_FAILED": "{name}: FAILED",
    "VALIDATION_ERRORS": "Errors: {errors}",
    "VALIDATION_WARNINGS": "Warnings: {warnings}",
    "ALL_PASSED": "All agent validations passed!",
    "VALIDATION_FAILED_COUNT": "Agent validation failed with {count} errors",
}

# SUCCESS MESSAGES
SUCCESS_MESSAGES = {
    "CREWAI_NATIVE": "Using CrewAI native approach",
    "CORRECT_CREW_USAGE": "Using correct CrewAI kickoff pattern",
}


@dataclass
class ValidationResult:
    """Result of a validation check."""

    passed: bool
    errors: list[str]
    warnings: list[str]
    details: dict[str, Any]


class AgentValidator:
    """Validates agent components for common runtime issues."""

    def __init__(self) -> None:
        """Initialize the agent validator."""
        self.validation_results: list[ValidationResult] = []



    def validate_configurable_agent_methods(self) -> ValidationResult:
        """Validate ConfigurableAgent class methods and attributes."""
        errors = []
        warnings = []
        details = {}

        try:
            configurable_agent = self._import_configurable_agent()
            if not configurable_agent:
                return self._create_import_error_result(CONFIGURABLE_AGENT_CLASS)

            # Validate inheritance chain
            inheritance_result = self._validate_inheritance_chain(configurable_agent)
            errors.extend(inheritance_result.errors)
            details.update(inheritance_result.details)

            # Validate required methods
            method_result = self._validate_required_methods(configurable_agent, REQUIRED_AGENT_METHODS)
            errors.extend(method_result.errors)
            details.update(method_result.details)

            details["crewai_native_tools"] = True

        except Exception as e:
            errors.append(ERROR_MESSAGES["VALIDATION_ERROR"].format(
                component=CONFIGURABLE_AGENT_CLASS, error=str(e)
            ))

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, warnings=warnings, details=details
        )

    def validate_method_calls(self) -> ValidationResult:
        """Validate that method calls are made on correct object types."""
        errors = []
        warnings = []
        details = {}

        try:
            # Validate CrewAI agent methods
            crewai_result = self._validate_crewai_agent_methods()
            warnings.extend(crewai_result.warnings)
            details.update(crewai_result.details)

            # Validate ConfigurableAgent execute method
            execute_result = self._validate_execute_method_implementation()
            errors.extend(execute_result.errors)
            details.update(execute_result.details)

        except Exception as e:
            errors.append(ERROR_MESSAGES["VALIDATION_ERROR"].format(
                component="method calls", error=str(e)
            ))

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, warnings=warnings, details=details
        )

    def validate_agent_factory(self) -> ValidationResult:
        """Validate AgentFactory class."""
        errors = []
        warnings = []
        details = {}

        try:
            agent_factory = self._import_agent_factory()
            if not agent_factory:
                return self._create_import_error_result(AGENT_FACTORY_CLASS)

            factory_methods = set(dir(agent_factory))
            missing_methods = REQUIRED_FACTORY_METHODS - factory_methods

            if missing_methods:
                errors.append(ERROR_MESSAGES["MISSING_METHODS"].format(
                    class_name=AGENT_FACTORY_CLASS, methods=missing_methods
                ))

            details["factory_methods"] = list(factory_methods)

        except Exception as e:
            errors.append(ERROR_MESSAGES["VALIDATION_ERROR"].format(
                component=AGENT_FACTORY_CLASS, error=str(e)
            ))

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, warnings=warnings, details=details
        )

    def validate_all(self) -> ValidationResult:
        """Run all validation checks."""
        logger.info(LOG_MESSAGES["VALIDATION_STARTED"])

        all_errors = []
        all_warnings = []
        all_details = {}

        validations = [
            ("Configurable Agent Methods", self.validate_configurable_agent_methods()),
            ("Method Calls", self.validate_method_calls()),
            ("Agent Factory", self.validate_agent_factory()),
        ]

        for name, result in validations:
            self._log_validation_result(name, result)

            if result.errors:
                all_errors.extend([f"{name}: {error}" for error in result.errors])

            if result.warnings:
                all_warnings.extend([f"{name}: {warning}" for warning in result.warnings])

            all_details[name] = result.details

        overall_result = ValidationResult(
            passed=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            details=all_details,
        )

        self._log_overall_result(overall_result)
        return overall_result

    def _import_configurable_agent(self) -> Any | None:
        """Import ConfigurableAgent class."""
        try:
            module = __import__(CONFIGURABLE_AGENT_MODULE, fromlist=[CONFIGURABLE_AGENT_CLASS])
            return getattr(module, CONFIGURABLE_AGENT_CLASS)
        except ImportError as e:
            logger.error(ERROR_MESSAGES["IMPORT_ERROR"].format(
                module=CONFIGURABLE_AGENT_MODULE, error=str(e)
            ))
            return None

    def _import_agent_factory(self) -> Any | None:
        """Import AgentFactory class."""
        try:
            module = __import__(CONFIGURABLE_AGENT_MODULE, fromlist=[AGENT_FACTORY_CLASS])
            return getattr(module, AGENT_FACTORY_CLASS)
        except ImportError as e:
            logger.error(ERROR_MESSAGES["IMPORT_ERROR"].format(
                module=AGENT_FACTORY_CLASS, error=str(e)
            ))
            return None



    def _validate_inheritance_chain(self, agent_class: Any) -> ValidationResult:
        """Validate inheritance chain of agent class."""
        errors = []
        details = {}

        if not hasattr(agent_class, "__mro__"):
            errors.append(ERROR_MESSAGES["MISSING_MRO"].format(class_name=CONFIGURABLE_AGENT_CLASS))
        else:
            inheritance_chain = [str(base) for base in agent_class.__mro__]
            details["inheritance_chain"] = inheritance_chain

        return ValidationResult(passed=len(errors) == 0, errors=errors, warnings=[], details=details)

    def _validate_required_methods(self, class_obj: Any, required_methods: set[str]) -> ValidationResult:
        """Validate that class has required methods."""
        errors = []
        details = {}

        class_methods = set(dir(class_obj))
        missing_methods = required_methods - class_methods

        if missing_methods:
            errors.append(ERROR_MESSAGES["MISSING_METHODS"].format(
                class_name=class_obj.__name__, methods=missing_methods
            ))

        details["class_methods"] = list(class_methods)
        return ValidationResult(passed=len(errors) == 0, errors=errors, warnings=[], details=details)



    def _validate_crewai_agent_methods(self) -> ValidationResult:
        """Validate CrewAI agent methods."""
        warnings = []
        details = {}

        try:
            crewai_module = __import__(CREWAI_AGENT_MODULE, fromlist=[CREWAI_AGENT_CLASS])
            crewai_agent = getattr(crewai_module, CREWAI_AGENT_CLASS)

            crewai_agent_methods = [m for m in dir(crewai_agent) if not m.startswith("_")]
            details["crewai_agent_methods"] = crewai_agent_methods

            if EXECUTE_METHOD not in crewai_agent_methods:
                warnings.append(WARNING_MESSAGES["CREWAI_NO_EXECUTE"])

            if KICKOFF_METHOD not in crewai_agent_methods:
                warnings.append(WARNING_MESSAGES["CREWAI_NO_KICKOFF"])

        except ImportError:
            warnings.append(WARNING_MESSAGES["CREWAI_IMPORT_ERROR"])

        return ValidationResult(passed=True, errors=[], warnings=warnings, details=details)

    def _validate_execute_method_implementation(self) -> ValidationResult:
        """Validate ConfigurableAgent execute method implementation."""
        errors = []
        details = {}

        try:
            configurable_agent = self._import_configurable_agent()
            if not configurable_agent or not hasattr(configurable_agent, EXECUTE_METHOD):
                return ValidationResult(passed=True, errors=[], warnings=[], details=details)

            execute_method = getattr(configurable_agent, EXECUTE_METHOD)
            if inspect.isfunction(execute_method):
                try:
                    source = inspect.getsource(execute_method)
                    if PROBLEMATIC_EXECUTE_PATTERN in source:
                        errors.append(ERROR_MESSAGES["PROBLEMATIC_EXECUTE"].format(
                            class_name=CONFIGURABLE_AGENT_CLASS
                        ))
                    elif CORRECT_CREW_PATTERN in source:
                        details["correct_crew_usage"] = True
                except (OSError, TypeError):
                    # Can't get source, skip this check
                    pass

        except Exception as e:
            errors.append(ERROR_MESSAGES["VALIDATION_ERROR"].format(
                component="execute method", error=str(e)
            ))

        return ValidationResult(passed=len(errors) == 0, errors=errors, warnings=[], details=details)

    def _create_import_error_result(self, class_name: str) -> ValidationResult:
        """Create validation result for import errors."""
        errors = [ERROR_MESSAGES["IMPORT_ERROR"].format(module=class_name, error="Import failed")]
        return ValidationResult(passed=False, errors=errors, warnings=[], details={})

    def _log_validation_result(self, name: str, result: ValidationResult) -> None:
        """Log individual validation result."""
        status = LOG_MESSAGES["VALIDATION_PASSED"] if result.passed else LOG_MESSAGES["VALIDATION_FAILED"]
        logger.info(status.format(name=name))

        if result.errors:
            logger.error(LOG_MESSAGES["VALIDATION_ERRORS"].format(errors=result.errors))

        if result.warnings:
            logger.warning(LOG_MESSAGES["VALIDATION_WARNINGS"].format(warnings=result.warnings))

    def _log_overall_result(self, result: ValidationResult) -> None:
        """Log overall validation result."""
        if result.passed:
            logger.info(LOG_MESSAGES["ALL_PASSED"])
        else:
            logger.error(LOG_MESSAGES["VALIDATION_FAILED_COUNT"].format(count=len(result.errors)))


def run_agent_validation() -> ValidationResult:
    """Run agent validation and return results."""
    validator = AgentValidator()
    return validator.validate_all()


if __name__ == "__main__":
    result = run_agent_validation()
    if not result.passed:
        sys.exit(1)
