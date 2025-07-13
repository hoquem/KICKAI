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
from core.dependency_container import get_service
from services.interfaces.player_service_interface import IPlayerService
from services.interfaces.team_service_interface import ITeamService
from services.interfaces.match_service_interface import IMatchService
from services.interfaces.payment_service_interface import IPaymentService
from services.interfaces.team_member_service_interface import ITeamMemberService
from services.interfaces.fa_registration_checker_interface import IFARegistrationChecker
from services.interfaces.daily_status_service_interface import IDailyStatusService
from services.interfaces.background_tasks_service_interface import IBackgroundTasksService
from services.interfaces.reminder_service_interface import IReminderService
from core.settings import get_settings

logger = logging.getLogger(__name__)


def get_command_operations(team_id: Optional[str] = None) -> ICommandOperations:
    """Get the command operations instance for a team."""
    logger.info(f"[CommandOperationsFactory] get_command_operations called with team_id={team_id}")
    
    # Use default team if none provided
    if team_id is None:
        team_id = 'KAI'  # Default team
        logger.info(f"[CommandOperationsFactory] Using default team_id: {team_id}")
    
    # Use dependency container for all services
    player_service = get_service(IPlayerService)
    team_service = get_service(ITeamService)
    match_service = get_service(IMatchService)
    payment_service = get_service(IPaymentService)
    team_member_service = get_service(ITeamMemberService)
    fa_registration_checker = get_service(IFARegistrationChecker)
    daily_status_service = get_service(IDailyStatusService)
    background_tasks_service = get_service(IBackgroundTasksService)
    reminder_service = get_service(IReminderService)
    settings = get_settings()
    
    player_adapter = PlayerOperationsAdapter(player_service)
    team_adapter = TeamOperationsAdapter(team_service)
    match_adapter = MatchOperationsAdapter(match_service)
    payment_adapter = PaymentOperationsAdapter(payment_service)
    utility_adapter = UtilityOperationsAdapter(
        fa_registration_checker=fa_registration_checker,
        daily_status_service=daily_status_service,
        background_tasks_service=background_tasks_service,
        reminder_service=reminder_service,
        team_member_service=team_member_service,
        bot_config_manager=settings
    )
    
    command_ops = CommandOperationsImpl(
        player_adapter=player_adapter,
        team_adapter=team_adapter,
        match_adapter=match_adapter,
        payment_adapter=payment_adapter,
        utility_adapter=utility_adapter
    )
    
    return command_ops


def reset_command_operations():
    """Reset the singleton instance (useful for testing)."""
    global _command_operations_instance
    _command_operations_instance = None
    logger.info("🔄 Command operations factory reset") 