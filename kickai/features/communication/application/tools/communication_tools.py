#!/usr/bin/env python3
"""
Communication Tools - Clean Architecture Application Layer

This module provides CrewAI tools for communication functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""


from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.communication.domain.interfaces.communication_service_interface import ICommunicationService
from kickai.utils.tool_validation import create_tool_response


def _get_communication_service() -> ICommunicationService:
    """Get communication service from container with error handling."""
    try:
        container = get_container()
        service = container.get_service(ICommunicationService)
        if not service:
            raise ValueError("Communication service not found in container")
        return service
    except Exception as e:
        logger.error(f"Failed to get communication service: {e}")
        raise


def _validate_chat_access(target_chat: str, user_chat_type: str) -> bool:
    """Validate user has access to target chat channel."""
    if not target_chat or not isinstance(target_chat, str):
        return False

    target_chat_lower = target_chat.lower().strip()
    user_chat_type_lower = user_chat_type.lower().strip() if user_chat_type else ""

    # Leadership chat requires leadership access
    if target_chat_lower == "leadership" and user_chat_type_lower != "leadership":
        return False

    # Only allow known chat types
    if target_chat_lower not in ["main", "leadership"]:
        return False

    return True


def _parse_poll_options(poll_options: str) -> tuple[list[str], str]:
    """Parse and validate poll options string with enhanced validation.

    Returns: (options_list, error_message or empty string)
    """
    if not poll_options or not isinstance(poll_options, str):
        return [], "Poll options must be provided as text"

    # Security: Sanitize input and check for malicious content
    if len(poll_options) > 1000:
        return [], "Poll options input is too long (maximum 1000 characters)"

    try:
        # Parse options with enhanced validation
        options_list = []
        for opt in poll_options.split(","):
            clean_opt = opt.strip()
            if clean_opt:
                # Basic security: Remove control characters and validate content
                if any(ord(char) < 32 and char not in ["\n", "\r", "\t"] for char in clean_opt):
                    return [], f"Invalid characters detected in poll option: {clean_opt[:20]}..."
                options_list.append(clean_opt)
    except Exception as e:
        logger.warning(f"Failed to parse poll options: {e}")
        return [], "Failed to parse poll options. Please use comma-separated values"

    if len(options_list) < 2:
        return [], "At least 2 poll options are required (separate with commas)"

    if len(options_list) > 10:
        return [], "Maximum 10 poll options allowed for readability"

    # Check for duplicates (case-insensitive)
    options_lower = [opt.lower() for opt in options_list]
    if len(options_lower) != len(set(options_lower)):
        return [], "Poll options must be unique (no duplicates allowed)"

    # Validate option lengths and content
    for i, option in enumerate(options_list, 1):
        if len(option) > 100:
            return [], f"Poll option {i} is too long (maximum 100 characters)"
        if len(option) < 1:
            return [], f"Poll option {i} cannot be empty"
        # Basic content validation
        if option.startswith(("/", "@", "#")) or option.strip() in ["", " "]:
            return [], f"Poll option {i} has invalid format or is empty"

    return options_list, ""


@tool("send_team_message")
async def send_team_message(team_id: str, message: str, target_chat: str = "main", chat_type: str = "main") -> str:
    """
    Send targeted message to specific team chat channel.

    Business operation to deliver messages to designated team communication channels
    with appropriate access control and channel-specific routing.

    Use when: Need to send targeted messages to specific team channels
    Required: User must have appropriate chat access permissions (leadership access required for leadership chat)

    Returns: Message delivery confirmation with channel details
    """
    try:
        # Input validation with enhanced security
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"

        if not message or not message.strip():
            return "❌ Message content is required"

        if not target_chat or not target_chat.strip():
            return "❌ Target chat is required"

        # Enhanced message validation for security
        if len(message) > 4000:  # Telegram message limit
            return "❌ Message is too long (maximum 4000 characters)"

        # Basic security check for malicious content
        if any(ord(char) < 32 and char not in ["\n", "\r", "\t"] for char in message):
            return "❌ Message contains invalid characters"

        # Validate target chat with enhanced security
        if not _validate_chat_access(target_chat, chat_type):
            return "❌ Invalid target chat or insufficient permissions"

        logger.info(f"📤 Message send request to {target_chat} chat for team {team_id}")

        # Get communication service with error handling
        try:
            communication_service = _get_communication_service()
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return "❌ Communication service temporarily unavailable"

        # Execute domain operation
        success = await communication_service.send_message(message, target_chat, team_id)

        if not success:
            logger.error(f"❌ Failed to send message to team {team_id} in {target_chat} chat")
            return f"❌ Failed to send message to {target_chat} chat"

        logger.info(f"✅ Message sent to {target_chat} chat for team {team_id}")
        return f"✅ Message delivered to {target_chat} chat"

    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        # Avoid exposing internal error details to users
        if "not found" in str(e).lower():
            return "❌ Team or chat channel not found"
        elif "permission" in str(e).lower() or "access" in str(e).lower():
            return "❌ Insufficient permissions to send message"
        elif "rate limit" in str(e).lower():
            return "❌ Too many messages sent. Please wait before sending another."
        return "❌ Failed to send message. Please try again or contact support."


@tool("send_team_announcement")
async def send_team_announcement(team_id: str, announcement: str) -> str:
    """
    Broadcast official team communication to all members.

    Business operation to deliver important information to every team member through
    established communication channels with delivery confirmation.

    Use when: Need to broadcast important information to entire team
    Required: User must have announcement privileges, typically leadership access

    Returns: Broadcast confirmation with delivery status to all team members
    """
    try:
        logger.info(f"📢 Announcement broadcast request for team {team_id}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not announcement.strip():
            return create_tool_response(False, "Announcement content is required")

        # Get communication service
        communication_service = _get_communication_service()

        # Execute domain operation
        success = await communication_service.send_announcement(announcement, team_id)

        if not success:
            logger.error(f"❌ Failed to broadcast announcement to team {team_id}")
            return create_tool_response(False, "Failed to send announcement")

        logger.info(f"✅ Announcement broadcast successful for team {team_id}")
        return create_tool_response(
            True,
            "Announcement sent successfully",
            data="📢 Announcement broadcast to all team members",
        )

    except Exception as e:
        logger.error(f"❌ Error sending announcement: {e}")
        return create_tool_response(False, f"Failed to send announcement: {e}")


@tool("send_team_poll")
async def send_team_poll(team_id: str, poll_question: str, poll_options: str) -> str:
    """
    Create team voting poll for democratic decision making.

    Business operation to generate interactive polls for team members to vote on decisions,
    gathering democratic input on various team topics and initiatives.

    Use when: Need team consensus or opinion gathering on decisions
    Required: User must have poll creation privileges, poll must have valid options

    Returns: Poll creation confirmation with voting details and option count
    """
    try:
        logger.info(f"🗳️ Poll creation request for team {team_id}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not poll_question.strip():
            return create_tool_response(False, "Poll question is required")

        if not poll_options.strip():
            return create_tool_response(False, "Poll options are required")

        # Parse and validate poll options
        options_list, error_message = _parse_poll_options(poll_options)
        if error_message:
            return create_tool_response(False, error_message)

        # Get communication service
        communication_service = _get_communication_service()

        # Execute domain operation
        success = await communication_service.send_poll(poll_question, poll_options, team_id)

        if not success:
            logger.error(f"❌ Failed to create poll for team {team_id}")
            return create_tool_response(False, "Failed to create poll")

        logger.info(f"✅ Poll created successfully for team {team_id}")
        return create_tool_response(
            True,
            "Poll created successfully",
            data=f"🗳️ Poll '{poll_question}' created with {len(options_list)} options",
        )

    except Exception as e:
        logger.error(f"❌ Error creating poll: {e}")
        return create_tool_response(False, f"Failed to create poll: {e}")
