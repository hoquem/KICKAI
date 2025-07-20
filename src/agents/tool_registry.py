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
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}
        self._factories: Dict[str, ToolFactory] = {}
        self._tool_aliases: Dict[str, str] = {}
        self._feature_tools: Dict[str, List[str]] = {}
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
        aliases: Optional[List[str]] = None
    ) -> None:
        """
        Register a tool with the registry.
        
        Args:
            tool_id: Unique identifier for the tool
            tool_type: Type of tool
            category: Category of tool
            name: Display name of the tool
            description: Description of the tool
            version: Tool version
            enabled: Whether the tool is enabled
            dependencies: List of tool dependencies
            required_permissions: Required permissions to use the tool
            tool_function: The actual tool function
            feature_module: Feature module this tool belongs to
            tags: Tags for categorization
            aliases: Alternative names
        """
        if tool_id in self._tools:
            logger.warning(f"Tool {tool_id} already registered, updating metadata")
        
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
            feature_module=feature_module,
            tags=tags or [],
            tool_function=tool_function
        )
        
        self._tools[tool_id] = metadata
        
        # Track feature tools
        if feature_module not in self._feature_tools:
            self._feature_tools[feature_module] = []
        self._feature_tools[feature_module].append(tool_id)
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self._tool_aliases[alias] = tool_id
        
        logger.debug(f"✅ Registered tool: {tool_id} ({feature_module})")
    
    def register_factory(self, tool_id: str, factory: ToolFactory) -> None:
        """Register a tool factory."""
        self._factories[tool_id] = factory
        logger.debug(f"✅ Registered factory for tool: {tool_id}")
    
    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID."""
        # Check direct match first
        if tool_id in self._tools:
            return self._tools[tool_id]
        
        # Check aliases
        if tool_id in self._tool_aliases:
            actual_id = self._tool_aliases[tool_id]
            return self._tools.get(actual_id)
        
        return None
    
    def get_tool_function(self, tool_id: str) -> Optional[Callable]:
        """Get the actual tool function by ID."""
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
        
        # Fallback to direct function if no factory
        tool_func = self.get_tool_function(tool_id)
        if tool_func:
            return tool_func
        
        raise ValueError(f"No factory or function found for tool: {tool_id}")
    
    def get_tools_by_feature(self, feature_module: str) -> List[ToolMetadata]:
        """Get all tools for a specific feature."""
        tool_ids = self._feature_tools.get(feature_module, [])
        return [self._tools[tool_id] for tool_id in tool_ids if tool_id in self._tools]
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[ToolMetadata]:
        """Get all tools of a specific type."""
        return [tool for tool in self._tools.values() if tool.tool_type == tool_type]
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """Get all tools in a specific category."""
        return [tool for tool in self._tools.values() if tool.category == category]
    
    def get_enabled_tools(self) -> List[ToolMetadata]:
        """Get all enabled tools."""
        return [tool for tool in self._tools.values() if tool.enabled]
    
    def get_tools_with_permission(self, permission: str) -> List[ToolMetadata]:
        """Get all tools that require a specific permission."""
        return [
            tool for tool in self._tools.values()
            if permission in tool.required_permissions
        ]
    
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
        
        self.register_tool(
            tool_id=tool_id,
            tool_type=tool_type,
            category=category,
            name=tool_func.name,
            description=tool_func.description,
            feature_module=feature_name,
            tool_function=tool_func
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
        
        return {
            "total_tools": total_tools,
            "total_aliases": total_aliases,
            "tools_by_type": tools_by_type,
            "tools_by_category": tools_by_category,
            "tools_by_feature": tools_by_feature,
            "features": list(self._feature_tools.keys()),
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