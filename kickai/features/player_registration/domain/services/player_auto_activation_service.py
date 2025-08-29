#!/usr/bin/env python3
"""
Player Auto-Activation Service

This service handles automatic player activation when users join via valid invite links.
It provides secure validation, status updates, and welcome message coordination.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from loguru import logger

from kickai.core.exceptions import ServiceNotAvailableError, PlayerNotFoundError
from kickai.database.interfaces import DataStoreInterface
from kickai.features.player_registration.domain.entities.player import Player
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService


@dataclass
class ActivationResult:
    """Result of player auto-activation attempt."""
    success: bool
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    was_activated: bool = False
    invite_valid: bool = False


class PlayerAutoActivationService:
    """
    Service for automatically activating players when they join via invite links.
    
    Handles:
    - Invite link validation
    - Player status updates (pending → active)
    - Welcome message coordination
    - Security and audit logging
    """

    def __init__(self, database: DataStoreInterface, team_id: str):
        self.database = database
        self.team_id = team_id
        
        # Initialize required services with proper dependencies
        from kickai.features.team_administration.domain.services.team_service import TeamService
        from kickai.features.team_administration.infrastructure.firebase_team_repository import FirebaseTeamRepository
        from kickai.features.player_registration.infrastructure.firebase_player_repository import FirebasePlayerRepository
        from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
        
        # Create repository instances
        team_repository = FirebaseTeamRepository(database)
        player_repository = FirebasePlayerRepository(database)
        
        # Create team service 
        team_service = TeamService(team_repository)
        
        # Initialize player service with both required dependencies
        self.player_service = PlayerService(player_repository, team_service)
        
        # Initialize invite service with database and team_id
        if database is not None:
            self.invite_service = InviteLinkService(database=database, team_id=team_id)
        else:
            # Get database from container if not provided
            from kickai.core.dependency_container import get_container
            container = get_container()
            db = container.get_database()
            self.invite_service = InviteLinkService(database=db, team_id=team_id)
        
        logger.info(f"🔧 PlayerAutoActivationService initialized for team: {team_id}")

    async def process_new_chat_member(
        self,
        telegram_id: int,
        username: str,
        chat_type: str,
        invite_context: Optional[Dict[str, Any]] = None
    ) -> ActivationResult:
        """
        Process a new chat member and attempt auto-activation via invite validation.
        
        Args:
            telegram_id: User's Telegram ID
            username: User's Telegram username
            chat_type: Type of chat they joined (main/leadership)
            invite_context: Optional invite context from join event
            
        Returns:
            ActivationResult with activation status and details
        """
        try:
            logger.info(f"🔄 Processing new chat member: {username} (ID: {telegram_id}) in {chat_type} chat")
            
            # Step 1: Validate invite link if present
            invite_validation = await self._validate_invite_link(invite_context, telegram_id, username)
            
            if not invite_validation["valid"]:
                logger.warning(f"❌ Invalid or missing invite for user {username} (ID: {telegram_id})")
                return ActivationResult(
                    success=False,
                    message=self._create_uninvited_user_message(username, chat_type),
                    error="No valid invite link found",
                    invite_valid=False
                )
            
            # Step 2: Find and activate the player
            activation_result = await self._activate_player_from_invite(
                invite_validation["invite_data"],
                telegram_id,
                username
            )
            
            if activation_result.success:
                logger.info(f"✅ Successfully auto-activated player: {activation_result.player_name} (ID: {activation_result.player_id})")
                
                # Step 3: Log successful activation for audit
                await self._log_activation_event(activation_result, invite_validation["invite_data"])
                
                return activation_result
            else:
                logger.error(f"❌ Failed to activate player for {username}: {activation_result.error}")
                return activation_result
                
        except Exception as e:
            logger.error(f"❌ Error in auto-activation for {username}: {e}")
            return ActivationResult(
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
                logger.debug(f"No invite context provided for {username}")
                return {"valid": False, "reason": "no_invite_context"}
            
            # Extract invite link from context
            invite_link = invite_context.get("invite_link")
            secure_data = invite_context.get("secure_data")
            
            if not invite_link and not secure_data:
                logger.debug(f"No invite link or secure data in context for {username}")
                return {"valid": False, "reason": "no_invite_data"}
            
            # Validate invite link
            invite_data = await self.invite_service.validate_and_use_invite_link(
                invite_link=invite_link or "",
                user_id=str(telegram_id),
                username=username,
                secure_data=secure_data
            )
            
            if invite_data:
                logger.info(f"✅ Valid invite link found for {username}: {invite_data.get('invite_id')}")
                return {
                    "valid": True,
                    "invite_data": invite_data,
                    "invite_id": invite_data.get("invite_id")
                }
            else:
                logger.warning(f"❌ Invalid invite link validation for {username}")
                return {"valid": False, "reason": "invalid_invite"}
                
        except Exception as e:
            logger.error(f"❌ Error validating invite for {username}: {e}")
            return {"valid": False, "reason": "validation_error", "error": str(e)}

    async def _activate_player_from_invite(
        self,
        invite_data: Dict[str, Any],
        telegram_id: int,
        username: str
    ) -> ActivationResult:
        """Activate player based on validated invite data."""
        try:
            # Extract player information from invite
            player_name = invite_data.get("player_name")
            player_phone = invite_data.get("player_phone")
            player_id = invite_data.get("player_id")
            
            if not player_name or not player_id:
                return ActivationResult(
                    success=False,
                    message="❌ Invalid invite data - missing player information.",
                    error="Missing player_name or player_id in invite",
                    invite_valid=True
                )
            
            # Find the player record
            player = await self._find_player_by_invite_data(player_id, player_phone, player_name)
            
            if not player:
                return ActivationResult(
                    success=False,
                    message=f"❌ Player record not found for {player_name}. Please contact team leadership.",
                    error=f"No player found for ID: {player_id}",
                    invite_valid=True
                )
            
            # Check if player is in correct status for activation
            if player.status != "pending":
                if player.status == "active":
                    return ActivationResult(
                        success=True,
                        player_id=player.player_id,
                        player_name=player.name,
                        message=f"👋 Welcome back, {player.name}! You're already activated and ready to go!",
                        was_activated=False,  # Already active
                        invite_valid=True
                    )
                else:
                    return ActivationResult(
                        success=False,
                        player_id=player.player_id,
                        player_name=player.name,
                        message=f"❌ Your account status ({player.status}) prevents activation. Please contact team leadership.",
                        error=f"Player status is {player.status}, not pending",
                        invite_valid=True
                    )
            
            # Update player with Telegram information and activate
            await self._update_and_activate_player(player, telegram_id, username)
            
            return ActivationResult(
                success=True,
                player_id=player.player_id,
                player_name=player.name,
                message=f"🎉 Welcome to the team, {player.name}! You've been automatically activated and are ready to participate!",
                was_activated=True,
                invite_valid=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error activating player from invite: {e}")
            return ActivationResult(
                success=False,
                message="❌ Error during activation. Please contact team leadership.",
                error=str(e),
                invite_valid=True
            )

    async def _find_player_by_invite_data(
        self,
        player_id: str,
        player_phone: Optional[str],
        player_name: str
    ) -> Optional[Player]:
        """Find player record using invite data."""
        try:
            # Try by player_id first (most reliable)
            try:
                player = await self.player_service.get_player_by_id(player_id, self.team_id)
                if player:
                    logger.debug(f"Found player by ID: {player_id}")
                    return player
            except PlayerNotFoundError:
                logger.debug(f"Player not found by ID: {player_id}")
            
            # Try by phone number as fallback
            if player_phone:
                try:
                    players = await self.player_service.get_players_by_phone(player_phone, self.team_id)
                    for player in players:
                        if player.status == "pending":
                            logger.debug(f"Found pending player by phone: {player_phone}")
                            return player
                except Exception:
                    logger.debug(f"No players found by phone: {player_phone}")
            
            logger.warning(f"No player found for ID: {player_id}, phone: {player_phone}, name: {player_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding player by invite data: {e}")
            return None

    async def _update_and_activate_player(
        self,
        player: Player,
        telegram_id: int,
        username: str
    ) -> None:
        """Update player with Telegram info and activate."""
        try:
            # Validate inputs
            if not player or not player.player_id:
                raise ValueError("Invalid player object provided")
            if telegram_id <= 0:
                raise ValueError("Invalid telegram_id provided")
            if not username or not username.strip():
                raise ValueError("Invalid username provided")
            
            # Import enum for status value
            from kickai.core.enums import UserStatus
            
            # Save updated player using correct method signature
            await self.player_service.update_player(
                player_id=player.player_id,
                team_id=player.team_id,
                telegram_id=telegram_id,
                username=username.strip(),
                status=UserStatus.ACTIVE.value,
                updated_at=datetime.utcnow()
            )
            
            logger.info(f"✅ Player {player.name} (ID: {player.player_id}) activated with Telegram ID: {telegram_id}")
            
        except Exception as e:
            logger.error(f"❌ Error updating and activating player {player.player_id}: {e}")
            raise

    async def _log_activation_event(
        self,
        activation_result: ActivationResult,
        invite_data: Dict[str, Any]
    ) -> None:
        """Log successful activation event for audit trail."""
        try:
            event_data = {
                "event_type": "player_auto_activation",
                "player_id": activation_result.player_id,
                "player_name": activation_result.player_name,
                "team_id": self.team_id,
                "invite_id": invite_data.get("invite_id"),
                "was_activated": activation_result.was_activated,
                "timestamp": datetime.utcnow().isoformat(),
                "success": activation_result.success
            }
            
            # Store in audit log collection with team-specific naming
            from kickai.core.firestore_constants import get_team_specific_collection_name
            collection_name = get_team_specific_collection_name(self.team_id, "player_activation_logs")
            
            await self.database.create_document(
                collection_name,
                event_data,
                f"activation_{activation_result.player_id}_{int(datetime.utcnow().timestamp())}"
            )
            
            logger.info(f"📝 Logged activation event for player: {activation_result.player_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to log activation event: {e}")
            # Don't fail the activation if logging fails

    def _create_uninvited_user_message(self, username: str, chat_type: str) -> str:
        """Create appropriate message for uninvited users."""
        if chat_type.lower() in ["main", "main_chat"]:
            return f"""
👋 Hi {username}!

❌ It looks like you joined without a valid invite link. This is a private team chat.

🔗 To join the team:
1. Contact a team leader to invite you with `/addplayer`
2. Use the invite link they provide
3. You'll be automatically activated when you join!

📞 Or contact team leadership directly for assistance.

Please leave this chat and rejoin with a proper invite link. Thanks! ⚽
            """.strip()
        else:
            return f"""
👋 Hi {username}!

❌ This appears to be an unauthorized join to our leadership chat.

🔒 Leadership chat access requires:
- Proper invitation from existing leadership
- Team administrator approval

📞 **Please contact team administration for proper access.**

Thanks for understanding! ⚽
            """.strip()

    def get_welcome_message_context(self, activation_result: ActivationResult) -> Dict[str, Any]:
        """Get context for enhanced welcome message."""
        return {
            "player_name": activation_result.player_name,
            "player_id": activation_result.player_id,
            "was_activated": activation_result.was_activated,
            "activation_success": activation_result.success,
            "team_id": self.team_id
        }