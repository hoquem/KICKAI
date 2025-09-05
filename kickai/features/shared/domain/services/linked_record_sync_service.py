#!/usr/bin/env python3
"""
Linked Record Sync Service

This service handles bidirectional synchronization of common fields between
Player and TeamMember records that are linked by telegram_id.

When a Player or TeamMember record is updated, this service ensures that
any linked record (same telegram_id) is also updated with the same information
for common fields like phone_number, email, and emergency contact details.
"""

from dataclasses import dataclass

from loguru import logger

from kickai.core.dependency_container import get_container


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    synced_fields: list[str]
    error_message: str | None = None
    target_entity_updated: bool = False


class LinkedRecordSyncService:
    """Service for synchronizing common fields between Player and TeamMember records."""

    # Fields that can be synced between Player and TeamMember entities
    SYNCABLE_FIELDS = {"phone_number", "email", "emergency_contact_name", "emergency_contact_phone"}

    def __init__(self):
        """Initialize the sync service."""
        self.container = get_container()

    async def sync_player_to_team_member(
        self, telegram_id: int, updated_fields: dict[str, any]
    ) -> SyncResult:
        """
        Sync updated Player fields to linked TeamMember record.

        Args:
            telegram_id: Telegram ID linking the records
            updated_fields: Dictionary of field names and their new values

        Returns:
            SyncResult indicating success/failure and what was synced
        """
        try:
            logger.info(f"🔄 Syncing player fields to team member for telegram_id: {telegram_id}")

            # Filter to only syncable fields that actually changed
            syncable_updates = {
                field: value
                for field, value in updated_fields.items()
                if field in self.SYNCABLE_FIELDS and value is not None
            }

            if not syncable_updates:
                logger.debug(f"No syncable fields to update for telegram_id: {telegram_id}")
                return SyncResult(success=True, synced_fields=[], target_entity_updated=False)

            # Get team member service
            from kickai.features.team_administration.domain.services.team_member_service import (
                TeamMemberService,
            )

            team_member_service = self.container.get_service(TeamMemberService)
            if not team_member_service:
                logger.warning("TeamMemberService not available for sync")
                return SyncResult(
                    success=False, synced_fields=[], error_message="TeamMemberService not available"
                )

            # Find linked team member by telegram_id
            team_members = await team_member_service.get_members_by_telegram_id(telegram_id)

            if not team_members:
                logger.debug(f"No linked team member found for telegram_id: {telegram_id}")
                return SyncResult(success=True, synced_fields=[], target_entity_updated=False)

            # Update each linked team member (there should typically be only one)
            synced_fields = []
            for team_member in team_members:
                logger.info(f"🔄 Updating team member {team_member.member_id} with player data")

                # Update the team member with syncable fields
                for field, value in syncable_updates.items():
                    if hasattr(team_member, field):
                        setattr(team_member, field, value)
                        synced_fields.append(field)
                        logger.debug(f"   • {field}: {value}")

                # Save the updated team member
                await team_member_service.update_team_member(team_member)

            logger.info(f"✅ Successfully synced {len(synced_fields)} fields to team member")
            return SyncResult(
                success=True,
                synced_fields=list(set(synced_fields)),  # Remove duplicates
                target_entity_updated=True,
            )

        except Exception as e:
            logger.error(f"❌ Error syncing player to team member: {e}")
            return SyncResult(success=False, synced_fields=[], error_message=str(e))

    async def sync_team_member_to_player(
        self, telegram_id: int, updated_fields: dict[str, any]
    ) -> SyncResult:
        """
        Sync updated TeamMember fields to linked Player record.

        Args:
            telegram_id: Telegram ID linking the records
            updated_fields: Dictionary of field names and their new values

        Returns:
            SyncResult indicating success/failure and what was synced
        """
        try:
            logger.info(f"🔄 Syncing team member fields to player for telegram_id: {telegram_id}")

            # Filter to only syncable fields that actually changed
            syncable_updates = {
                field: value
                for field, value in updated_fields.items()
                if field in self.SYNCABLE_FIELDS and value is not None
            }

            if not syncable_updates:
                logger.debug(f"No syncable fields to update for telegram_id: {telegram_id}")
                return SyncResult(success=True, synced_fields=[], target_entity_updated=False)

            # Get player service
            from kickai.features.player_registration.domain.services.player_service import (
                PlayerService,
            )

            player_service = self.container.get_service(PlayerService)
            if not player_service:
                logger.warning("PlayerService not available for sync")
                return SyncResult(
                    success=False, synced_fields=[], error_message="PlayerService not available"
                )

            # Find linked player by telegram_id
            players = await player_service.get_players_by_telegram_id(telegram_id)

            if not players:
                logger.debug(f"No linked player found for telegram_id: {telegram_id}")
                return SyncResult(success=True, synced_fields=[], target_entity_updated=False)

            # Update each linked player (there should typically be only one per team)
            synced_fields = []
            for player in players:
                logger.info(f"🔄 Updating player {player.player_id} with team member data")

                # Update the player with syncable fields
                for field, value in syncable_updates.items():
                    if hasattr(player, field):
                        setattr(player, field, value)
                        synced_fields.append(field)
                        logger.debug(f"   • {field}: {value}")

                # Save the updated player
                await player_service.update_player(player)

            logger.info(f"✅ Successfully synced {len(synced_fields)} fields to player")
            return SyncResult(
                success=True,
                synced_fields=list(set(synced_fields)),  # Remove duplicates
                target_entity_updated=True,
            )

        except Exception as e:
            logger.error(f"❌ Error syncing team member to player: {e}")
            return SyncResult(success=False, synced_fields=[], error_message=str(e))

    def get_syncable_fields(self) -> set[str]:
        """
        Get set of fields that can be synchronized between entities.

        Returns:
            Set of syncable field names
        """
        return self.SYNCABLE_FIELDS.copy()

    def is_field_syncable(self, field_name: str) -> bool:
        """
        Check if a field can be synchronized between entities.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field can be synced, False otherwise
        """
        return field_name in self.SYNCABLE_FIELDS

    def create_sync_summary(
        self, sync_result: SyncResult, source_entity: str, target_entity: str
    ) -> str:
        """
        Create a human-readable summary of sync operation.

        Args:
            sync_result: Result of the sync operation
            source_entity: Name of source entity ('player' or 'team_member')
            target_entity: Name of target entity ('player' or 'team_member')

        Returns:
            Human-readable sync summary
        """
        if not sync_result.success:
            return f"❌ Failed to sync {source_entity} data to {target_entity}: {sync_result.error_message}"

        if not sync_result.target_entity_updated:
            return f"ℹ️ No linked {target_entity} found - only {source_entity} updated"

        if not sync_result.synced_fields:
            return f"ℹ️ No common fields to sync between {source_entity} and {target_entity}"

        synced_list = ", ".join(sync_result.synced_fields)
        return f"✅ Updated {source_entity} and synced to linked {target_entity}: {synced_list}"

    async def sync_update_operation(
        self, entity_type: str, telegram_id: int, updated_fields: dict[str, any]
    ) -> SyncResult:
        """
        Perform sync operation based on entity type.

        Args:
            entity_type: 'player' or 'team_member'
            telegram_id: Telegram ID linking the records
            updated_fields: Dictionary of updated fields

        Returns:
            SyncResult from the appropriate sync operation
        """
        # Filter out None values
        filtered_fields = {
            field: value for field, value in updated_fields.items() if value is not None
        }

        if entity_type == "player":
            return await self.sync_player_to_team_member(telegram_id, filtered_fields)
        elif entity_type == "team_member":
            return await self.sync_team_member_to_player(telegram_id, filtered_fields)
        else:
            logger.error(f"Unknown entity type for sync: {entity_type}")
            return SyncResult(
                success=False, synced_fields=[], error_message=f"Unknown entity type: {entity_type}"
            )

    def log_sync_operation(
        self,
        entity_type: str,
        telegram_id: int,
        updated_fields: dict[str, any],
        sync_result: SyncResult,
    ):
        """
        Log the sync operation for audit purposes.

        Args:
            entity_type: Source entity type
            telegram_id: Telegram ID
            updated_fields: Fields that were updated
            sync_result: Result of sync operation
        """
        target_entity = "team_member" if entity_type == "player" else "player"

        log_entry = {
            "operation": "linked_record_sync",
            "source_entity": entity_type,
            "target_entity": target_entity,
            "telegram_id": telegram_id,
            "updated_fields": list(updated_fields.keys()),
            "synced_fields": sync_result.synced_fields,
            "success": sync_result.success,
            "target_updated": sync_result.target_entity_updated,
        }

        if sync_result.success:
            logger.info(f"📋 Sync audit: {log_entry}")
        else:
            logger.error(f"📋 Sync audit (failed): {log_entry}")


# Global instance for use across the system
linked_record_sync_service = LinkedRecordSyncService()
