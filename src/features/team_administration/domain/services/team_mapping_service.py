#!/usr/bin/env python3
"""
Team mapping service for KICKAI.

This service handles the mapping between Telegram chat IDs and team IDs,
with intelligent fallback mechanisms.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TeamMappingService:
    """
    Service for managing team mappings.
    
    This service provides a clean interface for resolving team IDs from
    chat IDs, with intelligent fallback mechanisms.
    """
    
    def __init__(self):
        """Initialize the team mapping service."""
        self._default_team_id = None
        self._chat_mappings: Dict[str, str] = {}
        
        logger.info("TeamMappingService initialized")
    
    def set_default_team_id(self, team_id: str) -> None:
        """Set the default team ID for fallback scenarios."""
        self._default_team_id = team_id
        logger.info(f"Default team ID set to: {team_id}")
    
    def get_default_team_id(self) -> Optional[str]:
        """Get the default team ID."""
        return self._default_team_id
    
    def add_chat_mapping(self, chat_id: str, team_id: str) -> None:
        """Add a chat ID to team ID mapping."""
        self._chat_mappings[str(chat_id)] = team_id
        logger.info(f"Added chat mapping: {chat_id} -> {team_id}")
    
    def get_team_id_for_chat(self, chat_id: str) -> Optional[str]:
        """
        Get team ID for a chat ID.
        
        Resolution order:
        1. In-memory mapping (fastest)
        2. Environment lookup
        3. Default team ID (fallback)
        4. None (if no mapping found)
        """
        chat_id_str = str(chat_id)
        
        # 1. Check in-memory mapping first (fastest)
        if chat_id_str in self._chat_mappings:
            logger.debug(f"Team ID found in memory: {chat_id} -> {self._chat_mappings[chat_id_str]}")
            return self._chat_mappings[chat_id_str]
        
        # 2. Check if this is a known chat ID from environment
        team_id = self._get_team_id_from_environment(chat_id_str)
        if team_id:
            # Add to memory mapping for future fast access
            self._chat_mappings[chat_id_str] = team_id
            logger.info(f"Team ID resolved from environment: {chat_id} -> {team_id}")
            return team_id
        
        # 3. Use default team ID as fallback
        if self._default_team_id:
            logger.warning(f"No team mapping found for chat {chat_id}, using default: {self._default_team_id}")
            return self._default_team_id
        
        logger.warning(f"No team mapping found for chat {chat_id} and no default team ID set")
        return None
    
    def _get_team_id_from_environment(self, chat_id: str) -> Optional[str]:
        """Get team ID from environment variables for known chat IDs."""
        try:
            from core.settings import get_settings
            settings = get_settings()
            
            # Check if this is the main chat
            if str(settings.telegram_main_chat_id) == chat_id:
                return settings.default_team_id
            
            # Check if this is the leadership chat
            if str(settings.telegram_leadership_chat_id) == chat_id:
                return settings.default_team_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting team ID from environment: {e}")
            return None
    
    async def load_mappings_from_firestore(self) -> None:
        """Load team mappings from Firestore and cache them."""
        try:
            from database.firebase_client import FirebaseClient
            from core.settings import get_settings
            
            settings = get_settings()
            firebase_client = FirebaseClient(settings)
            
            # Query team mappings from the bot_mappings collection
            # Note: FirebaseClient adds 'kickai_' prefix, so we use COLLECTION_BOT_MAPPINGS
            mappings = await firebase_client.query_documents(COLLECTION_BOT_MAPPINGS, [])
            
            for mapping in mappings:
                chat_id = mapping.get('chat_id')
                team_id = mapping.get('team_id')
                
                if chat_id and team_id:
                    self.add_chat_mapping(str(chat_id), team_id)
            
            logger.info(f"Loaded {len(mappings)} team mappings from Firestore")
            
        except Exception as e:
            logger.error(f"Error loading team mappings from Firestore: {e}")
    
    async def save_mapping_to_firestore(self, chat_id: str, team_id: str) -> bool:
        """Save a team mapping to Firestore."""
        try:
            from database.firebase_client import FirebaseClient
            from core.settings import get_settings
            
            settings = get_settings()
            firebase_client = FirebaseClient(settings)
            
            mapping_data = {
                'chat_id': str(chat_id),
                'team_id': team_id,
                'created_at': firebase_client.get_current_timestamp()
            }
            
            # Save to Firestore
            # Note: FirebaseClient adds 'kickai_' prefix, so we use COLLECTION_BOT_MAPPINGS
            await firebase_client.create_document(COLLECTION_BOT_MAPPINGS, mapping_data)
            
            # Update local cache
            self.add_chat_mapping(chat_id, team_id)
            
            logger.info(f"Saved team mapping to Firestore: {chat_id} -> {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving team mapping to Firestore: {e}")
            return False
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Get all current chat to team mappings."""
        return self._chat_mappings.copy()
    
    def clear_mappings(self) -> None:
        """Clear all mappings (useful for testing)."""
        self._chat_mappings.clear()
        # Note: This doesn't clear the cache, just the in-memory mappings
        logger.info("Cleared all team mappings")
    
    def get_mapping_stats(self) -> Dict[str, Any]:
        """Get statistics about team mappings."""
        return {
            "total_mappings": len(self._chat_mappings),
            "default_team_id": self._default_team_id,
            "mappings": self._chat_mappings.copy()
        } 