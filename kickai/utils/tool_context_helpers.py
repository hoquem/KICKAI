#!/usr/bin/env python3
"""
Tool Context Helpers - DEPRECATED

This module has been deprecated in favor of CrewAI native parameter passing.
Tools now receive parameters directly via their function signatures.

IMPORTANT: Use CrewAI native methods only - pass parameters directly to tools!
"""

import warnings
from typing import Any


def deprecated_function(name: str):
    """Issue deprecation warning for old context functions."""
    warnings.warn(
        f"{name} is deprecated. Use CrewAI native parameter passing instead.",
        DeprecationWarning,
        stacklevel=3
    )

def get_tool_context() -> dict[str, Any] | None:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_tool_context")
    return None

def get_required_context_value(key: str) -> str:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_required_context_value")
    raise ValueError(f"Context access is deprecated. Pass '{key}' as direct parameter to tool.")

def get_optional_context_value(key: str, default: Any = None) -> Any:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_optional_context_value")
    return default

def get_user_context() -> dict[str, str]:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_user_context")
    return {}

def validate_tool_context(required_keys: list[str]) -> dict[str, str]:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("validate_tool_context")
    raise ValueError(f"Context access is deprecated. Pass {required_keys} as direct parameters to tool.")

def log_tool_context_access(tool_name: str, context_keys: list[str]) -> None:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("log_tool_context_access")

def get_context_for_tool(tool_name: str, required_keys: list[str] | None = None) -> dict[str, Any]:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_context_for_tool")
    raise ValueError(f"Tool '{tool_name}' should receive parameters directly via function signature.")
