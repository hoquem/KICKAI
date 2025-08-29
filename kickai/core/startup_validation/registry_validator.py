"""
Registry startup validation.

This module validates all registries during startup to ensure
proper initialization and prevent runtime errors.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from loguru import logger


@dataclass
class RegistryValidationResult:
    """Result of registry validation."""

    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    registry_name: str = ""
    validation_duration: float = 0.0
    details: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default values after dataclass creation."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.details is None:
            self.details = {}


class RegistryStartupValidator:
    """
    Validates all registries during startup.
    
    Performs validation of:
    - Tool Registry: Ensures tools are properly discovered and registered
    - Command Registry: Validates command registration and uniqueness
    - Service Registry: Checks service availability and initialization
    """
    
    def __init__(self) -> None:
        """Initialize the registry validator."""
        self.validation_results: List[RegistryValidationResult] = []
        self.start_time: float = 0.0
        
        # Configuration for required services
        self.required_services = [
            "DataStoreInterface",
            "PlayerRepositoryInterface", 
            "TeamRepositoryInterface",
        ]

    def validate_all_registries(self) -> RegistryValidationResult:
        """
        Validate all registries and return success status.
        
        Returns:
            RegistryValidationResult: Overall validation result
        """
        logger.info("🔍 Validating all registries...")
        self.start_time = time.time()

        # Validate tool registry
        tool_result = self._validate_tool_registry()
        self.validation_results.append(tool_result)

        # Validate command registry
        command_result = self._validate_command_registry()
        self.validation_results.append(command_result)

        # Validate service registry
        service_result = self._validate_service_registry()
        self.validation_results.append(service_result)

        # Calculate overall results
        total_duration = time.time() - self.start_time
        all_success = all(result.success for result in self.validation_results)
        all_errors = []
        all_warnings = []

        for result in self.validation_results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)

        if all_success:
            logger.info(f"✅ All registries validated successfully in {total_duration:.2f}s")
        else:
            logger.error(f"❌ Registry validation failed in {total_duration:.2f}s")
            for result in self.validation_results:
                if not result.success:
                    logger.error(f"❌ {result.registry_name}: {result.errors}")

        return RegistryValidationResult(
            success=all_success,
            errors=all_errors,
            warnings=all_warnings,
            registry_name="All Registries",
            validation_duration=total_duration,
            details={
                "total_registries": len(self.validation_results),
                "passed_registries": sum(1 for r in self.validation_results if r.success),
                "failed_registries": sum(1 for r in self.validation_results if not r.success)
            }
        )

    def _validate_tool_registry(self) -> RegistryValidationResult:
        """
        Validate tool registry.
        
        Returns:
            RegistryValidationResult: Tool registry validation result
        """
        start_time = time.time()
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, any] = {}

        try:
            from kickai.agents.tool_registry import initialize_tool_registry

            registry = initialize_tool_registry()
            details["total_tools"] = len(registry._tools) if registry._tools else 0

            # Check if tools are discovered
            if not registry._discovered:
                errors.append("Tool registry not discovered - auto-discovery may have failed")
            else:
                details["discovered"] = True

            # Check if any tools are registered
            if not registry._tools:
                warnings.append("No tools registered - this may indicate a configuration issue")
                details["tools_registered"] = 0
            else:
                details["tools_registered"] = len(registry._tools)

            # Check for duplicate tool names
            if registry._tools:
                tool_names = list(registry._tools.keys())
                unique_names = set(tool_names)
                if len(tool_names) != len(unique_names):
                    duplicates = [name for name in tool_names if tool_names.count(name) > 1]
                    errors.append(f"Duplicate tool names found: {duplicates}")
                    details["duplicate_tools"] = duplicates
                else:
                    details["duplicate_tools"] = []

            # Check tool registry state
            if hasattr(registry, '_initialized') and not registry._initialized:
                errors.append("Tool registry not properly initialized")
                details["initialized"] = False
            else:
                details["initialized"] = True

            duration = time.time() - start_time
            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Tool Registry",
                validation_duration=duration,
                details=details
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Tool registry validation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return RegistryValidationResult(
                success=False,
                errors=[error_msg],
                warnings=[],
                registry_name="Tool Registry",
                validation_duration=duration,
                details={"error": str(e)}
            )

    def _validate_command_registry(self) -> RegistryValidationResult:
        """
        Validate command registry.
        
        Returns:
            RegistryValidationResult: Command registry validation result
        """
        start_time = time.time()
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, any] = {}

        try:
            from kickai.core.command_registry_initializer import initialize_command_registry

            registry = initialize_command_registry()
            details["total_commands"] = len(registry._commands) if registry._commands else 0

            # Check if commands are registered
            if not registry._commands:
                warnings.append("No commands registered - this may indicate a configuration issue")
                details["commands_registered"] = 0
            else:
                details["commands_registered"] = len(registry._commands)

            # Check for duplicate command names
            if registry._commands:
                command_names = list(registry._commands.keys())
                unique_names = set(command_names)
                if len(command_names) != len(unique_names):
                    duplicates = [name for name in command_names if command_names.count(name) > 1]
                    errors.append(f"Duplicate command names found: {duplicates}")
                    details["duplicate_commands"] = duplicates
                else:
                    details["duplicate_commands"] = []

            # Check command registry state
            if hasattr(registry, '_initialized') and not registry._initialized:
                errors.append("Command registry not properly initialized")
                details["initialized"] = False
            else:
                details["initialized"] = True

            # Check for command conflicts
            if registry._commands:
                conflicts = self._check_command_conflicts(registry._commands)
                if conflicts:
                    warnings.extend(conflicts)
                    details["conflicts"] = conflicts

            duration = time.time() - start_time
            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Command Registry",
                validation_duration=duration,
                details=details
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Command registry validation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return RegistryValidationResult(
                success=False,
                errors=[error_msg],
                warnings=[],
                registry_name="Command Registry",
                validation_duration=duration,
                details={"error": str(e)}
            )

    def _validate_service_registry(self) -> RegistryValidationResult:
        """
        Validate service registry.
        
        Returns:
            RegistryValidationResult: Service registry validation result
        """
        start_time = time.time()
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, any] = {}

        try:
            from kickai.core.dependency_container import get_container

            container = get_container()
            
            # Initialize container asynchronously
            try:
                asyncio.run(container.initialize())
            except RuntimeError:
                # If already in event loop, use create_task
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create a task and wait for it
                    task = loop.create_task(container.initialize())
                    loop.run_until_complete(task)
                else:
                    # Run in new event loop
                    asyncio.run(container.initialize())

            # Check required services
            available_services = 0
            failed_services = 0
            
            for service_name in self.required_services:
                try:
                    service = container.get_service(service_name)
                    if service is None:
                        error_msg = f"Service {service_name} is None"
                        errors.append(error_msg)
                        failed_services += 1
                        logger.error(f"❌ {error_msg}")
                    else:
                        available_services += 1
                        logger.info(f"✅ Service {service_name} available")
                except Exception as e:
                    error_msg = f"Service {service_name} failed: {str(e)}"
                    errors.append(error_msg)
                    failed_services += 1
                    logger.error(f"❌ {error_msg}")

            details.update({
                "required_services": len(self.required_services),
                "available_services": available_services,
                "failed_services": failed_services,
                "service_list": self.required_services
            })

            duration = time.time() - start_time
            return RegistryValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                registry_name="Service Registry",
                validation_duration=duration,
                details=details
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Service registry validation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return RegistryValidationResult(
                success=False,
                errors=[error_msg],
                warnings=[],
                registry_name="Service Registry",
                validation_duration=duration,
                details={"error": str(e)}
            )

    def _check_command_conflicts(self, commands: Dict[str, any]) -> List[str]:
        """
        Check for command conflicts between different features.
        
        Args:
            commands: Dictionary of registered commands
            
        Returns:
            List[str]: List of conflict warnings
        """
        conflicts = []
        
        # Check for feature conflicts (same command registered by different features)
        command_features = {}
        for cmd_name, cmd_info in commands.items():
            if hasattr(cmd_info, 'feature'):
                if cmd_name in command_features:
                    conflicts.append(f"Command '{cmd_name}' registered by multiple features: {command_features[cmd_name]} and {cmd_info.feature}")
                else:
                    command_features[cmd_name] = cmd_info.feature
        
        return conflicts

    def get_validation_report(self) -> str:
        """
        Generate a comprehensive validation report.
        
        Returns:
            str: Formatted validation report
        """
        if not self.validation_results:
            return "No validation results available"

        report = []
        report.append("📋 REGISTRY VALIDATION REPORT")
        report.append("=" * 50)
        report.append("")

        total_duration = sum(r.validation_duration for r in self.validation_results)
        passed_count = sum(1 for r in self.validation_results if r.success)
        failed_count = len(self.validation_results) - passed_count

        report.append(f"OVERALL STATUS: {'✅ PASS' if all(r.success for r in self.validation_results) else '❌ FAIL'}")
        report.append(f"TOTAL DURATION: {total_duration:.2f}s")
        report.append(f"REGISTRIES PASSED: {passed_count}/{len(self.validation_results)}")
        report.append("")

        for result in self.validation_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report.append(f"{result.registry_name.upper()}: {status} ({result.validation_duration:.2f}s)")
            
            if result.details:
                report.append("  Details:")
                for key, value in result.details.items():
                    if isinstance(value, list) and value:
                        report.append(f"    {key}: {value}")
                    elif not isinstance(value, list):
                        report.append(f"    {key}: {value}")

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
