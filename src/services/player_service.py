"""
Player Service for KICKAI

This module provides business logic for player management including
registration, validation, and team operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import re
from uuid import uuid4
import logging

from ..core.exceptions import (
    PlayerError, PlayerNotFoundError, PlayerValidationError, 
    PlayerDuplicateError, create_error_context
)
from ..database.interfaces import DataStoreInterface
from ..database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus
from .interfaces.player_service_interface import IPlayerService


class PlayerService(IPlayerService):
    """Service for player management operations."""
    
    def __init__(self, data_store=None, team_id: Optional[str] = None):
        if data_store is None:
            from ..database.firebase_client import get_firebase_client
            self._data_store = get_firebase_client()
        else:
            self._data_store = data_store
        self._team_id = team_id
    
    async def create_player(self, name: str, phone: str, team_id: str, 
                          email: Optional[str] = None, position: PlayerPosition = PlayerPosition.UTILITY,
                          role: PlayerRole = PlayerRole.PLAYER, fa_registered: bool = False) -> Player:
        """Create a new player with validation."""
        try:
            # Validate input data
            self._validate_player_data(name, phone, email, team_id)
            
            # Check for duplicate phone number in the same team
            existing_player = await self._data_store.get_player_by_phone(phone)
            if existing_player:
                raise PlayerDuplicateError(
                    f"Player with phone {phone} already exists in team {team_id}",
                    create_error_context("create_player", team_id=team_id, additional_info={'phone': phone})
                )
            
            # Create player object
            player = Player(
                name=name.strip(),
                phone=phone.strip(),
                email=email.strip() if email else None,
                position=position,
                role=role,
                fa_registered=fa_registered,
                fa_eligible=True,  # Default to eligible
                team_id=team_id
            )
            
            # Save to database
            player_id = await self._data_store.create_player(player)
            player.id = player_id
            
            logging.info(
                f"Player created successfully: {player.name} ({player_id})"
            )
            
            return player
            
        except (PlayerError, PlayerDuplicateError):
            raise
        except Exception as e:
            logging.error("Failed to create player")
            raise PlayerError(
                f"Failed to create player: {str(e)}",
                create_error_context("create_player", team_id=team_id)
            )
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        try:
            player = await self._data_store.get_player(player_id)
            if player:
                logging.info(
                    f"Player retrieved: {player.name}"
                )
            return player
            
        except Exception as e:
            logging.error("Failed to get player")
            raise PlayerError(
                f"Failed to get player: {str(e)}",
                create_error_context("get_player", entity_id=player_id)
            )
    
    async def update_player(self, player_id: str, **updates) -> Player:
        """Update a player with validation."""
        try:
            # Get existing player
            player = await self.get_player(player_id)
            if not player:
                raise PlayerNotFoundError(
                    f"Player not found: {player_id}",
                    create_error_context("update_player", entity_id=player_id)
                )
            
            # Validate updates if they include validation fields
            if 'name' in updates:
                self._validate_name(updates['name'])
            if 'phone' in updates:
                self._validate_phone(updates['phone'])
                # Check for duplicate phone if changed
                if updates['phone'] != player.phone:
                    existing_player = await self._data_store.get_player_by_phone(updates['phone'])
                    if existing_player and existing_player.id != player_id:
                        raise PlayerDuplicateError(
                            f"Player with phone {updates['phone']} already exists in team {player.team_id}",
                            create_error_context("update_player", entity_id=player_id, team_id=player.team_id)
                        )
            if 'email' in updates:
                self._validate_email(updates['email'])
            
            # Update player
            player.update(**updates)
            
            # Save to database
            success = await self._data_store.update_player(player)
            if not success:
                raise PlayerError(
                    "Failed to update player in database",
                    create_error_context("update_player", entity_id=player_id)
                )
            
            logging.info(
                f"Player updated: {player.name}"
            )
            
            return player
            
        except (PlayerError, PlayerNotFoundError, PlayerDuplicateError):
            raise
        except Exception as e:
            logging.error("Failed to update player")
            raise PlayerError(
                f"Failed to update player: {str(e)}",
                create_error_context("update_player", entity_id=player_id)
            )
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        try:
            # Get player first to log the operation
            player = await self.get_player(player_id)
            if not player:
                raise PlayerNotFoundError(
                    f"Player not found: {player_id}",
                    create_error_context("delete_player", entity_id=player_id)
                )
            
            # Delete from database
            success = await self._data_store.delete_player(player_id)
            if not success:
                raise PlayerError(
                    "Failed to delete player from database",
                    create_error_context("delete_player", entity_id=player_id)
                )
            
            logging.info(
                f"Player deleted: {player.name}"
            )
            
            return True
            
        except (PlayerError, PlayerNotFoundError):
            raise
        except Exception as e:
            logging.error("Failed to delete player")
            raise PlayerError(
                f"Failed to delete player: {str(e)}",
                create_error_context("delete_player", entity_id=player_id)
            )
    
    async def get_team_players(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        try:
            players = await self._data_store.get_players_by_team(team_id)
            
            logging.info(
                f"Retrieved {len(players)} players for team {team_id}"
            )
            
            return players
            
        except Exception as e:
            logging.error("Failed to get team players")
            raise PlayerError(
                f"Failed to get team players: {str(e)}",
                create_error_context("get_team_players", team_id=team_id)
            )
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number and team."""
        try:
            player = await self._data_store.get_player_by_phone(phone)
            return player
            
        except Exception as e:
            logging.error("Failed to get player by phone")
            raise PlayerError(
                f"Failed to get player by phone: {str(e)}",
                create_error_context("get_player_by_phone", team_id=team_id, additional_info={'phone': phone})
            )
    
    async def update_onboarding_status(self, player_id: str, status: OnboardingStatus) -> Player:
        """Update player onboarding status."""
        return await self.update_player(player_id, onboarding_status=status)
    
    async def generate_invite_link(self, player_id: str, invite_link: str) -> Player:
        """Generate and store invite link for a player."""
        return await self.update_player(player_id, invite_link=invite_link)
    
    def _validate_player_data(self, name: str, phone: str, email: Optional[str], team_id: str):
        """Validate player data."""
        self._validate_name(name)
        self._validate_phone(phone)
        if email:
            self._validate_email(email)
        self._validate_team_id(team_id)
    
    def _validate_name(self, name: str):
        """Validate player name."""
        if not name or not name.strip():
            raise PlayerValidationError(
                "Player name cannot be empty",
                create_error_context("validate_name")
            )
        
        if len(name.strip()) < 2:
            raise PlayerValidationError(
                "Player name must be at least 2 characters long",
                create_error_context("validate_name")
            )
        
        if len(name.strip()) > 100:
            raise PlayerValidationError(
                "Player name cannot exceed 100 characters",
                create_error_context("validate_name")
            )
    
    def _validate_phone(self, phone: str):
        """Validate phone number."""
        if not phone or not phone.strip():
            raise PlayerValidationError(
                "Phone number cannot be empty",
                create_error_context("validate_phone")
            )
        
        # Clean the phone number
        phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # UK phone number validation - more lenient
        # Mobile: 07xxx, 08xxx, +447xxx, +448xxx
        # Landline: 01xxx, 02xxx, +441xxx, +442xxx
        phone_pattern = r'^(\+44|0)(7\d{9}|8\d{9}|1\d{9}|2\d{9})$'
        if not re.match(phone_pattern, phone_clean):
            raise PlayerValidationError(
                "Invalid phone number format. Must be a valid UK phone number (e.g., 07123456789, +447123456789)",
                create_error_context("validate_phone")
            )
    
    def _validate_email(self, email: str):
        """Validate email address."""
        if not email or not email.strip():
            return  # Email is optional
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email.strip()):
            raise PlayerValidationError(
                "Invalid email format",
                create_error_context("validate_email")
            )
    
    def _validate_team_id(self, team_id: str):
        """Validate team ID."""
        if not team_id or not team_id.strip():
            raise PlayerValidationError(
                "Team ID cannot be empty",
                create_error_context("validate_team_id")
            )
    
    async def generate_player_id(self, name: str) -> str:
        """Generate a unique player ID from name."""
        if not name:
            return ""
        
        # Split name into first and last name
        name_parts = name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]
        else:
            first_name = name
            last_name = ""
        
        # Use the new ID generator system
        from ..utils.id_generator import generate_player_id as generate_human_readable_id
        
        # Get existing player IDs to avoid collisions
        existing_ids = set()
        try:
            # Get all existing player IDs from the database
            if self._team_id:
                players = await self._data_store.get_players_by_team(self._team_id)
                existing_ids = {player.player_id for player in players if player.player_id}
        except Exception as e:
            logging.warning(f"Could not load existing player IDs for collision detection: {e}")
        
        return generate_human_readable_id(first_name, last_name, existing_ids)


# Global player service instance
_player_service: Optional[PlayerService] = None


def get_player_service(data_store=None) -> PlayerService:
    """Get the global player service instance with optional data store injection."""
    global _player_service
    if _player_service is None:
        if data_store is None:
            # Use Firebase client for production
            from ..database.firebase_client import get_firebase_client
            data_store = get_firebase_client()
        _player_service = PlayerService(data_store=data_store)
    return _player_service


def initialize_player_service(data_store=None) -> PlayerService:
    """Initialize the global player service with optional data store injection."""
    global _player_service
    if data_store is None:
        # Use Firebase client for production
        from ..database.firebase_client import get_firebase_client
        data_store = get_firebase_client()
    _player_service = PlayerService(data_store=data_store)
    return _player_service


def reset_player_service():
    """Reset the global player service (useful for testing)."""
    global _player_service
    _player_service = None 