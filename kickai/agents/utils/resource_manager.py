#!/usr/bin/env python3
"""
Resource management utilities.

Handles rate limiting, concurrent request management, and resource cleanup.
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Any

from loguru import logger

from kickai.agents.config.message_router_config import (
    DEFAULT_CLEANUP_INTERVAL,
    DEFAULT_MAX_CONCURRENT,
    DEFAULT_MAX_REQUESTS_PER_MINUTE,
    LOG_MESSAGES,
    WARNING_MESSAGES,
)


class ResourceManager:
    """
    Handles resource management and cleanup for the message router.

    Manages rate limiting, concurrent requests, and periodic cleanup.
    """

    def __init__(
        self,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        max_requests_per_minute: int = DEFAULT_MAX_REQUESTS_PER_MINUTE,
        cleanup_interval: int = DEFAULT_CLEANUP_INTERVAL,
    ) -> None:
        """
        Initialize the resource manager.

        Args:
            max_concurrent: Maximum concurrent requests allowed
            max_requests_per_minute: Maximum requests per minute per user
            cleanup_interval: Interval in seconds for cleanup tasks
        """
        try:
            # ALL business logic here
            self.max_concurrent = max_concurrent
            self.max_requests_per_minute = max_requests_per_minute
            self.cleanup_interval = cleanup_interval

            # Request tracking
            self.active_requests: set = set()
            self.request_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=100))
            self.last_cleanup = time.time()

            # Semaphore for concurrent request limiting
            self._semaphore = asyncio.Semaphore(max_concurrent)

            logger.info(
                LOG_MESSAGES["RESOURCE_MANAGER_INITIALIZED"].format(
                    max_concurrent=max_concurrent, max_requests_per_minute=max_requests_per_minute
                )
            )

        except Exception as e:
            logger.error(f"❌ Error in ResourceManager.__init__: {e}")
            raise

    def add_request(self) -> object:
        """
        Add a new request to tracking.

        Returns:
            Request token for tracking
        """
        try:
            # ALL business logic here
            request_token = object()
            self.active_requests.add(request_token)
            return request_token

        except Exception as e:
            logger.error(f"❌ Error in add_request: {e}")
            return object()

    def remove_request(self, request_token: object) -> None:
        """
        Remove a request from tracking.

        Args:
            request_token: Token returned from add_request
        """
        try:
            # ALL business logic here
            self.active_requests.discard(request_token)

        except Exception as e:
            logger.error(f"❌ Error in remove_request: {e}")

    def check_rate_limit(self, telegram_id: int) -> bool:
        """
        Check if user has exceeded rate limits.

        Args:
            telegram_id: User's Telegram ID

        Returns:
            True if rate limit exceeded, False otherwise
        """
        try:
            # ALL business logic here
            current_time = time.time()
            user_requests = self.request_history[telegram_id]

            # Remove old requests (older than 1 minute)
            while user_requests and current_time - user_requests[0] > 60:
                user_requests.popleft()

            # Check if user has exceeded rate limit
            if len(user_requests) >= self.max_requests_per_minute:
                logger.warning(
                    WARNING_MESSAGES["RATE_LIMIT_EXCEEDED"].format(
                        telegram_id=telegram_id, request_count=len(user_requests)
                    )
                )
                return True

            # Add current request
            user_requests.append(current_time)
            return False

        except Exception as e:
            logger.error(f"❌ Error in check_rate_limit: {e}")
            # Fail safe - allow request if rate limiting fails
            return False

    async def acquire_semaphore(self) -> bool:
        """
        Acquire semaphore for concurrent request limiting.

        Returns:
            True if acquired successfully, False if timeout
        """
        try:
            # ALL business logic here
            try:
                await asyncio.wait_for(self._semaphore.acquire(), timeout=1.0)
                return True
            except TimeoutError:
                logger.warning(WARNING_MESSAGES["CONCURRENT_LIMIT_EXCEEDED"])
                return False

        except Exception as e:
            logger.error(f"❌ Error in acquire_semaphore: {e}")
            return False

    def release_semaphore(self) -> None:
        """
        Release semaphore after request completion.
        """
        try:
            # ALL business logic here
            self._semaphore.release()

        except Exception as e:
            logger.error(f"❌ Error in release_semaphore: {e}")

    async def cleanup_old_requests(self) -> None:
        """
        Clean up old request history to prevent memory leaks.
        """
        try:
            # ALL business logic here
            current_time = time.time()
            if current_time - self.last_cleanup < self.cleanup_interval:
                return

            # Clean up old request history
            for telegram_id in list(self.request_history.keys()):
                user_requests = self.request_history[telegram_id]

                # Remove requests older than 5 minutes
                while user_requests and current_time - user_requests[0] > 300:
                    user_requests.popleft()

                # Remove empty user histories
                if not user_requests:
                    del self.request_history[telegram_id]

            self.last_cleanup = current_time
            logger.debug(
                LOG_MESSAGES["CLEANUP_COMPLETED"].format(
                    user_count=len(self.request_history), active_requests=len(self.active_requests)
                )
            )

        except Exception as e:
            logger.error(f"❌ Error in cleanup_old_requests: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """
        Get current resource usage metrics.

        Returns:
            Dictionary with current metrics
        """
        try:
            # ALL business logic here
            current_time = time.time()

            # Calculate average requests per user
            total_requests = sum(len(requests) for requests in self.request_history.values())
            avg_requests_per_user = (
                total_requests / len(self.request_history) if self.request_history else 0
            )

            return {
                "active_requests": len(self.active_requests),
                "total_users": len(self.request_history),
                "total_requests": total_requests,
                "avg_requests_per_user": avg_requests_per_user,
                "max_concurrent": self.max_concurrent,
                "max_requests_per_minute": self.max_requests_per_minute,
                "last_cleanup": self.last_cleanup,
            }

        except Exception as e:
            logger.error(f"❌ Error in get_metrics: {e}")
            return {
                "error": "Failed to get metrics",
                "active_requests": len(self.active_requests),
                "last_cleanup": self.last_cleanup,
            }
