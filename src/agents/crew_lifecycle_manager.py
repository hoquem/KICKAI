#!/usr/bin/env python3
"""
Crew Lifecycle Manager

This module provides enhanced management of long-lived crews for each team,
including resource monitoring, health checks, and lifecycle management.
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from loguru import logger

from src.agents.crew_agents import TeamManagementSystem


class CrewStatus(Enum):
    """Status of a crew instance."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class CrewMetrics:
    """Metrics for crew performance monitoring."""
    team_id: str
    created_at: datetime
    last_activity: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    memory_usage: dict[str, Any]
    agent_health: dict[str, bool]


class CrewLifecycleManager:
    """
    Manages long-lived crews for each team with enhanced monitoring and resource management.
    
    This manager ensures that each team has a persistent, healthy crew instance
    that can handle requests efficiently while maintaining conversation context.
    """

    def __init__(self):
        self._crews: dict[str, TeamManagementSystem] = {}
        self._crew_status: dict[str, CrewStatus] = {}
        self._crew_metrics: dict[str, CrewMetrics] = {}
        self._crew_locks: dict[str, asyncio.Lock] = {}
        self._monitoring_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

        logger.info("🚀 CrewLifecycleManager initialized")

    async def get_or_create_crew(self, team_id: str) -> TeamManagementSystem:
        """
        Get an existing crew or create a new one for the team.
        
        Args:
            team_id: The team ID to get/create crew for
            
        Returns:
            TeamManagementSystem instance for the team
        """
        # Check if crew already exists
        if team_id in self._crews:
            crew = self._crews[team_id]
            if self._crew_status[team_id] == CrewStatus.ACTIVE:
                logger.info(f"🔄 Reusing existing crew for team {team_id}")
                return crew
            elif self._crew_status[team_id] == CrewStatus.ERROR:
                logger.warning(f"⚠️ Crew for team {team_id} in error state, recreating")
                await self._shutdown_crew(team_id)

        # Create new crew
        logger.info(f"🆕 Creating new crew for team {team_id}")
        return await self._create_crew(team_id)

    async def _create_crew(self, team_id: str) -> TeamManagementSystem:
        """Create a new crew for the specified team."""
        try:
            # Set status to initializing
            self._crew_status[team_id] = CrewStatus.INITIALIZING

            # Create lock for this crew
            if team_id not in self._crew_locks:
                self._crew_locks[team_id] = asyncio.Lock()

            # Create the crew
            crew = TeamManagementSystem(team_id=team_id)

            # Store the crew
            self._crews[team_id] = crew

            # Initialize metrics
            self._crew_metrics[team_id] = CrewMetrics(
                team_id=team_id,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                memory_usage={},
                agent_health={}
            )

            # Set status to active
            self._crew_status[team_id] = CrewStatus.ACTIVE

            logger.info(f"✅ Crew created successfully for team {team_id}")
            return crew

        except Exception as e:
            self._crew_status[team_id] = CrewStatus.ERROR
            logger.error(f"❌ Failed to create crew for team {team_id}: {e}")
            raise

    async def execute_task(self, team_id: str, task_description: str, execution_context: dict[str, Any]) -> str:
        """
        Execute a task using the team's crew with metrics tracking.
        
        Args:
            team_id: The team ID
            task_description: The task to execute
            execution_context: Execution context
            
        Returns:
            Task execution result
        """
        start_time = datetime.now()

        try:
            # Get or create crew
            crew = await self.get_or_create_crew(team_id)

            # Update metrics
            metrics = self._crew_metrics[team_id]
            metrics.total_requests += 1
            metrics.last_activity = datetime.now()

            # Execute task
            result = await crew.execute_task(task_description, execution_context)

            # Update success metrics
            metrics.successful_requests += 1

            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_requests - 1) + response_time) /
                metrics.total_requests
            )

            # Update agent health
            health_status = crew.health_check()
            metrics.agent_health = health_status.get('agents', {})
            metrics.memory_usage = {
                'conversation_count': len(crew.team_memory._conversation_history),
                'user_count': len(crew.team_memory._user_memories)
            }

            logger.info(f"✅ Task executed successfully for team {team_id} in {response_time:.2f}s")
            return result

        except Exception as e:
            # Update failure metrics
            if team_id in self._crew_metrics:
                metrics = self._crew_metrics[team_id]
                metrics.failed_requests += 1
                metrics.last_activity = datetime.now()

            logger.error(f"❌ Task execution failed for team {team_id}: {e}")
            raise

    async def _shutdown_crew(self, team_id: str):
        """Shutdown a crew for the specified team."""
        try:
            if team_id in self._crews:
                crew = self._crews[team_id]
                # Note: TeamManagementSystem doesn't have explicit shutdown method
                # but we can clean up references
                del self._crews[team_id]

            if team_id in self._crew_status:
                self._crew_status[team_id] = CrewStatus.SHUTDOWN

            if team_id in self._crew_locks:
                del self._crew_locks[team_id]

            logger.info(f"🛑 Crew shutdown for team {team_id}")

        except Exception as e:
            logger.error(f"❌ Error shutting down crew for team {team_id}: {e}")

    async def get_crew_status(self, team_id: str) -> CrewStatus | None:
        """Get the status of a crew for the specified team."""
        return self._crew_status.get(team_id)

    async def get_crew_metrics(self, team_id: str) -> CrewMetrics | None:
        """Get metrics for a crew for the specified team."""
        return self._crew_metrics.get(team_id)

    async def get_all_crew_metrics(self) -> dict[str, CrewMetrics]:
        """Get metrics for all crews."""
        return self._crew_metrics.copy()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on all crews."""
        health_status = {
            'total_crews': len(self._crews),
            'active_crews': 0,
            'error_crews': 0,
            'crews': {}
        }

        for team_id, status in self._crew_status.items():
            crew_health = {
                'status': status.value,
                'metrics': self._crew_metrics.get(team_id)
            }

            if status == CrewStatus.ACTIVE:
                health_status['active_crews'] += 1
                # Perform detailed health check on active crews
                if team_id in self._crews:
                    try:
                        crew = self._crews[team_id]
                        crew_health['crew_health'] = crew.health_check()
                    except Exception as e:
                        crew_health['crew_health'] = {'error': str(e)}
                        health_status['error_crews'] += 1
            elif status == CrewStatus.ERROR:
                health_status['error_crews'] += 1

            health_status['crews'][team_id] = crew_health

        return health_status

    async def start_monitoring(self):
        """Start the monitoring task for crew health checks."""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("🔍 Crew monitoring started")

    async def stop_monitoring(self):
        """Stop the monitoring task."""
        if self._monitoring_task and not self._monitoring_task.done():
            self._shutdown_event.set()
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Crew monitoring stopped")

    async def _monitoring_loop(self):
        """Monitoring loop for crew health checks."""
        while not self._shutdown_event.is_set():
            try:
                # Perform health checks every 5 minutes
                health_status = await self.health_check()

                # Log health status
                logger.info(f"🔍 Crew health check: {health_status['active_crews']} active, {health_status['error_crews']} errors")

                # Check for idle crews (no activity for 30 minutes)
                await self._check_idle_crews()

                # Wait 5 minutes before next check
                await asyncio.sleep(300)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _check_idle_crews(self):
        """Check for idle crews and mark them appropriately."""
        idle_threshold = datetime.now() - timedelta(minutes=30)

        for team_id, metrics in self._crew_metrics.items():
            if metrics.last_activity < idle_threshold:
                if self._crew_status[team_id] == CrewStatus.ACTIVE:
                    self._crew_status[team_id] = CrewStatus.IDLE
                    logger.info(f"💤 Crew for team {team_id} marked as idle")

    async def shutdown_all_crews(self):
        """Shutdown all crews."""
        logger.info("🛑 Shutting down all crews...")

        # Stop monitoring
        await self.stop_monitoring()

        # Shutdown all crews
        shutdown_tasks = []
        for team_id in list(self._crews.keys()):
            shutdown_tasks.append(self._shutdown_crew(team_id))

        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        logger.info("✅ All crews shutdown complete")

    @asynccontextmanager
    async def crew_context(self, team_id: str):
        """
        Context manager for safe crew access.
        
        Args:
            team_id: The team ID to get crew for
            
        Yields:
            TeamManagementSystem instance
        """
        crew = await self.get_or_create_crew(team_id)
        try:
            yield crew
        except Exception as e:
            logger.error(f"❌ Error in crew context for team {team_id}: {e}")
            # Mark crew as error state
            self._crew_status[team_id] = CrewStatus.ERROR
            raise


# Global instance for easy access
_crew_lifecycle_manager: CrewLifecycleManager | None = None


def get_crew_lifecycle_manager() -> CrewLifecycleManager:
    """Get the global crew lifecycle manager instance."""
    global _crew_lifecycle_manager
    if _crew_lifecycle_manager is None:
        _crew_lifecycle_manager = CrewLifecycleManager()
    return _crew_lifecycle_manager


async def initialize_crew_lifecycle_manager():
    """Initialize the global crew lifecycle manager."""
    global _crew_lifecycle_manager
    if _crew_lifecycle_manager is None:
        _crew_lifecycle_manager = CrewLifecycleManager()
        await _crew_lifecycle_manager.start_monitoring()
        logger.info("🚀 Global crew lifecycle manager initialized")


async def shutdown_crew_lifecycle_manager():
    """Shutdown the global crew lifecycle manager."""
    global _crew_lifecycle_manager
    if _crew_lifecycle_manager:
        await _crew_lifecycle_manager.shutdown_all_crews()
        _crew_lifecycle_manager = None
        logger.info("🛑 Global crew lifecycle manager shutdown")
