#!/usr/bin/env python3
"""
Communication tools module.

This module provides tools for communication and messaging.
"""

# Import the native CrewAI tools (working version with plain string returns)
from .communication_tools_native import send_announcement, send_message, send_poll
from .telegram_tools_native import get_invite_link

__all__ = [
    # Communication tools (only the ones actually used by agents)
    "send_message",
    "send_announcement", 
    "send_poll",
    # Telegram tools
    "get_invite_link",
]

# Note: JSON versions of these tools are deprecated and should not be used
# All imports now use native CrewAI tools with plain string returns
