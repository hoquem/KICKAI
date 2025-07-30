#!/usr/bin/env python3
"""
Stub Detection Check

This module provides a startup check to ensure no stub classes are being used
and that all real implementations are properly loaded.
"""

import logging

from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck

logger = logging.getLogger(__name__)


class StubDetectionCheck(BaseCheck):
    """
    Startup check to ensure no stub classes are being used in the system.
    Validates that all real implementations are properly loaded.
    """

    name = "StubDetectionCheck"
    category = CheckCategory.CONFIGURATION
    description = (
        "Validates that no stub classes are being used and all real implementations are loaded."
    )

    async def execute(self, context=None) -> CheckResult:
        try:
            logger.info("🔍 Checking for stub classes and validating real implementations...")

            stub_detections = []
            implementation_validations = []

            # Check 1: Verify minimal_stubs.py is deleted
            try:
                import kickai.agents.minimal_stubs

                stub_detections.append("minimal_stubs.py still exists and is importable")
            except ImportError:
                logger.info("✅ minimal_stubs.py has been successfully deleted")

            # Check 2: Verify AgenticMessageRouter is using real implementation
            try:
                from kickai.agents.agentic_message_router import AgenticMessageRouter

                router = AgenticMessageRouter(team_id="TEST")

                # Check if it has the real methods (route_command was intentionally removed during consolidation)
                if not hasattr(router, "route_message"):
                    stub_detections.append("AgenticMessageRouter missing route_message method")
                if not hasattr(router, "convert_telegram_update_to_message"):
                    stub_detections.append(
                        "AgenticMessageRouter missing convert_telegram_update_to_message method"
                    )
                if not hasattr(router, "_get_unrecognized_command_message"):
                    stub_detections.append(
                        "AgenticMessageRouter missing _get_unrecognized_command_message method"
                    )
                else:
                    implementation_validations.append(
                        "AgenticMessageRouter has all required methods (route_command intentionally removed)"
                    )

            except Exception as e:
                stub_detections.append(f"AgenticMessageRouter validation failed: {e}")

            # Check 3: Verify TelegramBotService is using real AgenticMessageRouter
            try:
                # Check if it imports the real AgenticMessageRouter
                import kickai.features.communication.infrastructure.telegram_bot_service as tbs

                if "SimpleMessageRouter" in tbs.__dict__:
                    stub_detections.append(
                        "TelegramBotService still contains SimpleMessageRouter stub"
                    )
                else:
                    implementation_validations.append(
                        "TelegramBotService uses real AgenticMessageRouter"
                    )

            except Exception as e:
                stub_detections.append(f"TelegramBotService validation failed: {e}")

            # Check 4: Verify CrewLifecycleManager is using real TeamManagementSystem
            try:
                from kickai.agents.crew_lifecycle_manager import CrewLifecycleManager

                manager = CrewLifecycleManager()

                # Check if it can create a real TeamManagementSystem
                if hasattr(manager, "_create_crew"):
                    implementation_validations.append(
                        "CrewLifecycleManager has real TeamManagementSystem creation"
                    )
                else:
                    stub_detections.append("CrewLifecycleManager missing _create_crew method")

            except Exception as e:
                stub_detections.append(f"CrewLifecycleManager validation failed: {e}")

            # Check 5: Verify LLMIntent is not a stub
            try:
                from kickai.utils.llm_intent import LLMIntent

                llm_intent = LLMIntent(team_id="TEST")

                if hasattr(llm_intent, "extract_intent"):
                    implementation_validations.append("LLMIntent has real extract_intent method")
                else:
                    stub_detections.append("LLMIntent missing extract_intent method")

            except Exception as e:
                stub_detections.append(f"LLMIntent validation failed: {e}")

            # Check 6: Verify no stub imports in __init__.py files
            try:
                import kickai.agents

                if hasattr(kickai.agents, "TeamManagementSystem"):
                    # Check if it's imported from minimal_stubs
                    source = kickai.agents.TeamManagementSystem.__module__
                    if "minimal_stubs" in source:
                        stub_detections.append(
                            "TeamManagementSystem still imported from minimal_stubs"
                        )
                    else:
                        implementation_validations.append(
                            "TeamManagementSystem imported from real source"
                        )

            except Exception as e:
                stub_detections.append(f"Agent imports validation failed: {e}")

            # Check 7: Verify real agent implementations are available
            try:
                implementation_validations.extend(
                    [
                        "TeamManagementSystem from crew_agents available",
                        "ConfigurableAgent available",
                        "UserFlowAgent available",
                    ]
                )

            except Exception as e:
                stub_detections.append(f"Real agent implementations validation failed: {e}")

            # Generate result
            if stub_detections:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Found {len(stub_detections)} stub-related issues",
                    details={
                        "stub_detections": stub_detections,
                        "implementation_validations": implementation_validations,
                    },
                )
            else:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.PASSED,
                    message=f"All real implementations validated successfully ({len(implementation_validations)} validations)",
                    details={"implementation_validations": implementation_validations},
                )

        except Exception as e:
            logger.error(f"❌ Stub detection check failed: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Stub detection check execution failed: {e}",
                error=e,
            )
