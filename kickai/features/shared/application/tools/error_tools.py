#!/usr/bin/env python3
"""
Error Handling Tools - Clean Architecture Compliant

This module contains CrewAI tools for error handling and user feedback.
These tools follow the clean naming convention: [action]_[entity]_[modifier].
"""

from crewai.tools import tool
from loguru import logger


@tool("show_permission_error")
async def show_permission_error(
    telegram_username: str, chat_type: str, action: str = "perform this action"
) -> str:
    """Display permission denial with context-aware guidance.

    Shows helpful permission error messages based on user context
    and provides actionable next steps for resolution.

    Use when: User lacks required permissions for action
    Required: Valid user and chat context
    Context: Permission validation workflow

    Returns: Context-aware permission denial with guidance
    """
    try:
        # Basic parameter validation (CrewAI handles parameter passing)
        if not telegram_username or not chat_type:
            return "❌ Username and chat type are required"

        # Ensure proper types and defaults
        telegram_username = str(telegram_username)
        chat_type = str(chat_type).lower()
        action = str(action) if action else "perform this action"

        logger.info(f"🚫 Permission denied for {telegram_username} in {chat_type} chat: {action}")

        # Context-aware permission messages with improved guidance
        if chat_type == "main":
            message = f"""🚫 Permission Denied

Sorry {telegram_username}, you don't have permission to {action} in the main chat.

💡 Need Help?
- Some commands are only available to team leadership
- Try using /help to see available commands
- Contact a team administrator for assistance

📍 Your Current Access: Player (main chat)"""
        elif chat_type == "leadership":
            message = f"""🚫 Permission Denied

Sorry {telegram_username}, you don't have sufficient permissions to {action}.

💡 Need Help?
- This action requires higher administrative privileges
- Contact a system administrator for assistance
- Try /help to see available commands

📍 Your Current Access: Leadership (leadership chat)"""
        elif chat_type == "private":
            message = f"""🚫 Permission Denied

Sorry {telegram_username}, you don't have permission to {action} in private chat.

💡 Need Help?
- Some commands are only available in team chats
- Try using /help to see available commands
- Contact team leadership for assistance

📍 Your Current Access: Private chat"""
        else:
            message = f"""🚫 Permission Denied

Sorry {telegram_username}, you don't have permission to {action}.

💡 Need Help?
- Try using /help to see available commands
- Some commands require specific permissions
- Contact team leadership for assistance

📍 Your Current Access: {chat_type} chat"""

        return message

    except Exception as e:
        logger.error(f"❌ Error showing permission message: {e}")
        return f"❌ Error showing permission message: {e!s}"


@tool("show_command_error")
async def show_command_error(
    telegram_username: str, chat_type: str, command: str = "unknown command"
) -> str:
    """Display command availability error with helpful alternatives.

    Shows guidance when commands are not found or unavailable in current context,
    providing suggestions and common alternatives.

    Use when: Command not found or unavailable in current context
    Required: Valid user and chat context
    Context: Command validation workflow

    Returns: Command error with alternatives and suggestions
    """
    try:
        # Basic parameter validation (CrewAI handles parameter passing)
        if not telegram_username or not chat_type:
            return "❌ Username and chat type are required"

        # Ensure proper types and defaults with improved handling
        telegram_username = str(telegram_username)
        chat_type = str(chat_type).lower()
        command = str(command) if command else "unknown command"

        logger.info(f"❓ Command error for {telegram_username} in {chat_type} chat: {command}")

        # Context-aware command error messages with better suggestions
        common_commands = {
            "main": ["/help", "/myinfo", "/ping", "/version", "/addplayer", "/mystatus"],
            "leadership": [
                "/help",
                "/myinfo",
                "/ping",
                "/version",
                "/players",
                "/members",
                "/approve",
            ],
            "private": ["/help", "/myinfo", "/ping", "/version", "/addplayer"],
        }

        chat_commands = common_commands.get(chat_type, ["/help", "/ping", "/version"])

        message = f"""❓ Command Not Available

Sorry {telegram_username}, the command {command} is not available or doesn't exist.

💡 Suggestions:
- Check your spelling: /help instead of /halp
- Use /help to see all available commands
- Some commands are chat-specific (main vs leadership)
- Try typing / to see command suggestions

🔧 Common Commands for {chat_type} chat:
{chr(10).join(f"- {cmd}" for cmd in chat_commands[:4])}

📍 Current Chat: {chat_type}"""

        return message

    except Exception as e:
        logger.error(f"❌ Error showing command help: {e}")
        return f"❌ Error showing command help: {e!s}"


@tool("show_system_error")
async def show_system_error(
    telegram_username: str,
    chat_type: str,
    error_type: str = "system error",
    details: str = "An unexpected error occurred",
) -> str:
    """Display system error with recovery guidance.

    Shows user-friendly system error messages with helpful context
    and actionable recovery steps when system issues occur.

    Use when: System error requiring user notification occurs
    Required: Valid user and chat context
    Context: System error handling workflow

    Returns: System error message with recovery guidance
    """
    try:
        # Basic parameter validation (CrewAI handles parameter passing)
        if not telegram_username or not chat_type:
            return "❌ Username and chat type are required"

        # Ensure proper types and defaults with sanitization
        telegram_username = str(telegram_username)[:50]  # Limit username length for security
        chat_type = str(chat_type).lower()
        error_type = str(error_type)[:100] if error_type else "system error"
        details = str(details)[:500] if details else "An unexpected error occurred"

        logger.warning(
            f"⚠️ System error for {telegram_username} in {chat_type} chat: {error_type} - {details}"
        )

        # Enhanced system error message with recovery guidance
        message = f"""⚠️ System Error

Sorry {telegram_username}, a {error_type} has occurred.

📋 Details: {details}

💡 What You Can Do:
- Try your request again in a few moments
- Check if the system is experiencing issues with /ping
- Use /help to see available commands
- Contact team leadership if the problem persists

🔧 Quick Fixes:
- Refresh your connection
- Try a simpler command first
- Check system status with /version

📍 Current Chat: {chat_type}
🏷️ Error Type: {error_type}

We apologize for the inconvenience and are working to resolve this issue."""

        return message

    except Exception as e:
        logger.error(f"❌ Error showing system error message: {e}")
        return f"❌ Error showing system error message: {e!s}"


@tool("show_validation_error")
async def show_validation_error(
    telegram_username: str,
    chat_type: str,
    field_name: str = "input field",
    issue: str = "validation failed",
    suggestion: str = "Please check your input and try again",
) -> str:
    """Display validation error with specific correction guidance.

    Shows clear validation error feedback with specific guidance
    on what went wrong and how to fix input issues.

    Use when: User input validation fails
    Required: Valid user and chat context
    Context: Input validation workflow

    Returns: Validation error with specific correction guidance
    """
    try:
        # Basic parameter validation (CrewAI handles parameter passing)
        if not telegram_username or not chat_type:
            return "❌ Username and chat type are required"

        # Ensure proper types and defaults with improved security
        telegram_username = str(telegram_username)[:50]  # Security limit
        chat_type = str(chat_type).lower()
        field_name = str(field_name)[:100] if field_name else "input field"
        issue = str(issue)[:200] if issue else "validation failed"
        suggestion = (
            str(suggestion)[:300] if suggestion else "Please check your input and try again"
        )

        logger.info(
            f"⚠️ Validation error for {telegram_username} in {chat_type} chat: {field_name} - {issue}"
        )

        # Enhanced validation error message with specific guidance
        message = f"""⚠️ Validation Error

Sorry {telegram_username}, there's an issue with your {field_name}.

❌ Problem: {issue}

💡 How to Fix:
{suggestion}

🔧 Additional Help:
- Make sure all required fields are filled
- Check the format of your input (numbers, text, etc.)
- Use /help to see command requirements and examples
- Try the command again with corrected input
- Contact team leadership if you need assistance

📍 Current Chat: {chat_type}
🏷️ Field: {field_name}"""

        return message

    except Exception as e:
        logger.error(f"❌ Error showing validation error message: {e}")
        return f"❌ Error showing validation error message: {e!s}"
