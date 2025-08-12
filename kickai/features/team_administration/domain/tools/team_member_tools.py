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
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    create_json_response,
    extract_single_value,
    format_tool_error,
    format_tool_success,
    validate_required_input,
)


@tool("team_member_registration", result_as_answer=True)
def team_member_registration(
    name: str,
    telegram_id: str,
    phone_number: str,
    role: str,
    team_id: str,
    is_admin: bool = False
) -> str:
    """Register a new team member.
    
    Registers a new team member (coach, manager, assistant) with
    administrative privileges and role assignment.
    
    :param name: Name of the team member
    :type name: str
    :param telegram_id: Telegram ID of the team member
    :type telegram_id: str
    :param phone_number: Phone number of the team member
    :type phone_number: str
    :param role: Role of the team member (e.g., Coach, Manager, Assistant)
    :type role: str
    :param team_id: Team ID (required)
    :type team_id: str
    :param is_admin: Whether the member has admin privileges, defaults to False
    :type is_admin: bool
    :returns: JSON string with registration details or error message
    :rtype: str
    :raises ServiceNotAvailableError: When TeamMemberService is not available
    :raises Exception: When registration fails or validation errors occur
    
    .. example::
       >>> result = team_member_registration("John Coach", "123456", "+1234567890", "Coach", "KTI", True)
       >>> print(result)
       '{"status": "success", "data": {"message": "Team Member Registered Successfully!", ...}}'
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
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(phone_number, "Phone Number")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(role, "Role")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        # Get TeamMemberService from container
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            raise ServiceNotAvailableError("TeamMemberService")

        # Build TeamMember entity
        try:
            telegram_id_int = int(telegram_id)
        except Exception:
            return create_json_response("error", message="Invalid Telegram ID: must be a number")

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
            return create_json_response("success", data={
                'message': 'Team Member Registered Successfully!',
                'name': team_member.name,
                'telegram_id': team_member.telegram_id,
                'phone_number': team_member.phone_number,
                'role': team_member.role.title(),
                'team_id': team_member.team_id,
                'member_id': created_id,
                'is_admin': team_member.is_admin
            })
        else:
            return create_json_response("error", message="Failed to register team member")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in team_member_registration: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to register team member: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to register team member: {e}")


@tool("get_my_team_member_status", result_as_answer=True)
def get_my_team_member_status(team_id: str, telegram_id: str) -> str:
    """Get current user's team member status and information.
    
    Retrieves team member status and details for users in leadership chat.
    For players in main chat, use get_my_status instead.
    
    :param team_id: The team ID
    :type team_id: str
    :param telegram_id: The user's Telegram ID
    :type telegram_id: str
    :returns: JSON string with team member status information or error message
    :rtype: str
    :raises Exception: When service unavailable or status retrieval fails
    
    .. note::
       This tool is specifically for team members in leadership chat.
       Players should use get_my_status tool instead.
    """
    try:
        # Lazy-load services only when needed
        try:
            container = get_container()
            team_member_service = container.get_service("TeamMemberService")
        except Exception as e:
            logger.error(f"Failed to get TeamMemberService from container: {e}")
            return create_json_response("error", message="Service temporarily unavailable. Please try again in a moment.")

        logger.info(
            f"get_my_team_member_status called with team_id: {team_id}, telegram_id: {telegram_id}"
        )

        # Use synchronous service method
        status = team_member_service.get_my_status_sync(telegram_id, team_id)
        logger.info(f"Retrieved team member status for {telegram_id}")
        return create_json_response("success", data={'status': status})

    except Exception as e:
        logger.error(f"Failed to get team member status: {e}")
        return create_json_response("error", message=f"Failed to get team member status: {e!s}")


@tool("get_team_members", result_as_answer=True)
def get_team_members(team_id: str, role: Optional[str] = None) -> str:
    """Get team members for a team.
    
    Retrieves list of team members (administrative staff) with
    optional filtering by role.
    
    :param team_id: The team ID
    :type team_id: str
    :param role: Optional role to filter by (e.g., Coach, Manager)
    :type role: Optional[str]
    :returns: JSON string with team member list or error message
    :rtype: str
    :raises Exception: When service unavailable or retrieval fails
    
    .. note::
       Returns empty list with success status if no members found
    """
    try:
        # Lazy-load services only when needed
        try:
            container = get_container()
            team_member_service = container.get_service("TeamMemberService")
        except Exception as e:
            logger.error(f"Failed to get TeamMemberService from container: {e}")
            return create_json_response("error", message="Service temporarily unavailable. Please try again in a moment.")

        # Use synchronous service methods
        if role:
            members = team_member_service.get_team_members_by_role_sync(team_id, role)
        else:
            members = team_member_service.get_team_members_by_team_sync(team_id)

        if not members:
            return create_json_response("success", data={'message': f'No team members found for team {team_id}', 'members': []})

        members_data = []
        for member in members:
            role_text = member.role if member.role else "No role"
            admin_status = "Admin" if member.is_admin else "Member"
            members_data.append({
                'name': member.name or 'Unknown',
                'role': role_text,
                'admin_status': admin_status,
                'is_admin': member.is_admin
            })

        return create_json_response("success", data={'message': f'Team Members for {team_id}', 'members': members_data})

    except Exception as e:
        logger.error(f"Failed to get team members for {team_id}: {e}")
        return create_json_response("error", message=f"Failed to get team members: {e!s}")


@tool("add_team_member_role", result_as_answer=True)
def add_team_member_role(telegram_id: str, team_id: str, role: str) -> str:
    """Add a role to a team member.
    
    Assigns an additional role to an existing team member.
    
    :param telegram_id: The user's Telegram ID
    :type telegram_id: str
    :param team_id: The team ID
    :type team_id: str
    :param role: The role to add
    :type role: str
    :returns: JSON string with confirmation or error message
    :rtype: str
    :raises Exception: When role addition fails
    
    .. example::
       >>> result = add_team_member_role("123456", "KTI", "Assistant Coach")
       >>> print(result)
       '{"status": "success", "data": {"message": "Successfully added role...", ...}}'
    """
    try:
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        success = team_member_service.add_role_to_member_sync(telegram_id, team_id, role)

        if success:
            return create_json_response("success", data={'message': f"Successfully added role '{role}' to team member {telegram_id}", 'telegram_id': telegram_id, 'role': role})
        else:
            return create_json_response("error", message=f"Failed to add role '{role}' to team member {telegram_id}")

    except Exception as e:
        logger.error(f"❌ Failed to add role {role} to member {telegram_id}: {e}")
        return create_json_response("error", message=f"Error adding role: {e!s}")


@tool("remove_team_member_role", result_as_answer=True)
def remove_team_member_role(telegram_id: str, team_id: str, role: str) -> str:
    """Remove a role from a team member.
    
    Removes a specific role from an existing team member.
    
    :param telegram_id: The user's Telegram ID
    :type telegram_id: str
    :param team_id: The team ID
    :type team_id: str
    :param role: The role to remove
    :type role: str
    :returns: JSON string with confirmation or error message
    :rtype: str
    :raises Exception: When role removal fails
    """
    try:
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        success = team_member_service.remove_role_from_member_sync(telegram_id, team_id, role)

        if success:
            return create_json_response("success", data={'message': f"Successfully removed role '{role}' from team member {telegram_id}", 'telegram_id': telegram_id, 'role': role})
        else:
            return create_json_response("error", message=f"Failed to remove role '{role}' from team member {telegram_id}")

    except Exception as e:
        logger.error(f"❌ Failed to remove role {role} from member {telegram_id}: {e}")
        return create_json_response("error", message=f"Error removing role: {e!s}")


@tool("promote_team_member_to_admin", result_as_answer=True)
def promote_team_member_to_admin(telegram_id: str, team_id: str, promoted_by: str) -> str:
    """Promote a team member to admin role.
    
    Grants administrative privileges to an existing team member.
    
    :param telegram_id: The user's Telegram ID to promote
    :type telegram_id: str
    :param team_id: The team ID
    :type team_id: str
    :param promoted_by: The user ID of who is doing the promotion
    :type promoted_by: str
    :returns: JSON string with confirmation or error message
    :rtype: str
    :raises Exception: When promotion fails
    
    .. note::
       Promotion requires existing admin privileges for the promoting user
    """
    try:
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        success = team_member_service.promote_to_admin_sync(telegram_id, team_id, promoted_by)

        if success:
            return create_json_response("success", data={'message': f"Successfully promoted team member {telegram_id} to admin by {promoted_by}", 'telegram_id': telegram_id, 'promoted_by': promoted_by})
        else:
            return create_json_response("error", message=f"Failed to promote team member {telegram_id} to admin")

    except Exception as e:
        logger.error(f"❌ Failed to promote member {telegram_id} to admin: {e}")
        return create_json_response("error", message=f"Error promoting to admin: {e!s}")
