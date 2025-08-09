"""
Service factory for creating business service implementations.

This factory handles the creation of service instances with proper
dependency injection and repository wiring.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from loguru import logger

from kickai.core.interfaces import (
    IAnalyticsService,
    INotificationService,
    IPlayerService,
    ITeamService,
    IUserService,
    IValidationService,
)
from kickai.core.value_objects import TeamId

from .repository_factory import RepositoryFactory


class ServiceFactory:
    """
    Factory for creating business service instances.

    This factory creates service instances with their required repository
    dependencies properly injected. Includes cache management to prevent memory leaks.
    """

    # Cache configuration constants
    MAX_CACHE_SIZE = 100  # Maximum number of cached services
    CACHE_TTL_SECONDS = 3600  # 1 hour TTL for cached services

    def __init__(
        self,
        repository_factory: RepositoryFactory,
        config: Optional[Dict[str, Any]] = None,
        max_cache_size: int = MAX_CACHE_SIZE,
        cache_ttl: int = CACHE_TTL_SECONDS
    ):
        """
        Initialize service factory.

        Args:
            repository_factory: Factory for creating repositories
            config: Optional configuration for services
            max_cache_size: Maximum number of services to cache
            cache_ttl: Time-to-live for cached services in seconds
        """
        self.repository_factory = repository_factory
        self.config = config or {}
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl

        # Cache: key -> (service_instance, creation_timestamp)
        self._service_cache: dict[str, tuple[Any, float]] = {}

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get service from cache if valid, otherwise return None."""
        if cache_key not in self._service_cache:
            return None

        service, creation_time = self._service_cache[cache_key]
        current_time = time.time()

        # Check if cache entry has expired
        if current_time - creation_time > self.cache_ttl:
            del self._service_cache[cache_key]
            logger.debug(f"Cache entry expired and removed: {cache_key}")
            return None

        return service

    def _put_in_cache(self, cache_key: str, service: Any) -> None:
        """Put service in cache with size and TTL management."""
        current_time = time.time()

        # Clean expired entries first
        self._clean_expired_entries()

        # If cache is at max size, remove oldest entry
        if len(self._service_cache) >= self.max_cache_size:
            self._evict_oldest_entry()

        # Add new entry
        self._service_cache[cache_key] = (service, current_time)
        logger.debug(f"Service cached: {cache_key}")

    def _clean_expired_entries(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, creation_time) in self._service_cache.items()
            if current_time - creation_time > self.cache_ttl
        ]

        for key in expired_keys:
            del self._service_cache[key]

        if expired_keys:
            logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

    def _evict_oldest_entry(self) -> None:
        """Remove the oldest cache entry to make room for new ones."""
        if not self._service_cache:
            return

        # Find oldest entry by creation time
        oldest_key = min(
            self._service_cache.keys(),
            key=lambda k: self._service_cache[k][1]
        )

        del self._service_cache[oldest_key]
        logger.debug(f"Evicted oldest cache entry: {oldest_key}")

    def create_player_service(self, team_id: TeamId) -> IPlayerService:
        """
        Create player service instance.

        Args:
            team_id: Team identifier for service scope

        Returns:
            Player service implementation
        """
        cache_key = f"player_service_{team_id}"

        # Try to get from cache first
        cached_service = self._get_from_cache(cache_key)
        if cached_service is not None:
            return cached_service

        # Create new service if not in cache
        # Create required repositories
        player_repo = self.repository_factory.create_player_repository(team_id)
        user_repo = self.repository_factory.create_user_repository(team_id)

        # Create validation service
        validation_service = self.create_validation_service()

        # Create notification service
        notification_service = self.create_notification_service(team_id)

        # Import and create service
        from kickai.features.player_registration.domain.services.player_service import PlayerService

        service = PlayerService(
            player_repository=player_repo,
            user_repository=user_repo,
            validation_service=validation_service,
            notification_service=notification_service,
            team_id=team_id
        )

        # Cache the new service
        self._put_in_cache(cache_key, service)
        logger.info(f"Created player service for team {team_id}")

        return service

    def create_team_service(self, team_id: TeamId) -> ITeamService:
        """
        Create team service instance.

        Args:
            team_id: Team identifier for service scope

        Returns:
            Team service implementation
        """
        cache_key = f"team_service_{team_id}"

        # Try to get from cache first
        cached_service = self._get_from_cache(cache_key)
        if cached_service is not None:
            return cached_service

        # Create new service if not in cache
        # Create required repositories
        team_repo = self.repository_factory.create_team_repository(team_id)
        user_repo = self.repository_factory.create_user_repository(team_id)

        # Create validation service
        validation_service = self.create_validation_service()

        # Create notification service
        notification_service = self.create_notification_service(team_id)

        # Import and create service
        from kickai.features.team_administration.domain.services.team_service import TeamService

        service = TeamService(
            team_repository=team_repo,
            user_repository=user_repo,
            validation_service=validation_service,
            notification_service=notification_service,
            team_id=team_id
        )

        # Cache the new service
        self._put_in_cache(cache_key, service)
        logger.info(f"Created team service for team {team_id}")

        return service

    def create_user_service(self, team_id: TeamId) -> IUserService:
        """
        Create user service instance.

        Args:
            team_id: Team identifier for service scope

        Returns:
            User service implementation
        """
        cache_key = f"user_service_{team_id}"

        # Try to get from cache first
        cached_service = self._get_from_cache(cache_key)
        if cached_service is not None:
            return cached_service

        # Create new service if not in cache
        # Create required repositories
        user_repo = self.repository_factory.create_user_repository(team_id)
        player_repo = self.repository_factory.create_player_repository(team_id)
        team_repo = self.repository_factory.create_team_repository(team_id)

        # Import and create service
        from kickai.features.shared.domain.services.user_service import UserService

        service = UserService(
            user_repository=user_repo,
            player_repository=player_repo,
            team_repository=team_repo,
            team_id=team_id
        )

        # Cache the new service
        self._put_in_cache(cache_key, service)
        logger.info(f"Created user service for team {team_id}")

        return service

    def create_validation_service(self) -> IValidationService:
        """
        Create validation service instance.

        Returns:
            Validation service implementation
        """
        cache_key = "validation_service"

        # Try to get from cache first
        cached_service = self._get_from_cache(cache_key)
        if cached_service is not None:
            return cached_service

        # Create new service if not in cache
        from kickai.features.shared.domain.services.validation_service import ValidationService

        service = ValidationService()

        # Cache the new service
        self._put_in_cache(cache_key, service)
        logger.info("Created validation service")

        return service

    def create_notification_service(self, team_id: TeamId) -> INotificationService:
        """
        Create notification service instance.

        Args:
            team_id: Team identifier for service scope

        Returns:
            Notification service implementation
        """
        cache_key = f"notification_service_{team_id}"

        # Try to get from cache first
        cached_service = self._get_from_cache(cache_key)
        if cached_service is not None:
            return cached_service

        # Create new service if not in cache
        # Get notification configuration
        notification_config = self.config.get("notification", {})

        from kickai.features.communication.domain.services.notification_service import (
            NotificationService,
        )

        service = NotificationService(
            team_id=team_id,
            config=notification_config
        )

        # Cache the new service
        self._put_in_cache(cache_key, service)
        logger.info(f"Created notification service for team {team_id}")

        return service

    def create_analytics_service(self, team_id: TeamId) -> IAnalyticsService:
        """
        Create analytics service instance.

        Args:
            team_id: Team identifier for service scope

        Returns:
            Analytics service implementation
        """
        cache_key = f"analytics_service_{team_id}"

        # Try to get from cache first
        cached_service = self._get_from_cache(cache_key)
        if cached_service is not None:
            return cached_service

        # Create new service if not in cache
        # Get analytics configuration
        analytics_config = self.config.get("analytics", {})

        from kickai.features.analytics.domain.services.analytics_service import AnalyticsService

        service = AnalyticsService(
            team_id=team_id,
            config=analytics_config
        )

        # Cache the new service
        self._put_in_cache(cache_key, service)
        logger.info(f"Created analytics service for team {team_id}")

        return service

    def clear_cache(self) -> None:
        """Clear service cache."""
        cache_size = len(self._service_cache)
        self._service_cache.clear()
        logger.info(f"Service cache cleared ({cache_size} entries removed)")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for monitoring."""
        current_time = time.time()
        expired_count = sum(
            1 for _, creation_time in self._service_cache.values()
            if current_time - creation_time > self.cache_ttl
        )

        return {
            "total_entries": len(self._service_cache),
            "expired_entries": expired_count,
            "max_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl,
            "cache_utilization": len(self._service_cache) / self.max_cache_size
        }

    @classmethod
    def create_for_testing(cls, repository_factory: RepositoryFactory) -> ServiceFactory:
        """Create factory configured for testing."""
        return cls(
            repository_factory=repository_factory,
            config={
                "notification": {"type": "mock"},
                "analytics": {"type": "mock"}
            }
        )

    @classmethod
    def create_for_production(cls, repository_factory: RepositoryFactory) -> ServiceFactory:
        """Create factory configured for production."""
        return cls(
            repository_factory=repository_factory,
            config={
                "notification": {"type": "telegram"},
                "analytics": {"type": "firebase"}
            }
        )
