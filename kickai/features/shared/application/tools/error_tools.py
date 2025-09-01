"""Error Handling Tools - Clean Architecture Compliant

This module contains CrewAI tools for error handling and user feedback.
These tools follow the clean naming convention: [action]_[entity]_[modifier].
"""

from crewai.tools import tool
from typing import Any


@tool("show_error_permission")
async def show_error_permission(
    telegram_id: str,
    team_id: str, 
    username: str,
    chat_type: str,
    action: str = "perform this action"
) -> str:
    """Show permission denied error message with user-friendly guidance.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        action: The action that was denied (optional)
    
    Returns:
        Formatted permission denied message
    """
    try:
        # Format user-friendly error message
        if chat_type == "main":
            message = f"""🚫 **Permission Denied**

Sorry {username}, you don't have permission to {action} in the main chat.

💡 **Need Help?**
- Some commands are only available to team leadership
- Try using `/help` to see available commands
- Contact a team administrator for assistance

📍 **Your Current Access**: Player ({chat_type} chat)"""
        
        elif chat_type == "leadership":
            message = f"""🚫 **Permission Denied**

Sorry {username}, you don't have sufficient permissions to {action}.

💡 **Need Help?**
- This action requires higher administrative privileges
- Contact a system administrator for assistance
- Try `/help` to see available commands

📍 **Your Current Access**: Leadership ({chat_type} chat)"""
        
        else:
            message = f"""🚫 **Permission Denied**

Sorry {username}, you don't have permission to {action}.

💡 **Need Help?**
- Try using `/help` to see available commands
- Some commands require specific permissions
- Contact team leadership for assistance

📍 **Your Current Access**: {chat_type} chat"""

        return message
        
    except Exception as e:
        return f"❌ Error showing permission message: {str(e)}"


@tool("show_error_command") 
async def show_error_command(
    telegram_id: str,
    team_id: str,
    username: str, 
    chat_type: str,
    command: str = "unknown command"
) -> str:
    """Show command not available error message with helpful suggestions.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        command: The command that was not found (optional)
    
    Returns:
        Formatted command unavailable message with suggestions
    """
    try:
        # Format helpful error message with suggestions
        message = f"""❓ **Command Not Available**

Sorry {username}, the command `{command}` is not available or doesn't exist.

💡 **Suggestions**:
- Check your spelling: `/help` instead of `/halp`
- Use `/help` to see all available commands
- Some commands are chat-specific (main vs leadership)
- Try typing `/` to see command suggestions

🔧 **Common Commands**:
- `/help` - Show help and available commands
- `/myinfo` - Get your information and status
- `/ping` - Test system connectivity
- `/version` - Show system version

📍 **Current Chat**: {chat_type}"""

        return message
        
    except Exception as e:
        return f"❌ Error showing command help: {str(e)}"