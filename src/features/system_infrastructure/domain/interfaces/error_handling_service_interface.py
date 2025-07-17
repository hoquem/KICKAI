from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class IErrorHandlingService(ABC):
    @abstractmethod
    async def handle_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        message_text: Optional[str] = None,
        operation: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        pass
    @abstractmethod
    def get_error_statistics(self) -> Dict[str, Any]:
        pass
    @abstractmethod
    def get_recent_errors(self, limit: int = 10) -> List[Any]:
        pass 