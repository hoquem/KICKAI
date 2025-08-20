#!/usr/bin/env python3
"""
Permission Tools - Permission Denied Messages and Access Control

This module provides tools for handling permission denied scenarios and
providing user-friendly error messages when commands are not accessible.
"""

from loguru import logger
from crewai.tools import tool
from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response


@tool("permission_denied_message", result_as_answer=True)
async def permission_denied_message(
    telegram_id: int,
    team_id: str, 
    username: str,
    chat_type: str,
    command_attempted: str,
    required_permission: str = "Unknown"
) -> str:
    """
    Generate a user-friendly permission denied message.
    
    This tool should be used when a user attempts a command they don't have
    permission to execute. It provides clear guidance on why access was denied
    and what the user can do to get access.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type where command was attempted
        command_attempted: The command that was denied
        required_permission: The permission level required
        
    Returns:
        User-friendly permission denied message
    """
    try:
        logger.info(f"🔧 [PERMISSION] Generating permission denied message for {username}, command: {command_attempted}")
        
        # Base permission denied message
        message_parts = [
            "❌ **Access Denied**",
            "",
            f"🚫 **Command**: {command_attempted}",
            f"🔒 **Required Access**: {required_permission}",
            f"👤 **Your Context**: {chat_type.title()} Chat"
        ]
        
        # Add specific guidance based on command and context
        if chat_type.lower() in ["main", "main_chat"]:
            if required_permission.lower() in ["leadership", "admin"]:
                message_parts.extend([
                    "",
                    "💡 **Why was this blocked?**",
                    f"• {command_attempted} requires leadership or admin access",
                    "• This command is only available in the leadership chat",
                    "",
                    "🔧 **What you can do:**",
                    "• Contact your team leadership for access",
                    "• Ask leadership to promote you if appropriate",
                    "• Use leadership chat if you already have access"
                ])
            else:
                message_parts.extend([
                    "",
                    "💡 **Why was this blocked?**",
                    f"• You don't have the required permissions for {command_attempted}",
                    "",
                    "🔧 **What you can do:**",
                    "• Contact your team admin for access",
                    "• Check if you're registered as a player or team member",
                    "• Use /help to see available commands"
                ])
        
        elif chat_type.lower() in ["leadership", "leadership_chat"]:
            message_parts.extend([
                "",
                "💡 **Why was this blocked?**",
                f"• {command_attempted} requires higher permissions than your current role",
                "",
                "🔧 **What you can do:**",
                "• Contact your team admin for access",
                "• Verify your leadership role is properly configured",
                "• Use /help to see available commands"
            ])
        
        else:  # Private chat
            message_parts.extend([
                "",
                "💡 **Why was this blocked?**",
                f"• {command_attempted} is not available in private chat",
                "",
                "🔧 **What you can do:**",
                "• Use the main team chat for player commands",
                "• Use the leadership chat for admin commands",
                "• Use /help to see available commands"
            ])
        
        # Add footer
        message_parts.extend([
            "",
            "---",
            "💬 **Need Help?**",
            "• Type /help for available commands",
            "• Contact your team leadership",
            "• Check pinned messages for team info"
        ])
        
        permission_denied_text = "\n".join(message_parts)
        
        logger.info(f"✅ [PERMISSION] Generated permission denied message for {username}")
        return create_json_response(ResponseStatus.SUCCESS, data=permission_denied_text)
        
    except Exception as e:
        logger.error(f"❌ [PERMISSION] Error generating permission denied message: {e}")
        return create_json_response(
            ResponseStatus.ERROR, 
            message=f"❌ Access denied for {command_attempted}. Contact team admin for support."
        )


@tool("command_not_available", result_as_answer=True)
async def command_not_available(
    telegram_id: int,
    team_id: str,
    username: str, 
    chat_type: str,
    command_attempted: str
) -> str:
    """
    Generate a message for commands that are not available in the current context.
    
    This is different from permission denied - this is when a command simply
    doesn't exist or is not available in the current chat type.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type where command was attempted
        command_attempted: The command that was not found
        
    Returns:
        User-friendly command not available message
    """
    try:
        logger.info(f"🔧 [COMMAND] Generating command not available message for {username}, command: {command_attempted}")
        
        message_parts = [
            "❓ **Command Not Found**",
            "",
            f"🔍 **Command**: {command_attempted}",
            f"📍 **Context**: {chat_type.title()} Chat",
            "",
            "💡 **Possible Issues:**",
            "• Command doesn't exist or was mistyped",
            f"• Command not available in {chat_type.lower()} chat",
            "• You might be looking for a different command",
            "",
            "🔧 **What you can try:**",
            "• Check your spelling and try again",
            "• Use /help to see all available commands",
            "• Try the command in a different chat if appropriate",
            "• Contact team leadership if you need assistance",
            "",
            "💬 **Popular Commands:**",
            "• /help - Show available commands",
            "• /myinfo - Show your status", 
            "• /list - Show team/player list",
            "• /ping - Check system status"
        ]
        
        command_not_found_text = "\n".join(message_parts)
        
        logger.info(f"✅ [COMMAND] Generated command not available message for {username}")
        return create_json_response(ResponseStatus.SUCCESS, data=command_not_found_text)
        
    except Exception as e:
        logger.error(f"❌ [COMMAND] Error generating command not available message: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message=f"❓ Command {command_attempted} not found. Use /help for available commands."
        )