"""
Real Bot Integration for Mock Telegram Tester

This module provides integration between the mock Telegram service
and the real KICKAI CrewAI system using Groq LLM.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import real bot integration components
try:
    # Import centralized types
    from kickai.core.types import AgentResponse, TelegramMessage
    from kickai.agents.agentic_message_router import AgenticMessageRouter
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
        chat_type: str
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
    3. Routes through real AgenticMessageRouter with Groq LLM
    4. Returns formatted response from real agents
    
    Args:
        message_data: Message data from mock service
        
    Returns:
        Bot response data from real CrewAI agents
    """
    if not BOT_INTEGRATION_AVAILABLE:
        # Provide fallback response when bot integration is not available
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
    
    try:
        # Ensure dependency container is initialized first
        from kickai.core.dependency_container import initialize_container, get_container
        
        try:
            # Try to get existing container
            container = get_container()
            if not container._initialized:
                logger.info("🔧 Initializing dependency container...")
                initialize_container()
        except Exception:
            logger.info("🔧 Creating new dependency container...")
            initialize_container()
        
        # Extract message information
        text = message_data.get("text", "")
        user_id = message_data.get("from", {}).get("id")
        chat_id = message_data.get("chat", {}).get("id")
        chat_context = message_data.get("chat_context", "main")
        username = message_data.get("from", {}).get("username", f"user_{user_id}")
        
        logger.info(f"🤖 Groq LLM processing: {text} from user {user_id} ({username}) in {chat_context} chat")
        
        # Convert to TelegramMessage format for real agent processing
        telegram_message = await _create_telegram_message(message_data)
        
        # Get team ID dynamically from available teams in Firestore
        team_id = await _get_available_team_id()
        
        # Create real AgenticMessageRouter with Groq LLM
        logger.info(f"🔧 Creating AgenticMessageRouter with team_id={team_id}")
        logger.info(f"🔧 AgenticMessageRouter class: {AgenticMessageRouter}")
        logger.info(f"🔧 AgenticMessageRouter __init__: {AgenticMessageRouter.__init__}")
        
        try:
            router = AgenticMessageRouter(team_id)
            # Set chat IDs for proper chat type determination
            router.set_chat_ids(main_chat_id="2001", leadership_chat_id="2002")
            logger.info("✅ AgenticMessageRouter created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create AgenticMessageRouter: {e}")
            raise
        
        logger.info(f"🔧 Agent selected: AgenticMessageRouter for team {team_id}")
        
        # Route through real CrewAI agents with Groq LLM
        response = await router.route_message(telegram_message)
        
        logger.info(f"🛠️ Tools used: {getattr(response, 'tools_used', 'unknown')}")
        logger.info(f"📊 Token usage: {getattr(response, 'token_count', 'unknown')}")
        
        # Extract response content
        if hasattr(response, 'content'):
            response_text = response.content
        elif hasattr(response, 'message'):
            response_text = response.message
        else:
            response_text = str(response)
        
        return {
            "success": True,
            "message": response_text,
            "agent_type": getattr(response, 'agent_type', 'unknown'),
            "confidence": getattr(response, 'confidence', 1.0),
            "tools_used": getattr(response, 'tools_used', []),
            "token_count": getattr(response, 'token_count', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        return {
            "success": False,
            "message": f"❌ Error processing message: {str(e)}",
            "error": str(e),
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
        teams = teams_ref.limit(1).stream()
        
        for team in teams:
            team_id = team.id
            logger.info(f"🎯 Using dynamic team_id: {team_id}")
            return team_id
        
        # Fallback to KTI if no teams found
        logger.warning("⚠️ No teams found in Firestore, using fallback team_id: KTI")
        return "KTI"
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to get team_id from Firestore: {e}, using fallback: KTI")
        return "KTI"


async def _create_telegram_message(message_data: Dict[str, Any]) -> TelegramMessage:
    """Convert mock message data to TelegramMessage format for real agent processing."""
    
    # Extract message components
    text = message_data.get("text", "")
    user_id = message_data.get("from", {}).get("id")
    username = message_data.get("from", {}).get("username", f"user_{user_id}")
    chat_id = message_data.get("chat", {}).get("id")
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


def process_mock_message_sync(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for async message processing."""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a new task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, process_mock_message(message_data))
                return future.result()
        else:
            return asyncio.run(process_mock_message(message_data))
    except Exception as e:
        logger.error(f"❌ Error in sync message processing: {e}")
        raise


async def check_bot_integration_health() -> Dict[str, Any]:
    """Check the health of the real bot integration with Groq LLM."""
    try:
        # Test basic imports
        from kickai.core.dependency_container import get_container
        from kickai.agents.agentic_message_router import AgenticMessageRouter
        
        # Check container
        container = get_container()
        container_status = "healthy" if container._initialized else "not_initialized"
        
        # Test router creation with dynamic team_id
        team_id = await _get_available_team_id()
        router = AgenticMessageRouter(team_id)
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