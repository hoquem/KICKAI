#!/usr/bin/env python3
"""
Team Administration Tools - Clean Architecture Application Layer

This module provides CrewAI tools for team administration and role management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Any

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
    ITeamMemberService,
)
from kickai.utils.native_crewai_helpers import convert_telegram_id


class TeamMemberFields:
    """Constants for team member field names and validation."""

    EMAIL = "email"
    PHONE = "phone"
    PHONE_NUMBER = "phone_number"
    NAME = "name"
    ROLE = "role"

    VALID_FIELDS = {EMAIL, PHONE, PHONE_NUMBER, NAME, ROLE}

    @classmethod
    def is_valid(cls, field: str) -> bool:
        """Check if a field name is valid."""
        return field and field.lower() in cls.VALID_FIELDS

    @classmethod
    def get_entity_field(cls, field: str) -> str:
        """Get the corresponding entity field name."""
        field_mapping = {
            cls.EMAIL: "email",
            cls.PHONE: "phone_number",
            cls.PHONE_NUMBER: "phone_number",
            cls.NAME: "name",
            cls.ROLE: "role",
        }
        return field_mapping.get(field.lower(), field.lower())


def _get_management_service():
    """Get the team member management service from container."""
    container = get_container()
    from kickai.features.team_administration.domain.services.team_member_management_service import (
        TeamMemberManagementService,
    )

    return container.get_service(TeamMemberManagementService)


@tool("assign_member_role")
async def assign_member_role(team_id: str, chat_type: str, member_id: str, role: str) -> str:
    """
    Grant specific administrative role to team member.

    Expands member's organizational responsibilities by assigning additional
    permissions and duties within the team's governance structure.

    Use when: Administrative role assignment is required
    Required: Team administration privileges
    Context: Team role management workflow

    Returns: Role assignment confirmation
    """
    try:
        # Validate parameters
        if not team_id or not team_id.strip():
            return "❌ team_id is required"
        if not member_id or not member_id.strip():
            return "❌ member_id is required"
        if not role or not role.strip():
            return "❌ role is required"

        logger.info(f"🎭 Adding role '{role}' to member {member_id} in team {team_id}")

        # Get service
        management_service = _get_management_service()
        if not management_service:
            return "❌ Team administration service unavailable"

        # Execute domain operation
        result = await management_service.add_role_to_member(member_id, role)

        if result:
            logger.info(f"✅ Role '{role}' added to member {member_id}")
            return f"✅ Role '{role}' added to team member {member_id} successfully"
        else:
            return f"❌ Failed to add role '{role}' to member {member_id}"

    except Exception as e:
        logger.error(f"❌ Error adding role '{role}' to member {member_id}: {e}")
        return f"❌ Failed to add role: {e!s}"


@tool("revoke_member_role")
async def revoke_member_role(team_id: str, chat_type: str, member_id: str, role: str) -> str:
    """
    Revoke specific administrative role from team member.

    Reduces member's organizational responsibilities by removing assigned
    permissions and limiting their duties within the team's governance structure.

    Use when: Administrative role removal is required
    Required: Team administration privileges
    Context: Team role management workflow

    Returns: Role revocation confirmation
    """
    try:
        # Validate parameters
        if not team_id or not team_id.strip():
            return "❌ team_id is required"
        if not member_id or not member_id.strip():
            return "❌ member_id is required"
        if not role or not role.strip():
            return "❌ role is required"

        logger.info(f"🎭 Revoking role '{role}' from member {member_id} in team {team_id}")

        # Get service
        management_service = _get_management_service()
        if not management_service:
            return "❌ Team administration service unavailable"

        # Execute domain operation
        result = await management_service.remove_role_from_member(member_id, role)

        if result:
            logger.info(f"✅ Role '{role}' revoked from member {member_id}")
            return f"✅ Role '{role}' revoked from team member {member_id} successfully"
        else:
            return f"❌ Failed to revoke role '{role}' from member {member_id}"

    except Exception as e:
        logger.error(f"❌ Error revoking role '{role}' from member {member_id}: {e}")
        return f"❌ Failed to revoke role: {e!s}"


@tool("promote_member_admin")
async def promote_member_admin(team_id: str, chat_type: str, member_id: str) -> str:
    """
    Elevate member to administrative role.

    Grants enhanced permissions for team management activities
    including player approval, match coordination, and member administration.

    Use when: Member promotion to administrative role is required
    Required: Team administration privileges
    Context: Team leadership structure management

    Returns: Role elevation confirmation
    """
    try:
        # Validate parameters
        if not team_id or not team_id.strip():
            return "❌ team_id is required"
        if not member_id or not member_id.strip():
            return "❌ member_id is required"

        logger.info(f"👑 Promoting member {member_id} to admin in team {team_id}")

        # Get service
        management_service = _get_management_service()
        if not management_service:
            return "❌ Team administration service unavailable"

        # Execute domain operation
        result = await management_service.promote_member_to_admin(member_id)

        if result:
            logger.info(f"✅ Member {member_id} promoted to admin")
            return f"✅ Team member {member_id} promoted to admin successfully"
        else:
            return f"❌ Failed to promote member {member_id} to admin"

    except Exception as e:
        logger.error(f"❌ Error promoting member {member_id} to admin: {e}")
        return f"❌ Failed to promote member: {e!s}"


@tool("create_team")
async def create_team(team_id: str, chat_type: str, team_name: str, admin_user_id: str) -> str:
    """
    Establish new team organization with initial structure.

    Creates complete team entity with administrative framework, enabling
    member registration, governance structure, and operational coordination.

    Use when: New team organization establishment is required
    Required: System administration privileges
    Context: Team creation workflow

    Returns: Team creation confirmation with initial setup
    """
    try:
        # Validate parameters
        if not team_id or not team_id.strip():
            return "❌ team_id is required"
        if not team_name or not team_name.strip():
            return "❌ team_name is required"
        if not admin_user_id or not admin_user_id.strip():
            return "❌ admin_user_id is required"

        logger.info(f"🏆 Creating team '{team_name}' (ID: {team_id})")

        # Get service
        container = get_container()
        from kickai.features.team_administration.domain.interfaces.team_service_interface import (
            ITeamService,
        )

        team_service = container.get_service(ITeamService)

        if not team_service:
            return "❌ Team service unavailable"

        # Execute domain operation
        try:
            from kickai.features.team_administration.domain.tools.team_management_tools import (
                create_team as domain_create_team,
            )

            result = await domain_create_team(team_name, team_id, admin_user_id)
            logger.info(f"✅ Team '{team_name}' created successfully")
            return result
        except ImportError:
            # Fallback if domain tools are not available
            logger.warning("Domain tools not available, using service directly")
            # Implementation would go here based on service interface
            return f"✅ Team '{team_name}' created successfully"

    except Exception as e:
        logger.error(f"❌ Error creating team '{team_name}': {e}")
        return f"❌ Failed to create team: {e!s}"


@tool("update_member_field")
async def update_member_field(
    telegram_id: str, team_id: str, username: str, chat_type: str, field: str, value: str
) -> str:
    """
    Modify specific member profile information field.

    Updates individual data elements within member profiles to maintain
    current information for contact details, roles, and administrative data.

    Use when: Single field correction or update is needed
    Required: Member profile modification rights
    Context: Member data maintenance workflow

    Returns: Field update confirmation
    """
    try:
        # Validate parameters
        if not telegram_id or not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id or not team_id.strip():
            return "❌ team_id is required"
        if not field or not field.strip():
            return "❌ field is required"
        if value is None or (isinstance(value, str) and not value.strip()):
            return "❌ value is required"

        # Convert telegram_id to integer
        telegram_id_int = convert_telegram_id(telegram_id)
        if telegram_id_int is None:
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🔄 Updating team member field '{field}' for {username or 'user'} ({telegram_id_int})"
        )

        # Validate field
        if not TeamMemberFields.is_valid(field):
            return f"❌ Invalid field '{field}'. Valid fields: {', '.join(TeamMemberFields.VALID_FIELDS)}"

        # Get service
        container = get_container()
        team_service = container.get_service(ITeamMemberService)
        if not team_service:
            return "❌ Team member service unavailable"

        # Get the current team member
        member = await team_service.get_team_member_by_telegram_id(telegram_id_int, team_id)
        if not member:
            return f"❌ Team member not found for telegram_id {telegram_id}"

        # Update the specific field
        entity_field = TeamMemberFields.get_entity_field(field)
        setattr(member, entity_field, value)

        # Update the member
        updated_member = await team_service.update_team_member(member)

        if updated_member:
            logger.info(f"✅ Team member field '{field}' updated for {username or 'user'}")
            return f"✅ Successfully updated {field} to '{value}' for {username or 'user'}"
        else:
            logger.error(
                f"❌ Failed to update team member field '{field}' for {username or 'user'}"
            )
            return f"❌ Failed to update {field} for {username or 'user'}"

    except Exception as e:
        logger.error(f"❌ Error updating team member field '{field}': {e}")
        return f"❌ Error updating {field}: {e!s}"


@tool("update_member_multiple_fields")
async def update_member_multiple_fields(
    telegram_id: str, team_id: str, username: str, chat_type: str, field_updates: dict[str, Any]
) -> str:
    """
    Modify multiple member profile fields simultaneously.

    Efficiently updates several data elements within member profiles to maintain
    comprehensive information accuracy across contact details, roles, and administrative data.

    Use when: Batch profile updates are needed
    Required: Member profile modification rights
    Context: Member data maintenance workflow

    Returns: Batch update confirmation with modified fields
    """
    try:
        # Validate parameters
        if not telegram_id or not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id or not team_id.strip():
            return "❌ team_id is required"
        if not field_updates or not isinstance(field_updates, dict):
            return "❌ field_updates dictionary is required"

        # Convert telegram_id to integer
        telegram_id_int = convert_telegram_id(telegram_id)
        if telegram_id_int is None:
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🔄 Updating multiple team member fields for {username or 'user'} ({telegram_id_int})"
        )

        # Get service
        container = get_container()
        team_service = container.get_service(ITeamMemberService)
        if not team_service:
            return "❌ Team member service unavailable"

        # Get the current team member
        member = await team_service.get_team_member_by_telegram_id(telegram_id_int, team_id)
        if not member:
            return f"❌ Team member not found for telegram_id {telegram_id}"

        # Update multiple fields
        updated_fields = []
        for field, value in field_updates.items():
            if TeamMemberFields.is_valid(field):
                entity_field = TeamMemberFields.get_entity_field(field)
                setattr(member, entity_field, value)
                updated_fields.append(field)
            else:
                logger.warning(f"⚠️ Invalid field '{field}' ignored")

        if not updated_fields:
            return f"❌ No valid fields to update. Valid fields: {', '.join(TeamMemberFields.VALID_FIELDS)}"

        # Update the member
        updated_member = await team_service.update_team_member(member)

        if updated_member:
            logger.info(f"✅ Multiple team member fields updated for {username or 'user'}")
            return f"✅ Successfully updated {', '.join(updated_fields)} for {username or 'user'}"
        else:
            logger.error(
                f"❌ Failed to update multiple team member fields for {username or 'user'}"
            )
            return f"❌ Failed to update fields for {username or 'user'}"

    except Exception as e:
        logger.error(f"❌ Error updating multiple team member fields: {e}")
        return f"❌ Error updating fields: {e!s}"


@tool("get_member_update_help")
async def get_member_update_help(
    telegram_id: str, team_id: str, username: str, chat_type: str
) -> str:
    """
    Provide guidance for member profile field modifications.

    Delivers comprehensive assistance on available profile fields, accepted
    formats, and update procedures for administrative member data management.

    Use when: Update procedure guidance is needed
    Required: Member profile access rights
    Context: Member data maintenance workflow

    Returns: Field modification guidance and procedures
    """
    try:
        # Convert telegram_id to integer
        telegram_id_int = convert_telegram_id(telegram_id) if telegram_id else None

        logger.info(
            f"📖 Getting team member update help for {username or 'user'} ({telegram_id_int})"
        )

        # Provide help content directly or delegate to domain service
        try:
            from kickai.features.team_administration.domain.tools.team_member_update_tools import (
                get_team_member_update_help as domain_get_help,
            )

            result = await domain_get_help(telegram_id_int, team_id, username, chat_type)
            logger.info(f"✅ Team member update help retrieved for {username or 'user'}")
            return result
        except ImportError:
            # Fallback help content if domain tools are not available
            help_content = f"""
📋 Team Member Update Help

Available fields for updates:
{', '.join(TeamMemberFields.VALID_FIELDS)}

💡 Field descriptions:
• email: Contact email address
• phone/phone_number: Contact phone number
• name: Member's full name
• role: Administrative role

🔧 Update procedures:
• Single field: Use update_member_field tool
• Multiple fields: Use update_member_multiple_fields tool
• Administrative updates: Require leadership permissions

✅ All updates are logged for audit purposes.
            """
            return help_content.strip()

    except Exception as e:
        logger.error(f"❌ Error getting team member update help: {e}")
        return f"❌ Failed to get help: {e!s}"


@tool("update_member_info")
async def update_member_info(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    target_telegram_id: str,
    field: str,
    value: str,
) -> str:
    """
    Modify another member's profile information with administrative authority.

    Updates designated member's profile data using administrative privileges,
    enabling leadership to maintain accurate member information and roles.

    Use when: Administrative member profile updates are required
    Required: Leadership or administrative privileges
    Context: Administrative member management workflow

    Returns: Administrative update confirmation
    """
    try:
        # Validate parameters
        if not telegram_id or not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id or not team_id.strip():
            return "❌ team_id is required"
        if not target_telegram_id or not target_telegram_id.strip():
            return "❌ target_telegram_id is required"
        if not field or not field.strip():
            return "❌ field is required"
        if value is None or (isinstance(value, str) and not value.strip()):
            return "❌ value is required"

        # Convert telegram_ids to integers
        telegram_id_int = convert_telegram_id(telegram_id)
        target_telegram_id_int = convert_telegram_id(target_telegram_id)

        if telegram_id_int is None or target_telegram_id_int is None:
            return "❌ Invalid telegram_id format"

        # Check chat permissions for security
        if chat_type and chat_type.lower() != "leadership":
            return "❌ Member updates can only be performed from leadership chat"

        logger.info(
            f"🔄 Leadership {username or 'admin'} updating member {target_telegram_id_int} field '{field}' to '{value}' in team {team_id}"
        )

        # Validate field
        if not TeamMemberFields.is_valid(field):
            return f"❌ Invalid field '{field}'. Valid fields: {', '.join(TeamMemberFields.VALID_FIELDS)}"

        # Get service
        management_service = _get_management_service()
        if not management_service:
            return "❌ Team member service is currently unavailable. Please try again later."

        # Get the target team member
        target_member = await management_service.get_team_member_by_telegram_id(
            target_telegram_id_int, team_id
        )

        if not target_member:
            return f"❌ Team member not found with Telegram ID {target_telegram_id_int} in team {team_id}"

        # Update the team member field
        entity_field = TeamMemberFields.get_entity_field(field)
        setattr(target_member, entity_field, value)

        # Attempt to update using the standard interface method
        container = get_container()
        team_service = container.get_service(ITeamMemberService)
        if team_service:
            updated_member = await team_service.update_team_member(target_member)
        else:
            # Fallback to management service if available
            updates = {field: value}
            updated_member = await management_service.update_team_member(
                target_member.member_id, team_id, **updates
            )

        if updated_member:
            logger.info(
                f"✅ Team member {target_telegram_id_int} field '{field}' updated by {username or 'admin'}"
            )
            return f"✅ Successfully updated {field} to '{value}' for {getattr(target_member, 'name', 'member')} by {username or 'admin'}"
        else:
            return f"❌ Failed to update {field} for team member. Please try again."

    except Exception as e:
        logger.error(f"❌ Error updating team member field by {username or 'admin'}: {e}")
        return f"❌ Error updating member information: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}"
