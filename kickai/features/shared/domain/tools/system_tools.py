#!/usr/bin/env python3
"""
System Tools - Basic System Operations

This module provides basic system tools that don't require external services.
"""

from datetime import datetime

from crewai.tools import tool
from loguru import logger

from kickai.core.constants import BOT_VERSION
from kickai.utils.json_helper import json_error, json_response


@tool("ping")
def ping() -> str:
    """
    Simple ping test to verify bot connectivity and response time.

    :return: JSON response with pong status and timestamp
    :rtype: str
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            'status': 'pong',
            'timestamp': timestamp,
            'bot_version': BOT_VERSION,
            'system_status': 'Operational'
        }

        ui_format = f"🏓 Pong!\n\n⏰ Response Time: {timestamp}\n🤖 Bot Version: {BOT_VERSION}\n✅ System Status: Operational"

        logger.info(f"✅ Ping response sent at {timestamp}")
        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"❌ Error in ping tool: {e}")
        return json_error(f"Ping failed: {e!s}", "Operation failed")

@tool("version")
def version() -> str:
    """
    Get bot version and system information.

    :return: JSON response with version information and system details
    :rtype: str
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            'bot_version': BOT_VERSION,
            'timestamp': timestamp,
            'architecture': 'CrewAI Agentic System',
            'status': 'Production Ready'
        }

        ui_format = f"📱 KICKAI Bot Information\n\n🤖 Version: {BOT_VERSION}\n⏰ Current Time: {timestamp}\n🏗️ Architecture: CrewAI Agentic System\n✅ Status: Production Ready"

        logger.info(f"✅ Version info requested at {timestamp}")
        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"❌ Error in version tool: {e}")
        return json_error(f"Version check failed: {e!s}", "Operation failed")
