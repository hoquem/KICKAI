#!/usr/bin/env python3
"""
Player Registration Tools - Clean Architecture Application Layer

This module provides CrewAI tools for player registration functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Dict, List, Any
from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
from kickai.utils.tool_helpers import create_json_response


@tool("approve_player", result_as_answer=True)
async def approve_player(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.

    This tool serves as the application boundary for player approval functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Telegram ID of the approving user
        team_id: Team ID (required) - available from context
        username: Username of the approving user
        chat_type: Chat type context
        player_id: The player ID to approve (M001MH format)

    Returns:
        JSON formatted approval result or error message
    """
    try:
        logger.info(f"🎯 Player approval request for {player_id} from {username} ({telegram_id}) in team {team_id}")

        if not player_id:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Player ID is required for approval"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation
        result = await player_service.approve_player(player_id, team_id)
        
        logger.info(f"✅ Player {player_id} approved successfully by {username}")
        
        return create_json_response(ResponseStatus.SUCCESS, data=result)

    except Exception as e:
        logger.error(f"❌ Error approving player {player_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to approve player: {e}")


def _create_player_status_data(player, telegram_id: int, team_id: str) -> dict:
    """Create standardized player status data structure."""
    return {
        "user_type": "Player",
        "telegram_id": telegram_id,
        "team_id": team_id,
        "name": player.name,
        "position": player.position,
        "status": player.status.title() if hasattr(player.status, 'title') else str(player.status),
        "player_id": player.player_id,
        "is_registered": True,
        "formatted_message": f"""👤 Player Information

📋 Name: {player.name or 'Not set'}
📱 Phone: {getattr(player, 'phone_number', 'Not set')}
⚽ Position: {player.position or 'Not set'}
🏷️ Player ID: {player.player_id or 'Not assigned'}
✅ Status: {player.status.title() if hasattr(player.status, 'title') else str(player.status)}
🏢 Team: {team_id}"""
    }


def _create_team_member_status_data(team_member, telegram_id: int, team_id: str) -> dict:
    """Create standardized team member status data structure."""
    return {
        "user_type": "Team Member",
        "telegram_id": telegram_id,
        "team_id": team_id,
        "name": team_member.name,
        "role": getattr(team_member, 'role', 'Member'),
        "is_admin": getattr(team_member, 'is_admin', False),
        "is_registered": True,
        "formatted_message": f"""👤 Team Member Information

📋 Name: {team_member.name or 'Not set'}
👑 Role: {getattr(team_member, 'role', 'Member')}
✅ Admin: {'Yes' if getattr(team_member, 'is_admin', False) else 'No'}
🏷️ Member ID: {getattr(team_member, 'member_id', 'Not assigned')}
✅ Status: {getattr(team_member, 'status', 'active').title()}
🏢 Team: {team_id}"""
    }


def _create_dual_role_status_data(player, team_member, telegram_id: int, team_id: str) -> dict:
    """Create standardized dual-role status data structure for users who are both players and team members."""
    return {
        "user_type": "Player & Team Member",
        "telegram_id": telegram_id,
        "team_id": team_id,
        "name": player.name or team_member.name,
        "has_player_role": True,
        "has_team_member_role": True,
        "is_registered": True,
        "formatted_message": f"""👤 Dual Role Information

📋 Name: {player.name or team_member.name or 'Not set'}
🏆 Player Role:
   • Position: {player.position or 'Not set'}
   • Player ID: {player.player_id or 'Not assigned'}
   • Status: {player.status.title() if hasattr(player.status, 'title') else str(player.status)}
   • Phone: {getattr(player, 'phone_number', 'Not set')}

👑 Team Member Role:
   • Role: {getattr(team_member, 'role', 'Member')}
   • Admin: {'Yes' if getattr(team_member, 'is_admin', False) else 'No'}
   • Member ID: {getattr(team_member, 'member_id', 'Not assigned')}
   • Status: {getattr(team_member, 'status', 'active').title()}

🏢 Team: {team_id}"""
    }


@tool("get_my_status", result_as_answer=True)
async def get_my_status(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get the current user's player or team member status based on chat context.
    
    Note: Only called for registered users - no need to handle unregistered cases.
    """
    try:
        logger.info(f"👤 Status request from {username} ({telegram_id}) in {chat_type} chat")

        # Get required services from container (application boundary)
        container = get_container()
        
        # Ensure container is initialized
        if not container._initialized:
            logger.warning("⚠️ Container not initialized, attempting to initialize...")
            try:
                await container.initialize()
                logger.info("✅ Container initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize container: {e}")
                return create_json_response(
                    ResponseStatus.ERROR, 
                    message="System initialization error. Please try again."
                )
        
        chat_type_normalized = chat_type.lower()
        
        if chat_type_normalized in ['main', 'main_chat']:
            # Main chat: Player status only
            logger.info(f"🏆 Checking player status for {username}")
            player_service = container.get_service(PlayerService)
            player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
            if player:
                return create_json_response(
                    ResponseStatus.SUCCESS, 
                    data=_create_player_status_data(player, telegram_id, team_id)
                )
                
        elif chat_type_normalized in ['leadership', 'leadership_chat']:
            # Leadership chat: Team member status only
            logger.info(f"👑 Checking team member status for {username}")
            team_member_service = container.get_service(TeamMemberService)
            if team_member_service:
                team_member = await team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)
                if team_member:
                    return create_json_response(
                        ResponseStatus.SUCCESS,
                        data=_create_team_member_status_data(team_member, telegram_id, team_id)
                    )
        elif chat_type_normalized in ['private', 'private_chat']:
            # Private chat: Check both player and team member status (user might have dual roles)
            logger.info(f"🔍 Checking both player and team member status for {username}")
            
            player_service = container.get_service(PlayerService)
            team_member_service = container.get_service(TeamMemberService)
            
            # Check both roles simultaneously
            player = None
            team_member = None
            
            if player_service:
                player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
            
            if team_member_service:
                team_member = await team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)
            
            # Determine which role to prioritize based on what we found
            if player and team_member:
                # User has both roles - show combined information
                logger.info(f"🎯 User {username} has both player and team member roles")
                
                # Show comprehensive dual-role information
                return create_json_response(
                    ResponseStatus.SUCCESS, 
                    data=_create_dual_role_status_data(player, team_member, telegram_id, team_id)
                )
                
            elif player:
                # User is only a player
                logger.info(f"🏆 User {username} found as player only")
                return create_json_response(
                    ResponseStatus.SUCCESS, 
                    data=_create_player_status_data(player, telegram_id, team_id)
                )
                
            elif team_member:
                # User is only a team member
                logger.info(f"👑 User {username} found as team member only")
                return create_json_response(
                    ResponseStatus.SUCCESS,
                    data=_create_team_member_status_data(team_member, telegram_id, team_id)
                )
            
            # If neither found, fall through to error case
            logger.warning(f"⚠️ User {username} not found in either player or team member collections")
        else:
            # If we reach here, user exists but not found in expected collections
            logger.warning(f"⚠️ Registered user {username} not found in expected collections")
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Unable to retrieve status information for {username}"
            )

    except Exception as e:
        logger.error(f"❌ Error getting status for {username}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get your status: {e}")


@tool("get_all_players", result_as_answer=True)
async def get_all_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all players for the team.

    This tool serves as the application boundary for player listing functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context

    Returns:
        JSON formatted list of all players
    """
    try:
        logger.info(f"📋 All players request from {username} ({telegram_id}) in team {team_id}")

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation
        players = await player_service.get_all_players(team_id)
        
        if not players:
            return create_json_response(
                ResponseStatus.SUCCESS, 
                data="No players found in the team."
            )

        # Format player list at application boundary
        formatted_players = []
        for player in players:
            player_data = {
                "name": player.name or "Unknown",
                "position": player.position or "Not specified",
                "status": player.status.title() if hasattr(player.status, 'title') else str(player.status),
                "player_id": player.player_id or "Not assigned",
                "phone_number": getattr(player, 'phone_number', 'Not provided')
            }
            formatted_players.append(player_data)

        # Create formatted message
        message_lines = ["🏆 Team Players", ""]
        for i, player in enumerate(formatted_players, 1):
            message_lines.append(f"{i}. {player['name']} ({player['position']})")
            message_lines.append(f"   🏷️ ID: {player['player_id']} | ✅ Status: {player['status']}")
            message_lines.append("")

        formatted_message = "\n".join(message_lines)
        
        response_data = {
            "players": formatted_players,
            "total_count": len(formatted_players),
            "formatted_message": formatted_message
        }

        logger.info(f"✅ Retrieved {len(formatted_players)} players for team {team_id}")
        return create_json_response(ResponseStatus.SUCCESS, data=response_data)

    except Exception as e:
        logger.error(f"❌ Error getting all players for team {team_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get players: {e}")


@tool("get_active_players", result_as_answer=True)
async def get_active_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all active players for the team.

    This tool serves as the application boundary for active player listing functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context

    Returns:
        JSON formatted list of active players
    """
    try:
        logger.info(f"🟢 Active players request from {username} ({telegram_id}) in team {team_id}")

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation
        active_players = await player_service.get_active_players(team_id)
        
        if not active_players:
            return create_json_response(
                ResponseStatus.SUCCESS, 
                data="No active players found in the team."
            )

        # Format active player list at application boundary
        formatted_players = []
        for player in active_players:
            player_data = {
                "name": player.name or "Unknown",
                "position": player.position or "Not specified",
                "status": "Active",
                "player_id": player.player_id or "Not assigned",
                "phone_number": getattr(player, 'phone_number', 'Not provided')
            }
            formatted_players.append(player_data)

        # Create formatted message
        message_lines = ["🟢 Active Players", ""]
        for i, player in enumerate(formatted_players, 1):
            message_lines.append(f"{i}. {player['name']} ({player['position']})")
            message_lines.append(f"   🏷️ ID: {player['player_id']} | 📱 Phone: {player['phone_number']}")
            message_lines.append("")

        formatted_message = "\n".join(message_lines)
        
        response_data = {
            "active_players": formatted_players,
            "total_count": len(formatted_players),
            "formatted_message": formatted_message
        }

        logger.info(f"✅ Retrieved {len(formatted_players)} active players for team {team_id}")
        return create_json_response(ResponseStatus.SUCCESS, data=response_data)

    except Exception as e:
        logger.error(f"❌ Error getting active players for team {team_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get active players: {e}")


@tool("get_player_match", result_as_answer=True)
async def get_player_match(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: str) -> str:
    """
    Get match information for a specific player.

    This tool serves as the application boundary for player match information functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        player_id: The player ID to get match info for

    Returns:
        JSON formatted match information for the player
    """
    try:
        logger.info(f"🏈 Match info request for player {player_id} from {username} ({telegram_id})")

        if not player_id:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Player ID is required to get match information"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation to get player
        player = await player_service.get_player_by_id(player_id, team_id)
        
        if not player:
            return create_json_response(
                ResponseStatus.ERROR, 
                message=f"Player {player_id} not found"
            )

        # For now, return basic player match-related info
        # This could be expanded to include actual match scheduling data
        match_info = {
            "player_id": player.player_id,
            "name": player.name,
            "position": player.position,
            "status": player.status.title() if hasattr(player.status, 'title') else str(player.status),
            "is_available_for_selection": player.status.lower() == "active" if player.status else False,
            "formatted_message": f"""🏈 Match Information for {player.name}

🏷️ Player ID: {player.player_id}
⚽ Position: {player.position or 'Not specified'}
✅ Status: {player.status.title() if hasattr(player.status, 'title') else str(player.status)}
🟢 Available for Selection: {'Yes' if player.status and player.status.lower() == 'active' else 'No'}

💡 Contact team management for specific match assignments."""
        }

        logger.info(f"✅ Retrieved match info for player {player_id}")
        return create_json_response(ResponseStatus.SUCCESS, data=match_info)

    except Exception as e:
        logger.error(f"❌ Error getting match info for player {player_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get match information: {e}")


# NOTE: list_team_members_and_players tool has been moved to team_administration module
# to avoid duplication and maintain clean architecture separation