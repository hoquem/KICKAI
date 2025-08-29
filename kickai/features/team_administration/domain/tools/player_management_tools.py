#!/usr/bin/env python3
"""
Player Management Tools for Team Administration

This module provides tools for player management by team administrators,
including adding new players with invite link generation.
"""

from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ChatType
from kickai.core.exceptions import (
    ServiceNotAvailableError,
    TeamNotConfiguredError,
    TeamNotFoundError,
)
from kickai.features.team_administration.domain.exceptions import MissingRequiredFieldError
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.constants import (
    ERROR_MESSAGES,
    MAX_PHONE_LENGTH,
    MAX_TEAM_ID_LENGTH,
    PLAYER_DEFAULT_POSITION,
    PLAYER_DEFAULT_STATUS,
    PLAYER_MAX_NAME_LENGTH,
    SUCCESS_MESSAGES,
)
from crewai.tools import tool
from kickai.utils.id_generator import generate_player_id
from kickai.utils.tool_validation import create_tool_response, validate_required_input
from kickai.utils.validation_utils import is_valid_phone, normalize_phone, sanitize_input


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def add_player(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_name: str,
    phone_number: str
) -> str:
    """
    🏃‍♂️ AI EXPERT: Player Registration Tool

    PRIMARY FUNCTION: Add a new player to the team and generate a secure invite link for main chat access.

    CORE WORKFLOW:
    1. Validate leadership permissions and input data
    2. Check for duplicate phone numbers (prevent conflicts)
    3. Generate unique player ID using name-based algorithm
    4. Create player record with "PENDING" status
    5. Generate secure, time-limited invite link
    6. Return formatted success response with instructions

    CRITICAL VALIDATIONS:
    - Leadership chat context required (chat_type must be "leadership")
    - Phone number must be unique within team
    - UK phone format validation (+447123456789 or 07123456789)
    - Name length validation (2-100 characters)
    - Team configuration validation (main_chat_id must exist)

    SECURITY FEATURES:
    - Leadership-only access control
    - Duplicate phone number prevention
    - Secure invite link generation with expiration
    - Input sanitization and validation

    Args:
        telegram_id (int): Admin's Telegram ID (from context)
        team_id (str): Team identifier (from context)
        username (str): Admin's username (from context)
        chat_type (str): Chat type - MUST be "leadership" for this tool
        player_name (str): Player's full name (2-100 characters)
        phone_number (str): Player's phone number (UK format required)

    Returns:
        JSON string with success/error status and formatted message

    🎯 CONTEXT USAGE GUIDANCE:
    - LEADERSHIP CHAT: Primary tool for player registration workflows
    - MAIN CHAT: NOT AVAILABLE - blocked by permission system
    - PRIVATE CHAT: NOT AVAILABLE - blocked by permission system

    📋 USE WHEN:
    - User requests to add a new player to the team
    - Leadership needs to register players with invite links
    - Player registration workflow initiation
    - Team expansion and player onboarding

    ❌ AVOID WHEN:
    - User is not in leadership chat (permission error)
    - Phone number already exists (duplicate error)
    - Team not properly configured (configuration error)
    - Need to update existing player (use different tool)

    🔄 ALTERNATIVES:
    - team_member_registration: For adding team members (coaches, managers)
    - get_player_status: For checking existing player information
    - approve_player: For approving pending players

    💡 AI AGENT EXAMPLES:
    - User Input: "Add player John Smith with phone +447123456789"
    - Action: Call add_player(telegram_id, team_id, username, "leadership", "John Smith", "+447123456789")
    - Expected Output: Success message with invite link and instructions

    - User Input: "Can you register Sarah Johnson, her number is 07123456789"
    - Action: Call add_player(telegram_id, team_id, username, "leadership", "Sarah Johnson", "07123456789")
    - Expected Output: Success message with invite link and instructions

    - User Input: "I need to add Mike with phone +447987654321"
    - Action: Call add_player(telegram_id, team_id, username, "leadership", "Mike", "+447987654321")
    - Expected Output: Success message with invite link and instructions

    🚨 ERROR SCENARIOS:
    - Permission Error: User not in leadership chat → Return permission error message
    - Duplicate Phone: Phone already registered → Return existing player details
    - Invalid Phone: Wrong format → Return format guidance with examples
    - Missing Data: Incomplete information → Return specific missing field guidance
    - System Error: Service unavailable → Return system error with admin contact

    🔧 TECHNICAL NOTES:
    - Player is created with "PENDING" status (requires approval later)
    - Position field is empty (set via /update command by player)
    - Invite link expires in 7 days (configurable)
    - Player ID is generated using name-based algorithm
    - All inputs are sanitized and validated before processing

    📊 PERFORMANCE CHARACTERISTICS:
    - Response Time: < 2 seconds for successful operations
    - Database Operations: 2-3 queries (team lookup, player creation, invite generation)
    - External Calls: 1 Telegram API call for invite link generation
    - Error Recovery: Graceful degradation with clear error messages
    """
    try:
        # Validate required inputs
        validations = [
            validate_required_input(player_name, "player_name"),
            validate_required_input(phone_number, "phone_number"),
            validate_required_input(team_id, "team_id"),
            validate_required_input(telegram_id, "telegram_id"),
            validate_required_input(username, "username"),
            validate_required_input(chat_type, "chat_type"),
        ]

        validation_errors = [error for error in validations if error]
        if validation_errors:
            return create_tool_response(False, f"❌ Missing Information\n\n💡 I need complete details to add a player:\n{'; '.join(validation_errors)}")

        # Validate chat type is leadership
        if chat_type.lower() != ChatType.LEADERSHIP.value:
            return create_tool_response(False, ERROR_MESSAGES["PERMISSION_REQUIRED"])

        # Sanitize inputs using configuration constants
        player_name = sanitize_input(player_name, PLAYER_MAX_NAME_LENGTH)
        phone_number = sanitize_input(phone_number, MAX_PHONE_LENGTH)
        team_id = sanitize_input(team_id, MAX_TEAM_ID_LENGTH)

        # Validate phone number format
        if not is_valid_phone(phone_number):
            return create_tool_response(False, ERROR_MESSAGES["INVALID_PHONE_FORMAT"].format(phone=phone_number))

        # Normalize phone number
        normalized_phone = normalize_phone(phone_number)

        logger.info(f"🏃‍♂️ Adding player: {player_name} ({normalized_phone}) to team {team_id}")

        # Get services from container
        container = get_container()
        if not container:
            raise ServiceNotAvailableError("Dependency container not available")

        team_service = container.get_service(TeamService)
        if not team_service:
            raise ServiceNotAvailableError("Team service not available")

        player_service = container.get_service(PlayerService)
        if not player_service:
            raise ServiceNotAvailableError("Player service not available")

        # Get all existing player IDs for collision detection
        all_players = await player_service.get_all_players(team_id)
        existing_ids = {p.player_id for p in all_players if p.player_id}

        # Generate unique player ID with collision detection
        player_id = generate_player_id(player_name, team_id, existing_ids)
        logger.info(f"Generated unique player_id: {player_id}")

        # Get team using optimized cache (eliminates 200-500ms database query)
        try:
            from kickai.core.team_config_cache import TeamConfigCache
            team_cache = container.get_service(TeamConfigCache)
            team = team_cache.get_team(team_id)
            cache_used = True
        except Exception:
            # Fallback to database if cache not available
            team = await team_service.get_team(team_id=team_id)
            cache_used = False
            
        if not team:
            raise TeamNotFoundError(f"Team not found for team_id: {team_id}")

        if not team.main_chat_id:
            raise TeamNotConfiguredError(team_id, "Main chat not configured for invite links")

        # Determine team name with robust fallback logic
        if team.name and team.name.strip():
            team_name = team.name.strip()
        elif team_id and team_id.strip():
            team_name = team_id.strip()
        else:
            raise MissingRequiredFieldError("Team ID or team information")
        
        logger.debug(f"🏷️ Using team name for player invite: '{team_name}' (from {'team.name' if team.name else 'team_id fallback'}) | Cache: {'✅' if cache_used else '❌'}")

        # Create player using service layer with PlayerCreateParams
        from kickai.features.player_registration.domain.services.player_service import PlayerCreateParams

        player_params = PlayerCreateParams(
            name=player_name,
            phone=normalized_phone,  # PlayerCreateParams uses 'phone' not 'phone_number'
            position=PLAYER_DEFAULT_POSITION,
            team_id=team_id,
            player_id=player_id  # Pass the generated player_id to ensure consistency
        )

        # Save player using service layer
        created_player = await player_service.create_player(player_params)
        logger.info(f"✅ Created player record: {created_player.player_id}")

        # Generate invite link using InviteLinkService with team-specific collections
        database = container.get_database()  # Get database for invite service
        invite_service = InviteLinkService(bot_token=team.bot_token, database=database, team_id=team_id)

        # Create player invite link using the actual player_id from the created player
        invite_data = await invite_service.create_player_invite_link(
            team_id=team_id,
            player_name=player_name,
            player_phone=normalized_phone,
            player_position=PLAYER_DEFAULT_POSITION,  # Use constant
            main_chat_id=team.main_chat_id,
            player_id=created_player.player_id  # Use actual player_id from database
        )

        invite_link = invite_data["invite_link"]
        expires_at = invite_data["expires_at"]

        logger.info(f"✅ Generated invite link for {player_name}: {invite_data['invite_id']}")

        # Format success response using template
        success_response = SUCCESS_MESSAGES["PLAYER_ADDED_WITH_INVITE"].format(
            name=player_name,
            phone=normalized_phone,
            status=PLAYER_DEFAULT_STATUS,
            team_name=team_name,
            invite_link=invite_link,
            expires_at=expires_at
        )

        # Return JSON response with properly formatted message
        return create_tool_response(True, "Operation completed successfully", data=success_response)

    except Exception as e:
        logger.error(f"❌ Error in add_player tool: {e}")
        return create_tool_response(False, ERROR_MESSAGES["ADDPLAYER_SYSTEM_ERROR"].format(error=str(e))
        )

