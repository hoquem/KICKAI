from typing import Optional
import logging
from datetime import time

from kickai.core.exceptions import AttendanceError, create_error_context
from kickai.features.match_management.domain.entities.attendance import (
    AttendanceStatus,
    MatchAttendance,
)
from kickai.features.match_management.domain.repositories.attendance_repository_interface import (
    AttendanceRepositoryInterface,
)
from kickai.utils.simple_id_generator import SimpleIDGenerator

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service for managing actual match day attendance."""

    def __init__(self, attendance_repository: AttendanceRepositoryInterface):
        self.attendance_repository = attendance_repository
        self.id_generator = SimpleIDGenerator()

    async def record_attendance(
        self,
        match_id: str,
        player_id: str,
        status: AttendanceStatus,
        reason: Optional[str] = None,
        recorded_by: str = "",
        arrival_time: Optional[time] = None,
    ) -> MatchAttendance:
        """Record actual attendance for a player at a match."""
        try:
            # Check if attendance already exists
            existing_attendance = await self.attendance_repository.get_by_match_and_player(
                match_id, player_id
            )

            if existing_attendance:
                # Update existing attendance
                existing_attendance.update(status, reason, arrival_time)
                updated_attendance = await self.attendance_repository.update(existing_attendance)
                logger.info(f"Updated attendance for player {player_id} in match {match_id}: {status.value}")
                return updated_attendance
            else:
                # Create new attendance record
                attendance_id = self.id_generator.generate_attendance_id(match_id, player_id)
                attendance = MatchAttendance.create(
                    match_id=match_id,
                    player_id=player_id,
                    status=status,
                    reason=reason,
                    recorded_by=recorded_by,
                    arrival_time=arrival_time,
                    attendance_id=attendance_id,
                )

                created_attendance = await self.attendance_repository.create(attendance)
                logger.info(f"Created attendance for player {player_id} in match {match_id}: {status.value}")
                return created_attendance

        except Exception as e:
            logger.error(f"Failed to record attendance for player {player_id} in match {match_id}: {e}")
            raise AttendanceError(
                f"Failed to record attendance: {e!s}",
                create_error_context("record_attendance")
            )

    async def get_match_attendance(self, match_id: str) -> list[MatchAttendance]:
        """Get all attendance records for a match."""
        try:
            attendances = await self.attendance_repository.get_by_match(match_id)
            return attendances
        except Exception as e:
            logger.error(f"Failed to get attendance for match {match_id}: {e}")
            raise AttendanceError(
                f"Failed to get match attendance: {e!s}",
                create_error_context("get_match_attendance")
            )

    async def get_player_attendance_history(self, player_id: str, limit: int = 10) -> list[MatchAttendance]:
        """Get attendance history for a player."""
        try:
            history = await self.attendance_repository.get_by_player(player_id, limit)
            return history
        except Exception as e:
            logger.error(f"Failed to get attendance history for player {player_id}: {e}")
            raise AttendanceError(
                f"Failed to get player attendance history: {e!s}",
                create_error_context("get_player_attendance_history")
            )

    async def get_attended_players(self, match_id: str) -> list[MatchAttendance]:
        """Get all players who attended a match."""
        try:
            attendances = await self.attendance_repository.get_by_status(match_id, AttendanceStatus.ATTENDED)
            return attendances
        except Exception as e:
            logger.error(f"Failed to get attended players for match {match_id}: {e}")
            raise AttendanceError(
                f"Failed to get attended players: {e!s}",
                create_error_context("get_attended_players")
            )

    async def get_absent_players(self, match_id: str) -> list[MatchAttendance]:
        """Get all players who were absent from a match."""
        try:
            attendances = await self.attendance_repository.get_by_status(match_id, AttendanceStatus.ABSENT)
            return attendances
        except Exception as e:
            logger.error(f"Failed to get absent players for match {match_id}: {e}")
            raise AttendanceError(
                f"Failed to get absent players: {e!s}",
                create_error_context("get_absent_players")
            )

    async def get_late_players(self, match_id: str) -> list[MatchAttendance]:
        """Get all players who were late to a match."""
        try:
            attendances = await self.attendance_repository.get_by_status(match_id, AttendanceStatus.LATE)
            return attendances
        except Exception as e:
            logger.error(f"Failed to get late players for match {match_id}: {e}")
            raise AttendanceError(
                f"Failed to get late players: {e!s}",
                create_error_context("get_late_players")
            )

    async def get_attendance_summary(self, match_id: str) -> dict:
        """Get attendance summary for a match."""
        try:
            summary = await self.attendance_repository.get_match_summary(match_id)
            return summary
        except Exception as e:
            logger.error(f"Failed to get attendance summary for match {match_id}: {e}")
            raise AttendanceError(
                f"Failed to get attendance summary: {e!s}",
                create_error_context("get_attendance_summary")
            )

    async def calculate_attendance_stats(self, player_id: str) -> dict:
        """Calculate attendance statistics for a player."""
        try:
            history = await self.get_player_attendance_history(player_id, limit=100)  # Get more history for stats

            total_matches = len(history)
            if total_matches == 0:
                return {
                    "total_matches": 0,
                    "attendance_rate": 0.0,
                    "attended": 0,
                    "absent": 0,
                    "late": 0,
                    "reliability_rating": "No Data"
                }

            attended = len([a for a in history if a.is_attended])
            absent = len([a for a in history if a.is_absent])
            late = len([a for a in history if a.is_late])

            attendance_rate = (attended / total_matches) * 100

            # Calculate reliability rating
            if attendance_rate >= 90:
                reliability_rating = "Excellent"
            elif attendance_rate >= 80:
                reliability_rating = "Good"
            elif attendance_rate >= 70:
                reliability_rating = "Fair"
            elif attendance_rate >= 60:
                reliability_rating = "Poor"
            else:
                reliability_rating = "Very Poor"

            stats = {
                "total_matches": total_matches,
                "attendance_rate": round(attendance_rate, 1),
                "attended": attended,
                "absent": absent,
                "late": late,
                "reliability_rating": reliability_rating
            }

            logger.info(f"Calculated attendance stats for player {player_id}: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Failed to calculate attendance stats for player {player_id}: {e}")
            raise AttendanceError(
                f"Failed to calculate attendance stats: {e!s}",
                create_error_context("calculate_attendance_stats")
            )

    async def bulk_record_attendance(
        self,
        match_id: str,
        attendance_records: list[dict],
        recorded_by: str = ""
    ) -> list[MatchAttendance]:
        """Record attendance for multiple players at once."""
        try:
            recorded_attendances = []

            for record in attendance_records:
                player_id = record.get("player_id")
                status = AttendanceStatus(record.get("status"))
                reason = record.get("reason")
                arrival_time_str = record.get("arrival_time")

                arrival_time = None
                if arrival_time_str:
                    arrival_time = time.fromisoformat(arrival_time_str)

                attendance = await self.record_attendance(
                    match_id=match_id,
                    player_id=player_id,
                    status=status,
                    reason=reason,
                    recorded_by=recorded_by,
                    arrival_time=arrival_time,
                )
                recorded_attendances.append(attendance)

            logger.info(f"Bulk recorded attendance for {len(recorded_attendances)} players in match {match_id}")
            return recorded_attendances
        except Exception as e:
            logger.error(f"Failed to bulk record attendance for match {match_id}: {e}")
            raise AttendanceError(
                f"Failed to bulk record attendance: {e!s}",
                create_error_context("bulk_record_attendance")
            )
