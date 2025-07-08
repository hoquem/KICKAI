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


class ConfigurationManager(BaseConfigurationManager):
    """Configuration manager wrapper."""
    
    def __init__(self):
        super().__init__()

    @property
    def environment(self):
        return self.configuration.environment

    @property
    def ai(self):
        return self.configuration.ai

    @property
    def database(self):
        return self.configuration.database

    @property
    def telegram(self):
        return self.configuration.telegram

    @property
    def team(self):
        return self.configuration.team

    @property
    def payment(self):
        return self.configuration.payment

    @property
    def llm(self):
        return self.configuration.llm

    @property
    def advanced_memory(self):
        return self.configuration.advanced_memory

    @property
    def logging(self):
        return self.configuration.logging

    @property
    def performance(self):
        return self.configuration.performance

    @property
    def security(self):
        return self.configuration.security

    @classmethod
    def get_instance(cls) -> 'ConfigurationManager':
        """Get singleton instance."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance 