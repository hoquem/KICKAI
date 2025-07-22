#!/usr/bin/env python3
"""
Help tools for the KICKAI system.
"""

from typing import Optional, List
from crewai.tools import tool
from loguru import logger

from src.core.enums import PermissionLevel, ChatType
from src.core.command_registry_initializer import get_initialized_command_registry


def _determine_user_permissions(user_status: str, chat_type: str) -> List[PermissionLevel]:
    """
    Determine user permissions based on status and chat type.
    
    Args:
        user_status: The user's status (e.g., 'player', 'leadership', 'admin')
        chat_type: The chat type (e.g., 'main_chat', 'leadership_chat')
    
    Returns:
        List of permission levels the user has
    """
    permissions = [PermissionLevel.PUBLIC]  # Everyone has public permissions
    
    # Add permissions based on user status
    if user_status in ['player', 'active', 'approved']:
        permissions.append(PermissionLevel.PLAYER)
    elif user_status in ['leadership', 'admin', 'manager']:
        permissions.append(PermissionLevel.LEADERSHIP)
        permissions.append(PermissionLevel.PLAYER)
    elif user_status == 'admin':
        permissions.extend([PermissionLevel.ADMIN, PermissionLevel.LEADERSHIP, PermissionLevel.PLAYER])
    
    # Add permissions based on chat type
    if chat_type == ChatType.LEADERSHIP.value:
        permissions.append(PermissionLevel.LEADERSHIP)
    
    return list(set(permissions))  # Remove duplicates


@tool("get_user_status")
def get_user_status_tool(user_id: str, team_id: Optional[str] = None) -> str:
    """
    Get the status of a user in the system. Requires: user_id
    
    Args:
        user_id: The user ID to check
        team_id: Optional team ID for context
    
    Returns:
        User status (registered, unregistered, admin, etc.)
    """
    try:
        # Simple status check - in a real implementation, this would query the database
        # For now, return a basic status based on user_id format
        if user_id and len(user_id) > 0:
            # This is a simplified version - in practice, you'd query the database
            # For now, assume all users with valid IDs are registered
            logger.info(f"ℹ️ Checking status for user {user_id}")
            return "registered"
        else:
            logger.info(f"ℹ️ User {user_id} not found, returning 'unregistered'")
            return "unregistered"
            
    except Exception as e:
        logger.error(f"❌ Failed to get user status for {user_id}: {e}")
        return "unknown"


@tool("get_available_commands")
def get_available_commands(user_id: str, chat_type: str, team_id: Optional[str] = None) -> str:
    """
    Get available commands based on user status and chat type. Requires: user_id, chat_type
    
    Args:
        user_id: The user ID to get commands for
        chat_type: The chat type (main_chat or leadership_chat)
        team_id: Optional team ID for context
    
    Returns:
        List of available commands for the user
    """
    try:
        # Simple command mapping based on chat type - no service dependencies
        if chat_type.lower() == "main_chat":
            commands = {
                "Player Management": [
                    ("/register", "Register as a new player"),
                    ("/myinfo", "View your player information"),
                    ("/status", "Check your current status")
                ],
                "Team Information": [
                    ("/list", "List all active players"),
                    ("/help", "Show available commands")
                ]
            }
        elif chat_type.lower() == "leadership_chat":
            commands = {
                "Player Management": [
                    ("/approve", "Approve a player for matches"),
                    ("/reject", "Reject a player application"),
                    ("/pending", "List players awaiting approval")
                ],
                "Team Administration": [
                    ("/list", "List all players with status"),
                    ("/addplayer", "Add a player directly"),
                    ("/addmember", "Add a team member")
                ],
                "Help": [
                    ("/help", "Show leadership commands")
                ]
            }
        else:
            commands = {
                "General": [
                    ("/help", "Show available commands")
                ]
            }
        
        # Format the response with plain text and emojis
        chat_display = "Main Chat" if chat_type.lower() == "main_chat" else "Leadership Chat"
        result = f"📋 Available Commands for {chat_display}:\n\n"
        
        for category, cmd_list in commands.items():
            result += f"{category}:\n"
            for cmd_name, cmd_desc in cmd_list:
                # Use plain text formatting
                result += f"• {cmd_name} - {cmd_desc}\n"
            result += "\n"
        
        result += "💡 Use /help [command] for detailed help on any command."
        
        logger.info(f"✅ Successfully retrieved commands for user {user_id} in {chat_type}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get available commands: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return f"❌ {error_msg}"


@tool("format_help_message")
def format_help_message(commands_text: str, user_context: str = "") -> str:
    """
    Format a help message with proper styling and context. Requires: commands_text
    
    Args:
        commands_text: The raw commands text to format
        user_context: Optional user context to include
    
    Returns:
        Formatted help message
    """
    try:
        # Add header
        header = "🤖 KICKAI Help System\n\n"
        
        # Add user context if provided
        context_section = ""
        if user_context:
            context_section = f"Your Context: {user_context}\n\n"
        
        # Add the commands
        commands_section = commands_text
        
        # Add footer
        footer = "\n---\n💡 Need more help?\n• Type /help [command] for detailed help\n• Contact team admin for support"
        
        # Combine all sections
        formatted_message = header + context_section + commands_section + footer
        
        logger.info("✅ Successfully formatted help message")
        return formatted_message
        
    except Exception as e:
        error_msg = f"Failed to format help message: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return f"❌ {error_msg}" 