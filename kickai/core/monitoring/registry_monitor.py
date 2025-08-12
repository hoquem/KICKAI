"""
Registry monitoring and metrics collection.

This module provides monitoring capabilities for registry
performance and usage tracking.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class RegistryMetrics:
    """Metrics for a registry."""

    name: str
    total_items: int = 0
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_response_time: float = 0.0
    errors: int = 0
    last_updated: float = field(default_factory=time.time)


class RegistryMonitor:
    """Monitors registry performance and usage."""

    def __init__(self):
        self._metrics: dict[str, RegistryMetrics] = defaultdict(lambda: RegistryMetrics(""))
        self._request_times: dict[str, list[float]] = defaultdict(list)
        self._enabled = True

        logger.info("📊 Registry Monitor initialized")

    def record_request(
        self, registry_name: str, item_name: str, success: bool, response_time: float
    ) -> None:
        """Record a registry request."""
        if not self._enabled:
            return

        metrics = self._metrics[registry_name]
        metrics.name = registry_name
        metrics.total_requests += 1
        metrics.last_updated = time.time()

        if success:
            metrics.cache_hits += 1
        else:
            metrics.cache_misses += 1
            metrics.errors += 1

        # Update average response time
        self._request_times[registry_name].append(response_time)
        if len(self._request_times[registry_name]) > 100:  # Keep last 100 requests
            self._request_times[registry_name] = self._request_times[registry_name][-100:]

        metrics.average_response_time = sum(self._request_times[registry_name]) / len(
            self._request_times[registry_name]
        )

    def record_item_count(self, registry_name: str, count: int) -> None:
        """Record the number of items in a registry."""
        if not self._enabled:
            return

        metrics = self._metrics[registry_name]
        metrics.name = registry_name
        metrics.total_items = count
        metrics.last_updated = time.time()

    def get_metrics(self, registry_name: str | None = None) -> dict[str, Any]:
        """Get metrics for a specific registry or all registries."""
        if registry_name:
            return self._metrics[registry_name].__dict__

        return {name: metrics.__dict__ for name, metrics in self._metrics.items()}

    def get_performance_report(self) -> str:
        """Generate a performance report."""
        if not self._metrics:
            return "No registry metrics available"

        report = ["📊 Registry Performance Report", ""]

        for name, metrics in self._metrics.items():
            report.append(f"**{name}**")
            report.append(f"  Total Items: {metrics.total_items}")
            report.append(f"  Total Requests: {metrics.total_requests}")
            report.append(
                f"  Cache Hit Rate: {metrics.cache_hits / max(metrics.total_requests, 1) * 100:.1f}%"
            )
            report.append(f"  Average Response Time: {metrics.average_response_time * 1000:.2f}ms")
            report.append(f"  Errors: {metrics.errors}")
            report.append("")

        return "\n".join(report)

    def reset_metrics(self, registry_name: str | None = None) -> None:
        """Reset metrics for a specific registry or all registries."""
        if registry_name:
            self._metrics[registry_name] = RegistryMetrics(registry_name)
            self._request_times[registry_name].clear()
        else:
            self._metrics.clear()
            self._request_times.clear()

        logger.info(f"🔄 Reset metrics for {registry_name or 'all registries'}")

    def enable(self) -> None:
        """Enable monitoring."""
        self._enabled = True
        logger.info("📊 Registry monitoring enabled")

    def disable(self) -> None:
        """Disable monitoring."""
        self._enabled = False
        logger.info("📊 Registry monitoring disabled")

    def is_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self._enabled
