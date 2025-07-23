#!/usr/bin/env python3
"""
Tool Registry for KICKAI System

This module provides a centralized registry for all CrewAI tools used in the system.
It follows the single source of truth principle and clean architecture patterns.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import re
import json

from crewai.tools import BaseTool
from loguru import logger

from core.entity_types import EntityType
from core.context_types import StandardizedContext


class ToolType(Enum):
    """Types of tools supported by the system."""
    COMMUNICATION = "communication"
    PLAYER_MANAGEMENT = "player_management"
    TEAM_MANAGEMENT = "team_management"
    PAYMENT = "payment"
    LOGGING = "logging"
    FIREBASE = "firebase"
    HELP = "help"
    SYSTEM = "system"
    CUSTOM = "custom"


class ToolCategory(Enum):
    """Categories of tools for organization."""
    CORE = "core"
    FEATURE = "feature"
    UTILITY = "utility"
    CUSTOM = "custom"


@dataclass
class ToolMetadata:
    """Metadata for tool registration."""
    tool_id: str
    tool_type: ToolType
    category: ToolCategory
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True
    dependencies: list[str] = field(default_factory=list)
    required_permissions: list[str] = field(default_factory=list)
    feature_module: str = "unknown"
    tags: list[str] = field(default_factory=list)
    tool_function: Callable | None = None
    entity_types: list[EntityType] = field(default_factory=lambda: [EntityType.NEITHER])
    access_control: dict[str, list[str]] = field(default_factory=dict)  # agent_role -> allowed_entity_types
    requires_context: bool = False  # Whether the tool requires context parameter


class ContextAwareToolWrapper(BaseTool):
    """Wrapper for tools that need context but are called without parameters."""
    
    # Define Pydantic model fields
    original_tool: Any  # Changed from Callable to Any to handle CrewAI Tool objects
    tool_name: str
    
    def __init__(self, original_tool: Any, tool_name: str):
        # Initialize BaseTool with required attributes
        super().__init__(
            name=tool_name,
            description=getattr(original_tool, 'description', f'Context-aware wrapper for {tool_name}'),
            func=self._run,
            original_tool=original_tool,
            tool_name=tool_name
        )
        
        # Copy all attributes from the original tool to make it compatible with CrewAI
        for attr_name in dir(original_tool):
            if not attr_name.startswith('_') and not hasattr(self, attr_name):
                try:
                    setattr(self, attr_name, getattr(original_tool, attr_name))
                except Exception:
                    pass
        
    def _run(self, *args, **kwargs):
        """Extract context from task description and call the original tool."""
        try:
            # Check if we have a context argument (either as first arg or in kwargs)
            context = None
            if args and isinstance(args[0], dict):
                context = args[0]
                args = args[1:]  # Remove context from args
            elif 'context' in kwargs:
                context = kwargs.pop('context')
            
            # If no context provided, try to extract from task description
            if not context:
                logger.info(f"🔧 ContextAwareToolWrapper: No context provided for {self.tool_name}, attempting to extract from task")
                context = self._extract_context_from_task()
            else:
                logger.info(f"🔧 ContextAwareToolWrapper: Using provided context for {self.tool_name}: {context}")
            
            # Handle CrewAI Tool objects vs regular callables
            if hasattr(self.original_tool, '_run'):
                # It's a CrewAI Tool object
                return self.original_tool._run(context, *args, **kwargs)
            else:
                # It's a regular callable
                return self.original_tool(context, *args, **kwargs)
                
        except Exception as e:
            logger.error(f"❌ ContextAwareToolWrapper: Error calling {self.tool_name}: {e}")
            return f"❌ Error executing {self.tool_name}: {e!s}"
    
    def _extract_context_from_task(self) -> dict:
        """Extract context from the current task description."""
        try:
            # This method is deprecated - context should be passed explicitly to tools
            # For now, return a clear error message to indicate the issue
            logger.error(f"❌ ContextAwareToolWrapper: Tool {self.tool_name} called without explicit context")
            logger.error(f"❌ ContextAwareToolWrapper: This indicates a system configuration issue")
            
            # Return a context that clearly indicates the problem
            context = {
                'user_id': 'CONTEXT_NOT_PROVIDED',
                'team_id': 'CONTEXT_NOT_PROVIDED',
                'chat_type': 'unknown',
                'is_registered': False,
                'is_player': False,
                'is_team_member': False,
                'username': '',
                'telegram_name': '',
                'message_text': '',
                'chat_id': 'unknown'
            }
            
            return context
            
        except Exception as e:
            logger.error(f"❌ ContextAwareToolWrapper: Error in deprecated context extraction: {e}")
            return self._get_fallback_context()


class ToolFactory(ABC):
    """Abstract base class for tool factories."""

    @abstractmethod
    def create_tool(self, **kwargs) -> Any:
        """Create a tool instance."""
        pass

    @abstractmethod
    def get_tool_info(self) -> dict[str, Any]:
        """Get information about the tool this factory creates."""
        pass


class ToolRegistry:
    """
    Centralized tool registry for the KICKAI system.
    
    This registry provides:
    - Fully automatic tool discovery from feature modules
    - Single source of truth for all tools
    - Factory pattern for tool creation
    - Dependency management
    - Permission-based access control
    - Feature-based organization
    - Entity-specific access control
    - Context-aware tool wrapping
    """

    def __init__(self):
        self._tools: dict[str, ToolMetadata] = {}
        self._factories: dict[str, ToolFactory] = {}
        self._tool_aliases: dict[str, str] = {}
        self._feature_tools: dict[str, list[str]] = {}
        self._entity_tools: dict[EntityType, list[str]] = {entity_type: [] for entity_type in EntityType}
        self._discovered = False

        logger.info("🔧 ToolRegistry initialized")

    def register_tool(
        self,
        tool_id: str,
        tool_type: ToolType,
        category: ToolCategory,
        name: str,
        description: str,
        version: str = "1.0.0",
        enabled: bool = True,
        dependencies: list[str] | None = None,
        required_permissions: list[str] | None = None,
        tool_function: Callable | None = None,
        feature_module: str = "unknown",
        tags: list[str] | None = None,
        aliases: list[str] | None = None,
        entity_types: list[EntityType] | None = None,
        access_control: dict[str, list[str]] | None = None,
        requires_context: bool = False
    ) -> None:
        """Register a tool with the registry."""
        try:
            # Note: Tools that require context should be modified to extract context from task description
            # instead of requiring context parameters. This is more compatible with CrewAI.
            if requires_context:
                logger.info(f"⚠️ Tool {tool_id} requires context but should be modified to extract context from task description")
            
            tool_metadata = ToolMetadata(
                tool_id=tool_id,
                tool_type=tool_type,
                category=category,
                name=name,
                description=description,
                version=version,
                enabled=enabled,
                dependencies=dependencies or [],
                required_permissions=required_permissions or [],
                tool_function=tool_function,
                feature_module=feature_module,
                tags=tags or [],
                entity_types=entity_types or [EntityType.NEITHER],
                access_control=access_control or {},
                requires_context=requires_context
            )

            self._tools[tool_id] = tool_metadata

            # Register aliases
            if aliases:
                for alias in aliases:
                    self._tool_aliases[alias] = tool_id

            # Update feature tools mapping
            if feature_module not in self._feature_tools:
                self._feature_tools[feature_module] = []
            self._feature_tools[feature_module].append(tool_id)

            # Update entity tools mapping
            for entity_type in tool_metadata.entity_types:
                self._entity_tools[entity_type].append(tool_id)

            logger.info(f"✅ Registered tool: {tool_id} ({tool_type.value})")

        except Exception as e:
            logger.error(f"❌ Failed to register tool {tool_id}: {e}")

    def register_factory(self, tool_id: str, factory: ToolFactory) -> None:
        """Register a tool factory."""
        self._factories[tool_id] = factory
        logger.info(f"✅ Registered factory for tool: {tool_id}")

    def get_tool(self, tool_id: str) -> ToolMetadata | None:
        """Get tool metadata by ID."""
        # Check direct match first
        if tool_id in self._tools:
            return self._tools[tool_id]
        
        # Check aliases
        if tool_id in self._tool_aliases:
            alias_target = self._tool_aliases[tool_id]
            return self._tools.get(alias_target)
        
        return None

    def get_tool_function(self, tool_id: str) -> Callable | None:
        """Get the actual tool function by ID."""
        tool_metadata = self.get_tool(tool_id)
        return tool_metadata.tool_function if tool_metadata else None

    def get_factory(self, tool_id: str) -> ToolFactory | None:
        """Get tool factory by ID."""
        return self._factories.get(tool_id)

    def create_tool(self, tool_id: str, **kwargs) -> Any:
        """Create a tool instance using its factory."""
        factory = self.get_factory(tool_id)
        if factory:
            return factory.create_tool(**kwargs)
        else:
            logger.error(f"❌ No factory found for tool: {tool_id}")
            return None

    def get_tools_by_feature(self, feature_module: str) -> list[ToolMetadata]:
        """Get all tools for a specific feature module."""
        tool_ids = self._feature_tools.get(feature_module, [])
        return [self._tools[tool_id] for tool_id in tool_ids if tool_id in self._tools]

    def get_tools_by_type(self, tool_type: ToolType) -> list[ToolMetadata]:
        """Get all tools of a specific type."""
        return [tool for tool in self._tools.values() if tool.tool_type == tool_type]

    def get_tools_by_category(self, category: ToolCategory) -> list[ToolMetadata]:
        """Get all tools of a specific category."""
        return [tool for tool in self._tools.values() if tool.category == category]

    def get_tools_by_entity_type(self, entity_type: EntityType) -> list[ToolMetadata]:
        """Get all tools for a specific entity type."""
        tool_ids = self._entity_tools.get(entity_type, [])
        return [self._tools[tool_id] for tool_id in tool_ids if tool_id in self._tools]

    def get_enabled_tools(self) -> list[ToolMetadata]:
        """Get all enabled tools."""
        return [tool for tool in self._tools.values() if tool.enabled]

    def get_tools_with_permission(self, permission: str) -> list[ToolMetadata]:
        """Get all tools that require a specific permission."""
        return [tool for tool in self._tools.values() if permission in tool.required_permissions]

    def get_tools_for_agent(self, agent_role: str, entity_type: EntityType | None = None) -> list[ToolMetadata]:
        """Get tools available for a specific agent role and entity type."""
        available_tools = []

        for tool in self._tools.values():
            if not tool.enabled:
                continue

            # Check if agent has access to this tool
            if self.validate_tool_access(tool.tool_id, agent_role, entity_type):
                available_tools.append(tool)

        return available_tools

    def validate_tool_access(self, tool_id: str, agent_role: str, entity_type: EntityType | None = None) -> bool:
        """Validate if an agent can access a specific tool."""
        tool = self.get_tool(tool_id)
        if not tool:
            return False

        # Check access control
        if tool.access_control:
            if agent_role in tool.access_control:
                allowed_entity_types = tool.access_control[agent_role]
                if entity_type:
                    return entity_type.value in allowed_entity_types
                else:
                    return True  # No entity type specified, assume access
            else:
                return False  # Agent role not in access control

        return True  # No access control specified, allow access

    def auto_discover_tools(self, src_path: str = "src") -> None:
        """Automatically discover and register tools from the source directory."""
        if self._discovered:
            logger.info("🔧 Tools already discovered, skipping auto-discovery")
            return

        logger.info(f"🔍 Auto-discovering tools from {src_path}")
        src_path_obj = Path(src_path)

        if not src_path_obj.exists():
            logger.warning(f"⚠️ Source path {src_path} does not exist")
            return

        total_discovered = 0

        # Discover tools from features directory
        features_path = src_path_obj / "features"
        if features_path.exists():
            for feature_dir in features_path.iterdir():
                if feature_dir.is_dir():
                    feature_name = feature_dir.name
                    tools_path = feature_dir / "domain" / "tools"
                    if tools_path.exists():
                        discovered_count = self._discover_tools_from_path(tools_path, feature_name)
                        total_discovered += discovered_count

        # Discover tools from shared directory
        shared_path = src_path_obj / "features" / "shared" / "domain" / "tools"
        if shared_path.exists():
            discovered_count = self._discover_tools_from_path(shared_path, "shared")
            total_discovered += discovered_count

        self._discovered = True
        logger.info(f"✅ Auto-discovery complete. Found {total_discovered} tools")

    def _discover_tools_from_path(self, tools_path: Path, feature_name: str) -> int:
        """Discover tools from a specific path."""
        discovered_count = 0

        for file_path in tools_path.glob("*.py"):
            if file_path.name.startswith("__"):
                continue

            discovered_count += self._discover_tools_from_file(file_path, feature_name)

        return discovered_count

    def _discover_tools_from_file(self, file_path: Path, feature_name: str) -> int:
        """Discover tools from a specific file."""
        discovered_count = 0

        try:
            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(feature_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for CrewAI tools (objects with 'name' attribute and proper tool structure)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Skip private attributes and built-in objects
                if attr_name.startswith('_'):
                    continue
                    
                # Skip logging objects and other non-tool objects
                if hasattr(attr, '__module__') and attr.__module__ == 'logging':
                    continue
                    
                # Check if this is a valid CrewAI tool
                if hasattr(attr, 'name') and hasattr(attr, 'description'):
                    # This is a CrewAI tool
                    tool_name = getattr(attr, 'name', attr_name)
                    
                    # Check if tool requires context by examining its signature
                    # For CrewAI tools, we need to check the underlying function
                    requires_context = False
                    if hasattr(attr, 'func'):
                        import inspect
                        try:
                            sig = inspect.signature(attr.func)
                            requires_context = any(
                                param.name == 'context' and (
                                    param.annotation == dict or 
                                    str(param.annotation).startswith('dict') or
                                    'dict' in str(param.annotation)
                                )
                                for param in sig.parameters.values()
                            )
                        except Exception as e:
                            logger.debug(f"Could not inspect signature for {tool_name}: {e}")
                    
                    logger.info(f"🔍 Discovered tool: {tool_name} (requires_context: {requires_context})")
                    
                    self._register_discovered_tool(attr, feature_name, file_path, requires_context)
                    discovered_count += 1

        except Exception as e:
            logger.error(f"❌ Error discovering tools from {file_path}: {e}")

        return discovered_count

    def _register_discovered_tool(self, tool_func: Callable, feature_name: str, file_path: Path, requires_context: bool = False) -> None:
        """Register a discovered tool."""
        tool_id = tool_func.name

        # Determine tool type based on function name
        tool_type = self._determine_tool_type(tool_func.name)
        category = self._determine_tool_category(feature_name)

        # Determine entity types based on function name
        entity_types = self._determine_entity_types(tool_func.name)

        # Determine access control based on function name
        access_control = self._determine_access_control(tool_func.name)

        # Get description safely
        description = getattr(tool_func, 'description', f"Tool: {tool_func.name}")
        
        self.register_tool(
            tool_id=tool_id,
            tool_type=tool_type,
            category=category,
            name=tool_func.name,
            description=description,
            feature_module=feature_name,
            tool_function=tool_func,
            entity_types=entity_types,
            access_control=access_control,
            requires_context=requires_context
        )

    def _determine_tool_type(self, tool_name: str) -> ToolType:
        """Determine tool type based on tool name."""
        tool_lower = tool_name.lower()

        if any(keyword in tool_lower for keyword in ['send', 'message', 'announce', 'poll']):
            return ToolType.COMMUNICATION
        elif any(keyword in tool_lower for keyword in ['player', 'register', 'approve']):
            return ToolType.PLAYER_MANAGEMENT
        elif any(keyword in tool_lower for keyword in ['team', 'member', 'admin']):
            return ToolType.TEAM_MANAGEMENT
        elif any(keyword in tool_lower for keyword in ['payment', 'finance', 'budget']):
            return ToolType.PAYMENT
        elif any(keyword in tool_lower for keyword in ['log', 'error']):
            return ToolType.LOGGING
        elif any(keyword in tool_lower for keyword in ['firebase', 'firestore']):
            return ToolType.FIREBASE
        elif any(keyword in tool_lower for keyword in ['help', 'format', 'available']):
            return ToolType.HELP
        elif any(keyword in tool_lower for keyword in ['system', 'health', 'config']):
            return ToolType.SYSTEM
        else:
            return ToolType.CUSTOM

    def _determine_tool_category(self, feature_name: str) -> ToolCategory:
        """Determine tool category based on feature name."""
        if feature_name in ['shared', 'core']:
            return ToolCategory.CORE
        elif feature_name in ['utils', 'helpers']:
            return ToolCategory.UTILITY
        else:
            return ToolCategory.FEATURE

    def _determine_entity_types(self, tool_name: str) -> list[EntityType]:
        """Determine entity types based on tool name."""
        tool_lower = tool_name.lower()

        if any(keyword in tool_lower for keyword in ['player', 'register', 'approve', 'remove']):
            return [EntityType.PLAYER]
        elif any(keyword in tool_lower for keyword in ['team', 'member', 'admin', 'remove']):
            return [EntityType.TEAM_MEMBER]
        elif any(keyword in tool_lower for keyword in ['both', 'both_players', 'both_members']):
            return [EntityType.BOTH]
        else:
            return [EntityType.NEITHER]

    def _determine_access_control(self, tool_name: str) -> dict[str, list[str]]:
        """Determine access control based on tool name."""
        tool_lower = tool_name.lower()

        # Default access control
        access_control: dict[str, list[str]] = {}

        if any(keyword in tool_lower for keyword in ['admin', 'manage', 'control']):
            access_control['admin'] = ['both'] # Admins can access everything
        elif any(keyword in tool_lower for keyword in ['player', 'register', 'approve', 'remove']):
            access_control['player'] = ['player']
        elif any(keyword in tool_lower for keyword in ['team', 'member', 'admin', 'remove']):
            access_control['team_member'] = ['team_member']
        elif any(keyword in tool_lower for keyword in ['both', 'both_players', 'both_members']):
            access_control['both'] = ['both']

        return access_control

    def get_tool_statistics(self) -> dict[str, Any]:
        """Get statistics about registered tools."""
        total_tools = len(self._tools)
        total_aliases = len(self._tool_aliases)

        tools_by_type = {}
        for tool_type in ToolType:
            tools_by_type[tool_type.value] = len(self.get_tools_by_type(tool_type))

        tools_by_category = {}
        for category in ToolCategory:
            tools_by_category[category.value] = len(self.get_tools_by_category(category))

        tools_by_entity = {}
        for entity_type in EntityType:
            tools_by_entity[entity_type.value] = len(self.get_tools_by_entity_type(entity_type))

        context_aware_tools = len([tool for tool in self._tools.values() if tool.requires_context])

        return {
            'total_tools': total_tools,
            'total_aliases': total_aliases,
            'tools_by_type': tools_by_type,
            'tools_by_category': tools_by_category,
            'tools_by_entity': tools_by_entity,
            'context_aware_tools': context_aware_tools,
            'features': list(self._feature_tools.keys()),
            'features_with_tools': list(self._feature_tools.keys()),  # Add this for backward compatibility
            'discovered': self._discovered
        }

    def list_all_tools(self) -> list[ToolMetadata]:
        """Get all registered tools."""
        return list(self._tools.values())

    def search_tools(self, query: str) -> list[ToolMetadata]:
        """Search tools by name or description."""
        query_lower = query.lower()
        results = []

        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower() or
                query_lower in tool.feature_module.lower()):
                results.append(tool)

        return results

    def get_tool_names(self) -> list[str]:
        """Get list of all tool names."""
        return list(self._tools.keys())

    def get_tool_functions(self) -> dict[str, Callable]:
        """Get dictionary of tool names to their functions."""
        return {
            tool_id: tool.tool_function 
            for tool_id, tool in self._tools.items() 
            if tool.tool_function is not None
        }

    def get_context_aware_tools(self) -> list[str]:
        """Get list of tools that require context."""
        return [tool_id for tool_id, tool in self._tools.items() if tool.requires_context]


# Global tool registry instance
_tool_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def get_tool(tool_name: str) -> Callable | None:
    """Get a tool function by name."""
    registry = get_tool_registry()
    return registry.get_tool_function(tool_name)


def get_tool_names() -> list[str]:
    """Get list of all available tool names."""
    registry = get_tool_registry()
    return registry.get_tool_names()


def get_all_tools() -> list[Callable]:
    """Get all available tool functions."""
    registry = get_tool_registry()
    return list(registry.get_tool_functions().values())
