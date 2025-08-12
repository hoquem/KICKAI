#!/usr/bin/env python3
"""
System Infrastructure Help Tools

This module provides tools for system infrastructure help and information.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.system_infrastructure.domain.services.system_service import SystemService
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.validation_utils import (
    validate_team_id,
)


@tool("get_version_info")
def get_version_info(team_id: str) -> str:
    """
    Get system version information.


        team_id: Team ID (required) - available from context


    :return: JSON response with version information
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'team_id': team_id}


        # Get service
        container = get_container()
        system_service = container.get_service(SystemService)

        if not system_service:
            return json_error(message="SystemService is not available", error_type="Service unavailable")

        # Get version info
        version_info = system_service.get_version_info_sync()

        data = {
            'team_id': team_id,
            'version_info': version_info
        }

        ui_format = "📋 **System Version Information**\n\n"
        for key, value in version_info.items():
            ui_format += f"• **{key.title()}**: {value}\n"

        return json_response(data=data, ui_format=ui_format)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_version_info: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to get version info: {e}")
        return json_error(message=f"Failed to get version info: {e}", error_type="Operation failed")

@tool("get_system_available_commands")
def get_system_available_commands(team_id: str) -> str:
    """
    Get all available system commands.


        team_id: Team ID (required) - available from context


    :return: JSON response with available system commands
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'team_id': team_id}


        # Get service
        container = get_container()
        system_service = container.get_service(SystemService)

        if not system_service:
            return json_error(message="SystemService is not available", error_type="Service unavailable")

        # Get available commands
        commands = system_service.get_system_available_commands_sync(team_id)

        if commands:
            data = {
                'team_id': team_id,
                'commands': commands,
                'total_count': len(commands)
            }

            ui_format = "📋 **Available System Commands**\n\n"
            for command in commands:
                ui_format += f"• **{command['name']}** - {command['description']}\n"

            return json_response(data=data, ui_format=ui_format)
        else:
            data = {
                'team_id': team_id,
                'commands': [],
                'total_count': 0
            }
            return json_response(data=data, ui_format="📋 No system commands available.")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_system_available_commands: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to get system available commands: {e}")
        return json_error(message=f"Failed to get system available commands: {e}", error_type="Operation failed")
