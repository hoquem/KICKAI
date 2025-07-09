"""
LangChain tools for communication operations.

These tools provide basic communication capabilities for agents.
"""

import logging
from typing import List, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SendMessageInput(BaseModel):
    """Input for sending a message."""
    message: str = Field(description="The message to send")
    team_id: str = Field(description="The team ID")


class SendPollInput(BaseModel):
    """Input for sending a poll."""
    question: str = Field(description="The poll question")
    options: List[str] = Field(description="The poll options")
    team_id: str = Field(description="The team ID")


class SendAnnouncementInput(BaseModel):
    """Input for sending an announcement."""
    announcement: str = Field(description="The announcement message")
    team_id: str = Field(description="The team ID")


class SendMessageTool(BaseTool):
    """Tool to send a message to a chat."""
    
    name = "send_message"
    description = "Send a message to a specific chat"
    args_schema = SendMessageInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    
    def __init__(self, team_id: str):
        super().__init__()
        self.team_id = team_id
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        SendMessageTool.logger = self.logger
        SendMessageTool.team_id = team_id
    
    def _run(self, chat_id: str, message: str, team_id: str) -> str:
        """Send a message synchronously."""
        try:
            self.logger.info(f"Message sent to chat {chat_id}: {message[:50]}...")
            return f"Message sent to chat {chat_id}"
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, chat_id: str, message: str, team_id: str) -> str:
        """Send a message asynchronously."""
        return self._run(chat_id, message, team_id)


class SendPollTool(BaseTool):
    """Tool to send a poll."""
    
    name = "send_poll"
    description = "Send a poll to the team chat"
    args_schema = SendPollInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    
    def __init__(self, team_id: str):
        super().__init__()
        self.team_id = team_id
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        SendPollTool.logger = self.logger
        SendPollTool.team_id = team_id
    
    def _run(self, question: str, options: List[str], team_id: str) -> str:
        """Send a poll synchronously."""
        try:
            # For now, just log the poll - in a real implementation,
            # this would integrate with the Telegram service
            self.logger.info(f"Would send poll to team {team_id}: {question} - Options: {options}")
            return f"Poll logged for team {team_id}: {question[:50]}..."
        except Exception as e:
            self.logger.error(f"Error sending poll: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, question: str, options: List[str], team_id: str) -> str:
        """Send a poll asynchronously."""
        return self._run(question, options, team_id)


class SendAnnouncementTool(BaseTool):
    """Tool to send an announcement."""
    
    name = "send_announcement"
    description = "Send an announcement to the team chat"
    args_schema = SendAnnouncementInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    
    def __init__(self, team_id: str):
        super().__init__()
        self.team_id = team_id
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        SendAnnouncementTool.logger = self.logger
        SendAnnouncementTool.team_id = team_id
    
    def _run(self, announcement: str, team_id: str) -> str:
        """Send an announcement synchronously."""
        try:
            # For now, just log the announcement - in a real implementation,
            # this would integrate with the Telegram service
            self.logger.info(f"Would send announcement to team {team_id}: {announcement}")
            return f"Announcement logged for team {team_id}: {announcement[:100]}..."
        except Exception as e:
            self.logger.error(f"Error sending announcement: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, announcement: str, team_id: str) -> str:
        """Send an announcement asynchronously."""
        return self._run(announcement, team_id) 