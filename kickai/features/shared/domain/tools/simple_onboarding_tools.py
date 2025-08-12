#!/usr/bin/env python3
"""
Simple Onboarding Tools

This module provides tools for simplified onboarding processes.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.tool_helpers import (
    validate_required_input,
)
from kickai.utils.validation_utils import (
    is_valid_phone,
    validate_team_id,
)


@tool("register_player")
def register_player(player_name: str, phone_number: str, position: str, team_id: str, telegram_id: int) -> str:
    """
    Register a new player through the onboarding process.

    :param player_name: Full name of the player
    :type player_name: str
    :param phone_number: Phone number (UK format)
    :type phone_number: str
    :param position: Playing position
    :type position: str
    :param team_id: Team ID (required)
    :type team_id: str
    :param telegram_id: Telegram ID of the requesting user (required)
    :type telegram_id: int
    :return: Registration confirmation with next steps
    :rtype: str
    """
    try:
        # Validate inputs
        player_name = validate_required_input(player_name, "Player name")
        
        # Validate phone number
        if not is_valid_phone(phone_number):
            return json_error(f"Invalid phone number: {phone_number}")
        phone_number = validate_required_input(phone_number, "Phone number")
        
        position = validate_required_input(position, "Position")
        
        # Validate team_id
        is_valid, error = validate_team_id(team_id)
        if not is_valid:
            return json_error(error)
            
        # Validate telegram_id
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return json_error(f"Invalid telegram ID: {telegram_id}")

        # Log tool execution start
        inputs = {'player_name': player_name, 'phone_number': phone_number, 'position': position, 'team_id': team_id, 'telegram_id': telegram_id}
        logger.info(f"Executing register_player with inputs: {inputs}")

        # Get service
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            return json_error(message="PlayerService is not available", error_type="Service unavailable")

        # Register player
        success = player_service.register_player_sync(player_name, phone_number, position, team_id, telegram_id)

        if success:
            data = {
                'player_name': player_name,
                'phone_number': phone_number,
                'position': position,
                'team_id': team_id,
                'telegram_id': telegram_id,
                'status': 'pending_approval'
            }

            success_msg = f"""
🎉 **REGISTRATION SUCCESSFUL!**

✅ **Player Registered:**
• **Name:** {player_name}
• **Position:** {position.title()}
• **Status:** Pending Approval

📋 **WHAT'S NEXT:**
• Your registration is pending leadership approval
• You'll be notified when approved
• Once approved, you can participate in matches
• Contact leadership for any questions

💬 **NEED HELP?**
Type /help to see available commands or ask me anything!

Welcome to the team! ⚽
            """

            return json_response(data=data, ui_format=success_msg.strip())
        else:
            return json_error(message="Registration failed", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in register_player: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return json_error(message=f"Registration failed: {e!s}", error_type="Operation failed")

@tool("register_team_member")
def register_team_member(player_name: str, phone_number: str, role: str, team_id: str, telegram_id: int) -> str:
    """
    Register a new team member through the onboarding process.

    :param player_name: Full name of the team member
    :type player_name: str
    :param phone_number: Phone number (UK format)
    :type phone_number: str
    :param role: Administrative role
    :type role: str
    :param team_id: Team ID (required)
    :type team_id: str
    :param telegram_id: Telegram ID of the requesting user (required)
    :type telegram_id: int
    :return: Registration confirmation with next steps
    :rtype: str
    """
    try:
        # Validate inputs
        player_name = validate_required_input(player_name, "Player name")
        # Basic phone validation
        if not phone_number or len(phone_number.strip()) < 5:
            return json_error(f"Invalid phone number: {phone_number}")
        role = validate_required_input(role, "Role")
        team_id = validate_team_id(team_id)
        # Basic telegram_id validation
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return json_error(f"Invalid telegram ID: {telegram_id}")

        # Log tool execution start
        inputs = {'player_name': player_name, 'phone_number': phone_number, 'role': role, 'team_id': team_id, 'telegram_id': telegram_id}
        logger.info(f"Executing register_team_member with inputs: {inputs}")

        # Get service
        container = get_container()
        team_service = container.get_service(TeamService)

        if not team_service:
            return json_error(message="TeamService is not available", error_type="Service unavailable")

        # Register team member
        success = team_service.register_team_member_sync(player_name, phone_number, role, team_id, telegram_id)

        if success:
            data = {
                'player_name': player_name,
                'phone_number': phone_number,
                'role': role,
                'team_id': team_id,
                'telegram_id': telegram_id,
                'status': 'active'
            }

            success_msg = f"""
🎉 **REGISTRATION SUCCESSFUL!**

✅ **Team Member Registered:**
• **Name:** {player_name}
• **Role:** {role.title()}
• **Status:** Active (immediate access)

🚀 **WHAT'S NEXT:**
• You now have administrative access
• Explore team management features
• Contact leadership for orientation
• Access leadership chat for admin functions

💬 **NEED HELP?**
Type /help to see available commands or ask me anything!

Welcome to the team! 🤝
            """

            return json_response(data=data, ui_format=success_msg.strip())
        else:
            return json_error(message="Registration failed", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in register_team_member: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return json_error(message=f"Registration failed: {e!s}", error_type="Operation failed")

@tool("registration_guidance")
def registration_guidance(telegram_id: int, team_id: str) -> str:
    """
    Provide guidance for the registration process.

    :param telegram_id: Telegram ID of the user (required) - available from context
    :type telegram_id: int
    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :return: JSON response with registration guidance
    :rtype: str
    """
    try:
        # Validate inputs
        # Basic telegram_id validation
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return json_error(f"Invalid telegram ID: {telegram_id}")
        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'telegram_id': telegram_id, 'team_id': team_id}
        logger.info(f"Executing registration_guidance with inputs: {inputs}")

        guidance_msg = """
📋 **REGISTRATION GUIDANCE**

👋 **Welcome to KICKAI!**

🎯 **REGISTRATION OPTIONS:**

1️⃣ **Player Registration:**
   • Use: `/register [player_name] [phone] [position]`
   • Example: `/register John Smith +447123456789 Striker`
   • Status: Pending approval by leadership
   • Access: Match participation once approved

2️⃣ **Team Member Registration:**
   • Use: `/addmember [name] [phone] [role]`
   • Example: `/addmember Jane Doe +447123456789 Coach`
   • Status: Immediate active access
   • Access: Administrative functions

📱 **REQUIRED INFORMATION:**
• Full name (as it appears on official documents)
• UK phone number (with country code +44)
• Position (for players) or role (for team members)

🔒 **SECURITY:**
• All information is securely stored
• Access is controlled by team leadership
• Personal data is protected

💡 **NEED HELP?**
• Contact team leadership for assistance
• Use `/help` for command information
• Check pinned messages for updates

🎉 **Welcome to the team!** ⚽
        """

        data = {
            'telegram_id': telegram_id,
            'team_id': team_id,
            'guidance_type': 'registration',
            'guidance_content': guidance_msg.strip()
        }

        return json_response(data=data, ui_format=guidance_msg.strip())

    except Exception as e:
        logger.error(f"Failed to provide registration guidance: {e}")
        return json_error(message=f"Failed to provide registration guidance: {e}", error_type="Operation failed")
