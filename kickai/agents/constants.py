"""
Constants for CrewAI agent system configuration.

This module centralizes configuration values to eliminate magic numbers
and improve maintainability across the agent system.
"""

# CrewAI System Configuration
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BACKOFF_FACTOR = 2
DEFAULT_MAX_ITERATIONS = 3
DEFAULT_TASK_DESCRIPTION_LIMIT = 500
DEFAULT_RESULT_PREVIEW_LIMIT = 100
DEFAULT_VERBOSE_MODE = True
DEFAULT_MEMORY_ENABLED = False

# Memory and Truncation Configuration
MEMORY_HISTORY_LIMIT = 1
COMMAND_TRUNCATE_LENGTH = 50
RESPONSE_TYPE_TRUNCATE_LENGTH = 50

# REMOVED: Hardcoded routing constants
# These have been removed to enforce native CrewAI routing:
# - SIMPLE_SYSTEM_COMMANDS (used hardcoded command lists)
# - AGENT_NAME_MAPPING (used for pattern-based routing)
# - COMMAND_PATTERNS (used for command extraction)
# - COMMON_COMMAND_WORDS (used for keyword matching)
#
# All routing is now handled by agent LLM intelligence and native CrewAI delegation

# Logging Configuration
LOG_LEVELS = {
    'DEBUG': 'debug',
    'INFO': 'info', 
    'WARNING': 'warning',
    'ERROR': 'error'
}
