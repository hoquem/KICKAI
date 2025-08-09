"""
Shared formatting utilities for KICKAI bot responses.
This module serves as the single source of truth for all user-facing formatting.
"""

from datetime import datetime

from kickai.features.player_registration.domain.entities.player import Player
from typing import List


class PlayerFormattingService:
    """Single source of truth for all player-related formatting."""

    @staticmethod
    def format_player_list(players: List[Player], team_name: str = "Team") -> str:
        """
        Format a list of players in a clean, Telegram-friendly format.

        Args:
            players: List of Player objects
            team_name: Name of the team

        Returns:
            Formatted string for Telegram display
        """
        if not players:
            return f"📋 {team_name} Players\n\n❌ No players found."

        # Group players by onboarding status
        active_players = [p for p in players if p.is_active()]
        pending_players = [p for p in players if p.is_pending_approval()]
        inactive_players = [p for p in players if not p.is_active() and not p.is_pending_approval()]

        # Build the formatted output
        output = [f"📋 {team_name} Players ({len(players)} total)"]
        output.append("")  # Empty line

        # Active players
        if active_players:
            output.append("✅ Active Players:")
            for player in sorted(active_players, key=lambda p: p.name):
                output.append(f"• {player.player_id} - {player.name} ({player.position})")
            output.append("")  # Empty line

        # Pending players
        if pending_players:
            output.append("⏳ Pending Approval:")
            for player in sorted(pending_players, key=lambda p: p.name):
                output.append(f"• {player.player_id} - {player.name} ({player.position})")
            output.append("")  # Empty line

        # Inactive players
        if inactive_players:
            output.append("❌ Inactive Players:")
            for player in sorted(inactive_players, key=lambda p: p.name):
                output.append(f"• {player.player_id} - {player.name} ({player.position})")
            output.append("")  # Empty line

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        output.append(f"📅 Last updated: {timestamp}")

        return "\n".join(output)

    @staticmethod
    def format_player_list_for_leadership(players: List[Player], team_name: str = "Team") -> str:
        """
        Format a list of players for leadership view - shows all players with detailed status.

        Args:
            players: List of Player objects
            team_name: Name of the team

        Returns:
            Formatted string for Telegram display (leadership view)
        """
        if not players:
            return f"📋 {team_name} Players - Leadership View\n\n❌ No players found."

        # Group players by onboarding status
        active_players = [p for p in players if p.is_active()]
        pending_players = [p for p in players if p.is_pending_approval()]
        inactive_players = [p for p in players if not p.is_active() and not p.is_pending_approval()]

        # Build the formatted output
        output = [f"📋 {team_name} Players - Leadership View ({len(players)} total)"]
        output.append("")  # Empty line

        # Active players
        if active_players:
            output.append("✅ Active Players:")
            for player in sorted(active_players, key=lambda p: p.name):
                output.append(
                    f"• {player.player_id} - {player.name} ({player.position}) - {player.phone_number}"
                )
            output.append("")  # Empty line

        # Pending players
        if pending_players:
            output.append("⏳ Pending Approval:")
            for player in sorted(pending_players, key=lambda p: p.name):
                output.append(
                    f"• {player.player_id} - {player.name} ({player.position}) - {player.phone_number}"
                )
            output.append("")  # Empty line

        # Inactive players
        if inactive_players:
            output.append("❌ Inactive Players:")
            for player in sorted(inactive_players, key=lambda p: p.name):
                output.append(
                    f"• {player.player_id} - {player.name} ({player.position}) - {player.phone_number}"
                )
            output.append("")  # Empty line

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        output.append(f"📅 Last updated: {timestamp}")

        return "\n".join(output)

    @staticmethod
    def format_player_status(player: Player, team_name: str = "Team") -> str:
        """
        Format a single player's status in a clean, Telegram-friendly format.

        Args:
            player: Player object
            team_name: Name of the team

        Returns:
            Formatted string for Telegram display
        """
        if not player:
            return "❌ Player not found."

        # Status emoji mapping based on player state
        if player.is_active():
            status_icon = "✅"
            status_text = "Active"
        elif player.is_pending_approval():
            status_icon = "⏳"
            status_text = "Pending Approval"
        else:
            status_icon = "❌"
            status_text = "Inactive"

        output = [
            f"👤 Player Status - {team_name}",
            "",
            f"Name: {player.name}",
            f"ID: {player.player_id}",
            f"Phone: {player.phone_number}",
            f"Position: {player.position}",
            f"Status: {status_icon} {status_text}",
            f"Registration: {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'N/A'}",
            "",
            f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ]

        return "\n".join(output)

    @staticmethod
    def format_error_message(error: str, context: str = "") -> str:
        """
        Format error messages consistently.

        Args:
            error: Error message
            context: Additional context

        Returns:
            Formatted error message
        """
        output = [f"❌ {error}"]
        if context:
            output.append(f"💡 {context}")
        return "\n".join(output)

    @staticmethod
    def format_success_message(message: str, context: str = "") -> str:
        """
        Format success messages consistently.

        Args:
            message: Success message
            context: Additional context

        Returns:
            Formatted success message
        """
        output = [f"✅ {message}"]
        if context:
            output.append(f"💡 {context}")
        return "\n".join(output)


# Global instance for easy access
player_formatter = PlayerFormattingService()
