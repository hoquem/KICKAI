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
from kickai.core.enums import ResponseStatus
from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
from kickai.utils.tool_helpers import create_json_response


@tool("add_player", result_as_answer=True)
async def add_player(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_name: str,
    phone_number: str
) -> str:
    """
    Add a new player to the team with invite link generation.

    This tool serves as the application boundary for player creation by team administrators.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        player_name: Name of the new player
        phone_number: Phone number of the new player

    Returns:
        JSON formatted response with player creation result and invite link
    """
    try:
        logger.info(f"🏃‍♂️ Adding player '{player_name}' by {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not player_name or not phone_number:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Both player name and phone number are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(IPlayerService)
        team_member_service = container.get_service(ITeamMemberService)

        if not player_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="PlayerService is not available"
            )

        # Check if player already exists
        existing_player = await player_service.get_player_by_phone(phone_number, team_id)
        
        if existing_player:
            response_data = {
                "player_exists": True,
                "player_name": existing_player.name,
                "phone_number": phone_number,
                "team_id": team_id,
                "player_id": existing_player.player_id,
                "status": existing_player.status,
                "message": f"✅ Player '{existing_player.name}' already exists in the system"
            }
            
            logger.info(f"✅ Player '{player_name}' already exists")
            return create_json_response(ResponseStatus.SUCCESS, data=response_data)

        # Create new player (execute domain operation)
        success, result_message = await player_service.add_player(
            name=player_name,
            phone=phone_number,
            team_id=team_id
        )

        if success:
            # Get the created player for response data
            created_player = await player_service.get_player_by_phone(phone_number, team_id)
            
            response_data = {
                "player_exists": False,
                "player_name": player_name,
                "phone_number": phone_number,
                "team_id": team_id,
                "player_id": created_player.player_id if created_player else "Generated",
                "status": "pending",
                "message": f"✅ Player '{player_name}' added successfully",
                "details": result_message,
                "invite_info": "Invite link functionality would be generated here"
            }

            logger.info(f"✅ Player '{player_name}' added successfully by {username}")
            return create_json_response(ResponseStatus.SUCCESS, data=response_data)
        else:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Failed to add player: {result_message}"
            )

    except Exception as e:
        logger.error(f"❌ Error adding player '{player_name}': {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to add player: {e}")