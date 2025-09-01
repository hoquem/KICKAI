#!/usr/bin/env python3
"""
Crew Lifecycle Manager

This module provides enhanced management of long-lived crews for each team,
including resource monitoring, health checks, and lifecycle management.
"""

import asyncio
from asyncio import Task
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol, Dict

from loguru import logger

# Constants
MONITORING_INTERVAL_SECONDS = 300  # 5 minutes
IDLE_THRESHOLD_MINUTES = 30
RETRY_DELAY_SECONDS = 60

# Lazy import to avoid circular dependencies
# from kickai.agents.crew_agents import TeamManagementSystem


class CrewError(Exception):
    """Base exception for crew-related errors."""
    pass


class CrewTimeoutError(CrewError):
    """Raised when crew execution times out."""
    pass


class CrewHealthError(CrewError):
    """Raised when crew health check fails."""
    pass


class CrewInitializationError(CrewError):
    """Raised when crew initialization fails."""
    pass


class CrewProtocol(Protocol):
    """Protocol defining the interface for crew instances."""
    
    def execute_task(self, task_description: str, execution_context: Dict[str, Any]) -> str:
        """Execute a task and return the result."""
        ...
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check and return status."""
        ...


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
    memory_usage: Dict[str, Any]
    agent_health: Dict[str, bool]


class CrewLifecycleManager:
    """
    Manages long-lived crews for each team with enhanced monitoring and resource management.

    This manager ensures that each team has a persistent, healthy crew instance
    that can handle requests efficiently while maintaining conversation context.
    """

    def __init__(self):
        self._crews: dict[str, Any] = {}
        self._crew_status: dict[str, CrewStatus] = {}
        self._crew_metrics: dict[str, CrewMetrics] = {}
        self._crew_locks: dict[str, asyncio.Lock] = {}
        self._monitoring_task: Task | None = None
        self._shutdown_event = asyncio.Event()

        logger.info("🚀 CrewLifecycleManager initialized")

    async def get_or_create_crew(self, team_id: str) -> Any:
        """
        Get an existing crew or create a new one for the team.
        
        CREWAI BUG WORKAROUND: Always create fresh crew to avoid manager agent tools bug.
        """
        # CREWAI BUG WORKAROUND: Always create new crew to avoid "Manager agent should not have tools" bug
        if team_id in self._crews:
            logger.warning(f"🔄 CrewAI bug workaround: Shutting down existing crew for team {team_id}")
            await self._shutdown_crew(team_id)
        
        # Create new crew
        logger.info(f"🆕 Creating new crew for team {team_id}")
        return await self._create_crew(team_id)

    async def _create_crew(self, team_id: str) -> Any:
        """Create a new crew for the specified team."""
        # Set status to initializing
        self._crew_status[team_id] = CrewStatus.INITIALIZING

        # Create lock for this crew
        if team_id not in self._crew_locks:
            self._crew_locks[team_id] = asyncio.Lock()

        # Create the crew with lazy import to avoid circular dependencies
        from kickai.agents.crew_agents import TeamManagementSystem

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
            agent_health={},
        )

        # Set status to active
        self._crew_status[team_id] = CrewStatus.ACTIVE

        logger.info(f"✅ Crew created successfully for team {team_id}")
        return crew

    async def execute_task(
        self, team_id: str, task_description: str, execution_context: dict[str, Any]
    ) -> str:
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

            # Execute task with timeout
            result = await self._execute_task_with_timeout(crew, team_id, task_description, execution_context)

            # Update success metrics
            metrics.successful_requests += 1

            # Calculate and update response time
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_response_time_metrics(metrics, response_time)

            # Update agent health
            self._update_agent_health_metrics(crew, team_id, metrics)

            logger.info(f"✅ Task executed successfully for team {team_id} in {response_time:.2f}s")
            return result

        except Exception as e:
            # Update failure metrics
            self._update_failure_metrics(team_id)
            logger.error(f"❌ Task execution failed for team {team_id}: {e}")

            # Always return a response, even on complete failure
            return self._generate_formatted_response(
                title="🚨 System Error",
                problem_summary=f"I'm experiencing technical difficulties right now. This is a system-level issue that needs attention.",
                task_description=task_description,
                suggestions=[
                    "Try again in a few minutes",
                    "Use basic commands like `/help` or `/info`",
                    "Contact your team administrator if the problem persists"
                ],
                commands_to_show=["/help", "/info"]
            )

    def _generate_formatted_response(self, title: str, problem_summary: str, task_description: str, suggestions: list[str], commands_to_show: list[str]) -> str:
        """Generates a formatted, user-friendly response for errors and fallbacks."""
        
        suggestions_list = "\n".join([f"• {s}" for s in suggestions])
        commands_list = "\n".join([f"• `{cmd}` - {desc}" for cmd, desc in {
            "/help": "Show available commands",
            "/info": "Show your information",
            "/list": "List team members/players",
            "/status": "Check status"
        }.items() if cmd in commands_to_show])

        return f"""🤖 I was processing: "{task_description}"

{title}

{problem_summary}

💡 **Quick Solutions:**
{suggestions_list}

🔧 **Available Commands:**
{commands_list}

If the problem persists, please contact your team administrator."""

    async def _execute_task_with_timeout(self, crew: CrewProtocol, team_id: str, task_description: str, execution_context: Dict[str, Any]) -> str:
        """
        Execute task with timeout handling and comprehensive error catching.
        
        Args:
            crew: The crew instance to execute the task on
            team_id: The team ID
            task_description: The task description
            execution_context: The execution context
            
        Returns:
            Task execution result
            
        Raises:
            CrewTimeoutError: If task execution times out
            CrewError: For other crew-related errors
        """
        from kickai.core.constants.agent_constants import AgentConstants
        timeout_seconds = AgentConstants.CREW_MAX_EXECUTION_TIME

        try:
            # Clear manager tools before execution (workaround for CrewAI issues #1851, #909)
            # This prevents "Manager agent should not have tools" error on crew reuse
            if hasattr(crew, 'crew') and hasattr(crew.crew, 'manager_agent') and crew.crew.manager_agent:
                crew.crew.manager_agent.tools = []
                logger.debug("🧹 Cleared manager agent tools (CrewAI bug workaround)")
            
            # Execute CrewAI task with timeout - task description is already enhanced in crew_agents.py
            result = await asyncio.wait_for(
                crew.execute_task(task_description, execution_context),
                timeout=timeout_seconds
            )

            # Check if result is empty or indicates failure
            if not result or result.strip() == "":
                logger.warning(f"⚠️ Empty result from crew for team {team_id}, providing fallback response")
                return self._generate_formatted_response(
                    title="🤔 I'm having trouble with this request.",
                    problem_summary="I was able to process your request, but couldn't generate a specific answer.",
                    task_description=task_description,
                    suggestions=[
                        "Try rephrasing your question.",
                        "Use a more specific command like `/help` for assistance.",
                        "Check if you're in the right chat (main vs leadership)."
                    ],
                    commands_to_show=["/help", "/info", "/list", "/status"]
                )

            return result

        except asyncio.TimeoutError as e:
            logger.error(f"⏰ Timeout after {timeout_seconds}s for team {team_id}")
            raise CrewTimeoutError(f"Task execution timed out after {timeout_seconds} seconds for team {team_id}") from e
            
        except Exception as e:
            logger.error(f"❌ Crew execution failed for team {team_id}: {e}")
            import traceback
            logger.error(f"❌ Crew error traceback: {traceback.format_exc()}")

            # Check if it's a max iterations error
            if "Maximum iterations reached" in str(e) or "max_iter" in str(e).lower():
                logger.warning(f"⚠️ Max iterations reached for team {team_id}, providing iteration limit response")
                return self._generate_formatted_response(
                    title="⏱️ Processing Time Limit Reached",
                    problem_summary="I've reached the maximum number of processing steps for this request. This usually happens when the request is very complex or requires multiple tools.",
                    task_description=task_description,
                    suggestions=[
                        "Try breaking down your request into smaller parts.",
                        "Use specific commands instead of natural language.",
                    ],
                    commands_to_show=["/help", "/info", "/list"]
                )

            # For all other errors, raise as CrewError
            raise CrewError(f"Unexpected crew error for team {team_id}: {e}") from e

    def _update_response_time_metrics(self, metrics: CrewMetrics, response_time: float) -> None:
        """Update response time metrics."""
        metrics.average_response_time = (
            metrics.average_response_time * (metrics.total_requests - 1) + response_time
        ) / metrics.total_requests

    def _update_agent_health_metrics(self, crew: Any, team_id: str, metrics: CrewMetrics) -> None:
        """Update agent health metrics."""
        health_status = crew.health_check()
        metrics.agent_health = health_status.get("agents", {})
        
        # Handle memory usage - simplified TeamManagementSystem doesn't have team_memory
        try:
            if hasattr(crew, 'team_memory') and crew.team_memory is not None:
                metrics.memory_usage = {
                    "conversation_count": len(crew.team_memory._conversation_history),
                    "user_count": len(crew.team_memory._telegram_memories),
                }
            else:
                # Simplified system - no memory tracking
                metrics.memory_usage = {
                    "conversation_count": 0,
                    "user_count": 0,
                    "note": "Simplified system - memory tracking disabled"
                }
        except Exception as e:
            logger.warning(f"⚠️ Could not update memory metrics for team {team_id}: {e}")
            metrics.memory_usage = {
                "conversation_count": 0,
                "user_count": 0,
                "error": "Memory metrics unavailable"
            }

    def _update_failure_metrics(self, team_id: str) -> None:
        """Update failure metrics."""
        if team_id in self._crew_metrics:
            metrics = self._crew_metrics[team_id]
            metrics.failed_requests += 1
            metrics.last_activity = datetime.now()



    async def _shutdown_crew(self, team_id: str):
        """Shutdown a crew for the specified team."""
        try:
            if team_id in self._crews:
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

    async def force_recreate_crew(self, team_id: str) -> Any:
        """
        Force recreation of a crew for configuration changes.
        
        This method ensures that any cached crew is removed and a new one is created
        with the latest configuration. Useful when the underlying crew configuration
        has changed (e.g., manager agent fixes, tool updates, etc.).
        
        Args:
            team_id: The team ID to force recreate crew for
            
        Returns:
            Newly created TeamManagementSystem instance
        """
        logger.info(f"🔄 Force recreating crew for team {team_id}")
        
        # Always shutdown existing crew regardless of status
        if team_id in self._crews:
            logger.info(f"🛑 Shutting down existing crew for configuration update")
            await self._shutdown_crew(team_id)
        
        # Create new crew with updated configuration
        logger.info(f"🆕 Creating new crew with updated configuration")
        return await self._create_crew(team_id)

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
            "total_crews": len(self._crews),
            "active_crews": 0,
            "error_crews": 0,
            "crews": {},
        }

        for team_id, status in self._crew_status.items():
            crew_health = {"status": status.value, "metrics": self._crew_metrics.get(team_id)}

            if status == CrewStatus.ACTIVE:
                health_status["active_crews"] += 1
                # Perform detailed health check on active crews
                if team_id in self._crews:
                    crew = self._crews[team_id]
                    crew_health["crew_health"] = crew.health_check()
            elif status == CrewStatus.ERROR:
                health_status["error_crews"] += 1

            health_status["crews"][team_id] = crew_health

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
            await self._monitoring_task
            logger.info("🛑 Crew monitoring stopped")

    async def _monitoring_loop(self):
        """Monitoring loop for crew health checks."""
        while not self._shutdown_event.is_set():
            try:
                # Perform health checks every 5 minutes
                health_status = await self.health_check()

                # Log health status
                logger.info(
                    f"🔍 Crew health check: {health_status['active_crews']} active, {health_status['error_crews']} errors"
                )

                # Check for idle crews (no activity for 30 minutes)
                await self._check_idle_crews()

                # Wait before next check
                await asyncio.sleep(MONITORING_INTERVAL_SECONDS)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(RETRY_DELAY_SECONDS)  # Wait before retrying

    async def _check_idle_crews(self):
        """Check for idle crews and mark them appropriately."""
        idle_threshold = datetime.now() - timedelta(minutes=IDLE_THRESHOLD_MINUTES)
        # Use list(items()) to avoid issues with modifying dict during iteration
        for team_id, metrics in list(self._crew_metrics.items()):
            if metrics.last_activity < idle_threshold:
                if self._crew_status[team_id] == CrewStatus.ACTIVE:
                    self._crew_status[team_id] = CrewStatus.IDLE
                    logger.info(f"💤 Crew for team {team_id} is idle. Shutting down to conserve resources.")
                    # Shut down the idle crew to free up memory and resources
                    await self._shutdown_crew(team_id)

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
        yield crew


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
