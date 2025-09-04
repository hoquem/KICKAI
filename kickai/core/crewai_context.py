#!/usr/bin/env python3
"""
CrewAI Context Management - DEPRECATED

This module has been deprecated in favor of CrewAI native parameter passing.
Tools now receive parameters directly via their function signatures.

IMPORTANT: Use CrewAI native methods only - pass parameters directly to tools!
"""

# Deprecated - keeping file for compatibility but all functions are no-ops
import warnings
from typing import Any


def deprecated_function(name: str):
    """Issue deprecation warning for old context functions."""
    warnings.warn(
        f"{name} is deprecated. Use CrewAI native parameter passing instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def set_current_task_context(task) -> None:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("set_current_task_context")


def get_current_task_context() -> Any | None:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_current_task_context")
    return None


def get_current_task_config() -> dict[str, Any] | None:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_current_task_config")
    return None


def get_context_value(key: str, default: Any = None) -> Any:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("get_context_value")
    return default


def validate_context_completeness(context: dict[str, Any]) -> None:
    """Context validation - still used for initial validation."""
    if not context:
        raise ValueError("Context cannot be empty")

    required_fields = ["team_id", "telegram_id", "username", "chat_type"]
    missing_fields = [
        field for field in required_fields if field not in context or not context[field]
    ]

    if missing_fields:
        raise ValueError(f"Missing required context fields: {missing_fields}")


def clear_current_task_context() -> None:
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("clear_current_task_context")


class TaskContextManager:
    """DEPRECATED: Use CrewAI native parameter passing."""

    def __init__(self, task):
        deprecated_function("TaskContextManager")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def ensure_task_context_cleanup():
    """DEPRECATED: Use CrewAI native parameter passing."""
    deprecated_function("ensure_task_context_cleanup")
