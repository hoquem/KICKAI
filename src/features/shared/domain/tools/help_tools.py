#!/usr/bin/env python3
"""
Help Tools for KICKAI

This module provides tools for generating help responses and command information.
"""

import logging
from typing import Dict, Any, List, Tuple
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool

from core.constants import (
    get_commands_for_chat_type,
    get_command_by_name,
    normalize_chat_type,
    get_chat_type_display_name,
    ChatType
)
from core.enums import ChatType as ChatTypeEnum

logger = logging.getLogger(__name__)


class GenerateHelpResponseTool(BaseTool):
    """Tool to generate comprehensive help responses based on chat type and user context."""
    
    name: str = "FINAL_HELP_RESPONSE"
    description: str = """
    Generate a comprehensive help response for users based on their chat type and context.
    
    This tool should be used when users ask for help, show commands, or need guidance.
    The response should be tailored to the specific chat type (main chat vs leadership chat)
    and include all relevant commands with descriptions.
    """
    
    def __init__(self):
        super().__init__()
    
    def _run(self, context: Dict[str, Any]) -> str:
        """
        Generate help response based on context.
        
        Args:
            context: Dictionary containing:
                - chat_type: Chat type (string or enum)
                - user_id: User ID
                - team_id: Team ID
                - username: Username (optional)
                - message_text: Original message (optional)
        
        Returns:
            Formatted help response string
        """
        try:
            # Extract context
            chat_type = context.get('chat_type', 'main')
            user_id = context.get('user_id', 'Unknown')
            username = context.get('username', 'Unknown')
            
            logger.info(f"🔧 [TOOL DEBUG] Generating help for chat_type: {chat_type}, user: {user_id}")
            
            # Normalize chat type to enum
            chat_type_enum = normalize_chat_type(chat_type)
            
            # Get commands for this chat type
            commands = get_commands_for_chat_type(chat_type_enum)
            
            # Generate help message
            help_message = self._format_help_message(chat_type_enum, commands, username)
            
            logger.info(f"🔧 [TOOL DEBUG] Final response preview: {help_message[:100]}...")
            
            return help_message
            
        except Exception as e:
            logger.error(f"Error generating help response: {e}", exc_info=True)
            return f"❌ Error generating help: {str(e)}"
    
    def _format_help_message(self, chat_type: ChatTypeEnum, commands: List, username: str) -> str:
        """Format the help message with commands organized by category."""
        try:
            # Get chat type display name
            chat_display_name = get_chat_type_display_name(chat_type)
            
            # Start building the message
            message_parts = [
                f"🤖 KICKAI Help System",
                f"Your Context: {chat_display_name.upper()} (User: {username})",
                f"📋 Available Commands for {chat_display_name}:",
                ""
            ]
            
            # Group commands by feature/category
            command_categories = self._group_commands_by_category(commands)
            
            # Add each category
            for category, category_commands in command_categories.items():
                if category_commands:
                    message_parts.append(f"{category}:")
                    for cmd in category_commands:
                        message_parts.append(f"• {cmd.name} - {cmd.description}")
                    message_parts.append("")
            
            # Add footer
            message_parts.extend([
                "💡 Use /help [command] for detailed help on any command.",
                "---",
                "💡 Need more help?",
                "• Type /help [command] for detailed help",
                "• Contact team admin for support"
            ])
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Error formatting help message: {e}", exc_info=True)
            return f"❌ Error formatting help message: {str(e)}"
    
    def _group_commands_by_category(self, commands: List) -> Dict[str, List]:
        """Group commands by their feature/category."""
        categories = {
            "Player Commands": [],
            "Leadership Commands": [],
            "Match Management": [],
            "Attendance": [],
            "Payments": [],
            "Communication": [],
            "Team Administration": [],
            "System": [],
            "Health & Monitoring": []
        }
        
        # Map features to display categories
        feature_to_category = {
            "player_registration": "Player Commands",
            "match_management": "Match Management",
            "attendance_management": "Attendance",
            "payment_management": "Payments",
            "communication": "Communication",
            "team_administration": "Team Administration",
            "health_monitoring": "Health & Monitoring",
            "system_infrastructure": "System",
            "shared": "System"
        }
        
        for cmd in commands:
            category = feature_to_category.get(cmd.feature, "System")
            categories[category].append(cmd)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


class GetAvailableCommandsTool(BaseTool):
    """Tool to get available commands for a specific chat type."""
    
    name: str = "get_available_commands"
    description: str = """
    Get all available commands for a specific chat type.
    
    Args:
        chat_type: The chat type (main_chat, leadership_chat, or private)
    
    Returns:
        List of available commands with descriptions
    """
    
    def __init__(self):
        super().__init__()
    
    def _run(self, chat_type: str) -> str:
        """
        Get available commands for chat type.
        
        Args:
            chat_type: Chat type string
        
        Returns:
            Formatted string with available commands
        """
        try:
            # Normalize chat type
            chat_type_enum = normalize_chat_type(chat_type)
            
            # Get commands
            commands = get_commands_for_chat_type(chat_type_enum)
            
            # Format response
            if not commands:
                return f"No commands available for chat type: {chat_type}"
            
            response_parts = [f"Available commands for {get_chat_type_display_name(chat_type_enum)}:"]
            
            for cmd in commands:
                response_parts.append(f"• {cmd.name} - {cmd.description}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error getting available commands: {e}", exc_info=True)
            return f"❌ Error getting commands: {str(e)}"


class GetCommandHelpTool(BaseTool):
    """Tool to get detailed help for a specific command."""
    
    name: str = "get_command_help"
    description: str = """
    Get detailed help for a specific command.
    
    Args:
        command_name: The command name (e.g., /register, /help)
        chat_type: The chat type context
    
    Returns:
        Detailed help information for the command
    """
    
    def __init__(self):
        super().__init__()
    
    def _run(self, command_name: str, chat_type: str = "main") -> str:
        """
        Get detailed help for a command.
        
        Args:
            command_name: Command name
            chat_type: Chat type context
        
        Returns:
            Detailed help string
        """
        try:
            # Get command definition
            cmd = get_command_by_name(command_name)
            
            if not cmd:
                return f"❌ Command '{command_name}' not found."
            
            # Check if command is available in this chat type
            chat_type_enum = normalize_chat_type(chat_type)
            if chat_type_enum not in cmd.chat_types:
                return f"❌ Command '{command_name}' is not available in {get_chat_type_display_name(chat_type_enum)}."
            
            # Build detailed help
            help_parts = [
                f"📖 Help for {cmd.name}",
                f"Description: {cmd.description}",
                f"Permission Level: {cmd.permission_level.value}",
                f"Available in: {', '.join(get_chat_type_display_name(ct) for ct in cmd.chat_types)}",
                f"Feature: {cmd.feature}",
                ""
            ]
            
            if cmd.examples:
                help_parts.append("Examples:")
                for example in cmd.examples:
                    help_parts.append(f"• {example}")
                help_parts.append("")
            
            help_parts.append("💡 Use this command in the appropriate chat type.")
            
            return "\n".join(help_parts)
            
        except Exception as e:
            logger.error(f"Error getting command help: {e}", exc_info=True)
            return f"❌ Error getting command help: {str(e)}" 