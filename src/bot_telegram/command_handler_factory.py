"""
Factory for creating command handlers with proper dependency injection.

This factory ensures that the presentation layer (commands) only depends on
interfaces, not concrete implementations.
"""

import logging
from typing import Optional

from .interfaces.command_handler_interface import ICommandHandler
from .command_handler_impl import CommandHandlerImpl

# Import service factories
from services.player_service import get_player_service
from services.team_service import get_team_service
from services.match_service import get_match_service
from services.payment_service import get_payment_service
from services.reminder_service import get_reminder_service
from services.daily_status_service import get_daily_status_service
from services.fa_registration_checker import get_fa_registration_checker
from services.expense_service import get_expense_service

logger = logging.getLogger(__name__)


class CommandHandlerFactory:
    """Factory for creating command handlers."""
    
    _instance: Optional[ICommandHandler] = None
    
    @classmethod
    def get_command_handler(cls, team_id: str) -> ICommandHandler:
        """Get or create a command handler instance."""
        if cls._instance is None:
            cls._instance = cls._create_command_handler(team_id)
        return cls._instance
    
    @classmethod
    def _create_command_handler(cls, team_id: str) -> ICommandHandler:
        """Create a new command handler instance with all dependencies."""
        try:
            # Get all service instances
            player_service = get_player_service(team_id=team_id)
            team_service = get_team_service(team_id=team_id)
            match_service = get_match_service()
            payment_service = get_payment_service(team_id=team_id)
            reminder_service = get_reminder_service()
            daily_status_service = get_daily_status_service()
            fa_registration_checker = get_fa_registration_checker()
            expense_service = get_expense_service()
            
            # Create command handler with all dependencies
            command_handler = CommandHandlerImpl(
                player_service=player_service,
                team_service=team_service,
                match_service=match_service,
                payment_service=payment_service,
                reminder_service=reminder_service,
                daily_status_service=daily_status_service,
                fa_registration_checker=fa_registration_checker,
                expense_service=expense_service
            )
            
            logger.info(f"✅ Command handler created for team {team_id}")
            return command_handler
            
        except Exception as e:
            logger.error(f"❌ Error creating command handler: {e}")
            raise RuntimeError(f"Failed to create command handler: {e}")
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        logger.info("🔄 Command handler factory reset")


# Convenience function for getting command handler
def get_command_handler(team_id: str) -> ICommandHandler:
    """Get the command handler instance with proper dependency injection."""
    # Get application layer services with team_id
    player_service = get_player_service(team_id=team_id)
    team_service = get_team_service(team_id=team_id)
    match_service = get_match_service()
    payment_service = get_payment_service(team_id=team_id)
    reminder_service = get_reminder_service()
    daily_status_service = get_daily_status_service()
    fa_registration_checker = get_fa_registration_checker()
    expense_service = get_expense_service()
    
    # Create the command handler implementation
    command_handler = CommandHandlerImpl(
        player_service=player_service,
        team_service=team_service,
        match_service=match_service,
        payment_service=payment_service,
        reminder_service=reminder_service,
        daily_status_service=daily_status_service,
        fa_registration_checker=fa_registration_checker,
        expense_service=expense_service
    )
    
    logger.info(f"✅ Command handler created for team {team_id}")
    return command_handler 