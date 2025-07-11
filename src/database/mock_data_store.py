"""
Mock data store for testing purposes.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from unittest.mock import Mock
from database.models_improved import (
    Player, Team, Match, TeamMember, BotMapping, 
    PlayerPosition, PlayerRole, OnboardingStatus, TeamStatus, MatchStatus
)


class MockDataStore:
    """Comprehensive mock data store for testing."""
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.teams: Dict[str, Team] = {}
        self.matches: Dict[str, Match] = {}
        self.team_members: Dict[str, TeamMember] = {}
        self.bot_mappings: Dict[str, BotMapping] = {}
        self.fixtures: Dict[str, Dict[str, Any]] = {}
        self.command_logs: Dict[str, Dict[str, Any]] = {}
        self.team_bots: Dict[str, Dict[str, Any]] = {}
        self.mock = Mock()
    
    # Collection listing
    async def list_collections(self) -> List[str]:
        """List all available collections."""
        return ['players', 'teams', 'matches', 'team_members', 'team_bots', 'fixtures', 'command_logs', 'bot_mappings']
    
    # Player operations
    async def create_player(self, player: Player) -> str:
        """Create a player."""
        if player.id in self.players:
            raise ValueError("Player already exists")
        self.players[player.id] = player
        return player.id
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        return self.players.get(player_id)
    
    async def update_player(self, player: Player) -> bool:
        """Update a player."""
        if player.id in self.players:
            self.players[player.id] = player
            return True
        return False
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    async def get_players_by_team(self, team_id: str) -> List[Player]:
        """Get players by team ID."""
        return [p for p in self.players.values() if p.team_id == team_id]
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get player by phone number and team."""
        for player in self.players.values():
            if player.phone == phone and player.team_id == team_id:
                return player
        return None
    
    # Team operations
    async def create_team(self, team: Team) -> str:
        """Create a team."""
        if team.id in self.teams:
            raise ValueError("Team already exists")
        self.teams[team.id] = team
        return team.id
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        return self.teams.get(team_id)
    
    async def update_team(self, team: Team) -> bool:
        """Update a team."""
        if team.id in self.teams:
            self.teams[team.id] = team
            return True
        return False
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        if team_id in self.teams:
            del self.teams[team_id]
            return True
        return False
    
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get team by name."""
        for team in self.teams.values():
            if team.name == name:
                return team
        return None
    
    # Team member operations
    async def create_team_member(self, member: TeamMember) -> str:
        """Create a team member."""
        if member.id in self.team_members:
            raise ValueError("Team member already exists")
        self.team_members[member.id] = member
        return member.id
    
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        return self.team_members.get(member_id)
    
    async def update_team_member(self, member: TeamMember) -> bool:
        """Update a team member."""
        if member.id in self.team_members:
            self.team_members[member.id] = member
            return True
        return False
    
    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        if member_id in self.team_members:
            del self.team_members[member_id]
            return True
        return False
    
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get team members by team ID."""
        return [m for m in self.team_members.values() if m.team_id == team_id]
    
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        """Get team member by Telegram ID and team."""
        for member in self.team_members.values():
            if member.telegram_id == telegram_id and member.team_id == team_id:
                return member
        return None
    
    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members by role."""
        return [m for m in self.team_members.values() if m.team_id == team_id and role in m.roles]
    
    async def get_leadership_members(self, team_id: str) -> List[TeamMember]:
        """Get leadership team members."""
        return [m for m in self.team_members.values() if m.team_id == team_id and m.has_any_leadership_role()]
    
    # Match operations
    async def create_match(self, match: Match) -> str:
        """Create a match."""
        if match.id in self.matches:
            raise ValueError("Match already exists")
        self.matches[match.id] = match
        return match.id
    
    async def get_match(self, match_id: str) -> Optional[Match]:
        """Get a match by ID."""
        return self.matches.get(match_id)
    
    async def update_match(self, match: Match) -> bool:
        """Update a match."""
        if match.id in self.matches:
            self.matches[match.id] = match
            return True
        return False
    
    async def delete_match(self, match_id: str) -> bool:
        """Delete a match."""
        if match_id in self.matches:
            del self.matches[match_id]
            return True
        return False
    
    async def get_matches_by_team(self, team_id: str) -> List[Match]:
        """Get matches by team ID."""
        return [m for m in self.matches.values() if m.team_id == team_id]
    
    # Bot mapping operations
    async def create_bot_mapping(self, mapping: BotMapping) -> str:
        """Create a bot mapping."""
        if mapping.id in self.bot_mappings:
            raise ValueError("Bot mapping already exists")
        self.bot_mappings[mapping.id] = mapping
        return mapping.id
    
    async def get_bot_mapping(self, mapping_id: str) -> Optional[BotMapping]:
        """Get a bot mapping by ID."""
        return self.bot_mappings.get(mapping_id)
    
    async def update_bot_mapping(self, mapping: BotMapping) -> bool:
        """Update a bot mapping."""
        if mapping.id in self.bot_mappings:
            self.bot_mappings[mapping.id] = mapping
            return True
        return False
    
    async def delete_bot_mapping(self, mapping_id: str) -> bool:
        """Delete a bot mapping."""
        if mapping_id in self.bot_mappings:
            del self.bot_mappings[mapping_id]
            return True
        return False
    
    async def get_bot_mapping_by_team(self, team_name: str) -> Optional[BotMapping]:
        """Get bot mapping by team name."""
        for mapping in self.bot_mappings.values():
            if mapping.team_name == team_name:
                return mapping
        return None
    
    # Generic document operations
    async def create_document(self, collection: str, data: Dict[str, Any]) -> str:
        """Create a generic document."""
        doc_id = f"{collection}_{len(self._get_collection(collection)) + 1}"
        self._get_collection(collection)[doc_id] = data
        return doc_id
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a generic document."""
        return self._get_collection(collection).get(doc_id)
    
    async def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update a generic document."""
        if doc_id in self._get_collection(collection):
            self._get_collection(collection)[doc_id] = data
            return True
        return False
    
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a generic document."""
        if doc_id in self._get_collection(collection):
            del self._get_collection(collection)[doc_id]
            return True
        return False
    
    async def query_documents(self, collection: str, filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Query documents with filters."""
        collection_data = self._get_collection(collection)
        results = []
        for doc_id, doc_data in collection_data.items():
            # Handle list of filter dictionaries
            if isinstance(filters, list):
                matches_all = True
                for filter_dict in filters:
                    field = filter_dict.get('field')
                    operator = filter_dict.get('operator', '==')
                    value = filter_dict.get('value')
                    
                    if field and field in doc_data:
                        if operator == '==' and doc_data[field] != value:
                            matches_all = False
                            break
                        elif operator == '>=' and doc_data[field] < value:
                            matches_all = False
                            break
                        elif operator == '<' and doc_data[field] >= value:
                            matches_all = False
                            break
                    else:
                        matches_all = False
                        break
                
                if matches_all:
                    # Handle both dict and object types
                    if hasattr(doc_data, 'to_dict'):
                        results.append({**doc_data.to_dict(), 'id': doc_id})
                    else:
                        results.append({**doc_data, 'id': doc_id})
            else:
                # Handle dict format for backward compatibility
                if all(doc_data.get(k) == v for k, v in filters.items()):
                    # Handle both dict and object types
                    if hasattr(doc_data, 'to_dict'):
                        results.append({**doc_data.to_dict(), 'id': doc_id})
                    else:
                        results.append({**doc_data, 'id': doc_id})
        return results
    
    # Additional collection operations
    async def create_fixture(self, fixture_data: Dict[str, Any]) -> str:
        """Create a fixture."""
        fixture_id = f"fixture_{len(self.fixtures) + 1}"
        self.fixtures[fixture_id] = fixture_data
        return fixture_id
    
    # Health check and utility methods
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "collections": len(await self.list_collections()),
            "total_documents": sum(len(self._get_collection(c)) for c in await self.list_collections()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics for all collections."""
        return {
            "players": len(self.players),
            "teams": len(self.teams),
            "matches": len(self.matches),
            "team_members": len(self.team_members),
            "bot_mappings": len(self.bot_mappings),
            "fixtures": len(self.fixtures),
            "command_logs": len(self.command_logs),
            "team_bots": len(self.team_bots)
        }
    
    def clear_all_data(self):
        """Clear all data from the store."""
        self.players.clear()
        self.teams.clear()
        self.matches.clear()
        self.team_members.clear()
        self.bot_mappings.clear()
        self.fixtures.clear()
        self.command_logs.clear()
        self.team_bots.clear()
        self.mock.reset_mock()
    
    def reset(self):
        """Reset the mock data store."""
        self.clear_all_data()
    
    def _get_collection(self, collection: str) -> Dict[str, Any]:
        """Get the appropriate collection dictionary."""
        collections = {
            'players': self.players,
            'teams': self.teams,
            'matches': self.matches,
            'team_members': self.team_members,
            'bot_mappings': self.bot_mappings,
            'fixtures': self.fixtures,
            'command_logs': self.command_logs,
            'team_bots': self.team_bots
        }
        return collections.get(collection, {}) 