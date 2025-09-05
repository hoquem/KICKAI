"""
CrewAI Task Factory for KICKAI

This module provides a factory for creating well-defined, specific CrewAI tasks
following 2025 best practices with structured outputs and clear descriptions.
"""

import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from crewai import Agent, Task
from loguru import logger
from pydantic import BaseModel

from kickai.core.enums import AgentRole
from kickai.core.models.task_outputs import (
    CommunicationOutput,
    HelpOutput,
    MatchAvailabilityOutput,
    MatchListOutput,
    PlayersListOutput,
    PlayerStatusOutput,
    SystemStatusOutput,
    TaskExecutionMetrics,
    TeamMembersOutput,
)


class TaskType:
    """Enumeration of task types for KICKAI operations."""

    PLAYER_STATUS = "player_status"
    PLAYER_LIST = "player_list"
    TEAM_MEMBERS = "team_members"
    MATCH_LIST = "match_list"
    MATCH_AVAILABILITY = "match_availability"
    HELP_REQUEST = "help_request"
    SYSTEM_STATUS = "system_status"
    COMMUNICATION = "communication"
    REGISTRATION = "registration"
    GENERIC_OPERATION = "generic_operation"


class TaskTemplate:
    """Template for creating specific task types."""

    def __init__(
        self,
        task_type: str,
        description_template: str,
        expected_output: str,
        output_model: type[BaseModel] | None = None,
        required_tools: list[str] | None = None,
        agent_role: AgentRole | None = None,
        async_execution: bool = False,
        context_dependencies: list[str] | None = None,
    ):
        self.task_type = task_type
        self.description_template = description_template
        self.expected_output = expected_output
        self.output_model = output_model
        self.required_tools = required_tools or []
        self.agent_role = agent_role
        self.async_execution = async_execution
        self.context_dependencies = context_dependencies or []


class TaskFactory:
    """Factory for creating well-defined CrewAI tasks."""

    def __init__(self):
        self.task_templates = self._initialize_templates()
        self.execution_callbacks: list[Callable] = []
        self.metrics_store: dict[str, TaskExecutionMetrics] = {}

    def _initialize_templates(self) -> dict[str, TaskTemplate]:
        """Initialize task templates for different operation types."""
        return {
            TaskType.PLAYER_STATUS: TaskTemplate(
                task_type=TaskType.PLAYER_STATUS,
                description_template="""
                Get detailed status information for player: {player_name}

                Team Context:
                - Team ID: {team_id}
                - Requesting User: {telegram_username} (Telegram ID: {telegram_id})
                - Chat Type: {chat_type}

                Required Information:
                1. Player registration status and date
                2. Current activity level
                3. Match participation history
                4. Position and jersey number (if available)
                5. Last activity timestamp

                Use the get_player_status tool with the provided context.
                If player not found, provide clear indication.
                """,
                expected_output="""
                Structured player status information including:
                - Player identification (username, full name)
                - Registration status and date
                - Activity level and last seen
                - Match statistics
                - Position and jersey number
                - Any relevant notes or warnings
                """,
                output_model=PlayerStatusOutput,
                required_tools=["get_player_status"],
                agent_role=AgentRole.PLAYER_COORDINATOR,
            ),
            TaskType.PLAYER_LIST: TaskTemplate(
                task_type=TaskType.PLAYER_LIST,
                description_template="""
                Retrieve and format list of players for team: {team_id}

                Context:
                - Requesting User: {telegram_username} (Telegram ID: {telegram_id})
                - Chat Type: {chat_type}
                - Filter: {filter_type} (active, all, pending)

                Requirements:
                1. Get appropriate player list based on chat type and permissions
                2. Apply requested filter (active/all/pending)
                3. Include player status, registration date, activity
                4. Sort by activity level and name
                5. Provide count summaries

                Use get_active_players for main chat, get_all_players for leadership.
                """,
                expected_output="""
                Structured list of players with:
                - Individual player information (name, status, activity)
                - Total count and filtered count
                - Summary statistics (active, inactive, pending)
                - Appropriate formatting for the requesting chat type
                """,
                output_model=PlayersListOutput,
                required_tools=["get_active_players", "get_all_players"],
                agent_role=AgentRole.PLAYER_COORDINATOR,
            ),
            TaskType.TEAM_MEMBERS: TaskTemplate(
                task_type=TaskType.TEAM_MEMBERS,
                description_template="""
                Retrieve team member information for team: {team_id}

                Context:
                - Requesting User: {telegram_username} (Telegram ID: {telegram_id})
                - Chat Type: {chat_type}
                - Permission Level: {user_role}

                Requirements:
                1. Get team member list with roles and permissions
                2. Include admin and leadership counts
                3. Show join dates and activity
                4. Respect permission levels for information display

                Use list_team_members_and_players tool.
                """,
                expected_output="""
                Structured team member information with:
                - Member details (username, role, permissions)
                - Admin and leadership counts
                - Join dates and activity status
                - Total member count
                """,
                output_model=TeamMembersOutput,
                required_tools=["list_team_members_and_players"],
                agent_role=AgentRole.TEAM_ADMINISTRATOR,
            ),
            TaskType.MATCH_LIST: TaskTemplate(
                task_type=TaskType.MATCH_LIST,
                description_template="""
                Get match schedule and information for team: {team_id}

                Context:
                - Requesting User: {telegram_username} (Telegram ID: {telegram_id})
                - Time Range: {time_range} (upcoming, recent, all)
                - Include Details: {include_details}

                Requirements:
                1. Retrieve match list for specified time range
                2. Include opponent, date, location, type
                3. Show match status (upcoming, completed, cancelled)
                4. Include results for completed matches
                5. Sort by date (upcoming first, then chronological)

                Use list_matches tool with appropriate filters.
                """,
                expected_output="""
                Structured match information with:
                - Match details (opponent, date, location, type)
                - Match status and results
                - Count of upcoming vs completed matches
                - Chronologically sorted list
                """,
                output_model=MatchListOutput,
                required_tools=["list_matches", "get_match_details"],
                agent_role=AgentRole.SQUAD_SELECTOR,
            ),
            TaskType.MATCH_AVAILABILITY: TaskTemplate(
                task_type=TaskType.MATCH_AVAILABILITY,
                description_template="""
                Get player availability for match: {match_id}

                Context:
                - Match Date: {match_date}
                - Requesting User: {telegram_username} (Telegram ID: {telegram_id})
                - Team ID: {team_id}

                Requirements:
                1. Get all player availability responses for the match
                2. Categorize by availability status (available, unavailable, maybe, no response)
                3. Include response timestamps and notes
                4. Calculate summary statistics
                5. Identify players who haven't responded

                Use get_availability and get_available_players_for_match tools.
                """,
                expected_output="""
                Structured availability information with:
                - Player availability status and response times
                - Summary counts (available, unavailable, no response)
                - Player notes and comments
                - Match context (date, opponent)
                """,
                output_model=MatchAvailabilityOutput,
                required_tools=["get_availability", "get_available_players_for_match"],
                agent_role=AgentRole.SQUAD_SELECTOR,
            ),
            TaskType.HELP_REQUEST: TaskTemplate(
                task_type=TaskType.HELP_REQUEST,
                description_template="""
                Provide help information for user request: {query}

                Context:
                - User: {telegram_username} (Telegram ID: {telegram_id})
                - Chat Type: {chat_type}
                - User Role: {user_role}
                - Team ID: {team_id}

                Requirements:
                1. Analyze the help query and user context
                2. Get available commands for user's role and chat type
                3. Provide relevant command information and examples
                4. Include usage guidelines and permissions
                5. Offer welcome guidance for new users

                Use get_available_commands, get_command_help, and get_welcome_message tools.
                """,
                expected_output="""
                Structured help response with:
                - Available commands for user's context
                - Command descriptions and usage examples
                - Permission requirements and chat type applicability
                - Welcome guidance and next steps
                """,
                output_model=HelpOutput,
                required_tools=[
                    "get_available_commands",
                    "get_command_help",
                    "get_welcome_message",
                ],
                agent_role=AgentRole.HELP_ASSISTANT,
            ),
            TaskType.COMMUNICATION: TaskTemplate(
                task_type=TaskType.COMMUNICATION,
                description_template="""
                Handle communication request: {communication_type}

                Context:
                - Sender: {telegram_username} (Telegram ID: {telegram_id})
                - Team ID: {team_id}
                - Message: {message}
                - Recipients: {recipients}
                - Communication Type: {communication_type} (message, announcement, poll)

                Requirements:
                1. Validate sender permissions for communication type
                2. Process recipient list and validate targets
                3. Send communication using appropriate tool
                4. Track delivery status and failures
                5. Provide delivery confirmation

                Use send_message, send_announcement, or send_poll tools.
                """,
                expected_output="""
                Communication delivery report with:
                - Successful and failed deliveries
                - Recipient delivery status
                - Broadcast tracking information
                - Error details for failed deliveries
                """,
                output_model=CommunicationOutput,
                required_tools=["send_message", "send_announcement", "send_poll"],
                agent_role=AgentRole.MESSAGE_PROCESSOR,
            ),
            TaskType.SYSTEM_STATUS: TaskTemplate(
                task_type=TaskType.SYSTEM_STATUS,
                description_template="""
                Get system status and health information

                Context:
                - Requesting User: {telegram_username} (Telegram ID: {telegram_id})
                - Team ID: {team_id}
                - Status Type: {status_type} (general, detailed, health)

                Requirements:
                1. Check overall system status and version
                2. Verify database connectivity
                3. Check API endpoints and services
                4. Get activity metrics (users, teams)
                5. Report any issues or warnings

                Use ping, version, and system health tools.
                """,
                expected_output="""
                System status report with:
                - Version and uptime information
                - Database and API status
                - User activity statistics
                - Any system warnings or issues
                """,
                output_model=SystemStatusOutput,
                required_tools=["ping", "version"],
                agent_role=AgentRole.MESSAGE_PROCESSOR,
            ),
        }

    def add_execution_callback(self, callback: Callable[[TaskExecutionMetrics], None]):
        """Add a callback to be executed after task completion."""
        self.execution_callbacks.append(callback)

    def create_task(
        self,
        task_type: str,
        agent: Agent,
        context: dict[str, Any],
        output_file: str | None = None,
        human_input: bool = False,
        additional_tools: list[str] | None = None,
    ) -> Task:
        """
        Create a specific task based on type and context.

        Args:
            task_type: Type of task to create
            agent: CrewAI agent to execute the task
            context: Context variables for task description
            output_file: Optional output file path
            human_input: Whether task requires human input
            additional_tools: Additional tools to include

        Returns:
            Configured CrewAI Task with structured output
        """
        if task_type not in self.task_templates:
            raise ValueError(f"Unknown task type: {task_type}")

        template = self.task_templates[task_type]
        task_id = str(uuid.uuid4())[:8]

        # Format description with context
        try:
            description = template.description_template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing context variable {e} for task {task_type}, using default")
            # Provide default values for missing context
            safe_context = {
                "team_id": context.get("team_id", "unknown"),
                "telegram_id": context.get("telegram_id", 0),
                "telegram_username": context.get("telegram_username", "unknown"),
                "chat_type": context.get("chat_type", "main"),
                "user_role": context.get("user_role", "public"),
                **context,
            }
            description = template.description_template.format(**safe_context)

        # Create task with structured output
        task_config = {
            "description": description.strip(),
            "expected_output": template.expected_output.strip(),
            "agent": agent,
            "async_execution": template.async_execution,
            "config": {
                "task_id": task_id,
                "task_type": task_type,
                "created_at": datetime.now().isoformat(),
                **context,
            },
        }

        # Add structured output model if available
        if template.output_model:
            task_config["output_pydantic"] = template.output_model

        # Add output file if specified
        if output_file:
            task_config["output_file"] = output_file

        # Add human input if needed
        if human_input:
            task_config["human_input"] = True

        # Add callback for monitoring
        task_config["callback"] = self._create_task_callback(task_id, task_type)

        task = Task(**task_config)

        # Initialize metrics tracking
        self.metrics_store[task_id] = TaskExecutionMetrics(
            task_id=task_id,
            agent_role=str(getattr(agent, "role", "unknown")),
            start_time=datetime.now(),
            success=False,
            tools_called=template.required_tools + (additional_tools or []),
        )

        logger.info(f"📋 Created {task_type} task (ID: {task_id}) with structured output")
        return task

    def _create_task_callback(self, task_id: str, task_type: str) -> Callable:
        """Create a callback function for task execution monitoring."""

        def task_callback(task_output):
            """Callback executed after task completion."""
            try:
                # Update metrics
                if task_id in self.metrics_store:
                    metrics = self.metrics_store[task_id]
                    metrics.end_time = datetime.now()
                    metrics.success = task_output is not None

                    # Try to extract error information
                    if hasattr(task_output, "error") and task_output.error:
                        metrics.error_message = str(task_output.error)
                        metrics.error_type = type(task_output.error).__name__

                    # Execute registered callbacks
                    for callback in self.execution_callbacks:
                        try:
                            callback(metrics)
                        except Exception as e:
                            logger.error(f"Error in task callback: {e}")

                logger.info(f"✅ Task {task_id} ({task_type}) completed successfully")

            except Exception as e:
                logger.error(f"Error in task callback for {task_id}: {e}")

        return task_callback

    def get_metrics(self, task_id: str) -> TaskExecutionMetrics | None:
        """Get execution metrics for a specific task."""
        return self.metrics_store.get(task_id)

    def get_all_metrics(self) -> dict[str, TaskExecutionMetrics]:
        """Get all task execution metrics."""
        return self.metrics_store.copy()

    def clear_metrics(self, older_than_hours: int = 24):
        """Clear old metrics to prevent memory buildup."""
        cutoff = datetime.now().timestamp() - (older_than_hours * 3600)
        to_remove = []

        for task_id, metrics in self.metrics_store.items():
            if metrics.start_time.timestamp() < cutoff:
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.metrics_store[task_id]

        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} old task metrics")


# Global task factory instance
_task_factory = None


def get_task_factory() -> TaskFactory:
    """Get the global task factory instance."""
    global _task_factory
    if _task_factory is None:
        _task_factory = TaskFactory()
    return _task_factory


def create_structured_task(task_type: str, agent: Agent, context: dict[str, Any], **kwargs) -> Task:
    """Convenience function for creating structured tasks."""
    factory = get_task_factory()
    return factory.create_task(task_type, agent, context, **kwargs)


# Enhanced monitoring and callback system
class TaskMonitor:
    """Enhanced task execution monitoring with real-time insights."""

    def __init__(self):
        self.active_tasks: dict[str, TaskExecutionMetrics] = {}
        self.completed_tasks: dict[str, TaskExecutionMetrics] = {}
        self.callbacks: list[Callable[[str, TaskExecutionMetrics], None]] = []
        self.error_callbacks: list[Callable[[str, Exception], None]] = []

    def register_callback(self, callback: Callable[[str, TaskExecutionMetrics], None]):
        """Register a callback for task completion events."""
        self.callbacks.append(callback)

    def register_error_callback(self, callback: Callable[[str, Exception], None]):
        """Register a callback for task error events."""
        self.error_callbacks.append(callback)

    def start_task(self, task_id: str, agent_role: str, task_type: str) -> TaskExecutionMetrics:
        """Start monitoring a task."""
        metrics = TaskExecutionMetrics(
            task_id=task_id,
            agent_role=agent_role,
            start_time=datetime.now(),
            success=False,
            tools_called=[],
        )
        self.active_tasks[task_id] = metrics
        logger.info(f"📊 Started monitoring task {task_id} ({task_type}) for {agent_role}")
        return metrics

    def complete_task(self, task_id: str, success: bool = True, result: Any = None):
        """Mark a task as completed."""
        if task_id in self.active_tasks:
            metrics = self.active_tasks[task_id]
            metrics.end_time = datetime.now()
            metrics.success = success

            # Move to completed tasks
            self.completed_tasks[task_id] = metrics
            del self.active_tasks[task_id]

            # Execute callbacks
            for callback in self.callbacks:
                try:
                    callback(task_id, metrics)
                except Exception as e:
                    logger.error(f"Error in task completion callback: {e}")

            status = "✅" if success else "❌"
            logger.info(f"{status} Task {task_id} completed in {metrics.duration_ms}ms")

    def task_error(self, task_id: str, error: Exception):
        """Handle task error."""
        if task_id in self.active_tasks:
            metrics = self.active_tasks[task_id]
            metrics.end_time = datetime.now()
            metrics.success = False
            metrics.error_type = type(error).__name__
            metrics.error_message = str(error)

            # Move to completed tasks
            self.completed_tasks[task_id] = metrics
            del self.active_tasks[task_id]

            # Execute error callbacks
            for callback in self.error_callbacks:
                try:
                    callback(task_id, error)
                except Exception as cb_error:
                    logger.error(f"Error in task error callback: {cb_error}")

            logger.error(f"❌ Task {task_id} failed: {error}")

    def add_tool_call(self, task_id: str, tool_name: str):
        """Record a tool call for a task."""
        if task_id in self.active_tasks:
            if tool_name not in self.active_tasks[task_id].tools_called:
                self.active_tasks[task_id].tools_called.append(tool_name)

    def get_active_tasks(self) -> dict[str, TaskExecutionMetrics]:
        """Get currently active tasks."""
        return dict(self.active_tasks)

    def get_completed_tasks(self, limit: int = 100) -> dict[str, TaskExecutionMetrics]:
        """Get recently completed tasks."""
        # Sort by completion time, most recent first
        sorted_tasks = sorted(
            self.completed_tasks.items(), key=lambda x: x[1].end_time or datetime.min, reverse=True
        )
        return dict(sorted_tasks[:limit])

    def get_task_statistics(self) -> dict[str, Any]:
        """Get task execution statistics."""
        total_completed = len(self.completed_tasks)
        successful = sum(1 for metrics in self.completed_tasks.values() if metrics.success)
        failed = total_completed - successful

        if total_completed > 0:
            avg_duration = (
                sum(metrics.duration_ms or 0 for metrics in self.completed_tasks.values())
                / total_completed
            )
        else:
            avg_duration = 0

        return {
            "active_tasks": len(self.active_tasks),
            "total_completed": total_completed,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_completed * 100) if total_completed > 0 else 0,
            "average_duration_ms": avg_duration,
            "most_used_tools": self._get_tool_usage_stats(),
        }

    def _get_tool_usage_stats(self) -> dict[str, int]:
        """Get tool usage statistics."""
        tool_counts: dict[str, int] = {}
        for metrics in self.completed_tasks.values():
            for tool in metrics.tools_called:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1

        # Return top 10 most used tools
        return dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10])

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = [
            task_id
            for task_id, metrics in self.completed_tasks.items()
            if metrics.end_time and metrics.end_time < cutoff
        ]

        for task_id in to_remove:
            del self.completed_tasks[task_id]

        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} old task records")


# Global task monitor instance
_task_monitor = None


def get_task_monitor() -> TaskMonitor:
    """Get the global task monitor instance."""
    global _task_monitor
    if _task_monitor is None:
        _task_monitor = TaskMonitor()
    return _task_monitor


# Enhanced task creation with monitoring
def create_monitored_task(
    task_type: str, agent: Agent, context: dict[str, Any], monitor_callbacks: bool = True, **kwargs
) -> Task:
    """
    Create a task with enhanced monitoring capabilities.

    Args:
        task_type: Type of task to create
        agent: CrewAI agent to execute the task
        context: Context variables for task description
        monitor_callbacks: Whether to enable monitoring callbacks
        **kwargs: Additional task parameters

    Returns:
        Monitored CrewAI Task
    """
    factory = get_task_factory()
    monitor = get_task_monitor()

    # Create base task
    task = factory.create_task(task_type, agent, context, **kwargs)

    if monitor_callbacks and hasattr(task, "config") and task.config:
        task_id = task.config.get("task_id", "unknown")
        agent_role = getattr(agent, "role", "unknown")

        # Start monitoring
        monitor.start_task(task_id, agent_role, task_type)

        # Create enhanced callback that includes monitoring
        original_callback = getattr(task, "callback", None)

        def enhanced_callback(task_output):
            try:
                # Execute original callback first
                if original_callback:
                    original_callback(task_output)

                # Determine success based on output
                success = task_output is not None and (
                    not hasattr(task_output, "error") or not task_output.error
                )

                # Complete monitoring
                monitor.complete_task(task_id, success, task_output)

            except Exception as e:
                # Handle callback error
                monitor.task_error(task_id, e)
                logger.error(f"Error in enhanced task callback for {task_id}: {e}")

        # Set enhanced callback
        task.callback = enhanced_callback

    return task
