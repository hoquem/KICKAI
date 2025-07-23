#!/usr/bin/env python3
"""
Tool Registry for KICKAI System

This module provides a centralized registry for all CrewAI tools used in the system.
It follows the single source of truth principle and clean architecture patterns.
"""

import logging
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path

from loguru import logger
from core.entity_types import EntityType


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
    dependencies: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    feature_module: str = "unknown"
    tags: List[str] = field(default_factory=list)
    tool_function: Optional[Callable] = None
    entity_types: List[EntityType] = field(default_factory=lambda: [EntityType.NEITHER])
    access_control: Dict[str, List[str]] = field(default_factory=dict)  # agent_role -> allowed_entity_types


class ToolFactory(ABC):
    """Abstract base class for tool factories."""
    
    @abstractmethod
    def create_tool(self, **kwargs) -> Any:
        """Create a tool instance."""
        pass
    
    @abstractmethod
    def get_tool_info(self) -> Dict[str, Any]:
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
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}
        self._factories: Dict[str, ToolFactory] = {}
        self._tool_aliases: Dict[str, str] = {}
        self._feature_tools: Dict[str, List[str]] = {}
        self._entity_tools: Dict[EntityType, List[str]] = {entity_type: [] for entity_type in EntityType}
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
        dependencies: Optional[List[str]] = None,
        required_permissions: Optional[List[str]] = None,
        tool_function: Optional[Callable] = None,
        feature_module: str = "unknown",
        tags: Optional[List[str]] = None,
        aliases: Optional[List[str]] = None,
        entity_types: Optional[List[EntityType]] = None,
        access_control: Optional[Dict[str, List[str]]] = None
    ) -> None:
        """Register a tool with the registry."""
        try:
            # Create tool metadata
            metadata = ToolMetadata(
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
                access_control=access_control or {}
            )
            
            # Register the tool
            self._tools[tool_id] = metadata
            
            # Register aliases
            if aliases:
                for alias in aliases:
                    self._tool_aliases[alias] = tool_id
            
            # Register with feature
            if feature_module not in self._feature_tools:
                self._feature_tools[feature_module] = []
            self._feature_tools[feature_module].append(tool_id)
            
            # Register with entity types
            for entity_type in metadata.entity_types:
                if entity_type not in self._entity_tools:
                    self._entity_tools[entity_type] = []
                self._entity_tools[entity_type].append(tool_id)
            
            logger.info(f"🔧 Registered tool: {tool_id} (entity_types: {[et.value for et in entity_types or [EntityType.NEITHER]]})")
            
        except Exception as e:
            logger.error(f"❌ Failed to register tool {tool_id}: {e}")
            raise
    
    def register_factory(self, tool_id: str, factory: ToolFactory) -> None:
        """Register a tool factory."""
        self._factories[tool_id] = factory
        logger.info(f"🔧 Registered factory for tool: {tool_id}")
    
    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID."""
        # Check direct match
        if tool_id in self._tools:
            return self._tools[tool_id]
        
        # Check aliases
        if tool_id in self._tool_aliases:
            actual_id = self._tool_aliases[tool_id]
            return self._tools.get(actual_id)
        
        return None
    
    def get_tool_function(self, tool_id: str) -> Optional[Callable]:
        """Get tool function by ID."""
        tool = self.get_tool(tool_id)
        return tool.tool_function if tool else None
    
    def get_factory(self, tool_id: str) -> Optional[ToolFactory]:
        """Get tool factory by ID."""
        return self._factories.get(tool_id)
    
    def create_tool(self, tool_id: str, **kwargs) -> Any:
        """Create a tool instance using its factory."""
        factory = self.get_factory(tool_id)
        if factory:
            return factory.create_tool(**kwargs)
        else:
            logger.warning(f"No factory found for tool: {tool_id}")
            return None
    
    def get_tools_by_feature(self, feature_module: str) -> List[ToolMetadata]:
        """Get all tools for a specific feature module."""
        tool_ids = self._feature_tools.get(feature_module, [])
        return [self._tools[tool_id] for tool_id in tool_ids if tool_id in self._tools]
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[ToolMetadata]:
        """Get all tools of a specific type."""
        return [tool for tool in self._tools.values() if tool.tool_type == tool_type]
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """Get all tools of a specific category."""
        return [tool for tool in self._tools.values() if tool.category == category]
    
    def get_tools_by_entity_type(self, entity_type: EntityType) -> List[ToolMetadata]:
        """Get all tools that operate on a specific entity type."""
        tool_ids = self._entity_tools.get(entity_type, [])
        return [self._tools[tool_id] for tool_id in tool_ids if tool_id in self._tools]
    
    def get_enabled_tools(self) -> List[ToolMetadata]:
        """Get all enabled tools."""
        return [tool for tool in self._tools.values() if tool.enabled]
    
    def get_tools_with_permission(self, permission: str) -> List[ToolMetadata]:
        """Get all tools that require a specific permission."""
        return [tool for tool in self._tools.values() if permission in tool.required_permissions]
    
    def get_tools_for_agent(self, agent_role: str, entity_type: Optional[EntityType] = None) -> List[ToolMetadata]:
        """Get tools available for a specific agent role and entity type."""
        available_tools = []
        
        for tool in self._tools.values():
            if not tool.enabled:
                continue
            
            # Check if agent has access to this tool
            if agent_role in tool.access_control:
                allowed_entity_types = tool.access_control[agent_role]
                if entity_type is None or entity_type.value in allowed_entity_types:
                    available_tools.append(tool)
            else:
                # If no access control specified, allow access
                available_tools.append(tool)
        
        return available_tools
    
    def validate_tool_access(self, tool_id: str, agent_role: str, entity_type: Optional[EntityType] = None) -> bool:
        """Validate if an agent can access a specific tool for a given entity type."""
        tool = self.get_tool(tool_id)
        if not tool or not tool.enabled:
            return False
        
        # Check access control
        if agent_role in tool.access_control:
            allowed_entity_types = tool.access_control[agent_role]
            if entity_type is None or entity_type.value in allowed_entity_types:
                return True
            return False
        
        # If no access control specified, allow access
        return True
    
    def auto_discover_tools(self, src_path: str = "src") -> None:
        """
        Automatically discover and register tools from feature modules.
        
        This method scans the features directory and looks for tool definitions
        in the domain/tools directories. This is the ONLY mechanism for tool registration.
        """
        if self._discovered:
            logger.info("Tools already discovered, skipping auto-discovery")
            return
        
        logger.info("🔍 Starting automatic tool discovery...")
        
        src_path = Path(src_path)
        features_path = src_path / "features"
        
        if not features_path.exists():
            logger.warning(f"Features path not found: {features_path}")
            return
        
        discovered_count = 0
        
        for feature_dir in features_path.iterdir():
            if not feature_dir.is_dir() or feature_dir.name.startswith('_'):
                continue
            
            feature_name = feature_dir.name
            tools_path = feature_dir / "domain" / "tools"
            
            if not tools_path.exists():
                continue
            
            logger.info(f"🔍 Discovering tools for feature: {feature_name}")
            count = self._discover_tools_from_path(tools_path, feature_name)
            discovered_count += count
        
        self._discovered = True
        logger.info(f"✅ Auto-discovery complete. Registered {discovered_count} tools from {len(self._feature_tools)} features")
    
    def _discover_tools_from_path(self, tools_path: Path, feature_name: str) -> int:
        """Discover tools from a specific path. Returns count of discovered tools."""
        discovered_count = 0
        
        for py_file in tools_path.glob("*.py"):
            if py_file.name.startswith('_') or py_file.name == "__init__.py":
                continue
            
            try:
                count = self._discover_tools_from_file(py_file, feature_name)
                discovered_count += count
            except Exception as e:
                logger.error(f"Error discovering tools from {py_file}: {e}")
        
        return discovered_count
    
    def _discover_tools_from_file(self, file_path: Path, feature_name: str) -> int:
        """Discover tools from a specific file. Returns count of discovered tools."""
        import importlib.util
        import sys
        import os
        
        # Set PYTHONPATH to include src directory
        src_path = file_path.parent.parent.parent.parent  # Go up to src directory
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Also set PYTHONPATH environment variable
        current_pythonpath = os.environ.get('PYTHONPATH', '')
        if str(src_path) not in current_pythonpath:
            new_pythonpath = f"{src_path}:{current_pythonpath}" if current_pythonpath else str(src_path)
            os.environ['PYTHONPATH'] = new_pythonpath
        
        spec = importlib.util.spec_from_file_location(feature_name, file_path)
        if not spec or not spec.loader:
            return 0
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        discovered_count = 0
        
        # Look for tool functions in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Check if it's a CrewAI tool (has name and description attributes)
            if hasattr(attr, 'name') and hasattr(attr, 'description'):
                # Register the tool properly using the metadata system
                self._register_discovered_tool(attr, feature_name, file_path)
                discovered_count += 1
                logger.debug(f"🔧 Discovered tool: {attr.name} from {feature_name}")
        
        return discovered_count
    
    def _register_discovered_tool(self, tool_func: Callable, feature_name: str, file_path: Path) -> None:
        """Register a discovered tool."""
        tool_id = tool_func.name
        
        # Determine tool type based on function name
        tool_type = self._determine_tool_type(tool_func.name)
        category = self._determine_tool_category(feature_name)
        
        # Determine entity types based on function name
        entity_types = self._determine_entity_types(tool_func.name)
        
        # Determine access control based on function name
        access_control = self._determine_access_control(tool_func.name)
        
        self.register_tool(
            tool_id=tool_id,
            tool_type=tool_type,
            category=category,
            name=tool_func.name,
            description=tool_func.description,
            feature_module=feature_name,
            tool_function=tool_func,
            entity_types=entity_types,
            access_control=access_control
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
    
    def _determine_entity_types(self, tool_name: str) -> List[EntityType]:
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
    
    def _determine_access_control(self, tool_name: str) -> Dict[str, List[str]]:
        """Determine access control based on tool name."""
        tool_lower = tool_name.lower()
        
        # Default access control
        access_control: Dict[str, List[str]] = {}
        
        if any(keyword in tool_lower for keyword in ['admin', 'manage', 'control']):
            access_control['admin'] = ['both'] # Admins can access everything
        elif any(keyword in tool_lower for keyword in ['player', 'register', 'approve', 'remove']):
            access_control['player'] = ['player']
        elif any(keyword in tool_lower for keyword in ['team', 'member', 'admin', 'remove']):
            access_control['team_member'] = ['team_member']
        elif any(keyword in tool_lower for keyword in ['both', 'both_players', 'both_members']):
            access_control['both'] = ['both']
        
        return access_control
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about registered tools."""
        total_tools = len(self._tools)
        total_aliases = len(self._tool_aliases)
        
        tools_by_type = {}
        for tool_type in ToolType:
            tools_by_type[tool_type.value] = len(self.get_tools_by_type(tool_type))
        
        tools_by_category = {}
        for category in ToolCategory:
            tools_by_category[category.value] = len(self.get_tools_by_category(category))
        
        tools_by_feature = {}
        for feature in self._feature_tools:
            tools_by_feature[feature] = len(self._feature_tools[feature])
        
        tools_by_entity_type = {}
        for entity_type in EntityType:
            tools_by_entity_type[entity_type.value] = len(self.get_tools_by_entity_type(entity_type))
        
        # Count enabled tools
        enabled_tools = len(self.get_enabled_tools())
        
        # Get features with tools
        features_with_tools = list(self._feature_tools.keys())
        
        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_tools,
            "total_aliases": total_aliases,
            "tools_by_type": tools_by_type,
            "tools_by_category": tools_by_category,
            "tools_by_feature": tools_by_feature,
            "tools_by_entity_type": tools_by_entity_type,
            "features": features_with_tools,
            "features_with_tools": features_with_tools,
            "discovered": self._discovered
        }
    
    def list_all_tools(self) -> List[ToolMetadata]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def search_tools(self, query: str) -> List[ToolMetadata]:
        """Search tools by name, description, or feature."""
        query_lower = query.lower()
        results = []
        
        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower() or
                query_lower in tool.feature_module.lower() or
                any(query_lower in tag.lower() for tag in tool.tags)):
                results.append(tool)
        
        return results
    
    def get_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def get_tool_functions(self) -> Dict[str, Callable]:
        """Get dictionary of tool ID to function mapping."""
        return {
            tool_id: tool.tool_function
            for tool_id, tool in self._tools.items()
            if tool.tool_function
        }


# Global tool registry instance
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def get_tool(tool_name: str) -> Optional[Callable]:
    """Get a tool function by name from the registry."""
    registry = get_tool_registry()
    if not registry._discovered:
        registry.auto_discover_tools()
    return registry.get_tool_function(tool_name)


def get_tool_names() -> List[str]:
    """Get a list of all registered tool names."""
    registry = get_tool_registry()
    if not registry._discovered:
        registry.auto_discover_tools()
    return registry.get_tool_names()


def get_all_tools() -> List[Callable]:
    """Get all tool functions from the registry."""
    registry = get_tool_registry()
    if not registry._discovered:
        registry.auto_discover_tools()
    return list(registry.get_tool_functions().values()) 