#!/usr/bin/env python3
"""
Simplified Team Member Tools - Native CrewAI Implementation

This module provides tools for simplified team member management using ONLY CrewAI native patterns.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.interfaces.team_repositories import ITeamRepository
from kickai.features.team_administration.domain.services.simplified_team_member_service import (
    SimplifiedTeamMemberService,
)


@tool("add_team_member_simplified")
def add_team_member_simplified(
    telegram_id: int,
    team_id: str,
    chat_type: str,
    name: str,
    phone: str,
    role: str = "Member"
) -> str:
    """
    Add a new team member with simplified ID generation.

    :param telegram_id: Telegram ID of the user making the request
    :type telegram_id: int
    :param team_id: Team identifier for context and data isolation
    :type team_id: str
    :param chat_type: Chat context (main, leadership, private)
    :type chat_type: str
    :param name: Team member's full name
    :type name: str
    :param phone: Team member's phone number
    :type phone: str
    :param role: Team member's role (optional, defaults to Member)
    :type role: str
    :return: Team member addition status and invite link
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to add team member."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to add team member."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to add team member."

    if not name or name.strip() == "":
        return "❌ Name is required to add team member."

    if not phone or phone.strip() == "":
        return "❌ Phone number is required to add team member."

    try:
        # Get services using simple container access
        container = get_container()
        team_repository = container.get_service(ITeamRepository)

        if not team_repository:
            return "❌ Team repository service is temporarily unavailable. Please try again later."

        # Default role if not provided
        if not role or role.strip() == "":
            role = "Member"

        # Normalize inputs
        name = name.strip()
        phone = phone.strip()
        role = role.strip()

        # Normalize phone number
        from kickai.utils.validation_utils import normalize_phone
        phone = normalize_phone(phone)

        # Create simplified team member service
        team_member_service = SimplifiedTeamMemberService(team_repository)

        # Add team member
        import asyncio
        success, message = asyncio.run(team_member_service.add_team_member(name, phone, role, team_id))

        if success:
            # Extract member ID from message
            import re
            member_id_match = re.search(r"ID: (\w+)", message)
            member_id = member_id_match.group(1) if member_id_match else "Unknown"

            # Create invite link
            invite_result = asyncio.run(team_member_service.create_team_member_invite_link(
                name, phone, role, team_id
            ))

            # Format as simple string response
            result = "✅ Team Member Added Successfully!\\n\\n"
            result += "👤 Member Details:\\n"
            result += f"• Name: {name}\\n"
            result += f"• Phone: {phone}\\n"
            result += f"• Role: {role}\\n"
            result += f"• Member ID: {member_id}\\n"
            result += "• Status: Active\\n\\n"

            if invite_result and invite_result.get("success"):
                result += "🔗 Invite Link for Leadership Chat:\\n"
                result += f"{invite_result['invite_link']}\\n\\n"
                result += "📋 Next Steps:\\n"
                result += f"1. Send the invite link to {name}\\n"
                result += "2. Ask them to join the leadership chat\\n"
                result += "3. They can then access admin commands\\n\\n"
                result += "🔒 Security Note: Link expires in 7 days and is one-time use only."
            else:
                result += f"⚠️ Note: Could not generate invite link - {invite_result.get('error', 'Unknown error')}.\\n"
                result += "Please contact the system administrator."

            return result
        else:
            return f"❌ Failed to add team member: {message}"

    except Exception as e:
        logger.error(f"Failed to add team member: {e}")
        return f"❌ Failed to add team member: {e!s}"
