#!/usr/bin/env python3
"""
Team member management tools for KICKAI system.

This module provides tools for team member management and information retrieval.
"""

import asyncio
import logging
from typing import Optional

from crewai.tools import tool

from src.core.dependency_container import get_container
from src.features.team_administration.domain.services.team_member_service import TeamMemberService

logger = logging.getLogger(__name__)


@tool("get_my_team_member_status")
def get_my_team_member_status(team_id: str, user_id: str) -> str:
    """
    Get current user's team member status and information.
    This tool is for team members in the leadership chat.
    For players in main chat, use get_my_status.
    Uses context information from the task description.
    
    Returns:
        Team member status information or error message
    """
    try:
        # For now, we'll use a simplified approach that works with the current system
        # The agent system should provide this information in the task description
        
        # Lazy-load services only when needed
        try:
            container = get_container()
            team_member_service = container.get_service(TeamMemberService)
        except Exception as e:
            logger.error(f"❌ Failed to get TeamMemberService from container: {e}")
            return "❌ Service temporarily unavailable. Please try again in a moment."

        # Parameters are now passed explicitly - no context extraction needed
        logger.info(f"🔧 get_my_team_member_status called with team_id: {team_id}, user_id: {user_id}")
        
        # Get team member status
        status = asyncio.run(team_member_service.get_my_status(user_id, team_id))
        logger.info(f"✅ Retrieved team member status for {user_id}")
        return status

    except Exception as e:
        logger.error(f"❌ Failed to get team member status: {e}")
        return f"❌ Failed to get team member status: {e!s}"


@tool("get_team_members")
def get_team_members(team_id: str, role: Optional[str] = None) -> str:
    """
    Get team members for a team, optionally filtered by role.
    
    Args:
        team_id: The team ID
        role: Optional role to filter by
        
    Returns:
        Formatted string with team member information
    """
    try:
        # Lazy-load services only when needed
        try:
            container = get_container()
            team_member_service = container.get_service(TeamMemberService)
        except Exception as e:
            logger.error(f"❌ Failed to get TeamMemberService from container: {e}")
            return "❌ Service temporarily unavailable. Please try again in a moment."

        if role:
            members = asyncio.run(team_member_service.get_team_members_by_role(team_id, role))
        else:
            members = asyncio.run(team_member_service.get_team_members_by_team(team_id))
        
        if not members:
            return f"👥 No team members found for team {team_id}."
        
        result = f"👥 Team Members for {team_id}\n\n"
        for member in members:
            role_text = member.role if member.role else "No role"
            admin_status = "👑 Admin" if member.is_admin else "👤 Member"
            result += f"• {member.full_name or member.first_name or 'Unknown'} - {admin_status} ({role_text})\n"
        
        return result

    except Exception as e:
        logger.error(f"❌ Failed to get team members for {team_id}: {e}")
        return f"❌ Failed to get team members: {e!s}"


@tool("add_team_member_role")
def add_team_member_role(user_id: str, team_id: str, role: str) -> str:
    """
    Add a role to a team member.
    
    Args:
        user_id: The user's Telegram ID
        team_id: The team ID
        role: The role to add
        
    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        team_member_service = container.get_service(TeamMemberService)
        
        success = team_member_service.add_role_to_member(user_id, team_id, role)
        
        if success:
            return f"✅ Successfully added role '{role}' to team member {user_id}"
        else:
            return f"❌ Failed to add role '{role}' to team member {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Failed to add role {role} to member {user_id}: {e}")
        return f"❌ Error adding role: {str(e)}"


@tool("remove_team_member_role")
def remove_team_member_role(user_id: str, team_id: str, role: str) -> str:
    """
    Remove a role from a team member.
    
    Args:
        user_id: The user's Telegram ID
        team_id: The team ID
        role: The role to remove
        
    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        team_member_service = container.get_service(TeamMemberService)
        
        success = team_member_service.remove_role_from_member(user_id, team_id, role)
        
        if success:
            return f"✅ Successfully removed role '{role}' from team member {user_id}"
        else:
            return f"❌ Failed to remove role '{role}' from team member {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Failed to remove role {role} from member {user_id}: {e}")
        return f"❌ Error removing role: {str(e)}"


@tool("promote_team_member_to_admin")
def promote_team_member_to_admin(user_id: str, team_id: str, promoted_by: str) -> str:
    """
    Promote a team member to admin role.
    
    Args:
        user_id: The user's Telegram ID
        team_id: The team ID
        promoted_by: The user ID of who is doing the promotion
        
    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        team_member_service = container.get_service(TeamMemberService)
        
        success = team_member_service.promote_to_admin(user_id, team_id, promoted_by)
        
        if success:
            return f"👑 Successfully promoted team member {user_id} to admin by {promoted_by}"
        else:
            return f"❌ Failed to promote team member {user_id} to admin"
            
    except Exception as e:
        logger.error(f"❌ Failed to promote member {user_id} to admin: {e}")
        return f"❌ Error promoting to admin: {str(e)}" 