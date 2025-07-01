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
            
            return True, f"✅ Player {name} ({player.player_id}) added successfully! Phone: {phone} (FA eligible: {'Yes' if fa_eligible else 'No'})"
            
        except PlayerDuplicateError as e:
            return False, f"❌ Player with phone {phone} already exists"
        except PlayerValidationError as e:
            return False, f"❌ Validation error: {str(e)}"
        except Exception as e:
            self.logger.error("Failed to add player via Telegram", error=e, team_id=self.team_id)
            return False, f"❌ Error adding player: {str(e)}"
    
    @performance_timer("player_registration_remove_player")
    async def remove_player(self, phone: str, removed_by: str) -> Tuple[bool, str]:
        """
        Remove a player from the team using the new service layer.
        
        Args:
            phone: Player's phone number
            removed_by: Telegram user ID of leadership member
            
        Returns:
            (success, message)
        """
        try:
            # Get player by phone
            player = await self.player_service.get_player_by_phone(phone, self.team_id)
            if not player:
                return False, f"❌ Player with phone {phone} not found"
            
            # Delete player using service layer
            success = await self.player_service.delete_player(player.id)
            if not success:
                return False, "❌ Failed to remove player from database"
            
            self.logger.info(
                f"Player removed via Telegram: {player.name} ({phone}) by {removed_by}",
                operation="remove_player",
                entity_id=player.id,
                team_id=self.team_id,
                user_id=removed_by
            )
            
            return True, f"✅ Player {player.name} removed successfully"
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {phone} not found"
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
            
            return True, f"✅ Player {player.name} status updated to {status}"
            
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
            
            return True, f"✅ Invite link generated for {player.name}: {invite_link}"
            
        except PlayerNotFoundError:
            return False, f"❌ Player with phone {phone} not found"
        except Exception as e:
            self.logger.error("Failed to generate invite link via Telegram", error=e, team_id=self.team_id)
            return False, f"❌ Error generating invite link: {str(e)}"
    
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
            
            return True, f"✅ Welcome {player.name}! Let's get you set up. Please complete your profile."
            
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
                message = f"""🎉 Welcome to {team_name}, {player.name}!

I'm here to help you complete your registration. Let's start by confirming your details:

📋 **Current Information:**
• Name: {player.name}
• Phone: {player.phone}
• Position: {player.position.value if hasattr(player.position, 'value') else player.position}

Please confirm if this information is correct by replying with 'yes' or 'no'."""
            
            elif player.onboarding_status == OnboardingStatus.IN_PROGRESS:
                message = f"""🔄 Onboarding in progress for {player.name}

Please continue with the onboarding process. If you need help, type 'help'."""
            
            else:
                message = f"""✅ Onboarding completed for {player.name}

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
                    return True, f"✅ Onboarding completed! Welcome to the team, {player.name}! You are now ready to play."
            
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
                return False, f"❌ Player {player.name} does not require approval (status: {player.onboarding_status.value})"
            
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
            
            return True, f"✅ Player {player.name} approved successfully! They can now start onboarding."
            
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
                return False, f"❌ Player {player.name} does not require approval (status: {player.onboarding_status.value})"
            
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
            return True, f"✅ Player {player.name} rejected.{reason_msg}"
            
        except Exception as e:
            self.logger.error("Failed to reject player", error=e, player_id=player_id)
            return False, f"❌ Error rejecting player: {str(e)}"

    @performance_timer("player_registration_get_pending_approvals")
    async def get_pending_approvals(self) -> List[Player]:
        """Get all players pending approval."""
        try:
            players = await self.player_service.get_team_players(self.team_id)
            return [p for p in players if p.onboarding_status == OnboardingStatus.PENDING_APPROVAL]
        except Exception as e:
            self.logger.error("Failed to get pending approvals", error=e, team_id=self.team_id)
            return []

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
            info = f"""📋 **Player Information**

👤 **Name:** {player.name}
🆔 **Player ID:** {player.player_id}
📱 **Phone:** {player.phone}
⚽ **Position:** {player.position.value if hasattr(player.position, 'value') else player.position}
📧 **Email:** {player.email or 'Not provided'}
🏆 **FA Registered:** {'Yes' if player.fa_registered else 'No'}
✅ **FA Eligible:** {'Yes' if player.fa_eligible else 'No'}
📊 **Status:** {player.onboarding_status.value if hasattr(player.onboarding_status, 'value') else player.onboarding_status}
📅 **Date Added:** {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}"""
            
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
    
    async def handle_command(self, command: str, user_id: str) -> str:
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
                return await self._handle_generate_invite(command)
            elif command == '/myinfo':
                return await self._handle_myinfo(user_id)
            elif command.startswith('/approve '):
                return await self._handle_approve_player(command, user_id)
            elif command.startswith('/reject '):
                return await self._handle_reject_player(command, user_id)
            elif command == '/pending':
                return await self._handle_pending_approvals()
            elif command in ['/help', '/start']:
                return self._get_help_message()
            else:
                return "❌ Unknown command. Type /help for available commands."
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"

    async def _handle_add_player(self, command: str, user_id: str) -> str:
        """Handle /addplayer command."""
        try:
            parts = command.split()
            if len(parts) < 4:
                return "❌ Usage: /addplayer <name> <phone> <position> [fa_eligible]"
            
            name = parts[1]
            phone = parts[2]
            position = parts[3]
            fa_eligible = len(parts) > 4 and parts[4].lower() in ['true', 'yes', 'y']
            
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
                return "❌ Usage: /removeplayer <phone>"
            
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
            
            message = "📋 **Team Players**\n\n"
            
            if active_players:
                message += "✅ **Active Players:**\n"
                for player in active_players:
                    message += f"• {player.name} ({player.player_id}) - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
                message += "\n"
            
            if pending_players:
                message += "⏳ **Pending Players:**\n"
                for player in pending_players:
                    message += f"• {player.name} ({player.player_id}) - {player.position.value if hasattr(player.position, 'value') else player.position}\n"
            
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle list players command", error=e)
            return f"❌ Error listing players: {str(e)}"
    
    async def _handle_player_status(self, command: str) -> str:
        """Handle /playerstatus command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /playerstatus <phone>"
            
            phone = parts[1]
            player = await self.player_handler.get_player_by_phone(phone)
            
            if not player:
                return f"❌ Player with phone {phone} not found"
            
            status_message = f"""📊 **Player Status**

👤 **Name:** {player.name}
🆔 **Player ID:** {player.player_id}
📱 **Phone:** {player.phone}
⚽ **Position:** {player.position.value if hasattr(player.position, 'value') else player.position}
📊 **Onboarding Status:** {player.onboarding_status.value if hasattr(player.onboarding_status, 'value') else player.onboarding_status}
🏆 **FA Registered:** {'Yes' if player.fa_registered else 'No'}
✅ **FA Eligible:** {'Yes' if player.fa_eligible else 'No'}
📅 **Date Added:** {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}"""
            
            return status_message
            
        except Exception as e:
            self.logger.error("Failed to handle player status command", error=e)
            return f"❌ Error getting player status: {str(e)}"
    
    async def _handle_player_stats(self) -> str:
        """Handle /playerstats command."""
        try:
            stats = await self.player_handler.get_player_stats()
            
            message = f"""📊 **Team Statistics**

👥 **Total Players:** {stats['total_players']}
✅ **Active Players:** {stats['active_players']}
⏳ **Pending Players:** {stats['pending_players']}
🏆 **FA Registered:** {stats['fa_registered']}
✅ **FA Eligible:** {stats['fa_eligible']}

⚽ **Position Breakdown:**"""
            
            for position, count in stats['positions'].items():
                message += f"\n• {position}: {count}"
            
            if stats['recent_additions']:
                message += "\n\n🆕 **Recent Additions:**"
                for addition in stats['recent_additions'][:5]:  # Show last 5
                    message += f"\n• {addition['name']} ({addition['date']})"
            
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle player stats command", error=e)
            return f"❌ Error getting player stats: {str(e)}"
    
    async def _handle_generate_invite(self, command: str) -> str:
        """Handle /generateinvite command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /generateinvite <phone>"
            
            phone = parts[1]
            # Note: telegram_group_invite_base should be configured
            invite_base = "https://t.me/joinchat/your_group_invite"
            
            success, message = await self.player_handler.generate_invite_link(phone, invite_base)
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle generate invite command", error=e)
            return f"❌ Error generating invite: {str(e)}"
    
    async def _handle_myinfo(self, user_id: str) -> str:
        """Handle /myinfo command."""
        try:
            success, message = await self.player_handler.get_player_info(user_id)
            return message
            
        except Exception as e:
            self.logger.error("Failed to handle myinfo command", error=e, user_id=user_id)
            return f"❌ Error getting player info: {str(e)}"
    
    async def _handle_approve_player(self, command: str, user_id: str) -> str:
        """Handle player approval command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /approve <player_id>"
            
            player_id = parts[1]
            success, message = await self.player_handler.approve_player(player_id, user_id)
            return message
            
        except Exception as e:
            return f"❌ Error approving player: {str(e)}"

    async def _handle_reject_player(self, command: str, user_id: str) -> str:
        """Handle player rejection command."""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "❌ Usage: /reject <player_id> [reason]"
            
            player_id = parts[1]
            reason = ' '.join(parts[2:]) if len(parts) > 2 else None
            success, message = await self.player_handler.reject_player(player_id, user_id, reason)
            return message
            
        except Exception as e:
            return f"❌ Error rejecting player: {str(e)}"

    async def _handle_pending_approvals(self) -> str:
        """Handle pending approvals command."""
        try:
            pending_players = await self.player_handler.get_pending_approvals()
            
            if not pending_players:
                return "✅ No players pending approval."
            
            message = "📋 **Players Pending Approval:**\n\n"
            for player in pending_players:
                message += f"• **{player.name}** ({player.player_id})\n"
                message += f"  📱 Phone: {player.phone}\n"
                message += f"  ⚽ Position: {player.position.value}\n\n"
            
            message += "Use `/approve <player_id>` to approve or `/reject <player_id> [reason]` to reject."
            return message
            
        except Exception as e:
            return f"❌ Error getting pending approvals: {str(e)}"

    def _get_help_message(self) -> str:
        """Get help message with all available commands."""
        return """🤖 **KICKAI Player Registration Bot**

📋 **Available Commands:**

👥 **Player Management:**
• `/add <name> <phone> <position>` - Add a new player
• `/remove <phone>` - Remove a player
• `/list` - List all players
• `/status <phone>` - Get player status
• `/stats` - Get team statistics
• `/invite <phone>` - Generate invite link

👤 **Player Commands:**
• `/myinfo` - Get your player information

👨‍💼 **Admin Commands:**
• `/approve <player_id>` - Approve a player
• `/reject <player_id> [reason]` - Reject a player
• `/pending` - List players pending approval

❓ **Help:**
• `/help` - Show this help message

📝 **Examples:**
• `/add John Smith 07123456789 midfielder`
• `/status 07123456789`
• `/approve JS1`
• `/reject JS1 Not available for matches`

⚽ **Valid Positions:** goalkeeper, defender, midfielder, forward, utility""" 