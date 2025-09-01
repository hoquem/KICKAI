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
from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService


class TeamMemberFields:
    """Constants for team member field names."""
    EMAIL = "email"
    PHONE = "phone"
    PHONE_NUMBER = "phone_number"
    NAME = "name"
    ROLE = "role"
    
    VALID_FIELDS = {EMAIL, PHONE, PHONE_NUMBER, NAME, ROLE}
    
    @classmethod
    def is_valid(cls, field: str) -> bool:
        """Check if a field name is valid."""
        return field.lower() in cls.VALID_FIELDS
    
    @classmethod
    def get_entity_field(cls, field: str) -> str:
        """Get the corresponding entity field name."""
        field_mapping = {
            cls.EMAIL: "email",
            cls.PHONE: "phone_number",
            cls.PHONE_NUMBER: "phone_number",
            cls.NAME: "name",
            cls.ROLE: "role"
        }
        return field_mapping.get(field.lower(), field.lower())


def create_tool_response(success: bool, message: str) -> str:
    """Create a standardized tool response."""
    if success:
        return f"✅ {message}"
    else:
        return f"❌ {message}"


@tool("create_member_role")
async def create_member_role(
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
        telegram_id: Admin's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        member_id: ID of the team member to assign role to
        role: Role to assign (e.g., 'coach', 'manager', 'assistant')

    Returns:
        JSON formatted response with role assignment result
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            member_id = params.get('member_id', '')
            role = params.get('role', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(
                        False, 
                        "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(
                False, 
                "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(
                False, 
                "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(
                False, 
                "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(
                False, 
                "Valid chat_type is required"
            )
        
        logger.info(f"🎭 Adding role '{role}' to member {member_id} by {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not member_id or not role:
            return create_tool_response(
                False,
                "Both member ID and role are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        from kickai.features.team_administration.domain.services.team_member_management_service import TeamMemberManagementService
        management_service = container.get_service(TeamMemberManagementService)

        if not management_service:
            return create_tool_response(False, "TeamMemberManagementService is not available"
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
            return create_tool_response(True, f"Role '{role}' added to member {member_id}", response_data)
        else:
            return create_tool_response(
                False,
                f"Failed to add role '{role}' to member {member_id}"
            )

    except Exception as e:
        logger.error(f"❌ Error adding role '{role}' to member {member_id}: {e}")
        return create_tool_response(False, f"Failed to add role: {e}")


@tool("remove_member_role")
async def remove_member_role(
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
            return create_tool_response(False, "Both member ID and role are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        from kickai.features.team_administration.domain.services.team_member_management_service import TeamMemberManagementService
        management_service = container.get_service(TeamMemberManagementService)

        if not management_service:
            return create_tool_response(False, "TeamMemberManagementService is not available"
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
            return create_tool_response(True, "Operation completed successfully", data=response_data)
        else:
            return create_tool_response(False, f"Failed to remove role '{role}' from member {member_id}"
            )

    except Exception as e:
        logger.error(f"❌ Error removing role '{role}' from member {member_id}: {e}")
        return create_tool_response(False, f"Failed to remove role: {e}")


@tool("promote_member_admin")
async def promote_member_admin(
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
            return create_tool_response(False, "Member ID is required for promotion"
            )

        # Get required services from container (application boundary)
        container = get_container()
        from kickai.features.team_administration.domain.services.team_member_management_service import TeamMemberManagementService
        management_service = container.get_service(TeamMemberManagementService)

        if not management_service:
            return create_tool_response(False, "TeamMemberManagementService is not available"
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
            return create_tool_response(True, "Operation completed successfully", data=response_data)
        else:
            return create_tool_response(False, f"Failed to promote member {member_id} to admin"
            )

    except Exception as e:
        logger.error(f"❌ Error promoting member {member_id} to admin: {e}")
        return create_tool_response(False, f"Failed to promote member: {e}")


@tool("create_team")
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
        telegram_id: Creator's Telegram ID or dictionary with all parameters
        team_id: Unique team identifier
        username: Creator's username for logging
        chat_type: Chat type context
        team_name: Name of the new team
        admin_user_id: ID of the user who will be the team admin

    Returns:
        JSON formatted response with team creation result
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            team_name = params.get('team_name', '')
            admin_user_id = params.get('admin_user_id', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(False, "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(False, "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(False, "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(False, "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(False, "Valid chat_type is required"
            )
        
        logger.info(f"🏆 Creating team '{team_name}' (ID: {team_id}) by {username} ({telegram_id})")

        # Validate inputs at application boundary
        if not team_name or not admin_user_id:
            return create_tool_response(False, "Both team name and admin user ID are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        from kickai.features.team_administration.domain.interfaces.team_service_interface import ITeamService
        team_service = container.get_service(ITeamService)

        if not team_service:
            return create_tool_response(False, "TeamService is not available"
            )

        # Execute domain operation (delegate to existing create_team function)
        from kickai.features.team_administration.domain.tools.team_management_tools import create_team as domain_create_team
        result = await domain_create_team(team_name, team_id, admin_user_id)

        logger.info(f"✅ Team '{team_name}' created by {username}")
        return result  # Domain function already returns proper JSON response

    except Exception as e:
        logger.error(f"❌ Error creating team '{team_name}': {e}")
        return create_tool_response(False, f"Failed to create team: {e}")


@tool("update_member_field")
async def update_member_field(
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
        Formatted response with update result
    """
    try:
        logger.info(f"🔄 Updating team member field '{field}' for {username} ({telegram_id})")

        # Get container and service
        container = get_container()
        team_service = container.get_service(ITeamMemberService)

        # Get the current team member
        member = await team_service.get_team_member_by_telegram_id(telegram_id, team_id)
        if not member:
            return create_tool_response(False, f"Team member not found for telegram_id {telegram_id}")

        # Validate field
        if not TeamMemberFields.is_valid(field):
            return create_tool_response(False, f"Invalid field '{field}'. Valid fields: {', '.join(TeamMemberFields.VALID_FIELDS)}")

        # Update the specific field
        entity_field = TeamMemberFields.get_entity_field(field)
        setattr(member, entity_field, value)

        # Update the member
        success = await team_service.update_team_member(member)
        
        if success:
            logger.info(f"✅ Team member field '{field}' updated for {username}")
            return create_tool_response(True, f"Successfully updated {field} to '{value}' for {username}")
        else:
            logger.error(f"❌ Failed to update team member field '{field}' for {username}")
            return create_tool_response(False, f"Failed to update {field} for {username}")

    except Exception as e:
        logger.error(f"❌ Error updating team member field '{field}': {e}")
        return create_tool_response(False, f"Error updating {field}: {str(e)}")


@tool("update_member_multiple")
async def update_member_multiple(
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
        Formatted response with update result
    """
    try:
        logger.info(f"🔄 Updating multiple team member fields for {username} ({telegram_id})")

        # Get container and service
        container = get_container()
        team_service = container.get_service(ITeamMemberService)

        # Get the current team member
        member = await team_service.get_team_member_by_telegram_id(telegram_id, team_id)
        if not member:
            return create_tool_response(False, f"Team member not found for telegram_id {telegram_id}")

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
            return create_tool_response(False, f"No valid fields to update. Valid fields: {', '.join(TeamMemberFields.VALID_FIELDS)}")

        # Update the member
        success = await team_service.update_team_member(member)
        
        if success:
            logger.info(f"✅ Multiple team member fields updated for {username}")
            return create_tool_response(True, f"Successfully updated {', '.join(updated_fields)} for {username}")
        else:
            logger.error(f"❌ Failed to update multiple team member fields for {username}")
            return create_tool_response(False, f"Failed to update fields for {username}")

    except Exception as e:
        logger.error(f"❌ Error updating multiple team member fields: {e}")
        return create_tool_response(False, f"Error updating fields: {str(e)}")


@tool("get_member_update_help")
async def get_member_update_help(
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
        return create_tool_response(False, f"Failed to get help: {e}")




@tool("update_member_info")
async def update_member_info(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    target_telegram_id: int,
    field: str,
    value: str
) -> str:
    """
    Update team member information (leadership only).

    This tool serves as the application boundary for team member updates.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        target_telegram_id: Telegram ID of the team member to update
        field: Field name to update (name, phone_number, role, etc.)
        value: New value for the field

    Returns:
        Plain text response with update result
    """
    try:
        # Handle CrewAI parameter dictionary passing
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            target_telegram_id = params.get('target_telegram_id', 0)
            field = params.get('field', '')
            value = params.get('value', '')
            
            # Type conversion with error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return "❌ Invalid admin telegram_id format"
                    
            if isinstance(target_telegram_id, str):
                try:
                    target_telegram_id = int(target_telegram_id)
                except (ValueError, TypeError):
                    return "❌ Invalid target_telegram_id format"
        
        # Parameter validation
        if not all([telegram_id, team_id, username, chat_type, target_telegram_id, field, value]):
            return "❌ Missing required parameters for member update"
        
        if chat_type.lower() != 'leadership':
            return "❌ Member updates can only be performed from leadership chat"

        logger.info(f"🔄 Leadership {username} updating member {target_telegram_id} field '{field}' to '{value}' in team {team_id}")

        # Get services from container
        container = get_container()
        from kickai.features.team_administration.domain.services.team_member_management_service import TeamMemberManagementService
        team_member_service = container.get_service(TeamMemberManagementService)
        
        if not team_member_service:
            return f"""❌ System Error

Team member service is currently unavailable. Please try again later.

Technical Details:
• Service: TeamMemberManagementService
• Admin: {username} ({telegram_id})
• Team: {team_id}"""

        # Get the target team member
        target_member = await team_member_service.get_team_member_by_telegram_id(target_telegram_id, team_id)
        
        if not target_member:
            return f"""❌ Team Member Not Found

No team member found with Telegram ID {target_telegram_id} in team {team_id}.

💡 What you can try:
• Verify the Telegram ID is correct
• Check if the member is registered in the team
• Use /list to see all team members"""

        # Update the team member field
        updates = {field: value}
        updated_member = await team_member_service.update_team_member(target_member.member_id, team_id, **updates)
        
        if updated_member:
            logger.info(f"✅ Team member {target_telegram_id} field '{field}' updated by {username}")
            return f"""✅ Team Member Updated Successfully

👤 Member: {target_member.name}
🔄 Field: {field}
📝 New Value: {value}
👑 Updated By: {username}
🏢 Team: {team_id}

The team member information has been updated successfully."""
        else:
            return f"""❌ Update Failed

Failed to update {field} for team member {target_member.name}.

💡 What you can try:
• Check if the field name is valid
• Verify the new value is appropriate
• Try again in a moment

Technical Details:
• Target Member: {target_member.name} ({target_telegram_id})
• Field: {field}
• Value: {value}"""

    except Exception as e:
        logger.error(f"❌ Error updating team member field by {username}: {e}")
        return f"""❌ System Error

Unable to update team member information.

💡 What you can try:
• Wait a moment and try again
• Check your parameters are correct
• Contact system administrator if the issue persists

Technical Details:
• Error: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}
• Admin: {username} ({telegram_id})
• Target: {target_telegram_id}
• Team: {team_id}"""