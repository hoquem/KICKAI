#!/usr/bin/env python3
"""
Simple JSON Response Helper - KISS Principle Implementation

This module replaces the over-engineered decorator system with a simple,
maintainable helper function following Python best practices.

Replaces:
- crewai_tool_decorator.py (211 lines)
- json_response.py (140 lines)
- ui_formatter.py (200+ lines)
- Complex decorator abstraction

With:
- Single simple function (~50 lines)
- Pure function approach
- Standard Python patterns
"""

import json
from datetime import datetime
from typing import Any

from loguru import logger


def json_response(
    data: dict[str, Any],
    message: str = "Operation completed successfully",
    ui_format: str | None = None,
    success: bool = True
) -> str:
    """
    Create standardized JSON response for CrewAI tools.

    This simple function replaces the complex decorator system while
    maintaining the exact same JSON structure for backward compatibility.


        data: Tool-specific data to return
        message: Operation status message
        ui_format: Human-readable formatted text for display
        success: Whether the operation was successful


    :return: JSON string with standardized structure
    :rtype: str  # TODO: Fix type

    Example:
        >>> data = {"player_id": "123", "name": "John"}
        >>> json_response(data, ui_format="✅ John (Active Player)")
        '{"success": true, "data": {...}, "ui_format": "✅ John (Active Player)"}'
    """
    try:
        response = {
            "success": success,
            "data": data,
            "message": message,
            "error": None,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            },
            "ui_format": ui_format
        }
        return json.dumps(response, indent=2, default=str, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Failed to create JSON response: {e}")
        # Fallback response if JSON creation fails
        return json.dumps({
            "success": False,
            "data": {},
            "message": "JSON serialization failed",
            "error": str(e),
            "metadata": {"timestamp": datetime.utcnow().isoformat()},
            "ui_format": f"❌ Error: Failed to format response ({e!s})"
        }, indent=2)


def json_error(error: str, message: str = "Operation failed") -> str:
    """
    Create standardized error JSON response.


        error: Error description
        message: Error message


    :return: JSON string with error structure
    :rtype: str  # TODO: Fix type

    Example:
        >>> json_error("Player not found", "Lookup failed")
        '{"success": false, "error": "Player not found", "ui_format": "❌ Player not found"}'
    """
    return json_response(
        data={},
        message=message,
        ui_format=f"❌ {error}",
        success=False
    )


# Backward compatibility aliases (will be removed after migration)
def create_data_response(data: dict[str, Any], ui_format: str | None = None) -> str:
    """Backward compatibility alias - will be removed."""
    return json_response(data, ui_format=ui_format)


def create_error_response(error: str, message: str = "Operation failed") -> str:
    """Backward compatibility alias - will be removed."""
    return json_error(error, message)
