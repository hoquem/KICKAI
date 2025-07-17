#!/usr/bin/env python3
"""
Player Service Implementation

This module provides the business logic for player management operations.
"""

import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.interfaces.player_operations import IPlayerOperations as IPlayerService
from domain.interfaces.player_models import PlayerPosition, PlayerRole, OnboardingStatus
from database.models_improved import Player as InfrastructurePlayer
from domain.interfaces.user_management import IExternalPlayerService
from database.interfaces import DataStoreInterface
from database.firebase_client import FirebaseClient
from core.exceptions import (
    DatabaseError, ConnectionError, NotFoundError, 
    DuplicateError, create_error_context,
    PlayerError, PlayerValidationError, PlayerDuplicateError, PlayerNotFoundError
)
from utils.phone_utils import normalize_phone, get_phone_variants
from utils.validation_utils import validate_phone_with_error, validate_name_with_error, validate_email_with_error, validate_team_id_with_error
from utils.enum_utils import serialize_enums_for_firestore
from utils.player_id_service import generate_unique_player_id

logger = logging.getLogger(__name__)


class PlayerService(IPlayerService):
    """Implementation of the player service interface."""
    
    def __init__(self, data_store: DataStoreInterface, external_player_service: Optional[IExternalPlayerService] = None, team_id: Optional[str] = None):
        self._data_store = data_store
        self._external_player_service = external_player_service
        self._team_id = team_id
    
    async def create_player(self, name: str, phone: str, team_id: str, 
                          email: Optional[str] = None, position: PlayerPosition = None,
                          role: PlayerRole = PlayerRole.PLAYER, fa_registered: bool = False, player_id: Optional[str] = None) -> InfrastructurePlayer:
        """Create a new player with validation and Firestore-backed unique player_id."""
        try:
            # Validate input data
            self._validate_player_data(name, phone, email, team_id)
            
            # Normalize phone number for storage
            normalized_phone = normalize_phone(phone)
            if not normalized_phone:
                raise PlayerValidationError(
                    f"Invalid phone number format: {phone}",
                    create_error_context("create_player", team_id=team_id)
                )
            
            # Check for duplicate phone number in any team using normalized phone
            all_players_with_phone = await self._data_store.query_documents('players', [
                {'field': 'phone', 'operator': '==', 'value': normalized_phone}
            ])
            
            # Block if any player in the same team
            for p in all_players_with_phone:
                if p.get('team_id') == team_id:
                    raise PlayerDuplicateError(
                        f"Player with phone {phone} already exists in team {team_id}",
                        create_error_context("create_player", team_id=team_id, additional_info={'phone': phone})
                    )
            
            # If player exists in other teams, collect team names for warning
            other_teams = [p.get('team_id') for p in all_players_with_phone if p.get('team_id') != team_id]
            other_team_names = []
            if other_teams:
                # Try to get team names for these IDs
                # Note: This would need team_operations injected if we want to get team names
                # For now, just use team IDs
                for otid in set(other_teams):
                    other_team_names.append(otid)
            
            # --- Centralized player_id generation ---
            if player_id:
                generated_player_id = player_id
            else:
                # Use the centralized player ID service
                generated_player_id = await generate_unique_player_id(name, team_id, self._data_store)

            # Default position to ANY if not provided
            if position is None:
                from domain.interfaces.player_models import PlayerPosition
                position = PlayerPosition.ANY

            # Create player object with normalized phone and generated ID
            player = InfrastructurePlayer(
                id=generated_player_id, # Set the id to the generated player_id
                player_id=generated_player_id, # Set the player_id to the generated player_id
                name=name,
                phone=phone,
                email=email,
                position=position,
                role=role,
                fa_registered=fa_registered,
                team_id=team_id,
                onboarding_status=OnboardingStatus.PENDING
            )
            
            logging.info(f"Creating player with data: {player.to_dict()}")
            
            # Ensure enums are serialized for Firestore
            await self._data_store.create_player(player)

            # If external_id is provided, create/update in external system
            if player.external_id:
                try:
                    await self._external_player_service.create_external_player(player.to_dict())
                    logging.info(f"Player {player.name} ({player.id}) also created in external system.")
                except Exception as ex_e:
                    logging.warning(f"Failed to create player {player.name} in external system: {ex_e}")
            
            logging.info(
                f"Player created successfully: {player.name} ({generated_player_id})"
            )
            
            # If there are cross-team warnings, attach to player object for handler to use
            if other_team_names:
                player._cross_team_warning = f"⚠️ Note: Player with this phone exists in other team(s): {', '.join(other_team_names)}"
            
            return player
        
        except (PlayerError, PlayerDuplicateError):
            raise
        except Exception as e:
            logging.error(f"Failed to create player: {e}")
            raise PlayerError(
                f"Failed to create player: {str(e)}",
                create_error_context("create_player", team_id=team_id)
            )
    
    async def get_player(self, player_id: str) -> Optional[InfrastructurePlayer]:
        """Get a player by ID."""
        try:
            player = await self._data_store.get_player(player_id)
            if player:
                logging.info(
                    f"Player retrieved: {player.name}"
                )
            return player
            
        except Exception as e:
            logging.error(f"Failed to get player: {e} (player_id={player_id})")
            raise PlayerError(
                f"Failed to get player: {str(e)}",
                create_error_context("get_player", entity_id=player_id)
            )
    
    async def update_player(self, player_id: str, **updates) -> InfrastructurePlayer:
        """Update a player with validation."""
        try:
            # Get existing player
            player = await self.get_player(player_id)
            if not player:
                raise PlayerNotFoundError(
                    f"Player not found: {player_id}",
                    create_error_context("update_player", entity_id=player_id)
                )
            
            # Validate updates if they include validation fields
            if 'name' in updates:
                self._validate_name(updates['name'])
            if 'phone' in updates:
                # Normalize phone number for storage
                normalized_phone = normalize_phone(updates['phone'])
                if not normalized_phone:
                    raise PlayerValidationError(
                        f"Invalid phone number format: {updates['phone']}",
                        create_error_context("update_player", entity_id=player_id)
                    )
                updates['phone'] = normalized_phone
                
                # Check for duplicate phone if changed
                if normalized_phone != player.phone:
                    existing_player = await self._data_store.get_player_by_phone(normalized_phone, player.team_id)
                    if existing_player and existing_player.id != player_id:
                        raise PlayerDuplicateError(
                            f"Player with phone {updates['phone']} already exists in team {player.team_id}",
                            create_error_context("update_player", entity_id=player_id, team_id=player.team_id)
                        )
            if 'email' in updates:
                self._validate_email(updates['email'])
            
            # Update player - FirebaseClient.update_player now returns Optional[Player]
            updated_player = await self._data_store.update_player(player_id, updates)
            if not updated_player:
                raise PlayerError(
                    f"Failed to update player {player_id}",
                    create_error_context("update_player", entity_id=player_id)
                )
            
            logging.info(
                f"Player updated: {updated_player.name} ({player_id})"
            )
            
            return updated_player
            
        except (PlayerError, PlayerNotFoundError, PlayerDuplicateError):
            raise
        except Exception as e:
            logging.error(f"Failed to update player: {e}")
            raise PlayerError(
                f"Failed to update player: {str(e)}",
                create_error_context("update_player", entity_id=player_id)
            )
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        try:
            success = await self._data_store.delete_player(player_id)
            
            if success:
                logging.info(
                    f"Player deleted: {player_id}"
                )
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to delete player: {e}")
            raise PlayerError(
                f"Failed to delete player: {str(e)}",
                create_error_context("delete_player", entity_id=player_id)
            )
    
    async def get_team_players(self, team_id: str) -> List[InfrastructurePlayer]:
        """Get all players for a team."""
        try:
            players = await self._data_store.get_players_by_team(team_id)
            
            logging.info(
                f"Retrieved {len(players)} players for team {team_id}"
            )
            
            return players
            
        except Exception as e:
            logging.error(f"Failed to get team players: {e}")
            raise PlayerError(
                f"Failed to get team players: {str(e)}",
                create_error_context("get_team_players", team_id=team_id)
            )
    
    async def get_players_by_team(self, team_id: str) -> List[InfrastructurePlayer]:
        """Get all players for a team (interface compatibility)."""
        return await self.get_team_players(team_id)
    
    async def get_players_by_status(self, team_id: str, status: OnboardingStatus) -> List[InfrastructurePlayer]:
        """Get players by onboarding status."""
        try:
            players = await self._data_store.get_players_by_status(team_id, status)
            
            logging.info(
                f"Retrieved {len(players)} players with status {status.value} for team {team_id}"
            )
            
            return players
            
        except Exception as e:
            logging.error(f"Failed to get players by status: {e}")
            raise PlayerError(
                f"Failed to get players by status: {str(e)}",
                create_error_context("get_players_by_status", team_id=team_id, status=status.value)
            )
    
    async def get_all_players(self, team_id: str) -> List[InfrastructurePlayer]:
        """Get all players for a team (interface compatibility)."""
        return await self.get_team_players(team_id)
    
    async def get_player_by_phone(self, phone: str, team_id: Optional[str] = None) -> Optional[InfrastructurePlayer]:
        """Get a player by phone number, optionally filtered by team."""
        try:
            # If team_id is provided, use it; otherwise use the instance team_id
            target_team_id = team_id or self._team_id
            
            # Get all phone variants for flexible matching
            phone_variants = get_phone_variants(phone)
            
            # Try to find player with any of the phone variants
            for variant in phone_variants:
                player = await self._data_store.get_player_by_phone(variant, target_team_id)
                if player:
                    logging.info(f"Found player {player.name} with phone variant {variant}")
                    return player
            
            logging.info(f"No player found with phone variants: {phone_variants}")
            return None
            
        except Exception as e:
            logging.error(f"Failed to get player by phone: {e}")
            raise PlayerError(
                f"Failed to get player by phone: {str(e)}",
                create_error_context("get_player_by_phone", additional_info={'phone': phone, 'team_id': team_id})
            )
    
    async def get_player_by_telegram_id(self, telegram_id: str, team_id: Optional[str] = None) -> Optional[InfrastructurePlayer]:
        """Get a player by Telegram ID, optionally filtered by team."""
        print(f"🔍 [DEBUG] PlayerService.get_player_by_telegram_id called with telegram_id={telegram_id}, team_id={team_id}")
        try:
            # If team_id is provided, use it; otherwise use the instance team_id
            target_team_id = team_id or self._team_id
            print(f"🔍 [DEBUG] PlayerService using target_team_id={target_team_id}")
            if not target_team_id:
                print(f"🔍 [DEBUG] PlayerService: No team_id provided for get_player_by_telegram_id")
                logging.info(f"No team_id provided for get_player_by_telegram_id")
                return None
            # Use efficient Firestore query
            print(f"🔍 [DEBUG] PlayerService calling _data_store.get_player_by_telegram_id({telegram_id}, {target_team_id})")
            player = await self._data_store.get_player_by_telegram_id(telegram_id, target_team_id)
            print(f"🔍 [DEBUG] PlayerService._data_store.get_player_by_telegram_id result: {player}")
            if player:
                print(f"🔍 [DEBUG] PlayerService: Found player {player.name} with telegram_id {telegram_id}")
                logging.info(f"Found player {player.name} with telegram_id {telegram_id}")
                return player
            print(f"🔍 [DEBUG] PlayerService: No player found with telegram_id: {telegram_id}")
            logging.info(f"No player found with telegram_id: {telegram_id}")
            return None
        except Exception as e:
            print(f"❌ [DEBUG] PlayerService.get_player_by_telegram_id exception: {e}")
            logging.error(f"Failed to get player by telegram_id: {e}")
            raise PlayerError(
                f"Failed to get player by telegram_id: {str(e)}",
                create_error_context("get_player_by_telegram_id", additional_info={'telegram_id': telegram_id, 'team_id': team_id})
            )

    async def register_player(self, user_id: str, team_id: str, player_id: Optional[str] = None) -> tuple[bool, str]:
        """Register a player (complete onboarding process)."""
        try:
            # First, check if a player with this Telegram ID already exists
            existing_player_with_telegram_id = await self.get_player_by_telegram_id(user_id, team_id)
            
            # Get the player by ID or create a new one
            if player_id:
                player = await self.get_player(player_id)
                if not player:
                    return False, f"Player with ID {player_id} not found"
            else:
                # This would typically be called during onboarding
                # For now, return an error indicating player needs to be created first
                return False, "Player must be created first using /add command"
            
            # If a player with this Telegram ID already exists, check if it's the same player
            if existing_player_with_telegram_id:
                # Check if the existing player's ID matches the provided player_id
                if existing_player_with_telegram_id.player_id == player_id:
                    # Same player, just confirm registration and show details
                    detailed_status = existing_player_with_telegram_id.get_detailed_status()
                    return True, f"✅ You are already registered!\n\n👤 Player Details:\n• Name: {existing_player_with_telegram_id.name}\n• Player ID: {existing_player_with_telegram_id.player_id}\n• Phone: {existing_player_with_telegram_id.phone}\n• Position: {existing_player_with_telegram_id.position.value.title()}\n• Status: {detailed_status}"
                else:
                    # Different player ID, show conflict message
                    return False, f"❌ A player with your Telegram ID is already registered in the system.\n\n👤 Player Details:\n• Name: {existing_player_with_telegram_id.name}\n• Player ID: {existing_player_with_telegram_id.player_id}\n• Phone: {existing_player_with_telegram_id.phone}\n\n💡 To complete your registration:\nPlease ask the club admin to remove the existing player record so you can register with your correct player ID.\n\n🔧 Admin Action Required:\nUse `/remove {existing_player_with_telegram_id.player_id}` in the leadership chat.\n\n💡 Please contact the team admin if you believe this is an error."
            
            # Check if the player already has a Telegram ID
            if player.telegram_id and player.telegram_id != user_id:
                return False, f"❌ Player {player.name} ({player.player_id}) is already registered with a different Telegram account.\n\n💡 Please contact the team admin if you believe this is an error."
            
            # Update player status to completed onboarding and link Telegram ID
            update_data = serialize_enums_for_firestore({
                'onboarding_status': OnboardingStatus.COMPLETED,
                'onboarding_completed_at': datetime.now().isoformat(),
                'telegram_id': user_id,
            })
            await self._data_store.update_player(player_id, update_data)
            
            return True, f"✅ Player {player.name} ({player.player_id}) registration completed!"
            
        except Exception as e:
            logging.error(f"Failed to register player: {e}")
            return False, f"Error registering player: {str(e)}"

    async def approve_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Approve a player for match squad selection."""
        try:
            player = await self.get_player(player_id)
            if not player:
                return False, f"Player with ID {player_id} not found"
            
            # Update player to approved status - also set onboarding to completed
            update_data = serialize_enums_for_firestore({
                'admin_approved': True,
                'admin_approved_at': datetime.now().isoformat(),
                'onboarding_status': OnboardingStatus.COMPLETED,
                'onboarding_completed_at': datetime.now().isoformat(),
            })
            await self._data_store.update_player(player_id, update_data)
            
            return True, f"✅ Player {player.name} ({player_id}) approved successfully!"
        except Exception as e:
            logger.error(f"Failed to approve player: {e}")
            return False, f"Error approving player: {e}"

    async def reject_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player for match squad selection."""
        try:
            player = await self.get_player(player_id)
            if not player:
                return False, f"Player with ID {player_id} not found"
            
            # Update player status (could be enhanced with rejection details)
            updated_player = await self.update_player(
                player.id,
                admin_approved=False,
                onboarding_status=OnboardingStatus.FAILED.value
            )
            
            return True, f"❌ Player {updated_player.name} ({updated_player.player_id}) rejected. Reason: {reason}"
            
        except Exception as e:
            logging.error(f"Failed to reject player: {e}")
            return False, f"Error rejecting player: {str(e)}"

    async def get_pending_approvals(self, team_id: str) -> str:
        """Get list of players pending approval."""
        try:
            # Get all team players and filter for pending approval
            all_players = await self.get_team_players(team_id)
            pending_players = [p for p in all_players if p.is_pending_approval()]
            
            if not pending_players:
                return "✅ No players pending approval"
            
            result = "📋 Players pending approval:\n"
            for player in pending_players:
                result += f"• {player.player_id} - {player.name} ({player.phone})\n"
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to get pending approvals: {e}")
            return f"Error getting pending approvals: {str(e)}"

    async def get_player_info(self, user_id: str, team_id: str) -> tuple[bool, str]:
        """Get player information by user ID."""
        print(f"🔍 [DEBUG] PlayerService.get_player_info called with user_id={user_id}, team_id={team_id}")
        try:
            print(f"🔍 [DEBUG] PlayerService calling get_player_by_telegram_id({user_id}, {team_id})")
            player = await self.get_player_by_telegram_id(user_id, team_id)
            print(f"🔍 [DEBUG] PlayerService.get_player_by_telegram_id result: {player}")
            
            if not player:
                print(f"🔍 [DEBUG] PlayerService: Player not found for user_id={user_id}")
                return False, "Player not found. Please register first."
            
            detailed_status = player.get_detailed_status()
            result = f"👤 {player.name} ({player.player_id})\n📱 {player.phone}\n🏃 {player.position.value.title()}\n📊 Status: {detailed_status}"
            print(f"🔍 [DEBUG] PlayerService.get_player_info returning: {result}")
            # Remove markdown, use plain text formatting
            return True, result
            
        except Exception as e:
            print(f"❌ [DEBUG] PlayerService.get_player_info exception: {e}")
            logging.error(f"Failed to get player info: {e}")
            return False, f"Error getting player info: {str(e)}"

    async def list_players(self, team_id: str, is_leadership_chat: bool = False) -> str:
        """List all players in a team."""
        try:
            players = await self.get_team_players(team_id)
            if not players:
                return "📋 No players found in the team."
            
            # Group players by status
            active_players = [p for p in players if p.is_active()]
            pending_players = [p for p in players if p.is_pending_approval()]
            injured_players = [p for p in players if p.is_injured]
            suspended_players = [p for p in players if p.is_suspended]

            # Only count players that will be shown
            total_listed = len(active_players) + len(pending_players) + len(injured_players) + len(suspended_players)

            lines = [f"📋 Team Players ({total_listed} total)"]
            
            if active_players:
                lines.append("\n✅ Active Players:")
                for player in active_players:
                    info = f"• {player.player_id} - {player.name}"
                    if player.position:
                        info += f" ({player.position.value.title()})"
                    lines.append(info)
            
            if pending_players:
                lines.append("\n⏳ Pending Approval:")
                for player in pending_players:
                    info = f"• {player.player_id} - {player.name}"
                    if player.phone:
                        info += f" ({player.phone})"
                    lines.append(info)
            
            if injured_players:
                lines.append("\n🏥 Injured Players:")
                for player in injured_players:
                    details = player.injury_details or "No details"
                    lines.append(f"• {player.player_id} - {player.name} ({details})")
            
            if suspended_players:
                lines.append("\n🚫 Suspended Players:")
                for player in suspended_players:
                    details = player.suspension_details or "No details"
                    lines.append(f"• {player.player_id} - {player.name} ({details})")
            
            return "\n".join(lines)
        except Exception as e:
            logging.error(f"Failed to list players: {e}")
            return f"Error listing players: {str(e)}"

    async def remove_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Remove a player from the team."""
        try:
            player = await self.get_player(player_id)
            if not player:
                return False, f"Player with ID {player_id} not found"
            
            success = await self.delete_player(player_id)
            if success:
                return True, f"✅ Player {player.name} ({player.player_id}) removed from the team"
            else:
                return False, f"Failed to remove player {player.name}"
            
        except Exception as e:
            logging.error(f"Failed to remove player: {e}")
            return False, f"Error removing player: {str(e)}"

    async def injure_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as injured."""
        try:
            player = await self.get_player(player_id)
            if not player:
                return False, f"Player with ID {player_id} not found"
            
            updated_player = await self.update_player(
                player.id,
                is_injured=True,
                injury_details="Marked as injured by admin"
            )
            
            return True, f"🏥 Player {updated_player.name} ({updated_player.player_id}) marked as injured"
            
        except Exception as e:
            logging.error(f"Failed to injure player: {e}")
            return False, f"Error injuring player: {str(e)}"

    async def suspend_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as suspended."""
        try:
            player = await self.get_player(player_id)
            if not player:
                return False, f"Player with ID {player_id} not found"
            
            updated_player = await self.update_player(
                player.id,
                is_suspended=True,
                suspension_details=reason
            )
            
            return True, f"🚫 Player {updated_player.name} ({updated_player.player_id}) suspended. Reason: {reason}"
            
        except Exception as e:
            logging.error(f"Failed to suspend player: {e}")
            return False, f"Error suspending player: {str(e)}"

    async def recover_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as recovered from injury/suspension."""
        try:
            player = await self.get_player(player_id)
            if not player:
                return False, f"Player with ID {player_id} not found"
            
            updated_player = await self.update_player(
                player.id,
                is_injured=False,
                injury_details=None,
                is_suspended=False,
                suspension_details=None,
                return_date=None
            )
            
            return True, f"✅ Player {updated_player.name} ({updated_player.player_id}) recovered and eligible for matches"
            
        except Exception as e:
            logging.error(f"Failed to recover player: {e}")
            return False, f"Error recovering player: {str(e)}"
    
    async def add_player(self, name: str, phone: str, position: str, team_id: str) -> tuple[bool, str]:
        """Add a new player to the team."""
        try:
            # Convert position string to enum
            from domain.interfaces.player_models import PlayerPosition
            position_enum = PlayerPosition(position.lower()) if position else PlayerPosition.ANY
            
            # Create player
            player = await self.create_player(
                name=name,
                phone=phone,
                team_id=team_id,
                position=position_enum
            )
            
            return True, f"Player {player.name} ({player.player_id}) added successfully"
            
        except Exception as e:
            logging.error(f"Failed to add player: {e}")
            return False, f"Failed to add player: {str(e)}"
    
    async def reject_player_by_identifier(self, identifier: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player by player ID or phone number."""
        try:
            # Try to find player by ID first, then by phone
            player = await self.get_player(identifier)
            if not player:
                # Try by phone
                player = await self.get_player_by_phone(identifier, team_id)
            
            if not player:
                return False, f"Player with identifier {identifier} not found"
            
            # Use the existing reject_player method
            return await self.reject_player(player.player_id, reason, team_id)
            
        except Exception as e:
            logging.error(f"Failed to reject player by identifier {identifier}: {e}")
            return False, f"Failed to reject player: {str(e)}"
    
    async def update_player_info(self, user_id: str, field: str, value: str, team_id: str) -> tuple[bool, str]:
        """Update a player's information."""
        try:
            # Find player by telegram user_id
            player = await self.get_player_by_telegram_id(user_id, team_id)
            if not player:
                return False, f"Player with telegram ID {user_id} not found"
            
            # Validate field
            allowed_fields = ['name', 'phone', 'email', 'position']
            if field not in allowed_fields:
                return False, f"Invalid field '{field}'. Allowed fields: {', '.join(allowed_fields)}"
            
            # Validate value based on field
            if field == 'phone':
                normalized_phone = normalize_phone(value)
                if not normalized_phone:
                    return False, f"Invalid phone number format: {value}"
                value = normalized_phone
            elif field == 'position':
                from domain.interfaces.player_models import PlayerPosition
                try:
                    position_enum = PlayerPosition(value.lower())
                    value = position_enum.value
                except ValueError:
                    return False, f"Invalid position '{value}'. Valid positions: {', '.join([p.value for p in PlayerPosition])}"
            
            # Update player
            updates = {field: value}
            updated_player = await self.update_player(player.player_id, **updates)
            
            return True, f"Player {updated_player.name} {field} updated successfully"
            
        except Exception as e:
            logging.error(f"Failed to update player info: {e}")
            return False, f"Failed to update player info: {str(e)}"
    
    # Validation methods
    def _validate_player_data(self, name: str, phone: str, email: Optional[str], team_id: str):
        """Validate player data using centralized validation functions."""
        # Validate name
        is_valid, error_msg = validate_name_with_error(name)
        if not is_valid:
            raise PlayerValidationError(
                error_msg,
                create_error_context("validate_name")
            )
        
        # Validate phone
        is_valid, error_msg = validate_phone_with_error(phone)
        if not is_valid:
            raise PlayerValidationError(
                error_msg,
                create_error_context("validate_phone")
            )
        
        # Validate email (if provided)
        if email:
            is_valid, error_msg = validate_email_with_error(email)
            if not is_valid:
                raise PlayerValidationError(
                    error_msg,
                    create_error_context("validate_email")
                )
        
        # Validate team ID
        is_valid, error_msg = validate_team_id_with_error(team_id)
        if not is_valid:
            raise PlayerValidationError(
                error_msg,
                create_error_context("validate_team_id")
            )
    
    def _validate_name(self, name: str):
        """Validate player name using centralized validation."""
        is_valid, error_msg = validate_name_with_error(name)
        if not is_valid:
            raise PlayerValidationError(
                error_msg,
                create_error_context("validate_name")
            )
    
    def _validate_phone(self, phone: str):
        """Validate phone number using centralized validation."""
        is_valid, error_msg = validate_phone_with_error(phone)
        if not is_valid:
            raise PlayerValidationError(
                error_msg,
                create_error_context("validate_phone")
            )
    
    def _validate_email(self, email: str):
        """Validate email address using centralized validation."""
        if not email or not email.strip():
            return  # Email is optional
        
        is_valid, error_msg = validate_email_with_error(email)
        if not is_valid:
            raise PlayerValidationError(
                error_msg,
                create_error_context("validate_email")
            )
    
    def _validate_team_id(self, team_id: str):
        """Validate team ID format."""
        validate_team_id_with_error(team_id)


# Global instance and convenience function
_player_service: Optional[PlayerService] = None


def get_player_service(team_id: Optional[str] = None) -> PlayerService:
    """Get the global player service instance."""
    global _player_service
    if _player_service is None:
        from core.dependency_container import get_singleton
        data_store = get_singleton("data_store")
        _player_service = PlayerService(data_store, team_id=team_id)
    return _player_service 