#!/usr/bin/env python3
"""
Team Setup Verification Script

This script verifies that a team was set up correctly by checking:
1. Team record exists
2. Admin user exists
3. Bot mapping exists
4. Database connectivity
"""

import os
import sys
import argparse
import asyncio
import logging
from typing import Optional

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from database.firebase_client import get_firebase_client
from features.team_administration.domain.services.team_service import TeamService
from features.player_registration.domain.services.player_service import PlayerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeamSetupVerifier:
    """Verifies team setup completeness."""
    
    def __init__(self):
        self.data_store = get_firebase_client()
        self.team_service = TeamService(data_store=self.data_store)
        self.player_service = PlayerService(data_store=self.data_store)
    
    async def verify_team_setup(self, team_name: str) -> bool:
        """Verify complete team setup."""
        
        logger.info(f"🔍 Verifying team setup for: {team_name}")
        
        try:
            # Step 1: Verify team exists
            team = await self._verify_team(team_name)
            if not team:
                return False
            
            # Step 2: Verify admin user exists
            admin = await self._verify_admin_user(team.id)
            if not admin:
                return False
            
            # Step 3: Verify bot mapping exists
            bot_mapping = await self._verify_bot_mapping(team_name)
            if not bot_mapping:
                return False
            
            # Step 4: Verify database connectivity
            db_ok = await self._verify_database_connectivity()
            if not db_ok:
                return False
            
            logger.info(f"✅ All verifications passed for team: {team_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    async def _verify_team(self, team_name: str) -> Optional['Team']:
        """Verify team record exists."""
        
        logger.info(f"📝 Verifying team record: {team_name}")
        
        try:
            team = await self.team_service.get_team_by_name(team_name)
            if team:
                logger.info(f"✅ Team found: {team.id}")
                logger.info(f"   League: {team.settings.get('league_name', 'Unknown')}")
                logger.info(f"   Division: {team.settings.get('division', 'Unknown')}")
                logger.info(f"   Home Pitch: {team.settings.get('home_pitch', 'Unknown')}")
                return team
            else:
                logger.error(f"❌ Team not found: {team_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error verifying team: {e}")
            return None
    
    async def _verify_admin_user(self, team_id: str) -> Optional['Player']:
        """Verify admin user exists."""
        
        logger.info(f"👤 Verifying admin user for team: {team_id}")
        
        try:
            # Get team members
            members = await self.team_service.get_team_members(team_id)
            
            # Find admin member
            admin_member = None
            for member in members:
                if member.role == "admin":
                    admin_member = member
                    break
            
            if admin_member:
                # Get admin player details
                admin_player = await self.player_service.get_player_by_id(admin_member.user_id)
                if admin_player:
                    logger.info(f"✅ Admin user found: {admin_player.name}")
                    logger.info(f"   Phone: {admin_player.phone}")
                    logger.info(f"   Email: {admin_player.email}")
                    logger.info(f"   Role: {admin_player.role.value}")
                    return admin_player
                else:
                    logger.error(f"❌ Admin player not found: {admin_member.user_id}")
                    return None
            else:
                logger.error(f"❌ No admin member found for team: {team_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error verifying admin user: {e}")
            return None
    
    async def _verify_bot_mapping(self, team_name: str) -> Optional['BotMapping']:
        """Verify bot mapping exists."""
        
        logger.info(f"🤖 Verifying bot mapping for team: {team_name}")
        
        try:
            bot_mapping = await self.team_service.get_bot_mapping_by_team_name(team_name)
            if bot_mapping:
                logger.info(f"✅ Bot mapping found: {bot_mapping.bot_username}")
                logger.info(f"   Main Chat ID: {bot_mapping.chat_id}")
                logger.info(f"   Leadership Chat ID: {bot_mapping.settings.get('leadership_chat_id', 'Unknown')}")
                return bot_mapping
            else:
                logger.error(f"❌ Bot mapping not found for team: {team_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error verifying bot mapping: {e}")
            return None
    
    async def _verify_database_connectivity(self) -> bool:
        """Verify database connectivity."""
        
        logger.info(f"🗄️ Verifying database connectivity")
        
        try:
            # Test basic database operations
            await self.data_store.get_collection('teams')
            logger.info(f"✅ Database connectivity verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connectivity failed: {e}")
            return False


def main():
    """Main function to run team verification."""
    
    parser = argparse.ArgumentParser(description='Verify team setup in KICKAI')
    parser.add_argument('--team-name', required=True, help='Team name to verify')
    
    args = parser.parse_args()
    
    # Run verification
    verifier = TeamSetupVerifier()
    
    async def run_verification():
        success = await verifier.verify_team_setup(args.team_name)
        
        if success:
            logger.info("🎉 Team setup verification completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Team setup verification failed!")
            sys.exit(1)
    
    # Run async verification
    asyncio.run(run_verification())


if __name__ == "__main__":
    main() 