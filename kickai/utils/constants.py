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
}

# Success Messages
SUCCESS_MESSAGES = {
    "PLAYER_ADDED": "✅ Player {name} added successfully with ID: {player_id}",
    "MEMBER_ADDED": "✅ Team member {name} added successfully with ID: {member_id}",
    "PLAYER_APPROVED": "✅ Player {name} approved and activated successfully",
}

# Log Messages
LOG_MESSAGES = {
    "ID_GENERATED": "Generated player ID '{id}' for '{name}' in team '{team_id}'",
    "USED_IDS_CLEARED": "Cleared used IDs from SimpleIDGenerator",
    "TOO_MANY_PLAYERS": "Too many players with initials '{initials}' in team '{team_id}'",
}
