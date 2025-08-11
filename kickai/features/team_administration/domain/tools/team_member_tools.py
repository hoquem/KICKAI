#!/usr/bin/env python3
"""
Team Member Tools

This module provides tools for team member management operations.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio
from loguru import logger
from typing import Optional

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.crewai_tool_decorator import json_tool
from kickai.utils.json_response import create_data_response, create_error_response
from kickai.utils.ui_formatter import UIFormatBuilder
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    format_tool_success,
    validate_required_input,
)


@json_tool("team_member_registration")
def team_member_registration(
    name: str,
    telegram_id: str,
    phone_number: str,
    role: str,
    team_id: str,
    is_admin: bool = False
) -> dict:
    """
    Register a new team member. Requires: name, telegram_id, phone_number, role, team_id

    Args:
        name: Name of the team member
        telegram_id: Telegram ID of the team member
        phone_number: Phone number of the team member
        role: Role of the team member (e.g., Coach, Manager, Assistant)
        team_id: Team ID (required)
        is_admin: Whether the member is an admin (default: False)

    Returns:
        JSON response with registration status and team member details
    """
    try:
        # Handle JSON string input using utility functions
        name = extract_single_value(name, "name")
        telegram_id = extract_single_value(telegram_id, "telegram_id")
        phone_number = extract_single_value(phone_number, "phone_number")
        role = extract_single_value(role, "role")
        team_id = extract_single_value(team_id, "team_id")
        is_admin = extract_single_value(is_admin, "is_admin") if isinstance(is_admin, str) else is_admin

        # Validate inputs using utility functions
        validation_error = validate_required_input(name, "Name")
        if validation_error:
            return create_error_response(validation_error, "Validation failed")

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_error_response(validation_error, "Validation failed")

        validation_error = validate_required_input(phone_number, "Phone Number")
        if validation_error:
            return create_error_response(validation_error, "Validation failed")

        validation_error = validate_required_input(role, "Role")
        if validation_error:
            return create_error_response(validation_error, "Validation failed")

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_error_response(validation_error, "Validation failed")

        # Get TeamMemberService from container
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            raise ServiceNotAvailableError("TeamMemberService")

        # Build TeamMember entity
        try:
            telegram_id_int = int(telegram_id)
        except Exception:
            return create_error_response("Invalid Telegram ID: must be a number", "Validation failed")

        # Import here to avoid circular imports
        from kickai.features.team_administration.domain.entities.team_member import TeamMember

        team_member = TeamMember.create_from_telegram(
            team_id=team_id,
            telegram_id=telegram_id_int,
            name=name,
            username=None,
            is_admin=bool(is_admin),
        )

        # Apply provided details
        team_member.phone_number = phone_number
        team_member.role = role
        team_member.is_admin = bool(is_admin)

        # Persist team member
        created_id = asyncio.run(team_member_service.create_team_member(team_member))

        if created_id:
            ui_format = f"""✅ **Team Member Registered Successfully!**

👤 **Name**: {team_member.name}
📱 **Telegram ID**: {team_member.telegram_id}
📞 **Phone**: {team_member.phone_number}
👑 **Role**: {team_member.role.title()}
🏆 **Team ID**: {team_member.team_id}
🆔 **Member ID**: {created_id}
✅ **Admin**: {'Yes' if team_member.is_admin else 'No'}

🎉 Welcome to the team, {team_member.name}!"""

            data = {
                'member_id': created_id,
                'team_member': {
                    'name': team_member.name,
                    'telegram_id': team_member.telegram_id,
                    'phone_number': team_member.phone_number,
                    'role': team_member.role,
                    'team_id': team_member.team_id,
                    'is_admin': team_member.is_admin
                },
                'registration_status': 'success'
            }

            return create_data_response(data, ui_format)
        else:
            return create_error_response("Failed to register team member", "Registration failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in team_member_registration: {e}")
        return create_error_response(f"Service temporarily unavailable: {e.message}", "Service unavailable")
    except Exception as e:
        logger.error(f"Failed to register team member: {e}", exc_info=True)
        return create_error_response(f"Failed to register team member: {e}", "Registration failed")


@json_tool("get_my_team_member_status")
def get_my_team_member_status(team_id: str, telegram_id: str) -> dict:
    """
    Get current user's team member status and information.
    This tool is for team members in the leadership chat.
    For players in main chat, use get_my_status.

    Args:
        team_id: The team ID
        telegram_id: The user's Telegram ID

    Returns:
        JSON response with team member status information
    """
    try:
        # Lazy-load services only when needed
        try:
            container = get_container()
            team_member_service = container.get_service("TeamMemberService")
        except Exception as e:
            logger.error(f"❌ Failed to get TeamMemberService from container: {e}")
            return create_error_response("Service temporarily unavailable. Please try again in a moment.", "Service unavailable")

        logger.info(
            f"🔧 get_my_team_member_status called with team_id: {team_id}, telegram_id: {telegram_id}"
        )

        # Use synchronous service method
        status = team_member_service.get_my_status_sync(telegram_id, team_id)
        logger.info(f"✅ Retrieved team member status for {telegram_id}")
        
        # Create structured data
        data = {
            'team_id': team_id,
            'telegram_id': telegram_id,
            'status_text': status,
            'user_type': 'team_member'
        }
        
        return create_data_response(data, status)

    except Exception as e:
        logger.error(f"❌ Failed to get team member status: {e}")
        return create_error_response(f"Failed to get team member status: {e!s}", "Operation failed")


@tool("get_team_members")
def get_team_members(team_id: str, role: Optional[str] = None) -> str:
    """
    Get team members for a team, optionally filtered by role.

    Args:
        team_id: The team ID
        role: Optional role to filter by

    Returns:
        Formatted string with team member information
    """
    try:
        # Lazy-load services only when needed
        try:
            container = get_container()
            team_member_service = container.get_service("TeamMemberService")
        except Exception as e:
            logger.error(f"❌ Failed to get TeamMemberService from container: {e}")
            return "❌ Service temporarily unavailable. Please try again in a moment."

        # Use synchronous service methods
        if role:
            members = team_member_service.get_team_members_by_role_sync(team_id, role)
        else:
            members = team_member_service.get_team_members_by_team_sync(team_id)

        if not members:
            return f"👥 No team members found for team {team_id}."

        result = f"👥 Team Members for {team_id}\n\n"
        for member in members:
            role_text = member.role if member.role else "No role"
            admin_status = "👑 Admin" if member.is_admin else "👤 Member"
            result += f"• {member.name or 'Unknown'} - {admin_status} ({role_text})\n"

        return result

    except Exception as e:
        logger.error(f"❌ Failed to get team members for {team_id}: {e}")
        return f"❌ Failed to get team members: {e!s}"


@tool("add_team_member_role")
def add_team_member_role(telegram_id: str, team_id: str, role: str) -> str:
    """
    Add a role to a team member.

    Args:
        telegram_id: The user's Telegram ID
        team_id: The team ID
        role: The role to add

    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        success = team_member_service.add_role_to_member_sync(telegram_id, team_id, role)

        if success:
            return f"✅ Successfully added role '{role}' to team member {telegram_id}"
        else:
            return f"❌ Failed to add role '{role}' to team member {telegram_id}"

    except Exception as e:
        logger.error(f"❌ Failed to add role {role} to member {telegram_id}: {e}")
        return f"❌ Error adding role: {e!s}"


@tool("remove_team_member_role")
def remove_team_member_role(telegram_id: str, team_id: str, role: str) -> str:
    """
    Remove a role from a team member.

    Args:
        telegram_id: The user's Telegram ID
        team_id: The team ID
        role: The role to remove

    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        success = team_member_service.remove_role_from_member_sync(telegram_id, team_id, role)

        if success:
            return f"✅ Successfully removed role '{role}' from team member {telegram_id}"
        else:
            return f"❌ Failed to remove role '{role}' from team member {telegram_id}"

    except Exception as e:
        logger.error(f"❌ Failed to remove role {role} from member {telegram_id}: {e}")
        return f"❌ Error removing role: {e!s}"


@tool("promote_team_member_to_admin")
def promote_team_member_to_admin(telegram_id: str, team_id: str, promoted_by: str) -> str:
    """
    Promote a team member to admin role.

    Args:
        telegram_id: The user's Telegram ID
        team_id: The team ID
        promoted_by: The user ID of who is doing the promotion

    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        success = team_member_service.promote_to_admin_sync(telegram_id, team_id, promoted_by)

        if success:
            return f"👑 Successfully promoted team member {telegram_id} to admin by {promoted_by}"
        else:
            return f"❌ Failed to promote team member {telegram_id} to admin"

    except Exception as e:
        logger.error(f"❌ Failed to promote member {telegram_id} to admin: {e}")
        return f"❌ Error promoting to admin: {e!s}"
