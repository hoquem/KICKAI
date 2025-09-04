import logging

from kickai.core.dependency_container import get_container
from kickai.features.attendance_management.domain.entities.attendance import (
    Attendance,
    AttendanceResponseMethod,
    AttendanceStatus,
    AttendanceSummary,
)
from kickai.features.attendance_management.domain.repositories.attendance_repository_interface import (
    AttendanceRepositoryInterface,
)
from kickai.features.attendance_management.infrastructure.firestore_attendance_repository import (
    FirestoreAttendanceRepository,
)
from kickai.features.match_management.domain.interfaces.match_service_interface import IMatchService
from kickai.features.player_registration.domain.interfaces.player_service_interface import (
    IPlayerService,
)

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service for managing player attendance and availability."""

    def __init__(self, attendance_repository: AttendanceRepositoryInterface = None):
        self.attendance_repository = attendance_repository or FirestoreAttendanceRepository()

    async def mark_attendance(
        self,
        player_id: str,
        match_id: str,
        status: AttendanceStatus,
        team_id: str | None = None,
        response_method: AttendanceResponseMethod = AttendanceResponseMethod.COMMAND,
        notes: str | None = None,
        marked_by: str | None = None,
    ) -> Attendance:
        """
        Mark player attendance for a match.
        Creates new record or updates existing one.
        """
        try:
            # Get additional context for the attendance record
            container = get_container()
            try:
                player_service = container.get_service(IPlayerService)
            except (RuntimeError, KeyError, AttributeError):
                player_service = None
            try:
                match_service = container.get_service(IMatchService)
            except (RuntimeError, KeyError, AttributeError):
                match_service = None

            player_name = None
            match_opponent = None
            match_date = None

            # Get player information
            if player_service:
                try:
                    player = await player_service.get_player_by_id(player_id, team_id)
                    if player:
                        player_name = player.name
                except (RuntimeError, AttributeError, KeyError) as e:
                    logger.warning(f"Could not get player info for {player_id}: {e}")

            # Get match information
            if match_service:
                try:
                    match = await match_service.get_match(match_id)
                    if match:
                        match_opponent = match.opponent
                        match_date = match.date
                except (RuntimeError, AttributeError, KeyError) as e:
                    logger.warning(f"Could not get match info for {match_id}: {e}")

            # Check if attendance record already exists
            existing_attendance = await self.attendance_repository.get_by_player_and_match(
                player_id, match_id, team_id
            )

            if isinstance(existing_attendance, Attendance):
                # Update existing record
                existing_attendance.update_status(status, response_method, notes)
                updated_attendance = await self.attendance_repository.update(existing_attendance)
                logger.info(
                    f"Updated attendance for player {player_id} and match {match_id}: {status.value}"
                )
                return updated_attendance
            else:
                # Create new record
                new_attendance = Attendance.create(
                    player_id=player_id,
                    match_id=match_id,
                    team_id=team_id,
                    status=status,
                    response_method=response_method,
                    player_name=player_name,
                    match_opponent=match_opponent,
                    match_date=match_date,
                    notes=notes,
                )
                created_attendance = await self.attendance_repository.create(new_attendance)
                logger.info(
                    f"Created attendance for player {player_id} and match {match_id}: {status.value}"
                )
                return created_attendance

        except (RuntimeError, ValueError, KeyError, AttributeError) as e:
            from kickai.features.match_management.domain.exceptions import AttendanceError

            logger.error(f"Failed to mark attendance: {e}")
            attendance_error = AttendanceError(str(player_id), str(match_id), str(e))
            raise attendance_error from e

    async def get_attendance_by_id(self, attendance_id: str) -> Attendance | None:
        """Get attendance record by ID."""
        return await self.attendance_repository.get_by_id(attendance_id)

    async def get_attendance_by_team(self, team_id: str) -> list[Attendance]:
        """Get all attendance records for a team."""
        return await self.attendance_repository.get_by_team(team_id)

    async def get_attendance_by_match(
        self, match_id: str, team_id: str | None = None
    ) -> list[Attendance]:
        """Get all attendance records for a specific match."""
        # Repository in tests expects single arg; pass team_id only if provided
        if team_id is None:
            return await self.attendance_repository.get_by_match(match_id)
        return await self.attendance_repository.get_by_match(match_id, team_id)

    async def get_attendance_by_player(
        self, player_id: str, team_id: str | None = None
    ) -> list[Attendance]:
        """Get all attendance records for a specific player."""
        if team_id is None:
            return await self.attendance_repository.get_by_player(player_id)
        return await self.attendance_repository.get_by_player(player_id, team_id)

    async def get_player_attendance_for_match(
        self, player_id: str, match_id: str, team_id: str
    ) -> Attendance | None:
        """Get attendance record for a specific player and match."""
        return await self.attendance_repository.get_by_player_and_match(
            player_id, match_id, team_id
        )

    async def get_match_attendance_summary(self, match_id: str, team_id: str) -> AttendanceSummary:
        """Get attendance summary for a match."""
        return await self.attendance_repository.get_match_summary(match_id, team_id)

    async def get_player_attendance_stats(
        self, player_id: str, team_id: str, year: int | None = None
    ) -> dict:
        """Get attendance statistics for a player."""
        return await self.attendance_repository.get_player_stats(player_id, team_id, year)

    async def initialize_match_attendance(self, match_id: str, team_id: str) -> list[Attendance]:
        """
        Initialize attendance records for all active players for a new match.
        Sets all players to NOT_RESPONDED status initially.
        """
        try:
            container = get_container()
            player_service = container.get_service(IPlayerService)
            match_service = container.get_service(IMatchService)

            if not player_service or not match_service:
                logger.error("Required services not available for attendance initialization")
                return []

            # Get active players
            players = await player_service.get_active_players(team_id)
            if not players:
                logger.warning(f"No active players found for team {team_id}")
                return []

            # Get match information
            match = await match_service.get_match(match_id)
            if not match:
                logger.error(f"Match {match_id} not found")
                return []

            # Create attendance records for all active players
            attendance_records = []
            for player in players:
                try:
                    # Check if attendance record already exists
                    existing = await self.get_player_attendance_for_match(
                        player.player_id, match_id, team_id
                    )

                    if not existing:
                        attendance = Attendance.create(
                            player_id=player.player_id,
                            match_id=match_id,
                            team_id=team_id,
                            status=AttendanceStatus.NOT_RESPONDED,
                            response_method=AttendanceResponseMethod.AUTO_REMINDER,
                            player_name=player.name,
                            match_opponent=match.opponent,
                            match_date=match.date,
                        )
                        created_attendance = await self.attendance_repository.create(attendance)
                        attendance_records.append(created_attendance)
                    else:
                        attendance_records.append(existing)

                except (RuntimeError, ValueError, KeyError, AttributeError) as e:
                    logger.error(f"Failed to create attendance for player {player.player_id}: {e}")

            logger.info(
                f"Initialized attendance for {len(attendance_records)} players for match {match_id}"
            )
            return attendance_records

        except (RuntimeError, ValueError, KeyError, AttributeError) as e:
            logger.error(f"Failed to initialize match attendance: {e}")
            # Return empty list to prevent cascade failures
            return []

    async def update_attendance(self, attendance: Attendance) -> Attendance:
        """Update an existing attendance record."""
        return await self.attendance_repository.update(attendance)

    async def delete_attendance(self, attendance_id: str) -> None:
        """Delete an attendance record."""
        await self.attendance_repository.delete(attendance_id)

    async def get_available_players_for_match(self, match_id: str, team_id: str) -> list[dict]:
        """Get list of players who are available for a specific match."""
        try:
            attendance_records = await self.get_attendance_by_match(match_id, team_id)
            available_players = []

            for attendance in attendance_records:
                if attendance.status == AttendanceStatus.YES.value:
                    available_players.append(
                        {
                            "player_id": attendance.player_id,
                            "player_name": attendance.player_name,
                            "response_timestamp": attendance.response_timestamp,
                            "notes": attendance.notes,
                        }
                    )

            return available_players

        except (RuntimeError, ValueError, KeyError, AttributeError) as e:
            logger.error(f"Failed to get available players for match {match_id}: {e}")
            # Return empty list to prevent cascade failures
            return []

    async def get_team_attendance_summary(self, team_id: str) -> dict:
        """Get overall attendance summary for the team."""
        try:
            all_attendance = await self.get_attendance_by_team(team_id)

            if not all_attendance:
                return {
                    "team_id": team_id,
                    "total_records": 0,
                    "overall_response_rate": 0.0,
                    "overall_attendance_rate": 0.0,
                }

            total_records = len(all_attendance)
            responded = sum(1 for a in all_attendance if a.has_responded())
            available = sum(1 for a in all_attendance if a.is_available())

            response_rate = (responded / total_records * 100) if total_records > 0 else 0.0
            attendance_rate = (available / total_records * 100) if total_records > 0 else 0.0

            return {
                "team_id": team_id,
                "total_records": total_records,
                "responded_count": responded,
                "available_count": available,
                "overall_response_rate": round(response_rate, 1),
                "overall_attendance_rate": round(attendance_rate, 1),
            }

        except (RuntimeError, ValueError, KeyError, AttributeError) as e:
            logger.error(f"Failed to get team attendance summary: {e}")
            # Return empty dict to prevent cascade failures
            return {}
