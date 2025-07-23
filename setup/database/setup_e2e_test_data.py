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

from features.player_registration.domain.entities.player import (
    Player, PlayerPosition, PlayerRole, OnboardingStatus
)
from features.team_administration.domain.entities.team import Team, TeamStatus
from features.team_administration.domain.entities.team_member import TeamMember
from features.team_administration.domain.entities.bot_mapping import BotMapping
from features.team_administration.domain.entities.match import Match, MatchStatus
from features.team_administration.domain.entities.payment import Payment, PaymentType, PaymentStatus
from utils.id_generator import IDGenerator

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
TEAM_ID = "KAI"
TEAM_NAME = "KickAI Testing"
BOT_USERNAME = "KickAITesting_bot"
BOT_TOKEN = "7693359073:AAEnLqhdbCOfnf0RDfjn71z8GLRooNKNYsM"
MAIN_CHAT_ID = "-4889304885"
LEADERSHIP_CHAT_ID = "-4814449926"

# Test data configuration
TEST_PLAYERS = [
    {
        "name": "John Smith",
        "phone": "+447123456789",
        "position": PlayerPosition.MIDFIELDER,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.COMPLETED,
        "admin_approved": True,
        "fa_registered": True,
        "fa_registration_number": "FA123456",
        "player_id": "JS",
        "telegram_id": "1581500055",
        "telegram_username": "doods2000"
    },
    {
        "name": "Sarah Johnson",
        "phone": "+447234567890",
        "position": PlayerPosition.FORWARD,
        "role": PlayerRole.CAPTAIN,
        "onboarding_status": OnboardingStatus.COMPLETED,
        "admin_approved": True,
        "fa_registered": True,
        "fa_registration_number": "FA234567",
        "player_id": "SJ",
        "telegram_id": "1581500056",
        "telegram_username": "sarah_j"
    },
    {
        "name": "Mike Wilson",
        "phone": "+447345678901",
        "position": PlayerPosition.DEFENDER,
        "role": PlayerRole.VICE_CAPTAIN,
        "onboarding_status": OnboardingStatus.COMPLETED,
        "admin_approved": True,
        "fa_registered": True,
        "fa_registration_number": "FA345678",
        "player_id": "MW",
        "telegram_id": "1581500057",
        "telegram_username": "mike_w"
    },
    {
        "name": "Emma Davis",
        "phone": "+447456789012",
        "position": PlayerPosition.GOALKEEPER,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.IN_PROGRESS,
        "admin_approved": False,
        "fa_registered": False,
        "player_id": "ED",
        "telegram_id": "1581500058",
        "telegram_username": "emma_d"
    },
    {
        "name": "Alex Brown",
        "phone": "+447567890123",
        "position": PlayerPosition.UTILITY,
        "role": PlayerRole.PLAYER,
        "onboarding_status": OnboardingStatus.PENDING_APPROVAL,
        "admin_approved": False,
        "fa_registered": False,
        "player_id": "AB",
        "telegram_id": "1581500059",
        "telegram_username": "alex_b"
    },
    {
        "name": "Lisa Thompson",
        "phone": "+447678901234",
        "position": PlayerPosition.MIDFIELDER,
        "role": PlayerRole.MANAGER,
        "onboarding_status": OnboardingStatus.COMPLETED,
        "admin_approved": True,
        "fa_registered": False,
        "player_id": "LT",
        "telegram_id": "1581500060",
        "telegram_username": "lisa_t"
    },
    {
        "name": "David Clark",
        "phone": "+447789012345",
        "position": PlayerPosition.UTILITY,
        "role": PlayerRole.COACH,
        "onboarding_status": OnboardingStatus.COMPLETED,
        "admin_approved": True,
        "fa_registered": False,
        "player_id": "DC",
        "telegram_id": "1581500061",
        "telegram_username": "david_c"
    }
]

# Leadership team members (non-players)
LEADERSHIP_MEMBERS = [
    {
        "name": "Admin User",
        "phone": "+447890123456",
        "role": PlayerRole.MANAGER,
        "telegram_id": "1581500062",
        "telegram_username": "admin_user",
        "is_player": False
    },
    {
        "name": "Team Secretary",
        "phone": "+447901234567",
        "role": PlayerRole.MANAGER,
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

def create_test_matches() -> List[Dict[str, Any]]:
    """Create test match data."""
    now = datetime.now()
    return [
        {
            "id": "MATCH001",
            "team_id": TEAM_ID,
            "opponent": "Test FC",
            "date": now + timedelta(days=7),
            "location": "Test Ground",
            "status": MatchStatus.SCHEDULED.value,  # Convert enum to string
            "home_away": "home",
            "competition": "Friendly",
            "confirmed_players": ["JS", "SJ", "MW"],
            "attendees": ["JS", "SJ", "MW"],
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "MATCH002",
            "team_id": TEAM_ID,
            "opponent": "Rivals United",
            "date": now + timedelta(days=14),
            "location": "Away Ground",
            "status": MatchStatus.CONFIRMED.value,  # Convert enum to string
            "home_away": "away",
            "competition": "League",
            "confirmed_players": ["JS", "SJ", "MW", "ED"],
            "attendees": ["JS", "SJ", "MW"],
            "created_at": now,
            "updated_at": now
        }
    ]

def create_test_payments() -> List[Dict[str, Any]]:
    """Create test payment data."""
    now = datetime.now()
    return [
        {
            "id": "PAY001",
            "team_id": TEAM_ID,
            "player_id": "JS",
            "amount": 10.0,
            "type": PaymentType.MATCH_FEE.value,  # Convert enum to string
            "status": PaymentStatus.PAID.value,  # Convert enum to string
            "due_date": now - timedelta(days=1),
            "paid_date": now - timedelta(hours=2),
            "related_entity_id": "MATCH001",
            "description": "Match fee for Test FC game",
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(hours=2)
        },
        {
            "id": "PAY002",
            "team_id": TEAM_ID,
            "player_id": "SJ",
            "amount": 10.0,
            "type": PaymentType.MATCH_FEE.value,  # Convert enum to string
            "status": PaymentStatus.PENDING.value,  # Convert enum to string
            "due_date": now + timedelta(days=6),
            "related_entity_id": "MATCH001",
            "description": "Match fee for Test FC game",
            "created_at": now - timedelta(days=1),
            "updated_at": now - timedelta(days=1)
        }
    ]



async def setup_test_data():
    """Set up all test data in Firestore."""
    logger.info("🚀 Setting up E2E test data...")
    
    # Initialize ID generator
    id_generator = IDGenerator()
    
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
            player_ref = db.collection('kickai_players').document(player_id)
            
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
                "match_eligible": player_data['admin_approved'] and player_data['onboarding_status'] == OnboardingStatus.COMPLETED,
                "team_id": TEAM_ID,
                "telegram_id": player_data['telegram_id'],
                "telegram_username": player_data['telegram_username'],
                "onboarding_started_at": datetime.now() if player_data['onboarding_status'] in [OnboardingStatus.IN_PROGRESS, OnboardingStatus.COMPLETED] else None,
                "onboarding_completed_at": datetime.now() if player_data['onboarding_status'] == OnboardingStatus.COMPLETED else None,
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
            member_ref = db.collection('kickai_team_members').document(member_id)
            
            # Determine roles based on player role
            roles = [player_data['role'].value]
            if player_data['role'] in [PlayerRole.CAPTAIN, PlayerRole.VICE_CAPTAIN, PlayerRole.MANAGER, PlayerRole.COACH]:
                roles.append('admin')
            
            # Determine chat access
            chat_access = {
                "main_chat": True,
                "leadership_chat": player_data['role'] in [PlayerRole.CAPTAIN, PlayerRole.VICE_CAPTAIN, PlayerRole.MANAGER, PlayerRole.COACH]
            }
            
            member_data = {
                "id": member_id,
                "team_id": TEAM_ID,
                "user_id": player_data['player_id'],
                "roles": roles,
                "permissions": ["read", "write"] if "admin" in roles else ["read"],
                "chat_access": chat_access,
                "telegram_id": player_data['telegram_id'],
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
            member_ref = db.collection('kickai_team_members').document(member_id)
            
            member_data = {
                "id": member_id,
                "team_id": TEAM_ID,
                "user_id": leader_data['telegram_username'],
                "roles": [leader_data['role'].value, 'admin'],
                "permissions": ["read", "write", "admin"],
                "chat_access": {
                    "main_chat": True,
                    "leadership_chat": True
                },
                "telegram_id": leader_data['telegram_id'],
                "telegram_username": leader_data['telegram_username'],
                "joined_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            member_ref.set(member_data)
            logger.info(f"  ✅ Created leadership member: {leader_data['name']} ({leader_data['role'].value})")
        
        # 5. Create test matches
        logger.info("⚽ Creating test matches...")
        for match_data in create_test_matches():
            match_ref = db.collection('kickai_matches').document(match_data['id'])
            match_ref.set(match_data)
            logger.info(f"  ✅ Created match: {match_data['opponent']} ({match_data['id']})")
        
        # 6. Create test payments
        logger.info("💰 Creating test payments...")
        for payment_data in create_test_payments():
            payment_ref = db.collection('kickai_payments').document(payment_data['id'])
            payment_ref.set(payment_data)
            logger.info(f"  ✅ Created payment: {payment_data['amount']} for {payment_data['player_id']}")
        
        logger.info("🎉 E2E test data setup completed successfully!")
        logger.info("📊 Summary:")
        logger.info(f"  - Team: {TEAM_NAME}")
        logger.info(f"  - Players: {len(TEST_PLAYERS)}")
        logger.info(f"  - Leadership members: {len(LEADERSHIP_MEMBERS)}")
        logger.info(f"  - Matches: {len(create_test_matches())}")
        logger.info(f"  - Payments: {len(create_test_payments())}")
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