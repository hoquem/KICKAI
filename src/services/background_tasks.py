#!/usr/bin/env python3
"""
Background Tasks Manager

This module manages background tasks like FA registration checks, daily status reports,
and automated onboarding reminders.
"""

import asyncio
from datetime import datetime
import logging

from core.settings import get_settings
from services.player_service import PlayerService
from services.team_service import TeamService
from services.team_member_service import TeamMemberService
from services.fa_registration_checker import run_fa_registration_check
from services.daily_status_service import start_daily_status_service
from services.reminder_service import get_reminder_service
from services.financial_report_service import start_financial_report_service

class BackgroundTaskManager:
    """Manages background tasks for the KICKAI system."""
    
    def __init__(self):
        self.tasks = []
        self.running = False
        
    async def start_fa_registration_checker(self, team_id: str, player_service: PlayerService, team_service: TeamService) -> None:
        """
        Start the FA registration checker task.
        
        Args:
            team_id: The team ID to check
            player_service: Player service instance
        """
        while self.running:
            try:
                logging.info(f"🔍 Starting FA registration check for team {team_id}")
                
                # Run FA registration check
                updates = await run_fa_registration_check(team_id, player_service, team_service)
                
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
            settings = get_settings()
            leadership_chat_id = settings.telegram_leadership_chat_id
            
            if not leadership_chat_id:
                logging.error(f"❌ No leadership chat configured for team {team_id}")
                return
            
            logging.info(f"📊 Starting daily status service for team {team_id}")
            
            # Start the daily status service
            await start_daily_status_service(
                team_id=team_id,
                leadership_chat_id=leadership_chat_id,
                player_service=player_service,
                team_service=team_service,
                team_member_service=team_member_service,
                bot_token=bot_token,
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
                
                # Get reminder service
                reminder_service = get_reminder_service(team_id)
                
                # Check and send reminders
                reminders_sent = await reminder_service.check_and_send_reminders()
                
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
                reminder_service = get_reminder_service(team_id)
                
                # Get all players
                players = await reminder_service.get_players_needing_reminders()
                
                cleanup_count = 0
                for player in players:
                    # If player has completed onboarding, reset reminder counters
                    if player.is_onboarding_complete():
                        await reminder_service.player_service.update_player(
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
            
            # Initialize services
            player_service = PlayerService()
            team_service = TeamService()
            from database.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
            team_member_service = TeamMemberService(firebase_client)
            
            # Get bot configuration
            settings = get_settings()
            bot_token = settings.telegram_bot_token
            
            if not bot_token:
                logging.error(f"❌ No bot configuration found for team {team_id}")
                return
            
            logging.info(f"🚀 Starting background tasks for team {team_id}")
            
            # Start FA registration checker
            fa_task = asyncio.create_task(
                self.start_fa_registration_checker(team_id, player_service, team_service)
            )
            self.tasks.append(fa_task)
            
            # Start daily status service
            status_task = asyncio.create_task(
                self.start_daily_status_service(
                    team_id, player_service, team_service, team_member_service, bot_token, settings
                )
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
            
            # Start financial report service
            financial_report_task = asyncio.create_task(
                start_financial_report_service(team_id, bot_token)
            )
            self.tasks.append(financial_report_task)

            logging.info(f"✅ Background tasks started for team {team_id}")
            logging.info("   📋 Active tasks:")
            logging.info("   • FA Registration Checker (24h interval)")
            logging.info("   • Daily Status Service (daily)")
            logging.info("   • Onboarding Reminder Service (6h interval)")
            logging.info("   • Reminder Cleanup Service (24h interval)")
            logging.info("   • Financial Report Service (configured interval)")
            logging.info("   • Financial Report Service (configured interval)")
            
            # Wait for all tasks to complete (they should run indefinitely)
            await asyncio.gather(*self.tasks)
            
        except Exception as e:
            logging.error(f"❌ Error starting background tasks: {e}")
        finally:
            self.running = False
    
    async def stop_all_tasks(self) -> None:
        """Stop all background tasks."""
        logging.info("🛑 Stopping all background tasks")
        self.running = False
        
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to be cancelled
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logging.info("✅ All background tasks stopped")
    
    async def get_task_status(self) -> dict:
        """Get status of all background tasks."""
        status = {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "active_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "task_details": []
        }
        
        for i, task in enumerate(self.tasks):
            task_status = {
                "task_id": i,
                "done": task.done(),
                "cancelled": task.cancelled(),
                "exception": None
            }
            
            if task.done():
                status["completed_tasks"] += 1
                try:
                    await task  # This will raise the exception if there was one
                except Exception as e:
                    task_status["exception"] = str(e)
                    status["failed_tasks"] += 1
            else:
                status["active_tasks"] += 1
            
            status["task_details"].append(task_status)
        
        return status


# Global background task manager instance
background_task_manager = BackgroundTaskManager()


def get_background_tasks_service() -> BackgroundTaskManager:
    """Get the global background tasks service instance."""
    return background_task_manager


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


async def get_background_task_status() -> dict:
    """Get status of background tasks."""
    return await background_task_manager.get_task_status()


async def start_reminder_service_only(team_id: str) -> None:
    """
    Start only the reminder service for testing purposes.
    
    Args:
        team_id: The team ID to start reminder service for
    """
    try:
        background_task_manager.running = True
        
        logging.info(f"⏰ Starting reminder service only for team {team_id}")
        
        # Start onboarding reminder service
        reminder_task = asyncio.create_task(
            background_task_manager.start_onboarding_reminder_service(team_id)
        )
        background_task_manager.tasks.append(reminder_task)
        
        # Start reminder cleanup service
        cleanup_task = asyncio.create_task(
            background_task_manager.start_reminder_cleanup_service(team_id)
        )
        background_task_manager.tasks.append(cleanup_task)
        
        logging.info(f"✅ Reminder services started for team {team_id}")
        
        # Wait for tasks to complete
        await asyncio.gather(*background_task_manager.tasks)
        
    except Exception as e:
        logging.error(f"❌ Error starting reminder service: {e}")
    finally:
        background_task_manager.running = False 