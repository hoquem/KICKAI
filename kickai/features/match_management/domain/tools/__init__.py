#!/usr/bin/env python3
"""
Match Management Domain Tools - Clean Architecture Compliant

This module contains pure domain functions for match management, availability, and attendance.
These functions contain business logic only and delegate to application layer for CrewAI tools.

NOTE: All @tool decorators have been removed from domain layer to comply with Clean Architecture.
The application layer provides the CrewAI tool interfaces that delegate to these domain functions.
"""

# Domain layer exports nothing - all tools come from application layer
# This ensures Clean Architecture compliance by separating framework concerns
__all__ = []