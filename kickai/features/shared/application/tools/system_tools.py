#!/usr/bin/env python3
"""
System Tools - Clean Architecture Application Layer

This module provides CrewAI tools for system functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators) are confined to this layer.
"""

from typing import Dict, Any
from crewai.tools import tool
from loguru import logger

from kickai.features.shared.domain.services.system_service import SystemService
from kickai.utils.tool_validation import create_tool_response


@tool("check_system_ping")
async def check_system_ping(telegram_id: str, team_id: str, username: str, chat_type: str) -> str:
    """
    Check system connectivity and response time with ping test.
    
    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: Telegram ID of the requesting user (string)
        team_id: Team ID
        username: Username of the requesting user
        chat_type: Chat type context
    
    Returns:
        Formatted pong response string ready for display
    """
    try:
        # Simple type conversion
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"
        
        # Basic validation
        if telegram_id_int <= 0:
            return "❌ Valid telegram_id is required"
        
        if not team_id or not username or not chat_type:
            return "❌ All parameters are required"
        
        logger.info(f"🏓 Ping request from user {username} ({telegram_id_int}) in team {team_id}")
        
        # Get domain service (pure business logic)
        system_service = SystemService()
        
        # Execute pure business logic
        ping_result = system_service.perform_ping()
        formatted_response = system_service.format_ping_response(ping_result)
        
        logger.info(f"✅ Ping response sent at {ping_result.response_time}")
        
        # Return formatted string directly (like help tools do)
        return formatted_response
        
    except Exception as e:
        logger.error(f"❌ Error in ping tool: {e}")
        return f"❌ Ping failed: {str(e)}"


@tool("check_system_version")
async def check_system_version(telegram_id: str, team_id: str, username: str, chat_type: str) -> str:
    """
    Check system version and detailed information.
    
    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: Telegram ID of the requesting user (string)
        team_id: Team ID
        username: Username of the requesting user
        chat_type: Chat type context
    
    Returns:
        Formatted version information string ready for display
    """
    try:
        # Simple type conversion
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"
        
        # Basic validation
        if telegram_id_int <= 0:
            return "❌ Valid telegram_id is required"
        
        if not team_id or not username or not chat_type:
            return "❌ All parameters are required"
        
        logger.info(f"📱 Version info request from user {username} ({telegram_id_int}) in team {team_id}")
        
        # Get domain service (pure business logic)
        system_service = SystemService()
        
        # Execute pure business logic
        system_info = system_service.get_system_info()
        formatted_response = system_service.format_version_response(system_info)
        
        logger.info(f"✅ Version info sent at {system_info.timestamp}")
        
        # Return formatted string directly (like help tools do)
        return formatted_response
        
    except Exception as e:
        logger.error(f"❌ Error in version tool: {e}")
        return f"❌ Version check failed: {str(e)}"