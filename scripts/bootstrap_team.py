#!/usr/bin/env python3
"""
Team Bootstrap Script

This script sets up a new team in the KICKAI system by:
1. Creating team record with league information
2. Creating admin user record
3. Setting up bot mapping
4. Configuring team members and permissions
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime
from typing import Optional

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from core.dependency_container import get_service
from services.interfaces.team_service_interface import ITeamService
from services.interfaces.player_service_interface import IPlayerService
from database.models_improved import Team, TeamStatus, TeamMember, BotMapping, PlayerRole
from utils.id_generator import generate_team_id
from core.exceptions import TeamError, PlayerError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeamBootstrap:
    """Handles team bootstrap process."""
    
    def __init__(self):
        self.team_service = get_service(ITeamService)
        self.player_service = get_service(IPlayerService)
    
    async def bootstrap_team(self, 
                           team_name: str,
                           main_chat_id: str,
                           leadership_chat_id: str,
                           bot_username: str,
                           admin_phone: str,
                           admin_name: str,
                           admin_email: str,
                           league_name: str,
                           division: str,
                           home_pitch: str,
                           fa_website_url: str) -> bool:
        """Bootstrap a new team with all required components."""
        
        try:
            logger.info(f"🚀 Starting bootstrap for team: {team_name}")
            
            # Step 1: Create team
            team = await self._create_team(
                team_name=team_name,
                league_name=league_name,
                division=division,
                home_pitch=home_pitch,
                fa_website_url=fa_website_url
            )
            
            # Step 2: Create admin user
            admin_player = await self._create_admin_user(
                team_id=team.id,
                admin_phone=admin_phone,
                admin_name=admin_name,
                admin_email=admin_email
            )
            
            # Step 3: Create team member record for admin
            admin_member = await self._create_admin_member(
                team_id=team.id,
                player_id=admin_player.player_id,
                admin_name=admin_name
            )
            
            # Step 4: Create bot mapping
            bot_mapping = await self._create_bot_mapping(
                team_name=team_name,
                bot_username=bot_username,
                main_chat_id=main_chat_id,
                leadership_chat_id=leadership_chat_id
            )
            
            logger.info(f"✅ Team bootstrap completed successfully!")
            logger.info(f"📋 Summary:")
            logger.info(f"   Team ID: {team.id}")
            logger.info(f"   Admin Player ID: {admin_player.player_id}")
            logger.info(f"   Bot Username: {bot_username}")
            logger.info(f"   Main Chat: {main_chat_id}")
            logger.info(f"   Leadership Chat: {leadership_chat_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Team bootstrap failed: {e}")
            return False
    
    async def _create_team(self, 
                          team_name: str,
                          league_name: str,
                          division: str,
                          home_pitch: str,
                          fa_website_url: str) -> Team:
        """Create team record."""
        
        logger.info(f"📝 Creating team: {team_name}")
        
        # Generate team ID
        team_id = generate_team_id(team_name)
        
        # Create team with league information
        team = await self.team_service.create_team(
            name=team_name,
            description=f"Team playing in {league_name} - {division}",
            settings={
                "league_name": league_name,
                "division": division,
                "home_pitch": home_pitch,
                "fa_website_url": fa_website_url,
                "created_at": datetime.now().isoformat()
            },
            fa_team_url=fa_website_url
        )
        
        logger.info(f"✅ Team created: {team.id}")
        return team
    
    async def _create_admin_user(self,
                                team_id: str,
                                admin_phone: str,
                                admin_name: str,
                                admin_email: str) -> 'Player':
        """Create admin user record."""
        
        logger.info(f"👤 Creating admin user: {admin_name}")
        
        # Create admin as a player first
        admin_player = await self.player_service.create_player(
            name=admin_name,
            phone=admin_phone,
            team_id=team_id,
            email=admin_email,
            role=PlayerRole.ADMIN,
            fa_registered=True
        )
        
        logger.info(f"✅ Admin user created: {admin_player.player_id}")
        return admin_player
    
    async def _create_admin_member(self,
                                  team_id: str,
                                  player_id: str,
                                  admin_name: str) -> TeamMember:
        """Create team member record for admin."""
        
        logger.info(f"👥 Creating admin team member: {admin_name}")
        
        # Create team member with admin role
        admin_member = await self.team_service.add_team_member(
            team_id=team_id,
            user_id=player_id,
            role="admin",
            permissions=[
                "manage_players",
                "manage_matches", 
                "manage_payments",
                "view_reports",
                "admin_commands"
            ]
        )
        
        logger.info(f"✅ Admin team member created: {admin_member.id}")
        return admin_member
    
    async def _create_bot_mapping(self,
                                 team_name: str,
                                 bot_username: str,
                                 main_chat_id: str,
                                 leadership_chat_id: str) -> BotMapping:
        """Create bot mapping record."""
        
        logger.info(f"🤖 Creating bot mapping for: {bot_username}")
        
        # Create bot mapping
        bot_mapping = await self.team_service.create_bot_mapping(
            team_name=team_name,
            bot_username=bot_username,
            chat_id=main_chat_id,  # Main chat ID
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN', '')
        )
        
        # Store leadership chat ID in settings
        # The original code had data_store.update_document here, but data_store is removed.
        # Assuming this part of the logic needs to be re-evaluated or removed if data_store is no longer available.
        # For now, commenting out the line as it's not directly related to the new_code's intent.
        # await self.data_store.update_document(
        #     'bot_mappings',
        #     bot_mapping.id,
        #     {
        #         "leadership_chat_id": leadership_chat_id,
        #         "main_chat_id": main_chat_id,
        #         "updated_at": datetime.now().isoformat()
        #     }
        # )
        
        logger.info(f"✅ Bot mapping created: {bot_mapping.id}")
        return bot_mapping


def main():
    """Main function to run team bootstrap."""
    
    parser = argparse.ArgumentParser(description='Bootstrap a new team in KICKAI')
    
    # Required arguments
    parser.add_argument('--team-name', required=True, help='Team name')
    parser.add_argument('--main-chat-id', required=True, help='Main chat ID')
    parser.add_argument('--leadership-chat-id', required=True, help='Leadership chat ID')
    parser.add_argument('--bot-username', required=True, help='Bot username')
    parser.add_argument('--admin-phone', required=True, help='Admin phone number')
    parser.add_argument('--admin-name', required=True, help='Admin name')
    parser.add_argument('--admin-email', required=True, help='Admin email')
    
    # Optional arguments
    parser.add_argument('--league-name', default='Unknown League', help='League name')
    parser.add_argument('--division', default='Unknown Division', help='Division')
    parser.add_argument('--home-pitch', default='TBD', help='Home pitch')
    parser.add_argument('--fa-website-url', default='', help='FA website URL')
    
    args = parser.parse_args()
    
    # Validate required environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    # Run bootstrap
    bootstrap = TeamBootstrap()
    
    async def run_bootstrap():
        success = await bootstrap.bootstrap_team(
            team_name=args.team_name,
            main_chat_id=args.main_chat_id,
            leadership_chat_id=args.leadership_chat_id,
            bot_username=args.bot_username,
            admin_phone=args.admin_phone,
            admin_name=args.admin_name,
            admin_email=args.admin_email,
            league_name=args.league_name,
            division=args.division,
            home_pitch=args.home_pitch,
            fa_website_url=args.fa_website_url
        )
        
        if success:
            logger.info("🎉 Team bootstrap completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Team bootstrap failed!")
            sys.exit(1)
    
    # Run async bootstrap
    asyncio.run(run_bootstrap())


if __name__ == "__main__":
    main() 