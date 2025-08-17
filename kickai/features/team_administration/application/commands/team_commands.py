#!/usr/bin/env python3
"""
Team Administration Commands

This module registers all team administration related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType, MemberRole
from kickai.core.types import TelegramMessage
# AgenticMessageRouter import moved to function level to avoid circular imports
from kickai.utils.constants import ERROR_MESSAGES, PLAYER_MIN_NAME_LENGTH, EMAIL_PATTERN, VALID_TEAM_MEMBER_ROLES
from kickai.utils.validation_utils import sanitize_input
from kickai.utils.phone_utils import is_valid_phone
from loguru import logger
import re

# ============================================================================
# TEAM MANAGEMENT COMMANDS
# ============================================================================


@command(
    name="/addmember",
    description="Add a team member (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=["/addmember", "/addmember Sarah Johnson +447987654321"],
    parameters={
        "name": "Team member's full name",
        "phone": "Team member's phone number",
    },
    help_text="""
👔 Add Team Member (Leadership Only)

Add a new team member (coach, manager, etc.) to the team.

Usage:
/addmember [name] [phone]

Example:
/addmember Sarah Johnson +447987654321

What happens:
1. Team member is added to the system with default "Team Member" role
2. Unique invite link is generated
3. Member can join leadership chat
4. Member gets access to admin commands

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_addmember_command(update, context, **kwargs):
    """
    Handle /addmember command for adding new team members with invite links.

    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional context including team_id, user permissions, etc.

    Returns:
        Response message with member details and invite link
    """
    try:

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
        if command_text.startswith("/addmember"):
            args_text = command_text[10:].strip()  # Remove "/addmember"
        else:
            return "❌ Invalid command format."

        if not args_text:
            return ERROR_MESSAGES["ADDMEMBER_MISSING_ARGUMENTS"]

        # Parse arguments using simplified parser (name and phone only)
        member_name, phone_number = parse_addmember_args(args_text)

        if not member_name or not phone_number:
            return ERROR_MESSAGES["ADDMEMBER_INVALID_FORMAT"] + f"\n\n📝 **What you provided:** {args_text}\n🎯 **What I need:** Member name + phone number"

        # Sanitize inputs
        member_name = sanitize_input(member_name, 100)
        phone_number = sanitize_input(phone_number, 20)

        # Validate inputs
        if not member_name or not member_name.strip():
            return ERROR_MESSAGES["NAME_REQUIRED"] + f"\n\n📝 **What you provided:** {args_text}"

        # Validate name length
        if len(member_name.strip()) < PLAYER_MIN_NAME_LENGTH:
            return ERROR_MESSAGES["NAME_TOO_SHORT"].format(min_length=PLAYER_MIN_NAME_LENGTH) + f"\n\n📝 **What you provided:** {args_text}"

        # Validate phone number format
        if not is_valid_phone(phone_number):
            return ERROR_MESSAGES["INVALID_PHONE_FORMAT"].format(phone=phone_number)


        # Route to CrewAI agent via AgenticMessageRouter
        from kickai.agents.agentic_message_router import AgenticMessageRouter
        router = AgenticMessageRouter(team_id)

        # Create structured message for the agent
        agent_message_text = f"/addmember {member_name} {phone_number}"

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
            return f"❌ Failed to add team member: {error_msg}"

    except Exception as e:
        logger.error(f"❌ Error in handle_addmember_command: {e}")
        return ERROR_MESSAGES["ADDMEMBER_SYSTEM_ERROR"].format(error=str(e))


def parse_addmember_args(args_text: str) -> tuple[str, str]:
    """
    Parse /addmember command arguments with intelligent phone number detection.

    Supported formats:
    - "John Smith +447123456789" → ("John Smith", "+447123456789")
    - "John +447123456789" → ("John", "+447123456789")
    - "John Smith 07123456789" → ("John Smith", "07123456789")

    Args:
        args_text: Raw argument text after /addmember command

    Returns:
        Tuple of (member_name, phone_number) or (None, None) if parsing fails
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

    for part in parts:
        if is_valid_phone(part):
            phone_number = part
        else:
            name_parts.append(part)

    if not phone_number or not name_parts:
        return None, None

    member_name = " ".join(name_parts)
    return member_name, phone_number





# Commands removed: /createteam, /teamstatus, /updateteam, /listmembers
# /list command will handle listing all players and members in leadership chat
# /update command will handle updating team member information
