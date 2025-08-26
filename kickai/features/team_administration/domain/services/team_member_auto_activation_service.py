#!/usr/bin/env python3
"""
Team Member Auto-Activation Service

This service handles automatic team member activation when users join leadership chat 
via valid invite links. It provides secure validation, status updates, and welcome 
message coordination for team members.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from loguru import logger

from kickai.core.exceptions import ServiceNotAvailableError
from kickai.database.interfaces import DataStoreInterface
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.team_administration.domain.exceptions import (
    TeamMemberNotFoundError,
    TeamMemberServiceUnavailableError,
)


@dataclass
class TeamMemberActivationResult:
    """Result of team member auto-activation attempt."""
    success: bool
    member_id: Optional[str] = None
    member_name: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    was_activated: bool = False
    invite_valid: bool = False


class TeamMemberAutoActivationService:
    """
    Service for automatically activating team members when they join leadership chat via invite links.
    
    Handles:
    - Invite link validation for team members
    - Team member status updates (pending → active)
    - Welcome message coordination for leadership chat
    - Security and audit logging
    """

    def __init__(self, database: DataStoreInterface, team_id: str):
        self.database = database
        self.team_id = team_id
        
        # Initialize required services with proper dependencies
        from kickai.features.team_administration.domain.services.team_service import TeamService
        from kickai.features.team_administration.infrastructure.firebase_team_repository import FirebaseTeamRepository
        from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
        
        # Create repository instances
        team_repository = FirebaseTeamRepository(database)
        
        # Create team service 
        team_service = TeamService(team_repository)
        
        # Initialize team member service
        self.team_member_service = TeamMemberService(team_repository)
        
        # Initialize invite service with database
        if database is not None:
            self.invite_service = InviteLinkService(database=database)
        else:
            # Get database from container if not provided
            from kickai.core.dependency_container import get_container
            container = get_container()
            db = container.get_database()
            self.invite_service = InviteLinkService(database=db)
        
        logger.info(f"🔧 TeamMemberAutoActivationService initialized for team: {team_id}")

    async def process_new_leadership_chat_member(
        self,
        telegram_id: int,
        username: str,
        invite_context: Optional[Dict[str, Any]] = None
    ) -> TeamMemberActivationResult:
        """
        Process a new leadership chat member and attempt auto-activation via invite validation.
        
        Args:
            telegram_id: User's Telegram ID
            username: User's Telegram username
            invite_context: Optional invite context from join event
            
        Returns:
            TeamMemberActivationResult with activation status and details
        """
        try:
            logger.info(f"🔄 Processing new leadership chat member: {username} (ID: {telegram_id})")
            
            # Step 1: Validate invite link if present
            invite_validation = await self._validate_invite_link(invite_context, telegram_id, username)
            
            if not invite_validation["valid"]:
                logger.warning(f"❌ Invalid or missing invite for team member {username} (ID: {telegram_id})")
                return TeamMemberActivationResult(
                    success=False,
                    message=self._create_uninvited_member_message(username),
                    error="No valid invite link found",
                    invite_valid=False
                )
            
            # Step 2: Find and activate the team member
            activation_result = await self._activate_team_member_from_invite(
                invite_validation["invite_data"],
                telegram_id,
                username
            )
            
            if activation_result.success:
                logger.info(f"✅ Successfully auto-activated team member: {activation_result.member_name} (ID: {activation_result.member_id})")
                
                # Step 3: Log successful activation for audit
                await self._log_activation_event(activation_result, invite_validation["invite_data"])
                
                return activation_result
            else:
                logger.error(f"❌ Failed to activate team member for {username}: {activation_result.error}")
                return activation_result
                
        except Exception as e:
            logger.error(f"❌ Error in team member auto-activation for {username}: {e}")
            return TeamMemberActivationResult(
                success=False,
                message="❌ Error processing your join. Please contact team leadership.",
                error=str(e)
            )

    async def _validate_invite_link(
        self,
        invite_context: Optional[Dict[str, Any]],
        telegram_id: int,
        username: str
    ) -> Dict[str, Any]:
        """Validate invite link from join context."""
        try:
            if not invite_context:
                logger.debug(f"No invite context provided for team member {username}")
                return {"valid": False, "reason": "no_invite_context"}
            
            # Extract invite link from context
            invite_link = invite_context.get("invite_link")
            secure_data = invite_context.get("secure_data")
            
            if not invite_link and not secure_data:
                logger.debug(f"No invite link or secure data in context for team member {username}")
                return {"valid": False, "reason": "no_invite_data"}
            
            # Validate invite link
            invite_data = await self.invite_service.validate_and_use_invite_link(
                invite_link=invite_link or "",
                user_id=str(telegram_id),
                username=username,
                secure_data=secure_data
            )
            
            if invite_data:
                logger.info(f"✅ Valid invite link found for team member {username}: {invite_data.get('invite_id')}")
                return {
                    "valid": True,
                    "invite_data": invite_data,
                    "invite_id": invite_data.get("invite_id")
                }
            else:
                logger.warning(f"❌ Invalid invite link validation for team member {username}")
                return {"valid": False, "reason": "invalid_invite"}
                
        except Exception as e:
            logger.error(f"❌ Error validating invite for team member {username}: {e}")
            return {"valid": False, "reason": "validation_error", "error": str(e)}

    async def _activate_team_member_from_invite(
        self,
        invite_data: Dict[str, Any],
        telegram_id: int,
        username: str
    ) -> TeamMemberActivationResult:
        """Activate team member based on validated invite data."""
        try:
            # Extract team member information from invite
            member_name = invite_data.get("member_name")
            member_phone = invite_data.get("member_phone")
            member_id = invite_data.get("member_id")
            
            if not member_name or not member_id:
                return TeamMemberActivationResult(
                    success=False,
                    message="❌ Invalid invite data - missing team member information.",
                    error="Missing member_name or member_id in invite",
                    invite_valid=True
                )
            
            # Find the team member record
            team_member = await self._find_team_member_by_invite_data(member_id, member_phone, member_name)
            
            if not team_member:
                return TeamMemberActivationResult(
                    success=False,
                    message=f"❌ Team member record not found for {member_name}. Please contact team leadership.",
                    error=f"No team member found for ID: {member_id}",
                    invite_valid=True
                )
            
            # Check if team member is in correct status for activation
            if team_member.status != "pending":
                if team_member.status == "active":
                    return TeamMemberActivationResult(
                        success=True,
                        member_id=team_member.member_id,
                        member_name=team_member.name,
                        message=f"👋 Welcome back, {team_member.name}! You're already activated and have full leadership access!",
                        was_activated=False,  # Already active
                        invite_valid=True
                    )
                else:
                    return TeamMemberActivationResult(
                        success=False,
                        member_id=team_member.member_id,
                        member_name=team_member.name,
                        message=f"❌ Your account status ({team_member.status}) prevents activation. Please contact team leadership.",
                        error=f"Team member status is {team_member.status}, not pending",
                        invite_valid=True
                    )
            
            # Update team member with Telegram information and activate
            await self._update_and_activate_team_member(team_member, telegram_id, username)
            
            return TeamMemberActivationResult(
                success=True,
                member_id=team_member.member_id,
                member_name=team_member.name,
                message=f"🎉 Welcome to the leadership team, {team_member.name}! You've been automatically activated and have full access to team management features!",
                was_activated=True,
                invite_valid=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error activating team member from invite: {e}")
            return TeamMemberActivationResult(
                success=False,
                message="❌ Error during activation. Please contact team leadership.",
                error=str(e),
                invite_valid=True
            )

    async def _find_team_member_by_invite_data(
        self,
        member_id: str,
        member_phone: Optional[str],
        member_name: str
    ) -> Optional[TeamMember]:
        """Find team member record using invite data."""
        try:
            # Try by member_id first (most reliable)
            try:
                team_member = await self.team_member_service.get_team_member_by_id(member_id, self.team_id)
                if team_member:
                    logger.debug(f"Found team member by ID: {member_id}")
                    return team_member
            except TeamMemberNotFoundError:
                logger.debug(f"Team member not found by ID: {member_id}")
            
            # Try by phone number as fallback
            if member_phone:
                try:
                    team_member = await self.team_member_service.get_team_member_by_phone(member_phone, self.team_id)
                    if team_member and team_member.status == "pending":
                        logger.debug(f"Found pending team member by phone: {member_phone}")
                        return team_member
                except Exception:
                    logger.debug(f"No team members found by phone: {member_phone}")
            
            logger.warning(f"No team member found for ID: {member_id}, phone: {member_phone}, name: {member_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding team member by invite data: {e}")
            return None

    async def _update_and_activate_team_member(
        self,
        team_member: TeamMember,
        telegram_id: int,
        username: str
    ) -> None:
        """Update team member with Telegram info and activate."""
        try:
            # Validate inputs
            if not team_member or not team_member.member_id:
                raise ValueError("Invalid team member object provided")
            if telegram_id <= 0:
                raise ValueError("Invalid telegram_id provided")
            if not username or not username.strip():
                raise ValueError("Invalid username provided")
            
            # Update team member with Telegram information and active status
            team_member.telegram_id = telegram_id
            team_member.username = username.strip()
            team_member.status = "active"
            team_member.updated_at = datetime.utcnow()
            
            # Save updated team member
            await self.team_member_service.update_team_member(team_member)
            
            logger.info(f"✅ Team member {team_member.name} (ID: {team_member.member_id}) activated with Telegram ID: {telegram_id}")
            
        except Exception as e:
            logger.error(f"❌ Error updating and activating team member {team_member.member_id}: {e}")
            raise

    async def _log_activation_event(
        self,
        activation_result: TeamMemberActivationResult,
        invite_data: Dict[str, Any]
    ) -> None:
        """Log successful activation event for audit trail."""
        try:
            event_data = {
                "event_type": "team_member_auto_activation",
                "member_id": activation_result.member_id,
                "member_name": activation_result.member_name,
                "team_id": self.team_id,
                "invite_id": invite_data.get("invite_id"),
                "was_activated": activation_result.was_activated,
                "timestamp": datetime.utcnow().isoformat(),
                "success": activation_result.success
            }
            
            # Store in audit log collection
            await self.database.create_document(
                "kickai_team_member_activation_logs",
                event_data,
                f"activation_{activation_result.member_id}_{int(datetime.utcnow().timestamp())}"
            )
            
            logger.info(f"📝 Logged team member activation event for: {activation_result.member_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to log team member activation event: {e}")
            # Don't fail the activation if logging fails

    def _create_uninvited_member_message(self, username: str) -> str:
        """Create appropriate message for uninvited users trying to join leadership chat."""
        return f"""
👋 Hi {username}!

❌ It looks like you joined the leadership chat without a valid invite link. This is a private leadership channel.

🔗 To join as a team member:
1. Contact existing leadership to invite you with `/addmember`
2. Use the invite link they provide
3. You'll be automatically activated when you join!

🔒 **Leadership chat access requires:**
- Proper invitation from existing leadership
- Team administrator approval

📞 **Please contact team administration for proper access.**

Thanks for understanding! ⚽
        """.strip()

    def get_welcome_message_context(self, activation_result: TeamMemberActivationResult) -> Dict[str, Any]:
        """Get context for enhanced welcome message."""
        return {
            "member_name": activation_result.member_name,
            "member_id": activation_result.member_id,
            "was_activated": activation_result.was_activated,
            "activation_success": activation_result.success,
            "team_id": self.team_id
        }