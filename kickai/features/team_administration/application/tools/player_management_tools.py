#!/usr/bin/env python3
"""
Player Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for player management by team administrators.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger
from kickai.core.dependency_container import get_container
from kickai.utils.tool_helpers import create_json_response, ResponseStatus


@tool("create_player")
async def create_player(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_name: str,
    phone_number: str
) -> str:
    """
    Create a new player in the team with invite link generation.

    This tool serves as the application boundary for player creation by team administrators.
    It delegates all business logic to the domain layer function.

    Args:
        telegram_id: Admin's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        player_name: Name of the new player
        phone_number: Phone number of the new player

    Returns:
        JSON formatted response with player creation result and invite link
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            player_name = params.get('player_name', '')
            phone_number = params.get('phone_number', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    from kickai.utils.tool_validation import create_tool_response
                    return create_tool_response(
                        False, 
                        "Invalid telegram_id format"
                    )

        logger.info(f"🏃‍♂️ Application layer: Creating player '{player_name}' by {username} ({telegram_id}) in team {team_id}")

        # Get services from container
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
        player_service = container.get_service(IPlayerService)
        
        # Create player using domain service
        from kickai.features.player_registration.domain.entities.player_create_params import PlayerCreateParams
        
        params = PlayerCreateParams(
            name=player_name,
            phone=phone_number,
            team_id=team_id,
            position="TBD"  # Default position
        )
        
        player = await player_service.create_player(params)
        
        return create_json_response(
            ResponseStatus.SUCCESS,
            f"Player '{player_name}' created successfully with ID: {player.player_id}",
            data={
                "player_id": player.player_id,
                "name": player.name,
                "phone": player.phone_number,
                "status": player.status.value if hasattr(player.status, 'value') else str(player.status)
            }
        )

    except Exception as e:
        logger.error(f"❌ Application layer error creating player '{player_name}': {e}")
        from kickai.utils.tool_validation import create_tool_response
        return create_tool_response(False, f"Failed to create player: {e}")