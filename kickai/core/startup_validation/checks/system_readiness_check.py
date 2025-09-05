"""
System Readiness Check

This check ensures all critical system components are available and properly configured
before allowing the system to start. This is the final gatekeeper check.
"""

import asyncio
import logging
from typing import Any

from kickai.core.enums import AgentRole, CheckCategory, CheckStatus
from kickai.core.startup_validation.checks.base_check import BaseCheck

logger = logging.getLogger(__name__)


class SystemReadinessCheck(BaseCheck):
    """Check that all critical system components are ready for operation."""

    name = "System Readiness"
    category = CheckCategory.SYSTEM
    description = "Ensures all critical system components are ready for operation"

    async def execute(self, context: dict[str, Any]) -> Any:
        """
        Execute the system readiness check.

        This check validates:
        1. All required services are available
        2. All required tools are registered
        3. All required agents are configured
        4. All required databases are accessible
        5. All required configurations are loaded
        """
        start_time = asyncio.get_event_loop().time()

        try:
            logger.info("🔍 Checking system readiness...")

            # Check 1: Dependency container is initialized
            readiness_checks = []

            # Check dependency container
            try:
                from kickai.core.dependency_container import get_container

                container = get_container()
                if container is None:
                    readiness_checks.append("❌ Dependency container not initialized")
                else:
                    readiness_checks.append("✅ Dependency container initialized")
            except Exception as e:
                readiness_checks.append(f"❌ Dependency container error: {e}")

            # Check 2: Required services are available
            try:
                from kickai.core.dependency_container import get_service
                from kickai.features.player_registration.domain.interfaces.player_service_interface import (
                    IPlayerService,
                )
                from kickai.features.team_administration.domain.interfaces.team_service_interface import (
                    ITeamService,
                )

                # Check team service
                try:
                    team_service = get_service(ITeamService)
                    if team_service is None:
                        readiness_checks.append("❌ Team service not available")
                    else:
                        readiness_checks.append("✅ Team service available")
                except Exception as e:
                    readiness_checks.append(f"❌ Team service error: {e}")

                # Check player service
                try:
                    player_service = get_service(IPlayerService)
                    if player_service is None:
                        readiness_checks.append("❌ Player service not available")
                    else:
                        readiness_checks.append("✅ Player service available")
                except Exception as e:
                    readiness_checks.append(f"❌ Player service error: {e}")

            except Exception as e:
                readiness_checks.append(f"❌ Service availability check error: {e}")

            # Check 3: Tool registry is populated
            try:
                from kickai.agents.tool_registry import get_tool_registry, initialize_tool_registry

                tool_registry = get_tool_registry()

                # Initialize tool registry if empty
                if not tool_registry.list_all_tools():
                    initialize_tool_registry("kickai")
                    tool_registry = get_tool_registry()

                tools = tool_registry.list_all_tools()
                if not tools:
                    readiness_checks.append("❌ No tools registered in tool registry")
                else:
                    readiness_checks.append(f"✅ {len(tools)} tools registered")
            except Exception as e:
                readiness_checks.append(f"❌ Tool registry error: {e}")

            # Check 4: Simplified Agent Configuration is available
            try:
                from kickai.agents.simplified_agent_factory import SimplifiedAgentFactory
                from kickai.config.agents import get_agent_config_manager

                # Check if agent configuration manager is available
                config_manager = get_agent_config_manager()
                # Use default context for validation
                context = {
                    "team_name": "KICKAI",
                    "team_id": "KAI",
                    "chat_type": "main",
                    "user_role": "public",
                    "username": "user",
                }
                enabled_configs = config_manager.get_enabled_agent_configs(context)

                if not enabled_configs:
                    readiness_checks.append("❌ No enabled agent configurations found")
                else:
                    readiness_checks.append(
                        f"✅ {len(enabled_configs)} agent configurations available"
                    )

                    # Test if we can create a simple agent
                    try:
                        factory = SimplifiedAgentFactory()
                        test_agent = factory.create_agent(AgentRole.HELP_ASSISTANT)
                        if test_agent:
                            readiness_checks.append("✅ Simplified agent factory working")
                        else:
                            readiness_checks.append(
                                "❌ Simplified agent factory failed to create agent"
                            )
                    except Exception as e:
                        readiness_checks.append(f"❌ Simplified agent factory error: {e}")

            except Exception as e:
                readiness_checks.append(f"❌ Simplified agent configuration error: {e}")

            # Check 5: Command registry is populated
            try:
                from kickai.core.command_registry_initializer import (
                    get_initialized_command_registry,
                    initialize_command_registry,
                )

                try:
                    command_registry = get_initialized_command_registry()
                except RuntimeError:
                    # Initialize if not already done
                    command_registry = initialize_command_registry()

                commands = command_registry.list_all_commands()
                if not commands:
                    readiness_checks.append("❌ No commands registered in command registry")
                else:
                    readiness_checks.append(f"✅ {len(commands)} commands registered")
            except Exception as e:
                readiness_checks.append(f"❌ Command registry error: {e}")

            # Check 6: Database connectivity
            try:
                from kickai.database.firebase_client import get_firebase_client

                firebase_client = get_firebase_client()
                if firebase_client is None:
                    readiness_checks.append("❌ Firebase client not available")
                else:
                    readiness_checks.append("✅ Firebase client available")
            except Exception as e:
                readiness_checks.append(f"❌ Database connectivity error: {e}")

            # Check 7: Settings configuration
            try:
                from kickai.core.config import get_settings

                settings = get_settings()
                if settings is None:
                    readiness_checks.append("❌ Settings not loaded")
                else:
                    readiness_checks.append("✅ Settings loaded")
            except Exception as e:
                readiness_checks.append(f"❌ Settings error: {e}")

            # Check 8: Bot configuration (if team_id provided)
            if context.get("team_id"):
                try:
                    from kickai.core.dependency_container import get_service
                    from kickai.features.team_administration.domain.interfaces.team_service_interface import (
                        ITeamService,
                    )

                    team_service = get_service(ITeamService)
                    if team_service:
                        team = await team_service.get_team(team_id=context["team_id"])
                        if team:
                            if team.bot_token:
                                readiness_checks.append("✅ Bot configuration available")
                            else:
                                readiness_checks.append("❌ Bot token not configured")
                        else:
                            readiness_checks.append(f"❌ Team {context['team_id']} not found")
                    else:
                        readiness_checks.append(
                            "❌ Team service not available for bot config check"
                        )
                except Exception as e:
                    readiness_checks.append(f"❌ Bot configuration check error: {e}")

            # Evaluate results
            failed_checks = [check for check in readiness_checks if check.startswith("❌")]
            passed_checks = [check for check in readiness_checks if check.startswith("✅")]

            if failed_checks:
                status = CheckStatus.FAILED
                message = f"System not ready: {len(failed_checks)} critical components missing"
                details = {
                    "failed_checks": failed_checks,
                    "passed_checks": passed_checks,
                    "total_checks": len(readiness_checks),
                    "failure_count": len(failed_checks),
                    "success_count": len(passed_checks),
                }
            else:
                status = CheckStatus.PASSED
                message = f"System ready: All {len(passed_checks)} critical components available"
                details = {
                    "passed_checks": passed_checks,
                    "total_checks": len(readiness_checks),
                    "success_count": len(passed_checks),
                }

            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000

            return self.create_result(
                status=status, message=message, details=details, duration_ms=duration_ms
            )

        except Exception as e:
            logger.error(f"❌ System readiness check failed with exception: {e}")
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000

            return self.create_result(
                status=CheckStatus.FAILED,
                message=f"System readiness check failed: {e!s}",
                error=e,
                duration_ms=duration_ms,
            )
