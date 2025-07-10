#!/usr/bin/env python3
"""
Team Mapping Service for KICKAI

This service provides dynamic team ID resolution based on various context clues,
replacing hardcoded team IDs with a flexible mapping system.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Import centralized logging configuration
from core.logging_config import (
    get_logger, LogContext, LogMessages,
    log_system_event, log_performance
)

# Import core components
from database.interfaces import DataStoreInterface
from database.firebase_client import get_firebase_client

logger = get_logger(__name__)


class TeamMappingStrategy(Enum):
    """Team mapping strategies."""
    BOT_TOKEN = "bot_token"
    CHAT_ID = "chat_id"
    USER_CONTEXT = "user_context"
    DEFAULT = "default"


@dataclass
class TeamMapping:
    """Team mapping configuration."""
    team_id: str
    bot_token: Optional[str] = None
    bot_username: Optional[str] = None
    chat_ids: Optional[list] = None
    description: str = ""


class TeamMappingService:
    """
    Service for mapping context to team IDs.
    
    This service supports multiple strategies for determining which team
    a message belongs to based on bot token, chat ID, or user context.
    """
    
    def __init__(self, data_store=None):
        self._team_mappings: Dict[str, TeamMapping] = {}
        self._default_team_id: Optional[str] = None
        self._data_store = data_store or get_firebase_client()
        self._load_team_mappings()
    
    def _load_team_mappings(self):
        """Load team mappings from environment and configuration."""
        try:
            # Load environment variables from .env for production, .env.test only for tests
            try:
                from dotenv import load_dotenv
                if os.getenv('PYTEST_CURRENT_TEST') or os.getenv('E2E_TESTING'):
                    load_dotenv('.env.test')
                else:
                    load_dotenv('.env')
            except ImportError:
                pass

            # Load default team ID
            self._default_team_id = os.getenv("DEFAULT_TEAM_ID")
            
            # Load team mappings from environment variables
            main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID")
            leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID")
            
            if main_chat_id and leadership_chat_id:
                # Create default team mapping with leadership chat first, main chat second
                default_mapping = TeamMapping(
                    team_id=self._default_team_id,
                    bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
                    bot_username=os.getenv("TELEGRAM_BOT_USERNAME"),
                    chat_ids=[leadership_chat_id, main_chat_id],  # Leadership first, main second
                    description="Default team mapping from environment"
                )
                self._team_mappings[self._default_team_id] = default_mapping
                
                logger.info(f"Team mapping service initialized with {len(self._team_mappings)} mappings")
                for team_id, mapping in self._team_mappings.items():
                    logger.debug(f"Team mapping: {team_id} -> {mapping}")
            else:
                logger.warning("TELEGRAM_MAIN_CHAT_ID or TELEGRAM_LEADERSHIP_CHAT_ID not found in environment")
                
        except Exception as e:
            logger.error(f"Error loading team mappings: {e}")
            raise
    
    def get_team_id_by_bot_token(self, bot_token: str) -> Optional[str]:
        """Get team ID by bot token."""
        for mapping in self._team_mappings.values():
            if mapping.bot_token == bot_token:
                team_id = mapping.team_id
                logger.debug(f"Resolved team ID by bot token: {team_id}",
                           context=LogContext(component="team_mapping_service", operation="resolve_bot_token"))
                return team_id
        return None
    
    def get_team_id_by_bot_username(self, bot_username: str) -> Optional[str]:
        """Get team ID by bot username."""
        for mapping in self._team_mappings.values():
            if mapping.bot_username == bot_username:
                team_id = mapping.team_id
                logger.debug(f"Resolved team ID by bot username: {team_id}",
                           context=LogContext(component="team_mapping_service", operation="resolve_bot_username"))
                return team_id
        return None
    
    def get_team_id_by_chat_id(self, chat_id: str) -> Optional[str]:
        """Get team ID by chat ID."""
        for mapping in self._team_mappings.values():
            if mapping.chat_ids and chat_id in mapping.chat_ids:
                team_id = mapping.team_id
                logger.debug(f"Resolved team ID by chat ID: {team_id}",
                           context=LogContext(component="team_mapping_service", operation="resolve_chat_id"))
                return team_id
        return None
    
    async def get_team_id_by_user_context_async(self, user_id: str) -> Optional[str]:
        """
        Get team ID by user context (from database).
        Tries both team_members and players collections.
        Returns the first team_id found, or None.
        """
        log_context = LogContext(
            component="team_mapping_service",
            operation="resolve_user_context",
            user_id=user_id
        )
        
        # Try team_members by user_id or telegram_id
        filters = [
            {"field": "user_id", "operator": "==", "value": user_id}
        ]
        try:
            team_members = await self._data_store.query_documents("team_members", filters)
            if team_members:
                team_id = team_members[0].get("team_id")
                logger.debug(f"Resolved team ID by user context: {team_id}", context=log_context)
                return team_id
        except Exception as e:
            logger.warning(f"Failed to query team_members for user {user_id}: {e}", context=log_context)

        # Try players by id or telegram_id
        filters = [
            {"field": "id", "operator": "==", "value": user_id}
        ]
        try:
            players = await self._data_store.query_documents("players", filters)
            if players:
                team_id = players[0].get("team_id")
                logger.debug(f"Resolved team ID by user context: {team_id}", context=log_context)
                return team_id
        except Exception as e:
            logger.warning(f"Failed to query players for user {user_id}: {e}", context=log_context)

        # Try players by telegram_id
        filters = [
            {"field": "telegram_id", "operator": "==", "value": user_id}
        ]
        try:
            players = await self._data_store.query_documents("players", filters)
            if players:
                team_id = players[0].get("team_id")
                logger.debug(f"Resolved team ID by user context: {team_id}", context=log_context)
                return team_id
        except Exception as e:
            logger.warning(f"Failed to query players by telegram_id for user {user_id}: {e}", context=log_context)

        # Fallback
        logger.debug(f"Using default team ID: {self._default_team_id}", context=log_context)
        return self._default_team_id

    def get_team_id_by_user_context(self, user_id: str) -> Optional[str]:
        """
        Synchronous wrapper for get_team_id_by_user_context_async.
        For legacy compatibility. Will block the event loop if called in async context.
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Should not be called from async context; warn and fallback
                logger.warning("get_team_id_by_user_context called from async context; returning default team_id",
                              context=LogContext(component="team_mapping_service", user_id=user_id, operation="sync_wrapper"))
                return self._default_team_id
            return loop.run_until_complete(self.get_team_id_by_user_context_async(user_id))
        except Exception as e:
            logger.error(f"Error in get_team_id_by_user_context: {e}",
                        context=LogContext(component="team_mapping_service", user_id=user_id, operation="sync_wrapper"), exc_info=e)
            return self._default_team_id
    
    def resolve_team_id(self, 
                       bot_token: Optional[str] = None,
                       bot_username: Optional[str] = None,
                       chat_id: Optional[str] = None,
                       user_id: Optional[str] = None) -> str:
        """
        Resolve team ID using multiple strategies.
        
        Priority order:
        1. Bot token (most specific)
        2. Bot username
        3. Chat ID
        4. User context
        5. Default team ID (fallback)
        """
        log_context = LogContext(
            component="team_mapping_service",
            operation="resolve_team_id",
            user_id=user_id,
            chat_id=chat_id,
            metadata={
                "bot_token_provided": bot_token is not None,
                "bot_username_provided": bot_username is not None,
                "chat_id_provided": chat_id is not None,
                "user_id_provided": user_id is not None
            }
        )
        
        # Try bot token first
        if bot_token:
            team_id = self.get_team_id_by_bot_token(bot_token)
            if team_id:
                return team_id
        
        # Try bot username
        if bot_username:
            team_id = self.get_team_id_by_bot_username(bot_username)
            if team_id:
                return team_id
        
        # Try chat ID
        if chat_id:
            team_id = self.get_team_id_by_chat_id(chat_id)
            if team_id:
                return team_id
        
        # Try user context
        if user_id:
            team_id = self.get_team_id_by_user_context(user_id)
            if team_id:
                return team_id
        
        # Fallback to default
        if self._default_team_id:
            logger.warning("No team ID could be resolved, using hardcoded fallback",
                          context=log_context)
            return self._default_team_id
        
        # Last resort
        logger.error("No team ID could be resolved and no default available",
                    context=log_context)
        raise ValueError("Unable to resolve team ID from any available context")
    
    def get_team_mapping(self, team_id: str) -> Optional[TeamMapping]:
        """Get team mapping by team ID."""
        return self._team_mappings.get(team_id)
    
    def get_all_team_mappings(self) -> Dict[str, TeamMapping]:
        """Get all team mappings."""
        return self._team_mappings.copy()
    
    def get_all_mappings(self) -> Dict[str, TeamMapping]:
        """Get all team mappings (alias for get_all_team_mappings for compatibility)."""
        return self.get_all_team_mappings()
    
    def add_team_mapping(self, mapping: TeamMapping):
        """Add a new team mapping."""
        self._team_mappings[mapping.team_id] = mapping
        logger.info(f"Added team mapping for team {mapping.team_id}")
    
    def remove_team_mapping(self, team_id: str):
        """Remove a team mapping."""
        if team_id in self._team_mappings:
            del self._team_mappings[team_id]
            logger.info(f"Removed team mapping for team {team_id}")
    
    def get_default_team_id(self) -> Optional[str]:
        """Get the default team ID."""
        return self._default_team_id


# Global instance
_team_mapping_service: Optional[TeamMappingService] = None


def get_team_mapping_service(team_id: Optional[str] = None) -> TeamMappingService:
    """Get the global team mapping service instance."""
    global _team_mapping_service
    if _team_mapping_service is None:
        _team_mapping_service = TeamMappingService()
    return _team_mapping_service


def initialize_team_mapping_service(team_id: Optional[str] = None) -> TeamMappingService:
    """Initialize the team mapping service."""
    global _team_mapping_service
    _team_mapping_service = TeamMappingService()
    return _team_mapping_service 