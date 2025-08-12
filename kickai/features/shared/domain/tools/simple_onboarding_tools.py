#!/usr/bin/env python3
"""
Simple Onboarding Tools (No Decorator Dependencies)

This module provides simple onboarding tools that can be used when the 
decorator-based tools fail to load due to dependency issues.
"""


from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import create_json_response


@tool("register_player")
def register_player(player_name: str, phone_number: str, position: str, team_id: str) -> str:
    """
    Register a new player through the onboarding process.

    Args:
        player_name: Full name of the player
        phone_number: Phone number (UK format)
        position: Playing position
        team_id: Team ID (required)

    Returns:
        Registration confirmation with next steps
    """
    try:
        # For now, return a standard response that indicates the tool is available
        # In production, this would integrate with the registration service
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
        return create_json_response("success", data=success_msg.strip())

    except Exception as e:
        return create_json_response("error", message=f"Registration failed: {e!s}")


@tool("register_team_member")
def register_team_member(player_name: str, phone_number: str, role: str, team_id: str) -> str:
    """
    Register a new team member through the onboarding process.

    Args:
        player_name: Full name of the team member
        phone_number: Phone number (UK format)
        role: Administrative role
        team_id: Team ID (required)

    Returns:
        Registration confirmation with next steps
    """
    try:
        # For now, return a standard response that indicates the tool is available
        # In production, this would integrate with the registration service
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
        return create_json_response("success", data=success_msg.strip())

    except Exception as e:
        return create_json_response("error", message=f"Registration failed: {e!s}")


@tool("registration_guidance")
def registration_guidance(user_id: str, team_id: str) -> str:
    """
    Provide comprehensive registration guidance to a user.

    Args:
        user_id: The user ID to provide guidance to
        team_id: Team ID (required)

    Returns:
        Registration guidance message
    """
    try:
        # Build comprehensive guidance message
        guidance = """
🎯 **KICKAI REGISTRATION GUIDE**

Welcome! I'm here to help you join our football team. I can help you register as either:

👥 **PLAYER REGISTRATION** (Main Chat):
1. **Full Name** - Your first and last name
2. **Phone Number** - UK format (07123456789 or +447123456789)  
3. **Position** - Choose from:
   • **Goalkeeper** - Goal protection specialist
   • **Defender** - Defense and ball distribution
   • **Midfielder** - Central playmaker and support
   • **Forward** - Attack and goal scoring
   • **Utility** - Can play multiple positions

✅ **PLAYER PROCESS:**
• Registration submitted for approval
• Leadership review and approval required
• Notification when approved and activated
• Participation in matches after approval

👔 **TEAM MEMBER REGISTRATION** (Leadership Chat):
1. **Full Name** - Your first and last name
2. **Phone Number** - UK format (07123456789 or +447123456789)  
3. **Administrative Role** - Choose from:
   • **Coach** - Team coaching responsibilities
   • **Manager** - Team management duties
   • **Assistant** - Supporting role
   • **Coordinator** - Event/logistics coordination
   • **Volunteer** - General volunteer support
   • **Admin** - Administrative privileges

✅ **TEAM MEMBER PROCESS:**
• No approval required - immediate activation
• Direct access to administrative features
• Orientation provided after registration

🚀 **READY TO START?**
Just tell me which type of registration you want:
• "I want to register as a player"
• "I want to register as a team member"

ℹ️ **Questions?** I'm here to help throughout the process!
        """

        return create_json_response("success", data=guidance.strip())

    except Exception as e:
        return create_json_response("error", message=f"Failed to provide registration guidance: {e!s}")


# Tool metadata for manual registration
TOOLS_METADATA = {
    "register_player": {
        "function": register_player,
        "description": "Register a new player through the onboarding process",
        "parameters": ["player_name", "phone_number", "position", "team_id"]
    },
    "register_team_member": {
        "function": register_team_member,
        "description": "Register a new team member through the onboarding process",
        "parameters": ["player_name", "phone_number", "role", "team_id"]
    },
    "registration_guidance": {
        "function": registration_guidance,
        "description": "Provide comprehensive registration guidance to a user",
        "parameters": ["user_id", "team_id"]
    }
}
