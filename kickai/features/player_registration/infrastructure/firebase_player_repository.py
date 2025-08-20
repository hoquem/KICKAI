#!/usr/bin/env python3
"""
Firebase Player Repository Implementation

This module provides the Firebase implementation of the player repository interface.
"""

# Standard library
import logging

# Local application
from kickai.core.firestore_constants import COLLECTION_PLAYERS, get_team_players_collection
from kickai.database.interfaces import DataStoreInterface
from kickai.features.player_registration.domain.entities.player import Player
from kickai.features.player_registration.domain.repositories.player_repository_interface import (
    PlayerRepositoryInterface,
)

# Constants
ERROR_MESSAGES = {
    "CREATE_PLAYER_FAILED": "Failed to create player {} in team {}: {}",
    "GET_PLAYER_BY_ID_FAILED": "Failed to get player by ID {} for team {}: {}",
    "GET_PLAYER_BY_PHONE_FAILED": "Failed to get player by phone {} for team {}: {}",
    "GET_ALL_PLAYERS_FAILED": "Failed to get all players for team {}: {}",
    "UPDATE_PLAYER_FAILED": "Failed to update player {} in team {}: {}",
    "DELETE_PLAYER_FAILED": "Failed to delete player {} from team {}: {}",
    "GET_PLAYERS_BY_STATUS_FAILED": "Failed to get players by status {} for team {}: {}",
    "PLAYER_NOT_FOUND_DELETION": "Player {} not found in team {} for deletion",
    "PLAYER_MISSING_ID": "Player must have player_id",
}

SUCCESS_MESSAGES = {
    "PLAYER_CREATED": "Successfully created player {} in team {}",
    "PLAYER_UPDATED": "Successfully updated player {} in team {}",
    "PLAYER_DELETED": "Successfully deleted player {} from team {}",
}

logger = logging.getLogger(__name__)


class FirebasePlayerRepository(PlayerRepositoryInterface):
    """Firebase implementation of the player repository."""

    def __init__(self, database: DataStoreInterface):
        self.database = database
        # Use team-specific collection naming - will be set per operation
        self.collection_name = COLLECTION_PLAYERS

    async def create_player(self, player: Player) -> Player:
        """Create a new player."""
        try:
            # Generate consistent document ID
            document_id = self._generate_document_id(player)

            # Prepare player data
            player_data = self._prepare_player_data(player)

            # Use team-specific collection naming
            collection_name = get_team_players_collection(player.team_id)

            await self.database.create_document(
                collection=collection_name, document_id=document_id, data=player_data
            )
            logger.info(SUCCESS_MESSAGES["PLAYER_CREATED"].format(document_id, player.team_id))
            return player

        except Exception as e:
            logger.error(
                ERROR_MESSAGES["CREATE_PLAYER_FAILED"].format(document_id, player.team_id, e)
            )
            raise

    def _generate_document_id(self, player: Player) -> str:
        """
        Generate consistent document ID for player.
        
        Priority order:
        1. player_id (preferred - always use when available)
        2. phone_number (fallback only)
        
        This ensures consistent document IDs across all operations.
        """
        # Always prefer player_id when available
        if player.player_id and player.player_id.strip():
            return player.player_id.strip()
        
        raise ValueError(ERROR_MESSAGES["PLAYER_MISSING_ID"])

    def _prepare_player_data(self, player: Player) -> dict:
        """Prepare player data for database operations."""
        return {
            "team_id": player.team_id,
            "telegram_id": player.telegram_id,
            "player_id": player.player_id,
            "name": player.name,
            "username": player.username,
            "position": player.position,
            "phone_number": player.phone_number,
            "email": player.email,
            "date_of_birth": player.date_of_birth,
            "emergency_contact_name": player.emergency_contact_name,
            "emergency_contact_phone": player.emergency_contact_phone,
            "status": player.status,
            "created_at": player.created_at.isoformat() if player.created_at else None,
            "updated_at": player.updated_at.isoformat() if player.updated_at else None,
            "source": player.source,
            "sync_version": player.sync_version,
        }

    def _prepare_update_player_data(self, player: Player) -> dict:
        """Prepare player data for update operations."""
        base_data = self._prepare_player_data(player)
        # Add fields specific to updates
        base_data.update(
            {
                "preferred_foot": player.preferred_foot,
                "jersey_number": player.jersey_number,
                "medical_notes": player.medical_notes,
            }
        )
        return base_data

    async def get_player_by_id(self, player_id: str, team_id: str) -> Player | None:
        """Get a player by ID."""
        try:
            # Use team-specific collection naming
            collection_name = get_team_players_collection(team_id)

            doc = await self.database.get_document(
                collection=collection_name, document_id=player_id
            )

            if doc and doc.get("team_id") == team_id:
                return self._doc_to_player(doc)
            return None

        except Exception as e:
            logger.error(ERROR_MESSAGES["GET_PLAYER_BY_ID_FAILED"].format(player_id, team_id, e))
            return None

    async def get_player_by_phone(self, phone: str, team_id: str) -> Player | None:
        """Get a player by phone number."""
        try:
            # Use team-specific collection naming
            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "phone_number", "operator": "==", "value": phone},
                    {"field": "team_id", "operator": "==", "value": team_id},
                ],
            )

            if docs:
                return self._doc_to_player(docs[0])
            return None

        except Exception as e:
            logger.error(ERROR_MESSAGES["GET_PLAYER_BY_PHONE_FAILED"].format(phone, team_id, e))
            return None

    async def get_all_players(self, team_id: str) -> list[Player]:
        """Get all players in a team."""
        try:
            # Use team-specific collection naming
            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[{"field": "team_id", "operator": "==", "value": team_id}],
            )

            return [self._doc_to_player(doc) for doc in docs]

        except Exception as e:
            logger.error(ERROR_MESSAGES["GET_ALL_PLAYERS_FAILED"].format(team_id, e))
            return []

    async def update_player(self, player: Player) -> Player:
        """Update a player."""
        try:
            # Generate consistent document ID
            document_id = self._generate_document_id(player)

            # Prepare player data for update
            player_data = self._prepare_update_player_data(player)

            # Use team-specific collection naming
            collection_name = get_team_players_collection(player.team_id)

            await self.database.update_document(
                collection=collection_name, document_id=document_id, data=player_data
            )
            logger.info(SUCCESS_MESSAGES["PLAYER_UPDATED"].format(document_id, player.team_id))
            return player

        except Exception as e:
            logger.error(
                ERROR_MESSAGES["UPDATE_PLAYER_FAILED"].format(document_id, player.team_id, e)
            )
            raise

    async def delete_player(self, player_id: str, team_id: str) -> bool:
        """Delete a player."""
        try:
            # Verify the player exists and belongs to the team
            player = await self.get_player_by_id(player_id, team_id)
            if not player:
                logger.warning(
                    ERROR_MESSAGES["PLAYER_NOT_FOUND_DELETION"].format(player_id, team_id)
                )
                return False

            # Use team-specific collection naming
            collection_name = get_team_players_collection(team_id)

            await self.database.delete_document(collection=collection_name, document_id=player_id)

            logger.info(SUCCESS_MESSAGES["PLAYER_DELETED"].format(player_id, team_id))
            return True

        except Exception as e:
            logger.error(ERROR_MESSAGES["DELETE_PLAYER_FAILED"].format(player_id, team_id, e))
            return False

    async def get_players_by_status(self, team_id: str, status: str) -> list[Player]:
        """Get players by status."""
        try:
            # Use team-specific collection naming
            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "status", "operator": "==", "value": status},
                ],
            )

            return [self._doc_to_player(doc) for doc in docs]

        except Exception as e:
            logger.error(ERROR_MESSAGES["GET_PLAYERS_BY_STATUS_FAILED"].format(status, team_id, e))
            return []

    def _doc_to_player(self, doc: dict) -> Player:
        """Convert a Firestore document to a Player entity."""
        return Player.from_database_dict(doc)
