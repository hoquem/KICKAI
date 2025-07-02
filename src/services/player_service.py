"""
Player Service for KICKAI

This module provides business logic for player management including
registration, validation, and team operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import re
from uuid import uuid4

from ..core.exceptions import (
    PlayerError, PlayerNotFoundError, PlayerValidationError, 
    PlayerDuplicateError, create_error_context
)
from ..core.logging import get_logger, performance_timer
from ..database.firebase_client import get_firebase_client
from ..database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus


class PlayerService:
    """Service for player management operations."""
    
    def __init__(self):
        self._firebase_client = get_firebase_client()
        self._logger = get_logger("player_service")
    
    @performance_timer("player_service_create_player")
    async def create_player(self, name: str, phone: str, team_id: str, 
                          email: Optional[str] = None, position: PlayerPosition = PlayerPosition.UTILITY,
                          role: PlayerRole = PlayerRole.PLAYER, fa_registered: bool = False) -> Player:
        """Create a new player with validation."""
        try:
            # Validate input data
            self._validate_player_data(name, phone, email, team_id)
            
            # Check for duplicate phone number in the same team
            existing_player = await self._firebase_client.get_player_by_phone(phone, team_id)
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
            player_id = await self._firebase_client.create_player(player)
            player.id = player_id
            
            self._logger.info(
                f"Player created successfully: {player.name} ({player_id})",
                operation="create_player",
                entity_id=player_id,
                team_id=team_id
            )
            
            return player
            
        except (PlayerError, PlayerDuplicateError):
            raise
        except Exception as e:
            self._logger.error("Failed to create player", error=e, team_id=team_id)
            raise PlayerError(
                f"Failed to create player: {str(e)}",
                create_error_context("create_player", team_id=team_id)
            )
    
    @performance_timer("player_service_get_player")
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        try:
            player = await self._firebase_client.get_player(player_id)
            if player:
                self._logger.info(
                    f"Player retrieved: {player.name}",
                    operation="get_player",
                    entity_id=player_id
                )
            return player
            
        except Exception as e:
            self._logger.error("Failed to get player", error=e, entity_id=player_id)
            raise PlayerError(
                f"Failed to get player: {str(e)}",
                create_error_context("get_player", entity_id=player_id)
            )
    
    @performance_timer("player_service_update_player")
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
                    existing_player = await self._firebase_client.get_player_by_phone(
                        updates['phone'], player.team_id
                    )
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
            success = await self._firebase_client.update_player(player)
            if not success:
                raise PlayerError(
                    "Failed to update player in database",
                    create_error_context("update_player", entity_id=player_id)
                )
            
            self._logger.info(
                f"Player updated: {player.name}",
                operation="update_player",
                entity_id=player_id,
                team_id=player.team_id
            )
            
            return player
            
        except (PlayerError, PlayerNotFoundError, PlayerDuplicateError):
            raise
        except Exception as e:
            self._logger.error("Failed to update player", error=e, entity_id=player_id)
            raise PlayerError(
                f"Failed to update player: {str(e)}",
                create_error_context("update_player", entity_id=player_id)
            )
    
    @performance_timer("player_service_delete_player")
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
            success = await self._firebase_client.delete_player(player_id)
            if not success:
                raise PlayerError(
                    "Failed to delete player from database",
                    create_error_context("delete_player", entity_id=player_id)
                )
            
            self._logger.info(
                f"Player deleted: {player.name}",
                operation="delete_player",
                entity_id=player_id,
                team_id=player.team_id
            )
            
            return True
            
        except (PlayerError, PlayerNotFoundError):
            raise
        except Exception as e:
            self._logger.error("Failed to delete player", error=e, entity_id=player_id)
            raise PlayerError(
                f"Failed to delete player: {str(e)}",
                create_error_context("delete_player", entity_id=player_id)
            )
    
    @performance_timer("player_service_get_team_players")
    async def get_team_players(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        try:
            players = await self._firebase_client.get_players_by_team(team_id)
            
            self._logger.info(
                f"Retrieved {len(players)} players for team {team_id}",
                operation="get_team_players",
                team_id=team_id
            )
            
            return players
            
        except Exception as e:
            self._logger.error("Failed to get team players", error=e, team_id=team_id)
            raise PlayerError(
                f"Failed to get team players: {str(e)}",
                create_error_context("get_team_players", team_id=team_id)
            )
    
    @performance_timer("player_service_get_player_by_phone")
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number and team."""
        try:
            player = await self._firebase_client.get_player_by_phone(phone, team_id)
            return player
            
        except Exception as e:
            self._logger.error("Failed to get player by phone", error=e, team_id=team_id)
            raise PlayerError(
                f"Failed to get player by phone: {str(e)}",
                create_error_context("get_player_by_phone", team_id=team_id, additional_info={'phone': phone})
            )
    
    @performance_timer("player_service_update_onboarding_status")
    async def update_onboarding_status(self, player_id: str, status: OnboardingStatus) -> Player:
        """Update player onboarding status."""
        return await self.update_player(player_id, onboarding_status=status)
    
    @performance_timer("player_service_generate_invite_link")
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
        
        # UK phone number validation
        phone_pattern = r'^(\+44|0)[1-9]\d{8,9}$'
        if not re.match(phone_pattern, phone.replace(' ', '')):
            raise PlayerValidationError(
                "Invalid phone number format. Must be a valid UK phone number",
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
    
    def generate_player_id(self, name: str) -> str:
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
            players = self._firebase_client.get_all_players(self.team_id)
            existing_ids = {player.player_id for player in players if player.player_id}
        except Exception as e:
            logger.warning(f"Could not load existing player IDs for collision detection: {e}")
        
        return generate_human_readable_id(first_name, last_name, existing_ids)


# Global player service instance
_player_service: Optional[PlayerService] = None


def get_player_service() -> PlayerService:
    """Get the global player service instance."""
    global _player_service
    if _player_service is None:
        _player_service = PlayerService()
    return _player_service


def initialize_player_service() -> PlayerService:
    """Initialize the global player service."""
    global _player_service
    _player_service = PlayerService()
    return _player_service 