#!/usr/bin/env python3
"""
KTI Test Data Manager

Manages test data creation, validation, and cleanup for functional testing
using real Firestore with the KTI team.
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from kickai.core.dependency_container import ensure_container_initialized, get_container
from kickai.core.firestore_constants import (
    get_team_players_collection,
    get_team_members_collection,
    get_collection_name,
    COLLECTION_INVITE_LINKS,
    COLLECTION_TEAMS
)
from kickai.database.interfaces import DataStoreInterface
from loguru import logger

@dataclass
class TestPlayer:
    """Test player data structure"""
    name: str
    phone: str
    telegram_id: int
    status: str = "active"
    position: str = "midfielder"
    player_id: Optional[str] = None

@dataclass 
class TestMember:
    """Test team member data structure"""
    name: str
    phone: str
    telegram_id: int
    role: str = "team_member"
    status: str = "active"
    member_id: Optional[str] = None

@dataclass
class TestUser:
    """Test user profile for Mock Telegram"""
    telegram_id: int
    username: str
    chat_type: str
    role: str

class KTITestDataManager:
    """Manages test data for KTI team functional testing"""
    
    def __init__(self, team_id: str = "KTI"):
        self.team_id = team_id
        self.database: Optional[DataStoreInterface] = None
        self.created_data: Dict[str, List[str]] = {
            "players": [],
            "members": [], 
            "invite_links": [],
            "test_data_markers": []
        }
        
    async def initialize(self):
        """Initialize database connection"""
        try:
            ensure_container_initialized()
            container = get_container()
            self.database = container.get_database()
            logger.info(f"✅ KTI Test Data Manager initialized for team: {self.team_id}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize KTI Test Data Manager: {e}")
            raise

    def get_test_data_set(self) -> Dict[str, Any]:
        """Get comprehensive test data set for KTI team"""
        return {
            "team": {
                "team_id": self.team_id,
                "name": "KickAI Test Team",
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "test_marker": "FUNCTIONAL_TEST_DATA"
            },
            "initial_players": [
                TestPlayer(
                    name="Test Player One",
                    phone="+447111111111", 
                    telegram_id=111111111,
                    status="active",
                    position="midfielder"
                ),
                TestPlayer(
                    name="Test Player Two", 
                    phone="+447222222222",
                    telegram_id=222222222,
                    status="pending",
                    position="forward"
                ),
                TestPlayer(
                    name="Inactive Test Player",
                    phone="+447333333333",
                    telegram_id=333333333,
                    status="inactive", 
                    position="defender"
                )
            ],
            "initial_members": [
                TestMember(
                    name="Test Coach",
                    phone="+447444444444",
                    telegram_id=444444444,
                    role="coach",
                    status="active"
                ),
                TestMember(
                    name="Test Manager",
                    phone="+447555555555", 
                    telegram_id=555555555,
                    role="manager",
                    status="pending"
                )
            ],
            "test_users": {
                "leadership_user": TestUser(
                    telegram_id=999999999,
                    username="test_leader",
                    chat_type="leadership",
                    role="leadership"
                ),
                "player_user": TestUser(
                    telegram_id=888888888,
                    username="test_player", 
                    chat_type="main",
                    role="player"
                ),
                "unregistered_user": TestUser(
                    telegram_id=777777777,
                    username="test_unregistered",
                    chat_type="main", 
                    role="unregistered"
                )
            }
        }

    async def setup_test_data(self) -> bool:
        """Create all test data for functional testing"""
        try:
            logger.info("🚀 Setting up KTI test data...")
            test_data = self.get_test_data_set()
            
            # 1. Ensure KTI team exists
            await self._ensure_team_exists(test_data["team"])
            
            # 2. Create test players
            for player in test_data["initial_players"]:
                await self._create_test_player(player)
                
            # 3. Create test members  
            for member in test_data["initial_members"]:
                await self._create_test_member(member)
                
            # 4. Create test data marker
            await self._create_test_marker()
            
            logger.info("✅ KTI test data setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup KTI test data: {e}")
            await self.cleanup_test_data()  # Clean up partial data
            return False

    async def _ensure_team_exists(self, team_data: Dict[str, Any]):
        """Ensure KTI team exists in Firestore"""
        try:
            teams_collection = get_collection_name(COLLECTION_TEAMS)
            existing_team = await self.database.get_document(teams_collection, self.team_id)
            
            if not existing_team:
                await self.database.create_document(teams_collection, team_data, self.team_id)
                logger.info(f"✅ Created KTI team record")
            else:
                logger.info(f"✅ KTI team already exists")
                
        except Exception as e:
            logger.error(f"❌ Failed to ensure team exists: {e}")
            raise

    async def _create_test_player(self, player: TestPlayer):
        """Create a test player in KTI players collection"""
        try:
            players_collection = get_team_players_collection(self.team_id)
            
            # Generate player ID
            player_id = f"TEST_P{player.telegram_id}"
            player.player_id = player_id
            
            player_data = {
                "player_id": player_id,
                "name": player.name,
                "phone": player.phone,
                "telegram_id": player.telegram_id,
                "status": player.status,
                "position": player.position,
                "team_id": self.team_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "test_marker": "FUNCTIONAL_TEST_DATA"
            }
            
            await self.database.create_document(players_collection, player_data, player_id)
            self.created_data["players"].append(player_id)
            logger.info(f"✅ Created test player: {player.name} ({player_id})")
            
        except Exception as e:
            logger.error(f"❌ Failed to create test player {player.name}: {e}")
            raise

    async def _create_test_member(self, member: TestMember):
        """Create a test member in KTI team members collection"""
        try:
            members_collection = get_team_members_collection(self.team_id)
            
            # Generate member ID
            member_id = f"TEST_M{member.telegram_id}"
            member.member_id = member_id
            
            member_data = {
                "member_id": member_id,
                "name": member.name,
                "phone": member.phone,
                "telegram_id": member.telegram_id,
                "role": member.role,
                "status": member.status,
                "team_id": self.team_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "test_marker": "FUNCTIONAL_TEST_DATA"
            }
            
            await self.database.create_document(members_collection, member_data, member_id)
            self.created_data["members"].append(member_id)
            logger.info(f"✅ Created test member: {member.name} ({member_id})")
            
        except Exception as e:
            logger.error(f"❌ Failed to create test member {member.name}: {e}")
            raise

    async def _create_test_marker(self):
        """Create a test data marker for tracking"""
        try:
            marker_collection = get_collection_name("test_markers")
            marker_id = f"FUNCTIONAL_TEST_{self.team_id}_{int(datetime.now().timestamp())}"
            
            marker_data = {
                "marker_id": marker_id,
                "team_id": self.team_id,
                "test_type": "FUNCTIONAL_TESTING",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "created_data": self.created_data
            }
            
            await self.database.create_document(marker_collection, marker_data, marker_id)
            self.created_data["test_data_markers"].append(marker_id)
            logger.info(f"✅ Created test marker: {marker_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create test marker: {e}")
            # Don't raise - marker creation failure shouldn't stop testing

    async def cleanup_test_data(self) -> bool:
        """Clean up all created test data"""
        try:
            logger.info("🧹 Cleaning up KTI test data...")
            cleanup_success = True
            
            # 1. Clean up players
            if self.created_data["players"]:
                players_collection = get_team_players_collection(self.team_id)
                for player_id in self.created_data["players"]:
                    try:
                        await self.database.delete_document(players_collection, player_id)
                        logger.info(f"✅ Deleted test player: {player_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to delete player {player_id}: {e}")
                        cleanup_success = False
            
            # 2. Clean up members
            if self.created_data["members"]:
                members_collection = get_team_members_collection(self.team_id)
                for member_id in self.created_data["members"]:
                    try:
                        await self.database.delete_document(members_collection, member_id)
                        logger.info(f"✅ Deleted test member: {member_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to delete member {member_id}: {e}")
                        cleanup_success = False
            
            # 3. Clean up invite links created during testing
            await self._cleanup_test_invite_links()
            
            # 4. Clean up test markers
            if self.created_data["test_data_markers"]:
                marker_collection = get_collection_name("test_markers")
                for marker_id in self.created_data["test_data_markers"]:
                    try:
                        await self.database.delete_document(marker_collection, marker_id)
                        logger.info(f"✅ Deleted test marker: {marker_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to delete marker {marker_id}: {e}")
            
            # 5. Reset tracking
            self.created_data = {
                "players": [],
                "members": [],
                "invite_links": [], 
                "test_data_markers": []
            }
            
            if cleanup_success:
                logger.info("✅ KTI test data cleanup completed successfully")
            else:
                logger.warning("⚠️ KTI test data cleanup completed with some errors")
                
            return cleanup_success
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup KTI test data: {e}")
            return False

    async def _cleanup_test_invite_links(self):
        """Clean up invite links created during testing"""
        try:
            invite_links_collection = get_collection_name(COLLECTION_INVITE_LINKS)
            
            # Query for invite links with test markers
            test_links = await self.database.query_documents(
                invite_links_collection,
                filters=[{"field": "test_marker", "operator": "==", "value": "FUNCTIONAL_TEST_DATA"}]
            )
            
            for link_doc in test_links:
                try:
                    await self.database.delete_document(invite_links_collection, link_doc["id"])
                    logger.info(f"✅ Deleted test invite link: {link_doc['id']}")
                except Exception as e:
                    logger.error(f"❌ Failed to delete invite link {link_doc['id']}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to cleanup test invite links: {e}")

    async def validate_test_data(self) -> Dict[str, bool]:
        """Validate that test data exists and is correct"""
        try:
            logger.info("🔍 Validating KTI test data...")
            validation_results = {
                "team_exists": False,
                "players_exist": False,
                "members_exist": False,
                "data_integrity": False
            }
            
            # 1. Validate team exists
            teams_collection = get_collection_name(COLLECTION_TEAMS)
            team_doc = await self.database.get_document(teams_collection, self.team_id)
            validation_results["team_exists"] = team_doc is not None
            
            # 2. Validate players exist
            players_collection = get_team_players_collection(self.team_id)
            players = await self.database.query_documents(
                players_collection,
                filters=[{"field": "test_marker", "operator": "==", "value": "FUNCTIONAL_TEST_DATA"}]
            )
            validation_results["players_exist"] = len(players) >= 2  # At least 2 test players
            
            # 3. Validate members exist  
            members_collection = get_team_members_collection(self.team_id)
            members = await self.database.query_documents(
                members_collection,
                filters=[{"field": "test_marker", "operator": "==", "value": "FUNCTIONAL_TEST_DATA"}]
            )
            validation_results["members_exist"] = len(members) >= 1  # At least 1 test member
            
            # 4. Validate data integrity
            validation_results["data_integrity"] = all([
                validation_results["team_exists"],
                validation_results["players_exist"], 
                validation_results["members_exist"]
            ])
            
            logger.info(f"✅ Test data validation: {validation_results}")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Failed to validate test data: {e}")
            return {"error": True, "message": str(e)}

    async def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of created test data"""
        try:
            summary = {
                "team_id": self.team_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "created_data": self.created_data.copy()
            }
            
            # Add detailed counts
            summary["counts"] = {
                "players": len(self.created_data["players"]),
                "members": len(self.created_data["members"]),
                "invite_links": len(self.created_data["invite_links"]),
                "markers": len(self.created_data["test_data_markers"])
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get test summary: {e}")
            return {"error": str(e)}

# Utility functions for direct script usage
async def setup_kti_test_data():
    """Setup KTI test data - can be called directly"""
    manager = KTITestDataManager()
    await manager.initialize()
    return await manager.setup_test_data()

async def cleanup_kti_test_data():
    """Cleanup KTI test data - can be called directly"""
    manager = KTITestDataManager()
    await manager.initialize()
    return await manager.cleanup_test_data()

async def validate_kti_test_data():
    """Validate KTI test data - can be called directly"""
    manager = KTITestDataManager()
    await manager.initialize()
    return await manager.validate_test_data()

if __name__ == "__main__":
    """Direct script execution for test data management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KTI Test Data Manager")
    parser.add_argument("action", choices=["setup", "cleanup", "validate"], 
                       help="Action to perform")
    args = parser.parse_args()
    
    async def main():
        if args.action == "setup":
            success = await setup_kti_test_data()
            print("✅ Test data setup successful" if success else "❌ Test data setup failed")
        elif args.action == "cleanup":
            success = await cleanup_kti_test_data()
            print("✅ Test data cleanup successful" if success else "❌ Test data cleanup failed")
        elif args.action == "validate":
            results = await validate_kti_test_data()
            print(f"📊 Validation results: {json.dumps(results, indent=2)}")
    
    asyncio.run(main())