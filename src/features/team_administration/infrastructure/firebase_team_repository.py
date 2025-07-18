#!/usr/bin/env python3
"""
Firebase Team Repository Implementation

This module provides the Firebase implementation of the team repository interface.
"""

from typing import List, Optional
from datetime import datetime

from features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
from features.team_administration.domain.entities.team import Team
from database.interfaces import DataStoreInterface
from core.constants import COLLECTION_TEAMS


class FirebaseTeamRepository(TeamRepositoryInterface):
    """Firebase implementation of the team repository."""
    
    def __init__(self, database: DataStoreInterface):
        self.database = database
        self.collection_name = COLLECTION_TEAMS
    
    async def create_team(self, team: Team) -> Team:
        """Create a new team."""
        team_data = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "status": team.status.value if hasattr(team.status, 'value') else team.status,
            "created_by": team.created_by,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "settings": team.settings,
            "fa_team_url": team.fa_team_url,
            "fa_fixtures_url": team.fa_fixtures_url,
            "bot_id": team.bot_id,
            "bot_token": team.bot_token,
            "main_chat_id": team.main_chat_id,
            "leadership_chat_id": team.leadership_chat_id
        }
        
        # Create document and get the generated ID
        # Only pass document_id if team.id is not None
        doc_id = await self.database.create_document(
            collection=self.collection_name,
            document_id=team.id if team.id else None,
            data=team_data
        )
        
        # Update the team entity with the generated ID
        team.id = doc_id
        
        return team
    
    async def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        try:
            doc = await self.database.get_document(
                collection=self.collection_name,
                document_id=team_id
            )
            
            if doc:
                return self._doc_to_team(doc)
            return None
        except Exception:
            return None
    
    async def get_all_teams(self) -> List[Team]:
        """Get all teams."""
        try:
            docs = await self.database.query_documents(
                collection=self.collection_name
            )
            
            return [self._doc_to_team(doc) for doc in docs]
        except Exception:
            return []
    
    async def update_team(self, team: Team) -> Team:
        """Update a team."""
        team_data = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "status": team.status.value if hasattr(team.status, 'value') else team.status,
            "created_by": team.created_by,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "settings": team.settings,
            "fa_team_url": team.fa_team_url,
            "fa_fixtures_url": team.fa_fixtures_url,
            "bot_id": team.bot_id,
            "bot_token": team.bot_token,
            "main_chat_id": team.main_chat_id,
            "leadership_chat_id": team.leadership_chat_id
        }
        
        await self.database.update_document(
            collection=self.collection_name,
            document_id=team.id,
            data=team_data
        )
        
        return team
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        try:
            await self.database.delete_document(
                collection=self.collection_name,
                document_id=team_id
            )
            
            return True
        except Exception:
            return False
    
    async def list_all(self, limit: int = 100) -> List[Team]:
        """List all teams with optional limit."""
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔍 [REPO] list_all called with limit={limit}")
            logger.info(f"🔍 [REPO] Using collection: {self.collection_name}")
            logger.info(f"🔍 [REPO] Database type: {type(self.database)}")
            
            docs = await self.database.query_documents(
                collection=self.collection_name,
                limit=limit
            )
            
            logger.info(f"🔍 [REPO] Got {len(docs)} documents from database")
            
            teams = [self._doc_to_team(doc) for doc in docs]
            logger.info(f"🔍 [REPO] Converted to {len(teams)} teams")
            
            return teams
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ [REPO] Error in list_all: {e}")
            import traceback
            logger.error(f"❌ [REPO] Traceback: {traceback.format_exc()}")
            return []
    
    def _doc_to_team(self, doc: dict) -> Team:
        """Convert a Firestore document to a Team entity."""
        from features.team_administration.domain.entities.team import TeamStatus
        
        # Convert status string back to enum if needed
        status = doc.get("status")
        if isinstance(status, str):
            try:
                status = TeamStatus(status)
            except ValueError:
                status = TeamStatus.ACTIVE  # Default fallback
        
        return Team(
            id=doc.get("id"),
            name=doc.get("name"),
            description=doc.get("description"),
            status=status,
            created_by=doc.get("created_by", "system"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            settings=doc.get("settings", {}),
            fa_team_url=doc.get("fa_team_url"),
            fa_fixtures_url=doc.get("fa_fixtures_url"),
            bot_id=doc.get("bot_id"),
            bot_token=doc.get("bot_token"),
            main_chat_id=doc.get("main_chat_id"),
            leadership_chat_id=doc.get("leadership_chat_id")
        ) 