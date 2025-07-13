"""
Factory for creating user management adapters.

This factory creates adapters that wrap application layer services and provides
them to the presentation layer, maintaining clean architecture.
"""

import logging
from typing import Optional

from domain.interfaces.user_management import IUserManagement
from domain.adapters import UserManagementAdapter
from services.interfaces.team_member_service_interface import ITeamMemberService
from services.interfaces.access_control_service_interface import IAccessControlService

logger = logging.getLogger(__name__)


def create_user_management(team_member_service: ITeamMemberService, 
                          access_control_service: IAccessControlService) -> IUserManagement:
    """Create a user management adapter with proper dependency injection."""
    try:
        # Create adapter
        user_management = UserManagementAdapter(
            team_member_service=team_member_service,
            access_control_service=access_control_service
        )
        
        logger.info("✅ User management adapter created successfully")
        return user_management
        
    except Exception as e:
        logger.error(f"❌ Failed to create user management adapter: {e}")
        raise 