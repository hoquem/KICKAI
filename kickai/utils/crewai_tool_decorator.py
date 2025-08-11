#!/usr/bin/env python3
"""
CrewAI Tool Decorator with JSON Response Support

This module provides enhanced tool decorators that support JSON responses
while maintaining backward compatibility with existing string-based tools.
"""

import json
import functools
from typing import Callable, Any, Optional, Union
from loguru import logger

# Import the native CrewAI tool decorator
from crewai.tools import tool as crewai_tool

# Import our JSON response infrastructure
from .json_response import ToolResponse, JSONResponseBuilder, create_data_response, create_error_response
from .ui_formatter import DynamicUIFormatter


def tool(tool_name: str, json_output: bool = False):
    """
    Enhanced tool decorator that supports both string and JSON outputs.
    
    Args:
        tool_name: Name of the tool
        json_output: If True, tool returns JSON. If False, returns string (backward compatibility)
    """
    def decorator(func: Callable) -> Callable:
        # Ensure the function has a docstring (CrewAI requirement)
        if not func.__doc__:
            func.__doc__ = f"Tool: {tool_name}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Execute the original function
                result = func(*args, **kwargs)
                
                # If json_output is True, ensure we return JSON
                if json_output:
                    return _ensure_json_response(result, tool_name)
                else:
                    # Backward compatibility: return string as-is
                    return result
                    
            except Exception as e:
                logger.error(f"Error in tool {tool_name}: {e}")
                if json_output:
                    return create_error_response(str(e), f"Tool {tool_name} failed")
                else:
                    return f"❌ Error in {tool_name}: {e}"
        
        # Apply the CrewAI tool decorator and return the tool object
        return crewai_tool(tool_name)(wrapper)
    
    return decorator


def json_tool(tool_name: str):
    """
    Convenience decorator for tools that should return JSON.
    Equivalent to @tool(tool_name, json_output=True)
    """
    return tool(tool_name, json_output=True)


def _ensure_json_response(result: Any, tool_name: str) -> str:
    """
    Ensure the result is a valid JSON response string.
    
    Args:
        result: The result from the tool function
        tool_name: Name of the tool for error context
        
    Returns:
        JSON string response
    """
    # If result is already a JSON string, validate and return
    if isinstance(result, str):
        try:
            # Try to parse as JSON to validate
            json.loads(result)
            return result
        except json.JSONDecodeError:
            # Not valid JSON, treat as error message
            return create_error_response(result, f"Tool {tool_name} returned invalid response")
    
    # If result is a ToolResponse object, convert to JSON
    if isinstance(result, ToolResponse):
        return JSONResponseBuilder.to_json(result)
    
    # If result is a dict, create success response
    if isinstance(result, dict):
        return create_data_response(result)
    
    # For any other type, convert to string and create error response
    return create_error_response(
        str(result), 
        f"Tool {tool_name} returned unexpected type: {type(result).__name__}"
    )


def migrate_tool_to_json(tool_name: str):
    """
    Decorator to migrate existing string-based tools to JSON output.
    This decorator wraps the original function and converts its string output to JSON.
    """
    def decorator(func: Callable) -> Callable:
        # Ensure the function has a docstring (CrewAI requirement)
        if not func.__doc__:
            func.__doc__ = f"Tool: {tool_name}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Execute the original function (returns string)
                string_result = func(*args, **kwargs)
                
                # Convert string result to JSON with UI format
                return _convert_string_to_json(string_result, tool_name)
                
            except Exception as e:
                logger.error(f"Error in migrated tool {tool_name}: {e}")
                return create_error_response(str(e), f"Tool {tool_name} failed")
        
        # Apply the CrewAI tool decorator and return the tool object
        return crewai_tool(tool_name)(wrapper)
    
    return decorator


def _convert_string_to_json(string_result: str, tool_name: str) -> str:
    """
    Convert a string result to JSON format with UI formatting.
    
    Args:
        string_result: The original string result from the tool
        tool_name: Name of the tool for context
        
    Returns:
        JSON string with UI format
    """
    try:
        # Check if the result looks like an error
        if string_result.startswith("❌") or "error" in string_result.lower():
            return create_error_response(string_result, f"Tool {tool_name} failed")
        
        # Create a data structure based on the tool name
        data = _extract_data_from_string(string_result, tool_name)
        
        # Use the string result as UI format
        ui_format = string_result
        
        # Create JSON response with UI format
        return create_data_response(data, ui_format)
        
    except Exception as e:
        logger.error(f"Error converting string to JSON for {tool_name}: {e}")
        return create_error_response(str(e), f"JSON conversion failed for {tool_name}")


def _extract_data_from_string(string_result: str, tool_name: str) -> dict:
    """
    Extract structured data from a string result based on tool name.
    This is a simple heuristic - tools should be updated to return proper data structures.
    
    Args:
        string_result: The string result from the tool
        tool_name: Name of the tool for context
        
    Returns:
        Dictionary with extracted data
    """
    # Simple data extraction based on tool name patterns
    if "player" in tool_name.lower():
        return {
            "tool_type": "player_operation",
            "result": string_result,
            "raw_output": string_result
        }
    elif "team" in tool_name.lower():
        return {
            "tool_type": "team_operation", 
            "result": string_result,
            "raw_output": string_result
        }
    elif "match" in tool_name.lower():
        return {
            "tool_type": "match_operation",
            "result": string_result,
            "raw_output": string_result
        }
    elif "help" in tool_name.lower():
        return {
            "tool_type": "help_operation",
            "result": string_result,
            "raw_output": string_result
        }
    else:
        return {
            "tool_type": "general_operation",
            "result": string_result,
            "raw_output": string_result
        }


# Export both the original and enhanced decorators
__all__ = ["tool", "json_tool", "migrate_tool_to_json"]
