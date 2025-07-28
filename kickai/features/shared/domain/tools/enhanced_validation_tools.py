#!/usr/bin/env python3
"""
Enhanced Validation Tools for KICKAI onboarding system.

This module provides comprehensive validation tools with detailed feedback,
suggestions, and smart corrections for user input during onboarding.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

from kickai.utils.crewai_tool_decorator import tool
from loguru import logger

from kickai.utils.constants import VALID_PLAYER_POSITIONS, VALID_TEAM_MEMBER_ROLES
from kickai.utils.validation_utils import normalize_phone, sanitize_input


# Smart suggestion mappings
POSITION_SUGGESTIONS = {
    "gk": "goalkeeper",
    "keeper": "goalkeeper", 
    "goalie": "goalkeeper",
    "def": "defender",
    "defense": "defender",
    "cb": "defender",
    "lb": "defender", 
    "rb": "defender",
    "mid": "midfielder",
    "midfield": "midfielder",
    "cm": "midfielder",
    "cdm": "midfielder",
    "cam": "midfielder",
    "att": "forward",
    "attack": "forward",
    "striker": "forward",
    "winger": "forward",
    "lw": "forward",
    "rw": "forward",
    "cf": "forward"
}

ROLE_SUGGESTIONS = {
    "head coach": "coach",
    "trainer": "coach",
    "coaching": "coach",
    "team manager": "manager",
    "management": "manager",
    "assistant coach": "assistant",
    "helper": "assistant",
    "organize": "coordinator",
    "organizer": "coordinator",
    "logistics": "coordinator",
    "volunteer work": "volunteer",
    "help": "volunteer",
    "administrator": "admin",
    "administration": "admin"
}

# Common name validation patterns
NAME_PATTERNS = {
    "too_short": re.compile(r"^.{1,2}$"),
    "single_name": re.compile(r"^[a-zA-Z]+$"),
    "has_numbers": re.compile(r"\d"),
    "has_special": re.compile(r"[^a-zA-Z\s\-\']"),
    "multiple_spaces": re.compile(r"\s{2,}"),
    "valid_name": re.compile(r"^[a-zA-Z\s\-\']{3,50}$")
}

# Phone number patterns for better validation
PHONE_PATTERNS = {
    "uk_international": re.compile(r"^\+44[0-9]{10}$"),
    "uk_national": re.compile(r"^0[0-9]{10}$"),
    "has_spaces": re.compile(r"\s"),
    "has_dashes": re.compile(r"-"),
    "has_brackets": re.compile(r"[\(\)]"),
    "only_digits": re.compile(r"^[0-9]+$"),
    "valid_length": re.compile(r"^.{10,15}$")
}


@tool("validate_name_enhanced")
def validate_name_enhanced(name: str, entity_type: str = "player") -> str:
    """
    Enhanced name validation with detailed feedback and suggestions.
    
    Args:
        name: Name to validate
        entity_type: "player" or "team_member"
        
    Returns:
        Validation result with detailed feedback
    """
    try:
        if not name:
            entity_display = "player" if entity_type == "player" else "team member"
            return f"""
❌ **NAME REQUIRED**

Please provide your full name for {entity_type} registration.

📝 **EXAMPLE:** "John Smith" or "Sarah Jones"
            """
            
        name_clean = sanitize_input(name).strip()
        
        # Check for obvious issues
        if NAME_PATTERNS["too_short"].match(name_clean):
            return f"""
❌ **NAME TOO SHORT**

You provided: "{name}"

Please provide your full name (first and last):
📝 **EXAMPLE:** "John Smith" instead of just "John"
            """
            
        if NAME_PATTERNS["has_numbers"].search(name_clean):
            return f"""
❌ **NUMBERS NOT ALLOWED**

You provided: "{name}"

Please provide your name using letters only:
📝 **EXAMPLE:** "John Smith" (no numbers)
            """
            
        if NAME_PATTERNS["has_special"].search(name_clean):
            # Allow hyphens and apostrophes in names
            special_chars = re.findall(r"[^a-zA-Z\s\-\']", name_clean)
            return f"""
❌ **INVALID CHARACTERS**

You provided: "{name}"
Found invalid characters: {', '.join(set(special_chars))}

✅ **ALLOWED:** Letters, spaces, hyphens (-), apostrophes (')
📝 **EXAMPLE:** "Mary-Jane O'Connor" or "John Smith"
            """
            
        # Clean up multiple spaces
        if NAME_PATTERNS["multiple_spaces"].search(name_clean):
            name_clean = re.sub(r"\s+", " ", name_clean)
            
        # Check if single name (needs first and last)
        name_parts = name_clean.split()
        if len(name_parts) < 2:
            return f"""
❌ **NEED FIRST AND LAST NAME**

You provided: "{name}"

Please provide both first and last name:
📝 **EXAMPLE:** "John Smith" or "Sarah Johnson"
            """
            
        if len(name_parts) > 4:
            return f"""
⚠️ **LONG NAME DETECTED**

You provided: "{name}"

This seems quite long. Is this correct? If so, it's fine!
Otherwise, please provide first and last name:
📝 **EXAMPLE:** "John Smith"
            """
            
        # Name looks good
        return f"""
✅ **NAME VALIDATED**

Confirmed: {name_clean}

📱 **NEXT:** Please provide your phone number in UK format:
• +447123456789 (international)
• 07123456789 (national)
        """
        
    except Exception as e:
        logger.error(f"❌ Name validation error: {e}")
        return f"❌ Name validation failed: {e!s}"


@tool("validate_phone_enhanced")
def validate_phone_enhanced(phone: str, provide_suggestions: bool = True) -> str:
    """
    Enhanced phone validation with format suggestions and corrections.
    
    Args:
        phone: Phone number to validate
        provide_suggestions: Whether to provide format suggestions
        
    Returns:
        Validation result with suggestions
    """
    try:
        if not phone:
            return f"""
❌ **PHONE NUMBER REQUIRED**

📱 **ACCEPTED FORMATS:**
• +447123456789 (international)
• 07123456789 (national)

Please provide your UK phone number.
            """
            
        original_phone = phone
        phone_clean = phone.strip()
        
        # Remove common formatting characters
        if PHONE_PATTERNS["has_spaces"].search(phone_clean):
            phone_clean = phone_clean.replace(" ", "")
            
        if PHONE_PATTERNS["has_dashes"].search(phone_clean):
            phone_clean = phone_clean.replace("-", "")
            
        if PHONE_PATTERNS["has_brackets"].search(phone_clean):
            phone_clean = re.sub(r"[\(\)]", "", phone_clean)
            
        # Try to normalize
        try:
            normalized = normalize_phone(phone_clean)
        except:
            normalized = None
            
        # Check various patterns and provide specific feedback
        if not PHONE_PATTERNS["only_digits"].match(phone_clean.replace("+", "")):
            invalid_chars = re.findall(r"[^0-9\+]", phone_clean)
            return f"""
❌ **INVALID CHARACTERS IN PHONE**

You provided: "{original_phone}"
Invalid characters: {', '.join(set(invalid_chars))}

📱 **CORRECT FORMAT:**
• +447123456789 (only digits after +44)
• 07123456789 (only digits)
            """
            
        if not PHONE_PATTERNS["valid_length"].match(phone_clean):
            return f"""
❌ **INCORRECT PHONE LENGTH**

You provided: "{original_phone}" ({len(phone_clean)} characters)

📱 **UK PHONE LENGTHS:**
• +447123456789 (13 characters)
• 07123456789 (11 characters)

Please check your number and try again.
            """
            
        # Check specific UK patterns
        if normalized:
            if PHONE_PATTERNS["uk_international"].match(normalized) or PHONE_PATTERNS["uk_national"].match(normalized):
                # Valid UK number
                display_number = normalized if normalized.startswith('+') else f"+44{normalized[1:]}"
                return f"""
✅ **PHONE NUMBER VALIDATED**

Confirmed: {display_number}

🔒 **PRIVACY:** Used only for team communication.

⚽ **NEXT STEP:** Ready for position/role selection!
                """
            else:
                return f"""
❌ **NOT A UK NUMBER**

You provided: "{original_phone}"

📱 **UK FORMATS REQUIRED:**
• +447123456789 (international)
• 07123456789 (national)

Please provide a UK phone number.
                """
        else:
            # Provide specific suggestions based on what they entered
            suggestions = _generate_phone_suggestions(phone_clean)
            return f"""
❌ **INVALID PHONE FORMAT**

You provided: "{original_phone}"

{suggestions}

Please try again with correct UK format.
            """
            
    except Exception as e:
        logger.error(f"❌ Phone validation error: {e}")
        return f"❌ Phone validation failed: {e!s}"


def _generate_phone_suggestions(phone: str) -> str:
    """Generate specific phone format suggestions."""
    
    suggestions = "💡 **POSSIBLE CORRECTIONS:**\n"
    
    # If it looks like it might be missing country code
    if phone.startswith("07") and len(phone) == 11:
        suggestions += f"• Try: +44{phone[1:]} (add +44, remove first 0)\n"
        
    # If it looks like it has country code but wrong format
    elif phone.startswith("44") and len(phone) == 12:
        suggestions += f"• Try: +{phone} (add + at start)\n"
        
    # If it looks like international but missing digits
    elif phone.startswith("+44") and len(phone) != 13:
        suggestions += "• Check: +44 should be followed by 10 digits\n"
        suggestions += "• Example: +447123456789\n"
        
    # Generic suggestions
    else:
        suggestions += "• Use: +447123456789 (international format)\n"
        suggestions += "• Use: 07123456789 (national format)\n"
        
    return suggestions


@tool("validate_position_enhanced") 
def validate_position_enhanced(position: str, provide_suggestions: bool = True) -> str:
    """
    Enhanced position validation with smart suggestions and alternatives.
    
    Args:
        position: Position to validate
        provide_suggestions: Whether to provide suggestions
        
    Returns:
        Validation result with suggestions
    """
    try:
        if not position:
            return f"""
❌ **POSITION REQUIRED**

⚽ **CHOOSE YOUR POSITION:**
• **Goalkeeper** - Protect the goal
• **Defender** - Defensive play  
• **Midfielder** - Central play
• **Forward** - Attacking play
• **Utility** - Multiple positions

Please select your preferred position.
            """
            
        pos_clean = sanitize_input(position).strip().lower()
        
        # Check if it's a valid position
        if pos_clean in VALID_PLAYER_POSITIONS:
            return f"""
✅ **POSITION CONFIRMED**

Selected: {pos_clean.title()}

🎯 **GREAT CHOICE!** This position involves:
{_get_position_summary(pos_clean)}

Ready to complete registration!
            """
            
        # Check for smart suggestions
        if pos_clean in POSITION_SUGGESTIONS:
            suggested = POSITION_SUGGESTIONS[pos_clean]
            return f"""
🤔 **DID YOU MEAN?**

You entered: "{position}"
Did you mean: **{suggested.title()}**?

⚽ **{suggested.upper()}:** {_get_position_summary(suggested)}

Type **"yes"** to confirm {suggested.title()}, or choose from:
• Goalkeeper • Defender • Midfielder • Forward • Utility
            """
            
        # Find closest matches using fuzzy matching
        closest_matches = _find_closest_positions(pos_clean)
        
        if closest_matches:
            suggestions_text = "\n".join([f"• **{pos.title()}** - {_get_position_summary(pos)}" for pos in closest_matches[:3]])
            return f"""
❓ **POSITION NOT RECOGNIZED**

You entered: "{position}"

🎯 **DID YOU MEAN ONE OF THESE?**
{suggestions_text}

Please type the exact position name or ask for more details!
            """
        else:
            return f"""
❌ **INVALID POSITION**

You entered: "{position}"

⚽ **VALID POSITIONS:**
• **Goalkeeper** - Protect the goal, shot stopping
• **Defender** - Defensive play, tackling  
• **Midfielder** - Central play, passing
• **Forward** - Attacking play, scoring
• **Utility** - Multiple positions, versatile

Please choose one of the above positions.
            """
            
    except Exception as e:
        logger.error(f"❌ Position validation error: {e}")
        return f"❌ Position validation failed: {e!s}"


@tool("validate_role_enhanced")
def validate_role_enhanced(role: str, provide_suggestions: bool = True) -> str:
    """
    Enhanced role validation with smart suggestions and alternatives.
    
    Args:
        role: Role to validate
        provide_suggestions: Whether to provide suggestions
        
    Returns:
        Validation result with suggestions  
    """
    try:
        if not role:
            return f"""
❌ **ROLE REQUIRED**

🎯 **CHOOSE YOUR ROLE:**
• **Coach** - Team coaching
• **Manager** - Team management
• **Assistant** - Supporting role
• **Coordinator** - Events/logistics  
• **Volunteer** - General support
• **Admin** - System administration

Please select your administrative role.
            """
            
        role_clean = sanitize_input(role).strip().lower()
        
        # Check if it's a valid role
        if role_clean in VALID_TEAM_MEMBER_ROLES:
            return f"""
✅ **ROLE CONFIRMED**

Selected: {role_clean.title()}

🎯 **EXCELLENT CHOICE!** This role involves:
{_get_role_summary(role_clean)}

Ready to complete registration!
            """
            
        # Check for smart suggestions
        if role_clean in ROLE_SUGGESTIONS:
            suggested = ROLE_SUGGESTIONS[role_clean]
            return f"""
🤔 **DID YOU MEAN?**

You entered: "{role}"
Did you mean: **{suggested.title()}**?

🎯 **{suggested.upper()}:** {_get_role_summary(suggested)}

Type **"yes"** to confirm {suggested.title()}, or choose from:
• Coach • Manager • Assistant • Coordinator • Volunteer • Admin
            """
            
        # Find closest matches
        closest_matches = _find_closest_roles(role_clean)
        
        if closest_matches:
            suggestions_text = "\n".join([f"• **{r.title()}** - {_get_role_summary(r)}" for r in closest_matches[:3]])
            return f"""
❓ **ROLE NOT RECOGNIZED**

You entered: "{role}"

🎯 **DID YOU MEAN ONE OF THESE?**
{suggestions_text}

Please type the exact role name or ask for more details!
            """
        else:
            return f"""
❌ **INVALID ROLE**

You entered: "{role}"

🎯 **VALID ROLES:**
• **Coach** - Team coaching responsibilities
• **Manager** - Overall team management
• **Assistant** - Supporting coaching role
• **Coordinator** - Events and logistics
• **Volunteer** - General team support  
• **Admin** - System administration

Please choose one of the above roles.
            """
            
    except Exception as e:
        logger.error(f"❌ Role validation error: {e}")
        return f"❌ Role validation failed: {e!s}"


def _get_position_summary(position: str) -> str:
    """Get brief position summary."""
    summaries = {
        "goalkeeper": "Shot stopping and goal protection",
        "defender": "Defensive play and tackling",
        "midfielder": "Central play and ball distribution", 
        "forward": "Attacking play and goal scoring",
        "utility": "Versatile play in multiple positions"
    }
    return summaries.get(position, "Football position")


def _get_role_summary(role: str) -> str:
    """Get brief role summary."""
    summaries = {
        "coach": "Team coaching and tactical guidance",
        "manager": "Overall team management and operations",
        "assistant": "Supporting coaching and admin tasks",
        "coordinator": "Event planning and logistics management", 
        "volunteer": "General team support and assistance",
        "admin": "System administration and technical support"
    }
    return summaries.get(role, "Team administrative role")


def _find_closest_positions(input_pos: str) -> List[str]:
    """Find closest matching positions using simple string similarity."""
    
    matches = []
    for pos in VALID_PLAYER_POSITIONS:
        # Simple fuzzy matching
        if input_pos in pos or pos in input_pos:
            matches.append(pos)
        elif len(input_pos) > 3:
            # Check for partial matches
            if any(char in pos for char in input_pos[:3]):
                matches.append(pos)
                
    return matches[:3]


def _find_closest_roles(input_role: str) -> List[str]:
    """Find closest matching roles using simple string similarity."""
    
    matches = []
    for role in VALID_TEAM_MEMBER_ROLES:
        # Simple fuzzy matching
        if input_role in role or role in input_role:
            matches.append(role)
        elif len(input_role) > 3:
            # Check for partial matches
            if any(char in role for char in input_role[:3]):
                matches.append(role)
                
    return matches[:3]


@tool("comprehensive_validation")
def comprehensive_validation(
    name: str,
    phone: str, 
    role_or_position: str,
    entity_type: str,
    team_id: str
) -> str:
    """
    Comprehensive validation of all registration data with detailed feedback.
    
    Args:
        name: Full name
        phone: Phone number
        role_or_position: Role or position
        entity_type: "player" or "team_member"
        team_id: Team ID
        
    Returns:
        Complete validation results
    """
    try:
        issues = []
        warnings = []
        
        # Validate name
        name_result = validate_name_enhanced(name, entity_type)
        if not name_result.startswith("✅"):
            issues.append(f"**Name:** {name_result.split('**')[1]}")
            
        # Validate phone
        phone_result = validate_phone_enhanced(phone, False)
        if not phone_result.startswith("✅"):
            issues.append(f"**Phone:** {phone_result.split('**')[1]}")
            
        # Validate role/position
        if entity_type == "player":
            pos_result = validate_position_enhanced(role_or_position, False)
            if not pos_result.startswith("✅"):
                issues.append(f"**Position:** {pos_result.split('**')[1]}")
        else:
            role_result = validate_role_enhanced(role_or_position, False)
            if not role_result.startswith("✅"):
                issues.append(f"**Role:** {role_result.split('**')[1]}")
                
        # Return results
        if issues:
            issues_text = "\n".join(issues)
            return f"""
❌ **VALIDATION ISSUES FOUND**

{issues_text}

Please correct the above issues and try again.
            """
        else:
            entity_display = "player" if entity_type == "player" else "team member"
            field_display = "position" if entity_type == "player" else "role"
            
            return f"""
🎉 **ALL DATA VALIDATED!**

✅ **Name:** {name}
✅ **Phone:** {phone}
✅ **{field_display.title()}:** {role_or_position.title()}

Ready to register as {entity_display}!

Type **"CONFIRM"** to complete registration.
            """
            
    except Exception as e:
        logger.error(f"❌ Comprehensive validation error: {e}")
        return f"❌ Validation failed: {e!s}"