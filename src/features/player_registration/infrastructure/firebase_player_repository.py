#!/usr/bin/env python3
"""
Firebase Player Repository Implementation

This module provides the Firebase implementation of the player repository interface.
"""

from typing import List, Optional
from datetime import datetime

from features.player_registration.domain.repositories.player_repository_interface import (
    PlayerRepositoryInterface,
    Player
)
from database.interfaces import DataStoreInterface
from core.constants import COLLECTION_PLAYERS


class FirebasePlayerRepository(PlayerRepositoryInterface):
    """Firebase implementation of the player repository."""
    
    def __init__(self, database: DataStoreInterface):
        self.database = database
        self.collection_name = COLLECTION_PLAYERS
    
    async def create_player(self, player: Player) -> Player:
        """Create a new player."""
        player_data = {
            "id": player.id,
            "name": player.name,
            "phone": player.phone,
            "position": player.position,
            "team_id": player.team_id,
            "status": player.status,
            "created_at": player.created_at.isoformat() if player.created_at else None,
            "updated_at": player.updated_at.isoformat() if player.updated_at else None
        }
        
        await self.database.create_document(
            collection=self.collection_name,
            document_id=player.id,
            data=player_data
        )
        
        return player
    
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        """Get a player by ID."""
        try:
            doc = await self.database.get_document(
                collection=self.collection_name,
                document_id=player_id
            )
            
            if doc and doc.get("team_id") == team_id:
                return self._doc_to_player(doc)
            return None
        except Exception:
            return None
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number."""
        try:
            docs = await self.database.query_documents(
                collection=self.collection_name,
                filters=[
                    {"field": "phone", "operator": "==", "value": phone},
                    {"field": "team_id", "operator": "==", "value": team_id}
                ]
            )
            
            if docs:
                return self._doc_to_player(docs[0])
            return None
        except Exception:
            return None
    
    async def get_all_players(self, team_id: str) -> List[Player]:
        """Get all players in a team."""
        try:
            docs = await self.database.query_documents(
                collection=self.collection_name,
                filters=[{"field": "team_id", "operator": "==", "value": team_id}]
            )
            
            return [self._doc_to_player(doc) for doc in docs]
        except Exception:
            return []
    
    async def update_player(self, player: Player) -> Player:
        """Update a player."""
        player_data = {
            "id": player.id,
            "name": player.name,
            "phone": player.phone,
            "position": player.position,
            "team_id": player.team_id,
            "status": player.status,
            "created_at": player.created_at.isoformat() if player.created_at else None,
            "updated_at": player.updated_at.isoformat() if player.updated_at else None
        }
        
        await self.database.update_document(
            collection=self.collection_name,
            document_id=player.id,
            data=player_data
        )
        
        return player
    
    async def delete_player(self, player_id: str, team_id: str) -> bool:
        """Delete a player."""
        try:
            # Verify the player exists and belongs to the team
            player = await self.get_player_by_id(player_id, team_id)
            if not player:
                return False
            
            await self.database.delete_document(
                collection=self.collection_name,
                document_id=player_id
            )
            
            return True
        except Exception:
            return False
    
    async def get_players_by_status(self, team_id: str, status: str) -> List[Player]:
        """Get players by status."""
        try:
            docs = await self.database.query_documents(
                collection=self.collection_name,
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "status", "operator": "==", "value": status}
                ]
            )
            
            return [self._doc_to_player(doc) for doc in docs]
        except Exception:
            return []
    
    def _doc_to_player(self, doc: dict) -> Player:
        """Convert a Firestore document to a Player entity."""
        return Player(
            id=doc.get("id"),
            name=doc.get("name"),
            phone=doc.get("phone"),
            position=doc.get("position"),
            team_id=doc.get("team_id"),
            status=doc.get("status", "pending"),
            created_at=self._parse_datetime(doc.get("created_at")),
            updated_at=self._parse_datetime(doc.get("updated_at"))
        )
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            return None 