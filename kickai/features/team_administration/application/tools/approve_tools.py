#!/usr/bin/env python3
"""
Approve Tools

This module provides tools for approving players and team members.
"""

import logging
from datetime import datetime
from typing import Optional

from crewai.tools import tool
from loguru import logger

from kickai.core.container import get_container
from kickai.core.enums import ResponseStatus
from kickai.database.firebase_client import FirebaseClient
from kickai.features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
from kickai.utils.tool_helpers import create_json_response

# Get services from container
container = get_container()


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
        logger.info(f"🔍 Approve request: {user_id} in team {team_id} by {username}")
        
        # Determine if this is a player or team member based on ID format
        is_team_member = user_id.startswith('M')
        
        if is_team_member:
            return await _approve_team_member(telegram_id, team_id, username, user_id)
        else:
            return await _approve_player(telegram_id, team_id, username, user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in approve_user: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to approve user: {e}")


async def _approve_team_member(telegram_id: int, team_id: str, username: str, member_id: str) -> str:
    """Approve a team member by changing status to ACTIVE."""
    try:
        # Get team member service
        team_member_service = container.get_service(TeamMemberService)
        if not team_member_service:
            return create_json_response(ResponseStatus.ERROR, message="TeamMemberService is not available")
        
        # Get the team member
        team_member = await team_member_service.get_team_member_by_id(member_id, team_id)
        if not team_member:
            return create_json_response(ResponseStatus.ERROR, message=f"Team member {member_id} not found")
        
        # Check if already active
        if team_member.status.value == "active":
            return create_json_response(ResponseStatus.SUCCESS, data={
                'message': f'Team member {team_member.name} is already active',
                'member_id': member_id,
                'name': team_member.name,
                'status': 'active'
            })
        
        # Update status to active
        from kickai.core.enums import MemberStatus
        team_member.status = MemberStatus.ACTIVE
        team_member.updated_at = datetime.utcnow()
        
        # Save the update
        success = await team_member_service.update_team_member(team_member)
        if not success:
            return create_json_response(ResponseStatus.ERROR, message="Failed to update team member status")
        
        logger.info(f"✅ Approved team member: {team_member.name} ({member_id})")
        
        return create_json_response(ResponseStatus.SUCCESS, data={
            'message': f'Team member {team_member.name} approved successfully',
            'member_id': member_id,
            'name': team_member.name,
            'status': 'active',
            'approved_by': username,
            'approved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error approving team member {member_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to approve team member: {e}")


async def _approve_player(telegram_id: int, team_id: str, username: str, player_id: str) -> str:
    """Approve a player by changing status to active."""
    try:
        # Get player registration service
        player_service = container.get_service(PlayerRegistrationService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerRegistrationService is not available")
        
        # Get the player
        player = await player_service.get_player(player_id=player_id, team_id=team_id)
        if not player:
            return create_json_response(ResponseStatus.ERROR, message=f"Player {player_id} not found")
        
        # Check if already active
        if player.status == "active":
            return create_json_response(ResponseStatus.SUCCESS, data={
                'message': f'Player {player.name} is already active',
                'player_id': player_id,
                'name': player.name,
                'status': 'active'
            })
        
        # Approve the player
        approved_player = await player_service.approve_player(player_id=player_id, team_id=team_id)
        
        logger.info(f"✅ Approved player: {approved_player.name} ({player_id})")
        
        return create_json_response(ResponseStatus.SUCCESS, data={
            'message': f'Player {approved_player.name} approved successfully',
            'player_id': player_id,
            'name': approved_player.name,
            'status': 'active',
            'approved_by': username,
            'approved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error approving player {player_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to approve player: {e}")


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
        logger.info(f"🔍 Getting pending users for team {team_id}")
        
        pending_data = {
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
                        'name': p.name,
                        'phone': p.phone_number,
                        'position': p.position,
                        'status': p.status
                    } for p in pending_players
                ]
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
                        'name': m.name,
                        'role': m.role,
                        'phone': m.phone_number,
                        'status': m.status.value
                    } for m in pending_members
                ]
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
                formatted_message += f"   📱 {player['phone']} | ⚽ {player['position'] or 'Not set'}\n\n"
        
        if pending_data['pending_team_members']:
            formatted_message += "👤 PENDING TEAM MEMBERS:\n"
            for i, member in enumerate(pending_data['pending_team_members'], 1):
                formatted_message += f"{i}. {member['name']} ({member['member_id']})\n"
                formatted_message += f"   👑 {member['role']} | 📱 {member['phone'] or 'Not set'}\n\n"
        
        if pending_data['total_pending'] == 0:
            formatted_message += "✅ No pending approvals"
        
        return create_json_response(ResponseStatus.SUCCESS, data={
            'message': 'Pending users retrieved successfully',
            'formatted_message': formatted_message,
            **pending_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting pending users: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get pending users: {e}")
