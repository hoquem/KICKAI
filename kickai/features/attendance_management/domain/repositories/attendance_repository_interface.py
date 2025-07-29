from abc import ABC, abstractmethod

from kickai.features.attendance_management.domain.entities.attendance import (
    Attendance,
    AttendanceSummary,
)


class AttendanceRepositoryInterface(ABC):
    """Repository interface for attendance management."""

    @abstractmethod
    async def create(self, attendance: Attendance) -> Attendance:
        """Create a new attendance record."""
        pass

    @abstractmethod
    async def get_by_id(self, attendance_id: str) -> Attendance | None:
        """Get attendance record by ID."""
        pass

    @abstractmethod
    async def get_by_team(self, team_id: str) -> list[Attendance]:
        """Get all attendance records for a team."""
        pass

    @abstractmethod
    async def get_by_match(self, match_id: str, team_id: str) -> list[Attendance]:
        """Get all attendance records for a specific match."""
        pass

    @abstractmethod
    async def get_by_player(self, player_id: str, team_id: str) -> list[Attendance]:
        """Get all attendance records for a specific player."""
        pass

    @abstractmethod
    async def get_by_player_and_match(
        self, player_id: str, match_id: str, team_id: str
    ) -> Attendance | None:
        """Get attendance record for a specific player and match."""
        pass

    @abstractmethod
    async def update(self, attendance: Attendance) -> Attendance:
        """Update an existing attendance record."""
        pass

    @abstractmethod
    async def delete(self, attendance_id: str) -> None:
        """Delete an attendance record."""
        pass

    @abstractmethod
    async def get_match_summary(self, match_id: str, team_id: str) -> AttendanceSummary:
        """Get attendance summary for a match."""
        pass

    @abstractmethod
    async def get_player_stats(self, player_id: str, team_id: str, year: int | None = None) -> dict:
        """Get attendance statistics for a player."""
        pass
