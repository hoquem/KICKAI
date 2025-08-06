#!/usr/bin/env python3
"""
Match Management Tools

This module provides tools for match creation, management, and squad selection.
These tools integrate with the existing match management services.
"""

import logging
from datetime import datetime, time

from crewai import Tool

from kickai.features.match_management.domain.services.match_service import MatchService

logger = logging.getLogger(__name__)


class CreateMatchTool(Tool):
    """Tool for creating new matches."""

    name: str = "create_match"
    description: str = "Create a new match with opponent, date, time, venue, and competition details"

    def __init__(self, match_service: MatchService):
        super().__init__()
        self.match_service = match_service

    def _run(
        self,
        team_id: str,
        opponent: str,
        match_date: str,  # YYYY-MM-DD format
        match_time: str,  # HH:MM format
        venue: str,
        competition: str = "League Match",
        notes: str | None = None,
        created_by: str = "",
    ) -> str:
        """Create a new match."""
        try:
            # Parse date and time
            date_obj = datetime.strptime(match_date, "%Y-%m-%d")
            time_obj = time.fromisoformat(match_time)

            # Create match
            match = self.match_service.create_match(
                team_id=team_id,
                opponent=opponent,
                match_date=date_obj,
                match_time=time_obj,
                venue=venue,
                competition=competition,
                notes=notes,
                created_by=created_by,
            )

            return f"✅ Match created successfully!\n\n🏆 **Match Details**\n• **Opponent**: {match.opponent}\n• **Date**: {match.formatted_date}\n• **Time**: {match.formatted_time}\n• **Venue**: {match.venue}\n• **Competition**: {match.competition}\n• **Match ID**: {match.match_id}\n\n📋 **Next Steps**\n• Players will be notified automatically\n• Availability requests will be sent 7 days before\n• Squad selection will open 3 days before match"

        except Exception as e:
            logger.error(f"Failed to create match: {e}")
            return f"❌ **Error creating match**: {e!s}"


class ListMatchesTool(Tool):
    """Tool for listing matches."""

    name: str = "list_matches"
    description: str = "List matches for a team with optional status filter (upcoming, past, all)"

    def __init__(self, match_service: MatchService):
        super().__init__()
        self.match_service = match_service

    def _run(
        self,
        team_id: str,
        status: str = "all",
        limit: int = 10,
    ) -> str:
        """List matches for a team."""
        try:
            if status == "upcoming":
                matches = self.match_service.get_upcoming_matches(team_id, limit)
                title = f"📅 **Upcoming Matches** (Next {len(matches)})"
            elif status == "past":
                matches = self.match_service.get_past_matches(team_id, limit)
                title = f"📅 **Past Matches** (Last {len(matches)})"
            else:
                matches = self.match_service.list_matches(team_id, limit=limit)
                title = f"📅 **All Matches** (Last {len(matches)})"

            if not matches:
                return f"{title}\n\nNo matches found."

            result = [title, ""]
            for i, match in enumerate(matches, 1):
                result.append(
                    f"{i}️⃣ **{match.match_id}** - vs {match.opponent}\n"
                    f"   📅 {match.formatted_date}\n"
                    f"   🕐 {match.formatted_time} | 🏟️ {match.venue}\n"
                    f"   📊 Status: {match.status.value.title()}"
                )

            result.append("\n📋 **Quick Actions**")
            result.append("• /matchdetails [match_id] - View full details")
            result.append("• /markattendance [match_id] - Mark availability")

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to list matches: {e}")
            return f"❌ **Error listing matches**: {e!s}"


class GetMatchDetailsTool(Tool):
    """Tool for getting detailed match information."""

    name: str = "get_match_details"
    description: str = "Get detailed information about a specific match"

    def __init__(self, match_service: MatchService):
        super().__init__()
        self.match_service = match_service

    def _run(self, match_id: str) -> str:
        """Get detailed match information."""
        try:
            match = self.match_service.get_match(match_id)
            if not match:
                return f"❌ **Match not found**: {match_id}"

            result = [
                f"🏆 **Match Details: {match.match_id}**",
                "",
                f"**Opponent**: {match.opponent}",
                f"**Date**: {match.formatted_date}",
                f"**Time**: {match.formatted_time}",
                f"**Venue**: {match.venue}",
                f"**Competition**: {match.competition}",
                f"**Status**: {match.status.value.title()}",
            ]

            if match.notes:
                result.append(f"**Notes**: {match.notes}")

            if match.result:
                result.append("")
                result.append("📊 **Match Result**")
                result.append(f"**Score**: {match.result.home_score} - {match.result.away_score}")
                if match.result.scorers:
                    result.append(f"**Scorers**: {', '.join(match.result.scorers)}")
                if match.result.notes:
                    result.append(f"**Notes**: {match.result.notes}")

            result.append("")
            result.append("📋 **Actions**")
            result.append("• /markattendance [match_id] - Mark availability")
            result.append("• /selectsquad [match_id] - Select final squad (Leadership only)")

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to get match details: {e}")
            return f"❌ **Error getting match details**: {e!s}"


class SelectSquadTool(Tool):
    """Tool for selecting squad for a match."""

    name: str = "select_squad"
    description: str = "Select squad for a match (Leadership only)"

    def __init__(self, match_service: MatchService):
        super().__init__()
        self.match_service = match_service

    def _run(
        self,
        match_id: str,
        player_ids: list[str] | None = None,
    ) -> str:
        """Select squad for a match."""
        try:
            match = self.match_service.get_match(match_id)
            if not match:
                return f"❌ **Match not found**: {match_id}"

            if not match.is_upcoming:
                return "❌ **Cannot select squad**: Match is not in upcoming status"

            # TODO: Implement squad selection logic
            # This would integrate with the availability service to get available players
            # and then create a squad selection record

            result = [
                f"👥 **Squad Selection: {match.match_id}**",
                "",
                f"**Match**: vs {match.opponent}",
                f"**Date**: {match.formatted_date}",
                f"**Time**: {match.formatted_time}",
                "",
                "📋 **Squad Selection**",
                "Squad selection functionality will be implemented in the next phase.",
                "",
                "**Available Players**: To be determined from availability data",
                "**Selected Squad**: To be selected",
                "",
                "📋 **Actions**",
                "• /markattendance [match_id] - Mark availability",
                "• /attendance [match_id] - View current availability",
            ]

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to select squad: {e}")
            return f"❌ **Error selecting squad**: {e!s}"


class RecordMatchResultTool(Tool):
    """Tool for recording match results."""

    name: str = "record_match_result"
    description: str = "Record the result of a completed match (Leadership only)"

    def __init__(self, match_service: MatchService):
        super().__init__()
        self.match_service = match_service

    def _run(
        self,
        match_id: str,
        home_score: int,
        away_score: int,
        scorers: list[str] | None = None,
        assists: list[str] | None = None,
        notes: str | None = None,
        recorded_by: str = "",
    ) -> str:
        """Record match result."""
        try:
            match = self.match_service.get_match(match_id)
            if not match:
                return f"❌ **Match not found**: {match_id}"

            if match.is_completed:
                return "❌ **Match already completed**: Result already recorded"

            # Record the result
            updated_match = self.match_service.record_match_result(
                match_id=match_id,
                home_score=home_score,
                away_score=away_score,
                scorers=scorers or [],
                assists=assists or [],
                notes=notes,
                recorded_by=recorded_by,
            )

            result = [
                "🏆 **Match Result Recorded**",
                "",
                f"**Match**: vs {updated_match.opponent}",
                f"**Date**: {updated_match.formatted_date}",
                f"**Score**: {home_score} - {away_score}",
            ]

            if scorers:
                result.append(f"**Scorers**: {', '.join(scorers)}")
            if assists:
                result.append(f"**Assists**: {', '.join(assists)}")
            if notes:
                result.append(f"**Notes**: {notes}")

            result.append("")
            result.append("✅ Match result has been recorded and match status updated to completed.")

            return "\n".join(result)

        except Exception as e:
            logger.error(f"Failed to record match result: {e}")
            return f"❌ **Error recording match result**: {e!s}"
