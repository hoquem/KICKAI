from abc import ABC, abstractmethod

# from features.attendance_management.domain.entities.attendance import Attendance  # Uncomment and implement Attendance entity as needed

class AttendanceRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, attendance):  # Use Attendance type when available
        pass

    @abstractmethod
    async def get_by_id(self, attendance_id: str):  # -> Optional[Attendance]
        pass

    @abstractmethod
    async def get_by_team(self, team_id: str):  # -> List[Attendance]
        pass

    @abstractmethod
    async def update(self, attendance):  # -> Attendance
        pass

    @abstractmethod
    async def delete(self, attendance_id: str) -> None:
        pass
