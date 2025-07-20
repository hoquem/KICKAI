#!/usr/bin/env python3
"""
Help Tools for KICKAI

This module provides tools for the help assistant agent to process help requests
with proper user validation and context-aware responses.
"""

from typing import Dict, Any, Optional
from loguru import logger
from crewai.tools import tool

from core.enums import ChatType
from features.shared.domain.services.command_processing_service import (
    CommandProcessingService, get_command_processing_service
)


@tool("get_user_status")
def get_user_status_tool(user_id: str, team_id: str, chat_type: str) -> str:
    """
    Get current user's player/team member status.
    
    Args:
        user_id: Telegram user ID
        team_id: Team ID
        chat_type: Type of chat (main_chat|leadership_chat)
        
    Returns:
        JSON string with user status information
    """
    try:
        from features.system_infrastructure.domain.services.permission_service import (
            get_permission_service
        )
        
        # Convert chat_type string to enum
        chat_type_enum = ChatType.MAIN if chat_type == "main_chat" else ChatType.LEADERSHIP
        
        # Get permission service
        permission_service = get_permission_service()
        
        # Get user permissions
        user_permissions = await permission_service.get_user_permissions(user_id, team_id)
        
        # Build status response
        status_info = {
            "user_id": user_id,
            "team_id": team_id,
            "chat_type": chat_type,
            "is_registered": user_permissions.is_player or user_permissions.is_team_member,
            "is_player": user_permissions.is_player,
            "is_team_member": user_permissions.is_team_member,
            "is_admin": user_permissions.is_admin,
            "is_first_user": user_permissions.is_first_user,
            "roles": user_permissions.roles,
            "chat_access": user_permissions.chat_access
        }
        
        logger.info(f"📊 User status retrieved for {user_id}: {status_info}")
        return str(status_info)
        
    except Exception as e:
        logger.error(f"❌ Error getting user status: {e}")
        return f'{{"error": "Failed to get user status: {str(e)}"}}'


@tool("get_available_commands")
def get_available_commands_tool(chat_type: str, user_id: str, team_id: str) -> str:
    """
    Get list of commands available to this user.
    
    Args:
        chat_type: Type of chat (main_chat|leadership_chat)
        user_id: Telegram user ID
        team_id: Team ID
        
    Returns:
        JSON string with available commands information
    """
    try:
        from features.shared.application.commands.help_commands import get_available_commands
        
        # Convert chat_type string to enum
        chat_type_enum = ChatType.MAIN if chat_type == "main_chat" else ChatType.LEADERSHIP
        
        # Get available commands
        commands_info = get_available_commands(
            chat_type=chat_type_enum,
            user_id=user_id,
            team_id=team_id
        )
        
        logger.info(f"📋 Available commands retrieved for {user_id} in {chat_type}: {len(commands_info.get('features', {}))} features")
        return str(commands_info)
        
    except Exception as e:
        logger.error(f"❌ Error getting available commands: {e}")
        return f'{{"error": "Failed to get available commands: {str(e)}"}}'


@tool("format_help_message")
def format_help_message_tool(chat_type: str, user_id: str, team_id: str, user_status: str) -> str:
    """
    Format help message based on context.
    
    Args:
        chat_type: Type of chat (main_chat|leadership_chat)
        user_id: Telegram user ID
        team_id: Team ID
        user_status: User status information from get_user_status
        
    Returns:
        Formatted help message string
    """
    try:
        import json
        
        # Parse user status
        status_info = json.loads(user_status)
        
        # Get command processing service
        processing_service = get_command_processing_service()
        
        # Build user context for formatting
        from features.shared.domain.services.command_processing_service import UserContext
        
        # Convert chat_type string to enum
        chat_type_enum = ChatType.MAIN if chat_type == "main_chat" else ChatType.LEADERSHIP
        
        # Create minimal user context for formatting
        user_context = UserContext(
            user_id=user_id,
            team_id=team_id,
            chat_id="",  # Not needed for formatting
            chat_type=chat_type_enum,
            telegram_username="",  # Not needed for formatting
            telegram_name="",  # Not needed for formatting
            is_registered=status_info.get("is_registered", False),
            is_player=status_info.get("is_player", False),
            is_team_member=status_info.get("is_team_member", False),
            is_first_user=status_info.get("is_first_user", False)
        )
        
        # Get available commands
        commands_info = await processing_service._get_available_commands_for_user(user_context)
        
        # Format help message
        help_message = processing_service._format_help_message(user_context, commands_info)
        
        logger.info(f"📝 Help message formatted for {user_id} in {chat_type}")
        return help_message
        
    except Exception as e:
        logger.error(f"❌ Error formatting help message: {e}")
        return f"❌ Error formatting help message: {str(e)}"


@tool("process_user_registration_flow")
def process_user_registration_flow_tool(chat_type: str, user_id: str, team_id: str, user_status: str) -> str:
    """
    Process user registration flow based on user status and chat type.
    
    Args:
        chat_type: Type of chat (main_chat|leadership_chat)
        user_id: Telegram user ID
        team_id: Team ID
        user_status: User status information from get_user_status
        
    Returns:
        Registration flow message string
    """
    try:
        import json
        
        # Parse user status
        status_info = json.loads(user_status)
        
        # Get command processing service
        processing_service = get_command_processing_service()
        
        # Convert chat_type string to enum
        chat_type_enum = ChatType.MAIN if chat_type == "main_chat" else ChatType.LEADERSHIP
        
        # Create user context
        user_context = UserContext(
            user_id=user_id,
            team_id=team_id,
            chat_id="",  # Not needed for registration flow
            chat_type=chat_type_enum,
            telegram_username="",  # Not needed for registration flow
            telegram_name="",  # Not needed for registration flow
            is_registered=status_info.get("is_registered", False),
            is_player=status_info.get("is_player", False),
            is_team_member=status_info.get("is_team_member", False),
            is_first_user=status_info.get("is_first_user", False)
        )
        
        # Determine registration flow
        if not user_context.is_registered:
            if user_context.chat_type == ChatType.MAIN:
                message = processing_service._format_player_registration_message(user_context)
            elif user_context.chat_type == ChatType.LEADERSHIP:
                if user_context.is_first_user:
                    message = processing_service._format_first_user_welcome_message(user_context)
                else:
                    message = processing_service._format_team_member_registration_message(user_context)
            else:
                message = "❌ Invalid chat type for registration flow."
        else:
            message = "✅ User is already registered."
        
        logger.info(f"📝 Registration flow processed for {user_id} in {chat_type}")
        return message
        
    except Exception as e:
        logger.error(f"❌ Error processing registration flow: {e}")
        return f"❌ Error processing registration flow: {str(e)}"


@tool("get_user_display_info")
def get_user_display_info_tool(user_id: str, team_id: str, user_status: str) -> str:
    """
    Get user display information for message formatting.
    
    Args:
        user_id: Telegram user ID
        team_id: Team ID
        user_status: User status information from get_user_status
        
    Returns:
        JSON string with user display information
    """
    try:
        import json
        
        # Parse user status
        status_info = json.loads(user_status)
        
        # Get user display information
        display_info = {
            "user_id": user_id,
            "team_id": team_id,
            "is_player": status_info.get("is_player", False),
            "is_team_member": status_info.get("is_team_member", False),
            "is_admin": status_info.get("is_admin", False),
            "roles": status_info.get("roles", [])
        }
        
        # Try to get actual name and ID
        try:
            if status_info.get("is_player"):
                from features.player_registration.domain.services.player_service import PlayerService
                from core.dependency_container import get_service
                
                player_service = get_service(PlayerService)
                player_data = await player_service.get_player_by_telegram_id(user_id, team_id)
                
                if player_data:
                    display_info["actual_name"] = player_data.get("name", "Unknown")
                    display_info["player_id"] = player_data.get("id", "Unknown")
                    
            elif status_info.get("is_team_member"):
                from features.team_administration.domain.services.team_service import TeamService
                from core.dependency_container import get_service
                
                team_service = get_service(TeamService)
                member_data = await team_service.get_team_member_by_telegram_id(user_id, team_id)
                
                if member_data:
                    display_info["actual_name"] = member_data.get("name", "Unknown")
                    display_info["member_id"] = member_data.get("id", "Unknown")
                    
        except Exception as e:
            logger.warning(f"⚠️ Could not get detailed user info: {e}")
        
        logger.info(f"👤 User display info retrieved for {user_id}")
        return str(display_info)
        
    except Exception as e:
        logger.error(f"❌ Error getting user display info: {e}")
        return f'{{"error": "Failed to get user display info: {str(e)}"}}' 