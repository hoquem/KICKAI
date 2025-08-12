#!/usr/bin/env python3
"""
User Tools

This module provides tools for user management operations.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.validation_utils import (
    validate_team_id,
)


@tool("get_user_status")
def get_user_status(telegram_id: int, team_id: str) -> str:
    """
    Get the status of a user (player or team member).

    :param telegram_id: Telegram ID of the user (required) - available from context
    :type telegram_id: int
    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :return: JSON response with user status information
    :rtype: str
    """
    try:
        # Validate inputs

        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'telegram_id': telegram_id, 'team_id': team_id}


        # Get services
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service(TeamService)

        if not player_service or not team_service:
            return json_error(message="Required services are not available", error_type="Service unavailable")

        # Check if user is a player
        player = player_service.get_player_by_telegram_id_sync(telegram_id, team_id)
        if player:
            data = {
                'user_type': 'player',
                'telegram_id': telegram_id,
                'team_id': team_id,
                'player_info': {
                    'name': player.name,
                    'position': player.position,
                    'status': player.status,
                    'player_id': player.player_id
                }
            }

            ui_format = f"👤 **Player Status**\n\n📱 **Telegram ID**: {telegram_id}\n🏆 **Team ID**: {team_id}\n📋 **Name**: {player.name}\n⚽ **Position**: {player.position}\n📊 **Status**: {player.status.title()}"

            return json_response(data=data, ui_format=ui_format)

        # Check if user is a team member
        team_member = team_service.get_team_member_by_telegram_id_sync(team_id, telegram_id)
        if team_member:
            data = {
                'user_type': 'team_member',
                'telegram_id': telegram_id,
                'team_id': team_id,
                'member_info': {
                    'name': team_member.name,
                    'role': team_member.role,
                    'is_admin': team_member.is_admin,
                    'member_id': team_member.member_id
                }
            }

            ui_format = f"👔 **Team Member Status**\n\n📱 **Telegram ID**: {telegram_id}\n🏆 **Team ID**: {team_id}\n📋 **Name**: {team_member.name}\n👑 **Role**: {team_member.role.title()}\n✅ **Admin**: {'Yes' if team_member.is_admin else 'No'}"

            return json_response(data=data, ui_format=ui_format)

        # User not found
        data = {
            'user_type': 'not_registered',
            'telegram_id': telegram_id,
            'team_id': team_id,
            'message': 'User is not registered as a player or team member'
        }

        ui_format = f"❌ **User Not Registered**\n\n📱 **Telegram ID**: {telegram_id}\n🏆 **Team ID**: {team_id}\nℹ️ **Info**: User is not registered as a player or team member"

        return json_response(data=data, ui_format=ui_format)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_user_status: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to get user status: {e}")
        return json_error(message=f"Failed to get user status: {e}", error_type="Operation failed")
