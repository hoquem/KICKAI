from abc import ABC, abstractmethod
from typing import Dict, Any

class IBotStatusService(ABC):
    @abstractmethod
    def get_bot_status(self) -> Dict[str, Any]:
        pass
    @abstractmethod
    def is_bot_running(self) -> bool:
        pass
    @abstractmethod
    def get_uptime(self) -> str:
        pass 