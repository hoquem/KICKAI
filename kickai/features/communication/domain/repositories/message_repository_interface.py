from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MessageRepositoryInterface(ABC):
    @abstractmethod
    async def save(self, message: Dict[str, Any]) -> str:
        """Persist a message and return its ID."""
        pass

    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a message by its ID."""
        pass

    @abstractmethod
    async def get_by_conversation(
        self, conversation_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch messages for a conversation."""
        pass

    @abstractmethod
    async def list_for_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List messages for a user (sent or received)."""
        pass
