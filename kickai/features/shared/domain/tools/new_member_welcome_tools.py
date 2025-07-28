#!/usr/bin/env python3
"""
New Member Welcome Tools

This module provides tools for generating welcome messages for new members joining the chat.
"""

from kickai.utils.crewai_tool_decorator import tool
from loguru import logger
from kickai.core.enums import ChatType as ChatTypeEnum
from kickai.utils.tool_helpers import (
    format_tool_error,
    validate_required_input,
)
from kickai.core.constants import normalize_chat_type


@tool("get_new_member_welcome_message")
def get_new_member_welcome_message(
    username: str, 
    chat_type: str, 
    team_id: str, 
    user_id: str
) -> str:
    """
    Generate a welcome message for new members joining the chat.
    
    Args:
        username: New member's username
        chat_type: Chat type (main, leadership, private)
        team_id: Team ID
        user_id: User ID
        
    Returns:
        Welcome message for the new member
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(username, "Username")
        if validation_error:
            return format_tool_error(validation_error)

        validation_error = validate_required_input(chat_type, "Chat Type")
        if validation_error:
            return format_tool_error(validation_error)

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return format_tool_error(validation_error)

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return format_tool_error(validation_error)

        # Normalize chat type
        chat_type_enum = normalize_chat_type(chat_type)
        
        # Generate welcome message based on chat type
        if chat_type_enum == ChatTypeEnum.MAIN:
            welcome_message = f"""
🎉 **WELCOME TO THE TEAM, {username.upper()}!**

👋 **Welcome to KICKAI!** We're excited to have you join our football community!

⚽ **WHAT YOU CAN DO HERE:**
• Register as a player with `/register [player_id]`
• Check your status with `/myinfo`
• See available commands with `/help`
• View active players with `/list`

🔗 **GETTING STARTED:**
1. **Register as a player** - Use `/register` followed by your player ID
2. **Check your status** - Use `/myinfo` to see your current registration
3. **Explore commands** - Use `/help` to see all available options

📱 **NEED HELP?**
• Type `/help` for command information
• Contact team leadership for assistance
• Check pinned messages for important updates

Welcome aboard! Let's make this team amazing! ⚽🔥
            """
        elif chat_type_enum == ChatTypeEnum.LEADERSHIP:
            welcome_message = f"""
🎉 **WELCOME TO LEADERSHIP, {username.upper()}!**

👥 **Welcome to the KICKAI Leadership Team!** You're now part of our administrative team.

🛠️ **ADMINISTRATIVE FEATURES:**
• Manage players with `/add`, `/approve`, `/listmembers`
• View pending players with `/pending`
• Schedule training with `/scheduletraining`
• Manage matches with `/creatematch`, `/squadselect`
• Send announcements with `/announce`

📋 **QUICK START:**
1. **View pending players** - Use `/pending` to see who needs approval
2. **Add new players** - Use `/add [name] [phone] [position]`
3. **Approve players** - Use `/approve [player_id]`
4. **Explore admin commands** - Use `/help` for full list

🎯 **TEAM MANAGEMENT:**
• Player registration and approval
• Training session management
• Match scheduling and squad selection
• Team communication and announcements

Welcome to the leadership team! Let's build something great together! 👥🌟
            """
        else:  # PRIVATE
            welcome_message = f"""
🎉 **WELCOME, {username.upper()}!**

👋 **Welcome to KICKAI!** You're now connected to our football management system.

⚽ **AVAILABLE COMMANDS:**
• Get help with `/help`
• Check your status with `/myinfo`
• Register as a player with `/register`

🔗 **NEXT STEPS:**
1. Join the main team chat for full access
2. Register as a player or team member
3. Start participating in team activities

Welcome! We're glad to have you on board! ⚽
            """

        return welcome_message

    except Exception as e:
        logger.error(f"Error generating new member welcome message: {e}")
        return format_tool_error(f"Failed to generate welcome message: {e}")