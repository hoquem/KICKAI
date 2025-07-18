from typing import Optional, Type
from loguru import logger
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

TOOL_REGISTRY = {}

def register_tool_instance(tool_instance):
    TOOL_REGISTRY[tool_instance.name] = tool_instance
    return tool_instance

class SendMessageInput(BaseModel):
    chat_id: str = Field(..., description="Telegram chat ID")
    text: str = Field(..., description="Message text")
    team_id: Optional[str] = Field(None, description="Team ID (optional)")

class SendMessageTool(BaseTool):
    name: str = "send_message"
    description: str = "Send a message to a Telegram chat."
    args_schema: Type[BaseModel] = SendMessageInput

    def _run(self, chat_id: str, text: str, team_id: Optional[str] = None) -> bool:
        logger.info(f"[TOOL] Sending message to chat_id={chat_id}: {text}")
        # TODO: Integrate with TelegramBotService
        return True

register_tool_instance(SendMessageTool())

class SendAnnouncementInput(BaseModel):
    chat_id: str = Field(..., description="Telegram chat ID")
    text: str = Field(..., description="Announcement text")
    team_id: Optional[str] = Field(None, description="Team ID (optional)")

class SendAnnouncementTool(BaseTool):
    name: str = "send_announcement"
    description: str = "Send an announcement to a Telegram chat."
    args_schema: Type[BaseModel] = SendAnnouncementInput

    def _run(self, chat_id: str, text: str, team_id: Optional[str] = None) -> bool:
        logger.info(f"[TOOL] Sending announcement to chat_id={chat_id}: {text}")
        # TODO: Integrate with TelegramBotService
        return True

register_tool_instance(SendAnnouncementTool())

class SendPollInput(BaseModel):
    chat_id: str = Field(..., description="Telegram chat ID")
    question: str = Field(..., description="Poll question")
    options: list = Field(..., description="Poll options")
    team_id: Optional[str] = Field(None, description="Team ID (optional)")

class SendPollTool(BaseTool):
    name: str = "send_poll"
    description: str = "Send a poll to a Telegram chat."
    args_schema: Type[BaseModel] = SendPollInput

    def _run(self, chat_id: str, question: str, options: list, team_id: Optional[str] = None) -> bool:
        logger.info(f"[TOOL] Sending poll to chat_id={chat_id}: {question} | Options: {options}")
        # TODO: Integrate with TelegramBotService
        return True

register_tool_instance(SendPollTool())

__all__ = ["TOOL_REGISTRY"] 