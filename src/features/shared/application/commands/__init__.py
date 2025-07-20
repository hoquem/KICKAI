#!/usr/bin/env python3
"""
Shared Commands Module

This module contains commands that are shared across multiple features.
"""

# Import shared commands that exist
from .base_command import *
from .types import *

# Note: Help commands are now handled by the CrewAI system via the HELP_ASSISTANT agent
# This ensures consistent, context-aware help across all chat types and user states 