"""
Real Bot Integration for Mock Telegram Tester

This module provides integration between the mock Telegram service
and the real KICKAI CrewAI system using Groq LLM.
"""

# Set required environment variables BEFORE any imports
import os
os.environ.setdefault("KICKAI_INVITE_SECRET_KEY", "test_secret_key_for_debugging_only_32_chars_long")

# Standard library imports
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Constants
MOCK_MAIN_CHAT_ID = "2001"
MOCK_LEADERSHIP_CHAT_ID = "2002"
DEFAULT_TEAM_ID = "KTI"
TEAM_LIMIT = 1

logger = logging.getLogger(__name__)

# Import real bot integration components
try:
    # Local imports
    from kickai.core.types import AgentResponse, TelegramMessage
    from kickai.agents.telegram_message_adapter import TelegramMessageAdapter
    from kickai.core.enums import ChatType
    BOT_INTEGRATION_AVAILABLE = True
    logger.info("✅ Real bot components imported successfully")
except ImportError as e:
    BOT_INTEGRATION_AVAILABLE = False
    logger.warning(f"❌ Real bot integration not available: {e}")
    
    # Create fallback types for when real bot is not available
    from dataclasses import dataclass
    
    @dataclass
    class AgentResponse:
        success: bool
        message: str
        error: Optional[str] = None
        agent_type: Optional[str] = None
        confidence: float = 1.0
        metadata: Optional[Dict[str, Any]] = None
        needs_contact_button: bool = False
    
    @dataclass
    class TelegramMessage:
        telegram_id: int
        text: str
        chat_id: str
        chat_type: Any  # Accept both str and ChatType enum for fallback compatibility
        team_id: Optional[str] = None
        username: Optional[str] = None
        first_name: Optional[str] = None
        last_name: Optional[str] = None
        raw_update: Optional[Any] = None
        contact_phone: Optional[str] = None
        contact_user_id: Optional[int] = None
    
    class ChatType:
        MAIN = "main"
        LEADERSHIP = "leadership"
        PRIVATE = "private"


async def process_mock_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a message through the real KICKAI CrewAI system with Groq LLM.
    
    This function:
    1. Ensures dependency container is initialized
    2. Converts mock message to TelegramMessage format
    3. Routes through real TelegramMessageAdapter with Groq LLM
    4. Returns formatted response from real agents
    
    Args:
        message_data: Message data from mock service
        
    Returns:
        Bot response data from real CrewAI agents
    """
    try:
        # Handle case when bot integration is not available
        if not BOT_INTEGRATION_AVAILABLE:
            return _create_fallback_response(message_data)
        
        # Initialize dependencies
        await _ensure_dependencies_initialized()
        
        # Process message through real system
        telegram_message = await _create_telegram_message(message_data)
        team_id = await _get_available_team_id()
        router = await _create_router(team_id)
        response = await router.process_message(telegram_message)
        
        # Format and return response
        formatted_text = await _format_response(response)
        return _create_success_response(formatted_text, response)
        
    except Exception as e:
        logger.error(f"❌ Error in process_mock_message: {e}")
        return _create_error_response(str(e))


async def _create_fallback_response(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create fallback response when bot integration is not available.
    
    Args:
        message_data: Message data from mock service
        
    Returns:
        Fallback response data
    """
    text = message_data.get("text", "")
    user_id = message_data.get("from", {}).get("id", "unknown")
    
    logger.warning(f"🤖 Bot integration not available - providing fallback response for: {text}")
    
    # Simple fallback responses
    if text.lower().startswith("/help"):
        return {
            "success": True,
            "message": "🤖 **KICKAI Bot Help**\n\nAvailable commands:\n• /help - Show this help message\n• /myinfo - Show your information\n• /list - List players/members\n• /status [phone] - Check status\n\nBot integration is currently in development mode.",
            "agent_type": "help_assistant",
            "confidence": 1.0
        }
    elif text.lower().startswith("/myinfo"):
        return {
            "success": True,
            "message": f"🤖 **Your Information**\n\nUser ID: {user_id}\nStatus: Active\nRole: Test User\n\nBot integration is currently in development mode.",
            "agent_type": "message_processor",
            "confidence": 1.0
        }
    else:
        return {
            "success": True,
            "message": f"🤖 **Bot Response**\n\nYou said: {text}\n\nBot integration is currently in development mode. This is a fallback response.",
            "agent_type": "message_processor",
            "confidence": 1.0
        }


async def _ensure_dependencies_initialized() -> None:
    """
    Ensure dependency container is initialized.
    
    Raises:
        Exception: When initialization fails
    """
    from kickai.core.dependency_container import initialize_container, get_container
    
    # Try to get existing container
    container = get_container()
    if not container._initialized:
        logger.info("🔧 Initializing dependency container...")
        await initialize_container()


async def _create_router(team_id: str) -> TelegramMessageAdapter:
    """
    Create and configure TelegramMessageAdapter.
    
    Args:
        team_id: Team ID for the router
        
    Returns:
        Configured TelegramMessageAdapter instance
        
    Raises:
        Exception: When router creation fails
    """
    logger.info(f"🔧 Creating TelegramMessageAdapter with team_id={team_id}")
    
    router = TelegramMessageAdapter(team_id)
    router.set_chat_ids(main_chat_id=MOCK_MAIN_CHAT_ID, leadership_chat_id=MOCK_LEADERSHIP_CHAT_ID)
    logger.info("✅ TelegramMessageAdapter created successfully")
    
    return router


async def _format_response(response: Any) -> str:
    """
    Extract response text directly.
    
    Args:
        response: Response from agent
        
    Returns:
        Response text
    """
    # Extract response content
    if hasattr(response, 'content'):
        response_text = response.content
    elif hasattr(response, 'message'):
        response_text = response.message
    else:
        response_text = str(response)
    
    logger.info(f"🔄 Response text: {len(response_text)} chars")
    return response_text


def _create_success_response(formatted_text: str, response: Any) -> Dict[str, Any]:
    """
    Create success response.
    
    Args:
        formatted_text: Formatted response text
        response: Original response object
        
    Returns:
        Success response data
    """
    return {
        "success": True,
        "message": formatted_text,
        "agent_type": getattr(response, 'agent_type', 'unknown'),
        "confidence": getattr(response, 'confidence', 1.0),
        "tools_used": getattr(response, 'tools_used', []),
        "token_count": getattr(response, 'token_count', 0)
    }


def _create_error_response(error_message: str) -> Dict[str, Any]:
    """
    Create error response.
    
    Args:
        error_message: Error message
        
    Returns:
        Error response data
    """
    return {
        "success": False,
        "message": f"❌ Error processing message: {error_message}",
        "error": error_message,
        "agent_type": "error_handler",
        "confidence": 0.0
    }


async def _get_available_team_id() -> str:
    """Get the first available team ID from Firestore for testing."""
    try:
        from kickai.database.firebase_client import get_firebase_client
        
        client = get_firebase_client()
        db = client.client
        
        # Get the first available team from kickai_teams collection
        teams_ref = db.collection('kickai_teams')
        teams = teams_ref.limit(TEAM_LIMIT).stream()
        
        for team in teams:
            team_id = team.id
            logger.info(f"🎯 Using dynamic team_id: {team_id}")
            return team_id
        
        # Fallback to KTI if no teams found
        logger.warning(f"⚠️ No teams found in Firestore, using fallback team_id: {DEFAULT_TEAM_ID}")
        return DEFAULT_TEAM_ID
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to get team_id from Firestore: {e}, using fallback: {DEFAULT_TEAM_ID}")
        return DEFAULT_TEAM_ID


async def _create_telegram_message(message_data: Dict[str, Any]) -> TelegramMessage:
    """Convert mock message data to TelegramMessage format for real agent processing."""
    
    # Extract message components - handle both "from" and "user" fields
    text = message_data.get("text", "")
    
    # Try "user" field first (our test format), then "from" field (Telegram format)
    user_data = message_data.get("user") or message_data.get("from", {})
    user_id = user_data.get("id")
    username = user_data.get("username", f"user_{user_id}")
    
    # Try "chat_id" field first, then "chat" object
    chat_id = message_data.get("chat_id")
    if not chat_id:
        chat_data = message_data.get("chat", {})
        chat_id = chat_data.get("id")
    
    chat_context = message_data.get("chat_context", "main")
    
    # Determine chat type
    if chat_context == "leadership":
        chat_type = ChatType.LEADERSHIP
    elif chat_context == "main":
        chat_type = ChatType.MAIN
    else:
        chat_type = ChatType.PRIVATE
    
    # Get dynamic team ID
    team_id = await _get_available_team_id()
    
    # Create TelegramMessage for real agent processing
    return TelegramMessage(
        telegram_id=user_id,  # Keep as integer - Telegram's native type
        chat_id=str(chat_id),
        chat_type=chat_type,
        username=username,
        team_id=team_id,  # Dynamic team ID
        text=text,
        raw_update=message_data  # Pass raw data for context
    )


# Fallback response removed - all errors should propagate properly





async def check_bot_integration_health() -> Dict[str, Any]:
    """Check the health of the real bot integration with Groq LLM."""
    try:
        # Test basic imports
        from kickai.core.dependency_container import get_container
        from kickai.agents.telegram_message_adapter import TelegramMessageAdapter
        
        # Check container
        container = get_container()
        container_status = "healthy" if container._initialized else "not_initialized"
        
        # Test router creation with dynamic team_id
        team_id = await _get_available_team_id()
        router = TelegramMessageAdapter(team_id)
        router_status = "healthy"
        
        # Test LLM configuration
        from kickai.core.config import get_settings
        config = get_settings()
        llm_provider = config.ai_provider
        llm_model = config.ai_model_simple or config.ai_model_advanced or config.ai_model_name
        
        return {
            "status": "healthy",
            "components": {
                "dependency_container": container_status,
                "agentic_message_router": router_status,
                "llm_provider": llm_provider,
                "llm_model": llm_model
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Bot integration health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 