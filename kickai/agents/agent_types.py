#!/usr/bin/env python3
"""
Agent Types

This module provides shared types and data structures used across the agent system.
"""

from dataclasses import dataclass
from typing import Any, Optional

from kickai.core.enums import AgentRole


@dataclass
class AgentContext:
    """Context for creating configurable agents."""
    role: AgentRole
    team_id: str
    llm: Any
    tool_registry: Any
    config: Optional[Any] = None
    team_memory: Optional[Any] = None  # Add team memory for context persistence 