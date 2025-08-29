#!/usr/bin/env python3
"""
System Tools - Basic System Operations

This module provides basic system tools that don't require external services.
"""

from datetime import datetime
from loguru import logger

from crewai.tools import tool
from kickai.utils.tool_validation import create_tool_response
from kickai.core.constants import BOT_VERSION


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def ping(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Simple ping test to verify bot connectivity and response time.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        username: Username of the requesting user
        chat_type: Chat type context
    
    Returns:
        Pong response with timestamp and bot version
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f"🏓 Pong!\n\n⏰ Response Time: {timestamp}\n🤖 Bot Version: {BOT_VERSION}\n✅ System Status: Operational"
        
        logger.info(f"✅ Ping response sent at {timestamp}")
        return create_tool_response(True, "Operation completed successfully", data=response)
        
    except Exception as e:
        logger.error(f"❌ Error in ping tool: {e}")
        return create_tool_response(False, f"Ping failed: {str(e)}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def version(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get bot version and system information.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        username: Username of the requesting user
        chat_type: Chat type context
    
    Returns:
        Version information and system details
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f"📱 KICKAI Bot Information\n\n🤖 Version: {BOT_VERSION}\n⏰ Current Time: {timestamp}\n🏗️ Architecture: CrewAI Agentic System\n✅ Status: Production Ready"
        
        logger.info(f"✅ Version info requested at {timestamp}")
        return create_tool_response(True, "Operation completed successfully", data=response)
        
    except Exception as e:
        logger.error(f"❌ Error in version tool: {e}")
        return create_tool_response(False, f"Version check failed: {str(e)}")
