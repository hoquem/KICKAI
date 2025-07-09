"""
Configuration module for KICKAI.
"""

from enum import Enum
from typing import Optional
from .improved_config_system import ImprovedConfigurationManager as BaseConfigurationManager


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigurationError(Exception):
    """Configuration error."""
    pass


# Remove legacy ConfigurationManager class and references 