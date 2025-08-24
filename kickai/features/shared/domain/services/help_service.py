#!/usr/bin/env python3
"""
Help Service - Pure Business Logic

This service provides help-related business logic without any framework dependencies.
It generates help content based on user context and available commands.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

from kickai.core.enums import ChatType


@dataclass
class CommandInfo:
    """Command information structure."""
    name: str
    description: str
    examples: List[str]
    permission_level: str
    chat_type: str


@dataclass
class HelpContent:
    """Help content structure."""
    title: str
    description: str
    commands: List[CommandInfo]
    footer: str


class HelpService:
    """Pure domain service for help functionality."""

    def __init__(self):
        pass

    def generate_help_content(self, chat_type: ChatType, username: str) -> HelpContent:
        """
        Generate help content for a specific chat type.
        
        Args:
            chat_type: The chat type context
            username: User's name for personalization
            
        Returns:
            HelpContent with personalized help information
        """
        if chat_type == ChatType.LEADERSHIP:
            return self._generate_leadership_help(username)
        elif chat_type == ChatType.PRIVATE:
            return self._generate_private_help(username)
        else:
            return self._generate_main_chat_help(username)

    def _generate_main_chat_help(self, username: str) -> HelpContent:
        """Generate help content for main chat."""
        commands = [
            CommandInfo(
                name="/help",
                description="Show this help message",
                examples=["/help"],
                permission_level="public",
                chat_type="main"
            ),
            CommandInfo(
                name="/ping",
                description="Check bot connectivity",
                examples=["/ping"],
                permission_level="public",
                chat_type="main"
            ),
            CommandInfo(
                name="/myinfo",
                description="Show your player/member information",
                examples=["/myinfo"],
                permission_level="player",
                chat_type="main"
            )
        ]
        
        return HelpContent(
            title=f"🏈 KICKAI Commands - Main Chat",
            description=f"Hello {username}! Here are the available commands for the main chat:",
            commands=commands,
            footer="💡 For team administration commands, contact leadership in the leadership chat."
        )

    def _generate_leadership_help(self, username: str) -> HelpContent:
        """Generate help content for leadership chat."""
        commands = [
            CommandInfo(
                name="/help",
                description="Show this help message",
                examples=["/help"],
                permission_level="leadership",
                chat_type="leadership"
            ),
            CommandInfo(
                name="/addplayer",
                description="Add a new player to the team",
                examples=['/addplayer "John Smith" "+447123456789"'],
                permission_level="leadership",
                chat_type="leadership"
            ),
            CommandInfo(
                name="/addmember", 
                description="Add a new team member",
                examples=['/addmember "Jane Doe" "+447987654321"'],
                permission_level="leadership",
                chat_type="leadership"
            ),
            CommandInfo(
                name="/list",
                description="List all players and team members",
                examples=["/list"],
                permission_level="leadership",
                chat_type="leadership"
            )
        ]
        
        return HelpContent(
            title=f"🏈 KICKAI Commands - Leadership Chat",
            description=f"Hello {username}! Here are the leadership commands:",
            commands=commands,
            footer="🔐 These commands are only available in the leadership chat."
        )

    def _generate_private_help(self, username: str) -> HelpContent:
        """Generate help content for private chat."""
        commands = [
            CommandInfo(
                name="/help",
                description="Show this help message",
                examples=["/help"],
                permission_level="public",
                chat_type="private"
            ),
            CommandInfo(
                name="/myinfo",
                description="Show your detailed information",
                examples=["/myinfo"],
                permission_level="player",
                chat_type="private"
            )
        ]
        
        return HelpContent(
            title=f"🏈 KICKAI Commands - Private Chat",
            description=f"Hello {username}! Here are the commands available in private chat:",
            commands=commands,
            footer="💬 Use private commands for personal information and updates."
        )

    def format_help_message(self, help_content: HelpContent) -> str:
        """
        Format help content into a user-friendly message.
        
        Args:
            help_content: The help content to format
            
        Returns:
            Formatted help message string
        """
        lines = [
            help_content.title,
            "=" * 50,
            "",
            help_content.description,
            ""
        ]
        
        for cmd in help_content.commands:
            lines.extend([
                f"🔸 **{cmd.name}**",
                f"   {cmd.description}",
                f"   Example: `{cmd.examples[0] if cmd.examples else cmd.name}`",
                ""
            ])
        
        lines.extend([
            "=" * 50,
            help_content.footer
        ])
        
        return "\n".join(lines)