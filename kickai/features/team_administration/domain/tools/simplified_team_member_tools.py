#!/usr/bin/env python3
"""
Simplified Team Member Tools

This module provides tools for simplified team member management
for the new /addmember command that only requires name and phone number.
"""

from typing import Any
from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.team_administration.domain.services.simplified_team_member_service import (
    SimplifiedTeamMemberService,
)
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    validate_required_input,
)
from kickai.utils.validation_utils import (
    normalize_phone,
    sanitize_input,
)


@tool("add_team_member_simplified")
async def add_team_member_simplified(team_id: str, user_id: str, name: str, phone: str, role: str = None) -> str:
    """
    Add a new team member with simplified ID generation.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        name: Team member's full name
        phone: Team member's phone number
        role: Team member's role (optional, can be set later)
        
    Returns:
        Success message with invite link or error
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error
        
        # Simplified validation - only name and phone required
        if not name or not name.strip():
            return format_tool_error("Team member name is required")
        
        if not phone or not phone.strip():
            return format_tool_error("Team member phone number is required")
        
        # Sanitize inputs
        name = sanitize_input(name, max_length=50)
        phone = sanitize_input(phone, max_length=20)
        role = sanitize_input(role, max_length=30) if role else "To be set"
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)
        
        # Normalize phone number
        phone = normalize_phone(phone)
        
        container = get_container()
        
        # Get team repository for the service
        team_repository = container.get_service("TeamRepositoryInterface")
        if not team_repository:
            raise ServiceNotAvailableError("TeamRepositoryInterface")
        
        # Create simplified team member service
        team_member_service = SimplifiedTeamMemberService(team_repository)
        
        # Add team member with simplified ID generation
        success, message = await team_member_service.add_team_member(name, phone, role, team_id)
        
        if success:
            # Extract member ID from message
            import re
            member_id_match = re.search(r'ID: (\w+)', message)
            member_id = member_id_match.group(1) if member_id_match else "Unknown"
            
            # Create invite link
            invite_result = await team_member_service.create_team_member_invite_link(
                name, phone, role, team_id
            )
            
            if invite_result.get("success"):
                return f"""✅ Team Member Added Successfully!

👔 Member Details:
• Name: {name}
• Phone: {phone}
• Role: {role}
• Member ID: {member_id}
• Status: Active

🔗 Invite Link for Leadership Chat:
{invite_result['invite_link']}

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
                return f"""✅ Team Member Added Successfully!

👔 Member Details:
• Name: {name}
• Phone: {phone}
• Role: {role}
• Member ID: {member_id}
• Status: Active

⚠️ Note: Could not generate invite link - {invite_result.get('error', 'Unknown error')}.
Please contact the system administrator.

🎯 Member ID: {member_id}"""
        else:
            return format_tool_error(f"Failed to add team member: {message}")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in add_team_member_simplified: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to add team member: {e}", exc_info=True)
        return format_tool_error(f"Failed to add team member: {e}") 