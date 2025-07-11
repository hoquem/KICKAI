from abc import ABC, abstractmethod
from typing import Dict

class IDailyStatusService(ABC):
    @abstractmethod
    async def generate_team_stats(self, team_id: str) -> Dict:
        pass

    @abstractmethod
    def format_daily_status_message(self, team_stats: Dict, team_name: str = "Team") -> str:
        pass

    @abstractmethod
    async def send_daily_status_report(self, team_id: str, leadership_chat_id: str) -> bool:
        pass

    @abstractmethod
    async def schedule_daily_status_task(self, team_id: str, leadership_chat_id: str) -> None:
        pass 