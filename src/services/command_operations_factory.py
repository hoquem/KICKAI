"""
Factory for creating command operations with proper dependency injection.

This factory creates adapters that wrap application layer services and injects them
into the domain implementation, maintaining clean architecture.
"""

from typing import Optional
import logging

from domain.interfaces.command_operations import ICommandOperations
from domain.command_operations_impl import CommandOperationsImpl
from domain.adapters import (
    PlayerOperationsAdapter,
    TeamOperationsAdapter,
    MatchOperationsAdapter,
    PaymentOperationsAdapter,
    UtilityOperationsAdapter
)

logger = logging.getLogger(__name__)

# Global instance for singleton pattern - now team-specific
_command_operations_instances: dict[str, ICommandOperations] = {}


def get_command_operations(team_id: Optional[str] = None) -> ICommandOperations:
    """Get the command operations instance for a team."""
    logger.info(f"[CommandOperationsFactory] get_command_operations called with team_id={team_id}")
    
    # Use default team if none provided
    if team_id is None:
        team_id = 'KAI'  # Default team
        logger.info(f"[CommandOperationsFactory] Using default team_id: {team_id}")
    
    # Check if we already have an instance for this team
    if team_id in _command_operations_instances:
        logger.info(f"[CommandOperationsFactory] Returning existing instance for team_id={team_id}")
        return _command_operations_instances[team_id]
    
    logger.info(f"[CommandOperationsFactory] Creating new instance for team_id={team_id}")
    
    try:
        logger.info(f"[CommandOperationsFactory] Creating adapters")
        
        # Create adapters
        logger.info(f"[CommandOperationsFactory] Creating PlayerOperationsAdapter")
        from services.player_service import get_player_service
        player_service = get_player_service(team_id=team_id)
        player_adapter = PlayerOperationsAdapter(player_service)
        
        logger.info(f"[CommandOperationsFactory] Creating TeamOperationsAdapter")
        from services.team_service import get_team_service
        team_service = get_team_service()
        team_adapter = TeamOperationsAdapter(team_service)
        
        logger.info(f"[CommandOperationsFactory] Creating MatchOperationsAdapter")
        from services.match_service import get_match_service
        match_service = get_match_service()
        match_adapter = MatchOperationsAdapter(match_service)
        
        logger.info(f"[CommandOperationsFactory] Creating PaymentOperationsAdapter")
        from services.payment_service import get_payment_service
        payment_service = get_payment_service()
        payment_adapter = PaymentOperationsAdapter(payment_service)
        
        logger.info(f"[CommandOperationsFactory] Creating UtilityOperationsAdapter")
        from services.team_member_service import get_team_member_service
        from services.fa_registration_checker import get_fa_registration_checker
        from services.daily_status_service import get_daily_status_service
        from services.background_tasks import get_background_tasks_service
        from services.reminder_service import get_reminder_service
        from core.settings import get_settings
        
        team_member_service = get_team_member_service(team_id=team_id)
        fa_registration_checker = get_fa_registration_checker()
        daily_status_service = get_daily_status_service(team_id=team_id)
        background_tasks_service = get_background_tasks_service()
        reminder_service = get_reminder_service(team_id=team_id)
        settings = get_settings()
        
        utility_adapter = UtilityOperationsAdapter(
            fa_registration_checker=fa_registration_checker,
            daily_status_service=daily_status_service,
            background_tasks_service=background_tasks_service,
            reminder_service=reminder_service,
            team_member_service=team_member_service,
            bot_config_manager=settings
        )
        
        logger.info(f"[CommandOperationsFactory] Creating CommandOperationsImpl")
        # Create the implementation
        command_ops = CommandOperationsImpl(
            player_adapter=player_adapter,
            team_adapter=team_adapter,
            match_adapter=match_adapter,
            payment_adapter=payment_adapter,
            utility_adapter=utility_adapter
        )
        
        logger.info(f"[CommandOperationsFactory] Storing instance for team_id={team_id}")
        # Store the instance
        _command_operations_instances[team_id] = command_ops
        
        logger.info(f"[CommandOperationsFactory] Successfully created and stored instance for team_id={team_id}")
        return command_ops
        
    except Exception as e:
        logger.error(f"[CommandOperationsFactory] Error creating command operations: {e}", exc_info=True)
        raise


def reset_command_operations():
    """Reset the singleton instance (useful for testing)."""
    global _command_operations_instance
    _command_operations_instance = None
    logger.info("🔄 Command operations factory reset") 