#!/usr/bin/env python3
"""
Intelligent Router Module - Wrapper for Standalone Implementation
Provides the expected interface for tests and other modules.
"""

from .standalone_router import (
    StandaloneIntelligentRouter,
    RoutingDecision,
    RequestContext
)

# Alias the class to match expected interface
IntelligentAgentRouter = StandaloneIntelligentRouter

# Re-export the classes
__all__ = ['IntelligentAgentRouter', 'RoutingDecision', 'RequestContext'] 