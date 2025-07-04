"""
Mock Data Store for KICKAI Testing

This module provides a comprehensive mock implementation of the data store interface
for testing purposes, with in-memory storage for all collections used in the system.
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import uuid
from dataclasses import dataclass, asdict

from .interfaces import DataStoreInterface
from .models import Player, Team, Match, TeamMember, BotMapping, OnboardingStatus, TeamStatus
from ..core.exceptions import NotFoundError, DuplicateError, DatabaseError


@dataclass
class MockDocument:
    """Mock document with metadata."""
    id: str
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class MockDataStore(DataStoreInterface):
    """
    Comprehensive mock data store with in-memory storage for all collections.
    
    Supports all collections found in the codebase:
    - players
    - teams  
    - matches
    - team_members
    - team_bots
    - fixtures
    - command_logs
    - bot_mappings
    """
    
    def __init__(self, collection_prefix: str = "kickai"):
        self.collection_prefix = collection_prefix
        self._collections: Dict[str, Dict[str, MockDocument]] = {
            "players": {},
            "teams": {},
            "matches": {},
            "team_members": {},
            "team_bots": {},
            "fixtures": {},
            "command_logs": {},
            "bot_mappings": {},
        }
        self._logger = None  # Will be set by dependency injection
        
    def _get_collection(self, collection: str) -> Dict[str, MockDocument]:
        """Get a collection by name."""
        if collection not in self._collections:
            self._collections[collection] = {}
        return self._collections[collection]
    
    def _generate_id(self) -> str:
        """Generate a unique document ID."""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> datetime:
        """Get current timestamp."""
        return datetime.utcnow()
    
    def _document_to_dict(self, doc: MockDocument) -> Dict[str, Any]:
        """Convert mock document to dictionary with ID."""
        result = doc.data.copy()
        result['id'] = doc.id
        result['created_at'] = doc.created_at
        result['updated_at'] = doc.updated_at
        return result
    
    # Generic document operations
    async def create_document(self, collection: str, data: Dict[str, Any], 
                            document_id: Optional[str] = None) -> str:
        """Create a document in the specified collection."""
        col = self._get_collection(collection)
        
        doc_id = document_id or self._generate_id()
        if doc_id in col:
            raise DuplicateError(f"Document with ID {doc_id} already exists in {collection}")
        
        timestamp = self._get_timestamp()
        doc = MockDocument(
            id=doc_id,
            data=data.copy(),
            created_at=timestamp,
            updated_at=timestamp
        )
        
        col[doc_id] = doc
        return doc_id
    
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        col = self._get_collection(collection)
        doc = col.get(document_id)
        return self._document_to_dict(doc) if doc else None
    
    async def update_document(self, collection: str, document_id: str, 
                            data: Dict[str, Any]) -> bool:
        """Update a document."""
        col = self._get_collection(collection)
        if document_id not in col:
            raise NotFoundError(f"Document {document_id} not found in {collection}")
        
        doc = col[document_id]
        doc.data.update(data)
        doc.updated_at = self._get_timestamp()
        return True
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        col = self._get_collection(collection)
        if document_id not in col:
            return False
        
        del col[document_id]
        return True
    
    async def query_documents(self, collection: str, filters: Optional[List[Dict[str, Any]]] = None,
                            order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query documents with filters."""
        col = self._get_collection(collection)
        docs = list(col.values())
        
        # Apply filters
        if filters:
            for filter_item in filters:
                field = filter_item.get('field')
                operator = filter_item.get('operator', '==')
                value = filter_item.get('value')
                
                if field and operator == '==':
                    docs = [doc for doc in docs if doc.data.get(field) == value]
                elif field and operator == '!=':
                    docs = [doc for doc in docs if doc.data.get(field) != value]
                elif field and operator == 'in' and value is not None:
                    docs = [doc for doc in docs if doc.data.get(field) in value]
                elif field and operator == '>':
                    docs = [doc for doc in docs if doc.data.get(field, 0) > value]
                elif field and operator == '<':
                    docs = [doc for doc in docs if doc.data.get(field, 0) < value]
        
        # Apply ordering
        if order_by:
            reverse = order_by.startswith('-')
            field = order_by[1:] if reverse else order_by
            docs.sort(key=lambda doc: doc.data.get(field, ''), reverse=reverse)
        
        # Apply limit
        if limit:
            docs = docs[:limit]
        
        return [self._document_to_dict(doc) for doc in docs]
    
    async def list_collections(self) -> List[str]:
        """List all collection names."""
        return list(self._collections.keys())
    
    async def execute_batch(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """Execute a batch of operations."""
        results = []
        
        for operation in operations:
            op_type = operation['type']
            collection = operation['collection']
            data = operation.get('data', {})
            
            if op_type == 'create':
                doc_id = await self.create_document(collection, data)
                results.append(doc_id)
            
            elif op_type == 'update':
                doc_id = operation['document_id']
                success = await self.update_document(collection, doc_id, data)
                results.append(doc_id if success else None)
            
            elif op_type == 'delete':
                doc_id = operation['document_id']
                success = await self.delete_document(collection, doc_id)
                results.append(doc_id if success else None)
        
        return results
    
    # Player operations
    async def create_player(self, player: Player) -> str:
        """Create a new player."""
        data = asdict(player)
        data.pop('id', None)  # Remove ID if present
        return await self.create_document('players', data)
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        data = await self.get_document('players', player_id)
        return Player.from_dict(data) if data else None
    
    async def update_player(self, player: Player) -> bool:
        """Update a player."""
        data = asdict(player)
        data.pop('id', None)  # Remove ID for update
        return await self.update_document('players', player.id, data)
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        return await self.delete_document('players', player_id)
    
    async def get_players_by_team(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        docs = await self.query_documents('players', filters)
        return [Player.from_dict(doc) for doc in docs]
    
    async def get_all_players(self, team_id: str) -> List[Player]:
        """Get all players for a team (alias for get_players_by_team)."""
        return await self.get_players_by_team(team_id)
    
    async def get_player_by_phone(self, phone: str) -> Optional[Player]:
        """Get a player by phone number."""
        filters = [{'field': 'phone', 'operator': '==', 'value': phone}]
        docs = await self.query_documents('players', filters, limit=1)
        return Player.from_dict(docs[0]) if docs else None
    
    async def get_team_players(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        return await self.get_players_by_team(team_id)
    
    async def get_players_by_status(self, team_id: str, status: OnboardingStatus) -> List[Player]:
        """Get players by onboarding status."""
        filters = [
            {'field': 'team_id', 'operator': '==', 'value': team_id},
            {'field': 'onboarding_status', 'operator': '==', 'value': status.value}
        ]
        docs = await self.query_documents('players', filters)
        return [Player.from_dict(doc) for doc in docs]
    
    # Team operations
    async def create_team(self, team: Team) -> str:
        """Create a new team."""
        data = asdict(team)
        data.pop('id', None)
        return await self.create_document('teams', data)
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        data = await self.get_document('teams', team_id)
        return Team.from_dict(data) if data else None
    
    async def update_team(self, team: Team) -> bool:
        """Update a team."""
        data = asdict(team)
        data.pop('id', None)
        return await self.update_document('teams', team.id, data)
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        return await self.delete_document('teams', team_id)
    
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get a team by name."""
        filters = [{'field': 'name', 'operator': '==', 'value': name}]
        docs = await self.query_documents('teams', filters, limit=1)
        return Team.from_dict(docs[0]) if docs else None
    
    async def get_all_teams(self, status: Optional[TeamStatus] = None) -> List[Team]:
        """Get all teams, optionally filtered by status."""
        filters = []
        if status:
            filters.append({'field': 'status', 'operator': '==', 'value': status.value})
        docs = await self.query_documents('teams', filters)
        return [Team.from_dict(doc) for doc in docs]
    
    # Bot mapping operations
    async def create_bot_mapping(self, mapping: BotMapping) -> str:
        """Create a new bot mapping."""
        data = asdict(mapping)
        data.pop('id', None)
        return await self.create_document('bot_mappings', data)
    
    async def get_bot_mapping(self, team_name: str) -> Optional[BotMapping]:
        """Get a bot mapping by team name."""
        filters = [{'field': 'team_name', 'operator': '==', 'value': team_name}]
        docs = await self.query_documents('bot_mappings', filters, limit=1)
        return BotMapping.from_dict(docs[0]) if docs else None
    
    async def update_bot_mapping(self, bot_mapping: BotMapping) -> bool:
        """Update a bot mapping."""
        data = asdict(bot_mapping)
        data.pop('id', None)
        return await self.update_document('bot_mappings', bot_mapping.id, data)
    
    async def delete_bot_mapping(self, team_name: str) -> bool:
        """Delete a bot mapping by team name."""
        filters = [{'field': 'team_name', 'operator': '==', 'value': team_name}]
        docs = await self.query_documents('bot_mappings', filters, limit=1)
        if docs:
            return await self.delete_document('bot_mappings', docs[0]['id'])
        return False
    

    
    # Match operations
    async def create_match(self, match: Match) -> str:
        """Create a new match."""
        data = asdict(match)
        data.pop('id', None)
        return await self.create_document('matches', data)
    
    async def get_match(self, match_id: str) -> Optional[Match]:
        """Get a match by ID."""
        data = await self.get_document('matches', match_id)
        return Match.from_dict(data) if data else None
    
    async def update_match(self, match: Match) -> bool:
        """Update a match."""
        data = asdict(match)
        data.pop('id', None)
        return await self.update_document('matches', match.id, data)
    
    async def delete_match(self, match_id: str) -> bool:
        """Delete a match."""
        return await self.delete_document('matches', match_id)
    
    async def get_matches_by_team(self, team_id: str) -> List[Match]:
        """Get all matches for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        docs = await self.query_documents('matches', filters)
        return [Match.from_dict(doc) for doc in docs]
    
    async def get_team_matches(self, team_id: str) -> List[Match]:
        """Get all matches for a team."""
        return await self.get_matches_by_team(team_id)
    
    # Team member operations
    async def create_team_member(self, team_member: TeamMember) -> str:
        """Create a new team member."""
        data = asdict(team_member)
        data.pop('id', None)
        return await self.create_document('team_members', data)
    
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        data = await self.get_document('team_members', member_id)
        return TeamMember.from_dict(data) if data else None
    
    async def update_team_member(self, team_member: TeamMember) -> bool:
        """Update a team member."""
        data = asdict(team_member)
        data.pop('id', None)
        return await self.update_document('team_members', team_member.id, data)
    
    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        return await self.delete_document('team_members', member_id)
    
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all team members for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        docs = await self.query_documents('team_members', filters)
        return [TeamMember.from_dict(doc) for doc in docs]
    
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by Telegram ID and team."""
        filters = [
            {'field': 'telegram_id', 'operator': '==', 'value': telegram_id},
            {'field': 'team_id', 'operator': '==', 'value': team_id}
        ]
        docs = await self.query_documents('team_members', filters, limit=1)
        return TeamMember.from_dict(docs[0]) if docs else None
    
    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members by role."""
        filters = [
            {'field': 'team_id', 'operator': '==', 'value': team_id},
            {'field': 'roles', 'operator': 'in', 'value': [role]}
        ]
        docs = await self.query_documents('team_members', filters)
        return [TeamMember.from_dict(doc) for doc in docs]
    
    async def get_leadership_members(self, team_id: str) -> List[TeamMember]:
        """Get leadership team members."""
        leadership_roles = {'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer'}
        all_members = await self.get_team_members_by_team(team_id)
        return [
            member for member in all_members 
            if any(role in leadership_roles for role in member.roles)
        ]
    
    # Additional collection operations for completeness
    async def create_fixture(self, fixture_data: Dict[str, Any]) -> str:
        """Create a new fixture."""
        return await self.create_document('fixtures', fixture_data)
    
    async def get_fixture(self, fixture_id: str) -> Optional[Dict[str, Any]]:
        """Get a fixture by ID."""
        return await self.get_document('fixtures', fixture_id)
    
    async def update_fixture(self, fixture_id: str, fixture_data: Dict[str, Any]) -> bool:
        """Update a fixture."""
        return await self.update_document('fixtures', fixture_id, fixture_data)
    
    async def delete_fixture(self, fixture_id: str) -> bool:
        """Delete a fixture."""
        return await self.delete_document('fixtures', fixture_id)
    
    async def get_fixtures_by_team(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all fixtures for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        return await self.query_documents('fixtures', filters)
    
    async def create_command_log(self, log_data: Dict[str, Any]) -> str:
        """Create a new command log."""
        return await self.create_document('command_logs', log_data)
    
    async def get_command_logs(self, filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Get command logs with optional filters."""
        return await self.query_documents('command_logs', filters)
    
    async def create_team_bot(self, bot_data: Dict[str, Any]) -> str:
        """Create a new team bot configuration."""
        return await self.create_document('team_bots', bot_data)
    
    async def get_team_bot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get a team bot by ID."""
        return await self.get_document('team_bots', bot_id)
    
    async def update_team_bot(self, bot_id: str, bot_data: Dict[str, Any]) -> bool:
        """Update a team bot."""
        return await self.update_document('team_bots', bot_id, bot_data)
    
    async def delete_team_bot(self, bot_id: str) -> bool:
        """Delete a team bot."""
        return await self.delete_document('team_bots', bot_id)
    
    async def get_team_bots_by_team(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all bot configurations for a team."""
        filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
        return await self.query_documents('team_bots', filters)
    
    async def get_active_team_bot(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get the active bot configuration for a team."""
        filters = [
            {'field': 'team_id', 'operator': '==', 'value': team_id},
            {'field': 'is_active', 'operator': '==', 'value': True}
        ]
        docs = await self.query_documents('team_bots', filters, limit=1)
        return docs[0] if docs else None
    
    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the mock data store."""
        try:
            # Test basic operations
            test_data = {'test': 'health_check', 'timestamp': self._get_timestamp()}
            doc_id = await self.create_document('command_logs', test_data)
            retrieved = await self.get_document('command_logs', doc_id)
            await self.delete_document('command_logs', doc_id)
            
            return {
                'status': 'healthy',
                'message': 'Mock data store is operational',
                'collections': list(self._collections.keys()),
                'test_passed': retrieved is not None
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Mock data store health check failed: {str(e)}',
                'error': str(e)
            }
    
    # Utility methods for testing
    def clear_all_data(self):
        """Clear all data from all collections (for testing)."""
        for collection in self._collections:
            self._collections[collection].clear()
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about all collections."""
        return {
            collection: len(docs) 
            for collection, docs in self._collections.items()
        }
    
    def seed_test_data(self):
        """Seed the mock data store with test data."""
        # Create a test team
        test_team = {
            'name': 'Test Team',
            'description': 'A test team for development',
            'is_active': True,
            'created_at': self._get_timestamp()
        }
        
        # Create a test player
        test_player = {
            'name': 'Test Player',
            'phone_number': '+1234567890',
            'team_id': 'test-team-id',
            'is_active': True,
            'created_at': self._get_timestamp()
        }
        
        # Create a test team member
        test_member = {
            'user_id': 'test-user-id',
            'telegram_id': '123456789',
            'team_id': 'test-team-id',
            'roles': ['member'],
            'is_active': True,
            'created_at': self._get_timestamp()
        }
        
        # Add test data to collections
        asyncio.create_task(self.create_document('teams', test_team, 'test-team-id'))
        asyncio.create_task(self.create_document('players', test_player, 'test-player-id'))
        asyncio.create_task(self.create_document('team_members', test_member, 'test-member-id')) 
        asyncio.create_task(self.create_document('team_members', test_member, 'test-member-id')) 