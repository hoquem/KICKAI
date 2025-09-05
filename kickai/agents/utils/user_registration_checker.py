#!/usr/bin/env python3
"""
User registration checker utilities.

Handles user registration status checking for the KICKAI system.
"""

import asyncio

from loguru import logger

from kickai.agents.config.message_router_config import (
    DEFAULT_EXPONENTIAL_BACKOFF_FACTOR,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT_SECONDS,
    ERROR_MESSAGES,
    LOG_MESSAGES,
    WARNING_MESSAGES,
)
from kickai.core.enums import ChatType
from kickai.core.types import UserFlowType


class UserRegistrationChecker:
    """
    Handles user registration status checking.

    Determines if users are registered as players or team members.
    """

    @staticmethod
    async def check_user_registration_status(telegram_id: int, team_id: str) -> UserFlowType:
        """
        Check if a user is registered as a player or team member.

        Args:
            telegram_id: Telegram ID of the user
            team_id: Team ID to check against

        Returns:
            UserFlowType indicating if user is registered or not

        Raises:
            RuntimeError: If critical services are unavailable
            ConnectionError: If database connection fails
        """
        try:
            # ALL business logic here
            # Normalize telegram_id to int
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except ValueError:
                    logger.error(ERROR_MESSAGES["INVALID_USER_ID"])
                    return UserFlowType.UNREGISTERED_USER

            # Validate that required services are available
            try:
                from kickai.utils.dependency_utils import validate_required_services

                validate_required_services("PlayerService", "TeamService")
            except RuntimeError as e:
                logger.critical(ERROR_MESSAGES["SERVICE_UNAVAILABLE"].format(error=e))
                raise

            # Get services from dependency container with retries
            max_retries = DEFAULT_RETRY_ATTEMPTS
            for attempt in range(max_retries):
                try:
                    from kickai.utils.dependency_utils import get_player_service, get_team_service

                    player_service = get_player_service()
                    team_service = get_team_service()
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.critical(
                            ERROR_MESSAGES["SERVICE_RETRIEVAL_FAILED"].format(
                                attempt=attempt + 1, error=e
                            )
                        )
                        raise RuntimeError(
                            ERROR_MESSAGES["SERVICE_INITIALIZATION_FAILED"].format(error=e)
                        ) from None
                    logger.warning(
                        WARNING_MESSAGES["SERVICE_RETRIEVAL_FAILED"].format(
                            attempt=attempt + 1, error=e
                        )
                    )
                    await asyncio.sleep(
                        DEFAULT_RETRY_DELAY * (DEFAULT_EXPONENTIAL_BACKOFF_FACTOR**attempt)
                    )  # Exponential backoff

            # Check if user exists as player or team member with timeout
            try:
                # Use asyncio.wait_for to add timeout protection
                player_task = asyncio.create_task(
                    player_service.get_player_by_telegram_id(telegram_id, team_id)
                )
                team_member_task = asyncio.create_task(
                    team_service.get_team_member_by_telegram_id(team_id, telegram_id)
                )

                # Wait for both with timeout
                is_player, is_team_member = await asyncio.wait_for(
                    asyncio.gather(player_task, team_member_task, return_exceptions=True),
                    timeout=DEFAULT_TIMEOUT_SECONDS,
                )

                # Handle exceptions in results
                if isinstance(is_player, Exception):
                    logger.warning(WARNING_MESSAGES["PLAYER_LOOKUP_FAILED"].format(error=is_player))
                    is_player = None
                if isinstance(is_team_member, Exception):
                    logger.warning(
                        WARNING_MESSAGES["TEAM_MEMBER_LOOKUP_FAILED"].format(error=is_team_member)
                    )
                    is_team_member = None

            except TimeoutError:
                logger.error(
                    ERROR_MESSAGES["USER_REGISTRATION_TIMEOUT"].format(telegram_id=telegram_id)
                )
                # In case of timeout, assume unregistered to fail safe
                return UserFlowType.UNREGISTERED_USER
            except Exception as e:
                logger.error(ERROR_MESSAGES["USER_REGISTRATION_ERROR"].format(error=e))
                # In case of error, assume unregistered to fail safe
                return UserFlowType.UNREGISTERED_USER

            return (
                UserFlowType.REGISTERED_USER
                if (is_player or is_team_member)
                else UserFlowType.UNREGISTERED_USER
            )

        except Exception as e:
            logger.error(f"❌ Error in check_user_registration_status: {e}")
            return UserFlowType.UNREGISTERED_USER

    @staticmethod
    async def get_detailed_registration_status(
        telegram_id: int, team_id: str
    ) -> tuple[bool, bool, bool]:
        """
        Get detailed registration status for a user.

        Args:
            telegram_id: Telegram ID of the user
            team_id: Team ID to check against

        Returns:
            Tuple of (is_player, is_team_member, is_registered)
        """
        try:
            # ALL business logic here
            from kickai.utils.dependency_utils import get_player_service, get_team_service

            player_service = get_player_service()
            team_service = get_team_service()
        except Exception as e:
            logger.warning(WARNING_MESSAGES["SERVICE_UNAVAILABLE"].format(error=e))
            return False, False, False

        is_player = False
        is_team_member = False

        # Check actual registration status
        if player_service:
            try:
                player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
                is_player = player is not None
                logger.debug(f"🔍 Player check for {telegram_id}: {is_player}")
            except Exception as e:
                logger.warning(WARNING_MESSAGES["PLAYER_LOOKUP_FAILED"].format(error=e))
                pass

        if team_service:
            try:
                team_member = await team_service.get_team_member_by_telegram_id(
                    team_id, telegram_id
                )
                is_team_member = team_member is not None
                logger.debug(f"🔍 Team member check for {telegram_id}: {is_team_member}")
            except Exception as e:
                logger.warning(WARNING_MESSAGES["TEAM_MEMBER_LOOKUP_FAILED"].format(error=e))
                pass

        # Determine registration status based on actual data
        is_registered = is_player or is_team_member

        # Log the actual registration status
        logger.info(
            LOG_MESSAGES["ACTUAL_REGISTRATION_STATUS"].format(
                is_player=is_player, is_team_member=is_team_member, is_registered=is_registered
            )
        )

        return is_player, is_team_member, is_registered

    @staticmethod
    async def check_command_availability(command: str, chat_type: ChatType, username: str) -> None:
        """
        Check if a command is available for the given chat type.

        Args:
            command: Command to check
            chat_type: Type of chat
            username: Username for context

        Returns:
            None if command is available, raises exception if not found
        """
        try:
            # ALL business logic here
            from kickai.core.command_registry_initializer import get_initialized_command_registry

            registry = get_initialized_command_registry()

            # Handle case where chat_type might be a string instead of enum
            if isinstance(chat_type, str):
                logger.warning(WARNING_MESSAGES["CHAT_TYPE_STRING"].format(chat_type=chat_type))
                try:
                    from kickai.core.constants import normalize_chat_type

                    chat_type = normalize_chat_type(chat_type)
                except Exception as e:
                    logger.error(
                        WARNING_MESSAGES["CHAT_TYPE_NORMALIZATION_FAILED"].format(
                            chat_type=chat_type, error=e
                        )
                    )
                    # Default to main chat type
                    chat_type = ChatType.MAIN

            chat_type_str = chat_type.value
            available_command = registry.get_command_for_chat(command, chat_type_str)

            if not available_command:
                # Command not found - this is NOT a critical error, just an unrecognized command
                logger.info(
                    f"Command {command} not found in registry - treating as unrecognized command"
                )
                # This will be handled by the calling context
                return None

        except Exception as e:
            logger.error(f"❌ Error in check_command_availability: {e}")
            # This will be handled by the calling context
            return None
