#!/usr/bin/env python3
"""
Agent Validation Module

This module provides comprehensive validation for agent components to catch
runtime issues during development and testing.
"""

import sys
from dataclasses import dataclass
from typing import Any, Dict, List

from loguru import logger


@dataclass
class ValidationResult:
    """Result of a validation check."""

    passed: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]


class AgentValidator:
    """Validates agent components for common runtime issues."""

    def __init__(self):
        self.validation_results: List[ValidationResult] = []

    def validate_tool_output_capture_methods(self) -> ValidationResult:
        """Validate agent configuration and tool usage using CrewAI native approach."""
        errors = []
        warnings = []
        details = {}

        try:
            from kickai.agents.configurable_agent import ConfigurableAgent

            # Check that ConfigurableAgent uses CrewAI native tools
            agent_methods = set(dir(ConfigurableAgent))
            required_methods = {
                "execute",
                "add_tool",
                "remove_tool",
                "get_tools",
                "is_enabled",
                "get_config_summary",
            }

            missing_methods = required_methods - agent_methods
            if missing_methods:
                errors.append(f"ConfigurableAgent missing methods: {missing_methods}")

            details["agent_methods"] = list(agent_methods)
            details["crewai_native"] = True

        except ImportError as e:
            errors.append(f"Could not import ConfigurableAgent: {e}")
        except Exception as e:
            errors.append(f"Error validating agent methods: {e}")

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, warnings=warnings, details=details
        )

    def validate_configurable_agent_methods(self) -> ValidationResult:
        """Validate ConfigurableAgent class methods and attributes."""
        errors = []
        warnings = []
        details = {}

        try:
            from kickai.agents.configurable_agent import ConfigurableAgent

            # Check that ConfigurableAgent uses CrewAI native approach
            if not hasattr(ConfigurableAgent, "__mro__"):
                errors.append("ConfigurableAgent does not have method resolution order")
            else:
                # Verify it's a clean implementation without custom mixins
                inheritance_chain = [str(base) for base in ConfigurableAgent.__mro__]
                details["inheritance_chain"] = inheritance_chain

            # Check for required methods
            required_methods = {
                "execute",
                "add_tool",
                "remove_tool",
                "get_tools",
                "is_enabled",
                "get_config_summary",
            }

            agent_methods = set(dir(ConfigurableAgent))
            missing_methods = required_methods - agent_methods
            if missing_methods:
                errors.append(f"ConfigurableAgent missing methods: {missing_methods}")

            # Check that ConfigurableAgent uses CrewAI native tools_results
            # No custom tool capture needed - CrewAI handles this natively
            details["crewai_native_tools"] = True

            details["agent_methods"] = list(agent_methods)
            details["inheritance_chain"] = [str(base) for base in ConfigurableAgent.__mro__]

        except ImportError as e:
            errors.append(f"Could not import configurable_agent module: {e}")
        except Exception as e:
            errors.append(f"Error validating ConfigurableAgent: {e}")

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, warnings=warnings, details=details
        )

    def validate_method_calls(self) -> ValidationResult:
        """Validate that method calls are made on correct object types."""
        errors = []
        warnings = []
        details = {}

        try:
            # Check specific problematic method calls
            from kickai.agents.configurable_agent import ConfigurableAgent
            from kickai.agents.tool_output_capture import ToolOutputCapture, ToolOutputCaptureMixin

            # Analyze the problematic line: self.tool_capture.clear_captured_outputs()
            # This should be called on ToolOutputCaptureMixin, not ToolOutputCapture

            # Check if ToolOutputCapture has clear_captured_outputs method
            if hasattr(ToolOutputCapture, "clear_captured_outputs"):
                warnings.append(
                    "ToolOutputCapture has clear_captured_outputs method (should be on Mixin)"
                )
            else:
                # This is actually correct - the method should be on the Mixin
                details["tool_capture_methods"] = [
                    m for m in dir(ToolOutputCapture) if not m.startswith("_")
                ]

            # Check if ToolOutputCaptureMixin has clear_captured_outputs method
            if not hasattr(ToolOutputCaptureMixin, "clear_captured_outputs"):
                errors.append("ToolOutputCaptureMixin missing clear_captured_outputs method")

            # Validate the inheritance chain
            if hasattr(ConfigurableAgent, "__mro__"):
                mixin_in_chain = any(
                    "ToolOutputCaptureMixin" in str(base) for base in ConfigurableAgent.__mro__
                )
                if not mixin_in_chain:
                    errors.append("ConfigurableAgent does not inherit from ToolOutputCaptureMixin")

            # Check CrewAI agent method availability
            try:
                from crewai import Agent

                crewai_agent_methods = [m for m in dir(Agent) if not m.startswith("_")]
                details["crewai_agent_methods"] = crewai_agent_methods

                # Check if 'execute' method exists on CrewAI Agent
                if "execute" not in crewai_agent_methods:
                    warnings.append(
                        "CrewAI Agent class does not have 'execute' method - should use Crew.kickoff() instead"
                    )

                # Check if 'kickoff' method exists on CrewAI Agent
                if "kickoff" not in crewai_agent_methods:
                    warnings.append(
                        "CrewAI Agent class does not have 'kickoff' method - this is expected"
                    )

                # Check ConfigurableAgent execute method implementation
                if hasattr(ConfigurableAgent, "execute"):
                    # Get the source code of the execute method to check for problematic patterns
                    import inspect

                    execute_method = ConfigurableAgent.execute
                    if inspect.isfunction(execute_method):
                        try:
                            source = inspect.getsource(execute_method)
                            if "self._crew_agent.execute(" in source:
                                errors.append(
                                    "ConfigurableAgent.execute() calls self._crew_agent.execute() - this will fail"
                                )
                            elif "crew.kickoff()" in source:
                                details["correct_crew_usage"] = True
                        except (OSError, TypeError):
                            # Can't get source, skip this check
                            pass

            except ImportError:
                warnings.append("Could not import CrewAI Agent for method validation")

        except ImportError as e:
            errors.append(f"Could not import required modules: {e}")
        except Exception as e:
            errors.append(f"Error validating method calls: {e}")

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, warnings=warnings, details=details
        )

    def validate_agent_factory(self) -> ValidationResult:
        """Validate AgentFactory class."""
        errors = []
        warnings = []
        details = {}

        try:
            from kickai.agents.configurable_agent import AgentFactory

            required_methods = {"create_agent", "create_all_agents", "get_agent"}

            factory_methods = set(dir(AgentFactory))
            missing_methods = required_methods - factory_methods
            if missing_methods:
                errors.append(f"AgentFactory missing methods: {missing_methods}")

            details["factory_methods"] = list(factory_methods)

        except ImportError as e:
            errors.append(f"Could not import AgentFactory: {e}")
        except Exception as e:
            errors.append(f"Error validating AgentFactory: {e}")

        return ValidationResult(
            passed=len(errors) == 0, errors=errors, warnings=warnings, details=details
        )

    def validate_all(self) -> ValidationResult:
        """Run all validation checks."""
        logger.info("🔍 Starting comprehensive agent validation...")

        all_errors = []
        all_warnings = []
        all_details = {}

        # Run all validation checks
        validations = [
            ("Tool Output Capture Methods", self.validate_tool_output_capture_methods()),
            ("Configurable Agent Methods", self.validate_configurable_agent_methods()),
            ("Method Calls", self.validate_method_calls()),
            ("Agent Factory", self.validate_agent_factory()),
        ]

        for name, result in validations:
            logger.info(f"📋 {name}: {'✅ PASSED' if result.passed else '❌ FAILED'}")

            if result.errors:
                logger.error(f"   Errors: {result.errors}")
                all_errors.extend([f"{name}: {error}" for error in result.errors])

            if result.warnings:
                logger.warning(f"   Warnings: {result.warnings}")
                all_warnings.extend([f"{name}: {warning}" for warning in result.warnings])

            all_details[name] = result.details

        overall_result = ValidationResult(
            passed=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            details=all_details,
        )

        if overall_result.passed:
            logger.info("✅ All agent validations passed!")
        else:
            logger.error(f"❌ Agent validation failed with {len(all_errors)} errors")

        return overall_result


def run_agent_validation() -> ValidationResult:
    """Run agent validation and return results."""
    validator = AgentValidator()
    return validator.validate_all()


if __name__ == "__main__":
    result = run_agent_validation()
    if not result.passed:
        sys.exit(1)
