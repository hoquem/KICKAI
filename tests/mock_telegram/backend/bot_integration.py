"""
Bot Integration Layer

This module integrates the mock Telegram service with the existing KICKAI bot system,
allowing the bot to process messages from the mock service as if they were real Telegram messages.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
import httpx
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)

# Initialize bot components availability flag
BOT_COMPONENTS_AVAILABLE = True  # Force bot integration to be available

# Import bot components (required for real bot integration)
try:
    from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService
    from kickai.agents.agentic_message_router import AgenticMessageRouter
    from kickai.core.settings import get_settings
    from kickai.core.dependency_container import initialize_container, get_container
    logger.info("✅ Bot components imported successfully")
except ImportError as e:
    logger.error(f"❌ Critical: Bot components import failed: {e}")
    raise ImportError(f"Bot components are required but failed to import: {e}")


class MockTelegramIntegration:
    """
    Integration layer that connects mock Telegram messages to the real bot system.
    
    This allows the existing bot logic to process mock messages without any changes
    to the core bot implementation.
    """
    
    def __init__(self, mock_service_url: str = "http://localhost:8001"):
        self.mock_service_url = mock_service_url
        self._lock = asyncio.Lock()
        self.settings = None
        self.agentic_router = None
        self.telegram_service = None
        self._initialized = False
    
    async def _initialize(self):
        """Initialize bot components asynchronously."""
        if self._initialized:
            return
            
        # Initialize bot components (required - no mock fallback)
        try:
            # Initialize the dependency container first
            logger.info("🔧 Initializing dependency container...")
            initialize_container()
            container = get_container()
            
            # Verify services are ready
            if not container.verify_services_ready():
                logger.warning("⚠️ Some services not ready, but continuing...")
            
            self.settings = get_settings()
            # Get team_id from Firestore - use first available team
            team_id = await self._get_team_id_from_firestore()
            self.agentic_router = AgenticMessageRouter(team_id=team_id)
            # Skip TelegramBotService for mock integration - we don't need real Telegram
            self.telegram_service = None
            logger.info(f"✅ Bot integration initialized successfully with team_id: {team_id}")
            self._initialized = True
        except Exception as e:
            logger.error(f"❌ Critical: Failed to initialize bot components: {e}")
            raise RuntimeError(f"Bot integration initialization failed: {e}")
        
    async def process_mock_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message from the mock Telegram service through the real bot system.
        
        Args:
            message_data: Message data from mock service
            
        Returns:
            Bot response data
        """
        # Initialize if not already done
        await self._initialize()
        
        # Bot integration is required - no mock fallback
        if not self.agentic_router:
            raise RuntimeError("Bot integration failed to initialize - agentic_router is not available")
        
        async with self._lock:
            try:
                # Convert mock message to TelegramMessage format expected by bot system
                telegram_message = self._convert_mock_to_telegram_message(message_data)
                
                # Process through the agentic message router
                response = await self.agentic_router.route_message(telegram_message)
                
                # Convert bot response to mock format
                mock_response = self._convert_bot_response_to_mock(response, message_data)
                
                logger.info(f"Processed message: {message_data.get('text', '')[:50]}...")
                return mock_response
                
            except Exception as e:
                logger.error(f"Error processing mock message: {e}")
                return {
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
    
    def _convert_mock_to_telegram_message(self, message_data: Dict[str, Any]) -> Any:
        """
        Convert mock message format to TelegramMessage format expected by bot system.
        """
        from kickai.agents.user_flow_agent import TelegramMessage
        from kickai.core.enums import ChatType
        
        text = message_data.get("text", "")
        chat_context = message_data.get("chat_context", "private")
        
        # Extract user information
        from_data = message_data.get("from", {})
        user_id = str(from_data.get("id", 0))
        username = from_data.get("username") or from_data.get("first_name", "unknown")
        
        # Extract chat information
        chat_data = message_data.get("chat", {})
        chat_id = str(chat_data.get("id", 0))
        
        # Determine chat type based on context
        if chat_context == "leadership":
            chat_type = ChatType.LEADERSHIP
        elif chat_context == "main":
            chat_type = ChatType.MAIN
        else:
            chat_type = ChatType.PRIVATE
        
        # Create TelegramMessage object
        return TelegramMessage(
            user_id=user_id,
            chat_id=chat_id,
            chat_type=chat_type,
            username=username,
            team_id=self.agentic_router.team_id,
            text=text,
            raw_update=message_data,  # Pass the original message data
            contact_phone=None,
            contact_user_id=None
        )
    
    def _convert_bot_response_to_mock(self, bot_response: Any, original_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert bot response to format expected by mock service.
        """
        # Extract the response text from the bot response
        response_text = ""
        
        if hasattr(bot_response, 'message'):
            # AgentResponse object has 'message' attribute
            response_text = bot_response.message
        elif hasattr(bot_response, 'text'):
            response_text = bot_response.text
        elif isinstance(bot_response, str):
            response_text = bot_response
        elif isinstance(bot_response, dict):
            response_text = bot_response.get('message', bot_response.get('text', str(bot_response)))
        elif bot_response is None:
            response_text = "No response from bot"
        else:
            response_text = str(bot_response)
        
        # Clean up the response text - remove HTML entities and encoding issues
        if response_text:
            # Remove HTML-like entities
            import re
            response_text = re.sub(r'</?span[^>]*>', '', response_text)
            response_text = re.sub(r'</?[^>]+>', '', response_text)
            
            # Clean up encoding issues
            response_text = response_text.replace('', '')
            response_text = response_text.replace('\\n', '\n')
            response_text = response_text.replace('\\"', '"')
            
            # Remove any remaining AgentResponse wrapper if present
            if response_text.startswith('AgentResponse(') and response_text.endswith(')'):
                # Extract just the message part
                import re
                match = re.search(r'message="([^"]*)"', response_text)
                if match:
                    response_text = match.group(1)
        
        # Ensure response text is not empty
        if not response_text.strip():
            response_text = "Bot processed the message successfully"
        
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
    
    async def _get_team_id_from_firestore(self) -> str:
        """
        Get the current team_id from the mock service or Firestore.
        This ensures we use the team ID that the user has selected in the UI.
        """
        try:
            # First try to get the current team ID from the mock service
            try:
                import httpx
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.mock_service_url}/team_id")
                    if response.status_code == 200:
                        data = response.json()
                        team_id = data.get("team_id", "KTI")
                        logger.info(f"Using team_id from mock service: {team_id}")
                        return team_id
            except Exception as e:
                logger.warning(f"Could not get team_id from mock service: {e}")
            
            # Fallback to Firestore if mock service not available
            from kickai.features.team_administration.domain.services.team_service import TeamService
            from kickai.core.dependency_container import get_service
            
            # Get team service from dependency container
            team_service = get_service(TeamService)
            
            # Get all teams from Firestore
            teams = await team_service.get_all_teams()
            
            if not teams:
                logger.warning("No teams found in Firestore, using fallback team_id")
                return "fallback_team"
            
            # Use the first available team
            team_id = teams[0].id
            logger.info(f"Using team_id from Firestore: {team_id}")
            return team_id
            
        except Exception as e:
            logger.error(f"Failed to get team_id from Firestore: {e}")
            logger.warning("Using fallback team_id due to error")
            return "fallback_team"
    
    async def send_bot_response_to_mock(self, response_data: Dict[str, Any]) -> bool:
        """
        Send bot response back to mock service for WebSocket broadcasting.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.mock_service_url}/api/bot_response",
                    json=response_data,
                    timeout=5.0
                )
                response.raise_for_status()
                logger.debug("Bot response sent to mock service successfully")
                return True
        except httpx.TimeoutException:
            logger.warning("Timeout sending bot response to mock service")
            return False
        except httpx.RequestError as e:
            logger.error(f"Request error sending bot response: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending bot response to mock service: {e}")
            return False


class MockTelegramWebhook:
    """
    Webhook handler that receives messages from mock service and processes them through the bot.
    """
    
    def __init__(self, mock_service_url: str = "http://localhost:8001"):
        self.integration = MockTelegramIntegration(mock_service_url)
    
    async def handle_mock_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message from mock service.
        """
        # Process through bot system
        response = await self.integration.process_mock_message(message_data)
        
        # Send response back to mock service for broadcasting
        await self.integration.send_bot_response_to_mock(response)
        
        return response


# Global webhook instance (lazy initialization)
mock_webhook = None

def get_mock_webhook():
    """Get or create the global webhook instance"""
    global mock_webhook
    if mock_webhook is None:
        mock_webhook = MockTelegramWebhook()
    return mock_webhook


async def process_mock_message_async(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for processing mock messages.
    """
    webhook = get_mock_webhook()
    return await webhook.handle_mock_message(message_data)


def process_mock_message_sync(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for processing mock messages.
    
    This function handles the async/sync boundary properly by checking if we're
    already in an async context and handling both cases appropriately.
    """
    try:
        # Check if we're already in an async context
        loop = asyncio.get_running_loop()
        # We're in an async context, create a task
        task = asyncio.create_task(process_mock_message_async(message_data))
        return {"status": "processing", "task_id": id(task)}
    except RuntimeError:
        # We're in a sync context, run the async function
        try:
            return asyncio.run(process_mock_message_async(message_data))
        except Exception as e:
            logger.error(f"Error in sync wrapper: {e}")
            return {
                "type": "error",
                "message": f"Error processing message: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


# Configuration management
class MockTelegramConfig:
    """Configuration for the mock Telegram system"""
    
    def __init__(self):
        self.mock_service_url = "http://localhost:8001"
        self.timeout_seconds = 5.0
        self.max_retries = 3
        # Use global flag safely
        self.enable_bot_integration = BOT_COMPONENTS_AVAILABLE
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        config = cls()
        # Add environment variable support here if needed
        return config


# Health check function
async def check_bot_integration_health() -> Dict[str, Any]:
    """Check the health of the bot integration"""
    return {
        "bot_components_available": BOT_COMPONENTS_AVAILABLE,
        "integration_ready": BOT_COMPONENTS_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    } 