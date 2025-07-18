"""
Telegram tools for KICKAI (placeholder, not used in production).
"""

from typing import Type
from loguru import logger
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

TOOL_REGISTRY = {}

def register_tool_instance(tool_instance):
    TOOL_REGISTRY[tool_instance.name] = tool_instance
    return tool_instance

class SendTelegramMessageInput(BaseModel):
    chat_id: str = Field(..., description="Telegram chat ID")
    text: str = Field(..., description="Message text")

class SendTelegramMessageTool(BaseTool):
    name: str = "send_telegram_message"
    description: str = "Send a message to a Telegram chat (example tool)."
    args_schema: Type[BaseModel] = SendTelegramMessageInput

    def _run(self, chat_id: str, text: str) -> bool:
        logger.info(f"[TOOL] Sending Telegram message to chat_id={chat_id}: {text}")
        # Placeholder logic
        return True

register_tool_instance(SendTelegramMessageTool())

__all__ = ["TOOL_REGISTRY"] 