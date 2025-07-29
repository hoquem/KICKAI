#!/usr/bin/env python3
"""
Phone Linking Tools

This module provides tools for linking Telegram users to existing player records
via phone number matching.
"""

from loguru import logger

from kickai.features.player_registration.domain.services.player_linking_service import (
    PlayerLinkingService,
)
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.phone_validation import validate_phone_number


@tool("link_telegram_user_by_phone")
async def link_telegram_user_by_phone(
    phone: str, telegram_id: str, team_id: str, username: str = None
) -> str:
    """
    Link a Telegram user to an existing player record using phone number.

    Args:
        phone: Phone number to search for (e.g., "+447123456789")
        telegram_id: Telegram user ID to link
        team_id: Team ID for the player
        username: Telegram username (optional)

    Returns:
        Success or error message
    """
    try:
        logger.info(f"🔗 [TOOL] Linking telegram_id={telegram_id} to phone={phone}")

        # Create linking service
        linking_service = PlayerLinkingService(team_id)

        # Validate phone number using enhanced international validation
        try:
            validation_result = validate_phone_number(phone)
            if not validation_result.is_valid:
                error_msg = validation_result.error_message or "Invalid phone number format"
                return f"❌ {error_msg}. Please use international format (e.g., +447123456789)"

            # Normalize phone number
            normalized_phone = validation_result.normalized_number

        except Exception as e:
            logger.error(f"❌ Error in phone validation: {e}")
            return "❌ Phone validation error. Please try again or contact team leadership."

        # Attempt to link
        linked_player = await linking_service.link_telegram_user_by_phone(
            phone=normalized_phone, telegram_id=str(telegram_id), username=username
        )

        if linked_player:
            return f"✅ Successfully linked to your player record: {linked_player.full_name} ({linked_player.player_id})"
        else:
            return (
                "❌ No player record found with that phone number. Please contact team leadership."
            )

    except Exception as e:
        logger.error(f"❌ Error in link_telegram_user_by_phone tool: {e}")
        import traceback

        logger.debug(f"❌ Traceback: {traceback.format_exc()}")
        return f"❌ Error linking account: {e!s}"


@tool("get_pending_players_count")
async def get_pending_players_count(team_id: str) -> str:
    """
    Get the count of pending players without telegram_id.

    Args:
        team_id: Team ID to check

    Returns:
        Count of pending players
    """
    try:
        logger.info(f"📋 [TOOL] Getting pending players count for team={team_id}")

        linking_service = PlayerLinkingService(team_id)
        pending_players = await linking_service.get_pending_players_without_telegram_id()

        count = len(pending_players)
        logger.info(f"📋 Found {count} pending players without telegram_id")

        return str(count)

    except Exception as e:
        logger.error(f"❌ Error in get_pending_players_count tool: {e}")
        import traceback

        logger.debug(f"❌ Traceback: {traceback.format_exc()}")
        return "0"


@tool("validate_phone_number_tool")
async def validate_phone_number_tool(phone: str) -> str:
    """
    Validate phone number format using enhanced international validation.

    Args:
        phone: Phone number to validate

    Returns:
        "valid:normalized_number" or "invalid:error_message"
    """
    try:
        logger.info(f"📱 [TOOL] Validating phone number: {phone}")

        # Use enhanced phone validation
        result = validate_phone_number(phone)

        if result.is_valid:
            return f"valid:{result.normalized_number}:{result.number_type}:{result.country_code}"
        else:
            return f"invalid:{result.error_message}"

    except Exception as e:
        logger.error(f"❌ Error in validate_phone_number tool: {e}")
        import traceback

        logger.debug(f"❌ Traceback: {traceback.format_exc()}")
        return "invalid:Validation error occurred"


@tool("create_linking_prompt")
async def create_linking_prompt(telegram_id: str, team_id: str) -> str:
    """
    Create a message prompting the user to provide their phone number for linking.

    Args:
        telegram_id: Telegram user ID
        team_id: Team ID

    Returns:
        Formatted prompt message
    """
    try:
        logger.info(f"💬 [TOOL] Creating linking prompt for telegram_id={telegram_id}")

        linking_service = PlayerLinkingService(team_id)
        prompt_message = await linking_service.create_linking_prompt_message(telegram_id)

        return prompt_message

    except Exception as e:
        logger.error(f"❌ Error in create_linking_prompt tool: {e}")
        return "❌ Error creating linking prompt. Please contact team leadership."
