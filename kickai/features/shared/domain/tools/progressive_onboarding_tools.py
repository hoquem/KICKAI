#!/usr/bin/env python3
"""
Progressive Onboarding Tools for KICKAI system.

This module provides step-by-step progressive information collection tools
that guide users through the onboarding process without overwhelming them.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional

from kickai.utils.crewai_tool_decorator import tool
from loguru import logger
from pydantic import BaseModel

from kickai.utils.constants import VALID_PLAYER_POSITIONS, VALID_TEAM_MEMBER_ROLES
from kickai.utils.validation_utils import normalize_phone, sanitize_input


class OnboardingStep(Enum):
    """Onboarding step enumeration."""
    
    WELCOME = "welcome"
    ENTITY_TYPE = "entity_type"
    NAME = "name" 
    PHONE = "phone"
    ROLE_POSITION = "role_position"
    OPTIONAL_INFO = "optional_info"
    CONFIRMATION = "confirmation"
    COMPLETE = "complete"


class OnboardingState(BaseModel):
    """Onboarding state tracking."""
    
    user_id: str
    team_id: str
    current_step: OnboardingStep
    entity_type: Optional[str] = None  # "player" or "team_member"
    collected_data: Dict[str, str] = {}
    validation_errors: list = []
    chat_type: Optional[str] = None


@tool("progressive_onboarding_step")
def progressive_onboarding_step(
    user_id: str,
    team_id: str, 
    current_step: str,
    user_input: str = None,
    entity_type: str = None,
    chat_type: str = None
) -> str:
    """
    Handle progressive onboarding step-by-step.
    
    Args:
        user_id: User ID
        team_id: Team ID
        current_step: Current onboarding step
        user_input: User's input for current step
        entity_type: "player" or "team_member" 
        chat_type: Chat context
        
    Returns:
        Next step guidance or completion message
    """
    try:
        step = OnboardingStep(current_step)
        
        if step == OnboardingStep.WELCOME:
            return _handle_welcome_step(user_id, chat_type, entity_type)
        elif step == OnboardingStep.ENTITY_TYPE:
            return _handle_entity_type_step(user_input, chat_type)
        elif step == OnboardingStep.NAME:
            return _handle_name_step(user_input, entity_type)
        elif step == OnboardingStep.PHONE:
            return _handle_phone_step(user_input, entity_type)
        elif step == OnboardingStep.ROLE_POSITION:
            return _handle_role_position_step(user_input, entity_type)
        elif step == OnboardingStep.OPTIONAL_INFO:
            return _handle_optional_info_step(user_input, entity_type)
        elif step == OnboardingStep.CONFIRMATION:
            return _handle_confirmation_step(user_input, entity_type)
        else:
            return "❌ Invalid onboarding step"
            
    except Exception as e:
        logger.error(f"❌ Progressive onboarding error: {e}")
        return f"❌ Onboarding error: {e!s}"


def _handle_welcome_step(user_id: str, chat_type: str, entity_type: str = None) -> str:
    """Handle welcome step."""
    
    if entity_type == "player":
        return f"""
🎉 **WELCOME TO KICKAI PLAYER ONBOARDING!**

Hi there! I'm excited to help you join our team as a player! ⚽

📝 **WHAT WE'LL COLLECT:**
1. Your full name
2. Phone number  
3. Preferred playing position
4. Optional: Additional details

⏱️ **TIME NEEDED:** About 2-3 minutes

🚀 **LET'S START!**
What's your full name? (First and last name please)
        """
    elif entity_type == "team_member":
        return f"""
🎯 **WELCOME TO KICKAI TEAM MEMBER ONBOARDING!**

Great! I'm here to help you join as a team member with administrative access! 

📝 **WHAT WE'LL COLLECT:**
1. Your full name
2. Phone number
3. Administrative role  
4. Optional: Additional contact info

⏱️ **TIME NEEDED:** About 2 minutes

🚀 **LET'S START!**
What's your full name? (First and last name please)
        """
    else:
        # Need to determine entity type
        return f"""
👋 **WELCOME TO KICKAI ONBOARDING!**

I'm here to help you join our team! First, I need to know:

🤔 **ARE YOU REGISTERING AS:**
• **Player** - To play in matches (requires approval)
• **Team Member** - For administrative/coaching role (immediate access)

Please reply with either "Player" or "Team Member"
        """


def _handle_entity_type_step(user_input: str, chat_type: str) -> str:
    """Handle entity type determination."""
    
    if not user_input:
        return "❌ Please specify whether you're registering as a 'Player' or 'Team Member'"
        
    input_lower = user_input.lower().strip()
    
    if any(word in input_lower for word in ['player', 'play', 'match', 'football']):
        return f"""
⚽ **PLAYER REGISTRATION SELECTED!**

Perfect! You'll be registered as a player for matches.

📋 **PROCESS:**
• Information collection
• Leadership approval required
• Access after approval

🚀 **NEXT STEP:**
What's your full name? (First and last name please)

📨 **EXAMPLE:** "John Smith" or "Sarah Jones"
        """
    elif any(word in input_lower for word in ['team member', 'member', 'admin', 'coach', 'manager']):
        return f"""
🎯 **TEAM MEMBER REGISTRATION SELECTED!**

Excellent! You'll be registered with administrative access.

📋 **PROCESS:**
• Information collection
• Immediate activation
• Administrative features available

🚀 **NEXT STEP:**
What's your full name? (First and last name please)

📨 **EXAMPLE:** "John Smith" or "Sarah Jones"
        """
    else:
        return f"""
❓ **PLEASE CLARIFY:**

I didn't understand "{user_input}".

Please choose one:
• Type **"Player"** - To play in matches
• Type **"Team Member"** - For administrative role
        """


def _handle_name_step(user_input: str, entity_type: str) -> str:
    """Handle name collection step."""
    
    if not user_input:
        return "❌ Please provide your full name (first and last name)"
        
    name = sanitize_input(user_input).strip()
    name_parts = name.split()
    
    if len(name_parts) < 2:
        return f"""
❌ **NEED FULL NAME**

You provided: "{name}"

Please provide both first and last name:
📨 **EXAMPLE:** "John Smith" or "Sarah Jones"
        """
        
    # Valid name provided
    entity_display = "player" if entity_type == "player" else "team member"
    
    return f"""
✅ **NAME CONFIRMED:** {name}

📱 **NEXT STEP - PHONE NUMBER:**
Please provide your phone number in UK format.

📨 **ACCEPTED FORMATS:**
• +447123456789
• 07123456789

🔒 **PRIVACY:** Used only for team communication and verification.
    """


def _handle_phone_step(user_input: str, entity_type: str) -> str:
    """Handle phone collection step."""
    
    if not user_input:
        return "❌ Please provide your phone number"
        
    try:
        phone = normalize_phone(user_input)
        
        if not phone:
            return f"""
❌ **INVALID PHONE FORMAT**

You provided: "{user_input}"

📱 **PLEASE USE UK FORMAT:**
• +447123456789
• 07123456789

Try again with correct format.
            """
            
        if not (phone.startswith('+44') or phone.startswith('07')):
            return f"""
❌ **UK FORMAT REQUIRED**

You provided: "{user_input}"

📱 **ACCEPTED FORMATS:**
• +447123456789 (international)
• 07123456789 (national)

Please try again.
            """
            
        # Valid phone number
        if entity_type == "player":
            return f"""
✅ **PHONE CONFIRMED:** {phone}

⚽ **NEXT STEP - PLAYING POSITION:**
What position do you prefer to play?

🎯 **CHOOSE FROM:**
• **Goalkeeper** - Between the posts
• **Defender** - Defensive play
• **Midfielder** - Central play
• **Forward** - Attacking play  
• **Utility** - Can play multiple positions

Please type your preferred position.
            """
        else:  # team_member
            return f"""
✅ **PHONE CONFIRMED:** {phone}

🎯 **NEXT STEP - ADMINISTRATIVE ROLE:**
What role will you take on?

👥 **CHOOSE FROM:**
• **Coach** - Team coaching responsibilities
• **Manager** - Overall team management
• **Assistant** - Supporting coaching role
• **Coordinator** - Events and logistics
• **Volunteer** - General team support
• **Admin** - Administrative privileges

Please type your preferred role.
            """
            
    except Exception as e:
        return f"❌ Phone validation error: {e!s}"


def _handle_role_position_step(user_input: str, entity_type: str) -> str:
    """Handle role/position collection step."""
    
    if not user_input:
        if entity_type == "player":
            return "❌ Please specify your preferred position"
        else:
            return "❌ Please specify your administrative role"
            
    input_clean = sanitize_input(user_input).strip().lower()
    
    if entity_type == "player":
        if input_clean not in VALID_PLAYER_POSITIONS:
            valid_positions = ", ".join([pos.title() for pos in VALID_PLAYER_POSITIONS])
            return f"""
❌ **INVALID POSITION**

You provided: "{user_input}"

⚽ **VALID POSITIONS:**
{valid_positions}

Please choose one of the above positions.
            """
        
        # Valid position
        return f"""
✅ **POSITION CONFIRMED:** {input_clean.title()}

🎉 **INFORMATION COMPLETE!**

📋 **SUMMARY:**
• **Type:** Player
• **Position:** {input_clean.title()}
• **Status:** Pending approval

❓ **OPTIONAL INFORMATION:**
Would you like to provide additional details?
• Jersey number preference
• Emergency contact
• Medical notes

Type **"skip"** to proceed to registration, or provide additional info.
        """
        
    else:  # team_member
        if input_clean not in VALID_TEAM_MEMBER_ROLES:
            valid_roles = ", ".join([role.title() for role in VALID_TEAM_MEMBER_ROLES])
            return f"""
❌ **INVALID ROLE**

You provided: "{user_input}"

👥 **VALID ROLES:**
{valid_roles}

Please choose one of the above roles.
            """
            
        # Valid role
        return f"""
✅ **ROLE CONFIRMED:** {input_clean.title()}

🎉 **INFORMATION COMPLETE!**

📋 **SUMMARY:**  
• **Type:** Team Member
• **Role:** {input_clean.title()}
• **Status:** Ready for activation

❓ **OPTIONAL INFORMATION:**
Would you like to provide additional details?
• Email address
• Emergency contact

Type **"skip"** to proceed to registration, or provide additional info.
        """


def _handle_optional_info_step(user_input: str, entity_type: str) -> str:
    """Handle optional information step."""
    
    if not user_input or user_input.lower().strip() == "skip":
        return f"""
✅ **READY FOR REGISTRATION!**

📋 **FINAL CONFIRMATION:**
All required information has been collected.

🚀 **CONFIRM REGISTRATION:**
Type **"YES"** to complete your registration
Type **"NO"** to cancel or make changes

Proceed with registration?
        """
    
    # Process optional information
    entity_display = "player" if entity_type == "player" else "team member"
    
    return f"""
✅ **ADDITIONAL INFO NOTED:** {user_input}

📋 **READY FOR REGISTRATION!**

🚀 **CONFIRM REGISTRATION:**
Type **"YES"** to complete your {entity_display} registration
Type **"NO"** to cancel or make changes

Proceed with registration?
    """


def _handle_confirmation_step(user_input: str, entity_type: str) -> str:
    """Handle final confirmation step."""
    
    if not user_input:
        return "❌ Please confirm with 'YES' or 'NO'"
        
    input_clean = user_input.lower().strip()
    
    if input_clean in ['yes', 'y', 'confirm', 'proceed']:
        entity_display = "player" if entity_type == "player" else "team member"
        return f"""
🎉 **CONFIRMATION RECEIVED!**

✅ Proceeding with {entity_display} registration...

⏳ **PROCESSING:** Please wait while I complete your registration.
        """
    elif input_clean in ['no', 'n', 'cancel', 'stop']:
        return f"""
❌ **REGISTRATION CANCELLED**

No problem! You can restart the onboarding process anytime.

🔄 **TO RESTART:** Just say "I want to register" and I'll help you again.

Thanks for your interest! 👋
        """
    else:
        return f"""
❓ **PLEASE CONFIRM:**

You said: "{user_input}"

Please respond with:
• **YES** - Complete registration
• **NO** - Cancel registration
        """


@tool("get_onboarding_progress")
def get_onboarding_progress(user_id: str, team_id: str) -> str:
    """
    Get current onboarding progress for a user.
    
    Args:
        user_id: User ID
        team_id: Team ID
        
    Returns:
        Current progress status
    """
    try:
        # This would integrate with a state management system
        # For now, return generic progress message
        
        return f"""
📊 **ONBOARDING PROGRESS**

👤 **User:** {user_id}
🏆 **Team:** {team_id}

📈 **STATUS:** In Progress
🔄 **NEXT:** Awaiting user input

💡 **TIP:** I'll guide you step by step through the process!
        """
        
    except Exception as e:
        logger.error(f"❌ Progress check error: {e}")
        return f"❌ Could not check progress: {e!s}"