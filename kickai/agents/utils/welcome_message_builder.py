#!/usr/bin/env python3
"""
Welcome message builder utilities.

Provides standardized welcome message creation for the KICKAI system.
"""

from typing import Optional
from loguru import logger

from kickai.core.enums import ChatType
from kickai.agents.config.message_router_config import (
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
)


class WelcomeMessageBuilder:
    """
    Standardized welcome message creation.
    
    Builds appropriate welcome messages based on user context and chat type.
    """

    @staticmethod
    def get_unregistered_user_message(chat_type: ChatType, username: str, team_id: str) -> str:
        """
        Get message for unregistered users based on chat type.

        Args:
            chat_type: Type of chat the user is in
            username: User's username
            team_id: Team identifier

        Returns:
            Appropriate welcome message for unregistered users
        """
        try:
            # ALL business logic here
            from kickai.core.constants import BOT_VERSION

            if chat_type == ChatType.LEADERSHIP:
                return SUCCESS_MESSAGES["WELCOME_LEADERSHIP"].format(
                    team_id=team_id, username=username, version=BOT_VERSION
                )
            else:
                return SUCCESS_MESSAGES["WELCOME_MAIN"].format(
                    team_id=team_id, username=username, version=BOT_VERSION
                )
                
        except Exception as e:
            logger.error(f"❌ Error in get_unregistered_user_message: {e}")
            # Fallback to simple welcome message
            return f"👋 Welcome to KICKAI for {team_id}, {username}!"

    @staticmethod
    def create_enhanced_welcome_message(activation_result, chat_type: ChatType) -> str:
        """
        Create enhanced welcome message for successfully activated players.

        Args:
            activation_result: ActivationResult from PlayerAutoActivationService
            chat_type: Type of chat the user joined

        Returns:
            Enhanced welcome message string
        """
        try:
            # ALL business logic here
            player_name = activation_result.player_name or "Player"
            was_activated = activation_result.was_activated

            # Base welcome message with activation status
            if was_activated:
                # Player was just activated from pending -> active
                base_message = SUCCESS_MESSAGES["AUTO_ACTIVATION_WELCOME"].format(
                    player_name=player_name
                )
            else:
                # Player was already active
                base_message = SUCCESS_MESSAGES["WELCOME_BACK"].format(player_name=player_name)

            # Add chat-specific guidance
            if chat_type == ChatType.MAIN:
                chat_guidance = SUCCESS_MESSAGES["MAIN_CHAT_GUIDANCE"]
            elif chat_type == ChatType.LEADERSHIP:
                chat_guidance = SUCCESS_MESSAGES["LEADERSHIP_CHAT_GUIDANCE"]
            else:
                chat_guidance = SUCCESS_MESSAGES["PRIVATE_CHAT_GUIDANCE"]

            # Combine messages
            full_message = base_message + chat_guidance + SUCCESS_MESSAGES["KICKAI_FOOTER"]

            return full_message

        except Exception as e:
            logger.error(f"❌ Error in create_enhanced_welcome_message: {e}")
            # Fallback to simple message
            player_name = getattr(activation_result, "player_name", "Player")
            return SUCCESS_MESSAGES["WELCOME_FALLBACK"].format(player_name=player_name)

    @staticmethod
    def get_regular_member_welcome(username: str, chat_type: ChatType) -> str:
        """
        Get welcome message for members who joined without invite links.

        Args:
            username: User's username
            chat_type: Type of chat they joined

        Returns:
            Appropriate welcome message
        """
        try:
            # ALL business logic here
            if chat_type == ChatType.MAIN:
                return SUCCESS_MESSAGES["REGULAR_MEMBER_WELCOME_MAIN"].format(username=username)
            elif chat_type == ChatType.LEADERSHIP:
                return SUCCESS_MESSAGES["REGULAR_MEMBER_WELCOME_LEADERSHIP"].format(username=username)
            else:
                return SUCCESS_MESSAGES["REGULAR_MEMBER_WELCOME_DEFAULT"].format(username=username)
                
        except Exception as e:
            logger.error(f"❌ Error in get_regular_member_welcome: {e}")
            # Fallback to simple welcome message
            return f"👋 Welcome, {username}!"

    @staticmethod
    def get_team_member_welcome(member_name: str) -> str:
        """
        Get welcome message for team members joining leadership chat.

        Args:
            member_name: Team member's name

        Returns:
            Welcome message for team members
        """
        try:
            # ALL business logic here
            return SUCCESS_MESSAGES["TEAM_MEMBER_WELCOME"].format(member_name=member_name)
            
        except Exception as e:
            logger.error(f"❌ Error in get_team_member_welcome: {e}")
            # Fallback to simple welcome message
            return f"👋 Welcome to the leadership team, {member_name}!"

    @staticmethod
    async def get_unrecognized_command_message(command: str, chat_type: ChatType) -> str:
        """
        Get dynamic help message for unrecognized commands.

        Args:
            command: The unrecognized command
            chat_type: Type of chat for context

        Returns:
            Helpful message with available commands
        """
        try:
            # ALL business logic here
            from kickai.features.shared.domain.tools.help_tools import help_response

            # Use dynamic help tailored to chat context; preserve emojis and formatting
            # Convert telegram_id to int for the help tool (which expects int)
            telegram_id_int = 0  # Default for unregistered users
            return await help_response(
                telegram_id=telegram_id_int,
                team_id="",  # Will be filled by the calling context
                username="user",
                chat_type=chat_type.value,
            )
            
        except Exception as e:
            logger.error(f"❌ Error in get_unrecognized_command_message: {e}")
            # Minimal safe fallback
            return (
                f"🤔 I don't recognize the command `{command}`.\n\n"
                f"💡 Try `/help` to see available commands for this chat."
            )
