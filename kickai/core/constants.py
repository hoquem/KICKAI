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
# PLAYER MANAGEMENT COMMANDS
# =============================================================================

PLAYER_COMMANDS = {
    CommandDefinition(
        name="/register",
        description="Register as a new player",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/register", "/register John Smith 07123456789 midfielder"),
        feature="player_registration",
    ),
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
        examples=("/update phone 07123456789", "/update position midfielder", "/update email john@example.com"),
        feature="player_registration",
    ),
}

# =============================================================================
# LEADERSHIP COMMANDS
# =============================================================================

LEADERSHIP_COMMANDS = {
    CommandDefinition(
        name="/approve",
        description="Approve a player for matches",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/approve", "/approve MH123"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/reject",
        description="Reject a player application",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/reject", "/reject MH123 reason"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/pending",
        description="List players awaiting approval",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/pending",),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/addplayer",
        description="Add a player directly",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/addplayer", "/addplayer John Smith 07123456789 midfielder"),
        feature="player_registration",
    ),
    CommandDefinition(
        name="/addmember",
        description="Add a team member",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/addmember", "/addmember John Smith 07123456789 manager"),
        feature="team_administration",
    ),
    CommandDefinition(
        name="/list",
        description="List all players with status",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/list", "/list members"),
        feature="shared",
    ),
    CommandDefinition(
        name="/update",
        description="Update your team member information",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/update phone 07123456789", "/update email admin@example.com", "/update role Assistant Coach"),
        feature="team_administration",
    ),
}

# =============================================================================
# SYSTEM COMMANDS
# =============================================================================

SYSTEM_COMMANDS = {
    CommandDefinition(
        name="/start",
        description="Start the bot",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/start",),
        feature="shared",
    ),
    CommandDefinition(
        name="/help",
        description="Show available commands",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/help", "/help register"),
        feature="shared",
    ),
    CommandDefinition(
        name="/info",
        description="Show user information",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/info", "/myinfo"),
        feature="shared",
    ),
    CommandDefinition(
        name="/ping",
        description="Check bot status",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/ping",),
        feature="shared",
    ),
    CommandDefinition(
        name="/version",
        description="Show bot version",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/version",),
        feature="shared",
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
        examples=("/creatematch", "/creatematch vs Team B 2024-01-15 14:00"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/listmatches",
        description="List upcoming matches",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/listmatches", "/listmatches upcoming"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/matchdetails",
        description="Get match details",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/matchdetails", "/matchdetails MATCH123"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/selectsquad",
        description="Select match squad",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/selectsquad", "/selectsquad MATCH123"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/updatematch",
        description="Update match information",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/updatematch", "/updatematch MATCH123"),
        feature="match_management",
    ),
}

# =============================================================================
# TRAINING MANAGEMENT COMMANDS
# =============================================================================

TRAINING_COMMANDS = {
    CommandDefinition(
        name="/scheduletraining",
        description="Schedule a training session (Leadership only)",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/scheduletraining", "/scheduletraining Technical 2024-01-15 18:00 90"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/listtrainings",
        description="List upcoming training sessions",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/listtrainings", "/listtrainings this week", "/listtrainings today"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/marktraining",
        description="Mark attendance for a training session",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/marktraining", "/marktraining yes", "/marktraining no TRAIN123"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/canceltraining",
        description="Cancel a training session (Leadership only)",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/canceltraining", "/canceltraining TRAIN123", "/canceltraining TRAIN123 Bad weather"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/trainingstats",
        description="Show training statistics and attendance",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/trainingstats", "/trainingstats this month", "/trainingstats TRAIN123"),
        feature="training_management",
    ),
    CommandDefinition(
        name="/mytrainings",
        description="Show my training schedule and history",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/mytrainings", "/mytrainings upcoming", "/mytrainings history"),
        feature="training_management",
    ),
}

# =============================================================================
# ATTENDANCE COMMANDS
# =============================================================================

ATTENDANCE_COMMANDS = {
    CommandDefinition(
        name="/markattendance",
        description="Mark attendance for a match",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/markattendance", "/markattendance yes", "/markattendance no"),
        feature="attendance_management",
    ),
    CommandDefinition(
        name="/attendance",
        description="View match attendance",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/attendance", "/attendance MATCH123"),
        feature="attendance_management",
    ),
    CommandDefinition(
        name="/attendancehistory",
        description="View attendance history",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/attendancehistory", "/attendancehistory 2024"),
        feature="attendance_management",
    ),
    CommandDefinition(
        name="/attendanceexport",
        description="Export attendance data",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/attendanceexport", "/attendanceexport MATCH123"),
        feature="attendance_management",
    ),
    CommandDefinition(
        name="/attendancealerts",
        description="Manage attendance alerts",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/attendancealerts", "/attendancealerts enable", "/attendancealerts disable"),
        feature="attendance_management",
    ),
}

# =============================================================================
# PAYMENT COMMANDS
# =============================================================================

PAYMENT_COMMANDS = {
    CommandDefinition(
        name="/createpayment",
        description="Create a new payment",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/createpayment", "/createpayment Match Fee 25.00"),
        feature="payment_management",
    ),
    CommandDefinition(
        name="/payments",
        description="View payment history",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/payments", "/payments pending", "/payments completed"),
        feature="payment_management",
    ),
    CommandDefinition(
        name="/budget",
        description="View budget information",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/budget", "/budget 2024"),
        feature="payment_management",
    ),
    CommandDefinition(
        name="/markpaid",
        description="Mark payment as paid",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/markpaid", "/markpaid PAYMENT123"),
        feature="payment_management",
    ),
    CommandDefinition(
        name="/paymentexport",
        description="Export payment data",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/paymentexport", "/paymentexport 2024"),
        feature="payment_management",
    ),
}

# =============================================================================
# COMMUNICATION COMMANDS
# =============================================================================

COMMUNICATION_COMMANDS = {
    CommandDefinition(
        name="/announce",
        description="Send announcement to team",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/announce", "/announce Important match tomorrow"),
        feature="communication",
    ),
    CommandDefinition(
        name="/remind",
        description="Send reminder to players",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/remind", "/remind Match in 2 hours"),
        feature="communication",
    ),
    CommandDefinition(
        name="/broadcast",
        description="Broadcast message to all chats",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/broadcast", "/broadcast Emergency message"),
        feature="communication",
    ),
}

# =============================================================================
# TEAM ADMINISTRATION COMMANDS
# =============================================================================

TEAM_ADMIN_COMMANDS = {
    CommandDefinition(
        name="/createteam",
        description="Create a new team",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/createteam", "/createteam My Team Name"),
        feature="team_administration",
    ),
    CommandDefinition(
        name="/teamstatus",
        description="View team status",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/teamstatus",),
        feature="team_administration",
    ),
    CommandDefinition(
        name="/updateteam",
        description="Update team information",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/updateteam", "/updateteam name New Team Name"),
        feature="team_administration",
    ),
    CommandDefinition(
        name="/listmembers",
        description="List team members",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/listmembers",),
        feature="team_administration",
    ),
}

# =============================================================================
# HEALTH MONITORING COMMANDS
# =============================================================================

HEALTH_COMMANDS = {
    CommandDefinition(
        name="/healthcheck",
        description="Check system health",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/healthcheck", "/healthcheck detailed"),
        feature="health_monitoring",
    ),
    CommandDefinition(
        name="/systemstatus",
        description="View system status",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/systemstatus", "/systemstatus performance"),
        feature="health_monitoring",
    ),
    CommandDefinition(
        name="/logs",
        description="View system logs",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/logs", "/logs error", "/logs 50"),
        feature="health_monitoring",
    ),
    CommandDefinition(
        name="/restart",
        description="Restart system components",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/restart", "/restart agents", "/restart llm"),
        feature="health_monitoring",
    ),
    CommandDefinition(
        name="/alerts",
        description="Manage system alerts",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/alerts", "/alerts enable", "/alerts disable"),
        feature="health_monitoring",
    ),
}

# =============================================================================
# SYSTEM INFRASTRUCTURE COMMANDS
# =============================================================================

SYSTEM_INFRA_COMMANDS = {
    CommandDefinition(
        name="/config",
        description="View system configuration",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/config", "/config show", "/config validate"),
        feature="system_infrastructure",
    ),
    CommandDefinition(
        name="/backup",
        description="Create system backup",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/backup", "/backup full", "/backup data"),
        feature="system_infrastructure",
    ),
    CommandDefinition(
        name="/maintenance",
        description="Manage maintenance mode",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/maintenance", "/maintenance enable", "/maintenance disable"),
        feature="system_infrastructure",
    ),
    CommandDefinition(
        name="/diagnostics",
        description="Run system diagnostics",
        permission_level=PermissionLevel.ADMIN,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/diagnostics", "/diagnostics network", "/diagnostics performance"),
        feature="system_infrastructure",
    ),
}

# =============================================================================
# ALL COMMANDS COLLECTION
# =============================================================================

ALL_COMMANDS = (
    PLAYER_COMMANDS
    | LEADERSHIP_COMMANDS
    | SYSTEM_COMMANDS
    | MATCH_COMMANDS
    | TRAINING_COMMANDS
    | ATTENDANCE_COMMANDS
    | PAYMENT_COMMANDS
    | COMMUNICATION_COMMANDS
    | TEAM_ADMIN_COMMANDS
    | HEALTH_COMMANDS
    | SYSTEM_INFRA_COMMANDS
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
