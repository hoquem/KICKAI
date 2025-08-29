#!/usr/bin/env python3
"""
Context Validation Check

This module provides validation for the single source of truth context system.
"""

import asyncio
from typing import Any, Dict

from loguru import logger

from kickai.core.startup_validation.checks.base_check import BaseCheck
from kickai.core.startup_validation.reporting import CheckResult, CheckStatus, CheckCategory
from kickai.core.context_types import StandardizedContext, validate_context_data, create_safe_context_fallback


class ContextValidationCheck(BaseCheck):
    """
    Validates the single source of truth context system.
    
    This check ensures that:
    - Context creation works properly
    - Validation functions work correctly
    - Factory methods create valid contexts
    - Serialization/deserialization works
    - Fallback mechanisms work
    """

    name = "Context Validation Check"
    category = CheckCategory.SYSTEM
    description = "Validates the single source of truth context system"

    async def execute(self, context: Dict[str, Any] = None) -> CheckResult:
        """Execute context validation checks."""
        try:
            errors = []
            
            # Test 1: Basic context creation
            try:
                test_context = StandardizedContext.create_from_telegram_message(
                    telegram_id=12345,
                    team_id="TEST",
                    chat_id="-1001234567890",
                    chat_type="main",
                    message_text="Hello world",
                    username="testuser",
                    telegram_name="Test User",
                    is_player=True
                )
                logger.info("✅ Basic context creation passed")
            except Exception as e:
                errors.append(f"Basic context creation failed: {e}")

            # Test 2: Context validation
            try:
                if test_context.validate_for_tool("test_tool"):
                    logger.info("✅ Context validation passed")
                else:
                    errors.append("Context validation failed")
            except Exception as e:
                errors.append(f"Context validation check failed: {e}")

            # Test 3: Serialization/deserialization
            try:
                context_dict = test_context.to_dict()
                recreated_context = StandardizedContext.from_dict(context_dict)
                if recreated_context.telegram_id == test_context.telegram_id:
                    logger.info("✅ Context serialization/deserialization passed")
                else:
                    errors.append("Context serialization/deserialization failed")
            except Exception as e:
                errors.append(f"Context serialization/deserialization failed: {e}")

            # Test 4: Command context creation
            try:
                command_context = StandardizedContext.create_from_command(
                    telegram_id=12345,
                    team_id="TEST",
                    chat_id="-1001234567890",
                    chat_type="leadership",
                    command="/addplayer",
                    username="admin",
                    telegram_name="Admin User",
                    is_team_member=True,
                    is_admin=True
                )
                logger.info("✅ Command context creation passed")
            except Exception as e:
                errors.append(f"Command context creation failed: {e}")

            # Test 5: System context creation
            try:
                system_context = StandardizedContext.create_system_context(
                    team_id="TEST",
                    operation="startup_validation"
                )
                logger.info("✅ System context creation passed")
            except Exception as e:
                errors.append(f"System context creation failed: {e}")

            # Test 6: Validation function
            try:
                test_data = {
                    "telegram_id": 12345,
                    "team_id": "TEST",
                    "chat_id": "-1001234567890",
                    "chat_type": "main",
                    "message_text": "test",
                    "username": "testuser"
                }
                if validate_context_data(test_data):
                    logger.info("✅ Context data validation passed")
                else:
                    errors.append("Context data validation failed")
            except Exception as e:
                errors.append(f"Context data validation failed: {e}")

            # Test 7: Fallback mechanism
            try:
                invalid_data = {"invalid": "data"}
                fallback = create_safe_context_fallback(invalid_data)
                if fallback["team_id"] == "unknown":
                    logger.info("✅ Context fallback mechanism passed")
                else:
                    errors.append("Context fallback mechanism failed")
            except Exception as e:
                errors.append(f"Context fallback mechanism failed: {e}")

            # Test 8: Context summary
            try:
                summary = test_context.get_context_summary()
                if "User: testuser" in summary and "Team: TEST" in summary:
                    logger.info("✅ Context summary generation passed")
                else:
                    errors.append("Context summary generation failed")
            except Exception as e:
                errors.append(f"Context summary generation failed: {e}")

            if errors:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Context validation failed with {len(errors)} errors",
                    details={"errors": errors}
                )
            
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message="Single source of truth context system validated successfully",
                details={"tests_passed": 8}
            )

        except Exception as e:
            logger.error(f"ContextValidationCheck failed: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"ContextValidationCheck failed: {e}",
                details={"error": str(e)}
            )
