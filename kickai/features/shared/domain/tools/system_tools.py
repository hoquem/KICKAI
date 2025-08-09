#!/usr/bin/env python3
"""
System Tools - Basic System Operations

This module provides basic system tools that don't require external services.
"""

from datetime import datetime
from loguru import logger

from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import format_tool_success
from kickai.core.constants import BOT_VERSION


@tool("ping")
def ping() -> str:
    """
    Simple ping test to verify bot connectivity and response time.
    
    Returns:
        Pong response with timestamp and bot version
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f"🏓 Pong!\n\n⏰ Response Time: {timestamp}\n🤖 Bot Version: {BOT_VERSION}\n✅ System Status: Operational"
        
        logger.info(f"✅ Ping response sent at {timestamp}")
        return format_tool_success(response)
        
    except Exception as e:
        logger.error(f"❌ Error in ping tool: {e}")
        return f"❌ Ping failed: {str(e)}"


@tool("version")
def version() -> str:
    """
    Get bot version and system information.
    
    Returns:
        Version information and system details
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f"📱 KICKAI Bot Information\n\n🤖 Version: {BOT_VERSION}\n⏰ Current Time: {timestamp}\n🏗️ Architecture: CrewAI Agentic System\n✅ Status: Production Ready"
        
        logger.info(f"✅ Version info requested at {timestamp}")
        return format_tool_success(response)
        
    except Exception as e:
        logger.error(f"❌ Error in version tool: {e}")
        return f"❌ Version check failed: {str(e)}"
