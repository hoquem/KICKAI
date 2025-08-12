#!/usr/bin/env python3
"""
Update Command Handler for KICKAI System

This module provides context-aware routing for the /update command to the appropriate agent
based on chat type. Players in main chat update player info, team members in leadership
chat update team member info.
"""

from typing import Any

from loguru import logger

from kickai.core.interfaces.player_repositories import IPlayerRepository
from kickai.core.interfaces.team_repositories import TeamRepositoryInterface
from kickai.core.value_objects.entity_context import EntityContext


class UpdateCommandHandler:
    """Handler for update commands that can update both players and team members."""

    def __init__(
        self,
        player_repository: IPlayerRepository,
        team_repository: TeamRepositoryInterface,
    ):
        self.player_repository = player_repository
        self.team_repository = team_repository
        self.logger = logger

    async def handle_update_command(
        self, user_context: EntityContext, field: str, value: str
    ) -> dict[str, Any]:
        """
        Handle update command for both players and team members.


            user_context: User context with telegram_id and team_id
            field: Field to update
            value: New value for the field


    :return: Dictionary with update result
    :rtype: str  # TODO: Fix type
        """
        try:
            # Determine if user is a player or team member
            player = await self.player_repository.get_by_telegram_id(
                user_context.telegram_id.value, user_context.team_id.value
            )
            team_member = await self.team_repository.get_team_member_by_telegram_id(
                user_context.telegram_id.value, user_context.team_id.value
            )

            if player and team_member:
                # User is both player and team member - update both
                return await self._update_dual_role_user(user_context, field, value, player, team_member)
            elif player:
                # User is only a player
                return await self._update_player(user_context, field, value, player)
            elif team_member:
                # User is only a team member
                return await self._update_team_member(user_context, field, value, team_member)
            else:
                # User is not registered
                return {
                    "success": False,
                    "message": "❌ You are not registered as a player or team member.",
                    "error": "User not found",
                }

        except Exception as e:
            self.logger.error(f"Error handling update command: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while updating your information.",
                "error": str(e),
            }

    async def _update_player(
        self, user_context: EntityContext, field: str, value: str, player: Any
    ) -> dict[str, Any]:
        """Update player information."""
        try:
            self.logger.info(f"👤 Player update: telegram_id={user_context.telegram_id.value}, field={field}")

            # Validate field is updatable
            if not self._is_player_field_updatable(field):
                return {
                    "success": False,
                    "message": f"❌ Field '{field}' cannot be updated for players.",
                    "error": "Invalid field",
                }

            # Update the player
            updated_player = await self.player_repository.update_player(
                player_id=player.player_id,
                team_id=user_context.team_id.value,
                telegram_id=user_context.telegram_id.value,
                updates={field: value},
            )

            if updated_player:
                return {
                    "success": True,
                    "message": "✅ Player information updated successfully!",
                    "updated_field": field,
                    "new_value": value,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Failed to update player information.",
                    "error": "Update failed",
                }

        except Exception as e:
            self.logger.error(f"Error updating player: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while updating player information.",
                "error": str(e),
            }

    async def _update_team_member(
        self, user_context: EntityContext, field: str, value: str, team_member: Any
    ) -> dict[str, Any]:
        """Update team member information."""
        try:
            self.logger.info(f"👔 Team member update: telegram_id={user_context.telegram_id.value}, field={field}")

            # Validate field is updatable
            if not self._is_team_member_field_updatable(field):
                return {
                    "success": False,
                    "message": f"❌ Field '{field}' cannot be updated for team members.",
                    "error": "Invalid field",
                }

            # Update the team member
            updated_member = await self.team_repository.update_team_member(
                telegram_id=user_context.telegram_id.value,
                team_id=user_context.team_id.value,
                updates={field: value},
            )

            if updated_member:
                return {
                    "success": True,
                    "message": "✅ Team member information updated successfully!",
                    "updated_field": field,
                    "new_value": value,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Failed to update team member information.",
                    "error": "Update failed",
                }

        except Exception as e:
            self.logger.error(f"Error updating team member: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while updating team member information.",
                "error": str(e),
            }

    async def _update_dual_role_user(
        self, user_context: EntityContext, field: str, value: str, player: Any, team_member: Any
    ) -> dict[str, Any]:
        """Update information for a user who is both player and team member."""
        try:
            self.logger.info(f"🔄 Dual role update: telegram_id={user_context.telegram_id.value}, field={field}")

            # Determine which entity to update based on field
            if self._is_player_field_updatable(field):
                return await self._update_player(user_context, field, value, player)
            elif self._is_team_member_field_updatable(field):
                return await self._update_team_member(user_context, field, value, team_member)
            else:
                return {
                    "success": False,
                    "message": f"❌ Field '{field}' cannot be updated.",
                    "error": "Invalid field",
                }

        except Exception as e:
            self.logger.error(f"Error updating dual role user: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while updating your information.",
                "error": str(e),
            }

    def _is_player_field_updatable(self, field: str) -> bool:
        """Check if a field can be updated for players."""
        updatable_fields = {
            "name",
            "phone_number",
            "email",
            "position",
            "preferred_foot",
            "jersey_number",
            "emergency_contact",
            "medical_notes",
        }
        return field in updatable_fields

    def _is_team_member_field_updatable(self, field: str) -> bool:
        """Check if a field can be updated for team members."""
        updatable_fields = {
            "name",
            "phone_number",
            "email",
            "emergency_contact",
        }
        return field in updatable_fields

    async def get_updatable_fields(self, user_context: EntityContext) -> dict[str, Any]:
        """
        Get list of updatable fields for the user.


            user_context: User context


    :return: Dictionary with updatable fields
    :rtype: str  # TODO: Fix type
        """
        try:
            player = await self.player_repository.get_by_telegram_id(
                user_context.telegram_id.value, user_context.team_id.value
            )
            team_member = await self.team_repository.get_team_member_by_telegram_id(
                user_context.telegram_id.value, user_context.team_id.value
            )

            player_fields = []
            team_member_fields = []

            if player:
                player_fields = [
                    "name",
                    "phone_number",
                    "email",
                    "position",
                    "preferred_foot",
                    "jersey_number",
                    "emergency_contact",
                    "medical_notes",
                ]

            if team_member:
                team_member_fields = [
                    "name",
                    "phone_number",
                    "email",
                    "emergency_contact",
                ]

            return {
                "success": True,
                "player_fields": player_fields,
                "team_member_fields": team_member_fields,
                "is_player": player is not None,
                "is_team_member": team_member is not None,
            }

        except Exception as e:
            self.logger.error(f"Error getting updatable fields: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while getting updatable fields.",
                "error": str(e),
            }
