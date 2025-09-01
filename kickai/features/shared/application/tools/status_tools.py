#!/usr/bin/env python3
"""
Status Tools - Clean Architecture Application Layer

This module provides CrewAI tools for user status functionality.
These tools serve as the application boundary and delegate to appropriate domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger
from typing import Any, Dict, Union

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
from kickai.utils.player_search_utils import (
    find_player_by_identifier, 
    validate_player_identifier,
    format_search_suggestions,
    get_search_method_display
)


@tool("get_status_my")
async def get_status_my(telegram_id: str, team_id: str = "", username: str = "", chat_type: str = "") -> str:
    """
    Get current user's status information.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat type (main/leadership/private)
        
    Returns:
        User's status information
    """
    try:
        # Type conversion with error handling
        if isinstance(telegram_id, str):
            try:
                telegram_id_int = int(telegram_id)
            except (ValueError, TypeError):
                return f"""❌ System Error

Invalid user ID format. Please try again.

Technical Details:
• Invalid telegram_id: {telegram_id}
• User: {username}
• Team: {team_id}"""
        else:
            telegram_id_int = telegram_id

        # Parameter validation
        if not telegram_id_int or telegram_id_int <= 0:
            return f"""❌ System Error

Invalid user ID provided.

Technical Details:
• User: {username}
• Team: {team_id}"""
        
        if not team_id or not isinstance(team_id, str):
            return f"""❌ System Error

Team information is missing. Please try again.

Technical Details:
• User: {username} ({telegram_id})"""
            
        if not username or not isinstance(username, str):
            return f"""❌ System Error

User information is incomplete. Please try again.

Technical Details:
• Telegram ID: {telegram_id}
• Team: {team_id}"""
            
        if not chat_type or not isinstance(chat_type, str):
            return f"""❌ System Error

Chat context is missing. Please try again from a valid chat.

Technical Details:
• User: {username} ({telegram_id})
• Team: {team_id}"""
        
        logger.info(f"👤 Status request from {username} ({telegram_id_int}) in {chat_type} chat for team {team_id}")

        # Get services from container
        container = get_container()
        
        if not container._initialized:
            logger.warning("⚠️ Container not initialized, attempting to initialize...")
            try:
                await container.initialize()
                logger.info("✅ Container initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize container: {e}")
                return f"""❌ System Error

System is currently initializing. Please try again in a moment.

Technical Details:
• User: {username} ({telegram_id_int})
• Team: {team_id}"""
        
        player_service = container.get_service(PlayerService)
        team_member_service = container.get_service(TeamMemberService)
        
        if not player_service or not team_member_service:
            return f"""❌ System Error

User status services are currently unavailable. Please try again later.

If this problem persists, contact system administrator.

Technical Details:
• User: {username} ({telegram_id_int})
• Team: {team_id}"""

        # Determine user type based on chat context and check both services
        user_info = None
        user_type = "unknown"
        
        # Check if user is a team member (leadership chat context)
        if chat_type == "leadership":
            try:
                user_info = await team_member_service.get_team_member_by_telegram_id(telegram_id_int, team_id)
                if user_info:
                    user_type = "team_member"
                    logger.info(f"✅ Found team member: {user_info.name} ({user_info.role}) - Admin: {user_info.is_admin}")
                else:
                    logger.warning(f"⚠️ Team member not found for telegram_id {telegram_id_int} in team {team_id}")
            except Exception as e:
                logger.error(f"❌ Error getting team member info for {telegram_id_int}: {e}")
                logger.error(f"   Team ID: {team_id}, Chat Type: {chat_type}")
        
        # If not a team member or in main chat, check if user is a player
        if not user_info or chat_type == "main":
            try:
                user_info = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)
                if user_info:
                    user_type = "player"
                    logger.info(f"✅ Found player: {user_info.name} ({user_info.position})")
                else:
                    logger.warning(f"⚠️ Player not found for telegram_id {telegram_id_int} in team {team_id}")
            except Exception as e:
                logger.error(f"❌ Error getting player info for {telegram_id_int}: {e}")
                logger.error(f"   Team ID: {team_id}, Chat Type: {chat_type}")
        
        # Generate status response based on user type
        if user_type == "team_member" and user_info:
            return f"""👤 YOUR TEAM MEMBER STATUS

PERSONAL INFORMATION:
• Name: {user_info.name}
• Role: {user_info.role}
• Username: @{username}
• Team: {team_id}

CONTACT INFORMATION:
• Phone: {user_info.phone_number if user_info.phone_number else 'Not provided'}
• Email: {user_info.email if user_info.email else 'Not provided'}

TEAM INFORMATION:
• Member ID: {user_info.member_id}
• Status: {'✅ Active' if user_info.is_active else '❌ Inactive'}
• Joined: {user_info.created_at.strftime('%B %d, %Y') if user_info.created_at else 'Unknown'}

PERMISSIONS:
• Chat Access: {chat_type.title()} Chat
• Admin Level: {user_info.role.title()}

💡 Need to update your information? Contact team leadership."""

        elif user_type == "player" and user_info:
            return f"""👤 YOUR PLAYER STATUS

PERSONAL INFORMATION:
• Name: {user_info.name}
• Position: {user_info.position if user_info.position else 'Not assigned'}
• Username: @{username}
• Team: {team_id}

CONTACT INFORMATION:
• Phone: {user_info.phone_number if user_info.phone_number else 'Not provided'}

PLAYER INFORMATION:
• Player ID: {user_info.player_id}
• Status: {'✅ Active' if user_info.is_active else '❌ Inactive'}
• Joined: {user_info.created_at.strftime('%B %d, %Y') if user_info.created_at else 'Unknown'}

AVAILABILITY:
• Last Updated: {user_info.updated_at.strftime('%B %d, %Y at %I:%M %p') if user_info.updated_at else 'Never'}

💡 Need to update your information? Use /update [field] [value] or contact team leadership."""

        else:
            # Log detailed debugging information
            logger.error(f"❌ User lookup failed for telegram_id {telegram_id_int}")
            logger.error(f"   Team ID: {team_id}, Chat Type: {chat_type}, Username: {username}")
            logger.error(f"   User Type: {user_type}, User Info: {user_info}")
            
            # Determine appropriate error message based on chat context
            if chat_type == "leadership":
                error_title = "❌ MEMBER NOT FOUND"
                error_message = "We couldn't find your team member information in the system."
                suggestions = [
                    "• Contact the team administrator to be added as a team member",
                    "• Make sure you're using the correct chat",
                    "• Verify your Telegram account is properly linked"
                ]
            else:
                error_title = "❌ USER NOT FOUND"
                error_message = "We couldn't find your information in the system."
                suggestions = [
                    "• If you're a new player, ask team leadership to add you",
                    "• If you're a team member, contact the team administrator",
                    "• Make sure you're using the correct chat"
                ]
            
            return f"""{error_title}

{error_message}

WHAT YOU CAN TRY:
{chr(10).join(suggestions)}

YOUR DETAILS:
• Username: @{username}
• Team: {team_id}
• Chat: {chat_type.title()} Chat

💡 Need help? Contact team leadership or use /help for available commands."""

    except Exception as e:
        logger.error(f"❌ Error in get_status_my for {telegram_id}: {e}")
        return f"""❌ SYSTEM ERROR

Unable to retrieve your status information.

💡 What you can try:
• Wait a moment and try again
• Contact team leadership if the issue persists

TECHNICAL DETAILS:
• Error: {str(e)}
• User: {username} ({telegram_id})
• Team: {team_id}"""


@tool("get_status_user")
async def get_status_user(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    target_user: str = ""
) -> str:
    """
    Get another user's status information (for administrators).

    This tool allows authorized users to check the status of other team members or players.
    Access is typically restricted to leadership chat or admin users.

    Args:
        telegram_id: Requesting user's Telegram ID
        team_id: Team ID
        username: Requesting username
        chat_type: Chat type context (leadership/main/private)
        target_user: Username or name of the user to check

    Returns:
        Formatted user status information or error message
    """
    try:
        # Handle CrewAI parameter dictionary passing
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            target_user = params.get('target_user', '')

            # Type conversion with error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return "❌ Invalid user ID format provided."

        # Parameter validation
        if not telegram_id or telegram_id <= 0:
            return "❌ Invalid requesting user ID."
        
        if not team_id or not isinstance(team_id, str):
            return "❌ Team information is missing."
            
        if not target_user:
            return "❌ Please specify which user to check (e.g., /status @username or /status John Smith)"

        logger.info(f"👤 User status request for '{target_user}' from {username} ({telegram_id}) in {chat_type} chat")

        # Get services from container
        container = get_container()
        
        if not container._initialized:
            logger.warning("⚠️ Container not initialized, attempting to initialize...")
            try:
                await container.initialize()
                logger.info("✅ Container initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize container: {e}")
                return "❌ System is currently initializing. Please try again in a moment."
        
        player_service = container.get_service(PlayerService)
        team_member_service = container.get_service(TeamMemberService)
        
        if not player_service or not team_member_service:
            return "❌ User status services are currently unavailable."

        # Search for user by name or username
        found_player = None
        found_member = None
        
        # Try to find as player first
        try:
            # Search by name (approximate match)
            target_clean = target_user.strip().replace('@', '').lower()
            all_players = await player_service.get_all_players(team_id)
            
            for player in all_players:
                if player.name and target_clean in player.name.lower():
                    found_player = player
                    break
        except Exception as e:
            logger.warning(f"⚠️ Error searching players: {e}")

        # Try to find as team member
        try:
            all_members = await team_member_service.get_team_members(team_id)
            
            for member in all_members:
                if member.name and target_clean in member.name.lower():
                    found_member = member
                    break
        except Exception as e:
            logger.warning(f"⚠️ Error searching team members: {e}")

        # Format response based on what was found
        if found_player and found_member:
            # User has both roles
            return f"""👤 USER PROFILE: {target_user.upper()}

🏷️ TEAM MEMBER STATUS:
• Name: {found_member.name}
• Role: {getattr(found_member, 'role', 'Member')}
• Member ID: {getattr(found_member, 'member_id', 'Not assigned')}
• Status: {str(found_member.status).title() if hasattr(found_member, 'status') and found_member.status else 'Active'}
• Admin Access: {'Yes' if getattr(found_member, 'is_admin', False) else 'No'}

⚽ PLAYER STATUS:
• Player ID: {found_player.player_id or 'Not assigned'}
• Position: {found_player.position or 'Not specified'}
• Status: {found_player.status.title() if hasattr(found_player.status, 'title') else str(found_player.status)}

🏢 Team: {team_id}"""

        elif found_player:
            # Only player found
            status_emoji = "✅" if found_player.status and str(found_player.status).lower() == 'active' else "⏳"
            
            return f"""⚽ PLAYER: {target_user.upper()}

{status_emoji} Name: {found_player.name or 'Not set'}
🏷️ Player ID: {found_player.player_id or 'Not assigned'}
🥅 Position: {found_player.position or 'Not specified'}
📱 Phone: {getattr(found_player, 'phone_number', 'Not provided')}
✅ Status: {found_player.status.title() if hasattr(found_player.status, 'title') else str(found_player.status)}

🏢 Team: {team_id}"""

        elif found_member:
            # Only team member found
            return f"""👤 TEAM MEMBER: {target_user.upper()}

📋 Name: {found_member.name or 'Not set'}
👑 Role: {getattr(found_member, 'role', 'Member')}
🏷️ Member ID: {getattr(found_member, 'member_id', 'Not assigned')}
✅ Status: {str(found_member.status).title() if hasattr(found_member, 'status') and found_member.status else 'Active'}
🔐 Admin: {'Yes' if getattr(found_member, 'is_admin', False) else 'No'}

🏢 Team: {team_id}"""

        else:
            # User not found
            return f"""❌ User Not Found

No player or team member found matching: "{target_user}"

💡 Try:
• Exact name: /status John Smith
• Part of name: /status John
• Check spelling and try again

🔍 Searched in team: {team_id}"""

    except Exception as e:
        logger.error(f"❌ Error getting user status for {target_user}: {e}")
        return f"""❌ System Error

Unable to retrieve status for user: {target_user}

💡 What you can try:
• Check the username/name spelling
• Wait a moment and try again
• Contact system administrator if issue persists

Technical Details:
• Error: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}"""


@tool("get_status_player")
async def get_status_player(
    telegram_id: Union[int, Dict[str, Any]],
    team_id: str,
    username: str,
    chat_type: str,
    player_identifier: str
) -> str:
    """
    Get status information for a specific player by ID, name, or phone number.
    
    Args:
        telegram_id: Requesting user's Telegram ID
        team_id: Team ID (required)
        username: Username for logging  
        chat_type: Chat type context
        player_identifier: Player ID, name, or phone number to search for
        
    Returns:
        Formatted player status information or error message
    """
    try:
        # Handle CrewAI parameter dictionary passing
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            player_identifier = params.get('player_identifier', '')

            # Type conversion with error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return "❌ Invalid user ID format provided."

        # Validate input parameters using shared utility
        is_valid, error_msg = validate_player_identifier(player_identifier)
        if not is_valid:
            return f"❌ {error_msg}"
            
        if not team_id or not team_id.strip():
            return "❌ Team ID is required."
        
        logger.info(f"🔍 Getting player status for '{player_identifier}' in team {team_id}")
        
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Use shared search utility
        search_result = await find_player_by_identifier(
            player_service, 
            player_identifier, 
            team_id
        )
        
        if not search_result:
            return format_search_suggestions(player_identifier, team_id)
        
        player = search_result.player
        search_method = get_search_method_display(search_result.search_method)
        
        # Format player status information
        status_emoji = "✅" if player.status and str(player.status).lower() == 'active' else "⏳"
        
        status_info = f"""⚽ PLAYER STATUS

{status_emoji} Name: {player.name}
🏷️ Player ID: {player.player_id}
🥅 Position: {getattr(player, 'position', 'Not specified')}
📱 Phone: {player.phone_number}
✅ Status: {player.status.title() if hasattr(player.status, 'title') else str(player.status)}
🏢 Team: {team_id}

🔍 Found by: {search_method}"""

        # Try to add recent activity info
        try:
            availability_service = container.get_availability_service()
            recent_availability = await availability_service.get_player_latest_availability(
                player.player_id, team_id
            )
            if recent_availability:
                availability_status = recent_availability.get('status', 'unknown').title()
                last_update = recent_availability.get('date', 'Unknown')
                status_info += f"\n\n📊 Latest Availability: {availability_status}"
                status_info += f"\n📅 Last Update: {last_update}"
        except:
            # Availability info is optional
            pass
            
        return status_info
        
    except Exception as e:
        logger.error(f"❌ Error getting player status for '{player_identifier}': {e}")
        return f"""❌ System Error

Unable to retrieve status for player: {player_identifier}

💡 What you can try:
• Check the player identifier spelling
• Wait a moment and try again  
• Contact system administrator if issue persists

Technical Details:
• Error: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}"""