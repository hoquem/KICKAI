#!/usr/bin/env python3
"""
Approve Tools - Clean Architecture Application Layer

This module provides CrewAI tools for approving players and team members.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from datetime import datetime
from typing import Any

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import MemberStatus


def _validate_user_id(user_id: str) -> bool:
    """
    Validate user ID format and content.

    Args:
        user_id: The user ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) < 2:
        return False

    # Allow alphanumeric characters and common separators
    valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
    return all(c in valid_chars for c in user_id.strip())


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
        container = get_container()
        from kickai.features.team_administration.domain.services.team_member_service import (
            TeamMemberService,
        )

        team_member_service = container.get_service(TeamMemberService)

        if not team_member_service:
            logger.warning("⚠️ TeamMemberService not available for permission check")
            return False

        team_member = await team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)
        if not team_member:
            logger.warning(f"⚠️ User {telegram_id} not found as team member")
            return False

        # Check if user is admin or has leadership role
        admin_roles = {"club administrator", "team manager", "coach", "head coach"}
        is_admin = team_member.is_admin or team_member.role.lower() in admin_roles

        if not is_admin:
            logger.warning(f"⚠️ User {telegram_id} lacks admin permissions")

        return is_admin

    except Exception as e:
        logger.error(f"❌ Error checking admin permissions for {telegram_id}: {e}")
        return False


@tool("approve_member")
async def approve_member(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str, member_id: str
) -> str:
    """
    Grant active membership status to pending team member.

    Confirms member eligibility and activates their administrative privileges,
    enabling full participation in team governance and operations.

    Use when: Member verification is complete
    Required: Administrative approval rights
    Context: Member onboarding workflow

    Returns: Member activation confirmation
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not member_id.strip():
            return "❌ member_id is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🔍 Approve member request: {member_id} in team {team_id} by {telegram_username} ({telegram_id_int})"
        )

        # Input validation
        if not _validate_user_id(member_id):
            return f"❌ Invalid member ID format: {member_id}. Member ID must be at least 2 characters long and contain only alphanumeric characters."

        # Permission check
        has_permission = await _check_admin_permissions(telegram_id_int, team_id)
        if not has_permission:
            return "❌ Access denied: You must have admin permissions to approve team members"

        # Approve team member
        return await _approve_team_member(telegram_id_int, team_id, telegram_username, member_id)

    except Exception as e:
        logger.error(f"❌ Error in approve_member: {e}")
        return f"❌ Failed to approve team member: {e!s}"


@tool("approve_player")
async def approve_player(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str, player_id: str
) -> str:
    """
    Grant player eligibility for squad selection.

    Validates and activates player's participation rights, enabling
    them to be selected for match squads and team activities.

    Use when: Player verification is complete
    Required: Leadership or administrative approval rights
    Context: Player onboarding workflow

    Returns: Player activation confirmation
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not player_id.strip():
            return "❌ player_id is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🔍 Approve player request: {player_id} in team {team_id} by {telegram_username} ({telegram_id_int})"
        )

        # Input validation
        if not _validate_user_id(player_id):
            return f"❌ Invalid player ID format: {player_id}. Player ID must be at least 2 characters long and contain only alphanumeric characters."

        # Permission check
        has_permission = await _check_admin_permissions(telegram_id_int, team_id)
        if not has_permission:
            return "❌ Access denied: You must have admin permissions to approve players"

        # Approve player
        return await _approve_player(telegram_id_int, team_id, telegram_username, player_id)

    except Exception as e:
        logger.error(f"❌ Error in approve_player: {e}")
        return f"❌ Failed to approve player: {e!s}"


async def _approve_team_member(
    telegram_id: int, team_id: str, telegram_username: str, member_id: str
) -> str:
    """
    Approve a team member by changing status to ACTIVE.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        telegram_username: Username of the requesting user
        member_id: The team member ID to approve

    Returns:
        Plain text approval result
    """
    try:
        # Get team member service
        container = get_container()
        from kickai.features.team_administration.domain.services.team_member_service import (
            TeamMemberService,
        )

        team_member_service = container.get_service(TeamMemberService)
        if not team_member_service:
            return "❌ TeamMemberService is not available"

        # Get the team member
        team_member = await team_member_service.get_team_member_by_id(member_id, team_id)
        if not team_member:
            return f"❌ Team member {member_id} not found in team {team_id}"

        # Check if already active
        if team_member.status.value == "active":
            return f"✅ Team member {team_member.name} is already active"

        # Update status to active
        team_member.status = MemberStatus.ACTIVE
        team_member.updated_at = datetime.utcnow()

        # Save the update
        success = await team_member_service.update_team_member(team_member)
        if not success:
            return "❌ Failed to update team member status in database"

        logger.info(
            f"✅ Approved team member: {team_member.name} ({member_id}) by {telegram_username}"
        )

        return f"✅ Team member {team_member.name} approved successfully"

    except Exception as e:
        logger.error(f"❌ Error approving team member {member_id}: {e}")
        return f"❌ Failed to approve team member: {e!s}"


async def _approve_player(
    telegram_id: int, team_id: str, telegram_username: str, player_id: str
) -> str:
    """
    Approve a player by changing status to active.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        telegram_username: Username of the requesting user
        player_id: The player ID to approve

    Returns:
        Plain text approval result
    """
    try:
        # Get player registration service
        container = get_container()
        from kickai.features.player_registration.domain.services.player_registration_service import (
            PlayerRegistrationService,
        )

        player_service = container.get_service(PlayerRegistrationService)
        if not player_service:
            return "❌ PlayerRegistrationService is not available"

        # Get the player
        player = await player_service.get_player(player_id=player_id, team_id=team_id)
        if not player:
            return f"❌ Player {player_id} not found in team {team_id}"

        # Check if already active
        if player.status == "active":
            return f"✅ Player {player.name} is already active"

        # Approve the player
        approved_player = await player_service.approve_player(player_id=player_id, team_id=team_id)

        logger.info(
            f"✅ Approved player: {approved_player.name} ({player_id}) by {telegram_username}"
        )

        return f"✅ Player {approved_player.name} approved successfully"

    except Exception as e:
        logger.error(f"❌ Error approving player {player_id}: {e}")
        return f"❌ Failed to approve player: {e!s}"


@tool("list_pending_approvals")
async def list_pending_approvals(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str
) -> str:
    """
    Retrieve queue of members and players awaiting approval.

    Provides comprehensive list of pending registrations requiring
    administrative review and activation approval.

    Use when: Administrative review queue assessment is needed
    Required: Administrative approval rights
    Context: Approval workflow management

    Returns: Pending approval queue summary
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(f"🔍 Getting pending users for team {team_id} by {telegram_username}")

        # Permission check (only admins can see pending users)
        has_permission = await _check_admin_permissions(telegram_id_int, team_id)
        if not has_permission:
            return "❌ Access denied: You must have admin permissions to view pending users"

        pending_data: dict[str, Any] = {
            "pending_players": [],
            "pending_team_members": [],
            "total_pending": 0,
        }

        # Get pending players
        try:
            container = get_container()
            from kickai.features.player_registration.domain.services.player_registration_service import (
                PlayerRegistrationService,
            )

            player_service = container.get_service(PlayerRegistrationService)
            if player_service:
                pending_players = await player_service.get_pending_players(team_id=team_id)
                pending_data["pending_players"] = [
                    {
                        "player_id": p.player_id,
                        "name": p.name or "Unknown",
                        "phone": p.phone_number or "Not set",
                        "position": p.position or "Not set",
                        "status": p.status,
                    }
                    for p in pending_players
                ]
                logger.info(f"📊 Found {len(pending_data['pending_players'])} pending players")
        except Exception as e:
            logger.warning(f"⚠️ Could not get pending players: {e}")

        # Get pending team members
        try:
            from kickai.features.team_administration.domain.services.team_member_service import (
                TeamMemberService,
            )

            team_member_service = container.get_service(TeamMemberService)
            if team_member_service:
                all_members = await team_member_service.get_team_members(team_id)
                pending_members = [m for m in all_members if m.status.value == "pending"]
                pending_data["pending_team_members"] = [
                    {
                        "member_id": m.member_id,
                        "name": m.name or "Unknown",
                        "role": m.role or "Team Member",
                        "phone": m.phone_number or "Not set",
                        "status": m.status.value,
                    }
                    for m in pending_members
                ]
                logger.info(
                    f"📊 Found {len(pending_data['pending_team_members'])} pending team members"
                )
        except Exception as e:
            logger.warning(f"⚠️ Could not get pending team members: {e}")

        # Calculate total
        pending_data["total_pending"] = len(pending_data["pending_players"]) + len(
            pending_data["pending_team_members"]
        )

        # Create formatted message
        formatted_message = "📋 PENDING APPROVALS\n\n"

        if pending_data["pending_players"]:
            formatted_message += "👥 PENDING PLAYERS:\n"
            for i, player in enumerate(pending_data["pending_players"], 1):
                formatted_message += f"{i}. {player['name']} ({player['player_id']})\n"
                formatted_message += f"   📱 {player['phone']} | ⚽ {player['position']}\n\n"

        if pending_data["pending_team_members"]:
            formatted_message += "👤 PENDING TEAM MEMBERS:\n"
            for i, member in enumerate(pending_data["pending_team_members"], 1):
                formatted_message += f"{i}. {member['name']} ({member['member_id']})\n"
                formatted_message += f"   👑 {member['role']} | 📱 {member['phone']}\n\n"

        if pending_data["total_pending"] == 0:
            formatted_message += "✅ No pending approvals"

        logger.info(f"✅ Retrieved {pending_data['total_pending']} total pending users")

        return formatted_message

    except Exception as e:
        logger.error(f"❌ Error getting pending users: {e}")
        return f"❌ Failed to get pending users: {e!s}"
