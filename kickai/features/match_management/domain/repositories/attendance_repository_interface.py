from abc import ABC, abstractmethod

from kickai.features.match_management.domain.entities.attendance import (
    AttendanceStatus,
    MatchAttendance,
)


class AttendanceRepositoryInterface(ABC):
    """Interface for attendance repository."""

    @abstractmethod
    async def create(self, attendance: MatchAttendance) -> MatchAttendance:
        """Create a new attendance record."""
        pass

    @abstractmethod
    async def get_by_id(self, attendance_id: str) -> MatchAttendance | None:
        """Get attendance by ID."""
        pass

    @abstractmethod
    async def get_by_match_and_player(
        self, match_id: str, player_id: str
    ) -> MatchAttendance | None:
        """Get attendance for a specific match and player."""
        pass

    @abstractmethod
    async def get_by_match(self, match_id: str) -> list[MatchAttendance]:
        """Get all attendance records for a match."""
        pass

    @abstractmethod
    async def get_by_player(self, player_id: str, limit: int = 10) -> list[MatchAttendance]:
        """Get attendance history for a player."""
        pass

    @abstractmethod
    async def get_by_status(self, match_id: str, status: AttendanceStatus) -> list[MatchAttendance]:
        """Get attendance records by status for a match."""
        pass

    @abstractmethod
    async def update(self, attendance: MatchAttendance) -> MatchAttendance:
        """Update an attendance record."""
        pass

    @abstractmethod
    async def delete(self, attendance_id: str) -> bool:
        """Delete an attendance record."""
        pass

    @abstractmethod
    async def get_match_summary(self, match_id: str) -> dict:
        """Get attendance summary for a match."""
        pass
