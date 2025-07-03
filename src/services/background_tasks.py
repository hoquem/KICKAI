#!/usr/bin/env python3
"""
Background Tasks Manager

This module manages background tasks like FA registration checks and daily status reports.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional

from src.core.logging import get_logger
from src.services.player_service import PlayerService
from src.services.team_service import TeamService
from src.services.team_member_service import TeamMemberService
from src.services.fa_registration_checker import run_fa_registration_check
from src.services.daily_status_service import start_daily_status_service
from src.core.bot_config_manager import get_bot_config_manager

logger = get_logger("background_tasks")

class BackgroundTaskManager:
    """Manages background tasks for the KICKAI system."""
    
    def __init__(self):
        self.tasks = []
        self.running = False
        
    async def start_fa_registration_checker(self, team_id: str, player_service: PlayerService) -> None:
        """
        Start the FA registration checker task.
        
        Args:
            team_id: The team ID to check
            player_service: Player service instance
        """
        while self.running:
            try:
                logger.info(f"🔍 Starting FA registration check for team {team_id}")
                
                # Run FA registration check
                updates = await run_fa_registration_check(team_id, player_service)
                
                if updates:
                    logger.info(f"✅ FA registration check found {len(updates)} updates")
                else:
                    logger.info("ℹ️ FA registration check completed - no updates found")
                
                # Wait 24 hours before next check
                await asyncio.sleep(24 * 60 * 60)  # 24 hours
                
            except Exception as e:
                logger.error(f"❌ Error in FA registration checker: {e}")
                # Wait 1 hour before retrying
                await asyncio.sleep(60 * 60)  # 1 hour
    
    async def start_daily_status_service(self, team_id: str, 
                                       player_service: PlayerService,
                                       team_service: TeamService,
                                       team_member_service: TeamMemberService,
                                       bot_token: str) -> None:
        """
        Start the daily status service.
        
        Args:
            team_id: The team ID to monitor
            player_service: Player service instance
            team_service: Team service instance
            team_member_service: Team member service instance
            bot_token: Telegram bot token
        """
        try:
            # Get leadership chat ID
            manager = get_bot_config_manager()
            bot_config = manager.get_bot_config(team_id)
            
            if not bot_config or not bot_config.leadership_chat_id:
                logger.error(f"❌ No leadership chat configured for team {team_id}")
                return
            
            logger.info(f"📊 Starting daily status service for team {team_id}")
            
            # Start the daily status service
            await start_daily_status_service(
                team_id=team_id,
                leadership_chat_id=bot_config.leadership_chat_id,
                player_service=player_service,
                team_service=team_service,
                team_member_service=team_member_service,
                bot_token=bot_token
            )
            
        except Exception as e:
            logger.error(f"❌ Error starting daily status service: {e}")
    
    async def start_all_background_tasks(self, team_id: str) -> None:
        """
        Start all background tasks for a team.
        
        Args:
            team_id: The team ID to start tasks for
        """
        try:
            self.running = True
            
            # Initialize services
            player_service = PlayerService()
            team_service = TeamService()
            from src.database.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
            team_member_service = TeamMemberService(firebase_client)
            
            # Get bot configuration
            manager = get_bot_config_manager()
            bot_config = manager.get_bot_config(team_id)
            
            if not bot_config:
                logger.error(f"❌ No bot configuration found for team {team_id}")
                return
            
            logger.info(f"🚀 Starting background tasks for team {team_id}")
            
            # Start FA registration checker
            fa_task = asyncio.create_task(
                self.start_fa_registration_checker(team_id, player_service)
            )
            self.tasks.append(fa_task)
            
            # Start daily status service
            status_task = asyncio.create_task(
                self.start_daily_status_service(
                    team_id, player_service, team_service, team_member_service, bot_config.token
                )
            )
            self.tasks.append(status_task)
            
            logger.info(f"✅ Background tasks started for team {team_id}")
            
            # Wait for all tasks to complete (they should run indefinitely)
            await asyncio.gather(*self.tasks)
            
        except Exception as e:
            logger.error(f"❌ Error starting background tasks: {e}")
        finally:
            self.running = False
    
    async def stop_all_tasks(self) -> None:
        """Stop all background tasks."""
        logger.info("🛑 Stopping all background tasks")
        self.running = False
        
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to be cancelled
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("✅ All background tasks stopped")


# Global background task manager instance
background_task_manager = BackgroundTaskManager()


async def start_background_tasks_for_team(team_id: str) -> None:
    """
    Start background tasks for a specific team.
    
    Args:
        team_id: The team ID to start tasks for
    """
    await background_task_manager.start_all_background_tasks(team_id)


async def stop_background_tasks() -> None:
    """Stop all background tasks."""
    await background_task_manager.stop_all_tasks() 