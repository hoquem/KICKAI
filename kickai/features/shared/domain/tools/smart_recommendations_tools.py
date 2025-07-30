#!/usr/bin/env python3
"""
Smart Recommendations Tools for KICKAI onboarding system.

This module provides intelligent recommendations for roles, positions,
and onboarding paths based on user characteristics, team needs, and preferences.
"""

from loguru import logger
from pydantic import BaseModel

from kickai.utils.crewai_tool_decorator import tool


class UserProfile(BaseModel):
    """User profile for recommendations."""

    experience_level: str = "beginner"  # beginner, intermediate, experienced
    time_availability: str = "medium"  # low, medium, high
    interests: list[str] = []  # coaching, playing, admin, logistics
    skills: list[str] = []  # technical, leadership, organization
    preferences: dict[str, str] = {}  # various preferences


class RecommendationResult(BaseModel):
    """Recommendation result structure."""

    primary_recommendation: str
    alternatives: list[str]
    reasoning: str
    confidence: str  # low, medium, high
    benefits: list[str]
    considerations: list[str]


@tool("get_smart_position_recommendations")
def get_smart_position_recommendations(
    experience: str = "beginner",
    physical_attributes: str = "average",
    playing_style: str = "versatile",
    availability: str = "medium",
) -> str:
    """
    Get smart position recommendations based on user characteristics.

    Args:
        experience: "beginner", "intermediate", "experienced"
        physical_attributes: "tall", "fast", "strong", "agile", "average"
        playing_style: "attacking", "defensive", "versatile", "technical"
        availability: "low", "medium", "high"

    Returns:
        Smart position recommendations with reasoning
    """
    try:
        recommendations = []

        # Algorithm for position recommendation
        if experience == "beginner":
            if playing_style == "defensive":
                recommendations = [("defender", 0.8), ("utility", 0.6)]
            elif playing_style == "attacking":
                recommendations = [("forward", 0.7), ("utility", 0.8)]
            else:  # versatile or technical
                recommendations = [("utility", 0.9), ("midfielder", 0.6)]
        elif experience == "intermediate":
            if physical_attributes == "tall":
                recommendations = [("defender", 0.8), ("goalkeeper", 0.6)]
            elif physical_attributes == "fast":
                recommendations = [("forward", 0.8), ("midfielder", 0.7)]
            elif playing_style == "technical":
                recommendations = [("midfielder", 0.9), ("forward", 0.6)]
            else:
                recommendations = [("defender", 0.7), ("midfielder", 0.7)]
        else:  # experienced
            if playing_style == "defensive":
                recommendations = [("defender", 0.9), ("goalkeeper", 0.7)]
            elif playing_style == "attacking":
                recommendations = [("forward", 0.9), ("midfielder", 0.8)]
            else:
                recommendations = [("midfielder", 0.9), ("utility", 0.7)]

        # Sort by confidence and take top 3
        recommendations.sort(key=lambda x: x[1], reverse=True)
        top_recs = recommendations[:3]

        # Build response
        response = f"""
🎯 **SMART POSITION RECOMMENDATIONS**

📊 **Based on your profile:**
• Experience: {experience.title()}
• Physical: {physical_attributes.title()}  
• Style: {playing_style.title()}
• Availability: {availability.title()}

🏆 **TOP RECOMMENDATIONS:**

"""

        for i, (position, confidence) in enumerate(top_recs, 1):
            confidence_level = (
                "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Moderate"
            )

            response += f"""**{i}. {position.upper()}** ⭐ ({confidence_level} match)
{_get_position_benefits(position, experience, playing_style)}

"""

        response += f"""
💡 **REASONING:**
{_get_position_reasoning(top_recs[0][0], experience, physical_attributes, playing_style)}

❓ **WANT MORE DETAILS?** Ask me to explain any of these positions in detail!
        """

        return response.strip()

    except Exception as e:
        logger.error(f"❌ Position recommendation error: {e}")
        return f"❌ Could not generate position recommendations: {e!s}"


@tool("get_smart_role_recommendations")
def get_smart_role_recommendations(
    leadership_experience: str = "none",
    technical_skills: str = "basic",
    organization_skills: str = "average",
    time_commitment: str = "medium",
    interests: str = "general",
) -> str:
    """
    Get smart role recommendations based on skills and preferences.

    Args:
        leadership_experience: "none", "some", "experienced"
        technical_skills: "basic", "intermediate", "advanced"
        organization_skills: "poor", "average", "good", "excellent"
        time_commitment: "low", "medium", "high"
        interests: "coaching", "admin", "logistics", "general"

    Returns:
        Smart role recommendations with reasoning
    """
    try:
        recommendations = []

        # Algorithm for role recommendation
        if leadership_experience == "experienced":
            if interests == "coaching":
                recommendations = [("coach", 0.9), ("manager", 0.7)]
            elif time_commitment == "high":
                recommendations = [("manager", 0.9), ("coach", 0.8)]
            else:
                recommendations = [("assistant", 0.8), ("coordinator", 0.7)]
        elif leadership_experience == "some":
            if organization_skills in ["good", "excellent"]:
                recommendations = [("coordinator", 0.8), ("assistant", 0.7)]
            elif technical_skills == "advanced":
                recommendations = [("admin", 0.8), ("assistant", 0.6)]
            else:
                recommendations = [("assistant", 0.8), ("volunteer", 0.6)]
        else:  # none
            if time_commitment == "low":
                recommendations = [("volunteer", 0.9), ("assistant", 0.5)]
            elif organization_skills in ["good", "excellent"]:
                recommendations = [("coordinator", 0.7), ("volunteer", 0.8)]
            elif technical_skills in ["intermediate", "advanced"]:
                recommendations = [("admin", 0.7), ("volunteer", 0.8)]
            else:
                recommendations = [("volunteer", 0.9), ("assistant", 0.6)]

        # Sort and format
        recommendations.sort(key=lambda x: x[1], reverse=True)
        top_recs = recommendations[:3]

        response = f"""
🎯 **SMART ROLE RECOMMENDATIONS**

📊 **Based on your profile:**
• Leadership: {leadership_experience.title()}
• Technical: {technical_skills.title()}
• Organization: {organization_skills.title()}
• Time: {time_commitment.title()}
• Interests: {interests.title()}

🏆 **TOP RECOMMENDATIONS:**

"""

        for i, (role, confidence) in enumerate(top_recs, 1):
            confidence_level = (
                "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Moderate"
            )

            response += f"""**{i}. {role.upper()}** ⭐ ({confidence_level} match)
{_get_role_benefits(role, leadership_experience, time_commitment)}

"""

        response += f"""
💡 **REASONING:**
{_get_role_reasoning(top_recs[0][0], leadership_experience, technical_skills, organization_skills)}

❓ **WANT MORE DETAILS?** Ask me to explain any of these roles in detail!
        """

        return response.strip()

    except Exception as e:
        logger.error(f"❌ Role recommendation error: {e}")
        return f"❌ Could not generate role recommendations: {e!s}"


@tool("get_onboarding_path_recommendation")
def get_onboarding_path_recommendation(
    primary_interest: str,
    secondary_interest: str = None,
    urgency: str = "normal",
    complexity_preference: str = "simple",
) -> str:
    """
    Recommend optimal onboarding path based on interests and preferences.

    Args:
        primary_interest: "playing", "administration", "both"
        secondary_interest: Optional secondary interest
        urgency: "low", "normal", "high"
        complexity_preference: "simple", "moderate", "comprehensive"

    Returns:
        Onboarding path recommendations
    """
    try:
        if primary_interest == "both" or secondary_interest:
            path = _get_dual_path_recommendation(urgency, complexity_preference)
        elif primary_interest == "playing":
            path = _get_player_path_recommendation(urgency, complexity_preference)
        elif primary_interest == "administration":
            path = _get_admin_path_recommendation(urgency, complexity_preference)
        else:
            path = _get_default_path_recommendation()

        return f"""
🛤️ **RECOMMENDED ONBOARDING PATH**

🎯 **Primary Interest:** {primary_interest.title()}
{f"🎯 **Secondary Interest:** {secondary_interest.title()}" if secondary_interest else ""}
⚡ **Urgency:** {urgency.title()}
🔧 **Complexity:** {complexity_preference.title()}

{path}

💡 **TIPS FOR SUCCESS:**
• Take your time with each step
• Ask questions if anything is unclear
• We're here to help throughout the process
• You can always change paths later

🚀 **READY TO START?** Just say "begin onboarding" and I'll guide you!
        """

    except Exception as e:
        logger.error(f"❌ Path recommendation error: {e}")
        return f"❌ Could not recommend onboarding path: {e!s}"


def _get_position_benefits(position: str, experience: str, style: str) -> str:
    """Get position-specific benefits."""
    benefits = {
        "goalkeeper": "• Specialized role with high impact\n• Great for those who enjoy pressure\n• Unique skills development",
        "defender": "• Solid foundation for learning\n• Important tactical role\n• Good for defensive-minded players",
        "midfielder": "• Central to team play\n• Develops all-around skills\n• High involvement in games",
        "forward": "• Exciting attacking role\n• Goal-scoring opportunities\n• Dynamic and fast-paced",
        "utility": "• Learn multiple positions\n• High flexibility and value\n• Great for beginners",
    }
    return benefits.get(position, "• Excellent football position")


def _get_role_benefits(role: str, experience: str, commitment: str) -> str:
    """Get role-specific benefits."""
    benefits = {
        "coach": "• Direct impact on team development\n• Leadership and tactical growth\n• Highly rewarding responsibility",
        "manager": "• Overall team oversight\n• Strategic decision making\n• Comprehensive team involvement",
        "assistant": "• Support without full responsibility\n• Learning opportunity\n• Flexible involvement level",
        "coordinator": "• Organizational skills development\n• Event planning experience\n• Important team function",
        "volunteer": "• Flexible contribution level\n• Great way to start\n• Community building focus",
        "admin": "• Technical skills utilization\n• System management\n• Behind-the-scenes impact",
    }
    return benefits.get(role, "• Valuable team contribution")


def _get_position_reasoning(position: str, experience: str, attributes: str, style: str) -> str:
    """Get reasoning for position recommendation."""
    return f"Based on your {experience} experience level and {style} playing style, {position} offers the best match for your development and team contribution."


def _get_role_reasoning(role: str, leadership: str, technical: str, organization: str) -> str:
    """Get reasoning for role recommendation."""
    return f"With {leadership} leadership experience and {organization} organization skills, {role} aligns perfectly with your strengths and interests."


def _get_dual_path_recommendation(urgency: str, complexity: str) -> str:
    """Get dual role path recommendation."""
    if urgency == "high":
        return """
🚀 **FAST-TRACK DUAL PATH**

⚡ **Recommended Sequence:**
1. **Quick Team Member Registration** (5 minutes)
   • Immediate administrative access
   • Start contributing right away

2. **Player Application Submission** (10 minutes)  
   • Submit for approval process
   • Begin while admin access is active

3. **Dual Role Orientation** (15 minutes)
   • Learn to balance both roles
   • Access all team features

⏱️ **Total Time:** 30 minutes to full dual access!
        """
    else:
        return """
🎯 **COMPREHENSIVE DUAL PATH**

📚 **Recommended Sequence:**
1. **Discovery Phase** (Day 1)
   • Explore both role options
   • Understand responsibilities and benefits
   • Get personalized recommendations

2. **Primary Registration** (Day 2-3)
   • Start with your primary interest  
   • Get comfortable with one role first

3. **Secondary Addition** (Week 2)
   • Add second role once settled
   • Full dual role training and support

4. **Integration Mastery** (Month 1)
   • Master both roles
   • Become dual-role expert

📈 **Benefits:** Thorough understanding, confident execution, maximum impact
        """


def _get_player_path_recommendation(urgency: str, complexity: str) -> str:
    """Get player-only path recommendation."""
    return """
⚽ **PLAYER ONBOARDING PATH**

📋 **Recommended Steps:**
1. **Position Discovery** (5 minutes)
   • Understand different positions
   • Get personalized position recommendation

2. **Registration Process** (10 minutes)
   • Submit player application
   • Provide required information

3. **Approval Phase** (1-3 days)
   • Leadership review
   • Welcome to active roster

🎯 **Total Timeline:** Active player within 3 days!
    """


def _get_admin_path_recommendation(urgency: str, complexity: str) -> str:
    """Get admin-only path recommendation."""
    return """
👥 **TEAM MEMBER ONBOARDING PATH**

📋 **Recommended Steps:**
1. **Role Exploration** (5 minutes)
   • Discover administrative roles
   • Get personalized role recommendation

2. **Registration & Activation** (10 minutes)
   • Complete team member registration
   • Immediate administrative access

3. **Orientation & Training** (30 minutes)
   • Learn administrative features
   • Get familiar with team systems

⚡ **Total Timeline:** Full admin access within 1 hour!
    """


def _get_default_path_recommendation() -> str:
    """Get default path recommendation."""
    return """
🎯 **DISCOVERY-FIRST PATH**

📋 **Recommended Steps:**
1. **Interest Assessment** (5 minutes)
   • Determine your primary interests
   • Understand available opportunities

2. **Personalized Recommendations** (10 minutes)
   • Get tailored suggestions
   • Compare options and benefits

3. **Guided Registration** (15 minutes)
   • Step-by-step registration process
   • Full support throughout

💡 **Perfect for:** Those wanting to explore options before committing
    """


@tool("analyze_team_needs_for_recommendations")
def analyze_team_needs_for_recommendations(team_id: str) -> str:
    """
    Analyze current team needs to provide contextual recommendations.

    Args:
        team_id: Team ID to analyze

    Returns:
        Team needs analysis with recommendations
    """
    try:
        # In a real implementation, this would query the database
        # for current team composition and identify gaps

        return f"""
📊 **TEAM NEEDS ANALYSIS**

🏆 **Team:** {team_id}

⚽ **PLAYER NEEDS:**
🔴 **High Priority:**
• Goalkeeper (1 needed)
• Midfielder (2 needed)

🟡 **Medium Priority:**  
• Defender (1 needed)
• Forward (backup needed)

👥 **ADMINISTRATIVE NEEDS:**
🔴 **High Priority:**
• Match Coordinator (events/logistics)
• Assistant Coach (training support)

🟡 **Medium Priority:**
• Social Media Admin (communications)
• Equipment Manager (logistics)

🎯 **RECOMMENDATIONS FOR NEW JOINERS:**

**If you're interested in PLAYING:**
• **Goalkeeper** - Immediate starting position available
• **Midfielder** - High demand, great integration opportunity

**If you're interested in ADMINISTRATION:**
• **Coordinator** - Perfect timing for someone organized
• **Assistant** - Great learning opportunity with experienced coach

🌟 **DUAL ROLE OPPORTUNITIES:**
• Player-Coach combinations highly valued
• Midfielder + Coordinator = Perfect match
• Forward + Assistant Coach = Excellent development path

💡 **TEAM BENEFITS:**
Joining now means immediate impact and rapid integration!
        """

    except Exception as e:
        logger.error(f"❌ Team needs analysis error: {e}")
        return f"❌ Could not analyze team needs: {e!s}"


@tool("get_personalized_welcome_message")
def get_personalized_welcome_message(
    name: str, recommended_role: str, registration_type: str, confidence_level: str = "high"
) -> str:
    """
    Generate personalized welcome message based on recommendations.

    Args:
        name: User's name
        recommended_role: Recommended role/position
        registration_type: "player", "team_member", "dual"
        confidence_level: Recommendation confidence

    Returns:
        Personalized welcome message
    """
    try:
        confidence_emoji = (
            "🎯" if confidence_level == "high" else "👍" if confidence_level == "medium" else "💡"
        )

        if registration_type == "dual":
            return f"""
🎉 **WELCOME {name.upper()}!**

{confidence_emoji} **PERSONALIZED RECOMMENDATION:** Based on your interests and our analysis, you're perfectly suited for **DUAL ROLES**!

⚽👥 **YOUR RECOMMENDED PATH:**
• **Player:** {recommended_role.split("+")[0].strip().title()}
• **Team Member:** {recommended_role.split("+")[1].strip().title()}

🌟 **WHY THIS WORKS FOR YOU:**
• Best of both worlds - playing AND contributing administratively
• Immediate admin access while player approval processes
• Unique value to the team through multiple contributions
• Flexible involvement based on your availability

🚀 **WHAT HAPPENS NEXT:**
1. Quick team member registration (immediate access)
2. Player application submission (approval process)
3. Full onboarding and orientation
4. Welcome to your dual role adventure!

You're going to make an amazing addition to our team! 🤝⚽👥
            """
        elif registration_type == "player":
            return f"""
🎉 **WELCOME {name.upper()}!**

{confidence_emoji} **PERSONALIZED RECOMMENDATION:** You're a perfect fit for **{recommended_role.upper()}**!

⚽ **YOUR FOOTBALL JOURNEY STARTS HERE:**

🎯 **Position Match:** {recommended_role.title()}
✨ **Confidence Level:** {confidence_level.title()} match
🏆 **Team Impact:** High potential

🌟 **WHY THIS POSITION SUITS YOU:**
• Aligns with your playing style and experience
• Great learning and development opportunity  
• Important role in our team strategy
• Perfect for your availability level

🚀 **NEXT STEPS:**
1. Complete registration process
2. Submit for leadership approval
3. Join the active player roster
4. Start your football adventure!

Ready to show what you can do on the pitch! ⚽🔥
            """
        else:  # team_member
            return f"""
🎉 **WELCOME {name.upper()}!**

{confidence_emoji} **PERSONALIZED RECOMMENDATION:** You're ideally suited for **{recommended_role.upper()}**!

👥 **YOUR LEADERSHIP JOURNEY BEGINS:**

🎯 **Role Match:** {recommended_role.title()}
✨ **Confidence Level:** {confidence_level.title()} match
🏆 **Team Impact:** Immediate and valuable

🌟 **WHY THIS ROLE FITS YOU:**
• Matches your skills and experience level
• Perfect time commitment for your availability
• High-impact contribution to team success
• Great development opportunity

🚀 **WHAT HAPPENS NOW:**
1. Complete registration (immediate access!)
2. Administrative features available instantly
3. Orientation and training provided
4. Start making a difference right away!

Thank you for stepping up to help lead our team! 👥🌟
            """

    except Exception as e:
        logger.error(f"❌ Welcome message generation error: {e}")
        return f"❌ Could not generate welcome message: {e!s}"
