"""
Simple Bot Integration for Mock Telegram Tester

This module provides clean, simple integration between the mock Telegram service
and the real KICKAI CrewAI system using Groq LLM.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import bot integration (optional - will be skipped if not available)
try:
    from kickai.agents.user_flow_agent import TelegramMessage, AgentResponse
    from kickai.agents.agentic_message_router import AgenticMessageRouter
    from kickai.core.enums import ChatType
    BOT_INTEGRATION_AVAILABLE = True
    logger.info("✅ Bot components imported successfully")
except ImportError as e:
    BOT_INTEGRATION_AVAILABLE = False
    logger.warning(f"❌ Bot integration not available: {e}")


async def process_mock_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a message through the real KICKAI CrewAI system.
    
    This is a simple, clean async function that:
    1. Converts mock message to TelegramMessage format
    2. Routes through AgenticMessageRouter
    3. Returns formatted response
    
    Args:
        message_data: Message data from mock service
        
    Returns:
        Bot response data
    """
    if not BOT_INTEGRATION_AVAILABLE:
        return _get_fallback_response(message_data, "Bot integration not available")
    
    try:
        # Extract message information
        text = message_data.get("text", "")
        user_id = message_data.get("from", {}).get("id")
        chat_id = message_data.get("chat", {}).get("id")
        chat_context = message_data.get("chat_context", "main")
        
        logger.info(f"🚀 Processing message through REAL CrewAI system: {text} from user {user_id} in {chat_context} chat")
        
        # Convert to TelegramMessage format
        telegram_message = _create_telegram_message(message_data)
        
        # Get team ID (use default for testing)
        team_id = "KTI"
        
        # Initialize router (simple, no complex initialization)
        router = AgenticMessageRouter(team_id=team_id)
        
        # Route message through CrewAI system
        logger.info(f"🔄 Routing message through CrewAI agents: {text}")
        response = await router.route_message(telegram_message)
        
        logger.info(f"✅ CrewAI response received: {response.message[:100]}...")
        
        return {
            "type": "text",
            "text": response.message,
            "chat_id": chat_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "source": "real_crewai"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in CrewAI processing: {e}")
        return _get_fallback_response(message_data, f"CrewAI processing failed: {str(e)}")


def _create_telegram_message(message_data: Dict[str, Any]) -> TelegramMessage:
    """Create TelegramMessage from mock message data."""
    text = message_data.get("text", "")
    user_id = message_data.get("from", {}).get("id")
    chat_id = message_data.get("chat", {}).get("id")
    chat_context = message_data.get("chat_context", "main")
    username = message_data.get("from", {}).get("username", f"user_{user_id}")
    
    # Determine chat type
    if chat_context == "leadership":
        chat_type = ChatType.LEADERSHIP
    elif chat_context == "main":
        chat_type = ChatType.MAIN
    else:
        chat_type = ChatType.PRIVATE
    
    return TelegramMessage(
        user_id=str(user_id),
        chat_id=str(chat_id),
        chat_type=chat_type,
        username=username,
        team_id="KTI",  # Default team for testing
        text=text
    )


def _get_fallback_response(message_data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
    """Get fallback response when CrewAI processing fails."""
    text = message_data.get("text", "")
    user_id = message_data.get("from", {}).get("id")
    chat_id = message_data.get("chat", {}).get("id")
    
    return {
        "type": "text",
        "text": f"🤖 **Bot Response**\n\nYou said: \"{text}\"\n\n{error_msg}\n\nThis is a fallback response.",
        "chat_id": chat_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "source": "fallback"
    }


# Legacy sync wrapper for backward compatibility (deprecated)
def process_mock_message_sync(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """DEPRECATED: Use process_mock_message() instead."""
    logger.warning("⚠️ process_mock_message_sync is deprecated, use process_mock_message()")
    import asyncio
    
    try:
        # Simple async execution
        return asyncio.run(process_mock_message(message_data))
    except Exception as e:
        logger.error(f"❌ Error in sync wrapper: {e}")
        return _get_fallback_response(message_data, f"Sync wrapper error: {str(e)}")


# Health check function
async def check_bot_integration_health() -> Dict[str, Any]:
    """Check the health of the bot integration."""
    return {
        "bot_components_available": BOT_INTEGRATION_AVAILABLE,
        "status": "healthy" if BOT_INTEGRATION_AVAILABLE else "unavailable",
        "timestamp": datetime.now().isoformat()
    } 