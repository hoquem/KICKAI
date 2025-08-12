#!/usr/bin/env python3
"""
Team Member Tools - Native CrewAI Implementation

This module provides tools for team member management operations using ONLY CrewAI native patterns.
"""


from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container


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
    Register a new team member.

    :param name: Name of the team member
    :type name: str
    :param telegram_id: Telegram ID of the team member
    :type telegram_id: int
    :param phone_number: Phone number of the team member
    :type phone_number: str
    :param role: Role of the team member (e.g., Coach, Manager, Assistant)
    :type role: str
    :param team_id: Team ID for context
    :type team_id: str
    :param is_admin: Whether the member is an admin (default: False)
    :type is_admin: bool
    :return: Registration status and team member details
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not name or name.strip() == "":
        return "❌ Name is required to register team member."

    if not telegram_id:
        return "❌ Telegram ID is required to register team member."

    if not phone_number or phone_number.strip() == "":
        return "❌ Phone number is required to register team member."

    if not role or role.strip() == "":
        return "❌ Role is required to register team member."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to register team member."

    try:
        # Get service using simple container access
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return "❌ Team member service is temporarily unavailable. Please try again later."

        # telegram_id is already an int
        telegram_id_int = telegram_id

        # is_admin is already a boolean
        is_admin_bool = is_admin

        # Create team member entity
        from kickai.features.team_administration.domain.entities.team_member import TeamMember

        team_member = TeamMember.create_from_telegram(
            team_id=team_id,
            telegram_id=telegram_id_int,
            name=name,
            username=None,
            is_admin=is_admin_bool,
        )

        # Apply provided details
        team_member.phone_number = phone_number
        team_member.role = role
        team_member.is_admin = is_admin_bool

        # Register team member
        import asyncio
        created_id = asyncio.run(team_member_service.create_team_member(team_member))

        if created_id:
            # Format as simple string response
            admin_status = "Admin" if is_admin_bool else "Member"
            result = "✅ Team Member Registered Successfully!\\n\\n"
            result += f"• Name: {name}\\n"
            result += f"• Role: {role}\\n"
            result += f"• Status: {admin_status}\\n"
            result += f"• Phone: {phone_number}\\n"
            result += f"• Telegram ID: {telegram_id_int}\\n"
            result += f"• Team: {team_id}\\n"
            result += f"• Member ID: {created_id}\\n\\n"
            result += f"🎉 Welcome to the team, {name}!"
            return result
        else:
            return "❌ Failed to register team member. Please try again."

    except Exception as e:
        logger.error(f"Failed to register team member: {e}")
        return f"❌ Failed to register team member: {e!s}"


@tool("get_my_team_member_status")
def get_my_team_member_status(team_id: str, telegram_id: int) -> str:
    """
    Get the current user's team member status.

    :param team_id: Team ID for context
    :type team_id: str
    :param telegram_id: Telegram ID of the user
    :type telegram_id: int
    :return: Current user's team member status information
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get team member status."

    if not telegram_id:
        return "❌ Telegram ID is required to get team member status."

    try:
        # Get service using simple container access
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return "❌ Team member service is temporarily unavailable. Please try again later."

        # Get team member status
        status = team_member_service.get_my_status_sync(str(telegram_id), team_id)

        # Return simple string response
        return status if status else "❌ Team member status not found."

    except Exception as e:
        logger.error(f"Failed to get team member status: {e}")
        return f"❌ Failed to get team member status: {e!s}"


@tool("get_team_members")
def get_team_members(team_id: str, role: str = "") -> str:
    """
    Get all team members for a team.

    :param team_id: Team ID for context
    :type team_id: str
    :param role: Optional role filter (leave empty for all members)
    :type role: str
    :return: List of team members
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get team members."

    try:
        # Get service using simple container access
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return "❌ Team member service is temporarily unavailable. Please try again later."

        # Get team members
        if role and role.strip() != "":
            members = team_member_service.get_team_members_by_role_sync(team_id, role.strip())
        else:
            members = team_member_service.get_team_members_by_team_sync(team_id)

        if not members:
            filter_text = f" with role '{role}'" if role and role.strip() != "" else ""
            return f"👥 Team Members (Team: {team_id})\\n\\nNo team members found{filter_text}."

        # Format as simple string response
        filter_text = f" - {role} Role" if role and role.strip() != "" else ""
        result = f"👥 Team Members{filter_text} (Team: {team_id})\\n\\n"

        for member in members:
            admin_emoji = "👑" if member.is_admin else "👤"
            role_text = member.role if member.role else "No role"
            result += f"{admin_emoji} {member.name or 'Unknown'} - {role_text}\\n"

        result += f"\\nTotal Members: {len(members)}"
        return result

    except Exception as e:
        logger.error(f"Failed to get team members: {e}")
        return f"❌ Failed to get team members: {e!s}"


@tool("add_team_member_role")
def add_team_member_role(telegram_id: int, team_id: str, role: str) -> str:
    """
    Add a role to a team member.

    :param telegram_id: Telegram ID of the team member
    :type telegram_id: int
    :param team_id: Team ID for context
    :type team_id: str
    :param role: Role to add
    :type role: str
    :return: Role addition status
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not telegram_id:
        return "❌ Telegram ID is required to add role."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to add role."

    if not role or role.strip() == "":
        return "❌ Role is required to add to team member."

    try:
        # Get service using simple container access
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return "❌ Team member service is temporarily unavailable. Please try again later."

        # Add role to team member
        success = team_member_service.add_role_to_member_sync(str(telegram_id), team_id, role)

        if success:
            return f"✅ Role Added Successfully\\n\\n• Member: {telegram_id}\\n• Role: {role}\\n• Team: {team_id}\\n\\nRole '{role}' has been added to the team member."
        else:
            return f"❌ Failed to add role '{role}' to team member {telegram_id}. Please check if the member exists and try again."

    except Exception as e:
        logger.error(f"Failed to add role: {e}")
        return f"❌ Failed to add role: {e!s}"


@tool("remove_team_member_role")
def remove_team_member_role(telegram_id: int, team_id: str, role: str) -> str:
    """
    Remove a role from a team member.

    :param telegram_id: Telegram ID of the team member
    :type telegram_id: int
    :param team_id: Team ID for context
    :type team_id: str
    :param role: Role to remove
    :type role: str
    :return: Role removal status
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not telegram_id:
        return "❌ Telegram ID is required to remove role."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to remove role."

    if not role or role.strip() == "":
        return "❌ Role is required to remove from team member."

    try:
        # Get service using simple container access
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return "❌ Team member service is temporarily unavailable. Please try again later."

        # Remove role from team member
        success = team_member_service.remove_role_from_member_sync(str(telegram_id), team_id, role)

        if success:
            return f"✅ Role Removed Successfully\\n\\n• Member: {telegram_id}\\n• Role: {role}\\n• Team: {team_id}\\n\\nRole '{role}' has been removed from the team member."
        else:
            return f"❌ Failed to remove role '{role}' from team member {telegram_id}. Please check if the member and role exist."

    except Exception as e:
        logger.error(f"Failed to remove role: {e}")
        return f"❌ Failed to remove role: {e!s}"


@tool("promote_team_member_to_admin")
def promote_team_member_to_admin(telegram_id: int, team_id: str, promoted_by: int) -> str:
    """
    Promote a team member to admin status.

    :param telegram_id: Telegram ID of the team member to promote
    :type telegram_id: int
    :param team_id: Team ID for context
    :type team_id: str
    :param promoted_by: Telegram ID of the person making the promotion
    :type promoted_by: int
    :return: Promotion status
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not telegram_id:
        return "❌ Telegram ID is required to promote team member."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to promote team member."

    if not promoted_by:
        return "❌ Promoter Telegram ID is required for promotion."

    try:
        # Get service using simple container access
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")

        if not team_member_service:
            return "❌ Team member service is temporarily unavailable. Please try again later."

        # Promote team member to admin
        success = team_member_service.promote_to_admin_sync(str(telegram_id), team_id, str(promoted_by))

        if success:
            return f"👑 Admin Promotion Successful\\n\\n• Promoted Member: {telegram_id}\\n• Promoted By: {promoted_by}\\n• Team: {team_id}\\n\\nTeam member has been promoted to admin status."
        else:
            return f"❌ Failed to promote team member {telegram_id} to admin. Please check permissions and try again."

    except Exception as e:
        logger.error(f"Failed to promote to admin: {e}")
        return f"❌ Failed to promote to admin: {e!s}"
