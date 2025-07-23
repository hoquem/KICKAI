#!/usr/bin/env python3
"""
Tool Registration Check

This module provides health checks for tool registration and discovery.
"""

from typing import Any

from loguru import logger

from ..reporting import CheckCategory, CheckResult, CheckStatus
from .base_check import BaseCheck


class ToolRegistrationCheck(BaseCheck):
    """
    Health check for tool registration and discovery.
    
    This check validates that:
    1. Tool registry can be initialized
    2. Tools are discovered from the source code
    3. Tools are properly registered
    4. Each agent has access to appropriate tools
    """

    def __init__(self):
        self.name = "Tool Registration Check"
        self.category = CheckCategory.TOOL
        self.description = "Validates tool registration and discovery"

    async def execute(self, context: dict[str, Any]) -> CheckResult:
        """Execute the tool registration check."""
        try:
            logger.info("🔧 Starting tool registration check...")

            # Import required modules
            from agents.tool_registry import ToolRegistry, get_tool_registry
            from core.registry_manager import RegistryManager, get_registry_manager

            # Test 1: Tool registry initialization
            logger.info("🔧 Testing tool registry initialization...")
            tool_registry = get_tool_registry()
            if not isinstance(tool_registry, ToolRegistry):
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="Tool registry initialization failed - wrong type returned"
                )

            # Test 2: Tool discovery
            logger.info("🔧 Testing tool discovery...")
            src_path = context.get('src_path', 'src')
            tool_registry.auto_discover_tools(src_path)

            # Test 3: Check if tools were discovered
            tool_stats = tool_registry.get_tool_statistics()
            total_tools = tool_stats.get('total_tools', 0)
            enabled_tools = tool_stats.get('enabled_tools', 0)

            logger.info(f"🔧 Tool discovery results: {total_tools} total tools, {enabled_tools} enabled")

            if total_tools == 0:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"No tools discovered from {src_path}. This indicates a critical issue with tool registration."
                )

            # Test 4: Check registry manager integration
            logger.info("🔧 Testing registry manager integration...")
            registry_manager = get_registry_manager()
            if not isinstance(registry_manager, RegistryManager):
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="Registry manager initialization failed - wrong type returned"
                )

            # Test 5: Check if tools are available for agents
            logger.info("🔧 Testing agent tool availability...")
            from config.agents import get_enabled_agent_configs

            agent_configs = get_enabled_agent_configs()
            agents_without_tools = []

            for agent_role, config in agent_configs.items():
                if not config.enabled:
                    continue

                # Get tools for this agent
                tools_for_agent = tool_registry.get_tools_for_agent(agent_role.value)
                if not tools_for_agent:
                    agents_without_tools.append(agent_role.value)

            if agents_without_tools:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message=f"Agents without tools: {', '.join(agents_without_tools)}. This will cause agent execution failures."
                )

            # Test 6: Check tool discovery from specific paths
            logger.info("🔧 Testing tool discovery from feature paths...")
            features_with_tools = tool_stats.get('features_with_tools', [])
            if not features_with_tools:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="No features with tools discovered. Check tool discovery paths and tool decorators."
                )

            logger.info(f"✅ Tool registration check passed: {total_tools} tools discovered across {len(features_with_tools)} features")

            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.PASSED,
                message=f"Tool registration successful: {total_tools} tools discovered, {enabled_tools} enabled, {len(features_with_tools)} features with tools"
            )

        except ImportError as e:
            logger.error(f"❌ Tool registration check failed due to import error: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Import error during tool registration check: {e!s}"
            )
        except Exception as e:
            logger.error(f"❌ Tool registration check failed: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Tool registration check failed: {e!s}"
            )
