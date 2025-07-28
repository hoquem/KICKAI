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
from typing import Any, Dict, List, Optional, Union

# Minimal tool registry for compatibility
class Tool:
    pass
from loguru import logger

from kickai.core.entity_types import EntityType
from kickai.core.models.context_models import BaseContext, validate_context_data
from kickai.utils.context_validation import (
    ContextError,
    log_context_validation_failure,
    log_context_validation_success,
    validate_context_for_tool,
)


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
    access_control: Dict[str, List[str]] = field(
        default_factory=dict
    )  # agent_role -> allowed_entity_types
    requires_context: bool = False  # Whether the tool requires context parameter
    context_model: Optional[type[BaseContext]] = None  # Pydantic model for context validation


class ContextAwareTool(Tool):
    """Enhanced context-aware tool wrapper using Pydantic models."""

    def __init__(
        self, original_tool: Any, tool_name: str, context_model: Optional[type[BaseContext]] = None
    ):
        """Initialize context-aware tool wrapper."""

        # Initialize Tool with required attributes
        super().__init__(
            name=tool_name,
            description=getattr(
                original_tool, "description", f"Context-aware wrapper for {tool_name}"
            ),
            func=self._run,
            original_tool=original_tool,
            tool_name=tool_name,
            context_model=context_model,
        )

        # Copy all attributes from the original tool
        for attr_name in dir(original_tool):
            if not attr_name.startswith("_") and not hasattr(self, attr_name):
                try:
                    setattr(self, attr_name, getattr(original_tool, attr_name))
                except Exception:
                    pass

    def _run(self, *args, **kwargs):
        """Run the tool with validated context."""
        try:
            # Extract context from arguments
            context_data = self._extract_context_from_args(args, kwargs)

            # Validate context if model is provided
            if self.context_model and context_data:
                try:
                    validated_context = validate_context_for_tool(
                        context_data, self.context_model, self.tool_name
                    )
                    log_context_validation_success(self.tool_name, validated_context)
                    # Call original tool with validated context
                    return self.original_tool(validated_context)
                except ContextError as e:
                    log_context_validation_failure(self.tool_name, e)
                    return f"Error: {e.message}"

            # Fallback to original tool if no context model or no context data
            return self.original_tool(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error in context-aware tool {self.tool_name}: {e}")
            return f"Error: {e!s}"

    def _extract_context_from_args(self, args: tuple, kwargs: dict) -> Optional[Dict[str, Any]]:
        """Extract context data from tool arguments."""
        # With CrewAI's native approach, context is passed through task description
        # and the LLM decides which parameters to pass to tools
        # This method is kept for backward compatibility but simplified
        return None

    def _extract_context_from_task(self) -> Optional[Dict[str, Any]]:
        """Extract context from CrewAI task description."""
        # With CrewAI's native approach, context is included in task description
        # and the LLM extracts and passes relevant parameters to tools
        # This method is kept for backward compatibility but simplified
        return None


class ContextAwareToolWrapper(Tool):
    """Legacy wrapper for backward compatibility."""

    # Define Pydantic model fields
    original_tool: Any  # Changed from Callable to Any to handle CrewAI Tool objects
    tool_name: str

    def __init__(self, original_tool: Any, tool_name: str):
        # Initialize Tool with required attributes
        super().__init__(
            name=tool_name,
            description=getattr(
                original_tool, "description", f"Context-aware wrapper for {tool_name}"
            ),
            func=self._run,
            original_tool=original_tool,
            tool_name=tool_name,
        )

        # Copy all attributes from the original tool to make it compatible with CrewAI
        for attr_name in dir(original_tool):
            if not attr_name.startswith("_") and not hasattr(self, attr_name):
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
            elif "context" in kwargs:
                context = kwargs.pop("context")

            # If no context provided, try to extract from task description
            if not context:
                context = self._extract_context_from_task()

            # Call the original tool with context
            if context:
                return self.original_tool(context, *args, **kwargs)
            else:
                return self.original_tool(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error in context-aware wrapper for {self.tool_name}: {e}")
            return f"Error: {e!s}"

    def _extract_context_from_task(self) -> dict:
        """Extract context from task description."""
        # This is a simplified implementation
        # In a real implementation, you would parse the task description
        # to extract context information
        return {}


class ToolFactory(ABC):
    """Abstract base class for tool factories."""

    @abstractmethod
    def create_tool(self, **kwargs) -> Any:
        """Create a tool instance."""
        pass

    @abstractmethod
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about the tool."""
        pass


class ToolRegistry:
    """Enhanced tool registry with context support."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, ToolMetadata] = {}
        self._factories: Dict[str, ToolFactory] = {}
        self._context_aware_tools: set[str] = set()
        self._tool_aliases: Dict[str, str] = {}  # alias -> tool_id mapping
        self._feature_tools: Dict[str, List[str]] = {}  # feature_module -> list of tool_ids
        self._entity_tools: Dict[EntityType, List[str]] = {
            entity_type: [] for entity_type in EntityType
        }  # entity_type -> list of tool_ids
        self._discovered = False  # Track if tools have been auto-discovered
        logger.info("🔧 Tool Registry initialized")

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
        access_control: Optional[Dict[str, List[str]]] = None,
        requires_context: bool = False,
        context_model: Optional[type[BaseContext]] = None,
    ) -> None:
        """Register a tool with enhanced context support."""

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
            access_control=access_control or {},
            requires_context=requires_context,
            context_model=context_model,
        )

        # Register the tool
        self._tools[tool_id] = metadata

        # Track context-aware tools
        if requires_context or context_model:
            self._context_aware_tools.add(tool_id)

        # Register aliases if provided
        if aliases:
            for alias in aliases:
                self._tool_aliases[alias] = tool_id

        # Update feature tools mapping
        if feature_module not in self._feature_tools:
            self._feature_tools[feature_module] = []
        self._feature_tools[feature_module].append(tool_id)

        # Update entity tools mapping
        for entity_type in metadata.entity_types:
            if entity_type not in self._entity_tools:
                self._entity_tools[entity_type] = []
            if tool_id not in self._entity_tools[entity_type]:
                self._entity_tools[entity_type].append(tool_id)

        logger.info(
            f"✅ Registered tool: {tool_id} (context-aware: {requires_context or context_model is not None})"
        )

    def register_context_tool(
        self, tool_id: str, tool_function: Callable, context_model: type[BaseContext], **kwargs
    ) -> None:
        """Register a tool with specific context model."""

        # Determine tool type and category from function name
        tool_type = self._determine_tool_type(tool_id)
        category = self._determine_tool_category(kwargs.get("feature_module", "unknown"))

        self.register_tool(
            tool_id=tool_id,
            tool_type=tool_type,
            category=category,
            name=tool_id,
            description=kwargs.get("description", f"Context-aware tool: {tool_id}"),
            tool_function=tool_function,
            requires_context=True,
            context_model=context_model,
            **kwargs,
        )

    def create_context_aware_tool(self, tool_id: str, **kwargs) -> Any:
        """Create a context-aware tool instance."""
        metadata = self._tools.get(tool_id)
        if not metadata:
            raise ValueError(f"Tool not found: {tool_id}")

        if not metadata.tool_function:
            raise ValueError(f"Tool function not available: {tool_id}")

        # Create context-aware wrapper
        return ContextAwareTool(
            original_tool=metadata.tool_function,
            tool_name=tool_id,
            context_model=metadata.context_model,
        )

    def validate_tool_context(self, tool_id: str, context_data: Dict[str, Any]) -> bool:
        """Validate context data for a specific tool."""
        metadata = self._tools.get(tool_id)
        if not metadata or not metadata.context_model:
            return True  # No context model means no validation needed

        return validate_context_data(context_data, metadata.context_model.__name__.lower())

    def get_context_aware_tools(self) -> List[str]:
        """Get list of context-aware tools."""
        return list(self._context_aware_tools)

    def get_tools_by_context_type(self, context_type: str) -> List[ToolMetadata]:
        """Get tools that use a specific context type."""
        context_tools = []
        for metadata in self._tools.values():
            if (
                metadata.context_model
                and metadata.context_model.__name__.lower() == context_type.lower()
            ):
                context_tools.append(metadata)
        return context_tools

    def register_factory(self, tool_id: str, factory: ToolFactory) -> None:
        """Register a tool factory."""
        self._factories[tool_id] = factory
        logger.info(f"✅ Registered factory for tool: {tool_id}")

    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID."""
        # Check direct match first
        if tool_id in self._tools:
            return self._tools[tool_id]

        # Check aliases
        if tool_id in self._tool_aliases:
            alias_target = self._tool_aliases[tool_id]
            return self._tools.get(alias_target)

        return None

    def get_tool_function(self, tool_id: str) -> Optional[Callable]:
        """Get the actual tool function by ID."""
        tool_metadata = self.get_tool(tool_id)
        return tool_metadata.tool_function if tool_metadata else None

    def get_factory(self, tool_id: str) -> Optional[ToolFactory]:
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
        """Get all tools for a specific entity type."""
        tool_ids = self._entity_tools.get(entity_type, [])
        return [self._tools[tool_id] for tool_id in tool_ids if tool_id in self._tools]

    def get_enabled_tools(self) -> List[ToolMetadata]:
        """Get all enabled tools."""
        return [tool for tool in self._tools.values() if tool.enabled]

    def get_tools_with_permission(self, permission: str) -> List[ToolMetadata]:
        """Get all tools that require a specific permission."""
        return [tool for tool in self._tools.values() if permission in tool.required_permissions]

    def get_tools_for_agent(
        self, agent_role: str, entity_type: Optional[EntityType] = None
    ) -> List[ToolMetadata]:
        """Get tools available for a specific agent role and entity type."""
        available_tools = []

        for tool in self._tools.values():
            if not tool.enabled:
                continue

            # Check if agent has access to this tool
            if self.validate_tool_access(tool.tool_id, agent_role, entity_type):
                available_tools.append(tool)

        return available_tools

    def validate_tool_access(
        self, tool_id: str, agent_role: str, entity_type: Optional[EntityType] = None
    ) -> bool:
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

    def auto_discover_tools(self, src_path: str = "kickai") -> None:
        """Automatically discover and register tools from the source directory."""
        if self._discovered:
            logger.info("🔧 Tools already discovered, skipping auto-discovery")
            return

        logger.info(f"🔍 Auto-discovering tools from {src_path}")

        # First try entry points discovery
        entry_points_discovered = self._discover_from_entry_points()

        # Fallback to file system discovery
        file_discovered = self._discover_from_filesystem(src_path)

        total_discovered = entry_points_discovered + file_discovered

        self._discovered = True
        logger.info(
            f"✅ Auto-discovery complete. Found {total_discovered} tools ({entry_points_discovered} from entry points, {file_discovered} from filesystem)"
        )

    def _discover_from_entry_points(self) -> int:
        """Discover tools from setuptools entry points."""
        discovered_count = 0

        try:
            import pkg_resources

            for entry_point in pkg_resources.iter_entry_points("kickai.tools"):
                try:
                    tool = entry_point.load()
                    self.register_tool(
                        tool_id=entry_point.name,
                        tool_type=ToolType.CUSTOM,  # Default type
                        category=ToolCategory.FEATURE,
                        name=entry_point.name,
                        description=getattr(tool, "description", f"Tool: {entry_point.name}"),
                        tool_function=tool,
                        feature_module="entry_points",
                    )
                    discovered_count += 1
                    logger.info(f"✅ Discovered tool from entry points: {entry_point.name}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to load tool {entry_point.name} from entry points: {e}"
                    )
        except Exception as e:
            logger.warning(f"⚠️ Entry points discovery failed: {e}")

        return discovered_count

    def _discover_from_filesystem(self, src_path: str) -> int:
        """Discover tools from file system."""
        src_path_obj = Path(src_path)

        if not src_path_obj.exists():
            logger.warning(f"⚠️ Source path {src_path} does not exist")
            return 0

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

        return total_discovered

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
            # Import the module with proper context
            import importlib.util
            import sys
            from pathlib import Path

            # Add the parent directory to sys.path to ensure proper imports
            parent_dir = file_path.parent.parent.parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            spec = importlib.util.spec_from_file_location(feature_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for CrewAI tools (objects with 'name' attribute and proper tool structure)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Skip private attributes and built-in objects
                if attr_name.startswith("_"):
                    continue

                # Skip logging objects and other non-tool objects
                if hasattr(attr, "__module__") and attr.__module__ == "logging":
                    continue

                # Check if this is a valid CrewAI tool
                if hasattr(attr, "name") and hasattr(attr, "description"):
                    # This is a CrewAI tool
                    tool_name = getattr(attr, "name", attr_name)

                    # Check if tool requires context by examining its signature
                    # For CrewAI tools, we need to check the underlying function
                    requires_context = False
                    if hasattr(attr, "func"):
                        import inspect

                        try:
                            sig = inspect.signature(attr.func)
                            requires_context = any(
                                param.name == "context"
                                and (
                                    param.annotation == dict
                                    or str(param.annotation).startswith("dict")
                                    or "dict" in str(param.annotation)
                                )
                                for param in sig.parameters.values()
                            )
                        except Exception as e:
                            logger.debug(f"Could not inspect signature for {tool_name}: {e}")

                    logger.info(
                        f"🔍 Discovered tool: {tool_name} (requires_context: {requires_context})"
                    )

                    self._register_discovered_tool(attr, feature_name, file_path, requires_context)
                    discovered_count += 1

        except Exception as e:
            logger.error(f"❌ Error discovering tools from {file_path}: {e}")

        return discovered_count

    def _register_discovered_tool(
        self,
        tool_func: Callable,
        feature_name: str,
        file_path: Path,
        requires_context: bool = False,
    ) -> None:
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
        description = getattr(tool_func, "description", f"Tool: {tool_func.name}")

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
            requires_context=requires_context,
        )

    def _determine_tool_type(self, tool_name: str) -> ToolType:
        """Determine tool type based on tool name."""
        tool_lower = tool_name.lower()

        if any(keyword in tool_lower for keyword in ["send", "message", "announce", "poll"]):
            return ToolType.COMMUNICATION
        elif any(keyword in tool_lower for keyword in ["player", "register", "approve"]):
            return ToolType.PLAYER_MANAGEMENT
        elif any(keyword in tool_lower for keyword in ["team", "member", "admin"]):
            return ToolType.TEAM_MANAGEMENT
        elif any(keyword in tool_lower for keyword in ["payment", "finance", "budget"]):
            return ToolType.PAYMENT
        elif any(keyword in tool_lower for keyword in ["log", "error"]):
            return ToolType.LOGGING
        elif any(keyword in tool_lower for keyword in ["firebase", "firestore"]):
            return ToolType.FIREBASE
        elif any(keyword in tool_lower for keyword in ["help", "format", "available"]):
            return ToolType.HELP
        elif any(keyword in tool_lower for keyword in ["system", "health", "config"]):
            return ToolType.SYSTEM
        else:
            return ToolType.CUSTOM

    def _determine_tool_category(self, feature_name: str) -> ToolCategory:
        """Determine tool category based on feature name."""
        if feature_name in ["shared", "core"]:
            return ToolCategory.CORE
        elif feature_name in ["utils", "helpers"]:
            return ToolCategory.UTILITY
        else:
            return ToolCategory.FEATURE

    def _determine_entity_types(self, tool_name: str) -> List[EntityType]:
        """Determine entity types based on tool name."""
        tool_lower = tool_name.lower()

        if any(keyword in tool_lower for keyword in ["player", "register", "approve", "remove"]):
            return [EntityType.PLAYER]
        elif any(keyword in tool_lower for keyword in ["team", "member", "admin", "remove"]):
            return [EntityType.TEAM_MEMBER]
        elif any(keyword in tool_lower for keyword in ["both", "both_players", "both_members"]):
            return [EntityType.BOTH]
        else:
            return [EntityType.NEITHER]

    def _determine_access_control(self, tool_name: str) -> Dict[str, List[str]]:
        """Determine access control based on tool name."""
        tool_lower = tool_name.lower()

        # Default access control
        access_control: Dict[str, List[str]] = {}

        # Admin tools - accessible by team administrators and managers
        if any(keyword in tool_lower for keyword in ["admin", "manage", "control"]):
            access_control["team_administrator"] = ["both"]
            access_control["team_manager"] = ["both"]
        
        # Player management tools - accessible by team managers and coordinators
        elif any(keyword in tool_lower for keyword in ["player", "register", "approve", "remove", "add"]):
            access_control["team_manager"] = ["both"]
            access_control["player_coordinator"] = ["both"]
            access_control["team_administrator"] = ["both"]
        
        # Team management tools - accessible by team administrators and managers
        elif any(keyword in tool_lower for keyword in ["team", "member", "squad"]):
            access_control["team_administrator"] = ["both"]
            access_control["team_manager"] = ["both"]
        
        # Match management tools - accessible by match coordinators and team managers
        elif any(keyword in tool_lower for keyword in ["match", "game", "fixture"]):
            access_control["match_coordinator"] = ["both"]
            access_control["team_manager"] = ["both"]
        
        # Communication tools - accessible by communication managers
        elif any(keyword in tool_lower for keyword in ["message", "notification", "communication"]):
            access_control["communication_manager"] = ["both"]
        
        # Finance tools - accessible by finance managers
        elif any(keyword in tool_lower for keyword in ["payment", "finance", "budget", "expense"]):
            access_control["finance_manager"] = ["both"]
        
        # Help tools - accessible by help assistants
        elif any(keyword in tool_lower for keyword in ["help", "assist", "guide"]):
            access_control["help_assistant"] = ["both"]
        
        # System tools - accessible by intelligent system
        elif any(keyword in tool_lower for keyword in ["system", "health", "status"]):
            access_control["intelligent_system"] = ["both"]

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

        tools_by_entity = {}
        for entity_type in EntityType:
            tools_by_entity[entity_type.value] = len(self.get_tools_by_entity_type(entity_type))

        context_aware_tools = len([tool for tool in self._tools.values() if tool.requires_context])

        return {
            "total_tools": total_tools,
            "total_aliases": total_aliases,
            "tools_by_type": tools_by_type,
            "tools_by_category": tools_by_category,
            "tools_by_entity": tools_by_entity,
            "context_aware_tools": context_aware_tools,
            "features": list(self._feature_tools.keys()),
            "features_with_tools": list(
                self._feature_tools.keys()
            ),  # Add this for backward compatibility
            "discovered": self._discovered,
        }

    def list_all_tools(self) -> List[ToolMetadata]:
        """Get all registered tools."""
        return list(self._tools.values())

    def search_tools(self, query: str) -> List[ToolMetadata]:
        """Search tools by name or description."""
        query_lower = query.lower()
        results = []

        for tool in self._tools.values():
            if (
                query_lower in tool.name.lower()
                or query_lower in tool.description.lower()
                or query_lower in tool.feature_module.lower()
            ):
                results.append(tool)

        return results

    def get_tool_names(self) -> List[str]:
        """Get list of all tool names."""
        return list(self._tools.keys())

    def get_tool_functions(self) -> Dict[str, Callable]:
        """Get dictionary of tool names to their functions."""
        return {
            tool_id: tool.tool_function
            for tool_id, tool in self._tools.items()
            if tool.tool_function is not None
        }

    def get_context_aware_tools(self) -> List[str]:
        """Get list of tools that require context."""
        return [tool_id for tool_id, tool in self._tools.items() if tool.requires_context]


# Global tool registry instance - True singleton
_tool_registry: Optional[ToolRegistry] = None
_tool_registry_initialized = False


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance - ensures single instance."""
    global _tool_registry, _tool_registry_initialized

    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        logger.info("🔧 Created new global ToolRegistry instance")

    return _tool_registry


def initialize_tool_registry(src_path: str = "kickai") -> ToolRegistry:
    """Initialize the global tool registry with auto-discovery."""
    global _tool_registry_initialized

    registry = get_tool_registry()

    if not _tool_registry_initialized:
        logger.info(f"🔍 Initializing global ToolRegistry with auto-discovery from {src_path}")
        registry.auto_discover_tools(src_path)
        _tool_registry_initialized = True
        logger.info("✅ Global ToolRegistry initialized and ready")

    return registry


def reset_tool_registry() -> None:
    """Reset the global tool registry (for testing)."""
    global _tool_registry, _tool_registry_initialized
    _tool_registry = None
    _tool_registry_initialized = False
    logger.info("🔄 Global ToolRegistry reset")


def get_tool(tool_name: str) -> Optional[Callable]:
    """Get a tool function by name."""
    registry = get_tool_registry()
    return registry.get_tool_function(tool_name)


def get_tool_names() -> List[str]:
    """Get list of all available tool names."""
    registry = get_tool_registry()
    return registry.get_tool_names()


def get_all_tools() -> List[Callable]:
    """Get all available tool functions."""
    registry = get_tool_registry()
    return list(registry.get_tool_functions().values())
