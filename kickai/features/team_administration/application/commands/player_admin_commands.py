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
        '/addplayer "John Smith" "+447123456789"',  # Quoted name (recommended)
        "/addplayer John +447123456789",  # Single name (works too)
        "/addplayer John Smith 07123456789",  # Unquoted multi-word name (smart parsing)
    ],
    parameters={
        "player_name": "Player's full name (use quotes if contains spaces)",
        "phone_number": "Player's phone number (UK format: +447123456789 or 07123456789)",
    },
    help_text="""
🏃‍♂️ Add Player (Leadership Only)

Add a new player to the team and generate an invite link for them to join the main chat.

📝 Flexible Usage:
/addplayer <player_name> <phone_number>

✅ All these formats work:
• /addplayer "John Smith" "+447123456789" (quoted - best for names with spaces)
• /addplayer John +447123456789 (unquoted single name)
• /addplayer John Smith 07123456789 (smart parsing - detects phone at end)

📱 Phone Number Format:
• UK format: +447123456789 or 07123456789
• Must be unique within the team

⚡ What happens:
1. Player record created with "pending_activation" status
2. Secure invite link generated (expires in 7 days)
3. You get formatted message with link to send to player
4. Player joins via link → uses /update → ready to play!

💡 Smart Features:
• Automatically detects names vs phone numbers
• Works with or without quotes around names
• Handles multi-word names intelligently
• Phone number validation prevents duplicates
• Only works in leadership chat
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
        from kickai.core.enums import ChatType
        from kickai.core.types import TelegramMessage
        from kickai.utils.validation_utils import sanitize_input

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
            return """❌ Missing Arguments

Usage: /addplayer <player_name> <phone_number>

Examples:
• /addplayer "John Smith" "+447123456789"
• /addplayer "Sarah Johnson" "07987654321"

💡 Use quotes around names with spaces."""

        # Parse arguments using simplified parser
        player_name, phone_number = parse_addplayer_args(args_text)

        if not player_name or not phone_number:
            return (
                """❌ Invalid Format

I need both a player name and phone number.

💡 Examples that work:
• /addplayer John Smith +447123456789
• /addplayer "John Smith" +447123456789
• /addplayer John +447123456789

📝 What you provided: """
                + args_text
                + """
🎯 What I need: Player name + phone number (phone number should be last)"""
            )

        player_name = sanitize_input(player_name, 100)
        phone_number = sanitize_input(phone_number, 20)

        # Validate inputs using configuration constants
        from kickai.utils.constants import (
            ERROR_MESSAGES,
            PLAYER_MIN_NAME_LENGTH,
        )

        if not player_name or not player_name.strip():
            return ERROR_MESSAGES["MISSING_ARGUMENTS"] + f"\n\n📝 What you provided: {args_text}"

        # Validate name length
        if len(player_name.strip()) < PLAYER_MIN_NAME_LENGTH:
            return (
                ERROR_MESSAGES["NAME_TOO_SHORT"].format(min_length=PLAYER_MIN_NAME_LENGTH)
                + f"\n\n📝 What you provided: {args_text}"
            )

        # Validate phone number format using standard phone utils
        from kickai.utils.phone_utils import is_valid_phone

        if not is_valid_phone(phone_number):
            return ERROR_MESSAGES["INVALID_PHONE_FORMAT"].format(phone=phone_number)

        # Route to CrewAI agent via AgenticMessageRouter
        from kickai.agents.agentic_message_router import AgenticMessageRouter

        router = AgenticMessageRouter(team_id)

        # Create structured message for the agent
        agent_message_text = f"/addplayer {player_name} {phone_number}"

        telegram_message = TelegramMessage(
            telegram_id=telegram_id,
            text=agent_message_text,
            chat_id=chat_id,
            chat_type=ChatType.LEADERSHIP,
            team_id=team_id,
            username=username,
            raw_update=update,
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
        return ERROR_MESSAGES["ADDPLAYER_SYSTEM_ERROR"].format(error=str(e))


def parse_addplayer_args(args_text: str) -> tuple[str, str]:
    """
    🧠 AI EXPERT: Simplified Argument Parser

    PURPOSE: Parse /addplayer command arguments with intelligent phone number detection.

    PARSING STRATEGY:
    1. Split arguments by whitespace
    2. Identify phone number (last token matching phone pattern)
    3. Combine remaining tokens as player name
    4. Validate both components exist

    SUPPORTED FORMATS:
    - "John Smith +447123456789" → ("John Smith", "+447123456789")
    - "John +447123456789" → ("John", "+447123456789")
    - "John Smith 07123456789" → ("John Smith", "07123456789")

    Args:
        args_text: Raw argument text after /addplayer command

    Returns:
        Tuple of (player_name, phone_number) or (None, None) if parsing fails

    🎯 AI AGENT USAGE:
    - Use this function to parse user input before calling add_player tool
    - Handle (None, None) return as parsing failure
    - Provide clear error message for parsing failures
    """
    if not args_text or not args_text.strip():
        return None, None

    args_text = args_text.strip()
    parts = args_text.split()

    if len(parts) < 2:
        return None, None

    # Find phone number (last part that looks like a phone number)
    phone_number = None
    name_parts = []

    # Import standard phone validation
    from kickai.utils.phone_utils import is_valid_phone

    for part in parts:
        if is_valid_phone(part):
            phone_number = part
        else:
            name_parts.append(part)

    if not phone_number or not name_parts:
        return None, None

    player_name = " ".join(name_parts)
    return player_name, phone_number
