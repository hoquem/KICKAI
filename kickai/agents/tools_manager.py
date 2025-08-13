#!/usr/bin/env python3
"""
Agent Tools Manager

This module provides the AgentToolsManager class for managing tool assignment
for agents with entity-specific validation.
"""

from functools import wraps
from typing import Any, Dict, Optional

from loguru import logger

# Removed entity_specific_agents dependency for simplified 5-agent architecture
from typing import Optional
from kickai.config.agents import get_agent_config
from kickai.core.enums import AgentRole


def log_errors(func):
    """Decorator to log errors in tool management."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise

    return wrapper


class AgentToolsManager:
    """Manages tool assignment for agents with entity-specific validation."""

    def __init__(self, tool_registry):
        self._tool_registry = tool_registry
        # Simplified initialization without entity-specific validation
        logger.info("🔧 AgentToolsManager initialized for 5-agent architecture")

    @log_errors
    def get_tools_for_role(
        self, role: AgentRole, entity_type: Optional[str] = None
    ) -> list[Any]:
        """Get tools for a specific role with entity-specific filtering."""
        try:
            # Use default context for tool configuration
            context = {
                "team_name": "KICKAI",
                "team_id": "KAI",
                "chat_type": "main",
                "user_role": "public",
                "username": "user"
            }
            config = get_agent_config(role, context)
            if not config:
                logger.warning(f"No configuration found for role {role}")
                return []

            # Get tools based on agent-specific configuration
            tools = []
            for tool_name in config.tools:
                # Try to get tool by name from registry
                tool_func = self._tool_registry.get_tool_function(tool_name)
                if tool_func:
                    tools.append(tool_func)
                    logger.info(f"[AGENT TOOLS] ✅ Found tool '{tool_name}' for {role.value}")
                else:
                    # Try alternative approaches if direct lookup fails
                    logger.warning(f"[AGENT TOOLS] ❌ Tool '{tool_name}' not found directly, trying alternatives...")
                    
                    # Try getting all tools and finding by name
                    all_tools = self._tool_registry.list_all_tools()
                    found_tool = None
                    for tool in all_tools:
                        if tool.name == tool_name:
                            found_tool = tool
                            break
                    
                    if found_tool:
                        tools.append(found_tool)
                        logger.info(f"[AGENT TOOLS] ✅ Found tool '{tool_name}' via search for {role.value}")
                    else:
                        logger.error(f"[AGENT TOOLS] ❌ Tool '{tool_name}' not found for {role.value}")

            logger.info(f"🔧 Loading {len(tools)} tools for {role.value}")
            return tools

        except Exception as e:
            logger.error(f"Error getting tools for agent {role}: {e}")
            return []

    def get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        return self._tool_registry.get_tool_names()

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        tool = self._tool_registry.get_tool(tool_name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "type": tool.tool_type.value if hasattr(tool, 'tool_type') else "unknown",
                "category": tool.category.value if hasattr(tool, 'category') else "unknown",
                "feature": tool.feature_module if hasattr(tool, 'feature_module') else "unknown",
            }
        return None
