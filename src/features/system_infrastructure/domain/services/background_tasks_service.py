#!/usr/bin/env python3
"""
Background Tasks Service for KICKAI

This service manages long-running background tasks like:
- FA registration checking
- Daily status reports
- Onboarding reminders
- Financial reports
"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from database.interfaces import DataStoreInterface
from features.player_registration.domain.interfaces.player_service_interface import IPlayerService
from features.team_administration.domain.interfaces.team_service_interface import ITeamService
from features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
from features.communication.domain.interfaces.reminder_service_interface import IReminderService
from features.communication.domain.interfaces.daily_status_service_interface import IDailyStatusService
from core.settings import get_settings

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manages background tasks for the KICKAI system."""
    
    def __init__(self, 
                 data_store: DataStoreInterface,
                 player_service: IPlayerService,
                 team_service: ITeamService,
                 team_member_service: ITeamMemberService,
                 reminder_service: IReminderService,
                 daily_status_service: IDailyStatusService):
        self.data_store = data_store
        self.player_service = player_service
        self.team_service = team_service
        self.team_member_service = team_member_service
        self.reminder_service = reminder_service
        self.daily_status_service = daily_status_service
        self.running = False
        self.tasks: List[asyncio.Task] = []
        
    async def start_fa_registration_checker(self, team_id: str) -> None:
        """
        Start the FA registration checker task.
        
        Args:
            team_id: The team ID to check
        """
        while self.running:
            try:
                logging.info(f"🔍 Starting FA registration check for team {team_id}")
                
                # Run FA registration check
                updates = await self.fa_registration_checker.run_fa_registration_check(team_id)
                
                if updates:
                    logging.info(f"✅ FA registration check found {len(updates)} updates")
                else:
                    logging.info("ℹ️ FA registration check completed - no updates found")
                
                # Wait 24 hours before next check
                await asyncio.sleep(24 * 60 * 60)  # 24 hours
                
            except Exception as e:
                logging.error(f"❌ Error in FA registration checker: {e}")
                # Wait 1 hour before retrying
                await asyncio.sleep(60 * 60)  # 1 hour
    
    async def start_daily_status_service(self, team_id: str) -> None:
        """
        Start the daily status service.
        
        Args:
            team_id: The team ID to monitor
        """
        try:
            # Get leadership chat ID
            settings = get_settings()
            leadership_chat_id = settings.telegram_leadership_chat_id
            
            if not leadership_chat_id:
                logging.error(f"❌ No leadership chat configured for team {team_id}")
                return
            
            logging.info(f"📊 Starting daily status service for team {team_id}")
            
            # Start the daily status service
            await self.daily_status_service.start_daily_status_service(
                team_id=team_id,
                leadership_chat_id=leadership_chat_id,
                player_service=self.player_service,
                team_service=self.team_service,
                team_member_service=self.team_member_service,
                bot_token=settings.telegram_bot_token,
                bot_config_manager=settings
            )
            
        except Exception as e:
            logging.error(f"❌ Error starting daily status service: {e}")
    
    async def start_onboarding_reminder_service(self, team_id: str) -> None:
        """
        Start the onboarding reminder service.
        
        This service checks for players who need reminders and sends them automatically.
        
        Args:
            team_id: The team ID to monitor
        """
        while self.running:
            try:
                logging.info(f"⏰ Starting onboarding reminder check for team {team_id}")
                
                # Check and send reminders
                reminders_sent = await self.reminder_service.check_and_send_reminders(team_id)
                
                if reminders_sent:
                    logging.info(f"✅ Sent {len(reminders_sent)} onboarding reminders")
                    for reminder in reminders_sent:
                        logging.info(f"   📢 Reminder sent to {reminder.player_id} (reminder #{reminder.reminder_number})")
                else:
                    logging.info("ℹ️ No reminders needed at this time")
                
                # Wait 6 hours before next check (reminders are typically sent every 24 hours)
                # But we check more frequently to catch players who need reminders
                await asyncio.sleep(6 * 60 * 60)  # 6 hours
                
            except Exception as e:
                logging.error(f"❌ Error in onboarding reminder service: {e}")
                # Wait 1 hour before retrying
                await asyncio.sleep(60 * 60)  # 1 hour
    
    async def start_reminder_cleanup_service(self, team_id: str) -> None:
        """
        Start the reminder cleanup service.
        
        This service cleans up old reminder data and resets reminder counters
        for players who have completed onboarding.
        
        Args:
            team_id: The team ID to monitor
        """
        while self.running:
            try:
                logging.info(f"🧹 Starting reminder cleanup for team {team_id}")
                
                # Get reminder service
                players_needing_reminders = await self.reminder_service.get_players_needing_reminders(team_id)
                
                cleanup_count = 0
                for player in players_needing_reminders:
                    # If player has completed onboarding, reset reminder counters
                    if player.is_onboarding_complete():
                        await self.reminder_service.update_player(
                            player.id,
                            reminders_sent=0,
                            last_reminder_sent=None,
                            next_reminder_due=None
                        )
                        cleanup_count += 1
                
                if cleanup_count > 0:
                    logging.info(f"✅ Cleaned up reminder data for {cleanup_count} completed players")
                else:
                    logging.info("ℹ️ No cleanup needed")
                
                # Run cleanup once per day
                await asyncio.sleep(24 * 60 * 60)  # 24 hours
                
            except Exception as e:
                logging.error(f"❌ Error in reminder cleanup service: {e}")
                # Wait 6 hours before retrying
                await asyncio.sleep(6 * 60 * 60)  # 6 hours
    
    async def start_all_background_tasks(self, team_id: str) -> None:
        """
        Start all background tasks for a team.
        
        Args:
            team_id: The team ID to start tasks for
        """
        try:
            self.running = True
            
            logging.info(f"🚀 Starting background tasks for team {team_id}")
            
            # Start FA registration checker
            fa_task = asyncio.create_task(
                self.start_fa_registration_checker(team_id)
            )
            self.tasks.append(fa_task)
            
            # Start daily status service
            status_task = asyncio.create_task(
                self.start_daily_status_service(team_id)
            )
            self.tasks.append(status_task)
            
            # Start onboarding reminder service
            reminder_task = asyncio.create_task(
                self.start_onboarding_reminder_service(team_id)
            )
            self.tasks.append(reminder_task)
            
            # Start reminder cleanup service
            cleanup_task = asyncio.create_task(
                self.start_reminder_cleanup_service(team_id)
            )
            self.tasks.append(cleanup_task)
            
        except Exception as e:
            logging.error(f"❌ Error starting background tasks: {e}")
    
    async def stop_all_tasks(self) -> None:
        """
        Stop all running background tasks.
        """
        self.running = False
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        logging.info("🛑 All background tasks stopped")
    
    async def get_task_status(self) -> dict:
        """
        Get the status of all background tasks.
        """
        return {
            'running': self.running,
            'task_count': len(self.tasks)
        } 