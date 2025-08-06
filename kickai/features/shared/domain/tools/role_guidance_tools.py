#!/usr/bin/env python3
"""
Role-Specific Guidance Tools for KICKAI system.

This module provides detailed guidance and explanations for different
player positions and team member roles during onboarding.
"""

from loguru import logger

from kickai.utils.constants import VALID_PLAYER_POSITIONS, VALID_TEAM_MEMBER_ROLES
from kickai.utils.crewai_tool_decorator import tool

# Detailed position descriptions
PLAYER_POSITION_GUIDE: dict[str, dict[str, str]] = {
    "goalkeeper": {
        "description": "The last line of defense, protecting the goal",
        "responsibilities": [
            "Shot stopping and penalty saves",
            "Distribution and throwing",
            "Commanding the penalty area",
            "Communication with defense",
        ],
        "skills": "Reflexes, handling, distribution, communication",
        "commitment": "High - Key position requiring consistent availability",
    },
    "defender": {
        "description": "Defensive players who protect against attacks",
        "responsibilities": [
            "Marking opposing attackers",
            "Tackling and interceptions",
            "Aerial duels and clearing",
            "Supporting attacking play",
        ],
        "skills": "Tackling, heading, positioning, passing",
        "commitment": "Medium-High - Important for team structure",
    },
    "midfielder": {
        "description": "The engine room, linking defense and attack",
        "responsibilities": [
            "Ball distribution and passing",
            "Pressing and defensive work",
            "Creating attacking opportunities",
            "Box-to-box covering",
        ],
        "skills": "Passing, stamina, vision, versatility",
        "commitment": "High - Central to team play",
    },
    "forward": {
        "description": "Primary goal scorers and attacking threats",
        "responsibilities": [
            "Scoring goals and finishing",
            "Creating space for teammates",
            "Pressing opposing defense",
            "Hold-up play and link-up",
        ],
        "skills": "Finishing, pace, movement, first touch",
        "commitment": "Medium-High - Key for scoring goals",
    },
    "utility": {
        "description": "Versatile players who can play multiple positions",
        "responsibilities": [
            "Adapting to different positions",
            "Providing squad depth",
            "Learning multiple roles",
            "Supporting team needs",
        ],
        "skills": "Adaptability, football intelligence, versatility",
        "commitment": "Medium - Flexible availability helpful",
    },
}

# Team member role descriptions
TEAM_MEMBER_ROLE_GUIDE: dict[str, dict[str, str]] = {
    "coach": {
        "description": "Lead the team's tactical and technical development",
        "responsibilities": [
            "Plan and conduct training sessions",
            "Develop match tactics and strategy",
            "Player development and feedback",
            "Match day team selection",
        ],
        "skills": "Tactical knowledge, communication, leadership, organization",
        "time_commitment": "High - Training sessions, matches, planning",
        "access_level": "Full - Team management and player data",
    },
    "manager": {
        "description": "Overall team management and operations",
        "responsibilities": [
            "Team logistics and coordination",
            "Communication with players",
            "Administrative oversight",
            "Liaison with leagues/opponents",
        ],
        "skills": "Organization, communication, problem-solving, leadership",
        "time_commitment": "High - Ongoing management duties",
        "access_level": "Full - All team operations",
    },
    "assistant": {
        "description": "Support coaching staff and team operations",
        "responsibilities": [
            "Assist with training sessions",
            "Help with match preparation",
            "Support player development",
            "Administrative support",
        ],
        "skills": "Supportive mindset, reliability, football knowledge",
        "time_commitment": "Medium - Training and match support",
        "access_level": "Medium - Player support functions",
    },
    "coordinator": {
        "description": "Organize events, logistics, and team activities",
        "responsibilities": [
            "Match and training scheduling",
            "Event planning and organization",
            "Equipment and facility management",
            "Communication coordination",
        ],
        "skills": "Organization, planning, attention to detail, communication",
        "time_commitment": "Medium - Event-based involvement",
        "access_level": "Medium - Scheduling and logistics",
    },
    "volunteer": {
        "description": "General team support in various capacities",
        "responsibilities": [
            "Help with match day operations",
            "Support team events and activities",
            "General assistance as needed",
            "Community and social activities",
        ],
        "skills": "Enthusiasm, reliability, team spirit, flexibility",
        "time_commitment": "Low-Medium - Flexible involvement",
        "access_level": "Basic - General team support",
    },
    "admin": {
        "description": "System administration and technical oversight",
        "responsibilities": [
            "Manage team data and records",
            "System configuration and maintenance",
            "User access and permissions",
            "Technical support and troubleshooting",
        ],
        "skills": "Technical aptitude, attention to detail, problem-solving",
        "time_commitment": "Medium - Ongoing system maintenance",
        "access_level": "Full - Administrative privileges",
    },
}


@tool("explain_player_position")
def explain_player_position(position: str, detail_level: str = "standard") -> str:
    """
    Provide detailed explanation of a football player position.

    Args:
        position: Player position to explain
        detail_level: "brief", "standard", or "detailed"

    Returns:
        Position explanation and guidance
    """
    try:
        pos_lower = position.lower().strip()

        if pos_lower not in PLAYER_POSITION_GUIDE:
            valid_positions = ", ".join([p.title() for p in VALID_PLAYER_POSITIONS])
            return f"❌ Unknown position '{position}'. Valid positions: {valid_positions}"

        guide = PLAYER_POSITION_GUIDE[pos_lower]

        if detail_level == "brief":
            return f"""
⚽ **{position.upper()}**
{guide["description"]}

💪 **Key Skills:** {guide["skills"]}
⏰ **Commitment:** {guide["commitment"]}
            """

        elif detail_level == "detailed":
            responsibilities = "\n".join([f"• {resp}" for resp in guide["responsibilities"]])
            return f"""
⚽ **{position.upper()} - DETAILED GUIDE**

📋 **DESCRIPTION:**
{guide["description"]}

🎯 **KEY RESPONSIBILITIES:**
{responsibilities}

💪 **REQUIRED SKILLS:**
{guide["skills"]}

⏰ **COMMITMENT LEVEL:**
{guide["commitment"]}

❓ **IS THIS RIGHT FOR YOU?**
Consider your football experience, availability, and interest in this role.
Choose this position if you enjoy these responsibilities and can commit the time needed.
            """
        else:  # standard
            responsibilities = "\n".join([f"• {resp}" for resp in guide["responsibilities"][:2]])
            return f"""
⚽ **{position.upper()}**

📋 **ROLE:** {guide["description"]}

🎯 **MAIN DUTIES:**
{responsibilities}

💪 **KEY SKILLS:** {guide["skills"]}
⏰ **COMMITMENT:** {guide["commitment"]}

❓ **GOOD FIT?** This position suits players who are {guide["skills"].split(",")[0].lower()} and can {guide["commitment"].split(" - ")[1].lower()}.
            """

    except Exception as e:
        logger.error(f"❌ Position explanation error: {e}")
        return f"❌ Could not explain position: {e!s}"


@tool("explain_team_role")
def explain_team_role(role: str, detail_level: str = "standard") -> str:
    """
    Provide detailed explanation of a team member role.

    Args:
        role: Team member role to explain
        detail_level: "brief", "standard", or "detailed"

    Returns:
        Role explanation and guidance
    """
    try:
        role_lower = role.lower().strip()

        if role_lower not in TEAM_MEMBER_ROLE_GUIDE:
            valid_roles = ", ".join([r.title() for r in VALID_TEAM_MEMBER_ROLES])
            return f"❌ Unknown role '{role}'. Valid roles: {valid_roles}"

        guide = TEAM_MEMBER_ROLE_GUIDE[role_lower]

        if detail_level == "brief":
            return f"""
🎯 **{role.upper()}**
{guide["description"]}

💼 **Skills Needed:** {guide["skills"]}
⏰ **Time Commitment:** {guide["time_commitment"]}
            """

        elif detail_level == "detailed":
            responsibilities = "\n".join([f"• {resp}" for resp in guide["responsibilities"]])
            return f"""
🎯 **{role.upper()} - DETAILED GUIDE**

📋 **DESCRIPTION:**
{guide["description"]}

🎯 **KEY RESPONSIBILITIES:**
{responsibilities}

💼 **REQUIRED SKILLS:**
{guide["skills"]}

⏰ **TIME COMMITMENT:**
{guide["time_commitment"]}

🔐 **ACCESS LEVEL:**
{guide["access_level"]}

❓ **IS THIS RIGHT FOR YOU?**
This role is perfect if you have {guide["skills"].split(",")[0].lower()} skills and can commit to {guide["time_commitment"].split(" - ")[0].lower()} involvement.
You'll have {guide["access_level"].split(" - ")[0].lower()} access to team systems.
            """
        else:  # standard
            responsibilities = "\n".join([f"• {resp}" for resp in guide["responsibilities"][:2]])
            return f"""
🎯 **{role.upper()}**

📋 **ROLE:** {guide["description"]}

🎯 **MAIN DUTIES:**
{responsibilities}

💼 **SKILLS NEEDED:** {guide["skills"]}
⏰ **TIME COMMITMENT:** {guide["time_commitment"]}
🔐 **ACCESS:** {guide["access_level"]}

❓ **GOOD FIT?** Perfect if you have {guide["skills"].split(",")[0].lower()} skills and want {guide["time_commitment"].split(" - ")[0].lower()} involvement.
            """

    except Exception as e:
        logger.error(f"❌ Role explanation error: {e}")
        return f"❌ Could not explain role: {e!s}"


@tool("compare_positions")
def compare_positions(position1: str, position2: str) -> str:
    """
    Compare two player positions to help with selection.

    Args:
        position1: First position to compare
        position2: Second position to compare

    Returns:
        Comparison of the two positions
    """
    try:
        pos1_lower = position1.lower().strip()
        pos2_lower = position2.lower().strip()

        if pos1_lower not in PLAYER_POSITION_GUIDE or pos2_lower not in PLAYER_POSITION_GUIDE:
            return "❌ One or both positions are invalid"

        guide1 = PLAYER_POSITION_GUIDE[pos1_lower]
        guide2 = PLAYER_POSITION_GUIDE[pos2_lower]

        return f"""
⚽ **POSITION COMPARISON**

**{position1.upper()}:**
• {guide1["description"]}
• Skills: {guide1["skills"]}
• Commitment: {guide1["commitment"]}

**{position2.upper()}:**
• {guide2["description"]}
• Skills: {guide2["skills"]}
• Commitment: {guide2["commitment"]}

🤔 **DECISION HELP:**
Choose {position1} if you prefer {guide1["skills"].split(",")[0].lower()} and {guide1["commitment"].split(" - ")[1].lower()}.
Choose {position2} if you prefer {guide2["skills"].split(",")[0].lower()} and {guide2["commitment"].split(" - ")[1].lower()}.
        """

    except Exception as e:
        logger.error(f"❌ Position comparison error: {e}")
        return f"❌ Could not compare positions: {e!s}"


@tool("compare_roles")
def compare_roles(role1: str, role2: str) -> str:
    """
    Compare two team member roles to help with selection.

    Args:
        role1: First role to compare
        role2: Second role to compare

    Returns:
        Comparison of the two roles
    """
    try:
        role1_lower = role1.lower().strip()
        role2_lower = role2.lower().strip()

        if role1_lower not in TEAM_MEMBER_ROLE_GUIDE or role2_lower not in TEAM_MEMBER_ROLE_GUIDE:
            return "❌ One or both roles are invalid"

        guide1 = TEAM_MEMBER_ROLE_GUIDE[role1_lower]
        guide2 = TEAM_MEMBER_ROLE_GUIDE[role2_lower]

        return f"""
🎯 **ROLE COMPARISON**

**{role1.upper()}:**
• {guide1["description"]}
• Skills: {guide1["skills"]}
• Time: {guide1["time_commitment"]}
• Access: {guide1["access_level"]}

**{role2.upper()}:**
• {guide2["description"]}
• Skills: {guide2["skills"]}
• Time: {guide2["time_commitment"]}
• Access: {guide2["access_level"]}

🤔 **DECISION HELP:**
Choose {role1} if you want {guide1["time_commitment"].split(" - ")[0].lower()} commitment and {guide1["access_level"].split(" - ")[0].lower()} access.
Choose {role2} if you want {guide2["time_commitment"].split(" - ")[0].lower()} commitment and {guide2["access_level"].split(" - ")[0].lower()} access.
        """

    except Exception as e:
        logger.error(f"❌ Role comparison error: {e}")
        return f"❌ Could not compare roles: {e!s}"


@tool("get_role_recommendations")
def get_role_recommendations(
    experience_level: str = "beginner",
    time_availability: str = "medium",
    interests: str = "general",
) -> str:
    """
    Get personalized role recommendations based on user preferences.

    Args:
        experience_level: "beginner", "intermediate", "experienced"
        time_availability: "low", "medium", "high"
        interests: "coaching", "admin", "logistics", "general"

    Returns:
        Personalized role recommendations
    """
    try:
        recommendations = []

        # Base recommendations on time availability
        if time_availability == "low":
            base_roles = ["volunteer", "assistant"]
        elif time_availability == "high":
            base_roles = ["coach", "manager", "admin"]
        else:  # medium
            base_roles = ["coordinator", "assistant", "admin"]

        # Filter by interests
        if interests == "coaching":
            base_roles = [r for r in base_roles if r in ["coach", "assistant"]]
            if not base_roles:
                base_roles = ["coach", "assistant"]
        elif interests == "admin":
            base_roles = [r for r in base_roles if r in ["admin", "manager"]]
            if not base_roles:
                base_roles = ["admin", "coordinator"]
        elif interests == "logistics":
            base_roles = [r for r in base_roles if r in ["coordinator", "manager"]]
            if not base_roles:
                base_roles = ["coordinator"]

        # Build recommendation message
        rec_text = "🎯 **PERSONALIZED ROLE RECOMMENDATIONS**\n\n"
        rec_text += f"📊 **Based on:** {experience_level.title()} experience, {time_availability} availability, {interests} interests\n\n"

        for i, role in enumerate(base_roles[:3], 1):  # Top 3 recommendations
            guide = TEAM_MEMBER_ROLE_GUIDE[role]

            rec_text += f"**{i}. {role.upper()}** ⭐\n"
            rec_text += f"• {guide['description']}\n"
            rec_text += f"• Time: {guide['time_commitment']}\n"
            rec_text += f"• Access: {guide['access_level']}\n\n"

        rec_text += "❓ **WANT MORE INFO?** Ask me to explain any of these roles in detail!"

        return rec_text

    except Exception as e:
        logger.error(f"❌ Recommendation error: {e}")
        return f"❌ Could not generate recommendations: {e!s}"
