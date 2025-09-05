#!/usr/bin/env python3
"""
Firebase Team Member Repository Implementation

This module provides the Firebase implementation of the team member repository interface.
"""

import logging

from kickai.core.firestore_constants import get_team_members_collection
from kickai.database.interfaces import DataStoreInterface
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.features.team_administration.domain.repositories.team_member_repository_interface import (
    TeamMemberRepositoryInterface,
)

logger = logging.getLogger(__name__)


class FirebaseTeamMemberRepository(TeamMemberRepositoryInterface):
    """Firebase implementation of the team member repository."""

    def __init__(self, database: DataStoreInterface):
        self.database = database

    async def create_team_member(self, team_member: TeamMember) -> TeamMember:
        """Create a new team member."""
        try:
            # Generate document ID from member_id
            document_id = team_member.member_id or f"member_{team_member.telegram_id}"

            # Prepare team member data
            member_data = self._prepare_team_member_data(team_member)

            # Use team-specific collection naming
            collection_name = get_team_members_collection(team_member.team_id)

            await self.database.create_document(
                collection=collection_name, document_id=document_id, data=member_data
            )

            logger.info(
                f"Successfully created team member {document_id} in team {team_member.team_id}"
            )
            return team_member

        except Exception as e:
            logger.error(f"Failed to create team member in team {team_member.team_id}: {e}")
            raise

    def _prepare_team_member_data(self, team_member: TeamMember) -> dict:
        """Prepare team member data for database operations."""
        return {
            "team_id": team_member.team_id,
            "telegram_id": team_member.telegram_id,
            "member_id": team_member.member_id,
            "name": team_member.name,
            "username": team_member.username,
            "phone_number": team_member.phone_number,
            "email": getattr(team_member, "email", None),
            "role": getattr(team_member, "role", "Member"),
            "status": team_member.status.value
            if hasattr(team_member.status, "value")
            else str(team_member.status),
            "is_admin": getattr(team_member, "is_admin", False),
            "created_at": team_member.created_at.isoformat() if team_member.created_at else None,
            "updated_at": team_member.updated_at.isoformat() if team_member.updated_at else None,
        }

    async def get_team_member_by_id(self, member_id: str, team_id: str) -> TeamMember | None:
        """Get a team member by ID."""
        try:
            collection_name = get_team_members_collection(team_id)

            doc = await self.database.get_document(
                collection=collection_name, document_id=member_id
            )

            if doc and doc.get("team_id") == team_id:
                return self._doc_to_team_member(doc)
            return None

        except Exception as e:
            logger.error(f"Failed to get team member by ID {member_id} for team {team_id}: {e}")
            return None

    async def get_team_member_by_telegram_id(
        self, telegram_id: int, team_id: str
    ) -> TeamMember | None:
        """Get a team member by Telegram ID."""
        try:
            collection_name = get_team_members_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "telegram_id", "operator": "==", "value": telegram_id},
                    {"field": "team_id", "operator": "==", "value": team_id},
                ],
            )

            if docs:
                return self._doc_to_team_member(docs[0])
            return None

        except Exception as e:
            logger.error(
                f"Failed to get team member by telegram_id {telegram_id} for team {team_id}: {e}"
            )
            return None

    async def get_team_member_by_phone(self, phone_number: str, team_id: str) -> TeamMember | None:
        """Get a team member by phone number."""
        try:
            collection_name = get_team_members_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "phone_number", "operator": "==", "value": phone_number},
                    {"field": "team_id", "operator": "==", "value": team_id},
                ],
            )

            if docs:
                return self._doc_to_team_member(docs[0])
            return None

        except Exception as e:
            logger.error(
                f"Failed to get team member by phone {phone_number} for team {team_id}: {e}"
            )
            return None

    async def get_team_members(self, team_id: str) -> list[TeamMember]:
        """Get all team members for a team."""
        try:
            collection_name = get_team_members_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[{"field": "team_id", "operator": "==", "value": team_id}],
            )

            return [self._doc_to_team_member(doc) for doc in docs]

        except Exception as e:
            logger.error(f"Failed to get team members for team {team_id}: {e}")
            return []

    async def get_team_members_by_status(self, team_id: str, status: str) -> list[TeamMember]:
        """Get team members by status."""
        try:
            collection_name = get_team_members_collection(team_id)

            docs = await self.database.query_documents(
                collection=collection_name,
                filters=[
                    {"field": "team_id", "operator": "==", "value": team_id},
                    {"field": "status", "operator": "==", "value": status},
                ],
            )

            return [self._doc_to_team_member(doc) for doc in docs]

        except Exception as e:
            logger.error(f"Failed to get team members by status {status} for team {team_id}: {e}")
            return []

    async def update_team_member(self, team_member: TeamMember) -> TeamMember:
        """Update an existing team member."""
        try:
            document_id = team_member.member_id or f"member_{team_member.telegram_id}"
            member_data = self._prepare_team_member_data(team_member)
            collection_name = get_team_members_collection(team_member.team_id)

            await self.database.update_document(
                collection=collection_name, document_id=document_id, data=member_data
            )

            logger.info(
                f"Successfully updated team member {document_id} in team {team_member.team_id}"
            )
            return team_member

        except Exception as e:
            logger.error(f"Failed to update team member in team {team_member.team_id}: {e}")
            raise

    async def delete_team_member(self, member_id: str, team_id: str) -> bool:
        """Delete a team member."""
        try:
            # Verify the member exists
            member = await self.get_team_member_by_id(member_id, team_id)
            if not member:
                logger.warning(f"Team member {member_id} not found in team {team_id} for deletion")
                return False

            collection_name = get_team_members_collection(team_id)
            await self.database.delete_document(collection=collection_name, document_id=member_id)

            logger.info(f"Successfully deleted team member {member_id} from team {team_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete team member {member_id} from team {team_id}: {e}")
            return False

    async def activate_team_member(self, telegram_id: int, team_id: str) -> TeamMember | None:
        """Activate a team member (change status from pending to active)."""
        try:
            member = await self.get_team_member_by_telegram_id(telegram_id, team_id)
            if not member:
                return None

            member.status = "active"
            return await self.update_team_member(member)

        except Exception as e:
            logger.error(f"Failed to activate team member {telegram_id} in team {team_id}: {e}")
            raise

    async def search_team_members(self, team_id: str, search_term: str) -> list[TeamMember]:
        """Search team members by name, phone, or email."""
        try:
            # Get all members first, then filter (simple implementation)
            all_members = await self.get_team_members(team_id)
            search_lower = search_term.lower()

            matching_members = []
            for member in all_members:
                if (
                    (member.name and search_lower in member.name.lower())
                    or (member.phone_number and search_lower in member.phone_number.lower())
                    or (getattr(member, "email", None) and search_lower in member.email.lower())
                ):
                    matching_members.append(member)

            return matching_members

        except Exception as e:
            logger.error(f"Failed to search team members in team {team_id}: {e}")
            return []

    async def update_team_member_field(
        self, telegram_id: int, team_id: str, field: str, value: str
    ) -> bool:
        """Update a single field for a team member."""
        try:
            member = await self.get_team_member_by_telegram_id(telegram_id, team_id)
            if not member:
                return False

            setattr(member, field, value)
            await self.update_team_member(member)
            return True

        except Exception as e:
            logger.error(
                f"Failed to update team member field {field} for telegram_id {telegram_id}: {e}"
            )
            return False

    async def update_team_member_multiple_fields(
        self, telegram_id: int, team_id: str, updates: dict[str, str]
    ) -> bool:
        """Update multiple fields for a team member."""
        try:
            member = await self.get_team_member_by_telegram_id(telegram_id, team_id)
            if not member:
                return False

            for field, value in updates.items():
                setattr(member, field, value)

            await self.update_team_member(member)
            return True

        except Exception as e:
            logger.error(f"Failed to update multiple fields for telegram_id {telegram_id}: {e}")
            return False

    def _doc_to_team_member(self, doc: dict) -> TeamMember:
        """Convert a Firestore document to a TeamMember entity."""
        return TeamMember.from_dict(doc)
