"""
Refactored Player Registration Handler for Telegram

This module provides a modernized version of the player registration handler
that uses the improved command parser with Typer and Pydantic for robust
command parsing and validation.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from ..core.exceptions import (
    PlayerError, PlayerNotFoundError, PlayerValidationError, 
    PlayerDuplicateError
)
from ..services.player_service import get_player_service
from ..services.team_service import get_team_service
from domain.interfaces.player_models import Player, PlayerPosition, PlayerRole, OnboardingStatus
from domain.interfaces.llm_intent import LLMIntentExtractor
from domain.adapters.llm_intent_adapter import LLMIntentExtractorAdapter
from domain.interfaces.llm_client import LLMClient
from domain.adapters.llm_client_adapter import LLMClientAdapter
from domain.interfaces.bot_config import BotConfigManager
from domain.adapters.bot_config_adapter import BotConfigManagerAdapter

# Import improved onboarding workflow
from .onboarding_handler_improved import get_improved_onboarding_workflow

# Import improved command parser
from .improved_command_parser import (
    ImprovedCommandParser, CommandType, ParsedCommand,
    get_improved_parser, parse_command_improved
)
from utils.format_utils import format_player_name


class PlayerRegistrationHandler:
    """Telegram-specific player registration handler using improved architecture.
    
    UPDATED: Now uses improved command parser and onboarding workflow.
    """
    
    def __init__(self, team_id: str, player_service=None, team_service=None, 
                 bot_config_manager=None, llm_intent_extractor=None, llm_client=None,
                 improved_workflow=None, command_parser=None):
        self.team_id = team_id
        self.player_service = player_service or get_player_service(team_id=team_id)
        self.team_service = team_service or get_team_service(team_id=team_id)
        
        # Initialize domain interfaces with dependency injection for testability
        if bot_config_manager is None:
            from core.bot_config_manager import get_bot_config_manager
            infrastructure_manager = get_bot_config_manager()
            self.bot_config_manager = BotConfigManagerAdapter(infrastructure_manager)
        else:
            self.bot_config_manager = bot_config_manager
            
        if llm_intent_extractor is None:
            self.llm_intent_extractor = LLMIntentExtractorAdapter()
        else:
            self.llm_intent_extractor = llm_intent_extractor
            
        if llm_client is None:
            self.llm_client = LLMClientAdapter()
        else:
            self.llm_client = llm_client
        
        # Initialize improved onboarding workflow with dependency injection for testability
        if improved_workflow is None:
            self.improved_workflow = get_improved_onboarding_workflow(team_id)
        else:
            self.improved_workflow = improved_workflow
        
        # Initialize improved command parser
        self.command_parser = command_parser or get_improved_parser()
    
    async def add_player(self, name: str, phone: str, position: str, 
                        added_by: str, fa_eligible: bool = False, player_id: Optional[str] = None) -> Tuple[bool, str]:
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
                fa_registered=False,
                player_id=player_id
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
    
    async def get_player_info(self, user_id: str) -> Tuple[bool, str]:
        """Get player information by Telegram user ID."""
        try:
            player = await self.player_service.get_player_by_telegram_id(user_id, self.team_id)
            if not player:
                return False, "❌ Player not found"
            
            return True, f"""📊 <b>Your Information</b>

👤 <b>Name:</b> {format_player_name(player.name)}
🆔 <b>Player ID:</b> {player.player_id.upper()}
📱 <b>Phone:</b> {player.phone}
⚽ <b>Position:</b> {player.position.value.title()}
📊 <b>Status:</b> {player.get_display_status()}
🏆 <b>FA Registered:</b> {'Yes' if player.is_fa_registered() else 'No'}
✅ <b>FA Eligible:</b> {'Yes' if player.is_fa_eligible() else 'No'}
📅 <b>Date Added:</b> {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}"""
            
        except Exception as e:
            logging.error("Failed to get player info")
            return False, f"❌ Error getting player info: {str(e)}"
    
    async def get_player_stats(self) -> Dict[str, int]:
        """Get player statistics for the team."""
        try:
            players = await self.get_all_players()
            
            stats = {
                'total_players': len(players),
                'active_players': len([p for p in players if p.is_active()]),
                'pending_players': len([p for p in players if p.is_pending_approval()]),
                'fa_registered': len([p for p in players if p.is_fa_registered()]),
                'fa_eligible': len([p for p in players if p.is_fa_eligible()])
            }
            
            return stats
        except Exception as e:
            logging.error("Failed to get player stats")
            return {
                'total_players': 0,
                'active_players': 0,
                'pending_players': 0,
                'fa_registered': 0,
                'fa_eligible': 0
            }
    
    async def generate_invitation_message(self, identifier: str) -> Tuple[bool, str]:
        """Generate invitation message for a player."""
        try:
            # Find player by phone or ID
            player = None
            if any(char.isalpha() for char in identifier):
                # It's a player ID
                players = await self.get_all_players()
                for p in players:
                    if p.player_id.lower() == identifier.lower():
                        player = p
                        break
            else:
                # It's a phone number
                player = await self.get_player_by_phone(identifier)
            
            if not player:
                return False, f"❌ Player not found"
            
            # Generate invitation message
            message = f"""🎉 <b>Welcome to the Team!</b>

👤 <b>Player:</b> {format_player_name(player.name)}
🆔 <b>Player ID:</b> {player.player_id.upper()}
📱 <b>Phone:</b> {player.phone}
⚽ <b>Position:</b> {player.position.value.title()}

💬 <b>Next Steps:</b>
1. Complete your onboarding via Telegram
2. Wait for admin approval
3. Join team activities

🏆 <b>FA Registration:</b>
Contact team admin for FA registration assistance."""
            
            return True, message
            
        except Exception as e:
            logging.error("Failed to generate invitation message")
            return False, f"❌ Error generating invitation: {str(e)}"
    
    async def approve_player(self, player_id: str, approved_by: str) -> Tuple[bool, str]:
        """Approve a player for team access."""
        try:
            # Find player by ID
            players = await self.get_all_players()
            player = None
            for p in players:
                if p.player_id.lower() == player_id.lower():
                    player = p
                    break
            
            if not player:
                return False, f"❌ Player with ID {player_id} not found"
            
            # Update player status
            await self.player_service.update_player(
                player.id,
                status="approved"
            )
            
            logging.info(
                f"Player approved via Telegram: {player.name} by {approved_by}"
            )
            
            return True, f"✅ Player {format_player_name(player.name)} approved successfully"
            
        except Exception as e:
            logging.error("Failed to approve player")
            return False, f"❌ Error approving player: {str(e)}"
    
    async def reject_player(self, player_id: str, rejected_by: str, reason: str = None) -> Tuple[bool, str]:
        """Reject a player from team access."""
        try:
            # Find player by ID
            players = await self.get_all_players()
            player = None
            for p in players:
                if p.player_id.lower() == player_id.lower():
                    player = p
                    break
            
            if not player:
                return False, f"❌ Player with ID {player_id} not found"
            
            # Update player status
            await self.player_service.update_player(
                player.id,
                status="rejected"
            )
            
            logging.info(
                f"Player rejected via Telegram: {player.name} by {rejected_by}"
            )
            
            reason_text = f" (Reason: {reason})" if reason else ""
            return True, f"❌ Player {format_player_name(player.name)} rejected{reason_text}"
            
        except Exception as e:
            logging.error("Failed to reject player")
            return False, f"❌ Error rejecting player: {str(e)}"
    
    async def get_pending_approvals(self) -> Tuple[bool, str]:
        """Get list of players pending approval."""
        try:
            players = await self.get_all_players()
            pending_players = [p for p in players if p.is_pending_approval()]
            
            if not pending_players:
                return True, "📋 No players pending approval"
            
            message = "📋 <b>Players Pending Approval</b>\n\n"
            for player in pending_players:
                message += f"👤 <b>{format_player_name(player.name)}</b>\n"
                message += f"🆔 <b>ID:</b> {player.player_id.upper()}\n"
                message += f"📱 <b>Phone:</b> {player.phone}\n"
                message += f"⚽ <b>Position:</b> {player.position.value.title()}\n"
                message += f"📅 <b>Added:</b> {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}\n\n"
            
            return True, message
            
        except Exception as e:
            logging.error("Failed to get pending approvals")
            return False, f"❌ Error getting pending approvals: {str(e)}"


class PlayerCommandHandler:
    """Telegram command handler for player operations using improved parser."""
    
    def __init__(self, player_handler: PlayerRegistrationHandler):
        self.player_handler = player_handler
    
    async def handle_command(self, command: str, user_id: str, is_leadership_chat: bool = False) -> str:
        """Handle player registration commands using improved parser."""
        try:
            # Parse command using improved parser
            parsed = self.player_handler.command_parser.parse(command)
            
            if not parsed.is_valid:
                return f"❌ {parsed.error_message}"
            
            # Route to appropriate handler based on command type
            if parsed.command_type == CommandType.ADD_PLAYER:
                return await self._handle_add_player_improved(parsed.parameters, user_id)
            elif parsed.command_type == CommandType.REMOVE_PLAYER:
                return await self._handle_remove_player_improved(parsed.parameters, user_id)
            elif parsed.command_type == CommandType.LIST:
                return await self._handle_list_players_improved(parsed.parameters, is_leadership_chat)
            elif parsed.command_type == CommandType.STATUS:
                return await self._handle_player_status_improved(parsed.parameters, user_id)
            elif parsed.command_type == CommandType.INVITE:
                return await self._handle_generate_invitation_improved(parsed.parameters)
            elif parsed.command_type == CommandType.APPROVE:
                return await self._handle_approve_player_improved(parsed.parameters, user_id)
            elif parsed.command_type == CommandType.REJECT:
                return await self._handle_reject_player_improved(parsed.parameters, user_id)
            elif parsed.command_type == CommandType.PENDING:
                return await self._handle_pending_approvals_improved()
            elif parsed.command_type == CommandType.START:
                return await self._handle_start_command_improved(user_id)
            elif parsed.command_type == CommandType.HELP:
                return self._get_help_message_improved(parsed.parameters, is_leadership_chat)
            else:
                # Try to handle as natural language query
                return await self._handle_natural_language_query(command, user_id)
                
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            return f"❌ Error processing command: {str(e)}"
    
    async def _handle_natural_language_query(self, message: str, user_id: str) -> str:
        """Handle natural language queries using the LLM client domain interface."""
        try:
            response = await self.player_handler.llm_client.generate_response(message)
            return response
        except Exception as e:
            logging.error("Failed to handle natural language query")
            return f"❌ Error processing query: {str(e)}"
    
    async def _handle_add_player_improved(self, parameters: Dict[str, Any], user_id: str) -> str:
        """Handle /add command using improved parser."""
        try:
            name = parameters.get('name')
            phone = parameters.get('phone')
            position = parameters.get('position')
            admin_approved = parameters.get('admin_approved', False)
            
            success, message = await self.player_handler.add_player(
                name, phone, position, user_id, fa_eligible=admin_approved
            )
            return message
            
        except Exception as e:
            logging.error("Failed to handle add player command")
            return f"❌ Error adding player: {str(e)}"
    
    async def _handle_remove_player_improved(self, parameters: Dict[str, Any], user_id: str) -> str:
        """Handle /remove command using improved parser."""
        try:
            identifier = parameters.get('identifier')
            success, message = await self.player_handler.remove_player(identifier, user_id)
            return message
            
        except Exception as e:
            logging.error("Failed to handle remove player command")
            return f"❌ Error removing player: {str(e)}"
    
    async def _handle_list_players_improved(self, parameters: Dict[str, Any], is_leadership_chat: bool) -> str:
        """Handle /list command using improved parser."""
        try:
            players = await self.player_handler.get_all_players()
            if not players:
                return "📋 No players found for this team."
            
            filter_type = parameters.get('filter')
            message = "📋 <b>Team Players</b>\n\n"
            
            # Apply filters if specified
            if filter_type:
                if filter_type == 'pending':
                    players = [p for p in players if p.is_pending_approval()]
                    message = "📋 <b>Players - Pending Approval</b>\n\n"
                elif filter_type == 'active':
                    players = [p for p in players if p.is_active()]
                    message = "📋 <b>Players - Active</b>\n\n"
                elif filter_type == 'fa_registered':
                    players = [p for p in players if p.is_fa_registered()]
                    message = "📋 <b>Players - FA Registered</b>\n\n"
            
            # Format player list
            for player in players:
                message += f"👤 <b>{format_player_name(player.name)}</b>\n"
                message += f"🆔 <b>ID:</b> {player.player_id.upper()}\n"
                message += f"📱 <b>Phone:</b> {player.phone}\n"
                message += f"⚽ <b>Position:</b> {player.position.value.title()}\n"
                message += f"📊 <b>Status:</b> {player.get_display_status()}\n"
                message += f"🏆 <b>FA:</b> {'Yes' if player.is_fa_registered() else 'No'}\n\n"
            
            return message
            
        except Exception as e:
            logging.error("Failed to handle list players command")
            return f"❌ Error listing players: {str(e)}"
    
    async def _handle_player_status_improved(self, parameters: Dict[str, Any], user_id: str) -> str:
        """Handle /status command using improved parser."""
        try:
            identifier = parameters.get('identifier')
            
            if not identifier:
                # Check user's own status
                success, message = await self.player_handler.get_player_info(user_id)
                if success:
                    return f"📊 <b>Your Status</b>\n\n{message}"
                else:
                    return "❌ Player not found. Please contact team admin."
            
            # Check specific player's status
            player = await self.player_handler.get_player_by_phone(identifier)
            if not player:
                return f"❌ Player with phone {identifier} not found"
            
            status_message = f"""📊 <b>Player Status</b>

👤 <b>Name:</b> {format_player_name(player.name)}
🆔 <b>Player ID:</b> {player.player_id.upper()}
📱 <b>Phone:</b> {player.phone}
⚽ <b>Position:</b> {player.position.value.title()}
📊 <b>Status:</b> {player.get_display_status()}
🏆 <b>FA Registered:</b> {'Yes' if player.is_fa_registered() else 'No'}
✅ <b>FA Eligible:</b> {'Yes' if player.is_fa_eligible() else 'No'}
📅 <b>Date Added:</b> {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}"""
            
            return status_message
            
        except Exception as e:
            logging.error("Failed to handle player status command")
            return f"❌ Error getting player status: {str(e)}"
    
    async def _handle_generate_invitation_improved(self, parameters: Dict[str, Any]) -> str:
        """Handle /invite command using improved parser."""
        try:
            identifier = parameters.get('identifier')
            success, message = await self.player_handler.generate_invitation_message(identifier)
            return message
            
        except Exception as e:
            logging.error("Failed to handle generate invitation command")
            return f"❌ Error generating invitation: {str(e)}"
    
    async def _handle_approve_player_improved(self, parameters: Dict[str, Any], user_id: str) -> str:
        """Handle /approve command using improved parser."""
        try:
            player_id = parameters.get('player_id')
            success, message = await self.player_handler.approve_player(player_id, user_id)
            return message
            
        except Exception as e:
            logging.error("Failed to handle approve player command")
            return f"❌ Error approving player: {str(e)}"
    
    async def _handle_reject_player_improved(self, parameters: Dict[str, Any], user_id: str) -> str:
        """Handle /reject command using improved parser."""
        try:
            player_id = parameters.get('player_id')
            reason = parameters.get('reason', 'No reason provided')
            success, message = await self.player_handler.reject_player(player_id, user_id, reason)
            return message
            
        except Exception as e:
            logging.error("Failed to handle reject player command")
            return f"❌ Error rejecting player: {str(e)}"
    
    async def _handle_pending_approvals_improved(self) -> str:
        """Handle /pending command using improved parser."""
        try:
            success, message = await self.player_handler.get_pending_approvals()
            return message
            
        except Exception as e:
            logging.error("Failed to handle pending approvals command")
            return f"❌ Error getting pending approvals: {str(e)}"
    
    async def _handle_start_command_improved(self, user_id: str) -> str:
        """Handle /start command using improved parser."""
        try:
            return """🤖 <b>Welcome to KICKAI Team Bot!</b>

📋 <b>Available Commands:</b>
• `/myinfo` - View your information
• `/list` - List team players
• `/status` - Check your status
• `/help` - Get help

💬 <b>Need Help?</b>
Contact the team admin in the leadership chat for assistance."""
        except Exception as e:
            logging.error("Failed to handle start command")
            return f"❌ Error processing start command: {str(e)}"
    
    def _get_help_message_improved(self, parameters: Dict[str, Any], is_leadership_chat: bool) -> str:
        """Get help message using improved parser."""
        try:
            command = parameters.get('command')
            
            if command:
                # Return help for specific command
                help_text = self.player_handler.command_parser.get_help_text(command)
                return f"📖 <b>Help for /{command}</b>\n\n{help_text}"
            
            # Return general help
            if is_leadership_chat:
                return """📖 <b>Leadership Commands</b>

👥 <b>Player Management:</b>
• `/add name phone position` - Add new player
• `/remove phone_or_id` - Remove player
• `/approve player_id` - Approve player
• `/reject player_id [reason]` - Reject player
• `/pending` - List pending approvals

📊 <b>Information:</b>
• `/list [filter]` - List players
• `/status phone` - Check player status
• `/stats` - Team statistics
• `/invite phone_or_id` - Generate invitation

💬 <b>Other:</b>
• `/help [command]` - Get help
• `/start` - Welcome message"""
            else:
                return """📖 <b>Player Commands</b>

👤 <b>Your Information:</b>
• `/myinfo` - View your details
• `/status` - Check your status

📊 <b>Team Information:</b>
• `/list` - List team players
• `/stats` - Team statistics

💬 <b>Other:</b>
• `/help [command]` - Get help
• `/start` - Welcome message"""
                
        except Exception as e:
            logging.error("Failed to get help message")
            return f"❌ Error getting help: {str(e)}"


# Factory function for creating handlers
def create_player_registration_handler(team_id: str, **kwargs) -> PlayerRegistrationHandler:
    """Create a new player registration handler with dependency injection."""
    return PlayerRegistrationHandler(team_id=team_id, **kwargs)


def create_player_command_handler(player_handler: PlayerRegistrationHandler) -> PlayerCommandHandler:
    """Create a new player command handler."""
    return PlayerCommandHandler(player_handler=player_handler) 