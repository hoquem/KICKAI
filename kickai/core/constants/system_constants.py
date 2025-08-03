"""
System-wide constants for KICKAI.

This module contains fundamental system constants that are used across
the entire application.
"""

from dataclasses import dataclass
from kickai.core.enums import ChatType


@dataclass(frozen=True)
class SystemConstants:
    """System-wide configuration constants."""
    
    # Application Information
    APP_NAME: str = "KICKAI"
    APP_VERSION: str = "3.1"
    BOT_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "AI-Powered Football Team Management System"
    
    # System Limits
    MAX_TEAMS_PER_INSTANCE: int = 100
    MAX_PLAYERS_PER_TEAM: int = 50
    MAX_TEAM_MEMBERS_PER_TEAM: int = 20
    MAX_MESSAGE_LENGTH: int = 4096
    MAX_COMMAND_ARGUMENTS: int = 10
    
    # Cache Settings
    DEFAULT_CACHE_TTL_SECONDS: int = 300  # 5 minutes
    LONG_CACHE_TTL_SECONDS: int = 3600    # 1 hour
    SHORT_CACHE_TTL_SECONDS: int = 60     # 1 minute
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    MIN_PAGE_SIZE: int = 1
    
    # File Size Limits
    MAX_FILE_SIZE_MB: int = 10
    MAX_IMAGE_SIZE_MB: int = 5
    MAX_DOCUMENT_SIZE_MB: int = 20
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT_PER_MINUTE: int = 60
    ADMIN_RATE_LIMIT_PER_MINUTE: int = 120
    PUBLIC_RATE_LIMIT_PER_MINUTE: int = 30
    
    # Session Management
    SESSION_TIMEOUT_MINUTES: int = 60
    MAX_CONCURRENT_SESSIONS: int = 5
    SESSION_CLEANUP_INTERVAL_MINUTES: int = 15
    
    # Security
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    PASSWORD_HASH_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Monitoring
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    METRICS_COLLECTION_INTERVAL_SECONDS: int = 60
    LOG_RETENTION_DAYS: int = 30
    
    # Feature Flags
    ENABLE_ANALYTICS: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_AUDIT_LOGGING: bool = True
    
    @classmethod
    def get_max_retries_for_operation(cls, operation_type: str) -> int:
        """Get max retries for specific operation types."""
        retry_map = {
            "database": 3,
            "api_call": 2,
            "file_upload": 2,
            "notification": 1,
            "analytics": 1,
        }
        return retry_map.get(operation_type, 1)
    
    @classmethod
    def get_timeout_for_operation(cls, operation_type: str) -> int:
        """Get timeout in seconds for specific operation types."""
        timeout_map = {
            "database": 30,
            "api_call": 15,
            "file_upload": 60,
            "notification": 10,
            "analytics": 5,
        }
        return timeout_map.get(operation_type, 10)

    @classmethod
    def normalize_chat_type(cls, chat_type: str) -> ChatType:
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

    @classmethod
    def get_chat_type_display_name(cls, chat_type: ChatType) -> str:
        """Get display name for chat type."""
        display_names = {
            ChatType.MAIN: "Main Chat",
            ChatType.LEADERSHIP: "Leadership Chat",
            ChatType.PRIVATE: "Private Chat",
        }
        return display_names.get(chat_type, str(chat_type.value))

    @classmethod
    def get_chat_type_description(cls, chat_type: ChatType) -> str:
        """Get description for chat type."""
        descriptions = {
            ChatType.MAIN: "Main team chat for all players",
            ChatType.LEADERSHIP: "Leadership chat for team management",
            ChatType.PRIVATE: "Private messages with the bot",
        }
        return descriptions.get(chat_type, "Unknown chat type")