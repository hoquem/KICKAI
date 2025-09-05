"""Player Information Tools - Clean Architecture Compliant (CrewAI Semantic Update)

This module contains CrewAI tools for player information retrieval with semantic naming.
These tools follow the CrewAI semantic convention: _self for requesting user, _by_identifier for lookups.
"""

from typing import Any, ClassVar, Protocol

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.utils.native_crewai_helpers import validate_required_strings
from kickai.utils.player_search_utils import (
    find_player_by_identifier,
    format_search_suggestions,
    get_search_method_display,
    validate_player_identifier,
)


# Service Protocols for better type safety
class PlayerServiceProtocol(Protocol):
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Any | None:
        ...

    async def get_active_players(self, team_id: str) -> list[Any]:
        ...


class MatchServiceProtocol(Protocol):
    async def get_upcoming_matches(self, team_id: str, limit: int = 10) -> list[Any]:
        ...

    async def get_matches_for_player(self, player_id: str, team_id: str) -> list[Any]:
        ...


class AvailabilityServiceProtocol(Protocol):
    async def get_player_latest_availability(
        self, player_id: str, team_id: str
    ) -> dict[str, Any] | None:
        ...


class ServiceManager:
    """Centralized service management with caching and error handling."""

    _service_cache: ClassVar[dict[str, Any]] = {}

    @classmethod
    async def get_player_service(cls) -> PlayerServiceProtocol | None:
        """Get player service with caching and error handling."""
        cache_key = "player_service"

        if cache_key in cls._service_cache:
            return cls._service_cache[cache_key]

        try:
            container = get_container()
            from kickai.features.player_registration.domain.interfaces.player_service_interface import (
                IPlayerService,
            )

            service = container.get_service(IPlayerService)

            if service:
                cls._service_cache[cache_key] = service
                logger.debug("Player service cached successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to get player service: {e}")
            return None

    @classmethod
    async def get_match_service(cls) -> MatchServiceProtocol | None:
        """Get match service with caching and error handling."""
        cache_key = "match_service"

        if cache_key in cls._service_cache:
            return cls._service_cache[cache_key]

        try:
            container = get_container()
            from kickai.features.match_management.domain.interfaces.match_service_interface import (
                IMatchService,
            )

            service = container.get_service(IMatchService)

            if service:
                cls._service_cache[cache_key] = service
                logger.debug("Match service cached successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to get match service: {e}")
            return None

    @classmethod
    async def get_availability_service(cls) -> AvailabilityServiceProtocol | None:
        """Get availability service with caching and error handling."""
        cache_key = "availability_service"

        if cache_key in cls._service_cache:
            return cls._service_cache[cache_key]

        try:
            container = get_container()
            from kickai.features.match_management.domain.interfaces.availability_service_interface import (
                IAvailabilityService,
            )

            service = container.get_service(IAvailabilityService)

            if service:
                cls._service_cache[cache_key] = service
                logger.debug("Availability service cached successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to get availability service: {e}")
            return None

    @classmethod
    def clear_cache(cls) -> None:
        """Clear service cache - useful for testing."""
        cls._service_cache.clear()
        logger.debug("Service cache cleared")


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_and_convert_telegram_id(telegram_id: str) -> int:
    """Validate and convert telegram_id with proper error handling.

    Args:
        telegram_id: String representation of telegram ID

    Returns:
        Integer telegram ID

    Raises:
        ValidationError: If telegram_id is invalid
    """
    if not telegram_id or not telegram_id.strip():
        raise ValidationError("telegram_id is required")

    try:
        telegram_id_int = int(telegram_id.strip())
        if telegram_id_int <= 0:
            raise ValidationError("telegram_id must be positive")
        return telegram_id_int
    except ValueError as e:
        raise ValidationError("telegram_id must be a valid number") from e


def format_player_info(player: Any) -> str:
    """Format player information consistently.

    Args:
        player: Player entity

    Returns:
        Formatted player information string
    """
    if not player:
        return "❌ No player information available"

    # Get status value consistently
    status_value = player.status.value if hasattr(player.status, "value") else str(player.status)

    info_text = f"📋 {player.name} - Player Information\n\n"
    info_text += f"🆔 ID: {player.player_id}\n"
    info_text += f"📞 Phone: {player.phone_number or 'Not provided'}\n"

    # Only add email if available
    if hasattr(player, "email") and player.email:
        info_text += f"📧 Email: {player.email}\n"

    info_text += f"⚽ Position: {player.position or 'Not set'}\n"
    info_text += f"📊 Status: {status_value}\n"

    is_active = status_value.lower() == "active"
    info_text += f"✅ Active: {'Yes' if is_active else 'No'}\n"

    return info_text


async def get_player_availability_info(player_id: str, team_id: str) -> str:
    """Get player availability information with error handling.

    Args:
        player_id: Player identifier
        team_id: Team identifier

    Returns:
        Formatted availability information
    """
    try:
        availability_service = await ServiceManager.get_availability_service()
        if not availability_service:
            return "📅 Last Availability: N/A (service unavailable)\n"

        recent_availability = await availability_service.get_player_latest_availability(
            player_id, team_id
        )

        if recent_availability:
            date_str = recent_availability.get("date", "N/A")
            status_str = recent_availability.get("status", "unknown")
            return f"📅 Last Availability: {date_str}\n✅ Availability Status: {status_str}\n"
        else:
            return "📅 Last Availability: N/A\n"

    except Exception as e:
        logger.warning(f"Failed to get availability info for player {player_id}: {e}")
        return "📅 Last Availability: N/A (error)\n"


async def get_upcoming_matches_count(team_id: str) -> str:
    """Get upcoming matches count with error handling.

    Args:
        team_id: Team identifier

    Returns:
        Formatted upcoming matches information
    """
    try:
        match_service = await ServiceManager.get_match_service()
        if not match_service:
            return "⚽ Upcoming Matches: 0 (service unavailable)"

        upcoming_matches = await match_service.get_upcoming_matches(team_id, limit=3)
        match_count = len(upcoming_matches) if upcoming_matches else 0
        return f"⚽ Upcoming Matches: {match_count}"

    except Exception as e:
        logger.warning(f"Failed to get upcoming matches for team {team_id}: {e}")
        return "⚽ Upcoming Matches: 0 (error)"


def format_match_info(match: Any, player_name: str | None = None) -> str:
    """Format match information consistently.

    Args:
        match: Match entity
        player_name: Optional player name for title

    Returns:
        Formatted match information string
    """
    if not match:
        return "❌ No match information available"

    title = (
        f"⚽ Current Match for {player_name}\n\n" if player_name else "⚽ Your Current Match\n\n"
    )

    match_text = title
    match_text += f"🆚 Opponent: {getattr(match, 'opponent', 'TBD')}\n"

    # Format date safely
    if hasattr(match, "match_date") and match.match_date:
        if hasattr(match.match_date, "isoformat"):
            date_str = match.match_date.isoformat()
        else:
            date_str = str(match.match_date)
        match_text += f"📅 Date: {date_str}\n"
    else:
        match_text += "📅 Date: TBD\n"

    match_text += f"📍 Location: {getattr(match, 'location', 'TBD')}\n"
    match_text += f"📊 Status: {getattr(match, 'status', 'unknown')}\n"

    # Add availability if present
    if hasattr(match, "player_availability") and match.player_availability:
        availability_label = "Your Availability" if not player_name else "Player Availability"
        match_text += f"✅ {availability_label}: {match.player_availability}"

    return match_text


@tool("get_player_self")
async def get_player_self(
    team_id: str, telegram_id: str, telegram_username: str = "system", chat_type: str = "main"
) -> str:
    """Retrieve requesting user's own player profile and status.

    Provides personal player information including registration status,
    position assignment, and contact details for self-service queries.

    Use when: User needs to check their own player information
    Required: Valid player registration in team

    Returns: Personal player profile with current status
    """
    try:
        # Validate only parameters actually used by this tool
        validation_error = validate_required_strings(
            telegram_id, team_id, names=["telegram_id", "team_id"]
        )
        if validation_error:
            return validation_error

        # Convert telegram_id safely
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        container = get_container()

        # Get player service with availability check
        try:
            from kickai.features.player_registration.domain.interfaces.player_service_interface import (
                IPlayerService,
            )

            player_service = container.get_service(IPlayerService)
            if not player_service:
                return "❌ Player service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get player service: {e}")
            return "❌ Player service is not available"

        # Get info for requesting user with graceful error handling
        try:
            player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)
            if not player:
                return "❌ You are not registered as a player in this team"
        except Exception as e:
            logger.error(f"❌ Error getting player by telegram_id {telegram_id_int}: {e}")
            return f"❌ Failed to retrieve your player information: {e!s}"

        logger.info(f"🔍 Getting self info for player {player.name} ({player.player_id})")

        # Format current info as clean text (no markdown)
        info_text = f"📋 Your Player Information ({player.name})\n\n"
        info_text += f"🆔 ID: {player.player_id}\n"
        info_text += f"📞 Phone: {player.phone_number or 'Not provided'}\n"
        info_text += f"📧 Email: {player.email or 'Not provided'}\n"
        info_text += f"⚽ Position: {player.position or 'Not set'}\n"
        status_value = (
            player.status.value if hasattr(player.status, "value") else str(player.status)
        )
        info_text += f"📊 Status: {status_value}\n"
        is_active = status_value.lower() == "active"
        info_text += f"✅ Active: {'Yes' if is_active else 'No'}\n"

        # Try to get recent availability (optional) with graceful error handling
        try:
            from kickai.features.match_management.domain.interfaces.availability_service_interface import (
                IAvailabilityService,
            )

            availability_service = container.get_service(IAvailabilityService)
            if availability_service:
                recent_availability = await availability_service.get_player_latest_availability(
                    player.player_id, team_id
                )
                if recent_availability:
                    info_text += f"📅 Last Availability: {recent_availability.get('date', 'N/A')}\n"
                    info_text += (
                        f"✅ Availability Status: {recent_availability.get('status', 'unknown')}\n"
                    )
                else:
                    info_text += "📅 Last Availability: N/A\n"
            else:
                info_text += "📅 Last Availability: N/A\n"
        except Exception as e:
            logger.warning(f"⚠️ Availability service check failed: {e}")
            info_text += "📅 Last Availability: N/A\n"

        # Try to get upcoming matches (optional) with graceful error handling
        try:
            from kickai.features.match_management.domain.interfaces.match_service_interface import (
                IMatchService,
            )

            match_service = container.get_service(IMatchService)
            if match_service:
                upcoming_matches = await match_service.get_upcoming_matches(team_id, limit=3)
                match_count = len(upcoming_matches) if upcoming_matches else 0
                info_text += f"⚽ Upcoming Matches: {match_count}"
            else:
                info_text += "⚽ Upcoming Matches: 0"
        except Exception as e:
            logger.warning(f"⚠️ Match service check failed: {e}")
            info_text += "⚽ Upcoming Matches: 0"

        return info_text

    except Exception as e:
        logger.error(f"❌ Error getting self player info: {e}")
        return f"❌ Failed to retrieve your player information: {e!s}"


@tool("get_player_by_identifier")
async def get_player_by_identifier(
    team_id: str,
    player_identifier: str,
    telegram_id: str,
    telegram_username: str = "system",
    chat_type: str = "main",
) -> str:
    """Search for and retrieve player information by identifier.

    Searches team roster for player using name, ID, or phone number,
    providing comprehensive player details and current status.

    Use when: Looking up specific player information for another team member
    Required: Valid player identifier and team access

    Returns: Player profile information or search suggestions
    """
    try:
        # Validate only parameters actually used by this tool
        validation_error = validate_required_strings(
            team_id, player_identifier, names=["team_id", "player_identifier"]
        )
        if validation_error:
            return validation_error

        # Validate input parameters
        is_valid, error_msg = validate_player_identifier(player_identifier)
        if not is_valid:
            return f"❌ {error_msg}"

        logger.info(
            f"🔍 Getting player info for '{player_identifier}' in team {team_id} (user: {telegram_id or 'unknown'})"
        )

        # Get player service with availability check
        container = get_container()
        try:
            from kickai.features.player_registration.domain.interfaces.player_service_interface import (
                IPlayerService,
            )

            player_service = container.get_service(IPlayerService)
            if not player_service:
                return "❌ Player service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get player service: {e}")
            return "❌ Player service is not available"

        # Use shared search utility
        search_result = await find_player_by_identifier(player_service, player_identifier, team_id)

        if not search_result:
            return f"❌ {format_search_suggestions(player_identifier, team_id)}"

        player = search_result.player

        # Build comprehensive player information
        player_data: dict[str, Any] = {
            "player_id": player.player_id,
            "name": player.name,
            "phone": player.phone_number,
            "position": player.position or "Not set",
            "status": player.status.value
            if hasattr(player.status, "value")
            else str(player.status),
            "team_id": player.team_id,
            "search_method": get_search_method_display(search_result.search_method),
            "created_at": str(getattr(player, "created_at", "N/A")),
            "last_updated": str(getattr(player, "updated_at", "N/A")),
        }

        # Format player info as clean text (no markdown)
        info_text = f"📋 {player.name} - Player Information\n\n"
        info_text += f"🆔 ID: {player_data['player_id']}\n"
        info_text += f"📞 Phone: {player_data['phone']}\n"
        info_text += f"⚽ Position: {player_data['position']}\n"
        info_text += f"📊 Status: {player_data['status']}\n"
        info_text += f"🔍 Found by: {player_data['search_method']}\n"
        info_text += f"📅 Created: {player_data['created_at']}\n"
        info_text += f"🔄 Updated: {player_data['last_updated']}"
        return info_text

    except Exception as e:
        logger.error(f"❌ Error getting player info for '{player_identifier}': {e}")
        return f"❌ Failed to retrieve player information: {e!s}"


@tool("get_player_match_self")
async def get_player_match_self(
    team_id: str, telegram_id: str, telegram_username: str = "system", chat_type: str = "main"
) -> str:
    """Retrieve requesting user's upcoming match schedule and availability.

    Provides personal match calendar with upcoming fixtures and
    availability status for self-service match queries.

    Use when: User needs to check their own match schedule
    Required: Valid player registration and match participation

    Returns: Personal match schedule with availability status
    """
    try:
        # Validate only parameters actually used by this tool
        validation_error = validate_required_strings(
            telegram_id, team_id, names=["telegram_id", "team_id"]
        )
        if validation_error:
            return validation_error

        container = get_container()

        # Get match service with availability check
        try:
            from kickai.features.match_management.domain.interfaces.match_service_interface import (
                IMatchService,
            )

            match_service = container.get_service(IMatchService)
            if not match_service:
                return "❌ Match service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get match service: {e}")
            return "❌ Match service is not available"

        # Use telegram_id for current player
        current_player_id = str(telegram_id)

        # Get player's current/upcoming matches with graceful error handling
        try:
            matches = await match_service.get_matches_for_player(current_player_id, team_id)
        except Exception as e:
            logger.warning(f"⚠️ Match service operation failed for {current_player_id}: {e}")
            return f"⚠️ Unable to retrieve match information: {e!s}"

        if not matches:
            return "📅 No current or upcoming matches found for you"

        # Find current or next match
        current_match = None
        for match in matches:
            if match.status in ["upcoming", "in_progress"]:
                current_match = match
                break

        if current_match:
            match_text = "⚽ Your Current Match\n\n"
            match_text += f"🆚 Opponent: {current_match.opponent}\n"
            match_text += f"📅 Date: {current_match.match_date.isoformat()}\n"
            match_text += f"📍 Location: {current_match.location}\n"
            match_text += f"📊 Status: {current_match.status}\n"
            if hasattr(current_match, "player_availability"):
                match_text += f"✅ Your Availability: {current_match.player_availability}"
            return match_text
        else:
            return "📅 No current or upcoming matches scheduled for you"

    except Exception as e:
        logger.error(f"❌ Error getting self match information: {e}")
        return f"❌ Failed to get your match information: {e!s}"


@tool("get_player_match_by_identifier")
async def get_player_match_by_identifier(
    team_id: str,
    player_identifier: str,
    telegram_id: str,
    telegram_username: str = "system",
    chat_type: str = "main",
) -> str:
    """Retrieve match schedule for specified player by identifier.

    Searches team roster for player and provides their upcoming match
    schedule and availability status for coaching and planning purposes.

    Use when: Checking another player's match participation schedule
    Required: Valid player identifier and team access

    Returns: Player's match schedule with availability details
    """
    try:
        # Validate only parameters actually used by this tool
        validation_error = validate_required_strings(
            team_id, player_identifier, names=["team_id", "player_identifier"]
        )
        if validation_error:
            return validation_error

        container = get_container()

        # First, find the player
        try:
            from kickai.features.player_registration.domain.interfaces.player_service_interface import (
                IPlayerService,
            )

            player_service = container.get_service(IPlayerService)
            if not player_service:
                return "❌ Player service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get player service: {e}")
            return "❌ Player service is not available"

        # Use shared search utility to find player
        search_result = await find_player_by_identifier(player_service, player_identifier, team_id)

        if not search_result:
            return f"❌ {format_search_suggestions(player_identifier, team_id)}"

        player = search_result.player

        # Get match service with availability check
        try:
            from kickai.features.match_management.domain.interfaces.match_service_interface import (
                IMatchService,
            )

            match_service = container.get_service(IMatchService)
            if not match_service:
                return "❌ Match service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get match service: {e}")
            return "❌ Match service is not available"

        # Get player's current/upcoming matches with graceful error handling
        try:
            matches = await match_service.get_matches_for_player(player.player_id, team_id)
        except Exception as e:
            logger.warning(f"⚠️ Match service operation failed for {player.player_id}: {e}")
            return f"⚠️ Unable to retrieve match information: {e!s}"

        if not matches:
            return f"📅 No current or upcoming matches found for {player.name}"

        # Find current or next match
        current_match = None
        for match in matches:
            if match.status in ["upcoming", "in_progress"]:
                current_match = match
                break

        if current_match:
            match_text = f"⚽ Current Match for {player.name}\n\n"
            match_text += f"🆚 Opponent: {current_match.opponent}\n"
            match_text += f"📅 Date: {current_match.match_date.isoformat()}\n"
            match_text += f"📍 Location: {current_match.location}\n"
            match_text += f"📊 Status: {current_match.status}\n"
            if hasattr(current_match, "player_availability"):
                match_text += f"✅ Player Availability: {current_match.player_availability}"
            return match_text
        else:
            return f"📅 No current or upcoming matches scheduled for {player.name}"

    except Exception as e:
        logger.error(f"❌ Error getting player match information for {player_identifier}: {e}")
        return f"❌ Failed to get player match information: {e!s}"


@tool("list_players_active")
async def list_players_active(
    team_id: str, telegram_id: str, telegram_username: str = "system", chat_type: str = "main"
) -> str:
    """Display active players available for selection.

    Shows current roster of approved and active players eligible
    for match squad selection and team activities.

    Use when: Squad selection or active roster review is needed
    Required: Team member access

    Returns: Active player roster with positions
    """
    try:
        # Validate only parameters actually used by this tool
        validation_error = validate_required_strings(team_id, names=["team_id"])
        if validation_error:
            return validation_error

        container = get_container()

        # Get player service with availability check
        try:
            from kickai.features.player_registration.domain.interfaces.player_service_interface import (
                IPlayerService,
            )

            player_service = container.get_service(IPlayerService)
            if not player_service:
                return "❌ Player service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get player service: {e}")
            return "❌ Player service is not available"

        # Get active players with graceful error handling
        try:
            players = await player_service.get_active_players(team_id)
        except Exception as e:
            logger.warning(f"⚠️ Player service operation failed: {e}")
            return f"⚠️ Unable to retrieve active players: {e!s}"

        if not players:
            return f"📋 No active players found in team {team_id}"

        # Sort by name
        players.sort(key=lambda x: x.name.lower() if x.name else "")

        # Format as clean text (no markdown)
        list_text = f"⚽ Active Players ({len(players)} total)\n\n"

        for i, player in enumerate(players, 1):
            list_text += f"{i}. {player.name or 'Unnamed'}\n"
            list_text += f"   🆔 ID: {player.player_id}\n"
            list_text += f"   📞 Phone: {player.phone_number or 'Not provided'}\n"
            list_text += f"   ⚽ Position: {player.position or 'Not set'}\n\n"

        return list_text.strip()

    except Exception as e:
        logger.error(f"❌ Error getting active players: {e}")
        return f"❌ Failed to get active players: {e!s}"
