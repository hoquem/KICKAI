#!/usr/bin/env python3
"""
Team Member Update Tools

This module provides CrewAI tools for team members to update their personal information.
These tools include field validation, admin permission checks, and bidirectional sync 
with linked Player records.
"""

from typing import Dict, Any
from loguru import logger
from crewai.tools import tool

from kickai.core.dependency_container import get_container
from kickai.core.enums import ChatType
from kickai.utils.tool_validation import create_tool_response
from kickai.utils.field_validation import FieldValidator, ValidationError
from kickai.features.shared.domain.services.linked_record_sync_service import linked_record_sync_service


def _is_admin_user(chat_type: str, team_member: Any) -> bool:
    """
    Check if the current user has admin privileges.
    
    Args:
        chat_type: Type of chat the command was issued from
        team_member: Team member object
        
    Returns:
        True if user has admin privileges
    """
    # Admin privileges if in leadership chat and has admin role
    is_leadership_chat = chat_type.lower() == ChatType.LEADERSHIP.value
    is_admin_role = hasattr(team_member, 'role') and team_member.role and 'admin' in team_member.role.lower()
    
    return is_leadership_chat and is_admin_role


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
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
    
    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team identifier
        username: Team member's username
        chat_type: Type of chat (should be 'leadership' for team members)
        field: Field name to update (phone, email, role, emergency_contact_name, etc.)
        value: New value for the field
        
    Returns:
        JSON response with success status and details
    """
    try:
        logger.info(f"🔄 Updating team member field: {field} for telegram_id: {telegram_id}")
        
        # Get team member service
        container = get_container()
        from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
        team_member_service = container.get_service(ITeamMemberService)
        if not team_member_service:
            return create_tool_response(False, "Team member service not available"
            )
        
        # Find the team member
        team_members = await team_member_service.get_members_by_telegram_id(telegram_id)
        if not team_members:
            return create_tool_response(False, "Team member not found. Please contact an administrator."
            )
        
        team_member = team_members[0]  # Get the first (should be only) team member
        logger.info(f"📋 Updating team member {team_member.member_id} field: {field}")
        
        # Check admin privileges for admin-only operations
        is_admin = _is_admin_user(chat_type, team_member)
        
        # Validate the field and value with admin context
        try:
            normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                field, value, 'team_member', current_user_is_admin=is_admin
            )
        except ValidationError as e:
            logger.warning(f"❌ Validation error for field {field}: {e}")
            return create_tool_response(False, str(e)
            )
        
        # Update the team member field
        old_value = getattr(team_member, normalized_field, None)
        setattr(team_member, normalized_field, validated_value)
        
        # Save the updated team member
        updated_team_member = await team_member_service.update_team_member(team_member)
        
        logger.info(f"✅ Successfully updated team member field {normalized_field}")
        
        # Sync with linked Player record
        sync_result = await linked_record_sync_service.sync_team_member_to_player(
            telegram_id, {normalized_field: validated_value}
        )
        
        # Create success response
        response_data = {
            'member_id': updated_team_member.member_id,
            'field': normalized_field,
            'old_value': old_value,
            'new_value': validated_value,
            'sync_summary': linked_record_sync_service.create_sync_summary(
                sync_result, 'team_member', 'player'
            )
        }
        
        return create_tool_response(True, f"Updated {normalized_field} successfully",
            data=response_data
        )
        
    except (RuntimeError, AttributeError, KeyError, ValueError) as e:
        from kickai.features.team_administration.domain.exceptions import TeamMemberUpdateError
        logger.error(f"❌ Error updating team member field: {e}")
        update_error = TeamMemberUpdateError(str(telegram_id), field, str(e))
        return create_tool_response(False, f"Failed to update field: {update_error.message}"
        )


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def update_team_member_multiple_fields(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    field_updates: Dict[str, Any]
) -> str:
    """
    Update multiple fields for a team member in a single operation.
    
    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team identifier  
        username: Team member's username
        chat_type: Type of chat (should be 'leadership' for team members)
        field_updates: Dictionary of field names to new values
        
    Returns:
        JSON response with success status and details
    """
    try:
        logger.info(f"🔄 Updating multiple team member fields for telegram_id: {telegram_id}")
        logger.info(f"📝 Fields to update: {list(field_updates.keys())}")
        
        # Get team member service
        container = get_container()
        from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
        team_member_service = container.get_service(ITeamMemberService)
        if not team_member_service:
            return create_tool_response(False, "Team member service not available"
            )
        
        # Find the team member
        team_members = await team_member_service.get_members_by_telegram_id(telegram_id)
        if not team_members:
            return create_tool_response(False, "Team member not found. Please contact an administrator."
            )
        
        team_member = team_members[0]
        logger.info(f"📋 Updating team member {team_member.member_id} with {len(field_updates)} fields")
        
        # Check admin privileges
        is_admin = _is_admin_user(chat_type, team_member)
        
        # Validate all fields first
        validated_updates = {}
        validation_errors = []
        
        for field, value in field_updates.items():
            try:
                normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                    field, str(value), 'team_member', current_user_is_admin=is_admin
                )
                validated_updates[normalized_field] = validated_value
            except ValidationError as e:
                validation_errors.append(f"{field}: {str(e)}")
        
        # If there are validation errors, return them
        if validation_errors:
            logger.warning(f"❌ Validation errors: {validation_errors}")
            return create_tool_response(False, "Field validation failed",
                data={'validation_errors': validation_errors}
            )
        
        # Update all validated fields
        updated_fields = {}
        for normalized_field, validated_value in validated_updates.items():
            old_value = getattr(team_member, normalized_field, None)
            setattr(team_member, normalized_field, validated_value)
            updated_fields[normalized_field] = {
                'old_value': old_value,
                'new_value': validated_value
            }
        
        # Save the updated team member
        updated_team_member = await team_member_service.update_team_member(team_member)
        
        logger.info(f"✅ Successfully updated {len(validated_updates)} team member fields")
        
        # Sync with linked Player record
        sync_result = await linked_record_sync_service.sync_team_member_to_player(
            telegram_id, validated_updates
        )
        
        # Create success response
        response_data = {
            'member_id': updated_team_member.member_id,
            'updated_fields': updated_fields,
            'sync_summary': linked_record_sync_service.create_sync_summary(
                sync_result, 'team_member', 'player'
            )
        }
        
        return create_tool_response(True, f"Updated {len(validated_updates)} fields successfully",
            data=response_data
        )
        
    except (RuntimeError, AttributeError, KeyError, ValueError) as e:
        from kickai.features.team_administration.domain.exceptions import TeamMemberUpdateError
        logger.error(f"❌ Error updating multiple team member fields: {e}")
        update_error = TeamMemberUpdateError(str(telegram_id), "multiple_fields", str(e))
        return create_tool_response(False, f"Failed to update fields: {update_error.message}"
        )


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_team_member_update_help(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get help information about available team member update fields.
    
    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team identifier
        username: Team member's username
        chat_type: Type of chat
        
    Returns:
        JSON response with help information
    """
    try:
        logger.info(f"📖 Getting team member update help for telegram_id: {telegram_id}")
        
        # Check if user has admin privileges for contextualized help
        container = get_container()
        from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
        team_member_service = container.get_service(ITeamMemberService)
        
        is_admin = False
        if team_member_service:
            team_members = await team_member_service.get_members_by_telegram_id(telegram_id)
            if team_members:
                is_admin = _is_admin_user(chat_type, team_members[0])
        
        # Generate help message with admin context
        help_message = FieldValidator.create_help_message('team_member', current_user_is_admin=is_admin)
        
        # Add usage examples
        examples = [
            "/update phone +447123456789",
            "/update email newadmin@team.com", 
            "/update role coach",
            "/update emergency_contact_name \"Jane Smith\"",
            "/update emergency_contact_phone \"+447987654321\""
        ]
        
        # Add admin-specific examples if user is admin
        if is_admin:
            examples.append("/update role admin  # Admin privileges required")
        
        help_message += "\n\n📚 Usage Examples:\n"
        for example in examples:
            help_message += f"• {example}\n"
        
        help_message += "\n💡 Tips:\n"
        help_message += "• Use quotes around values with spaces\n"
        help_message += "• Phone numbers can be in UK format: +447XXXXXXXXX or 07XXXXXXXXX\n"
        help_message += "• Changes to common fields (phone, email, emergency contact) will also update your player record if linked\n"
        
        if not is_admin:
            help_message += "• Admin role changes require administrator privileges\n"
        
        return create_tool_response(True, "Team member update help",
            data={'help_text': help_message, 'is_admin': is_admin}
        )
        
    except (RuntimeError, AttributeError, KeyError) as e:
        from kickai.features.shared.domain.exceptions import HelpSystemError
        logger.error(f"❌ Error getting team member update help: {e}")
        help_error = HelpSystemError(str(telegram_id), str(e))
        return create_tool_response(False, f"Failed to get help information: {help_error.message}"
        )


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_team_member_current_info(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get current team member information before making updates.
    
    Args:
        telegram_id: Team member's Telegram ID
        team_id: Team identifier
        username: Team member's username
        chat_type: Type of chat
        
    Returns:
        JSON response with current team member information
    """
    try:
        logger.info(f"📋 Getting current team member info for telegram_id: {telegram_id}")
        
        # Get team member service
        container = get_container()
        from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
        team_member_service = container.get_service(ITeamMemberService)
        if not team_member_service:
            return create_tool_response(False, "Team member service not available"
            )
        
        # Find the team member
        team_members = await team_member_service.get_members_by_telegram_id(telegram_id)
        if not team_members:
            return create_tool_response(False, "Team member not found. Please contact an administrator."
            )
        
        team_member = team_members[0]
        logger.info(f"📋 Retrieved info for team member {team_member.member_id}")
        
        # Create safe info dictionary (excluding sensitive data)
        team_member_info = {
            'member_id': team_member.member_id,
            'name': team_member.name,
            'phone_number': team_member.phone_number,
            'email': team_member.email,
            'role': team_member.role,
            'emergency_contact_name': getattr(team_member, 'emergency_contact_name', 'Not set'),
            'emergency_contact_phone': getattr(team_member, 'emergency_contact_phone', 'Not set'),
            'team_id': team_member.team_id,
            'status': team_member.status,
            'is_admin': _is_admin_user(chat_type, team_member)
        }
        
        return create_tool_response(True, "Current team member information",
            data={'team_member_info': team_member_info}
        )
        
    except (RuntimeError, AttributeError, KeyError, ValueError) as e:
        from kickai.features.team_administration.domain.exceptions import TeamMemberLookupError
        logger.error(f"❌ Error getting team member current info: {e}")
        lookup_error = TeamMemberLookupError(str(telegram_id), team_id, str(e))
        return create_tool_response(False, f"Failed to get team member information: {lookup_error.message}"
        )


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
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
    
    Args:
        telegram_id: Admin's Telegram ID
        team_id: Team identifier
        username: Admin's username
        chat_type: Type of chat (should be 'leadership')
        target_member_id: ID of the team member to update
        field: Field name to update
        value: New value for the field
        
    Returns:
        JSON response with success status and details
    """
    try:
        logger.info(f"🔄 Admin updating team member {target_member_id} field: {field}")
        
        # Get team member service
        container = get_container()
        from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
        team_member_service = container.get_service(ITeamMemberService)
        if not team_member_service:
            return create_tool_response(False, "Team member service not available"
            )
        
        # Verify admin permissions
        admin_members = await team_member_service.get_members_by_telegram_id(telegram_id)
        if not admin_members:
            return create_tool_response(False, "Administrator not found."
            )
        
        admin_member = admin_members[0]
        if not _is_admin_user(chat_type, admin_member):
            return create_tool_response(False, "This operation requires administrator privileges in the leadership chat."
            )
        
        # Find the target team member
        target_member = await team_member_service.get_team_member_by_id(target_member_id)
        if not target_member:
            return create_tool_response(False, f"Target team member {target_member_id} not found."
            )
        
        logger.info(f"📋 Admin {admin_member.member_id} updating {target_member.member_id}")
        
        # Validate the field and value with admin privileges
        try:
            normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                field, value, 'team_member', current_user_is_admin=True
            )
        except ValidationError as e:
            logger.warning(f"❌ Validation error for field {field}: {e}")
            return create_tool_response(False, str(e)
            )
        
        # Update the target member field
        old_value = getattr(target_member, normalized_field, None)
        setattr(target_member, normalized_field, validated_value)
        
        # Save the updated team member
        updated_member = await team_member_service.update_team_member(target_member)
        
        logger.info(f"✅ Admin successfully updated {target_member_id} field {normalized_field}")
        
        # Sync with linked Player record if target member has one
        sync_result = await linked_record_sync_service.sync_team_member_to_player(
            target_member.telegram_id, {normalized_field: validated_value}
        )
        
        # Create success response
        response_data = {
            'admin_member_id': admin_member.member_id,
            'target_member_id': target_member.member_id,
            'target_member_name': target_member.name,
            'field': normalized_field,
            'old_value': old_value,
            'new_value': validated_value,
            'sync_summary': linked_record_sync_service.create_sync_summary(
                sync_result, 'team_member', 'player'
            )
        }
        
        return create_tool_response(True, f"Updated {target_member.name}'s {normalized_field} successfully",
            data=response_data
        )
        
    except (RuntimeError, AttributeError, KeyError, ValueError) as e:
        from kickai.features.team_administration.domain.exceptions import TeamMemberUpdateError
        logger.error(f"❌ Error updating other team member: {e}")
        update_error = TeamMemberUpdateError(target_member_id, field, str(e))
        return create_tool_response(False, f"Failed to update team member: {update_error.message}"
        )