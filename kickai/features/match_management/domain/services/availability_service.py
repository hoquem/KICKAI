import logging

from kickai.core.exceptions import AvailabilityError, create_error_context
from kickai.features.match_management.domain.entities.availability import (
    Availability,
    AvailabilityStatus,
)
from kickai.features.match_management.domain.repositories.availability_repository_interface import (
    AvailabilityRepositoryInterface,
)
from kickai.utils.simple_id_generator import SimpleIDGenerator

logger = logging.getLogger(__name__)


class AvailabilityService:
    """Service for managing player availability for matches."""

    def __init__(self, availability_repository: AvailabilityRepositoryInterface):
        self.availability_repository = availability_repository
        self.id_generator = SimpleIDGenerator()

    async def mark_availability(
        self,
        match_id: str,
        player_id: str,
        status: AvailabilityStatus,
        reason: str | None = None,
    ) -> Availability:
        """Mark player availability for a match."""
        try:
            # Check if availability already exists
            existing_availability = await self.availability_repository.get_by_match_and_player(
                match_id, player_id
            )

            if existing_availability:
                # Update existing availability
                existing_availability.update(status, reason, player_id)
                updated_availability = await self.availability_repository.update(
                    existing_availability
                )
                logger.info(
                    f"Updated availability for player {player_id} in match {match_id}: {status.value}"
                )
                return updated_availability
            else:
                # Create new availability
                availability_id = self.id_generator.generate_availability_id(match_id, player_id)
                availability = Availability.create(
                    match_id=match_id,
                    player_id=player_id,
                    status=status,
                    reason=reason,
                    availability_id=availability_id,
                )

                created_availability = await self.availability_repository.create(availability)
                logger.info(
                    f"Created availability for player {player_id} in match {match_id}: {status.value}"
                )
                return created_availability

        except Exception as e:
            logger.error(
                f"Failed to mark availability for player {player_id} in match {match_id}: {e}"
            )
            raise AvailabilityError(
                f"Failed to mark availability: {e!s}", create_error_context("mark_availability")
            )

    async def get_availability(self, match_id: str, player_id: str) -> Availability | None:
        """Get availability for a specific match and player."""
        try:
            availability = await self.availability_repository.get_by_match_and_player(
                match_id, player_id
            )
            return availability
        except Exception as e:
            logger.error(
                f"Failed to get availability for player {player_id} in match {match_id}: {e}"
            )
            raise AvailabilityError(
                f"Failed to get availability: {e!s}", create_error_context("get_availability")
            )

    async def list_match_availability(self, match_id: str) -> list[Availability]:
        """Get all availability records for a match."""
        try:
            availabilities = await self.availability_repository.get_by_match(match_id)
            return availabilities
        except Exception as e:
            logger.error(f"Failed to get availability for match {match_id}: {e}")
            raise AvailabilityError(
                f"Failed to get match availability: {e!s}",
                create_error_context("list_match_availability"),
            )

    async def get_player_history(self, player_id: str, limit: int = 10) -> list[Availability]:
        """Get availability history for a player."""
        try:
            history = await self.availability_repository.get_by_player(player_id, limit)
            return history
        except Exception as e:
            logger.error(f"Failed to get availability history for player {player_id}: {e}")
            raise AvailabilityError(
                f"Failed to get player history: {e!s}", create_error_context("get_player_history")
            )

    async def get_available_players(self, match_id: str) -> list[Availability]:
        """Get all available players for a match."""
        try:
            availabilities = await self.availability_repository.get_by_status(
                match_id, AvailabilityStatus.AVAILABLE
            )
            return availabilities
        except Exception as e:
            logger.error(f"Failed to get available players for match {match_id}: {e}")
            raise AvailabilityError(
                f"Failed to get available players: {e!s}",
                create_error_context("get_available_players"),
            )

    async def get_unavailable_players(self, match_id: str) -> list[Availability]:
        """Get all unavailable players for a match."""
        try:
            availabilities = await self.availability_repository.get_by_status(
                match_id, AvailabilityStatus.UNAVAILABLE
            )
            return availabilities
        except Exception as e:
            logger.error(f"Failed to get unavailable players for match {match_id}: {e}")
            raise AvailabilityError(
                f"Failed to get unavailable players: {e!s}",
                create_error_context("get_unavailable_players"),
            )

    async def get_maybe_players(self, match_id: str) -> list[Availability]:
        """Get all maybe players for a match."""
        try:
            availabilities = await self.availability_repository.get_by_status(
                match_id, AvailabilityStatus.MAYBE
            )
            return availabilities
        except Exception as e:
            logger.error(f"Failed to get maybe players for match {match_id}: {e}")
            raise AvailabilityError(
                f"Failed to get maybe players: {e!s}", create_error_context("get_maybe_players")
            )

    async def get_pending_players(self, match_id: str) -> list[Availability]:
        """Get all pending players for a match."""
        try:
            availabilities = await self.availability_repository.get_pending_availability(match_id)
            return availabilities
        except Exception as e:
            logger.error(f"Failed to get pending players for match {match_id}: {e}")
            raise AvailabilityError(
                f"Failed to get pending players: {e!s}", create_error_context("get_pending_players")
            )

    async def get_availability_summary(self, match_id: str) -> dict:
        """Get availability summary for a match."""
        try:
            all_availabilities = await self.list_match_availability(match_id)

            summary = {
                "total_players": len(all_availabilities),
                "available": len([a for a in all_availabilities if a.is_available]),
                "unavailable": len([a for a in all_availabilities if a.is_unavailable]),
                "maybe": len([a for a in all_availabilities if a.is_maybe]),
                "pending": len([a for a in all_availabilities if a.is_pending]),
            }

            logger.info(f"Generated availability summary for match {match_id}: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Failed to get availability summary for match {match_id}: {e}")
            raise AvailabilityError(
                f"Failed to get availability summary: {e!s}",
                create_error_context("get_availability_summary"),
            )

    async def send_availability_reminders(self, match_id: str) -> bool:
        """Send reminders to players who haven't responded to availability requests."""
        try:
            pending_players = await self.get_pending_players(match_id)

            # This would integrate with the notification system
            # For now, just log the reminder
            logger.info(
                f"Sending availability reminders to {len(pending_players)} players for match {match_id}"
            )

            # TODO: Implement actual notification sending
            # for availability in pending_players:
            #     await notification_service.send_availability_reminder(availability.player_id, match_id)

            return True
        except Exception as e:
            logger.error(f"Failed to send availability reminders for match {match_id}: {e}")
            return False
