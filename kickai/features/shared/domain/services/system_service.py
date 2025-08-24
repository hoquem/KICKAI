#!/usr/bin/env python3
"""
System Service - Pure Business Logic

This service provides system-related business logic without any framework dependencies.
It handles system information, health checks, and basic operational data.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from kickai.core.constants import BOT_VERSION


@dataclass
class SystemInfo:
    """System information structure."""
    version: str
    timestamp: str
    architecture: str
    status: str


@dataclass
class PingResult:
    """Ping result structure."""
    response_time: str
    version: str
    status: str
    success: bool


class SystemService:
    """Pure domain service for system functionality."""

    def __init__(self):
        pass

    def get_system_info(self) -> SystemInfo:
        """
        Get comprehensive system information.
        
        Returns:
            SystemInfo with current system details
        """
        return SystemInfo(
            version=BOT_VERSION,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            architecture="CrewAI Agentic System",
            status="Production Ready"
        )

    def perform_ping(self) -> PingResult:
        """
        Perform a system ping check.
        
        Returns:
            PingResult with ping details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return PingResult(
            response_time=timestamp,
            version=BOT_VERSION,
            status="Operational",
            success=True
        )

    def format_ping_response(self, ping_result: PingResult) -> str:
        """
        Format ping result into user-friendly message.
        
        Args:
            ping_result: The ping result to format
            
        Returns:
            Formatted ping message
        """
        return (
            f"🏓 Pong!\n\n"
            f"⏰ Response Time: {ping_result.response_time}\n"
            f"🤖 Bot Version: {ping_result.version}\n"
            f"✅ System Status: {ping_result.status}"
        )

    def format_version_response(self, system_info: SystemInfo) -> str:
        """
        Format system info into user-friendly message.
        
        Args:
            system_info: The system info to format
            
        Returns:
            Formatted version message
        """
        return (
            f"📱 KICKAI Bot Information\n\n"
            f"🤖 Version: {system_info.version}\n"
            f"⏰ Current Time: {system_info.timestamp}\n"
            f"🏗️ Architecture: {system_info.architecture}\n"
            f"✅ Status: {system_info.status}"
        )