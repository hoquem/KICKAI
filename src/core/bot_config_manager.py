"""
Bot Configuration Manager for KICKAI

This module provides centralized bot configuration management supporting:
- Local file-based configuration for testing/staging
- Firestore-based configuration for production
- Multiple teams with dual bots (main + leadership)
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


class BotType(Enum):
    """Bot types for different chat purposes."""
    MAIN = "main"
    LEADERSHIP = "leadership"


@dataclass
class BotConfig:
    """Configuration for a single bot."""
    token: str
    username: str
    chat_id: str
    is_active: bool = True
    webhook_url: Optional[str] = None


@dataclass
class TeamConfig:
    """Configuration for a team with dual bots."""
    name: str
    description: str
    bots: Dict[BotType, BotConfig]
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
            teams_ref = self._firebase_client.collection('teams')
            teams_query = teams_ref.where('is_active', '==', True)
            teams_docs = teams_query.stream()
            
            for team_doc in teams_docs:
                team_data = team_doc.to_dict()
                team_id = team_doc.id
                
                # Load bot mappings for this team
                bots = self._load_team_bots_from_firestore(team_id)
                
                if bots:  # Only include teams with active bots
                    teams[team_id] = TeamConfig(
                        name=team_data.get('name', 'Unknown'),
                        description=team_data.get('description', ''),
                        bots=bots,
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
    
    def _load_team_bots_from_firestore(self, team_id: str) -> Dict[BotType, BotConfig]:
        """Load bot configurations for a team from Firestore."""
        bots = {}
        
        try:
            # Load main bot
            main_bot = self._get_bot_from_firestore(team_id, BotType.MAIN)
            if main_bot:
                bots[BotType.MAIN] = main_bot
            
            # Load leadership bot
            leadership_bot = self._get_bot_from_firestore(team_id, BotType.LEADERSHIP)
            if leadership_bot:
                bots[BotType.LEADERSHIP] = leadership_bot
            
        except Exception as e:
            logger.error(f"Failed to load bots for team {team_id}: {e}")
        
        return bots
    
    def _get_bot_from_firestore(self, team_id: str, bot_type: BotType) -> Optional[BotConfig]:
        """Get a specific bot configuration from Firestore."""
        try:
            bots_ref = self._firebase_client.collection('team_bots')
            
            if bot_type == BotType.MAIN:
                # Main bot uses the standard chat_id
                query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
            else:
                # Leadership bot uses leadership_chat_id
                query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
            
            docs = list(query.stream())
            
            if docs:
                bot_data = docs[0].to_dict()
                
                # Determine chat_id based on bot type
                if bot_type == BotType.MAIN:
                    chat_id = bot_data.get('chat_id')
                else:
                    chat_id = bot_data.get('leadership_chat_id')
                
                if chat_id:
                    return BotConfig(
                        token=bot_data.get('bot_token', ''),
                        username=bot_data.get('bot_username', ''),
                        chat_id=chat_id,
                        is_active=bot_data.get('is_active', True)
                    )
            
        except Exception as e:
            logger.error(f"Failed to get {bot_type.value} bot for team {team_id}: {e}")
        
        return None
    
    def _parse_team_config_with_env_overrides(self, team_id: str, team_data: Dict[str, Any]) -> TeamConfig:
        """Parse team configuration from JSON data with environment variable overrides for bot tokens and chat IDs."""
        bots = {}
        
        # Parse main bot with environment variable overrides
        if 'main' in team_data.get('bots', {}):
            main_bot_data = team_data['bots']['main']
            # Use environment variable if available, otherwise use JSON value
            main_token = os.getenv("TELEGRAM_BOT_TOKEN", main_bot_data.get('token', ''))
            main_chat_id = os.getenv("TELEGRAM_CHAT_ID", main_bot_data.get('chat_id', ''))
            
            if main_token:
                logger.info(f"Using environment variable for main bot token in team {team_id}")
            else:
                logger.warning(f"No main bot token found in environment or config for team {team_id}")
            
            if main_chat_id:
                logger.info(f"Using environment variable for main bot chat ID in team {team_id}")
            else:
                logger.warning(f"No main bot chat ID found in environment or config for team {team_id}")
            
            bots[BotType.MAIN] = BotConfig(
                token=main_token,
                username=main_bot_data.get('username', ''),
                chat_id=main_chat_id,
                is_active=main_bot_data.get('is_active', True)
            )
        
        # Parse leadership bot with environment variable overrides
        if 'leadership' in team_data.get('bots', {}):
            leadership_bot_data = team_data['bots']['leadership']
            # Use environment variable if available, otherwise use JSON value
            leadership_token = os.getenv("TELEGRAM_LEADERSHIP_BOT_TOKEN", leadership_bot_data.get('token', ''))
            leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID", leadership_bot_data.get('chat_id', ''))
            
            if leadership_token:
                logger.info(f"Using environment variable for leadership bot token in team {team_id}")
            else:
                logger.warning(f"No leadership bot token found in environment or config for team {team_id}")
            
            if leadership_chat_id:
                logger.info(f"Using environment variable for leadership bot chat ID in team {team_id}")
            else:
                logger.warning(f"No leadership bot chat ID found in environment or config for team {team_id}")
            
            bots[BotType.LEADERSHIP] = BotConfig(
                token=leadership_token,
                username=leadership_bot_data.get('username', ''),
                chat_id=leadership_chat_id,
                is_active=leadership_bot_data.get('is_active', True)
            )
        
        return TeamConfig(
            name=team_data.get('name', team_id),
            description=team_data.get('description', ''),
            bots=bots,
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
    
    def get_bot_config(self, team_id: str, bot_type: BotType) -> Optional[BotConfig]:
        """Get configuration for a specific bot."""
        team_config = self.get_team_config(team_id)
        if team_config:
            return team_config.bots.get(bot_type)
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
    
    def get_team_bot_tokens(self, team_id: str) -> Dict[BotType, str]:
        """Get bot tokens for a team."""
        team_config = self.get_team_config(team_id)
        if not team_config:
            return {}
        
        tokens = {}
        for bot_type, bot_config in team_config.bots.items():
            if bot_config.is_active:
                tokens[bot_type] = bot_config.token
        
        return tokens
    
    def get_team_chat_ids(self, team_id: str) -> Dict[BotType, str]:
        """Get chat IDs for a team."""
        team_config = self.get_team_config(team_id)
        if not team_config:
            return {}
        
        chat_ids = {}
        for bot_type, bot_config in team_config.bots.items():
            if bot_config.is_active:
                chat_ids[bot_type] = bot_config.chat_id
        
        return chat_ids
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration and return any errors."""
        errors = []
        config = self.load_configuration()
        
        if not config.teams:
            errors.append("No teams configured")
            return errors
        
        for team_id, team_config in config.teams.items():
            # Check if team has at least one bot
            if not team_config.bots:
                errors.append(f"Team '{team_id}' has no bots configured")
                continue
            
            # Validate each bot
            for bot_type, bot_config in team_config.bots.items():
                if not bot_config.token:
                    errors.append(f"Team '{team_id}' {bot_type.value} bot has no token")
                
                if not bot_config.username:
                    errors.append(f"Team '{team_id}' {bot_type.value} bot has no username")
                
                if not bot_config.chat_id:
                    errors.append(f"Team '{team_id}' {bot_type.value} bot has no chat ID")
        
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
                    'bots': {},
                    'settings': team_config.settings
                }
                
                for bot_type, bot_config in team_config.bots.items():
                    data['teams'][team_id]['bots'][bot_type.value] = {
                        'token': bot_config.token,
                        'username': bot_config.username,
                        'chat_id': bot_config.chat_id,
                        'is_active': bot_config.is_active
                    }
            
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False


# Global instance
_bot_config_manager: Optional[BotConfigManager] = None


def get_bot_config_manager() -> BotConfigManager:
    """Get the global bot configuration manager instance."""
    global _bot_config_manager
    if _bot_config_manager is None:
        _bot_config_manager = BotConfigManager()
    return _bot_config_manager


def initialize_bot_config_manager() -> BotConfigManager:
    """Initialize the global bot configuration manager."""
    global _bot_config_manager
    _bot_config_manager = BotConfigManager()
    return _bot_config_manager 