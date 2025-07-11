from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from datetime import datetime

class IReminderService(ABC):
    @abstractmethod
    async def check_and_send_reminders(self) -> List:
        pass

    @abstractmethod
    async def send_automated_reminder(self, player) -> Optional:
        pass

    @abstractmethod
    async def send_manual_reminder(self, player_id: str, admin_id: str) -> Tuple[bool, str]:
        pass

    @abstractmethod
    async def get_players_needing_reminders(self) -> List:
        pass 