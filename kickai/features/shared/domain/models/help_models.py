#!/usr/bin/env python3
"""
Help Models - Data structures for help functionality

This module contains data models for help content without any dependencies
to avoid circular imports.
"""

from dataclasses import dataclass


@dataclass
class CommandInfo:
    """Command information structure."""

    name: str
    description: str
    examples: list[str]
    permission_level: str
    chat_type: str


@dataclass
class HelpContent:
    """Help content structure."""

    title: str
    description: str
    commands: list[CommandInfo]
    footer: str
