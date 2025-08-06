#!/usr/bin/env python3
"""
KICKAI Centralized Constants - Single Source of Truth

This module contains all constants used across the KICKAI system.
This is the ONLY place where these constants should be defined to prevent
inconsistencies and maintenance issues.

References:
- https://realpython.com/python-constants/
- Fail-fast principle: https://en.wikipedia.org/wiki/Fail-fast_system
"""

import os
from dataclasses import dataclass, field
from typing import Final

from kickai.core.enums import ChatType, PermissionLevel

# =============================================================================
# SYSTEM CONSTANTS
# =============================================================================

BOT_VERSION: Final[str] = "2.0.0"

# =============================================================================
# NETWORK CONSTANTS
# =============================================================================

class NetworkConstants:
    """Network-related constants."""

    # Default ports for services
    DEFAULT_MOCK_TELEGRAM_PORT: Final[int] = 8001
    DEFAULT_FIREBASE_PORT: Final[int] = 9099
    DEFAULT_OLLAMA_PORT: Final[int] = 11434
    DEFAULT_HTTP_PORT: Final[int] = 8000
    DEFAULT_WEBSOCKET_PORT: Final[int] = 8001

    # Default hosts
    DEFAULT_HOST: Final[str] = "localhost"
    DEFAULT_OLLAMA_HOST: Final[str] = "macmini1.local"

    # URL Templates (use .format() for substitution)
    MOCK_TELEGRAM_URL_TEMPLATE: Final[str] = "http://{host}:{port}"
    OLLAMA_URL_TEMPLATE: Final[str] = "http://{host}:{port}"
    WEBSOCKET_URL_TEMPLATE: Final[str] = "ws://{host}:{port}/ws"

    @classmethod
    def get_default_mock_telegram_url(cls) -> str:
        """Get default mock telegram URL."""
        return cls.MOCK_TELEGRAM_URL_TEMPLATE.format(
            host=cls.DEFAULT_HOST,
            port=cls.DEFAULT_MOCK_TELEGRAM_PORT
        )

    @classmethod
    def get_default_ollama_url(cls) -> str:
        """Get default Ollama URL."""
        return cls.OLLAMA_URL_TEMPLATE.format(
            host=cls.DEFAULT_OLLAMA_HOST,
            port=cls.DEFAULT_OLLAMA_PORT
        )


# =============================================================================
# TIMEOUT CONSTANTS
# =============================================================================

class TimeoutConstants:
    """Timeout-related constants in seconds."""

    # HTTP timeouts
    HTTP_CONNECTION_TIMEOUT: Final[float] = 30.0
    HTTP_REQUEST_TIMEOUT: Final[float] = 120.0
    HTTP_SHORT_TIMEOUT: Final[float] = 5.0
    HTTP_LONG_TIMEOUT: Final[float] = 600.0  # 10 minutes

    # Database timeouts
    FIREBASE_TIMEOUT: Final[int] = 30
    DATABASE_QUERY_TIMEOUT: Final[float] = 60.0

    # AI/LLM timeouts
    OLLAMA_CONNECTION_TIMEOUT: Final[float] = 30.0
    OLLAMA_REQUEST_TIMEOUT: Final[float] = 120.0
    AI_GENERATION_TIMEOUT: Final[int] = 120

    # WebSocket timeouts
    WEBSOCKET_CONNECT_TIMEOUT: Final[float] = 10.0
    WEBSOCKET_MESSAGE_TIMEOUT: Final[float] = 5.0

    # Process timeouts
    PROCESS_SHUTDOWN_TIMEOUT: Final[float] = 10.0
    SYSTEM_STARTUP_TIMEOUT: Final[float] = 60.0


# =============================================================================
# RETRY CONSTANTS
# =============================================================================

class RetryConstants:
    """Retry and circuit breaker constants."""

    # Retry attempts
    DEFAULT_MAX_RETRIES: Final[int] = 3
    DATABASE_MAX_RETRIES: Final[int] = 5
    NETWORK_MAX_RETRIES: Final[int] = 3
    AI_MAX_RETRIES: Final[int] = 5

    # Retry delays (seconds)
    DEFAULT_RETRY_DELAY: Final[float] = 1.0
    MIN_RETRY_WAIT: Final[float] = 1.0
    MAX_RETRY_WAIT: Final[float] = 10.0
    EXPONENTIAL_BACKOFF_MULTIPLIER: Final[float] = 2.0

    # Circuit breaker settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: Final[int] = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: Final[float] = 60.0
    CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS: Final[int] = 3


# =============================================================================
# LIMIT CONSTANTS
# =============================================================================

class LimitConstants:
    """Limit and size constants."""

    # Data limits
    DEFAULT_QUERY_LIMIT: Final[int] = 100
    MAX_QUERY_LIMIT: Final[int] = 1000
    FIREBASE_BATCH_SIZE: Final[int] = 500

    # String length limits
    MIN_NAME_LENGTH: Final[int] = 2
    MAX_NAME_LENGTH: Final[int] = 100
    MIN_TEAM_ID_LENGTH: Final[int] = 2
    MAX_TEAM_ID_LENGTH: Final[int] = 20
    MIN_PHONE_DIGITS: Final[int] = 10

    # AI token limits
    DEFAULT_AI_MAX_TOKENS: Final[int] = 800
    AI_MAX_TOKENS_TOOLS: Final[int] = 500
    AI_MAX_TOKENS_CREATIVE: Final[int] = 1000

    # Pool limits
    HTTP_CONNECTION_POOL_SIZE: Final[int] = 1000


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

class ValidationConstants:
    """Validation patterns and constants."""

    # Regular expressions
    TEAM_ID_PATTERN: Final[str] = r"^[A-Z0-9]+$"
    PHONE_CLEANUP_PATTERN: Final[str] = r'[\x00-\x1f\x7f-\x9f]'

    # UK phone number constants
    UK_COUNTRY_CODE: Final[str] = "+44"
    UK_MOBILE_PREFIX: Final[str] = "44"

    # Validation messages
    TEAM_ID_TOO_SHORT_MSG: Final[str] = "Team ID must be at least {min} characters"
    TEAM_ID_TOO_LONG_MSG: Final[str] = "Team ID must be less than {max} characters"
    NAME_TOO_SHORT_MSG: Final[str] = "Name must be at least {min} characters"
    NAME_TOO_LONG_MSG: Final[str] = "Name must be less than {max} characters"
    PHONE_TOO_SHORT_MSG: Final[str] = "Phone number must have at least {min} digits"


# =============================================================================
# AI CONSTANTS
# =============================================================================

class AIConstants:
    """AI and LLM constants."""

    # Temperature settings
    AI_TEMPERATURE_DEFAULT: Final[float] = 0.3
    AI_TEMPERATURE_TOOLS: Final[float] = 0.1
    AI_TEMPERATURE_CREATIVE: Final[float] = 0.7
    AI_TEMPERATURE_MIN: Final[float] = 0.0
    AI_TEMPERATURE_MAX: Final[float] = 1.0

    # Default models
    DEFAULT_OLLAMA_MODEL: Final[str] = "llama3.2:3b"
    DEFAULT_GOOGLE_MODEL: Final[str] = "gemini-1.5-flash"
    DEFAULT_HUGGINGFACE_MODEL: Final[str] = "Qwen/Qwen2.5-1.5B-Instruct"

    # Model configurations
    TOOL_CALLING_MODEL: Final[str] = "llama3.2:1b"  # For precision
    CREATIVE_MODEL: Final[str] = "llama3.2:3b"      # For reasoning
    ANALYTICAL_MODEL: Final[str] = "llama3.2:3b"    # For analysis


# =============================================================================
# ENVIRONMENT CONSTANTS
# =============================================================================

class EnvironmentConstants:
    """Environment variable names and defaults."""

    # Firebase environment variables
    FIREBASE_PROJECT_ID: Final[str] = "FIREBASE_PROJECT_ID"
    FIREBASE_CREDENTIALS_FILE: Final[str] = "FIREBASE_CREDENTIALS_FILE"
    FIREBASE_CREDENTIALS_JSON: Final[str] = "FIREBASE_CREDENTIALS_JSON"

    # AI environment variables
    OLLAMA_BASE_URL: Final[str] = "OLLAMA_BASE_URL"
    OLLAMA_MODEL: Final[str] = "OLLAMA_MODEL"
    AI_PROVIDER: Final[str] = "AI_PROVIDER"

    # Mock environment variables
    MOCK_TELEGRAM_BASE_URL: Final[str] = "MOCK_TELEGRAM_BASE_URL"
    MOCK_TELEGRAM_PORT: Final[str] = "MOCK_TELEGRAM_PORT"

    # Security environment variables
    KICKAI_INVITE_SECRET_KEY: Final[str] = "KICKAI_INVITE_SECRET_KEY"


# =============================================================================
# STATUS CONSTANTS
# =============================================================================

class StatusConstants:
    """Status codes and messages."""

    # HTTP status codes that we handle specially
    HTTP_OK: Final[int] = 200
    HTTP_CREATED: Final[int] = 201
    HTTP_BAD_REQUEST: Final[int] = 400
    HTTP_UNAUTHORIZED: Final[int] = 401
    HTTP_FORBIDDEN: Final[int] = 403
    HTTP_NOT_FOUND: Final[int] = 404
    HTTP_INTERNAL_SERVER_ERROR: Final[int] = 500
    HTTP_SERVICE_UNAVAILABLE: Final[int] = 503

    # System status messages
    STATUS_ONLINE: Final[str] = "Online"
    STATUS_OFFLINE: Final[str] = "Offline"
    STATUS_ERROR: Final[str] = "Error"
    STATUS_CHECKING: Final[str] = "Checking..."
    STATUS_CONNECTED: Final[str] = "Connected"
    STATUS_DISCONNECTED: Final[str] = "Disconnected"

# =============================================================================
# FIRESTORE CONSTANTS
# =============================================================================

FIRESTORE_COLLECTION_PREFIX = "kickai"


def get_team_members_collection(team_id: str) -> str:
    """Get the collection name for team members."""
    return f"{FIRESTORE_COLLECTION_PREFIX}_{team_id}_team_members"


def get_players_collection(team_id: str) -> str:
    """Get the collection name for players."""
    return f"{FIRESTORE_COLLECTION_PREFIX}_{team_id}_players"


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
        name="/myinfo",
        description="View your player information",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/myinfo",),
        feature="shared",
    ),
    CommandDefinition(
        name="/status",
        description="Check your current status",
        permission_level=PermissionLevel.PLAYER,
        chat_types=frozenset([ChatType.MAIN]),
        examples=("/status", "/status MH123", "/status +447123456789"),
        feature="shared",
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
}

# =============================================================================
# SYSTEM COMMANDS
# =============================================================================

SYSTEM_COMMANDS = {
    CommandDefinition(
        name="/help",
        description="Show available commands",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/help", "/help register"),
        feature="shared",
    ),
    CommandDefinition(
        name="/list",
        description="List team members or players (context-aware)",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/list", "/list players", "/list members"),
        feature="shared",
    ),
    CommandDefinition(
        name="/update",
        description="Update your information (context-aware for players/team members)",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=(
            "/update phone 07123456789",
            "/update position midfielder",
            "/update email admin@example.com",
        ),
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
    CommandDefinition(
        name="/deletematch",
        description="Delete a match (Leadership only)",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/deletematch", "/deletematch MATCH123"),
        feature="match_management",
    ),
    CommandDefinition(
        name="/availableplayers",
        description="Get list of available players for a match",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/availableplayers", "/availableplayers MATCH123"),
        feature="match_management",
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
}

# =============================================================================
# PAYMENT COMMANDS


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

# Commands removed: /createteam, /teamstatus, /updateteam, /listmembers
# /list command will handle listing all players and members in leadership chat
TEAM_ADMIN_COMMANDS = set()

# =============================================================================
# ALL COMMANDS COLLECTION
# =============================================================================

ALL_COMMANDS = (
    PLAYER_COMMANDS
    | LEADERSHIP_COMMANDS
    | SYSTEM_COMMANDS
    | MATCH_COMMANDS
    | ATTENDANCE_COMMANDS
    | COMMUNICATION_COMMANDS
    | TEAM_ADMIN_COMMANDS
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


def get_commands_for_chat_type(chat_type: ChatType) -> list[CommandDefinition]:
    """Get all commands available for a specific chat type."""
    return sorted(COMMANDS_BY_CHAT_TYPE.get(chat_type, []), key=lambda x: x.name)


def get_commands_for_permission_level(permission_level: PermissionLevel) -> list[CommandDefinition]:
    """Get all commands available for a specific permission level."""
    return sorted(COMMANDS_BY_PERMISSION.get(permission_level, []), key=lambda x: x.name)


def get_commands_for_feature(feature: str) -> list[CommandDefinition]:
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
# UTILITY FUNCTIONS FOR CONFIGURATION
# =============================================================================

def get_environment_with_default(env_var: str, default: str, required: bool = False) -> str:
    """
    Get environment variable with default value (fail-fast approach).

    Args:
        env_var: Environment variable name
        default: Default value to use
        required: Whether the environment variable is required

    Returns:
        Environment variable value or default

    Raises:
        ValueError: If required environment variable is missing
    """
    value = os.getenv(env_var, default)

    if required and not value:
        raise ValueError(f"Required environment variable {env_var} is not set")

    return value


def get_mock_telegram_url() -> str:
    """Get mock telegram URL from environment or default."""
    return get_environment_with_default(
        EnvironmentConstants.MOCK_TELEGRAM_BASE_URL,
        NetworkConstants.get_default_mock_telegram_url()
    )


def get_ollama_url() -> str:
    """Get Ollama URL from environment or default."""
    return get_environment_with_default(
        EnvironmentConstants.OLLAMA_BASE_URL,
        NetworkConstants.get_default_ollama_url()
    )


def get_mock_telegram_port() -> int:
    """Get mock telegram port from environment or default (fail-fast validation)."""
    port_str = get_environment_with_default(
        EnvironmentConstants.MOCK_TELEGRAM_PORT,
        str(NetworkConstants.DEFAULT_MOCK_TELEGRAM_PORT)
    )

    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} is not in valid range 1-65535")
        return port
    except ValueError as e:
        raise ValueError(f"Invalid port value '{port_str}': {e}")


def validate_timeout(timeout: float, name: str) -> None:
    """Validate timeout value (fail-fast)."""
    if timeout <= 0:
        raise ValueError(f"{name} must be positive, got {timeout}")


def validate_retry_count(retries: int, name: str) -> None:
    """Validate retry count (fail-fast)."""
    if retries < 0:
        raise ValueError(f"{name} must be non-negative, got {retries}")


def validate_temperature(temperature: float) -> None:
    """Validate AI temperature (fail-fast)."""
    if not (AIConstants.AI_TEMPERATURE_MIN <= temperature <= AIConstants.AI_TEMPERATURE_MAX):
        raise ValueError(
            f"Temperature must be between {AIConstants.AI_TEMPERATURE_MIN} "
            f"and {AIConstants.AI_TEMPERATURE_MAX}, got {temperature}"
        )


def validate_constants() -> None:
    """
    Validate all constants at module import time (fail-fast principle).

    Raises:
        ValueError: If any constant has invalid values.
    """
    # Validate timeout constants
    validate_timeout(TimeoutConstants.HTTP_CONNECTION_TIMEOUT, "HTTP_CONNECTION_TIMEOUT")
    validate_timeout(TimeoutConstants.HTTP_REQUEST_TIMEOUT, "HTTP_REQUEST_TIMEOUT")

    if TimeoutConstants.HTTP_REQUEST_TIMEOUT <= TimeoutConstants.HTTP_CONNECTION_TIMEOUT:
        raise ValueError("HTTP_REQUEST_TIMEOUT must be greater than HTTP_CONNECTION_TIMEOUT")

    # Validate retry constants
    validate_retry_count(RetryConstants.DEFAULT_MAX_RETRIES, "DEFAULT_MAX_RETRIES")
    validate_timeout(RetryConstants.MIN_RETRY_WAIT, "MIN_RETRY_WAIT")
    validate_timeout(RetryConstants.MAX_RETRY_WAIT, "MAX_RETRY_WAIT")

    if RetryConstants.MAX_RETRY_WAIT <= RetryConstants.MIN_RETRY_WAIT:
        raise ValueError("MAX_RETRY_WAIT must be greater than MIN_RETRY_WAIT")

    # Validate AI constants
    validate_temperature(AIConstants.AI_TEMPERATURE_DEFAULT)
    validate_temperature(AIConstants.AI_TEMPERATURE_TOOLS)
    validate_temperature(AIConstants.AI_TEMPERATURE_CREATIVE)

    # Validate limit constants
    if LimitConstants.MAX_QUERY_LIMIT <= LimitConstants.DEFAULT_QUERY_LIMIT:
        raise ValueError("MAX_QUERY_LIMIT must be greater than DEFAULT_QUERY_LIMIT")

    if LimitConstants.MIN_NAME_LENGTH <= 0:
        raise ValueError("MIN_NAME_LENGTH must be positive")

    if LimitConstants.MAX_NAME_LENGTH <= LimitConstants.MIN_NAME_LENGTH:
        raise ValueError("MAX_NAME_LENGTH must be greater than MIN_NAME_LENGTH")


# Validate constants on module import (fail-fast principle)
validate_constants()
