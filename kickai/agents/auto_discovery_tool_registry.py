#!/usr/bin/env python3
"""
Auto-Discovery Tool Registry for KICKAI System

This module provides automatic tool discovery using CrewAI's @tool decorator.
It eliminates the need for manual tool registration by scanning the codebase
for @tool decorated functions and automatically registering them.
"""

import ast
import importlib
import importlib.util
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger


class ToolType(Enum):
    """Types of tools supported by the system."""
    COMMUNICATION = "communication"
    PLAYER_MANAGEMENT = "player_management"
    TEAM_MANAGEMENT = "team_management"
    HELP = "help"
    SYSTEM = "system"
    CUSTOM = "custom"


class ToolCategory(Enum):
    """Categories of tools for organization."""
    CORE = "core"
    FEATURE = "feature"
    UTILITY = "utility"


@dataclass
class AutoDiscoveredTool:
    """Auto-discovered tool information."""
    tool_id: str
    name: str
    description: str
    tool_function: Callable
    tool_type: ToolType
    category: ToolCategory
    feature_module: str
    file_path: str
    line_number: int
    enabled: bool = True


class AutoDiscoveryToolRegistry:
    """Auto-discovery tool registry using CrewAI @tool decorator."""

    def __init__(self):
        """Initialize the auto-discovery tool registry."""
        self._tools: dict[str, AutoDiscoveredTool] = {}
        self._discovered = False
        logger.info("🔍 Auto-Discovery Tool Registry initialized")

    def auto_discover_tools(self, src_path: str = "kickai") -> None:
        """Auto-discover all @tool decorated functions."""
        if self._discovered:
            logger.info("✅ Tools already discovered")
            return

        logger.info(f"🔍 Auto-discovering tools from {src_path}")

        # Discover tools from the codebase
        discovered_tools = self._discover_tools_from_codebase(src_path)

        # Register discovered tools
        for tool in discovered_tools:
            self._register_discovered_tool(tool)

        logger.info(f"✅ Auto-discovered {len(discovered_tools)} tools")
        self._discovered = True

    def _discover_tools_from_codebase(self, src_path: str) -> list[AutoDiscoveredTool]:
        """Discover all @tool decorated functions from the codebase."""
        discovered_tools = []

        # Find all Python files in the codebase
        src_path_obj = Path(src_path)
        if not src_path_obj.exists():
            logger.warning(f"⚠️ Source path {src_path} does not exist")
            return discovered_tools

        # Search for Python files containing @tool decorators
        for py_file in src_path_obj.rglob("*.py"):
            if "test" in py_file.name.lower() or "test" in str(py_file):
                continue  # Skip test files

            tools_in_file = self._discover_tools_from_file(py_file)
            discovered_tools.extend(tools_in_file)

        return discovered_tools

    def _discover_tools_from_file(self, file_path: Path) -> list[AutoDiscoveredTool]:
        """Discover @tool decorated functions from a single file."""
        tools = []

        try:
            # Parse the file
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Parse AST to find @tool decorated functions
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has @tool decorator
                    tool_info = self._extract_tool_info_from_node(node, content, file_path)
                    if tool_info:
                        tools.append(tool_info)

        except Exception as e:
            logger.warning(f"⚠️ Error parsing {file_path}: {e}")

        return tools

    def _extract_tool_info_from_node(self, node: ast.FunctionDef, content: str, file_path: Path) -> AutoDiscoveredTool | None:
        """Extract tool information from an AST function node."""
        try:
            # Check for @tool decorator
            tool_name = None
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'tool':
                    # Extract tool name from @tool("tool_name")
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        tool_name = decorator.args[0].value
                        break
                elif isinstance(decorator, ast.Name) and decorator.id == 'tool':
                    # Handle @tool without arguments (uses function name)
                    tool_name = node.name
                    break

            if not tool_name:
                return None

            # Extract function information
            function_name = node.name

            # Extract docstring
            docstring = ast.get_docstring(node) or f"Tool: {function_name}"

            # Determine tool type and category from file path
            tool_type = self._determine_tool_type_from_path(file_path)
            category = self._determine_tool_category_from_path(file_path)
            feature_module = self._determine_feature_module_from_path(file_path)

            # Import and get the actual function
            tool_function = self._import_function_from_file(file_path, function_name)
            if not tool_function:
                logger.warning(f"⚠️ Could not import function {function_name} from {file_path}")
                return None

            return AutoDiscoveredTool(
                tool_id=tool_name,
                name=tool_name,
                description=docstring,
                tool_function=tool_function,
                tool_type=tool_type,
                category=category,
                feature_module=feature_module,
                file_path=str(file_path),
                line_number=node.lineno
            )

        except Exception as e:
            logger.warning(f"⚠️ Error extracting tool info from {file_path}:{node.lineno}: {e}")
            return None

    def _determine_tool_type_from_path(self, file_path: Path) -> ToolType:
        """Determine tool type from file path."""
        path_str = str(file_path).lower()

        if "communication" in path_str:
            return ToolType.COMMUNICATION
        elif "player" in path_str:
            return ToolType.PLAYER_MANAGEMENT
        elif "team" in path_str:
            return ToolType.TEAM_MANAGEMENT
        elif "help" in path_str:
            return ToolType.HELP
        elif "system" in path_str or "firebase" in path_str or "logging" in path_str:
            return ToolType.SYSTEM
        else:
            return ToolType.CUSTOM

    def _determine_tool_category_from_path(self, file_path: Path) -> ToolCategory:
        """Determine tool category from file path."""
        path_str = str(file_path).lower()

        if "shared" in path_str or "core" in path_str:
            return ToolCategory.CORE
        elif "tools" in path_str:
            return ToolCategory.FEATURE
        else:
            return ToolCategory.UTILITY

    def _determine_feature_module_from_path(self, file_path: Path) -> str:
        """Determine feature module from file path."""
        parts = file_path.parts

        # Look for feature module in path
        for i, part in enumerate(parts):
            if part == "features" and i + 1 < len(parts):
                return parts[i + 1]

        return "unknown"

    def _import_function_from_file(self, file_path: Path, function_name: str) -> Callable | None:
        """Import a function from a file."""
        try:
            # Convert file path to module path
            module_path = str(file_path).replace('/', '.').replace('.py', '')
            if module_path.startswith('kickai.'):
                module_path = module_path
            else:
                module_path = f"kickai.{module_path}"

            # Import the module
            module = importlib.import_module(module_path)

            # Get the function
            if hasattr(module, function_name):
                return getattr(module, function_name)
            else:
                logger.warning(f"⚠️ Function {function_name} not found in {module_path}")
                return None

        except Exception as e:
            logger.warning(f"⚠️ Error importing {function_name} from {file_path}: {e}")
            return None

    def _register_discovered_tool(self, tool: AutoDiscoveredTool) -> None:
        """Register a discovered tool."""
        if tool.tool_id in self._tools:
            logger.warning(f"⚠️ Tool {tool.tool_id} already registered, skipping")
            return

        self._tools[tool.tool_id] = tool
        logger.info(f"✅ Auto-registered tool: {tool.tool_id} ({tool.tool_type.value})")

    def get_tool_function(self, tool_id: str) -> Callable | None:
        """Get tool function by ID."""
        if tool_id not in self._tools:
            logger.error(f"❌ Tool not found: {tool_id}")
            logger.info(f"Available tools: {list(self._tools.keys())}")
            return None

        tool = self._tools[tool_id]
        # If it's a CrewAI Tool object, return the original function
        if hasattr(tool.tool_function, 'func'):
            return tool.tool_function.func
        else:
            return tool.tool_function

    def get_tool_names(self) -> list[str]:
        """Get all tool names."""
        return list(self._tools.keys())

    def get_tools_by_type(self, tool_type: ToolType) -> list[AutoDiscoveredTool]:
        """Get tools by type."""
        return [tool for tool in self._tools.values() if tool.tool_type == tool_type]

    def get_tools_by_category(self, category: ToolCategory) -> list[AutoDiscoveredTool]:
        """Get tools by category."""
        return [tool for tool in self._tools.values() if tool.category == category]

    def get_enabled_tools(self) -> list[AutoDiscoveredTool]:
        """Get all enabled tools."""
        return [tool for tool in self._tools.values() if tool.enabled]

    def list_all_tools(self) -> list[AutoDiscoveredTool]:
        """List all tools."""
        return list(self._tools.values())

    def get_tool_statistics(self) -> dict[str, Any]:
        """Get statistics about discovered tools."""
        total_tools = len(self._tools)
        enabled_tools = len(self.get_enabled_tools())

        type_counts = {}
        for tool_type in ToolType:
            type_counts[tool_type.value] = len(self.get_tools_by_type(tool_type))

        category_counts = {}
        for category in ToolCategory:
            category_counts[category.value] = len(self.get_tools_by_category(category))

        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_tools,
            "tool_types": type_counts,
            "categories": category_counts,
            "discovery_status": self._discovered
        }

    def get_tool_info(self, tool_id: str) -> AutoDiscoveredTool | None:
        """Get detailed information about a tool."""
        return self._tools.get(tool_id)


# Global registry instance
_auto_discovery_registry: AutoDiscoveryToolRegistry | None = None


def get_auto_discovery_tool_registry() -> AutoDiscoveryToolRegistry:
    """Get the global auto-discovery tool registry instance."""
    global _auto_discovery_registry
    if _auto_discovery_registry is None:
        _auto_discovery_registry = AutoDiscoveryToolRegistry()
        _auto_discovery_registry.auto_discover_tools()
    return _auto_discovery_registry


def reset_auto_discovery_tool_registry() -> None:
    """Reset the global auto-discovery tool registry."""
    global _auto_discovery_registry
    _auto_discovery_registry = None
    logger.info("🔄 Auto-Discovery Tool Registry reset")


def get_tool(tool_name: str) -> Callable | None:
    """Get a tool function by name."""
    registry = get_auto_discovery_tool_registry()
    return registry.get_tool_function(tool_name)


def get_tool_names() -> list[str]:
    """Get all tool names."""
    registry = get_auto_discovery_tool_registry()
    return registry.get_tool_names()


def get_tool_statistics() -> dict[str, Any]:
    """Get tool discovery statistics."""
    registry = get_auto_discovery_tool_registry()
    return registry.get_tool_statistics()

