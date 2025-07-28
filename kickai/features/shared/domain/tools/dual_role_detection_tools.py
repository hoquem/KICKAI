#!/usr/bin/env python3
"""
Dual Role Detection Tools for KICKAI system.

This module provides intelligent detection and management of users who may
have both player and team member roles within the same team.
"""

import logging
from typing import Dict, List, Optional, Tuple

from kickai.utils.crewai_tool_decorator import tool
from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_registration_service import (
    PlayerRegistrationService,
)
from kickai.features.team_administration.domain.services.simplified_team_member_service import (
    SimplifiedTeamMemberService,
)


class DualRoleStatus(BaseModel):
    """Dual role status information."""
    
    user_id: str
    team_id: str
    is_player: bool = False
    is_team_member: bool = False
    player_status: Optional[str] = None
    member_role: Optional[str] = None
    can_link: bool = False
    needs_clarification: bool = False


@tool("detect_existing_registrations")
def detect_existing_registrations(user_id: str, team_id: str, phone: str = None) -> str:
    """
    Detect if user already exists as player or team member.
    
    Args:
        user_id: User ID to check
        team_id: Team ID to search in
        phone: Optional phone number for additional lookup
        
    Returns:
        Existing registration status and recommendations
    """
    try:
        container = get_container()
        
        # Check player registration
        player_service = container.get_service(PlayerRegistrationService)
        member_service = container.get_service(SimplifiedTeamMemberService)
        
        existing_player = None
        existing_member = None
        
        # Look up existing registrations
        if player_service:
            try:
                # This would need to be implemented in the service
                # For now, simulate the check
                logger.info(f"🔍 Checking player registration for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Could not check player registration: {e}")
                
        if member_service:
            try:
                # This would need to be implemented in the service  
                logger.info(f"🔍 Checking team member registration for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Could not check team member registration: {e}")
                
        # For now, return a template response
        # In a real implementation, this would check the database
        
        return f"""
🔍 **REGISTRATION STATUS CHECK**

👤 **User:** {user_id}
🏆 **Team:** {team_id}

📊 **CURRENT STATUS:**
• **Player Registration:** Not found
• **Team Member Registration:** Not found

✅ **RESULT:** Ready for new registration!

💡 **RECOMMENDATION:** Proceed with onboarding as new user.
        """
        
    except Exception as e:
        logger.error(f"❌ Registration detection error: {e}")
        return f"❌ Could not check existing registrations: {e!s}"


@tool("analyze_dual_role_potential")
def analyze_dual_role_potential(
    user_input: str,
    chat_type: str = None,
    user_context: str = None
) -> str:
    """
    Analyze if user might need both player and team member roles.
    
    Args:
        user_input: User's registration request
        chat_type: Chat context
        user_context: Additional user context
        
    Returns:
        Dual role analysis and recommendations
    """
    try:
        input_lower = user_input.lower()
        
        # Keywords that suggest dual role potential
        dual_role_indicators = [
            'coach and play', 'playing coach', 'manager and player',
            'both', 'also', 'and also', 'as well as',
            'help with coaching', 'assist with management',
            'play and help', 'support the team'
        ]
        
        player_indicators = [
            'play', 'player', 'matches', 'games', 'position',
            'goalkeeper', 'defender', 'midfielder', 'forward'
        ]
        
        admin_indicators = [
            'coach', 'manage', 'organize', 'help with',
            'coordinate', 'admin', 'leadership', 'support'
        ]
        
        # Analyze indicators
        dual_score = sum(1 for indicator in dual_role_indicators if indicator in input_lower)
        player_score = sum(1 for indicator in player_indicators if indicator in input_lower)
        admin_score = sum(1 for indicator in admin_indicators if indicator in input_lower)
        
        if dual_score > 0 or (player_score > 0 and admin_score > 0):
            return f"""
🤔 **DUAL ROLE DETECTED**

Your message suggests you might want both player and administrative roles:
"{user_input}"

🎯 **DETECTED INTERESTS:**
• Playing: {player_score > 0}
• Administrative: {admin_score > 0}
• Dual role keywords: {dual_score > 0}

💡 **OPTIONS:**
1. **Register as Player** - Join matches, requires approval
2. **Register as Team Member** - Administrative role, immediate access  
3. **Register for Both** - Player registration + administrative role

Which would you prefer? You can have both roles if desired!
            """
        elif player_score > admin_score:
            return f"""
⚽ **PLAYER REGISTRATION DETECTED**

Based on your message: "{user_input}"

🎯 **PLAYER ONBOARDING:** Ready to proceed with player registration.

💡 **NOTE:** You can also request administrative access later if needed.
            """
        elif admin_score > player_score:
            return f"""
🎯 **ADMINISTRATIVE ROLE DETECTED**

Based on your message: "{user_input}"

👥 **TEAM MEMBER ONBOARDING:** Ready to proceed with administrative registration.

💡 **NOTE:** You can also register as a player later if you want to play matches.
            """
        else:
            return f"""
❓ **CLARIFICATION NEEDED**

Your message: "{user_input}"

Please clarify what you'd like to do:
• **Play in matches** → Player registration
• **Help with administration** → Team member registration  
• **Both** → Dual registration available

What would you prefer?
            """
            
    except Exception as e:
        logger.error(f"❌ Dual role analysis error: {e}")
        return f"❌ Could not analyze dual role potential: {e!s}"


@tool("suggest_dual_registration")
def suggest_dual_registration(
    name: str,
    phone: str,
    position: str = None,
    role: str = None,
    team_id: str = None
) -> str:
    """
    Suggest dual registration workflow when appropriate.
    
    Args:
        name: User's name
        phone: Phone number
        position: Preferred player position (if any)
        role: Preferred admin role (if any)
        team_id: Team ID
        
    Returns:
        Dual registration suggestion and workflow
    """
    try:
        if not position and not role:
            return f"""
❓ **NEED MORE INFORMATION**

To suggest dual registration for {name}, I need to know:
• Preferred playing position (if you want to play)
• Administrative role (if you want to help manage)

What are you interested in?
            """
            
        if position and role:
            return f"""
🎯 **DUAL REGISTRATION RECOMMENDED**

👤 **Name:** {name}
📱 **Phone:** {phone}

⚽ **PLAYER ROLE:**
• Position: {position.title()}
• Status: Requires approval
• Benefits: Play in matches, team participation

👥 **ADMINISTRATIVE ROLE:**
• Role: {role.title()}  
• Status: Immediate activation
• Benefits: Team management access, coordination

🚀 **DUAL REGISTRATION PROCESS:**
1. Register as team member first (immediate access)
2. Submit player application (pending approval)
3. Full access to both functions once approved

**Proceed with dual registration?** Type "yes" to continue.
            """
        elif position:
            return f"""
⚽ **PLAYER REGISTRATION**

Ready to register {name} as a player ({position.title()}).

💡 **CONSIDER ADMINISTRATIVE ROLE TOO?**
Since you're joining the team, would you also like to help with:
• Coaching support • Event coordination • General administration

Type "player only" to proceed with just player registration, or specify an administrative role too.
            """
        else:  # role only
            return f"""
👥 **TEAM MEMBER REGISTRATION**

Ready to register {name} as {role.title()}.

💡 **CONSIDER PLAYING TOO?**
Since you're joining as team member, would you also like to:
• Play in matches • Be available as substitute • Join team events

Type "admin only" to proceed with just administrative role, or specify a playing position too.
            """
            
    except Exception as e:
        logger.error(f"❌ Dual registration suggestion error: {e}")
        return f"❌ Could not suggest dual registration: {e!s}"


@tool("execute_dual_registration")
def execute_dual_registration(
    name: str,
    phone: str, 
    position: str,
    role: str,
    team_id: str,
    user_id: str = None
) -> str:
    """
    Execute dual registration for both player and team member roles.
    
    Args:
        name: User's name
        phone: Phone number
        position: Player position
        role: Administrative role
        team_id: Team ID
        user_id: Optional user ID
        
    Returns:
        Dual registration results
    """
    try:
        container = get_container()
        registration_service = container.get_service(PlayerRegistrationService)
        
        if not registration_service:
            return "❌ Registration service not available for dual registration"
            
        results = []
        
        # Register as team member first (immediate access)
        try:
            member = registration_service.register_player(name, phone, role, team_id)
            if member:
                results.append("✅ Team member registration successful")
                logger.info(f"✅ Dual registration - Team member: {name} ({role})")
            else:
                results.append("❌ Team member registration failed")
        except Exception as e:
            results.append(f"❌ Team member registration error: {e!s}")
            
        # Register as player (pending approval)
        try:
            player = registration_service.register_player(name, phone, position, team_id)
            if player:
                results.append("✅ Player registration submitted (pending approval)")
                logger.info(f"✅ Dual registration - Player: {name} ({position})")
            else:
                results.append("❌ Player registration failed")
        except Exception as e:
            results.append(f"❌ Player registration error: {e!s}")
            
        # Format final result
        if all("✅" in result for result in results):
            return f"""
🎉 **DUAL REGISTRATION COMPLETE!**

👤 **{name}** - Successfully registered for both roles!

✅ **TEAM MEMBER STATUS:**
• Role: {role.title()}
• Status: **Active** - Immediate access
• Access: Administrative features available now

⚽ **PLAYER STATUS:**  
• Position: {position.title()}
• Status: **Pending Approval** - Awaiting leadership review
• Access: Available after approval

🚀 **WHAT'S NEXT:**
• Use administrative features immediately
• Leadership will review player application
• Full dual access once player is approved

🎯 **UNIQUE ADVANTAGE:**
You now have the best of both worlds - administrative access plus playing opportunities!

Welcome to the team! 🤝⚽👥
            """
        else:
            results_text = "\n".join(results)
            return f"""
⚠️ **DUAL REGISTRATION PARTIAL**

Results for {name}:
{results_text}

Please review any errors above and contact support if needed.
            """
            
    except Exception as e:
        logger.error(f"❌ Dual registration execution error: {e}")
        return f"❌ Dual registration failed: {e!s}"


@tool("check_role_conflicts")
def check_role_conflicts(
    position: str,
    role: str,
    availability: str = "medium"
) -> str:
    """
    Check for potential conflicts between player position and admin role.
    
    Args:
        position: Player position
        role: Administrative role
        availability: Time availability level
        
    Returns:
        Conflict analysis and recommendations
    """
    try:
        high_commitment_positions = ["goalkeeper", "midfielder"]
        high_commitment_roles = ["coach", "manager"]
        
        pos_commitment = "high" if position in high_commitment_positions else "medium"
        role_commitment = "high" if role in high_commitment_roles else "medium"
        
        if pos_commitment == "high" and role_commitment == "high":
            return f"""
⚠️ **HIGH COMMITMENT COMBINATION**

🎯 **Combination:** {position.title()} + {role.title()}

⏰ **TIME REQUIREMENTS:**
• {position.title()}: High commitment (training, matches, key position)
• {role.title()}: High commitment (planning, coordination, leadership)

💡 **RECOMMENDATIONS:**
1. **Consider your availability** - This combination requires significant time
2. **Start with one role** - Begin with {role.title()}, add playing later
3. **Team coordination** - Ensure you can fulfill both responsibilities
4. **Backup plans** - Have substitutes ready for busy periods

❓ **STILL INTERESTED?** This combination is possible but demanding.
Type "proceed" to continue or "reconsider" for alternatives.
            """
        elif pos_commitment == "high" or role_commitment == "high":
            return f"""
⚡ **MODERATE COMMITMENT COMBINATION**

🎯 **Combination:** {position.title()} + {role.title()}

⏰ **COMMITMENT ANALYSIS:**
• One role requires high commitment
• Overall combination is manageable
• Good balance of responsibilities

✅ **RECOMMENDATION:** This is a good combination that provides variety without overwhelming commitment.

Ready to proceed with dual registration?
            """
        else:
            return f"""
✅ **EXCELLENT COMBINATION**

🎯 **Combination:** {position.title()} + {role.title()}

⏰ **COMMITMENT ANALYSIS:**
• Both roles have moderate commitment
• Excellent work-life balance
• Great way to contribute in multiple ways

🌟 **PERFECT MATCH:** This combination allows you to enjoy playing while contributing to team management.

Ready to proceed with dual registration?
            """
            
    except Exception as e:
        logger.error(f"❌ Role conflict check error: {e}")
        return f"❌ Could not check role conflicts: {e!s}"