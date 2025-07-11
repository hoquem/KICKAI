from .mock_external_player_service import MockExternalPlayerService
from .mock_payment_service import MockPaymentService
from database.models_improved import Player, Team, TeamMember, OnboardingStatus
from services.interfaces.player_service_interface import IPlayerService
from services.interfaces.team_service_interface import ITeamService
from services.interfaces.fa_registration_checker_interface import IFARegistrationChecker
from typing import List, Optional, Dict, Any
import asyncio
from copy import deepcopy

class MockPlayerService(IPlayerService):
    def __init__(self):
        self.players: Dict[str, Player] = {}

    async def create_player(self, name: str, phone: str, team_id: str, position=None, role=None, fa_registered=False, **kwargs) -> Player:
        player = Player.with_generated_id(name, phone, team_id, position=position, role=role, fa_registered=fa_registered, **kwargs)
        self.players[player.id] = player
        return player

    async def get_player(self, player_id: str) -> Optional[Player]:
        return self.players.get(player_id)

    async def update_player(self, player_id: str, **updates) -> Player:
        player = self.players.get(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        # Create a copy of the player to avoid modifying the original
        updated_player = deepcopy(player)
        
        # Update player attributes
        for key, value in updates.items():
            if hasattr(updated_player, key):
                setattr(updated_player, key, value)
        
        # Update the stored player
        self.players[player_id] = updated_player
        
        return updated_player

    async def delete_player(self, player_id: str) -> bool:
        return self.players.pop(player_id, None) is not None

    async def get_players_by_team(self, team_id: str) -> List[Player]:
        return [p for p in self.players.values() if p.team_id == team_id]

    async def get_player_by_phone(self, phone: str, team_id: Optional[str] = None) -> Optional[Player]:
        for p in self.players.values():
            if p.phone == phone and (team_id is None or p.team_id == team_id):
                return p
        return None

    async def get_player_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[Player]:
        for player in self.players.values():
            if player.telegram_id == telegram_id and player.team_id == team_id:
                return player
        return None

    async def get_team_players(self, team_id: str) -> List[Player]:
        return await self.get_players_by_team(team_id)

    async def get_players_by_status(self, team_id: str, status: OnboardingStatus) -> List[Player]:
        return [p for p in self.players.values() if p.team_id == team_id and p.onboarding_status == status]

    async def get_all_players(self, team_id: str) -> List[Player]:
        return await self.get_players_by_team(team_id)

    async def update_onboarding_status(self, player_id: str, status: OnboardingStatus) -> Player:
        player = self.players[player_id]
        player.onboarding_status = status
        return player

    def reset(self):
        """Reset the mock service to clean state."""
        self.players.clear()

class MockTeamService(ITeamService):
    def __init__(self):
        self.teams: Dict[str, Team] = {}
        self.team_members: Dict[str, List[TeamMember]] = {}

    async def create_team(self, name: str, description: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Team:
        team = Team.create(name, description, settings=settings or {})
        self.teams[team.id] = team
        self.team_members[team.id] = []
        return team

    async def get_team(self, team_id: str) -> Optional[Team]:
        return self.teams.get(team_id)

    async def get_team_by_name(self, name: str) -> Optional[Team]:
        for t in self.teams.values():
            if t.name == name:
                return t
        return None

    async def update_team(self, team_id: str, **updates) -> Team:
        team = self.teams[team_id]
        team.update(**updates)
        return team

    async def delete_team(self, team_id: str) -> bool:
        self.teams.pop(team_id, None)
        self.team_members.pop(team_id, None)
        return True

    async def get_all_teams(self, status=None) -> List[Team]:
        if status:
            return [t for t in self.teams.values() if t.status == status]
        return list(self.teams.values())

    async def add_team_member(self, team_id: str, user_id: str, role: str = "player", permissions: Optional[List[str]] = None) -> TeamMember:
        member = TeamMember.create(team_id, user_id, [role], permissions=permissions or [])
        self.team_members[team_id].append(member)
        return member

    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        members = self.team_members.get(team_id, [])
        for m in members:
            if m.user_id == user_id:
                members.remove(m)
                return True
        return False

    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        return self.team_members.get(team_id, [])

    async def create_bot_mapping(self, team_name: str, bot_username: str, chat_id: str, bot_token: str) -> Any:
        return None

    async def get_bot_mapping(self, team_name: str) -> Any:
        return None

    def reset(self):
        """Reset the mock service to clean state."""
        self.teams.clear()
        self.team_members.clear()

class MockFARegistrationChecker(IFARegistrationChecker):
    def __init__(self, player_service: MockPlayerService):
        self.player_service = player_service
        self._registered_players = set()

    def set_registered_players(self, names: List[str]):
        self._registered_players = set(n.lower() for n in names)

    async def scrape_team_page(self) -> Dict[str, bool]:
        # Simulate scraping by returning the set
        return {name: True for name in self._registered_players}

    async def check_player_registration(self, team_id: str) -> Dict[str, bool]:
        players = await self.player_service.get_team_players(team_id)
        updates = {}
        for player in players:
            if player.name.lower() in self._registered_players:
                updates[player.id] = True
                player.fa_registered = True
        return updates

    async def scrape_fixtures(self) -> List[Dict]:
        return [] 