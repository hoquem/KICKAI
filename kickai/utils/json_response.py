#!/usr/bin/env python3
"""
JSON Response Infrastructure

This module provides standardized JSON response structures for all tools
to ensure consistent, parseable output while maintaining human-friendly UI display.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json
from datetime import datetime
from loguru import logger


@dataclass
class ToolResponse:
    """Standardized tool response structure."""
    success: bool
    data: Dict[str, Any]
    message: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    ui_format: Optional[str] = None  # Human-friendly formatted text


class JSONResponseBuilder:
    """Builder for creating standardized JSON responses."""
    
    @staticmethod
    def success(data: Dict[str, Any], message: str = "Operation completed successfully") -> ToolResponse:
        """Create a success response."""
        return ToolResponse(
            success=True,
            data=data,
            message=message,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    @staticmethod
    def error(error: str, message: str = "Operation failed") -> ToolResponse:
        """Create an error response."""
        return ToolResponse(
            success=False,
            data={},
            message=message,
            error=error,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    @staticmethod
    def to_json(response: ToolResponse) -> str:
        """Convert ToolResponse to JSON string."""
        try:
            return json.dumps(response.__dict__, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to serialize ToolResponse to JSON: {e}")
            # Fallback to simple error response
            fallback = {
                "success": False,
                "data": {},
                "message": "Serialization error",
                "error": str(e),
                "metadata": {"timestamp": datetime.utcnow().isoformat()},
                "ui_format": f"❌ Error: Failed to format response ({str(e)})"
            }
            return json.dumps(fallback, indent=2)
    
    @staticmethod
    def from_json(json_str: str) -> Optional[ToolResponse]:
        """Create ToolResponse from JSON string."""
        try:
            data = json.loads(json_str)
            return ToolResponse(**data)
        except Exception as e:
            logger.error(f"Failed to parse JSON to ToolResponse: {e}")
            return None


class ToolResponseValidator:
    """Validate tool responses for consistency."""
    
    @staticmethod
    def validate_response(response: ToolResponse) -> bool:
        """Validate a ToolResponse object."""
        if not isinstance(response, ToolResponse):
            return False
        
        if not isinstance(response.success, bool):
            return False
        
        if not isinstance(response.data, dict):
            return False
        
        if not isinstance(response.message, str):
            return False
        
        if response.error is not None and not isinstance(response.error, str):
            return False
        
        if not isinstance(response.metadata, dict):
            return False
        
        if response.ui_format is not None and not isinstance(response.ui_format, str):
            return False
        
        return True
    
    @staticmethod
    def validate_json_response(json_str: str) -> bool:
        """Validate a JSON response string."""
        try:
            response = JSONResponseBuilder.from_json(json_str)
            if response is None:
                return False
            return ToolResponseValidator.validate_response(response)
        except Exception:
            return False


# Convenience functions for common response patterns
def create_success_response(data: Dict[str, Any], message: str = "Success") -> str:
    """Create a success JSON response."""
    response = JSONResponseBuilder.success(data, message)
    return JSONResponseBuilder.to_json(response)


def create_error_response(error: str, message: str = "Error occurred") -> str:
    """Create an error JSON response."""
    response = JSONResponseBuilder.error(error, message)
    return JSONResponseBuilder.to_json(response)


def create_data_response(data: Dict[str, Any], ui_format: str = None) -> str:
    """Create a data response with optional UI format."""
    response = JSONResponseBuilder.success(data)
    if ui_format:
        response.ui_format = ui_format
    return JSONResponseBuilder.to_json(response)
