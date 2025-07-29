#!/usr/bin/env python3
"""
CrewAI Tool Decorator

This module provides compatibility with the modern CrewAI tool decorator.
For CrewAI 0.150.0+, we can use the native tool decorator directly.
"""

# Import the native CrewAI tool decorator
from crewai.tools import tool

# Export the tool decorator for compatibility
__all__ = ["tool"]
