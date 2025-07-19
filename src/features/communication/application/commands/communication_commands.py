#!/usr/bin/env python3
"""
Communication Commands

This module registers all communication related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from core.command_registry import command, CommandType, PermissionLevel


@command(
    name="/help",
    description="Show help information and available commands",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="communication",
    examples=["/help", "/help addplayer"],
    parameters={
        "command": "Specific command to get help for (optional)"
    },
    help_text="""
🤖 **KICKAI Help**

Get help information about available commands and features.

**Usage:**
• `/help` - Show general help
• `/help [command]` - Get help for specific command

**Examples:**
• `/help` - Show all available commands
• `/help addplayer` - Get detailed help for addplayer command

**What you'll see:**
• List of available commands for your permission level
• Command descriptions and usage examples
• Quick tips and guidance

💡 **Tip:** You can also ask me questions in natural language!
    """
)
async def handle_help_command(update, context, **kwargs):
    """Handle /help command."""
    # This will be handled by the agent system
    return None


@command(
    name="/start",
    description="Start the bot and show welcome message",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="communication",
    examples=["/start"],
    help_text="""
👋 **Welcome to KICKAI!**

Start the bot and get a welcome message with basic information.

**Usage:**
`/start`

**What you'll see:**
• Welcome message
• Basic bot information
• Quick start guide
• Links to help and registration

💡 **New here?** Use `/register` to join the team!
    """
)
async def handle_start_command(update, context, **kwargs):
    """Handle /start command."""
    # This will be handled by the agent system
    return None


@command(
    name="/announce",
    description="Make an announcement to the team (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="communication",
    examples=["/announce Important match this weekend!"],
    parameters={
        "message": "Announcement message to send to the team"
    },
    help_text="""
📢 **Team Announcement (Leadership Only)**

Make an important announcement to all team members.

**Usage:**
`/announce [message]`

**Example:**
`/announce Important match this weekend!`

**What happens:**
1. Announcement is sent to the main team chat
2. All team members are notified
3. Message is formatted for clarity
4. Announcement is logged for record keeping

💡 **Note:** This command is only available in the leadership chat.
    """
)
async def handle_announce_command(update, context, **kwargs):
    """Handle /announce command."""
    # This will be handled by the agent system
    return None


@command(
    name="/remind",
    description="Send a reminder to team members (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="communication",
    examples=["/remind Don't forget training tomorrow at 7pm"],
    parameters={
        "message": "Reminder message to send"
    },
    help_text="""
⏰ **Send Reminder (Leadership Only)**

Send a reminder message to team members.

**Usage:**
`/remind [message]`

**Example:**
`/remind Don't forget training tomorrow at 7pm`

**What happens:**
1. Reminder is sent to the main team chat
2. Team members receive notification
3. Message is clearly marked as a reminder
4. Reminder is logged for tracking

💡 **Note:** This command is only available in the leadership chat.
    """
)
async def handle_remind_command(update, context, **kwargs):
    """Handle /remind command."""
    # This will be handled by the agent system
    return None


@command(
    name="/broadcast",
    description="Broadcast message to all team chats (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="communication",
    examples=["/broadcast Team meeting tonight at 8pm"],
    parameters={
        "message": "Message to broadcast to all chats"
    },
    help_text="""
📡 **Broadcast Message (Leadership Only)**

Send a message to all team chats (main and leadership).

**Usage:**
`/broadcast [message]`

**Example:**
`/broadcast Team meeting tonight at 8pm`

**What happens:**
1. Message is sent to main team chat
2. Message is sent to leadership chat
3. All team members receive the message
4. Broadcast is logged for record keeping

💡 **Note:** This command is only available in the leadership chat.
    """
)
async def handle_broadcast_command(update, context, **kwargs):
    """Handle /broadcast command."""
    # This will be handled by the agent system
    return None 