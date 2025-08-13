#!/usr/bin/env python3
"""
Player Administration Commands

This module provides commands for player management by team administrators,
including adding new players with invite link generation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# PLAYER MANAGEMENT COMMANDS
# ============================================================================


@command(
    name="/addplayer",
    description="Add a new player and generate invite link (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=[
        "/addplayer \"John Smith\" \"+447123456789\"",
        "/addplayer \"Sarah Johnson\" \"07987654321\""
    ],
    parameters={
        "player_name": "Player's full name (use quotes if contains spaces)",
        "phone_number": "Player's phone number (UK format: +447123456789 or 07123456789)",
    },
    help_text="""
🏃‍♂️ Add Player (Leadership Only)

Add a new player to the team and generate an invite link for them to join the main chat.

Usage:
/addplayer <player_name> <phone_number>

Examples:
/addplayer "John Smith" "+447123456789"
/addplayer "Sarah Johnson" "07987654321"

Phone Number Format:
• UK format required: +447123456789 or 07123456789
• Must be unique within the team

What happens:
1. Player record is created with "pending_activation" status
2. Secure one-time invite link is generated (expires in 7 days)
3. You receive formatted message with invite link to send to player
4. Player uses invite link to join main chat
5. Player uses /update command to set position and complete profile

Workflow:
• Admin: Uses /addplayer command
• System: Creates player + generates invite link
• Admin: Sends invite link to player
• Player: Joins via link → uses /update → ready to play!

💡 Notes:
• Command only works in leadership chat
• Replaces the old /register command (removed for clarity)
• Players don't need to know their position initially
• Phone number validation prevents duplicates
    """,
)
async def handle_addplayer_command(update, context, **kwargs):
    """
    Handle /addplayer command for adding new players with invite links.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional context including team_id, user permissions, etc.
    
    Returns:
        Response message with player details and invite link
    """
    try:
        from kickai.core.dependency_container import get_container
        from kickai.core.types import TelegramMessage
        from kickai.core.enums import ChatType
        from kickai.utils.validation_utils import sanitize_input
        import re
        
        # Get message info
        message = update.message
        chat_id = str(message.chat_id)
        telegram_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Get team_id from context
        team_id = kwargs.get("team_id")
        if not team_id:
            return "❌ Team ID not available. Please contact system administrator."
        
        # Parse command arguments
        command_text = message.text.strip()
        
        # Remove the command name to get arguments
        if command_text.startswith("/addplayer"):
            args_text = command_text[10:].strip()  # Remove "/addplayer"
        else:
            return "❌ Invalid command format."
        
        if not args_text:
            return """❌ **Missing Arguments**

Usage: `/addplayer <player_name> <phone_number>`

Examples:
• `/addplayer "John Smith" "+447123456789"`
• `/addplayer "Sarah Johnson" "07987654321"`

💡 Use quotes around names with spaces."""
        
        # Parse arguments - handle quoted names and phone numbers
        # Pattern to match quoted strings and unquoted words
        pattern = r'"([^"]*)"|\S+'
        matches = re.findall(pattern, args_text)
        
        # Extract arguments (quoted strings are in group 1, unquoted in group 0)
        args = []
        for match in re.finditer(pattern, args_text):
            if match.group(1):  # Quoted string
                args.append(match.group(1))
            else:  # Unquoted string
                args.append(match.group(0))
        
        if len(args) < 2:
            return """❌ **Insufficient Arguments**

Usage: `/addplayer <player_name> <phone_number>`

You provided: """ + str(len(args)) + """ argument(s)
Required: 2 arguments (player name and phone number)

Examples:
• `/addplayer "John Smith" "+447123456789"`
• `/addplayer "Sarah Johnson" "07987654321"`"""
        
        if len(args) > 2:
            return """❌ **Too Many Arguments**

Usage: `/addplayer <player_name> <phone_number>`

You provided: """ + str(len(args)) + """ argument(s)
Expected: 2 arguments (player name and phone number)

💡 Use quotes around names with spaces:
• Correct: `/addplayer "John Smith" "+447123456789"`
• Incorrect: `/addplayer John Smith +447123456789`"""
        
        player_name = sanitize_input(args[0], 100)
        phone_number = sanitize_input(args[1], 20)
        
        # Validate inputs
        if not player_name or not player_name.strip():
            return "❌ Player name cannot be empty."
        
        if not phone_number or not phone_number.strip():
            return "❌ Phone number cannot be empty."
        
        if len(player_name.strip()) < 2:
            return "❌ Player name must be at least 2 characters long."
        
        # Route to CrewAI agent via AgenticMessageRouter
        container = get_container()
        router = container.get_agentic_message_router()
        
        # Create structured message for the agent
        agent_message_text = f"/addplayer {player_name} {phone_number}"
        
        telegram_message = TelegramMessage(
            telegram_id=telegram_id,
            text=agent_message_text,
            chat_id=chat_id,
            chat_type=ChatType.LEADERSHIP,
            team_id=team_id,
            username=username,
            raw_update=update
        )
        
        # Route to CrewAI system
        response = await router.route_message(telegram_message)
        
        if response and response.success:
            return response.message
        else:
            error_msg = response.error if response else "Unknown error"
            return f"❌ Failed to add player: {error_msg}"
            
    except Exception as e:
        from loguru import logger
        logger.error(f"❌ Error in handle_addplayer_command: {e}")
        return f"❌ System error: {str(e)}"