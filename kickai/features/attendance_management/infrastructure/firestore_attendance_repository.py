import logging
from datetime import datetime

from typing import Dict, List, Optional
from kickai.database.firebase_client import get_firebase_client
from kickai.features.attendance_management.domain.entities.attendance import (
    Attendance,
    AttendanceStatus,
    AttendanceSummary,
)
from kickai.features.attendance_management.domain.repositories.attendance_repository_interface import (
    AttendanceRepositoryInterface,
)

logger = logging.getLogger(__name__)


class FirestoreAttendanceRepository(AttendanceRepositoryInterface):
    """Firestore implementation of attendance repository."""

    def __init__(self, firebase_client=None):
        self.firebase_client = firebase_client or get_firebase_client()

    def _get_collection_name(self, team_id: str) -> str:
        """Get team-specific attendance collection name."""
        return f"kickai_{team_id}_attendance"

    async def create(self, attendance: Attendance) -> Attendance:
        """Create a new attendance record."""
        try:
            collection_name = self._get_collection_name(attendance.team_id)
            data = attendance.to_dict()
            
            await self.firebase_client.create_document(collection_name, attendance.id, data)
            logger.info(f"Created attendance record: {attendance.id}")
            return attendance
            
        except Exception as e:
            logger.error(f"Failed to create attendance record: {e}")
            raise

    async def get_by_id(self, attendance_id: str) -> Optional[Attendance]:
        """Get attendance record by ID."""
        try:
            # Extract team_id from attendance_id format: {team_id}_{match_id}_{player_id}
            team_id = attendance_id.split('_')[0]
            collection_name = self._get_collection_name(team_id)
            
            data = await self.firebase_client.get_document(collection_name, attendance_id)
            if data:
                return Attendance.from_dict(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get attendance record {attendance_id}: {e}")
            return None

    async def get_by_team(self, team_id: str) -> List[Attendance]:
        """Get all attendance records for a team."""
        try:
            collection_name = self._get_collection_name(team_id)
            filters = [{"field": "team_id", "operator": "==", "value": team_id}]
            
            docs = await self.firebase_client.query_documents(collection_name, filters)
            return [Attendance.from_dict(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Failed to get attendance records for team {team_id}: {e}")
            return []

    async def get_by_match(self, match_id: str, team_id: str) -> List[Attendance]:
        """Get all attendance records for a specific match."""
        try:
            collection_name = self._get_collection_name(team_id)
            filters = [
                {"field": "team_id", "operator": "==", "value": team_id},
                {"field": "match_id", "operator": "==", "value": match_id}
            ]
            
            docs = await self.firebase_client.query_documents(collection_name, filters)
            return [Attendance.from_dict(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Failed to get attendance records for match {match_id}: {e}")
            return []

    async def get_by_player(self, player_id: str, team_id: str) -> List[Attendance]:
        """Get all attendance records for a specific player."""
        try:
            collection_name = self._get_collection_name(team_id)
            filters = [
                {"field": "team_id", "operator": "==", "value": team_id},
                {"field": "player_id", "operator": "==", "value": player_id}
            ]
            
            docs = await self.firebase_client.query_documents(collection_name, filters)
            return [Attendance.from_dict(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Failed to get attendance records for player {player_id}: {e}")
            return []

    async def get_by_player_and_match(self, player_id: str, match_id: str, team_id: str) -> Optional[Attendance]:
        """Get attendance record for a specific player and match."""
        try:
            attendance_id = f"{team_id}_{match_id}_{player_id}"
            return await self.get_by_id(attendance_id)
            
        except Exception as e:
            logger.error(f"Failed to get attendance for player {player_id} and match {match_id}: {e}")
            return None

    async def update(self, attendance: Attendance) -> Attendance:
        """Update an existing attendance record."""
        try:
            collection_name = self._get_collection_name(attendance.team_id)
            data = attendance.to_dict()
            
            await self.firebase_client.update_document(collection_name, attendance.id, data)
            logger.info(f"Updated attendance record: {attendance.id}")
            return attendance
            
        except Exception as e:
            logger.error(f"Failed to update attendance record: {e}")
            raise

    async def delete(self, attendance_id: str) -> None:
        """Delete an attendance record."""
        try:
            # Extract team_id from attendance_id
            team_id = attendance_id.split('_')[0]
            collection_name = self._get_collection_name(team_id)
            
            await self.firebase_client.delete_document(collection_name, attendance_id)
            logger.info(f"Deleted attendance record: {attendance_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete attendance record {attendance_id}: {e}")
            raise

    async def get_match_summary(self, match_id: str, team_id: str) -> AttendanceSummary:
        """Get attendance summary for a match."""
        try:
            attendance_list = await self.get_by_match(match_id, team_id)
            return AttendanceSummary.from_attendance_list(match_id, team_id, attendance_list)
            
        except Exception as e:
            logger.error(f"Failed to get match summary for {match_id}: {e}")
            # Return empty summary
            return AttendanceSummary(
                match_id=match_id,
                team_id=team_id,
                total_players=0,
                available_count=0,
                unavailable_count=0,
                maybe_count=0,
                no_response_count=0,
                response_rate=0.0,
                last_updated=datetime.utcnow().isoformat(),
            )

    async def get_player_stats(self, player_id: str, team_id: str, year: Optional[int] = None) -> dict:
        """Get attendance statistics for a player."""
        try:
            attendance_list = await self.get_by_player(player_id, team_id)
            
            # Filter by year if specified
            if year:
                year_str = str(year)
                attendance_list = [
                    a for a in attendance_list
                    if a.match_date and a.match_date.startswith(year_str)
                ]
            
            total_matches = len(attendance_list)
            if total_matches == 0:
                return {
                    "player_id": player_id,
                    "team_id": team_id,
                    "year": year,
                    "total_matches": 0,
                    "attended": 0,
                    "missed": 0,
                    "maybe_responses": 0,
                    "no_responses": 0,
                    "attendance_rate": 0.0,
                    "response_rate": 0.0,
                }
            
            attended = sum(1 for a in attendance_list if a.status == AttendanceStatus.YES.value)
            missed = sum(1 for a in attendance_list if a.status == AttendanceStatus.NO.value)
            maybe = sum(1 for a in attendance_list if a.status == AttendanceStatus.MAYBE.value)
            no_response = sum(1 for a in attendance_list if a.status == AttendanceStatus.NOT_RESPONDED.value)
            
            attendance_rate = (attended / total_matches * 100) if total_matches > 0 else 0.0
            response_rate = ((total_matches - no_response) / total_matches * 100) if total_matches > 0 else 0.0
            
            return {
                "player_id": player_id,
                "team_id": team_id,
                "year": year,
                "total_matches": total_matches,
                "attended": attended,
                "missed": missed,
                "maybe_responses": maybe,
                "no_responses": no_response,
                "attendance_rate": round(attendance_rate, 1),
                "response_rate": round(response_rate, 1),
            }
            
        except Exception as e:
            logger.error(f"Failed to get player stats for {player_id}: {e}")
            return {}
