import logging
from typing import Any, Dict, Optional


class MultiTeamManager:
    """
    Manages multiple teams, their configurations, and team-level operations.
    Loads team configurations, provides team lookup, and supports team-level actions.
    """

    def __init__(self, data_store: Any):
        self.data_store = data_store
        self.teams: dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    async def load_team_configurations(self) -> list[dict[str, Any]]:
        self.logger.info("🔍 Loading team configurations from data store...")
        teams = await self.data_store.query_documents("teams", filters=[])
        self.teams = {team["id"]: team for team in teams}
        self.logger.info(f"✅ Loaded {len(self.teams)} team configurations.")
        return teams

    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        return self.teams.get(team_id)

    def list_teams(self) -> list[dict[str, Any]]:
        return list(self.teams.values())
