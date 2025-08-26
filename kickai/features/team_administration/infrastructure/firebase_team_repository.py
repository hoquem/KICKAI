#!/usr/bin/env python3
"""
Firebase Team Repository Implementation

This module provides the Firebase implementation of the team repository interface.
"""

from datetime import datetime
from typing import List, Optional, Union

from loguru import logger

from kickai.core.firestore_constants import (
    COLLECTION_TEAMS,
    get_team_members_collection,
)
from kickai.database.interfaces import DataStoreInterface
from kickai.features.team_administration.domain.entities.team import Team
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.features.team_administration.domain.repositories.team_repository_interface import (
    TeamRepositoryInterface,
)


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
            "status": team.status.value if hasattr(team.status, "value") else team.status,
            "created_by": team.created_by,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "settings": team.settings,
            "fa_team_url": team.fa_team_url,
            "fa_fixtures_url": team.fa_fixtures_url,
            "bot_id": team.bot_id,
            "bot_token": team.bot_token,
            "main_chat_id": team.main_chat_id,
            "leadership_chat_id": team.leadership_chat_id,
        }

        # Create document and get the generated ID
        # Only pass document_id if team.id is not None
        doc_id = await self.database.create_document(
            collection=self.collection_name,
            document_id=team.id if team.id else None,
            data=team_data,
        )

        # Update the team entity with the generated ID
        team.id = doc_id

        return team

    # Alias methods required by tests/interfaces
    async def create(self, team: Team) -> Team:
        return await self.create_team(team)

    async def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        try:
            doc = await self.database.get_document(
                collection=self.collection_name, document_id=team_id
            )

            if doc:
                return self._doc_to_team(doc)
            return None
        except Exception:
            return None

    async def get_by_id(self, team_id: str) -> Optional[Team]:
        return await self.get_team_by_id(team_id)

    async def get_all_teams(self) -> List[Team]:
        """Get all teams."""
        try:
            docs = await self.database.query_documents(collection=self.collection_name)

            return [self._doc_to_team(doc) for doc in docs]
        except Exception:
            return []

    async def get_by_status(self, status: str) -> List[Team]:
        try:
            docs = await self.database.query_documents(
                collection=self.collection_name,
                filters=[{"field": "status", "operator": "==", "value": status}],
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
            "status": team.status.value if hasattr(team.status, "value") else team.status,
            "created_by": team.created_by,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "settings": team.settings,
            "fa_team_url": team.fa_team_url,
            "fa_fixtures_url": team.fa_fixtures_url,
            "bot_id": team.bot_id,
            "bot_token": team.bot_token,
            "main_chat_id": team.main_chat_id,
            "leadership_chat_id": team.leadership_chat_id,
        }

        await self.database.update_document(
            collection=self.collection_name, document_id=team.id, data=team_data
        )

        return team

    async def update(self, team: Team) -> Team:
        return await self.update_team(team)

    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        try:
            await self.database.delete_document(
                collection=self.collection_name, document_id=team_id
            )

            return True
        except Exception:
            return False

    async def list_all(self, limit: int = 100) -> List[Team]:
        """List all teams with optional limit."""
        try:
            logger.info(f"🔍 [REPO] list_all called with limit={limit}")
            logger.info(f"🔍 [REPO] Using collection: {self.collection_name}")
            logger.info(f"🔍 [REPO] Database type: {type(self.database)}")

            docs = await self.database.query_documents(collection=self.collection_name, limit=limit)

            logger.info(f"🔍 [REPO] Got {len(docs)} documents from database")

            teams = [self._doc_to_team(doc) for doc in docs]
            logger.info(f"🔍 [REPO] Converted to {len(teams)} teams")

            return teams
        except Exception as e:
            logger.error(f"❌ [REPO] Error in list_all: {e}")
            import traceback
            logger.error(f"❌ [REPO] Traceback: {traceback.format_exc()}")
            return []

    # Team Member Methods
    async def create_team_member(self, team_member: TeamMember) -> TeamMember:
        """Create a new team member."""
        # TeamMember entity uses telegram_id as the primary identifier
        # Generate member_id if not already set
        if not team_member.member_id:
            from kickai.utils.simple_id_generator import generate_simple_team_member_id
            existing_members = await self.get_team_members(team_member.team_id)
            existing_ids = {member.member_id for member in existing_members if member.member_id}
            team_member.member_id = generate_simple_team_member_id(team_member.name or f"User{team_member.telegram_id}", team_member.team_id, existing_ids)

        team_member_data = team_member.to_dict()

        # Create document in team_members collection using member_id as document ID
        doc_id = await self.database.create_document(
            collection=get_team_members_collection(team_member.team_id),
            document_id=team_member.member_id,
            data=team_member_data,
        )

        return team_member

    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        try:
            docs = await self.database.query_documents(
                collection=get_team_members_collection(team_id),
                filters=[{"field": "team_id", "operator": "==", "value": team_id}],
            )

            return [self._doc_to_team_member(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ [REPO] Error getting team members: {e}")
            return []

    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team (alias for get_team_members for compatibility)."""
        return await self.get_team_members(team_id)

    async def get_team_member_by_telegram_id(
        self, team_id: str, telegram_id: Union[str, int]
    ) -> Optional[TeamMember]:
        """Get a team member by Telegram ID."""
        try:
            # Normalize telegram_id to handle both string and integer inputs
            from kickai.utils.telegram_id_converter import normalize_telegram_id_for_query
            normalized_telegram_id = normalize_telegram_id_for_query(telegram_id)
            
            if normalized_telegram_id is None:
                logger.warning(f"❌ Invalid telegram_id format: {telegram_id}")
                return None
            
            docs = await self.database.query_documents(
                collection=get_team_members_collection(team_id),
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "telegram_id", "operator": "==", "value": normalized_telegram_id},
                ],
            )

            if docs:
                return self._doc_to_team_member(docs[0])
            return None
        except Exception as e:
            logger.error(f"❌ [REPO] Error getting team member by telegram_id: {e}")
            return None

    async def get_team_member_by_phone(
        self, phone: str, team_id: str
    ) -> Optional[TeamMember]:
        """Get a team member by phone number."""
        try:
            docs = await self.database.query_documents(
                collection=get_team_members_collection(team_id),
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "phone_number", "operator": "==", "value": phone},
                ],
            )

            if docs:
                return self._doc_to_team_member(docs[0])
            return None
        except Exception as e:
            logger.error(f"❌ [REPO] Error getting team member by phone: {e}")
            return None

    async def get_team_member_by_id(self, member_id: str, team_id: str = None) -> Optional[TeamMember]:
        """Get a team member by their member ID.
        
        Args:
            member_id: The member ID to search for
            team_id: Optional team ID to narrow the search. If not provided, searches all teams.
        """
        try:
            # If team_id is provided, search within that team's collection first
            if team_id:
                try:
                    doc = await self.database.get_document(
                        collection=get_team_members_collection(team_id),
                        document_id=member_id
                    )
                    if doc:
                        return self._doc_to_team_member(doc)
                except Exception:
                    pass  # Continue to broader search
            
            # If not found in specific team or no team_id provided, search all teams
            # Get list of all teams to search their member collections
            teams = await self.get_all_teams()
            
            for team in teams:
                try:
                    doc = await self.database.get_document(
                        collection=get_team_members_collection(team.id),
                        document_id=member_id
                    )
                    if doc:
                        return self._doc_to_team_member(doc)
                except Exception:
                    continue  # Try next team
            
            return None
            
        except Exception as e:
            logger.error(f"❌ [REPO] Error getting team member by ID {member_id}: {e}")
            return None

    async def get_team_members_by_status(
        self, team_id: str, status: str
    ) -> List[TeamMember]:
        """Get team members by status."""
        try:
            docs = await self.database.query_documents(
                collection=get_team_members_collection(team_id),
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "status", "operator": "==", "value": status},
                ],
            )

            return [self._doc_to_team_member(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ [REPO] Error getting team members by status: {e}")
            return []

    async def update_team_member(self, team_member: TeamMember) -> TeamMember:
        """Update a team member."""
        team_member_data = team_member.to_dict()

        await self.database.update_document(
            collection=get_team_members_collection(team_member.team_id),
            document_id=team_member.member_id,
            data=team_member_data,
        )

        return team_member

    async def delete_team_member(self, team_member_id: str) -> bool:
        """Delete a team member."""
        try:
            await self.database.delete_document(
                collection=get_team_members_collection(team_member_id.split("_")[0]),
                document_id=team_member_id,
            )

            return True
        except Exception as e:
            logger.error(f"❌ [REPO] Error deleting team member: {e}")
            return False

    def _doc_to_team(self, doc: dict) -> Team:
        """Convert a Firestore document to a Team entity."""
        from kickai.features.team_administration.domain.entities.team import TeamStatus

        # Convert status string back to enum if needed
        status = doc.get("status")
        if isinstance(status, str):
            try:
                status = TeamStatus(status)
            except ValueError:
                status = TeamStatus.ACTIVE  # Default fallback

        # Get settings
        settings = doc.get("settings", {})

        # Create team entity - bot configuration is now in explicit fields
        # Check settings fallback for backward compatibility
        main_chat_id = doc.get("main_chat_id") or settings.get("main_chat_id")
        leadership_chat_id = doc.get("leadership_chat_id") or settings.get("leadership_chat_id")
        
        team = Team(
            id=doc.get("id"),
            name=doc.get("name"),
            description=doc.get("description"),
            status=status,
            created_by=doc.get("created_by", "system"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            settings=settings,
            fa_team_url=doc.get("fa_team_url"),
            fa_fixtures_url=doc.get("fa_fixtures_url"),
            bot_id=doc.get("bot_id"),
            bot_token=doc.get("bot_token"),
            main_chat_id=main_chat_id,
            leadership_chat_id=leadership_chat_id,
        )

        return team

    def _doc_to_team_member(self, doc: dict) -> TeamMember:
        """Convert a Firestore document to a TeamMember entity."""

        # Parse datetime strings back to datetime objects
        created_at = doc.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = doc.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        telegram_id = doc.get("telegram_id")

        return TeamMember(
            team_id=doc.get("team_id", ""),
            telegram_id=telegram_id,
            member_id=doc.get("member_id"),
            name=doc.get("name"),
            username=doc.get("username"),
            role=doc.get("role", "Team Member"),
            is_admin=doc.get("is_admin", False),
            status=doc.get("status", "active"),
            phone_number=doc.get("phone_number"),
            email=doc.get("email"),
            emergency_contact_name=doc.get("emergency_contact_name"),
            emergency_contact_phone=doc.get("emergency_contact_phone"),
            created_at=created_at,
            updated_at=updated_at,
            source=doc.get("source"),
            sync_version=doc.get("sync_version"),
        )
