#!/usr/bin/env python3
"""
Player Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for player management by team administrators.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container


@tool("create_player")
async def create_player(
    telegram_id: str,
    team_id: str,
    telegram_username: str,
    chat_type: str,
    player_name: str,
    phone_number: str,
) -> str:
    """
    Register new player in team roster.

    Establishes player profile with contact information and position assignment,
    initiating the verification and approval workflow for team participation.

    Use when: New team member joins as player
    Required: Leadership or administrative privileges
    Context: Player onboarding process

    Returns: Player registration confirmation
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not player_name.strip():
            return "❌ player_name is required"
        if not phone_number.strip():
            return "❌ phone_number is required"

        # Convert telegram_id to int for logging
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🏃‍♂️ Creating player '{player_name}' by {telegram_username} ({telegram_id_int}) in team {team_id}"
        )

        # Get services from container
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import (
            IPlayerService,
        )

        player_service = container.get_service(IPlayerService)

        if not player_service:
            return "❌ Player service is not available"

        # Create player using domain service
        from kickai.features.player_registration.domain.entities.player_create_params import (
            PlayerCreateParams,
        )

        params = PlayerCreateParams(
            name=player_name,
            phone=phone_number,
            team_id=team_id,
            position="TBD",  # Default position
        )

        player = await player_service.create_player(params)

        if player:
            logger.info(
                f"✅ Player '{player_name}' created successfully with ID: {player.player_id}"
            )
            return f"✅ Player '{player_name}' created successfully with ID: {player.player_id}"
        else:
            return f"❌ Failed to create player '{player_name}'"

    except Exception as e:
        logger.error(f"❌ Error creating player '{player_name}': {e}")
        return f"❌ Failed to create player: {e!s}"
