#!/usr/bin/env python3
"""
Enhanced Onboarding Tools for KICKAI system.

This module provides comprehensive onboarding tools for both players and team members,
supporting the dual-entity PLAYER_COORDINATOR functionality.
"""

from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_registration_service import (
    PlayerRegistrationService,
)
from typing import Optional, Union
from kickai.features.team_administration.domain.services.simplified_team_member_service import (
    SimplifiedTeamMemberService,
)
from kickai.utils.constants import (
    VALID_PLAYER_POSITIONS,
    VALID_TEAM_MEMBER_ROLES,
)
from kickai.core.enums import ResponseStatus
from crewai.tools import tool
from kickai.utils.validation_utils import normalize_phone, sanitize_input
from kickai.utils.tool_helpers import create_json_response


class TeamMemberGuidanceInput(BaseModel):
    """Input model for team_member_guidance tool."""

    user_id: str
    team_id: str
    chat_type: Optional[str] = None


class ValidationInput(BaseModel):
    """Input model for validate_registration_data tool."""

    name: str
    phone: str
    role_or_position: str
    entity_type: str  # "player" or "team_member"
    team_id: str


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def team_member_guidance(user_id: str, team_id: str, chat_type: str = None) -> str:
    """
    Provide team member registration guidance to a user.

    Args:
        user_id: The user ID to provide guidance to
        team_id: Team ID (required)
        chat_type: Chat type context (optional)

    Returns:
        Team member registration guidance message
    """
    try:
        container = get_container()

        # Build comprehensive guidance message
        guidance = """
🎯 TEAM MEMBER REGISTRATION GUIDE

Welcome! I'm here to help you join as a team member (administrative role).

📝 INFORMATION NEEDED:
1. Full Name - Your first and last name
2. Phone Number - UK format (07123456789 or +447123456789)  
3. Administrative Role - Choose from:
   • Coach - Team coaching responsibilities
   • Manager - Team management duties
   • Assistant - Supporting role
   • Coordinator - Event/logistics coordination
   • Volunteer - General volunteer support
   • Admin - Administrative privileges

✅ PROCESS:
• No approval required - immediate activation
• Direct access to administrative features
• Orientation provided after registration

🚀 READY TO START?
Just say "I want to register as a team member" and I'll guide you through step by step!

ℹ️ Questions? I'm here to help throughout the process.
        """

        logger.info(f"Team member guidance provided to user {user_id}")
        return create_json_response(ResponseStatus.SUCCESS, data=guidance.strip())

    except Exception as e:
        logger.error(f"❌ Failed to provide team member guidance: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to provide team member guidance: {e!s}")

    # Registration tools removed - /register command has been removed from the system
    # @tool("validate_registration_data")
    # def validate_registration_data(
    #     name: str,
    #     phone: str,
    #     role_or_position: str,
    #     entity_type: str,
    #     team_id: str
    # ) -> str:
    """
    Validate registration data for players or team members.

    Args:
        name: Full name to validate
        phone: Phone number to validate  
        role_or_position: Role (team member) or position (player) to validate
        entity_type: Either "player" or "team_member"
        team_id: Team ID (required)

    Returns:
        Validation result message
    """
    try:
        errors = []

        # Sanitize inputs
        name = sanitize_input(name).strip()
        phone = normalize_phone(phone)
        role_or_position = sanitize_input(role_or_position).strip().lower()

        # Validate name
        if not name or len(name.split()) < 2:
            errors.append("❌ Full name required (first and last name)")

        # Validate phone
        if not phone:
            errors.append("❌ Phone number is required")
        elif not (phone.startswith("+44") or phone.startswith("07")):
            errors.append("❌ Phone must be UK format (+447123456789 or 07123456789)")

        # Validate role/position based on entity type
        if entity_type.lower() == "player":
            if role_or_position not in VALID_PLAYER_POSITIONS:
                valid_positions = ", ".join(VALID_PLAYER_POSITIONS)
                errors.append(f"❌ Position must be one of: {valid_positions}")
        elif entity_type.lower() == "team_member":
            if role_or_position not in VALID_TEAM_MEMBER_ROLES:
                valid_roles = ", ".join(VALID_TEAM_MEMBER_ROLES)
                errors.append(f"❌ Role must be one of: {valid_roles}")
        else:
            errors.append("❌ Entity type must be 'player' or 'team_member'")

        if errors:
            return create_json_response(ResponseStatus.ERROR, message="\n".join(errors))

        # All validation passed
        entity_display = "player" if entity_type.lower() == "player" else "team member"
        return create_json_response(ResponseStatus.SUCCESS, data=f"All data validated successfully for {entity_display} registration!")

    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Validation failed: {e!s}")

    # Registration tools removed - /register command has been removed from the system
    # @tool("register_team_member_onboarding")
    # def register_team_member_onboarding(
    #     name: str,
    #     phone: str,
    #     role: str,
    #     team_id: str,
    #     user_id: str = None
    # ) -> str:
    """
    Register a new team member through the onboarding process.
    Optimized for PLAYER_COORDINATOR with enhanced feedback.

    Args:
        name: Full name of the team member
        phone: Phone number (UK format)
        role: Administrative role
        team_id: Team ID (required)
        user_id: Optional user ID

    Returns:
        Registration confirmation with next steps
    """
    try:
        container = get_container()

        # Try to get the simplified team member service first
        team_member_service = container.get_service(SimplifiedTeamMemberService)

        if team_member_service:
            # Use dedicated team member service
            logger.info("🔧 Using SimplifiedTeamMemberService for team member registration")

            # Note: This would need to be implemented in the service
            # For now, fall back to player registration service

        # Fall back to player registration service
        registration_service = container.get_service(PlayerRegistrationService)

        if not registration_service:
            logger.error("❌ No registration service available")
            return create_json_response(ResponseStatus.ERROR, message=f"Registration service not available. Please try again later.")

        # Register using player service (temporary solution)
        member = registration_service.register_player(name, phone, role, team_id)

        if member:
            logger.info(f"✅ Team member registered via onboarding: {name} ({role})")

            # Enhanced success message with next steps
            success_msg = f"""
🎉 REGISTRATION SUCCESSFUL!

✅ Team Member Registered:
• Name: {name}
• Role: {role.title()}
• Status: Active (immediate access)

🚀 WHAT'S NEXT:
• You now have administrative access
• Explore team management features
• Contact leadership for orientation
• Access leadership chat for admin functions

💬 NEED HELP?
Type /help to see available commands or ask me anything!

Welcome to the team! 🤝
            """
            return create_json_response(ResponseStatus.SUCCESS, data=success_msg.strip())
        else:
            logger.error(f"❌ Failed to register team member: {name}")
            return create_json_response(ResponseStatus.ERROR, message=f"Registration failed for {name}. Please check the information and try again.")

    except Exception as e:
        logger.error(f"❌ Team member registration error: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Registration failed: {e!s}")

    # Context detection helpers
    # Registration tools removed - /register command has been removed from the system
    # @tool("detect_registration_context")
    # def detect_registration_context(
    #     message: str,
    #     chat_type: str = None,
    #     user_context: str = None
    # ) -> str:
    """
    Detect whether user wants player or team member registration.

    Args:
        message: User's message/request
        chat_type: Chat type (main/leadership)
        user_context: Additional user context

    Returns:
        Detected registration type and confidence
    """
    try:
        message_lower = message.lower()

        # Team member indicators
        team_member_keywords = [
            "team member",
            "admin",
            "coach",
            "manager",
            "coordinator",
            "volunteer",
            "staff",
            "administrative",
            "leadership",
        ]

        # Player indicators
        player_keywords = [
            "player",
            "play",
            "match",
            "position",
            "goalkeeper",
            "defender",
            "midfielder",
            "forward",
            "football",
        ]

        team_member_score = sum(1 for keyword in team_member_keywords if keyword in message_lower)
        player_score = sum(1 for keyword in player_keywords if keyword in message_lower)

        # Chat type weighting
        if chat_type == "leadership" and team_member_score == 0 and player_score == 0:
            team_member_score += 1
        elif chat_type == "main" and team_member_score == 0 and player_score == 0:
            player_score += 1

        if team_member_score > player_score:
            confidence = "high" if team_member_score >= 2 else "medium"
            return create_json_response(ResponseStatus.SUCCESS, data={
                "entity_type": "team_member",
                "confidence": confidence,
                "message": "Team member registration detected"
            })
        elif player_score > team_member_score:
            confidence = "high" if player_score >= 2 else "medium"
            return create_json_response(ResponseStatus.SUCCESS, data={
                "entity_type": "player",
                "confidence": confidence,
                "message": "Player registration detected"
            })
        else:
            return create_json_response(ResponseStatus.SUCCESS, data={
                "entity_type": "ambiguous",
                "confidence": "low",
                "message": "Cannot determine registration type - clarification needed"
            })

    except Exception as e:
        logger.error(f"❌ Context detection error: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Context detection failed")
