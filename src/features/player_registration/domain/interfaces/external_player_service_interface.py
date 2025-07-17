from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class IExternalPlayerService(ABC):
    @abstractmethod
    async def get_external_player(self, external_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def find_external_player_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        pass 