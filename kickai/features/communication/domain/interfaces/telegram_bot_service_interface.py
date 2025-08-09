from abc import ABC, abstractmethod
from typing import Any, Union


class TelegramBotServiceInterface(ABC):
    @abstractmethod
    async def start_polling(self) -> None:
        """Start polling for Telegram updates/messages."""
        pass

    @abstractmethod
    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs) -> Any:
        """Send a message to a Telegram chat."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the bot and clean up resources."""
        pass
