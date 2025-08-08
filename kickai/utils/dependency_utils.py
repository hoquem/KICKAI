#!/usr/bin/env python3
"""
Dependency Injection Utilities

This module provides standardized utilities for accessing services through
the dependency container to ensure consistent patterns across the codebase.
"""

from typing import Any, Optional, Type, TypeVar
from loguru import logger

from kickai.core.dependency_container import get_container

# Type variable for service types
T = TypeVar('T')


def get_service(service_name: str) -> Any:
    """
    Get a service from the dependency container by name.
    
    Args:
        service_name: Name of the service to retrieve
        
    Returns:
        The requested service instance
        
    Raises:
        RuntimeError: If the service is not available in the container
    """
    container = get_container()
    service = container.get_service(service_name)
    
    if service is None:
        raise RuntimeError(f"Service '{service_name}' is not available in dependency container")
    
    return service


def get_service_by_type(service_type: Type[T]) -> T:
    """
    Get a service from the dependency container by type.
    
    Args:
        service_type: Type of the service to retrieve
        
    Returns:
        The requested service instance of the specified type
        
    Raises:
        RuntimeError: If the service is not available in the container
    """
    container = get_container()
    service = container.get_service(service_type)
    
    if service is None:
        raise RuntimeError(f"Service of type '{service_type.__name__}' is not available in dependency container")
    
    return service


def get_player_service():
    """
    Get the PlayerService from the dependency container.
    
    Returns:
        PlayerService instance
        
    Raises:
        RuntimeError: If PlayerService is not available
    """
    return get_service("PlayerService")


def get_team_service():
    """
    Get the TeamService from the dependency container.
    
    Returns:
        TeamService instance
        
    Raises:
        RuntimeError: If TeamService is not available
    """
    return get_service("TeamService")


def get_team_member_service():
    """
    Get the TeamMemberService from the dependency container.
    
    Returns:
        TeamMemberService instance
        
    Raises:
        RuntimeError: If TeamMemberService is not available
    """
    return get_service("TeamMemberService")


def get_match_service():
    """
    Get the MatchService from the dependency container.
    
    Returns:
        MatchService instance
        
    Raises:
        RuntimeError: If MatchService is not available
    """
    return get_service("MatchService")


def get_attendance_service():
    """
    Get the AttendanceService from the dependency container.
    
    Returns:
        AttendanceService instance
        
    Raises:
        RuntimeError: If AttendanceService is not available
    """
    return get_service("AttendanceService")


def get_invite_link_service():
    """
    Get the InviteLinkService from the dependency container.
    
    Returns:
        InviteLinkService instance
        
    Raises:
        RuntimeError: If InviteLinkService is not available
    """
    return get_service("InviteLinkService")


def get_telegram_bot_service():
    """
    Get the TelegramBotService from the dependency container.
    
    Returns:
        TelegramBotService instance
        
    Raises:
        RuntimeError: If TelegramBotService is not available
    """
    return get_service("TelegramBotService")


def get_communication_service():
    """
    Get the CommunicationService from the dependency container.
    
    Returns:
        CommunicationService instance
        
    Raises:
        RuntimeError: If CommunicationService is not available
    """
    return get_service("CommunicationService")


def get_validation_service():
    """
    Get the ValidationService from the dependency container.
    
    Returns:
        ValidationService instance
        
    Raises:
        RuntimeError: If ValidationService is not available
    """
    return get_service("ValidationService")


def get_analytics_service():
    """
    Get the AnalyticsService from the dependency container.
    
    Returns:
        AnalyticsService instance
        
    Raises:
        RuntimeError: If AnalyticsService is not available
    """
    return get_service("AnalyticsService")


def get_health_check_service():
    """
    Get the HealthCheckService from the dependency container.
    
    Returns:
        HealthCheckService instance
        
    Raises:
        RuntimeError: If HealthCheckService is not available
    """
    return get_service("HealthCheckService")


def get_permission_service():
    """
    Get the PermissionService from the dependency container.
    
    Returns:
        PermissionService instance
        
    Raises:
        RuntimeError: If PermissionService is not available
    """
    return get_service("PermissionService")


def get_access_control_service():
    """
    Get the AccessControlService from the dependency container.
    
    Returns:
        AccessControlService instance
        
    Raises:
        RuntimeError: If AccessControlService is not available
    """
    return get_service("AccessControlService")


def validate_required_services(*service_names: str) -> None:
    """
    Validate that all required services are available in the dependency container.
    
    Args:
        *service_names: Names of services to validate
        
    Raises:
        RuntimeError: If any required service is not available
    """
    container = get_container()
    missing_services = []
    
    for service_name in service_names:
        if container.get_service(service_name) is None:
            missing_services.append(service_name)
    
    if missing_services:
        raise RuntimeError(
            f"The following required services are not available in dependency container: {', '.join(missing_services)}"
        )


def get_container_status() -> dict[str, Any]:
    """
    Get the status of the dependency container.
    
    Returns:
        Dictionary containing container status information
    """
    container = get_container()
    return container.get_container_status()


def ensure_container_initialized() -> None:
    """
    Ensure the dependency container is properly initialized.
    
    Raises:
        RuntimeError: If the container is not properly initialized
    """
    container = get_container()
    status = container.get_container_status()
    
    if not status.get('initialized', False):
        raise RuntimeError("Dependency container is not properly initialized")
    
    if not status.get('services_loaded', False):
        raise RuntimeError("Services are not loaded in dependency container")

