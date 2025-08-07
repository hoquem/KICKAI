"""
Real Bot Integration for Mock Telegram Tester

This module provides integration between the mock Telegram service
and the real KICKAI CrewAI system using Groq LLM.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import real bot integration components
try:
    from kickai.agents.user_flow_agent import TelegramMessage, AgentResponse
    from kickai.agents.agentic_message_router import AgenticMessageRouter
    from kickai.core.enums import ChatType
    BOT_INTEGRATION_AVAILABLE = True
    logger.info("✅ Real bot components imported successfully")
except ImportError as e:
    BOT_INTEGRATION_AVAILABLE = False
    logger.warning(f"❌ Real bot integration not available: {e}")


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
        return _get_fallback_response(message_data, "Real bot integration not available")
    
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
        telegram_message = _create_telegram_message(message_data)
        
        # Get team ID (use default for testing)
        team_id = "KTI"
        
        # Create real AgenticMessageRouter with Groq LLM
        router = AgenticMessageRouter(team_id=team_id)
        
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
        
        logger.info(f"✅ Real CrewAI response created for {username}: {response_text[:100]}...")
        
        return {
            "type": "text",
            "text": response_text,
            "chat_id": chat_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "source": "real_crewai_groq"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in real CrewAI processing: {e}")
        return _get_fallback_response(message_data, f"Real CrewAI processing failed: {str(e)}")


def _create_telegram_message(message_data: Dict[str, Any]) -> TelegramMessage:
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
    
    # Create TelegramMessage for real agent processing
    return TelegramMessage(
        telegram_id=str(user_id),  # Use telegram_id as requested
        chat_id=str(chat_id),
        chat_type=chat_type,
        username=username,
        team_id="KTI",  # Default team for testing
        text=text,
        raw_update=message_data  # Pass raw data for context
    )


def _get_fallback_response(message_data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
    """Get fallback response when real agent processing fails."""
    return {
        "type": "text",
        "text": f"🤖 Bot Response\n\nYou said: \"{message_data.get('text', '')}\"\n\n{error_msg}\n\nThis is a fallback response due to system issues.",
        "chat_id": message_data.get("chat", {}).get("id"),
        "user_id": message_data.get("from", {}).get("id"),
        "timestamp": datetime.now().isoformat(),
        "source": "fallback"
    }


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
        return _get_fallback_response(message_data, f"Sync processing failed: {str(e)}")


async def check_bot_integration_health() -> Dict[str, Any]:
    """Check the health of the real bot integration with Groq LLM."""
    try:
        # Test basic imports
        from kickai.core.dependency_container import get_container
        from kickai.agents.agentic_message_router import AgenticMessageRouter
        
        # Check container
        container = get_container()
        container_status = "healthy" if container._initialized else "not_initialized"
        
        # Test router creation
        router = AgenticMessageRouter(team_id="KTI")
        router_status = "healthy"
        
        # Test LLM configuration
        from kickai.core.config import get_config
        config = get_config()
        llm_provider = config.ai_provider
        llm_model = config.ai_model_name
        
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