#!/usr/bin/env python3
"""
Simplified Team Member Tools

This module provides tools for simplified team member management
for the new /addmember command that only requires name and phone number.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.core.interfaces.team_repositories import (
    ITeamRepository,
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
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.tool_helpers import (
    validate_required_input,
)
from kickai.utils.validation_utils import (
    normalize_phone,
    sanitize_input,
)


@tool("add_team_member_simplified")
def add_team_member_simplified(
    team_id: str, telegram_id: int, name: str, phone: str, role: str | None = None
) -> str:
    """
    Add a new team member with simplified ID generation.

    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :param telegram_id: Telegram ID (required) - available from context
    :type telegram_id: int
    :param name: Team member's full name
    :type name: str
    :param phone: Team member's phone number
    :type phone: str
    :param role: Team member's role (optional, can be set later)
    :type role: str | None
    :return: JSON response with team member addition status
    :rtype: str
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return validation_error

        # Simplified validation - only name and phone required
        if not name or not name.strip():
            return json_error(message=ERROR_MESSAGES["NAME_REQUIRED"], error_type="Validation failed")

        if not phone or not phone.strip():
            return json_error(message=ERROR_MESSAGES["PHONE_REQUIRED"], error_type="Validation failed")

        # Sanitize inputs
        name = sanitize_input(name, max_length=MAX_NAME_LENGTH)
        phone = sanitize_input(phone, max_length=MAX_PHONE_LENGTH)
        role = sanitize_input(role, max_length=MAX_POSITION_LENGTH) if role else DEFAULT_MEMBER_ROLE
        team_id = sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH)
        # Validate telegram_id as positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return create_error_response(
                message=f"Invalid telegram_id: {telegram_id}. Must be a positive integer.",
                error_type="Invalid input"
            )

        # Normalize phone number
        phone = normalize_phone(phone)

        container = get_container()

        # Get team repository for the service
        team_repository = container.get_service(ITeamRepository)
        if not team_repository:
            raise ServiceNotAvailableError(
                ERROR_MESSAGES["SERVICE_UNAVAILABLE"].format(service="ITeamRepository")
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

            data = {
                'team_id': team_id,
                'telegram_id': telegram_id,
                'member_details': {
                    'name': name,
                    'phone': phone,
                    'role': role,
                    'member_id': member_id,
                    'status': 'Active'
                },
                'invite_link': invite_result.get("invite_link") if invite_result.get("success") else None,
                'invite_success': invite_result.get("success", False)
            }

            if invite_result.get("success"):
                ui_format = f"""✅ Team Member Added Successfully!

👔 Member Details:
• Name: {name}
• Phone: {phone}
• Role: {role}
• Member ID: {member_id}
• Status: Active

🔗 Invite Link for Leadership Chat:
{invite_result["invite_link"]}

📋 Next Steps:
1. Send the invite link to {name}
2. Ask them to join the leadership chat
3. They can then access admin commands and team management features

🔒 Security:
• Link expires in 7 days
• One-time use only
• Automatically tracked in system

💡 Note: This invite link is unique, expires in 7 days, and can only be used once.

🎯 Member ID: {member_id}"""
            else:
                ui_format = f"""✅ Team Member Added Successfully!

👔 Member Details:
• Name: {name}
• Phone: {phone}
• Role: {role}
• Member ID: {member_id}
• Status: Active

⚠️ Note: Could not generate invite link - {invite_result.get("error", "Unknown error")}.
Please contact the system administrator.

🎯 Member ID: {member_id}"""

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message=f"Failed to add team member: {message}", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in add_team_member_simplified: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to add team member: {e}", exc_info=True)
        return json_error(message=f"Failed to add team member: {e}", error_type="Operation failed")
