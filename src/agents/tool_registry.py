"""
Tool Registry for KICKAI System

This module provides a centralized registry for all CrewAI tools used in the system.
"""

import logging
from typing import Dict, List, Any

# Import all tool modules to ensure they are loaded and registered
from features.communication.domain.tools import communication_tools
from features.communication.domain.tools import telegram_tools
from features.system_infrastructure.domain.tools import logging_tools
from features.system_infrastructure.domain.tools import firebase_tools
from features.team_administration.domain.tools import team_management_tools
from features.player_registration.domain.tools import registration_tools
from features.player_registration.domain.tools import player_tools
from features.shared.application.commands import help_commands

logger = logging.getLogger(__name__)

# Global tool registry - maps tool names to tool objects
GLOBAL_TOOL_REGISTRY: Dict[str, Any] = {}

def _build_tool_registry() -> Dict[str, Any]:
    """
    Build the global tool registry by collecting all tools from imported modules.
    
    Returns:
        Dictionary mapping tool names to tool objects
    """
    registry = {}
    
    # Import all tools from the modules
    tool_modules = [
        communication_tools,
        telegram_tools,
        logging_tools,
        firebase_tools,
        team_management_tools,
        registration_tools,
        player_tools,
        help_commands
    ]
    
    for module in tool_modules:
        # Get all functions decorated with @tool from the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Check if it's a CrewAI tool (has name attribute)
            if hasattr(attr, 'name') and hasattr(attr, 'description'):
                tool_name = attr.name
                registry[tool_name] = attr
                logger.info(f"🔧 Registered tool: {tool_name}")
    
    logger.info(f"✅ Tool registry built with {len(registry)} tools")
    return registry

# Build the registry when the module is imported
GLOBAL_TOOL_REGISTRY = _build_tool_registry()

def get_tool(tool_name: str) -> Any:
    """
    Get a tool by name from the registry.
    
    Args:
        tool_name: The name of the tool to retrieve
        
    Returns:
        The tool object or None if not found
    """
    return GLOBAL_TOOL_REGISTRY.get(tool_name)

def get_tool_names() -> List[str]:
    """
    Get a list of all registered tool names.
    
    Returns:
        List of tool names
    """
    return list(GLOBAL_TOOL_REGISTRY.keys())

def get_tools_for_roles(role_tool_names: List[str]) -> List[Any]:
    """
    Get tools for specific roles.
    
    Args:
        role_tool_names: List of tool names for the role
        
    Returns:
        List of tool objects
    """
    tools = []
    
    for tool_name in role_tool_names:
        tool_obj = get_tool(tool_name)
        if tool_obj:
            tools.append(tool_obj)
            logger.info(f"✅ Found tool '{tool_name}' for role")
        else:
            logger.warning(f"❌ Tool '{tool_name}' not found in registry")
    
    return tools

def get_all_tools() -> List[Any]:
    """
    Get all registered tools.
    
    Returns:
        List of all tool objects
    """
    return list(GLOBAL_TOOL_REGISTRY.values()) 