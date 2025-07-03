"""
Player Registration Handler for Telegram

This module provides Telegram-specific player registration functionality
using the new service layer architecture.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..core.exceptions import (
    PlayerError, PlayerNotFoundError, PlayerValidationError, 
    PlayerDuplicateError, create_error_context
)
from ..core.logging import get_logger, performance_timer
from ..services.player_service import get_player_service
from ..services.team_service import get_team_service
from ..database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus


def format_player_name(name: str) -> str:
    """Format player name for display (ALL CAPS)."""
    return name.upper()


class PlayerRegistrationHandler:
    """Telegram-specific player registration handler using new architecture."""
    
    def __init__(self, team_id: str, player_service=None, team_service=None):
        self.team_id = team_id
        self.player_service = player_service or get_player_service()
        self.team_service = team_service or get_team_service()
        self.logger = get_logger("player_registration_handler")
    
    @performance_timer("player_registration_add_player")
    async def add_player(self, name: str, phone: str, position: str, 
                        added_by: str, fa_eligible: bool = False) -> Tuple[bool, str]:
        """
        Add a new player to the team using the new service layer.
        
        Args:
            name: Player's full name
            phone: Player's phone number (primary identifier)
            position: Player's position
            added_by: Telegram user ID of leadership member
            fa_eligible: True if player is eligible for FA registration
            
        Returns:
            (success, message)
        """
        try:
            # Convert position string to enum
            try:
                player_position = PlayerPosition(position.lower())
            except ValueError:
                return False, f"❌ Invalid position: {position}. Valid positions: {', '.join([p.value for p in PlayerPosition])}"
            
            # Create player using service layer
            player = await self.player_service.create_player(
                name=name,
                phone=phone,
                team_id=self.team_id,
                position=player_position,
                role=PlayerRole.PLAYER,
                fa_registered=False
            )
            
            # Update FA eligibility
            if fa_eligible:
                await self.player_service.update_player(
                    player.id, 
                    fa_eligible=True
                )
            
            self.logger.info(
                f"Player added via Telegram: {name} ({phone}) by {added_by}",
                operation="add_player",
                entity_id=player.id,
                team_id=self.team_id,
                user_id=added_by
            )
            
            return True, f"""✅ <b>Player Added Successfully!</b>

👤 <b>Name:</b> {format_player_name(name)}
🆔 <b>Player ID:</b> {player.player_id.upper()}
📱 <b>Phone:</b> {phone}
⚽ <b>Position:</b> {position.title()}
🏆 <b>FA Eligible:</b> {'Yes' if fa_eligible else 'No'}
📊 <b>Status:</b> Pending Onboarding

💡 <b>Next Steps:</b>
• Send invitation message to player
• Player completes onboarding via Telegram
• Admin approves player for team access"""
            
        except PlayerDuplicateError as e:
            return False, f"❌ Player with phone {phone} already exists"
        except PlayerValidationError as e:
            return False, f"❌ Validation error: {str(e)}"
        except Exception as e:
            self.logger.error("Failed to add player via Telegram", error=e, team_id=self.team_id)
            return False, f"❌ Error adding player: {str(e)}"
    
    @performance_timer("player_registration_remove_player")
    async def remove_player(self, identifier: str, removed_by: str) -> Tuple[bool, str]:
        """
        Remove a player from the team using the new service layer.
        
        Args:
            identifier: Player's phone number or player ID (e.g., "07123456789" or "JS1")
            removed_by: Telegram user ID of leadership member
            
        Returns:
            (success, message)
        """
        try:
            player = None
            
            # Check if identifier is a player ID (contains letters) or phone number
            if any(char.isalpha() for char in identifier):
                # It's a player ID, find player by ID (case-insensitive)
                players = await self.player_service.get_team_players(self.team_id)
                for p in players:
                    if p.player_id.lower() == identifier.lower():
                        player = p
                        break
                
                if not player:
                    return False, f"❌ Player with ID {identifier} not found"
            else:
                # It's a phone number
                player = await self.player_service.get_player_by_phone(identifier, self.team_id)
                if not player:
                    return False, f"❌ Player with phone {identifier} not found"
            
            # Delete player using service layer
            success = await self.player_service.delete_player(player.id)
            if not success:
                return False, "❌ Failed to remove player from database"
            
            self.logger.info(
                f"Player removed via Telegram: {player.name} ({player.phone}) by {removed_by}",
                operation="remove_player",
                entity_id=player.id,
                team_id=self.team_id,
                user_id=removed_by
            )
            
            return True, f"✅ Player {format_player_name(player.name)} removed successfully"
            
        except PlayerNotFoundError:
            return False, f"❌ Player not found"
        except Exception as e:
            self.logger.error("Failed to remove player via Telegram", error=e, team_id=self.team_id)
            return False, f"❌ Error removing player: {str(e)}"
    
    @performance_timer("player_registration_get_all_players")
    async def get_all_players(self) -> List[Player]:
        """Get all players for the team using the new service layer."""
        try:
            players = await self.player_service.get_team_players(self.team_id)
            return players
        except Exception as e:
            self.logger.error("Failed to get all players via Telegram", error=e, team_id=self.team_id)
            return []
    
    @performance_timer("player_registration_get_player_by_phone")
    async def get_player_by_phone(self, phone: str) -> Optional[Player]:
        """Get player by phone number using the new service layer."""
        try:
            player = await self.player_service.get_player_by_phone(phone, self.team_id)
            return player
        except Exception as e:
            self.logger.error("Failed to get player by phone via Telegram", error=e, team_id=self.team_id)
            return None
    
    @performance_timer("player_registration_update_player_status")
    async def update_player_status(self, phone: str, status: str) -> Tuple[bool, str]:
        """Update player status using the new service layer."""
        try:
            player = await self.player_service.get_player_by_phone(phone, self.team_id)
            if not player:
                return False, f"❌ Player with phone {phone} not found"
            
            # Update player status
            updated_player = await self.player_service.update_player(
                player.id, 
                status=status
            )
            
            self.logger.info(
                f"Player status updated via Telegram: {player.name} -> {status}",
                operation="update_player_status",
                entity_id=player.id,
                team_id=self.team_id
            )
            
            return True, f"✅ Player {format_player_name(player.name)} status updated to {status}"
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {phone} not found"
        except Exception as e:
            self.logger.error("Failed to update player status via Telegram", error=e, team_id=self.team_id)
            return False, f"❌ Error updating player status: {str(e)}"
    
    @performance_timer("player_registration_generate_invite_link")
    async def generate_invite_link(self, phone: str, telegram_group_invite_base: str) -> Tuple[bool, str]:
        """Generate invite link for a player using the new service layer."""
        try:
            player = await self.player_service.get_player_by_phone(phone, self.team_id)
            if not player:
                return False, f"❌ Player with phone {phone} not found"
            
            # Generate invite link
            invite_link = f"{telegram_group_invite_base}?start={player.player_id}"
            
            # Update player with invite link
            updated_player = await self.player_service.generate_invite_link(player.id, invite_link)
            
            self.logger.info(
                f"Invite link generated for player: {player.name}",
                operation="generate_invite_link",
                entity_id=player.id,
                team_id=self.team_id
            )
            
            return True, f"✅ Invite link generated for {format_player_name(player.name)}: {invite_link}"
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {phone} not found"
        except Exception as e:
            self.logger.error("Failed to generate invite link via Telegram", error=e, team_id=self.team_id)
            return False, f"❌ Error generating invite link: {str(e)}"

    @performance_timer("player_registration_generate_invitation_message")
    async def generate_invitation_message(self, phone: str, team_name: Optional[str] = None, 
                                        telegram_group_invite_base: Optional[str] = None) -> Tuple[bool, str]:
        """
        Generate a formatted invitation message for a player.
        
        Args:
            phone: Player's phone number
            team_name: Team name for the invitation (optional, will be fetched if not provided)
            telegram_group_invite_base: Base URL for Telegram group invite (optional)
            
        Returns:
            (success, message)
        """
        try:
            player = await self.player_service.get_player_by_phone(str(phone), self.team_id)
            if not player:
                return False, f"❌ Player with phone {str(phone)} not found"
            
            # Get actual team name if not provided
            if not team_name:
                try:
                    team = await self.team_service.get_team(self.team_id)
                    team_name = team.name if team and team.name else "KICKAI Team"
                except Exception as e:
                    self.logger.warning(f"Could not get team name: {e}")
                    team_name = "KICKAI Team"
            team_name = str(team_name) if team_name else "KICKAI Team"
            
            # Get actual Telegram link if not provided
            if not telegram_group_invite_base:
                try:
                    from src.core.bot_config_manager import get_bot_config_manager
                    manager = get_bot_config_manager()
                    bot_config = manager.get_bot_config(self.team_id)
                    if bot_config and bot_config.main_chat_id:
                        # Create a proper Telegram group invite link
                        invite_link = await self._create_telegram_invite_link(bot_config)
                    else:
                        error_msg = f"CRITICAL ERROR: Main chat ID not available for team {self.team_id}. Cannot generate invitation link."
                        self.logger.error(error_msg)
                        raise ValueError(error_msg)
                except Exception as e:
                    error_msg = f"CRITICAL ERROR: Failed to get bot configuration for team {self.team_id}: {e}"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)
            else:
                invite_link = str(telegram_group_invite_base) if telegram_group_invite_base else ""
            
            # Create invitation message
            invitation_message = f"""🎉 <b>Welcome to {team_name}!</b>

Hi {format_player_name(player.name)},

You've been invited to join {team_name}! We're excited to have you on the team.

📋 <b>Your Details:</b>
• Name: {format_player_name(player.name)}
• Position: {player.position.value.title()}
• Player ID: {player.player_id.upper()}

🔗 <b>Join Our Main Team Chat:</b>
{invite_link}

📱 <b>Next Steps:</b>
1. Click the link above to join our main team group directly
2. Introduce yourself in the group
3. Complete your onboarding process
4. Get ready for training and matches!

⚠️ <b>Note:</b> This invitation is for our main team chat only. Leadership chat access is managed separately.

⚽ <b>What to Expect:</b>
• Team announcements and updates
• Training schedules
• Match information
• Team communication

If you have any questions, please contact the team leadership.

Welcome aboard! 🏆

- {team_name} Management"""
            
            self.logger.info(
                f"Invitation message generated for player: {player.name}",
                operation="generate_invitation_message",
                entity_id=player.id,
                team_id=self.team_id
            )
            
            return True, invitation_message
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {str(phone)} not found"
        except Exception as e:
            self.logger.error("Failed to generate invitation message", error=e, team_id=self.team_id)
            return False, f"❌ Error generating invitation message: {str(e)}"
    
    @performance_timer("player_registration_player_joined_via_invite")
    async def player_joined_via_invite(self, player_id: str, telegram_user_id: str, 
                                     telegram_username: str = None) -> Tuple[bool, str]:
        """Handle player joining via invite link using the new service layer."""
        try:
            # Find player by player_id
            players = await self.player_service.get_team_players(self.team_id)
            player = None
            for p in players:
                if p.player_id == player_id:
                    player = p
                    break
            
            if not player:
                return False, f"❌ Player with ID {player_id} not found"
            
            # Update player with Telegram info and start onboarding
            updates = {
                'telegram_id': telegram_user_id,
                'onboarding_status': OnboardingStatus.IN_PROGRESS.value
            }
            if telegram_username:
                updates['telegram_username'] = telegram_username
            
            updated_player = await self.player_service.update_player(player.id, **updates)
            
            self.logger.info(
                f"Player joined via invite: {player.name} ({telegram_user_id})",
                operation="player_joined_via_invite",
                entity_id=player.id,
                team_id=self.team_id,
                user_id=telegram_user_id
            )
            
            return True, f"✅ Welcome {format_player_name(player.name)}! Let's get you set up. Please complete your profile."
            
        except Exception as e:
            self.logger.error("Failed to handle player join via invite", error=e, team_id=self.team_id)
            return False, f"❌ Error processing join: {str(e)}"
    
    @performance_timer("player_registration_get_onboarding_message")
    async def get_onboarding_message(self, player_id: str) -> Tuple[bool, str]:
        """Get onboarding message for a player using the new service layer."""
        try:
            # Find player by player_id
            players = await self.player_service.get_team_players(self.team_id)
            player = None
            for p in players:
                if p.player_id == player_id:
                    player = p
                    break
            
            if not player:
                return False, f"❌ Player with ID {player_id} not found"
            
            # Get team info for personalized message
            team = await self.team_service.get_team(self.team_id)
            team_name = team.name if team else "the team"
            
            # Generate onboarding message based on current status
            if player.onboarding_status == OnboardingStatus.PENDING:
                message = f"""🎉 Welcome to {team_name}, {format_player_name(player.name)}!

I'm here to help you complete your registration. Let's start by confirming your details:

📋 <b>Current Information:</b>
• Name: {format_player_name(player.name)}
• Phone: {player.phone}
• Position: {player.position.value if hasattr(player.position, 'value') else player.position}

Please confirm if this information is correct by replying with 'yes' or 'no'."""
            
            elif player.onboarding_status == OnboardingStatus.IN_PROGRESS:
                message = f"""🔄 Onboarding in progress for {format_player_name(player.name)}

Please continue with the onboarding process. If you need help, type 'help'."""
            
            else:
                message = f"""✅ Onboarding completed for {format_player_name(player.name)}

You're all set up! You can now use team features."""
            
            return True, message
            
        except Exception as e:
            self.logger.error("Failed to get onboarding message", error=e, team_id=self.team_id)
            return False, f"❌ Error getting onboarding message: {str(e)}"
    
    @performance_timer("player_registration_process_onboarding_response")
    async def process_onboarding_response(self, player_id: str, response: str) -> Tuple[bool, str]:
        """
        Process onboarding response and move to next step or complete onboarding.
        
        Args:
            player_id: Player ID
            response: Player's response to onboarding question
            
        Returns:
            (success, message)
        """
        try:
            # Get player
            player = await self.player_service.get_player(player_id)
            if not player:
                return False, f"❌ Player {player_id} not found"
            
            # Handle different onboarding steps
            if player.onboarding_status == OnboardingStatus.PENDING:
                # First step: Confirm participation
                if response.lower() in ['yes', 'confirm', 'y']:
                    updated_player = await self.player_service.update_player(
                        player.id,
                        onboarding_status=OnboardingStatus.IN_PROGRESS,
                        onboarding_step="emergency_contact"
                    )
                    return True, "✅ Great! Now please provide your emergency contact (name and phone number):"
                else:
                    return False, "❌ Please confirm your participation to continue with onboarding."
            
            elif player.onboarding_status == OnboardingStatus.IN_PROGRESS:
                if player.onboarding_step == "emergency_contact":
                    # Validate emergency contact format
                    if not self._validate_emergency_contact(response):
                        return False, "❌ Please provide emergency contact in format: 'Name, Phone' (e.g., 'Jane Smith, 07987654321')"
                    
                    updated_player = await self.player_service.update_player(
                        player.id,
                        emergency_contact=response,
                        onboarding_step="date_of_birth"
                    )
                    return True, "✅ Emergency contact saved! Now please provide your date of birth (DD/MM/YYYY):"
                
                elif player.onboarding_step == "date_of_birth":
                    # Validate date format
                    if not self._validate_date_of_birth(response):
                        return False, "❌ Please provide date of birth in format DD/MM/YYYY (e.g., 15/05/1995)"
                    
                    updated_player = await self.player_service.update_player(
                        player.id,
                        date_of_birth=response,
                        onboarding_step="fa_eligibility"
                    )
                    return True, "✅ Date of birth saved! Are you eligible for FA registration? (yes/no):"
                
                elif player.onboarding_step == "fa_eligibility":
                    fa_eligible = response.lower() in ['yes', 'y', 'true']
                    # Update player without onboarding_step to avoid type issues
                    updated_player = await self.player_service.update_player(
                        player.id,
                        fa_eligible=fa_eligible,
                        onboarding_status=OnboardingStatus.COMPLETED
                    )
                    return True, f"✅ Onboarding completed! Welcome to the team, {format_player_name(player.name)}! You are now ready to play."
            
            return False, "❌ Invalid onboarding state"
            
        except Exception as e:
            self.logger.error("Failed to process onboarding response", error=e, player_id=player_id)
            return False, f"❌ Error processing response: {str(e)}"

    @performance_timer("player_registration_admin_approve_player")
    async def approve_player(self, player_id: str, approved_by: str) -> Tuple[bool, str]:
        """
        Approve a player for the team (admin/coach workflow).
        
        Args:
            player_id: Player ID to approve
            approved_by: Telegram user ID of admin/coach
            
        Returns:
            (success, message)
        """
        try:
            # Get player
            player = await self.player_service.get_player(player_id)
            if not player:
                return False, f"❌ Player {player_id} not found"
            
            # Check if player needs approval
            if player.onboarding_status != OnboardingStatus.PENDING_APPROVAL:
                return False, f"❌ Player {format_player_name(player.name)} does not require approval (status: {player.onboarding_status.value})"
            
            # Approve player
            updated_player = await self.player_service.update_player(
                player.id,
                onboarding_status=OnboardingStatus.PENDING,
                role=PlayerRole.PLAYER
            )
            
            self.logger.info(
                f"Player approved by admin: {player.name} by {approved_by}",
                operation="approve_player",
                entity_id=player.id,
                team_id=self.team_id,
                user_id=approved_by
            )
            
            return True, f"✅ Player {format_player_name(player.name)} approved successfully! They can now start onboarding."
            
        except Exception as e:
            self.logger.error("Failed to approve player", error=e, player_id=player_id)
            return False, f"❌ Error approving player: {str(e)}"

    @performance_timer("player_registration_admin_reject_player")
    async def reject_player(self, player_id: str, rejected_by: str, reason: Optional[str] = None) -> Tuple[bool, str]:
        """
        Reject a player from the team (admin/coach workflow).
        
        Args:
            player_id: Player ID to reject
            rejected_by: Telegram user ID of admin/coach
            reason: Optional reason for rejection
            
        Returns:
            (success, message)
        """
        try:
            # Get player
            player = await self.player_service.get_player(player_id)
            if not player:
                return False, f"❌ Player {player_id} not found"
            
            # Check if player needs approval
            if player.onboarding_status != OnboardingStatus.PENDING_APPROVAL:
                return False, f"❌ Player {format_player_name(player.name)} does not require approval (status: {player.onboarding_status.value})"
            
            # Reject player
            updated_player = await self.player_service.update_player(
                player.id,
                onboarding_status=OnboardingStatus.FAILED
            )
            
            self.logger.info(
                f"Player rejected by admin: {player.name} by {rejected_by}",
                operation="reject_player",
                entity_id=player.id,
                team_id=self.team_id,
                user_id=rejected_by
            )
            
            reason_msg = f" Reason: {reason}" if reason else ""
            return True, f"✅ Player {format_player_name(player.name)} rejected.{reason_msg}"
            
        except Exception as e:
            self.logger.error("Failed to reject player", error=e, player_id=player_id)
            return False, f"❌ Error rejecting player: {str(e)}"

    @performance_timer("player_registration_get_pending_approvals")
    async def get_pending_approvals(self) -> Tuple[bool, str]:
        """Get list of players pending approval."""
        try:
            # Get all players with pending approval status
            players = await self.player_service.get_team_players(self.team_id)
            pending_players = [p for p in players if p.onboarding_status == OnboardingStatus.PENDING_APPROVAL]
            
            if not pending_players:
                return True, "✅ No players pending approval."
            
            message = "📋 <b>Players Pending Approval:</b>\n\n"
            for player in pending_players:
                message += f"• <b>{format_player_name(player.name)}</b> ({player.player_id.upper()})\n"
                message += f"  📱 Phone: {player.phone or 'Not provided'}\n"
                message += f"  ⚽ Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}\n"
                if player.telegram_username:
                    message += f"  📱 Telegram: @{player.telegram_username}\n"
                message += "\n"
            
            message += "💡 <b>Commands:</b>\n"
            message += "• `/approve <player_id>` - Approve player\n"
            message += "• `/reject <player_id> [reason]` - Reject player"
            
            return True, message
            
        except Exception as e:
            self.logger.error(f"Error getting pending approvals: {e}")
            return False, f"❌ Error getting pending approvals: {str(e)}"

    def _validate_emergency_contact(self, contact: str) -> bool:
        """Validate emergency contact format."""
        # Expected format: "Name, Phone"
        parts = contact.split(',')
        if len(parts) != 2:
            return False
        
        name, phone = parts[0].strip(), parts[1].strip()
        if not name or not phone:
            return False
        
        # Validate phone number
        return self._validate_phone(phone)

    def _validate_date_of_birth(self, dob: str) -> bool:
        """Validate date of birth format (DD/MM/YYYY)."""
        try:
            # Check format
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', dob):
                return False
            
            # Parse date
            day, month, year = map(int, dob.split('/'))
            datetime(year, month, day)  # This will raise ValueError if invalid
            
            # Check reasonable range (e.g., 16-80 years old)
            current_year = datetime.now().year
            if year < current_year - 80 or year > current_year - 16:
                return False
            
            return True
        except (ValueError, TypeError):
            return False

    def _validate_phone(self, phone: str) -> bool:
        """Validate UK phone number format."""
        pattern = r'^07\d{9}$'
        return bool(re.match(pattern, phone.replace(' ', '')))
    
    async def _create_telegram_invite_link(self, bot_config) -> str:
        """Create a Telegram group invite link using the Bot API."""
        try:
            import requests
            
            # Create invite link using Telegram Bot API
            url = f"https://api.telegram.org/bot{bot_config.token}/createChatInviteLink"
            data = {
                'chat_id': bot_config.main_chat_id,
                'name': 'KICKAI Team Invite',
                'creates_join_request': False,
                'expire_date': None,  # No expiration
                'member_limit': None  # No member limit
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok') and result.get('result'):
                invite_link = result['result']['invite_link']
                self.logger.info(f"Created Telegram invite link: {invite_link}")
                return invite_link
            else:
                error_msg = f"Failed to create invite link: {result.get('description', 'Unknown error')}"
                self.logger.error(error_msg)
                # Fallback to a placeholder link
                return f"https://t.me/+{bot_config.main_chat_id.replace('-', '')}"
                
        except Exception as e:
            self.logger.error(f"Error creating Telegram invite link: {e}")
            # Fallback to a placeholder link
            return f"https://t.me/+{bot_config.main_chat_id.replace('-', '')}"

    @performance_timer("player_registration_get_player_info")
    async def get_player_info(self, telegram_user_id: str) -> Tuple[bool, str]:
        """Get player information for a Telegram user using the new service layer."""
        try:
            # Find player by Telegram ID
            players = await self.player_service.get_team_players(self.team_id)
            player = None
            for p in players:
                if p.telegram_id == telegram_user_id:
                    player = p
                    break
            
            if not player:
                return False, "❌ Player not found. Please contact team leadership."
            
            # Format player information
            info = f"""📋 <b>Player Information</b>

👤 <b>Name:</b> {format_player_name(player.name)}
🆔 <b>Player ID:</b> {player.player_id.upper()}
📱 <b>Phone:</b> {player.phone}
⚽ <b>Position:</b> {player.position.value if hasattr(player.position, 'value') else player.position}
📧 <b>Email:</b> {player.email or 'Not provided'}
🏆 <b>FA Registered:</b> {'Yes' if player.fa_registered else 'No'}
✅ <b>FA Eligible:</b> {'Yes' if player.fa_eligible else 'No'}
📊 <b>Status:</b> {player.onboarding_status.value if hasattr(player.onboarding_status, 'value') else player.onboarding_status}
📅 <b>Date Added:</b> {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}"""
            
            return True, info
            
        except Exception as e:
            self.logger.error("Failed to get player info", error=e, team_id=self.team_id)
            return False, f"❌ Error getting player information: {str(e)}"

    @performance_timer("player_registration_get_player_stats")
    async def get_player_stats(self) -> Dict:
        """Get player statistics using the new service layer."""
        try:
            players = await self.player_service.get_team_players(self.team_id)
            
            stats = {
                'total_players': len(players),
                'active_players': len([p for p in players if p.onboarding_status == OnboardingStatus.COMPLETED]),
                'pending_players': len([p for p in players if p.onboarding_status == OnboardingStatus.PENDING]),
                'pending_approval': len([p for p in players if p.onboarding_status == OnboardingStatus.PENDING_APPROVAL]),
                'fa_registered': len([p for p in players if p.fa_registered]),
                'fa_eligible': len([p for p in players if p.fa_eligible]),
                'positions': {},
                'recent_additions': []
            }
            
            # Position breakdown
            for player in players:
                position = player.position.value if hasattr(player.position, 'value') else player.position
                stats['positions'][position] = stats['positions'].get(position, 0) + 1
            
            # Recent additions (last 7 days)
            recent_cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            for player in players:
                if player.created_at and player.created_at >= recent_cutoff:
                    stats['recent_additions'].append({
                        'name': player.name,
                        'date': player.created_at.strftime('%Y-%m-%d')
                    })
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get player stats", error=e, team_id=self.team_id)
            return {
                'total_players': 0,
                'active_players': 0,
                'pending_players': 0,
                'pending_approval': 0,
                'fa_registered': 0,
                'fa_eligible': 0,
                'positions': {},
                'recent_additions': []
            }


class PlayerCommandHandler:
    """Telegram command handler for player operations using new architecture."""
    
    def __init__(self, player_handler: PlayerRegistrationHandler):
        self.player_handler = player_handler
        self.logger = get_logger("player_command_handler")
    
    async def handle_command(self, command: str, user_id: str, is_leadership_chat: bool = False) -> str:
        """Handle player registration commands."""
        try:
            command = command.strip().lower()
            
            if command.startswith('/add '):
                return await self._handle_add_player(command, user_id)
            elif command.startswith('/remove '):
                return await self._handle_remove_player(command, user_id)
            elif command == '/list':
                return await self._handle_list_players()
            elif command.startswith('/status '):
                return await self._handle_player_status(command)
            elif command == '/stats':
                return await self._handle_player_stats()
            elif command.startswith('/invite '):
                return await self._handle_generate_invitation_message(command)
            elif command == '/myinfo':
                return await self._handle_myinfo(user_id)
            elif command.startswith('/approve '):
                return await self._handle_approve_player(command, user_id)
            elif command.startswith('/reject '):
                return await self._handle_reject_player(command, user_id)
            elif command == '/pending':
                return await self._handle_pending_approvals()
            elif command == '/checkfa':
                return await self._handle_check_fa_registration()
            elif command == '/dailystatus':
                return await self._handle_daily_status()
            elif command == '/help':
                return self._get_help_message(is_leadership_chat)
            elif command.startswith('/start'):
                return await self._handle_start_command(command, user_id)
            else:
                return "❌ Unknown command. Type /help for available commands."
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"

    async def _handle_add_player(self, command: str, user_id: str) -> str:
        """Handle /add command."""
        try:
            # Remove the /add part and split the rest
            command_parts = command[5:].strip()  # Remove "/add "
            
            # Use a more sophisticated parsing approach
            # Look for phone number pattern to separate name from phone
            import re
            phone_pattern = r'\b(?:07\d{9}|08\d{9}|\+44\d{10}|01\d{8,9}|02\d{8,9})\b'
            phone_match = re.search(phone_pattern, command_parts)
            
            if not phone_match:
                return "❌ Usage: /add &lt;name&gt; &lt;phone&gt; &lt;position&gt; [fa_eligible]\n\nPlease provide a valid UK phone number (e.g., 07123456789, +447123456789)"
            
            phone = phone_match.group()
            phone_start = phone_match.start()
            phone_end = phone_match.end()
            
            # Extract position (last word after phone)
            after_phone = command_parts[phone_end:].strip()
            if not after_phone:
                return "❌ Usage: /add &lt;name&gt; &lt;phone&gt; &lt;position&gt; [fa_eligible]\n\nPlease provide a position (goalkeeper, defender, midfielder, forward, striker, utility)"
            
            # Split after phone to get position and optional fa_eligible
            position_parts = after_phone.split()
            position = position_parts[0]
            fa_eligible = len(position_parts) > 1 and position_parts[1].lower() in ['true', 'yes', 'y']
            
            # Extract name (everything before phone)
            name = command_parts[:phone_start].strip()
            if not name:
                return "❌ Usage: /add &lt;name&gt; &lt;phone&gt; &lt;position&gt; [fa_eligible]\n\nPlease provide a player name"
            
            success, message = await self.player_handler.add_player(
                name, phone, position, user_id, fa_eligible
            )
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle add player command", error=e, user_id=user_id)
            return f"❌ Error adding player: {str(e)}"
    
    async def _handle_remove_player(self, command: str, user_id: str) -> str:
        """Handle /removeplayer command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /removeplayer &lt;phone&gt;"
            
            phone = parts[1]
            success, message = await self.player_handler.remove_player(phone, user_id)
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle remove player command", error=e, user_id=user_id)
            return f"❌ Error removing player: {str(e)}"
    
    async def _handle_list_players(self) -> str:
        """Handle /listplayers command."""
        try:
            players = await self.player_handler.get_all_players()
            
            if not players:
                return "📋 No players found for this team."
            
            # Group by status
            active_players = [p for p in players if p.onboarding_status == OnboardingStatus.COMPLETED]
            pending_players = [p for p in players if p.onboarding_status == OnboardingStatus.PENDING]
            
            message = "📋 <b>Team Players</b>\n\n"
            
            if active_players:
                message += "✅ <b>Active Players:</b>\n"
                for player in active_players:
                    message += f"• {format_player_name(player.name)} ({player.player_id.upper()}) - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
                message += "\n"
            
            if pending_players:
                message += "⏳ <b>Pending Players:</b>\n"
                for player in pending_players:
                    message += f"• {format_player_name(player.name)} ({player.player_id.upper()}) - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
            
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle list players command", error=e)
            return f"❌ Error listing players: {str(e)}"
    
    async def _handle_player_status(self, command: str) -> str:
        """Handle /playerstatus command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /playerstatus &lt;phone&gt;"
            
            phone = parts[1]
            player = await self.player_handler.get_player_by_phone(phone)
            
            if not player:
                return f"❌ Player with phone {phone} not found"
            
            status_message = f"""📊 <b>Player Status</b>

👤 <b>Name:</b> {format_player_name(player.name)}
🆔 <b>Player ID:</b> {player.player_id.upper()}
📱 <b>Phone:</b> {player.phone}
⚽ <b>Position:</b> {player.position.value if hasattr(player.position, 'value') else player.position}
📊 <b>Onboarding Status:</b> {player.onboarding_status.value if hasattr(player.onboarding_status, 'value') else player.onboarding_status}
🏆 <b>FA Registered:</b> {'Yes' if player.fa_registered else 'No'}
✅ <b>FA Eligible:</b> {'Yes' if player.fa_eligible else 'No'}
📅 <b>Date Added:</b> {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}"""
            
            return status_message
            
        except Exception as e:
            self.logger.error("Failed to handle player status command", error=e)
            return f"❌ Error getting player status: {str(e)}"
    
    async def _handle_player_stats(self) -> str:
        """Handle /playerstats command."""
        try:
            stats = await self.player_handler.get_player_stats()
            
            message = f"""📊 <b>Team Statistics</b>

👥 <b>Total Players:</b> {stats['total_players']}
✅ <b>Active Players:</b> {stats['active_players']}
⏳ <b>Pending Players:</b> {stats['pending_players']}
🏆 <b>FA Registered:</b> {stats['fa_registered']}
✅ <b>FA Eligible:</b> {stats['fa_eligible']}

⚽ <b>Position Breakdown:</b>"""
            
            for position, count in stats['positions'].items():
                message += f"\n• {position}: {count}"
            
            if stats['recent_additions']:
                message += "\n\n🆕 <b>Recent Additions:</b>"
                for addition in stats['recent_additions'][:5]:  # Show last 5
                    message += f"\n• {format_player_name(addition['name'])} ({addition['date']})"
            
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle player stats command", error=e)
            return f"❌ Error getting player stats: {str(e)}"
    
    async def _handle_generate_invite(self, command: str) -> str:
        """Handle /generateinvite command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /generateinvite &lt;phone&gt;"
            
            phone = parts[1]
            # Note: telegram_group_invite_base should be configured
            invite_base = "https://t.me/joinchat/your_group_invite"
            
            success, message = await self.player_handler.generate_invite_link(phone, invite_base)
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle generate invite command", error=e)
            return f"❌ Error generating invite: {str(e)}"
    
    async def _handle_generate_invitation_message(self, command: str) -> str:
        """Handle /invitation command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /invite &lt;phone_or_player_id&gt;"
            
            identifier = parts[1]
            
            # Check if it's a player ID (contains letters) or phone number
            if any(char.isalpha() for char in identifier):
                # It's a player ID, find player by ID (case-insensitive)
                players = await self.player_handler.get_all_players()
                player = None
                for p in players:
                    if p.player_id.lower() == identifier.lower():
                        player = p
                        break
                
                if not player:
                    return f"❌ Player with ID {identifier} not found"
                
                success, message = await self.player_handler.generate_invitation_message(player.phone)
            else:
                # It's a phone number
                success, message = await self.player_handler.generate_invitation_message(identifier)
            
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle generate invitation message command", error=e)
            return f"❌ Error generating invitation message: {str(e)}"
    
    async def _handle_myinfo(self, user_id: str) -> str:
        """Handle /myinfo command."""
        try:
            success, message = await self.player_handler.get_player_info(user_id)
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle myinfo command", error=e, user_id=user_id)
            return f"❌ Error getting player info: {str(e)}"
    
    async def _handle_approve_player(self, command: str, user_id: str) -> str:
        """Handle /approve command for admin approval."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /approve &lt;player_id&gt;"
            
            player_id = parts[1].upper()
            success, message = await self.player_handler.approve_player(player_id, user_id)
            return message
            
        except Exception as e:
            return f"❌ Error approving player: {str(e)}"

    async def _handle_reject_player(self, command: str, user_id: str) -> str:
        """Handle /reject command for admin rejection."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /reject &lt;player_id&gt; [reason]"
            
            player_id = parts[1].upper()
            reason = " ".join(parts[2:]) if len(parts) > 2 else None
            
            success, message = await self.player_handler.reject_player(player_id, user_id, reason)
            return message
            
        except Exception as e:
            return f"❌ Error rejecting player: {str(e)}"

    async def _handle_pending_approvals(self) -> str:
        """Handle /pending command to show pending approvals."""
        try:
            success, message = await self.player_handler.get_pending_approvals()
            return message
            
        except Exception as e:
            return f"❌ Error getting pending approvals: {str(e)}"

    async def _handle_check_fa_registration(self) -> str:
        """Handle /checkfa command."""
        try:
            from src.services.fa_registration_checker import run_fa_registration_check
            
            # Get team ID from player handler
            team_id = self.player_handler.team_id
            
            # Run FA registration check
            updates = await run_fa_registration_check(team_id, self.player_handler.player_service)
            
            if updates:
                message = "✅ <b>FA Registration Check Complete</b>\n\n"
                message += f"Found {len(updates)} new FA registrations:\n"
                for player_id, registered in updates.items():
                    if registered:
                        message += f"• Player {player_id} is now FA registered!\n"
            else:
                message = "ℹ️ <b>FA Registration Check Complete</b>\n\n"
                message += "No new FA registrations found."
            
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle FA registration check command", error=e)
            return f"❌ Error checking FA registration: {str(e)}"

    async def _handle_daily_status(self) -> str:
        """Handle /dailystatus command."""
        try:
            from src.services.daily_status_service import DailyStatusService
            from src.core.bot_config_manager import get_bot_config_manager
            
            # Get team ID and bot token
            team_id = self.player_handler.team_id
            manager = get_bot_config_manager()
            bot_config = manager.get_bot_config(team_id)
            
            if not bot_config:
                return "❌ Bot configuration not found for this team."
            
            # Create daily status service
            service = DailyStatusService(
                player_service=self.player_handler.player_service,
                team_service=self.player_handler.team_service,
                team_member_service=None,  # Not needed for this operation
                bot_token=bot_config.token
            )
            
            # Generate stats
            team_stats = await service.generate_team_stats(team_id)
            
            # Format message
            message = service.format_daily_status_message(team_stats)
            
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle daily status command", error=e)
            return f"❌ Error generating daily status: {str(e)}"

    async def _handle_start_command(self, command: str, user_id: str) -> str:
        """Handle /start command with optional player ID parameter."""
        try:
            parts = command.split()
            
            # If no parameters, show welcome message
            if len(parts) == 1:
                return """🎉 <b>Welcome to KICKAI Team Management Bot!</b>

I'm here to help you manage your football team. Here's what I can do:

📋 <b>Player Management:</b>
• Add and remove players
• Track player status and statistics
• Generate invitation messages
• Manage player registrations

👑 <b>Leadership Features:</b>
• Approve/reject player registrations
• View pending approvals
• Team management tools

💡 <b>Getting Started:</b>
• Type `/help` to see all available commands
• Use `/add &lt;name&gt; &lt;phone&gt; &lt;position&gt;` to add a player
• Use `/list` to see all team players

⚽ <b>Need Help?</b>
Type `/help` for a complete list of commands and examples.

🏆 <b>Team Access:</b>
• Main team chat: For all players and general communication
• Leadership chat: For team management (access granted separately)

Welcome to the team! 🏆"""
            
            # If there's a player ID parameter, handle player join
            if len(parts) > 1:
                player_id = parts[1]
                success, message = await self.player_handler.player_joined_via_invite(player_id, user_id)
                
                if success:
                    # Get onboarding message for the player
                    onboarding_success, onboarding_message = await self.player_handler.get_onboarding_message(player_id)
                    if onboarding_success:
                        return f"{message}\n\n{onboarding_message}"
                    else:
                        return f"{message}\n\n❌ Error getting onboarding message: {onboarding_message}"
                else:
                    return f"❌ {message}\n\n💡 Please contact the team admin if you believe this is an error."
            
            return "❌ Invalid start command format. Use `/start` or `/start &lt;player_id&gt;`"
            
        except Exception as e:
            self.logger.error("Failed to handle start command", error=e, user_id=user_id)
            return f"❌ Error processing start command: {str(e)}"

    def _get_help_message(self, is_leadership_chat: bool = False) -> str:
        """Get help message with context-aware commands."""
        if is_leadership_chat:
            return """🤖 <b>KICKAI Player Registration Bot (Leadership)</b>

📋 <b>Available Commands:</b>

👥 <b>Player Management:</b>
• `/add &lt;name&gt; &lt;phone&gt; &lt;position&gt;` - Add a new player
• `/remove &lt;phone&gt;` - Remove a player
• `/list` - List all players
• `/status &lt;phone&gt;` - Get player status
• `/stats` - Get team statistics
• `/invite &lt;phone_or_player_id&gt;` - Generate invitation message

👤 <b>Player Commands:</b>
• `/myinfo` - Get your player information

👨‍💼 <b>Admin Commands:</b>
• `/approve &lt;player_id&gt;` - Approve a player
• `/reject &lt;player_id&gt; [reason]` - Reject a player
• `/pending` - List players pending approval
• `/checkfa` - Check FA registration status
• `/dailystatus` - Generate daily team status report

❓ <b>Help:</b>
• `/help` - Show this help message

📝 <b>Examples:</b>
• `/add John Smith 07123456789 midfielder`
• `/status 07123456789`
• `/approve JS1`
• `/reject JS1 Not available for matches`

⚽ <b>Valid Positions:</b> goalkeeper, defender, midfielder, forward, utility"""
        else:
            return """🤖 <b>KICKAI Player Registration Bot</b>

📋 <b>Available Commands:</b>

👥 <b>Player Information:</b>
• `/list` - List all players
• `/myinfo` - Get your player information
• `/status &lt;phone&gt;` - Get player status
• `/stats` - Get team statistics

❓ <b>Help:</b>
• `/help` - Show this help message

📝 <b>Examples:</b>
• `/status 07123456789`
• `/myinfo`

💡 <b>Note:</b> Admin commands are only available in the leadership chat.""" 