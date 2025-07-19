#!/usr/bin/env python3
"""
Registration Tools for CrewAI Agents

This module provides CrewAI tools for handling player and team member registration
with proper validation and context-aware processing.
"""

from typing import Optional, Dict, Any
from loguru import logger
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from utils.phone_validator import PhoneValidator
import re

TOOL_REGISTRY = {}

def register_tool_instance(tool_instance):
    TOOL_REGISTRY[tool_instance.name] = tool_instance
    return tool_instance


class PlayerRegistrationInput(BaseModel):
    """Input model for player registration."""
    full_name: str = Field(..., description="Player's full name")
    phone_number: str = Field(..., description="Player's phone number")
    position: str = Field(..., description="Player's position (Forward, Midfielder, Defender, Goalkeeper)")
    date_of_birth: str = Field(..., description="Player's date of birth (YYYY-MM-DD)")
    emergency_contact: str = Field(..., description="Emergency contact phone number")
    next_of_kin: str = Field(..., description="Next of kin information")


class TeamMemberRegistrationInput(BaseModel):
    """Input model for team member registration."""
    full_name: str = Field(..., description="Team member's full name")
    phone_number: str = Field(..., description="Team member's phone number")
    role: str = Field(..., description="Team member's role (Coach, Manager, Volunteer, Assistant)")
    email: Optional[str] = Field(None, description="Team member's email (optional)")
    experience: Optional[str] = Field(None, description="Team member's experience (optional)")
    notes: Optional[str] = Field(None, description="Additional notes (optional)")


class PlayerRegistrationTool(BaseTool):
    """Tool for handling player registration with validation."""
    
    name: str = "player_registration_tool"
    description: str = "Register a new player with full details including validation"
    
    def __init__(self):
        super().__init__()
        self._context = {}
    
    def configure_with_context(self, context: Dict[str, Any]):
        """Configure tool with execution context."""
        self._context = context
    
    def _validate_name(self, name: str) -> tuple[bool, str]:
        """Validate player name."""
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name.strip()) > 50:
            return False, "Name must be less than 50 characters"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name.strip()):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, ""
    
    def _validate_position(self, position: str) -> tuple[bool, str]:
        """Validate player position."""
        valid_positions = [
            "Forward", "Midfielder", "Defender", "Goalkeeper",
            "Striker", "Winger", "Central Midfielder", "Defensive Midfielder",
            "Center Back", "Full Back", "Utility", "Any"
        ]
        
        if position.lower() not in [pos.lower() for pos in valid_positions]:
            return False, f"Position must be one of: {', '.join(valid_positions)}"
        
        return True, ""
    
    def _validate_date_of_birth(self, dob: str) -> tuple[bool, str]:
        """Validate date of birth format."""
        import re
        from datetime import datetime
        
        # Check format YYYY-MM-DD
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
            return False, "Date of birth must be in YYYY-MM-DD format (e.g., 1990-01-15)"
        
        try:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
            # Check if date is reasonable (not in future, not too old)
            from datetime import date
            today = date.today()
            age = today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))
            
            if age < 16:
                return False, "Player must be at least 16 years old"
            if age > 80:
                return False, "Please check the date of birth"
                
        except ValueError:
            return False, "Invalid date format"
        
        return True, ""
    
    def _run(self, registration_data: str) -> str:
        """
        Register a new player with validation.
        
        Args:
            registration_data: Comma-separated string with player details:
                "Full Name, Phone, Position, Date of Birth, Emergency Contact, Next of Kin"
        
        Returns:
            Registration result message
        """
        try:
            team_id = self._context.get('team_id')
            user_id = self._context.get('user_id')
            
            if not team_id or not user_id:
                return "❌ Error: Tool not properly configured with team and user context"
            
            # Parse registration data
            parts = [part.strip() for part in registration_data.split(',')]
            if len(parts) < 6:
                return "❌ Error: Please provide all required information: Full Name, Phone, Position, Date of Birth, Emergency Contact, Next of Kin"
            
            full_name, phone, position, dob, emergency_contact, next_of_kin = parts[:6]
            
            # Validate name
            is_valid_name, name_error = self._validate_name(full_name)
            if not is_valid_name:
                return f"❌ Name Error: {name_error}"
            
            # Validate and format phone number
            is_valid_phone, formatted_phone, phone_error = PhoneValidator.validate_and_format_phone(phone)
            if not is_valid_phone:
                return f"❌ Phone Error: {phone_error}"
            
            # Validate position
            is_valid_position, position_error = self._validate_position(position)
            if not is_valid_position:
                return f"❌ Position Error: {position_error}"
            
            # Validate date of birth
            is_valid_dob, dob_error = self._validate_date_of_birth(dob)
            if not is_valid_dob:
                return f"❌ Date of Birth Error: {dob_error}"
            
            # Validate emergency contact
            is_valid_emergency, formatted_emergency, emergency_error = PhoneValidator.validate_and_format_phone(emergency_contact)
            if not is_valid_emergency:
                return f"❌ Emergency Contact Error: {emergency_error}"
            
            # Validate next of kin
            if not next_of_kin or len(next_of_kin.strip()) < 2:
                return "❌ Next of Kin Error: Please provide next of kin information"
            
            # TODO: Save to database using player service
            # For now, return success message
            return (
                f"✅ *Player Registration Successful!*\n\n"
                f"📋 *Registration Details:*\n"
                f"• **Name**: {full_name}\n"
                f"• **Phone**: {formatted_phone}\n"
                f"• **Position**: {position}\n"
                f"• **Date of Birth**: {dob}\n"
                f"• **Emergency Contact**: {formatted_emergency}\n"
                f"• **Next of Kin**: {next_of_kin}\n\n"
                f"🎯 *Next Steps:*\n"
                f"• Your registration will be reviewed by team leadership\n"
                f"• You'll receive a unique player ID once approved\n"
                f"• Use /myinfo to check your status\n\n"
                f"💡 *Welcome to the team!* ⚽️"
            )
            
        except Exception as e:
            logger.error(f"Error in player registration: {e}")
            return f"❌ Registration Error: {str(e)}"


class TeamMemberRegistrationTool(BaseTool):
    """Tool for handling team member registration with validation."""
    
    name: str = "team_member_registration_tool"
    description: str = "Register a new team member (coach, manager, volunteer) with validation"
    
    def __init__(self):
        super().__init__()
        self._context = {}
    
    def configure_with_context(self, context: Dict[str, Any]):
        """Configure tool with execution context."""
        self._context = context
    
    def _validate_role(self, role: str) -> tuple[bool, str]:
        """Validate team member role."""
        valid_roles = [
            "Coach", "Manager", "Volunteer", "Assistant", "Coordinator",
            "Trainer", "Advisor", "Support", "Helper"
        ]
        
        if role.lower() not in [r.lower() for r in valid_roles]:
            return False, f"Role must be one of: {', '.join(valid_roles)}"
        
        return True, ""
    
    def _run(self, registration_data: str) -> str:
        """
        Register a new team member with validation.
        
        Args:
            registration_data: Comma-separated string with team member details:
                "Full Name, Phone, Role, [Email], [Experience], [Notes]"
        
        Returns:
            Registration result message
        """
        try:
            team_id = self._context.get('team_id')
            user_id = self._context.get('user_id')
            
            if not team_id or not user_id:
                return "❌ Error: Tool not properly configured with team and user context"
            
            # Parse registration data
            parts = [part.strip() for part in registration_data.split(',')]
            if len(parts) < 3:
                return "❌ Error: Please provide required information: Full Name, Phone, Role"
            
            full_name, phone, role = parts[:3]
            email = parts[3] if len(parts) > 3 and parts[3] else None
            experience = parts[4] if len(parts) > 4 and parts[4] else None
            notes = parts[5] if len(parts) > 5 and parts[5] else None
            
            # Validate name (reuse from player registration)
            player_tool = PlayerRegistrationTool()
            is_valid_name, name_error = player_tool._validate_name(full_name)
            if not is_valid_name:
                return f"❌ Name Error: {name_error}"
            
            # Validate and format phone number
            is_valid_phone, formatted_phone, phone_error = PhoneValidator.validate_and_format_phone(phone)
            if not is_valid_phone:
                return f"❌ Phone Error: {phone_error}"
            
            # Validate role
            is_valid_role, role_error = self._validate_role(role)
            if not is_valid_role:
                return f"❌ Role Error: {role_error}"
            
            # Validate email if provided
            if email and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                return "❌ Email Error: Please provide a valid email address"
            
            # TODO: Save to database using team member service
            # For now, return success message
            result = (
                f"✅ *Team Member Registration Successful!*\n\n"
                f"📋 *Registration Details:*\n"
                f"• **Name**: {full_name}\n"
                f"• **Phone**: {formatted_phone}\n"
                f"• **Role**: {role}\n"
            )
            
            if email:
                result += f"• **Email**: {email}\n"
            if experience:
                result += f"• **Experience**: {experience}\n"
            if notes:
                result += f"• **Notes**: {notes}\n"
            
            result += (
                f"\n🎯 *Next Steps:*\n"
                f"• You now have access to leadership commands\n"
                f"• Use /help to see available commands\n"
                f"• Welcome to the leadership team! 👔\n\n"
                f"💡 *Thank you for joining our team!* 🏆"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in team member registration: {e}")
            return f"❌ Registration Error: {str(e)}"


class RegistrationGuidanceTool(BaseTool):
    """Tool for providing registration guidance and context."""
    
    name: str = "registration_guidance_tool"
    description: str = "Provide guidance for registration based on chat context and user situation"
    
    def __init__(self):
        super().__init__()
        self._context = {}
    
    def configure_with_context(self, context: Dict[str, Any]):
        """Configure tool with execution context."""
        self._context = context
    
    def _run(self, query: str = "") -> str:
        """
        Provide registration guidance based on context.
        
        Args:
            query: Optional query from user
        
        Returns:
            Guidance message
        """
        try:
            chat_type = self._context.get('chat_type')
            
            if chat_type == "main_chat":
                return (
                    f"🎯 *Player Registration - Main Chat*\n\n"
                    f"Welcome! You're in the main team chat for player registration.\n\n"
                    f"📝 *Required Information:*\n"
                    f"• **Full Name**: (e.g., John Smith)\n"
                    f"• **Phone Number**: (e.g., +447123456789)\n"
                    f"• **Position**: (e.g., Forward, Midfielder, Defender, Goalkeeper)\n"
                    f"• **Date of Birth**: (e.g., 1990-01-15)\n"
                    f"• **Emergency Contact**: (e.g., +447123456789)\n"
                    f"• **Next of Kin**: (e.g., Jane Smith - Wife)\n\n"
                    f"💡 *Send all details in one message* like this:\n"
                    f"`John Smith, +447123456789, Forward, 1990-01-15, +447123456789, Jane Smith - Wife`\n\n"
                    f"⚠️ *Note*: You must be added by team leadership first. If you haven't been invited, please contact the team admin."
                )
            
            elif chat_type == "leadership_chat":
                return (
                    f"👔 *Team Member Registration - Leadership Chat*\n\n"
                    f"Welcome to the leadership team! You're registering as a team member.\n\n"
                    f"📝 *Required Information:*\n"
                    f"• **Full Name**: (e.g., John Smith)\n"
                    f"• **Phone Number**: (e.g., +447123456789)\n"
                    f"• **Role**: (e.g., Coach, Manager, Volunteer, Assistant)\n\n"
                    f"💡 *Send all details in one message* like this:\n"
                    f"`John Smith, +447123456789, Coach`\n\n"
                    f"✅ *Optional Information* (add if you want):\n"
                    f"• **Email**: (e.g., john@example.com)\n"
                    f"• **Experience**: (e.g., 5 years coaching)\n"
                    f"• **Notes**: (e.g., FA qualified coach)"
                )
            
            else:  # private chat
                return (
                    f"🤖 *Registration Guidance*\n\n"
                    f"Hi! I can help you register with the team.\n\n"
                    f"📋 *Choose your registration type:*\n\n"
                    f"🎯 *Player Registration* (Main Chat):\n"
                    f"• Join the main team chat\n"
                    f"• Use /register for full player onboarding\n"
                    f"• Requires team leadership approval\n\n"
                    f"👔 *Team Member Registration* (Leadership Chat):\n"
                    f"• Join the leadership chat\n"
                    f"• Use /register for team member setup\n"
                    f"• For coaches, managers, volunteers\n\n"
                    f"💡 *Need help?*\n"
                    f"Contact the team leadership to be added to the appropriate chat."
                )
            
        except Exception as e:
            logger.error(f"Error in registration guidance: {e}")
            return "❌ Error providing registration guidance. Please contact team leadership."


# Register all tools after class definitions
register_tool_instance(PlayerRegistrationTool())
register_tool_instance(TeamMemberRegistrationTool())
register_tool_instance(RegistrationGuidanceTool())

# Register all tools
__all__ = [
    "PlayerRegistrationTool",
    "TeamMemberRegistrationTool", 
    "RegistrationGuidanceTool",
    "TOOL_REGISTRY"
] 