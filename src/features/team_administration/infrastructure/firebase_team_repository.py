#!/usr/bin/env python3
"""
Firebase Team Repository Implementation

This module provides the Firebase implementation of the team repository interface.
"""

from typing import List, Optional
from datetime import datetime

from features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
from features.team_administration.domain.entities.team import Team
from features.team_administration.domain.entities.team_member import TeamMember
from database.interfaces import DataStoreInterface
from core.constants import COLLECTION_TEAMS, get_team_members_collection, get_team_players_collection


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
    
    # Team Member Methods
    async def create_team_member(self, team_member: TeamMember) -> TeamMember:
        """Create a new team member."""
        # Generate a unique ID for the team member
        from utils.id_generator import generate_team_member_id
        if not team_member.id:
            team_member.id = generate_team_member_id(team_member.name)
        
        # Set user_id and id to the same value (document ID)
        team_member.user_id = team_member.id
        
        team_member_data = team_member.to_dict()
        
        # Create document in team_members collection
        doc_id = await self.database.create_document(
            collection=get_team_members_collection(team_member.team_id),
            document_id=team_member.id,
            data=team_member_data
        )
        
        # Update the team member entity with the generated ID
        team_member.id = doc_id
        team_member.user_id = doc_id
        
        return team_member
    
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        try:
            docs = await self.database.query_documents(
                collection=get_team_members_collection(team_id),
                filters=[{"field": "team_id", "operator": "==", "value": team_id}]
            )
            
            return [self._doc_to_team_member(doc) for doc in docs]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ [REPO] Error getting team members: {e}")
            return []
    
    async def get_team_member_by_telegram_id(self, team_id: str, telegram_id: str) -> Optional[TeamMember]:
        """Get a team member by Telegram ID."""
        try:
            docs = await self.database.query_documents(
                collection=get_team_members_collection(team_id),
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "telegram_id", "operator": "==", "value": telegram_id}
                ]
            )
            
            if docs:
                return self._doc_to_team_member(docs[0])
            return None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ [REPO] Error getting team member by telegram_id: {e}")
            return None
    
    async def update_team_member(self, team_member: TeamMember) -> TeamMember:
        """Update a team member."""
        team_member_data = team_member.to_dict()
        
        await self.database.update_document(
            collection=get_team_members_collection(team_member.team_id),
            document_id=team_member.id,
            data=team_member_data
        )
        
        return team_member
    
    async def delete_team_member(self, team_member_id: str) -> bool:
        """Delete a team member."""
        try:
            await self.database.delete_document(
                collection=get_team_members_collection(team_member_id.split("_")[0]),
                document_id=team_member_id
            )
            
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ [REPO] Error deleting team member: {e}")
            return False
    
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
    
    def _doc_to_team_member(self, doc: dict) -> TeamMember:
        """Convert a Firestore document to a TeamMember entity."""
        from datetime import datetime
        
        # Parse datetime strings back to datetime objects
        created_at = doc.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        joined_at = doc.get("joined_at")
        if isinstance(joined_at, str):
            joined_at = datetime.fromisoformat(joined_at)
        
        return TeamMember(
            id=doc.get("id"),
            user_id=doc.get("user_id", ""),
            telegram_id=doc.get("telegram_id"),
            telegram_username=doc.get("telegram_username"),
            team_id=doc.get("team_id", ""),
            roles=doc.get("roles", []),
            permissions=doc.get("permissions", []),
            chat_access=doc.get("chat_access", {}),
            created_at=created_at,
            joined_at=joined_at
        ) 