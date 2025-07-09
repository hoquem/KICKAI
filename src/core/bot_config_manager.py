"""
Bot Configuration Manager for KICKAI

This module manages bot configuration and settings.
"""

import logging
from typing import Dict, Any, Optional, List
from core.improved_config_system import get_improved_config

logger = logging.getLogger(__name__)


class BotConfigManager:
    """Manager for bot configuration and settings."""
    
    def __init__(self):
        self.config = get_improved_config()
        logger.info("✅ BotConfigManager initialized")
    
    def get_bot_token(self) -> str:
        """Get the bot token from configuration."""
        return self.config.telegram.bot_token
    
    def get_team_id(self) -> str:
        """Get the default team ID from configuration."""
        return self.config.team.default_team_id
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "project_id": self.config.database.project_id
        }
    
    def get_payment_config(self) -> Dict[str, Any]:
        """Get payment configuration."""
        return {
            "collectiv_api_key": self.config.payment.collectiv_api_key,
            "collectiv_base_url": self.config.payment.collectiv_base_url
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return {
            "provider": self.config.llm.provider,
            "model": self.config.llm.model,
            "api_key": self.config.llm.api_key
        }
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return self.config.environment.mode == "development"
    
    def get_log_level(self) -> str:
        """Get logging level from configuration."""
        return self.config.logging.level

    def get_onboarding_steps(self, team_id: str) -> Optional[List[str]]:
        """Get the onboarding steps for a specific team."""
        # Return default onboarding steps since team-specific config is not available
        return [
            "personal_info",
            "emergency_contact", 
            "date_of_birth",
            "position_confirmation"
        ]

    def get_daily_report_config(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get the daily report configuration for a specific team."""
        # Return default daily report config
        return {
            "enabled": True,
            "time": "09:00",
            "timezone": "UTC",
            "channels": ["main", "leadership"]
        }

    def get_financial_report_config(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get the financial report configuration for a specific team."""
        # Return default financial report config
        return {
            "enabled": True,
            "frequency": "weekly",
            "day": "monday",
            "time": "10:00",
            "timezone": "UTC"
        }

    def get_bot_config(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get bot configuration for a specific team."""
        # For now, return the default bot configuration
        # In the future, this could be extended to support team-specific bot configs
        return {
            "token": self.get_bot_token(),
            "team_id": team_id,
            "parse_mode": "MarkdownV2",
            "message_timeout": 30
        }


# Global instance
_bot_config_manager: Optional[BotConfigManager] = None


def get_bot_config_manager() -> BotConfigManager:
    """Get the global bot config manager instance."""
    global _bot_config_manager
    if _bot_config_manager is None:
        _bot_config_manager = BotConfigManager()
    return _bot_config_manager


def initialize_bot_config_manager() -> BotConfigManager:
    """Initialize the global bot config manager."""
    global _bot_config_manager
    _bot_config_manager = BotConfigManager()
    return _bot_config_manager 