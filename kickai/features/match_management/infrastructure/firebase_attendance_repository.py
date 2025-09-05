import logging

from kickai.features.match_management.domain.entities.attendance import (
    AttendanceStatus,
    MatchAttendance,
)
from kickai.features.match_management.domain.repositories.attendance_repository_interface import (
    AttendanceRepositoryInterface,
)

logger = logging.getLogger(__name__)


class FirebaseAttendanceRepository(AttendanceRepositoryInterface):
    """Firebase implementation of attendance repository."""

    def __init__(self, firebase_client):
        self.firebase_client = firebase_client

    def _get_collection_name(self, team_id: str) -> str:
        """Get the collection name for a team's attendance."""
        return f"kickai_{team_id}_match_attendance"

    async def create(self, attendance: MatchAttendance) -> MatchAttendance:
        """Create a new attendance record."""
        try:
            # We need to get the team_id from the match
            # For now, we'll use a simple approach - this could be optimized
            collection_name = self._get_collection_name("KTI")  # Default team
            await self.firebase_client.create_document(
                collection=collection_name,
                document_id=attendance.attendance_id,
                data=attendance.to_dict(),
            )
            logger.info(f"Created attendance {attendance.attendance_id}")
            return attendance
        except Exception as e:
            logger.error(f"Failed to create attendance {attendance.attendance_id}: {e}")
            raise

    async def get_by_id(self, attendance_id: str) -> MatchAttendance | None:
        """Get attendance by ID."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                data = await self.firebase_client.get_document(collection_name, attendance_id)
                if data:
                    return MatchAttendance.from_dict(data)

            return None
        except Exception as e:
            logger.error(f"Failed to get attendance {attendance_id}: {e}")
            return None

    async def get_by_match_and_player(
        self, match_id: str, player_id: str
    ) -> MatchAttendance | None:
        """Get attendance for a specific match and player."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                docs = await self.firebase_client.query_documents(
                    collection_name, filters={"match_id": match_id, "player_id": player_id}
                )
                if docs:
                    return MatchAttendance.from_dict(docs[0])

            return None
        except Exception as e:
            logger.error(
                f"Failed to get attendance for match {match_id} and player {player_id}: {e}"
            )
            return None

    async def get_by_match(self, match_id: str) -> list[MatchAttendance]:
        """Get all attendance records for a match."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")
            all_attendances = []

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                docs = await self.firebase_client.query_documents(
                    collection_name, filters={"match_id": match_id}
                )
                attendances = [MatchAttendance.from_dict(doc) for doc in docs]
                all_attendances.extend(attendances)

            logger.info(f"Retrieved {len(all_attendances)} attendance records for match {match_id}")
            return all_attendances
        except Exception as e:
            logger.error(f"Failed to get attendance for match {match_id}: {e}")
            return []

    async def get_by_player(self, player_id: str, limit: int = 10) -> list[MatchAttendance]:
        """Get attendance history for a player."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")
            all_attendances = []

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                docs = await self.firebase_client.query_documents(
                    collection_name, filters={"player_id": player_id}
                )
                attendances = [MatchAttendance.from_dict(doc) for doc in docs]
                all_attendances.extend(attendances)

            # Sort by recorded_at (newest first) and limit
            all_attendances.sort(key=lambda a: a.recorded_at, reverse=True)

            logger.info(
                f"Retrieved {len(all_attendances[:limit])} attendance records for player {player_id}"
            )
            return all_attendances[:limit]
        except Exception as e:
            logger.error(f"Failed to get attendance for player {player_id}: {e}")
            return []

    async def get_by_status(self, match_id: str, status: AttendanceStatus) -> list[MatchAttendance]:
        """Get attendance records by status for a match."""
        try:
            match_attendances = await self.get_by_match(match_id)
            filtered_attendances = [
                attendance for attendance in match_attendances if attendance.status == status
            ]

            logger.info(
                f"Retrieved {len(filtered_attendances)} {status.value} attendance records for match {match_id}"
            )
            return filtered_attendances
        except Exception as e:
            logger.error(f"Failed to get {status.value} attendance for match {match_id}: {e}")
            return []

    async def update(self, attendance: MatchAttendance) -> MatchAttendance:
        """Update an attendance record."""
        try:
            # We need to find the team_id - for now using default
            collection_name = self._get_collection_name("KTI")  # Default team
            await self.firebase_client.update_document(
                collection=collection_name,
                document_id=attendance.attendance_id,
                data=attendance.to_dict(),
            )
            logger.info(f"Updated attendance {attendance.attendance_id}")
            return attendance
        except Exception as e:
            logger.error(f"Failed to update attendance {attendance.attendance_id}: {e}")
            raise

    async def delete(self, attendance_id: str) -> bool:
        """Delete an attendance record."""
        try:
            # We need to find the attendance first to get the team_id
            attendance = await self.get_by_id(attendance_id)
            if not attendance:
                logger.warning(f"Attendance {attendance_id} not found for deletion")
                return False

            collection_name = self._get_collection_name("KTI")  # Default team
            await self.firebase_client.delete_document(collection_name, attendance_id)
            logger.info(f"Deleted attendance {attendance_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete attendance {attendance_id}: {e}")
            return False

    async def get_match_summary(self, match_id: str) -> dict:
        """Get attendance summary for a match."""
        try:
            match_attendances = await self.get_by_match(match_id)

            summary = {
                "total_players": len(match_attendances),
                "attended": len([a for a in match_attendances if a.is_attended]),
                "absent": len([a for a in match_attendances if a.is_absent]),
                "late": len([a for a in match_attendances if a.is_late]),
                "not_recorded": len(
                    [a for a in match_attendances if a.status == AttendanceStatus.NOT_RECORDED]
                ),
            }

            logger.info(f"Generated attendance summary for match {match_id}: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Failed to get attendance summary for match {match_id}: {e}")
            return {
                "total_players": 0,
                "attended": 0,
                "absent": 0,
                "late": 0,
                "not_recorded": 0,
            }
