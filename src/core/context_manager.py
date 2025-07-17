#!/usr/bin/env python3
"""
Context Manager for KICKAI

This module provides a centralized, robust context management system that handles:
- User identification and player mapping
- Team ID resolution
- Chat type detection
- Context propagation throughout the system
- Welcome messages for unregistered users

Follows clean architecture principles with proper separation of concerns.
"""

import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from telegram import Update
from telegram.ext import ContextTypes

from core.settings import Settings
from domain.interfaces.team_operations import ITeamOperations
from domain.interfaces.player_operations import IPlayerOperations
from services.access_control_service import AccessControlService
from database.models_improved import Player, OnboardingStatus

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """User context information for a message."""
    user_id: str
    chat_id: str
    team_id: Optional[str]
    player_id: Optional[str]
    is_leadership_chat: bool
    is_registered: bool
    is_in_correct_team: bool
    onboarding_message: Optional[str] = None
    username: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ContextManager:
    """
    Centralized context manager for KICKAI.
    
    This class is responsible for:
    1. Resolving team_id from chat_id
    2. Resolving player_id from telegram_id
    3. Validating that the player is in the correct team for the chat
    4. Determining if the chat is a leadership chat
    5. Providing onboarding messages for unregistered users
    """
    
    def __init__(self, team_operations: ITeamOperations = None, player_operations: IPlayerOperations = None):
        self.settings = Settings()
        self.team_operations = team_operations
        self.player_operations = player_operations
        self.access_control_service = AccessControlService()
        self.logger = logging.getLogger(__name__)
        
        # Fallback to legacy pattern for backward compatibility
        if not self.team_operations:
            from services.team_mapping_service import TeamMappingService
            from database.firebase_client import FirebaseClient
            from core.cache.cache_manager import CacheManager
            from core.settings import get_settings
            settings = get_settings()
            firebase_client = FirebaseClient(settings)
            cache_manager = CacheManager()
            self.team_operations = TeamMappingService(firebase_client, cache_manager)
        if not self.player_operations:
            from services.player_service import get_player_service
            self.player_operations = get_player_service()
        
    async def build_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str) -> UserContext:
        """
        Build comprehensive user context for a message.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            message_text: The message text
            
        Returns:
            UserContext object with all resolved information
        """
        try:
            user_id = str(update.effective_user.id)
            chat_id = str(update.effective_chat.id)
            username = update.effective_user.username or "unknown"
            
            self.logger.info(f"[CONTEXT] Building context for user {username} ({user_id}) in chat {chat_id}")
            
            # Step 1: Resolve team_id from chat_id
            team_id = await self._resolve_team_id(chat_id)
            self.logger.info(f"[CONTEXT] Step 1: Resolved team_id={team_id} for chat_id={chat_id}")
            
            # Step 2: Determine if this is a leadership chat
            is_leadership_chat = self.access_control_service.is_leadership_chat(chat_id, team_id)
            self.logger.info(f"[CONTEXT] Step 2: Determined is_leadership_chat={is_leadership_chat}")
            
            # Step 3: Resolve player_id from telegram_id
            player_id = await self._resolve_player_id(user_id)
            self.logger.info(f"[CONTEXT] Step 3: Resolved player_id={player_id} for user_id={user_id}")
            
            # Step 4: Validate player registration and team membership
            is_registered = player_id is not None
            is_in_correct_team = False
            onboarding_message = None
            
            if is_registered and team_id:
                is_in_correct_team = await self._validate_player_team_membership(player_id, team_id)
                self.logger.info(f"[CONTEXT] Step 4: Validated player team membership: {is_in_correct_team}")
            
            # Step 5: Generate onboarding message if needed
            if not is_registered or not is_in_correct_team:
                onboarding_message = self._generate_onboarding_message(is_registered, is_in_correct_team, team_id)
                self.logger.info(f"[CONTEXT] Step 5: Generated onboarding message for unregistered/misplaced user")
            
            # Create and return the context
            user_context = UserContext(
                user_id=user_id,
                chat_id=chat_id,
                team_id=team_id,
                player_id=player_id,
                is_leadership_chat=is_leadership_chat,
                is_registered=is_registered,
                is_in_correct_team=is_in_correct_team,
                onboarding_message=onboarding_message,
                username=username
            )
            
            self.logger.info(f"[CONTEXT] ✅ Context built successfully: {user_context}")
            return user_context
            
        except Exception as e:
            self.logger.error(f"[CONTEXT] ❌ Error building context: {e}", exc_info=True)
            # Return a minimal context with error information
            return UserContext(
                user_id=str(update.effective_user.id),
                chat_id=str(update.effective_chat.id),
                team_id=None,
                player_id=None,
                is_leadership_chat=False,
                is_registered=False,
                is_in_correct_team=False,
                onboarding_message="Sorry, I'm having trouble processing your request. Please try again later.",
                username=update.effective_user.username or "unknown"
            )
    
    async def _resolve_team_id(self, chat_id: str) -> Optional[str]:
        """
        Resolve team_id from chat_id using team mapping service.
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Team ID if found, None otherwise
        """
        try:
            # Check if this is a main chat
            main_chat_id = self.settings.telegram_main_chat_id
            if chat_id == main_chat_id:
                team_id = self.settings.team_id
                self.logger.info(f"[CONTEXT] Chat {chat_id} is main chat, using team_id={team_id}")
                return team_id
            
            # Check if this is a leadership chat
            leadership_chat_id = self.settings.telegram_leadership_chat_id
            if chat_id == leadership_chat_id:
                team_id = self.settings.team_id
                self.logger.info(f"[CONTEXT] Chat {chat_id} is leadership chat, using team_id={team_id}")
                return team_id
            
            # For now, assume it's the main team if not explicitly configured
            # In a multi-team setup, this would use the team mapping service
            team_id = self.settings.team_id
            self.logger.info(f"[CONTEXT] Chat {chat_id} mapped to default team_id={team_id}")
            return team_id
            
        except Exception as e:
            self.logger.error(f"[CONTEXT] Error resolving team_id for chat {chat_id}: {e}")
            return None
    
    async def _resolve_player_id(self, user_id: str) -> Optional[str]:
        """
        Resolve player_id from telegram user_id.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Player ID if found, None otherwise
        """
        try:
            # Get player by telegram ID
            player = await self.player_operations.get_player_by_telegram_id(user_id)
            if player:
                self.logger.info(f"[CONTEXT] Found player {player.player_id} for user {user_id}")
                return player.player_id
            else:
                self.logger.info(f"[CONTEXT] No player found for user {user_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"[CONTEXT] Error resolving player_id for user {user_id}: {e}")
            return None
    
    async def _validate_player_team_membership(self, player_id: str, team_id: str) -> bool:
        """
        Validate that a player is a member of the specified team.
        
        Args:
            player_id: Player ID
            team_id: Team ID
            
        Returns:
            True if player is in the team, False otherwise
        """
        try:
            player = await self.player_operations.get_player_by_id(player_id, team_id)
            if player and player.team_id == team_id:
                self.logger.info(f"[CONTEXT] Player {player_id} is confirmed member of team {team_id}")
                return True
            else:
                self.logger.warning(f"[CONTEXT] Player {player_id} is not a member of team {team_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"[CONTEXT] Error validating player team membership: {e}")
            return False
    
    def _generate_onboarding_message(self, is_registered: bool, is_in_correct_team: bool, team_id: Optional[str]) -> str:
        """
        Generate an appropriate onboarding message based on user status.
        
        Args:
            is_registered: Whether the user is registered
            is_in_correct_team: Whether the user is in the correct team
            team_id: The team ID for the chat
            
        Returns:
            Onboarding message string
        """
        if not is_registered:
            return (
                "🤖 **Welcome to KICKAI!**\n\n"
                "I'm your AI-powered football team management assistant. "
                "To use the system, you need to join a football team first.\n\n"
                "**Next Steps:**\n"
                "1. Ask a team admin to add you to their team\n"
                "2. They'll send you an invitation to join the team chat room\n"
                "3. Once added, you'll be able to use all the features!\n\n"
                "If you're already a team member, please contact your team admin for assistance."
            )
        elif not is_in_correct_team:
            return (
                "⚠️ **Team Access Issue**\n\n"
                "You're registered with KICKAI, but you're not a member of this team's chat room. "
                "Please contact your team admin to be added to the correct team chat.\n\n"
                "If you believe this is an error, please contact support."
            )
        else:
            return None  # No onboarding message needed


# Singleton instance
_context_manager = None


def get_context_manager() -> ContextManager:
    """Get the singleton context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


def reset_context_manager() -> None:
    """Reset the context manager (useful for testing)."""
    global _context_manager
    _context_manager = None 