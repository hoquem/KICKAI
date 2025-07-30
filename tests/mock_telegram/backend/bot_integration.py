"""
Bot Integration Layer

This module integrates the mock Telegram service with the existing KICKAI bot system,
allowing the bot to process messages from the mock service as if they were real Telegram messages.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService
from kickai.agents.agentic_message_router import AgenticMessageRouter
from kickai.core.settings import get_settings

logger = logging.getLogger(__name__)


class MockTelegramIntegration:
    """
    Integration layer that connects mock Telegram messages to the real bot system.
    
    This allows the existing bot logic to process mock messages without any changes
    to the core bot implementation.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.agentic_router = AgenticMessageRouter()
        self.telegram_service = TelegramBotService()
        self.mock_service_url = "http://localhost:8001"
        
        # Track bot responses to send back to mock service
        self.response_queue = asyncio.Queue()
        
    async def process_mock_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message from the mock Telegram service through the real bot system.
        
        Args:
            message_data: Message data from mock service
            
        Returns:
            Bot response data
        """
        try:
            # Convert mock message to format expected by bot system
            telegram_update = self._convert_mock_to_telegram_update(message_data)
            
            # Process through the agentic message router
            response = await self.agentic_router.route_message(telegram_update)
            
            # Convert bot response to mock format
            mock_response = self._convert_bot_response_to_mock(response, message_data)
            
            return mock_response
            
        except Exception as e:
            logger.error(f"Error processing mock message: {e}")
            return {
                "type": "error",
                "message": f"Error processing message: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _convert_mock_to_telegram_update(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert mock message format to Telegram update format expected by bot system.
        """
        return {
            "update_id": message_data.get("message_id", 0),
            "message": {
                "message_id": message_data.get("message_id", 0),
                "from": message_data.get("from", {}),
                "chat": message_data.get("chat", {}),
                "date": message_data.get("date", int(datetime.now().timestamp())),
                "text": message_data.get("text", ""),
                "entities": [] if not message_data.get("text", "").startswith("/") else [
                    {
                        "type": "bot_command",
                        "offset": 0,
                        "length": len(message_data.get("text", "").split()[0])
                    }
                ]
            }
        }
    
    def _convert_bot_response_to_mock(self, bot_response: Any, original_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert bot response to format expected by mock service.
        """
        # Extract the response text from the bot response
        response_text = ""
        if hasattr(bot_response, 'text'):
            response_text = bot_response.text
        elif isinstance(bot_response, str):
            response_text = bot_response
        elif isinstance(bot_response, dict):
            response_text = bot_response.get('text', str(bot_response))
        else:
            response_text = str(bot_response)
        
        return {
            "type": "bot_response",
            "message": {
                "message_id": original_message.get("message_id", 0) + 1000,  # Offset to avoid conflicts
                "from": {
                    "id": 0,  # Bot ID
                    "username": "kickai_bot",
                    "first_name": "KickAI",
                    "is_bot": True
                },
                "chat": original_message.get("chat", {}),
                "date": int(datetime.now().timestamp()),
                "text": response_text
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def send_bot_response_to_mock(self, response_data: Dict[str, Any]):
        """
        Send bot response back to mock service for WebSocket broadcasting.
        """
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.mock_service_url}/bot_response",
                    json=response_data,
                    timeout=5.0
                )
        except Exception as e:
            logger.error(f"Error sending bot response to mock service: {e}")


class MockTelegramWebhook:
    """
    Webhook handler that receives messages from mock service and processes them through the bot.
    """
    
    def __init__(self):
        self.integration = MockTelegramIntegration()
    
    async def handle_mock_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message from mock service.
        """
        # Process through bot system
        response = await self.integration.process_mock_message(message_data)
        
        # Send response back to mock service for broadcasting
        await self.integration.send_bot_response_to_mock(response)
        
        return response


# Global webhook instance
mock_webhook = MockTelegramWebhook()


async def process_mock_message_async(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for processing mock messages.
    """
    return await mock_webhook.handle_mock_message(message_data)


def process_mock_message_sync(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for processing mock messages.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If we're already in an async context, create a new task
        task = asyncio.create_task(process_mock_message_async(message_data))
        return {"status": "processing", "task_id": id(task)}
    else:
        # If we're in a sync context, run the async function
        return asyncio.run(process_mock_message_async(message_data)) 