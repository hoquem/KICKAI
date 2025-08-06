#!/usr/bin/env python3
"""
Firestore Data Cleanup and Standardization Script

This script:
1. Reviews current Firestore data structure
2. Cleans up data to comply with expected schema
3. Creates additional test users for comprehensive testing
4. Ensures data consistency across both teams
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load test environment
load_dotenv('.env.test')

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kickai.database.firebase_client import get_firebase_client
from kickai.utils.user_id_generator import generate_user_id
from kickai.core.enums import PlayerPosition, TeamStatus
from kickai.features.player_registration.domain.entities.player import Player
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.features.team_administration.domain.entities.team import Team

class FirestoreDataManager:
    """Manages Firestore data cleanup and standardization."""
    
    def __init__(self):
        self.firebase_client = get_firebase_client()
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for the script."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def review_current_data(self):
        """Review current Firestore data structure."""
        self.logger.info("🔍 Reviewing current Firestore data...")
        
        # Check teams
        teams = await self.firebase_client.query_documents('kickai_teams')
        self.logger.info(f"Found {len(teams)} teams")
        
        for team in teams:
            team_id = team.get('id')
            team_name = team.get('name')
            self.logger.info(f"  - {team_id}: {team_name}")
            
            # Check players
            players = await self.firebase_client.query_documents(f'kickai_{team_id}_players')
            self.logger.info(f"    Players: {len(players)}")
            
            # Check team members
            members = await self.firebase_client.query_documents(f'kickai_{team_id}_team_members')
            self.logger.info(f"    Team Members: {len(members)}")
    
    async def cleanup_team_data(self, team_id: str):
        """Clean up team data to comply with expected schema."""
        self.logger.info(f"🧹 Cleaning up team {team_id} data...")
        
        # Clean up players
        players = await self.firebase_client.query_documents(f'kickai_{team_id}_players')
        for player in players:
            await self._standardize_player_data(team_id, player)
        
        # Clean up team members
        members = await self.firebase_client.query_documents(f'kickai_{team_id}_team_members')
        for member in members:
            await self._standardize_team_member_data(team_id, member)
    
    async def _standardize_player_data(self, team_id: str, player_data: Dict[str, Any]):
        """Standardize player data structure."""
        player_id = player_data.get('id') or player_data.get('player_id')
        if not player_id:
            self.logger.warning(f"Player missing ID: {player_data}")
            return
        
        # Standardize field names and values
        updates = {}
        
        # Fix position field
        position = player_data.get('position')
        if position:
            # Standardize position values
            position_mapping = {
                'Forward': 'forward',
                'FORWARD': 'forward',
                'FWD': 'forward',
                'Defender': 'defender',
                'DEFENDER': 'defender',
                'DEF': 'defender',
                'Midfielder': 'midfielder',
                'MIDFIELDER': 'midfielder',
                'MID': 'midfielder',
                'Goalkeeper': 'goalkeeper',
                'GOALKEEPER': 'goalkeeper',
                'GK': 'goalkeeper',
                'Striker': 'striker',
                'STRIKER': 'striker',
                'ST': 'striker',
            }
            if position in position_mapping:
                updates['position'] = position_mapping[position]
        
        # Ensure required fields exist
        if 'user_id' not in player_data or not player_data['user_id']:
            telegram_id = player_data.get('telegram_id')
            if telegram_id:
                updates['user_id'] = generate_user_id(str(telegram_id))
        
        # Ensure player_id field exists
        if 'player_id' not in player_data:
            updates['player_id'] = player_id
        
        # Standardize status
        status = player_data.get('status')
        if status and status not in ['active', 'inactive', 'pending', 'approved', 'rejected']:
            updates['status'] = 'active'  # Default to active
        
        # Add missing timestamps
        if 'created_at' not in player_data:
            updates['created_at'] = datetime.now().isoformat()
        if 'updated_at' not in player_data:
            updates['updated_at'] = datetime.now().isoformat()
        
        # Add source and sync_version if missing
        if 'source' not in player_data:
            updates['source'] = 'data_cleanup'
        if 'sync_version' not in player_data:
            updates['sync_version'] = '1.0'
        
        # Apply updates if any
        if updates:
            self.logger.info(f"  Updating player {player_id}: {updates}")
            await self.firebase_client.update_document(
                f'kickai_{team_id}_players', 
                player_id, 
                updates
            )
    
    async def _standardize_team_member_data(self, team_id: str, member_data: Dict[str, Any]):
        """Standardize team member data structure."""
        member_id = member_data.get('id') or member_data.get('member_id') or member_data.get('user_id')
        if not member_id:
            self.logger.warning(f"Team member missing ID: {member_data}")
            return
        
        # Standardize field names and values
        updates = {}
        
        # Ensure user_id field exists
        if 'user_id' not in member_data or not member_data['user_id']:
            telegram_id = member_data.get('telegram_id')
            if telegram_id:
                updates['user_id'] = generate_user_id(str(telegram_id))
        
        # Standardize role field
        role = member_data.get('role')
        if role:
            # Standardize role values
            role_mapping = {
                'admin': 'club_administrator',
                'team member': 'team_member',
                'team_member': 'team_member',
                'club administrator': 'club_administrator',
                'club_administrator': 'club_administrator',
                'team manager': 'team_manager',
                'team_manager': 'team_manager',
                'coach': 'coach',
                'assistant_coach': 'assistant_coach',
            }
            if role.lower() in role_mapping:
                updates['role'] = role_mapping[role.lower()]
        
        # Standardize is_admin field
        if 'is_admin' not in member_data:
            role = member_data.get('role', '')
            updates['is_admin'] = role in ['club_administrator', 'team_manager', 'coach']
        
        # Standardize status
        status = member_data.get('status')
        if status and status not in ['active', 'inactive', 'suspended']:
            updates['status'] = 'active'  # Default to active
        
        # Add missing timestamps
        if 'created_at' not in member_data:
            updates['created_at'] = datetime.now().isoformat()
        if 'updated_at' not in member_data:
            updates['updated_at'] = datetime.now().isoformat()
        
        # Add source and sync_version if missing
        if 'source' not in member_data:
            updates['source'] = 'data_cleanup'
        if 'sync_version' not in member_data:
            updates['sync_version'] = '1.0'
        
        # Apply updates if any
        if updates:
            self.logger.info(f"  Updating team member {member_id}: {updates}")
            await self.firebase_client.update_document(
                f'kickai_{team_id}_team_members', 
                member_id, 
                updates
            )
    
    async def create_test_users(self):
        """Create additional test users for comprehensive testing."""
        self.logger.info("👥 Creating additional test users...")
        
        # Get existing teams
        teams = await self.firebase_client.query_documents('kickai_teams')
        
        for team in teams:
            team_id = team.get('id')
            if team_id == 'KTI':
                await self._create_kai_test_users(team_id)
            elif team_id == 'TEST_TEAM_001':
                await self._create_test_team_users(team_id)
    
    async def _create_kai_test_users(self, team_id: str):
        """Create test users for KAI team."""
        self.logger.info(f"Creating test users for team {team_id}...")
        
        # Test Players
        test_players = [
            {
                'player_id': 'KAI_001',
                'full_name': 'Alex Johnson',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'position': 'forward',
                'phone_number': '+447700900001',
                'telegram_id': '10001',
                'status': 'active'
            },
            {
                'player_id': 'KAI_002',
                'full_name': 'Ben Smith',
                'first_name': 'Ben',
                'last_name': 'Smith',
                'position': 'midfielder',
                'phone_number': '+447700900002',
                'telegram_id': '10002',
                'status': 'active'
            },
            {
                'player_id': 'KAI_003',
                'full_name': 'Carlos Rodriguez',
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'position': 'defender',
                'phone_number': '+447700900003',
                'telegram_id': '10003',
                'status': 'active'
            },
            {
                'player_id': 'KAI_004',
                'full_name': 'David Wilson',
                'first_name': 'David',
                'last_name': 'Wilson',
                'position': 'goalkeeper',
                'phone_number': '+447700900004',
                'telegram_id': '10004',
                'status': 'active'
            },
            {
                'player_id': 'KAI_005',
                'full_name': 'Emma Davis',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'position': 'midfielder',
                'phone_number': '+447700900005',
                'telegram_id': '10005',
                'status': 'pending'
            }
        ]
        
        # Test Team Members
        test_members = [
            {
                'user_id': 'user_10001',
                'full_name': 'Coach Mike Thompson',
                'first_name': 'Mike',
                'last_name': 'Thompson',
                'role': 'coach',
                'phone_number': '+447700900101',
                'telegram_id': '20001',
                'is_admin': True,
                'status': 'active'
            },
            {
                'user_id': 'user_10002',
                'full_name': 'Assistant Coach Lisa Park',
                'first_name': 'Lisa',
                'last_name': 'Park',
                'role': 'assistant_coach',
                'phone_number': '+447700900102',
                'telegram_id': '20002',
                'is_admin': True,
                'status': 'active'
            },
            {
                'user_id': 'user_10003',
                'full_name': 'Team Secretary Tom Brown',
                'first_name': 'Tom',
                'last_name': 'Brown',
                'role': 'team_member',
                'phone_number': '+447700900103',
                'telegram_id': '20003',
                'is_admin': False,
                'status': 'active'
            }
        ]
        
        # Create players
        for player_data in test_players:
            await self._create_test_player(team_id, player_data)
        
        # Create team members
        for member_data in test_members:
            await self._create_test_team_member(team_id, member_data)
    
    async def _create_test_team_users(self, team_id: str):
        """Create test users for TEST_TEAM_001."""
        self.logger.info(f"Creating test users for team {team_id}...")
        
        # Test Players
        test_players = [
            {
                'player_id': 'TEST_001',
                'full_name': 'Frank Miller',
                'first_name': 'Frank',
                'last_name': 'Miller',
                'position': 'forward',
                'phone_number': '+447700900201',
                'telegram_id': '30001',
                'status': 'active'
            },
            {
                'player_id': 'TEST_002',
                'full_name': 'Grace Lee',
                'first_name': 'Grace',
                'last_name': 'Lee',
                'position': 'midfielder',
                'phone_number': '+447700900202',
                'telegram_id': '30002',
                'status': 'active'
            },
            {
                'player_id': 'TEST_003',
                'full_name': 'Henry Taylor',
                'first_name': 'Henry',
                'last_name': 'Taylor',
                'position': 'defender',
                'phone_number': '+447700900203',
                'telegram_id': '30003',
                'status': 'pending'
            }
        ]
        
        # Test Team Members
        test_members = [
            {
                'user_id': 'user_20001',
                'full_name': 'Manager Sarah Williams',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'role': 'team_manager',
                'phone_number': '+447700900301',
                'telegram_id': '40001',
                'is_admin': True,
                'status': 'active'
            }
        ]
        
        # Create players
        for player_data in test_players:
            await self._create_test_player(team_id, player_data)
        
        # Create team members
        for member_data in test_members:
            await self._create_test_team_member(team_id, member_data)
    
    async def _create_test_player(self, team_id: str, player_data: Dict[str, Any]):
        """Create a test player."""
        player_id = player_data['player_id']
        
        # Check if player already exists
        existing = await self.firebase_client.get_document(f'kickai_{team_id}_players', player_id)
        if existing:
            self.logger.info(f"  Player {player_id} already exists, skipping")
            return
        
        # Create player document
        player_doc = {
            'id': player_id,
            'player_id': player_id,
            'user_id': generate_user_id(str(player_data['telegram_id'])),
            'team_id': team_id,
            'telegram_id': player_data['telegram_id'],
            'first_name': player_data['first_name'],
            'last_name': player_data['last_name'],
            'full_name': player_data['full_name'],
            'position': player_data['position'],
            'phone_number': player_data['phone_number'],
            'status': player_data['status'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'source': 'test_data_creation',
            'sync_version': '1.0'
        }
        
        await self.firebase_client.create_document(
            f'kickai_{team_id}_players',
            player_doc,
            player_id
        )
        self.logger.info(f"  ✅ Created player: {player_data['full_name']} ({player_id})")
    
    async def _create_test_team_member(self, team_id: str, member_data: Dict[str, Any]):
        """Create a test team member."""
        member_id = member_data['user_id']
        
        # Check if member already exists
        existing = await self.firebase_client.get_document(f'kickai_{team_id}_team_members', member_id)
        if existing:
            self.logger.info(f"  Team member {member_id} already exists, skipping")
            return
        
        # Create team member document
        member_doc = {
            'id': member_id,
            'user_id': member_id,
            'team_id': team_id,
            'telegram_id': member_data['telegram_id'],
            'first_name': member_data['first_name'],
            'last_name': member_data['last_name'],
            'full_name': member_data['full_name'],
            'role': member_data['role'],
            'is_admin': member_data['is_admin'],
            'status': member_data['status'],
            'phone_number': member_data['phone_number'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'source': 'test_data_creation',
            'sync_version': '1.0'
        }
        
        await self.firebase_client.create_document(
            f'kickai_{team_id}_team_members',
            member_doc,
            member_id
        )
        self.logger.info(f"  ✅ Created team member: {member_data['full_name']} ({member_id})")
    
    async def run_cleanup_and_standardization(self):
        """Run the complete cleanup and standardization process."""
        self.logger.info("🚀 Starting Firestore data cleanup and standardization...")
        
        # Step 1: Review current data
        await self.review_current_data()
        
        # Step 2: Clean up existing data
        teams = await self.firebase_client.query_documents('kickai_teams')
        for team in teams:
            team_id = team.get('id')
            if team_id:
                await self.cleanup_team_data(team_id)
        
        # Step 3: Create additional test users
        await self.create_test_users()
        
        # Step 4: Final review
        self.logger.info("🔍 Final data review...")
        await self.review_current_data()
        
        self.logger.info("✅ Firestore data cleanup and standardization completed!")

async def main():
    """Main function."""
    manager = FirestoreDataManager()
    await manager.run_cleanup_and_standardization()

if __name__ == "__main__":
    asyncio.run(main()) 