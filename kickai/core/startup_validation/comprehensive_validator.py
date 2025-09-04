"""
Comprehensive startup validation for the KICKAI system.

This module provides a comprehensive validation system that checks all critical
components before the bot starts accepting requests.
"""

import asyncio
import time
from dataclasses import dataclass, field

from loguru import logger

from kickai.core.startup_validation.checks.database_check import DatabaseValidator
from kickai.core.startup_validation.checks.environment_check import EnvironmentValidator
from kickai.core.startup_validation.registry_validator import RegistryStartupValidator


@dataclass
class ComprehensiveValidationResult:
    """Result of comprehensive system validation."""

    success: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    critical_failures: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    validation_duration: float = 0.0
    component_results: dict[str, dict[str, any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default values after dataclass creation."""
        if self.critical_failures is None:
            self.critical_failures = []
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.recommendations is None:
            self.recommendations = []
        if self.component_results is None:
            self.component_results = {}


class ComprehensiveStartupValidator:
    """
    Comprehensive startup validator for the KICKAI system.

    Performs validation of all critical system components including:
    - Environment configuration
    - Database connectivity
    - Registry initialization
    - Service availability
    - Filesystem permissions
    """

    def __init__(self) -> None:
        """Initialize the comprehensive validator."""
        self.start_time: float = 0.0
        self.component_results: dict[str, dict[str, any]] = {}

    def validate_system_startup(self) -> ComprehensiveValidationResult:
        """
        Perform comprehensive system startup validation.

        Returns:
            ComprehensiveValidationResult: Detailed validation results
        """
        logger.info("🚀 Starting comprehensive system startup validation...")
        self.start_time = time.time()

        # Initialize result tracking
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        warnings: list[str] = []
        errors: list[str] = []
        critical_failures: list[str] = []
        recommendations: list[str] = []

        # 1. Environment Validation
        logger.info("🔍 Validating environment configuration...")
        env_start = time.time()
        try:
            env_check = EnvironmentValidator()
            env_result = env_check.validate_environment()
            env_duration = time.time() - env_start

            self.component_results["environment"] = {
                "success": env_result.success,
                "duration": env_duration,
                "errors": env_result.errors,
                "warnings": env_result.warnings,
            }

            # Environment validation doesn't have total_checks, passed_checks, failed_checks
            # It only has success, errors, warnings
            if env_result.success:
                passed_checks += 1
            else:
                failed_checks += 1
            total_checks += 1
            errors.extend(env_result.errors)
            warnings.extend(env_result.warnings)

            if not env_result.success:
                critical_failures.extend(env_result.errors)
                logger.error(f"❌ Environment validation failed: {env_result.errors}")
            else:
                logger.info(f"✅ Environment validation passed in {env_duration:.2f}s")

        except Exception as e:
            env_duration = time.time() - env_start
            error_msg = f"Environment validation crashed: {e!s}"
            critical_failures.append(error_msg)
            errors.append(error_msg)
            failed_checks += 1
            total_checks += 1
            logger.error(f"❌ {error_msg}")

            self.component_results["environment"] = {
                "success": False,
                "duration": env_duration,
                "errors": [error_msg],
                "warnings": [],
            }

        # 2. Database Validation
        logger.info("🗄️ Validating database connectivity...")
        db_start = time.time()
        try:
            db_check = DatabaseValidator()
            db_result = db_check.validate_database()
            db_duration = time.time() - db_start

            self.component_results["database"] = {
                "success": db_result.success,
                "duration": db_duration,
                "errors": db_result.errors,
                "warnings": db_result.warnings,
            }

            # Database validation doesn't have total_checks, passed_checks, failed_checks
            # It only has success, errors, warnings
            if db_result.success:
                passed_checks += 1
            else:
                failed_checks += 1
            total_checks += 1
            errors.extend(db_result.errors)
            warnings.extend(db_result.warnings)

            if not db_result.success:
                critical_failures.extend(db_result.errors)
                logger.error(f"❌ Database validation failed: {db_result.errors}")
            else:
                logger.info(f"✅ Database validation passed in {db_duration:.2f}s")

        except Exception as e:
            db_duration = time.time() - db_start
            error_msg = f"Database validation crashed: {e!s}"
            critical_failures.append(error_msg)
            errors.append(error_msg)
            failed_checks += 1
            total_checks += 1
            logger.error(f"❌ {error_msg}")

            self.component_results["database"] = {
                "success": False,
                "duration": db_duration,
                "errors": [error_msg],
                "warnings": [],
            }

        # 3. Registry Validation
        logger.info("📋 Validating registry initialization...")
        registry_start = time.time()
        try:
            registry_check = RegistryStartupValidator()
            registry_result = registry_check.validate_all_registries()
            registry_duration = time.time() - registry_start

            self.component_results["registry"] = {
                "success": registry_result.success,
                "duration": registry_duration,
                "errors": registry_result.errors,
                "warnings": registry_result.warnings,
            }

            # Registry validation doesn't have total_checks, passed_checks, failed_checks
            # It only has success, errors, warnings
            if registry_result.success:
                passed_checks += 1
            else:
                failed_checks += 1
            total_checks += 1
            errors.extend(registry_result.errors)
            warnings.extend(registry_result.warnings)

            if not registry_result.success:
                critical_failures.extend(registry_result.errors)
                logger.error(f"❌ Registry validation failed: {registry_result.errors}")
            else:
                logger.info(f"✅ Registry validation passed in {registry_duration:.2f}s")

        except Exception as e:
            registry_duration = time.time() - registry_start
            error_msg = f"Registry validation crashed: {e!s}"
            critical_failures.append(error_msg)
            errors.append(error_msg)
            failed_checks += 1
            total_checks += 1
            logger.error(f"❌ {error_msg}")

            self.component_results["registry"] = {
                "success": False,
                "duration": registry_duration,
                "errors": [error_msg],
                "warnings": [],
            }

        # 4. Service Validation
        logger.info("🔧 Validating service availability...")
        service_start = time.time()
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

            # Check critical services
            critical_services = [
                "DataStoreInterface",
                "PlayerRepositoryInterface",
                "TeamRepositoryInterface",
            ]

            service_errors = []
            service_warnings = []
            service_checks = 0
            service_passed = 0

            for service_name in critical_services:
                service_checks += 1
                try:
                    service = container.get_service(service_name)
                    if service is None:
                        error_msg = f"Service {service_name} is None"
                        service_errors.append(error_msg)
                        critical_failures.append(error_msg)
                        logger.error(f"❌ {error_msg}")
                    else:
                        service_passed += 1
                        logger.info(f"✅ Service {service_name} available")
                except Exception as e:
                    error_msg = f"Service {service_name} failed: {e!s}"
                    service_errors.append(error_msg)
                    critical_failures.append(error_msg)
                    logger.error(f"❌ {error_msg}")

            service_duration = time.time() - service_start
            service_success = len(service_errors) == 0

            self.component_results["services"] = {
                "success": service_success,
                "duration": service_duration,
                "errors": service_errors,
                "warnings": service_warnings,
            }

            total_checks += service_checks
            passed_checks += service_passed
            failed_checks += service_checks - service_passed
            errors.extend(service_errors)
            warnings.extend(service_warnings)

            if service_success:
                logger.info(f"✅ Service validation passed in {service_duration:.2f}s")
            else:
                logger.error(f"❌ Service validation failed: {service_errors}")

        except Exception as e:
            service_duration = time.time() - service_start
            error_msg = f"Service validation crashed: {e!s}"
            critical_failures.append(error_msg)
            errors.append(error_msg)
            failed_checks += 1
            total_checks += 1
            logger.error(f"❌ {error_msg}")

            self.component_results["services"] = {
                "success": False,
                "duration": service_duration,
                "errors": [error_msg],
                "warnings": [],
            }

        # Calculate overall success and duration
        total_duration = time.time() - self.start_time
        overall_success = len(critical_failures) == 0

        # Generate recommendations based on results
        if not overall_success:
            recommendations.append("Fix critical failures before starting the bot")
        if warnings:
            recommendations.append("Review warnings for potential issues")
        if failed_checks > 0:
            recommendations.append(f"Address {failed_checks} failed validation checks")

        # Create final result
        result = ComprehensiveValidationResult(
            success=overall_success,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            errors=errors,
            critical_failures=critical_failures,
            recommendations=recommendations,
            validation_duration=total_duration,
            component_results=self.component_results,
        )

        # Log final results
        if overall_success:
            logger.info(f"🎉 Comprehensive validation PASSED in {total_duration:.2f}s")
            logger.info(f"📊 Results: {passed_checks}/{total_checks} checks passed")
        else:
            logger.error(f"💥 Comprehensive validation FAILED in {total_duration:.2f}s")
            logger.error(f"📊 Results: {failed_checks}/{total_checks} checks failed")
            logger.error(f"🚨 Critical failures: {len(critical_failures)}")

        if warnings:
            logger.warning(f"⚠️ Warnings: {len(warnings)}")

        return result
