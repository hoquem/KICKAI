#!/usr/bin/env python3
"""
Player Update Commands

This module registers player update commands with the command registry.
These commands use the update tools created in Phase 4 and Phase 5.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command


@command(
    name="/update",
    description="Update your information (context-aware routing)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=[
        "/update phone +447123456789",
        "/update position midfielder",
        "/update email john@example.com",
    ],
    parameters={
        "field": "Field to update (phone, position, email, etc.)",
        "value": "New value for the field",
    },
    help_text="""
🔄 Update Information (Context-Aware)

Updates your player or team member information depending on the chat:
• Main Chat: Updates player information 
• Leadership Chat: Updates team member information

Usage:
/update [field] [value]

📋 Common Fields:
• phone - Your contact phone number
• email - Your email address  
• emergency_contact_name - Emergency contact name
• emergency_contact_phone - Emergency contact phone
• medical_notes - Medical information

👤 Player Fields (Main Chat):
• position - Football position

👔 Team Member Fields (Leadership Chat):  
• role - Administrative role

💡 Examples:
• /update phone +447123456789
• /update position midfielder (main chat)
• /update role Assistant Coach (leadership chat)
• /update email john@example.com

🔍 To see all available fields: /update (no arguments)
    """,
)
async def handle_update_command(update, context, **kwargs):
    """Handle /update command with context-aware routing."""
    # This will be handled by the agent system
    return None


@command(
    name="/updateplayer",
    description="Update player information directly (any chat)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=[
        "/updateplayer phone +447123456789",
        "/updateplayer position striker",
        "/updateplayer email player@example.com",
    ],
    parameters={"field": "Player field to update", "value": "New value for the field"},
    help_text="""
👤 Update Player Information 

Directly update your player information in any chat.

Usage:
/updateplayer [field] [value]

📋 Available Fields:
• phone - Contact phone number
• email - Email address
• position - Football position (goalkeeper, defender, midfielder, forward, etc.)
• date_of_birth - Date of birth (YYYY-MM-DD format)
• emergency_contact_name - Emergency contact name
• emergency_contact_phone - Emergency contact phone number  
• medical_notes - Medical information and conditions

💡 Examples:
• /updateplayer phone +447123456789
• /updateplayer position midfielder
• /updateplayer email john@example.com
• /updateplayer emergency_contact_name "Sarah Smith"
• /updateplayer emergency_contact_phone +447987654321
• /updateplayer medical_notes "No known allergies"

🔍 To see current information: /updateplayer info
🔍 To get detailed help: /updateplayer help
📱 To update multiple fields at once: /updateplayer multi

⚡ Note: This command works in any chat and only updates player records.
    """,
)
async def handle_updateplayer_command(update, context, **kwargs):
    """Handle /updateplayer command."""
    # This will be handled by the agent system
    return None


@command(
    name="/updatemember",
    description="Update team member information (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=[
        "/updatemember phone +447123456789",
        "/updatemember email admin@example.com",
        "/updatemember role Assistant Coach",
    ],
    parameters={"field": "Team member field to update", "value": "New value for the field"},
    help_text="""
👔 Update Team Member Information (Leadership Only)

Update your team member information in the leadership chat.

Usage:
/updatemember [field] [value]

📋 Available Fields:
• phone - Contact phone number
• email - Email address  
• emergency_contact_name - Emergency contact name
• emergency_contact_phone - Emergency contact phone number
• role - Administrative role (requires admin approval)

💡 Examples:
• /updatemember phone +447123456789
• /updatemember email admin@example.com
• /updatemember role Assistant Coach
• /updatemember emergency_contact_name "Jane Doe"

🔐 Admin Operations (Admin Only):
• /updatemember other [member_id] [field] [value] - Update another member

🔍 To see current information: /updatemember info  
🔍 To get detailed help: /updatemember help
📱 To update multiple fields at once: /updatemember multi

🔒 Note: 
• This command is only available in leadership chat
• Role changes require admin approval
• Some operations are restricted to admins only
    """,
)
async def handle_updatemember_command(update, context, **kwargs):
    """Handle /updatemember command."""
    # This will be handled by the agent system
    return None


@command(
    name="/playerinfo",
    description="Show your current player information",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/playerinfo"],
    help_text="""
👤 Player Information

Display your current player information and profile.

Usage:
/playerinfo

📋 Information Displayed:
• Basic Info: Name, position, status
• Contact Info: Phone, email
• Emergency Contacts: Name and phone  
• Medical Notes: Health information
• Registration: Join date and status
• Team Details: Team ID and role

💡 Quick Actions:
• To update any field: /updateplayer [field] [value]
• To get update help: /updateplayer help

🔍 Note: This shows your player profile information.
    """,
)
async def handle_playerinfo_command(update, context, **kwargs):
    """Handle /playerinfo command."""
    # This will be handled by the agent system
    return None


@command(
    name="/memberinfo",
    description="Show your current team member information (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="player_registration",
    examples=["/memberinfo"],
    help_text="""
👔 Team Member Information (Leadership Only)

Display your current team member information and administrative profile.

Usage:
/memberinfo

📋 Information Displayed:
• Basic Info: Name, role, admin status
• Contact Info: Phone, email
• Emergency Contacts: Name and phone
• Team Details: Team ID and permissions
• Registration: Join date and status

💡 Quick Actions:
• To update any field: /updatemember [field] [value] 
• To get update help: /updatemember help

🔒 Note: This command is only available in leadership chat.
    """,
)
async def handle_memberinfo_command(update, context, **kwargs):
    """Handle /memberinfo command."""
    # This will be handled by the agent system
    return None
