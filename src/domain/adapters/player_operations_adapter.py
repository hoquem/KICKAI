"""
Application layer adapter for player operations.

This adapter implements the domain interface by wrapping the application layer services.
"""

import logging
from typing import Optional, List
from datetime import datetime

from services.player_service import PlayerService
from database.firebase_client import get_firebase_client
from domain.interfaces.player_operations import IPlayerOperations, PlayerInfo
from domain.interfaces.player_models import PlayerPosition

logger = logging.getLogger(__name__)

# Initialize the real PlayerService with the real Firestore client
player_service = PlayerService(get_firebase_client())

def add_player(player_data, team_id=None):
    logger.info(f"[Adapter] add_player called with data: {player_data}, team_id: {team_id}")
    try:
        result = player_service.add_player(player_data, team_id=team_id)
        logger.info(f"[Adapter] add_player result: {result}")
        return result
    except Exception as e:
        logger.error(f"[Adapter] add_player failed: {e}", exc_info=True)
        raise

def register_player(player_data, team_id=None):
    logger.info(f"[Adapter] register_player called with data: {player_data}, team_id: {team_id}")
    try:
        result = player_service.register_player(player_data, team_id=team_id)
        logger.info(f"[Adapter] register_player result: {result}")
        return result
    except Exception as e:
        logger.error(f"[Adapter] register_player failed: {e}", exc_info=True)
        raise


class PlayerOperationsAdapter(IPlayerOperations):
    """Adapter that wraps the player service to implement domain interface."""
    
    def __init__(self, player_service):
        self.player_service = player_service
        self.logger = logging.getLogger(__name__)

    async def get_player_info(self, user_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] get_player_info called with user_id={user_id}, team_id={team_id}")
        try:
            result = await self.player_service.get_player_info(user_id, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] get_player_info result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting player info: {e}", exc_info=True)
            return False, f"Error getting player info: {str(e)}"

    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[PlayerInfo]:
        self.logger.info(f"[PlayerOperationsAdapter] get_player_by_phone called with phone={phone}, team_id={team_id}")
        try:
            result = await self.player_service.get_player_by_phone(phone, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] get_player_by_phone result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting player by phone: {e}", exc_info=True)
            return None

    async def list_players(self, team_id: str, is_leadership_chat: bool = False) -> str:
        self.logger.info(f"[PlayerOperationsAdapter] list_players called with team_id={team_id}, is_leadership_chat={is_leadership_chat}")
        try:
            result = await self.player_service.list_players(team_id, is_leadership_chat)
            self.logger.info(f"[PlayerOperationsAdapter] list_players result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error listing players: {e}", exc_info=True)
            return f"Error listing players: {str(e)}"

    async def register_player(self, user_id: str, team_id: str, player_id: Optional[str] = None) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] register_player called with user_id={user_id}, team_id={team_id}, player_id={player_id}")
        try:
            result = await self.player_service.register_player(user_id, team_id, player_id)
            self.logger.info(f"[PlayerOperationsAdapter] register_player result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error registering player: {e}", exc_info=True)
            return False, f"Error registering player: {str(e)}"

    async def add_player(self, name: str, phone: str, position: str = None, team_id: str = None) -> tuple[bool, str]:
        """Add a new player to the team."""
        logger.info(f"[PlayerOperationsAdapter] add_player called with name='{name}', phone='{phone}', position='{position}', team_id='{team_id}'")
        try:
            if not position or position == PlayerPosition.ANY or position == "any":
                position_enum = PlayerPosition.ANY
            elif isinstance(position, PlayerPosition):
                position_enum = position
            elif isinstance(position, str):
                try:
                    position_enum = PlayerPosition(position.lower())
                except ValueError:
                    logger.warning(f"[PlayerOperationsAdapter] Invalid position '{position}', using ANY")
                    position_enum = PlayerPosition.ANY
            else:
                logger.warning(f"[PlayerOperationsAdapter] Unknown position type '{type(position)}', using ANY")
                position_enum = PlayerPosition.ANY
            
            player = await self.player_service.create_player(name, phone, team_id, position=position_enum)
            success_message = f"✅ Player {player.name} ({player.player_id}) added successfully!"
            if hasattr(player, '_cross_team_warning'):
                success_message += f"\n\n{player._cross_team_warning}"
            return True, success_message
        except Exception as e:
            logger.error(f"[PlayerOperationsAdapter] Error in add_player: {e}", exc_info=True)
            return False, f"Error adding player: {str(e)}"

    async def remove_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] remove_player called with player_id={player_id}, team_id={team_id}")
        try:
            result = await self.player_service.remove_player(player_id, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] remove_player result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error removing player: {e}", exc_info=True)
            return False, f"Error removing player: {str(e)}"

    async def approve_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] approve_player called with player_id={player_id}, team_id={team_id}")
        try:
            result = await self.player_service.approve_player(player_id, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] approve_player result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error approving player: {e}", exc_info=True)
            return False, f"Error approving player: {str(e)}"

    async def reject_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] reject_player called with player_id={player_id}, reason={reason}, team_id={team_id}")
        try:
            result = await self.player_service.reject_player(player_id, reason, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] reject_player result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error rejecting player: {e}", exc_info=True)
            return False, f"Error rejecting player: {str(e)}"

    async def reject_player_by_identifier(self, identifier: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player by player ID or phone number."""
        self.logger.info(f"[PlayerOperationsAdapter] reject_player_by_identifier called with identifier={identifier}, reason={reason}, team_id={team_id}")
        try:
            # Determine if identifier is a player ID or phone number
            if identifier.replace('+', '').isdigit():
                # It's a phone number
                player = await self.player_service.get_player_by_phone(identifier, team_id)
                if not player:
                    return False, f"❌ No player found with phone number {identifier}"
                player_id = player.id
            else:
                # It's a player ID
                player_id = identifier
            
            # Now reject the player using the player ID
            result = await self.player_service.reject_player(player_id, reason, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] reject_player_by_identifier result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error rejecting player by identifier: {e}", exc_info=True)
            return False, f"Error rejecting player: {str(e)}"

    async def update_player_info(self, user_id: str, field: str, value: str, team_id: str) -> tuple[bool, str]:
        """Update a player's information."""
        self.logger.info(f"[PlayerOperationsAdapter] update_player_info called with user_id={user_id}, field={field}, value={value}, team_id={team_id}")
        try:
            # Get the current player
            player = await self.player_service.get_player_by_telegram_id(user_id, team_id)
            if not player:
                return False, "❌ Player not found. Please register first using /register"
            
            # Update the specific field
            field = field.lower()
            if field == "phone":
                # Validate phone number format
                if not value.replace('+', '').isdigit() or len(value.replace('+', '')) < 10:
                    return False, "❌ Invalid phone number format. Please use a valid phone number (e.g., 07123456789 or +447123456789)"
                player.phone = value
                update_message = f"✅ Phone number updated to {value}"
                
            elif field == "emergency":
                # Parse emergency contact (name and phone)
                parts = value.split()
                if len(parts) < 2:
                    return False, "❌ Emergency contact format: /update emergency [name] [phone]"
                contact_name = " ".join(parts[:-1])
                contact_phone = parts[-1]
                if not contact_phone.replace('+', '').isdigit():
                    return False, "❌ Invalid emergency contact phone number"
                player.emergency_contact = {"name": contact_name, "phone": contact_phone}
                update_message = f"✅ Emergency contact updated to {contact_name} ({contact_phone})"
                
            elif field == "dob":
                # Validate date format (YYYY-MM-DD)
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                    player.date_of_birth = value
                    update_message = f"✅ Date of birth updated to {value}"
                except ValueError:
                    return False, "❌ Invalid date format. Please use YYYY-MM-DD (e.g., 1990-01-15)"
                    
            elif field == "position":
                # Validate position
                valid_positions = ["goalkeeper", "defender", "midfielder", "forward", "striker", "winger"]
                if value.lower() not in valid_positions:
                    return False, f"❌ Invalid position. Please choose from: {', '.join(valid_positions)}"
                player.position = value.lower()
                update_message = f"✅ Position updated to {value}"
                
            else:
                return False, f"❌ Unknown field '{field}'. Available fields: phone, emergency, dob, position"
            
            # Save the updated player
            await self.player_service.update_player(player.id, player.to_dict(), team_id)
            
            self.logger.info(f"[PlayerOperationsAdapter] update_player_info success: {update_message}")
            return True, update_message
            
        except Exception as e:
            self.logger.error(f"Error updating player info: {e}", exc_info=True)
            return False, f"Error updating player information: {str(e)}"

    async def get_pending_approvals(self, team_id: str) -> str:
        self.logger.info(f"[PlayerOperationsAdapter] get_pending_approvals called with team_id={team_id}")
        try:
            result = await self.player_service.get_pending_approvals(team_id)
            self.logger.info(f"[PlayerOperationsAdapter] get_pending_approvals result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting pending approvals: {e}", exc_info=True)
            return f"Error getting pending approvals: {str(e)}"

    async def injure_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] injure_player called with player_id={player_id}, team_id={team_id}")
        try:
            result = await self.player_service.injure_player(player_id, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] injure_player result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error injuring player: {e}", exc_info=True)
            return False, f"Error injuring player: {str(e)}"

    async def suspend_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] suspend_player called with player_id={player_id}, reason={reason}, team_id={team_id}")
        try:
            result = await self.player_service.suspend_player(player_id, reason, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] suspend_player result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error suspending player: {e}", exc_info=True)
            return False, f"Error suspending player: {str(e)}"

    async def recover_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PlayerOperationsAdapter] recover_player called with player_id={player_id}, team_id={team_id}")
        try:
            result = await self.player_service.recover_player(player_id, team_id)
            self.logger.info(f"[PlayerOperationsAdapter] recover_player result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error recovering player: {e}", exc_info=True)
            return False, f"Error recovering player: {str(e)}" 