#!/usr/bin/env python3
"""
Firebase Player Repository Implementation

This module provides the Firebase implementation of the player repository interface.
"""

import logging
from datetime import datetime

from kickai.core.firestore_constants import COLLECTION_PLAYERS
from kickai.core.interfaces.player_repositories import (
    IPlayerRepository,
)
from kickai.core.value_objects import PhoneNumber, PlayerId, TeamId, TelegramId
from kickai.database.interfaces import DataStoreInterface
from kickai.features.player_registration.domain.entities.player import Player
from typing import Any

logger = logging.getLogger(__name__)


class FirebasePlayerRepository(IPlayerRepository):
    """Firebase implementation of the player repository."""

    def __init__(self, database: DataStoreInterface):
        self.database = database
        # Use team-specific collection naming - will be set per operation
        self.collection_name = COLLECTION_PLAYERS

    # IPlayerReadRepository methods

    async def get_by_phone(
        self,
        phone: PhoneNumber,
        team_id: TeamId
    ) -> dict[str, Any] | None:
        """Get player by phone number and team."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "phone_number", "operator": "==", "value": str(phone)},
                    {"field": "team_id", "operator": "==", "value": team_id},
                ],
            )

            if docs:
                return docs[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get player by phone {phone} for team {team_id}: {e}")
            return None

    async def get_by_telegram_id(
        self,
        user_id: TelegramId,
        team_id: TeamId
    ) -> dict[str, Any] | None:
        """Get player by telegram ID and team."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "telegram_id", "operator": "==", "value": int(user_id)},
                    {"field": "team_id", "operator": "==", "value": team_id},
                ],
            )

            if docs:
                return docs[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get player by user_id {user_id} for team {team_id}: {e}")
            return None

    async def get_active_players(
        self,
        team_id: TeamId
    ) -> list[dict[str, Any]]:
        """Get all active players for a team."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "status", "operator": "==", "value": "active"},
                ],
            )

            return docs
        except Exception as e:
            logger.error(f"Failed to get active players for team {team_id}: {e}")
            return []

    # IPlayerWriteRepository methods

    async def create_player(
        self,
        player_data: dict[str, Any],
        team_id: TeamId
    ) -> dict[str, Any]:
        """Create new player."""
        # Ensure team_id is set in player_data
        player_data = player_data.copy()
        player_data["team_id"] = team_id
        
        # Generate consistent document ID
        document_id = self._generate_document_id_from_data(player_data)

        # Use team-specific collection naming
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(team_id)

        try:
            await self.database.create_document(
                collection=collection_name, document_id=document_id, data=player_data
            )
            logger.info(f"Successfully created player {document_id} in team {team_id}")
        except Exception as e:
            logger.error(f"Failed to create player {document_id} in team {team_id}: {e}")
            raise

        return player_data

    async def update_player(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update player information."""
        # Use team-specific collection naming
        from kickai.core.firestore_constants import get_team_players_collection

        collection_name = get_team_players_collection(team_id)

        try:
            await self.database.update_document(
                collection=collection_name, document_id=player_id, data=updates
            )
            logger.info(f"Successfully updated player {player_id} in team {team_id}")
            
            # Return the updated player
            doc = await self.database.get_document(
                collection=collection_name, document_id=player_id
            )
            return doc
        except Exception as e:
            logger.error(f"Failed to update player {player_id} in team {team_id}: {e}")
            return None

    async def set_player_status(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        status: str
    ) -> bool:
        """Set player status."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            await self.database.update_document(
                collection=collection_name, 
                document_id=player_id, 
                data={"status": status, "updated_at": datetime.now().isoformat()}
            )
            logger.info(f"Successfully set status {status} for player {player_id} in team {team_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set status for player {player_id} in team {team_id}: {e}")
            return False

    # IPlayerApprovalRepository methods

    async def get_pending_approvals(
        self,
        team_id: TeamId
    ) -> list[dict[str, Any]]:
        """Get players pending approval."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "status", "operator": "==", "value": "pending_approval"},
                ],
            )

            return docs
        except Exception as e:
            logger.error(f"Failed to get pending approvals for team {team_id}: {e}")
            return []

    async def approve_player(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        approved_by: TelegramId
    ) -> bool:
        """Approve player registration."""
        try:
            # Use team-specific collection naming
            from kickai.core.firestore_constants import get_team_players_collection

            collection_name = get_team_players_collection(team_id)

            update_data = {
                "status": "active",
                "approved_by": int(approved_by),
                "approved_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            await self.database.update_document(
                collection=collection_name, 
                document_id=player_id, 
                data=update_data
            )
            logger.info(f"Successfully approved player {player_id} in team {team_id} by {approved_by}")
            return True
        except Exception as e:
            logger.error(f"Failed to approve player {player_id} in team {team_id}: {e}")
            return False

    # IRepository methods

    async def get_by_id(self, entity_id: str) -> dict[str, Any] | None:
        """Get entity by ID."""
        # For backward compatibility, we need team context
        # This method is part of the generic IRepository interface
        # We'll implement it but it's less useful without team context
        logger.warning("get_by_id called without team context - this may not work as expected")
        return None

    async def save(self, entity: Any) -> Any:
        """Save entity and return updated version."""
        # This is a generic interface method - for Player entities we use specific methods
        if isinstance(entity, Player):
            return await self.update_player_legacy(entity)
        elif isinstance(entity, dict):
            # If it's dict data, try to save it
            team_id = entity.get("team_id")
            player_id = entity.get("player_id")
            if team_id and player_id:
                result = await self.update_player(player_id, team_id, entity)
                return result
            else:
                logger.error("Cannot save entity without team_id and player_id")
                return entity
        return entity

    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        # For backward compatibility, we need team context
        logger.warning("delete called without team context - this may not work as expected")
        return False

    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists."""
        # For backward compatibility, we need team context
        logger.warning("exists called without team context - this may not work as expected")
        return False

    # Legacy methods for backward compatibility

    async def create_player_legacy(self, player: Player) -> Player:
        """Create a new player (legacy method)."""
        # Generate consistent document ID
        document_id = self._generate_document_id(player)

        player_data = {
            "team_id": player.team_id,
            "telegram_id": player.telegram_id,
            "player_id": player.player_id,
            "name": player.name,
            "username": player.username,
            "position": player.position,
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
        elif player.phone_number:
            # Clean phone number for use as document ID
            phone_clean = player.phone_number.replace("+", "").replace(" ", "").replace("-", "")
            return f"player_{phone_clean}"
        else:
            raise ValueError("Player must have either player_id or phone_number")
    
    def _generate_document_id_from_data(self, player_data: dict[str, Any]) -> str:
        """Generate consistent document ID for player from data dict."""
        if player_data.get("player_id"):
            return player_data["player_id"]
        elif player_data.get("phone_number"):
            # Clean phone number for use as document ID
            phone_clean = player_data["phone_number"].replace("+", "").replace(" ", "").replace("-", "")
            return f"player_{phone_clean}"
        else:
            raise ValueError("Player must have either player_id or phone_number")

    async def get_player_by_id(self, player_id: str, team_id: str) -> Player | None:
        """Get a player by ID (legacy method)."""
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
        """Get a player by phone number (legacy method)."""
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
        """Get all players in a team (legacy method)."""
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

    async def update_player_legacy(self, player: Player) -> Player:
        """Update a player (legacy method)."""
        # Generate consistent document ID
        document_id = self._generate_document_id(player)

        player_data = {
            "team_id": player.team_id,
            "telegram_id": player.telegram_id,
            "player_id": player.player_id,
            "name": player.name,
            "username": player.username,
            "position": player.position,
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
        """Delete a player (legacy method)."""
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
        """Get players by status (legacy method)."""
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
        return Player.from_database_dict(doc)

    def _parse_datetime(self, dt_str: str | None) -> datetime | None:
        """Parse datetime string to datetime object."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except ValueError:
            return None