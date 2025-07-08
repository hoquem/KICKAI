#!/usr/bin/env python3
"""
Player Registration Handler

This module handles player registration commands using the new command parser
and base handler architecture. It replaces the massive player_registration_handler.py
with a clean, maintainable implementation.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.telegram.improved_command_parser import (
    parse_command_improved, ParsedCommand, CommandType, get_help_text_improved
)
from src.telegram.handlers.base_handler import (
    BaseHandler, HandlerContext, HandlerResult
)
from src.services.player_service import get_player_service
from src.services.team_service import get_team_service
from src.database.models_improved import Player, PlayerPosition, PlayerRole
from src.core.exceptions import PlayerNotFoundError, TeamNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class RegistrationData:
    """Data for player registration."""
    name: str
    phone: str
    position: str
    admin_approved: bool = False
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None


class PlayerRegistrationHandler(BaseHandler):
    """Handler for player registration commands."""
    
    def __init__(self):
        super().__init__()
        self.player_service = get_player_service()
        self.team_service = get_team_service()
    
    async def handle(self, context: HandlerContext, **kwargs) -> HandlerResult:
        """Handle player registration commands."""
        parsed_command = kwargs.get('parsed_command')
        if not parsed_command:
            return HandlerResult.error_result("No command provided")
        
        command_type = parsed_command.command_type
        
        if command_type == CommandType.ADD_PLAYER:
            return await self._handle_add_player(context, parsed_command)
        elif command_type == CommandType.REGISTER:
            return await self._handle_register(context, parsed_command)
        elif command_type == CommandType.REMOVE_PLAYER:
            return await self._handle_remove_player(context, parsed_command)
        elif command_type == CommandType.APPROVE:
            return await self._handle_approve_player(context, parsed_command)
        elif command_type == CommandType.REJECT:
            return await self._handle_reject_player(context, parsed_command)
        elif command_type == CommandType.INVITE:
            return await self._handle_invite_player(context, parsed_command)
        elif command_type == CommandType.STATUS:
            return await self._handle_player_status(context, parsed_command)
        elif command_type == CommandType.LIST:
            return await self._handle_list_players(context, parsed_command)
        elif command_type == CommandType.PENDING:
            return await self._handle_pending_players(context, parsed_command)
        elif command_type == CommandType.HELP:
            return await self._handle_help(context, parsed_command)
        elif command_type == CommandType.START:
            return await self._handle_start(context, parsed_command)
        else:
            return HandlerResult.error_result(f"Unknown command: {command_type.value}")
    
    async def _handle_add_player(self, context: HandlerContext, 
                                parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /add command for adding players."""
        if not parsed_command.is_valid:
            return HandlerResult.error_result(parsed_command.error_message)
        
        params = parsed_command.parameters
        
        # Validate required parameters
        is_valid, error = self.validate_required_parameters(
            params, ['name', 'phone', 'position']
        )
        if not is_valid:
            return HandlerResult.error_result(error)
        
        try:
            # Create registration data
            registration_data = RegistrationData(
                name=params['name'],
                phone=params['phone'],
                position=params['position'],
                admin_approved=params.get('admin_approved', False),
                telegram_id=context.user_id,
                telegram_username=context.username
            )
            
            # Add player
            player = await self._add_player(context.team_id, registration_data)
            
            message = self.format_success_message(
                "Player Added Successfully",
                f"Added {player.name} to the team.",
                {
                    "Player ID": player.player_id,
                    "Position": player.position.value.title(),
                    "Phone": player.phone,
                    "Status": player.get_display_status()
                }
            )
            
            return HandlerResult.success_result(message, {"player_id": player.player_id})
            
        except Exception as e:
            self.logger.error(f"Error adding player: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to add player: {str(e)}")
    
    async def _handle_register(self, context: HandlerContext, 
                              parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /register command for self-registration."""
        if not parsed_command.is_valid:
            return HandlerResult.error_result(parsed_command.error_message)
        
        params = parsed_command.parameters
        
        # Validate required parameters
        is_valid, error = self.validate_required_parameters(
            params, ['name', 'phone']
        )
        if not is_valid:
            return HandlerResult.error_result(error)
        
        try:
            # Create registration data
            registration_data = RegistrationData(
                name=params['name'],
                phone=params['phone'],
                position=params.get('position', 'utility'),
                admin_approved=False,  # Self-registration requires approval
                telegram_id=context.user_id,
                telegram_username=context.username
            )
            
            # Check if player already exists
            existing_player = await self.player_service.get_player_by_phone(
                context.team_id, registration_data.phone
            )
            
            if existing_player:
                return HandlerResult.error_result(
                    f"Player with phone {registration_data.phone} already exists in the team."
                )
            
            # Add player
            player = await self._add_player(context.team_id, registration_data)
            
            message = self.format_success_message(
                "Registration Successful",
                f"Welcome {player.name}! Your registration has been submitted for approval.",
                {
                    "Player ID": player.player_id,
                    "Position": player.position.value.title(),
                    "Status": "Pending Approval"
                }
            )
            
            return HandlerResult.success_result(message, {"player_id": player.player_id})
            
        except Exception as e:
            self.logger.error(f"Error registering player: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to register: {str(e)}")
    
    async def _handle_remove_player(self, context: HandlerContext, 
                                   parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /remove command for removing players."""
        if not parsed_command.is_valid:
            return HandlerResult.error_result(parsed_command.error_message)
        
        params = parsed_command.parameters
        identifier = params.get('identifier')
        
        if not identifier:
            return HandlerResult.error_result("Please provide a player phone number or name")
        
        try:
            # Try to remove by phone first, then by name
            success = await self.player_service.remove_player_by_phone(
                context.team_id, identifier
            )
            
            if not success:
                success = await self.player_service.remove_player_by_name(
                    context.team_id, identifier
                )
            
            if success:
                message = self.format_success_message(
                    "Player Removed",
                    f"Successfully removed player: {identifier}"
                )
                return HandlerResult.success_result(message)
            else:
                return HandlerResult.error_result(f"Player not found: {identifier}")
                
        except Exception as e:
            self.logger.error(f"Error removing player: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to remove player: {str(e)}")
    
    async def _handle_approve_player(self, context: HandlerContext, 
                                    parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /approve command for approving players."""
        if not parsed_command.is_valid:
            return HandlerResult.error_result(parsed_command.error_message)
        
        params = parsed_command.parameters
        player_id = params.get('player_id')
        
        if not player_id:
            return HandlerResult.error_result("Please provide a player ID or name")
        
        try:
            # Approve player
            player = await self.player_service.approve_player(
                context.team_id, player_id, context.user_id
            )
            
            message = self.format_success_message(
                "Player Approved",
                f"Successfully approved {player.name}",
                {
                    "Player ID": player.player_id,
                    "Approved By": context.user_id,
                    "Status": player.get_display_status()
                }
            )
            
            return HandlerResult.success_result(message, {"player_id": player.player_id})
            
        except PlayerNotFoundError:
            return HandlerResult.error_result(f"Player not found: {player_id}")
        except Exception as e:
            self.logger.error(f"Error approving player: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to approve player: {str(e)}")
    
    async def _handle_reject_player(self, context: HandlerContext, 
                                   parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /reject command for rejecting players."""
        if not parsed_command.is_valid:
            return HandlerResult.error_result(parsed_command.error_message)
        
        params = parsed_command.parameters
        player_id = params.get('player_id')
        reason = params.get('reason', 'No reason provided')
        
        if not player_id:
            return HandlerResult.error_result("Please provide a player ID or name")
        
        try:
            # Reject player
            player = await self.player_service.reject_player(
                context.team_id, player_id, context.user_id, reason
            )
            
            message = self.format_success_message(
                "Player Rejected",
                f"Successfully rejected {player.name}",
                {
                    "Player ID": player.player_id,
                    "Rejected By": context.user_id,
                    "Reason": reason
                }
            )
            
            return HandlerResult.success_result(message, {"player_id": player.player_id})
            
        except PlayerNotFoundError:
            return HandlerResult.error_result(f"Player not found: {player_id}")
        except Exception as e:
            self.logger.error(f"Error rejecting player: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to reject player: {str(e)}")
    
    async def _handle_invite_player(self, context: HandlerContext, 
                                   parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /invite command for generating invitations."""
        if not parsed_command.is_valid:
            return HandlerResult.error_result(parsed_command.error_message)
        
        params = parsed_command.parameters
        identifier = params.get('identifier')
        
        if not identifier:
            return HandlerResult.error_result("Please provide a phone number or player name")
        
        try:
            # Generate invitation
            invite_link = await self.player_service.generate_invitation(
                context.team_id, identifier
            )
            
            message = self.format_success_message(
                "Invitation Generated",
                f"Invitation link generated for: {identifier}",
                {
                    "Invite Link": invite_link,
                    "Expires": "24 hours"
                }
            )
            
            return HandlerResult.success_result(message, {"invite_link": invite_link})
            
        except Exception as e:
            self.logger.error(f"Error generating invitation: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to generate invitation: {str(e)}")
    
    async def _handle_player_status(self, context: HandlerContext, 
                                   parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /status command for checking player status."""
        if not parsed_command.is_valid:
            return HandlerResult.error_result(parsed_command.error_message)
        
        params = parsed_command.parameters
        identifier = params.get('identifier')
        
        if not identifier:
            return HandlerResult.error_result("Please provide a phone number or player name")
        
        try:
            # Get player status
            player = await self.player_service.get_player_by_identifier(
                context.team_id, identifier
            )
            
            if not player:
                return HandlerResult.error_result(f"Player not found: {identifier}")
            
            message = self.format_success_message(
                "Player Status",
                f"Status for {player.name}",
                {
                    "Player ID": player.player_id,
                    "Position": player.position.value.title(),
                    "Status": player.get_display_status(),
                    "FA Registered": "Yes" if player.fa_registered else "No",
                    "Match Eligible": "Yes" if player.is_match_eligible() else "No",
                    "Onboarding": player.onboarding_status.value.title()
                }
            )
            
            return HandlerResult.success_result(message, {"player_id": player.player_id})
            
        except Exception as e:
            self.logger.error(f"Error getting player status: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to get player status: {str(e)}")
    
    async def _handle_list_players(self, context: HandlerContext, 
                                  parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /list command for listing players."""
        try:
            filter_type = parsed_command.parameters.get('filter', 'all')
            
            if filter_type == 'pending':
                players = await self.player_service.get_pending_players(context.team_id)
                title = "Pending Players"
            elif filter_type == 'active':
                players = await self.player_service.get_active_players(context.team_id)
                title = "Active Players"
            else:
                players = await self.player_service.get_all_players(context.team_id)
                title = "All Players"
            
            if not players:
                message = f"📋 **{title}**\n\nNo players found."
                return HandlerResult.success_result(message)
            
            # Format player list
            player_lines = []
            for player in players:
                status_emoji = "✅" if player.is_active() else "⏳" if player.is_pending_approval() else "❌"
                player_lines.append(
                    f"{status_emoji} **{player.name}** ({player.player_id})\n"
                    f"   📱 {player.phone} | 🏃 {player.position.value.title()} | "
                    f"📊 {player.get_display_status()}"
                )
            
            message = f"📋 **{title}**\n\n" + "\n\n".join(player_lines)
            
            return HandlerResult.success_result(message, {"player_count": len(players)})
            
        except Exception as e:
            self.logger.error(f"Error listing players: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to list players: {str(e)}")
    
    async def _handle_pending_players(self, context: HandlerContext, 
                                     parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /pending command for listing pending approvals."""
        try:
            pending_players = await self.player_service.get_pending_players(context.team_id)
            
            if not pending_players:
                message = "📋 **Pending Approvals**\n\nNo players pending approval."
                return HandlerResult.success_result(message)
            
            # Format pending players list
            player_lines = []
            for player in pending_players:
                player_lines.append(
                    f"⏳ **{player.name}** ({player.player_id})\n"
                    f"   📱 {player.phone} | 🏃 {player.position.value.title()}\n"
                    f"   📊 {player.onboarding_status.value.title()}"
                )
            
            message = "📋 **Pending Approvals**\n\n" + "\n\n".join(player_lines)
            
            return HandlerResult.success_result(message, {"pending_count": len(pending_players)})
            
        except Exception as e:
            self.logger.error(f"Error getting pending players: {str(e)}", exc_info=True)
            return HandlerResult.error_result(f"Failed to get pending players: {str(e)}")
    
    async def _handle_help(self, context: HandlerContext, 
                          parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /help command."""
        command_name = parsed_command.parameters.get('command')
        
        if command_name:
            # Get help for specific command
            try:
                command_type = CommandType(command_name.lower().replace(' ', '_'))
                help_text = get_help_text_improved(command_type)
                return HandlerResult.success_result(help_text)
            except ValueError:
                return HandlerResult.error_result(f"Unknown command: {command_name}")
        else:
            # Get general help
            help_text = get_help_text_improved()
            return HandlerResult.success_result(help_text)
    
    async def _handle_start(self, context: HandlerContext, 
                           parsed_command: ParsedCommand) -> HandlerResult:
        """Handle /start command."""
        message = """🤖 **Welcome to KICKAI Bot!**

I'm here to help manage your football team. Here are some things you can do:

**For Players:**
• `/register [name] [phone] [position]` - Register yourself
• `/status [phone]` - Check your status

**For Team Management:**
• `/add [name] [phone] [position]` - Add a player
• `/approve [player_id]` - Approve a player
• `/reject [player_id] [reason]` - Reject a player
• `/list` - List all players
• `/pending` - Show pending approvals

**Other Commands:**
• `/help` - Show this help message
• `/help [command]` - Get help for a specific command

Need help? Use `/help` for more information!"""
        
        return HandlerResult.success_result(message)
    
    async def _add_player(self, team_id: str, registration_data: RegistrationData) -> Player:
        """Add a player to the team."""
        # Convert position string to enum
        try:
            position = PlayerPosition(registration_data.position.lower())
        except ValueError:
            position = PlayerPosition.UTILITY
        
        # Use the canonical create_player method from the service
        player = await self.player_service.create_player(
            name=registration_data.name,
            phone=registration_data.phone,
            team_id=team_id,
            position=position,
            role=PlayerRole.PLAYER,
            fa_registered=False,
            player_id=None
        )
        # Optionally update telegram_id and username if needed
        player.telegram_id = registration_data.telegram_id
        player.telegram_username = registration_data.telegram_username
        player.admin_approved = registration_data.admin_approved
        return player


# Global handler instance
_player_registration_handler = None

def get_player_registration_handler() -> PlayerRegistrationHandler:
    """Get the global player registration handler instance."""
    global _player_registration_handler
    if _player_registration_handler is None:
        _player_registration_handler = PlayerRegistrationHandler()
    return _player_registration_handler


async def handle_player_registration_command(text: str, context: HandlerContext) -> HandlerResult:
    """Handle a player registration command using the global handler."""
    # Parse the command
    parsed_command = parse_command_improved(text)
    
    # Get handler and execute
    handler = get_player_registration_handler()
    return await handler.execute_with_logging(
        context, 
        parsed_command.command_type.value,
        parsed_command=parsed_command
    ) 