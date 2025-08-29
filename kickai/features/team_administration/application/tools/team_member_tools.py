#!/usr/bin/env python3
"""
Team Member Tools - Clean Architecture Application Layer

This module provides CrewAI tools for team member management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import List, Dict, Any
from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container


@tool("add_team_member_simplified", result_as_answer=True)
async def add_team_member_simplified(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_name: str,
    phone_number: str
) -> str:
    """
    Add a new team member with simplified workflow.

    This tool serves as the application boundary for team member creation.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context (should be 'leadership')
        member_name: Name of the new team member
        phone_number: Phone number of the new team member

    Returns:
        Plain text response with member creation result and invite link
    """
    try:
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            member_name = params.get('member_name', '')
            phone_number = params.get('phone_number', '')
            
            # Type conversion with error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return "❌ Invalid telegram_id format"
        
        # Basic parameter validation at application boundary
        if not all([telegram_id, team_id, member_name, phone_number]):
            return "❌ Missing required parameters: telegram_id, team_id, member_name, phone_number"
        
        logger.info(f"👥 Adding team member '{member_name}' by {username} ({telegram_id}) in team {team_id}")

        # Delegate to domain function (Clean Architecture)
        from kickai.features.team_administration.domain.tools.simplified_team_member_tools import add_team_member_simplified as add_team_member_simplified_domain
        return await add_team_member_simplified_domain(
            telegram_id, team_id, username, chat_type, member_name, phone_number
        )

    except Exception as e:
        logger.error(f"❌ Error adding team member in application layer: {e}")
        return f"❌ Application error: {str(e)}"


@tool("get_my_team_member_status", result_as_answer=True)
async def get_my_team_member_status(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get the current user's team member status and information.

    This tool serves as the application boundary for team member status functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: User's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Username for context
        chat_type: Chat type context

    Returns:
        JSON formatted team member status information
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(
                        False, 
                        "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(
                False, 
                "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(
                False, 
                "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(
                False, 
                "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(
                False, 
                "Valid chat_type is required"
            )
        
        logger.info(f"👤 Team member status request from {username} ({telegram_id}) in team {team_id}")

        # Get required services from container (application boundary)
        container = get_container()
        team_member_service = container.get_service(TeamMemberService)

        if not team_member_service:
            return create_tool_response(
                False,
                "TeamMemberService is not available"
            )

        # Execute domain operation
        team_member = await team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)

        if team_member:
            status_data = {
                "user_type": "Team Member",
                "telegram_id": telegram_id,
                "team_id": team_id,
                "name": team_member.name,
                "role": getattr(team_member, 'role', 'Member'),
                "status": team_member.status.name if hasattr(team_member, 'status') and team_member.status else 'Active',
                "is_admin": getattr(team_member, 'is_admin', False),
                "member_id": getattr(team_member, 'member_id', 'Not assigned'),
                "is_registered": True,
                "formatted_message": f"👤 TEAM MEMBER INFORMATION\n\n📋 Name: {team_member.name or 'Not set'}\n👑 Role: {getattr(team_member, 'role', 'Member')}\n🏷️ Member ID: {getattr(team_member, 'member_id', 'Not assigned')}\n✅ Status: {team_member.status.name if hasattr(team_member, 'status') and team_member.status else 'Active'}\n🔐 Admin: {'Yes' if getattr(team_member, 'is_admin', False) else 'No'}\n🏢 Team: {team_id}"
            }

            logger.info(f"✅ Team member status retrieved for {username}")
            return create_tool_response(True, f"Team member status for {username}", status_data)
        else:
            status_data = {
                "user_type": "Not a Team Member",
                "telegram_id": telegram_id,
                "team_id": team_id,
                "is_registered": False,
                "formatted_message": f"👤 TEAM MEMBER STATUS: NOT FOUND\n\n📱 TELEGRAM ID: {telegram_id}\n🏆 TEAM ID: {team_id}\nℹ️ INFO: You are not registered as a team member\n\n💡 Contact team leadership to be added as a team member"
            }

            logger.info(f"✅ User {username} is not a team member")
            return create_tool_response(True, f"User {username} is not a team member", status_data)

    except Exception as e:
        logger.error(f"❌ Error getting team member status for {username}: {e}")
        return create_tool_response(False, f"Failed to get team member status: {e}")


@tool("get_team_members", result_as_answer=True)
async def get_team_members(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get all team members for the team.

    This tool serves as the application boundary for team member listing functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context

    Returns:
        JSON formatted list of all team members
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(
                        False, 
                        "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(
                False, 
                "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(
                False, 
                "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(
                False, 
                "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(
                False, 
                "Valid chat_type is required"
            )
        
        logger.info(f"📋 Team members list request from {username} ({telegram_id}) in team {team_id}")

        # Get required services from container (application boundary)
        container = get_container()
        team_member_service = container.get_service(TeamMemberService)

        if not team_member_service:
            return create_tool_response(
                False,
                "TeamMemberService is not available"
            )

        # Execute domain operation
        team_members = await team_member_service.get_team_members(team_id)

        if not team_members:
            return create_tool_response(
                True,
                "No team members found in the team.",
                {"message": "No team members found in the team."}
            )

        # Format team member list at application boundary
        formatted_members = []
        for member in team_members:
            member_data = {
                "name": member.name or "Unknown",
                "role": getattr(member, 'role', 'Member'),
                "status": str(member.status) if hasattr(member, 'status') else 'Active',
                "member_id": getattr(member, 'member_id', 'Not assigned'),
                "is_admin": getattr(member, 'is_admin', False),
                "phone_number": getattr(member, 'phone_number', 'Not provided')
            }
            formatted_members.append(member_data)

        # Create formatted message
        message_lines = ["👥 TEAM MEMBERS", ""]
        for i, member in enumerate(formatted_members, 1):
            admin_indicator = " 👑" if member['is_admin'] else ""
            message_lines.append(f"{i}. {member['name']}{admin_indicator}")
            message_lines.append(f"   🏷️ ID: {member['member_id']} | 👑 Role: {member['role']}")
            message_lines.append(f"   ✅ Status: {member['status']}")
            message_lines.append("")

        formatted_message = "\n".join(message_lines)

        response_data = {
            "team_members": formatted_members,
            "total_count": len(formatted_members),
            "formatted_message": formatted_message
        }

        logger.info(f"✅ Retrieved {len(formatted_members)} team members for team {team_id}")
        return create_tool_response(True, "Operation completed successfully", data=response_data)

    except Exception as e:
        logger.error(f"❌ Error getting team members for team {team_id}: {e}")
        return create_tool_response(False, f"Failed to get team members: {e}")


@tool("activate_team_member", result_as_answer=True)
async def activate_team_member(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    target_telegram_id: int
) -> str:
    """
    Activate a team member (change status from pending to active).

    This tool serves as the application boundary for team member activation.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Admin's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Admin's username for logging
        chat_type: Chat type context
        target_telegram_id: Telegram ID of the team member to activate

    Returns:
        JSON formatted activation result
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            target_telegram_id = params.get('target_telegram_id', 0)
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(
                        False, 
                        "Invalid telegram_id format"
                    )
                    
            if isinstance(target_telegram_id, str):
                try:
                    target_telegram_id = int(target_telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(
                        False, 
                        "Invalid target_telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(
                False, 
                "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(
                False, 
                "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(
                False, 
                "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(
                False, 
                "Valid chat_type is required"
            )
        
        logger.info(f"🔓 Activating team member {target_telegram_id} by {username} ({telegram_id}) in team {team_id}")

        if not target_telegram_id:
            return create_tool_response(
                False,
                "Target telegram ID is required for activation"
            )

        # Get required services from container (application boundary)
        container = get_container()
        team_member_service = container.get_service(TeamMemberService)

        if not team_member_service:
            return create_tool_response(
                False,
                "TeamMemberService is not available"
            )

        # Execute domain operation
        activated_member = await team_member_service.activate_team_member(target_telegram_id, team_id)

        if activated_member:
            response_data = {
                "activated_member": {
                    "name": activated_member.name,
                    "telegram_id": target_telegram_id,
                    "team_id": team_id,
                    "status": "active",
                    "member_id": getattr(activated_member, 'member_id', 'Not assigned')
                },
                "message": f"✅ Team member '{activated_member.name}' activated successfully"
            }

            logger.info(f"✅ Team member {target_telegram_id} activated by {username}")
            return create_tool_response(True, f"Team member {target_telegram_id} activated", response_data)
        else:
            return create_tool_response(
                False,
                f"Team member with Telegram ID {target_telegram_id} not found or already active"
            )

    except Exception as e:
        logger.error(f"❌ Error activating team member {target_telegram_id}: {e}")
        return create_tool_response(False, f"Failed to activate team member: {e}")