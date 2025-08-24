#!/usr/bin/env python3
"""
Team Administration Tools - Clean Architecture Application Layer

This module provides CrewAI tools for team administration and role management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Dict, Any
from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.team_administration.domain.services.team_member_management_service import TeamMemberManagementService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.tool_helpers import create_json_response


@tool("add_team_member_role", result_as_answer=True)
async def add_team_member_role(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_id: str,
    role: str
) -> str:
    """
    Add a role to a team member.

    This tool serves as the application boundary for role assignment functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        member_id: ID of the team member to assign role to
        role: Role to assign (e.g., 'coach', 'manager', 'assistant')

    Returns:
        JSON formatted response with role assignment result
    """
    try:
        logger.info(f"🎭 Adding role '{role}' to member {member_id} by {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not member_id or not role:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Both member ID and role are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        management_service = container.get_service(TeamMemberManagementService)

        if not management_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="TeamMemberManagementService is not available"
            )

        # Execute domain operation
        result = await management_service.add_role_to_member(member_id, role)

        if result:
            response_data = {
                "member_id": member_id,
                "role_added": role,
                "team_id": team_id,
                "message": f"✅ Role '{role}' added to team member {member_id} successfully"
            }

            logger.info(f"✅ Role '{role}' added to member {member_id} by {username}")
            return create_json_response(ResponseStatus.SUCCESS, data=response_data)
        else:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Failed to add role '{role}' to member {member_id}"
            )

    except Exception as e:
        logger.error(f"❌ Error adding role '{role}' to member {member_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to add role: {e}")


@tool("remove_team_member_role", result_as_answer=True)
async def remove_team_member_role(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_id: str,
    role: str
) -> str:
    """
    Remove a role from a team member.

    This tool serves as the application boundary for role removal functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        member_id: ID of the team member to remove role from
        role: Role to remove

    Returns:
        JSON formatted response with role removal result
    """
    try:
        logger.info(f"🎭 Removing role '{role}' from member {member_id} by {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not member_id or not role:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Both member ID and role are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        management_service = container.get_service(TeamMemberManagementService)

        if not management_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="TeamMemberManagementService is not available"
            )

        # Execute domain operation
        result = await management_service.remove_role_from_member(member_id, role)

        if result:
            response_data = {
                "member_id": member_id,
                "role_removed": role,
                "team_id": team_id,
                "message": f"✅ Role '{role}' removed from team member {member_id} successfully"
            }

            logger.info(f"✅ Role '{role}' removed from member {member_id} by {username}")
            return create_json_response(ResponseStatus.SUCCESS, data=response_data)
        else:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Failed to remove role '{role}' from member {member_id}"
            )

    except Exception as e:
        logger.error(f"❌ Error removing role '{role}' from member {member_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to remove role: {e}")


@tool("promote_team_member_to_admin", result_as_answer=True)
async def promote_team_member_to_admin(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_id: str
) -> str:
    """
    Promote a team member to admin status.

    This tool serves as the application boundary for admin promotion functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        member_id: ID of the team member to promote

    Returns:
        JSON formatted response with promotion result
    """
    try:
        logger.info(f"👑 Promoting member {member_id} to admin by {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not member_id:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Member ID is required for promotion"
            )

        # Get required services from container (application boundary)
        container = get_container()
        management_service = container.get_service(TeamMemberManagementService)

        if not management_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="TeamMemberManagementService is not available"
            )

        # Execute domain operation
        result = await management_service.promote_member_to_admin(member_id)

        if result:
            response_data = {
                "member_id": member_id,
                "team_id": team_id,
                "promoted_by": username,
                "message": f"✅ Team member {member_id} promoted to admin successfully"
            }

            logger.info(f"✅ Member {member_id} promoted to admin by {username}")
            return create_json_response(ResponseStatus.SUCCESS, data=response_data)
        else:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Failed to promote member {member_id} to admin"
            )

    except Exception as e:
        logger.error(f"❌ Error promoting member {member_id} to admin: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to promote member: {e}")


@tool("create_team", result_as_answer=True)
async def create_team(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    team_name: str,
    admin_user_id: str
) -> str:
    """
    Create a new team.

    This tool serves as the application boundary for team creation functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Creator's Telegram ID
        team_id: Unique team identifier
        username: Creator's username for logging
        chat_type: Chat type context
        team_name: Name of the new team
        admin_user_id: ID of the user who will be the team admin

    Returns:
        JSON formatted response with team creation result
    """
    try:
        logger.info(f"🏆 Creating team '{team_name}' (ID: {team_id}) by {username} ({telegram_id})")

        # Validate inputs at application boundary
        if not team_name or not admin_user_id:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Both team name and admin user ID are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        team_service = container.get_service(TeamService)

        if not team_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="TeamService is not available"
            )

        # Execute domain operation (delegate to existing create_team function)
        from kickai.features.team_administration.domain.tools.team_management_tools import create_team as domain_create_team
        result = await domain_create_team(team_name, team_id, admin_user_id)

        logger.info(f"✅ Team '{team_name}' created by {username}")
        return result  # Domain function already returns proper JSON response

    except Exception as e:
        logger.error(f"❌ Error creating team '{team_name}': {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to create team: {e}")


@tool("update_team_member_field", result_as_answer=True)
async def update_team_member_field(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    field: str,
    value: str
) -> str:
    """
    Update a single field for a team member.

    This tool serves as the application boundary for team member field updates.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team ID (required)
        username: Team member's username
        chat_type: Chat type context
        field: Field name to update
        value: New value for the field

    Returns:
        JSON formatted response with update result
    """
    try:
        logger.info(f"🔄 Updating team member field '{field}' for {username} ({telegram_id})")

        # Delegate to domain service (which was converted from tool to function)
        from kickai.features.team_administration.domain.tools.team_member_update_tools import update_team_member_field as domain_update_field
        result = await domain_update_field(telegram_id, team_id, username, chat_type, field, value)

        logger.info(f"✅ Team member field '{field}' updated for {username}")
        return result  # Domain function already returns proper JSON response

    except Exception as e:
        logger.error(f"❌ Error updating team member field '{field}': {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to update field: {e}")


@tool("update_team_member_multiple_fields", result_as_answer=True)
async def update_team_member_multiple_fields(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    field_updates: Dict[str, Any]
) -> str:
    """
    Update multiple fields for a team member in a single operation.

    This tool serves as the application boundary for team member multi-field updates.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team ID (required)
        username: Team member's username
        chat_type: Chat type context
        field_updates: Dictionary of field names to new values

    Returns:
        JSON formatted response with update result
    """
    try:
        logger.info(f"🔄 Updating multiple team member fields for {username} ({telegram_id})")

        # Delegate to domain service (which was converted from tool to function)
        from kickai.features.team_administration.domain.tools.team_member_update_tools import update_team_member_multiple_fields as domain_update_fields
        result = await domain_update_fields(telegram_id, team_id, username, chat_type, field_updates)

        logger.info(f"✅ Multiple team member fields updated for {username}")
        return result  # Domain function already returns proper JSON response

    except Exception as e:
        logger.error(f"❌ Error updating multiple team member fields: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to update fields: {e}")


@tool("get_team_member_update_help", result_as_answer=True)
async def get_team_member_update_help(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get help information about available team member update fields.

    This tool serves as the application boundary for team member update help.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team ID (required)
        username: Team member's username
        chat_type: Chat type context

    Returns:
        JSON formatted help information
    """
    try:
        logger.info(f"📖 Getting team member update help for {username} ({telegram_id})")

        # Delegate to domain service (which was converted from tool to function)
        from kickai.features.team_administration.domain.tools.team_member_update_tools import get_team_member_update_help as domain_get_help
        result = await domain_get_help(telegram_id, team_id, username, chat_type)

        logger.info(f"✅ Team member update help retrieved for {username}")
        return result  # Domain function already returns proper JSON response

    except Exception as e:
        logger.error(f"❌ Error getting team member update help: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get help: {e}")


@tool("get_team_member_current_info", result_as_answer=True)
async def get_team_member_current_info(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get current team member information before making updates.

    This tool serves as the application boundary for team member info retrieval.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team ID (required)
        username: Team member's username
        chat_type: Chat type context

    Returns:
        JSON formatted current team member information
    """
    try:
        logger.info(f"📋 Getting current team member info for {username} ({telegram_id})")

        # Delegate to domain service (which was converted from tool to function)
        from kickai.features.team_administration.domain.tools.team_member_update_tools import get_team_member_current_info as domain_get_info
        result = await domain_get_info(telegram_id, team_id, username, chat_type)

        logger.info(f"✅ Current team member info retrieved for {username}")
        return result  # Domain function already returns proper JSON response

    except Exception as e:
        logger.error(f"❌ Error getting team member current info: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get info: {e}")


@tool("update_other_team_member", result_as_answer=True)
async def update_other_team_member(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    target_member_id: str,
    field: str,
    value: str
) -> str:
    """
    Update another team member's information (admin-only operation).

    This tool serves as the application boundary for admin team member updates.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID
        team_id: Team ID (required)
        username: Admin's username
        chat_type: Chat type context (should be 'leadership')
        target_member_id: ID of the team member to update
        field: Field name to update
        value: New value for the field

    Returns:
        JSON formatted response with update result
    """
    try:
        logger.info(f"🔄 Admin {username} updating member {target_member_id} field '{field}'")

        # Delegate to domain service (which was converted from tool to function)
        from kickai.features.team_administration.domain.tools.team_member_update_tools import update_other_team_member as domain_update_other
        result = await domain_update_other(telegram_id, team_id, username, chat_type, target_member_id, field, value)

        logger.info(f"✅ Admin update completed by {username}")
        return result  # Domain function already returns proper JSON response

    except Exception as e:
        logger.error(f"❌ Error in admin update operation: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to update team member: {e}")