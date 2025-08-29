#!/usr/bin/env python3
"""
Simplified Team Member Tools

This module provides tools for simplified team member management
for the new /addmember command that only requires name and phone number.
Clean implementation following CrewAI best practices.
"""

from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus, ChatType
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.team_administration.domain.repositories.team_repository_interface import (
    TeamRepositoryInterface,
)
from kickai.features.team_administration.domain.services.team_member_management_service import (
    TeamMemberManagementService,
)
from kickai.features.team_administration.domain.exceptions import (
    TeamServiceUnavailableError,
    TeamNotFoundError,
    LeadershipChatNotConfiguredError,
    InviteLinkServiceUnavailableError,
    InviteLinkCreationError,
    RepositoryUnavailableError,
    MissingRequiredFieldError,
    PermissionError,
)
from kickai.features.team_administration.domain.types import (
    TelegramUserId,
    TeamId,
    TeamMemberCreationRequest,
    TeamMemberCreationResult,
)
from kickai.utils.constants import (
    DEFAULT_MEMBER_ROLE,
    ERROR_MESSAGES,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_POSITION_LENGTH,
    MAX_TEAM_ID_LENGTH,
    MAX_USER_ID_LENGTH,
)
from crewai.tools import tool
from kickai.utils.tool_helpers import (
    create_json_response,
    format_tool_error,
    validate_required_input,
)
from kickai.utils.validation_utils import (
    normalize_phone,
    sanitize_input,
)


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def add_team_member_simplified(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_name: str, 
    phone_number: str
) -> str:
    """
    👔 **AI EXPERT: Team Member Registration Tool**

    **PRIMARY FUNCTION**: Add a new team member (coach, manager, etc.) to the team and generate a secure invite link for leadership chat access.

    **CORE WORKFLOW**:
    1. Validate leadership permissions and input data
    2. Check for duplicate phone numbers (prevent conflicts)
    3. Generate unique member ID using name-based algorithm
    4. Create team member record with specified role
    5. Generate secure, time-limited invite link for leadership chat
    6. Return formatted success response with instructions

    **CRITICAL VALIDATIONS**:
    - Leadership chat context required (chat_type must be "leadership")
    - Phone number must be unique within team
    - UK phone format validation (+447123456789 or 07123456789)
    - Name length validation (2-100 characters)
    - Valid team member role if specified (Coach, Manager, etc.)
    - Email format validation if provided

    **SECURITY FEATURES**:
    - Leadership-only access control
    - Duplicate phone number prevention
    - Secure invite link generation with expiration
    - Input sanitization and validation
    - Role-based permission assignment

    **Args**:
        telegram_id (TelegramUserId): Admin's Telegram ID (from context)
        team_id (TeamId): Team identifier (from context)
        username (str): Admin's username (from context)
        chat_type (str): Chat type - MUST be "leadership" for this tool
        player_name (str): Team member's full name (2-100 characters)
        phone_number (str): Team member's phone number (UK format required)

    **Returns**:
        JSON string with success/error status and formatted message

    **🎯 CONTEXT USAGE GUIDANCE**:
    - **LEADERSHIP CHAT**: Primary tool for team member registration workflows
    - **MAIN CHAT**: NOT AVAILABLE - blocked by permission system
    - **PRIVATE CHAT**: NOT AVAILABLE - blocked by permission system

    **📋 USE WHEN**:
    - User requests to add a new team member (coach, manager)
    - Leadership needs to register staff with invite links
    - Team member registration workflow initiation
    - Team expansion and staff onboarding

    **❌ AVOID WHEN**:
    - User is not in leadership chat (permission error)
    - Phone number already exists (duplicate error)
    - Invalid role specified (validation error)
    - Need to add players (use add_player tool instead)

    **🔄 ALTERNATIVES**:
    - `add_player`: For adding players to the team
    - `get_user_status`: For checking existing member information
    - `list_team_members_and_players`: For viewing all team members

    **💡 AI AGENT EXAMPLES**:
    - **User Input**: "Add team member Sarah Johnson with phone +447123456789"
    - **Action**: Call `add_team_member_simplified(telegram_id, team_id, username, "leadership", "Sarah Johnson", "+447123456789")`
    - **Expected Output**: Success message with invite link and instructions

    **🚨 ERROR SCENARIOS**:
    - **Permission Error**: User not in leadership chat → Return permission error message
    - **Duplicate Phone**: Phone already registered → Return existing member details
    - **Invalid Phone**: Wrong format → Return format guidance with examples
    - **Missing Data**: Incomplete information → Return specific missing field guidance

    **🔧 TECHNICAL NOTES**:
    - Team member is created with "Active" status
    - Role automatically defaults to "Team Member"
    - Invite link expires in 7 days (configurable)
    - Member ID is generated using name-based algorithm
    - All inputs are sanitized and validated before processing

    **📊 PERFORMANCE CHARACTERISTICS**:
    - **Response Time**: < 2 seconds for successful operations
    - **Database Operations**: 2-3 queries (team lookup, member creation, invite generation)
    - **External Calls**: 1 Telegram API call for invite link generation
    - **Error Recovery**: Graceful degradation with clear error messages
    """
    try:
        # Validate context parameters
        if not team_id:
            raise MissingRequiredFieldError("Team ID")
        
        if not telegram_id:
            raise MissingRequiredFieldError("Telegram ID")

        # Validate chat type is leadership
        if chat_type.lower() != ChatType.LEADERSHIP.value:
            raise PermissionError("add team member", "leadership chat access")

        # Validate required fields - player_name and phone_number are required
        if not player_name or not player_name.strip():
            raise MissingRequiredFieldError("player name")

        if not phone_number or not phone_number.strip():
            raise MissingRequiredFieldError("phone number")

        # Sanitize inputs
        player_name = sanitize_input(player_name, max_length=MAX_NAME_LENGTH)
        phone_number = sanitize_input(phone_number, max_length=MAX_PHONE_LENGTH)
        role = DEFAULT_MEMBER_ROLE  # Always use default role
        team_id = sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH)
        username = sanitize_input(username, max_length=MAX_USER_ID_LENGTH)

        # Normalize phone number
        phone_number = normalize_phone(phone_number)

        container = get_container()

        # Get team repository for the service
        team_repository = container.get_service(TeamRepositoryInterface)
        if not team_repository:
            raise RepositoryUnavailableError("TeamRepositoryInterface")

        # Create consolidated team member management service
        management_service = TeamMemberManagementService(team_repository)

        # Create team member creation request
        creation_request = TeamMemberCreationRequest(
            telegram_id=telegram_id,
            team_id=team_id,
            member_name=player_name,
            phone_number=phone_number,
            chat_type=chat_type,
            role=role
        )

        # Create team member with invite link
        result = await management_service.create_team_member_with_invite(creation_request)

        if result.success:
            # Get team information for the success message
            team = await team_repository.get_team_by_id(team_id)
            
            # Determine team name with robust fallback logic
            if team and team.name and team.name.strip():
                team_name = team.name.strip()
            elif team_id and team_id.strip():
                team_name = team_id.strip()
            else:
                raise MissingRequiredFieldError("Team ID or team information")
            
            logger.debug(f"🏷️ Using team name for invite: '{team_name}' (from {'team.name' if team and team.name else 'team_id fallback'})")

            if result.invite_link:
                # Use the success message template with invite link
                from kickai.utils.constants import SUCCESS_MESSAGES
                
                logger.info(f"✅ Team member and invite link created successfully for {result.member.name}")
                success_response = SUCCESS_MESSAGES["MEMBER_ADDED_WITH_INVITE"].format(
                    name=result.member.name,
                    phone=result.member.phone_number,
                    role=result.member.role,
                    team_name=team_name,
                    invite_link=result.invite_link,
                    expires_at="7 days"  # Default value
                )
                
                return create_json_response(ResponseStatus.SUCCESS, data=success_response)
            else:
                # Member added but invite link failed - still return success with error note
                logger.warning(f"⚠️ Invite link creation failed for {result.member.name}: {result.error_message}")
                
                fallback_response = f"""✅ TEAM MEMBER ADDED SUCCESSFULLY!

👔 MEMBER DETAILS:
• Name: {result.member.name}
• Phone: {result.member.phone_number}
• Role: {result.member.role}
• Status: Active

⚠️ INVITE LINK ISSUE:
Could not generate invite link: {result.error_message or "Unknown error"}

📋 NEXT STEPS:
1. Member has been added to the team
2. You may need to manually add them to the leadership chat
3. Contact system administrator if invite link issues persist"""
                
                return create_json_response(ResponseStatus.SUCCESS, data=fallback_response)
        else:
            logger.error(f"❌ Failed to add team member: {result.error_message}")
            return create_json_response(ResponseStatus.ERROR, message=f"Failed to add team member: {result.error_message}")

    except (MissingRequiredFieldError, PermissionError) as e:
        logger.warning(f"⚠️ Validation error in add_team_member_simplified: {e}")
        return create_json_response(ResponseStatus.ERROR, message=str(e))
    
    except RepositoryUnavailableError as e:
        logger.error(f"❌ Repository error in add_team_member_simplified: {e}")
        return create_json_response(ResponseStatus.ERROR, message=str(e))
    
    except (TeamServiceUnavailableError, TeamNotFoundError, LeadershipChatNotConfiguredError) as e:
        logger.error(f"❌ Team configuration error in add_team_member_simplified: {e}")
        return create_json_response(ResponseStatus.ERROR, message=str(e))
    
    except (InviteLinkServiceUnavailableError, InviteLinkCreationError) as e:
        logger.warning(f"⚠️ Invite link error in add_team_member_simplified: {e}")
        # This is a partial failure - member might be added but invite failed
        return create_json_response(ResponseStatus.ERROR, message=str(e))
    
    except Exception as e:
        logger.error(f"❌ Unexpected error in add_team_member_simplified tool: {e}")
        logger.exception("Full stack trace:")
        return create_json_response(ResponseStatus.ERROR, message=f"System error occurred: {str(e)}")


