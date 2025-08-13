#!/usr/bin/env python3
"""
Simple Onboarding Tools (No Decorator Dependencies)

This module provides simple onboarding tools that can be used when the 
decorator-based tools fail to load due to dependency issues.
"""


from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import create_json_response


@tool("registration_guidance", result_as_answer=True)
def registration_guidance(telegram_id: int, team_id: str, username: str, chat_type: str, user_id: str) -> str:

    """
    Provide comprehensive registration guidance to a user.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required)
        username: Username of the requesting user
        chat_type: Chat type context
        user_id: The user ID to provide guidance to

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
    "registration_guidance": {
        "function": registration_guidance,
        "description": "Provide comprehensive registration guidance to a user",
        "parameters": ["user_id", "team_id"]
    }
}
