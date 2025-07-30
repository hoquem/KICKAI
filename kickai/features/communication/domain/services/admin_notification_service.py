#!/usr/bin/env python3
"""
Admin Notification Service for KICKAI System

This module provides services for sending critical error notifications
and system alerts to administrators and team leadership.
"""

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from loguru import logger

from kickai.core.enums import ChatType
from kickai.features.communication.domain.interfaces.telegram_bot_service_interface import (
    TelegramBotServiceInterface,
)


class AdminNotificationService:
    """Service for sending admin notifications and critical error alerts."""
    
    def __init__(self, bot_service: TelegramBotServiceInterface, team_id: str):
        self.bot_service = bot_service
        self.team_id = team_id
        self.notification_queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self):
        """Start the notification service."""
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self._process_notification_queue())
            logger.info("Admin notification service started")
    
    async def stop(self):
        """Stop the notification service."""
        self.is_running = False
        logger.info("Admin notification service stopped")
    
    async def send_critical_error_notification(
        self, 
        error_type: str, 
        error_message: str, 
        context: Dict[str, Any] = None
    ):
        """Send a critical error notification to administrators."""
        try:
            notification = {
                "type": "critical_error",
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "team_id": self.team_id
            }
            
            await self.notification_queue.put(notification)
            logger.info(f"Critical error notification queued: {error_type}")
            
        except Exception as e:
            logger.error(f"❌ Error queuing critical error notification: {e}")
    
    async def send_system_alert(
        self, 
        alert_type: str, 
        message: str, 
        severity: str = "info",
        context: Dict[str, Any] = None
    ):
        """Send a system alert to administrators."""
        try:
            notification = {
                "type": "system_alert",
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "team_id": self.team_id
            }
            
            await self.notification_queue.put(notification)
            logger.info(f"System alert queued: {alert_type}")
            
        except Exception as e:
            logger.error(f"❌ Error queuing system alert: {e}")
    
    async def _process_notification_queue(self):
        """Process the notification queue."""
        while self.is_running:
            try:
                # Wait for notification with timeout
                try:
                    notification = await asyncio.wait_for(
                        self.notification_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                await self._send_notification(notification)
                
            except Exception as e:
                logger.error(f"❌ Error processing notification queue: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send a notification to administrators."""
        try:
            if notification["type"] == "critical_error":
                await self._send_critical_error(notification)
            elif notification["type"] == "system_alert":
                await self._send_system_alert(notification)
            else:
                logger.warning(f"Unknown notification type: {notification['type']}")
                
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
    
    async def _send_critical_error(self, notification: Dict[str, Any]):
        """Send a critical error notification."""
        try:
            error_type = notification["error_type"]
            error_message = notification["error_message"]
            context = notification.get("context", {})
            timestamp = notification["timestamp"]
            
            # Format the error message
            message = f"""🚨 **CRITICAL SYSTEM ERROR**

❌ **Error Type:** {error_type}
📝 **Error Message:** {error_message}
⏰ **Timestamp:** {timestamp}
🏷️ **Team ID:** {self.team_id}

🔍 **Context:**
"""
            
            # Add context information
            for key, value in context.items():
                message += f"• **{key}:** {value}\n"
            
            message += """
⚠️ **Action Required:**
• Review system logs for detailed information
• Check system health and performance
• Contact system administrator if needed

This is an automated alert from the KICKAI system."""
            
            # Send to leadership chat if available
            if hasattr(self.bot_service, 'leadership_chat_id') and self.bot_service.leadership_chat_id:
                await self.bot_service.send_message(
                    self.bot_service.leadership_chat_id, 
                    message
                )
                logger.info(f"Critical error notification sent to leadership chat: {error_type}")
            else:
                logger.warning("No leadership chat ID configured for critical error notifications")
                
        except Exception as e:
            logger.error(f"❌ Error sending critical error notification: {e}")
    
    async def _send_system_alert(self, notification: Dict[str, Any]):
        """Send a system alert notification."""
        try:
            alert_type = notification["alert_type"]
            message_text = notification["message"]
            severity = notification["severity"]
            context = notification.get("context", {})
            timestamp = notification["timestamp"]
            
            # Determine emoji based on severity
            severity_emoji = {
                "info": "ℹ️",
                "warning": "⚠️", 
                "error": "❌",
                "critical": "🚨"
            }.get(severity, "ℹ️")
            
            # Format the alert message
            message = f"""{severity_emoji} **SYSTEM ALERT**

📋 **Alert Type:** {alert_type}
📝 **Message:** {message_text}
🔴 **Severity:** {severity.upper()}
⏰ **Timestamp:** {timestamp}
🏷️ **Team ID:** {self.team_id}

🔍 **Context:**
"""
            
            # Add context information
            for key, value in context.items():
                message += f"• **{key}:** {value}\n"
            
            message += """
This is an automated alert from the KICKAI system."""
            
            # Send to leadership chat if available
            if hasattr(self.bot_service, 'leadership_chat_id') and self.bot_service.leadership_chat_id:
                await self.bot_service.send_message(
                    self.bot_service.leadership_chat_id, 
                    message
                )
                logger.info(f"System alert sent to leadership chat: {alert_type}")
            else:
                logger.warning("No leadership chat ID configured for system alerts")
                
        except Exception as e:
            logger.error(f"❌ Error sending system alert: {e}")


# Global instance for easy access
_admin_notification_service = None


def get_admin_notification_service(
    bot_service: TelegramBotServiceInterface, 
    team_id: str
) -> AdminNotificationService:
    """Get the global admin notification service instance."""
    global _admin_notification_service
    if _admin_notification_service is None:
        _admin_notification_service = AdminNotificationService(bot_service, team_id)
    return _admin_notification_service


async def send_critical_error_notification(
    bot_service: TelegramBotServiceInterface,
    team_id: str,
    error_type: str,
    error_message: str,
    context: Dict[str, Any] = None
):
    """Send a critical error notification using the global service."""
    service = get_admin_notification_service(bot_service, team_id)
    await service.send_critical_error_notification(error_type, error_message, context)


async def send_system_alert(
    bot_service: TelegramBotServiceInterface,
    team_id: str,
    alert_type: str,
    message: str,
    severity: str = "info",
    context: Dict[str, Any] = None
):
    """Send a system alert using the global service."""
    service = get_admin_notification_service(bot_service, team_id)
    await service.send_system_alert(alert_type, message, severity, context)