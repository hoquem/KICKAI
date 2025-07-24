"""
Firebase Team Repository Implementation
"""
import logging

from firebase_admin import firestore

from kickai.features.team_administration.domain.entities.team import Team, TeamStatus
from kickai.features.team_administration.domain.repositories.team_repository_interface import (
    TeamRepositoryInterface,
)


class FirebaseTeamRepository(TeamRepositoryInterface):
    """Firebase Firestore implementation of TeamRepository."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def create(self, team: Team) -> Team:
        """Create a new team in Firestore."""
        try:
            team_data = {
                'name': team.name,
                'description': team.description,
                'status': team.status.value,
                'created_at': team.created_at,
                'updated_at': team.updated_at,
                'owner_id': team.owner_id,
                'bot_token': getattr(team, 'bot_token', None),
                'main_chat_id': getattr(team, 'main_chat_id', None),
                'leadership_chat_id': getattr(team, 'leadership_chat_id', None),
            }

            doc_ref = self.db.collection('teams').add(team_data)[1]
            team.id = doc_ref.id
            self.logger.info(f"✅ Created team '{team.name}' with ID: {team.id}")
            return team
        except Exception as e:
            self.logger.error(f"❌ Failed to create team: {e}")
            raise

    async def get_by_id(self, team_id: str) -> Team | None:
        """Get a team by ID from Firestore."""
        try:
            doc = self.db.collection('teams').document(team_id).get()
            if doc.exists:
                team_data = doc.to_dict()
                team_data['id'] = doc.id
                return Team(**team_data)
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get team by ID {team_id}: {e}")
            return None

    async def update(self, team: Team) -> Team | None:
        """Update a team in Firestore."""
        try:
            team_data = {
                'name': team.name,
                'description': team.description,
                'status': team.status.value,
                'updated_at': team.updated_at,
                'owner_id': team.owner_id,
                'bot_token': getattr(team, 'bot_token', None),
                'main_chat_id': getattr(team, 'main_chat_id', None),
                'leadership_chat_id': getattr(team, 'leadership_chat_id', None),
            }

            self.db.collection('teams').document(team.id).update(team_data)
            self.logger.info(f"✅ Updated team '{team.name}' with ID: {team.id}")
            return team
        except Exception as e:
            self.logger.error(f"❌ Failed to update team: {e}")
            return None

    async def delete(self, team_id: str) -> bool:
        """Delete a team from Firestore."""
        try:
            self.db.collection('teams').document(team_id).delete()
            self.logger.info(f"✅ Deleted team with ID: {team_id}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to delete team {team_id}: {e}")
            return False

    async def list_all(self) -> list[Team]:
        """List all teams from Firestore."""
        try:
            teams_ref = self.db.collection('teams')
            docs = teams_ref.stream()

            teams = []
            for doc in docs:
                try:
                    team_data = doc.to_dict()
                    team_data['id'] = doc.id
                    team = Team(**team_data)
                    teams.append(team)
                except Exception as e:
                    self.logger.error(f"❌ Failed to convert document {doc.id} to Team: {e}")
                    continue

            self.logger.info(f"📊 Successfully loaded {len(teams)} teams from Firestore")
            return teams
        except Exception as e:
            self.logger.error(f"❌ Failed to list teams from Firestore: {e}")
            return []

    async def get_by_status(self, status: TeamStatus) -> list[Team]:
        """Get teams by status from Firestore."""
        try:
            teams_ref = self.db.collection('teams')
            docs = teams_ref.where('status', '==', status.value).stream()

            teams = []
            for doc in docs:
                try:
                    team_data = doc.to_dict()
                    team_data['id'] = doc.id
                    team = Team(**team_data)
                    teams.append(team)
                except Exception as e:
                    self.logger.error(f"❌ Failed to convert document {doc.id} to Team: {e}")
                    continue

            return teams
        except Exception as e:
            self.logger.error(f"❌ Failed to get teams by status {status.value}: {e}")
            return []

    async def get_by_owner(self, owner_id: str) -> list[Team]:
        """Get teams by owner ID from Firestore."""
        try:
            teams_ref = self.db.collection('teams')
            docs = teams_ref.where('owner_id', '==', owner_id).stream()

            teams = []
            for doc in docs:
                try:
                    team_data = doc.to_dict()
                    team_data['id'] = doc.id
                    team = Team(**team_data)
                    teams.append(team)
                except Exception as e:
                    self.logger.error(f"❌ Failed to convert document {doc.id} to Team: {e}")
                    continue

            return teams
        except Exception as e:
            self.logger.error(f"❌ Failed to get teams by owner {owner_id}: {e}")
            return []

    async def create_team(self, team: Team) -> Team:
        return await self.create(team)

    async def get_team_by_id(self, team_id: str) -> Team | None:
        return await self.get_by_id(team_id)

    async def update_team(self, team: Team) -> Team | None:
        return await self.update(team)

    async def delete_team(self, team_id: str) -> bool:
        return await self.delete(team_id)

    async def get_all_teams(self) -> list[Team]:
        return await self.list_all()
