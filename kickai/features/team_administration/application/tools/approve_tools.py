#!/usr/bin/env python3
"""
Approve Tools

This module provides tools for approving players and team members.
Implements robust validation, error handling, and permission checks.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from crewai.tools import tool
from loguru import logger

from kickai.core.container import get_container
from kickai.core.enums import ResponseStatus, MemberStatus
from kickai.database.firebase_client import FirebaseClient
from kickai.features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
from kickai.utils.tool_helpers import create_json_response
from kickai.utils.tool_validation import create_tool_response

# Get services from container
container = get_container()


def _validate_user_id(user_id: str) -> bool:
    """
    Validate user ID format and content.
    
    Args:
        user_id: The user ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not user_id or not isinstance(user_id, str):
        return False
    
    user_id = user_id.strip()
    if not user_id:
        return False
    
    # Check for minimum length and valid characters
    if len(user_id) < 2:
        return False
    
    # Allow alphanumeric characters and common separators
    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
    return all(c in valid_chars for c in user_id)


def _is_team_member_id(user_id: str) -> bool:
    """
    Determine if user_id is a team member ID.
    
    Args:
        user_id: The user ID to check
        
    Returns:
        True if team member ID, False if player ID
    """
    if not _validate_user_id(user_id):
        return False
    
    # Team member IDs start with 'M' followed by alphanumeric characters
    return user_id.upper().startswith('M') and len(user_id) >= 3


async def _check_admin_permissions(telegram_id: int, team_id: str) -> bool:
    """
    Check if the requesting user has admin permissions.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        
    Returns:
        True if user has admin permissions, False otherwise
    """
    try:
        team_member_service = container.get_service(TeamMemberService)
        if not team_member_service:
            logger.warning("⚠️ TeamMemberService not available for permission check")
            return False
        
        team_member = await team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)
        if not team_member:
            logger.warning(f"⚠️ User {telegram_id} not found as team member")
            return False
        
        # Check if user is admin or has leadership role
        is_admin = team_member.is_admin or team_member.role.lower() in [
            'club administrator', 'team manager', 'coach', 'head coach'
        ]
        
        if not is_admin:
            logger.warning(f"⚠️ User {telegram_id} lacks admin permissions")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking admin permissions for {telegram_id}: {e}")
        return False


@tool("approve_user", result_as_answer=True)
async def approve_user(telegram_id: int, team_id: str, username: str, chat_type: str, user_id: str) -> str:
    """
    Approve a user (player or team member) by changing their status to active.
    
    This tool can approve both players and team members based on the user_id format:
    - Player IDs: typically start with letters (e.g., "MH123", "01DN")
    - Team Member IDs: start with "M" (e.g., "M01AB", "M01BH")
    
    Args:
        telegram_id: Telegram ID of the requesting user (admin)
        team_id: Team ID (required)
        username: Username of the requesting user (for logging)
        chat_type: Chat type context
        user_id: The user ID to approve (player_id or member_id)
    
    Returns:
        JSON formatted approval result or error message
    """
    try:
        logger.info(f"🔍 Approve request: {user_id} in team {team_id} by {username} ({telegram_id})")
        
        # Input validation
        if not _validate_user_id(user_id):
            return create_tool_response(
                False, 
                f"Invalid user ID format: {user_id}. User ID must be at least 2 characters long and contain only alphanumeric characters."
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(
                False, 
                "Invalid team ID provided"
            )
        
        # Permission check
        has_permission = await _check_admin_permissions(telegram_id, team_id)
        if not has_permission:
            return create_tool_response(
                False, 
                "Access denied: You must have admin permissions to approve users"
            )
        
        # Determine if this is a player or team member based on ID format
        is_team_member = _is_team_member_id(user_id)
        
        if is_team_member:
            return await _approve_team_member(telegram_id, team_id, username, user_id)
        else:
            return await _approve_player(telegram_id, team_id, username, user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in approve_user: {e}")
        return create_tool_response(
            False, 
            f"Failed to approve user: {str(e)}"
        )


async def _approve_team_member(telegram_id: int, team_id: str, username: str, member_id: str) -> str:
    """
    Approve a team member by changing status to ACTIVE.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        username: Username of the requesting user
        member_id: The team member ID to approve
        
    Returns:
        JSON formatted approval result
    """
    try:
        # Get team member service
        team_member_service = container.get_service(TeamMemberService)
        if not team_member_service:
            return create_tool_response(
                False, 
                "TeamMemberService is not available"
            )
        
        # Get the team member
        team_member = await team_member_service.get_team_member_by_id(member_id, team_id)
        if not team_member:
            return create_tool_response(
                False, 
                f"Team member {member_id} not found in team {team_id}"
            )
        
        # Check if already active
        if team_member.status.value == "active":
            return create_tool_response(True, f'Team member {team_member.name} is already active', {
                'message': f'Team member {team_member.name} is already active',
                'member_id': member_id,
                'name': team_member.name,
                'status': 'active',
                'approved_by': username,
                'approved_at': datetime.utcnow().isoformat()
            })
        
        # Update status to active
        team_member.status = MemberStatus.ACTIVE
        team_member.updated_at = datetime.utcnow()
        
        # Save the update
        success = await team_member_service.update_team_member(team_member)
        if not success:
            return create_tool_response(
                False, 
                "Failed to update team member status in database"
            )
        
        logger.info(f"✅ Approved team member: {team_member.name} ({member_id}) by {username}")
        
        return create_tool_response(True, f'Team member {team_member.name} approved successfully', {
            'message': f'Team member {team_member.name} approved successfully',
            'member_id': member_id,
            'name': team_member.name,
            'status': 'active',
            'approved_by': username,
            'approved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error approving team member {member_id}: {e}")
        return create_tool_response(
            False, 
            f"Failed to approve team member: {str(e)}"
        )


async def _approve_player(telegram_id: int, team_id: str, username: str, player_id: str) -> str:
    """
    Approve a player by changing status to active.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        username: Username of the requesting user
        player_id: The player ID to approve
        
    Returns:
        JSON formatted approval result
    """
    try:
        # Get player registration service
        player_service = container.get_service(PlayerRegistrationService)
        if not player_service:
            return create_tool_response(
                False, 
                "PlayerRegistrationService is not available"
            )
        
        # Get the player
        player = await player_service.get_player(player_id=player_id, team_id=team_id)
        if not player:
            return create_tool_response(
                False, 
                f"Player {player_id} not found in team {team_id}"
            )
        
        # Check if already active
        if player.status == "active":
            return create_tool_response(True, f'Player {player.name} is already active', {
                'message': f'Player {player.name} is already active',
                'player_id': player_id,
                'name': player.name,
                'status': 'active',
                'approved_by': username,
                'approved_at': datetime.utcnow().isoformat()
            })
        
        # Approve the player
        approved_player = await player_service.approve_player(player_id=player_id, team_id=team_id)
        
        logger.info(f"✅ Approved player: {approved_player.name} ({player_id}) by {username}")
        
        return create_tool_response(True, f'Player {approved_player.name} approved successfully', {
            'message': f'Player {approved_player.name} approved successfully',
            'player_id': player_id,
            'name': approved_player.name,
            'status': 'active',
            'approved_by': username,
            'approved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error approving player {player_id}: {e}")
        return create_tool_response(
            False, 
            f"Failed to approve player: {str(e)}"
        )


@tool("get_pending_users", result_as_answer=True)
async def get_pending_users(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all pending users (players and team members) that need approval.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required)
        username: Username of the requesting user (for logging)
        chat_type: Chat type context
    
    Returns:
        JSON formatted list of pending users or error message
    """
    try:
        logger.info(f"🔍 Getting pending users for team {team_id} by {username}")
        
        # Input validation
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Invalid team ID provided"
            )
        
        # Permission check (only admins can see pending users)
        has_permission = await _check_admin_permissions(telegram_id, team_id)
        if not has_permission:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Access denied: You must have admin permissions to view pending users"
            )
        
        pending_data: Dict[str, Any] = {
            'pending_players': [],
            'pending_team_members': [],
            'total_pending': 0
        }
        
        # Get pending players
        try:
            player_service = container.get_service(PlayerRegistrationService)
            if player_service:
                pending_players = await player_service.get_pending_players(team_id=team_id)
                pending_data['pending_players'] = [
                    {
                        'player_id': p.player_id,
                        'name': p.name or 'Unknown',
                        'phone': p.phone_number or 'Not set',
                        'position': p.position or 'Not set',
                        'status': p.status
                    } for p in pending_players
                ]
                logger.info(f"📊 Found {len(pending_data['pending_players'])} pending players")
        except Exception as e:
            logger.warning(f"⚠️ Could not get pending players: {e}")
        
        # Get pending team members
        try:
            team_member_service = container.get_service(TeamMemberService)
            if team_member_service:
                all_members = await team_member_service.get_team_members(team_id)
                pending_members = [
                    m for m in all_members 
                    if m.status.value == "pending"
                ]
                pending_data['pending_team_members'] = [
                    {
                        'member_id': m.member_id,
                        'name': m.name or 'Unknown',
                        'role': m.role or 'Team Member',
                        'phone': m.phone_number or 'Not set',
                        'status': m.status.value
                    } for m in pending_members
                ]
                logger.info(f"📊 Found {len(pending_data['pending_team_members'])} pending team members")
        except Exception as e:
            logger.warning(f"⚠️ Could not get pending team members: {e}")
        
        # Calculate total
        pending_data['total_pending'] = len(pending_data['pending_players']) + len(pending_data['pending_team_members'])
        
        # Create formatted message
        formatted_message = "📋 PENDING APPROVALS\n\n"
        
        if pending_data['pending_players']:
            formatted_message += "👥 PENDING PLAYERS:\n"
            for i, player in enumerate(pending_data['pending_players'], 1):
                formatted_message += f"{i}. {player['name']} ({player['player_id']})\n"
                formatted_message += f"   📱 {player['phone']} | ⚽ {player['position']}\n\n"
        
        if pending_data['pending_team_members']:
            formatted_message += "👤 PENDING TEAM MEMBERS:\n"
            for i, member in enumerate(pending_data['pending_team_members'], 1):
                formatted_message += f"{i}. {member['name']} ({member['member_id']})\n"
                formatted_message += f"   👑 {member['role']} | 📱 {member['phone']}\n\n"
        
        if pending_data['total_pending'] == 0:
            formatted_message += "✅ No pending approvals"
        
        logger.info(f"✅ Retrieved {pending_data['total_pending']} total pending users")
        
        return create_json_response(ResponseStatus.SUCCESS, data={
            'message': 'Pending users retrieved successfully',
            'formatted_message': formatted_message,
            **pending_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting pending users: {e}")
        return create_json_response(
            ResponseStatus.ERROR, 
            message=f"Failed to get pending users: {str(e)}"
        )
