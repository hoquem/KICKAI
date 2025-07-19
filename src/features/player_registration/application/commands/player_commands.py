#!/usr/bin/env python3
"""
Player Registration Commands

This module registers all player registration related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from core.command_registry import command, CommandType, PermissionLevel
from agents.behavioral_mixins import PlayerAdditionMixin, TeamMemberAdditionMixin


# Initialize mixins for command handling
player_addition_mixin = PlayerAdditionMixin()
team_member_addition_mixin = TeamMemberAdditionMixin()


@command(
    name="/register",
    description="Register as a new player",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="player_registration",
    examples=["/register", "/register John Smith +447123456789 Forward"],
    parameters={
        "name": "Player's full name",
        "phone": "Phone number (e.g., +447123456789)",
        "position": "Playing position (e.g., Forward, Midfielder, Defender, Goalkeeper)"
    },
    help_text="""
📝 **Player Registration**

Register yourself as a new player in the team.

**Usage:**
• `/register` - Start registration process
• `/register [name] [phone] [position]` - Register with details

**Example:**
`/register John Smith +447123456789 Forward`

**What happens:**
1. Your details are recorded in the team database
2. You'll receive a welcome message
3. Team leadership will be notified for approval
4. You can start using player commands once approved

💡 **Need help?** Contact the team admin in the leadership chat.
    """
)
async def handle_register_command(update, context, **kwargs):
    """Handle /register command."""
    # This will be handled by the agent system
    return None


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
👤 **Add Player (Leadership Only)**

Add a new player to the team and generate a unique invite link.

**Usage:**
`/addplayer [name] [phone] [position]`

**Example:**
`/addplayer John Smith +447123456789 Forward`

**What happens:**
1. Player record is created in the database
2. Unique Telegram invite link is generated
3. Link is sent to you to share with the player
4. Player can join the main chat using the link

🔒 **Security:** Links are one-time use and expire automatically.

💡 **Note:** This command is only available in the leadership chat.
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
👔 **Add Team Member (Leadership Only)**

Add a new team member (coach, manager, etc.) and generate a unique invite link.

**Usage:**
`/addmember [name] [phone] [role]`

**Example:**
`/addmember John Smith +447123456789 Coach`

**What happens:**
1. Team member record is created in the database
2. Unique Telegram invite link is generated
3. Link is sent to you to share with the member
4. Member can join the leadership chat using the link

🔒 **Security:** Links are one-time use and expire automatically.

💡 **Note:** This command is only available in the leadership chat.
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
✅ **Approve Player (Leadership Only)**

Approve a player for team participation and match selection.

**Usage:**
`/approve [player_id]`

**Example:**
`/approve MH123`

**What happens:**
1. Player status is updated to 'approved'
2. Player can now participate in matches
3. Player receives notification of approval
4. Player appears in squad selection lists

💡 **Note:** This command is only available in the leadership chat.
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
❌ **Reject Player (Leadership Only)**

Reject a player with an optional reason.

**Usage:**
`/reject [player_id] [reason]`

**Example:**
`/reject MH123 Insufficient experience`

**What happens:**
1. Player status is updated to 'rejected'
2. Player receives notification with reason
3. Player can reapply if circumstances change
4. Reason is recorded for future reference

💡 **Note:** This command is only available in the leadership chat.
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
📋 **Pending Approvals (Leadership Only)**

List all players awaiting approval for team participation.

**Usage:**
`/pending`

**What you'll see:**
• List of players awaiting approval
• Registration date and time
• Player details (name, phone, position)
• Quick approve/reject options

💡 **Note:** This command is only available in the leadership chat.
    """
)
async def handle_pending_command(update, context, **kwargs):
    """Handle /pending command."""
    # This will be handled by the agent system
    return None


@command(
    name="/status",
    description="Check player status",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/status", "/status 07123456789"],
    parameters={
        "phone": "Phone number to check (optional)"
    },
    help_text="""
📊 **Check Player Status**

Check the status of a player in the team.

**Usage:**
• `/status` - Check your own status
• `/status [phone]` - Check status of a specific player

**Example:**
`/status 07123456789`

**What you'll see:**
• Player registration status
• Approval status
• Team membership details
• Recent activity

💡 **Note:** You can only check your own status or the status of players you have permission to view.
    """
)
async def handle_status_command(update, context, **kwargs):
    """Handle /status command."""
    # This will be handled by the agent system
    return None


@command(
    name="/myinfo",
    description="Get your player information",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/myinfo"],
    help_text="""
👤 **My Player Information**

Get your personal player information and details.

**Usage:**
`/myinfo`

**What you'll see:**
• Your player ID
• Name and contact details
• Position and playing role
• Registration date
• Approval status
• Team membership details
• Recent activity and statistics

💡 **Note:** This command shows your personal information only.
    """
)
async def handle_myinfo_command(update, context, **kwargs):
    """Handle /myinfo command."""
    # This will be handled by the agent system
    return None


@command(
    name="/list",
    description="List all team players",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/list"],
    help_text="""
👥 **Team Player List**

List all players in the team.

**Usage:**
`/list`

**What you'll see:**
• All registered players
• Player names and positions
• Registration status
• Approval status
• Contact information (if you have permission)

💡 **Note:** The information shown depends on your permission level.
    """
)
async def handle_list_command(update, context, **kwargs):
    """Handle /list command."""
    # This will be handled by the agent system
    return None