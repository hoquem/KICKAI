"""
Factory for creating command operations with proper dependency injection.

This factory creates adapters that wrap application layer services and injects them
into the domain implementation, maintaining clean architecture.
"""

from typing import Optional
import logging

from src.domain.interfaces.command_operations import ICommandOperations
from src.domain.command_operations_impl import CommandOperationsImpl
from src.domain.adapters import (
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
        from src.services.player_service import get_player_service
        player_service = get_player_service(team_id=team_id)
        player_adapter = PlayerOperationsAdapter(player_service)
        
        logger.info(f"[CommandOperationsFactory] Creating TeamOperationsAdapter")
        from src.services.team_service import get_team_service
        team_service = get_team_service()
        team_adapter = TeamOperationsAdapter(team_service)
        
        logger.info(f"[CommandOperationsFactory] Creating MatchOperationsAdapter")
        from src.services.match_service import get_match_service
        match_service = get_match_service()
        match_adapter = MatchOperationsAdapter(match_service)
        
        logger.info(f"[CommandOperationsFactory] Creating PaymentOperationsAdapter")
        from src.services.payment_service import get_payment_service
        payment_service = get_payment_service()
        payment_adapter = PaymentOperationsAdapter(payment_service)
        
        logger.info(f"[CommandOperationsFactory] Creating UtilityOperationsAdapter")
        utility_adapter = UtilityOperationsAdapter()
        
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