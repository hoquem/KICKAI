"""
Player Registration Handler for Telegram

This module provides Telegram-specific player registration functionality
using the new service layer architecture.

UPDATED: Now uses the improved onboarding workflow for better user experience and PRD compliance.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from ..core.exceptions import (
    PlayerError, PlayerNotFoundError, PlayerValidationError, 
    PlayerDuplicateError, create_error_context
)
from ..services.player_service import get_player_service
from ..services.team_service import get_team_service
from ..database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus

# Import improved onboarding workflow
from .onboarding_handler_improved import get_improved_onboarding_workflow


def format_player_name(name: str) -> str:
    """Format player name for display (ALL CAPS)."""
    return name.upper()


class PlayerRegistrationHandler:
    """Telegram-specific player registration handler using new architecture.
    
    UPDATED: Now uses improved onboarding workflow for better user experience.
    """
    
    def __init__(self, team_id: str, player_service=None, team_service=None):
        self.team_id = team_id
        self.player_service = player_service or get_player_service()
        self.team_service = team_service or get_team_service()
        
        # Initialize improved onboarding workflow
        self.improved_workflow = get_improved_onboarding_workflow(team_id)
    
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
            
            logging.info(
                f"Player added via Telegram: {name} ({phone}) by {added_by}"
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
            logging.error("Failed to add player via Telegram")
            return False, f"❌ Error adding player: {str(e)}"
    
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
            
            logging.info(
                f"Player removed via Telegram: {player.name} ({player.phone}) by {removed_by}"
            )
            
            return True, f"✅ Player {format_player_name(player.name)} removed successfully"
            
        except PlayerNotFoundError:
            return False, f"❌ Player not found"
        except Exception as e:
            logging.error("Failed to remove player via Telegram")
            return False, f"❌ Error removing player: {str(e)}"
    
    async def get_all_players(self) -> List[Player]:
        """Get all players for the team using the new service layer."""
        try:
            players = await self.player_service.get_team_players(self.team_id)
            return players
        except Exception as e:
            logging.error("Failed to get all players via Telegram")
            return []
    
    async def get_player_by_phone(self, phone: str) -> Optional[Player]:
        """Get player by phone number using the new service layer."""
        try:
            player = await self.player_service.get_player_by_phone(phone, self.team_id)
            return player
        except Exception as e:
            logging.error("Failed to get player by phone via Telegram")
            return None
    
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
            
            logging.info(
                f"Player status updated via Telegram: {player.name} -> {status}"
            )
            
            return True, f"✅ Player {format_player_name(player.name)} status updated to {status}"
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {phone} not found"
        except Exception as e:
            logging.error("Failed to update player status via Telegram")
            return False, f"❌ Error updating player status: {str(e)}"
    
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
            
            logging.info(
                f"Invite link generated for player: {player.name}"
            )
            
            return True, f"✅ Invite link generated for {format_player_name(player.name)}: {invite_link}"
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {phone} not found"
        except Exception as e:
            logging.error("Failed to generate invite link via Telegram")
            return False, f"❌ Error generating invite link: {str(e)}"

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
                    logging.warning(f"Could not get team name: {e}")
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
                        logging.error(error_msg)
                        raise ValueError(error_msg)
                except Exception as e:
                    error_msg = f"CRITICAL ERROR: Failed to get bot configuration for team {self.team_id}: {e}"
                    logging.error(error_msg)
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
1. Click the link above to join our main team group
2. Once you join, the bot will automatically welcome you
3. If the bot doesn't welcome you automatically, type: <code>/start {player.player_id.upper()}</code>
4. Complete your onboarding process by following the bot's prompts
5. Get ready for training and matches!

⚠️ <b>Important:</b> 
• This invitation is for our main team chat only
• Leadership chat access is managed separately
• Make sure to use your Player ID: <b>{player.player_id.upper()}</b> if needed

⚽ <b>What to Expect:</b>
• Team announcements and updates
• Training schedules
• Match information
• Team communication

If you have any questions, please contact the team leadership.

Welcome aboard! 🏆

- {team_name} Management"""
            
            logging.info(
                f"Invitation message generated for player: {player.name}"
            )
            
            return True, invitation_message
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {str(phone)} not found"
        except Exception as e:
            logging.error("Failed to generate invitation message")
            return False, f"❌ Error generating invitation message: {str(e)}"
    
    async def player_joined_via_invite(self, player_id: str, telegram_user_id: str, 
                                     telegram_username: Optional[str] = None) -> Tuple[bool, str]:
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
                'onboarding_status': OnboardingStatus.IN_PROGRESS
            }
            if telegram_username:
                updates['telegram_username'] = telegram_username
            
            updated_player = await self.player_service.update_player(player.id, **updates)
            
            logging.info(
                f"Player joined via invite: {player.name} ({telegram_user_id})"
            )
            
            return True, f"✅ Welcome {format_player_name(player.name)}! Let's get you set up. Please complete your profile."
            
        except Exception as e:
            logging.error("Failed to handle player join via invite")
            return False, f"❌ Error processing join: {str(e)}"
    
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
                message = (
                    f"Welcome to {team_name}, {format_player_name(player.name)}!\n\n"
                    f"I'm here to help you complete your registration. Let's start by confirming your details:\n\n"
                    f"Your Current Information:\n"
                    f"- Name: {format_player_name(player.name)}\n"
                    f"- Phone: {player.phone}\n"
                    f"- Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}\n\n"
                    f"Is this information correct?\n"
                    f"Please reply with yes if it's correct, or no if you need to update anything.\n\n"
                    f"Tip: You can type /myinfo at any time to see your details. To update or provide missing information, just reply in natural language. For example:\n"
                    f"- 'My phone is 07123456789'\n"
                    f"- 'Change my position to midfielder'\n\n"
                    f"If you need help, type help."
                )
            
            elif player.onboarding_status == OnboardingStatus.IN_PROGRESS:
                # Check if onboarding should be auto-completed
                if (player.emergency_contact and player.date_of_birth and player.fa_eligible is not None):
                    # Auto-complete onboarding if all required fields are present
                    await self.player_service.update_player(
                        player.id,
                        onboarding_status=OnboardingStatus.COMPLETED
                    )
                    # Return the completed message instead
                    return await self.get_onboarding_message(player_id)
                
                # Show current information and next step
                message = f"""Onboarding in progress for {format_player_name(player.name)}

Your Current Information:
- Name: {format_player_name(player.name)}
- Phone: {player.phone}
- Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
- Emergency Contact: {player.emergency_contact or 'Not provided yet'}
- Date of Birth: {player.date_of_birth or 'Not provided yet'}
- FA Eligible: {'Yes' if player.fa_eligible else 'No' if player.fa_eligible is False else 'Not set yet'}

What to do next:"""
                
                if not player.emergency_contact:
                    message += "\n- Please reply with your emergency contact (name and phone number). For example: 'Jane Smith, 07987654321'"
                elif not player.date_of_birth:
                    message += "\n- Please reply with your date of birth (DD/MM/YYYY). For example: '15/05/1995'"
                elif player.fa_eligible is None:
                    message += "\n- Please reply if you are eligible for FA registration (yes/no). For example: 'yes, I am eligible'"
                else:
                    message += "\n- Onboarding is complete! You can now use team features."
                
                message += "\n\nTip: You can type /myinfo at any time to see your details. To update or provide missing information, just reply in natural language. For example:\n- 'My emergency contact is John Doe, 07123456789'\n- 'My date of birth is 01/01/2000'\n- 'I am eligible for FA registration'"
                message += "\nIf you need help, type help."
            
            else:
                message = (
                    f"Onboarding completed for {format_player_name(player.name)}\n\n"
                    f"Welcome to the team! You're all set up and ready to play.\n\n"
                    f"Your Complete Information:\n"
                    f"- Name: {format_player_name(player.name)}\n"
                    f"- Phone: {player.phone}\n"
                    f"- Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}\n"
                    f"- Emergency Contact: {player.emergency_contact or 'Not provided'}\n"
                    f"- Date of Birth: {player.date_of_birth or 'Not provided'}\n"
                    f"- FA Eligible: {'Yes' if player.fa_eligible else 'No'}\n\n"
                    f"Tip: You can type /myinfo at any time to see your details. To update or provide missing information, just reply in natural language. For example:\n"
                    f"- 'Change my emergency contact to Jane Smith, 07987654321'\n"
                    f"- 'Update my date of birth to 15/05/1995'\n"
                    f"If you need help, type help.\n\n"
                    f"Available Commands:\n"
                    f"- /myinfo - View your details\n"
                    f"- /status - Check your status\n"
                    f"- /list - See all team members\n"
                    f"- help - Get assistance\n\n"
                    f"Next Steps:\n"
                    f"- Wait for admin approval to be eligible for match selection\n"
                    f"- Contact admin if you need to update any information\n"
                    f"- Join team training sessions and matches"
                )
            return True, message
            
        except Exception as e:
            logging.error("Failed to get onboarding message")
            return False, f"❌ Error getting onboarding message: {str(e)}"
    
    async def process_onboarding_response(self, player_id: str, response: str) -> Tuple[bool, str]:
        """
        Process onboarding response using improved workflow.
        
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
            
            # Use improved workflow to process response
            # First, find player by telegram_id to use the improved workflow
            if player.telegram_id:
                return await self.improved_workflow.process_response(player.telegram_id, response)
            else:
                # Fallback to legacy processing if no telegram_id
                return await self._legacy_process_onboarding_response(player, response)
            
        except Exception as e:
            logging.error("Failed to process onboarding response")
            return False, f"❌ Error processing response: {str(e)}"
    
    async def _legacy_process_onboarding_response(self, player: Player, response: str) -> Tuple[bool, str]:
        """Legacy onboarding response processing for backward compatibility."""
        try:
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
            logging.error("Failed to process legacy onboarding response")
            return False, f"❌ Error processing response: {str(e)}"

    async def approve_player(self, player_id: str, approved_by: str) -> Tuple[bool, str]:
        """
        Approve a player for match squad selection (admin/coach workflow).
        
        This command makes a player eligible to be picked for match squads
        after someone has verified all the player details are correct.
        
        Args:
            player_id: Player ID to approve (e.g., "JS1", "TP1")
            approved_by: Telegram user ID of admin/coach
            
        Returns:
            (success, message)
        """
        try:
            # Find player by player_id field (not UUID)
            players = await self.player_service.get_team_players(self.team_id)
            player = None
            for p in players:
                if p.player_id.upper() == player_id.upper():
                    player = p
                    break
            
            if not player:
                return False, f"❌ Player {player_id} not found"
            
            # Check if player is already a team member (should be after being added and invited)
            if player.onboarding_status not in [OnboardingStatus.COMPLETED, OnboardingStatus.PENDING]:
                return False, f"❌ Player {format_player_name(player.name)} is not yet a team member (status: {player.onboarding_status.value}). They need to complete onboarding first."
            
            # Check if player is already approved for match squad selection
            if player.match_eligible:
                return False, f"❌ Player {format_player_name(player.name)} is already approved for match squad selection."
            
            # Approve player for match squad selection
            updated_player = await self.player_service.update_player(
                player.id,
                match_eligible=True
            )
            
            logging.info(
                f"Player approved for match squad selection: {player.name} by {approved_by}"
            )
            
            # Build detailed approval message
            message = f"✅ Player {format_player_name(player.name)} approved for match squad selection!\n\n"
            message += f"📋 <b>Player Details:</b>\n"
            message += f"• Name: {format_player_name(player.name)}\n"
            message += f"• Player ID: {player.player_id.upper()}\n"
            message += f"• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}\n"
            message += f"• Phone: {player.phone}\n"
            message += f"• FA Registered: {'Yes' if player.fa_registered else 'No'}\n"
            message += f"• FA Eligible: {'Yes' if player.fa_eligible else 'No'}\n\n"
            
            if not player.fa_registered:
                message += "⚠️ <b>Important:</b> Player cannot be selected for FA-approved matches until they complete FA registration.\n\n"
                message += "📋 <b>FA Registration Required For:</b>\n"
                message += "• League matches\n"
                message += "• Cup competitions\n"
                message += "• Official tournaments\n\n"
                message += "✅ <b>Can Play In:</b>\n"
                message += "• Friendly matches\n"
                message += "• Training sessions\n"
                message += "• Non-competitive games\n\n"
                message += "💡 <b>Next Steps:</b>\n"
                message += "• Contact admin to arrange FA registration\n"
                message += "• Prepare required documents\n"
                message += "• Pay £15 registration fee"
            else:
                message += "✅ <b>Full Match Eligibility:</b> Player can be selected for all types of matches including FA-approved competitions."
            
            return True, message
            
        except Exception as e:
            logging.error("Failed to approve player for match squad selection")
            return False, f"❌ Error approving player: {str(e)}"

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
            
            logging.info(
                f"Player rejected by admin: {player.name} by {rejected_by}"
            )
            
            reason_msg = f" Reason: {reason}" if reason else ""
            return True, f"✅ Player {format_player_name(player.name)} rejected.{reason_msg}"
            
        except Exception as e:
            logging.error("Failed to reject player")
            return False, f"❌ Error rejecting player: {str(e)}"

    async def get_pending_approvals(self) -> Tuple[bool, str]:
        """Get list of players pending match squad approval."""
        try:
            # Get all players who are team members but not yet approved for match squad selection
            players = await self.player_service.get_team_players(self.team_id)
            pending_players = [p for p in players if 
                             p.onboarding_status in [OnboardingStatus.COMPLETED, OnboardingStatus.PENDING] and 
                             not p.match_eligible]
            
            if not pending_players:
                return True, "✅ No players pending match squad approval."
            
            message = "📋 <b>Players Pending Match Squad Approval:</b>\n\n"
            for player in pending_players:
                message += f"• <b>{format_player_name(player.name)}</b> ({player.player_id.upper()})\n"
                message += f"  📱 Phone: {player.phone or 'Not provided'}\n"
                message += f"  ⚽ Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}\n"
                message += f"  📊 Status: {player.onboarding_status.value.title()}\n"
                message += f"  🏆 FA Registered: {'Yes' if player.fa_registered else 'No'}\n"
                message += f"  ✅ FA Eligible: {'Yes' if player.fa_eligible else 'No'}\n"
                if player.telegram_username:
                    message += f"  📱 Telegram: @{player.telegram_username}\n"
                message += "\n"
            
            message += "💡 <b>Commands:</b>\n"
            message += "• `/approve player_id` - Approve player for match squad selection\n"
            message += "• `/reject player_id [reason]` - Reject player"
            
            return True, message
            
        except Exception as e:
            logging.error("Failed to get pending approvals")
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
                logging.info(f"Created Telegram invite link: {invite_link}")
                return invite_link
            else:
                error_msg = f"Failed to create invite link: {result.get('description', 'Unknown error')}"
                logging.error(error_msg)
                # Fallback to a placeholder link
                return f"https://t.me/+{bot_config.main_chat_id.replace('-', '')}"
                
        except Exception as e:
            logging.error("Error creating Telegram invite link")
            # Fallback to a placeholder link
            return f"https://t.me/+{bot_config.main_chat_id.replace('-', '')}"

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
            logging.error("Failed to get player info")
            return False, f"❌ Error getting player information: {str(e)}"

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
            logging.error("Failed to get player stats")
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
    
    async def handle_command(self, command: str, user_id: str, is_leadership_chat: bool = False) -> str:
        """Handle player registration commands."""
        try:
            command = command.strip().lower()
            
            if command.startswith('/add '):
                return await self._handle_add_player(command, user_id)
            elif command.startswith('/remove '):
                return await self._handle_remove_player(command, user_id)
            elif command == '/list':
                return await self._handle_list_players(is_leadership_chat=is_leadership_chat)
            elif command.startswith('/list '):
                # Handle /list with query
                query = command[6:].strip()  # Remove "/list "
                return await self._handle_list_players(query, is_leadership_chat=is_leadership_chat)
            elif command == '/status':
                return await self._handle_player_status(command, user_id)
            elif command.startswith('/status '):
                return await self._handle_player_status(command, user_id)
            elif command == '/stats':
                return await self._handle_player_stats()
            elif command.startswith('/stats '):
                # Handle /stats with query
                query = command[7:].strip()  # Remove "/stats "
                return await self._handle_player_stats(query)
            elif command.startswith('/invite '):
                return await self._handle_generate_invitation_message(command)
            elif command == '/myinfo':
                return await self._handle_myinfo(user_id)
            elif command.startswith('/myinfo '):
                # Handle /myinfo with query
                query = command[8:].strip()  # Remove "/myinfo "
                return await self._handle_myinfo(user_id, query)
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
                # Try to handle as natural language query
                return await self._handle_natural_language_query(command, user_id)
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"

    async def _handle_natural_language_query(self, message: str, user_id: str) -> str:
        """Handle natural language queries using LLM intent extraction."""
        try:
            from src.utils.llm_client import extract_intent
            
            # Use LLM to understand the intent (async version)
            llm_result = await extract_intent(message, context="Player in team chat asking questions or requesting information")
            
            intent = llm_result.intent if hasattr(llm_result, 'intent') else llm_result.get('intent', 'unknown')
            entities = llm_result.entities if hasattr(llm_result, 'entities') else llm_result.get('entities', {})
            
            if intent == 'get_player_info':
                # Handle player info requests
                return await self._handle_myinfo(user_id, message)
            
            elif intent == 'get_help':
                # Handle help requests
                return """💡 <b>How can I help you?</b>

📋 <b>Available Commands:</b>
• `/myinfo` - Get your player information
• `/list` - See all team players
• `/help` - Show this help message

💬 <b>Natural Language:</b>
You can also ask me things like:
• "What's my phone number?"
• "Show me my position"
• "Am I FA registered?"
• "What's my player ID?"
• "How do I update my info?"

🔧 <b>Need to update something?</b>
Contact the team admin in the leadership chat."""
            
            elif intent == 'update_profile':
                # Handle profile update requests
                return """📝 <b>Profile Updates</b>

To update your profile information, please contact the team admin in the leadership chat.

You can update:
• Name
• Phone number
• Position
• Emergency contact
• Date of birth

💡 <b>Tip:</b> Make sure to provide all the information you want to change."""
            
            elif intent == 'get_team_info':
                # Handle team info requests
                return await self._handle_list_players()
            
            elif intent == 'filter_players':
                # Handle player filtering requests
                return await self._handle_list_players(message)
            
            elif intent == 'get_team_stats':
                # Handle team statistics requests
                return await self._handle_player_stats(message)
            
            elif intent == 'get_player_status':
                # Handle player status requests
                return await self._handle_player_status("/status", user_id)
            
            else:
                # Unknown intent - provide helpful response
                return """🤔 <b>I didn't understand that.</b>

💡 <b>Try these:</b>
• `/myinfo` - Get your player information
• `/list` - See all team players
• `/help` - Show help and available commands

💬 <b>Or ask me naturally:</b>
• "What's my phone number?"
• "Show me my position"
• "Am I FA registered?"
• "How do I update my info?"

If you need specific help, contact the team admin."""
                
        except Exception as e:
            logging.error(f"Error handling natural language query: {e}")
            return """❌ <b>Sorry, I'm having trouble understanding.</b>

💡 <b>Try these commands:</b>
• `/myinfo` - Get your player information
• `/list` - See all team players
• `/help` - Show help and available commands

If you need help, contact the team admin."""

    async def handle_natural_language_update(self, user_id: str, message: str) -> str:
        """Handle natural language updates from completed players."""
        try:
            from src.utils.llm_intent import extract_intent
            
            # Use LLM to understand the update intent
            llm_result = extract_intent(message, context="Completed player requesting to update their profile information")
            
            intent = llm_result.get('intent', 'unknown')
            entities = llm_result.get('entities', {})
            
            # Get player info
            success, player_info = await self.player_handler.get_player_info(user_id)
            if not success:
                return "❌ Unable to find your player information. Please contact an admin."
            
            if intent == 'update_phone':
                new_phone = entities.get('phone_number')
                if new_phone:
                    return f"""📱 <b>Phone Number Update Request</b>

I understand you want to update your phone number to: {new_phone}

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Phone number updates require admin approval for security reasons.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new phone number: {new_phone}
3. Admin will update your information

🔒 <b>Security Note:</b> This helps prevent unauthorized changes to player information."""
                else:
                    return f"""📱 <b>Phone Number Update Request</b>

I understand you want to update your phone number.

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Phone number updates require admin approval for security reasons.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new phone number
3. Admin will update your information

🔒 <b>Security Note:</b> This helps prevent unauthorized changes to player information."""
                
            elif intent == 'update_emergency_contact':
                emergency_contact = entities.get('emergency_contact')
                if emergency_contact:
                    return f"""🚨 <b>Emergency Contact Update Request</b>

I understand you want to update your emergency contact to: {emergency_contact}

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Emergency contact updates require admin approval.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new emergency contact: {emergency_contact}
3. Admin will update your information

🔒 <b>Security Note:</b> This helps ensure accurate emergency contact information."""
                else:
                    return f"""🚨 <b>Emergency Contact Update Request</b>

I understand you want to update your emergency contact.

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Emergency contact updates require admin approval.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new emergency contact
3. Admin will update your information

🔒 <b>Security Note:</b> This helps ensure accurate emergency contact information."""
                
            elif intent == 'update_date_of_birth':
                dob = entities.get('date_of_birth')
                if dob:
                    return f"""📅 <b>Date of Birth Update Request</b>

I understand you want to update your date of birth to: {dob}

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Date of birth updates require admin approval.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new date of birth: {dob}
3. Admin will update your information

🔒 <b>Security Note:</b> This helps maintain accurate player records."""
                else:
                    return f"""📅 <b>Date of Birth Update Request</b>

I understand you want to update your date of birth.

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Date of birth updates require admin approval.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new date of birth
3. Admin will update your information

🔒 <b>Security Note:</b> This helps maintain accurate player records."""
                
            elif intent == 'update_position':
                position = entities.get('position')
                if position:
                    return f"""⚽ <b>Position Update Request</b>

I understand you want to update your position to: {position}

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Position updates require admin approval.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new position: {position}
3. Admin will update your information

🔒 <b>Security Note:</b> This helps maintain accurate team records."""
                else:
                    return f"""⚽ <b>Position Update Request</b>

I understand you want to update your position.

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Position updates require admin approval.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new position
3. Admin will update your information

🔒 <b>Security Note:</b> This helps maintain accurate team records."""
                
            elif intent == 'update_name':
                new_name = entities.get('name')
                if new_name:
                    return f"""📝 <b>Name Update Request</b>

I understand you want to update your name to: {new_name}

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Name updates require admin approval and may affect your player ID.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new name: {new_name}
3. Admin will update your information

🔒 <b>Security Note:</b> Name changes may require updating official team records."""
                else:
                    return f"""📝 <b>Name Update Request</b>

I understand you want to update your name.

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Name updates require admin approval and may affect your player ID.

💡 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Provide your new name
3. Admin will update your information

🔒 <b>Security Note:</b> Name changes may require updating official team records."""
                
            else:
                # Generic update request
                return f"""📝 <b>Profile Update Request</b>

I understand you want to update your profile information.

📋 <b>Current Information:</b>
{player_info}

⚠️ <b>Important:</b> Profile updates require admin approval for security reasons.

💡 <b>What you can update:</b>
• Phone number
• Emergency contact
• Date of birth
• Position
• Name (with admin approval)

🔧 <b>Next Steps:</b>
1. Contact the team admin in the leadership chat
2. Clearly state what you want to update
3. Provide the new information
4. Admin will process your request

🔒 <b>Security Note:</b> This process helps maintain accurate and secure player records."""
                
        except Exception as e:
            logging.error(f"Error handling natural language update: {e}")
            return """❌ <b>Sorry, I'm having trouble processing your update request.</b>

💡 <b>Please try:</b>
1. Contact the team admin directly in the leadership chat
2. Clearly state what you want to update
3. Provide the new information

🔧 <b>Available Updates:</b>
• Phone number
• Emergency contact
• Date of birth
• Position
• Name (with admin approval)"""

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
                return "❌ Usage: /add name phone position [fa_eligible]\n\nPlease provide a valid UK phone number (e.g., 07123456789, +447123456789)"
            
            phone = phone_match.group()
            phone_start = phone_match.start()
            phone_end = phone_match.end()
            
            # Extract position (last word after phone)
            after_phone = command_parts[phone_end:].strip()
            if not after_phone:
                return "❌ Usage: /add name phone position [fa_eligible]\n\nPlease provide a position (goalkeeper, defender, midfielder, forward, striker, utility)"
            
            # Split after phone to get position and optional fa_eligible
            position_parts = after_phone.split()
            position = position_parts[0]
            fa_eligible = len(position_parts) > 1 and position_parts[1].lower() in ['true', 'yes', 'y']
            
            # Extract name (everything before phone)
            name = command_parts[:phone_start].strip()
            if not name:
                return "❌ Usage: /add name phone position [fa_eligible]\n\nPlease provide a player name"
            
            success, message = await self.player_handler.add_player(
                name, phone, position, user_id, fa_eligible
            )
            return message
            
        except Exception as e:
            logging.error("Failed to handle add player command")
            return f"❌ Error adding player: {str(e)}"
    
    async def _handle_remove_player(self, command: str, user_id: str) -> str:
        """Handle /removeplayer command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /removeplayer phone"
            
            phone = parts[1]
            success, message = await self.player_handler.remove_player(phone, user_id)
            return message
            
        except Exception as e:
            logging.error("Failed to handle remove player command")
            return f"❌ Error removing player: {str(e)}"
    
    async def _handle_list_players(self, query: str = "", is_leadership_chat: bool = False) -> str:
        """Handle /list command with optional natural language filtering."""
        try:
            from src.utils.llm_intent import extract_intent
            
            players = await self.player_handler.get_all_players()
            
            if not players:
                return "📋 No players found for this team."
            
            # If query provided, use LLM to understand filtering intent
            if query:
                llm_result = extract_intent(query, context="Player asking about team players. Available filters: position, fa_status, match_eligibility, status")
                
                if llm_result.get('intent') == 'filter_players':
                    entities = llm_result.get('entities', {})
                    filter_type = entities.get('filter_type', 'all')
                    filter_value = entities.get('filter_value', '').lower()
                    
                    # Apply filters based on LLM extraction
                    if filter_type == 'position' and filter_value:
                        players = [p for p in players if filter_value in p.position.value.lower()]
                        message = f"📋 <b>Players - {filter_value.title()} Position</b>\n\n"
                    elif filter_type == 'fa_status' and filter_value:
                        if 'registered' in filter_value:
                            players = [p for p in players if p.fa_registered]
                            message = "📋 <b>Players - FA Registered</b>\n\n"
                        elif 'not' in filter_value or 'unregistered' in filter_value:
                            players = [p for p in players if not p.fa_registered]
                            message = "📋 <b>Players - FA Not Registered</b>\n\n"
                        else:
                            message = "📋 <b>Team Players</b>\n\n"
                    elif filter_type == 'match_eligibility' and filter_value:
                        if 'eligible' in filter_value:
                            players = [p for p in players if p.match_eligible]
                            message = "📋 <b>Players - Match Eligible</b>\n\n"
                        elif 'pending' in filter_value:
                            players = [p for p in players if not p.match_eligible]
                            message = "📋 <b>Players - Pending Approval</b>\n\n"
                        else:
                            message = "📋 <b>Team Players</b>\n\n"
                    elif filter_type == 'status' and filter_value:
                        if 'active' in filter_value or 'completed' in filter_value:
                            players = [p for p in players if p.onboarding_status == OnboardingStatus.COMPLETED]
                            message = "📋 <b>Players - Active</b>\n\n"
                        elif 'pending' in filter_value:
                            players = [p for p in players if p.onboarding_status == OnboardingStatus.PENDING]
                            message = "📋 <b>Players - Pending</b>\n\n"
                        else:
                            message = "📋 <b>Team Players</b>\n\n"
                    else:
                        message = "📋 <b>Team Players</b>\n\n"
                else:
                    message = "📋 <b>Team Players</b>\n\n"
            else:
                message = "📋 <b>Team Players</b>\n\n"
            
            # Group by status
            active_players = [p for p in players if p.onboarding_status == OnboardingStatus.COMPLETED]
            pending_players = [p for p in players if p.onboarding_status == OnboardingStatus.PENDING]
            
            if is_leadership_chat:
                # Leadership chat - show full information
                if active_players:
                    message += "✅ <b>Active Players:</b>\n"
                    for player in active_players:
                        fa_status = "🏆" if player.fa_registered else "⚠️"
                        match_status = "✅" if player.match_eligible else "⏳"
                        message += f"• {format_player_name(player.name)} ({player.player_id.upper()}) - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
                        message += f"  📱 {player.phone} | {fa_status} FA: {'Registered' if player.fa_registered else 'Not Registered'} | {match_status} Match: {'Eligible' if player.match_eligible else 'Pending Approval'}\n"
                        if player.emergency_contact:
                            message += f"  🚨 Emergency: {player.emergency_contact}\n"
                        if player.date_of_birth:
                            message += f"  📅 DOB: {player.date_of_birth}\n"
                    message += "\n"
                
                if pending_players:
                    message += "⏳ <b>Pending Players:</b>\n"
                    for player in pending_players:
                        fa_status = "🏆" if player.fa_registered else "⚠️"
                        match_status = "✅" if player.match_eligible else "⏳"
                        message += f"• {format_player_name(player.name)} ({player.player_id.upper()}) - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
                        message += f"  📱 {player.phone} | {fa_status} FA: {'Registered' if player.fa_registered else 'Not Registered'} | {match_status} Match: {'Eligible' if player.match_eligible else 'Pending Approval'}\n"
                        if player.emergency_contact:
                            message += f"  🚨 Emergency: {player.emergency_contact}\n"
                        if player.date_of_birth:
                            message += f"  📅 DOB: {player.date_of_birth}\n"
                
                # Add legend for leadership
                message += "\n📊 <b>Legend:</b>\n"
                message += "🏆 FA Registered | ⚠️ FA Not Registered\n"
                message += "✅ Match Eligible | ⏳ Pending Approval\n"
            else:
                # Main chat - show minimal information
                if active_players:
                    message += "✅ <b>Active Players:</b>\n"
                    for player in active_players:
                        message += f"• {format_player_name(player.name)} - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
                    message += "\n"
                
                if pending_players:
                    message += "⏳ <b>Pending Players:</b>\n"
                    for player in pending_players:
                        message += f"• {format_player_name(player.name)} - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
                
                # Add note for main chat
                message += "\n💡 <b>Note:</b> For detailed player information, check the leadership chat."
            
            # Add filtering help if query was used
            if query:
                message += "\n💡 <b>Try these filters:</b>\n"
                message += "• \"Show me strikers\"\n"
                message += "• \"Who's FA registered?\"\n"
                message += "• \"Show match eligible players\"\n"
                message += "• \"Active players only\"\n"
            
            return message
            
        except Exception as e:
            logging.error("Failed to handle list players command")
            return f"❌ Error listing players: {str(e)}"
    
    async def _handle_player_status(self, command: str, user_id: Optional[str] = None) -> str:
        """Handle /status command - players can check their own status, admins can check others."""
        try:
            parts = command.split()
            
            # If no phone provided, check the user's own status
            if len(parts) < 2:
                if not user_id:
                    return "❌ Usage: /status phone (for admins) or /status (for your own status)"
                
                # Get player by telegram user ID
                success, message = await self.player_handler.get_player_info(user_id)
                if success:
                    return f"📊 <b>Your Status</b>\n\n{message}"
                else:
                    return "❌ Player not found. Please contact team admin."
            
            # If phone provided, check that specific player's status (admin function)
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
            logging.error("Failed to handle player status command")
            return f"❌ Error getting player status: {str(e)}"
    
    async def _handle_player_stats(self, query: str = "") -> str:
        """Handle /stats command with optional natural language filtering."""
        try:
            from src.utils.llm_intent import extract_intent
            
            stats = await self.player_handler.get_player_stats()
            
            # If query provided, use LLM to understand what stats are requested
            if query:
                llm_result = extract_intent(query, context="Player asking about team statistics. Available stats: total_players, active_players, pending_players, fa_registered, fa_eligible, positions, recent_additions")
                
                if llm_result.get('intent') == 'get_team_stats':
                    entities = llm_result.get('entities', {})
                    stat_type = entities.get('stat_type', 'all')
                    
                    if stat_type == 'overview' or stat_type == 'summary':
                        message = f"""📊 <b>Team Overview</b>

👥 <b>Total Players:</b> {stats['total_players']}
✅ <b>Active Players:</b> {stats['active_players']}
⏳ <b>Pending Players:</b> {stats['pending_players']}
🏆 <b>FA Registered:</b> {stats['fa_registered']}
✅ <b>FA Eligible:</b> {stats['fa_eligible']}"""
                    
                    elif stat_type == 'positions':
                        message = f"""⚽ <b>Position Breakdown</b>

Total Players: {stats['total_players']}"""
                        for position, count in stats['positions'].items():
                            message += f"\n• {position}: {count}"
                    
                    elif stat_type == 'fa_status':
                        message = f"""🏆 <b>FA Registration Status</b>

Total Players: {stats['total_players']}
✅ <b>FA Registered:</b> {stats['fa_registered']}
✅ <b>FA Eligible:</b> {stats['fa_eligible']}
⚠️ <b>Not FA Registered:</b> {stats['total_players'] - stats['fa_registered']}"""
                    
                    elif stat_type == 'recent':
                        if stats['recent_additions']:
                            message = "🆕 <b>Recent Additions</b>\n\n"
                            for addition in stats['recent_additions'][:5]:
                                message += f"• {format_player_name(addition['name'])} ({addition['date']})\n"
                        else:
                            message = "🆕 <b>Recent Additions</b>\n\nNo recent additions."
                    
                    else:
                        # Default to full stats
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
                            for addition in stats['recent_additions'][:5]:
                                message += f"\n• {format_player_name(addition['name'])} ({addition['date']})"
                else:
                    # Default to full stats if LLM doesn't understand
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
                        for addition in stats['recent_additions'][:5]:
                            message += f"\n• {format_player_name(addition['name'])} ({addition['date']})"
            else:
                # Default to full stats
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
                    for addition in stats['recent_additions'][:5]:
                        message += f"\n• {format_player_name(addition['name'])} ({addition['date']})"
            
            # Add help if query was used
            if query:
                message += "\n\n💡 <b>Try these queries:</b>\n"
                message += "• \"Show me position breakdown\"\n"
                message += "• \"How many FA registered?\"\n"
                message += "• \"Recent additions\"\n"
                message += "• \"Team overview\"\n"
            
            return message
            
        except Exception as e:
            logging.error("Failed to handle player stats command")
            return f"❌ Error getting player stats: {str(e)}"
    
    async def _handle_generate_invite(self, command: str) -> str:
        """Handle /generateinvite command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /generateinvite phone"
            
            phone = parts[1]
            # Note: telegram_group_invite_base should be configured
            invite_base = "https://t.me/joinchat/your_group_invite"
            
            success, message = await self.player_handler.generate_invite_link(phone, invite_base)
            return message
            
        except Exception as e:
            logging.error("Failed to handle generate invite command")
            return f"❌ Error generating invite: {str(e)}"
    
    async def _handle_generate_invitation_message(self, command: str) -> str:
        """Handle /invitation command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /invite phone_or_player_id"
            
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
            logging.error("Failed to handle generate invitation message command")
            return f"❌ Error generating invitation message: {str(e)}"
    
    async def _handle_myinfo(self, user_id: str, query: str = "") -> str:
        """Handle /myinfo command and natural language queries about player info."""
        try:
            from src.utils.llm_intent import extract_intent
            
            # If query is provided, use LLM to understand what info is requested
            if query:
                llm_result = extract_intent(query, context="Player asking about their information. Available info: name, phone, position, player_id, fa_status, onboarding_status, match_eligibility")
                
                if llm_result.get('intent') == 'get_player_info':
                    # Extract specific info requested
                    entities = llm_result.get('entities', {})
                    info_type = entities.get('info_type', 'all')
                    
                    # Get player info
                    success, message = await self.player_handler.get_player_info(user_id)
                    if not success:
                        return message
                    
                    # If specific info requested, filter the response
                    if info_type != 'all':
                        # Parse the current message and extract relevant parts
                        if info_type in ['phone', 'number'] and 'Phone:' in message:
                            phone_line = [line for line in message.split('\n') if 'Phone:' in line]
                            if phone_line:
                                return f"📱 <b>Your Phone Number:</b>\n{phone_line[0].split('Phone:')[1].strip()}"
                        
                        elif info_type in ['position', 'role'] and 'Position:' in message:
                            position_line = [line for line in message.split('\n') if 'Position:' in line]
                            if position_line:
                                return f"⚽ <b>Your Position:</b>\n{position_line[0].split('Position:')[1].strip()}"
                        
                        elif info_type in ['fa', 'fa_status', 'registration'] and 'FA Registered:' in message:
                            fa_line = [line for line in message.split('\n') if 'FA Registered:' in line]
                            if fa_line:
                                return f"🏆 <b>Your FA Status:</b>\n{fa_line[0].split('FA Registered:')[1].strip()}"
                        
                        elif info_type in ['status', 'onboarding'] and 'Status:' in message:
                            status_line = [line for line in message.split('\n') if 'Status:' in line]
                            if status_line:
                                return f"📊 <b>Your Status:</b>\n{status_line[0].split('Status:')[1].strip()}"
                        
                        elif info_type in ['id', 'player_id'] and 'Player ID:' in message:
                            id_line = [line for line in message.split('\n') if 'Player ID:' in line]
                            if id_line:
                                return f"🆔 <b>Your Player ID:</b>\n{id_line[0].split('Player ID:')[1].strip()}"
                    
                    # Return full info if no specific type or LLM didn't extract specific request
                    return message
            
            # Default: return full player info
            success, message = await self.player_handler.get_player_info(user_id)
            return message
            
        except Exception as e:
            logging.error("Failed to handle myinfo command")
            return f"❌ Error getting player info: {str(e)}"
    
    async def _handle_approve_player(self, command: str, user_id: str) -> str:
        """Handle /approve command for admin approval."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /approve player_id"
            
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
                return "❌ Usage: /reject player_id [reason]"
            
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
            logging.error("Failed to handle FA registration check command")
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
            logging.error("Failed to handle daily status command")
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
• Use `/add name phone position` to add a player
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
            
            return "❌ Invalid start command format. Use `/start` or `/start player_id`"
            
        except Exception as e:
            logging.error("Failed to handle start command")
            return f"❌ Error processing start command: {str(e)}"

    def _get_help_message(self, is_leadership_chat: bool = False) -> str:
        """Get help message with context-aware commands."""
        if is_leadership_chat:
            return """🤖 <b>KICKAI Player Registration Bot (Leadership)</b>

📋 <b>Available Commands:</b>

👥 <b>Player Management:</b>
• `/add name phone position` - Add a new player
• `/remove phone` - Remove a player
• `/list` - List all players
• `/status phone` - Get specific player status (admin only)
• `/stats` - Get team statistics
• `/invite phone_or_player_id` - Generate invitation message

👤 <b>Player Commands:</b>
• `/myinfo` - Get your player information
• `/myinfo query` - Get specific info (e.g., "What's my phone number?")
• `/status` - Check your own status
• `/list` - See all team players
• `/list filter` - Filter players (e.g., "Show me strikers")
• `/stats` - Get team statistics
• `/stats type` - Get specific stats (e.g., "Position breakdown")

👨‍💼 <b>Admin Commands:</b>
• `/approve player_id` - Approve player for match squad selection
• `/reject player_id [reason]` - Reject a player
• `/pending` - List players pending match squad approval
• `/checkfa` - Check FA registration status
• `/dailystatus` - Generate daily team status report

❓ <b>Help:</b>
• `/help` - Show this help message

📝 <b>Examples:</b>
• `/add John Smith 07123456789 midfielder`
• `/status 07123456789`
• `/approve JS1` - Approve player for match squad selection
• `/reject JS1 Not available for matches`

💬 <b>Natural Language:</b>
Players can also ask naturally:
• "What's my phone number?"
• "Show me my position"
• "Am I FA registered?"
• "How do I update my info?"
• "What's my status?"
• "Show me strikers"
• "Who's FA registered?"
• "How many players do we have?"
• "Show position breakdown"
• "Recent additions"

⚽ <b>Valid Positions:</b> goalkeeper, defender, midfielder, forward, utility"""
        else:
            return """🤖 <b>KICKAI Player Registration Bot</b>

📋 <b>Available Commands:</b>

👥 <b>Player Information:</b>
• `/list` - List all players
• `/myinfo` - Get your player information
• `/status phone` - Get player status
• `/stats` - Get team statistics

❓ <b>Help:</b>
• `/help` - Show this help message

📝 <b>Examples:</b>
• `/status 07123456789`
• `/myinfo`

💡 <b>Note:</b> Admin commands are only available in the leadership chat.""" 