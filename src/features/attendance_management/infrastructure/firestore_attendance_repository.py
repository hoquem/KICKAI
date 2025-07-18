from features.attendance_management.domain.repositories.attendance_repository_interface import AttendanceRepositoryInterface
from core.constants import COLLECTION_ATTENDANCE
# from features.attendance_management.domain.entities.attendance import Attendance  # Uncomment and implement Attendance entity as needed

class FirestoreAttendanceRepository(AttendanceRepositoryInterface):
    def __init__(self, firebase_client):
        self.firebase_client = firebase_client
        self.collection_name = COLLECTION_ATTENDANCE

    async def create(self, attendance):  # Use Attendance type when available
        # Placeholder: Implement actual Firebase logic
        await self.firebase_client.set_document(self.collection_name, attendance.id, attendance.__dict__)
        return attendance

    async def get_by_id(self, attendance_id: str):  # -> Optional[Attendance]
        data = await self.firebase_client.get_document(self.collection_name, attendance_id)
        if data:
            return data  # Replace with Attendance(**data) when Attendance is implemented
        return None

    async def get_by_team(self, team_id: str):  # -> List[Attendance]
        docs = await self.firebase_client.query_collection(self.collection_name, {'team_id': team_id})
        return docs  # Replace with [Attendance(**doc) for doc in docs] when Attendance is implemented

    async def update(self, attendance):  # -> Attendance
        await self.firebase_client.set_document(self.collection_name, attendance.id, attendance.__dict__)
        return attendance

    async def delete(self, attendance_id: str) -> None:
        await self.firebase_client.delete_document(self.collection_name, attendance_id) 