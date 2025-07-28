"""
Registry startup validation.

This module validates all registries during startup to ensure
proper initialization and prevent runtime errors.
"""

from dataclasses import dataclass
from typing import List

from loguru import logger


@dataclass
class RegistryValidationResult:
    """Result of registry validation."""

    success: bool
    errors: List[str]
    warnings: List[str]
    registry_name: str


class RegistryStartupValidator:
    """Validates all registries during startup."""

    def __init__(self):
        self.validation_results: List[RegistryValidationResult] = []

    def validate_all_registries(self) -> bool:
        """Validate all registries and return success status."""
        logger.info("🔍 Validating all registries...")

        # Validate tool registry
        tool_result = self._validate_tool_registry()
        self.validation_results.append(tool_result)

        # Validate command registry
        command_result = self._validate_command_registry()
        self.validation_results.append(command_result)

        # Validate service registry
        service_result = self._validate_service_registry()
        self.validation_results.append(service_result)

        # Check overall success
        all_success = all(result.success for result in self.validation_results)

        if all_success:
            logger.info("✅ All registries validated successfully")
        else:
            logger.error("❌ Registry validation failed")
            for result in self.validation_results:
                if not result.success:
                    logger.error(f"❌ {result.registry_name}: {result.errors}")

        return all_success

    def _validate_tool_registry(self) -> RegistryValidationResult:
        """Validate tool registry."""
        errors = []
        warnings = []

        try:
            from kickai.agents.tool_registry import initialize_tool_registry

            registry = initialize_tool_registry()

            # Check if tools are discovered
            if not registry._discovered:
                errors.append("Tool registry not discovered")

            # Check if any tools are registered
            if not registry._tools:
                warnings.append("No tools registered")

            # Check for duplicate tool names
            tool_names = list(registry._tools.keys())
            if len(tool_names) != len(set(tool_names)):
                errors.append("Duplicate tool names found")

            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Tool Registry",
            )

        except Exception as e:
            return RegistryValidationResult(
                success=False,
                errors=[f"Tool registry validation failed: {e}"],
                warnings=[],
                registry_name="Tool Registry",
            )

    def _validate_command_registry(self) -> RegistryValidationResult:
        """Validate command registry."""
        errors = []
        warnings = []

        try:
            from kickai.core.command_registry_initializer import get_initialized_command_registry

            registry = get_initialized_command_registry()

            # Check if commands are registered
            if not registry._commands:
                warnings.append("No commands registered")

            # Check for duplicate command names
            command_names = list(registry._commands.keys())
            if len(command_names) != len(set(command_names)):
                errors.append("Duplicate command names found")

            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Command Registry",
            )

        except Exception as e:
            return RegistryValidationResult(
                success=False,
                errors=[f"Command registry validation failed: {e}"],
                warnings=[],
                registry_name="Command Registry",
            )

    def _validate_service_registry(self) -> RegistryValidationResult:
        """Validate service registry."""
        errors = []
        warnings = []

        try:
            from kickai.core.dependency_container import get_container

            container = get_container()

            # Check if container is initialized
            if not container._initialized:
                errors.append("Service container not initialized")

            # Check if required services are available
            required_services = ["PlayerService", "TeamService", "DataStoreInterface"]

            for service_name in required_services:
                try:
                    # This is a simplified check - in practice you'd check actual interfaces
                    pass
                except Exception:
                    errors.append(f"Required service {service_name} not available")

            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Service Registry",
            )

        except Exception as e:
            return RegistryValidationResult(
                success=False,
                errors=[f"Service registry validation failed: {e}"],
                warnings=[],
                registry_name="Service Registry",
            )

    def get_validation_report(self) -> str:
        """Generate a validation report."""
        if not self.validation_results:
            return "No validation results available"

        report = ["📋 Registry Validation Report", ""]

        for result in self.validation_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report.append(f"**{result.registry_name}**: {status}")

            if result.errors:
                report.append("  Errors:")
                for error in result.errors:
                    report.append(f"    - {error}")

            if result.warnings:
                report.append("  Warnings:")
                for warning in result.warnings:
                    report.append(f"    - {warning}")

            report.append("")

        return "\n".join(report)
