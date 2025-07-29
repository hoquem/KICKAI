#!/usr/bin/env python3
"""
KICKAI Centralized Constants - Single Source of Truth

This module contains all constants used across the KICKAI system.
This is the ONLY place where these constants should be defined to prevent
inconsistencies and maintenance issues.
"""

from dataclasses import dataclass, field
from typing import Union, List

from kickai.core.enums import ChatType, PermissionLevel

# =============================================================================
# SYSTEM CONSTANTS
# =============================================================================

BOT_VERSION = "2.0.0"

# =============================================================================
# FIRESTORE CONSTANTS
# =============================================================================

FIRESTORE_COLLECTION_PREFIX = "kickai"


def get_team_members_collection(team_id: str) -> str:
    """Get the collection name for team members."""
    return f"{FIRESTORE_COLLECTION_PREFIX}_{team_id}_team_members"


# =============================================================================
# COMMAND CONSTANTS
# =============================================================================


@dataclass(frozen=True)
class CommandDefinition:
    """Immutable command definition with metadata."""

    name: str
    description: str
    permission_level: PermissionLevel
    chat_types: frozenset[ChatType]
    examples: tuple[str, ...] = field(default_factory=tuple)
    feature: str = "shared"

    def __post_init__(self):
        # Ensure name starts with /
        if not self.name.startswith("/"):
            object.__setattr__(self, "name", f"/{self.name}")


# =============================================================================
# CORE COMMANDS
# =============================================================================

CORE_COMMANDS = {
    CommandDefinition(
        name="/help",
        description="Get help and command information",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/help", "/help /addplayer"),
        feature="shared",
    ),
}

# =============================================================================
# PLAYER MANAGEMENT COMMANDS
# =============================================================================

PLAYER_COMMANDS = {
    CommandDefinition(
        name="/myinfo",
        description="View your player information",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/myinfo",),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/status",
        description="Check your current status",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/status", "/status MH123", "/status +447123456789"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/list",
        description="List all active players",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/list", "/list players"),
        feature="shared",
    ),
    CommandDefinition(
        name="/update",
        description="Update your player information",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/update", "/update position Forward"),
        feature="player_registration",
    ),
}

# =============================================================================
# TEAM ADMINISTRATION COMMANDS
# =============================================================================

TEAM_ADMINISTRATION_COMMANDS = {
    CommandDefinition(
        name="/addplayer",
        description="Add a new player with invite link",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/addplayer", "/addplayer John Smith +447123456789"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/addmember",
        description="Add a new team member with invite link",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/addmember", "/addmember Jane Doe +447123456789"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/approve",
        description="Approve a pending player/member",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/approve", "/approve MH123"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/reject",
        description="Reject a pending player/member",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/reject", "/reject MH123"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/pending",
        description="List pending approvals",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/pending",),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/announce",
        description="Send team announcements",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/announce", "/announce Team meeting tonight"),
        feature="communication",
    ),
}

# =============================================================================
# TRAINING MANAGEMENT COMMANDS
# =============================================================================

TRAINING_COMMANDS = {
    CommandDefinition(
        name="/scheduletraining",
        description="Schedule a new training session",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/scheduletraining", "/scheduletraining Technical 2024-01-15 19:00"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/listtrainings",
        description="List upcoming training sessions",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/listtrainings", "/listtrainings 2024-01"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/marktraining",
        description="Mark attendance for training session",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/marktraining", "/marktraining TRAIN123 confirmed"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/canceltraining",
        description="Cancel a training session",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/canceltraining", "/canceltraining TRAIN123"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/trainingstats",
        description="View training statistics",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/trainingstats", "/trainingstats 2024"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/mytrainings",
        description="View your training history",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/mytrainings", "/mytrainings 2024"),
        feature="training_management",
    ),
}

# =============================================================================
# MATCH MANAGEMENT COMMANDS
# =============================================================================

MATCH_COMMANDS = {
    CommandDefinition(
        name="/creatematch",
        description="Create a new match",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/creatematch", "/creatematch Home vs Away 2024-01-20 15:00"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/listmatches",
        description="List upcoming matches",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/listmatches", "/listmatches 2024"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/matchstatus",
        description="Check match status",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/matchstatus", "/matchstatus MATCH123"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/selectsquad",
        description="Select squad for match",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/selectsquad", "/selectsquad MATCH123"),
        feature="match_management",
    ),
}

# =============================================================================
# ATTENDANCE MANAGEMENT COMMANDS
# =============================================================================

ATTENDANCE_COMMANDS = {
    CommandDefinition(
        name="/attendance",
        description="View match attendance information",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/attendance", "/attendance MATCH123"),
        feature="attendance_management",
    ),
    CommandDefinition(
        name="/markattendance",
        description="Mark your attendance for a match",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/markattendance", "/markattendance MATCH123 confirmed"),
        feature="attendance_management",
    ),
    CommandDefinition(
        name="/attendancehistory",
        description="View your attendance history",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/attendancehistory", "/attendancehistory 2024"),
        feature="attendance_management",
    ),
}

# =============================================================================
# PAYMENT MANAGEMENT COMMANDS
# =============================================================================

PAYMENT_COMMANDS = {
    CommandDefinition(
        name="/createpayment",
        description="Create a new payment record",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/createpayment", "/createpayment John Smith 50.00 Match fee"),
        feature="payment_management",
    ),
    CommandDefinition(
        name="/payments",
        description="View payment history",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/payments", "/payments John Smith"),
        feature="payment_management",
    ),
    CommandDefinition(
        name="/markpaid",
        description="Mark payment as paid",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/markpaid", "/markpaid PAY123"),
        feature="payment_management",
    ),
}

# =============================================================================
# COMMUNICATION COMMANDS
# =============================================================================

COMMUNICATION_COMMANDS = {
    CommandDefinition(
        name="/message",
        description="Send a message to team",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/message", "/message Important team update"),
        feature="communication",
    ),
}

# =============================================================================
# HEALTH MONITORING COMMANDS
# =============================================================================

HEALTH_COMMANDS = {
    CommandDefinition(
        name="/health",
        description="Check system health status",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/health",),
        feature="health_monitoring",
    ),
}

# =============================================================================
# ALL COMMANDS
# =============================================================================

ALL_COMMANDS = (
    CORE_COMMANDS
    | PLAYER_COMMANDS
    | TEAM_ADMINISTRATION_COMMANDS
    | TRAINING_COMMANDS
    | MATCH_COMMANDS
    | ATTENDANCE_COMMANDS
    | PAYMENT_COMMANDS
    | COMMUNICATION_COMMANDS
    | HEALTH_COMMANDS
)

# =============================================================================
# COMMAND LOOKUP DICTIONARIES
# =============================================================================

COMMANDS_BY_NAME = {cmd.name: cmd for cmd in ALL_COMMANDS}
COMMANDS_BY_FEATURE = {}
COMMANDS_BY_CHAT_TYPE = {}
COMMANDS_BY_PERMISSION = {}

# Build lookup dictionaries
for cmd in ALL_COMMANDS:
    # By feature
    if cmd.feature not in COMMANDS_BY_FEATURE:
        COMMANDS_BY_FEATURE[cmd.feature] = set()
    COMMANDS_BY_FEATURE[cmd.feature].add(cmd)

    # By chat type
    for chat_type in cmd.chat_types:
        if chat_type not in COMMANDS_BY_CHAT_TYPE:
            COMMANDS_BY_CHAT_TYPE[chat_type] = set()
        COMMANDS_BY_CHAT_TYPE[chat_type].add(cmd)

    # By permission level
    if cmd.permission_level not in COMMANDS_BY_PERMISSION:
        COMMANDS_BY_PERMISSION[cmd.permission_level] = set()
    COMMANDS_BY_PERMISSION[cmd.permission_level].add(cmd)

# =============================================================================
# CHAT TYPE CONSTANTS
# =============================================================================

CHAT_TYPE_DISPLAY_NAMES = {
    ChatType.MAIN: "Main Chat",
    ChatType.LEADERSHIP: "Leadership Chat",
    ChatType.PRIVATE: "Private Chat",
}

CHAT_TYPE_DESCRIPTIONS = {
    ChatType.MAIN: "Main team chat for all players",
    ChatType.LEADERSHIP: "Leadership chat for team management",
    ChatType.PRIVATE: "Private messages with the bot",
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_commands_for_chat_type(chat_type: ChatType) -> List[CommandDefinition]:
    """Get all commands available for a specific chat type."""
    return sorted(COMMANDS_BY_CHAT_TYPE.get(chat_type, []), key=lambda x: x.name)


def get_commands_for_permission_level(permission_level: PermissionLevel) -> List[CommandDefinition]:
    """Get all commands available for a specific permission level."""
    return sorted(COMMANDS_BY_PERMISSION.get(permission_level, []), key=lambda x: x.name)


def get_commands_for_feature(feature: str) -> List[CommandDefinition]:
    """Get all commands for a specific feature."""
    return sorted(COMMANDS_BY_FEATURE.get(feature, []), key=lambda x: x.name)


def get_command_by_name(command_name: str) -> CommandDefinition:
    """Get command definition by name."""
    # Ensure command name starts with /
    if not command_name.startswith("/"):
        command_name = f"/{command_name}"
    return COMMANDS_BY_NAME.get(command_name)


def is_valid_command(command_name: str) -> bool:
    """Check if a command name is valid."""
    # Ensure command name starts with /
    if not command_name.startswith("/"):
        command_name = f"/{command_name}"
    return get_command_by_name(command_name) is not None


def get_chat_type_display_name(chat_type: ChatType) -> str:
    """Get display name for chat type."""
    return CHAT_TYPE_DISPLAY_NAMES.get(chat_type, str(chat_type.value))


def get_chat_type_description(chat_type: ChatType) -> str:
    """Get description for chat type."""
    return CHAT_TYPE_DESCRIPTIONS.get(chat_type, "Unknown chat type")


def normalize_chat_type(chat_type: str) -> ChatType:
    """Normalize chat type string to enum."""
    chat_type_lower = chat_type.lower()

    if chat_type_lower in ["main_chat", "main"]:
        return ChatType.MAIN
    elif chat_type_lower in ["leadership_chat", "leadership"]:
        return ChatType.LEADERSHIP
    elif chat_type_lower in ["private", "private_chat"]:
        return ChatType.PRIVATE
    else:
        # Default to main chat for unknown types
        return ChatType.MAIN

# =============================================================================
# TELEGRAM CONFIGURATION CONSTANTS
# =============================================================================

class TelegramConfig:
    """Telegram bot configuration constants."""
    
    # Polling configuration
    POLL_INTERVAL = 1.0
    TIMEOUT = 30
    BOOTSTRAP_RETRIES = 5
    
    # Message formatting
    MAX_MESSAGE_LENGTH = 4096
    MAX_CAPTION_LENGTH = 1024
    
    # Contact sharing
    CONTACT_BUTTON_TEXT = "📱 Share My Phone Number"
    CONTACT_BUTTON_ONE_TIME = True
    CONTACT_BUTTON_RESIZE = True
