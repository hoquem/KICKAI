#!/usr/bin/env python3
"""
Database Performance Optimizer

This module provides database performance optimization utilities for the KICKAI system,
including indexing recommendations and query optimization strategies.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from loguru import logger

from kickai.database.interfaces import DataStoreInterface


class DatabasePerformanceOptimizer:
    """Database performance optimization utilities."""

    def __init__(self, database: DataStoreInterface):
        self.database = database
        self.collection_name = "kickai_invite_links"

    async def get_indexing_recommendations(self) -> Dict[str, Any]:
        """
        Get database indexing recommendations for optimal performance.

        Returns:
            Dict containing indexing recommendations
        """
        recommendations = {
            "critical_indexes": [
                {
                    "collection": "kickai_invite_links",
                    "fields": ["team_id", "status", "created_at"],
                    "description": "Optimize team-based invite link queries",
                    "priority": "HIGH"
                },
                {
                    "collection": "kickai_invite_links",
                    "fields": ["status", "expires_at"],
                    "description": "Optimize expired link cleanup queries",
                    "priority": "HIGH"
                },
                {
                    "collection": "kickai_players",
                    "fields": ["team_id", "status", "telegram_id"],
                    "description": "Optimize player lookup by telegram_id",
                    "priority": "HIGH"
                },
                {
                    "collection": "kickai_players",
                    "fields": ["team_id", "phone"],
                    "description": "Optimize player lookup by phone number",
                    "priority": "HIGH"
                },
                {
                    "collection": "kickai_team_members",
                    "fields": ["team_id", "telegram_id"],
                    "description": "Optimize team member lookup by telegram_id",
                    "priority": "HIGH"
                }
            ],
            "performance_metrics": await self._get_performance_metrics(),
            "optimization_suggestions": await self._get_optimization_suggestions()
        }

        return recommendations

    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current database performance metrics."""
        try:
            # Get invite link statistics
            total_links = await self._count_documents(self.collection_name)
            active_links = await self._count_documents_with_filter(
                self.collection_name, {"status": "active"}
            )
            expired_links = await self._count_documents_with_filter(
                self.collection_name, {"status": "active", "expires_at": {"$lt": datetime.now().isoformat()}}
            )

            return {
                "total_invite_links": total_links,
                "active_invite_links": active_links,
                "expired_invite_links": expired_links,
                "expired_percentage": (expired_links / max(active_links, 1)) * 100,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting performance metrics: {e}")
            return {"error": str(e)}

    async def _get_optimization_suggestions(self) -> List[str]:
        """Get database optimization suggestions."""
        suggestions = []

        try:
            # Check for expired links that need cleanup
            expired_count = await self._count_documents_with_filter(
                self.collection_name,
                {"status": "active", "expires_at": {"$lt": datetime.now().isoformat()}}
            )

            if expired_count > 0:
                suggestions.append(f"Clean up {expired_count} expired invite links")

            # Check for unused links (older than 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            old_unused = await self._count_documents_with_filter(
                self.collection_name,
                {"status": "active", "created_at": {"$lt": thirty_days_ago}}
            )

            if old_unused > 0:
                suggestions.append(f"Review {old_unused} invite links older than 30 days")

            # Check for high usage patterns
            recent_links = await self._count_documents_with_filter(
                self.collection_name,
                {"created_at": {"$gt": (datetime.now() - timedelta(days=7)).isoformat()}}
            )

            if recent_links > 100:
                suggestions.append("High invite link creation rate detected - consider rate limiting")

        except Exception as e:
            logger.error(f"❌ Error getting optimization suggestions: {e}")
            suggestions.append(f"Error analyzing database: {e}")

        return suggestions

    async def cleanup_expired_links(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Clean up expired invite links in batches.

        Args:
            batch_size: Number of links to process in each batch

        Returns:
            Dict containing cleanup results
        """
        try:
            logger.info(f"🧹 [DB_OPTIMIZATION] Starting expired link cleanup with batch_size={batch_size}")

            # Get expired links
            expired_links = await self._get_expired_links(batch_size)

            if not expired_links:
                logger.info("✅ [DB_OPTIMIZATION] No expired links found")
                return {"cleaned": 0, "total_expired": 0, "status": "no_expired_links"}

            # Mark as expired
            cleaned_count = 0
            for link in expired_links:
                try:
                    await self.database.update_document(
                        self.collection_name,
                        link["invite_id"],
                        {
                            "status": "expired",
                            "expired_at": datetime.now().isoformat()
                        }
                    )
                    cleaned_count += 1
                    logger.debug(f"🧹 [DB_OPTIMIZATION] Marked link as expired: {link['invite_id']}")
                except Exception as e:
                    logger.error(f"❌ [DB_OPTIMIZATION] Error marking link as expired: {link['invite_id']}, error={e}")

            logger.info(f"✅ [DB_OPTIMIZATION] Cleanup completed: {cleaned_count}/{len(expired_links)} links processed")

            return {
                "cleaned": cleaned_count,
                "total_expired": len(expired_links),
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"❌ [DB_OPTIMIZATION] Error during cleanup: {e}")
            return {"error": str(e), "status": "failed"}

    async def _count_documents(self, collection: str) -> int:
        """Count total documents in a collection."""
        try:
            # This is a simplified implementation - actual implementation would depend on the database interface
            return 0  # Placeholder
        except Exception as e:
            logger.error(f"❌ Error counting documents in {collection}: {e}")
            return 0

    async def _count_documents_with_filter(self, collection: str, filters: Dict[str, Any]) -> int:
        """Count documents matching specific filters."""
        try:
            # This is a simplified implementation - actual implementation would depend on the database interface
            return 0  # Placeholder
        except Exception as e:
            logger.error(f"❌ Error counting documents with filter in {collection}: {e}")
            return 0

    async def _get_expired_links(self, limit: int) -> List[Dict[str, Any]]:
        """Get expired invite links."""
        try:
            # This is a simplified implementation - actual implementation would depend on the database interface
            return []  # Placeholder
        except Exception as e:
            logger.error(f"❌ Error getting expired links: {e}")
            return []

    async def optimize_queries(self) -> Dict[str, Any]:
        """
        Provide query optimization recommendations.

        Returns:
            Dict containing optimization recommendations
        """
        recommendations = {
            "query_optimizations": [
                {
                    "query_type": "invite_link_lookup",
                    "recommendation": "Use compound index on (team_id, status, created_at)",
                    "impact": "HIGH",
                    "description": "Optimizes team-based invite link queries"
                },
                {
                    "query_type": "player_lookup",
                    "recommendation": "Use compound index on (team_id, phone)",
                    "impact": "HIGH",
                    "description": "Optimizes player lookup by phone number"
                },
                {
                    "query_type": "expired_cleanup",
                    "recommendation": "Use compound index on (status, expires_at)",
                    "impact": "MEDIUM",
                    "description": "Optimizes expired link cleanup queries"
                }
            ],
            "caching_strategies": [
                {
                    "cache_type": "team_config",
                    "recommendation": "Cache team configuration for 1 hour",
                    "impact": "HIGH",
                    "description": "Reduces database queries for team settings"
                },
                {
                    "cache_type": "active_links",
                    "recommendation": "Cache active invite links for 5 minutes",
                    "impact": "MEDIUM",
                    "description": "Reduces database queries for link validation"
                }
            ],
            "batch_operations": [
                {
                    "operation": "expired_cleanup",
                    "recommendation": "Process expired links in batches of 100",
                    "impact": "MEDIUM",
                    "description": "Prevents timeout on large cleanup operations"
                }
            ]
        }

        return recommendations


async def get_database_optimizer(database: DataStoreInterface) -> DatabasePerformanceOptimizer:
    """
    Get a database performance optimizer instance.

    Args:
        database: Database interface instance

    Returns:
        DatabasePerformanceOptimizer instance
    """
    return DatabasePerformanceOptimizer(database)


async def run_performance_audit(database: DataStoreInterface) -> Dict[str, Any]:
    """
    Run a comprehensive database performance audit.

    Args:
        database: Database interface instance

    Returns:
        Dict containing audit results
    """
    optimizer = await get_database_optimizer(database)

    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "indexing_recommendations": await optimizer.get_indexing_recommendations(),
        "query_optimizations": await optimizer.optimize_queries(),
        "cleanup_suggestions": await optimizer._get_optimization_suggestions()
    }

    logger.info("✅ [DB_AUDIT] Performance audit completed")
    return audit_results
