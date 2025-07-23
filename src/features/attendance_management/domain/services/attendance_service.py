from features.attendance_management.domain.repositories.attendance_repository_interface import (
    AttendanceRepositoryInterface,
)

# from features.attendance_management.domain.entities.attendance import Attendance  # Uncomment and implement Attendance entity as needed

class AttendanceService:
    def __init__(self, attendance_repository: AttendanceRepositoryInterface):
        self.attendance_repository = attendance_repository

    async def create_attendance(self, attendance):  # Use Attendance type when available
        return await self.attendance_repository.create(attendance)

    async def get_attendance_by_id(self, attendance_id: str):  # -> Optional[Attendance]
        return await self.attendance_repository.get_by_id(attendance_id)

    async def get_attendance_by_team(self, team_id: str):  # -> List[Attendance]
        return await self.attendance_repository.get_by_team(team_id)

    async def update_attendance(self, attendance):  # -> Attendance
        return await self.attendance_repository.update(attendance)

    async def delete_attendance(self, attendance_id: str) -> None:
        await self.attendance_repository.delete(attendance_id)
