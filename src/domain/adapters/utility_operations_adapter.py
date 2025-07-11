"""
Application layer adapter for utility operations.

This adapter implements the domain interface by wrapping the application layer services.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class UtilityOperationsAdapter:
    """Adapter that wraps utility services to implement domain interface."""
    
    def __init__(self, fa_registration_checker=None, daily_status_service=None, 
                 background_tasks_service=None, reminder_service=None, 
                 team_member_service=None, bot_config_manager=None):
        self.fa_registration_checker = fa_registration_checker
        self.daily_status_service = daily_status_service
        self.background_tasks_service = background_tasks_service
        self.reminder_service = reminder_service
        self.team_member_service = team_member_service
        self.settings = bot_config_manager  # Now using settings instead of bot_config_manager
        self.logger = logging.getLogger(__name__)

    async def check_fa_registration(self, player_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[UtilityOperationsAdapter] check_fa_registration called with player_id={player_id}, team_id={team_id}")
        try:
            if self.fa_registration_checker:
                result = await self.fa_registration_checker.check_registration(player_id, team_id)
                self.logger.info(f"[UtilityOperationsAdapter] check_fa_registration result: {result}")
                return result
            else:
                return False, "FA registration checker not available"
        except Exception as e:
            self.logger.error(f"Error checking FA registration: {e}", exc_info=True)
            return False, f"Error checking FA registration: {str(e)}"

    async def get_daily_status(self, team_id: str) -> str:
        self.logger.info(f"[UtilityOperationsAdapter] get_daily_status called with team_id={team_id}")
        try:
            if self.daily_status_service:
                result = await self.daily_status_service.get_daily_status(team_id)
                self.logger.info(f"[UtilityOperationsAdapter] get_daily_status result: {result}")
                return result
            else:
                return "Daily status service not available"
        except Exception as e:
            self.logger.error(f"Error getting daily status: {e}", exc_info=True)
            return f"Error getting daily status: {str(e)}"

    async def run_background_tasks(self, team_id: str) -> str:
        self.logger.info(f"[UtilityOperationsAdapter] run_background_tasks called with team_id={team_id}")
        try:
            if self.background_tasks_service:
                result = await self.background_tasks_service.run_tasks(team_id)
                self.logger.info(f"[UtilityOperationsAdapter] run_background_tasks result: {result}")
                return result
            else:
                return "Background tasks service not available"
        except Exception as e:
            self.logger.error(f"Error running background tasks: {e}", exc_info=True)
            return f"Error running background tasks: {str(e)}"

    async def send_reminder(self, message: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[UtilityOperationsAdapter] send_reminder called with message={message}, team_id={team_id}")
        try:
            if self.reminder_service:
                result = await self.reminder_service.send_reminder(message, team_id)
                self.logger.info(f"[UtilityOperationsAdapter] send_reminder result: {result}")
                return result
            else:
                return False, "Reminder service not available"
        except Exception as e:
            self.logger.error(f"Error sending reminder: {e}", exc_info=True)
            return False, f"Error sending reminder: {str(e)}"

    async def generate_invitation(self, identifier: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[UtilityOperationsAdapter] generate_invitation called with identifier={identifier}, team_id={team_id}")
        try:
            if self.team_member_service:
                result = await self.team_member_service.generate_invitation(identifier, team_id)
                self.logger.info(f"[UtilityOperationsAdapter] generate_invitation result: {result}")
                return result
            else:
                return False, "Team member service not available"
        except Exception as e:
            self.logger.error(f"Error generating invitation: {e}", exc_info=True)
            return False, f"Error generating invitation: {str(e)}"

    async def broadcast_message(self, message: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[UtilityOperationsAdapter] broadcast_message called with message={message}, team_id={team_id}")
        try:
            if self.team_member_service:
                result = await self.team_member_service.broadcast_message(message, team_id)
                self.logger.info(f"[UtilityOperationsAdapter] broadcast_message result: {result}")
                return result
            else:
                return False, "Team member service not available"
        except Exception as e:
            self.logger.error(f"Error broadcasting message: {e}", exc_info=True)
            return False, f"Error broadcasting message: {str(e)}"

    async def announce(self, message: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[UtilityOperationsAdapter] announce called with message={message}, team_id={team_id}")
        try:
            if self.team_member_service:
                result = await self.team_member_service.announce(message, team_id)
                self.logger.info(f"[UtilityOperationsAdapter] announce result: {result}")
                return result
            else:
                return False, "Team member service not available"
        except Exception as e:
            self.logger.error(f"Error announcing: {e}", exc_info=True)
            return False, f"Error announcing: {str(e)}"

    async def get_user_role(self, user_id: str, team_id: str) -> str:
        self.logger.info(f"[UtilityOperationsAdapter] get_user_role called with user_id={user_id}, team_id={team_id}")
        try:
            if self.team_member_service:
                result = await self.team_member_service.get_user_role(user_id, team_id)
                self.logger.info(f"[UtilityOperationsAdapter] get_user_role result: {result}")
                return result
            else:
                return "Team member service not available"
        except Exception as e:
            self.logger.error(f"Error getting user role: {e}", exc_info=True)
            return f"Error getting user role: {str(e)}" 