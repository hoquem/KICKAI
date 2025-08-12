#!/usr/bin/env python3
"""
Simplified Team Member Tools

This module provides tools for simplified team member management
for the new /addmember command that only requires name and phone number.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.team_administration.domain.repositories.team_repository_interface import (
    TeamRepositoryInterface,
)
from kickai.features.team_administration.domain.services.simplified_team_member_service import (
    SimplifiedTeamMemberService,
)
from kickai.utils.constants import (
    DEFAULT_MEMBER_ROLE,
    ERROR_MESSAGES,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_POSITION_LENGTH,
    MAX_TEAM_ID_LENGTH,
    MAX_USER_ID_LENGTH,
)
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    create_json_response,
    format_tool_error,
    validate_required_input,
)
from kickai.utils.validation_utils import (
    normalize_phone,
    sanitize_input,
)


@tool("add_team_member_simplified")
def add_team_member_simplified(
    team_id: str, user_id: str, name: str, phone: str, role: str = None
) -> str:
    """
    Add a new team member with simplified ID generation.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        name: Team member's full name
        phone: Team member's phone number
        role: Team member's role (optional, can be set later)

    Returns:
        JSON string with success message and invite link or error
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        # Simplified validation - only name and phone required
        if not name or not name.strip():
            return create_json_response("error", message=ERROR_MESSAGES["NAME_REQUIRED"])

        if not phone or not phone.strip():
            return create_json_response("error", message=ERROR_MESSAGES["PHONE_REQUIRED"])

        # Sanitize inputs
        name = sanitize_input(name, max_length=MAX_NAME_LENGTH)
        phone = sanitize_input(phone, max_length=MAX_PHONE_LENGTH)
        role = sanitize_input(role, max_length=MAX_POSITION_LENGTH) if role else DEFAULT_MEMBER_ROLE
        team_id = sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH)
        user_id = sanitize_input(user_id, max_length=MAX_USER_ID_LENGTH)

        # Normalize phone number
        phone = normalize_phone(phone)

        container = get_container()

        # Get team repository for the service
        team_repository = container.get_service(TeamRepositoryInterface)
        if not team_repository:
            raise ServiceNotAvailableError(
                ERROR_MESSAGES["SERVICE_UNAVAILABLE"].format(service="TeamRepositoryInterface")
            )

        # Create simplified team member service
        team_member_service = SimplifiedTeamMemberService(team_repository)

        # Add team member with simplified ID generation (sync call via asyncio.run)
        success, message = asyncio.run(team_member_service.add_team_member(name, phone, role, team_id))

        if success:
            # Extract member ID from message
            import re

            member_id_match = re.search(r"ID: (\w+)", message)
            member_id = member_id_match.group(1) if member_id_match else "Unknown"

            # Create invite link (sync call via asyncio.run)
            invite_result = asyncio.run(team_member_service.create_team_member_invite_link(
                name, phone, role, team_id
            ))

            member_data = {
                'name': name,
                'phone': phone,
                'role': role,
                'member_id': member_id,
                'status': 'Active'
            }

            if invite_result.get("success"):
                member_data['invite_link'] = invite_result["invite_link"]
                member_data['invite_success'] = True
                member_data['next_steps'] = [
                    f"Send the invite link to {name}",
                    "Ask them to join the leadership chat",
                    "They can then access admin commands and team management features"
                ]
                member_data['security_info'] = [
                    "Link expires in 7 days",
                    "One-time use only",
                    "Automatically tracked in system"
                ]
                return create_json_response("success", data=member_data)
            else:
                member_data['invite_link'] = None
                member_data['invite_success'] = False
                member_data['invite_error'] = invite_result.get("error", "Unknown error")
                return create_json_response("success", data=member_data)
        else:
            return create_json_response("error", message=f"Failed to add team member: {message}")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in add_team_member_simplified: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to add team member: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to add team member: {e}")
