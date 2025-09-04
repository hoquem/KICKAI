#!/usr/bin/env python3
"""
Status Tools - Clean Architecture Application Layer (CrewAI Semantic Update)

This module provides CrewAI tools for user status functionality with semantic naming.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.interfaces.player_service_interface import (
    IPlayerService,
)
from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
    ITeamMemberService,
)
from kickai.utils.native_crewai_helpers import validate_required_strings


@tool("get_player_status_self")
async def get_player_status_self(
    telegram_id: str,
    telegram_username: str,
    team_id: str = "",
) -> str:
    """
    Retrieve personal player information for requesting user.

    Provides current registration status, position assignment,
    and participation eligibility for the requesting player.

    Use when: Player needs personal status verification
    Required: Active player registration
    Context: Self-service information access

    Returns: Personal player status summary
    """
    try:
        # Basic parameter validation (CrewAI handles parameter passing)
        if not telegram_id or not telegram_username:
            return "❌ Telegram ID and username are required"

        # Convert telegram_id to integer for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid Telegram ID format"

        logger.info(f"📊 Status request from user {telegram_username} (ID: {telegram_id})")

        # Get domain services through dependency injection
        container = get_container()

        # Get services with consolidated error handling
        try:
            player_service = container.get_service(IPlayerService)
            team_member_service = container.get_service(ITeamMemberService)

            if not player_service or not team_member_service:
                return "❌ Required services are not available"
        except Exception as e:
            logger.error(f"❌ Failed to get required services: {e}")
            return "❌ Required services are not available"

        # Execute business logic with parallel fetching for performance
        import asyncio

        async def get_player_data():
            try:
                return await player_service.get_player_by_telegram_id(telegram_id_int, team_id)
            except Exception as e:
                logger.warning(f"⚠️ Failed to get player info: {e}")
                return None

        async def get_member_data():
            try:
                return await team_member_service.get_team_member_by_telegram_id(
                    telegram_id_int, team_id
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to get team member info: {e}")
                return None

        # Fetch both data sources concurrently for better performance
        player, team_member = await asyncio.gather(
            get_player_data(), get_member_data(), return_exceptions=True
        )

        # Handle exceptions from asyncio.gather
        if isinstance(player, Exception):
            logger.warning(f"⚠️ Player fetch exception: {player}")
            player = None
        if isinstance(team_member, Exception):
            logger.warning(f"⚠️ Team member fetch exception: {team_member}")
            team_member = None

        # Format response based on available data
        if player and team_member:
            status_text = f"👤 Your Status ({telegram_username})\n\n"
            status_text += "🏃 Player Info:\n"
            status_text += f"   • ID: {player.player_id}\n"
            status_text += f"   • Phone: {player.phone_number}\n"
            status_text += f"   • Position: {player.position}\n"
            status_text += f"   • Status: {player.status}\n\n"
            status_text += "👥 Team Member Info:\n"
            status_text += f"   • Role: {team_member.role}\n"
            status_text += f"   • Team: {team_member.team_id}\n"
            status_text += f"   • Status: {team_member.status}\n"
            if team_member.email:
                status_text += f"   • Email: {team_member.email}\n"
            status_text += "   • Permissions: Standard"
        elif player:
            status_text = f"👤 Your Status ({telegram_username})\n\n"
            status_text += "🏃 Player Info:\n"
            status_text += f"   • ID: {player.player_id}\n"
            status_text += f"   • Phone: {player.phone_number}\n"
            status_text += f"   • Position: {player.position}\n"
            status_text += f"   • Status: {player.status}\n\n"
            status_text += "ℹ️ Note: No team member role found"
        elif team_member:
            status_text = f"👤 Your Status ({telegram_username})\n\n"
            status_text += "👥 Team Member Info:\n"
            status_text += f"   • Role: {team_member.role}\n"
            status_text += f"   • Team: {team_member.team_id}\n"
            status_text += f"   • Status: {team_member.status}\n"
            if team_member.email:
                status_text += f"   • Email: {team_member.email}\n"
            status_text += "   • Permissions: Standard\n\n"
            status_text += "ℹ️ Note: No player profile found"
        else:
            status_text = f"👤 Your Status ({telegram_username})\n\n"
            status_text += "❌ No user information found\n\n"
            status_text += "💡 Try using /addplayer to register as a player"

        logger.info(f"✅ Status information provided for {telegram_username}")

        return status_text

    except Exception as e:
        logger.error(f"❌ Error getting user status: {e}")
        return f"❌ Failed to get user status: {e!s}"


@tool("get_player_status_by_identifier")
async def get_player_status_by_identifier(
    telegram_id: str, telegram_username: str, target_identifier: str, team_id: str = ""
) -> str:
    """
    Retrieve player information for specified team member.

    Provides comprehensive player details including registration status,
    position, and participation eligibility for administrative review.

    Use when: Administrative player information lookup is needed
    Required: Valid player identifier and lookup permissions
    Context: Player administration workflow

    Returns: Complete player information summary
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            telegram_id,
            telegram_username,
            target_identifier,
            names=["telegram_id", "telegram_username", "target_identifier"],
        )
        if validation_error:
            return validation_error

        logger.info(f"📊 Status lookup request from {telegram_username} for: {target_identifier}")

        # Get domain services through dependency injection
        container = get_container()

        # Check player service availability
        try:
            player_service = container.get_service(IPlayerService)
            if not player_service:
                return "❌ Player service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get player service: {e}")
            return "❌ Player service is not available"

        # Check team member service availability
        try:
            team_member_service = container.get_service(ITeamMemberService)
            if not team_member_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team member service: {e}")
            return "❌ Team member service is not available"

        # Execute business logic with error handling
        try:
            player = player_service.find_player_by_identifier(target_identifier)
        except Exception as e:
            logger.warning(f"⚠️ Failed to find player: {e}")
            player = None

        if not player:
            return f"❌ Player not found: {target_identifier}\n\n💡 Check the player ID, username, or phone number and try again"

        # Get team member info if available
        try:
            team_member = await team_member_service.get_team_member_by_telegram_id(
                int(player.telegram_id), team_id
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to get team member info: {e}")
            team_member = None

        # Format response
        status_text = f"👤 Player Status: {target_identifier}\n\n"
        status_text += "🏃 Player Info:\n"
        status_text += f"   • ID: {player.player_id}\n"
        status_text += f"   • Phone: {player.phone_number}\n"
        status_text += f"   • Position: {player.position}\n"
        status_text += f"   • Status: {player.status}\n"

        if team_member:
            status_text += "\n👥 Team Member Info:\n"
            status_text += f"   • Role: {team_member.role}\n"
            status_text += f"   • Team: {team_member.team_id}\n"
            status_text += f"   • Status: {team_member.status}"

        logger.info(
            f"✅ Status information provided for {target_identifier} by {telegram_username}"
        )

        return status_text

    except Exception as e:
        logger.error(f"❌ Error getting other user status: {e}")
        return f"❌ Failed to get user status: {e!s}"


@tool("get_member_status_self")
async def get_member_status_self(
    telegram_id: str, telegram_username: str, team_id: str = ""
) -> str:
    """
    Retrieve personal team member information for requesting user.

    Provides current administrative status, role assignments,
    and governance permissions for the requesting team member.

    Use when: Team member needs personal administrative status verification
    Required: Active team member registration
    Context: Administrative self-service workflow

    Returns: Personal team member status summary
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            telegram_id, telegram_username, names=["telegram_id", "telegram_username"]
        )
        if validation_error:
            return validation_error

        # Convert telegram_id to integer for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid Telegram ID format"

        logger.info(f"📊 Member status request from admin {telegram_username} (ID: {telegram_id})")

        # Get domain services through dependency injection
        container = get_container()

        # Check team member service availability
        try:
            team_member_service = container.get_service(ITeamMemberService)
            if not team_member_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team member service: {e}")
            return "❌ Team member service is not available"

        # Get player service for comprehensive info (optional)
        try:
            player_service = container.get_service(IPlayerService)
        except Exception as e:
            logger.warning(f"⚠️ Player service unavailable: {e}")
            player_service = None

        # Execute business logic with error handling
        try:
            team_member = await team_member_service.get_team_member_by_telegram_id(
                telegram_id_int, team_id
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to get team member info: {e}")
            team_member = None

        if not team_member:
            return "❌ You are not registered as a team member\n\n💡 Contact an admin to get team member access"

        # Try to get player info if service available
        player = None
        if player_service:
            try:
                player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)
            except Exception as e:
                logger.warning(f"⚠️ Failed to get player info: {e}")

        # Format response for team member context
        status_text = f"👥 Your Member Status ({telegram_username})\n\n"
        status_text += "🏢 Team Member Info:\n"
        status_text += f"   • Role: {team_member.role}\n"
        status_text += f"   • Team: {team_member.team_id}\n"
        status_text += f"   • Status: {team_member.status}\n"
        status_text += f"   • Permissions: {', '.join(team_member.permissions) if hasattr(team_member, 'permissions') else 'Standard'}\n"

        if player:
            status_text += "\n🏃 Player Info (if applicable):\n"
            status_text += f"   • Player ID: {player.player_id}\n"
            status_text += f"   • Position: {player.position}\n"
            status_text += f"   • Player Status: {player.status}"
        else:
            status_text += "\nℹ️ Note: No player profile found"

        logger.info(f"✅ Member status information provided for {telegram_username}")

        return status_text

    except Exception as e:
        logger.error(f"❌ Error getting member status: {e}")
        return f"❌ Failed to get member status: {e!s}"


@tool("get_member_status_by_identifier")
async def get_member_status_by_identifier(
    telegram_id: str, telegram_username: str, target_identifier: str, team_id: str = ""
) -> str:
    """
    Retrieve team member information for specified administrator.

    Provides comprehensive administrative details including role assignments,
    permissions, and governance status for leadership review.

    Use when: Administrative member information lookup is needed
    Required: Valid member identifier and administrative permissions
    Context: Team member administration workflow

    Returns: Complete team member information summary
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            telegram_id,
            telegram_username,
            target_identifier,
            names=["telegram_id", "telegram_username", "target_identifier"],
        )
        if validation_error:
            return validation_error

        logger.info(f"📊 Member status lookup from {telegram_username} for: {target_identifier}")

        # Get domain services through dependency injection
        container = get_container()

        # Check team member service availability
        try:
            team_member_service = container.get_service(ITeamMemberService)
            if not team_member_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team member service: {e}")
            return "❌ Team member service is not available"

        # Get player service for comprehensive info (optional)
        try:
            player_service = container.get_service(IPlayerService)
        except Exception as e:
            logger.warning(f"⚠️ Player service unavailable: {e}")
            player_service = None

        # Execute business logic with error handling
        try:
            # Get all team members and search manually since search_team_members is not implemented
            all_members = await team_member_service.get_team_members(team_id)
            search_lower = target_identifier.lower()

            # Search for matches by name, phone, or email
            team_member = None
            for member in all_members:
                if (
                    (member.name and search_lower in member.name.lower())
                    or (member.phone_number and search_lower in member.phone_number.lower())
                    or (getattr(member, "email", None) and search_lower in member.email.lower())
                ):
                    team_member = member
                    break

        except Exception as e:
            logger.warning(f"⚠️ Failed to search team member: {e}")
            team_member = None

        if not team_member:
            return f"❌ Team member not found: {target_identifier}\n\n💡 Check the member name, phone number, or email and try again"

        # Try to get player info if service available
        player = None
        if player_service and team_member.telegram_id:
            try:
                player = await player_service.get_player_by_telegram_id(
                    int(team_member.telegram_id), team_id
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to get player info: {e}")

        # Format response for team member lookup
        status_text = f"👥 Team Member Status: {target_identifier}\n\n"
        status_text += "🏢 Member Info:\n"
        status_text += f"   • Role: {team_member.role}\n"
        status_text += f"   • Team: {team_member.team_id}\n"
        status_text += f"   • Status: {team_member.status}\n"
        status_text += f"   • Permissions: {', '.join(team_member.permissions) if hasattr(team_member, 'permissions') else 'Standard'}\n"

        if player:
            status_text += "\n🏃 Player Info (if applicable):\n"
            status_text += f"   • Player ID: {player.player_id}\n"
            status_text += f"   • Position: {player.position}\n"
            status_text += f"   • Player Status: {player.status}"

        logger.info(
            f"✅ Member status information provided for {target_identifier} by {telegram_username}"
        )

        return status_text

    except Exception as e:
        logger.error(f"❌ Error getting member status: {e}")
        return f"❌ Failed to get member status: {e!s}"
