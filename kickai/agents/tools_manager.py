#!/usr/bin/env python3
"""
Agent Tools Manager

This module provides the AgentToolsManager class for managing tool assignment
for agents with entity-specific validation.
"""

import logging
from functools import wraps
from typing import Any, Dict, List, Optional

from loguru import logger

from kickai.agents.entity_specific_agents import (
    EntitySpecificAgentManager,
    EntityType,
)
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
        self._entity_manager = EntitySpecificAgentManager(tool_registry)

        logger.info("🔧 AgentToolsManager initialized with entity-specific validation")

    @log_errors
    def get_tools_for_role(
        self, role: AgentRole, entity_type: Optional[EntityType] = None
    ) -> List[Any]:
        """Get tools for a specific role with entity-specific filtering."""
        try:
            config = get_agent_config(role)
            if not config:
                logger.warning(f"No configuration found for role {role}")
                return []

            # Get tools based on agent-specific configuration
            tools = []
            for tool_name in config.tools:
                # Validate tool access for this agent and entity type
                if entity_type and not self._entity_manager.validate_agent_tool_combination(
                    role, tool_name, {}
                ):
                    logger.warning(
                        f"⚠️ Tool '{tool_name}' not accessible for {role.value} with entity type {entity_type.value}"
                    )
                    continue

                tool_func = self._tool_registry.get_tool_function(tool_name)
                if tool_func:
                    tools.append(tool_func)
                    logger.info(f"[AGENT TOOLS] ✅ Found tool '{tool_name}' for {role.value}")
                else:
                    logger.warning(
                        f"[AGENT TOOLS] ❌ Tool '{tool_name}' not found for {role.value}"
                    )

            logger.info(f"🔧 Loading {len(tools)} tools for {role.value}")
            return tools

        except Exception as e:
            logger.error(f"Error getting tools for agent {role}: {e}")
            return []

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return self._tool_registry.get_tool_names()

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        tool = self._tool_registry.get_tool(tool_name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "type": tool.tool_type.value,
                "category": tool.category.value,
                "feature": tool.feature_module,
                "entity_types": [et.value for et in tool.entity_types],
            }
        return None 