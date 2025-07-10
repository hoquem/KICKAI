import logging
from typing import List
from datetime import datetime

from services.player_service import get_player_service


logger = logging.getLogger(__name__)

class PlayerCommands:
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_service = get_player_service(team_id=team_id)

    async def handle_injure_player(self, args: List[str]) -> str:
        """Handles injuring a player."""
        if len(args) < 2:
            return "❌ Usage: /injure <player_id> <details> [return_date (DD/MM/YYYY)]"

        player_id = args[0]
        injury_details = args[1]
        return_date = None
        if len(args) > 2:
            try:
                return_date = datetime.strptime(args[2], "%d/%m/%Y")
            except ValueError:
                return "❌ Invalid return date format. Use DD/MM/YYYY."

        try:
            player = await self.player_service.update_player(
                player_id,
                is_injured=True,
                injury_details=injury_details,
                return_date=return_date
            )
            return f"✅ Player {player.name} ({player.player_id}) marked as injured. Details: {injury_details}. Return date: {return_date.strftime('%d/%m/%Y') if return_date else 'N/A'}"
        except Exception as e:
            logger.error(f"Error injuring player {player_id}: {e}")
            return f"❌ Failed to injure player: {str(e)}"

    async def handle_suspend_player(self, args: List[str]) -> str:
        """Handles suspending a player."""
        if len(args) < 2:
            return "❌ Usage: /suspend <player_id> <details> [return_date (DD/MM/YYYY)]"

        player_id = args[0]
        suspension_details = args[1]
        return_date = None
        if len(args) > 2:
            try:
                return_date = datetime.strptime(args[2], "%d/%m/%Y")
            except ValueError:
                return "❌ Invalid return date format. Use DD/MM/YYYY."

        try:
            player = await self.player_service.update_player(
                player_id,
                is_suspended=True,
                suspension_details=suspension_details,
                return_date=return_date
            )
            return f"✅ Player {player.name} ({player.player_id}) marked as suspended. Details: {suspension_details}. Return date: {return_date.strftime('%d/%m/%Y') if return_date else 'N/A'}"
        except Exception as e:
            logger.error(f"Error suspending player {player_id}: {e}")
            return f"❌ Failed to suspend player: {str(e)}"

    async def handle_recover_player(self, args: List[str]) -> str:
        """Handles recovering a player from injury/suspension."""
        if not args:
            return "❌ Usage: /recover <player_id>"

        player_id = args[0]

        try:
            player = await self.player_service.update_player(
                player_id,
                is_injured=False,
                injury_details=None,
                is_suspended=False,
                suspension_details=None,
                return_date=None
            )
            return f"✅ Player {player.name} ({player.player_id}) is now recovered and eligible."
        except Exception as e:
            logger.error(f"Error recovering player {player_id}: {e}")
            return f"❌ Failed to recover player: {str(e)}"
