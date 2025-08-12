#!/usr/bin/env python3
"""
Onboarding Tools

This module provides tools for user onboarding processes.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.shared.domain.services.onboarding_service import OnboardingService
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.validation_utils import (
    validate_team_id,
)


@tool("team_member_guidance")
def team_member_guidance(telegram_id: int, team_id: str) -> str:
    """
    Provide guidance for team member onboarding.

    :param telegram_id: Telegram ID of the user (required) - available from context
    :type telegram_id: int
    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :return: JSON response with team member guidance
    :rtype: str
    """
    try:
        # Validate inputs

        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'telegram_id': telegram_id, 'team_id': team_id}


        # Get service
        container = get_container()
        onboarding_service = container.get_service(OnboardingService)

        if not onboarding_service:
            return json_error(message="OnboardingService is not available", error_type="Service unavailable")

        # Get team member guidance
        guidance = onboarding_service.get_team_member_guidance_sync(telegram_id, team_id)

        data = {
            'telegram_id': telegram_id,
            'team_id': team_id,
            'guidance_type': 'team_member',
            'guidance_content': guidance
        }

        return json_response(data=data, ui_format=guidance)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in team_member_guidance: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to provide team member guidance: {e}")
        return json_error(message=f"Failed to provide team member guidance: {e}", error_type="Operation failed")

# Note: The following tools are commented out as they are not currently implemented
# but may be needed in the future

# @tool("validate_registration_data")
# def validate_registration_data(registration_data: dict, team_id: str) -> str:
#     """
#     Validate registration data before processing.
#
#     Args:
#         registration_data: Registration data to validate
#         team_id: Team ID (required) - available from context
#
#     Returns:
#         JSON response with validation results
#     """
#     try:
#         # Validate inputs
#         team_id = validate_team_id(team_id)
#
#         # Log tool execution start
#         inputs = {'registration_data': registration_data, 'team_id': team_id}

#
#         # Get service
#         container = get_container()
#         onboarding_service = container.get_service(OnboardingService)
#
#         if not onboarding_service:
#             return json_error(message="OnboardingService is not available", error_type="Service unavailable")
#
#         # Validate registration data
#         validation_result = onboarding_service.validate_registration_data_sync(registration_data, team_id)
#
#         data = {
#             'registration_data': registration_data,
#             'team_id': team_id,
#             'validation_result': validation_result
#         }
#
#         return json_response(data=data, ui_format=f"Validation result: {validation_result}")
#
#     except ServiceNotAvailableError as e:
#         logger.error(f"Service not available in validate_registration_data: {e}")
#         return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
#     except Exception as e:
#         logger.error(f"Failed to validate registration data: {e}")
#         return json_error(message=f"Failed to validate registration data: {e}", error_type="Operation failed")

# @tool("register_team_member_onboarding")
# def register_team_member_onboarding(registration_data: dict, team_id: str, telegram_id: int) -> str:
#     """
#     Register a team member through the onboarding process.
#
#     Args:
#         registration_data: Registration data for the team member
#         team_id: Team ID (required) - available from context
#         telegram_id: Telegram ID of the requesting user (required) - available from context
#
#     Returns:
#         JSON response with registration status
#     """
#     try:
#         # Validate inputs
#         team_id = validate_team_id(team_id)

#
#         # Log tool execution start
#         inputs = {'registration_data': registration_data, 'team_id': team_id, 'telegram_id': telegram_id}

#
#         # Get service
#         container = get_container()
#         onboarding_service = container.get_service(OnboardingService)
#
#         if not onboarding_service:
#             return json_error(message="OnboardingService is not available", error_type="Service unavailable")
#
#         # Register team member
#         success = onboarding_service.register_team_member_sync(registration_data, team_id, telegram_id)
#
#         if success:
#             data = {
#                 'registration_data': registration_data,
#                 'team_id': team_id,
#                 'telegram_id': telegram_id,
#                 'status': 'registered'
#             }
#
#             return json_response(data=data, ui_format="Team member registered successfully")
#         else:
#             return json_error(message="Failed to register team member", error_type="Operation failed")
#
#     except ServiceNotAvailableError as e:
#         logger.error(f"Service not available in register_team_member_onboarding: {e}")
#         return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
#     except Exception as e:
#         logger.error(f"Failed to register team member: {e}")
#         return json_error(message=f"Failed to register team member: {e}", error_type="Operation failed")

# @tool("detect_registration_context")
# def detect_registration_context(telegram_id: int, team_id: str, chat_type: str) -> str:
#     """
#     Detect the registration context for a user.
#
#     Args:
#         telegram_id: Telegram ID of the user (required) - available from context
#         team_id: Team ID (required) - available from context
#         chat_type: Chat type (main, leadership, private) - available from context
#
#     Returns:
#         JSON response with registration context
#     """
#     try:
#         # Validate inputs

#         team_id = validate_team_id(team_id)
#         chat_type = validate_required_input(chat_type, "Chat type")
#
#         # Log tool execution start
#         inputs = {'telegram_id': telegram_id, 'team_id': team_id, 'chat_type': chat_type}

#
#         # Get service
#         container = get_container()
#         onboarding_service = container.get_service(OnboardingService)
#
#         if not onboarding_service:
#             return json_error(message="OnboardingService is not available", error_type="Service unavailable")
#
#         # Detect registration context
#         context = onboarding_service.detect_registration_context_sync(telegram_id, team_id, chat_type)
#
#         data = {
#             'telegram_id': telegram_id,
#             'team_id': team_id,
#             'chat_type': chat_type,
#             'registration_context': context
#         }
#
#         return json_response(data=data, ui_format=f"Registration context: {context}")
#
#     except ServiceNotAvailableError as e:
#         logger.error(f"Service not available in detect_registration_context: {e}")
#         return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
#     except Exception as e:
#         logger.error(f"Failed to detect registration context: {e}")
#         return json_error(message=f"Failed to detect registration context: {e}", error_type="Operation failed")
