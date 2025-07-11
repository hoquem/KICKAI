"""
Factory for creating user management adapters.

This factory creates adapters that wrap application layer services and provides
them to the presentation layer, maintaining clean architecture.
"""

import logging
from typing import Optional

from domain.interfaces.user_management import IUserManagement
from domain.adapters import UserManagementAdapter

logger = logging.getLogger(__name__)

# Global instance for singleton pattern
_user_management_instance: Optional[IUserManagement] = None


def get_user_management() -> IUserManagement:
    """Get the user management instance with proper dependency injection."""
    global _user_management_instance
    
    if _user_management_instance is None:
        try:
            # Import services from application layer
            from services.team_member_service import TeamMemberService
            from services.access_control_service import AccessControlService
            from database.firebase_client import get_firebase_client
            
            # Create services
            firebase_client = get_firebase_client()
            team_member_service = TeamMemberService(firebase_client)
            access_control_service = AccessControlService()
            
            # Create adapter
            _user_management_instance = UserManagementAdapter(
                team_member_service=team_member_service,
                access_control_service=access_control_service
            )
            
            logger.info("✅ User management adapter created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create user management adapter: {e}")
            raise
    
    return _user_management_instance


def reset_user_management() -> None:
    """Reset the user management instance (useful for testing)."""
    global _user_management_instance
    _user_management_instance = None
    logger.info("User management instance reset") 