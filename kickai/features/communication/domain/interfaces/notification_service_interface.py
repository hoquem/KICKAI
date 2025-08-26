#!/usr/bin/env python3
"""
Notification Service Interface

Defines the contract for notification services.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class INotificationService(ABC):
    """Interface for notification service operations."""

    @abstractmethod
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        priority: str = "normal"
    ) -> str:
        """
        Send a notification to a user.
        
        Args:
            user_id: Target user identifier
            title: Notification title
            message: Notification content
            notification_type: Type of notification (info, warning, error)
            priority: Priority level (low, normal, high, urgent)
            
        Returns:
            Notification ID
        """
        pass

    @abstractmethod
    async def send_bulk_notifications(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        notification_type: str = "info"
    ) -> List[str]:
        """
        Send notifications to multiple users.
        
        Args:
            user_ids: List of target user identifiers
            title: Notification title
            message: Notification content
            notification_type: Type of notification
            
        Returns:
            List of notification IDs
        """
        pass

    @abstractmethod
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User identifier
            unread_only: Only return unread notifications
            limit: Maximum number of notifications to return
            
        Returns:
            List of notifications
        """
        pass

    @abstractmethod
    async def mark_notification_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification identifier
            
        Returns:
            True if successfully marked
        """
        pass

    @abstractmethod
    async def schedule_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        send_at: datetime,
        notification_type: str = "reminder"
    ) -> str:
        """
        Schedule a notification for future delivery.
        
        Args:
            user_id: Target user identifier
            title: Notification title
            message: Notification content
            send_at: When to send the notification
            notification_type: Type of notification
            
        Returns:
            Scheduled notification ID
        """
        pass