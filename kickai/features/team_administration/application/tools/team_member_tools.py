#!/usr/bin/env python3
"""
Team Member Tools - Clean Architecture Application Layer

This module provides CrewAI tools for team member management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.team_administration.domain.services.team_member_service import (
    TeamMemberService,
)


@tool("create_member")
async def create_member(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    member_name: str,
    phone_number: str,
) -> str:
    """
    Register new team member with administrative role.

    Establishes member profile with administrative access and communication
    preferences, enabling participation in team governance and coordination.

    Use when: New administrative member joins team
    Required: Team administration privileges
    Context: Team membership expansion workflow

    Returns: Member registration confirmation with access details
    """
    try:
        # Basic parameter validation (CrewAI handles parameter passing)
        if not telegram_id or not team_id or not member_name or not phone_number:
            return "❌ Required parameters missing for member creation"

        # Convert telegram_id to integer for database operations
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"👥 Adding team member '{member_name}' by {username} ({telegram_id_int}) in team {team_id}"
        )

        # Delegate to domain function (Clean Architecture)
        from kickai.features.team_administration.domain.tools.simplified_team_member_tools import (
            add_team_member_simplified as add_team_member_simplified_domain,
        )

        return await add_team_member_simplified_domain(
            telegram_id_int, team_id, username, chat_type, member_name, phone_number
        )

    except Exception as e:
        logger.error(f"❌ Error adding team member in application layer: {e}")
        return f"❌ Application error: {e!s}"


@tool("list_members_all")
async def list_members_all(
    team_id: str, telegram_id: str = "", username: str = "system", chat_type: str = "main"
) -> str:
    """
    Retrieve complete team administrative roster.

    Provides comprehensive overview of all team members with their roles,
    status, and administrative permissions for team governance review.

    Use when: Administrative roster review is needed
    Required: Team administrative access
    Context: Team governance workflow

    Returns: Team administrative roster summary
    """
    try:
        # Basic parameter validation (CrewAI handles parameter passing)
        if not team_id:
            return "❌ Team ID is required"

        logger.info(f"📋 Team members list request for team {team_id}")

        # Get required services from container with error handling
        container = get_container()
        try:
            team_member_service = container.get_service(TeamMemberService)
            if not team_member_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team member service: {e}")
            return "❌ Team member service is not available"

        # Execute domain operation
        team_members = await team_member_service.get_team_members(team_id)

        if not team_members:
            return "📋 No team members found in the team."

        # Format team member list with safe attribute access
        formatted_members = []
        for member in team_members:
            try:
                member_data = {
                    "name": getattr(member, "name", None) or "Unknown",
                    "role": getattr(member, "role", "Member"),
                    "status": str(getattr(member, "status", "Active")),
                    "member_id": getattr(member, "member_id", "Not assigned"),
                    "is_admin": getattr(member, "is_admin", False),
                    "phone_number": getattr(member, "phone_number", "Not provided"),
                }
                formatted_members.append(member_data)
            except Exception as e:
                logger.warning(f"⚠️ Error formatting member data: {e}")
                continue

        # Create formatted message with improved structure
        if not formatted_members:
            return "📋 No team members found in the team."

        message_lines = ["👥 TEAM MEMBERS", ""]
        for i, member in enumerate(formatted_members, 1):
            admin_indicator = " 👑" if member["is_admin"] else ""
            message_lines.extend(
                [
                    f"{i}. {member['name']}{admin_indicator}",
                    f"   🏷️ ID: {member['member_id']} | 👑 Role: {member['role']}",
                    f"   ✅ Status: {member['status']}",
                    "",
                ]
            )

        logger.info(f"✅ Retrieved {len(formatted_members)} team members for team {team_id}")
        return "\n".join(message_lines)

    except Exception as e:
        logger.error(f"❌ Error getting team members for team {team_id}: {e}")
        return f"❌ Failed to get team members: {e}"


@tool("activate_member")
async def activate_member(
    telegram_id: str, team_id: str, username: str, chat_type: str, target_telegram_id: str
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
        # Basic parameter validation (CrewAI handles parameter passing)
        if not telegram_id or not team_id or not target_telegram_id:
            return "❌ Required parameters missing for member activation"

        # Convert telegram_ids to integers for database operations
        try:
            telegram_id_int = int(telegram_id)
            target_telegram_id_int = int(target_telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🔓 Activating team member {target_telegram_id_int} by {username} ({telegram_id_int}) in team {team_id}"
        )

        # Get required services from container with error handling
        container = get_container()
        try:
            team_member_service = container.get_service(TeamMemberService)
            if not team_member_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team member service: {e}")
            return "❌ Team member service is not available"

        # Execute domain operation with enhanced error handling
        try:
            activated_member = await team_member_service.activate_team_member(
                target_telegram_id_int, team_id
            )

            if activated_member:
                member_name = (
                    getattr(activated_member, "name", None) or f"ID {target_telegram_id_int}"
                )
                logger.info(f"✅ Team member {target_telegram_id_int} activated by {username}")
                return f"✅ Team member '{member_name}' activated successfully"
            else:
                return f"❌ Team member with Telegram ID {target_telegram_id_int} not found or already active"
        except Exception as e:
            logger.error(f"❌ Error during team member activation: {e}")
            return f"❌ Failed to activate team member: {e!s}"

    except Exception as e:
        logger.error(f"❌ Error in activate_member tool: {e}")
        return f"❌ Failed to activate team member: {e!s}"
