#!/usr/bin/env python3
"""
Constants for KICKAI

This module contains configuration constants used throughout the application.
"""

# ID Generation Constants
MAX_ID_NUMBER = 99
ID_NUMBER_FORMAT = "{:02d}"
FALLBACK_ID_PREFIX = "99"

# Input Validation Constants
MAX_NAME_LENGTH = 50
MAX_PHONE_LENGTH = 20
MAX_POSITION_LENGTH = 30
MAX_TEAM_ID_LENGTH = 20
MAX_USER_ID_LENGTH = 20

# Phone Number Validation
PHONE_PATTERN = r"^\+?[1-9]\d{1,14}$"

# Player Positions
VALID_PLAYER_POSITIONS = ["goalkeeper", "defender", "midfielder", "forward", "utility"]

# Team Member Roles
VALID_TEAM_MEMBER_ROLES = ["coach", "manager", "assistant", "admin", "coordinator", "volunteer"]

# Default Values
DEFAULT_PLAYER_POSITION = "utility"
DEFAULT_MEMBER_ROLE = "volunteer"
DEFAULT_PLAYER_STATUS = "pending"
DEFAULT_MEMBER_STATUS = "active"
DEFAULT_CREATED_BY = "system"

# Player Management Constants
PLAYER_DEFAULT_STATUS = "pending"
PLAYER_DEFAULT_POSITION = ""  # Empty string, will be set via /update
PLAYER_MIN_NAME_LENGTH = 2
PLAYER_MAX_NAME_LENGTH = 100

# Phone Number Validation
PHONE_MIN_DIGITS = 10
PHONE_MAX_DIGITS = 15
PHONE_VALID_PREFIXES = ["+44", "07", "44"]

# Error Messages
ERROR_MESSAGES = {
    "NAME_REQUIRED": "Player name is required",
    "PHONE_REQUIRED": "Player phone number is required",
    "TEAM_ID_REQUIRED": "Team ID is required",
    "USER_ID_REQUIRED": "User ID is required",
    "INVALID_PHONE": "Phone number must be in international format (e.g., +447123456789)",
    "INVALID_POSITION": "Position must be one of: goalkeeper, defender, midfielder, forward, utility",
    "PLAYER_EXISTS": "Player with phone {phone} already exists in team {team_id}",
    "MEMBER_EXISTS": "Team member with phone {phone} already exists in team {team_id}",
    "SERVICE_UNAVAILABLE": "Service temporarily unavailable: {service}",
    "INVITE_LINK_ERROR": "Could not generate invite link - {error}",
    "TEAM_CONFIG_ERROR": "Could not generate invite link - team configuration incomplete",
    "SYSTEM_ERROR": "Could not generate invite link due to system error",

    # AddPlayer Command Specific Messages
    "MISSING_ARGUMENTS": "❌ **Missing Arguments**\n\nUsage: `/addplayer <player_name> <phone_number>`",
    "INVALID_FORMAT": "❌ **Invalid Format**\n\nI need both a player name and phone number.",
    "NAME_TOO_SHORT": "❌ **Name too short**\n\n💡 Player name must be at least {min_length} characters long.",
    "INVALID_PHONE_FORMAT": "❌ **Invalid phone number**\n\n📱 Please use UK format:\n• +447123456789\n• 07123456789\n\n🔍 You provided: {phone}",
    "DUPLICATE_PHONE": "❌ **Phone Number Already Registered**\n\n📱 {phone} is already used by: **{existing_name}**",
    "PERMISSION_REQUIRED": "❌ **Permission Required**\n\n🔒 Adding players is a leadership function.",
    "ADDPLAYER_SYSTEM_ERROR": "❌ **System Error**\n\n🛠️ Failed to add player: {error}"
}

# Success Messages
SUCCESS_MESSAGES = {
    "PLAYER_ADDED": "✅ Player {name} added successfully with ID: {player_id}",
    "MEMBER_ADDED": "✅ Team member {name} added successfully with ID: {member_id}",
    "PLAYER_APPROVED": "✅ Player {name} approved and activated successfully",

    # AddPlayer Command Specific Messages
    "PLAYER_ADDED_WITH_INVITE": """✅ **Player Added Successfully!**

👤 PLAYER DETAILS:
• Name: {name}
• Phone: {phone}
• Status: {status}

📱 Send this message to {name}:
"Hi {name}! You've been added to {team_name}. Click this link to join our main chat: {invite_link}"

🔗 Invite Link: {invite_link}
⏰ Expires: {expires_at}
🔄 Usage: One-time use only

📋 **Next Steps:**
1. Send the invite link to {name}
2. Player joins main chat via link
3. Player uses /update to set position and details
4. Player is ready to participate!"""
}

# Log Messages
LOG_MESSAGES = {
    "ID_GENERATED": "Generated player ID '{id}' for '{name}' in team '{team_id}'",
    "USED_IDS_CLEARED": "Cleared used IDs from SimpleIDGenerator",
    "TOO_MANY_PLAYERS": "Too many players with initials '{initials}' in team '{team_id}'",
}
