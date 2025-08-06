#!/usr/bin/env python3
"""
Availability Management Tools

This module provides tools for managing player availability for matches.
"""

import logging

from crewai import Tool

from kickai.features.match_management.domain.entities.availability import AvailabilityStatus
from kickai.features.match_management.domain.services.availability_service import (
    AvailabilityService,
)

logger = logging.getLogger(__name__)


class MarkAvailabilityTool(Tool):
    """Tool for marking player availability for matches."""

    name: str = "mark_availability"
    description: str = "Mark player availability for a match (available, unavailable, maybe)"

    def __init__(self, availability_service: AvailabilityService):
        super().__init__()
        self.availability_service = availability_service

    def _run(
        self,
        match_id: str,
        player_id: str,
        status: str,  # available, unavailable, maybe
        reason: str | None = None,
    ) -> str:
        """Mark player availability for a match."""
        try:
            # Convert status string to enum
            try:
                availability_status = AvailabilityStatus(status.lower())
            except ValueError:
                return f"❌ **Invalid status**: {status}. Valid options: available, unavailable, maybe"

            # Mark availability
            availability = self.availability_service.mark_availability(
                match_id=match_id,
                player_id=player_id,
                status=availability_status,
                reason=reason,
            )

            # Get availability summary for the match
            summary = self.availability_service.get_availability_summary(match_id)

            result = [
                "✅ **Availability Updated**",
                "",
                f"**Match**: {match_id}",
                f"**Your Status**: {availability.status_emoji} {availability_status.value.title()}",
            ]

            if reason:
                result.append(f"**Reason**: {reason}")

            result.extend([
                "",
                "📊 **Team Availability**",
                f"• Available: {summary['available']} players",
                f"• Unavailable: {summary['unavailable']} players",
                f"• Maybe: {summary['maybe']} players",
                f"• Pending: {summary['pending']} players",
                "",
                "💡 **Tip**: You can update your availability anytime before squad selection",
            ])

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to mark availability: {e}")
            return f"❌ **Error marking availability**: {e!s}"


class GetAvailabilityTool(Tool):
    """Tool for getting availability information for a match."""

    name: str = "get_availability"
    description: str = "Get availability information for a match"

    def __init__(self, availability_service: AvailabilityService):
        super().__init__()
        self.availability_service = availability_service

    def _run(self, match_id: str) -> str:
        """Get availability information for a match."""
        try:
            # Get availability summary
            summary = self.availability_service.get_availability_summary(match_id)

            # Get availability records by status
            available_players = self.availability_service.get_available_players(match_id)
            unavailable_players = self.availability_service.get_unavailable_players(match_id)
            maybe_players = self.availability_service.get_maybe_players(match_id)
            pending_players = self.availability_service.get_pending_players(match_id)

            result = [
                f"📊 **Match Availability: {match_id}**",
                "",
                f"**Total Players**: {summary['total_players']}",
                "",
            ]

            # Available players
            if available_players:
                result.append(f"✅ **Available** ({len(available_players)}):")
                for availability in available_players:
                    result.append(f"• {availability.player_id}")
                result.append("")

            # Unavailable players
            if unavailable_players:
                result.append(f"❌ **Unavailable** ({len(unavailable_players)}):")
                for availability in unavailable_players:
                    result.append(f"• {availability.player_id}")
                    if availability.reason:
                        result.append(f"  - Reason: {availability.reason}")
                result.append("")

            # Maybe players
            if maybe_players:
                result.append(f"❓ **Maybe** ({len(maybe_players)}):")
                for availability in maybe_players:
                    result.append(f"• {availability.player_id}")
                    if availability.reason:
                        result.append(f"  - Reason: {availability.reason}")
                result.append("")

            # Pending players
            if pending_players:
                result.append(f"⏳ **Pending** ({len(pending_players)}):")
                for availability in pending_players:
                    result.append(f"• {availability.player_id}")
                result.append("")

            result.append("📋 **Actions**")
            result.append("• /markattendance [match_id] [status] - Mark your availability")

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to get availability: {e}")
            return f"❌ **Error getting availability**: {e!s}"


class GetPlayerAvailabilityHistoryTool(Tool):
    """Tool for getting player availability history."""

    name: str = "get_player_availability_history"
    description: str = "Get availability history for a player"

    def __init__(self, availability_service: AvailabilityService):
        super().__init__()
        self.availability_service = availability_service

    def _run(
        self,
        player_id: str,
        limit: int = 10,
    ) -> str:
        """Get availability history for a player."""
        try:
            history = self.availability_service.get_player_history(player_id, limit)

            if not history:
                return f"📈 **Availability History**\n\nNo availability records found for player {player_id}."

            result = [
                f"📈 **Availability History for {player_id}**",
                "",
                f"**Last {len(history)} matches**:",
                "",
            ]

            for availability in history:
                result.append(
                    f"{availability.status_emoji} Match {availability.match_id} - {availability.status.value.title()}"
                )
                if availability.reason:
                    result.append(f"  - Reason: {availability.reason}")

            # Calculate statistics
            total_matches = len(history)
            available_count = len([a for a in history if a.is_available])
            unavailable_count = len([a for a in history if a.is_unavailable])
            maybe_count = len([a for a in history if a.is_maybe])

            availability_rate = (available_count / total_matches) * 100 if total_matches > 0 else 0

            result.extend([
                "",
                "📊 **Statistics**",
                f"• **Availability Rate**: {availability_rate:.1f}% ({available_count}/{total_matches} matches)",
                f"• **Available**: {available_count} matches",
                f"• **Unavailable**: {unavailable_count} matches",
                f"• **Maybe**: {maybe_count} matches",
            ])

            # Reliability rating
            if availability_rate >= 90:
                reliability = "⭐⭐⭐⭐⭐ (Excellent)"
            elif availability_rate >= 80:
                reliability = "⭐⭐⭐⭐ (Good)"
            elif availability_rate >= 70:
                reliability = "⭐⭐⭐ (Fair)"
            elif availability_rate >= 60:
                reliability = "⭐⭐ (Poor)"
            else:
                reliability = "⭐ (Very Poor)"

            result.append(f"• **Reliability Rating**: {reliability}")

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to get player availability history: {e}")
            return f"❌ **Error getting availability history**: {e!s}"


class SendRemindersTool(Tool):
    """Tool for sending availability reminders."""

    name: str = "send_availability_reminders"
    description: str = "Send reminders to players who haven't responded to availability requests"

    def __init__(self, availability_service: AvailabilityService):
        super().__init__()
        self.availability_service = availability_service

    def _run(self, match_id: str) -> str:
        """Send availability reminders for a match."""
        try:
            success = self.availability_service.send_availability_reminders(match_id)

            if success:
                pending_players = self.availability_service.get_pending_players(match_id)
                return f"✅ **Reminders Sent**\n\nReminders sent to {len(pending_players)} players who haven't responded to availability requests for match {match_id}."
            else:
                return f"❌ **Failed to send reminders**\n\nUnable to send availability reminders for match {match_id}."

        except Exception as e:
            logger.error(f"Failed to send reminders: {e}")
            return f"❌ **Error sending reminders**: {e!s}"
