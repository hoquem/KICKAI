"""
Timeout constants for KICKAI.

This module contains constants related to timeouts, retry logic,
and performance-related configuration.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeoutConstants:
    """Timeout and performance configuration constants."""

    # Database Operation Timeouts (seconds)
    DATABASE_CONNECTION_TIMEOUT: int = 30
    DATABASE_QUERY_TIMEOUT: int = 15
    DATABASE_TRANSACTION_TIMEOUT: int = 45
    DATABASE_BULK_OPERATION_TIMEOUT: int = 60

    # API Call Timeouts (seconds)
    EXTERNAL_API_TIMEOUT: int = 30
    TELEGRAM_API_TIMEOUT: int = 25
    LLM_API_TIMEOUT: int = 60
    WEBHOOK_TIMEOUT: int = 15

    # Agent System Timeouts (seconds)
    AGENT_EXECUTION_TIMEOUT: int = 60
    TOOL_EXECUTION_TIMEOUT: int = 30
    CREW_EXECUTION_TIMEOUT: int = 120
    AGENT_INITIALIZATION_TIMEOUT: int = 45

    # File Operation Timeouts (seconds)
    FILE_UPLOAD_TIMEOUT: int = 60
    FILE_DOWNLOAD_TIMEOUT: int = 45
    FILE_PROCESSING_TIMEOUT: int = 120

    # Cache Timeouts (seconds)
    CACHE_OPERATION_TIMEOUT: int = 5
    CACHE_CLEANUP_TIMEOUT: int = 30

    # Network Timeouts (seconds)
    HTTP_CONNECTION_TIMEOUT: int = 10
    HTTP_READ_TIMEOUT: int = 30
    HTTP_TOTAL_TIMEOUT: int = 45

    # Retry Configuration
    DEFAULT_MAX_RETRIES: int = 3
    DATABASE_MAX_RETRIES: int = 3
    API_CALL_MAX_RETRIES: int = 2
    FILE_OPERATION_MAX_RETRIES: int = 2
    AGENT_EXECUTION_MAX_RETRIES: int = 1

    # Retry Delays (seconds)
    DEFAULT_RETRY_DELAY: float = 1.0
    DATABASE_RETRY_DELAY: float = 2.0
    API_CALL_RETRY_DELAY: float = 1.5
    FILE_OPERATION_RETRY_DELAY: float = 3.0

    # Exponential Backoff
    RETRY_BACKOFF_MULTIPLIER: float = 2.0
    MAX_RETRY_DELAY: float = 30.0

    # Health Check Timeouts (seconds)
    HEALTH_CHECK_TIMEOUT: int = 10
    COMPONENT_HEALTH_TIMEOUT: int = 5
    SYSTEM_HEALTH_TIMEOUT: int = 30

    # Session Timeouts (seconds)
    USER_SESSION_TIMEOUT: int = 3600        # 1 hour
    ADMIN_SESSION_TIMEOUT: int = 7200       # 2 hours
    API_SESSION_TIMEOUT: int = 1800         # 30 minutes

    # Background Task Timeouts (seconds)
    BACKGROUND_TASK_TIMEOUT: int = 300      # 5 minutes
    SCHEDULED_TASK_TIMEOUT: int = 600       # 10 minutes
    CLEANUP_TASK_TIMEOUT: int = 1800        # 30 minutes

    # Performance Limits
    MAX_CONCURRENT_OPERATIONS: int = 10
    MAX_QUEUE_SIZE: int = 100
    OPERATION_THROTTLE_DELAY: float = 0.1

    @classmethod
    def get_timeout_for_operation(cls, operation_type: str) -> int:
        """
        Get timeout value for specific operation type.

        Args:
            operation_type: Type of operation

        Returns:
            Timeout in seconds
        """
        timeout_map = {
            # Database operations
            "database_connection": cls.DATABASE_CONNECTION_TIMEOUT,
            "database_query": cls.DATABASE_QUERY_TIMEOUT,
            "database_transaction": cls.DATABASE_TRANSACTION_TIMEOUT,
            "database_bulk": cls.DATABASE_BULK_OPERATION_TIMEOUT,

            # API operations
            "external_api": cls.EXTERNAL_API_TIMEOUT,
            "telegram_api": cls.TELEGRAM_API_TIMEOUT,
            "llm_api": cls.LLM_API_TIMEOUT,
            "webhook": cls.WEBHOOK_TIMEOUT,

            # Agent operations
            "agent_execution": cls.AGENT_EXECUTION_TIMEOUT,
            "tool_execution": cls.TOOL_EXECUTION_TIMEOUT,
            "crew_execution": cls.CREW_EXECUTION_TIMEOUT,
            "agent_init": cls.AGENT_INITIALIZATION_TIMEOUT,

            # File operations
            "file_upload": cls.FILE_UPLOAD_TIMEOUT,
            "file_download": cls.FILE_DOWNLOAD_TIMEOUT,
            "file_processing": cls.FILE_PROCESSING_TIMEOUT,

            # Network operations
            "http_connection": cls.HTTP_CONNECTION_TIMEOUT,
            "http_read": cls.HTTP_READ_TIMEOUT,
            "http_total": cls.HTTP_TOTAL_TIMEOUT,

            # Health checks
            "health_check": cls.HEALTH_CHECK_TIMEOUT,
            "component_health": cls.COMPONENT_HEALTH_TIMEOUT,
            "system_health": cls.SYSTEM_HEALTH_TIMEOUT,

            # Background tasks
            "background_task": cls.BACKGROUND_TASK_TIMEOUT,
            "scheduled_task": cls.SCHEDULED_TASK_TIMEOUT,
            "cleanup_task": cls.CLEANUP_TASK_TIMEOUT,
        }

        return timeout_map.get(operation_type, 30)  # Default 30 seconds

    @classmethod
    def get_retry_config_for_operation(cls, operation_type: str) -> dict[str, any]:
        """
        Get retry configuration for specific operation type.

        Args:
            operation_type: Type of operation

        Returns:
            Dictionary containing retry configuration
        """
        retry_configs = {
            "database": {
                "max_retries": cls.DATABASE_MAX_RETRIES,
                "delay": cls.DATABASE_RETRY_DELAY,
                "backoff_multiplier": cls.RETRY_BACKOFF_MULTIPLIER,
                "max_delay": cls.MAX_RETRY_DELAY,
            },
            "api_call": {
                "max_retries": cls.API_CALL_MAX_RETRIES,
                "delay": cls.API_CALL_RETRY_DELAY,
                "backoff_multiplier": cls.RETRY_BACKOFF_MULTIPLIER,
                "max_delay": cls.MAX_RETRY_DELAY,
            },
            "file_operation": {
                "max_retries": cls.FILE_OPERATION_MAX_RETRIES,
                "delay": cls.FILE_OPERATION_RETRY_DELAY,
                "backoff_multiplier": cls.RETRY_BACKOFF_MULTIPLIER,
                "max_delay": cls.MAX_RETRY_DELAY,
            },
            "agent_execution": {
                "max_retries": cls.AGENT_EXECUTION_MAX_RETRIES,
                "delay": cls.DEFAULT_RETRY_DELAY,
                "backoff_multiplier": 1.0,  # No backoff for agents
                "max_delay": cls.DEFAULT_RETRY_DELAY,
            },
        }

        return retry_configs.get(operation_type, {
            "max_retries": cls.DEFAULT_MAX_RETRIES,
            "delay": cls.DEFAULT_RETRY_DELAY,
            "backoff_multiplier": cls.RETRY_BACKOFF_MULTIPLIER,
            "max_delay": cls.MAX_RETRY_DELAY,
        })

    @classmethod
    def calculate_retry_delay(
        cls,
        attempt: int,
        base_delay: float = None,
        multiplier: float = None,
        max_delay: float = None
    ) -> float:
        """
        Calculate retry delay with exponential backoff.

        Args:
            attempt: Current retry attempt (0-based)
            base_delay: Base delay in seconds
            multiplier: Backoff multiplier
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds for this attempt
        """
        base_delay = base_delay or cls.DEFAULT_RETRY_DELAY
        multiplier = multiplier or cls.RETRY_BACKOFF_MULTIPLIER
        max_delay = max_delay or cls.MAX_RETRY_DELAY

        delay = base_delay * (multiplier ** attempt)
        return min(delay, max_delay)

    @classmethod
    def get_performance_limits(cls) -> dict[str, int]:
        """
        Get performance limit configuration.

        Returns:
            Dictionary containing performance limits
        """
        return {
            "max_concurrent_operations": cls.MAX_CONCURRENT_OPERATIONS,
            "max_queue_size": cls.MAX_QUEUE_SIZE,
            "throttle_delay": cls.OPERATION_THROTTLE_DELAY,
        }
