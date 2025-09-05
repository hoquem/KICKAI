#!/usr/bin/env python3
"""
Team Configuration Cache

This module provides a singleton cache for team configurations that are loaded
at startup and accessed without database queries during runtime.

Team configurations are immutable during normal operation:
- Bot tokens don't change
- Chat IDs don't change  
- Team settings rarely change

This cache eliminates 200-500ms per operation that was previously spent
querying team configuration from the database.
"""

from typing import Optional

from loguru import logger

from kickai.features.team_administration.domain.entities.team import Team


class TeamConfigCache:
    """
    Singleton cache for team configurations loaded at startup.

    Usage:
        # At startup
        cache = TeamConfigCache()
        await cache.initialize()

        # During operations
        team = cache.get_team("KTI")  # Instant access, no database query
    """

    _instance: Optional["TeamConfigCache"] = None
    _initialized: bool = False
    _configs: dict[str, Team] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """
        Load all team configurations from database at startup.

        This is called once during system initialization to populate
        the cache with all team configurations.
        """
        if self._initialized:
            logger.info("Team config cache already initialized")
            return

        logger.info("🚀 Loading team configurations at startup...")

        try:
            # Import here to avoid circular imports
            from kickai.core.dependency_container import get_container
            from kickai.features.team_administration.domain.services.team_service import TeamService

            # Get team service
            container = get_container()
            team_service = container.get_service(TeamService)

            if not team_service:
                raise RuntimeError("TeamService not available during initialization")

            # Load all teams
            all_teams = await team_service.get_all_teams()

            # Cache each team configuration
            for team in all_teams:
                team_id = team.id  # Team entity uses 'id' not 'team_id'
                if team_id:
                    self._configs[team_id] = team
                    logger.info(f"✅ Cached config for team: {team_id}")
                else:
                    logger.warning(f"⚠️ Skipping team with no ID: {team.name}")

            self._initialized = True
            logger.info(
                f"🎯 Team config cache initialized with {len(self._configs)} configurations"
            )

        except Exception as e:
            logger.error(f"❌ Failed to initialize team config cache: {e}")
            raise RuntimeError(f"Team config cache initialization failed: {e}")

    def get_team(self, team_id: str) -> Team | None:
        """
        Get team configuration from cache.

        Args:
            team_id: Team identifier (e.g., "KTI")

        Returns:
            Team configuration or None if not found

        Performance: ~0.001ms (instant dict lookup)
        """
        if not self._initialized:
            logger.warning("Team config cache not initialized, returning None")
            return None

        return self._configs.get(team_id)

    def get_bot_token(self, team_id: str) -> str | None:
        """Quick accessor for bot token"""
        team = self.get_team(team_id)
        return team.bot_token if team else None

    def get_main_chat_id(self, team_id: str) -> str | None:
        """Quick accessor for main chat ID"""
        team = self.get_team(team_id)
        return team.main_chat_id if team else None

    def get_leadership_chat_id(self, team_id: str) -> str | None:
        """Quick accessor for leadership chat ID"""
        team = self.get_team(team_id)
        return team.leadership_chat_id if team else None

    def get_team_name(self, team_id: str) -> str | None:
        """Quick accessor for team name with fallback to team_id"""
        team = self.get_team(team_id)
        if not team:
            return None

        # Use team name if available, otherwise fallback to team_id
        if team.name and team.name.strip():
            return team.name.strip()
        elif team_id and team_id.strip():
            return team_id.strip()
        else:
            return None

    def is_initialized(self) -> bool:
        """Check if cache has been initialized"""
        return self._initialized

    async def refresh_team(self, team_id: str):
        """
        Refresh configuration for a specific team.

        This is used in rare cases where team configuration changes
        during runtime (e.g., admin updates bot token).
        """
        if not self._initialized:
            logger.warning("Cannot refresh team config - cache not initialized")
            return

        try:
            from kickai.core.dependency_container import get_container
            from kickai.features.team_administration.domain.services.team_service import TeamService

            container = get_container()
            team_service = container.get_service(TeamService)

            team = await team_service.get_team(team_id=team_id)
            if team:
                self._configs[team_id] = team
                logger.info(f"🔄 Refreshed config for team: {team_id}")
            else:
                logger.warning(f"Team {team_id} not found during refresh")

        except Exception as e:
            logger.error(f"❌ Failed to refresh team {team_id} config: {e}")

    def get_all_team_ids(self) -> list[str]:
        """Get list of all cached team IDs"""
        return list(self._configs.keys())

    def get_stats(self) -> dict:
        """Get cache statistics for monitoring"""
        return {
            "initialized": self._initialized,
            "team_count": len(self._configs),
            "team_ids": list(self._configs.keys()),
        }


# Global function for easy access
def get_team_config_cache() -> TeamConfigCache:
    """Get the global team config cache instance"""
    return TeamConfigCache()
