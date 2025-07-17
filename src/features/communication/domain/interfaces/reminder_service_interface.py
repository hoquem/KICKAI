from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from features.player_registration.domain.entities.player import Player

class IReminderService(ABC):
    """Interface for reminder service operations."""
    
    @abstractmethod
    async def check_and_send_reminders(self) -> List:
        """Check for players who need reminders and send them."""
        pass
    
    @abstractmethod
    async def send_automated_reminder(self, player: Player):
        """Send an automated reminder to a player."""
        pass
    
    @abstractmethod
    async def send_manual_reminder(self, player_id: str, admin_id: str) -> Tuple[bool, str]:
        """Send a manual reminder to a player (admin triggered)."""
        pass
    
    @abstractmethod
    async def get_players_needing_reminders(self) -> List[Player]:
        """Get list of players who need reminders."""
        pass 