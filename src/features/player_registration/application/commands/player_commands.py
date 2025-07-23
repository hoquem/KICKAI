#!/usr/bin/env python3
"""
Player Registration Commands

This module registers all player registration related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from src.core.command_registry import CommandType, PermissionLevel, command
from src.core.enums import ChatType

# ============================================================================
# MAIN CHAT COMMANDS - For Player Registration
# ============================================================================

@command(
    name="/register",
    description="Register as a new player (Main Chat)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="player_registration",
    chat_type=ChatType.MAIN,
    examples=["/register", "/register John Smith +447123456789 Forward"],
    parameters={
        "name": "Player's full name",
        "phone": "Phone number (e.g., +447123456789)",
        "position": "Playing position (e.g., Forward, Midfielder, Defender, Goalkeeper)"
    },
    help_text="""
📝 Player Registration (Main Chat)

Register yourself as a new player in the team.

Usage:
• /register - Start registration process
• /register [name] [phone] [position] - Register with details

Example:
/register John Smith +447123456789 Forward

What happens:
1. Your details are recorded in the team database
2. You'll receive a welcome message
3. Team leadership will be notified for approval
4. You can start using player commands once approved

💡 Need help? Contact the team admin in the leadership chat.
    """
)
async def handle_register_player_main_chat(update, context, **kwargs):
    """Handle /register command in main chat - for player registration."""
    # This will be handled by the agent system
    return None


# ============================================================================
# LEADERSHIP CHAT COMMANDS - For Team Member Registration
# ============================================================================




# ============================================================================
# SHARED LEADERSHIP COMMANDS
# ============================================================================

@command(
    name="/addplayer",
    description="Add a new player with invite link (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=["/addplayer John Smith +447123456789 Forward"],
    parameters={
        "name": "Player's full name",
        "phone": "Phone number (e.g., +447123456789)",
        "position": "Playing position (e.g., Forward, Midfielder, Defender, Goalkeeper)"
    },
    help_text="""
👤 Add Player (Leadership Only)

Add a new player to the team and generate a unique invite link.

Usage:
/addplayer [name] [phone] [position]

Example:
/addplayer John Smith +447123456789 Forward

What happens:
1. Player record is created in the database
2. Unique Telegram invite link is generated
3. Link is sent to you to share with the player
4. Player can join the main chat using the link

🔒 Security: Links are one-time use and expire automatically.

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_addplayer_command(update, context, **kwargs):
    """Handle /addplayer command."""
    # This will be handled by the agent system
    return None


@command(
    name="/addmember",
    description="Add a new team member with invite link (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=["/addmember John Smith +447123456789 Coach"],
    parameters={
        "name": "Member's full name",
        "phone": "Phone number (e.g., +447123456789)",
        "role": "Team role (e.g., Coach, Manager, Assistant)"
    },
    help_text="""
👔 Add Team Member (Leadership Only)

Add a new team member (coach, manager, etc.) and generate a unique invite link.

Usage:
/addmember [name] [phone] [role]

Example:
/addmember John Smith +447123456789 Coach

What happens:
1. Team member record is created in the database
2. Unique Telegram invite link is generated
3. Link is sent to you to share with the member
4. Member can join the leadership chat using the link

🔒 Security: Links are one-time use and expire automatically.

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_addmember_command(update, context, **kwargs):
    """Handle /addmember command."""
    # This will be handled by the agent system
    return None


@command(
    name="/approve",
    description="Approve a player for team participation (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=["/approve MH123"],
    parameters={
        "player_id": "Player ID to approve"
    },
    help_text="""
✅ Approve Player (Leadership Only)

Approve a player for team participation and match selection.

Usage:
/approve [player_id]

Example:
/approve MH123

What happens:
1. Player status is updated to 'approved'
2. Player can now participate in matches
3. Player receives notification of approval
4. Player appears in squad selection lists

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_approve_command(update, context, **kwargs):
    """Handle /approve command."""
    # This will be handled by the agent system
    return None


@command(
    name="/reject",
    description="Reject a player with reason (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=["/reject MH123 Insufficient experience"],
    parameters={
        "player_id": "Player ID to reject",
        "reason": "Reason for rejection (optional)"
    },
    help_text="""
❌ Reject Player (Leadership Only)

Reject a player with an optional reason.

Usage:
/reject [player_id] [reason]

Example:
/reject MH123 Insufficient experience

What happens:
1. Player status is updated to 'rejected'
2. Player receives notification with reason
3. Player can reapply if circumstances change
4. Reason is recorded for future reference

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_reject_command(update, context, **kwargs):
    """Handle /reject command."""
    # This will be handled by the agent system
    return None


@command(
    name="/pending",
    description="List players awaiting approval (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=["/pending"],
    help_text="""
📋 Pending Approvals (Leadership Only)

List all players awaiting approval for team participation.

Usage:
/pending

What you'll see:
• List of players awaiting approval
• Registration date and time
• Player details (name, phone, position)
• Quick approve/reject options

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_pending_command(update, context, **kwargs):
    """Handle /pending command."""
    # This will be handled by the agent system
    return None
