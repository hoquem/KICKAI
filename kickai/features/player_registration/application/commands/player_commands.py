#!/usr/bin/env python3
"""
Player Registration Commands

This module registers all player registration related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""


from kickai.core.command_registry import CommandType, PermissionLevel, command

# ============================================================================
# MAIN CHAT COMMANDS - For Player Registration
# ============================================================================


# ============================================================================
# LEADERSHIP CHAT COMMANDS - For Team Member Registration
# ============================================================================


# ============================================================================
# SHARED LEADERSHIP COMMANDS
# ============================================================================


# /addplayer command moved to team_administration feature for better organization
# This avoids duplication and consolidates player management in one place


@command(
    name="/addmember",
    description="Add a new team member with simplified ID generation (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=["/addmember John Smith +447123456789"],
    parameters={"name": "Member's full name", "phone": "Phone number (e.g., +447123456789)"},
    help_text="""
👔 Add Team Member (Leadership Only)

Add a new team member with simplified ID generation and invite link.

Usage:
/addmember [name] [phone]

Example:
/addmember John Smith +447123456789

What happens:
1. Team member record is created with simple ID (e.g., 01JS)
2. Role can be set later by team members
3. Unique Telegram invite link is generated for leadership chat
4. Link is sent to you to share with the member

🔒 Security: Links are one-time use and expire automatically.

💡 Note: This command is only available in the leadership chat.
    """,
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
    parameters={"player_id": "Player ID to approve"},
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
    """,
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
    parameters={"player_id": "Player ID to reject", "reason": "Reason for rejection (optional)"},
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
    """,
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
    """,
)
async def handle_pending_command(update, context, **kwargs):
    """Handle /pending command."""
    # This will be handled by the agent system
    return None
