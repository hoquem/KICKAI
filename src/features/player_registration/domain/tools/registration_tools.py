"""
Player registration tools for KICKAI system.

This module provides tools for player registration and team member management.
"""

import logging
from typing import Optional
from pydantic import BaseModel

from crewai.tools import tool
from features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
from core.dependency_container import get_container

logger = logging.getLogger(__name__)


class RegisterPlayerInput(BaseModel):
    """Input model for register_player tool."""
    player_name: str
    phone_number: str
    position: str
    team_id: Optional[str] = None


class TeamMemberRegistrationInput(BaseModel):
    """Input model for team_member_registration tool."""
    player_name: str
    phone_number: str
    position: str
    team_id: str


class RegistrationGuidanceInput(BaseModel):
    """Input model for registration_guidance tool."""
    user_id: str
    team_id: Optional[str] = None


@tool("register_player")
def register_player(player_name: str, phone_number: str, position: str, team_id: Optional[str] = None) -> str:
    """
    Register a new player. Requires: player_name, phone_number, position
    
    Args:
        player_name: The name of the player to register
        phone_number: The player's phone number
        position: The player's position
        team_id: Optional team ID for context
    
    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        registration_service = container.get_service(PlayerRegistrationService)
        
        if not registration_service:
            logger.error("❌ PlayerRegistrationService not available")
            return "❌ Registration service not available"
        
        # Register the player
        player = registration_service.register_player(player_name, phone_number, position, team_id)
        
        if player:
            logger.info(f"✅ Player registered: {player_name} ({position})")
            return f"✅ Player registered successfully: {player_name} ({position})"
        else:
            logger.error(f"❌ Failed to register player: {player_name}")
            return f"❌ Failed to register player: {player_name}"
        
    except Exception as e:
        logger.error(f"❌ Failed to register player: {e}")
        return f"❌ Failed to register player: {str(e)}"


@tool("team_member_registration")
def team_member_registration(player_name: str, phone_number: str, position: str, team_id: str) -> str:
    """
    Register a new team member. Requires: player_name, phone_number, position, team_id
    
    Args:
        player_name: The name of the player to register
        phone_number: The player's phone number
        position: The player's position
        team_id: The team ID to register the player for
    
    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        registration_service = container.get_service(PlayerRegistrationService)
        
        if not registration_service:
            logger.error("❌ PlayerRegistrationService not available")
            return "❌ Registration service not available"
        
        # Register the team member
        player = registration_service.register_team_member(player_name, phone_number, position, team_id)
        
        if player:
            logger.info(f"✅ Team member registered: {player_name} for team {team_id}")
            return f"✅ Team member registered successfully: {player_name} for team {team_id}"
        else:
            logger.error(f"❌ Failed to register team member: {player_name}")
            return f"❌ Failed to register team member: {player_name}"
        
    except Exception as e:
        logger.error(f"❌ Failed to register team member: {e}")
        return f"❌ Failed to register team member: {str(e)}"


@tool("registration_guidance")
def registration_guidance(user_id: str, team_id: Optional[str] = None) -> str:
    """
    Provide registration guidance to a user. Requires: user_id
    
    Args:
        user_id: The user ID to provide guidance to
        team_id: Optional team ID for context
    
    Returns:
        Registration guidance message
    """
    try:
        container = get_container()
        registration_service = container.get_service(PlayerRegistrationService)
        
        if not registration_service:
            logger.error("❌ PlayerRegistrationService not available")
            return "❌ Registration service not available"
        
        # Get registration guidance
        guidance = registration_service.get_registration_guidance(user_id, team_id)
        
        logger.info(f"✅ Registration guidance provided to user {user_id}")
        return guidance
        
    except Exception as e:
        logger.error(f"❌ Failed to provide registration guidance: {e}")
        return f"❌ Failed to provide registration guidance: {str(e)}" 