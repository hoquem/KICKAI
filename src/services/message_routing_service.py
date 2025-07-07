"""
Message Routing Service

This service provides centralized message routing logic using the Player model's
encapsulated methods as the single source of truth for all routing decisions.
"""

import logging
from typing import Optional, Tuple
from src.database.models_improved import Player, OnboardingStatus

logger = logging.getLogger(__name__)


class MessageRoutingService:
    """
    Centralized message routing service that uses Player model's encapsulated methods
    as the single source of truth for all routing decisions.
    """
    
    @staticmethod
    def should_route_to_onboarding(player: Optional[Player], message: str) -> Tuple[bool, str]:
        """
        Determine if a message should be routed to onboarding handler.
        
        Uses Player.is_pending_onboarding() as the single source of truth.
        
        Args:
            player: Player object with encapsulated status methods
            message: The message to route
            
        Returns:
            Tuple of (should_route, reason)
        """
        if not player:
            return False, "No player found"
        
        # Use Player model's encapsulated method as single source of truth
        if player.is_pending_onboarding():
            # Only route PENDING players to onboarding - IN_PROGRESS players can use general commands
            if player.onboarding_status == OnboardingStatus.PENDING:
                logger.info(f"[ROUTING] Player {player.name} is pending onboarding, routing to onboarding handler")
                return True, f"Player {player.name} is pending onboarding"
            else:
                logger.info(f"[ROUTING] Player {player.name} is in progress but not pending, allowing general commands")
                return False, f"Player {player.name} is in progress but can use general commands"
        
        logger.info(f"[ROUTING] Player {player.name} is not in onboarding, allowing general commands")
        return False, f"Player {player.name} is not in onboarding"
    
    @staticmethod
    def should_route_to_player_update(player: Optional[Player], message: str) -> Tuple[bool, str]:
        """
        Determine if a message should be routed to player update handler.
        
        Uses Player.is_onboarding_complete() as the single source of truth.
        
        Args:
            player: Player object with encapsulated status methods
            message: The message to route
            
        Returns:
            Tuple of (should_route, reason)
        """
        if not player:
            return False, "No player found"
        
        # Use Player model's encapsulated method as single source of truth
        if player.is_onboarding_complete():
            update_keywords = ['update', 'change', 'my', 'phone', 'emergency', 'contact', 'date', 'birth', 'dob', 'position']
            message_lower = message.lower()
            
            if any(keyword in message_lower for keyword in update_keywords):
                logger.info(f"[ROUTING] Completed player {player.name} requesting update, routing to player update handler")
                return True, f"Player {player.name} requesting update"
        
        return False, "Not a player update request"
    
    @staticmethod
    def should_route_to_general_handler(player: Optional[Player], message: str) -> Tuple[bool, str]:
        """
        Determine if a message should be routed to general handler.
        
        This is the default case when other routing conditions are not met.
        
        Args:
            player: Player object with encapsulated status methods
            message: The message to route
            
        Returns:
            Tuple of (should_route, reason)
        """
        if not player:
            return True, "No player found, routing to general handler"
        
        # Check if player should be routed elsewhere first
        should_onboard, _ = MessageRoutingService.should_route_to_onboarding(player, message)
        if should_onboard:
            return False, "Routed to onboarding"
        
        should_update, _ = MessageRoutingService.should_route_to_player_update(player, message)
        if should_update:
            return False, "Routed to player update"
        
        logger.info(f"[ROUTING] Player {player.name} message routed to general handler")
        return True, f"Player {player.name} message routed to general handler"
    
    @staticmethod
    def get_routing_decision(player: Optional[Player], message: str, user_role: str = "player") -> dict:
        """
        Get the complete routing decision for a message.
        
        This is the main method that should be used by all routing logic.
        It uses Player model's encapsulated methods as the single source of truth.
        
        Args:
            player: Player object with encapsulated status methods
            message: The message to route
            user_role: User's role (admin, player, etc.)
            
        Returns:
            Dictionary containing routing decision and metadata
        """
        # Admin users bypass all routing logic
        if user_role == 'admin':
            return {
                'route_to': 'general',
                'reason': 'Admin user',
                'player_status': 'admin',
                'should_onboard': False,
                'should_update': False
            }
        
        # Get routing decisions using encapsulated methods
        should_onboard, onboard_reason = MessageRoutingService.should_route_to_onboarding(player, message)
        should_update, update_reason = MessageRoutingService.should_route_to_player_update(player, message)
        should_general, general_reason = MessageRoutingService.should_route_to_general_handler(player, message)
        
        # Determine final routing decision
        if should_onboard:
            route_to = 'onboarding'
            reason = onboard_reason
        elif should_update:
            route_to = 'player_update'
            reason = update_reason
        else:
            route_to = 'general'
            reason = general_reason
        
        # Get player status using encapsulated method
        player_status = player.get_status_category() if player else 'unknown'
        
        logger.info(f"[ROUTING DECISION] Player: {player.name if player else 'None'}, "
                   f"Status: {player_status}, Route: {route_to}, Reason: {reason}")
        
        return {
            'route_to': route_to,
            'reason': reason,
            'player_status': player_status,
            'should_onboard': should_onboard,
            'should_update': should_update,
            'player': player
        }


# Global instance for easy access
message_routing_service = MessageRoutingService() 