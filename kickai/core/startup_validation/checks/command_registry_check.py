#!/usr/bin/env python3
"""
Command Registry Validation Check

This module provides a startup check to ensure the command registry is properly
initialized and contains the expected commands.
"""

import logging

from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck

logger = logging.getLogger(__name__)


class CommandRegistryCheck(BaseCheck):
    """
    Startup check to ensure the command registry is properly initialized.
    Validates command discovery and registration.
    """

    name = "CommandRegistryCheck"
    category = CheckCategory.CONFIGURATION
    description = (
        "Validates that the command registry is properly initialized with all expected commands."
    )

    async def execute(self, context=None) -> CheckResult:
        try:
            logger.info("🔧 Validating command registry initialization...")

            # Try to get the initialized command registry
            try:
                from kickai.core.command_registry_initializer import (
                    get_initialized_command_registry,
                )

                registry = get_initialized_command_registry()
                logger.info("✅ Command registry successfully retrieved")
            except RuntimeError as e:
                if "Command registry not initialized" in str(e):
                    # Try to initialize the registry in this context
                    logger.warning("⚠️ Command registry not accessible, attempting to initialize...")
                    try:
                        from kickai.core.command_registry_initializer import (
                            initialize_command_registry,
                        )

                        registry = initialize_command_registry()
                        logger.info(
                            "✅ Command registry successfully initialized in validation context"
                        )
                    except Exception as init_error:
                        logger.error(f"❌ Failed to initialize command registry: {init_error}")
                        return CheckResult(
                            name=self.name,
                            category=self.category,
                            status=CheckStatus.FAILED,
                            message="Command registry not initialized and failed to initialize in validation context.",
                            error=init_error,
                        )
                else:
                    raise

            # Get command statistics
            stats = registry.get_command_statistics()
            total_commands = stats.get("total_commands", 0)
            features = stats.get("features", [])

            logger.info("📊 Command registry statistics:")
            logger.info(f"  - Total commands: {total_commands}")
            logger.info(f"  - Features: {features}")

            # Validate that we have commands
            if total_commands == 0:
                logger.warning("⚠️ No commands found in registry")
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.WARNING,
                    message="Command registry is initialized but contains no commands. This may indicate a discovery issue.",
                )

            # Check for expected commands
            expected_commands = ["/help", "/start", "/register", "/myinfo", "/list", "/status"]

            missing_commands = []
            for cmd in expected_commands:
                if not registry.get_command(cmd):
                    missing_commands.append(cmd)

            if missing_commands:
                logger.warning(f"⚠️ Missing expected commands: {missing_commands}")
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.WARNING,
                    message=f"Command registry initialized with {total_commands} commands, but missing expected commands: {missing_commands}",
                )

            # Check for expected features
            expected_features = ["player_registration", "team_administration", "shared"]

            missing_features = []
            for feature in expected_features:
                if feature not in features:
                    missing_features.append(feature)

            if missing_features:
                logger.warning(f"⚠️ Missing expected features: {missing_features}")
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.WARNING,
                    message=f"Command registry initialized but missing expected features: {missing_features}",
                )

            logger.info(
                f"✅ Command registry validation passed: {total_commands} commands from {len(features)} features"
            )
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message=f"Command registry properly initialized with {total_commands} commands from {len(features)} features",
            )

        except Exception as e:
            logger.error(f"❌ Command registry validation failed: {e}")
            import traceback

            logger.error(f"❌ Command registry validation traceback: {traceback.format_exc()}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Command registry validation failed: {e!s}",
                error=e,
            )
