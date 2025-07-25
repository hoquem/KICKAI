#!/usr/bin/env python3
"""
CrewAI Tool Decorator

This module provides a simple decorator to create CrewAI tools from functions.
It uses the Tool.from_function method to maintain compatibility with the current
CrewAI version.
"""

from typing import Callable, Any, Optional
from crewai.tools import BaseTool as Tool


def tool(name: str, description: Optional[str] = None):
    """
    Decorator to create a CrewAI tool from a function.
    
    Args:
        name: The name of the tool
        description: Optional description for the tool
    
    Returns:
        Decorated function that returns a CrewAI Tool instance
    """
    def decorator(func: Callable) -> Callable:
        # Get the function's docstring as description if none provided
        tool_description = description or func.__doc__ or f"Tool: {name}"
        
        # Create the tool using Tool.from_function
        tool_instance = Tool.from_function(
            func=func,
            name=name,
            description=tool_description
        )
        
        # Return the tool instance instead of the function
        return tool_instance
    
    return decorator 