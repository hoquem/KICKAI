#!/usr/bin/env python3
"""
Team Member Tools

This module provides tools for team member management operations.
"""

import asyncio

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.tool_helpers import (
    validate_required_input,
)
from kickai.utils.validation_utils import (
    validate_team_id,
)


@tool("team_member_registration")
def team_member_registration(
    name: str,
    telegram_id: int,
    phone_number: str,
    role: str,
    team_id: str,
    is_admin: bool = False
) -> str:
    """
    Register a new team member. Requires: name, telegram_id, phone_number, role, team_id

    :param name: Name of the team member
    :type name: str
    :param telegram_id: Telegram ID of the team member
    :type telegram_id: int
    :param phone_number: Phone number of the team member
    :type phone_number: str
    :param role: Role of the team member (e.g., Coach, Manager, Assistant)
    :type role: str
    :param team_id: Team ID (required)
    :type team_id: str
    :param is_admin: Whether the member is an admin (default: False)
    :type is_admin: bool
    :return: JSON response with registration status and team member details
    :rtype: str
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(name, "Name")
        if validation_error:
            return json_error(message=validation_error, error_type="Validation failed")

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return json_error(message=validation_error, error_type="Validation failed")

        validation_error = validate_required_input(phone_number, "Phone Number")
        if validation_error:
            return json_error(message=validation_error, error_type="Validation failed")

        validation_error = validate_required_input(role, "Role")
        if validation_error:
            return json_error(message=validation_error, error_type="Validation failed")

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return json_error(message=validation_error, error_type="Validation failed")

        # Get TeamMemberService from container
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            raise ServiceNotAvailableError("TeamMemberService")

        # Build TeamMember entity
        telegram_id_int = telegram_id  # Already an int

        # Import here to avoid circular imports
        from kickai.features.team_administration.domain.entities.team_member import TeamMember

        team_member = TeamMember.create_from_telegram(
            team_id=team_id,
            telegram_id=telegram_id,
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
                'name': team_member.name,
                'telegram_id': team_member.telegram_id,
                'phone_number': team_member.phone_number,
                'role': team_member.role,
                'team_id': team_member.team_id,
                'is_admin': team_member.is_admin,
                'status': 'registered'
            }

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message="Failed to register team member", error_type="Registration failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in team_member_registration: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to register team member: {e}")
        return json_error(message=f"Failed to register team member: {e}", error_type="Registration failed")

@tool("get_my_team_member_status")
def get_my_team_member_status(team_id: str, telegram_id: int) -> str:
    """
    Get the current user's team member status.

    :param team_id: Team ID (required)
    :type team_id: str
    :param telegram_id: Telegram ID (required)
    :type telegram_id: int
    :return: JSON response with team member status information
    :rtype: str
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)
        
        # Validate telegram_id as positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return json_error(message=f"Invalid telegram_id: {telegram_id}. Must be a positive integer.", error_type="Invalid input")

        # Log tool execution start
        inputs = {'team_id': team_id, 'telegram_id': telegram_id}


        # Get service
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return json_error(message="Service temporarily unavailable. Please try again in a moment.", error_type="Service unavailable")

        # Get team member status
        status = team_member_service.get_my_status_sync(telegram_id, team_id)

        data = {
            'team_id': team_id,
            'telegram_id': telegram_id,
            'status_text': status
        }

        return json_response(data=data, ui_format=status)

    except Exception as e:
        logger.error(f"Failed to get team member status: {e!s}")
        return json_error(message=f"Failed to get team member status: {e!s}", error_type="Operation failed")

@tool("get_team_members")
def get_team_members(team_id: str, role: str | None = None) -> str:
    """
    Get all team members for a team.


        team_id: Team ID (required)
        role: Optional role filter


    :return: JSON response with team members list
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'team_id': team_id, 'role': role}


        # Get service
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return json_error(message="Service temporarily unavailable. Please try again in a moment.", error_type="Service unavailable")

        # Get team members
        if role:
            members = team_member_service.get_team_members_by_role_sync(team_id, role)
        else:
            members = team_member_service.get_team_members_by_team_sync(team_id)

        if members:
            members_data = []
            ui_format = f"👥 **Team Members for {team_id}**\n\n"

            for member in members:
                admin_status = "👑 Admin" if member.is_admin else "👤 Member"
                role_text = member.role if member.role else "No role"
                ui_format += f"• {member.name or 'Unknown'} - {admin_status} ({role_text})\n"

                members_data.append({
                    'member_id': member.member_id,
                    'name': member.name,
                    'telegram_id': member.telegram_id,
                    'phone_number': member.phone_number,
                    'role': member.role,
                    'is_admin': member.is_admin,
                    'status': member.status
                })

            data = {
                'team_id': team_id,
                'role_filter': role,
                'members': members_data,
                'total_count': len(members)
            }

            return json_response(data=data, ui_format=ui_format)
        else:
            data = {
                'team_id': team_id,
                'role_filter': role,
                'members': [],
                'total_count': 0
            }
            return json_response(data=data, ui_format=f"👥 No team members found for team {team_id}.")

    except Exception as e:
        logger.error(f"Failed to get team members: {e!s}")
        return json_error(message=f"Failed to get team members: {e!s}", error_type="Operation failed")

@tool("add_team_member_role")
def add_team_member_role(telegram_id: int, team_id: str, role: str) -> str:
    """
    Add a role to a team member.

    :param telegram_id: Telegram ID of the team member
    :type telegram_id: int
    :param team_id: Team ID (required)
    :type team_id: str
    :param role: Role to add
    :type role: str
    :return: JSON response with role addition status
    :rtype: str
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)

        role = validate_required_input(role, "Role")

        # Log tool execution start
        inputs = {'team_id': team_id, 'telegram_id': telegram_id, 'role': role}


        # Get service
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return json_error(message="Service temporarily unavailable. Please try again in a moment.", error_type="Service unavailable")

        # Add role to team member
        success = team_member_service.add_role_to_member_sync(telegram_id, team_id, role)

        if success:
            data = {
                'telegram_id': telegram_id,
                'team_id': team_id,
                'role': role,
                'status': 'role_added'
            }

            ui_format = f"✅ Role '{role}' added successfully to team member {telegram_id}"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message=f"Failed to add role '{role}' to team member {telegram_id}", error_type="Role addition failed")

    except Exception as e:
        logger.error(f"Error adding role: {e!s}")
        return json_error(message=f"Error adding role: {e!s}", error_type="Operation failed")

@tool("remove_team_member_role")
def remove_team_member_role(telegram_id: int, team_id: str, role: str) -> str:
    """
    Remove a role from a team member.

    :param telegram_id: Telegram ID of the team member
    :type telegram_id: int
    :param team_id: Team ID (required)
    :type team_id: str
    :param role: Role to remove
    :type role: str
    :return: JSON response with role removal status
    :rtype: str
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)

        role = validate_required_input(role, "Role")

        # Log tool execution start
        inputs = {'team_id': team_id, 'telegram_id': telegram_id, 'role': role}


        # Get service
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return json_error(message="Service temporarily unavailable. Please try again in a moment.", error_type="Service unavailable")

        # Remove role from team member
        success = team_member_service.remove_role_from_member_sync(telegram_id, team_id, role)

        if success:
            data = {
                'telegram_id': telegram_id,
                'team_id': team_id,
                'role': role,
                'status': 'role_removed'
            }

            ui_format = f"✅ Role '{role}' removed successfully from team member {telegram_id}"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message=f"Failed to remove role '{role}' from team member {telegram_id}", error_type="Role removal failed")

    except Exception as e:
        logger.error(f"Error removing role: {e!s}")
        return json_error(message=f"Error removing role: {e!s}", error_type="Operation failed")

@tool("promote_team_member_to_admin")
def promote_team_member_to_admin(telegram_id: int, team_id: str, promoted_by: int) -> str:
    """
    Promote a team member to admin status.

    :param telegram_id: Telegram ID of the team member to promote
    :type telegram_id: int
    :param team_id: Team ID (required)
    :type team_id: str
    :param promoted_by: Telegram ID of the person making the promotion
    :type promoted_by: int
    :return: JSON response with promotion status
    :rtype: str
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)



        # Log tool execution start
        inputs = {'team_id': team_id, 'telegram_id': telegram_id, 'promoted_by': promoted_by}


        # Get service
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return json_error(message="Service temporarily unavailable. Please try again in a moment.", error_type="Service unavailable")

        # Promote team member to admin
        success = team_member_service.promote_to_admin_sync(telegram_id, team_id, promoted_by)

        if success:
            data = {
                'telegram_id': telegram_id,
                'team_id': team_id,
                'promoted_by': promoted_by,
                'status': 'promoted_to_admin'
            }

            ui_format = f"👑 Team member {telegram_id} promoted to admin successfully by {promoted_by}"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message=f"Failed to promote team member {telegram_id} to admin", error_type="Promotion failed")

    except Exception as e:
        logger.error(f"Error promoting to admin: {e!s}")
        return json_error(message=f"Error promoting to admin: {e!s}", error_type="Operation failed")
