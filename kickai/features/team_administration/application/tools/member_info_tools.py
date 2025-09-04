"""Team Member Information Tools - CrewAI Clean Architecture

This module contains CrewAI tools for team member information with semantic naming.
These tools follow the CrewAI semantic convention and Clean Architecture principles.
All framework dependencies are confined to this application layer.
"""


from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import MemberRole

# Constants for role priority sorting
MEMBER_ROLE_PRIORITY = {
    MemberRole.ADMIN.value: 1,
    MemberRole.LEADERSHIP.value: 2,
    MemberRole.CLUB_ADMINISTRATOR.value: 3,
    MemberRole.TEAM_MANAGER.value: 4,
    MemberRole.COACH.value: 5,
    MemberRole.ASSISTANT_COACH.value: 6,
    MemberRole.TEAM_MEMBER.value: 7,
}


@tool("get_member_by_identifier")
async def get_member_by_identifier(
    team_id: str,
    member_identifier: str,
    telegram_id: str = "",
    telegram_username: str = "system",
    chat_type: str = "main",
) -> str:
    """
    Retrieve designated team member's administrative profile and permissions.

    Provides comprehensive information about specified team member including
    roles, permissions, contact details, and current participation status.

    Use when: Individual member information lookup is required
    Required: Team administrative access

    Returns: Member administrative profile and status details
    """
    try:
        # Only validate required parameters for this tool
        if not team_id.strip():
            return "❌ team_id is required"
        if not member_identifier.strip():
            return "❌ member_identifier is required"

        logger.info(f"👥 Getting member info for '{member_identifier}' in team {team_id}")

        # Get container and service
        container = get_container()

        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)
            if not team_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team service: {e}")
            return "❌ Team member service is not available"

        # Search for member using comprehensive strategy
        try:
            member = await team_service.find_team_member_by_identifier(member_identifier, team_id)
            if not member:
                return f"❌ Team member not found: {member_identifier}\n\n💡 Check the member ID, name, phone number, or username and try again"
        except Exception as e:
            logger.error(f"❌ Error finding member by identifier {member_identifier}: {e}")
            return f"❌ Failed to retrieve member information: {e!s}"

        # Format member information as clean text
        info_text = f"👥 {member.name} - Team Member Information\n\n"
        info_text += f"🆔 Member ID: {member.member_id or 'N/A'}\n"
        info_text += f"📞 Phone: {member.phone_number or 'Not provided'}\n"
        info_text += f"📧 Email: {getattr(member, 'email', 'Not provided')}\n"
        info_text += f"🏢 Role: {member.role}\n"
        info_text += f"📊 Status: {member.status}\n"
        info_text += f"🏗️ Team: {member.team_id}\n"

        # Add permissions if available
        if hasattr(member, "permissions") and member.permissions:
            permissions = (
                ", ".join(member.permissions)
                if isinstance(member.permissions, list)
                else str(member.permissions)
            )
            info_text += f"🔑 Permissions: {permissions}\n"

        # Add timestamps
        if hasattr(member, "created_at") and member.created_at:
            info_text += f"📅 Created: {member.created_at!s}\n"
        if hasattr(member, "updated_at") and member.updated_at:
            info_text += f"🔄 Updated: {member.updated_at!s}"

        return info_text

    except Exception as e:
        logger.error(f"❌ Error getting member info for '{member_identifier}': {e}")
        return f"❌ Failed to retrieve member information: {e!s}"


@tool("list_members_all")
async def list_members_all(
    team_id: str, telegram_id: str = "", telegram_username: str = "system", chat_type: str = "main"
) -> str:
    """
    Retrieve complete team administrative roster.

    Provides comprehensive overview of all team members with their roles,
    status, and administrative permissions for team governance review.

    Use when: Administrative roster review is needed
    Required: Team administrative access

    Returns: Team administrative roster summary
    """
    try:
        # Only validate required parameters for this tool
        if not team_id.strip():
            return "❌ team_id is required"

        container = get_container()

        # Get team member service with availability check
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)
            if not team_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team service: {e}")
            return "❌ Team member service is not available"

        # Get all team members with graceful error handling
        try:
            members = await team_service.get_team_members_by_team(team_id)
        except Exception as e:
            logger.warning(f"⚠️ Team service operation failed: {e}")
            return f"⚠️ Unable to retrieve team members: {e!s}"

        if not members:
            return f"👥 No team members found in team {team_id}"

        # Sort by role priority, then by name
        members.sort(
            key=lambda x: (
                MEMBER_ROLE_PRIORITY.get(x.role.lower(), 999),  # Unknown roles go last
                (x.name or "").lower(),
            )
        )

        # Format as clean text (no markdown)
        list_text = f"👥 Team Members ({len(members)} total)\n\n"

        for i, member in enumerate(members, 1):
            list_text += f"{i}. {member.name or 'Unnamed'}\n"
            list_text += f"   🏢 Role: {member.role}\n"
            list_text += f"   📊 Status: {member.status}\n"
            if member.phone_number:
                list_text += f"   📞 Phone: {member.phone_number}\n"
            list_text += "\n"

        return list_text.strip()

    except Exception as e:
        logger.error(f"❌ Error getting team members: {e}")
        return f"❌ Failed to get team members: {e!s}"


@tool("get_member_update_help")
async def get_member_update_help(
    telegram_id: str = "",
    team_id: str = "",
    telegram_username: str = "system",
    chat_type: str = "main",
) -> str:
    """
    Provide guidance for team member information updates.

    Delivers comprehensive assistance on available member profile fields,
    update formats, and modification procedures for administrative operations.

    Use when: Administrative guidance for member updates is needed
    Required: Team administrative access
    Context: Member data management workflow

    Returns: Member update guidance and procedures
    """
    try:
        # No parameter validation needed - this returns static help text
        help_text = "📋 Team Member Update Help\n\n"
        help_text += "🔧 Member Information Management:\n\n"

        help_text += "📝 Profile Updates:\n"
        help_text += "   Individual field modifications available\n"
        help_text += "   Batch field updates supported\n\n"

        help_text += "🏷️ Updatable Fields:\n"
        help_text += "   • name - Member's full name\n"
        help_text += "   • role - admin, manager, coach, member\n"
        help_text += "   • status - active, inactive, pending\n"
        help_text += "   • phone_number - Contact phone\n"
        help_text += "   • email - Email address\n\n"

        help_text += "🔑 Administrative Operations:\n"
        help_text += "   Role promotions and demotions available\n"
        help_text += "   Permission level adjustments supported\n\n"

        help_text += "ℹ️ Access Requirements:\n"
        help_text += "   • Administrative privileges required\n"
        help_text += "   • Member identification by name or ID\n"
        help_text += "   • Changes tracked for audit purposes"

        return help_text

    except Exception as e:
        logger.error(f"❌ Error getting member update help: {e}")
        return f"❌ Failed to get member update help: {e!s}"
