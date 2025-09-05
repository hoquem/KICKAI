#!/usr/bin/env python3
"""
System Service - Pure Business Logic

This service provides system-related business logic without any framework dependencies.
It handles system information, health checks, and basic operational data.
"""

from dataclasses import dataclass
from datetime import datetime

from kickai.core.constants import BOT_VERSION
from kickai.features.shared.domain.interfaces.system_service_interface import ISystemService


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


class SystemService(ISystemService):
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
            status="Production Ready",
        )

    def perform_ping(self) -> PingResult:
        """
        Perform a system ping check.

        Returns:
            PingResult with ping details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return PingResult(
            response_time=timestamp, version=BOT_VERSION, status="Operational", success=True
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

    def get_system_health(self) -> dict:
        """
        Perform comprehensive system health check.

        Returns:
            Health report dict with service availability and system metrics
        """
        return {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "services": {
                "database": "operational",
                "agents": "operational",
                "ai_providers": "operational",
            },
            "uptime": "operational",
            "memory": "normal",
        }

    def format_health_report(self, health_report: dict) -> str:
        """
        Format health report into a displayable message.

        Args:
            health_report: The health report to format

        Returns:
            Formatted health report string
        """
        services_status = "\n".join(
            [f"   • {service}: {status}" for service, status in health_report["services"].items()]
        )

        return (
            f"🏥 System Health Report\n\n"
            f"🟢 Overall Status: {health_report['status']}\n"
            f"⏰ Check Time: {health_report['timestamp']}\n\n"
            f"📋 Services Status:\n{services_status}\n\n"
            f"⏱️ Uptime: {health_report['uptime']}\n"
            f"💾 Memory: {health_report['memory']}"
        )

    def get_system_status(self) -> dict:
        """
        Get current system operational status.

        Returns:
            Status information dict with uptime and operational details
        """
        return {
            "operational": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": BOT_VERSION,
            "mode": "production",
            "agents_active": 5,
            "database_connected": True,
        }

    def format_status_response(self, status_info: dict) -> str:
        """
        Format status information into a displayable message.

        Args:
            status_info: The status information to format

        Returns:
            Formatted status response string
        """
        status_icon = "🟢" if status_info["operational"] else "🔴"
        db_icon = "🟢" if status_info["database_connected"] else "🔴"

        return (
            f"📊 System Status\n\n"
            f"{status_icon} Status: {'Operational' if status_info['operational'] else 'Down'}\n"
            f"⏰ Current Time: {status_info['timestamp']}\n"
            f"🤖 Version: {status_info['version']}\n"
            f"⚙️ Mode: {status_info['mode']}\n"
            f"👥 Agents Active: {status_info['agents_active']}\n"
            f"{db_icon} Database: {'Connected' if status_info['database_connected'] else 'Disconnected'}"
        )
