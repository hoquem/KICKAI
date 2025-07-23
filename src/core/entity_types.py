#!/usr/bin/env python3
"""
Entity Types for KICKAI System

This module contains shared entity type definitions used across the system.
Moving these here helps avoid circular imports.
"""

from enum import Enum


class EntityType(Enum):
    """Entity types that tools can operate on."""
    PLAYER = "player"
    TEAM_MEMBER = "team_member"
    BOTH = "both"  # Tool can operate on both players and team members
    NEITHER = "neither"  # Tool doesn't operate on specific entities (e.g., communication tools) 