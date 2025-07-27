#!/usr/bin/env python3
"""
Firebase Player Repository Implementation

This module provides the Firebase implementation of the player repository interface.
"""

import logging
from datetime import datetime

from kickai.core.firestore_constants import COLLECTION_PLAYERS
from kickai.database.interfaces import DataStoreInterface
from kickai.features.player_registration.domain.entities.player import Player
from kickai.features.player_registration.domain.repositories.player_repository_interface import (
    PlayerRepositoryInterface,
)

logger = logging.getLogger(__name__)


class FirebasePlayerRepository(PlayerRepositoryInterface):
    """Firebase implementation of the player repository."""

    def __init__(self, database: DataStoreInterface):
        self.database = database
        # Use team-specific collection naming - will be set per operation
        self.collection_name = COLLECTION_PLAYERS

    async def create_player(self, player: Player) -> Player:
        """Create a new player."""
        # Generate consistent document ID
        document_id = self._generate_document_id(player)

        player_data = {
            "user_id": player.user_id,
            "team_id": player.team_id,
            "telegram_id": player.telegram_id,
            "player_id": player.player_id,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "username": player.username,
            "position": player.position,
            "preferred_foot": player.preferred_foot,
            "jersey_number": player.jersey_number,
            "phone_number": player.phone_number,
            "email": player.email,
            "date_of_birth": player.date_of_birth,
            "emergency_contact": player.emergency_contact,
            "medical_notes": player.medical_notes,
            "status": player.status,
            "created_at": player.created_at.isoformat() if player.created_at else None,
            "updated_at": player.updated_at.isoformat() if player.updated_at else None,
            "source": player.source,
            "sync_version": player.sync_version,
        }

        # Use team-specific collection naming
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(player.team_id)

        try:
            await self.database.create_document(
                collection=collection_name, document_id=document_id, data=player_data
            )
            logger.info(f"Successfully created player {document_id} in team {player.team_id}")
        except Exception as e:
            logger.error(f"Failed to create player {document_id} in team {player.team_id}: {e}")
            raise

        return player

    def _generate_document_id(self, player: Player) -> str:
        """Generate consistent document ID for player."""
        if player.player_id:
            return player.player_id  # Use the generated player ID as document ID
        elif player.user_id:
            return player.user_id
        elif player.phone_number:
            # Clean phone number for use as document ID
            phone_clean = player.phone_number.replace("+", "").replace(" ", "").replace("-", "")
            return f"player_{phone_clean}"
        else:
            raise ValueError("Player must have either player_id, user_id, or phone_number")

    async def get_player_by_id(self, player_id: str, team_id: str) -> Player | None:
        """Get a player by ID."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            doc = await self.database.get_document(
                collection=collection_name, document_id=player_id
            )

            if doc and doc.get("team_id") == team_id:
                return self._doc_to_player(doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get player by ID {player_id} for team {team_id}: {e}")
            return None

    async def get_player_by_phone(self, phone: str, team_id: str) -> Player | None:
        """Get a player by phone number."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

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
            logger.error(f"Failed to get player by phone {phone} for team {team_id}: {e}")
            return None

    async def get_all_players(self, team_id: str) -> list[Player]:
        """Get all players in a team."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[{"field": "team_id", "operator": "==", "value": team_id}],
            )

            return [self._doc_to_player(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get all players for team {team_id}: {e}")
            return []

    async def update_player(self, player: Player) -> Player:
        """Update a player."""
        # Generate consistent document ID
        document_id = self._generate_document_id(player)

        player_data = {
            "user_id": player.user_id,
            "team_id": player.team_id,
            "telegram_id": player.telegram_id,
            "player_id": player.player_id,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "username": player.username,
            "position": player.position,
            "preferred_foot": player.preferred_foot,
            "jersey_number": player.jersey_number,
            "phone_number": player.phone_number,
            "email": player.email,
            "date_of_birth": player.date_of_birth,
            "emergency_contact": player.emergency_contact,
            "medical_notes": player.medical_notes,
            "status": player.status,
            "created_at": player.created_at.isoformat() if player.created_at else None,
            "updated_at": player.updated_at.isoformat() if player.updated_at else None,
            "source": player.source,
            "sync_version": player.sync_version,
        }

        # Use team-specific collection naming
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(player.team_id)

        try:
            await self.database.update_document(
                collection=collection_name, document_id=document_id, data=player_data
            )
            logger.info(f"Successfully updated player {document_id} in team {player.team_id}")
        except Exception as e:
            logger.error(f"Failed to update player {document_id} in team {player.team_id}: {e}")
            raise

        return player

    async def delete_player(self, player_id: str, team_id: str) -> bool:
        """Delete a player."""
        try:
            # Verify the player exists and belongs to the team
            player = await self.get_player_by_id(player_id, team_id)
            if not player:
                logger.warning(f"Player {player_id} not found in team {team_id} for deletion")
                return False

            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            await self.database.delete_document(collection=collection_name, document_id=player_id)

            logger.info(f"Successfully deleted player {player_id} from team {team_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete player {player_id} from team {team_id}: {e}")
            return False

    async def get_players_by_status(self, team_id: str, status: str) -> list[Player]:
        """Get players by status."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

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
            logger.error(f"Failed to get players by status {status} for team {team_id}: {e}")
            return []

    def _doc_to_player(self, doc: dict) -> Player:
        """Convert a Firestore document to a Player entity."""
        return Player(
            user_id=doc.get("user_id", ""),
            team_id=doc.get("team_id", ""),
            telegram_id=doc.get("telegram_id"),
            player_id=doc.get("player_id"),
            first_name=doc.get("first_name"),
            last_name=doc.get("last_name"),
            full_name=doc.get("full_name"),
            username=doc.get("username"),
            position=doc.get("position"),
            preferred_foot=doc.get("preferred_foot"),
            jersey_number=doc.get("jersey_number"),
            phone_number=doc.get("phone_number"),
            email=doc.get("email"),
            date_of_birth=doc.get("date_of_birth"),
            emergency_contact=doc.get("emergency_contact"),
            medical_notes=doc.get("medical_notes"),
            status=doc.get("status", "pending"),
            created_at=self._parse_datetime(doc.get("created_at")),
            updated_at=self._parse_datetime(doc.get("updated_at")),
            source=doc.get("source"),
            sync_version=doc.get("sync_version"),
        )

    def _parse_datetime(self, dt_str: str | None) -> datetime | None:
        """Parse datetime string to datetime object."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except ValueError:
            return None
