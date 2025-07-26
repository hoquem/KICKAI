#!/usr/bin/env python3
"""
Tool Helper Utilities

This module provides utility functions for handling CrewAI tool inputs and
standardizing error messages across all tools.
"""

import json
from typing import Any, Dict, Union


def parse_crewai_json_input(input_value: str, expected_keys: list[str]) -> Dict[str, str]:
    """
    Parse CrewAI JSON input and extract expected keys.
    
    Args:
        input_value: The input value (could be JSON string or regular string)
        expected_keys: List of keys to extract from JSON
        
    Returns:
        Dictionary with extracted values for each expected key
        
    Raises:
        ValueError: If JSON parsing fails
    """
    if isinstance(input_value, str) and input_value.startswith('{'):
        try:
            parsed = json.loads(input_value)
            return {key: parsed.get(key, '') for key in expected_keys}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
    
    # If not JSON, return the input value for the first key (backward compatibility)
    return {expected_keys[0]: input_value} if expected_keys else {}


def extract_single_value(input_value: Any, key: str) -> str:
    """
    Extract a single value from CrewAI input, handling various input formats.
    
    Args:
        input_value: The input value (could be JSON string, dict, or other types)
        key: The key to extract
        
    Returns:
        Extracted value or original input_value if not found
    """
    # If it's already a string, try JSON parsing
    if isinstance(input_value, str):
        try:
            parsed = parse_crewai_json_input(input_value, [key])
            return parsed.get(key, input_value)
        except ValueError:
            return input_value
    
    # If it's a dict, search for the key recursively
    if isinstance(input_value, dict):
        # Direct key lookup
        if key in input_value:
            return str(input_value[key])
        
        # Search in security_context (common pattern in CrewAI)
        if 'security_context' in input_value:
            security_ctx = input_value['security_context']
            if isinstance(security_ctx, dict) and key in security_ctx:
                return str(security_ctx[key])
        
        # Search in execution_context (another common pattern)
        if 'execution_context' in input_value:
            exec_ctx = input_value['execution_context']
            if isinstance(exec_ctx, dict) and key in exec_ctx:
                return str(exec_ctx[key])
        
        # Recursive search in nested dictionaries
        for k, v in input_value.items():
            if isinstance(v, dict):
                result = extract_single_value(v, key)
                # Check if we found a meaningful result (not the original input)
                if result != str(v) and result != str(input_value):
                    return result
    
    # Fallback: return string representation
    return str(input_value)


def format_tool_error(message: str, error_type: str = "Error") -> str:
    """
    Format consistent error messages for tools.
    
    Args:
        message: The error message
        error_type: The type of error (Error, Warning, Info, etc.)
        
    Returns:
        Formatted error message
    """
    return f"❌ {error_type}: {message}"


def format_tool_success(message: str, success_type: str = "Success") -> str:
    """
    Format consistent success messages for tools.
    
    Args:
        message: The success message
        success_type: The type of success (Success, Info, etc.)
        
    Returns:
        Formatted success message
    """
    return f"✅ {success_type}: {message}"


def validate_required_input(value: str, field_name: str) -> str:
    """
    Validate that a required input field is not empty.
    
    Args:
        value: The input value to validate
        field_name: The name of the field for error messages
        
    Returns:
        Error message if validation fails, empty string if valid
    """
    if not value or not value.strip():
        return format_tool_error(f"{field_name} is required")
    return "" 


def extract_context_from_task_description(task_description: str) -> dict[str, str]:
    """
    Extract context information from CrewAI task description.
    
    Args:
        task_description: The task description that may contain context information
        
    Returns:
        Dictionary of context key-value pairs
    """
    context = {}
    
    try:
        # Look for context section in task description
        if "Context:" in task_description:
            context_section = task_description.split("Context:")[1].strip()
            
            # Parse key-value pairs
            for item in context_section.split(','):
                item = item.strip()
                if ':' in item:
                    key, value = item.split(':', 1)
                    context[key.strip()] = value.strip()
    
    except Exception as e:
        logger.warning(f"Failed to extract context from task description: {e}")
    
    return context 