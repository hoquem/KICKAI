#!/usr/bin/env python3
"""
Auto-Discovery Tool Registry for KICKAI System

This module provides automatic tool discovery using CrewAI's @tool decorator.
It eliminates the need for manual tool registration by scanning the codebase
for @tool decorated functions and automatically registering them.
"""

import ast
import importlib
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger

# CONSTANTS
DEFAULT_SRC_PATH = "kickai"
DEFAULT_FEATURE_MODULE = "unknown"
DEFAULT_DOCSTRING = "Tool: {function_name}"
DEFAULT_TOOL_VERSION = "1.0.0"

# FILE PATTERNS
TEST_FILE_PATTERNS = ["test", "tests", "_test", "test_"]
TOOL_DECORATOR_NAME = "tool"

# PATH PATTERNS FOR TOOL CLASSIFICATION
COMMUNICATION_PATTERNS = ["communication"]
PLAYER_PATTERNS = ["player"]
TEAM_PATTERNS = ["team"]
HELP_PATTERNS = ["help"]
SYSTEM_PATTERNS = ["system", "firebase", "logging"]
CORE_PATTERNS = ["shared", "core"]
FEATURE_PATTERNS = ["tools"]

# ERROR MESSAGES
ERROR_MESSAGES = {
    "SOURCE_PATH_NOT_FOUND": "Source path {path} does not exist",
    "FILE_PARSE_ERROR": "Error parsing {file_path}: {error}",
    "TOOL_INFO_EXTRACTION_ERROR": "Error extracting tool info from {file_path}:{line}: {error}",
    "FUNCTION_IMPORT_ERROR": "Could not import function {function_name} from {file_path}",
    "MODULE_IMPORT_ERROR": "Error importing {function_name} from {file_path}: {error}",
    "FUNCTION_NOT_FOUND": "Function {function_name} not found in {module_path}",
    "TOOL_ALREADY_REGISTERED": "Tool {tool_id} already registered, skipping",
    "TOOL_NOT_FOUND": "Tool not found: {tool_id}",
}

# LOG MESSAGES
LOG_MESSAGES = {
    "REGISTRY_INITIALIZED": "Auto-Discovery Tool Registry initialized",
    "TOOLS_ALREADY_DISCOVERED": "Tools already discovered",
    "DISCOVERY_STARTED": "Auto-discovering tools from {src_path}",
    "DISCOVERY_COMPLETED": "Auto-discovered {count} tools",
    "TOOL_REGISTERED": "Auto-registered tool: {tool_id} ({tool_type})",
    "REGISTRY_RESET": "Auto-Discovery Tool Registry reset",
    "AVAILABLE_TOOLS": "Available tools: {tools}",
}

# SUCCESS MESSAGES
SUCCESS_MESSAGES = {
    "TOOL_DISCOVERED": "Tool discovered: {tool_id}",
    "TOOL_IMPORTED": "Tool imported successfully: {tool_id}",
}


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

    def __init__(self) -> None:
        """Initialize the auto-discovery tool registry."""
        self._tools: dict[str, AutoDiscoveredTool] = {}
        self._discovered = False
        logger.info(LOG_MESSAGES["REGISTRY_INITIALIZED"])

    def auto_discover_tools(self, src_path: str = DEFAULT_SRC_PATH) -> None:
        """Auto-discover all @tool decorated functions."""
        if self._discovered:
            logger.info(LOG_MESSAGES["TOOLS_ALREADY_DISCOVERED"])
            return

        logger.info(LOG_MESSAGES["DISCOVERY_STARTED"].format(src_path=src_path))

        discovered_tools = self._discover_tools_from_codebase(src_path)

        for tool in discovered_tools:
            self._register_discovered_tool(tool)

        logger.info(LOG_MESSAGES["DISCOVERY_COMPLETED"].format(count=len(discovered_tools)))
        self._discovered = True

    def _discover_tools_from_codebase(self, src_path: str) -> list[AutoDiscoveredTool]:
        """Discover all @tool decorated functions from the codebase."""
        discovered_tools = []

        src_path_obj = Path(src_path)
        if not self._validate_source_path(src_path_obj):
            return discovered_tools

        for py_file in self._get_python_files(src_path_obj):
            tools_in_file = self._discover_tools_from_file(py_file)
            discovered_tools.extend(tools_in_file)

        return discovered_tools

    def _validate_source_path(self, src_path_obj: Path) -> bool:
        """Validate that the source path exists."""
        if not src_path_obj.exists():
            logger.warning(ERROR_MESSAGES["SOURCE_PATH_NOT_FOUND"].format(path=src_path_obj))
            return False
        return True

    def _get_python_files(self, src_path_obj: Path) -> list[Path]:
        """Get all Python files excluding test files."""
        python_files = []

        for py_file in src_path_obj.rglob("*.py"):
            if not self._is_test_file(py_file):
                python_files.append(py_file)

        return python_files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        file_str = str(file_path).lower()
        return any(pattern in file_str for pattern in TEST_FILE_PATTERNS)

    def _discover_tools_from_file(self, file_path: Path) -> list[AutoDiscoveredTool]:
        """Discover @tool decorated functions from a single file."""
        try:
            content = self._read_file_content(file_path)
            tree = ast.parse(content)

            tools = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    tool_info = self._extract_tool_info_from_node(node, content, file_path)
                    if tool_info:
                        tools.append(tool_info)

            return tools

        except Exception as e:
            logger.warning(ERROR_MESSAGES["FILE_PARSE_ERROR"].format(
                file_path=file_path, error=str(e)
            ))
            return []

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding."""
        with open(file_path, encoding='utf-8') as f:
            return f.read()

    def _extract_tool_info_from_node(
        self,
        node: ast.FunctionDef,
        content: str,
        file_path: Path
    ) -> AutoDiscoveredTool | None:
        """Extract tool information from an AST function node."""
        try:
            tool_name = self._extract_tool_name_from_decorators(node)
            if not tool_name:
                return None

            tool_info = self._create_tool_info(node, tool_name, file_path)
            return tool_info

        except Exception as e:
            logger.warning(ERROR_MESSAGES["TOOL_INFO_EXTRACTION_ERROR"].format(
                file_path=file_path, line=node.lineno, error=str(e)
            ))
            return None

    def _extract_tool_name_from_decorators(self, node: ast.FunctionDef) -> str | None:
        """Extract tool name from function decorators."""
        for decorator in node.decorator_list:
            if self._is_tool_decorator(decorator):
                return self._get_tool_name_from_decorator(decorator, node.name)
        return None

    def _is_tool_decorator(self, decorator: ast.expr) -> bool:
        """Check if a decorator is a @tool decorator."""
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id == TOOL_DECORATOR_NAME
        elif isinstance(decorator, ast.Name):
            return decorator.id == TOOL_DECORATOR_NAME
        return False

    def _get_tool_name_from_decorator(self, decorator: ast.expr, function_name: str) -> str:
        """Get tool name from decorator."""
        if isinstance(decorator, ast.Call) and decorator.args:
            if isinstance(decorator.args[0], ast.Constant):
                return decorator.args[0].value
        return function_name

    def _create_tool_info(self, node: ast.FunctionDef, tool_name: str, file_path: Path) -> AutoDiscoveredTool:
        """Create AutoDiscoveredTool object from function node."""
        function_name = node.name
        docstring = ast.get_docstring(node) or DEFAULT_DOCSTRING.format(function_name=function_name)

        tool_type = self._determine_tool_type_from_path(file_path)
        category = self._determine_tool_category_from_path(file_path)
        feature_module = self._determine_feature_module_from_path(file_path)

        tool_function = self._import_function_from_file(file_path, function_name)
        if not tool_function:
            raise ValueError(ERROR_MESSAGES["FUNCTION_IMPORT_ERROR"].format(
                function_name=function_name, file_path=file_path
            ))

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

    def _determine_tool_type_from_path(self, file_path: Path) -> ToolType:
        """Determine tool type from file path."""
        path_str = str(file_path).lower()

        if any(pattern in path_str for pattern in COMMUNICATION_PATTERNS):
            return ToolType.COMMUNICATION
        elif any(pattern in path_str for pattern in PLAYER_PATTERNS):
            return ToolType.PLAYER_MANAGEMENT
        elif any(pattern in path_str for pattern in TEAM_PATTERNS):
            return ToolType.TEAM_MANAGEMENT
        elif any(pattern in path_str for pattern in HELP_PATTERNS):
            return ToolType.HELP
        elif any(pattern in path_str for pattern in SYSTEM_PATTERNS):
            return ToolType.SYSTEM
        else:
            return ToolType.CUSTOM

    def _determine_tool_category_from_path(self, file_path: Path) -> ToolCategory:
        """Determine tool category from file path."""
        path_str = str(file_path).lower()

        if any(pattern in path_str for pattern in CORE_PATTERNS):
            return ToolCategory.CORE
        elif any(pattern in path_str for pattern in FEATURE_PATTERNS):
            return ToolCategory.FEATURE
        else:
            return ToolCategory.UTILITY

    def _determine_feature_module_from_path(self, file_path: Path) -> str:
        """Determine feature module from file path."""
        parts = file_path.parts

        for i, part in enumerate(parts):
            if part == "features" and i + 1 < len(parts):
                return parts[i + 1]

        return DEFAULT_FEATURE_MODULE

    def _import_function_from_file(self, file_path: Path, function_name: str) -> Callable | None:
        """Import a function from a file."""
        try:
            module_path = self._convert_file_path_to_module_path(file_path)
            module = importlib.import_module(module_path)

            if hasattr(module, function_name):
                return getattr(module, function_name)
            else:
                logger.warning(ERROR_MESSAGES["FUNCTION_NOT_FOUND"].format(
                    function_name=function_name, module_path=module_path
                ))
                return None

        except Exception as e:
            logger.warning(ERROR_MESSAGES["MODULE_IMPORT_ERROR"].format(
                function_name=function_name, file_path=file_path, error=str(e)
            ))
            return None

    def _convert_file_path_to_module_path(self, file_path: Path) -> str:
        """Convert file path to module path."""
        module_path = str(file_path).replace('/', '.').replace('.py', '')
        if not module_path.startswith('kickai.'):
            module_path = f"kickai.{module_path}"
        return module_path

    def _register_discovered_tool(self, tool: AutoDiscoveredTool) -> None:
        """Register a discovered tool."""
        if tool.tool_id in self._tools:
            logger.warning(ERROR_MESSAGES["TOOL_ALREADY_REGISTERED"].format(tool_id=tool.tool_id))
            return

        self._tools[tool.tool_id] = tool
        logger.info(LOG_MESSAGES["TOOL_REGISTERED"].format(
            tool_id=tool.tool_id, tool_type=tool.tool_type.value
        ))

    def get_tool_function(self, tool_id: str) -> Callable | None:
        """Get tool function by ID."""
        if tool_id not in self._tools:
            logger.error(ERROR_MESSAGES["TOOL_NOT_FOUND"].format(tool_id=tool_id))
            logger.info(LOG_MESSAGES["AVAILABLE_TOOLS"].format(tools=list(self._tools.keys())))
            return None

        tool = self._tools[tool_id]
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


# GLOBAL REGISTRY INSTANCE
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
    logger.info(LOG_MESSAGES["REGISTRY_RESET"])


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

