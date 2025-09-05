#!/usr/bin/env python3
"""
Setup E2E Test Data for KICKAI

This script creates comprehensive test data for end-to-end testing including:
- Test team with proper configuration
- Players in various onboarding states
- Team members with different roles
- Leadership team members
- Test matches and payments
"""

import os
import sys
import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from kickai.features.player_registration.domain.entities.player import (
    Player, PlayerPosition, PlayerRole, OnboardingStatus
)
from kickai.features.team_administration.domain.entities.team import Team, TeamStatus
from kickai.features.team_administration.domain.entities.team_member import TeamMember

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load credentials and initialize Firebase app
cred_file = os.getenv('FIREBASE_CREDENTIALS_FILE', './credentials/firebase_credentials_testing.json')
cred = credentials.Certificate(cred_file)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Test configuration
TEAM_ID = "KTI"
TEAM_NAME = "KickAI Testing"
BOT_USERNAME = "KickAITesting_bot"
# Bot token should come from environment variables, not hardcoded in source code
BOT_TOKEN = os.getenv("TEST_BOT_TOKEN", "")  # Should be set in .env.test
MAIN_CHAT_ID = os.getenv("TEST_MAIN_CHAT_ID", "-4889304885")  # Should come from Firestore
LEADERSHIP_CHAT_ID = os.getenv("TEST_LEADERSHIP_CHAT_ID", "-4814449926")  # Should come from Firestore

# Test data configuration
TEST_PLAYERS = [
    {
        "name": "John Smith",
        "phone": "+447123456789",
        "position": PlayerPosition.MIDFIELDER,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.ACTIVE,
        "admin_approved": True,
        "fa_registered": True,
        "fa_registration_number": "FA123456",
        "player_id": "06MFJS",
        "telegram_id": "1581500055",
        "telegram_username": "doods2000"
    },
    {
        "name": "Sarah Johnson",
        "phone": "+447234567890",
        "position": PlayerPosition.FORWARD,
        "role": PlayerRole.CAPTAIN,
        "onboarding_status": OnboardingStatus.ACTIVE,
        "admin_approved": True,
        "fa_registered": True,
        "fa_registration_number": "FA234567",
        "player_id": "09FWSJ",
        "telegram_id": "1581500056",
        "telegram_username": "sarah_j"
    },
    {
        "name": "Mike Wilson",
        "phone": "+447345678901",
        "position": PlayerPosition.DEFENDER,
        "role": PlayerRole.CAPTAIN,
        "onboarding_status": OnboardingStatus.ACTIVE,
        "admin_approved": True,
        "fa_registered": True,
        "fa_registration_number": "FA345678",
        "player_id": "02DFMW",
        "telegram_id": "1581500057",
        "telegram_username": "mike_w"
    },
    {
        "name": "Emma Davis",
        "phone": "+447456789012",
        "position": PlayerPosition.GOALKEEPER,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.PENDING,
        "admin_approved": False,
        "fa_registered": False,
        "player_id": "01GKED",
        "telegram_id": "1581500058",
        "telegram_username": "emma_d"
    },
    {
        "name": "Alex Brown",
        "phone": "+447567890123",
        "position": PlayerPosition.UTILITY,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.PENDING,
        "admin_approved": False,
        "fa_registered": False,
        "player_id": "06MFAB",
        "telegram_id": "1581500059",
        "telegram_username": "alex_b"
    },
    {
        "name": "Lisa Thompson",
        "phone": "+447678901234",
        "position": PlayerPosition.MIDFIELDER,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.ACTIVE,
        "admin_approved": True,
        "fa_registered": False,
        "player_id": "06MFLT",
        "telegram_id": "1581500060",
        "telegram_username": "lisa_t"
    },
    {
        "name": "David Clark",
        "phone": "+447789012345",
        "position": PlayerPosition.UTILITY,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.ACTIVE,
        "admin_approved": True,
        "fa_registered": False,
        "player_id": "06MFDC",
        "telegram_id": "1581500061",
        "telegram_username": "david_c"
    }
]

# Leadership team members (non-players)
LEADERSHIP_MEMBERS = [
    {
        "name": "Coach Wilson",
        "phone": "+447890123456",
        "role": PlayerRole.PLAYER,
        "telegram_id": "1003",
        "telegram_username": "coach_wilson",
        "is_player": False
    },
    {
        "name": "Admin User",
        "phone": "+447890123457",
        "role": PlayerRole.PLAYER,
        "telegram_id": "1581500062",
        "telegram_username": "admin_user",
        "is_player": False
    },
    {
        "name": "Team Secretary",
        "phone": "+447901234567",
        "role": PlayerRole.PLAYER,
        "telegram_id": "1581500063",
        "telegram_username": "team_secretary",
        "is_player": False
    }
]

def create_test_team() -> Dict[str, Any]:
    """Create test team data."""
    return {
        "id": TEAM_ID,
        "name": TEAM_NAME,
        "status": TeamStatus.ACTIVE.value,  # Convert enum to string
        "description": "Test team for E2E testing",
        "settings": {
            "match_fee": 10.0,
            "subscription_fee": 50.0,
            "auto_approve_players": False,
            "require_fa_registration": True
        },
        "payment_rules": {
            "match_fee": 10.0,
            "late_payment_fine": 5.0,
            "subscription_fee": 50.0
        },
        "budget_limits": {
            "max_expense": 1000.0,
            "max_match_fee": 15.0
        },
        "current_balance": 250.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }





async def setup_test_data():
    """Set up all test data in Firestore."""
    logger.info("🚀 Setting up E2E test data...")
    
    # Football ID generator is used automatically
    
    try:
        # 1. Create test team
        logger.info("📋 Creating test team...")
        team_data = create_test_team()
        team_ref = db.collection('kickai_teams').document(TEAM_ID)
        team_ref.set(team_data)
        logger.info(f"  ✅ Created team: {TEAM_NAME}")
        
        # 2. Create players
        logger.info("👥 Creating test players...")
        for player_data in TEST_PLAYERS:
            player_id = player_data['player_id']
            player_ref = db.collection('kickai_KTI_players').document(player_id)
            
            # Convert to Firestore format
            firestore_data = {
                "id": player_id,
                "player_id": player_id,  # Add the player_id field
                "name": player_data['name'],
                "phone": player_data['phone'],
                "position": player_data['position'].value,
                "role": player_data['role'].value,
                "onboarding_status": player_data['onboarding_status'].value,
                "admin_approved": player_data['admin_approved'],
                "admin_approved_at": datetime.now() if player_data['admin_approved'] else None,
                "admin_approved_by": "test_admin",
                "fa_registered": player_data['fa_registered'],
                "fa_registration_number": player_data.get('fa_registration_number'),
                "match_eligible": player_data['admin_approved'] and player_data['onboarding_status'] == OnboardingStatus.ACTIVE,
                "team_id": TEAM_ID,
                "telegram_id": player_data['telegram_id'],
                "telegram_username": player_data['telegram_username'],
                            "onboarding_started_at": datetime.now() if player_data['onboarding_status'] in [OnboardingStatus.PENDING, OnboardingStatus.ACTIVE] else None,
            "onboarding_completed_at": datetime.now() if player_data['onboarding_status'] == OnboardingStatus.ACTIVE else None,
                "last_activity": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            player_ref.set(firestore_data)
            logger.info(f"  ✅ Created player: {player_data['name']} ({player_id})")
        
        # 3. Create team members
        logger.info("👤 Creating team members...")
        for player_data in TEST_PLAYERS:
            member_id = f"TM_{player_data['player_id']}"
            member_ref = db.collection('kickai_KTI_team_members').document(member_id)
            
            # Determine roles based on player role
            roles = [player_data['role'].value]
            if player_data['role'] in [PlayerRole.CAPTAIN]:
                roles.append('admin')
            
            # Determine chat access
            chat_access = {
                "main_chat": True,
                "leadership_chat": player_data['role'] in [PlayerRole.CAPTAIN]
            }
            
            member_data = {
                "id": member_id,
                "team_id": TEAM_ID,
                "user_id": player_data['player_id'],
                "roles": roles,
                "permissions": ["read", "write"] if "admin" in roles else ["read"],
                "chat_access": chat_access,
                "telegram_id": int(player_data['telegram_id']),
                "telegram_username": player_data['telegram_username'],
                "joined_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            member_ref.set(member_data)
            logger.info(f"  ✅ Created team member: {player_data['name']} ({roles})")
        
        # 4. Create leadership members (non-players)
        logger.info("👑 Creating leadership members...")
        for leader_data in LEADERSHIP_MEMBERS:
            member_id = f"TM_LEADER_{leader_data['telegram_username']}"
            member_ref = db.collection('kickai_KTI_team_members').document(member_id)
            
            member_data = {
                "id": member_id,
                "member_id": member_id,
                "team_id": TEAM_ID,
                "name": leader_data['name'],
                "username": leader_data['telegram_username'],
                "role": leader_data['role'].value,
                "phone": leader_data['phone'],
                "status": "active",
                "is_admin": True,
                "roles": [leader_data['role'].value, 'admin'],
                "permissions": ["read", "write", "admin"],
                "chat_access": {
                    "main_chat": True,
                    "leadership_chat": True
                },
                "telegram_id": int(leader_data['telegram_id']),
                "telegram_username": leader_data['telegram_username'],
                "joined_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            member_ref.set(member_data)
            logger.info(f"  ✅ Created leadership member: {leader_data['name']} ({leader_data['role'].value})")
        
        logger.info("🎉 E2E test data setup completed successfully!")
        logger.info("📊 Summary:")
        logger.info(f"  - Team: {TEAM_NAME}")
        logger.info(f"  - Players: {len(TEST_PLAYERS)}")
        logger.info(f"  - Leadership members: {len(LEADERSHIP_MEMBERS)}")
        logger.info("🎯 Ready for end-to-end testing!")
        
    except Exception as e:
        logger.error(f"❌ Error setting up test data: {e}")
        raise

def main():
    """Main function to set up test data."""
    logger.info("🎯 Starting E2E test data setup...")
    
    # Run the setup
    asyncio.run(setup_test_data())
    
    logger.info("✅ Test data setup completed!")

if __name__ == "__main__":
    main() 