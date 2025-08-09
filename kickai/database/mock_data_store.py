"""
Mock Data Store for Testing

This module provides a mock data store for testing purposes,
simulating the behavior of the Firebase client without requiring
a real database connection.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock

from loguru import logger

from kickai.features.match_management.domain.entities.match import Match
from kickai.features.player_registration.domain.entities.player import Player
from kickai.features.team_administration.domain.entities.team import Team
from kickai.features.team_administration.domain.entities.team_member import TeamMember


class MockDataStore:
    """Comprehensive mock data store for testing."""

    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.teams: Dict[str, Team] = {}
        self.matches: Dict[str, Match] = {}
        self.team_members: Dict[str, TeamMember] = {}
        self.fixtures: Dict[str, Dict[str, Any]] = {}
        self.command_logs: Dict[str, Dict[str, Any]] = {}
        self.team_bots: Dict[str, Dict[str, Any]] = {}
        self.mock = Mock()

    # Collection listing
    async def list_collections(self) -> List[str]:
        """List all available collections."""
        return [
            "players",
            "teams",
            "matches",
            "team_members",
            "team_bots",
            "fixtures",
            "command_logs",
        ]

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

    async def update_player(self, player_id: str, updates: Dict[str, Any]) -> Optional[Player]:
        """Update a player by ID with updates dictionary."""
        if player_id in self.players:
            player = self.players[player_id]
            # Apply updates to the player object
            for key, value in updates.items():
                if hasattr(player, key):
                    setattr(player, key, value)
            self.players[player_id] = player
            return player
        return None

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
            if player.phone_number == phone and player.team_id == team_id:
                return player
        return None

    async def get_player_by_telegram_id(self, telegram_id: Union[str, int], team_id: str) -> Optional[Player]:
        """Get player by Telegram ID and team."""
        # Normalize telegram_id to int for consistent comparison
        normalized_telegram_id = int(telegram_id) if telegram_id else None
        if normalized_telegram_id is None:
            return None
            
        for player in self.players.values():
            # Compare using normalized integer values
            player_telegram_id = int(player.telegram_id) if player.telegram_id else None
            if player_telegram_id == normalized_telegram_id and player.team_id == team_id:
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

    async def get_team_member_by_telegram_id(
        self, telegram_id: Union[str, int], team_id: str
    ) -> Optional[TeamMember]:
        """Get team member by Telegram ID and team."""
        # Normalize telegram_id to int for consistent comparison
        normalized_telegram_id = int(telegram_id) if telegram_id else None
        if normalized_telegram_id is None:
            return None
            
        for member in self.team_members.values():
            # Compare using normalized integer values
            member_telegram_id = int(member.telegram_id) if member.telegram_id else None
            if member_telegram_id == normalized_telegram_id and member.team_id == team_id:
                return member
        return None

    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members by role."""
        return [m for m in self.team_members.values() if m.team_id == team_id and role in m.roles]

    async def get_leadership_members(self, team_id: str) -> List[TeamMember]:
        """Get leadership team members."""
        return [
            m
            for m in self.team_members.values()
            if m.team_id == team_id and m.has_any_leadership_role()
        ]

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

    # Additional collection operations
    async def create_fixture(self, fixture_data: Dict[str, Any]) -> str:
        """Create a fixture."""
        fixture_id = f"fixture_{len(self.fixtures) + 1}"
        self.fixtures[fixture_id] = fixture_data
        logger.info(f"✅ Created fixture with ID: {fixture_id}")
        return fixture_id

    async def get_fixture(self, fixture_id: str) -> Optional[Dict[str, Any]]:
        """Get a fixture by ID."""
        return self.fixtures.get(fixture_id)

    # Generic document operations
    async def create_document(
        self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None
    ) -> str:
        """Create a generic document."""
        if doc_id is None:
            doc_id = f"{collection}_{len(self._get_collection(collection)) + 1}"
        self._get_collection(collection)[doc_id] = data
        logger.info(f"✅ Created document with ID: {doc_id}")
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

    async def query_documents(
        self, collection: str, filters: Optional[List[Dict[str, Any]]] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query documents with filters."""
        collection_data = self._get_collection(collection)
        logger.info(
            f"🔍 [MOCK] query_documents called for collection '{collection}' with {len(collection_data)} documents"
        )
        logger.info(f"🔍 [MOCK] Collection data keys: {list(collection_data.keys())}")
        logger.info(f"🔍 [MOCK] Filters: {filters}, Limit: {limit}")

        results = []

        # If no filters provided, return all documents
        if not filters:
            for doc_id, doc_data in collection_data.items():
                logger.info(f"🔍 [MOCK] Processing document {doc_id}: {type(doc_data)}")
                # Handle both dict and object types
                if hasattr(doc_data, "to_dict"):
                    # Convert object to dict using to_dict method
                    doc_dict = doc_data.to_dict()
                    doc_dict["id"] = doc_id
                    results.append(doc_dict)
                elif isinstance(doc_data, dict):
                    # Already a dict, just add id
                    results.append({**doc_data, "id": doc_id})
                else:
                    # Try to convert to dict using vars() or __dict__
                    try:
                        if hasattr(doc_data, "__dict__"):
                            doc_dict = vars(doc_data)
                        else:
                            doc_dict = doc_data.__dict__
                        doc_dict["id"] = doc_id
                        results.append(doc_dict)
                    except Exception as e:
                        logger.error(f"🔍 [MOCK] Failed to convert document {doc_id} to dict: {e}")
                        continue
        else:
            # Apply filters
            for doc_id, doc_data in collection_data.items():
                # Handle both dict and object types for filtering
                if hasattr(doc_data, "to_dict"):
                    doc_dict = doc_data.to_dict()
                elif isinstance(doc_data, dict):
                    doc_dict = doc_data
                else:
                    try:
                        if hasattr(doc_data, "__dict__"):
                            doc_dict = vars(doc_data)
                        else:
                            doc_dict = doc_data.__dict__
                    except Exception as e:
                        logger.error(
                            f"🔍 [MOCK] Failed to convert document {doc_id} to dict for filtering: {e}"
                        )
                        continue

                # Apply filters
                matches = True
                for filter_dict in filters:
                    for field, value in filter_dict.items():
                        if field not in doc_dict or doc_dict[field] != value:
                            matches = False
                            break
                    if not matches:
                        break

                if matches:
                    # Handle both dict and object types for results
                    if hasattr(doc_data, "to_dict"):
                        doc_dict = doc_data.to_dict()
                        doc_dict["id"] = doc_id
                        results.append(doc_dict)
                    elif isinstance(doc_data, dict):
                        results.append({**doc_data, "id": doc_id})
                    else:
                        try:
                            if hasattr(doc_data, "__dict__"):
                                doc_dict = vars(doc_data)
                            else:
                                doc_dict = doc_data.__dict__
                            doc_dict["id"] = doc_id
                            results.append(doc_dict)
                        except Exception as e:
                            logger.error(
                                f"🔍 [MOCK] Failed to convert document {doc_id} to dict for results: {e}"
                            )
                            continue

        # Apply limit if specified
        if limit and len(results) > limit:
            results = results[:limit]

        logger.info(f"🔍 [MOCK] Returning {len(results)} documents")
        return results

    # Health check and utility methods
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "message": "Mock data store is operational",
            "collections": len(await self.list_collections()),
            "total_documents": sum(
                len(self._get_collection(c)) for c in await self.list_collections()
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics for all collections."""
        return {
            "players": len(self.players),
            "teams": len(self.teams),
            "matches": len(self.matches),
            "team_members": len(self.team_members),
            "fixtures": len(self.fixtures),
            "command_logs": len(self.command_logs),
            "team_bots": len(self.team_bots),
        }

    def clear_all_data(self):
        """Clear all data from the store."""
        self.players.clear()
        self.teams.clear()
        self.matches.clear()
        self.team_members.clear()
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
            "players": self.players,
            "teams": self.teams,
            "matches": self.matches,
            "team_members": self.team_members,
            "fixtures": self.fixtures,
            "command_logs": self.command_logs,
            "team_bots": self.team_bots,
        }
        return collections.get(collection, {})
