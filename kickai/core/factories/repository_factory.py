"""
Repository factory for creating repository implementations.

This factory handles the creation of repository instances with proper
dependency injection and configuration.
"""

from __future__ import annotations

import time
from typing import Any

from loguru import logger

from kickai.core.interfaces import (
    IMatchRepository,
    IPlayerRepository,
    ITeamRepository,
    IUserRepository,
)
from kickai.core.value_objects import TeamId


class RepositoryFactory:
    """
    Factory for creating repository instances.

    This factory implements the Abstract Factory pattern, allowing the creation
    of different repository implementations (Firebase, Mock, etc.) based on
    configuration. Includes cache management to prevent memory leaks.
    """

    # Cache configuration constants
    MAX_CACHE_SIZE = 50  # Maximum number of cached repositories
    CACHE_TTL_SECONDS = 1800  # 30 minutes TTL for cached repositories

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        max_cache_size: int = MAX_CACHE_SIZE,
        cache_ttl: int = CACHE_TTL_SECONDS
    ):
        """
        Initialize repository factory.


            config: Optional configuration for repositories
            max_cache_size: Maximum number of repositories to cache
            cache_ttl: Time-to-live for cached repositories in seconds
        """
        self.config = config or {}
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl

        # Cache: key -> (repository_instance, creation_timestamp)
        self._repository_cache: dict[str, tuple[Any, float]] = {}
        self._database_client = None

    def _get_from_cache(self, cache_key: str) -> Any | None:
        """Get repository from cache if valid, otherwise return None."""
        if cache_key not in self._repository_cache:
            return None

        repository, creation_time = self._repository_cache[cache_key]
        current_time = time.time()

        # Check if cache entry has expired
        if current_time - creation_time > self.cache_ttl:
            del self._repository_cache[cache_key]
            logger.debug(f"Repository cache entry expired and removed: {cache_key}")
            return None

        return repository

    def _put_in_cache(self, cache_key: str, repository: Any) -> None:
        """Put repository in cache with size and TTL management."""
        current_time = time.time()

        # Clean expired entries first
        self._clean_expired_entries()

        # If cache is at max size, remove oldest entry
        if len(self._repository_cache) >= self.max_cache_size:
            self._evict_oldest_entry()

        # Add new entry
        self._repository_cache[cache_key] = (repository, current_time)
        logger.debug(f"Repository cached: {cache_key}")

    def _clean_expired_entries(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, creation_time) in self._repository_cache.items()
            if current_time - creation_time > self.cache_ttl
        ]

        for key in expired_keys:
            del self._repository_cache[key]

        if expired_keys:
            logger.debug(f"Cleaned {len(expired_keys)} expired repository cache entries")

    def _evict_oldest_entry(self) -> None:
        """Remove the oldest cache entry to make room for new ones."""
        if not self._repository_cache:
            return

        # Find oldest entry by creation time
        oldest_key = min(
            self._repository_cache.keys(),
            key=lambda k: self._repository_cache[k][1]
        )

        del self._repository_cache[oldest_key]
        logger.debug(f"Evicted oldest repository cache entry: {oldest_key}")

    def create_player_repository(self, team_id: TeamId) -> IPlayerRepository:
        """
        Create player repository instance.


            team_id: Team identifier for repository scope


    :return: Player repository implementation
    :rtype: str  # TODO: Fix type
        """
        cache_key = f"player_repo_{team_id}"

        # Try to get from cache first
        cached_repo = self._get_from_cache(cache_key)
        if cached_repo is not None:
            return cached_repo

        # Create new repository if not in cache
        # Determine implementation type from config
        impl_type = self.config.get("repository_type", "firebase")

        if impl_type == "firebase":
            repo = self._create_firebase_player_repository(team_id)
        elif impl_type == "mock":
            repo = self._create_mock_player_repository(team_id)
        else:
            raise ValueError(f"Unknown repository type: {impl_type}")

        # Cache the new repository
        self._put_in_cache(cache_key, repo)
        logger.info(f"Created {impl_type} player repository for team {team_id}")

        return repo

    def create_team_repository(self, team_id: TeamId) -> ITeamRepository:
        """
        Create team repository instance.


            team_id: Team identifier for repository scope


    :return: Team repository implementation
    :rtype: str  # TODO: Fix type
        """
        cache_key = f"team_repo_{team_id}"

        # Try to get from cache first
        cached_repo = self._get_from_cache(cache_key)
        if cached_repo is not None:
            return cached_repo

        # Create new repository if not in cache
        impl_type = self.config.get("repository_type", "firebase")

        if impl_type == "firebase":
            repo = self._create_firebase_team_repository(team_id)
        elif impl_type == "mock":
            repo = self._create_mock_team_repository(team_id)
        else:
            raise ValueError(f"Unknown repository type: {impl_type}")

        # Cache the new repository
        self._put_in_cache(cache_key, repo)
        logger.info(f"Created {impl_type} team repository for team {team_id}")

        return repo

    def create_user_repository(self, team_id: TeamId) -> IUserRepository:
        """
        Create user repository instance.


            team_id: Team identifier for repository scope


    :return: User repository implementation
    :rtype: str  # TODO: Fix type
        """
        cache_key = f"user_repo_{team_id}"

        # Try to get from cache first
        cached_repo = self._get_from_cache(cache_key)
        if cached_repo is not None:
            return cached_repo

        # Create new repository if not in cache
        impl_type = self.config.get("repository_type", "firebase")

        if impl_type == "firebase":
            repo = self._create_firebase_user_repository(team_id)
        elif impl_type == "mock":
            repo = self._create_mock_user_repository(team_id)
        else:
            raise ValueError(f"Unknown repository type: {impl_type}")

        # Cache the new repository
        self._put_in_cache(cache_key, repo)
        logger.info(f"Created {impl_type} user repository for team {team_id}")

        return repo

    def create_match_repository(self, team_id: TeamId) -> IMatchRepository:
        """
        Create match repository instance.


            team_id: Team identifier for repository scope


    :return: Match repository implementation
    :rtype: str  # TODO: Fix type
        """
        cache_key = f"match_repo_{team_id}"

        # Try to get from cache first
        cached_repo = self._get_from_cache(cache_key)
        if cached_repo is not None:
            return cached_repo

        # Create new repository if not in cache
        impl_type = self.config.get("repository_type", "firebase")

        if impl_type == "firebase":
            repo = self._create_firebase_match_repository(team_id)
        elif impl_type == "mock":
            repo = self._create_mock_match_repository(team_id)
        else:
            raise ValueError(f"Unknown repository type: {impl_type}")

        # Cache the new repository
        self._put_in_cache(cache_key, repo)
        logger.info(f"Created {impl_type} match repository for team {team_id}")

        return repo

    def _get_database_client(self):
        """Get database client instance (cached)."""
        if self._database_client is None:
            # Import here to avoid circular dependencies
            from kickai.database.firebase_client import get_firebase_client
            self._database_client = get_firebase_client()
        return self._database_client

    def _create_firebase_player_repository(self, team_id: TeamId) -> IPlayerRepository:
        """Create Firebase player repository."""
        # Import here to avoid circular dependencies
        from kickai.features.player_registration.infrastructure.firebase_player_repository import (
            FirebasePlayerRepository,
        )

        db_client = self._get_database_client()
        return FirebasePlayerRepository(db_client, team_id)

    def _create_mock_player_repository(self, team_id: TeamId) -> IPlayerRepository:
        """Create mock player repository."""
        from kickai.testing.mocks.mock_player_repository import MockPlayerRepository
        return MockPlayerRepository(team_id)

    def _create_firebase_team_repository(self, team_id: TeamId) -> ITeamRepository:
        """Create Firebase team repository."""
        from kickai.features.team_administration.infrastructure.firebase_team_repository import (
            FirebaseTeamRepository,
        )

        db_client = self._get_database_client()
        return FirebaseTeamRepository(db_client, team_id)

    def _create_mock_team_repository(self, team_id: TeamId) -> ITeamRepository:
        """Create mock team repository."""
        from kickai.testing.mocks.mock_team_repository import MockTeamRepository
        return MockTeamRepository(team_id)

    def _create_firebase_user_repository(self, team_id: TeamId) -> IUserRepository:
        """Create Firebase user repository."""
        from kickai.features.shared.infrastructure.firebase_user_repository import (
            FirebaseUserRepository,
        )

        db_client = self._get_database_client()
        return FirebaseUserRepository(db_client, team_id)

    def _create_mock_user_repository(self, team_id: TeamId) -> IUserRepository:
        """Create mock user repository."""
        from kickai.testing.mocks.mock_user_repository import MockUserRepository
        return MockUserRepository(team_id)

    def _create_firebase_match_repository(self, team_id: TeamId) -> IMatchRepository:
        """Create Firebase match repository."""
        from kickai.features.match_management.infrastructure.firebase_match_repository import (
            FirebaseMatchRepository,
        )

        db_client = self._get_database_client()
        return FirebaseMatchRepository(db_client, team_id)

    def _create_mock_match_repository(self, team_id: TeamId) -> IMatchRepository:
        """Create mock match repository."""
        from kickai.testing.mocks.mock_match_repository import MockMatchRepository
        return MockMatchRepository(team_id)

    def clear_cache(self) -> None:
        """Clear repository cache."""
        cache_size = len(self._repository_cache)
        self._repository_cache.clear()
        logger.info(f"Repository cache cleared ({cache_size} entries removed)")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for monitoring."""
        current_time = time.time()
        expired_count = sum(
            1 for _, creation_time in self._repository_cache.values()
            if current_time - creation_time > self.cache_ttl
        )

        return {
            "total_entries": len(self._repository_cache),
            "expired_entries": expired_count,
            "max_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl,
            "cache_utilization": len(self._repository_cache) / self.max_cache_size
        }

    @classmethod
    def create_for_testing(cls) -> RepositoryFactory:
        """Create factory configured for testing with mock repositories."""
        return cls(config={"repository_type": "mock"})

    @classmethod
    def create_for_production(cls) -> RepositoryFactory:
        """Create factory configured for production with Firebase repositories."""
        return cls(config={"repository_type": "firebase"})
