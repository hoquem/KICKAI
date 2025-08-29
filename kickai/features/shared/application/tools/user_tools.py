#!/usr/bin/env python3
"""
User Tools - Clean Architecture Application Layer

This module provides CrewAI tools for user management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.shared.domain.services.user_service import UserService, UserRepositoryInterface
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.tool_helpers import create_json_response
from kickai.utils.tool_validation import create_tool_response


# Adapter to bridge existing services to our user repository interface
class ExistingServicesUserRepository:
    """Adapter to make existing services work with user repository interface."""
    
    def __init__(self, player_service, team_service):
        self.player_service = player_service
        self.team_service = team_service
    
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str):
        """Get player by telegram ID."""
        return await self.player_service.get_player_by_telegram_id(telegram_id, team_id)
    
    async def get_team_member_by_telegram_id(self, telegram_id: int, team_id: str):
        """Get team member by telegram ID."""
        return await self.team_service.get_team_member_by_telegram_id(team_id, telegram_id)


@tool("get_user_status", result_as_answer=True)
async def get_user_status(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get user status and information by Telegram ID lookup.

    This tool serves as the application boundary for user status functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Telegram ID of the user to look up
        team_id: Team ID (required)
        username: Username of the requesting user (for logging)
        chat_type: Chat type context

    Returns:
        JSON formatted user status information or error message
    """
    try:
        # Validate required parameters at application boundary
        if not telegram_id or not team_id:
            return create_tool_response(
                False, 
                "Missing required parameters: telegram_id and team_id"
            )

        # Ensure telegram_id is integer
        if not isinstance(telegram_id, int):
            try:
                telegram_id = int(telegram_id)
            except (ValueError, TypeError):
                return create_tool_response(
                    False, 
                    f"Invalid Telegram ID format: {telegram_id}. Must be an integer."
                )

        logger.info(f"👤 User status request for {telegram_id} in team {team_id}")

        # Get domain services from container and delegate to domain functions
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service(TeamService)
        
        # Create repository adapter (temporary bridge pattern)
        user_repository = ExistingServicesUserRepository(player_service, team_service)
        
        # Get domain service (pure business logic)
        user_service = UserService(user_repository)

        # Execute pure business logic
        user_status = await user_service.get_user_status(telegram_id, team_id)
        formatted_message = user_service.format_user_status_message(user_status)

        # Prepare response data
        response_data = {
            "user_type": user_status.user_type,
            "telegram_id": user_status.telegram_id,
            "team_id": user_status.team_id,
            "name": user_status.name,
            "position": user_status.position,
            "role": user_status.role,
            "status": user_status.status,
            "is_admin": user_status.is_admin,
            "is_registered": user_status.is_registered,
            "formatted_message": formatted_message
        }

        logger.info(f"✅ User status retrieved for {telegram_id}: {user_status.user_type}")
        
        return create_tool_response(True, f"User status for {telegram_id}", response_data)

    except Exception as e:
        logger.error(f"❌ Error in get_user_status tool: {e}")
        return create_tool_response(False, "Failed to get user status")