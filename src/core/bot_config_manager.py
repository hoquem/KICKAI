"""
Bot Configuration Manager for KICKAI

This module provides centralized bot configuration management supporting:
- Local file-based configuration for testing/staging
- Firestore-based configuration for production
- Multiple teams with single bot for dual chats (main + leadership)
- Environment-specific configuration loading
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from .config import get_config, Environment
from ..database.firebase_client import get_firebase_client

logger = logging.getLogger(__name__)


class ChatType(Enum):
    """Chat types for different purposes."""
    MAIN = "main"
    LEADERSHIP = "leadership"


@dataclass
class ChatConfig:
    """Configuration for a single chat."""
    chat_id: str
    chat_type: ChatType
    is_active: bool = True


@dataclass
class BotConfig:
    """Configuration for a single bot with dual chats."""
    token: str
    username: str
    main_chat_id: str
    leadership_chat_id: str
    is_active: bool = True
    webhook_url: Optional[str] = None


@dataclass
class TeamConfig:
    """Configuration for a team with single bot and dual chats."""
    name: str
    description: str
    bot: BotConfig
    settings: Dict[str, Any] = field(default_factory=dict)
    team_id: Optional[str] = None


@dataclass
class BotConfiguration:
    """Complete bot configuration for an environment."""
    environment: str
    teams: Dict[str, TeamConfig]
    default_team: str
    firebase_config: Dict[str, Any] = field(default_factory=dict)
    ai_config: Dict[str, Any] = field(default_factory=dict)


class BotConfigManager:
    """Manages bot configurations across different environments."""
    
    def __init__(self):
        self.config = get_config()
        self.environment = self.config.environment
        self._bot_config: Optional[BotConfiguration] = None
        self._firebase_client = None
        
        # Initialize Firebase client for production
        if self.environment == Environment.PRODUCTION:
            try:
                self._firebase_client = get_firebase_client()
            except Exception as e:
                logger.warning(f"Failed to initialize Firebase client: {e}")
    
    def load_configuration(self) -> BotConfiguration:
        """Load bot configuration based on environment."""
        if self._bot_config is not None:
            return self._bot_config
        
        if self.environment == Environment.PRODUCTION:
            self._bot_config = self._load_production_config()
        else:
            self._bot_config = self._load_local_config()
        
        return self._bot_config
    
    def _load_local_config(self) -> BotConfiguration:
        """Load configuration from local JSON files with environment variable overrides."""
        config_path = self._get_config_file_path()
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return self._create_default_config()
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Validate and parse configuration
            teams = {}
            for team_id, team_data in data.get('teams', {}).items():
                teams[team_id] = self._parse_team_config_with_env_overrides(team_id, team_data)
            
            return BotConfiguration(
                environment=data.get('environment', self.environment.value),
                teams=teams,
                default_team=data.get('default_team', ''),
                firebase_config=data.get('firebase_config', {}),
                ai_config=data.get('ai_config', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to load local config: {e}")
            return self._create_default_config()
    
    def _load_production_config(self) -> BotConfiguration:
        """Load configuration from Firestore (production)."""
        if not self._firebase_client:
            raise RuntimeError("Firebase client not available for production config")
        
        try:
            # Load teams from Firestore
            teams = {}
            teams_ref = self._firebase_client.client.collection('teams')
            teams_query = teams_ref.where('is_active', '==', True)
            teams_docs = teams_query.stream()
            
            for team_doc in teams_docs:
                team_data = team_doc.to_dict()
                team_id = team_doc.id
                
                # Load bot configuration for this team
                bot_config = self._load_team_bot_from_firestore(team_id)
                
                if bot_config:  # Only include teams with active bots
                    teams[team_id] = TeamConfig(
                        name=team_data.get('name', 'Unknown'),
                        description=team_data.get('description', ''),
                        bot=bot_config,
                        settings=team_data.get('settings', {}),
                        team_id=team_id
                    )
            
            # Determine default team (first team or specified)
            default_team = list(teams.keys())[0] if teams else ''
            
            return BotConfiguration(
                environment='production',
                teams=teams,
                default_team=default_team,
                firebase_config={},
                ai_config={}
            )
            
        except Exception as e:
            logger.error(f"Failed to load production config: {e}")
            raise
    
    def _load_team_bot_from_firestore(self, team_id: str) -> Optional[BotConfig]:
        """Load bot configuration for a team from Firestore."""
        if not self._firebase_client:
            logger.error("Firebase client not available")
            return None
            
        try:
            bots_ref = self._firebase_client.client.collection('team_bots')
            query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
            docs = list(query.stream())
            
            if docs:
                bot_data = docs[0].to_dict()
                
                # Map database fields to expected field names
                return BotConfig(
                    token=bot_data.get('bot_token', ''),  # Database: bot_token
                    username=bot_data.get('bot_username', ''),  # Database: bot_username
                    main_chat_id=bot_data.get('chat_id', ''),  # Database: chat_id
                    leadership_chat_id=bot_data.get('leadership_chat_id', ''),  # Database: leadership_chat_id
                    is_active=bot_data.get('is_active', True)
                )
            
        except Exception as e:
            logger.error(f"Failed to load bot for team {team_id}: {e}")
        
        return None
    
    def _parse_team_config_with_env_overrides(self, team_id: str, team_data: Dict[str, Any]) -> TeamConfig:
        """Parse team configuration from JSON data with environment variable overrides for bot token and chat IDs."""
        
        # Get bot data from JSON
        bot_data = team_data.get('bot', {})
        
        # Use environment variables if available, otherwise use JSON values
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", bot_data.get('token', ''))
        bot_username = os.getenv("TELEGRAM_BOT_USERNAME", bot_data.get('username', ''))
        main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID", bot_data.get('main_chat_id', ''))
        leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID", bot_data.get('leadership_chat_id', ''))
        
        if bot_token:
            logger.info(f"Using environment variable for bot token in team {team_id}")
        else:
            logger.warning(f"No bot token found in environment or config for team {team_id}")
        
        if bot_username:
            logger.info(f"Using environment variable for bot username in team {team_id}")
        else:
            error_msg = f"CRITICAL ERROR: TELEGRAM_BOT_USERNAME environment variable is not set for team {team_id}. Bot cannot function without a valid username."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if main_chat_id:
            logger.info(f"Using environment variable for main chat ID in team {team_id}")
        else:
            logger.warning(f"No main chat ID found in environment or config for team {team_id}")
        
        if leadership_chat_id:
            logger.info(f"Using environment variable for leadership chat ID in team {team_id}")
        else:
            logger.warning(f"No leadership chat ID found in environment or config for team {team_id}")
        
        bot_config = BotConfig(
            token=bot_token,
            username=bot_username,
            main_chat_id=main_chat_id,
            leadership_chat_id=leadership_chat_id,
            is_active=bot_data.get('is_active', True)
        )
        
        return TeamConfig(
            name=team_data.get('name', team_id),
            description=team_data.get('description', ''),
            bot=bot_config,
            settings=team_data.get('settings', {}),
            team_id=team_id
        )
    
    def _get_config_file_path(self) -> Path:
        """Get the path to the configuration file for the current environment."""
        config_dir = Path("config")
        
        # Check for Railway staging environment specifically
        if os.getenv("RAILWAY_SERVICE_NAME", "").lower() in ["kickai-staging", "staging"]:
            return config_dir / "bot_config.staging.json"
        
        if self.environment == Environment.TESTING:
            return config_dir / "bot_config.json"
        elif self.environment == Environment.DEVELOPMENT:
            return config_dir / "bot_config.json"
        else:
            # Production or other environments
            return config_dir / f"bot_config.{self.environment.value}.json"
    
    def _create_default_config(self) -> BotConfiguration:
        """Create a default configuration when no config file is found."""
        logger.warning("Creating default bot configuration")
        
        return BotConfiguration(
            environment=self.environment.value,
            teams={},
            default_team='',
            firebase_config={},
            ai_config={}
        )
    
    def get_team_config(self, team_id: str) -> Optional[TeamConfig]:
        """Get configuration for a specific team."""
        config = self.load_configuration()
        return config.teams.get(team_id)
    
    def get_bot_config(self, team_id: str) -> Optional[BotConfig]:
        """Get bot configuration for a specific team."""
        team_config = self.get_team_config(team_id)
        if team_config:
            return team_config.bot
        return None
    
    def get_default_team_config(self) -> Optional[TeamConfig]:
        """Get configuration for the default team."""
        config = self.load_configuration()
        if config.default_team:
            return config.teams.get(config.default_team)
        return None
    
    def get_all_teams(self) -> List[str]:
        """Get list of all team IDs."""
        config = self.load_configuration()
        return list(config.teams.keys())
    
    def get_bot_token(self, team_id: str) -> str:
        """Get bot token for a team."""
        bot_config = self.get_bot_config(team_id)
        if bot_config:
            return bot_config.token
        return ''
    
    def get_chat_ids(self, team_id: str) -> Dict[ChatType, str]:
        """Get chat IDs for a team."""
        bot_config = self.get_bot_config(team_id)
        if not bot_config:
            return {}
        
        return {
            ChatType.MAIN: bot_config.main_chat_id,
            ChatType.LEADERSHIP: bot_config.leadership_chat_id
        }
    
    def is_leadership_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if a chat is a leadership chat for the team."""
        bot_config = self.get_bot_config(team_id)
        if not bot_config:
            return False
        
        return str(chat_id) == str(bot_config.leadership_chat_id)
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration and return any errors."""
        errors = []
        config = self.load_configuration()
        
        if not config.teams:
            errors.append("No teams configured")
            return errors
        
        for team_id, team_config in config.teams.items():
            bot_config = team_config.bot
            
            if not bot_config.token:
                errors.append(f"Team '{team_id}' has no bot token")
            
            if not bot_config.username:
                errors.append(f"Team '{team_id}' has no bot username")
            
            if not bot_config.main_chat_id:
                errors.append(f"Team '{team_id}' has no main chat ID")
            
            if not bot_config.leadership_chat_id:
                errors.append(f"Team '{team_id}' has no leadership chat ID")
        
        # Check default team
        if config.default_team and config.default_team not in config.teams:
            errors.append(f"Default team '{config.default_team}' not found in teams")
        
        return errors
    
    def save_local_config(self, config: BotConfiguration) -> bool:
        """Save configuration to local file (for testing/staging only)."""
        if self.environment == Environment.PRODUCTION:
            logger.error("Cannot save local config in production environment")
            return False
        
        try:
            config_path = self._get_config_file_path()
            config_path.parent.mkdir(exist_ok=True)
            
            # Convert to JSON-serializable format
            data = {
                'environment': config.environment,
                'teams': {},
                'default_team': config.default_team,
                'firebase_config': config.firebase_config,
                'ai_config': config.ai_config
            }
            
            for team_id, team_config in config.teams.items():
                data['teams'][team_id] = {
                    'name': team_config.name,
                    'description': team_config.description,
                    'bot': {
                        'token': team_config.bot.token,
                        'username': team_config.bot.username,
                        'main_chat_id': team_config.bot.main_chat_id,
                        'leadership_chat_id': team_config.bot.leadership_chat_id,
                        'is_active': team_config.bot.is_active
                    },
                    'settings': team_config.settings
                }
            
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False


def get_bot_config_manager() -> BotConfigManager:
    """Get the bot configuration manager instance."""
    return BotConfigManager()


def initialize_bot_config_manager() -> BotConfigManager:
    """Initialize and return a new bot configuration manager instance."""
    return BotConfigManager() 